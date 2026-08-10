from __future__ import annotations

from app.catalog.normalizer import compact_text, normalize_text
from app.models.product import Product, ProductMatch


_BASE_EXCLUDED_TERMS = [
    "account only",
    "as is",
    "as-is",
    "battery only",
    "box only",
    "broken",
    "case only",
    "controller only",
    "controllers only",
    "for parts",
    "manual only",
    "not working",
    "parts only",
    "power supply",
    "read description",
    "repair",
    "shell only",
    "untested",
]


AI_CONSOLE_BETA_PRODUCTS = (
    Product(
        id="console-nintendo-64",
        category="consoles",
        category_label="Consoles",
        product_type="game_console",
        brand="Nintendo",
        model="64",
        aliases=[
            "Nintendo 64",
            "Nintendo 64 Console",
            "N64",
            "N64 Console",
        ],
        required_terms=[],
        excluded_terms=[
            *_BASE_EXCLUDED_TERMS,
            "cartridge only",
            "game only",
        ],
        metadata={
            "family": "nintendo-64",
            "ai_listing_review_beta": True,
        },
    ),
    Product(
        id="console-nintendo-wii",
        category="consoles",
        category_label="Consoles",
        product_type="game_console",
        brand="Nintendo",
        model="Wii",
        aliases=[
            "Nintendo Wii",
            "Nintendo Wii Console",
            "Wii Console",
        ],
        required_terms=["wii"],
        excluded_terms=[
            *_BASE_EXCLUDED_TERMS,
            "balance board only",
            "game only",
            "remote only",
            "sensor bar only",
            "wii u",
        ],
        metadata={
            "family": "nintendo-wii",
            "ai_listing_review_beta": True,
        },
    ),
)


def _normalized_category(category: str | None) -> str | None:
    if category is None:
        return None
    value = category.strip().lower()
    return "consoles" if value in {"console", "consoles", "nintendo"} else value


def _match_score(query: str, product: Product) -> float:
    normalized = normalize_text(query, strip_filler=False)
    compact = compact_text(query, strip_filler=False)

    candidates = [product.display_name, product.model, *product.aliases]
    for candidate in candidates:
        candidate_normalized = normalize_text(candidate, strip_filler=False)
        candidate_compact = compact_text(candidate, strip_filler=False)
        if normalized == candidate_normalized or compact == candidate_compact:
            return 1.0

    if product.id == "console-nintendo-64":
        if "nintendo64" in compact or compact.startswith("n64"):
            return 0.94
    elif product.id == "console-nintendo-wii":
        # Wii U is a separate console and must never resolve to the Wii beta.
        if "wiiu" in compact:
            return 0.0
        if compact in {"wii", "nintendowii", "wiiconsole", "nintendowiiconsole"}:
            return 1.0
        if "nintendowii" in compact:
            return 0.94

    return 0.0


def match_ai_console_beta_product(query: str, category: str | None) -> ProductMatch | None:
    if _normalized_category(category) != "consoles":
        return None

    matches = [
        (score, product)
        for product in AI_CONSOLE_BETA_PRODUCTS
        if (score := _match_score(query, product)) > 0
    ]
    if not matches:
        return None
    score, product = max(matches, key=lambda item: item[0])
    return ProductMatch(product=product, confidence=score, matched_alias=product.display_name)


def suggest_ai_console_beta_products(
    query: str,
    category: str | None,
    limit: int = 8,
) -> list[ProductMatch]:
    if _normalized_category(category) != "consoles" or len(query.strip()) < 2:
        return []

    matches: list[ProductMatch] = []
    query_compact = compact_text(query, strip_filler=False)
    for product in AI_CONSOLE_BETA_PRODUCTS:
        score = _match_score(query, product)
        if score <= 0:
            aliases = [product.display_name, *product.aliases]
            if any(query_compact in compact_text(alias, strip_filler=False) for alias in aliases):
                score = 0.82
        if score > 0:
            matches.append(
                ProductMatch(product=product, confidence=score, matched_alias=product.display_name)
            )

    return sorted(matches, key=lambda match: (-match.confidence, match.product.display_name))[: max(1, limit)]
