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


def test_light_analytics_digest_is_paste_ready_and_private(monkeypatch, tmp_path):
    from app.services.analytics_store import SearchEvent, analytics_digest, log_search_event

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))

    log_search_event(
        SearchEvent(
            category="cameras",
            query="Sony A7 IV",
            product_id="camera-sony-a7-iv-body",
            product_label="Sony A7 IV Body",
            resolved=True,
            result_count=3,
            provider_counts={"eBay": 2, "KEH": 1},
            candidate_count=35,
            filtered_count=20,
            no_inventory=False,
            us_only=False,
        )
    )
    log_search_event(
        SearchEvent(
            category="gpus",
            query="RTX 3070 8GB",
            product_id="gpu-nvidia-geforce-rtx-3070-8gb",
            product_label="NVIDIA GeForce RTX 3070 8GB",
            resolved=True,
            result_count=0,
            provider_counts={},
            candidate_count=35,
            filtered_count=35,
            no_inventory=True,
            us_only=True,
        )
    )

    digest = analytics_digest(30)

    assert digest["search_count"] == 2
    assert digest["with_results_count"] == 1
    assert digest["no_result_count"] == 1
    assert digest["us_only_count"] == 1
    assert digest["provider_shown_counts"] == {"eBay": 2, "KEH": 1}
    assert "PriceSift analytics — last 30 days" in digest["summary_text"]
    assert "No IP addresses" in digest["privacy_note"]


def test_light_analytics_digest_endpoint_requires_admin(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    assert client.get("/api/analytics/digest").status_code == 401
    response = client.get("/api/analytics/digest", params={"token": "secret", "days": 7})
    assert response.status_code == 200
    assert response.json()["days"] == 7


def test_awin_click_is_counted_as_affiliate(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))

    log_outbound_click(
        url="https://www.awin1.com/pclick.php?p=123&a=456&m=89435",
        tracked_url="https://www.awin1.com/pclick.php?p=123&a=456&m=89435",
        provider="KEH",
        category="cameras",
        product_id="camera-sony-a7-iv-body",
        query="Sony A7 IV",
        title="Sony A7 IV EX+",
    )

    from app.services.analytics_store import analytics_digest
    digest = analytics_digest(30)
    assert digest["click_count"] == 1
    assert digest["affiliate_click_count"] == 1
    assert digest["provider_click_counts"] == {"KEH": 1}


def test_public_search_can_record_light_analytics(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    response = client.get(
        "/api/search",
        params={
            "q": "Sony A7 III Body",
            "category": "cameras",
            "analytics": "true",
            "us_only": "true",
        },
    )
    assert response.status_code == 200

    digest = client.get("/api/analytics/digest", params={"token": "secret", "days": 30})
    assert digest.status_code == 200
    payload = digest.json()
    assert payload["search_count"] == 1
    assert payload["us_only_count"] == 1
    assert payload["category_rows"][0]["category"] == "cameras"
