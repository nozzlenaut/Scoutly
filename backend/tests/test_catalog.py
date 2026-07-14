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


def test_resolves_console_variants_to_grouped_core_models():
    ps5_disc = match_product("PS5 Disc", category="consoles")
    ps5_digital = match_product("PS5 Digital Edition", category="consoles")
    series_s_512 = match_product("Xbox Series S 512GB", category="consoles")
    series_s_1tb = match_product("Xbox Series S Carbon Black 1TB", category="consoles")

    assert ps5_disc is not None
    assert ps5_digital is not None
    assert series_s_512 is not None
    assert series_s_1tb is not None
    assert ps5_disc.product.id == "console-playstation-5"
    assert ps5_digital.product.id == "console-playstation-5"
    assert series_s_512.product.id == "console-xbox-series-s"
    assert series_s_1tb.product.id == "console-xbox-series-s"
    assert ps5_disc.product.metadata.get("variants_grouped") is True
    assert match_product("Switch OLED", category="consoles").product.id == "console-nintendo-switch-oled"
    assert match_product("Nintendo 3DS XL", category="consoles").product.id == "console-nintendo-3ds-xl"


def test_core_models_resolve_while_truly_broad_xbox_families_do_not():
    assert match_product("PlayStation 5", category="consoles").product.id == "console-playstation-5"
    assert match_product("PlayStation 4", category="consoles").product.id == "console-playstation-4"
    assert match_product("Xbox Series", category="consoles") is None
    assert match_product("Xbox One", category="consoles") is None
    switch = match_product("Nintendo Switch", category="consoles")
    assert switch is not None
    assert switch.product.id == "console-nintendo-switch"


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


def test_rejects_new_console_noise_terms():
    switch = match_product("Nintendo Switch OLED", category="consoles")
    ps5 = match_product("PlayStation 5 Disc Edition", category="consoles")
    xbox = match_product("Xbox Series X", category="consoles")
    assert switch is not None
    assert ps5 is not None
    assert xbox is not None

    assert listing_matches_product("Nintendo switch lite Metal Heat shield frame.", switch.product) is False
    assert listing_matches_product("Nintendo Switch OLED Model HEG-001 Handheld Console Only", switch.product) is False
    assert listing_matches_product("Genuine Nintendo Switch Oled LCD Screen Display Replacement", switch.product) is False
    assert listing_matches_product("PlayStation 5 Slim Disc Edition Console Cover", ps5.product) is False
    assert listing_matches_product("PS5 Variety Disk Games Bundle", ps5.product) is False
    assert listing_matches_product("PS5 Empty Box With Packing Material", ps5.product) is False
    assert listing_matches_product("Sony PS5 Slim Digital Edition 1TB - Trade For Xbox Series X Digital", ps5.product) is False
    assert listing_matches_product("Genuine OEM Xbox Series X WiFi Board Card M1090312-006 Replacement - Parts", xbox.product) is False


def test_rejects_xbox_generation_mismatches():
    series_x = match_product("Xbox Series X", category="consoles")
    series_s = match_product("Xbox Series S 512GB", category="consoles")
    one_x = match_product("Xbox One X", category="consoles")
    assert series_x is not None
    assert series_s is not None
    assert one_x is not None

    assert listing_matches_product("Microsoft Xbox One S With Xbox Series X Controller + Accessories", series_x.product) is False
    assert listing_matches_product("Halo: Infinite (Microsoft Xbox One/Xbox Series X, 2021)", series_x.product) is False
    assert listing_matches_product("Microsoft Xbox Series X 1TB Video Game Console", series_x.product) is True
    assert listing_matches_product("Microsoft Xbox Series S 512GB Console", series_x.product) is False
    assert listing_matches_product("Microsoft Xbox One X 1TB Console", one_x.product) is True
    assert listing_matches_product("Microsoft Xbox Series X 1TB Console", one_x.product) is False


