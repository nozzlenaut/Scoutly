import json
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from app.main import app


def test_outbound_adds_campaign_id_without_logging_get(monkeypatch, tmp_path):
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
    assert not (tmp_path / "outbound_clicks.json").exists()


def test_outbound_rejects_non_marketplace_url(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EBAY_CLIENT_ID", "client")
    monkeypatch.setenv("EBAY_CLIENT_SECRET", "secret")

    client = TestClient(app, follow_redirects=False)
    assert client.get("/api/out", params={"url": "https://example.com/itm/123"}).status_code == 400
    assert client.post("/api/out/click", params={"url": "https://example.com/itm/123"}).status_code == 400


def test_outbound_preserves_awin_affiliate_link_without_logging_get(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    awin_url = "https://www.awin1.com/pclick.php?p=44680921767&a=2980905&m=89435"

    client = TestClient(app, follow_redirects=False)
    response = client.get(
        "/api/out",
        params={
            "url": awin_url,
            "provider": "KEH",
            "category": "cameras",
            "product_id": "camera-sony-a7-iii-body",
        },
    )

    assert response.status_code == 302
    assert response.headers["location"] == awin_url
    assert not (tmp_path / "outbound_clicks.json").exists()


def test_outbound_adds_awin_click_reference_without_logging_get(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    awin_url = "https://www.awin1.com/pclick.php?p=44680921767&a=2980905&m=89435"

    client = TestClient(app, follow_redirects=False)
    response = client.get(
        "/api/out",
        params={"url": awin_url, "click_ref": "psabc123"},
    )

    assert response.status_code == 302
    params = parse_qs(urlsplit(response.headers["location"]).query)
    assert params["clickref"] == ["psabc123"]
    assert not (tmp_path / "outbound_clicks.json").exists()


def test_browser_confirmed_awin_click_logs_price_page_and_reference(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    awin_url = "https://www.awin1.com/pclick.php?p=44680921767&a=2980905&m=89435"

    client = TestClient(app, follow_redirects=False)
    response = client.post(
        "/api/out/click",
        params={
            "url": awin_url,
            "provider": "KEH",
            "category": "cameras",
            "product_id": "camera-fujifilm-x-s10-body",
            "q": "FUJIFILM X-S10 Body",
            "title": "FUJIFILM X-S10 Mirrorless Camera Body, Black",
            "price": "1314.00",
            "currency": "usd",
            "source_page": "/used/fujifilm-x-s10",
            "click_ref": "psabc123",
        },
    )

    assert response.status_code == 204
    click = json.loads((tmp_path / "outbound_clicks.json").read_text(encoding="utf-8"))[0]
    assert click["listing_price"] == 1314.0
    assert click["currency"] == "USD"
    assert click["source_page"] == "/used/fujifilm-x-s10"
    assert click["affiliate_reference"] == "psabc123"
    assert parse_qs(urlsplit(click["tracked_url"]).query)["clickref"] == ["psabc123"]


def test_browser_confirmed_amazon_click_is_logged(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    amazon_url = "https://www.amazon.com/dp/0593820258?tag=pricesift-20"
    params = {
        "url": amazon_url,
        "provider": "Amazon",
        "category": "books",
        "product_id": "isbn-0593820258",
        "q": "0593820258",
        "title": "Amazon exact product: 0593820258",
        "price": "18.99",
        "currency": "USD",
        "source_page": "/books/0593820258",
    }

    client = TestClient(app, follow_redirects=False)
    redirect_response = client.get("/api/out", params=params)
    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == amazon_url
    assert not (tmp_path / "outbound_clicks.json").exists()

    click_response = client.post("/api/out/click", params=params)
    assert click_response.status_code == 204
    click_text = (tmp_path / "outbound_clicks.json").read_text(encoding="utf-8")
    assert "Amazon" in click_text
    assert '"affiliate_campaign_present": true' in click_text
    assert '"affiliate_reference": "pricesift-20"' in click_text
    assert '"listing_price": 18.99' in click_text
    assert '"source_page": "/books/0593820258"' in click_text


def test_browser_confirmed_ebay_click_logs_metadata(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EBAY_CLIENT_ID", "client")
    monkeypatch.setenv("EBAY_CLIENT_SECRET", "secret")
    monkeypatch.setenv("EBAY_AFFILIATE_CAMPAIGN_ID", "1234567890")
    monkeypatch.setenv("EBAY_AFFILIATE_REFERENCE_ID", "scoutly")

    client = TestClient(app, follow_redirects=False)
    response = client.post(
        "/api/out/click",
        params={
            "url": "https://www.ebay.com/itm/377191325248?customid=scoutly",
            "provider": "eBay",
            "category": "cameras",
            "product_id": "camera-sony-a7-iii-body",
            "q": "Sony A7 III Body",
            "title": "Sony Alpha a7 III",
            "price": "899.95",
            "currency": "USD",
            "source_page": "/used/sony-a7-iii",
            "click_ref": "psebay123",
        },
    )

    assert response.status_code == 204
    click_text = (tmp_path / "outbound_clicks.json").read_text(encoding="utf-8")
    assert "camera-sony-a7-iii-body" in click_text
    assert "affiliate_campaign_present" in click_text
    assert "1234567890" in click_text
    assert '"affiliate_reference": "psebay123"' in click_text
    assert "customid=psebay123" in click_text
