from app.catalog.catalog import listing_matches_product, match_product
from app.catalog.retro_consoles import retro_console_price_cases
from app.services.ai_console_review import is_ai_console_review_target


def _resolve(query: str):
    match = match_product(query, "consoles")
    assert match is not None
    return match.product


def test_retro_console_queries_resolve_to_stable_products():
    expected = {
        "Sony PlayStation 2": "console-sony-playstation-2",
        "Sony PlayStation 3": "console-sony-playstation-3",
        "Xbox 360": "console-microsoft-xbox-360",
        "Nintendo GameCube": "console-nintendo-gamecube",
        "Nintendo Wii": "console-nintendo-wii",
    }
    for query, product_id in expected.items():
        assert _resolve(query).id == product_id


def test_retro_console_products_use_ai_listing_review():
    for query in [
        "Sony PlayStation 2",
        "Sony PlayStation 3",
        "Xbox 360",
        "Nintendo GameCube",
        "Nintendo Wii",
    ]:
        assert is_ai_console_review_target(_resolve(query)) is True


def test_wii_keeps_wii_u_out():
    product = _resolve("Nintendo Wii")
    assert listing_matches_product("Nintendo Wii Console System RVL-001 Tested Working", product)
    assert not listing_matches_product("Nintendo Wii U 32GB Console System Tested Working", product)


def test_retro_price_cases_cover_every_new_product():
    ids = {case["expected_product_id"] for case in retro_console_price_cases()}
    assert ids == {
        "console-sony-playstation-2",
        "console-sony-playstation-3",
        "console-microsoft-xbox-360",
        "console-nintendo-gamecube",
        "console-nintendo-wii",
    }