def test_rejects_local_pickup_only_globally():
    gpu = match_product("RTX 3060 12GB", category="gpus")
    assert gpu is not None
    assert listing_matches_product("NVIDIA RTX 3060 12GB Local Pickup Only", gpu.product) is False


def test_rejects_lego_bag_only_listing():
    falcon = match_product("LEGO Star Wars Millennium Falcon 75192", category="lego")
    assert falcon is not None
    assert listing_matches_product("75375 - Millennium Falcon - LEGO Star Wars - Bag 7 X2! Bag 7 ONLY!", falcon.product) is False


def test_switch_2_is_an_active_core_model():
    match = match_product("Nintendo Switch 2", category="consoles")
    assert match is not None
    assert match.product.id == "console-nintendo-switch-2"


def test_rejects_ps5_accessory_noise_from_reports():
    ps5 = match_product("PlayStation 5 Digital Edition", category="consoles")
    ps5_disc = match_product("PlayStation 5 Disc Edition", category="consoles")
    assert ps5 is not None
    assert ps5_disc is not None

    assert listing_matches_product("PlayStation5 Digital Edition External Drive Model CFI ZDD1 SONY", ps5.product) is False
    assert listing_matches_product("PS5 Digital Edition 30th Anniversary Limited Edition poster only", ps5.product) is False
    assert listing_matches_product("ps5 accessories bundle Includes Two Mirror Crome Plates ps5 Disk Edition", ps5_disc.product) is False


def test_rejects_console_apu_and_processor_parts():
    xbox = match_product("Xbox One X", category="consoles")
    assert xbox is not None
    assert listing_matches_product(
        "Procesor GPU APU XBOX ONE X X950118-002 X950118-003 M1067253-001 X950118 002",
        xbox.product,
    ) is False


def test_rejects_lego_cartridge_part_wording():
    lego = match_product("LEGO Super Mario Bros Nintendo Entertainment System 71374", category="lego")
    assert lego is not None
    assert listing_matches_product("Mario Bros. Cartridge for Lego Nintendo Entertainment System NES 71374", lego.product) is False


def test_rejects_multi_model_tesla_gpu_listing():
    p40 = match_product("Tesla P40", category="gpus")
    assert p40 is not None
    assert listing_matches_product(
        "Tesla NVIDIA P4 8GB P40 24GB K80 24GB M40 24GB P100 16GB GPU Graphics card",
        p40.product,
    ) is False
    assert listing_matches_product("NVIDIA Tesla P40 24GB PCIe GPU Graphics Card", p40.product) is True


def test_rejects_new_console_cover_game_and_stick_drift_noise():
    ps5 = match_product("PlayStation 5 Digital Edition", category="consoles")
    switch_lite = match_product("Nintendo Switch Lite", category="consoles")
    assert ps5 is not None
    assert switch_lite is not None

    assert listing_matches_product("Sony CFI-16019 PS5 Digital Edition Cover Used for CFI-2000/2200 Models", ps5.product) is False
    assert listing_matches_product("Nintendo Switch2 Final Fantasy VII Remake Game New Unopened Authentic", switch_lite.product) is False
    assert listing_matches_product("Nintendo Switch Lite Console Stick Drift", switch_lite.product) is False


def test_rejects_lego_loose_parts_but_allows_complete_sets_with_pieces():
    blacksmith = match_product("LEGO Medieval Blacksmith 21325", category="lego")
    nes = match_product("LEGO Super Mario Bros Nintendo Entertainment System 71374", category="lego")
    assert blacksmith is not None
    assert nes is not None

    assert listing_matches_product("LEGO Ideas Medieval Blacksmith 21325 Horse Only", blacksmith.product) is False
    assert listing_matches_product("LEGO Ideas Medieval Blacksmith 21325 Bed From Set", blacksmith.product) is False
    assert listing_matches_product("Mario Bros. Cartridge for Lego Nintendo Entertainment System NES 71374", nes.product) is False
    assert listing_matches_product("LEGO Ideas Medieval Blacksmith 21325 Complete Set 2164 Pieces", blacksmith.product) is True


