from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from statistics import median
from typing import Any, Iterable

from app.services.price_store import list_price_snapshots

DEFAULT_HISTORY_DAYS = 3650
DEFAULT_STALE_DAYS = 7
DEFAULT_MIN_SPAN_HOURS = 24
DEFAULT_MIN_CATEGORY_MODELS = 3
DEFAULT_MIN_ELIGIBLE_LISTINGS = 3
DEFAULT_MIN_QUALIFYING_SNAPSHOTS = 5
DEFAULT_BASELINE_SNAPSHOTS = 5
DEFAULT_CURRENT_SNAPSHOTS = 3


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


def qualifying_snapshots(
    snapshots: Iterable[dict[str, Any]],
    *,
    min_eligible_listings: int = DEFAULT_MIN_ELIGIBLE_LISTINGS,
) -> list[tuple[datetime, dict[str, Any], float]]:
    """Return chronologically sorted snapshots safe enough for index pricing."""
    qualified: list[tuple[datetime, dict[str, Any], float]] = []
    for snapshot in snapshots:
        observed_at = _parse_datetime(snapshot.get("observed_at"))
        median_price = _positive_median(snapshot)
        if observed_at is None or median_price is None:
            continue
        if int(snapshot.get("eligible_count") or 0) < min_eligible_listings:
            continue
        qualified.append((observed_at, snapshot, median_price))
    qualified.sort(key=lambda item: item[0])
    return qualified


def evaluate_model_history(
    product_id: str,
    product_snapshots: list[dict[str, Any]],
    *,
    observed_now: datetime,
    stale_days: int = DEFAULT_STALE_DAYS,
    min_span_hours: int = DEFAULT_MIN_SPAN_HOURS,
    min_eligible_listings: int = DEFAULT_MIN_ELIGIBLE_LISTINGS,
    min_qualifying_snapshots: int = DEFAULT_MIN_QUALIFYING_SNAPSHOTS,
    baseline_snapshot_count: int = DEFAULT_BASELINE_SNAPSHOTS,
    current_snapshot_count: int = DEFAULT_CURRENT_SNAPSHOTS,
) -> dict[str, Any]:
    """Evaluate one model without mutating its stored history."""
    qualifying = qualifying_snapshots(
        product_snapshots,
        min_eligible_listings=min_eligible_listings,
    )

    latest_source = product_snapshots[0] if product_snapshots else {}
    latest_qualified = qualifying[-1] if qualifying else None
    first_qualified = qualifying[0] if qualifying else None
    latest_snapshot = latest_qualified[1] if latest_qualified else latest_source
    first_snapshot = first_qualified[1] if first_qualified else latest_source

    category = str(
        latest_snapshot.get("category") or first_snapshot.get("category") or "unknown"
    ).strip().lower()
    product_label = str(
        latest_snapshot.get("product_label")
        or first_snapshot.get("product_label")
        or product_id
    ).strip()
    query = str(
        latest_snapshot.get("query") or first_snapshot.get("query") or product_label
    ).strip()

    first_at = first_qualified[0] if first_qualified else None
    latest_at = latest_qualified[0] if latest_qualified else None
    history_hours = (
        (latest_at - first_at).total_seconds() / 3600
        if first_at is not None and latest_at is not None
        else 0.0
    )

    status = "insufficient_history"
    insufficient_reason: str | None = None
    baseline_median: float | None = None
    current_median: float | None = None
    percent_change: float | None = None

    if len(qualifying) < min_qualifying_snapshots:
        insufficient_reason = (
            f"Needs {min_qualifying_snapshots} qualifying snapshots with at least "
            f"{min_eligible_listings} eligible listings each; has {len(qualifying)}."
        )
    else:
        initial = qualifying[:baseline_snapshot_count]
        initial_span_hours = (initial[-1][0] - initial[0][0]).total_seconds() / 3600
        if initial_span_hours < min_span_hours:
            insufficient_reason = (
                f"Initial {baseline_snapshot_count} qualifying snapshots span only "
                f"{initial_span_hours:.1f} hours; needs at least {min_span_hours}."
            )
        elif latest_at is None or latest_at < observed_now - timedelta(days=stale_days):
            status = "stale"
            insufficient_reason = f"Latest qualifying snapshot is older than {stale_days} days."
        else:
            baseline_values = [item[2] for item in initial]
            current_values = [item[2] for item in qualifying[-current_snapshot_count:]]
            baseline_median = float(median(baseline_values))
            current_median = float(median(current_values))
            if baseline_median > 0:
                percent_change = ((current_median - baseline_median) / baseline_median) * 100
            if percent_change is not None and math.isfinite(percent_change):
                status = "comparable"
            else:
                baseline_median = None
                current_median = None
                percent_change = None
                insufficient_reason = "Could not calculate a finite percentage change."

    return {
        "product_id": product_id,
        "category": category,
        "product_label": product_label,
        "query": query,
        "provider": "ebay",
        "status": status,
        "insufficient_reason": insufficient_reason,
        "baseline_median_price": round(baseline_median, 2) if baseline_median is not None else None,
        "latest_median_price": round(current_median, 2) if current_median is not None else None,
        "percent_change": round(percent_change, 1) if percent_change is not None else None,
        "snapshot_count": len(qualifying),
        "raw_snapshot_count": len(product_snapshots),
        "first_observed_at": first_at.isoformat() if first_at else None,
        "last_observed_at": latest_at.isoformat() if latest_at else None,
        "history_days": round(history_hours / 24, 1),
        "minimum_eligible_listings": min_eligible_listings,
        "minimum_qualifying_snapshots": min_qualifying_snapshots,
        "baseline_snapshot_count": baseline_snapshot_count,
        "current_snapshot_count": current_snapshot_count,
    }


