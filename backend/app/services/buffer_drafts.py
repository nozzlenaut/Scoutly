from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import secrets
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)

BUFFER_GRAPHQL_URL = "https://api.buffer.com"
MAX_IMAGE_BYTES = 4 * 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_FILE_LOCK = threading.Lock()


class BufferDraftError(RuntimeError):
    """A safe, user-facing Buffer draft failure."""


@dataclass(slots=True)
class DuplicateBufferDraft(BufferDraftError):
    status: str
    buffer_post_id: str | None = None

    def __str__(self) -> str:
        if self.status == "created":
            return "This audit already has a Buffer draft."
        if self.status == "creating":
            return "A Buffer draft is already being created for this audit."
        if self.status == "unknown":
            return (
                "The previous Buffer request had an uncertain result. Check Buffer before retrying "
                "so a duplicate draft is not created."
            )
        return "This audit has already been submitted to Buffer."


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _records_path() -> Path:
    return _data_dir() / "buffer_drafts.json"


def _read_file_records() -> dict[str, dict[str, Any]]:
    path = _records_path()
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_file_records(records: dict[str, dict[str, Any]]) -> None:
    path = _records_path()
    temp_path = path.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(path)


def _ensure_table(connection: Any) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS scoutly_buffer_drafts (
            audit_id TEXT PRIMARY KEY,
            request_hash TEXT NOT NULL,
            status TEXT NOT NULL,
            buffer_post_id TEXT,
            image_token TEXT NOT NULL UNIQUE,
            image_png BYTEA NOT NULL,
            post_text TEXT NOT NULL,
            alt_text TEXT NOT NULL,
            error_message TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS scoutly_buffer_drafts_status
        ON scoutly_buffer_drafts (status, updated_at DESC)
        """
    )


def decode_png_data_url(value: str) -> bytes:
    prefix = "data:image/png;base64,"
    if not value.startswith(prefix):
        raise BufferDraftError("The generated share image was not a PNG data URL.")
    try:
        image = base64.b64decode(value[len(prefix) :], validate=True)
    except (ValueError, TypeError) as error:
        raise BufferDraftError("The generated share image could not be decoded.") from error
    if not image.startswith(PNG_SIGNATURE):
        raise BufferDraftError("The generated share image did not contain a valid PNG.")
    if len(image) > MAX_IMAGE_BYTES:
        raise BufferDraftError("The generated share image is too large.")
    return image


def _request_hash(audit_id: str, post_text: str, alt_text: str, image_png: bytes) -> str:
    digest = hashlib.sha256()
    for value in (audit_id, post_text, alt_text):
        digest.update(value.encode("utf-8"))
        digest.update(b"\0")
    digest.update(image_png)
    return digest.hexdigest()


def _reserve_file_record(record: dict[str, Any]) -> None:
    with _FILE_LOCK:
        records = _read_file_records()
        existing = records.get(record["audit_id"])
        if existing and existing.get("status") != "failed":
            raise DuplicateBufferDraft(
                status=str(existing.get("status") or "unknown"),
                buffer_post_id=existing.get("buffer_post_id") or None,
            )
        serializable = dict(record)
        serializable.pop("image_png", None)
        records[record["audit_id"]] = serializable
        _write_file_records(records)


def _reserve_database_record(record: dict[str, Any]) -> None:
    with database_connection() as connection:
        _ensure_table(connection)
        row = connection.execute(
            """
            INSERT INTO scoutly_buffer_drafts (
                audit_id, request_hash, status, image_token, image_png,
                post_text, alt_text, created_at, updated_at
            ) VALUES (%s, %s, 'creating', %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (audit_id) DO NOTHING
            RETURNING audit_id
            """,
            (
                record["audit_id"],
                record["request_hash"],
                record["image_token"],
                record["image_png"],
                record["post_text"],
                record["alt_text"],
            ),
        ).fetchone()
        if row:
            return

        existing = connection.execute(
            """
            SELECT status, buffer_post_id
            FROM scoutly_buffer_drafts
            WHERE audit_id = %s
            """,
            (record["audit_id"],),
        ).fetchone()
        if existing and str(existing["status"]) == "failed":
            retried = connection.execute(
                """
                UPDATE scoutly_buffer_drafts
                SET request_hash = %s,
                    status = 'creating',
                    buffer_post_id = NULL,
                    image_token = %s,
                    image_png = %s,
                    post_text = %s,
                    alt_text = %s,
                    error_message = NULL,
                    updated_at = NOW()
                WHERE audit_id = %s AND status = 'failed'
                RETURNING audit_id
                """,
                (
                    record["request_hash"],
                    record["image_token"],
                    record["image_png"],
                    record["post_text"],
                    record["alt_text"],
                    record["audit_id"],
                ),
            ).fetchone()
            if retried:
                return

        status_value = str(existing["status"]) if existing else "unknown"
        post_id = str(existing["buffer_post_id"]) if existing and existing["buffer_post_id"] else None
        raise DuplicateBufferDraft(status=status_value, buffer_post_id=post_id)


def _reserve_record(record: dict[str, Any]) -> None:
    if database_configured():
        # Fail closed when PostgreSQL is configured but unavailable. Falling back to
        # a process-local file here could create duplicates across Railway instances.
        _reserve_database_record(record)
        return
    _reserve_file_record(record)


def _update_file_record(audit_id: str, **patch: Any) -> None:
    with _FILE_LOCK:
        records = _read_file_records()
        existing = records.get(audit_id)
        if not existing:
            return
        existing.update(patch)
        existing["updated_at"] = _now_iso()
        records[audit_id] = existing
        _write_file_records(records)


def _update_database_record(audit_id: str, **patch: Any) -> None:
    allowed = {"status", "buffer_post_id", "error_message"}
    values = {key: value for key, value in patch.items() if key in allowed}
    if not values:
        return
    assignments = [f"{key} = %s" for key in values]
    parameters = [*values.values(), audit_id]
    with database_connection() as connection:
        _ensure_table(connection)
        connection.execute(
            f"""
            UPDATE scoutly_buffer_drafts
            SET {', '.join(assignments)}, updated_at = NOW()
            WHERE audit_id = %s
            """,
            parameters,
        )


def _update_record(audit_id: str, **patch: Any) -> None:
    if database_configured():
        _update_database_record(audit_id, **patch)
    else:
        _update_file_record(audit_id, **patch)


def _public_image_url(public_base_url: str, image_token: str) -> str:
    base = public_base_url.strip().rstrip("/")
    if not base:
        raise BufferDraftError("PUBLIC_API_BASE_URL is not configured.")
    if not base.startswith("https://") and not _truthy_env("BUFFER_DRAFT_DRY_RUN"):
        raise BufferDraftError("PUBLIC_API_BASE_URL must use HTTPS for live Buffer drafts.")
    return f"{base}/api/search-audit/share-image/{image_token}.png"


def _graphql_error(payload: dict[str, Any]) -> str | None:
    errors = payload.get("errors")
    if isinstance(errors, list) and errors:
        first = errors[0]
        if isinstance(first, dict) and first.get("message"):
            return str(first["message"])
        return "Buffer returned a GraphQL error."

    result = (payload.get("data") or {}).get("createPost")
    if not isinstance(result, dict):
        return "Buffer returned an unexpected response."
    if result.get("__typename") == "MutationError":
        return str(result.get("message") or "Buffer rejected the draft.")
    if result.get("__typename") != "PostActionSuccess":
        return "Buffer returned an unexpected draft result."
    post = result.get("post")
    if not isinstance(post, dict) or not post.get("id"):
        return "Buffer did not return a draft ID."
    return None


async def create_buffer_draft(
    *,
    audit_id: str,
    post_text: str,
    alt_text: str,
    image_data_url: str,
    public_base_url: str,
) -> dict[str, Any]:
    audit_id = audit_id.strip()
    post_text = post_text.strip()
    alt_text = alt_text.strip()
    if not audit_id:
        raise BufferDraftError("Audit ID is required.")
    if not post_text:
        raise BufferDraftError("Post text is required.")
    if len(post_text) > 300:
        raise BufferDraftError("Bluesky post text must be 300 characters or fewer.")
    if not alt_text:
        raise BufferDraftError("Image alt text is required.")
    if len(alt_text) > 2000:
        raise BufferDraftError("Image alt text is too long.")

    dry_run = _truthy_env("BUFFER_DRAFT_DRY_RUN")
    if not dry_run and not database_configured():
        raise BufferDraftError(
            "PostgreSQL is required for live Buffer drafts so duplicate protection and images remain stable."
        )

    image_png = decode_png_data_url(image_data_url)
    image_token = secrets.token_urlsafe(32)
    request_hash = _request_hash(audit_id, post_text, alt_text, image_png)
    image_url = _public_image_url(public_base_url, image_token)
    now = _now_iso()
    record: dict[str, Any] = {
        "audit_id": audit_id,
        "request_hash": request_hash,
        "status": "creating",
        "buffer_post_id": None,
        "image_token": image_token,
        "image_png": image_png,
        "image_png_base64": base64.b64encode(image_png).decode("ascii"),
        "post_text": post_text,
        "alt_text": alt_text,
        "error_message": None,
        "created_at": now,
        "updated_at": now,
    }
    _reserve_record(record)

    if dry_run:
        dry_run_id = f"dry-run-{audit_id}"
        _update_record(audit_id, status="created", buffer_post_id=dry_run_id, error_message=None)
        return {
            "status": "created",
            "buffer_post_id": dry_run_id,
            "image_url": image_url,
            "dry_run": True,
            "message": "Dry run passed. No Buffer draft was created.",
        }

    api_key = os.getenv("BUFFER_API_KEY", "").strip()
    channel_id = os.getenv("BUFFER_BLUESKY_CHANNEL_ID", "").strip()
    if not api_key or not channel_id:
        _update_record(
            audit_id,
            status="failed",
            error_message="Buffer API credentials or Bluesky channel ID are not configured.",
        )
        raise BufferDraftError("Buffer API credentials or Bluesky channel ID are not configured.")

    query = """
    mutation CreateAuditBufferDraft($input: CreatePostInput!) {
      createPost(input: $input) {
        __typename
        ... on PostActionSuccess {
          post {
            id
            text
          }
        }
        ... on MutationError {
          message
        }
      }
    }
    """
    variables = {
        "input": {
            "channelId": channel_id,
            "schedulingType": "automatic",
            "mode": "addToQueue",
            "text": post_text,
            "assets": [
                {
                    "image": {
                        "url": image_url,
                        "metadata": {"altText": alt_text},
                    }
                }
            ],
            "saveToDraft": True,
            "source": "pricesift-search-audit",
        }
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                BUFFER_GRAPHQL_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={"query": query, "variables": variables},
            )
    except httpx.RequestError as error:
        _update_record(audit_id, status="unknown", error_message=type(error).__name__)
        raise BufferDraftError(
            "Buffer could not be reached and the result is uncertain. Check Buffer before retrying."
        ) from error

    if response.status_code >= 500:
        _update_record(audit_id, status="unknown", error_message=f"HTTP {response.status_code}")
        raise BufferDraftError(
            "Buffer returned a server error and the result is uncertain. Check Buffer before retrying."
        )
    if response.status_code >= 400:
        _update_record(audit_id, status="failed", error_message=f"HTTP {response.status_code}")
        raise BufferDraftError(f"Buffer rejected the request ({response.status_code}).")

    try:
        payload = response.json()
    except ValueError as error:
        _update_record(audit_id, status="unknown", error_message="invalid_json")
        raise BufferDraftError(
            "Buffer returned an unreadable response. Check Buffer before retrying."
        ) from error

    error_message = _graphql_error(payload)
    if error_message:
        _update_record(audit_id, status="failed", error_message=error_message[:500])
        raise BufferDraftError(error_message)

    post = payload["data"]["createPost"]["post"]
    post_id = str(post["id"])
    _update_record(audit_id, status="created", buffer_post_id=post_id, error_message=None)
    return {
        "status": "created",
        "buffer_post_id": post_id,
        "image_url": image_url,
        "dry_run": False,
        "message": "Buffer draft created. Nothing was published or scheduled.",
    }


def get_share_image(image_token: str) -> bytes | None:
    token = image_token.strip()
    if not token:
        return None

    if database_configured():
        with database_connection() as connection:
            _ensure_table(connection)
            row = connection.execute(
                """
                SELECT image_png
                FROM scoutly_buffer_drafts
                WHERE image_token = %s
                """,
                (token,),
            ).fetchone()
        if not row:
            return None
        return bytes(row["image_png"])

    with _FILE_LOCK:
        records = _read_file_records()
        for record in records.values():
            if record.get("image_token") != token:
                continue
            encoded = record.get("image_png_base64")
            if not encoded:
                return None
            try:
                return base64.b64decode(encoded, validate=True)
            except (ValueError, TypeError):
                return None
    return None
