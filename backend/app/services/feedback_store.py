from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from app.models.listing import Listing

REPORT_TTL_HOURS = 72
MAX_REPORTS = 500
MAX_CLICKS = 2000
MAX_FILTERED = 3000


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
    records = _active_reports(_read_json_list(_reports_path()), now)

    link_key = _normalized_link_key(report.url)
    record = {
        **asdict(report),
        "link_key": link_key,
        "ebay_item_id": ebay_item_id_from_url(report.url),
        "reported_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    # Keep only the newest report for a given product/category + link key.
    records = [
        existing
        for existing in records
        if not (
            existing.get("link_key") == link_key
            and existing.get("product_id") == report.product_id
            and existing.get("category") == report.category
        )
    ]
    records.append(record)
    records = records[-MAX_REPORTS:]
    _write_json_list(_reports_path(), records)

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
    reports = _active_reports(_read_json_list(_reports_path()))
    if not reports:
        return listings

    kept: list[Listing] = []
    for listing in listings:
        if any(_report_blocks_listing(report, listing, product_id, category) for report in reports):
            continue
        kept.append(listing)
    return kept


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
    records = _read_json_list(_clicks_path())
    params = parse_qs(urlsplit(tracked_url).query)
    records.append(
        {
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
    )
    records = records[-MAX_CLICKS:]
    _write_json_list(_clicks_path(), records)


def recent_outbound_clicks(limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(limit, MAX_CLICKS))
    return list(reversed(_read_json_list(_clicks_path())[-limit:]))


def active_bad_result_reports(limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(limit, MAX_REPORTS))
    return list(reversed(_active_reports(_read_json_list(_reports_path()))[-limit:]))



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
    records = _read_json_list(_filtered_path())
    records.append(
        {
            "filtered_at": _now().isoformat(),
            "provider": provider,
            "category": category,
            "product_id": product_id,
            "query": query,
            "title": title,
            "listing_type": listing_type,
            "reasons": reasons or [],
            "link_key": _normalized_link_key(url),
            "ebay_item_id": ebay_item_id_from_url(url),
            "url": url,
        }
    )
    records = records[-MAX_FILTERED:]
    _write_json_list(_filtered_path(), records)


def recent_filtered_listings(limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(limit, MAX_FILTERED))
    return list(reversed(_read_json_list(_filtered_path())[-limit:]))


def analytics_summary() -> dict[str, Any]:
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
        "provider_counts": provider_counts,
        "category_counts": category_counts,
        "latest_click": clicks[-1] if clicks else None,
    }
