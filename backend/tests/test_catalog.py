from app.catalog.catalog import listing_matches_product, match_product


def test_resolves_rtx_3060_12gb():
    match = match_product("3060 12gb")
    assert match is not None
    assert match.product.id == "gpu-nvidia-rtx-3060-12gb"


def test_rejects_3060_ti_when_looking_for_3060_12gb():
    match = match_product("rtx 3060 12gb")
    assert match is not None
    assert listing_matches_product("NVIDIA RTX 3060 Ti 8GB", match.product) is False


def test_rejects_broken_listing():
    match = match_product("rtx 3060 12gb")
    assert match is not None
    assert listing_matches_product("Broken RTX 3060 12GB for parts", match.product) is False


def test_accepts_valid_3060_listing():
    match = match_product("rtx 3060 12gb")
    assert match is not None
    assert listing_matches_product("EVGA GeForce RTX 3060 XC 12GB GDDR6 Graphics Card", match.product) is True
