from __future__ import annotations

from datetime import UTC, datetime
from statistics import median
from typing import Any, Iterable

from app.services.price_store import list_price_snapshots

MIN_PRIOR_POSITIVE_SNAPSHOTS = 2
PRICE_DROP_THRESHOLD_PERCENT = -7.5
PRICE_SPIKE_THRESHOLD_PERCENT = 10.0
STANDOUT_DEAL_THRESHOLD_PERCENT = -15.0
INVENTORY_SHIFT_THRESHOLD_PERCENT = 50.0
MIN_INVENTORY_SHIFT_COUNT = 3
WATCH_PRICE_MOVE_PERCENT = 3.0
WATCH_DEAL_GAP_PERCENT = -8.0
VIDEO_WORTHY_SCORE = 30.0


def _number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed


def _observed_at(value: Any) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _median(values: Iterable[float | int | None]) -> float | None:
    cleaned = [float(value) for value in values if value is not None]
    if not cleaned:
        return None
    return round(float(median(cleaned)), 2)


def _percent_change(current: float | None, baseline: float | None) -> float | None:
    if current is None or baseline is None or baseline <= 0:
        return None
    return round(((current - baseline) / baseline) * 100, 1)


def _confidence(prior_snapshot_count: int) -> tuple[str, float]:
    if prior_snapshot_count >= 8:
        return "high", 1.0
    if prior_snapshot_count >= 4:
        return "medium", min(0.92, 0.68 + (prior_snapshot_count - 4) * 0.06)
    return "low", 0.61


def _story_angle(
    *,
    label: str,
    primary_signal: str,
    median_change_percent: float | None,
    best_vs_baseline_percent: float | None,
    inventory_change_percent: float | None,
) -> str:
    if primary_signal == "price_drop" and median_change_percent is not None:
        return f"{label} clean used median is down {abs(median_change_percent):.1f}% versus prior observations."
    if primary_signal == "price_spike" and median_change_percent is not None:
        return f"{label} clean used median is up {median_change_percent:.1f}% versus prior observations."
    if primary_signal == "standout_deal" and best_vs_baseline_percent is not None:
        return f"A clean {label} listing is {abs(best_vs_baseline_percent):.1f}% below its recent median."
    if primary_signal == "inventory_surge" and inventory_change_percent is not None:
        return f"Clean {label} inventory is up {inventory_change_percent:.0f}% versus its recent level."
    if primary_signal == "inventory_squeeze" and inventory_change_percent is not None:
        return f"Clean {label} inventory is down {abs(inventory_change_percent):.0f}% versus its recent level."
    if median_change_percent is not None:
        direction = "down" if median_change_percent < 0 else "up"
        return f"{label} used pricing is {direction} {abs(median_change_percent):.1f}%; watching for confirmation."
    return f"{label} has a possible market change worth watching."


