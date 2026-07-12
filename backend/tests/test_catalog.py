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


def test_resolves_expanded_camera_catalog_entries():
    assert match_product("Canon R6 II", category="cameras").product.id == "camera-canon-eos-r6-mark-ii-body"
    assert match_product("Nikon Z8", category="cameras").product.id == "camera-nikon-z8-body"
    assert match_product("Fuji XT5", category="cameras").product.id == "camera-fujifilm-x-t5-body"


def test_resolves_expanded_lens_catalog_entries():
    assert match_product("Sony 85 1.8", category="lenses").product.id == "lens-sony-fe-85mm-f-1-8"
    assert match_product("Canon RF 70-200 2.8", category="lenses").product.id == "lens-canon-rf-70-200mm-f-2-8l-is-usm"
    assert match_product("Tamron 28-75 G2", category="lenses").product.id == "lens-tamron-28-75mm-f-2-8-di-iii-vxd-g2-sony-e"


def test_resolves_expanded_gpu_catalog_entries():
    assert match_product("rx580 8gb", category="gpus").product.id == "gpu-amd-rx-580-8gb"
    assert match_product("rx9070xt", category="gpus").product.id == "gpu-amd-rx-9070-xt-16gb"
    assert match_product("arc b580", category="gpus").product.id == "gpu-intel-arc-b580-12gb"


def test_rejects_more_lens_ring_accessories():
    match = match_product("Sony FE 85mm f/1.8", category="lenses")
    assert match is not None
    assert listing_matches_product("Zoom Ring Rubber Grip for Sony FE 85mm f/1.8 Lens", match.product) is False
    assert listing_matches_product("Step Up Ring Adapter for Sony FE 85mm f/1.8", match.product) is False
    assert listing_matches_product("Sony FE 85mm f/1.8 Lens Excellent Condition", match.product) is True


def test_rejects_lens_rubber_and_bayonet_ring_accessories():
    zoom = match_product("Sony FE 24-70mm f/2.8 GM", category="lenses")
    prime = match_product("Sony FE 85mm f/1.8", category="lenses")
    assert zoom is not None
    assert prime is not None
    assert listing_matches_product(
        "COPY NEW Lens Zoom Rubber Ring Focus Rubber Ring For Sony FE 24-70mm 1:2.8 GM",
        zoom.product,
    ) is False
    assert listing_matches_product(
        "For Sony FE 85mm F1.8 Rear Bayonet Mount Metal Ring SEL85F18 FE 85 1.8 85/1.8",
        prime.product,
    ) is False


def test_accepts_real_used_lens_with_normal_focus_ring_language():
    lens = match_product("Sony FE 85mm f/1.8", category="lenses")
    assert lens is not None
    assert listing_matches_product(
        "Sony FE 85mm f/1.8 Lens - clean glass, smooth focus ring, excellent condition",
        lens.product,
    ) is True


def test_resolves_more_camera_catalog_entries():
    assert match_product("Sony A7R V", category="cameras").product.id == "camera-sony-a7r-v-body"
    assert match_product("Canon R5 II", category="cameras").product.id == "camera-canon-eos-r5-mark-ii-body"
    assert match_product("Nikon Z6III", category="cameras").product.id == "camera-nikon-z6-iii-body"
    assert match_product("Fuji XH2S", category="cameras").product.id == "camera-fujifilm-x-h2s-body"
    assert match_product("OM-1", category="cameras").product.id == "camera-om-system-om-1-body"


def test_rejects_original_a7r_when_searching_a7r_iii():
    match = match_product("Sony A7R III Body", category="cameras")
    assert match is not None
    title = "Sony Alpha A7R 36.4MP Mirrorless Digital SLR Camera With 16-50mm Lens - 95% New"
    assert listing_matches_product(title, match.product) is False


def test_rejects_body_search_lens_kit_bundle():
    match = match_product("Sony A7R III Body", category="cameras")
    assert match is not None
    title = "Sony A7R III Mirrorless Camera Body with lens kit"
    assert listing_matches_product(title, match.product) is False


def test_resolves_more_gpu_catalog_entries():
    assert match_product("RTX 5050", category="gpus").product.id == "gpu-nvidia-rtx-5050-8gb"
    assert match_product("rx480 8gb", category="gpus").product.id == "gpu-amd-rx-480-8gb"
    assert match_product("radeon vii", category="gpus").product.id == "gpu-amd-radeon-vii-16gb"
    assert match_product("arc a580", category="gpus").product.id == "gpu-intel-arc-a580-8gb"


def test_rejects_camera_accessories_listing():
    match = match_product("Canon EOS RP Body", category="cameras")
    assert match is not None
    assert listing_matches_product("EOS RP Camera Accessories", match.product) is False


def test_resolves_larger_camera_catalog_entries():
    assert match_product("Sony A7 II", category="cameras").product.id == "camera-sony-a7-ii-body"
    assert match_product("Canon 5D Mark IV", category="cameras").product.id == "camera-canon-eos-5d-mark-iv-body"
    assert match_product("Nikon D850", category="cameras").product.id == "camera-nikon-d850-body"
    assert match_product("Fuji X100VI", category="cameras").product.id == "camera-fujifilm-x100vi"
    assert match_product("Ricoh GR IIIx", category="cameras").product.id == "camera-ricoh-gr-iiix"


