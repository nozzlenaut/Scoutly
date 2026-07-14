from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
MAX_FILE_FEEDBACK = 2000


def _now() -> datetime:
    return datetime.now(UTC)


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _feedback_path() -> Path:
    return _data_dir() / "beta_feedback.json"


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return payload if isinstance(payload, list) else []


def _write_json_list(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(path)


def _serialize(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value.isoformat() if isinstance(value, datetime) else value
        for key, value in record.items()
    }


def save_beta_feedback(
    *,
    feedback_type: str,
    message: str,
    category: str | None = None,
    email: str | None = None,
    page_url: str | None = None,
) -> dict[str, Any]:
    record = {
        "id": str(uuid4()),
        "submitted_at": _now(),
        "feedback_type": feedback_type.strip().lower(),
        "category": category.strip().lower() if category else None,
        "message": message.strip(),
        "email": email.strip() if email else None,
        "page_url": page_url.strip() if page_url else None,
    }

    if database_configured():
        try:
            with database_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO scoutly_beta_feedback (
                        id, submitted_at, feedback_type, category, message, email, page_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        record["id"],
                        record["submitted_at"],
                        record["feedback_type"],
                        record["category"],
                        record["message"],
                        record["email"],
                        record["page_url"],
                    ),
                )
            return _serialize(record)
        except Exception:
            logger.exception("PostgreSQL beta-feedback write failed; using file fallback.")

    records = _read_json_list(_feedback_path())
    records.append(_serialize(record))
    _write_json_list(_feedback_path(), records[-MAX_FILE_FEEDBACK:])
    return _serialize(record)


def list_beta_feedback(limit: int = 100) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 500))
    if database_configured():
        try:
            with database_connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, submitted_at, feedback_type, category, message, email, page_url
                    FROM scoutly_beta_feedback
                    ORDER BY submitted_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                ).fetchall()
            return [_serialize(dict(row)) for row in rows]
        except Exception:
            logger.exception("PostgreSQL beta-feedback read failed; using file fallback.")

    records = _read_json_list(_feedback_path())
    return list(reversed(records[-limit:]))


def beta_feedback_count() -> int:
    if database_configured():
        try:
            with database_connection() as connection:
                row = connection.execute(
                    "SELECT COUNT(*) AS count FROM scoutly_beta_feedback"
                ).fetchone()
            return int(row["count"] or 0)
        except Exception:
            logger.exception("PostgreSQL beta-feedback count failed; using file fallback.")
    return len(_read_json_list(_feedback_path()))
