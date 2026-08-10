import asyncio

import app.api.search as search_api
import app.services.ai_console_review as ai_console_review
from app.catalog.ai_console_beta import match_ai_console_beta_product
from app.catalog.catalog import listing_matches_product
from app.models.listing import Listing
from app.models.search import SearchDiagnostics
from app.services.ai_console_review import AIConsoleReviewResult, is_ai_console_review_target
from app.services.product_discovery import resolve_discoverable_product, suggest_discoverable_products


def _listing(title: str, item_id: str, price: float = 49.99) -> Listing:
    return Listing(
        provider="eBay",
        title=title,
        price=price,
        shipping=0,
        total_price=price,
        condition="Used",
        seller_rating=99.5,
        seller_feedback_score=500,
        url=f"https://www.ebay.com/itm/{item_id}",
    )


def test_wii_beta_resolves_without_stealing_wii_u():
    wii = resolve_discoverable_product("Nintendo Wii", "consoles")
    wii_u = resolve_discoverable_product("Nintendo Wii U", "consoles")

    assert wii is not None
    assert wii.product.id == "console-nintendo-wii"
    assert wii.product.metadata.get("ai_listing_review_beta") is True

    assert wii_u is not None
    assert wii_u.product.id == "console-nintendo-wii-u"


def test_wii_deterministic_filter_rejects_wii_u_before_ai_review():
    match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert match is not None

    assert listing_matches_product(
        "Nintendo Wii White Console System RVL-001 Tested Working",
        match.product,
    )
    assert not listing_matches_product(
        "Nintendo Wii U 32GB Black Console System Tested Working",
        match.product,
    )


def test_nintendo_64_is_discoverable_as_beta_product():
    resolved = resolve_discoverable_product("N64", "consoles")
    suggestions = suggest_discoverable_products("Nintendo 64", "consoles", limit=5)

    assert resolved is not None
    assert resolved.product.id == "console-nintendo-64"
    assert any(match.product.id == "console-nintendo-64" for match in suggestions)
    assert is_ai_console_review_target(resolved.product)


def test_switch_2_is_ai_review_target():
    resolved = resolve_discoverable_product("Nintendo Switch 2", "consoles")

    assert resolved is not None
    assert resolved.product.id == "console-nintendo-switch-2"
    assert is_ai_console_review_target(resolved.product)


def test_ai_review_fails_open_without_credentials(monkeypatch):
    product_match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert product_match is not None
    listing = _listing("Nintendo Wii Console System Tested Working", "1001")

    monkeypatch.setenv("AI_CONSOLE_REVIEW_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "")

    review = asyncio.run(
        ai_console_review.review_console_listings([listing], product_match.product)
    )

    assert review.applied is False
    assert review.kept == [listing]
    assert review.rejected == []


def test_ai_review_can_reject_wrong_generation_after_deterministic_pass(monkeypatch):
    product_match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert product_match is not None
    wrong_generation = _listing("Nintendo Wii U Console System", "2001")
    good = _listing("Nintendo Wii Console System Tested Working", "2002")

    async def fake_request_decisions(config, product, listings):
        assert product.id == "console-nintendo-wii"
        assert listings == [wrong_generation, good]
        return {
            0: (False, "wrong generation: Wii U"),
            1: (True, "target Wii console"),
        }

    monkeypatch.setenv("AI_CONSOLE_REVIEW_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(ai_console_review, "_request_decisions", fake_request_decisions)

    review = asyncio.run(
        ai_console_review.review_console_listings(
            [wrong_generation, good],
            product_match.product,
        )
    )

    assert review.applied is True
    assert review.kept == [good]
    assert review.rejected == [(wrong_generation, "wrong generation: Wii U")]


def test_api_post_review_updates_visible_results_and_diagnostics(monkeypatch):
    product_match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert product_match is not None
    bad_fixed = _listing("Nintendo Wii U Console System", "3001")
    good_fixed = _listing("Nintendo Wii Console System Tested Working", "3002")
    good_auction = _listing("Nintendo Wii Console Unit Working", "3003")

    async def fake_review(listings, product):
        assert product.id == "console-nintendo-wii"
        return AIConsoleReviewResult(
            kept=[good_fixed, good_auction],
            rejected=[(bad_fixed, "wrong generation")],
            applied=True,
        )

    monkeypatch.setattr(search_api, "review_console_listings", fake_review)
    diagnostics = SearchDiagnostics(
        fixed_price_candidates=5,
        fixed_price_filtered=2,
        fixed_price_eligible=3,
        auction_candidates=2,
        auction_filtered=1,
        auction_eligible=1,
    )

    reviewed_fixed, reviewed_auctions = asyncio.run(
        search_api._apply_ai_console_beta_review(
            product_match,
            [bad_fixed, good_fixed],
            [good_auction],
            diagnostics,
        )
    )

    assert reviewed_fixed == [good_fixed]
    assert reviewed_auctions == [good_auction]
    assert diagnostics.fixed_price_filtered == 3
    assert diagnostics.fixed_price_eligible == 2
    assert diagnostics.fixed_price_rejection_reasons["ai console review"] == 1
