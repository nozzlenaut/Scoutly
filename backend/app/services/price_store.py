from __future__ import annotations

import json
import logging
import math
import os
from decimal import Decimal
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Any, Iterable
from uuid import uuid4

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
MAX_FILE_SNAPSHOTS = 25000
SNAPSHOT_BUCKET_HOURS = 6


def _now() -> datetime:
    return datetime.now(UTC)


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _snapshots_path() -> Path:
    return _data_dir() / "price_snapshots.json"


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return payload if isinstance(payload, list) else []


def _write_json_list(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(path)


def _serialize_record(record: dict[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, Decimal):
            serialized[key] = float(value)
        elif isinstance(value, list):
            serialized[key] = [float(item) if isinstance(item, Decimal) else item for item in value]
        else:
            serialized[key] = value
    return serialized


def _bucket_start(value: datetime) -> datetime:
    value = value.astimezone(UTC)
    hour = (value.hour // SNAPSHOT_BUCKET_HOURS) * SNAPSHOT_BUCKET_HOURS
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


def _percentile(values: Iterable[float], fraction: float) -> float | None:
    ordered = sorted(float(value) for value in values if value is not None and math.isfinite(float(value)))
    if not ordered:
        return None
    if len(ordered) == 1:
        return round(ordered[0], 2)
    position = (len(ordered) - 1) * min(1.0, max(0.0, fraction))
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(ordered[lower], 2)
    weight = position - lower
    return round(ordered[lower] + (ordered[upper] - ordered[lower]) * weight, 2)


def _clean_prices(prices: Iterable[float]) -> list[float]:
    cleaned = sorted(round(float(price), 2) for price in prices if price is not None and float(price) >= 0)
    return cleaned[:100]


def _db_or_file_read(db_reader, file_reader):
    if database_configured():
        try:
            return db_reader()
        except Exception:
            logger.exception("PostgreSQL price-history read failed; using file fallback.")
    return file_reader()


def _db_write_or_file(db_writer, file_writer) -> None:
    if database_configured():
        try:
            db_writer()
            return
        except Exception:
            logger.exception("PostgreSQL price-history write failed; using file fallback.")
    file_writer()


def record_price_snapshot(
    *,
    product_id: str,
    category: str,
    product_label: str,
    provider: str,
    query: str,
    prices: Iterable[float],
    candidate_count: int = 0,
    filtered_count: int = 0,
    source: str = "search",
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    observed = observed_at or _now()
    bucket = _bucket_start(observed)
    clean_prices = _clean_prices(prices)
    record = {
        "id": str(uuid4()),
        "snapshot_bucket": bucket,
        "observed_at": observed,
        "product_id": product_id,
        "category": category,
        "product_label": product_label,
        "provider": provider.lower(),
        "query": query,
        "source": source,
        "candidate_count": max(0, int(candidate_count)),
        "filtered_count": max(0, int(filtered_count)),
        "eligible_count": len(clean_prices),
        "lowest_price": round(min(clean_prices), 2) if clean_prices else None,
        "median_price": round(float(median(clean_prices)), 2) if clean_prices else None,
        "p25_price": _percentile(clean_prices, 0.25),
        "p75_price": _percentile(clean_prices, 0.75),
        "sample_prices": clean_prices,
    }

    def db_write() -> None:
        with database_connection() as connection:
            connection.execute(
                """
                INSERT INTO scoutly_price_snapshots (
                    id, snapshot_bucket, observed_at, product_id, category,
                    product_label, provider, query, source, candidate_count,
                    filtered_count, eligible_count, lowest_price, median_price,
                    p25_price, p75_price, sample_prices
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s::jsonb
                )
                ON CONFLICT (product_id, provider, snapshot_bucket)
                DO UPDATE SET
                    observed_at = EXCLUDED.observed_at,
                    category = EXCLUDED.category,
                    product_label = EXCLUDED.product_label,
                    query = EXCLUDED.query,
                    source = EXCLUDED.source,
                    candidate_count = EXCLUDED.candidate_count,
                    filtered_count = EXCLUDED.filtered_count,
                    eligible_count = EXCLUDED.eligible_count,
                    lowest_price = EXCLUDED.lowest_price,
                    median_price = EXCLUDED.median_price,
                    p25_price = EXCLUDED.p25_price,
                    p75_price = EXCLUDED.p75_price,
                    sample_prices = EXCLUDED.sample_prices
                """,
                (
                    record["id"],
                    bucket,
                    observed,
                    product_id,
                    category,
                    product_label,
                    record["provider"],
                    query,
                    source,
                    record["candidate_count"],
                    record["filtered_count"],
                    record["eligible_count"],
                    record["lowest_price"],
                    record["median_price"],
                    record["p25_price"],
                    record["p75_price"],
                    json.dumps(clean_prices),
                ),
            )

    def file_write() -> None:
        records = _read_json_list(_snapshots_path())
        bucket_iso = bucket.isoformat()
        replacement = _serialize_record(record)
        replaced = False
        for index, existing in enumerate(records):
            if (
                existing.get("product_id") == product_id
                and str(existing.get("provider") or "").lower() == record["provider"]
                and existing.get("snapshot_bucket") == bucket_iso
            ):
                records[index] = replacement
                replaced = True
                break
        if not replaced:
            records.append(replacement)
        records.sort(key=lambda item: str(item.get("observed_at") or ""))
        _write_json_list(_snapshots_path(), records[-MAX_FILE_SNAPSHOTS:])

    _db_write_or_file(db_write, file_write)
    return _serialize_record(record)


def list_price_snapshots(
    *,
    product_id: str | None = None,
    days: int = 30,
    limit: int = 5000,
) -> list[dict[str, Any]]:
    days = max(1, min(days, 3650))
    limit = max(1, min(limit, 25000))
    cutoff = _now() - timedelta(days=days)

    def db_read() -> list[dict[str, Any]]:
        where = "observed_at >= %s"
        params: list[Any] = [cutoff]
        if product_id:
            where += " AND product_id = %s"
            params.append(product_id)
        params.append(limit)
        with database_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, snapshot_bucket, observed_at, product_id, category,
                       product_label, provider, query, source, candidate_count,
                       filtered_count, eligible_count, lowest_price, median_price,
                       p25_price, p75_price, sample_prices
                FROM scoutly_price_snapshots
                WHERE {where}
                ORDER BY observed_at DESC
                LIMIT %s
                """,
                tuple(params),
            ).fetchall()
        return [_serialize_record(dict(row)) for row in rows]

    def file_read() -> list[dict[str, Any]]:
        records = _read_json_list(_snapshots_path())
        filtered: list[dict[str, Any]] = []
        for record in records:
            if product_id and record.get("product_id") != product_id:
                continue
            try:
                observed = datetime.fromisoformat(str(record.get("observed_at") or "").replace("Z", "+00:00"))
            except ValueError:
                continue
            if observed.tzinfo is None:
                observed = observed.replace(tzinfo=UTC)
            if observed >= cutoff:
                filtered.append(record)
        filtered.sort(key=lambda item: str(item.get("observed_at") or ""), reverse=True)
        return filtered[:limit]

    return _db_or_file_read(db_read, file_read)


def _context_from_snapshots(
    *,
    product_id: str,
    snapshots: list[dict[str, Any]],
    current_prices: Iterable[float] = (),
    days: int = 30,
) -> dict[str, Any]:
    current = _clean_prices(current_prices)
    positive_snapshots = [snapshot for snapshot in snapshots if int(snapshot.get("eligible_count") or 0) > 0]
    historical_prices: list[float] = []
    for snapshot in positive_snapshots:
        historical_prices.extend(_clean_prices(snapshot.get("sample_prices") or []))

    history_ready = len(positive_snapshots) >= 3 and len(historical_prices) >= 9
    historical_median = _percentile(historical_prices, 0.5) if history_ready else None
    current_best = round(min(current), 2) if current else None
    comparison_percent = None
    if current_best is not None and historical_median and historical_median > 0:
        comparison_percent = round(((current_best - historical_median) / historical_median) * 100, 1)

    last_observed = snapshots[0].get("observed_at") if snapshots else None
    first_observed = snapshots[-1].get("observed_at") if snapshots else None
    available_count = len(positive_snapshots)

    return {
        "product_id": product_id,
        "window_days": days,
        "current_eligible_count": len(current),
        "current_best_price": current_best,
        "current_median_price": _percentile(current, 0.5),
        "current_low_price": _percentile(current, 0.0),
        "current_high_price": _percentile(current, 1.0),
        "snapshot_count": len(snapshots),
        "available_snapshot_count": available_count,
        "availability_rate": round((available_count / len(snapshots)) * 100, 1) if snapshots else None,
        "history_ready": history_ready,
        "typical_low_price": _percentile(historical_prices, 0.25) if history_ready else None,
        "typical_high_price": _percentile(historical_prices, 0.75) if history_ready else None,
        "historical_median_price": historical_median,
        "current_vs_median_percent": comparison_percent,
        "first_observed_at": first_observed,
        "last_observed_at": last_observed,
    }


def build_price_context(
    *,
    product_id: str,
    current_prices: Iterable[float] = (),
    days: int = 30,
) -> dict[str, Any]:
    snapshots = list_price_snapshots(product_id=product_id, days=days)
    return _context_from_snapshots(
        product_id=product_id,
        snapshots=snapshots,
        current_prices=current_prices,
        days=days,
    )


def price_overview(days: int = 30, limit: int = 500) -> dict[str, Any]:
    snapshots = list_price_snapshots(days=days, limit=25000)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for snapshot in snapshots:
        product_id = str(snapshot.get("product_id") or "")
        if product_id:
            grouped.setdefault(product_id, []).append(snapshot)

    products: list[dict[str, Any]] = []
    for product_id, product_snapshots in grouped.items():
        latest = product_snapshots[0]
        context = _context_from_snapshots(product_id=product_id, snapshots=product_snapshots, current_prices=latest.get("sample_prices") or [], days=days)
        products.append(
            {
                "product_id": product_id,
                "category": latest.get("category"),
                "product_label": latest.get("product_label"),
                "provider": latest.get("provider"),
                "last_observed_at": latest.get("observed_at"),
                "latest_eligible_count": latest.get("eligible_count", 0),
                "latest_best_price": latest.get("lowest_price"),
                "snapshot_count": context["snapshot_count"],
                "history_ready": context["history_ready"],
                "typical_low_price": context["typical_low_price"],
                "typical_high_price": context["typical_high_price"],
                "historical_median_price": context["historical_median_price"],
                "availability_rate": context["availability_rate"],
            }
        )

    products.sort(key=lambda item: str(item.get("last_observed_at") or ""), reverse=True)
    return {
        "window_days": days,
        "snapshot_count": len(snapshots),
        "product_count": len(grouped),
        "history_ready_count": sum(1 for product in products if product["history_ready"]),
        "available_latest_count": sum(1 for product in products if int(product.get("latest_eligible_count") or 0) > 0),
        "products": products[: max(1, min(limit, 2000))],
    }
