from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.services.market_signals import build_market_signals_from_snapshots


def _snapshot(
    product_id: str,
    label: str,
    observed_at: datetime,
    *,
    median_price: float,
    lowest_price: float,
    eligible_count: int,
    category: str = "gpus",
) -> dict:
    return {
        "product_id": product_id,
        "product_label": label,
        "category": category,
        "provider": "ebay",
        "observed_at": observed_at.isoformat(),
        "median_price": median_price,
        "lowest_price": lowest_price,
        "eligible_count": eligible_count,
    }


def test_price_drop_becomes_video_worthy_signal():
    product_id = "gpu-nvidia-rtx-3080-10gb"
    label = "NVIDIA RTX 3080 10GB"
    snapshots = [
        _snapshot(product_id, label, datetime(2026, 8, 10, tzinfo=UTC), median_price=300, lowest_price=280, eligible_count=10),
        _snapshot(product_id, label, datetime(2026, 8, 12, tzinfo=UTC), median_price=305, lowest_price=285, eligible_count=9),
        _snapshot(product_id, label, datetime(2026, 8, 14, tzinfo=UTC), median_price=295, lowest_price=275, eligible_count=11),
        _snapshot(product_id, label, datetime(2026, 8, 17, tzinfo=UTC), median_price=260, lowest_price=240, eligible_count=12),
    ]

    result = build_market_signals_from_snapshots(snapshots, days=30)

    assert result["ready_product_count"] == 1
    assert result["video_worthy_count"] == 1
    signal = result["signals"][0]
    assert signal["primary_signal"] == "price_drop"
    assert "standout_deal" in signal["signal_tags"]
    assert signal["baseline_median_price"] == 300.0
    assert signal["median_change_percent"] == -13.3
    assert signal["best_vs_baseline_percent"] == -20.0
    assert signal["video_score"] >= 30
    assert signal["video_worthy"] is True
    assert "down 13.3%" in signal["story_angle"]


def test_latest_snapshot_is_not_included_in_its_own_baseline():
    product_id = "gpu-nvidia-rtx-4070-12gb"
    label = "NVIDIA RTX 4070 12GB"
    snapshots = [
        _snapshot(product_id, label, datetime(2026, 8, 10, tzinfo=UTC), median_price=300, lowest_price=285, eligible_count=8),
        _snapshot(product_id, label, datetime(2026, 8, 12, tzinfo=UTC), median_price=300, lowest_price=280, eligible_count=8),
        _snapshot(product_id, label, datetime(2026, 8, 17, tzinfo=UTC), median_price=400, lowest_price=370, eligible_count=8),
    ]

    result = build_market_signals_from_snapshots(snapshots)
    signal = result["signals"][0]

    assert signal["baseline_median_price"] == 300.0
    assert signal["median_change_percent"] == 33.3
    assert signal["primary_signal"] == "price_spike"


def test_insufficient_history_builds_without_inventing_signal():
    product_id = "console-steam-deck-oled"
    label = "Steam Deck OLED"
    snapshots = [
        _snapshot(product_id, label, datetime(2026, 8, 15, tzinfo=UTC), median_price=450, lowest_price=420, eligible_count=7, category="consoles"),
        _snapshot(product_id, label, datetime(2026, 8, 17, tzinfo=UTC), median_price=390, lowest_price=370, eligible_count=8, category="consoles"),
    ]

    result = build_market_signals_from_snapshots(snapshots)

    assert result["product_count"] == 1
    assert result["ready_product_count"] == 0
    assert result["building_product_count"] == 1
    assert result["signal_count"] == 0
    assert result["signals"] == []


def test_category_filter_only_scores_requested_market():
    snapshots = [
        _snapshot("gpu-one", "GPU One", datetime(2026, 8, 10, tzinfo=UTC), median_price=200, lowest_price=190, eligible_count=10),
        _snapshot("gpu-one", "GPU One", datetime(2026, 8, 12, tzinfo=UTC), median_price=200, lowest_price=190, eligible_count=10),
        _snapshot("gpu-one", "GPU One", datetime(2026, 8, 17, tzinfo=UTC), median_price=170, lowest_price=160, eligible_count=10),
        _snapshot("cpu-one", "CPU One", datetime(2026, 8, 10, tzinfo=UTC), median_price=200, lowest_price=190, eligible_count=10, category="cpus"),
        _snapshot("cpu-one", "CPU One", datetime(2026, 8, 12, tzinfo=UTC), median_price=200, lowest_price=190, eligible_count=10, category="cpus"),
        _snapshot("cpu-one", "CPU One", datetime(2026, 8, 17, tzinfo=UTC), median_price=150, lowest_price=140, eligible_count=10, category="cpus"),
    ]

    result = build_market_signals_from_snapshots(snapshots, category="gpus")

    assert result["category"] == "gpus"
    assert result["snapshot_count"] == 3
    assert result["product_count"] == 1
    assert [signal["product_id"] for signal in result["signals"]] == ["gpu-one"]


def test_market_signals_endpoint_requires_admin_and_uses_static_route(monkeypatch):
    from app.api import prices as prices_api

    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    monkeypatch.setattr(
        prices_api,
        "market_signals",
        lambda **kwargs: {
            "window_days": kwargs["days"],
            "category": kwargs["category"],
            "snapshot_count": 10,
            "product_count": 2,
            "ready_product_count": 1,
            "building_product_count": 1,
            "signal_count": 1,
            "video_worthy_count": 1,
            "signals": [{"product_id": "gpu-one", "video_score": 42.0}],
        },
    )
    client = TestClient(app)

    assert client.get("/api/prices/signals").status_code == 401
    response = client.get(
        "/api/prices/signals",
        params={"token": "secret", "days": 30, "limit": 10, "category": "gpus"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["category"] == "gpus"
    assert payload["signals"][0]["video_score"] == 42.0
