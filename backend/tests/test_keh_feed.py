from fastapi.testclient import TestClient

from app.main import app
from app.services.keh_feed import (
    classify_keh_product,
    keh_overview,
    normalize_feed_row,
    parse_keh_grade,
    public_keh_listings,
    sync_keh_feed,
)
from app.catalog.catalog import match_product
from app.models.listing import Listing
from datetime import UTC, datetime


def _row(**overrides):
    row = {
        "aw_deep_link": "https://www.awin1.com/pclick.php?p=1&a=2&m=89435",
        "product_name": "Sony Alpha a7 III Mirrorless Camera Body - EX+ - Excellent Plus - With Battery and Charger | Used",
        "aw_product_id": "1",
        "merchant_product_id": "sony-a7iii-1",
        "merchant_image_url": "https://example.com/a7iii.jpg",
        "description": "Sony A7 III camera body",
        "merchant_category": "Cameras & Optics > Cameras > Digital Cameras",
        "search_price": "999.00",
        "currency": "USD",
        "merchant_deep_link": "https://www.keh.com/shop/sony-a7iii.html",
        "brand_name": "Sony",
        "condition": "used",
        "merchant_product_category_path": "Used Cameras > Used Digital Cameras > Used Digital Mirrorless Cameras > 123",
        "in_stock": "1",
        "is_for_sale": "1",
    }
    row.update(overrides)
    return row


def test_keh_grade_is_parsed_from_title():
    assert parse_keh_grade(_row()["product_name"]) == ("EX+", "Excellent Plus")


def test_keh_scope_accepts_body_with_battery_and_charger():
    assert classify_keh_product(_row()) == "camera_body"


def test_keh_scope_rejects_accessories_and_conversion_lenses():
    flash = _row(
        product_name="Canon Speedlite 430EX III-RT Flash",
        merchant_category="Cameras & Optics > Camera Parts & Accessories",
        merchant_product_category_path="Lighting > On-Camera Flashes & Lights",
    )
    converter = _row(
        product_name="Fujifilm WCL-X100 II Wide Conversion Lens 28mm",
        merchant_category="Cameras & Optics > Camera Lenses",
        merchant_product_category_path="Used Camera Lenses > Used Mirrorless Camera Lenses",
    )
    assert classify_keh_product(flash) is None
    assert classify_keh_product(converter) is None


def test_normalize_keh_row_matches_camera_qa_pilot_product(monkeypatch):
    monkeypatch.delenv("KEH_SHADOW_PRODUCT_IDS", raising=False)
    item = normalize_feed_row(_row(), datetime.now(UTC))
    assert item is not None
    assert item["matched_product_id"] == "camera-sony-a7-iii-body"
    assert item["match_status"] == "matched"
    assert item["condition_grade_code"] == "EX+"


