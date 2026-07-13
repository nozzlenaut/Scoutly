from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from app.models.listing import Listing
from app.services.database import database_configured, database_connection, database_health
from app.services.filter_rules import list_manual_filter_rules

REPORT_TTL_HOURS = 72
MAX_REPORTS = 500
MAX_CLICKS = 2000
MAX_FILTERED = 3000
DB_MAX_CLICKS = 50_000
DB_MAX_FILTERED = 20_000

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(UTC)


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _reports_path() -> Path:
    return _data_dir() / "bad_result_reports.json"


def _clicks_path() -> Path:
    return _data_dir() / "outbound_clicks.json"


def _filtered_path() -> Path:
    return _data_dir() / "filtered_listings.json"


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
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    tmp_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(path)


def _serialize_record(record: dict[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return serialized


def ebay_item_id_from_url(url: str) -> str | None:
    """Return the stable eBay item id when a URL uses /itm/<id> or /itm/title/<id>."""
    try:
        path_parts = [part for part in urlsplit(url).path.split("/") if part]
    except ValueError:
        return None

    if "itm" not in path_parts:
        return None

    itm_index = path_parts.index("itm")
    for part in path_parts[itm_index + 1 :]:
        if part.isdigit():
            return part
    return None


def _normalized_link_key(url: str) -> str:
    ebay_item_id = ebay_item_id_from_url(url)
    if ebay_item_id:
        return f"ebay:item:{ebay_item_id}"

    try:
        parts = urlsplit(url)
    except ValueError:
        return url.strip()
    return f"{parts.netloc.lower()}{parts.path}".strip()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _active_reports(records: list[dict[str, Any]], now: datetime | None = None) -> list[dict[str, Any]]:
    current = now or _now()
    active: list[dict[str, Any]] = []
    for record in records:
        expires_at = _parse_dt(record.get("expires_at"))
        if expires_at is None or expires_at <= current:
            continue
        active.append(record)
    return active[-MAX_REPORTS:]


def _db_active_reports(limit: int = MAX_REPORTS, newest_first: bool = False) -> list[dict[str, Any]]:
    direction = "DESC" if newest_first else "ASC"
    with database_connection() as connection:
        connection.execute("DELETE FROM scoutly_bad_result_reports WHERE expires_at <= NOW()")
        rows = connection.execute(
            f"""
            SELECT url, title, provider, category, product_id, query, reason,
                   link_key, ebay_item_id, reported_at, expires_at
            FROM scoutly_bad_result_reports
            WHERE expires_at > NOW()
            ORDER BY reported_at {direction}
            LIMIT %s
            """,
            (limit,),
        ).fetchall()
    return [_serialize_record(dict(row)) for row in rows]


def _db_or_file_read(db_reader, file_reader):
    if database_configured():
        try:
            return db_reader()
        except Exception:
            logger.exception("PostgreSQL read failed; using Scoutly file fallback.")
    return file_reader()


def _db_write_or_file(db_writer, file_writer) -> None:
    if database_configured():
        try:
            db_writer()
            return
        except Exception:
            logger.exception("PostgreSQL write failed; using Scoutly file fallback.")
    file_writer()


@dataclass
class BadResultReport:
    url: str
    title: str | None = None
    provider: str | None = None
    category: str | None = None
    product_id: str | None = None
    query: str | None = None
    reason: str = "wrong_item"


def report_bad_result(report: BadResultReport) -> dict[str, Any]:
    now = _now()
    expires_at = now + timedelta(hours=REPORT_TTL_HOURS)
    link_key = _normalized_link_key(report.url)
    ebay_item_id = ebay_item_id_from_url(report.url)

    def db_write() -> None:
        with database_connection() as connection:
            connection.execute(
                """
                DELETE FROM scoutly_bad_result_reports
                WHERE link_key = %s
                  AND product_id IS NOT DISTINCT FROM %s
                  AND category IS NOT DISTINCT FROM %s
                """,
                (link_key, report.product_id, report.category),
            )
            connection.execute(
                """
                INSERT INTO scoutly_bad_result_reports (
                    url, title, provider, category, product_id, query, reason,
                    link_key, ebay_item_id, reported_at, expires_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    report.url,
                    report.title,
                    report.provider,
                    report.category,
                    report.product_id,
                    report.query,
                    report.reason,
                    link_key,
                    ebay_item_id,
                    now,
                    expires_at,
                ),
            )
            connection.execute("DELETE FROM scoutly_bad_result_reports WHERE expires_at <= NOW()")

    def file_write() -> None:
        records = _active_reports(_read_json_list(_reports_path()), now)
        record = {
            **asdict(report),
            "link_key": link_key,
            "ebay_item_id": ebay_item_id,
            "reported_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
        }
        records[:] = [
            existing
            for existing in records
            if not (
                existing.get("link_key") == link_key
                and existing.get("product_id") == report.product_id
                and existing.get("category") == report.category
            )
        ]
        records.append(record)
        _write_json_list(_reports_path(), records[-MAX_REPORTS:])

    _db_write_or_file(db_write, file_write)
    return {
        "status": "ok",
        "hidden_until": expires_at.isoformat(),
        "link_key": link_key,
    }


def _report_blocks_listing(
    report: dict[str, Any],
    listing: Listing,
    product_id: str | None,
    category: str | None,
) -> bool:
    if report.get("link_key") != _normalized_link_key(str(listing.url)):
        return False

    reported_product_id = report.get("product_id")
    if reported_product_id and product_id and reported_product_id != product_id:
        return False

    reported_category = report.get("category")
    if reported_category and category and reported_category != category:
        return False

    return True


def filter_reported_listings(
    listings: list[Listing],
    product_id: str | None = None,
    category: str | None = None,
) -> list[Listing]:
    reports = _db_or_file_read(
        lambda: _db_active_reports(),
        lambda: _active_reports(_read_json_list(_reports_path())),
    )
    if not reports:
        return listings

    return [
        listing
        for listing in listings
        if not any(_report_blocks_listing(report, listing, product_id, category) for report in reports)
    ]


def log_outbound_click(
    *,
    url: str,
    tracked_url: str,
    provider: str | None = None,
    category: str | None = None,
    product_id: str | None = None,
    query: str | None = None,
    title: str | None = None,
) -> None:
    now = _now()
    params = parse_qs(urlsplit(tracked_url).query)
    record = {
        "clicked_at": now.isoformat(),
        "provider": provider,
        "category": category,
        "product_id": product_id,
        "query": query,
        "title": title,
        "link_key": _normalized_link_key(tracked_url),
        "ebay_item_id": ebay_item_id_from_url(tracked_url),
        "affiliate_campaign_present": bool(params.get("campid")),
        "affiliate_reference": (params.get("customid") or [None])[0],
        "url": url,
        "tracked_url": tracked_url,
    }

    def db_write() -> None:
        with database_connection() as connection:
            connection.execute(
                """
                INSERT INTO scoutly_outbound_clicks (
                    clicked_at, provider, category, product_id, query, title,
                    link_key, ebay_item_id, affiliate_campaign_present,
                    affiliate_reference, url, tracked_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    now,
                    provider,
                    category,
                    product_id,
                    query,
                    title,
                    record["link_key"],
                    record["ebay_item_id"],
                    record["affiliate_campaign_present"],
                    record["affiliate_reference"],
                    url,
                    tracked_url,
                ),
            )
            connection.execute(
                "DELETE FROM scoutly_outbound_clicks WHERE clicked_at < NOW() - INTERVAL '180 days'"
            )
            connection.execute(
                """
                DELETE FROM scoutly_outbound_clicks
                WHERE id NOT IN (
                    SELECT id FROM scoutly_outbound_clicks
                    ORDER BY clicked_at DESC
                    LIMIT %s
                )
                """,
                (DB_MAX_CLICKS,),
            )

    def file_write() -> None:
        records = _read_json_list(_clicks_path())
        records.append(record)
        _write_json_list(_clicks_path(), records[-MAX_CLICKS:])

    _db_write_or_file(db_write, file_write)


def recent_outbound_clicks(limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(limit, MAX_CLICKS))

    def db_read() -> list[dict[str, Any]]:
        with database_connection() as connection:
            rows = connection.execute(
                """
                SELECT clicked_at, provider, category, product_id, query, title,
                       link_key, ebay_item_id, affiliate_campaign_present,
                       affiliate_reference, url, tracked_url
                FROM scoutly_outbound_clicks
                ORDER BY clicked_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()
        return [_serialize_record(dict(row)) for row in rows]

    return _db_or_file_read(
        db_read,
        lambda: list(reversed(_read_json_list(_clicks_path())[-limit:])),
    )


def active_bad_result_reports(limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(limit, MAX_REPORTS))
    return _db_or_file_read(
        lambda: _db_active_reports(limit=limit, newest_first=True),
        lambda: list(reversed(_active_reports(_read_json_list(_reports_path()))[-limit:])),
    )


def delete_bad_result_report(
    *,
    link_key: str,
    product_id: str | None = None,
    category: str | None = None,
) -> bool:
    def db_delete() -> bool:
        clauses = ["link_key = %s"]
        params: list[Any] = [link_key]
        if product_id:
            clauses.append("product_id = %s")
            params.append(product_id)
        if category:
            clauses.append("category = %s")
            params.append(category)
        with database_connection() as connection:
            cursor = connection.execute(
                f"DELETE FROM scoutly_bad_result_reports WHERE {' AND '.join(clauses)}",
                tuple(params),
            )
            return cursor.rowcount > 0

    if database_configured():
        try:
            return db_delete()
        except Exception:
            logger.exception("PostgreSQL report delete failed; using file fallback.")

    records = _active_reports(_read_json_list(_reports_path()))
    kept: list[dict[str, Any]] = []
    deleted = False
    for record in records:
        if record.get("link_key") != link_key:
            kept.append(record)
            continue
        if product_id and record.get("product_id") != product_id:
            kept.append(record)
            continue
        if category and record.get("category") != category:
            kept.append(record)
            continue
        deleted = True

    if deleted:
        _write_json_list(_reports_path(), kept)
    return deleted


def log_filtered_listings(records_to_log: list[dict[str, Any]]) -> None:
    if not records_to_log:
        return

    normalized: list[dict[str, Any]] = []
    for item in records_to_log:
        url = str(item.get("url") or "")
        if not url:
            continue
        now = item.get("filtered_at") or _now()
        if isinstance(now, str):
            parsed = _parse_dt(now)
            now = parsed or _now()
        normalized.append(
            {
                "filtered_at": now,
                "provider": item.get("provider"),
                "category": item.get("category"),
                "product_id": item.get("product_id"),
                "query": item.get("query"),
                "title": item.get("title"),
                "listing_type": item.get("listing_type"),
                "reasons": list(item.get("reasons") or []),
                "link_key": _normalized_link_key(url),
                "ebay_item_id": ebay_item_id_from_url(url),
                "url": url,
            }
        )

    if not normalized:
        return

    def db_write() -> None:
        values = [
            (
                item["filtered_at"],
                item["provider"],
                item["category"],
                item["product_id"],
                item["query"],
                item["title"],
                item["listing_type"],
                json.dumps(item["reasons"]),
                item["link_key"],
                item["ebay_item_id"],
                item["url"],
            )
            for item in normalized
        ]
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    INSERT INTO scoutly_filtered_listings (
                        filtered_at, provider, category, product_id, query, title,
                        listing_type, reasons, link_key, ebay_item_id, url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s)
                    """,
                    values,
                )
            connection.execute(
                "DELETE FROM scoutly_filtered_listings WHERE filtered_at < NOW() - INTERVAL '45 days'"
            )
            connection.execute(
                """
                DELETE FROM scoutly_filtered_listings
                WHERE id NOT IN (
                    SELECT id FROM scoutly_filtered_listings
                    ORDER BY filtered_at DESC
                    LIMIT %s
                )
                """,
                (DB_MAX_FILTERED,),
            )

    def file_write() -> None:
        records = _read_json_list(_filtered_path())
        for item in normalized:
            records.append(
                {
                    **item,
                    "filtered_at": item["filtered_at"].isoformat(),
                }
            )
        _write_json_list(_filtered_path(), records[-MAX_FILTERED:])

    _db_write_or_file(db_write, file_write)


def log_filtered_listing(
    *,
    url: str,
    title: str | None = None,
    provider: str | None = None,
    category: str | None = None,
    product_id: str | None = None,
    query: str | None = None,
    listing_type: str | None = None,
    reasons: list[str] | None = None,
) -> None:
    log_filtered_listings(
        [
            {
                "url": url,
                "title": title,
                "provider": provider,
                "category": category,
                "product_id": product_id,
                "query": query,
                "listing_type": listing_type,
                "reasons": reasons or [],
            }
        ]
    )

def recent_filtered_listings(limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(limit, MAX_FILTERED))

    def db_read() -> list[dict[str, Any]]:
        with database_connection() as connection:
            rows = connection.execute(
                """
                SELECT filtered_at, provider, category, product_id, query, title,
                       listing_type, reasons, link_key, ebay_item_id, url
                FROM scoutly_filtered_listings
                ORDER BY filtered_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()
        return [_serialize_record(dict(row)) for row in rows]

    return _db_or_file_read(
        db_read,
        lambda: list(reversed(_read_json_list(_filtered_path())[-limit:])),
    )


def analytics_summary() -> dict[str, Any]:
    if database_configured():
        try:
            with database_connection() as connection:
                click_summary = connection.execute(
                    """
                    SELECT COUNT(*) AS total_clicks,
                           COUNT(*) FILTER (WHERE affiliate_campaign_present) AS affiliate_clicks,
                           MAX(clicked_at) AS latest_clicked_at
                    FROM scoutly_outbound_clicks
                    """
                ).fetchone()
                report_count = connection.execute(
                    "SELECT COUNT(*) AS count FROM scoutly_bad_result_reports WHERE expires_at > NOW()"
                ).fetchone()["count"]
                filtered_count = connection.execute(
                    "SELECT COUNT(*) AS count FROM scoutly_filtered_listings"
                ).fetchone()["count"]
                provider_rows = connection.execute(
                    """
                    SELECT COALESCE(provider, 'unknown') AS name, COUNT(*) AS count
                    FROM scoutly_outbound_clicks GROUP BY 1 ORDER BY count DESC
                    """
                ).fetchall()
                category_rows = connection.execute(
                    """
                    SELECT COALESCE(category, 'unknown') AS name, COUNT(*) AS count
                    FROM scoutly_outbound_clicks GROUP BY 1 ORDER BY count DESC
                    """
                ).fetchall()
                latest = connection.execute(
                    """
                    SELECT clicked_at, provider, category, product_id, query, title,
                           link_key, ebay_item_id, affiliate_campaign_present,
                           affiliate_reference, url, tracked_url
                    FROM scoutly_outbound_clicks ORDER BY clicked_at DESC LIMIT 1
                    """
                ).fetchone()

            health = database_health()
            return {
                "total_clicks": int(click_summary["total_clicks"] or 0),
                "affiliate_clicks": int(click_summary["affiliate_clicks"] or 0),
                "active_bad_result_reports": int(report_count or 0),
                "filtered_listing_count": int(filtered_count or 0),
                "manual_filter_rule_count": len(list_manual_filter_rules(include_disabled=True)),
                "provider_counts": {str(row["name"]): int(row["count"]) for row in provider_rows},
                "category_counts": {str(row["name"]): int(row["count"]) for row in category_rows},
                "latest_click": _serialize_record(dict(latest)) if latest else None,
                "storage": health,
            }
        except Exception:
            logger.exception("PostgreSQL analytics summary failed; using file fallback.")

    clicks = _read_json_list(_clicks_path())
    reports = _active_reports(_read_json_list(_reports_path()))
    filtered = _read_json_list(_filtered_path())
    provider_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    affiliate_clicks = 0

    for click in clicks:
        provider = click.get("provider") or "unknown"
        category = click.get("category") or "unknown"
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1
        if click.get("affiliate_campaign_present"):
            affiliate_clicks += 1

    return {
        "total_clicks": len(clicks),
        "affiliate_clicks": affiliate_clicks,
        "active_bad_result_reports": len(reports),
        "filtered_listing_count": len(filtered),
        "manual_filter_rule_count": len(list_manual_filter_rules(include_disabled=True)),
        "provider_counts": provider_counts,
        "category_counts": category_counts,
        "latest_click": clicks[-1] if clicks else None,
        "storage": database_health(),
    }
