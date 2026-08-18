import pytest

from app.catalog.catalog import listing_matches_product, match_product


@pytest.mark.parametrize(
    ("query", "product_id"),
    [
        ("Canon PowerShot G7X Digital Camera", "camera-canon-powershot-g7-x"),
        ("Panasonic Lumix G9 Mirrorless MFT Body, Black", "camera-panasonic-lumix-g9-body"),
        ("Nikon D300 body", "camera-nikon-d300-body"),
        ("Nikon D4 body", "camera-nikon-d4-body"),
        ("Sony Cyber-Shot DSC-RX1R", "camera-sony-cyber-shot-dsc-rx1r"),
        ("Sony DSC-RX1", "camera-sony-cyber-shot-dsc-rx1"),
        ("Canon PowerShot G7", "camera-canon-powershot-g7"),
        ("Olympus Stylus 1", "camera-olympus-stylus-1"),
        ("Nikon D800 body", "camera-nikon-d800-body"),
        ("Sony RX100 Black", "camera-sony-cyber-shot-dsc-rx100"),
    ],
)
def test_unresolved_camera_queries_now_resolve(query: str, product_id: str):
    match = match_product(query, category="cameras")
    assert match is not None
    assert match.product.id == product_id
    assert match.confidence >= 0.7


@pytest.mark.parametrize(
    ("query", "good_title", "bad_title"),
    [
        ("Canon PowerShot G7X Digital Camera", "Canon PowerShot G7 X Digital Camera Black Tested", "Canon PowerShot G7 X Mark II Digital Camera"),
        ("Panasonic Lumix G9 Mirrorless MFT Body, Black", "Panasonic Lumix DC-G9 Mirrorless Camera Body Black", "Panasonic Lumix G9 II DC-G9M2 Body"),
        ("Nikon D300 body", "Nikon D300 DSLR Camera Body Tested", "Nikon D300S DSLR Camera Body"),
        ("Nikon D4 body", "Nikon D4 DSLR Camera Body Tested", "Nikon D4S DSLR Camera Body"),
        ("Sony Cyber-Shot DSC-RX1R", "Sony Cyber-shot DSC-RX1R Digital Camera Tested", "Sony Cyber-shot DSC-RX1R II DSC-RX1RM2"),
        ("Sony DSC-RX1", "Sony Cyber-shot DSC-RX1 Full Frame Digital Camera", "Sony Cyber-shot DSC-RX1R Digital Camera"),
        ("Canon PowerShot G7", "Canon PowerShot G7 Digital Camera Tested", "Canon PowerShot G7 X Digital Camera"),
        ("Olympus Stylus 1", "Olympus Stylus 1 Digital Camera Tested", "Olympus Stylus 1s Digital Camera"),
        ("Nikon D800 body", "Nikon D800 DSLR Camera Body Tested", "Nikon D800E DSLR Camera Body"),
        ("Sony RX100 Black", "Sony Cyber-shot DSC-RX100 Digital Camera Black", "Sony Cyber-shot DSC-RX100 III RX100M3 Digital Camera"),
    ],
)
def test_new_camera_entries_keep_nearby_variants_separate(
    query: str,
    good_title: str,
    bad_title: str,
):
    match = match_product(query, category="cameras")
    assert match is not None
    assert listing_matches_product(good_title, match.product) is True
    assert listing_matches_product(bad_title, match.product) is False


def test_canon_g7_does_not_accept_panasonic_g7_title():
    match = match_product("Canon PowerShot G7", category="cameras")
    assert match is not None
    assert listing_matches_product("Panasonic Lumix G7 Mirrorless Camera Body", match.product) is False
