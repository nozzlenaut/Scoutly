from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.services.market_index import build_market_index, build_market_index_from_snapshots
from app.services.market_index_audit import audit_market_histories
from app.services.price_store import record_price_snapshot

NOW = datetime(2026, 8, 27, 12, 0, tzinfo=UTC)


def _snapshot(
    product_id: str,
    observed_at: datetime,
    median_price: float | None,
    *,
    eligible_count: int = 3,
    category: str = "consoles",
    provider: str = "ebay",
) -> dict:
    return {
        "product_id": product_id,
        "product_label": product_id,
        "query": product_id,
        "category": category,
        "provider": provider,
        "observed_at": observed_at.isoformat(),
        "median_price": median_price,
        "eligible_count": eligible_count,
        "candidate_count": 20,
        "filtered_count": 5,
        "sample_prices": [median_price] * eligible_count if median_price is not None else [],
        "source": "test",
    }


def _series(
    product_id: str,
    medians: list[float | None],
    *,
    eligible_count: int = 3,
    step_hours: int = 6,
    category: str = "consoles",
) -> list[dict]:
    start = NOW - timedelta(hours=step_hours * (len(medians) - 1))
    return [
        _snapshot(
            product_id,
            start + timedelta(hours=step_hours * index),
            value,
            eligible_count=eligible_count,
            category=category,
        )
        for index, value in enumerate(medians)
    ]


def _row(result: dict, product_id: str) -> dict:
    return next(row for row in result["models"] if row["product_id"] == product_id)


def test_single_bad_first_observation_does_not_become_permanent_baseline():
    result = build_market_index_from_snapshots(
        _series("ps5", [55, 400, 405, 410, 408]),
        observed_now=NOW,
        min_category_models=1,
    )
    row = _row(result, "ps5")
    assert row["baseline_median_price"] == 405.0
    assert row["latest_median_price"] == 408.0
    assert row["percent_change"] == 0.7
    assert row["status"] == "comparable"


def test_sparse_and_zero_inventory_do_not_qualify():
    rows = _series("sparse", [100, 110, 120, 130, 140], eligible_count=2)
    rows.append(_snapshot("empty", NOW, None, eligible_count=0))
    result = build_market_index_from_snapshots(rows, observed_now=NOW, min_category_models=1)

    sparse = _row(result, "sparse")
    empty = _row(result, "empty")
    assert sparse["status"] == "insufficient_history"
    assert sparse["snapshot_count"] == 0
    assert sparse["percent_change"] is None
    assert empty["status"] == "insufficient_history"
    assert empty["percent_change"] is None


def test_newly_added_model_is_shown_as_insufficient_history():
    result = build_market_index_from_snapshots(
        _series("new-model", [300, 305, 310, 315]),
        observed_now=NOW,
        min_category_models=1,
    )
    row = _row(result, "new-model")
    assert row["status"] == "insufficient_history"
    assert row["percent_change"] is None
    assert "Needs 5 qualifying snapshots" in row["insufficient_reason"]


def test_first_five_qualifying_snapshots_must_span_24_hours():
    result = build_market_index_from_snapshots(
        _series("too-fast", [100, 101, 102, 103, 104], step_hours=5),
        observed_now=NOW,
        min_category_models=1,
    )
    row = _row(result, "too-fast")
    assert row["status"] == "insufficient_history"
    assert "span only" in row["insufficient_reason"]


def test_large_legitimate_move_survives_smoothing():
    result = build_market_index_from_snapshots(
        _series("real-move", [100, 101, 99, 100, 100, 195, 200, 205]),
        observed_now=NOW,
        min_category_models=1,
    )
    row = _row(result, "real-move")
    assert row["baseline_median_price"] == 100.0
    assert row["latest_median_price"] == 200.0
    assert row["percent_change"] == 100.0


def test_old_bad_observation_followed_by_stable_data_is_bounded():
    result = build_market_index_from_snapshots(
        _series("wii-u", [43, 168, 169, 170, 169, 171, 170]),
        observed_now=NOW,
        min_category_models=1,
    )
    row = _row(result, "wii-u")
    assert row["baseline_median_price"] == 169.0
    assert row["latest_median_price"] == 170.0
    assert row["percent_change"] == 0.6


def test_missing_snapshots_are_ignored_and_non_ebay_history_is_excluded():
    rows = _series("mixed", [100, 105, 110, 115, 120, 125])
    rows.insert(2, _snapshot("mixed", NOW - timedelta(hours=33), None, eligible_count=0))
    rows.extend(
        _snapshot("keh-only", NOW - timedelta(hours=6 * index), 100, provider="keh")
        for index in range(5)
    )
    result = build_market_index_from_snapshots(rows, observed_now=NOW, min_category_models=1)

    assert _row(result, "mixed")["status"] == "comparable"
    assert all(row["product_id"] != "keh-only" for row in result["models"])


def test_category_index_uses_only_comparable_models():
    rows: list[dict] = []
    rows += _series("a", [100, 100, 100, 100, 100, 110, 110], category="cameras")
    rows += _series("b", [100, 100, 100, 100, 100, 90, 90], category="cameras")
    rows += _series("c", [100, 100, 100, 100, 100, 120, 120], category="cameras")
    rows += _series("new", [100, 101, 102, 103], category="cameras")

    result = build_market_index_from_snapshots(rows, observed_now=NOW)
    category = result["categories"][0]
    assert category["model_count"] == 3
    assert category["tracked_model_count"] == 4
    assert category["median_percent_change"] == 10.0
    assert category["index_value"] == 110.0


def test_audit_exposes_legacy_and_fixed_snapshot_windows():
    report = audit_market_histories(_series("ps5", [55, 400, 405, 410, 408]), now=NOW)
    row = report[0]
    assert row["legacy"]["baseline_price"] == 55
    assert row["legacy"]["current_price"] == 408
    assert row["legacy"]["percent_change"] > 600
    assert row["fixed"]["baseline_price"] == 405
    assert row["fixed"]["current_price"] == 408
    assert len(row["baseline_snapshots_used"]) == 5
    assert len(row["current_snapshots_used"]) == 3


def test_market_index_store_integration_and_public_endpoint(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")

    start = NOW - timedelta(hours=24)
    for index, median_price in enumerate([100, 101, 102, 103, 104]):
        record_price_snapshot(
            product_id="stored",
            category="cameras",
            product_label="Stored Camera",
            provider="ebay",
            query="Stored Camera",
            prices=[median_price - 10, median_price, median_price + 10],
            candidate_count=20,
            filtered_count=5,
            source="test",
            observed_at=start + timedelta(hours=6 * index),
        )

    result = build_market_index(now=NOW, min_category_models=1)
    assert _row(result, "stored")["status"] == "comparable"

    client = TestClient(app)
    response = client.get("/api/prices/market-index")
    assert response.status_code == 200
    payload = response.json()
    assert "categories" in payload
    assert "models" in payload
    assert "methodology" in payload