def test_rejects_lego_missing_fig_shorthand():
    blacksmith = match_product("LEGO Medieval Blacksmith 21325", category="lego")
    assert blacksmith is not None
    assert listing_matches_product("LEGO Ideas Medieval Blacksmith 21325 MISSING 1 fig", blacksmith.product) is False
    assert listing_matches_product("LEGO Ideas Medieval Blacksmith 21325 missing one figure", blacksmith.product) is False
    assert listing_matches_product("LEGO Ideas Medieval Blacksmith 21325 Complete Set With Minifigs", blacksmith.product) is True


def test_rejects_console_multi_variation_model_title_but_allows_console_only_for_playstation():
    ps4_pro = match_product("PS4 Pro", category="consoles")
    assert ps4_pro is not None
    assert listing_matches_product("All Original, Slim, & Pro Models PlayStation 4 PS4 Console", ps4_pro.product) is False
    assert listing_matches_product("Sony PlayStation 4 Pro 1TB Console Only", ps4_pro.product) is True


def test_switch_console_only_still_rejected():
    switch = match_product("Nintendo Switch OLED", category="consoles")
    assert switch is not None
    assert listing_matches_product("Nintendo Switch OLED Console Only", switch.product) is False


def test_resolves_expanded_lego_catalog_entries():
    assert match_product("76269", category="lego").product.id.startswith("lego-76269")
    assert match_product("LEGO Titanic 10294", category="lego").product.id.startswith("lego-10294")
    assert match_product("LEGO Hogwarts Castle 71043", category="lego").product.id.startswith("lego-71043")


def test_sony_a1_ii_resolves_exactly_and_does_not_fall_back_to_original_a1():
    match = match_product("Sony A1 II", category="cameras")
    assert match is not None
    assert match.product.id == "camera-sony-a1-ii-body"
    assert match.confidence == 1.0

    suggestions = suggest_products("Sony A1 II", category="cameras")
    ids = [item.product.id for item in suggestions]
    assert ids[0] == "camera-sony-a1-ii-body"
    assert "camera-sony-a1-body" not in ids


def test_strict_generation_and_storage_clues_do_not_fall_back():
    assert match_product("Sony A1 III", category="cameras") is None
    gpu_match = match_product("RTX 5060 Ti 16GB", category="gpus")
    assert gpu_match is not None
    assert "ti" in gpu_match.product.model.lower()
    assert "16gb" in gpu_match.product.display_name.lower().replace(" ", "")


def test_switch_oled_requires_positive_complete_system_evidence():
    switch = match_product("Nintendo Switch OLED", category="consoles")
    assert switch is not None

    assert listing_matches_product("Nintendo Switch OLED Model HEG-001 White", switch.product) is False
    assert listing_matches_product("Nintendo Switch OLED with White Joy-Con and Dock", switch.product) is True
    assert listing_matches_product("Nintendo Switch OLED Complete Console Bundle", switch.product) is True


def test_common_lego_catalog_entries_resolve_by_number_and_name():
    assert match_product("10333", category="lego").product.id == "lego-10333-the-lord-of-the-rings-barad-dur"
    assert match_product("LEGO Barad-dûr 10333", category="lego").product.id == "lego-10333-the-lord-of-the-rings-barad-dur"
    assert match_product("75313", category="lego").product.id == "lego-75313-star-wars-at-at"
    assert match_product("LEGO UCS AT-AT 75313", category="lego").product.id == "lego-75313-star-wars-at-at"


