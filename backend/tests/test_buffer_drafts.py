from __future__ import annotations

import asyncio
import base64
from pathlib import Path

import httpx
import pytest

from app.services import buffer_drafts


PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)
PNG_DATA_URL = "data:image/png;base64," + base64.b64encode(PNG_BYTES).decode("ascii")


@pytest.fixture
def local_store(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("BUFFER_API_KEY", raising=False)
    monkeypatch.delenv("BUFFER_BLUESKY_CHANNEL_ID", raising=False)
    monkeypatch.delenv("PUBLIC_API_BASE_URL", raising=False)
    return tmp_path


def test_dry_run_stores_image_and_blocks_duplicate(
    monkeypatch: pytest.MonkeyPatch,
    local_store: Path,
) -> None:
    monkeypatch.setenv("BUFFER_DRAFT_DRY_RUN", "true")

    result = asyncio.run(buffer_drafts.create_buffer_draft(
        audit_id="audit-1",
        post_text="A safe draft.",
        alt_text="A PriceSift audit card.",
        image_data_url=PNG_DATA_URL,
        public_base_url="http://localhost:8000",
    ))

    assert result["dry_run"] is True
    assert result["buffer_post_id"] == "dry-run-audit-1"
    token = result["image_url"].split("/")[-1].removesuffix(".png")
    assert buffer_drafts.get_share_image(token) == PNG_BYTES

    with pytest.raises(buffer_drafts.DuplicateBufferDraft) as duplicate:
        asyncio.run(buffer_drafts.create_buffer_draft(
            audit_id="audit-1",
            post_text="A second draft.",
            alt_text="Another card.",
            image_data_url=PNG_DATA_URL,
            public_base_url="http://localhost:8000",
        ))
    assert duplicate.value.status == "created"


def test_live_request_is_always_a_buffer_draft(
    monkeypatch: pytest.MonkeyPatch,
    local_store: Path,
) -> None:
    monkeypatch.setenv("BUFFER_DRAFT_DRY_RUN", "false")
    monkeypatch.setenv("BUFFER_API_KEY", "test-key")
    monkeypatch.setenv("BUFFER_BLUESKY_CHANNEL_ID", "6a6886964b2d03035f55c95e")
    monkeypatch.setattr(buffer_drafts, "database_configured", lambda: True)
    monkeypatch.setattr(buffer_drafts, "_reserve_record", lambda record: None)
    monkeypatch.setattr(buffer_drafts, "_update_record", lambda audit_id, **patch: None)

    captured: dict = {}

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json() -> dict:
            return {
                "data": {
                    "createPost": {
                        "__typename": "PostActionSuccess",
                        "post": {"id": "buffer-draft-1", "text": "A safe draft."},
                    }
                }
            }

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, url: str, **kwargs):
            captured["url"] = url
            captured["request"] = kwargs
            return FakeResponse()

    monkeypatch.setattr(buffer_drafts.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(buffer_drafts.create_buffer_draft(
        audit_id="audit-live",
        post_text="A safe draft.",
        alt_text="A PriceSift audit card.",
        image_data_url=PNG_DATA_URL,
        public_base_url="https://api.pricesift.app",
    ))

    assert result["dry_run"] is False
    assert result["buffer_post_id"] == "buffer-draft-1"
    request_json = captured["request"]["json"]
    create_input = request_json["variables"]["input"]
    assert captured["url"] == "https://api.buffer.com"
    assert create_input["saveToDraft"] is True
    assert create_input["mode"] == "addToQueue"
    assert create_input["schedulingType"] == "automatic"
    assert create_input["channelId"] == "6a6886964b2d03035f55c95e"
    assert create_input["assets"][0]["image"]["metadata"]["altText"] == "A PriceSift audit card."
    assert "dueAt" not in create_input


def test_network_error_becomes_unknown_and_blocks_retry(
    monkeypatch: pytest.MonkeyPatch,
    local_store: Path,
) -> None:
    monkeypatch.setenv("BUFFER_DRAFT_DRY_RUN", "false")
    monkeypatch.setenv("BUFFER_API_KEY", "test-key")
    monkeypatch.setenv("BUFFER_BLUESKY_CHANNEL_ID", "6a6886964b2d03035f55c95e")
    monkeypatch.setattr(buffer_drafts, "database_configured", lambda: True)
    records: dict[str, dict] = {}

    def reserve(record: dict) -> None:
        existing = records.get(record["audit_id"])
        if existing and existing.get("status") != "failed":
            raise buffer_drafts.DuplicateBufferDraft(
                status=str(existing.get("status") or "unknown"),
                buffer_post_id=existing.get("buffer_post_id"),
            )
        records[record["audit_id"]] = dict(record)

    def update(audit_id: str, **patch) -> None:
        records[audit_id].update(patch)

    monkeypatch.setattr(buffer_drafts, "_reserve_record", reserve)
    monkeypatch.setattr(buffer_drafts, "_update_record", update)

    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, url: str, **kwargs):
            request = httpx.Request("POST", url)
            raise httpx.ConnectTimeout("timeout", request=request)

    monkeypatch.setattr(buffer_drafts.httpx, "AsyncClient", lambda *args, **kwargs: FailingClient())

    with pytest.raises(buffer_drafts.BufferDraftError, match="uncertain"):
        asyncio.run(buffer_drafts.create_buffer_draft(
            audit_id="audit-timeout",
            post_text="A safe draft.",
            alt_text="A PriceSift audit card.",
            image_data_url=PNG_DATA_URL,
            public_base_url="https://api.pricesift.app",
        ))

    with pytest.raises(buffer_drafts.DuplicateBufferDraft) as duplicate:
        asyncio.run(buffer_drafts.create_buffer_draft(
            audit_id="audit-timeout",
            post_text="A safe draft.",
            alt_text="A PriceSift audit card.",
            image_data_url=PNG_DATA_URL,
            public_base_url="https://api.pricesift.app",
        ))
    assert duplicate.value.status == "unknown"


def test_invalid_image_is_rejected() -> None:
    with pytest.raises(buffer_drafts.BufferDraftError, match="valid PNG"):
        buffer_drafts.decode_png_data_url(
            "data:image/png;base64," + base64.b64encode(b"not a png").decode("ascii")
        )
