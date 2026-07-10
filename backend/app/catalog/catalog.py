import json
from functools import lru_cache
from pathlib import Path

from app.catalog.normalizer import has_term, normalize_text
from app.models.product import Product, ProductMatch

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "gpu_catalog.json"


@lru_cache(maxsize=1)
def load_products() -> list[Product]:
    with CATALOG_PATH.open("r", encoding="utf-8") as file:
        raw_products = json.load(file)
    return [Product(**item) for item in raw_products if item.get("active", True)]


def list_products(category: str | None = None) -> list[Product]:
    products = load_products()
    if category is None:
        return products
    return [product for product in products if product.category.lower() == category.lower()]


def match_product(query: str) -> ProductMatch | None:
    normalized_query = normalize_text(query)
    best_match: ProductMatch | None = None

    for product in load_products():
        candidates = [product.display_name, product.model, *product.aliases]
        for candidate in candidates:
            normalized_candidate = normalize_text(candidate)
            if not normalized_candidate:
                continue

            confidence = 0.0
            if normalized_query == normalized_candidate:
                confidence = 1.0
            elif normalized_candidate in normalized_query or normalized_query in normalized_candidate:
                confidence = 0.86
            else:
                required_hits = sum(1 for term in product.required_terms if has_term(normalized_query, term))
                if product.required_terms and required_hits == len(product.required_terms):
                    confidence = 0.78
                elif required_hits > 0:
                    confidence = 0.45

            if confidence > 0 and (best_match is None or confidence > best_match.confidence):
                best_match = ProductMatch(product=product, confidence=confidence, matched_alias=candidate)

    if best_match is None or best_match.confidence < 0.7:
        return None

    return best_match


def listing_matches_product(title: str, product: Product) -> bool:
    for excluded_term in product.excluded_terms:
        if has_term(title, excluded_term):
            return False

    return all(has_term(title, required_term) for required_term in product.required_terms)
