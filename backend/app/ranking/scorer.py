from app.catalog.catalog import listing_matches_product
from app.models.listing import Listing
from app.models.product import Product

BAD_TITLE_WORDS = [
    "broken",
    "for parts",
    "parts only",
    "repair",
    "no display",
    "laptop",
    "mobile",
]


def is_bad_listing(listing: Listing, product: Product | None = None) -> bool:
    title = listing.title.lower()
    if any(word in title for word in BAD_TITLE_WORDS):
        return True

    if product is not None and not listing_matches_product(listing.title, product):
        return True

    return False


def score_listing(listing: Listing, product: Product | None = None) -> float:
    """Higher is better. Price matters, but junk listings should never win."""
    if is_bad_listing(listing, product):
        return 0

    price_score = max(0, 500 - listing.total_price)
    seller_score = (listing.seller_rating or 90) * 0.45
    condition_bonus = 15 if "used" in listing.condition.lower() else 5
    shipping_bonus = 10 if listing.shipping == 0 else 0
    product_match_bonus = 35 if product is not None else 0

    return round(price_score + seller_score + condition_bonus + shipping_bonus + product_match_bonus, 2)


def best_listing(listings: list[Listing], product: Product | None = None) -> Listing | None:
    valid_listings = [listing for listing in listings if not is_bad_listing(listing, product)]
    if not valid_listings:
        return None

    for listing in valid_listings:
        listing.score = score_listing(listing, product)

    return max(valid_listings, key=lambda item: item.score)