def test_read_language_is_review_only_when_the_product_is_otherwise_valid():
    switch = match_product("Nintendo Switch OLED", category="consoles")
    assert switch is not None
    assert listing_matches_product(
        "Nintendo Switch OLED Console with Joy-Con and Dock READ",
        switch.product,
    ) is True
    assert listing_matches_product(
        "Nintendo Switch OLED Console with Joy-Con and Dock Complete",
        switch.product,
    ) is True


def test_resolves_v058_lego_catalog_expansion_by_set_number():
    expected = {
        "75159": "Death Star",
        "10267": "Gingerbread House",
        "21310": "Old Fishing Store",
        "42056": "Porsche 911 GT3 RS",
        "75827": "Ghostbusters Firehouse Headquarters",
    }
    for set_number, model_clue in expected.items():
        match = match_product(set_number, category="lego")
        assert match is not None
        assert match.product.metadata["set_number"] == set_number
        assert model_clue.lower() in match.product.model.lower()


def test_rejects_multi_model_rtx_a_series_variation_listings():
    a4000 = match_product("NVIDIA RTX A4000 16GB", category="gpus")
    assert a4000 is not None

    spam_title = "for DELL Precision 7760 SERIES NVIDIA RTX A3000 A4000 A5000 6GB 16GB VIDEO CARD"
    assert listing_matches_product(spam_title, a4000.product) is False
    assert listing_matches_product("NVIDIA RTX A4000 16GB GDDR6 PCIe Graphics Card", a4000.product) is True


def test_rejects_reported_gpu_core_cooler_shell_and_box_patterns():
    rtx_3080 = match_product("NVIDIA RTX 3080 10GB", category="gpus")
    rtx_5060_ti = match_product("NVIDIA RTX 5060 Ti 16GB", category="gpus")
    assert rtx_3080 is not None
    assert rtx_5060_ti is not None

    assert listing_matches_product(
        "NVIDIA GeForce RTX 3080 GPU Core - GA102-200-A1 - Tested & Pulled",
        rtx_3080.product,
    ) is False
    assert listing_matches_product(
        "Palit RTX 3080 10GB GDDR6X Graphics Card NO HEATSINK/COOLER",
        rtx_3080.product,
    ) is False
    assert listing_matches_product(
        "ZOTAC GAMING GeForce RTX 3080 Trinity OC Graphics Card - Shell ONLY",
        rtx_3080.product,
    ) is False
    assert listing_matches_product(
        "PNY GeForce RTX 5060 Ti 16GB - BOX & INSERT ONLY",
        rtx_5060_ti.product,
    ) is False


def test_rejects_camera_service_manual_parts_list():
    sony_a9 = match_product("Sony Alpha A9 Body", category="cameras")
    assert sony_a9 is not None
    assert listing_matches_product(
        "Sony Alpha 9 A9 ILCE-9 Service Manual Parts List Genuine Sony OEM NOT A COPY",
        sony_a9.product,
    ) is False


def test_rejects_3ds_accessories_games_and_selection_variations():
    three_ds = match_product("Nintendo 3DS XL", category="consoles")
    assert three_ds is not None

    assert listing_matches_product(
        "Nintendo 3DS LL XL smart pouch Kyogre Pokemon",
        three_ds.product,
    ) is False
    assert listing_matches_product(
        "Nintendo 3DS XL MANUAL ONLY No Games Or Consoles Different Languages",
        three_ds.product,
    ) is False
    assert listing_matches_product(
        "THE CHRONICLES OF NARNIA NINTENDO DS GAME 3DS 2DS LITE DSI XL",
        three_ds.product,
    ) is False
    assert listing_matches_product(
        "Nintendo WAP-002 3DS XL 3DS AC Adapter Charger Cable Cord Tested Authentic",
        three_ds.product,
    ) is False
    assert listing_matches_product(
        "Nintendo 3DS XL LL System | With Charger | USA English | 8GB SD | US Seller Pick",
        three_ds.product,
    ) is False
    assert listing_matches_product(
        "Nintendo New 3DS XL Handheld System With AC Adapter Charger Tested Working",
        three_ds.product,
    ) is True


