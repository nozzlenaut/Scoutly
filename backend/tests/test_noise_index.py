from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.services.noise_index import build_noise_index_from_records

NOW = datetime(2026, 8, 27, 12, 0, tzinfo=UTC)


def _snapshot(
    product_id: str,
    *,
    candidates: int,
    filtered: int,
    eligible: int,
    category: str = "cameras",
    age_hours: int = 1,
) -> dict:
    return {
        "product_id": product_id,
        "product_label": product_id,
        "query": product_id,
        "category": category,
        "provider": "ebay",
        "observed_at": (NOW - timedelta(hours=age_hours)).isoformat(),
        "candidate_count": candidates,
        "filtered_count": filtered,
        "eligible_count": eligible,
    }


def _event(product_id: str, reasons: list[str], age_hours: int = 1) -> dict:
    return {
        "product_id": product_id,
        "filtered_at": (NOW - timedelta(hours=age_hours)).isoformat(),
        "reasons": reasons,
    }


def test_noise_rate_excludes_duplicates_and_reports_them_separately():
    result = build_noise_index_from_records(
        [_snapshot("r10", candidates=100, filtered=40, eligible=50)],
        [],
        generated_at=NOW,
    )
    row = result["models"][0]
    assert row["noise_rate"] == 40.0
    assert row["duplicates_removed"] == 10
    assert row["eligible_count"] == 50


def test_weighted_category_rate_uses_underlying_candidate_counts():
    result = build_noise_index_from_records(
        [
            _snapshot("big", candidates=100, filtered=20, eligible=80),
            _snapshot("small", candidates=20, filtered=10, eligible=10),
        ],
        [],
        generated_at=NOW,
    )
    category = result["categories"][0]
    assert category["candidate_count"] == 120
    assert category["filtered_count"] == 30
    assert category["noise_rate"] == 25.0


def test_zero_candidates_have_no_rate_and_cannot_rank():
    result = build_noise_index_from_records(
        [_snapshot("empty", candidates=0, filtered=0, eligible=0)],
        [],
        generated_at=NOW,
    )
    assert result["models"][0]["noise_rate"] is None
    assert result["noisiest"] == []
    assert result["categories"][0]["noise_rate"] is None


def test_minimum_sample_threshold_blocks_tiny_noisy_searches():
    result = build_noise_index_from_records(
        [
            _snapshot("tiny", candidates=5, filtered=5, eligible=0),
            _snapshot("real", candidates=20, filtered=15, eligible=5),
        ],
        [],
        generated_at=NOW,
        min_ranking_candidates=20,
    )
    assert [row["product_id"] for row in result["noisiest"]] == ["real"]


def test_overlapping_rejection_reasons_do_not_change_noise_numerator():
    result = build_noise_index_from_records(
        [_snapshot("overlap", candidates=50, filtered=10, eligible=40)],
        [
            _event("overlap", ["wrong model", "broken"]),
            _event("overlap", ["wrong model", "seller quality"]),
        ],
        generated_at=NOW,
    )
    row = result["models"][0]
    assert row["noise_rate"] == 20.0
    assert row["filtered_count"] == 10
    assert sum(reason["count"] for reason in row["rejection_reasons"]) == 4


def test_missing_reason_history_is_not_invented():
    result = build_noise_index_from_records(
        [_snapshot("legacy", candidates=30, filtered=10, eligible=20)],
        [],
        generated_at=NOW,
    )
    row = result["models"][0]
    assert row["rejection_reasons"] == []
    assert row["rejection_reason_breakdown_available"] is False
    assert result["historical_trends_available"] is False
    assert result["snapshot_mode"] == "current_marketplace_snapshot"


def test_latest_snapshot_wins_and_stale_models_are_excluded():
    result = build_noise_index_from_records(
        [
            _snapshot("r10", candidates=40, filtered=20, eligible=20, age_hours=48),
            _snapshot("r10", candidates=80, filtered=20, eligible=60, age_hours=1),
            _snapshot("stale", candidates=80, filtered=20, eligible=60, age_hours=24 * 8),
        ],
        [],
        generated_at=NOW,
        stale_days=7,
    )
    assert [row["product_id"] for row in result["models"]] == ["r10"]
    assert result["models"][0]["candidate_count"] == 80
    assert result["stale_model_count"] == 1


def test_noise_index_endpoint_is_public(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    response = client.get("/api/prices/noise-index")

    assert response.status_code == 200
    payload = response.json()
    assert payload["snapshot_mode"] == "current_marketplace_snapshot"
    assert payload["historical_trends_available"] is False
    assert "models" in payload
    assert "categories" in payload
