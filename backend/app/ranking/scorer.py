from app.catalog.catalog import GLOBAL_BAD_LISTING_TERMS, listing_matches_product
from app.catalog.normalizer import has_term
from app.models.listing import Listing
from app.models.product import Product
from app.services.filter_rules import manual_filter_rejection_reasons

BAD_TITLE_WORDS = [
    *GLOBAL_BAD_LISTING_TERMS,
    "laptop",
    "mobile",
    "no display",
]

BAD_CONDITION_WORDS = [
    "for parts",
    "not working",
    "parts only",
    "repair",
]


def rejection_reasons(listing: Listing, product: Product | None = None) -> list[str]:
    title = listing.title.lower()
    condition = listing.condition.lower()
    reasons: list[str] = []

    for word in BAD_TITLE_WORDS:
        if word in title:
            reasons.append(f"bad title term: {word}")
            break

    for word in BAD_CONDITION_WORDS:
        if word in condition:
            reasons.append(f"bad condition: {word}")
            break

    manual_reasons = manual_filter_rejection_reasons(listing.title, product)
    reasons.extend(manual_reasons)

    if product is not None and not listing_matches_product(listing.title, product):
        reasons.append("catalog/product match rejected")

    return reasons


def is_bad_listing(listing: Listing, product: Product | None = None) -> bool:
    return bool(rejection_reasons(listing, product))


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


def top_listings(listings: list[Listing], product: Product | None = None, limit: int = 3) -> list[Listing]:
    valid_listings = [listing for listing in listings if not is_bad_listing(listing, product)]
    if not valid_listings:
        return []

    for listing in valid_listings:
        listing.score = score_listing(listing, product)

    deduped: list[Listing] = []
    seen: set[str] = set()
    for listing in sorted(valid_listings, key=lambda item: item.score, reverse=True):
        key = str(listing.url).split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(listing)
        if len(deduped) >= max(1, limit):
            break

    return deduped


def best_listing(listings: list[Listing], product: Product | None = None) -> Listing | None:
    top = top_listings(listings, product, limit=1)
    return top[0] if top else None
