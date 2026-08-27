from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from typing import Any

from app.services.market_index import (
    DEFAULT_BASELINE_SNAPSHOTS,
    DEFAULT_CURRENT_SNAPSHOTS,
    DEFAULT_MIN_ELIGIBLE_LISTINGS,
    evaluate_model_history,
    qualifying_snapshots,
)
from app.services.price_store import list_price_snapshots


def _snapshot_detail(item: tuple[datetime, dict[str, Any], float]) -> dict[str, Any]:
    observed_at, snapshot, median_price = item
    return {
        "observed_at": observed_at.isoformat(),
        "median_price": round(median_price, 2),
        "eligible_count": int(snapshot.get("eligible_count") or 0),
        "candidate_count": int(snapshot.get("candidate_count") or 0),
        "filtered_count": int(snapshot.get("filtered_count") or 0),
        "sample_prices": list(snapshot.get("sample_prices") or [])[:10],
        "source": snapshot.get("source"),
    }


def audit_market_histories(
    snapshots: list[dict[str, Any]],
    *,
    now: datetime | None = None,
    product_ids: set[str] | None = None,
    suspicious_only: bool = False,
) -> list[dict[str, Any]]:
    observed_now = (now or datetime.now(UTC)).astimezone(UTC)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for snapshot in snapshots:
        product_id = str(snapshot.get("product_id") or "").strip()
        if not product_id or str(snapshot.get("provider") or "").lower() != "ebay":
            continue
        if product_ids and product_id not in product_ids:
            continue
        grouped.setdefault(product_id, []).append(snapshot)

    reports: list[dict[str, Any]] = []
    for product_id, rows in grouped.items():
        rows.sort(key=lambda row: str(row.get("observed_at") or ""))
        legacy_usable = qualifying_snapshots(rows, min_eligible_listings=1)
        fixed_usable = qualifying_snapshots(
            rows,
            min_eligible_listings=DEFAULT_MIN_ELIGIBLE_LISTINGS,
        )

        legacy_before = None
        if len(legacy_usable) >= 2:
            first = legacy_usable[0][2]
            latest = legacy_usable[-1][2]
            legacy_before = {
                "baseline_price": round(first, 2),
                "current_price": round(latest, 2),
                "percent_change": round(((latest - first) / first) * 100, 1),
            }

        fixed = evaluate_model_history(
            product_id,
            list(reversed(rows)),
            observed_now=observed_now,
        )
        legacy_change = abs(float(legacy_before["percent_change"])) if legacy_before else 0.0
        first_low_sample = bool(
            legacy_usable
            and int(legacy_usable[0][1].get("eligible_count") or 0)
            < DEFAULT_MIN_ELIGIBLE_LISTINGS
        )
        suspicious = legacy_change >= 50 or first_low_sample
        if suspicious_only and not suspicious:
            continue

        reports.append(
            {
                "product_id": product_id,
                "product_label": fixed["product_label"],
                "category": fixed["category"],
                "suspicious": suspicious,
                "legacy": legacy_before,
                "fixed": {
                    "status": fixed["status"],
                    "baseline_price": fixed["baseline_median_price"],
                    "current_price": fixed["latest_median_price"],
                    "percent_change": fixed["percent_change"],
                    "reason": fixed["insufficient_reason"],
                },
                "legacy_first_snapshot": (
                    _snapshot_detail(legacy_usable[0]) if legacy_usable else None
                ),
                "baseline_snapshots_used": [
                    _snapshot_detail(item)
                    for item in fixed_usable[:DEFAULT_BASELINE_SNAPSHOTS]
                ],
                "current_snapshots_used": [
                    _snapshot_detail(item)
                    for item in fixed_usable[-DEFAULT_CURRENT_SNAPSHOTS:]
                ],
                "qualifying_snapshot_count": len(fixed_usable),
            }
        )

    reports.sort(
        key=lambda row: (
            not row["suspicious"],
            row["category"],
            row["product_label"].lower(),
        )
    )
    return reports


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit PriceSift Used Market Index baselines without modifying raw history."
    )
    parser.add_argument(
        "--product-id",
        action="append",
        default=[],
        help="Limit to one or more product IDs.",
    )
    parser.add_argument(
        "--suspicious",
        action="store_true",
        help="Only print histories with a >=50%% legacy move or a thin first sample.",
    )
    parser.add_argument("--days", type=int, default=3650)
    args = parser.parse_args()
    snapshots = list_price_snapshots(
        days=max(1, min(args.days, 3650)),
        limit=25000,
    )
    report = audit_market_histories(
        snapshots,
        product_ids=set(args.product_id) or None,
        suspicious_only=args.suspicious,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
