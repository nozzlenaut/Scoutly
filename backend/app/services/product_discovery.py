from __future__ import annotations

from app.catalog.catalog import match_product, normalize_category, suggest_products
from app.models.product import ProductMatch
from app.services.keh_feed import match_keh_camera_product, suggest_keh_camera_products


def resolve_discoverable_product(query: str, category: str | None) -> ProductMatch | None:
    catalog_match = match_product(query, category)
    if normalize_category(category) != "cameras":
        return catalog_match

    keh_match = match_keh_camera_product(query)
    if keh_match is None:
        return catalog_match
    if catalog_match is None or keh_match.product.id == catalog_match.product.id:
        return keh_match
    # A high-confidence KEH-native identity may beat a weaker catalog guess,
    # but an exact catalog identity must not be displaced by a related model
    # such as R6 versus R6 Mark II.
    if (
        keh_match.product.metadata.get("provider_scope") == "keh"
        and keh_match.confidence >= 0.92
        and keh_match.confidence >= catalog_match.confidence + 0.03
    ):
        return keh_match
    return catalog_match


def suggest_discoverable_products(
    query: str,
    category: str | None,
    limit: int = 8,
) -> list[ProductMatch]:
    limit = max(1, min(limit, 20))
    matches = list(suggest_products(query, category, limit=limit))
    if normalize_category(category) != "cameras":
        return matches

    by_product_id = {match.product.id: match for match in matches}
    for keh_match in suggest_keh_camera_products(query, limit=limit):
        existing = by_product_id.get(keh_match.product.id)
        if existing is None:
            by_product_id[keh_match.product.id] = keh_match
            continue
        # Prefer the KEH-enriched copy of a catalog product so autocomplete can
        # explain that both providers are available without changing identity.
        by_product_id[keh_match.product.id] = ProductMatch(
            product=keh_match.product,
            confidence=max(existing.confidence, keh_match.confidence),
            matched_alias=existing.matched_alias or keh_match.matched_alias,
        )

    return sorted(
        by_product_id.values(),
        key=lambda match: (-match.confidence, match.product.display_name.lower()),
    )[:limit]
