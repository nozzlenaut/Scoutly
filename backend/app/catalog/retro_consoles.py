from __future__ import annotations

from app.models.product import Product


COMMON_RETRO_CONSOLE_EXCLUSIONS = [
    "box only",
    "broken",
    "case only",
    "controller only",
    "controllers only",
    "empty box",
    "for parts",
    "game only",
    "games only",
    "manual only",
    "not working",
    "parts only",
    "repair",
    "replacement",
    "shell only",
    "untested",
]


def _retro_console(
    *,
    product_id: str,
    brand: str,
    model: str,
    aliases: list[str],
    required_terms: list[str],
    provider_query: str,
    family: str,
    exclusions: list[str] | None = None,
) -> Product:
    return Product(
        id=product_id,
        category="consoles",
        category_label="Consoles",
        product_type="console",
        brand=brand,
        model=model,
        aliases=aliases,
        required_terms=required_terms,
        excluded_terms=[*COMMON_RETRO_CONSOLE_EXCLUSIONS, *(exclusions or [])],
        metadata={
            "family": family,
            "provider_query": provider_query,
            "ai_listing_review": True,
        },
        active=True,
    )


def retro_console_products() -> list[Product]:
    """Small, high-confidence older-console supplement for SEO and price tracking.

    These intentionally avoid Wii U for now. Older-console marketplace results
    are noisy, so every product in this supplement is also sent through the
    optional AI console listing review after deterministic filtering.
    """

    return [
        _retro_console(
            product_id="console-sony-playstation-2",
            brand="Sony",
            model="PlayStation 2",
            aliases=["Sony PlayStation 2", "PlayStation 2", "Sony PS2", "PS2"],
            required_terms=["playstation", "2"],
            provider_query="Sony PlayStation 2 console",
            family="sony-playstation-2",
            exclusions=["playstation 3", "playstation 4", "playstation 5", "ps3", "ps4", "ps5"],
        ),
        _retro_console(
            product_id="console-sony-playstation-3",
            brand="Sony",
            model="PlayStation 3",
            aliases=["Sony PlayStation 3", "PlayStation 3", "Sony PS3", "PS3"],
            required_terms=["playstation", "3"],
            provider_query="Sony PlayStation 3 console",
            family="sony-playstation-3",
            exclusions=["playstation 2", "playstation 4", "playstation 5", "ps2", "ps4", "ps5"],
        ),
        _retro_console(
            product_id="console-microsoft-xbox-360",
            brand="Microsoft",
            model="Xbox 360",
            aliases=["Microsoft Xbox 360", "Xbox 360"],
            required_terms=["xbox", "360"],
            provider_query="Xbox 360 console",
            family="microsoft-xbox-360",
            exclusions=["xbox one", "series x", "series s"],
        ),
        _retro_console(
            product_id="console-nintendo-gamecube",
            brand="Nintendo",
            model="GameCube",
            aliases=["Nintendo GameCube", "GameCube", "Nintendo Game Cube"],
            required_terms=["gamecube"],
            provider_query="Nintendo GameCube console",
            family="nintendo-gamecube",
        ),
        _retro_console(
            product_id="console-nintendo-wii",
            brand="Nintendo",
            model="Wii",
            aliases=["Nintendo Wii", "Wii console"],
            required_terms=["wii"],
            provider_query="Nintendo Wii console",
            family="nintendo-wii",
            exclusions=["wii u", "wiiu"],
        ),
    ]


def retro_console_price_cases() -> list[dict[str, str]]:
    return [
        {
            "id": "price-retro-ps2",
            "category": "consoles",
            "query": "Sony PlayStation 2",
            "expected_product_id": "console-sony-playstation-2",
            "expected_label": "Sony PlayStation 2",
            "goal": "Track clean working PlayStation 2 console prices.",
            "priority": "medium",
        },
        {
            "id": "price-retro-ps3",
            "category": "consoles",
            "query": "Sony PlayStation 3",
            "expected_product_id": "console-sony-playstation-3",
            "expected_label": "Sony PlayStation 3",
            "goal": "Track clean working PlayStation 3 console prices.",
            "priority": "medium",
        },
        {
            "id": "price-retro-xbox-360",
            "category": "consoles",
            "query": "Xbox 360",
            "expected_product_id": "console-microsoft-xbox-360",
            "expected_label": "Microsoft Xbox 360",
            "goal": "Track clean working Xbox 360 console prices.",
            "priority": "medium",
        },
        {
            "id": "price-retro-gamecube",
            "category": "consoles",
            "query": "Nintendo GameCube",
            "expected_product_id": "console-nintendo-gamecube",
            "expected_label": "Nintendo GameCube",
            "goal": "Track clean working Nintendo GameCube console prices.",
            "priority": "medium",
        },
        {
            "id": "price-retro-wii",
            "category": "consoles",
            "query": "Nintendo Wii",
            "expected_product_id": "console-nintendo-wii",
            "expected_label": "Nintendo Wii",
            "goal": "Track clean working Nintendo Wii console prices while excluding Wii U.",
            "priority": "medium",
        },
    ]
