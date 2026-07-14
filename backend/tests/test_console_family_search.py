import asyncio

from app.catalog.catalog import listing_matches_product, match_product, suggest_products
from app.models.listing import Listing
from app.ranking.scorer import is_bad_listing
from app.services import search_service


class RecordingConsoleProvider:
    name = "eBay"

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def search(
        self,
        query: str,
        category: str | None = None,
        buying_option: str = "fixed_price",
    ) -> list[Listing]:
        self.calls.append((query, buying_option))
        if buying_option == "auction":
            return []
        if "Series X" in query:
            return [
                Listing(
                    provider="eBay",
                    title="Microsoft Xbox Series X 1TB Console Black Tested",
                    price=329.99,
                    shipping=0,
                    total_price=329.99,
                    condition="Used",
                    seller_rating=99.8,
                    seller_feedback_score=500,
                    url="https://www.ebay.com/itm/100000000002",
                )
            ]
        return []


def test_direct_console_search_runs_one_exact_catalog_query(monkeypatch):
    provider = RecordingConsoleProvider()
    monkeypatch.setitem(search_service.PROVIDERS, "ebay", provider)

    resolved, results, auctions, diagnostics = asyncio.run(
        search_service.search_best_deals_with_auctions(
            "Xbox Series X",
            ["ebay"],
            "consoles",
            include_auctions=False,
        )
    )

    assert resolved is not None
    assert resolved.product.id == "console-xbox-series-x-1tb"
    assert resolved.product.metadata.get("builder") is None
    assert len(provider.calls) == 1
    assert provider.calls[0][0] == "Xbox Series X 1TB"
    assert [listing.title for listing in results] == [
        "Microsoft Xbox Series X 1TB Console Black Tested"
    ]
    assert auctions == []
    assert diagnostics.fixed_price_candidates == 1


def test_console_autocomplete_returns_exact_model_choices():
    xbox = suggest_products("Xbox Series", category="consoles", limit=5)
    playstation = suggest_products("PlayStation 5", category="consoles", limit=8)

    assert {match.product.id for match in xbox[:3]} == {
        "console-xbox-series-x-1tb",
        "console-xbox-series-s-512gb",
        "console-xbox-series-s-1tb",
    }
    assert "console-playstation-5-slim-digital-edition" in {
        match.product.id for match in playstation
    }
    assert "console-playstation-5-slim-disc-edition" in {
        match.product.id for match in playstation
    }


def test_controller_requires_console_and_service_is_rejected():
    product = match_product("Xbox Series X", category="consoles").product
    controller_without_console = Listing(
        provider="eBay",
        title="Xbox Series X with Wireless Controller Tested",
        price=299,
        shipping=0,
        total_price=299,
        condition="Used",
        url="https://www.ebay.com/itm/100000000003",
    )
    controller_with_console = Listing(
        provider="eBay",
        title="Xbox Series X Console with Wireless Controller Tested",
        price=299,
        shipping=0,
        total_price=299,
        condition="Used",
        url="https://www.ebay.com/itm/100000000004",
    )
    service_listing = Listing(
        provider="eBay",
        title="Xbox Series X Cleaning Service",
        price=49,
        shipping=0,
        total_price=49,
        condition="Used",
        url="https://www.ebay.com/itm/100000000005",
    )

    assert is_bad_listing(controller_without_console, product) is True
    assert is_bad_listing(controller_with_console, product) is False
    assert is_bad_listing(service_listing, product) is True


def test_xbox_storage_accessories_remain_rejected():
    listing = Listing(
        provider="eBay",
        title="Xbox Series X|S External Hard Drive 2TB USB Game Storage",
        price=49.99,
        shipping=0,
        total_price=49.99,
        condition="Used",
        seller_rating=99.8,
        seller_feedback_score=500,
        url="https://www.ebay.com/itm/100000000006",
    )
    product = match_product("Xbox Series X", category="consoles").product
    assert is_bad_listing(listing, product) is True