def test_wii_u_storage_and_edition_variants_resolve_to_one_model():
    deluxe = match_product("Nintendo Wii U 32GB Deluxe", category="consoles")
    basic = match_product("Nintendo Wii U 8GB Basic", category="consoles")
    assert deluxe is not None
    assert basic is not None
    assert deluxe.product.id == "console-nintendo-wii-u"
    assert basic.product.id == "console-nintendo-wii-u"


def test_rejects_titanic_packaging_only_variations():
    titanic = match_product("LEGO Titanic 10294", category="lego")
    assert titanic is not None

    assert listing_matches_product("LEGO Titanic 10294 Empty outer box", titanic.product) is False
    assert listing_matches_product("LEGO Titanic 10294 Inner Boxes Only", titanic.product) is False
    assert listing_matches_product("LEGO Titanic 10294 3 Inner Boxes Only", titanic.product) is False
    assert listing_matches_product("LEGO Titanic 10294 Complete Set", titanic.product) is True


def test_bare_rtx_3080_query_does_not_choose_a_vram_variant():
    assert match_product("RTX 3080", category="gpus") is None

    suggestions = suggest_products("RTX 3080", category="gpus", limit=4)
    names = {match.product.display_name for match in suggestions}
    assert "NVIDIA RTX 3080 10GB" in names
    assert "NVIDIA RTX 3080 12GB" in names
    assert match_product("RTX 3080 10GB", category="gpus").product.id == "gpu-nvidia-rtx-3080-10gb"
    assert match_product("RTX 3080 12GB", category="gpus").product.id == "gpu-nvidia-rtx-3080-12gb"


def test_rejects_titanic_packaging_typos_and_phrase_variants():
    titanic = match_product("LEGO Titanic 10294", category="lego")
    assert titanic is not None

    assert listing_matches_product("LEGO Titanic 10294 EMPRY OUTER BOX", titanic.product) is False
    assert listing_matches_product("LEGO Titanic 10294 Outer Box", titanic.product) is False
    assert listing_matches_product("LEGO Titanic 10294 Packaging Only", titanic.product) is False
    assert listing_matches_product("LEGO Titanic 10294 Complete Set with Original Box", titanic.product) is True


def test_consumer_rtx_3080_rejects_server_passive_and_external_variants():
    rtx_3080 = match_product("NVIDIA RTX 3080 10GB", category="gpus")
    assert rtx_3080 is not None

    assert listing_matches_product("NVIDIA RTX 3080 10GB Passive Server GPU", rtx_3080.product) is False
    assert listing_matches_product("AORUS RTX 3080 Gaming Box eGPU External Graphics", rtx_3080.product) is False
    assert listing_matches_product("Gigabyte GeForce RTX 3080 10GB Desktop Graphics Card", rtx_3080.product) is True


def test_ram_builder_resolves_complete_specs():
    match = match_product("DDR4 Desktop 32GB 2x16GB 3200 MT/s Corsair", category="ram")
    assert match is not None
    assert match.confidence == 1.0
    assert match.product.category == "ram"
    assert match.product.metadata["form_factor"] == "desktop"
    assert match.product.metadata["generation"] == "ddr4"
    assert match.product.metadata["total_capacity_gb"] == 32
    assert match.product.metadata["stick_count"] == 2
    assert match.product.metadata["capacity_per_stick_gb"] == 16
    assert match.product.metadata["speed_mts"] == 3200


def test_ram_builder_rejects_unclear_or_incomplete_query():
    assert match_product("DDR4 Desktop 32GB", category="ram") is None
    assert match_product("DDR4 32GB 2x16GB", category="ram") is None
    assert match_product("Desktop 32GB 2x16GB", category="ram") is None


