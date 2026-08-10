from app.catalog.ai_console_beta import match_ai_console_beta_product
from app.catalog.catalog import listing_matches_product
from app.models.listing import Listing
from app.services.search_service import best_auction_listings


def _listing(title: str, item_id: str) -> Listing:
    return Listing(
        provider="eBay",
        title=title,
        price=49.99,
        shipping=0,
        total_price=49.99,
        condition="Used",
        seller_rating=99.5,
        seller_feedback_score=500,
        url=f"https://www.ebay.com/itm/{item_id}",
    )


def test_wii_beta_rejects_spaced_and_compact_wii_u_titles():
    match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert match is not None

    assert not listing_matches_product(
        "Nintendo Wii U 32GB Black Console System Tested Working",
        match.product,
    )
    assert not listing_matches_product(
        "Nintendo WiiU 32GB Black Console System Tested Working",
        match.product,
    )


def test_wii_u_cannot_survive_auction_shortlist_before_ai_review():
    match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert match is not None

    wii_u = _listing("Nintendo WiiU 32GB Black Console System Tested Working", "9001")
    wii = _listing("Nintendo Wii White Console System RVL-001 Tested Working", "9002")

    results = best_auction_listings(
        [wii_u, wii],
        match.product,
        max_hours=24,
        limit=6,
    )

    assert results == [wii]
