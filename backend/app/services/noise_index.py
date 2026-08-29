from __future__ import annotations

import math
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from app.services.feedback_store import recent_filtered_listings
from app.services.price_store import list_price_snapshots

DEFAULT_HISTORY_DAYS = 30
DEFAULT_STALE_DAYS = 7
DEFAULT_MIN_RANKING_CANDIDATES = 20
DEFAULT_REASON_WINDOW_MINUTES = 5


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


def _nonnegative_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _nullable_nonnegative_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return None


def _noise_rate(filtered_count: int, candidate_count: int) -> float | None:
    if candidate_count <= 0:
        return None
    return round((filtered_count / candidate_count) * 100, 1)


def _reason_counts_for_snapshot(
    product_id: str,
    observed_at: datetime | None,
    filtered_events: list[dict[str, Any]],
    *,
    reason_window_minutes: int,
) -> Counter[str]:
    counts: Counter[str] = Counter()
    if observed_at is None:
        return counts
    earliest = observed_at - timedelta(minutes=reason_window_minutes)
    latest = observed_at + timedelta(minutes=1)
    for event in filtered_events:
        if str(event.get("product_id") or "") != product_id:
            continue
        if str(event.get("listing_type") or "").strip().lower() != "fixed_price":
            continue
        filtered_at = _parse_datetime(event.get("filtered_at"))
        if filtered_at is None or filtered_at < earliest or filtered_at > latest:
            continue
        reasons = {
            str(reason).strip()
            for reason in (event.get("reasons") or [])
            if str(reason).strip()
        }
        counts.update(reasons)
    return counts


