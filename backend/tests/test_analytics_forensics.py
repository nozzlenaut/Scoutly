from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services import analytics_forensics as analytics_forensics_module


def _search_row(at: datetime, query: str, category: str = "cameras") -> dict:
    return {
        "searched_at": at.isoformat(),
        "category": category,
        "query": query,
    }


def test_analytics_forensics_flags_rapid_repeats(monkeypatch) -> None:
    base = datetime(2026, 8, 13, 12, 0, 0, tzinfo=UTC)
    searches = [
        _search_row(base, "Sony A7 III"),
        _search_row(base + timedelta(seconds=10), "Sony A7 III"),
        _search_row(base + timedelta(seconds=35), "Sony A7 III"),
        _search_row(base + timedelta(seconds=70), "Sony A7 III"),
        _search_row(base + timedelta(seconds=20), "Canon R6"),
    ]
    monkeypatch.setattr(
        analytics_forensics_module,
        "_records_for_days",
        lambda _days: (searches, []),
    )

    result = analytics_forensics_module.analytics_forensics(30)

    assert result["rapid_repeat_count"] == 2
    assert result["rapid_repeat_rate"] == 40.0
    assert result["busiest_minute_searches"] == 4
    assert result["minutes_with_10_or_more_searches"] == 0
    assert result["minutes_with_20_or_more_searches"] == 0
    assert result["top_burst_queries"][0]["query"] == "Sony A7 III"
    assert result["top_burst_queries"][0]["rapid_repeats"] == 2


def test_analytics_forensics_reports_minute_spikes_without_fake_repeats(monkeypatch) -> None:
    base = datetime(2026, 8, 13, 13, 0, 0, tzinfo=UTC)
    searches = [
        _search_row(base + timedelta(seconds=index), f"Camera model {index}")
        for index in range(12)
    ]
    monkeypatch.setattr(
        analytics_forensics_module,
        "_records_for_days",
        lambda _days: (searches, []),
    )

    result = analytics_forensics_module.analytics_forensics(30)

    assert result["rapid_repeat_count"] == 0
    assert result["busiest_minute_searches"] == 12
    assert result["minutes_with_10_or_more_searches"] == 1
    assert result["minutes_with_20_or_more_searches"] == 0
