import json
from functools import lru_cache
from pathlib import Path

from app.catalog.normalizer import compact_text, has_term, normalize_text
from app.models.product import Product, ProductMatch

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "product_catalog.json"
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

    return all(has_term(title, required_term) for required_term in product.required_terms)