def test_ram_listing_requires_exact_generation_form_factor_and_configuration():
    match = match_product("DDR4 Desktop 32GB 2x16GB 3200 MT/s", category="ram")
    assert match is not None

    assert listing_matches_product(
        "Corsair Vengeance LPX 32GB (2x16GB) DDR4 3200MHz UDIMM Desktop Memory Kit",
        match.product,
    ) is True
    assert listing_matches_product("Corsair 32GB DDR4 3200 Desktop RAM", match.product) is False
    assert listing_matches_product("Corsair 32GB (1x32GB) DDR4 3200 UDIMM", match.product) is False
    assert listing_matches_product("Corsair 32GB (2x16GB) DDR5 3200 UDIMM", match.product) is False
    assert listing_matches_product("Corsair 32GB (2x16GB) DDR4 3200 SODIMM Laptop RAM", match.product) is False
    assert listing_matches_product("Samsung 32GB (2x16GB) DDR4 3200 ECC RDIMM Server RAM", match.product) is False


def test_ram_laptop_and_ddr3_are_supported():
    match = match_product("DDR3 Laptop 16GB 2x8GB 1600 MT/s", category="ram")
    assert match is not None
    assert listing_matches_product(
        "Crucial 16GB Kit (2x8GB) DDR3 1600MHz PC3-12800 SODIMM Laptop Memory",
        match.product,
    ) is True
    assert listing_matches_product(
        "Crucial 16GB Kit (2x8GB) DDR3 1600MHz UDIMM Desktop Memory",
        match.product,
    ) is False


def test_ram_generation_selection_rejects_multi_generation_spam():
    match = match_product("DDR4 Desktop 32GB 2x16GB", category="ram")
    assert match is not None
    assert listing_matches_product(
        "DDR3 DDR4 DDR5 Desktop RAM 8GB 16GB 32GB 2x16GB UDIMM",
        match.product,
    ) is False


def test_console_direct_search_resolves_core_model_catalog_entries():
    series_x = match_product("Xbox Series X 1TB", category="consoles")
    ps5_slim_digital = match_product(
        "PlayStation 5 Slim Digital Edition", category="consoles"
    )
    switch_oled = match_product("Nintendo Switch OLED", category="consoles")

    assert series_x is not None
    assert ps5_slim_digital is not None
    assert switch_oled is not None
    assert series_x.product.id == "console-xbox-series-x"
    assert ps5_slim_digital.product.id == "console-playstation-5-slim"
    assert switch_oled.product.id == "console-nintendo-switch-oled"
    assert series_x.product.metadata.get("variants_grouped") is True
    assert ps5_slim_digital.product.metadata.get("variants_grouped") is True


def test_original_switch_aliases_resolve_to_grouped_switch_model():
    aliases = [
        "Nintendo Switch",
        "Nintendo Switch V1",
        "Switch V1",
        "Nintendo Switch V2",
        "Switch V2",
        "HAC-001",
        "HAC-001(-01)",
        "Nintendo Switch Standard",
        "Original Nintendo Switch",
    ]
    for alias in aliases:
        match = match_product(alias, category="consoles")
        assert match is not None, alias
        assert match.product.id == "console-nintendo-switch", alias
        assert match.product.metadata.get("variants_grouped") is True, alias


def test_console_core_model_filters_keep_model_boundaries_and_accept_variants():
    series_x = match_product("Xbox Series X", category="consoles")
    ps5 = match_product("PlayStation 5 Digital Edition", category="consoles")
    assert series_x is not None
    assert ps5 is not None

    assert listing_matches_product(
        "Microsoft Xbox Series X 1TB Console Black Tested", series_x.product
    ) is True
    assert listing_matches_product(
        "Microsoft Xbox Series X 2TB Galaxy Black Console", series_x.product
    ) is True
    assert listing_matches_product(
        "Microsoft Xbox Series S 512GB Console White Tested", series_x.product
    ) is False
    assert listing_matches_product(
        "Sony PS5 Digital Edition Console 825GB", ps5.product
    ) is True
    assert listing_matches_product(
        "Sony PS5 Disc Edition Console 825GB", ps5.product
    ) is True
    assert listing_matches_product(
        "Sony PS5 Slim Disc Edition Console 1TB", ps5.product
    ) is False

