import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.services import market_price_collector as collector


def test_tracked_price_cases_filters_to_high_priority_market_products(monkeypatch):
    monkeypatch.delenv("SCOUTLY_PRICE_TRACKING_CATEGORIES", raising=False)
    cases = [
        {
            "id": "console-ps5",
            "category": "consoles",
            "query": "PS5",
            "expected_product_id": "console-playstation-5",
            "expected_label": "PlayStation 5",
            "priority": "high",
        },
        {
            "id": "console-ps5-duplicate",
            "category": "consoles",
            "query": "PlayStation 5",
            "expected_product_id": "console-playstation-5",
            "expected_label": "PlayStation 5",
            "priority": "high",
        },
        {
            "id": "gpu-4070",
            "category": "gpus",
            "query": "RTX 4070",
            "expected_product_id": "gpu-rtx-4070",
            "expected_label": "RTX 4070",
            "priority": "high",
        },
        {
            "id": "camera-a7iii",
            "category": "cameras",
            "query": "Sony A7 III",
            "expected_product_id": "camera-sony-a7-iii-body",
            "priority": "high",
        },
        {
            "id": "cpu-medium",
            "category": "cpus",
            "query": "Intel Core i5",
            "expected_product_id": "cpu-medium",
            "priority": "medium",
        },
    ]

    tracked = collector.tracked_price_cases(cases)

    assert [case["expected_product_id"] for case in tracked] == [
        "console-playstation-5",
        "gpu-rtx-4070",
    ]


def test_tracked_price_categories_can_be_overridden(monkeypatch):
    monkeypatch.setenv("SCOUTLY_PRICE_TRACKING_CATEGORIES", "cameras, consoles")
    cases = [
        {
            "id": "camera-a7iii",
            "category": "cameras",
            "query": "Sony A7 III",
            "expected_product_id": "camera-sony-a7-iii-body",
            "priority": "high",
        },
        {
            "id": "gpu-4070",
            "category": "gpus",
            "query": "RTX 4070",
            "expected_product_id": "gpu-rtx-4070",
            "priority": "high",
        },
    ]

    tracked = collector.tracked_price_cases(cases)

    assert [case["expected_product_id"] for case in tracked] == [
        "camera-sony-a7-iii-body"
    ]


def test_due_tracked_price_cases_prioritizes_unseen_then_oldest():
    now = datetime(2026, 8, 17, 10, 0, tzinfo=UTC)
    cases = [
        {"category": "consoles", "query": "A", "expected_product_id": "a"},
        {"category": "consoles", "query": "B", "expected_product_id": "b"},
        {"category": "gpus", "query": "C", "expected_product_id": "c"},
    ]
    overview = {
        "products": [
            {
                "product_id": "b",
                "last_observed_at": (now - timedelta(hours=30)).isoformat(),
            },
            {
                "product_id": "c",
                "last_observed_at": (now - timedelta(hours=5)).isoformat(),
            },
        ]
    }

    due = collector.due_tracked_price_cases(
        cases,
        overview,
        now=now,
        min_age_hours=20,
    )

    assert [case["expected_product_id"] for case in due] == ["a", "b"]


def test_collect_tracked_price_batch_uses_existing_search_pipeline(monkeypatch):
    now = datetime(2026, 8, 17, 10, 0, tzinfo=UTC)
    case = {
        "id": "console-ps5",
        "category": "consoles",
        "query": "PS5",
        "expected_product_id": "console-playstation-5",
        "expected_label": "PlayStation 5",
        "priority": "high",
    }
    observed_calls = []

    monkeypatch.setattr(collector, "ebay_config_from_env", lambda: object())
    monkeypatch.setattr(collector, "tracked_price_cases", lambda: [case])
    monkeypatch.setattr(collector, "price_overview", lambda **_kwargs: {"products": []})
    monkeypatch.setattr(
        collector,
        "resolve_discoverable_product",
        lambda _query, _category: SimpleNamespace(
            product=SimpleNamespace(id="console-playstation-5")
        ),
    )

    async def fake_search(*args, **kwargs):
        observed_calls.append((args, kwargs))
        return (
            SimpleNamespace(product=SimpleNamespace(id="console-playstation-5")),
            [SimpleNamespace()],
            [],
            SimpleNamespace(fixed_price_eligible=7),
            SimpleNamespace(
                snapshot_count=4,
                last_observed_at="2026-08-17T10:00:00+00:00",
            ),
        )

    monkeypatch.setattr(
        collector.search_service,
        "search_best_deals_with_auctions",
        fake_search,
    )

    result = asyncio.run(collector.collect_tracked_price_batch(limit=5, now=now))

    assert result["enabled"] is True
    assert result["tracked_count"] == 1
    assert result["due_count"] == 1
    assert result["collected_count"] == 1
    assert result["collected"][0]["eligible_count"] == 7
    assert observed_calls[0][0] == ("PS5", ["ebay"], "consoles")
    assert observed_calls[0][1]["include_auctions"] is False
    assert observed_calls[0][1]["snapshot_source"] == "scheduled_tracker"


def test_collect_tracked_price_batch_refuses_identity_mismatch(monkeypatch):
    case = {
        "id": "console-ps5",
        "category": "consoles",
        "query": "PS5",
        "expected_product_id": "console-playstation-5",
        "priority": "high",
    }
    search_called = False

    monkeypatch.setattr(collector, "ebay_config_from_env", lambda: object())
    monkeypatch.setattr(collector, "tracked_price_cases", lambda: [case])
    monkeypatch.setattr(collector, "price_overview", lambda **_kwargs: {"products": []})
    monkeypatch.setattr(
        collector,
        "resolve_discoverable_product",
        lambda _query, _category: SimpleNamespace(
            product=SimpleNamespace(id="console-playstation-5-slim")
        ),
    )

    async def fake_search(*_args, **_kwargs):
        nonlocal search_called
        search_called = True
        raise AssertionError("search should not run after identity mismatch")

    monkeypatch.setattr(
        collector.search_service,
        "search_best_deals_with_auctions",
        fake_search,
    )

    result = asyncio.run(collector.collect_tracked_price_batch(limit=5))

    assert search_called is False
    assert result["collected_count"] == 0
    assert result["skipped_identity_count"] == 1


def test_price_tracking_can_be_disabled_without_ebay(monkeypatch):
    monkeypatch.delenv("SCOUTLY_PRICE_TRACKING_ENABLED", raising=False)
    monkeypatch.setattr(collector, "ebay_config_from_env", lambda: None)

    assert collector.price_tracking_enabled() is False

    result = asyncio.run(collector.collect_tracked_price_batch())
    assert result["enabled"] is False
    assert result["collected_count"] == 0