def _build_product_signal(product_id: str, snapshots: list[dict[str, Any]]) -> tuple[bool, dict[str, Any] | None]:
    ordered = sorted(snapshots, key=lambda item: _observed_at(item.get("observed_at")), reverse=True)
    if not ordered:
        return False, None

    latest = ordered[0]
    latest_eligible = int(latest.get("eligible_count") or 0)
    latest_median = _number(latest.get("median_price"))
    latest_best = _number(latest.get("lowest_price"))
    if latest_eligible <= 0 or latest_median is None:
        return False, None

    prior_positive = [
        snapshot
        for snapshot in ordered[1:]
        if int(snapshot.get("eligible_count") or 0) > 0
        and _number(snapshot.get("median_price")) is not None
    ]
    if len(prior_positive) < MIN_PRIOR_POSITIVE_SNAPSHOTS:
        return False, None

    baseline_median = _median(_number(snapshot.get("median_price")) for snapshot in prior_positive)
    baseline_best = _median(_number(snapshot.get("lowest_price")) for snapshot in prior_positive)
    baseline_inventory = _median(int(snapshot.get("eligible_count") or 0) for snapshot in prior_positive)
    median_change_percent = _percent_change(latest_median, baseline_median)
    best_vs_baseline_percent = _percent_change(latest_best, baseline_median)
    inventory_change_percent = _percent_change(float(latest_eligible), baseline_inventory)
    inventory_delta = (
        round(latest_eligible - baseline_inventory, 1)
        if baseline_inventory is not None
        else None
    )

    tags: list[str] = []
    if median_change_percent is not None and median_change_percent <= PRICE_DROP_THRESHOLD_PERCENT:
        tags.append("price_drop")
    if median_change_percent is not None and median_change_percent >= PRICE_SPIKE_THRESHOLD_PERCENT:
        tags.append("price_spike")
    if best_vs_baseline_percent is not None and best_vs_baseline_percent <= STANDOUT_DEAL_THRESHOLD_PERCENT:
        tags.append("standout_deal")
    if (
        inventory_change_percent is not None
        and inventory_delta is not None
        and inventory_delta >= MIN_INVENTORY_SHIFT_COUNT
        and inventory_change_percent >= INVENTORY_SHIFT_THRESHOLD_PERCENT
    ):
        tags.append("inventory_surge")
    if (
        inventory_change_percent is not None
        and inventory_delta is not None
        and inventory_delta <= -MIN_INVENTORY_SHIFT_COUNT
        and inventory_change_percent <= -INVENTORY_SHIFT_THRESHOLD_PERCENT
    ):
        tags.append("inventory_squeeze")

    primary_signal: str | None = None
    for candidate in ("price_drop", "price_spike", "standout_deal", "inventory_surge", "inventory_squeeze"):
        if candidate in tags:
            primary_signal = candidate
            break

    if primary_signal is None:
        modest_price_move = median_change_percent is not None and abs(median_change_percent) >= WATCH_PRICE_MOVE_PERCENT
        modest_deal_gap = best_vs_baseline_percent is not None and best_vs_baseline_percent <= WATCH_DEAL_GAP_PERCENT
        if not modest_price_move and not modest_deal_gap:
            return True, None
        primary_signal = "watch"
        tags.append("watch")

    movement_score = min(60.0, abs(median_change_percent or 0.0) * 3.0)
    deal_score = min(25.0, max(0.0, -(best_vs_baseline_percent or 0.0) - 5.0) * 1.25)
    inventory_score = 0.0
    if inventory_change_percent is not None and inventory_delta is not None and abs(inventory_delta) >= MIN_INVENTORY_SHIFT_COUNT:
        inventory_score = min(15.0, abs(inventory_change_percent) * 0.12)

    confidence_label, confidence_factor = _confidence(len(prior_positive))
    liquidity_factor = 1.0 if latest_eligible >= 3 else 0.8
    score = round((movement_score + deal_score + inventory_score) * confidence_factor * liquidity_factor, 1)
    video_worthy = primary_signal != "watch" and score >= VIDEO_WORTHY_SCORE
    label = str(latest.get("product_label") or product_id)

    signal = {
        "product_id": product_id,
        "product_label": label,
        "category": latest.get("category"),
        "provider": latest.get("provider"),
        "last_observed_at": latest.get("observed_at"),
        "primary_signal": primary_signal,
        "signal_tags": tags,
        "video_score": score,
        "video_worthy": video_worthy,
        "confidence": confidence_label,
        "latest_best_price": latest_best,
        "latest_median_price": latest_median,
        "latest_eligible_count": latest_eligible,
        "baseline_median_price": baseline_median,
        "baseline_best_price": baseline_best,
        "baseline_eligible_count": baseline_inventory,
        "median_change_percent": median_change_percent,
        "best_vs_baseline_percent": best_vs_baseline_percent,
        "inventory_change_percent": inventory_change_percent,
        "prior_snapshot_count": len(prior_positive),
        "story_angle": _story_angle(
            label=label,
            primary_signal=primary_signal,
            median_change_percent=median_change_percent,
            best_vs_baseline_percent=best_vs_baseline_percent,
            inventory_change_percent=inventory_change_percent,
        ),
    }
    return True, signal


def build_market_signals_from_snapshots(
    snapshots: list[dict[str, Any]],
    *,
    days: int = 30,
    limit: int = 25,
    category: str | None = None,
) -> dict[str, Any]:
    normalized_category = (category or "").strip().lower()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for snapshot in snapshots:
        if normalized_category and str(snapshot.get("category") or "").strip().lower() != normalized_category:
            continue
        product_id = str(snapshot.get("product_id") or "").strip()
        if product_id:
            grouped.setdefault(product_id, []).append(snapshot)

    ready_product_count = 0
    signals: list[dict[str, Any]] = []
    for product_id, product_snapshots in grouped.items():
        ready, signal = _build_product_signal(product_id, product_snapshots)
        if ready:
            ready_product_count += 1
        if signal is not None:
            signals.append(signal)

    signals.sort(
        key=lambda item: (
            not bool(item.get("video_worthy")),
            -float(item.get("video_score") or 0.0),
            str(item.get("product_label") or ""),
        )
    )
    bounded_limit = max(1, min(int(limit), 100))
    return {
        "window_days": days,
        "category": normalized_category or None,
        "snapshot_count": len(snapshots),
        "product_count": len(grouped),
        "ready_product_count": ready_product_count,
        "building_product_count": max(0, len(grouped) - ready_product_count),
        "signal_count": len(signals),
        "video_worthy_count": sum(1 for signal in signals if signal["video_worthy"]),
        "signals": signals[:bounded_limit],
    }


def market_signals(*, days: int = 30, limit: int = 25, category: str | None = None) -> dict[str, Any]:
    snapshots = list_price_snapshots(days=days, limit=25000)
    return build_market_signals_from_snapshots(
        snapshots,
        days=days,
        limit=limit,
        category=category,
    )
