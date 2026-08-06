import asyncio
import base64
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api import search_audit


def _listing(title: str, total_price: float) -> SimpleNamespace:
    return SimpleNamespace(
        title=title,
        price=total_price - 10,
        shipping=10.0,
        total_price=total_price,
        condition="Used",
        url="https://www.ebay.com/itm/123",
        image_url="https://i.ebayimg.com/images/example.jpg",
        item_location="Detroit, MI, US",
        marketplace_item_id="v1|123|0",
    )


def test_raw_audit_search_uses_literal_query_and_skips_pricesift_category(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "test-token")
    calls = {}

    class FakeProvider:
        async def search(
            self,
            query: str,
            category: str | None = None,
            buying_option: str = "fixed_price",
            item_location_country: str | None = None,
        ):
            calls.update(
                query=query,
                category=category,
                buying_option=buying_option,
                item_location_country=item_location_country,
            )
            return [
                _listing("First raw result", 1100.0),
                _listing("Second raw result", 1200.0),
                _listing("Third raw result", 1300.0),
            ]

    monkeypatch.setattr(search_audit, "EbayProvider", FakeProvider)

    result = asyncio.run(
        search_audit.get_raw_ebay_sample(
            q="  sony a7iii body only  ",
            limit=2,
            token="test-token",
        )
    )

    assert calls == {
        "query": "sony a7iii body only",
        "category": None,
        "buying_option": "fixed_price",
        "item_location_country": "US",
    }
    assert result["method"]["pricesift_filters_applied"] is False
    assert result["returned"] == 2
    assert result["listings"][0]["title"] == "First raw result"
    assert result["listings"][0]["total_price"] == 1100.0
    assert result["listings"][0]["condition"] == "Used"
    assert result["listings"][0]["url"] == "https://www.ebay.com/itm/123"

PNG_DATA_URL = "data:image/png;base64," + base64.b64encode(
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
).decode("ascii")


def _buffer_payload() -> search_audit.BufferDraftPayload:
    return search_audit.BufferDraftPayload(
        audit_id="audit-api",
        post_text="A draft only.",
        alt_text="A PriceSift audit card.",
        image_data_url=PNG_DATA_URL,
    )


def test_buffer_draft_endpoint_requires_admin(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "test-token")
    with pytest.raises(HTTPException) as error:
        asyncio.run(
            search_audit.create_audit_buffer_draft(
                payload=_buffer_payload(),
                request=SimpleNamespace(base_url="http://localhost:8000/"),
                token="wrong-token",
            )
        )
    assert error.value.status_code == 401


def test_buffer_draft_endpoint_uses_public_base_and_service(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "test-token")
    monkeypatch.setenv("PUBLIC_API_BASE_URL", "https://api.pricesift.test")
    calls = {}

    async def fake_create_buffer_draft(**kwargs):
        calls.update(kwargs)
        return {
            "status": "created",
            "buffer_post_id": "draft-123",
            "dry_run": True,
            "message": "Dry run passed.",
        }

    monkeypatch.setattr(search_audit, "create_buffer_draft", fake_create_buffer_draft)
    result = asyncio.run(
        search_audit.create_audit_buffer_draft(
            payload=_buffer_payload(),
            request=SimpleNamespace(base_url="http://localhost:8000/"),
            token="test-token",
        )
    )

    assert result["buffer_post_id"] == "draft-123"
    assert calls["audit_id"] == "audit-api"
    assert calls["public_base_url"] == "https://api.pricesift.test"
