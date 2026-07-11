from app.catalog.catalog import listing_matches_product, match_product, suggest_products


def test_resolves_camera_from_category_alias():
    match = match_product("a7iii", category="cameras")
    assert match is not None
    assert match.product.id == "camera-sony-a7-iii-body"


def test_camera_category_rejects_accessories():
    match = match_product("Sony A7 III Body", category="cameras")
    assert match is not None
    assert listing_matches_product("Sony A7III Battery Charger Bundle Only", match.product) is False


def test_resolves_lens_from_common_typing():
    match = match_product("sony 24-70 2.8", category="lenses")
    assert match is not None
    assert match.product.id == "lens-sony-fe-24-70-f28-gm"


def test_lens_category_rejects_lens_hood_only():
    match = match_product("Sony 24-70 GM", category="lenses")
    assert match is not None
    assert listing_matches_product("Sony 24-70 GM Lens Hood Only", match.product) is False


def test_category_suggestions_are_filtered():
    camera_suggestions = suggest_products("sony", category="cameras")
    lens_suggestions = suggest_products("sony", category="lenses")
    assert camera_suggestions
    assert lens_suggestions
    assert all(item.product.category == "cameras" for item in camera_suggestions)
    assert all(item.product.category == "lenses" for item in lens_suggestions)


def test_resolves_short_3060_to_rtx_3060_12gb():
    match = match_product("3060", category="gpus")
    assert match is not None
    assert match.product.id == "gpu-nvidia-rtx-3060-12gb"


def test_resolves_rtx3060_compact_alias():
    match = match_product("rtx3060", category="gpu")
    assert match is not None
    assert match.product.id == "gpu-nvidia-rtx-3060-12gb"


def test_resolves_rtx_3060_12gb():
    match = match_product("3060 12gb", category="gpus")
    assert match is not None
    assert match.product.id == "gpu-nvidia-rtx-3060-12gb"


def test_suggests_multiple_3060_products():
    suggestions = suggest_products("3060", category="gpus")
    ids = [item.product.id for item in suggestions]
    assert "gpu-nvidia-rtx-3060-12gb" in ids
    assert "gpu-nvidia-rtx-3060-ti-8gb" in ids


def test_rejects_3060_ti_when_looking_for_3060_12gb():
    match = match_product("rtx 3060 12gb", category="gpus")
    assert match is not None
    assert listing_matches_product("NVIDIA RTX 3060 Ti 8GB", match.product) is False


def test_rejects_broken_listing():
    match = match_product("rtx 3060 12gb", category="gpus")
    assert match is not None
    assert listing_matches_product("Broken RTX 3060 12GB for parts", match.product) is False


def test_accepts_valid_3060_listing():
    match = match_product("rtx 3060 12gb", category="gpus")
    assert match is not None
    assert listing_matches_product("EVGA GeForce RTX 3060 XC 12GB GDDR6 Graphics Card", match.product) is True


def test_resolves_amd_compact_alias():
    match = match_product("rx6700xt", category="gpus")
    assert match is not None
    assert match.product.id == "gpu-amd-rx-6700-xt-12gb"


def test_resolves_intel_arc_alias():
    match = match_product("a770 16gb", category="gpus")
    assert match is not None
    assert match.product.id == "gpu-intel-arc-a770-16gb"


def test_resolves_sony_a7_iv_body():
    match = match_product("Sony A7 IV Body", category="cameras")
    assert match is not None
    assert match.product.id == "camera-sony-a7-iv-body"


def test_rejects_a7r_iv_repair_part_for_a7_iv():
    match = match_product("Sony A7 IV Body", category="cameras")
    assert match is not None
    title = "For Sony ILCE-7RM4 A7R IV A7RM4 Body to Lens Mount Contact Flex Cable Original"
    assert listing_matches_product(title, match.product) is False


def test_accepts_valid_a7_iv_body_listing():
    match = match_product("Sony A7 IV Body", category="cameras")
    assert match is not None
    title = "Sony Alpha A7 IV 33MP Mirrorless Camera Body Only ILCE-7M4 Excellent"
    assert listing_matches_product(title, match.product) is True


def test_rejects_a7iii_mount_ring_accessory():
    match = match_product("Sony A7 III Body", category="cameras")
    assert match is not None
    title = "For Sony ILCE-A9 A7RM3 A7III A7M3 A7R4 Camera Body Lens Bayonet E Mount Ring"
    assert listing_matches_product(title, match.product) is False


def test_accepts_valid_a7iii_body_listing():
    match = match_product("Sony A7 III Body", category="cameras")
    assert match is not None
    title = "Sony Alpha A7 III 24.2MP Mirrorless Digital Camera Body ILCE-7M3 Excellent"
    assert listing_matches_product(title, match.product) is True


def test_rejects_a7iii_camera_error_please_read():
    match = match_product("Sony A7 III Body", category="cameras")
    assert match is not None
    title = "Sony A7 iii Full Frame Mirrorless Body A7 III *Camera Error Please READ*"
    assert listing_matches_product(title, match.product) is False


def test_rejects_box_only_for_everything():
    camera = match_product("Sony A7 III Body", category="cameras")
    lens = match_product("Sony 24-70 GM", category="lenses")
    gpu = match_product("RTX 3060 12GB", category="gpus")
    assert camera is not None
    assert lens is not None
    assert gpu is not None
    assert listing_matches_product("Sony A7 III Body Box Only", camera.product) is False
    assert listing_matches_product("Sony FE 24-70mm f/2.8 GM Box Only", lens.product) is False
    assert listing_matches_product("NVIDIA RTX 3060 12GB Box Only", gpu.product) is False


def test_rejects_lens_coat_and_ring_gear():
    match = match_product("Sony 24-70 GM", category="lenses")
    assert match is not None
    assert listing_matches_product("LensCoat Lens Coat for Sony 24-70 GM", match.product) is False
    assert listing_matches_product("Sony 24-70 GM Focus Ring Gear for Follow Focus", match.product) is False


def test_rejects_gpu_as_is_parts_listing():
    match = match_product("RTX 3060 12GB", category="gpus")
    assert match is not None
    assert listing_matches_product("EVGA RTX 3060 12GB AS-IS Parts Only No Display", match.product) is False
