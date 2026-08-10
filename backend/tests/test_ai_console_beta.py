import asyncio

import app.services.ai_console_rate_limit as ai_rate_limit
import app.services.ai_console_review as ai_console_review
import app.services.search_service as search_service
from app.catalog.ai_console_beta import match_ai_console_beta_product
from app.catalog.catalog import listing_matches_product
from app.models.listing import Listing
from app.models.search import SearchDiagnostics
from app.services.ai_console_rate_limit import AIRateLimitDecision
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
    assert listing_matches_product(
        "Nintendo N64 Nintendo 64 Console System Tested Working",
        resolved.product,
    )


def test_switch_2_is_ai_review_target():
    resolved = resolve_discoverable_product("Nintendo Switch 2", "consoles")

    assert resolved is not None
    assert resolved.product.id == "console-nintendo-switch-2"
    assert is_ai_console_review_target(resolved.product)


def test_ai_review_fails_open_without_credentials(monkeypatch):
    product_match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert product_match is not None
    listing = _listing("Nintendo Wii Console System Tested Working", "1001")

    monkeypatch.setattr(ai_console_review, "ai_console_review_enabled", lambda: True)
    monkeypatch.setenv("OPENAI_API_KEY", "")

    review = asyncio.run(
        ai_console_review.review_console_listings([listing], product_match.product)
    )

    assert review.applied is False
    assert review.kept == [listing]
    assert review.rejected == []
    assert review.skipped_reason == "disabled_or_unconfigured"


def test_ai_review_can_reject_wrong_generation_after_guardrails(monkeypatch):
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

    monkeypatch.setattr(ai_console_review, "ai_console_review_enabled", lambda: True)
    monkeypatch.setattr(
        ai_console_review,
        "reserve_ai_console_review_call",
        lambda: AIRateLimitDecision(True, None, 20, 300),
    )
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


def test_ai_shortlist_backfills_to_three_after_rejections(monkeypatch):
    product_match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert product_match is not None
    listings = [
        _listing(f"Nintendo Wii Console System Tested Working #{index}", str(3000 + index), 20 + index)
        for index in range(1, 6)
    ]

    async def fake_review(candidates, product):
        assert product.id == "console-nintendo-wii"
        assert candidates == listings
        return AIConsoleReviewResult(
            kept=listings[2:],
            rejected=[
                (listings[0], "wrong item"),
                (listings[1], "ambiguous listing"),
            ],
            applied=True,
        )

    monkeypatch.setattr(search_service, "review_console_listings", fake_review)
    diagnostics = SearchDiagnostics(fixed_price_candidates=20, fixed_price_eligible=5)

    assert search_service._candidate_limits(product_match.product) == (12, 6)
    reviewed_fixed, reviewed_auctions = asyncio.run(
        search_service._review_ai_console_shortlists(
            product_match.product,
            listings,
            [],
            diagnostics,
        )
    )
    final_fixed, _duplicates = search_service._cheapest_fixed_listings_with_stats(
        reviewed_fixed,
        limit=3,
    )

    assert reviewed_auctions == []
    assert final_fixed == listings[2:5]
    assert diagnostics.ai_review_applied is True
    assert diagnostics.ai_review_rejected == 2
    assert diagnostics.fixed_price_rejection_reasons["ai console review"] == 2


def test_ai_rate_limit_blocks_after_configured_minute_cap(monkeypatch):
    monkeypatch.setattr(ai_rate_limit, "database_configured", lambda: False)
    monkeypatch.setenv("AI_CONSOLE_REVIEW_MAX_PER_MINUTE", "2")
    monkeypatch.setenv("AI_CONSOLE_REVIEW_MAX_PER_DAY", "100")
    ai_rate_limit._MEMORY_BUCKETS.clear()

    first = ai_rate_limit.reserve_ai_console_review_call()
    second = ai_rate_limit.reserve_ai_console_review_call()
    third = ai_rate_limit.reserve_ai_console_review_call()

    assert first.allowed is True
    assert second.allowed is True
    assert third.allowed is False
    assert third.reason == "minute_limit"