def test_lego_rejects_requested_incomplete_unauthentic_and_bulk_phrases():
    titanic = match_product("LEGO Titanic 10294", category="lego")
    assert titanic is not None
    rejected = [
        "LEGO Titanic 10294 Box No Bricks",
        "LEGO Titanic 10294 Instructions No Bricks",
        "LEGO Titanic 10294 Without Minifigures",
        "LEGO Titanic 10294 MOC Compatible With LEGO",
        "LEGO Titanic 10294 Bootleg Clone Set",
        "LEGO Titanic 10294 Loose Bricks Bulk Lot",
    ]
    for title in rejected:
        assert listing_matches_product(title, titanic.product) is False
    assert listing_matches_product(
        "LEGO Titanic 10294 Complete Set With Original Box and Instructions",
        titanic.product,
    ) is True


def test_playstation_disc_and_digital_variants_share_the_core_model():
    slim_digital = match_product(
        "PlayStation 5 Slim 1TB Digital Edition", category="consoles"
    )
    slim_disc = match_product(
        "PlayStation 5 Slim Disc Edition", category="consoles"
    )
    standard_digital = match_product(
        "PlayStation 5 825GB Digital Edition", category="consoles"
    )
    standard_disc = match_product(
        "PlayStation 5 Disc Edition", category="consoles"
    )

    assert slim_digital is not None
    assert slim_disc is not None
    assert standard_digital is not None
    assert standard_disc is not None
    assert slim_digital.product.id == slim_disc.product.id == "console-playstation-5-slim"
    assert standard_digital.product.id == standard_disc.product.id == "console-playstation-5"
    assert listing_matches_product(
        "Sony PS5 Slim Digital Edition Console 1TB", slim_digital.product
    ) is True
    assert listing_matches_product(
        "Sony PS5 Slim Disc Edition Console 1TB", slim_digital.product
    ) is True
    assert listing_matches_product(
        "Sony PS5 Digital Edition Console 825GB", standard_digital.product
    ) is True
    assert listing_matches_product(
        "Sony PS5 Disc Edition Console 825GB", standard_digital.product
    ) is True
    assert listing_matches_product(
        "Sony PS5 Slim Digital Edition Console 1TB", standard_digital.product
    ) is False


def test_lego_complete_set_search_rejects_partial_components_and_percentages():
    examples = [
        ("LEGO Daily Bugle 76178", "LEGO Marvel Daily Bugle 76178 Taxi Cab Only"),
        ("LEGO AT-AT 75313", "LEGO Star Wars 75313 AT-AT Driver Minifigure"),
        ("LEGO Loop Coaster 10303", "LEGO 10303 Loop Coaster Two Loose Fence Pieces"),
        ("LEGO Hogwarts Castle 71043", "LEGO 71043 Hogwarts Castle Missing Some 99% Complete"),
        ("LEGO Porsche 911 10295", "LEGO 10295 Porsche 911 Missing Roof"),
        ("LEGO Mighty Bowser 71411", "LEGO 71411 Mighty Bowser Near Complete"),
        ("LEGO Mos Eisley Cantina 75290", "LEGO 75290 Mos Eisley Cantina 98% Complete"),
        ("LEGO Old Trafford 10272", "LEGO 10272 Old Trafford 99% Complete"),
    ]

    for query, title in examples:
        match = match_product(query, category="lego")
        assert match is not None, query
        assert listing_matches_product(title, match.product) is False, title

    complete = match_product("LEGO Hogwarts Castle 71043", category="lego")
    assert complete is not None
    assert listing_matches_product(
        "LEGO 71043 Hogwarts Castle 100% Complete No Missing Pieces",
        complete.product,
    ) is True


