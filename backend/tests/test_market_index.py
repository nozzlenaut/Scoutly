from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.services.market_index import build_market_index
from app.services.price_store import record_price_snapshot


def _record(
    *,
    product_id: str,
    label: str,
    observed_at: datetime,
    prices: list[float],
    category: str = "cameras",
    provider: str = "ebay",
) -> None:
    record_price_snapshot(
        product_id=product_id,
        category=category,
        product_label=label,
        provider=provider,
        query=label,
        prices=prices,
        candidate_count=20,
        filtered_count=5,
        source="test",
        observed_at=observed_at,
    )


def test_market_index_uses_model_medians_and_median_percent_change(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    now = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
    start = now - timedelta(days=4)

    # Lowest listing stays at $100. The model still moves +10% because the
    # snapshot median moves from $200 to $220.
    _record(product_id="camera-a", label="Camera A", observed_at=start, prices=[100, 200, 300])
    _record(product_id="camera-a", label="Camera A", observed_at=now, prices=[100, 220, 300])

    _record(product_id="camera-b", label="Camera B", observed_at=start, prices=[180, 200, 220])
    _record(product_id="camera-b", label="Camera B", observed_at=now, prices=[162, 180, 198])

    _record(product_id="camera-c", label="Camera C", observed_at=start, prices=[90, 100, 110])
    _record(product_id="camera-c", label="Camera C", observed_at=now, prices=[108, 120, 132])

    result = build_market_index(now=now)

    assert result["comparable_model_count"] == 3
    rows = {row["product_id"]: row for row in result["models"]}
    assert rows["camera-a"]["baseline_median_price"] == 200.0
    assert rows["camera-a"]["latest_median_price"] == 220.0
    assert rows["camera-a"]["percent_change"] == 10.0
    assert rows["camera-b"]["percent_change"] == -10.0
    assert rows["camera-c"]["percent_change"] == 20.0

    category = result["categories"][0]
    assert category["category"] == "cameras"
    assert category["model_count"] == 3
    assert category["median_percent_change"] == 10.0
    assert category["index_value"] == 110.0


def test_market_index_excludes_stale_short_and_non_ebay_history(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    now = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)

    # Good row.
    _record(product_id="good", label="Good", observed_at=now - timedelta(days=2), prices=[100, 110, 120])
    _record(product_id="good", label="Good", observed_at=now, prices=[110, 120, 130])

    # Latest usable observation is too old.
    _record(product_id="stale", label="Stale", observed_at=now - timedelta(days=20), prices=[100, 110, 120])
    _record(product_id="stale", label="Stale", observed_at=now - timedelta(days=10), prices=[110, 120, 130])

    # Two observations, but not enough elapsed time to count as market movement.
    _record(product_id="short", label="Short", observed_at=now - timedelta(hours=6), prices=[100, 110, 120])
    _record(product_id="short", label="Short", observed_at=now, prices=[110, 120, 130])

    # Specialty-retailer history is intentionally not mixed into the eBay index.
    _record(product_id="keh-only", label="KEH Only", observed_at=now - timedelta(days=2), prices=[100, 110, 120], provider="keh")
    _record(product_id="keh-only", label="KEH Only", observed_at=now, prices=[110, 120, 130], provider="keh")

    result = build_market_index(now=now, min_category_models=1)

    assert [row["product_id"] for row in result["models"]] == ["good"]
    assert result["categories"][0]["index_value"] is not None


def test_category_index_waits_for_three_comparable_models(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    now = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)

    for product_id in ("one", "two"):
        _record(product_id=product_id, label=product_id.title(), observed_at=now - timedelta(days=2), prices=[100, 110, 120])
        _record(product_id=product_id, label=product_id.title(), observed_at=now, prices=[110, 120, 130])

    result = build_market_index(now=now)

    assert result["comparable_model_count"] == 2
    assert result["categories"][0]["model_count"] == 2
    assert result["categories"][0]["median_percent_change"] is None
    assert result["categories"][0]["index_value"] is None


def test_market_index_endpoint_is_public(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    response = client.get("/api/prices/market-index")

    assert response.status_code == 200
    payload = response.json()
    assert "categories" in payload
    assert "models" in payload
    assert "methodology" in payload
