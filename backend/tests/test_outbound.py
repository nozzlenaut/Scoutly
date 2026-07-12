from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from app.main import app


def test_outbound_adds_campaign_id_to_partial_ebay_url(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EBAY_CLIENT_ID", "client")
    monkeypatch.setenv("EBAY_CLIENT_SECRET", "secret")
    monkeypatch.setenv("EBAY_AFFILIATE_CAMPAIGN_ID", "1234567890")
    monkeypatch.setenv("EBAY_AFFILIATE_REFERENCE_ID", "scoutly")

    partial_url = "https://www.ebay.com/itm/377191325248?customid=scoutly&toolid=10049"
    client = TestClient(app, follow_redirects=False)
    response = client.get("/api/out", params={"url": partial_url})

    assert response.status_code == 302
    location = response.headers["location"]
    params = parse_qs(urlsplit(location).query)
    assert params["campid"] == ["1234567890"]
    assert params["customid"] == ["scoutly"]
    assert params["toolid"] == ["10049"]
    assert params["mkevt"] == ["1"]
    assert params["mkcid"] == ["1"]
    assert params["mkrid"] == ["711-53200-19255-0"]


def test_outbound_rejects_non_ebay_url(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EBAY_CLIENT_ID", "client")
    monkeypatch.setenv("EBAY_CLIENT_SECRET", "secret")

    client = TestClient(app, follow_redirects=False)
    response = client.get("/api/out", params={"url": "https://example.com/itm/123"})

    assert response.status_code == 400


def test_outbound_logs_click_metadata(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EBAY_CLIENT_ID", "client")
    monkeypatch.setenv("EBAY_CLIENT_SECRET", "secret")
    monkeypatch.setenv("EBAY_AFFILIATE_CAMPAIGN_ID", "1234567890")
    monkeypatch.setenv("EBAY_AFFILIATE_REFERENCE_ID", "scoutly")

    client = TestClient(app, follow_redirects=False)
    response = client.get(
        "/api/out",
        params={
            "url": "https://www.ebay.com/itm/377191325248?customid=scoutly",
            "provider": "eBay",
            "category": "cameras",
            "product_id": "camera-sony-a7-iii-body",
            "q": "Sony A7 III Body",
            "title": "Sony Alpha a7 III",
        },
    )

    assert response.status_code == 302
    click_log = tmp_path / "outbound_clicks.json"
    assert click_log.exists()
    assert "camera-sony-a7-iii-body" in click_log.read_text(encoding="utf-8")
    assert "affiliate_campaign_present" in click_log.read_text(encoding="utf-8")