def test_resolves_llm_gpu_catalog_entries():
    assert match_product("Tesla P40", category="gpus").product.id == "gpu-nvidia-tesla-p40-24gb"
    assert match_product("RTX A5000", category="gpus").product.id == "gpu-nvidia-rtx-a5000-24gb"
    assert match_product("RTX 5000", category="gpus").product.id == "gpu-nvidia-quadro-rtx-5000-16gb"
    assert match_product("RTX 5000 Ada", category="gpus").product.id == "gpu-nvidia-rtx-5000-ada-32gb"
    assert match_product("Radeon Pro W7900", category="gpus").product.id == "gpu-amd-radeon-pro-w7900-48gb"


def test_rejects_tesla_v100_heatsink_accessory():
    match = match_product("Tesla V100 16GB", category="gpus")
    assert match is not None
    assert listing_matches_product("NVIDIA Tesla V100 16GB GPU Heatsink", match.product) is False
    assert listing_matches_product("For NVIDIA Tesla V100 16GB Replacement Heatsink Cooler", match.product) is False


def test_accepts_real_tesla_v100_card_with_passive_heatsink_note():
    match = match_product("Tesla V100 16GB", category="gpus")
    assert match is not None
    title = "NVIDIA Tesla V100 16GB PCIe GPU Accelerator with passive heatsink"
    assert listing_matches_product(title, match.product) is True


def test_rejects_camera_filter_accessory():
    match = match_product("Canon EOS RP Body", category="cameras")
    assert match is not None
    assert listing_matches_product("Canon EOS RP Camera UV Filter Kit", match.product) is False
    assert listing_matches_product("Canon EOS RP Body Excellent Condition", match.product) is True


def test_rejects_sxm_tesla_for_normal_pcie_search():
    p100 = match_product("Tesla P100 16GB", category="gpus")
    v100 = match_product("Tesla V100 16GB", category="gpus")
    assert p100 is not None
    assert v100 is not None
    assert listing_matches_product("699-2H403-0201-730 Nvidia Tesla P100 SXM2 16GB Module", p100.product) is False
    assert listing_matches_product("NVIDIA Tesla V100 SXM2 16GB Mezzanine Module", v100.product) is False
    assert listing_matches_product("NVIDIA Tesla P100 16GB PCIe GPU Accelerator", p100.product) is True


def test_resolves_lego_catalog_entries_by_set_number():
    assert match_product("75192", category="lego").product.id.startswith("lego-75192")
    assert match_product("LEGO Rivendell 10316", category="lego").product.id.startswith("lego-10316")
    assert match_product("21325", category="lego").product.id.startswith("lego-21325")


def test_rejects_lego_box_instruction_and_light_kit_listings():
    match = match_product("LEGO Millennium Falcon 75192", category="lego")
    assert match is not None
    assert listing_matches_product("LEGO 75192 Millennium Falcon Box Only", match.product) is False
    assert listing_matches_product("LEGO 75192 Millennium Falcon Instructions Only", match.product) is False
    assert listing_matches_product("Light Kit for LEGO 75192 Millennium Falcon", match.product) is False
    assert listing_matches_product("LEGO Star Wars Millennium Falcon 75192 Complete Set", match.product) is True


def test_accepts_real_rtx_4070_titles_without_false_ti_match():
    match = match_product("NVIDIA RTX 4070 12GB", category="gpus")
    assert match is not None
    assert listing_matches_product("ASUS Dual GeForce RTX 4070 OC Edition Graphics Card", match.product) is True
    assert listing_matches_product("PNY NVIDIA GeForce RTX 4070 12GB VERTO Dual Fan. Tested And Working", match.product) is True
    assert listing_matches_product("NVIDIA GeForce RTX 4070 Founders Edition 12GB Graphics Card", match.product) is True
    assert listing_matches_product("MSI GeForce RTX 4070 Ti SUPER 16GB VENTUS 2X White OC Dual Fan Card", match.product) is False


def test_rejects_smx_typo_tesla_for_normal_pcie_search():
    match = match_product("Tesla P100 16GB", category="gpus")
    assert match is not None
    assert listing_matches_product("699-2H403-0201-730 Nvidia Tesla P100 SMX2 16GB", match.product) is False


def test_rejects_lego_multi_set_listing_with_requested_set_number():
    match = match_product("LEGO Star Wars Millennium Falcon 75192", category="lego")
    assert match is not None
    assert listing_matches_product(
        "Lego Star Wars 75192 75376 75383 75386 *** FREE SHIPPING ***",
        match.product,
    ) is False
    assert listing_matches_product(
        "LEGO Star Wars Millennium Falcon 75192 Complete Set",
        match.product,
    ) is True



