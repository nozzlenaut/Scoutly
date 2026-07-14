import asyncio

from app.catalog.catalog import match_product
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
