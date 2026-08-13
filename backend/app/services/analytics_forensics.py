from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from app.services.analytics_store import _normalize_unresolved_query, _parse_dt, _records_for_days


def analytics_forensics(days: int = 30) -> dict[str, Any]:
    days = max(1, min(days, 365))
    searches, _clicks = _records_for_days(days)
    ordered = sorted(
        searches,
        key=lambda row: _parse_dt(row.get("searched_at")) or datetime.min.replace(tzinfo=UTC),
    )

    previous_by_query: dict[tuple[str, str], datetime] = {}
    rapid_repeats: Counter[tuple[str, str]] = Counter()
    minute_counts: Counter[str] = Counter()

    for row in ordered:
        searched_at = _parse_dt(row.get("searched_at"))
        if searched_at is None:
            continue
        category = str(row.get("category") or "unknown")
        normalized_query = _normalize_unresolved_query(row.get("query"))
        if not normalized_query:
            continue
        key = (category, normalized_query)
        previous = previous_by_query.get(key)
        if previous is not None and (searched_at - previous).total_seconds() <= 30:
            rapid_repeats[key] += 1
        previous_by_query[key] = searched_at
        minute_counts[searched_at.strftime("%Y-%m-%dT%H:%MZ")] += 1

    search_count = len(searches)
    rapid_repeat_count = sum(rapid_repeats.values())
    busiest_minute, busiest_minute_searches = (None, 0)
    if minute_counts:
        busiest_minute, busiest_minute_searches = minute_counts.most_common(1)[0]

    top_burst_queries = []
    for (category, normalized_query), count in rapid_repeats.most_common(10):
        representative = next(
            (
                str(row.get("query") or "").strip()
                for row in reversed(ordered)
                if str(row.get("category") or "unknown") == category
                and _normalize_unresolved_query(row.get("query")) == normalized_query
            ),
            normalized_query,
        )
        top_burst_queries.append(
            {
                "category": category,
                "query": representative,
                "rapid_repeats": count,
            }
        )

    return {
        "rapid_repeat_window_seconds": 30,
        "rapid_repeat_count": rapid_repeat_count,
        "rapid_repeat_rate": round((rapid_repeat_count / search_count) * 100, 1) if search_count else None,
        "busiest_minute": busiest_minute,
        "busiest_minute_searches": busiest_minute_searches,
        "minutes_with_10_or_more_searches": sum(count >= 10 for count in minute_counts.values()),
        "minutes_with_20_or_more_searches": sum(count >= 20 for count in minute_counts.values()),
        "top_burst_queries": top_burst_queries,
        "note": "Rapid repeats mean the same normalized category/query was logged again within 30 seconds. This is a diagnostic signal, not proof of automation.",
    }
