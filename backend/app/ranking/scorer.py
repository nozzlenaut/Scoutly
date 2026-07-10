from app.models.listing import Listing

BAD_TITLE_WORDS = [
    "broken",
    "for parts",
    "parts only",
    "repair",
    "no display",
    "laptop",
]


def is_bad_listing(listing: Listing) -> bool:
    title = listing.title.lower()
    return any(word in title for word in BAD_TITLE_WORDS)


def score_listing(listing: Listing) -> float:
    """Higher is better. Simple Sprint 1 scoring before real marketplace data."""
    if is_bad_listing(listing):
        return 0

    price_score = max(0, 300 - listing.total_price)
    seller_score = (listing.seller_rating or 90) * 0.5
    condition_bonus = 15 if "used" in listing.condition.lower() else 5
    shipping_bonus = 10 if listing.shipping == 0 else 0

    return round(price_score + seller_score + condition_bonus + shipping_bonus, 2)


def best_listing(listings: list[Listing]) -> Listing | None:
    valid_listings = [listing for listing in listings if not is_bad_listing(listing)]
    if not valid_listings:
        return None

    for listing in valid_listings:
        listing.score = score_listing(listing)

    return max(valid_listings, key=lambda item: item.score)
