import asyncio

from app.catalog.catalog import listing_matches_product, match_product
from app.catalog.consoles import console_search_products
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
        if "Series S" in query:
            return [
                Listing(
                    provider="eBay",
                    title="Microsoft Xbox Series S 512GB Console White Tested",
                    price=179.99,
                    shipping=0,
                    total_price=179.99,
                    condition="Used",
                    seller_rating=99.8,
                    seller_feedback_score=500,
                    url="https://www.ebay.com/itm/100000000001",
                )
            ]
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


def test_console_family_expands_into_each_active_model():
    family = match_product("Xbox Series", category="consoles")
    assert family is not None
    expanded = console_search_products(family.product)
    assert [product.metadata["model_scope"] for product in expanded] == ["Series S", "Series X"]
    assert [product.metadata["provider_query"] for product in expanded] == [
        "Xbox Series S console",
        "Xbox Series X console",
    ]


def test_console_family_storage_only_searches_compatible_models():
    family = match_product("Xbox Series 512GB", category="consoles")
    assert family is not None
    expanded = console_search_products(family.product)
    assert [product.metadata["model_scope"] for product in expanded] == ["Series S"]


def test_family_search_runs_each_model_and_combines_results(monkeypatch):
    provider = RecordingConsoleProvider()
    monkeypatch.setitem(search_service.PROVIDERS, "ebay", provider)

    resolved, results, auctions, diagnostics = asyncio.run(
        search_service.search_best_deals_with_auctions(
            "Xbox Series",
            ["ebay"],
            "consoles",
            include_auctions=False,
        )
    )

    assert resolved is not None
    assert [call[0] for call in provider.calls] == [
        "Xbox Series S console",
        "Xbox Series X 1TB",
    ]
    assert [listing.title for listing in results] == [
        "Microsoft Xbox Series S 512GB Console White Tested",
        "Microsoft Xbox Series X 1TB Console Black Tested",
    ]
    assert auctions == []
    assert diagnostics.fixed_price_candidates == 2


def test_exact_console_model_still_runs_one_search(monkeypatch):
    provider = RecordingConsoleProvider()
    monkeypatch.setitem(search_service.PROVIDERS, "ebay", provider)

    _, results, _, _ = asyncio.run(
        search_service.search_best_deals_with_auctions(
            "Xbox Series X",
            ["ebay"],
            "consoles",
            include_auctions=False,
        )
    )

    assert len(provider.calls) == 1
    assert "Xbox Series X" in provider.calls[0][0]
    assert len(results) == 1
    assert "Series X" in results[0].title


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


def test_family_child_uses_same_product_identity_as_direct_model_search():
    family = match_product("Xbox Series", category="consoles")
    direct_series_x = match_product("Xbox Series X", category="consoles")
    assert family is not None
    assert direct_series_x is not None

    scopes = search_service._search_product_scopes(family.product)
    series_x_scope = next(product for product in scopes if "Series X" in product.display_name)
    assert series_x_scope.id == direct_series_x.product.id


def test_xbox_storage_accessories_are_rejected_for_direct_and_family_scopes():
    title = "Xbox Series X|S External Hard Drive 2TB USB Game Storage"
    listing = Listing(
        provider="eBay",
        title=title,
        price=49.99,
        shipping=0,
        total_price=49.99,
        condition="Used",
        seller_rating=99.8,
        seller_feedback_score=500,
        url="https://www.ebay.com/itm/100000000006",
    )

    direct = match_product("Xbox Series X", category="consoles")
    family = match_product("Xbox Series", category="consoles")
    assert direct is not None
    assert family is not None
    assert is_bad_listing(listing, direct.product) is True
    for scoped_product in search_service._search_product_scopes(family.product):
        assert is_bad_listing(listing, scoped_product) is True


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


def test_standard_switch_uses_revision_and_generic_provider_queries():
    standard = match_product("Nintendo Switch Standard", category="consoles")
    assert standard is not None
    assert search_service._provider_queries_for_product(
        "Nintendo Switch Standard", standard.product
    ) == [
        "Nintendo Switch V1 console",
        "Nintendo Switch V2 console",
        "Nintendo Switch HAC-001 console",
        "Nintendo Switch HAC-001(-01) console",
        "Nintendo Switch Standard console",
        "Nintendo Switch console",
    ]


def test_standard_switch_combines_results_from_revision_queries(monkeypatch):
    provider = RecordingSwitchProvider()
    monkeypatch.setitem(search_service.PROVIDERS, "ebay", provider)

    resolved, results, auctions, diagnostics = asyncio.run(
        search_service.search_best_deals_with_auctions(
            "Nintendo Switch Standard",
            ["ebay"],
            "consoles",
            include_auctions=False,
        )
    )

    assert resolved is not None
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


def test_standard_switch_accepts_v1_v2_hac_and_standard_identity():
    product = match_product("Nintendo Switch Standard", category="consoles").product
    valid_titles = [
        "Nintendo Switch V1 Console Tested",
        "Nintendo Switch V2 Console Tested",
        "Nintendo Switch Console HAC-001 Gray Tested",
        "Nintendo Switch HAC-001(-01) Console Neon Tested",
        "Nintendo Switch Standard Console Complete",
    ]
    for title in valid_titles:
        assert listing_matches_product(title, product) is True, title


def test_standard_switch_still_rejects_other_models_and_incomplete_units():
    product = match_product("Nintendo Switch Standard", category="consoles").product
    rejected_titles = [
        "Nintendo Switch OLED Console Complete",
        "Nintendo Switch Lite Console Yellow",
        "Nintendo Switch 2 Console",
        "Nintendo Switch V2 Tablet Only",
        "Nintendo Switch Dock Only",
        "Nintendo Switch Joy-Con Only",
    ]
    for title in rejected_titles:
        assert listing_matches_product(title, product) is False, title
