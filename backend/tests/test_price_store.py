from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.services.price_store import (
    build_price_context,
    list_price_snapshots,
    price_overview,
    record_price_snapshot,
)


def _record(observed_at: datetime, prices: list[float]) -> None:
    record_price_snapshot(
        product_id="cpu-intel-core-i9-9900k",
        category="cpus",
        product_label="Intel Core i9-9900K",
        provider="ebay",
        query="Intel Core i9-9900K",
        prices=prices,
        candidate_count=35,
        filtered_count=12,
        source="test",
        observed_at=observed_at,
    )


def test_price_snapshots_upsert_six_hour_bucket(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    start = datetime(2026, 7, 14, 1, 0, tzinfo=UTC)

    _record(start, [200, 220, 240])
    _record(start + timedelta(hours=2), [190, 210, 230])

    snapshots = list_price_snapshots(product_id="cpu-intel-core-i9-9900k", days=3650)
    assert len(snapshots) == 1
    assert snapshots[0]["eligible_count"] == 3
    assert snapshots[0]["lowest_price"] == 190.0
    assert snapshots[0]["median_price"] == 210.0


def test_price_context_waits_for_three_inventory_snapshots(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    start = datetime(2026, 7, 13, 0, 0, tzinfo=UTC)

    _record(start, [200, 210, 220])
    _record(start + timedelta(hours=6), [205, 215, 225])
    early = build_price_context(
        product_id="cpu-intel-core-i9-9900k",
        current_prices=[190, 200, 210],
        days=3650,
    )
    assert early["history_ready"] is False
    assert early["current_best_price"] == 190.0

    _record(start + timedelta(hours=12), [210, 220, 230])
    ready = build_price_context(
        product_id="cpu-intel-core-i9-9900k",
        current_prices=[190, 200, 210],
        days=3650,
    )
    assert ready["history_ready"] is True
    assert ready["snapshot_count"] == 3
    assert ready["typical_low_price"] == 210.0
    assert ready["typical_high_price"] == 220.0
    assert ready["historical_median_price"] == 215.0
    assert ready["current_vs_median_percent"] == -11.6


def test_no_inventory_snapshots_are_kept_for_availability(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    observed = datetime.now(UTC)

    _record(observed, [])
    context = build_price_context(product_id="cpu-intel-core-i9-9900k", days=30)
    overview = price_overview(days=30)

    assert context["snapshot_count"] == 1
    assert context["available_snapshot_count"] == 0
    assert context["availability_rate"] == 0.0
    assert overview["product_count"] == 1
    assert overview["available_latest_count"] == 0


def test_price_overview_requires_admin_token(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    assert client.get("/api/prices/overview").status_code == 401
    response = client.get("/api/prices/overview", params={"token": "secret"})
    assert response.status_code == 200
    assert response.json()["snapshot_count"] == 0


def test_search_response_includes_current_price_context(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("EBAY_CLIENT_ID", raising=False)
    monkeypatch.delenv("EBAY_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    client = TestClient(app)

    response = client.get(
        "/api/search",
        params={"q": "Intel Core i7-12700K", "category": "cpus", "providers": "ebay"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["price_context"]["product_id"] == "cpu-intel-core-i7-12700k"
    assert payload["price_context"]["current_eligible_count"] == 1
    assert payload["price_context"]["history_ready"] is False


def test_admin_collector_runs_small_qa_batch(monkeypatch, tmp_path):
    from app.api import prices as prices_api
    from app.catalog.catalog import match_product
    from app.models.search import PriceContext, SearchDiagnostics

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    monkeypatch.setattr(prices_api, "ebay_config_from_env", lambda: object())
    monkeypatch.setattr(prices_api, "price_overview", lambda **_kwargs: {"products": []})
    monkeypatch.setattr(
        prices_api,
        "load_qa_cases",
        lambda: [
            {
                "id": "cpu-test",
                "query": "Intel Core i7-12700K",
                "category": "cpus",
                "expected_product_id": "cpu-intel-core-i7-12700k",
            }
        ],
    )

    async def fake_search(*_args, **_kwargs):
        return (
            match_product("Intel Core i7-12700K", "cpus"),
            [],
            [],
            SearchDiagnostics(fixed_price_eligible=4),
            PriceContext(
                product_id="cpu-intel-core-i7-12700k",
                snapshot_count=1,
                last_observed_at="2026-07-14T12:00:00+00:00",
            ),
        )

    monkeypatch.setattr(prices_api.search_service, "search_best_deals_with_auctions", fake_search)
    client = TestClient(app)
    response = client.post(
        "/api/prices/collect/qa",
        params={"token": "secret"},
        json={"limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["live_ebay"] is True
    assert payload["collected_count"] == 1
    assert payload["collected"][0]["eligible_count"] == 4
