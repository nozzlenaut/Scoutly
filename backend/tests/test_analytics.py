from fastapi.testclient import TestClient

from app.main import app
from app.services.feedback_store import BadResultReport, log_outbound_click, report_bad_result


def test_analytics_summary_and_clicks(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
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

    summary = client.get("/api/analytics/summary")
    clicks = client.get("/api/analytics/clicks")

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
