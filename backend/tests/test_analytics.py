from fastapi.testclient import TestClient

from app.main import app
from app.services.feedback_store import BadResultReport, log_outbound_click, report_bad_result


def test_analytics_summary_and_clicks(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    log_outbound_click(
        url="https://www.ebay.com/itm/123456789012",
        tracked_url="https://www.ebay.com/itm/123456789012?campid=1234567890&customid=scoutly",
        provider="eBay",
        category="gpus",
        product_id="gpu-nvidia-tesla-p100-16gb",
        query="Tesla P100",
        title="NVIDIA Tesla P100 16GB",
    )

    summary = client.get("/api/analytics/summary", params={"token": "secret"})
    clicks = client.get("/api/analytics/clicks", params={"token": "secret"})

    assert summary.status_code == 200
    assert summary.json()["total_clicks"] == 1
    assert summary.json()["affiliate_clicks"] == 1
    assert clicks.status_code == 200
    assert clicks.json()["clicks"][0]["query"] == "Tesla P100"


def test_analytics_reports_and_optional_token(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    report_bad_result(
        BadResultReport(
            url="https://www.ebay.com/itm/123456789012",
            title="Wrong item",
            provider="eBay",
            category="cameras",
            product_id="camera-sony-a7-iii-body",
            query="Sony A7 III Body",
            reason="wrong_item",
        )
    )

    assert client.get("/api/analytics/reports").status_code == 401
    response = client.get("/api/analytics/reports", params={"token": "secret"})
    assert response.status_code == 200
    assert response.json()["reports"][0]["reason"] == "wrong_item"


def test_analytics_filtered_listings_endpoint(monkeypatch, tmp_path):
    from app.services.feedback_store import log_filtered_listing

    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    log_filtered_listing(
        url="https://www.ebay.com/itm/111111111111",
        title="Canon EOS RP Camera UV Filter Kit",
        provider="eBay",
        category="cameras",
        product_id="camera-canon-eos-rp-body",
        query="Canon EOS RP Body",
        listing_type="fixed_price",
        reasons=["catalog/product match rejected"],
    )

    response = client.get("/api/analytics/filtered", params={"token": "secret"})
    assert response.status_code == 200
    assert response.json()["filtered"][0]["title"] == "Canon EOS RP Camera UV Filter Kit"
    assert response.json()["filtered"][0]["reasons"] == ["catalog/product match rejected"]


def test_manual_filter_rules_endpoint_and_matching(monkeypatch, tmp_path):
    from app.models.listing import Listing
    from app.ranking.scorer import rejection_reasons
    from app.catalog.catalog import match_product

    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    blocked = Listing(
        provider="eBay",
        title="Zotac Nvidia GeForce RTX 3060 12GB Graphics Card GPU PC FAN PROBLEM NOTES",
        price=100,
        shipping=0,
        total_price=100,
        condition="Used",
        url="https://www.ebay.com/itm/123456789012",
    )
    safe = Listing(
        provider="eBay",
        title="Zotac Nvidia GeForce RTX 3060 12GB Graphics Card Tested No Problems",
        price=100,
        shipping=0,
        total_price=100,
        condition="Used",
        url="https://www.ebay.com/itm/999999999999",
    )

    response = client.post(
        "/api/analytics/filter-rules",
        params={"token": "secret"},
        json={
            "phrase": "problem",
            "category": "gpus",
            "except_phrases": ["no problem", "no problems"],
            "note": "testing manual rules",
        },
    )

    assert response.status_code == 200
    rule = response.json()
    assert rule["phrase"] == "problem"

    rules = client.get("/api/analytics/filter-rules", params={"token": "secret"})
    assert rules.status_code == 200
    assert rules.json()["rules"][0]["id"] == rule["id"]

    product = match_product("RTX 3060 12GB", category="gpus").product
    assert any("manual filter" in reason for reason in rejection_reasons(blocked, product))
    assert not any("manual filter" in reason for reason in rejection_reasons(safe, product))

    delete = client.delete(f"/api/analytics/filter-rules/{rule['id']}", params={"token": "secret"})
    assert delete.status_code == 200
    assert client.get("/api/analytics/filter-rules", params={"token": "secret"}).json()["rules"] == []
