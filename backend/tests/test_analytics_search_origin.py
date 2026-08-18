import json

from fastapi.testclient import TestClient

from app.main import app


def test_seo_page_search_origin_is_separate_from_demand(monkeypatch, tmp_path):
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
            "analytics_source": "seo_page",
        },
    )
    assert response.status_code == 200

    raw_events = json.loads((tmp_path / "search_events.json").read_text(encoding="utf-8"))
    assert [event["source"] for event in raw_events] == [
        "public",
        "origin:seo_page",
    ]

    digest = client.get(
        "/api/analytics/digest",
        params={"token": "secret", "days": 30},
    )
    assert digest.status_code == 200
    payload = digest.json()

    # The normal public event remains available for click attribution and the
    # existing forensic logic. The origin marker is metadata, not a second
    # counted search.
    assert payload["search_count"] == 1
    assert payload["seo_page_search_count"] == 1
    assert payload["demand_search_count"] == 0
    assert payload["forensics"]["busiest_minute_searches"] == 1

    top = payload["top_searches"][0]
    assert top["label"] == "Sony A7 III Body"
    assert top["searches"] == 1
    assert top["seo_page_searches"] == 1
    assert top["demand_searches"] == 0
    assert "Demand searches excluding tracked SEO-page launches: 0" in payload["summary_text"]
    assert "source tagging starts with this release" in payload["summary_text"]
