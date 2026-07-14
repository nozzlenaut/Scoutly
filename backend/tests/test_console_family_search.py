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


def test_direct_console_search_uses_one_core_model_query(monkeypatch):
    provider = RecordingConsoleProvider()
    monkeypatch.setitem(search_service.PROVIDERS, "ebay", provider)

    resolved, results, auctions, diagnostics = asyncio.run(
        search_service.search_best_deals_with_auctions(
            "Xbox Series X 1TB",
            ["ebay"],
            "consoles",
            include_auctions=False,
        )
    )

    assert resolved is not None
    assert resolved.product.id == "console-xbox-series-x"
    assert resolved.product.metadata.get("variants_grouped") is True
    assert len(provider.calls) == 1
    assert provider.calls[0][0] == "Xbox Series X console"
    assert [listing.title for listing in results] == [
        "Microsoft Xbox Series X 1TB Console Black Tested"
    ]
    assert auctions == []
    assert diagnostics.fixed_price_candidates == 1


def test_console_autocomplete_returns_core_model_choices_without_variant_duplicates():
    xbox = suggest_products("Xbox Series", category="consoles", limit=8)
    playstation = suggest_products("PlayStation 5", category="consoles", limit=8)

    xbox_ids = {match.product.id for match in xbox}
    playstation_ids = {match.product.id for match in playstation}
    assert {"console-xbox-series-s", "console-xbox-series-x"}.issubset(xbox_ids)
    assert "console-xbox-series-s-512gb" not in xbox_ids
    assert "console-xbox-series-s-1tb" not in xbox_ids
    assert {
        "console-playstation-5",
        "console-playstation-5-slim",
        "console-playstation-5-pro",
    }.issubset(playstation_ids)


def test_storage_color_and_drive_queries_resolve_to_the_same_core_model():
    series_s_queries = [
        "Xbox Series S",
        "Xbox Series S 512GB",
        "Xbox Series S Carbon Black 1TB",
    ]
    ps5_slim_queries = [
        "PS5 Slim",
        "PS5 Slim Disc Edition",
        "PS5 Slim Digital Edition 1TB",
    ]

    assert {
        match_product(query, category="consoles").product.id
        for query in series_s_queries
    } == {"console-xbox-series-s"}
    assert {
        match_product(query, category="consoles").product.id
        for query in ps5_slim_queries
    } == {"console-playstation-5-slim"}


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
                    title="Nintendo Switch V2 HAC-001(-01) Complete System Neon Tested",
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
                    title="Nintendo Switch Console HAC-001 Gray Complete System Tested",
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
        assert match.product.id == "console-nintendo-switch", alias
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
    assert resolved.product.id == "console-nintendo-switch"
    assert [call[0] for call in provider.calls] == [
        "Nintendo Switch V1 console",
        "Nintendo Switch V2 console",
        "Nintendo Switch HAC-001 console",
        "Nintendo Switch HAC-001(-01) console",
        "Nintendo Switch Standard console",
        "Nintendo Switch console",
    ]
    assert [listing.title for listing in results] == [
        "Nintendo Switch Console HAC-001 Gray Complete System Tested",
        "Nintendo Switch V2 HAC-001(-01) Complete System Neon Tested",
    ]
    assert auctions == []
    assert diagnostics.fixed_price_candidates == 2


def test_original_switch_accepts_v1_v2_hac_and_rejects_other_models():
    product = match_product("Nintendo Switch V1", category="consoles").product
    valid_titles = [
        "Nintendo Switch V1 Complete System Tested",
        "Nintendo Switch V2 Console with Joy-Con and Dock Tested",
        "Nintendo Switch Console HAC-001 Gray Complete System Tested",
        "Nintendo Switch HAC-001(-01) Console Bundle Neon Tested",
        "Nintendo Switch Standard Console Complete",
    ]
    rejected_titles = [
        "Nintendo Switch OLED Console Complete",
        "Nintendo Switch Lite Console Yellow",
        "Nintendo Switch 2 Console",
        "Nintendo Switch HAC-001 Video Game Console Tested Working W/ Screen Protector",
        "Nintendo Switch V1 Console Tested",
        "Nintendo Switch V2 Tablet Only",
        "Nintendo Switch Dock Only",
        "Nintendo Switch Joy-Con Only",
    ]
    for title in valid_titles:
        assert listing_matches_product(title, product) is True, title
    for title in rejected_titles:
        assert listing_matches_product(title, product) is False, title