def build_market_index_from_snapshots(
    snapshots: list[dict[str, Any]],
    *,
    observed_now: datetime,
    stale_days: int = DEFAULT_STALE_DAYS,
    min_span_hours: int = DEFAULT_MIN_SPAN_HOURS,
    min_category_models: int = DEFAULT_MIN_CATEGORY_MODELS,
    min_eligible_listings: int = DEFAULT_MIN_ELIGIBLE_LISTINGS,
    min_qualifying_snapshots: int = DEFAULT_MIN_QUALIFYING_SNAPSHOTS,
    baseline_snapshot_count: int = DEFAULT_BASELINE_SNAPSHOTS,
    current_snapshot_count: int = DEFAULT_CURRENT_SNAPSHOTS,
    days: int = DEFAULT_HISTORY_DAYS,
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for snapshot in snapshots:
        product_id = str(snapshot.get("product_id") or "").strip()
        provider = str(snapshot.get("provider") or "").strip().lower()
        if not product_id or provider != "ebay":
            continue
        grouped.setdefault(product_id, []).append(snapshot)

    models: list[dict[str, Any]] = []
    for product_id, product_snapshots in grouped.items():
        product_snapshots.sort(
            key=lambda item: _parse_datetime(item.get("observed_at"))
            or datetime.min.replace(tzinfo=UTC),
            reverse=True,
        )
        models.append(
            evaluate_model_history(
                product_id,
                product_snapshots,
                observed_now=observed_now,
                stale_days=stale_days,
                min_span_hours=min_span_hours,
                min_eligible_listings=min_eligible_listings,
                min_qualifying_snapshots=min_qualifying_snapshots,
                baseline_snapshot_count=baseline_snapshot_count,
                current_snapshot_count=current_snapshot_count,
            )
        )

    models.sort(
        key=lambda item: (
            item["category"],
            item["product_label"].lower(),
            item["product_id"],
        )
    )
    comparable = [model for model in models if model["status"] == "comparable"]

    by_category: dict[str, list[dict[str, Any]]] = {}
    all_by_category: dict[str, list[dict[str, Any]]] = {}
    for model in models:
        all_by_category.setdefault(model["category"], []).append(model)
    for model in comparable:
        by_category.setdefault(model["category"], []).append(model)

    categories: list[dict[str, Any]] = []
    for category, tracked_rows in sorted(all_by_category.items()):
        rows = by_category.get(category, [])
        changes = [
            float(row["percent_change"])
            for row in rows
            if row["percent_change"] is not None
        ]
        enough_models = len(changes) >= min_category_models
        median_change = float(median(changes)) if changes else None
        first_dates = [
            str(row["first_observed_at"])
            for row in rows
            if row["first_observed_at"]
        ]
        last_dates = [
            str(row["last_observed_at"])
            for row in rows
            if row["last_observed_at"]
        ]
        categories.append(
            {
                "category": category,
                "model_count": len(rows),
                "tracked_model_count": len(tracked_rows),
                "insufficient_model_count": len(tracked_rows) - len(rows),
                "median_percent_change": (
                    round(median_change, 1)
                    if enough_models and median_change is not None
                    else None
                ),
                "index_value": (
                    round(100 + median_change, 1)
                    if enough_models and median_change is not None
                    else None
                ),
                "first_observed_at": min(first_dates) if first_dates else None,
                "last_observed_at": max(last_dates) if last_dates else None,
                "minimum_models_required": min_category_models,
            }
        )

    return {
        "generated_at": observed_now.isoformat(),
        "history_window_days": days,
        "stale_after_days": stale_days,
        "minimum_history_hours": min_span_hours,
        "minimum_category_models": min_category_models,
        "minimum_eligible_listings": min_eligible_listings,
        "minimum_qualifying_snapshots": min_qualifying_snapshots,
        "baseline_snapshot_count": baseline_snapshot_count,
        "current_snapshot_count": current_snapshot_count,
        "tracked_snapshot_count": len(snapshots),
        "tracked_model_count": len(models),
        "comparable_model_count": len(comparable),
        "methodology": (
            f"A snapshot qualifies for index pricing only when it has at least {min_eligible_listings} "
            f"eligible eBay listings. A model needs at least {min_qualifying_snapshots} qualifying "
            f"snapshots, and its first {baseline_snapshot_count} qualifying snapshots must span at "
            f"least {min_span_hours} hours. The model baseline is the median of those first "
            f"{baseline_snapshot_count} snapshot medians; the current comparison price is the median "
            f"of its latest {current_snapshot_count} qualifying snapshot medians. Models also need a "
            f"qualifying observation within the last {stale_days} days. Category movement is the "
            "median percentage change across comparable models, with each model weighted equally."
        ),
        "categories": categories,
        "models": models,
    }


def build_market_index(
    *,
    days: int = DEFAULT_HISTORY_DAYS,
    stale_days: int = DEFAULT_STALE_DAYS,
    min_span_hours: int = DEFAULT_MIN_SPAN_HOURS,
    min_category_models: int = DEFAULT_MIN_CATEGORY_MODELS,
    min_eligible_listings: int = DEFAULT_MIN_ELIGIBLE_LISTINGS,
    min_qualifying_snapshots: int = DEFAULT_MIN_QUALIFYING_SNAPSHOTS,
    baseline_snapshot_count: int = DEFAULT_BASELINE_SNAPSHOTS,
    current_snapshot_count: int = DEFAULT_CURRENT_SNAPSHOTS,
    now: datetime | None = None,
) -> dict[str, Any]:
    days = max(1, min(int(days), 3650))
    stale_days = max(1, min(int(stale_days), 365))
    min_span_hours = max(1, min(int(min_span_hours), 24 * 365))
    min_category_models = max(1, min(int(min_category_models), 100))
    min_eligible_listings = max(1, min(int(min_eligible_listings), 1000))
    min_qualifying_snapshots = max(1, min(int(min_qualifying_snapshots), 100))
    baseline_snapshot_count = max(
        1, min(int(baseline_snapshot_count), min_qualifying_snapshots)
    )
    current_snapshot_count = max(
        1, min(int(current_snapshot_count), min_qualifying_snapshots)
    )
    observed_now = (now or datetime.now(UTC)).astimezone(UTC)
    snapshots = list_price_snapshots(days=days, limit=25000)
    return build_market_index_from_snapshots(
        snapshots,
        observed_now=observed_now,
        stale_days=stale_days,
        min_span_hours=min_span_hours,
        min_category_models=min_category_models,
        min_eligible_listings=min_eligible_listings,
        min_qualifying_snapshots=min_qualifying_snapshots,
        baseline_snapshot_count=baseline_snapshot_count,
        current_snapshot_count=current_snapshot_count,
        days=days,
    )
