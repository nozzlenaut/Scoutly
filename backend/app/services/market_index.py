from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from statistics import median
from typing import Any

from app.services.price_store import list_price_snapshots

DEFAULT_HISTORY_DAYS = 3650
DEFAULT_STALE_DAYS = 7
DEFAULT_MIN_SPAN_HOURS = 24
DEFAULT_MIN_CATEGORY_MODELS = 3


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _positive_median(snapshot: dict[str, Any]) -> float | None:
    value = snapshot.get("median_price")
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number <= 0:
        return None
    return number


def build_market_index(
    *,
    days: int = DEFAULT_HISTORY_DAYS,
    stale_days: int = DEFAULT_STALE_DAYS,
    min_span_hours: int = DEFAULT_MIN_SPAN_HOURS,
    min_category_models: int = DEFAULT_MIN_CATEGORY_MODELS,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build an equal-weight used-market direction gauge from stored snapshots.

    Each model contributes one percentage change: its latest qualifying snapshot
    median versus its first qualifying snapshot median inside the requested
    history window. Category movement is the median of those model changes, so
    expensive models and extreme movers cannot dominate the category merely
    because of their dollar price or size of move.

    This intentionally describes movement since each model entered the current
    tracking window. It is not a fixed-basket investment index and should not be
    presented as a 30/90-day return unless every model shares that exact span.
    """

    days = max(1, min(int(days), 3650))
    stale_days = max(1, min(int(stale_days), 365))
    min_span_hours = max(1, min(int(min_span_hours), 24 * 365))
    min_category_models = max(1, min(int(min_category_models), 100))
    observed_now = (now or datetime.now(UTC)).astimezone(UTC)
    stale_cutoff = observed_now - timedelta(days=stale_days)

    snapshots = list_price_snapshots(days=days, limit=25000)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for snapshot in snapshots:
        product_id = str(snapshot.get("product_id") or "").strip()
        provider = str(snapshot.get("provider") or "").strip().lower()
        if not product_id or provider != "ebay":
            continue
        grouped.setdefault(product_id, []).append(snapshot)

    models: list[dict[str, Any]] = []
    for product_id, product_snapshots in grouped.items():
        qualifying: list[tuple[datetime, dict[str, Any], float]] = []
        for snapshot in product_snapshots:
            observed_at = _parse_datetime(snapshot.get("observed_at"))
            median_price = _positive_median(snapshot)
            if observed_at is None or median_price is None:
                continue
            if int(snapshot.get("eligible_count") or 0) <= 0:
                continue
            qualifying.append((observed_at, snapshot, median_price))

        qualifying.sort(key=lambda item: item[0])
        if len(qualifying) < 2:
            continue

        first_at, first_snapshot, first_median = qualifying[0]
        latest_at, latest_snapshot, latest_median = qualifying[-1]
        span_hours = (latest_at - first_at).total_seconds() / 3600
        if span_hours < min_span_hours or latest_at < stale_cutoff:
            continue

        percent_change = ((latest_median - first_median) / first_median) * 100
        if not math.isfinite(percent_change):
            continue

        category = str(latest_snapshot.get("category") or first_snapshot.get("category") or "unknown").strip().lower()
        product_label = str(latest_snapshot.get("product_label") or first_snapshot.get("product_label") or product_id).strip()
        query = str(latest_snapshot.get("query") or first_snapshot.get("query") or product_label).strip()

        models.append(
            {
                "product_id": product_id,
                "category": category,
                "product_label": product_label,
                "query": query,
                "provider": "ebay",
                "baseline_median_price": round(first_median, 2),
                "latest_median_price": round(latest_median, 2),
                "percent_change": round(percent_change, 1),
                "snapshot_count": len(qualifying),
                "first_observed_at": first_at.isoformat(),
                "last_observed_at": latest_at.isoformat(),
                "history_days": round(span_hours / 24, 1),
            }
        )

    models.sort(key=lambda item: (item["category"], item["product_label"].lower(), item["product_id"]))

    category_models: dict[str, list[dict[str, Any]]] = {}
    for model in models:
        category_models.setdefault(model["category"], []).append(model)

    categories: list[dict[str, Any]] = []
    for category, rows in sorted(category_models.items()):
        changes = [
            ((float(row["latest_median_price"]) - float(row["baseline_median_price"])) / float(row["baseline_median_price"])) * 100
            for row in rows
        ]
        median_change = float(median(changes))
        enough_models = len(rows) >= min_category_models
        categories.append(
            {
                "category": category,
                "model_count": len(rows),
                "median_percent_change": round(median_change, 1) if enough_models else None,
                "index_value": round(100 + median_change, 1) if enough_models else None,
                "first_observed_at": min(str(row["first_observed_at"]) for row in rows),
                "last_observed_at": max(str(row["last_observed_at"]) for row in rows),
                "minimum_models_required": min_category_models,
            }
        )

    return {
        "generated_at": observed_now.isoformat(),
        "history_window_days": days,
        "stale_after_days": stale_days,
        "minimum_history_hours": min_span_hours,
        "minimum_category_models": min_category_models,
        "tracked_snapshot_count": len(snapshots),
        "comparable_model_count": len(models),
        "methodology": (
            "Each model compares the median qualifying eBay listing price in its first usable snapshot "
            "with the median in its latest usable snapshot. Each model gets equal weight. A category's "
            "market move is the median percentage change across comparable models; index 100 is each "
            "model's own starting observation. Models need at least two qualifying snapshots, at least "
            f"{min_span_hours} hours of history, and a qualifying observation within the last {stale_days} days."
        ),
        "categories": categories,
        "models": models,
    }