def test_shadow_sync_uses_file_fallback_and_admin_endpoint(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")

    run = sync_keh_feed(feed_rows=[_row()])
    assert run["status"] == "success"
    assert run["matched_items"] == 1
    assert keh_overview()["matched_count"] == 1

    client = TestClient(app)
    assert client.get("/api/keh/overview").status_code == 401
    response = client.get("/api/keh/overview", params={"token": "secret"})
    assert response.status_code == 200
    assert response.json()["public_results_enabled"] is False


def test_public_keh_pilot_exposes_only_whitelisted_product(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("KEH_PUBLIC_RESULTS", "true")
    monkeypatch.delenv("KEH_PUBLIC_PRODUCT_IDS", raising=False)

    sync_keh_feed(feed_rows=[_row()])
    product_match = match_product("Sony A7 III Body", "cameras")
    assert product_match is not None

    listings = public_keh_listings(product_match.product)
    assert len(listings) == 1
    assert listings[0].provider == "KEH"
    assert listings[0].condition == "Used · EX+ · Excellent Plus"
    assert listings[0].affiliate_url_used is True

    non_public_match = match_product("Nikon Z5 Body", "cameras")
    assert non_public_match is not None
    assert public_keh_listings(non_public_match.product) == []


def test_public_search_can_merge_keh_pilot_result(monkeypatch):
    keh_listing = Listing(
        provider="KEH",
        title="Sony Alpha a7 III Camera Body - EX+ - Excellent Plus | Used",
        price=899,
        shipping=0,
        total_price=899,
        condition="Used · EX+ · Excellent Plus",
        url="https://www.awin1.com/pclick.php?p=1&a=2&m=89435",
        affiliate_url_used=True,
        affiliate_url_has_campaign_id=True,
        score=500,
    )
    monkeypatch.setattr(
        "app.services.search_service.public_keh_listings",
        lambda product, limit=50: [keh_listing] if product.id == "camera-sony-a7-iii-body" else [],
    )

    client = TestClient(app)
    response = client.get(
        "/api/search",
        params={
            "q": "Sony A7 III Body",
            "category": "cameras",
            "providers": "none",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"][0]["provider"] == "KEH"
    assert payload["results"][0]["price"] == 899


def _lens_row(**overrides):
    row = _row(
        aw_product_id="lens-1",
        merchant_product_id="lens-merchant-1",
        product_name="Sigma 24-70mm f/2.8 DG DN II Art Lens for Sony E-Mount - EX+ - Excellent Plus - With Caps | Used",
        description="Sigma 24-70mm f/2.8 DG DN II Art Lens for Sony E-Mount",
        merchant_category="Cameras & Optics > Camera & Video Camera Lenses > Camera Lenses",
        merchant_product_category_path="Used Camera Lenses > Used Mirrorless Camera Lenses > 999",
        search_price="1099.00",
        brand_name="Sigma",
        mpn="578965",
    )
    row.update(overrides)
    return row


def test_lens_feed_rows_are_retained_for_builder():
    item = normalize_feed_row(_lens_row(), datetime.now(UTC))
    assert item is not None
    assert item["product_type"] == "lens"
    assert item["match_status"] == "lens_inventory"
    assert item["matched_product_id"] is None


def test_keh_lens_builder_groups_inventory_and_returns_top_three(monkeypatch, tmp_path):
    from app.services.keh_feed import keh_lens_builder

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    rows = [
        _lens_row(aw_product_id="lens-1", search_price="1099.00"),
        _lens_row(aw_product_id="lens-2", merchant_product_id="lens-merchant-2", search_price="1149.00", product_name="Sigma 24-70mm f/2.8 DG DN II Art Lens for Sony E-Mount - LN- - Like New Minus - With Caps | Used"),
        _lens_row(aw_product_id="lens-3", merchant_product_id="lens-merchant-3", search_price="999.00", product_name="Sigma 24-70mm f/2.8 DG DN II Art Lens for Sony E-Mount - BGN - Bargain - With Caps | Used"),
        _lens_row(aw_product_id="lens-4", merchant_product_id="lens-merchant-4", search_price="1199.00"),
    ]
    sync_keh_feed(feed_rows=rows)
    payload = keh_lens_builder(mount="Sony E", lens_type="Zoom", focal_group="Standard zoom", brand="Sigma")
    assert payload["summary"]["listing_count"] == 4
    assert payload["summary"]["filtered_model_count"] == 1
    model = payload["models"][0]
    assert model["listing_count"] == 4
    assert model["lowest_price"] == 999.0
    assert model["highest_price"] == 1199.0
    assert model["condition_grades"] == ["LN-", "EX+", "BGN"]
    assert model["image_url"]
    assert len(model["listings"]) == 3
    assert model["listings"][0]["price"] == 999.0


def test_admin_lens_builder_endpoint_requires_token(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    sync_keh_feed(feed_rows=[_lens_row()])

    client = TestClient(app)
    assert client.get("/api/keh/lenses/builder").status_code == 401
    response = client.get(
        "/api/keh/lenses/builder",
        params={"token": "secret", "mount": "Sony E", "lens_type": "Zoom"},
    )
    assert response.status_code == 200
    assert response.json()["models"][0]["model_name"].startswith("Sigma 24-70mm")
