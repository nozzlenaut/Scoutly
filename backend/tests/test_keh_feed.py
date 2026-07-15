from fastapi.testclient import TestClient

from app.main import app
from app.services.keh_feed import (
    classify_keh_product,
    keh_overview,
    normalize_feed_row,
    parse_keh_grade,
    sync_keh_feed,
)
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
