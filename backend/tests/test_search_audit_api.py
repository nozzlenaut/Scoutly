import asyncio
from types import SimpleNamespace

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