def test_rejects_incomplete_lego_listings_without_rejecting_piece_count():
    match = match_product("LEGO Star Wars TIE Interceptor 75382", category="lego")
    assert match is not None
    assert listing_matches_product("LEGO Star Wars 75382 | TIE Interceptor | 1931 Pieces | Complete Set", match.product) is True
    assert listing_matches_product("LEGO Star Wars UCS: TIE Interceptor 75382 (2024) - Partial see description", match.product) is False
    assert listing_matches_product("LEGO Star Wars TIE Interceptor 75382 Missing Pieces", match.product) is False
    assert listing_matches_product("LEGO Star Wars TIE Interceptor 75382 Not Complete", match.product) is False


def test_rejects_lego_minifigure_and_parts_references_to_set_number():
    match = match_product("LEGO Star Wars Millennium Falcon 75192", category="lego")
    assert match is not None
    assert listing_matches_product("Lego Star Wars Han Solo - 75192 UCS Millennium Falcon", match.product) is False
    assert listing_matches_product("LEGO Finn Minifigure Star Wars sw0676 75192 75178 75105 B5", match.product) is False
    assert listing_matches_product("LEGO Star Wars Millennium Falcon 75192 Complete Set with Minifigures", match.product) is True


def test_allows_lego_complete_with_instructions_but_rejects_instructions_only():
    match = match_product("LEGO Star Wars Republic Gunship 75309", category="lego")
    assert match is not None
    assert listing_matches_product("LEGO Star Wars UCS Republic Gunship 75309 Complete Set No Box/Manual", match.product) is True
    assert listing_matches_product("LEGO Star Wars UCS Republic Gunship 75309 COMPLETE SET with all boxes", match.product) is True
    assert listing_matches_product("LEGO Star Wars UCS Republic Gunship 75309 RETIRED - MANUAL - Bags 14-17 Unopened", match.product) is False
    assert listing_matches_product("LEGO 75309 Star Wars Republic Gunship Instructions Only", match.product) is False


def test_rejects_lego_name_match_without_exact_set_number():
    match = match_product("LEGO Star Wars Millennium Falcon 75192", category="lego")
    assert match is not None
    assert listing_matches_product(
        "Used Main Build Complete Lego Star Wars 55555 Millenium (Millennium) Falcon",
        match.product,
    ) is False
    assert listing_matches_product(
        "LEGO Star Wars Millennium Falcon 75192 Complete Set",
        match.product,
    ) is True


def test_rejects_lego_base_or_build_only_listings():
    match = match_product("LEGO Super Mario The Mighty Bowser 71411", category="lego")
    assert match is not None
    assert listing_matches_product(
        "LEGO 71411 Super Mario: The Mighty Bowser Base & Towers Only READ",
        match.product,
    ) is False


def test_rejects_gpu_problem_notes_but_allows_no_problems():
    match = match_product("RTX 3060 12GB", category="gpus")
    assert match is not None
    assert listing_matches_product(
        "Zotac Nvidia GeForce RTX 3060 12GB Graphics Card GPU PC (FAN PROBLEM NOTES)",
        match.product,
    ) is False
    assert listing_matches_product(
        "Zotac Nvidia GeForce RTX 3060 12GB Graphics Card Tested Working No Problems",
        match.product,
    ) is True


def test_resolves_console_catalog_entries():
    assert match_product("PS5 Disc", category="consoles").product.id == "console-playstation-5-disc-edition"
    assert match_product("Xbox Series X", category="consoles").product.id == "console-xbox-series-x-1tb"
    assert match_product("Switch OLED", category="consoles").product.id == "console-nintendo-switch-oled"


def test_console_filters_reject_parts_and_switch_tablet_only():
    ps5 = match_product("PS5 Disc", category="consoles")
    switch = match_product("Nintendo Switch OLED", category="consoles")
    xbox = match_product("Xbox Series X", category="consoles")
    assert ps5 is not None
    assert switch is not None
    assert xbox is not None

    assert listing_matches_product("For PS5 HDMI Port Replacement Repair Part", ps5.product) is False
    assert listing_matches_product("Nintendo Switch OLED Tablet Only", switch.product) is False
    assert listing_matches_product("Xbox Series X Controller Only", xbox.product) is False
    assert listing_matches_product("Microsoft Xbox Series X 1TB Console Complete", xbox.product) is True


def test_rejects_recent_reported_gpu_and_lego_edge_cases():
    gpu = match_product("RTX 3060 12GB", category="gpus")
    lego = match_product("LEGO Super Mario Bros Nintendo Entertainment System 71374", category="lego")
    falcon = match_product("LEGO Star Wars Millennium Falcon 75192", category="lego")
    assert gpu is not None
    assert lego is not None
    assert falcon is not None

    assert listing_matches_product("ASUS Nvidia GeForce RTX 3060 12GB Graphics Card GPU PC NON-LHR (1x FAN MISSING)", gpu.product) is False
    assert listing_matches_product("LEGO Super Mario Bros Nintendo Entertainment System 71374 - Cartridge Only", lego.product) is False
    assert listing_matches_product("LABRIA (sw1126) from Lego Star Wars 75290 Mos Eisley Cantina Kardue'sai'Malloc", falcon.product) is False
