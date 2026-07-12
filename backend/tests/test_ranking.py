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


def test_top_listings_returns_multiple_valid_options():
    from app.catalog.catalog import match_product
    from app.ranking.scorer import top_listings

    product = match_product("RTX 3060 12GB", category="gpus").product
    listings = [
        Listing(provider="eBay", title="EVGA RTX 3060 12GB Graphics Card", price=190, shipping=0, total_price=190, condition="Used", url="https://example.com/1"),
        Listing(provider="eBay", title="ASUS RTX 3060 12GB Graphics Card", price=195, shipping=0, total_price=195, condition="Used", url="https://example.com/2"),
        Listing(provider="eBay", title="MSI RTX 3060 12GB Graphics Card", price=200, shipping=0, total_price=200, condition="Used", url="https://example.com/3"),
        Listing(provider="eBay", title="RTX 3060 12GB Box Only", price=20, shipping=0, total_price=20, condition="Used", url="https://example.com/4"),
    ]

    top = top_listings(listings, product, limit=3)
    assert len(top) == 3
    assert all("Box Only" not in item.title for item in top)