def test_console_qa_problem_titles_are_rejected_without_blocking_real_hardware():
    problem_cases = [
        (
            "PS5 Pro",
            "Disc Drive for PS5 Pro Digital Edition Console",
        ),
        (
            "PS4",
            "Sony PlayStation 4 PS4 Base Shell Replacement Housing Black",
        ),
        (
            "PS4",
            "PS4 Mid-Frame Cooling Fan Heat Sink Replacement Part",
        ),
        (
            "PS4",
            "Rust Console Edition PS4 Video Game",
        ),
        (
            "Xbox Series S",
            "Microsoft Xbox 360 S Series S Console 250GB Black",
        ),
        (
            "Nintendo Switch",
            "Nintendo Switch HEG-001 Console White Tested",
        ),
        (
            "Nintendo Switch",
            "Nintendo Switch Dock with Charger OEM HAC-007",
        ),
        (
            "Nintendo Switch Lite",
            "Nintendo Licensed Slim Hard Case Collection for Switch Lite",
        ),
        (
            "Nintendo 3DS XL",
            "Nintendo New 3DS XL Box & Tray and Manuals Only",
        ),
    ]

    for query, title in problem_cases:
        product = match_product(query, category="consoles").product
        assert is_bad_listing(
            Listing(
                provider="eBay",
                title=title,
                price=40,
                shipping=0,
                total_price=40,
                condition="Used",
                seller_rating=99.5,
                seller_feedback_score=200,
                url=f"https://example.com/{abs(hash((query, title)))}",
            ),
            product,
        ) is True, title

    valid_cases = [
        ("PS5 Pro", "Sony PlayStation 5 Pro PS5 Pro 2TB Console Tested"),
        ("PS5 Pro", "Sony PlayStation 5 Pro 2TB Console with Disc Drive Tested"),
        ("PS4", "Sony PlayStation 4 PS4 500GB Console Tested Working"),
        ("Xbox Series S", "Microsoft Xbox Series S 512GB Console Tested"),
        ("Nintendo Switch", "Nintendo Switch HAC-001 Console System Complete"),
        ("Nintendo Switch Lite", "Nintendo Switch Lite Handheld Console Tested"),
        ("Nintendo 3DS XL", "Nintendo New 3DS XL Handheld System Tested"),
    ]
    for query, title in valid_cases:
        product = match_product(query, category="consoles").product
        assert listing_matches_product(title, product) is True, title


class RankingConsoleProvider:
    name = "eBay"

    async def search(
        self,
        query: str,
        category: str | None = None,
        buying_option: str = "fixed_price",
    ) -> list[Listing]:
        if buying_option == "auction":
            return []
        return [
            Listing(
                provider="eBay",
                title="Sony PlayStation 5 Pro PS5 Pro 2TB Console READ DESCRIPTION",
                price=420,
                shipping=0,
                total_price=420,
                condition="Used",
                seller_rating=99.8,
                seller_feedback_score=500,
                url="https://www.ebay.com/itm/100000000020",
            ),
            Listing(
                provider="eBay",
                title="Sony PlayStation 5 Pro PS5 Pro 2TB Console Tested Working",
                price=465,
                shipping=0,
                total_price=465,
                condition="Used",
                seller_rating=99.8,
                seller_feedback_score=500,
                url="https://www.ebay.com/itm/100000000021",
            ),
            Listing(
                provider="eBay",
                title="Disc Drive for PS5 Pro Digital Edition Console",
                price=79,
                shipping=0,
                total_price=79,
                condition="Used",
                seller_rating=99.8,
                seller_feedback_score=500,
                url="https://www.ebay.com/itm/100000000022",
            ),
        ]


def test_console_search_preserves_quality_ranking_and_exposes_filter_reasons(monkeypatch):
    provider = RankingConsoleProvider()
    monkeypatch.setitem(search_service.PROVIDERS, "ebay", provider)

    resolved, results, auctions, diagnostics = asyncio.run(
        search_service.search_best_deals_with_auctions(
            "PS5 Pro",
            ["ebay"],
            "consoles",
            include_auctions=False,
        )
    )

    assert resolved is not None
    assert results[0].title.endswith("Tested Working")
    assert results[1].title.endswith("READ DESCRIPTION")
    assert all("Disc Drive for" not in listing.title for listing in results)
    assert diagnostics.fixed_price_candidates == 3
    assert diagnostics.fixed_price_eligible == 2
    assert diagnostics.fixed_price_filtered == 1
    assert diagnostics.fixed_price_rejection_reasons["console accessory/part/incomplete"] == 1
    assert auctions == []


class DuplicateTitleSwitchProvider:
    name = "eBay"

    def __init__(self) -> None:
        self.call_number = 0

    async def search(
        self,
        query: str,
        category: str | None = None,
        buying_option: str = "fixed_price",
    ) -> list[Listing]:
        if buying_option == "auction":
            return []
        self.call_number += 1
        offset = self.call_number * 10
        return [
            Listing(
                provider="eBay",
                title="Nintendo Switch HAC-001 Complete System Tested Working",
                price=170 + self.call_number,
                shipping=0,
                total_price=170 + self.call_number,
                condition="Used",
                seller_rating=99.8,
                seller_feedback_score=500,
                url=f"https://www.ebay.com/itm/{200000000000 + offset}",
            ),
            Listing(
                provider="eBay",
                title="Nintendo Switch V2 Console with Joy-Con and Dock Tested",
                price=180 + self.call_number,
                shipping=0,
                total_price=180 + self.call_number,
                condition="Used",
                seller_rating=99.7,
                seller_feedback_score=400,
                url=f"https://www.ebay.com/itm/{200000000001 + offset}",
            ),
        ]


def test_console_top_three_collapses_identical_titles_across_marketplace_items(monkeypatch):
    provider = DuplicateTitleSwitchProvider()
    monkeypatch.setitem(search_service.PROVIDERS, "ebay", provider)

    resolved, results, auctions, diagnostics = asyncio.run(
        search_service.search_best_deals_with_auctions(
            "Nintendo Switch",
            ["ebay"],
            "consoles",
            include_auctions=False,
        )
    )

    assert resolved is not None
    assert [listing.title for listing in results] == [
        "Nintendo Switch HAC-001 Complete System Tested Working",
        "Nintendo Switch V2 Console with Joy-Con and Dock Tested",
    ]
    assert diagnostics.fixed_price_duplicates_removed >= 10
    assert auctions == []