def test_lego_query_with_unknown_reissue_number_does_not_resolve_older_set():
    assert match_product("LEGO NASA Apollo Saturn V 92176", category="lego") is None
    original = match_product("LEGO NASA Apollo Saturn V 21309", category="lego")
    assert original is not None
    assert original.product.metadata["set_number"] == "21309"


def test_older_console_searches_require_hardware_evidence_and_reject_parts():
    rejected = [
        ("PlayStation 4 Slim", "Sony PlayStation 4 Slim Base Shell Housing"),
        ("PlayStation 4 Slim", "Sony PS4 Slim Mid-Frame Fan Heat Sink"),
        ("PlayStation 4 Slim", "PlayStation 4 Slim Game Disc Only"),
        ("PlayStation 4 Pro", "PS4 Pro Astro MixAmp Headset"),
        ("Xbox One S", "Xbox One S Standalone Disc Drive"),
        ("Nintendo 3DS XL", "Nintendo 3DS XL Box and Manuals Only"),
        ("Nintendo 3DS XL", "Pokemon Sun Nintendo 3DS XL"),
    ]
    for query, title in rejected:
        match = match_product(query, category="consoles")
        assert match is not None, query
        assert listing_matches_product(title, match.product) is False, title

    accepted = [
        ("PlayStation 4 Slim", "Sony PlayStation 4 Slim Console 1TB Tested"),
        ("PlayStation 4 Slim", "Sony PlayStation 4 Slim CUH-2215B 1TB Tested"),
        ("Xbox One S", "Microsoft Xbox One S Console 1TB Tested"),
        ("Nintendo 3DS XL", "New Nintendo 3DS XL RED-001 Tested"),
    ]
    for query, title in accepted:
        match = match_product(query, category="consoles")
        assert match is not None, query
        assert listing_matches_product(title, match.product) is True, title


def test_gpu_suffix_conflicts_and_hardware_failure_language_are_rejected():
    rx_xt = match_product("RX 5700 XT 8GB", category="gpus")
    super_card = match_product("RTX 4080 Super 16GB", category="gpus")
    ti_super = match_product("RTX 4070 Ti Super 16GB", category="gpus")
    assert rx_xt is not None
    assert super_card is not None
    assert ti_super is not None

    assert listing_matches_product(
        "AMD Radeon RX 5700 XT 8GB Graphics Card", rx_xt.product
    ) is True
    assert listing_matches_product(
        "AMD Radeon RX 5700 NON-XT 8GB Graphics Card", rx_xt.product
    ) is False
    assert listing_matches_product(
        "NVIDIA RTX 4080 Super 16GB Read! PARTS", super_card.product
    ) is False
    assert listing_matches_product(
        "NVIDIA RTX 4080 Super 16GB 3x PORTS FAILED", super_card.product
    ) is False
    assert listing_matches_product(
        "NVIDIA RTX 4080 16GB Graphics Card", super_card.product
    ) is False
    assert listing_matches_product(
        "NVIDIA RTX 4070 Ti 12GB Graphics Card", ti_super.product
    ) is False
    assert listing_matches_product(
        "NVIDIA RTX 4070 Ti Super 16GB Graphics Card", ti_super.product
    ) is True


def test_ram_selected_brand_rejects_mixed_brand_kits():
    match = match_product(
        "DDR4 Desktop 32GB 2x16GB 3200 MT/s SK Hynix", category="ram"
    )
    assert match is not None
    assert listing_matches_product(
        "SK Hynix 32GB Kit 2x16GB DDR4 3200 UDIMM Desktop RAM",
        match.product,
    ) is True
    assert listing_matches_product(
        "SK Hynix + A-Tech Pair 32GB 2x16GB DDR4 3200 UDIMM Desktop RAM",
        match.product,
    ) is False