class RecordingSwitchProvider:
    name = "eBay"

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def search(
        self,
        query: str,
        category: str | None = None,
        buying_option: str = "fixed_price",
    ) -> list[Listing]:
        self.calls.append((query, buying_option))
        if buying_option == "auction":
            return []
        if "HAC-001(-01)" in query:
            return [
                Listing(
                    provider="eBay",
                    title="Nintendo Switch V2 HAC-001(-01) Console Neon Tested",
                    price=179.99,
                    shipping=0,
                    total_price=179.99,
                    condition="Used",
                    seller_rating=99.8,
                    seller_feedback_score=500,
                    url="https://www.ebay.com/itm/100000000010",
                )
            ]
        if query == "Nintendo Switch console":
            return [
                Listing(
                    provider="eBay",
                    title="Nintendo Switch Console HAC-001 Gray Tested",
                    price=159.99,
                    shipping=0,
                    total_price=159.99,
                    condition="Used",
                    seller_rating=99.8,
                    seller_feedback_score=500,
                    url="https://www.ebay.com/itm/100000000011",
                )
            ]
        return []


def test_original_switch_aliases_use_revision_and_generic_provider_queries():
    aliases = [
        "Nintendo Switch",
        "Nintendo Switch V1",
        "Switch V1",
        "Nintendo Switch V2",
        "Switch V2",
        "HAC-001",
        "HAC-001(-01)",
        "Nintendo Switch Standard",
        "Original Nintendo Switch",
    ]
    expected_queries = [
        "Nintendo Switch V1 console",
        "Nintendo Switch V2 console",
        "Nintendo Switch HAC-001 console",
        "Nintendo Switch HAC-001(-01) console",
        "Nintendo Switch Standard console",
        "Nintendo Switch console",
    ]
    for alias in aliases:
        match = match_product(alias, category="consoles")
        assert match is not None, alias
        assert match.product.id == "console-nintendo-switch-v1-v2", alias
        assert search_service._provider_queries_for_product(alias, match.product) == expected_queries


def test_original_switch_combines_revision_results(monkeypatch):
    provider = RecordingSwitchProvider()
    monkeypatch.setitem(search_service.PROVIDERS, "ebay", provider)

    resolved, results, auctions, diagnostics = asyncio.run(
        search_service.search_best_deals_with_auctions(
            "Nintendo Switch V1",
            ["ebay"],
            "consoles",
            include_auctions=False,
        )
    )

    assert resolved is not None
    assert resolved.product.id == "console-nintendo-switch-v1-v2"
    assert [call[0] for call in provider.calls] == [
        "Nintendo Switch V1 console",
        "Nintendo Switch V2 console",
        "Nintendo Switch HAC-001 console",
        "Nintendo Switch HAC-001(-01) console",
        "Nintendo Switch Standard console",
        "Nintendo Switch console",
    ]
    assert [listing.title for listing in results] == [
        "Nintendo Switch Console HAC-001 Gray Tested",
        "Nintendo Switch V2 HAC-001(-01) Console Neon Tested",
    ]
    assert auctions == []
    assert diagnostics.fixed_price_candidates == 2


def test_original_switch_accepts_v1_v2_hac_and_rejects_other_models():
    product = match_product("Nintendo Switch V1", category="consoles").product
    valid_titles = [
        "Nintendo Switch V1 Console Tested",
        "Nintendo Switch V2 Console Tested",
        "Nintendo Switch Console HAC-001 Gray Tested",
        "Nintendo Switch HAC-001(-01) Console Neon Tested",
        "Nintendo Switch Standard Console Complete",
    ]
    rejected_titles = [
        "Nintendo Switch OLED Console Complete",
        "Nintendo Switch Lite Console Yellow",
        "Nintendo Switch 2 Console",
        "Nintendo Switch V2 Tablet Only",
        "Nintendo Switch Dock Only",
        "Nintendo Switch Joy-Con Only",
    ]
    for title in valid_titles:
        assert listing_matches_product(title, product) is True, title
    for title in rejected_titles:
        assert listing_matches_product(title, product) is False, title
