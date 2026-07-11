import json
from functools import lru_cache
from pathlib import Path

from app.catalog.normalizer import compact_text, has_term, normalize_text
from app.models.product import Product, ProductMatch

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "product_catalog.json"

CAMERA_PART_ACCESSORY_TERMS = [
    "adapter",
    "battery door",
    "button",
    "cable",
    "circuit board",
    "contact flex",
    "cover",
    "dial",
    "display screen",
    "door cover",
    "dummy",
    "flex",
    "flex cable",
    "hot shoe",
    "lcd",
    "lens bayonet",
    "lens mount",
    "lens mount contact",
    "main board",
    "mount ring",
    "motherboard",
    "pcb",
    "port cover",
    "repair part",
    "replacement",
    "replacement part",
    "ribbon",
    "screen repair",
    "sensor cleaning",
    "spare part",
    "strap lug",
    "top cover",
    "viewfinder",
]


def _has_any_term(text: str, terms: list[str]) -> bool:
    return any(has_term(text, term) for term in terms)


def _looks_like_camera_body_accessory(title: str) -> bool:
    normalized = normalize_text(title)
    if _has_any_term(title, CAMERA_PART_ACCESSORY_TERMS):
        return True

    # Marketplace accessory listings often start with "for Sony/Canon/etc."
    # Legitimate camera bodies usually start with the product name itself.
    # Only use the prefix as a reject signal when the title also has accessory
    # words so we do not reject a rare legitimate title just because it says "for".
    accessory_words = ["bayonet", "mount", "ring", "contact", "part", "repair", "cable"]
    return normalized.startswith("for ") and _has_any_term(title, accessory_words)


def _has_camera_model_alias(title: str, product: Product) -> bool:
    """Require a strong camera model clue so A7 IV does not match A7R IV parts.

    Generic required terms like sony + a7 + iv are too loose for camera bodies
    because eBay has many repair-part listings such as A7R IV flex cables.
    For camera bodies, require one of our exact model aliases after compact
    normalization.
    """

    title_compact = compact_text(title)
    title_has_brand = has_term(title, product.brand)

    candidates = [product.display_name, product.model, *product.aliases]
    for candidate in candidates:
        candidate_compact = compact_text(candidate)
        if not candidate_compact:
            continue

        # Short model aliases like "a74" are okay when the title also includes
        # the brand. Longer aliases are safe enough on their own.
        if candidate_compact in title_compact and (len(candidate_compact) >= 4 or title_has_brand):
            return True

    return False

CATEGORY_ALIASES = {
    "gpu": "gpus",
    "graphics": "gpus",
    "graphics-cards": "gpus",
    "camera": "cameras",
    "camera-body": "cameras",
    "camera-bodies": "cameras",
    "lens": "lenses",
}


def normalize_category(category: str | None) -> str | None:
    if category is None:
        return None
    cleaned = category.strip().lower()
    return CATEGORY_ALIASES.get(cleaned, cleaned)


@lru_cache(maxsize=1)
def load_products() -> list[Product]:
    with CATALOG_PATH.open("r", encoding="utf-8") as file:
        raw_products = json.load(file)
    return [Product(**item) for item in raw_products if item.get("active", True)]


def list_products(category: str | None = None) -> list[Product]:
    products = load_products()
    normalized_category = normalize_category(category)
    if normalized_category is None:
        return products
    return [product for product in products if product.category.lower() == normalized_category]


def _score_product_candidate(query: str, product: Product) -> ProductMatch | None:
    normalized_query = normalize_text(query)
    compact_query = compact_text(query)
    best_confidence = 0.0
    best_alias: str | None = None

    candidates = [product.display_name, product.model, *product.aliases]
    for candidate in candidates:
        normalized_candidate = normalize_text(candidate)
        compact_candidate = compact_text(candidate)
        if not normalized_candidate:
            continue

        confidence = 0.0
        if normalized_query == normalized_candidate or compact_query == compact_candidate:
            confidence = 1.0
        elif normalized_candidate.startswith(normalized_query) or compact_candidate.startswith(compact_query):
            confidence = 0.94
        elif normalized_query in normalized_candidate or compact_query in compact_candidate:
            confidence = 0.88
        elif normalized_candidate in normalized_query or compact_candidate in compact_query:
            confidence = 0.86
        else:
            required_hits = sum(1 for term in product.required_terms if has_term(normalized_query, term))
            if product.required_terms and required_hits == len(product.required_terms):
                confidence = 0.82
            elif required_hits >= 2:
                confidence = 0.62
            elif required_hits > 0:
                confidence = 0.44

        # Exact variant/mount/focal clues should help, without making them mandatory.
        if product.variant and has_term(normalized_query, product.variant):
            confidence = min(1.0, confidence + 0.04)

        # For GPUs, prefer the base card when the user types only the number.
        modifiers = ["ti", "super", "xtx", "xt", "gre"]
        product_text = normalize_text(f"{product.model} {product.variant or ''}")
        if product.category == "gpus" and any(
            has_term(product_text, modifier) and not has_term(normalized_query, modifier) for modifier in modifiers
        ):
            confidence = max(0.0, confidence - 0.07)

        if confidence > best_confidence:
            best_confidence = confidence
            best_alias = candidate

    if best_confidence <= 0:
        return None
    return ProductMatch(product=product, confidence=round(best_confidence, 2), matched_alias=best_alias)


def match_product(query: str, category: str | None = None) -> ProductMatch | None:
    matches = suggest_products(query, category=category, limit=1)
    if not matches:
        return None
    best_match = matches[0]
    if best_match.confidence < 0.7:
        return None
    return best_match


def suggest_products(query: str, category: str | None = None, limit: int = 8) -> list[ProductMatch]:
    if len(query.strip()) < 2:
        return []

    matches: list[ProductMatch] = []
    for product in list_products(category):
        match = _score_product_candidate(query, product)
        if match is not None and match.confidence >= 0.42:
            matches.append(match)

    matches.sort(
        key=lambda match: (
            match.confidence,
            match.product.category,
            match.product.display_name,
        ),
        reverse=True,
    )
    return matches[:limit]


def listing_matches_product(title: str, product: Product) -> bool:
    for excluded_term in product.excluded_terms:
        if has_term(title, excluded_term):
            return False

    if product.category == "cameras" and product.product_type == "camera_body":
        if _looks_like_camera_body_accessory(title):
            return False
        return _has_camera_model_alias(title, product)

    if product.category == "cameras" and _has_any_term(title, CAMERA_PART_ACCESSORY_TERMS):
        return False

    return all(has_term(title, required_term) for required_term in product.required_terms)
