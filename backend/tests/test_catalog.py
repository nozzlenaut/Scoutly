from app.catalog.catalog import listing_matches_product, match_product, suggest_products


def test_resolves_short_3060_to_rtx_3060_12gb():
    match = match_product("3060")
    assert match is not None
    assert match.product.id == "gpu-nvidia-rtx-3060-12gb"


def test_resolves_rtx3060_compact_alias():
    match = match_product("rtx3060")
    assert match is not None
    assert match.product.id == "gpu-nvidia-rtx-3060-12gb"


def test_resolves_rtx_3060_12gb():
    match = match_product("3060 12gb")
    assert match is not None
    assert match.product.id == "gpu-nvidia-rtx-3060-12gb"


def test_suggests_multiple_3060_products():
    suggestions = suggest_products("3060")
    ids = [item.product.id for item in suggestions]
    assert "gpu-nvidia-rtx-3060-12gb" in ids
    assert "gpu-nvidia-rtx-3060-ti-8gb" in ids


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


def test_resolves_amd_compact_alias():
    match = match_product("rx6700xt")
    assert match is not None
    assert match.product.id == "gpu-amd-rx-6700-xt-12gb"


def test_resolves_intel_arc_alias():
    match = match_product("a770 16gb")
    assert match is not None
    assert match.product.id == "gpu-intel-arc-a770-16gb"
