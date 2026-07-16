from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.catalog.catalog import match_product
from app.main import app
from app.services.keh_feed import (
    normalize_feed_row,
    public_keh_listings,
    public_product_ids,
    sync_keh_feed,
)


def _camera_row(**overrides):
    row = {
        "aw_deep_link": "https://www.awin1.com/pclick.php?p=2&a=2&m=89435",
        "product_name": "Nikon Z5 Mirrorless Camera Body - EX - Excellent - With Battery and Charger | Used",
        "aw_product_id": "nikon-z5-1",
        "merchant_product_id": "nikon-z5-1",
        "merchant_image_url": "https://example.com/nikon-z5.jpg",
        "description": "Nikon Z5 mirrorless camera body",
        "merchant_category": "Cameras & Optics > Cameras > Digital Cameras",
        "search_price": "799.00",
        "currency": "USD",
        "merchant_deep_link": "https://www.keh.com/shop/nikon-z5.html",
        "brand_name": "Nikon",
        "condition": "used",
        "merchant_product_category_path": "Used Cameras > Used Digital Cameras > Used Digital Mirrorless Cameras > 123",
        "in_stock": "1",
        "is_for_sale": "1",
    }
    row.update(overrides)
    return row


def _lens_row(**overrides):
    row = {
        "aw_deep_link": "https://www.awin1.com/pclick.php?p=3&a=2&m=89435",
        "product_name": "Sigma 24-70mm f/2.8 DG DN II Art Lens for Sony E-Mount - EX+ - Excellent Plus - With Caps | Used",
        "aw_product_id": "lens-public-1",
        "merchant_product_id": "lens-public-1",
        "merchant_image_url": "https://example.com/sigma-24-70.jpg",
        "description": "Sigma 24-70mm f/2.8 DG DN II Art Lens for Sony E-Mount",
        "merchant_category": "Cameras & Optics > Camera & Video Camera Lenses > Camera Lenses",
        "search_price": "1099.00",
        "currency": "USD",
        "merchant_deep_link": "https://www.keh.com/shop/sigma-24-70.html",
        "brand_name": "Sigma",
        "mpn": "578965",
        "condition": "used",
        "merchant_product_category_path": "Used Camera Lenses > Used Mirrorless Camera Lenses > 999",
        "in_stock": "1",
        "is_for_sale": "1",
    }
    row.update(overrides)
    return row


def test_all_active_camera_bodies_are_in_the_keh_public_catalog():
    public_ids = public_product_ids()
    assert "camera-sony-a7-iii-body" in public_ids
    assert "camera-nikon-z5-body" in public_ids
    assert "camera-canon-eos-r5-body" in public_ids
    assert len(public_ids) > 3


def test_keh_sync_and_public_results_accept_camera_outside_old_three_model_pilot(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("KEH_PUBLIC_RESULTS", "true")
    # A stale production allowlist must no longer limit publication to the old pilot.
    monkeypatch.setenv("KEH_PUBLIC_PRODUCT_IDS", "camera-sony-a7-iii-body")
    monkeypatch.setenv("KEH_SHADOW_PRODUCT_IDS", "camera-sony-a7-iii-body")

    normalized = normalize_feed_row(_camera_row(), datetime.now(UTC))
    assert normalized is not None
    assert normalized["matched_product_id"] == "camera-nikon-z5-body"
    assert normalized["match_status"] == "matched"

    run = sync_keh_feed(feed_rows=[_camera_row()])
    assert run["status"] == "success"
    assert run["matched_items"] == 1

    product_match = match_product("Nikon Z5 Body", "cameras")
    assert product_match is not None
    listings = public_keh_listings(product_match.product)
    assert len(listings) == 1
    assert listings[0].provider == "KEH"
    assert listings[0].price == 799.0


def test_public_keh_lens_endpoint_is_tokenless_and_keeps_ebay_out(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("KEH_PUBLIC_RESULTS", "true")
    sync_keh_feed(feed_rows=[_lens_row()])

    client = TestClient(app)
    response = client.get(
        "/api/keh/lenses/public",
        params={
            "mount": "Sony E",
            "lens_type": "Zoom",
            "focal_group": "Standard zoom",
            "brand": "Sigma",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["filtered_model_count"] == 1
    assert payload["summary"]["filtered_listing_count"] == 1
    assert payload["models"][0]["model_name"].startswith("Sigma 24-70mm")
    assert payload["models"][0]["listings"][0]["affiliate_url"].startswith("https://www.awin1.com/")


def test_public_marketplace_search_rejects_ebay_lenses():
    response = TestClient(app).get(
        "/api/search",
        params={
            "q": "Sony FE 85mm f/1.8",
            "category": "lenses",
            "providers": "ebay",
        },
    )
    assert response.status_code == 400
    assert "KEH-only" in response.json()["detail"]


def test_public_keh_lens_endpoint_respects_global_public_switch(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("KEH_PUBLIC_RESULTS", "false")

    response = TestClient(app).get("/api/keh/lenses/public")
    assert response.status_code == 503