def build_noise_index_from_records(
    snapshots: list[dict[str, Any]],
    filtered_events: list[dict[str, Any]],
    *,
    generated_at: datetime,
    stale_days: int = DEFAULT_STALE_DAYS,
    min_ranking_candidates: int = DEFAULT_MIN_RANKING_CANDIDATES,
    reason_window_minutes: int = DEFAULT_REASON_WINDOW_MINUTES,
) -> dict[str, Any]:
    """Build a current marketplace-noise snapshot from stored PriceSift data."""
    latest_by_product: dict[str, dict[str, Any]] = {}
    for snapshot in snapshots:
        if str(snapshot.get("provider") or "").lower() != "ebay":
            continue
        product_id = str(snapshot.get("product_id") or "").strip()
        observed_at = _parse_datetime(snapshot.get("observed_at"))
        if not product_id or observed_at is None:
            continue
        existing = latest_by_product.get(product_id)
        existing_at = _parse_datetime(existing.get("observed_at")) if existing else None
        if existing is None or existing_at is None or observed_at > existing_at:
            latest_by_product[product_id] = snapshot

    stale_cutoff = generated_at.astimezone(UTC) - timedelta(days=stale_days)
    stale_model_count = 0
    models: list[dict[str, Any]] = []
    for product_id, snapshot in latest_by_product.items():
        observed_at = _parse_datetime(snapshot.get("observed_at"))
        if observed_at is None or observed_at < stale_cutoff:
            stale_model_count += 1
            continue

        candidates = _nonnegative_int(snapshot.get("candidate_count"))
        filtered = _nonnegative_int(snapshot.get("filtered_count"))
        if candidates > 0:
            filtered = min(candidates, filtered)
        eligible = _nonnegative_int(snapshot.get("eligible_count"))
        duplicates = _nullable_nonnegative_int(snapshot.get("duplicates_removed"))
        eligible_count_exact = (
            duplicates is not None
            or eligible < 100
            or max(0, candidates - filtered) <= 100
        )
        reasons = _reason_counts_for_snapshot(
            product_id,
            observed_at,
            filtered_events,
            reason_window_minutes=reason_window_minutes,
        )
        rate = _noise_rate(filtered, candidates)
        models.append(
            {
                "product_id": product_id,
                "category": str(snapshot.get("category") or "unknown").strip().lower(),
                "product_label": str(snapshot.get("product_label") or product_id).strip(),
                "query": str(
                    snapshot.get("query") or snapshot.get("product_label") or product_id
                ).strip(),
                "provider": "ebay",
                "candidate_count": candidates,
                "filtered_count": filtered,
                "noise_rate": rate,
                "eligible_count": eligible,
                "eligible_count_exact": eligible_count_exact,
                "duplicates_removed": duplicates,
                "duplicates_source": (
                    "recorded_at_collection" if duplicates is not None else "not_recorded"
                ),
                "rejection_reasons": [
                    {"reason": reason, "count": count}
                    for reason, count in reasons.most_common(5)
                ],
                "rejection_reason_breakdown_available": bool(reasons) or filtered == 0,
                "observed_at": observed_at.isoformat(),
            }
        )

    models.sort(
        key=lambda item: (
            item["category"],
            item["product_label"].lower(),
            item["product_id"],
        )
    )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for model in models:
        grouped.setdefault(model["category"], []).append(model)

    categories: list[dict[str, Any]] = []
    for category, rows in sorted(grouped.items()):
        candidate_total = sum(int(row["candidate_count"]) for row in rows)
        filtered_total = sum(int(row["filtered_count"]) for row in rows)
        eligible_total = sum(int(row["eligible_count"]) for row in rows)
        known_duplicates = [
            int(row["duplicates_removed"])
            for row in rows
            if row["duplicates_removed"] is not None
        ]
        categories.append(
            {
                "category": category,
                "model_count": len(rows),
                "candidate_count": candidate_total,
                "filtered_count": filtered_total,
                "noise_rate": _noise_rate(filtered_total, candidate_total),
                "eligible_count": eligible_total,
                "eligible_count_exact": all(bool(row["eligible_count_exact"]) for row in rows),
                "duplicates_removed": sum(known_duplicates) if known_duplicates else None,
                "duplicates_reported_model_count": len(known_duplicates),
                "duplicates_complete": len(known_duplicates) == len(rows),
            }
        )

    ranked = [
        model
        for model in models
        if model["candidate_count"] >= min_ranking_candidates
        and model["noise_rate"] is not None
        and math.isfinite(float(model["noise_rate"]))
    ]
    ranked.sort(
        key=lambda item: (
            -float(item["noise_rate"]),
            -int(item["candidate_count"]),
            item["product_label"].lower(),
        )
    )

    observed_times = [
        observed
        for model in models
        if (observed := _parse_datetime(model.get("observed_at"))) is not None
    ]

    return {
        "generated_at": generated_at.astimezone(UTC).isoformat(),
        "latest_observed_at": max(observed_times).isoformat() if observed_times else None,
        "oldest_observed_at": min(observed_times).isoformat() if observed_times else None,
        "snapshot_mode": "current_marketplace_snapshot",
        "historical_trends_available": False,
        "stale_after_days": stale_days,
        "stale_model_count": stale_model_count,
        "minimum_ranking_candidates": min_ranking_candidates,
        "model_count": len(models),
        "methodology": (
            "Noise rate is filtered listings divided by marketplace candidates checked. "
            "Duplicate candidate matches are stored separately at collection time and never count as "
            "marketplace noise; older snapshots without an exact duplicate count stay marked unavailable. "
            "Rejection reasons use fixed-price filter events recorded near "
            "the current stored snapshot; PriceSift does not backfill missing reason history."
        ),
        "categories": categories,
        "models": models,
        "noisiest": ranked[:10],
    }


def build_noise_index(
    *,
    days: int = DEFAULT_HISTORY_DAYS,
    stale_days: int = DEFAULT_STALE_DAYS,
    min_ranking_candidates: int = DEFAULT_MIN_RANKING_CANDIDATES,
    now: datetime | None = None,
) -> dict[str, Any]:
    days = max(1, min(int(days), 90))
    stale_days = max(1, min(int(stale_days), 30))
    min_ranking_candidates = max(1, min(int(min_ranking_candidates), 1000))
    generated_at = (now or datetime.now(UTC)).astimezone(UTC)
    snapshots = list_price_snapshots(days=days, limit=25000)
    filtered_events = recent_filtered_listings(limit=20000)
    return build_noise_index_from_records(
        snapshots,
        filtered_events,
        generated_at=generated_at,
        stale_days=stale_days,
        min_ranking_candidates=min_ranking_candidates,
    )
