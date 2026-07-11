from app.models.listing import Listing
from app.ranking.scorer import is_bad_listing


def test_rejects_for_parts_condition():
    listing = Listing(
        provider="eBay",
        title="Sony Alpha A7 III Camera Body",
        price=500,
        shipping=0,
        total_price=500,
        condition="For parts or not working",
        url="https://example.com/item",
    )

    assert is_bad_listing(listing) is True
