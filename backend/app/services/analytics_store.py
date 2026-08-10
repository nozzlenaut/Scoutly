from __future__ import annotations

import json
import logging
import os
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
MAX_FILE_EVENTS = 20_000
DB_MAX_EVENTS = 100_000


def _now() -> datetime:
    return datetime.now(UTC)


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _events_path() -> Path:
    return _data_dir() / "search_events.json"


def _read_events() -> list[dict[str, Any]]:
    path = _events_path()
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return payload if isinstance(payload, list) else []


def _write_events(records: list[dict[str, Any]]) -> None:
    path = _events_path()
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(records[-MAX_FILE_EVENTS:], indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _parse_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


@dataclass
class SearchEvent:
    category: str | None
    query: str
    product_id: str | None
    product_label: str | None
    resolved: bool
    result_count: int
    provider_counts: dict[str, int]
    candidate_count: int = 0
    filtered_count: int = 0
    no_inventory: bool = True
    us_only: bool = False
    source: str = "public"


def log_search_event(event: SearchEvent) -> None:
    now = _now()
    record = {**asdict(event), "searched_at": now.isoformat()}

    if database_configured():
        try:
            with database_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO scoutly_search_events (
                        searched_at, category, query, product_id, product_label,
                        resolved, result_count, provider_counts, candidate_count,
                        filtered_count, no_inventory, us_only, source
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s)
                    """,
                    (
                        now,
                        event.category,
                        event.query,
                        event.product_id,
                        event.product_label,
                        event.resolved,
                        max(0, event.result_count),
                        json.dumps(event.provider_counts),
                        max(0, event.candidate_count),
                        max(0, event.filtered_count),
                        event.no_inventory,
                        event.us_only,
                        event.source,
                    ),
                )
                connection.execute(
                    "DELETE FROM scoutly_search_events WHERE searched_at < NOW() - INTERVAL '365 days'"
                )
                connection.execute(
                    """
                    DELETE FROM scoutly_search_events
                    WHERE id NOT IN (
                        SELECT id FROM scoutly_search_events
                        ORDER BY searched_at DESC
                        LIMIT %s
                    )
                    """,
                    (DB_MAX_EVENTS,),
                )
            return
        except Exception:
            logger.exception("PostgreSQL search analytics write failed; using file fallback.")

    records = _read_events()
    records.append(record)
    _write_events(records)


def _records_for_days(days: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cutoff = _now() - timedelta(days=days)
    if database_configured():
        try:
            with database_connection() as connection:
                search_rows = connection.execute(
                    """
                    SELECT searched_at, category, query, product_id, product_label,
                           resolved, result_count, provider_counts, candidate_count,
                           filtered_count, no_inventory, us_only, source
                    FROM scoutly_search_events
                    WHERE searched_at >= %s AND source = 'public'
                    ORDER BY searched_at ASC
                    """,
                    (cutoff,),
                ).fetchall()
                click_rows = connection.execute(
                    """
                    SELECT clicked_at, provider, category, product_id, query, title,
                           affiliate_campaign_present
                    FROM scoutly_outbound_clicks
                    WHERE clicked_at >= %s
                    ORDER BY clicked_at ASC
                    """,
                    (cutoff,),
                ).fetchall()
            return [dict(row) for row in search_rows], [dict(row) for row in click_rows]
        except Exception:
            logger.exception("PostgreSQL analytics digest failed; using file fallback.")

    search_rows = [
        row for row in _read_events()
        if row.get("source", "public") == "public"
        and (_parse_dt(row.get("searched_at")) or datetime.min.replace(tzinfo=UTC)) >= cutoff
    ]
    # Click fallback lives in feedback_store's file. Import lazily to avoid a cycle.
    try:
        from app.services.feedback_store import recent_outbound_clicks
        click_rows = [
            row for row in recent_outbound_clicks(2000)
            if (_parse_dt(row.get("clicked_at")) or datetime.min.replace(tzinfo=UTC)) >= cutoff
        ]
    except Exception:
        click_rows = []
    return search_rows, click_rows


def _pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 1)


def _display_query(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalize_unresolved_query(value: Any) -> str:
    normalized = unicodedata.normalize("NFKC", _display_query(value)).casefold()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[^\w\s]+", " ", normalized, flags=re.UNICODE)
    return re.sub(r"\s+", " ", normalized).strip()


def _model_clue_tokens(value: str) -> list[str]:
    return re.findall(
        r"\b(?:[a-z]*\d+[a-z\d]*|i|ii|iii|iv|v|vi|vii|viii|ix|x)\b",
        value,
    )


def _obvious_query_variants(left: str, right: str) -> bool:
    """Conservatively group punctuation variants and likely one-edit typos.

    Model numbers are kept separate even when the surrounding text is almost
    identical. The fuzzy threshold is intentionally high so this report does
    not turn nearby products into fake demand for one product.
    """

    if left == right:
        return True
    if min(len(left), len(right)) < 6 or left[:1] != right[:1]:
        return False
    if _model_clue_tokens(left) != _model_clue_tokens(right):
        return False
    left_tokens = left.split()
    right_tokens = right.split()
    if len(left_tokens) != len(right_tokens):
        return False
    changed_tokens = [
        (left_token, right_token)
        for left_token, right_token in zip(left_tokens, right_tokens, strict=True)
        if left_token != right_token
    ]
    if len(changed_tokens) != 1:
        return False
    changed_left, changed_right = changed_tokens[0]
    if min(len(changed_left), len(changed_right)) < 4:
        return False
    return (
        SequenceMatcher(None, changed_left, changed_right).ratio() >= 0.75
        and SequenceMatcher(None, left, right).ratio() >= 0.92
    )


def _iso_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _top_unresolved_searches(searches: list[dict[str, Any]], limit: int = 15) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []

    for row in searches:
        if bool(row.get("resolved")):
            continue
        query = _display_query(row.get("query"))
        normalized_query = _normalize_unresolved_query(query)
        if not query or not normalized_query:
            continue

        category = str(row.get("category") or "unknown")
        searched_at = _parse_dt(row.get("searched_at"))
        cluster = next(
            (
                item
                for item in clusters
                if item["category"] == category
                and any(
                    _obvious_query_variants(normalized_query, existing)
                    for existing in item["normalized_queries"]
                )
            ),
            None,
        )
        if cluster is None:
            cluster = {
                "category": category,
                "normalized_queries": set(),
                "variant_counts": Counter(),
                "variant_labels": {},
                "variant_last_seen": {},
                "searches": 0,
                "first_searched_at": searched_at,
                "last_searched_at": searched_at,
            }
            clusters.append(cluster)

        variant_key = query.casefold()
        cluster["normalized_queries"].add(normalized_query)
        cluster["variant_counts"][variant_key] += 1
        cluster["variant_labels"].setdefault(variant_key, query)
        if searched_at is not None:
            cluster["variant_last_seen"][variant_key] = max(
                searched_at,
                cluster["variant_last_seen"].get(variant_key, searched_at),
            )
            first_seen = cluster["first_searched_at"]
            last_seen = cluster["last_searched_at"]
            cluster["first_searched_at"] = min(first_seen, searched_at) if first_seen else searched_at
            cluster["last_searched_at"] = max(last_seen, searched_at) if last_seen else searched_at
        cluster["searches"] += 1

    rows: list[dict[str, Any]] = []
    for cluster in clusters:
        variants = sorted(
            cluster["variant_counts"],
            key=lambda key: (
                cluster["variant_counts"][key],
                cluster["variant_last_seen"].get(key, datetime.min.replace(tzinfo=UTC)),
                cluster["variant_labels"][key],
            ),
            reverse=True,
        )
        representative = variants[0]
        rows.append(
            {
                "category": cluster["category"],
                "query": cluster["variant_labels"][representative],
                "normalized_query": _normalize_unresolved_query(
                    cluster["variant_labels"][representative]
                ),
                "searches": cluster["searches"],
                "variants": [
                    {
                        "query": cluster["variant_labels"][key],
                        "searches": cluster["variant_counts"][key],
                    }
                    for key in variants[:5]
                ],
                "first_searched_at": _iso_datetime(cluster["first_searched_at"]),
                "last_searched_at": _iso_datetime(cluster["last_searched_at"]),
            }
        )

    rows.sort(
        key=lambda row: (
            row["searches"],
            _parse_dt(row.get("last_searched_at")) or datetime.min.replace(tzinfo=UTC),
            row["query"],
        ),
        reverse=True,
    )
    return rows[: max(1, limit)]


def analytics_digest(days: int = 30) -> dict[str, Any]:
    days = max(1, min(days, 365))
    searches, clicks = _records_for_days(days)

    search_count = len(searches)
    resolved_count = sum(1 for row in searches if bool(row.get("resolved")))
    with_results_count = sum(1 for row in searches if int(row.get("result_count") or 0) > 0)
    no_result_count = search_count - with_results_count
    unresolved_count = sum(1 for row in searches if not bool(row.get("resolved")))
    us_only_count = sum(1 for row in searches if bool(row.get("us_only")))
    total_click_count = len(clicks)
    top_unresolved_searches = _top_unresolved_searches(searches)

    category_searches: Counter[str] = Counter()
    category_no_results: Counter[str] = Counter()
    category_clicks: Counter[str] = Counter()
    provider_shown: Counter[str] = Counter()
    provider_clicks: Counter[str] = Counter()
    query_stats: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {"searches": 0, "no_results": 0, "clicks": 0}
    )
    search_refs: list[dict[str, Any]] = []
    daily: dict[str, dict[str, int]] = defaultdict(lambda: {"searches": 0, "clicks": 0, "no_results": 0})

    for row in searches:
        category = str(row.get("category") or "unknown")
        query = str(row.get("query") or "").strip()
        label = str(row.get("product_label") or query or "Unknown search")
        product_id = str(row.get("product_id") or "")
        category_searches[category] += 1
        is_no_result = int(row.get("result_count") or 0) <= 0
        if is_no_result:
            category_no_results[category] += 1
        key = (category, product_id, label)
        query_stats[key]["searches"] += 1
        if is_no_result:
            query_stats[key]["no_results"] += 1
        searched_at = _parse_dt(row.get("searched_at"))
        search_refs.append(
            {
                "key": key,
                "category": category,
                "product_id": product_id,
                "query": query.casefold(),
                "label": label.casefold(),
                "searched_at": searched_at,
            }
        )
        provider_counts = row.get("provider_counts") or {}
        if isinstance(provider_counts, str):
            try:
                provider_counts = json.loads(provider_counts)
            except json.JSONDecodeError:
                provider_counts = {}
        if isinstance(provider_counts, dict):
            for provider, count in provider_counts.items():
                provider_shown[str(provider)] += int(count or 0)
        if searched_at:
            day = searched_at.date().isoformat()
            daily[day]["searches"] += 1
            if is_no_result:
                daily[day]["no_results"] += 1

    linked_click_count = 0
    linked_affiliate_click_count = 0
    historical_click_count = 0
    historical_affiliate_click_count = 0

    for row in clicks:
        category = str(row.get("category") or "unknown")
        provider = str(row.get("provider") or "unknown")
        product_id = str(row.get("product_id") or "")
        click_query = str(row.get("query") or "").strip().casefold()
        clicked_at = _parse_dt(row.get("clicked_at"))

        # A click counts toward search analytics only when it can be tied to a
        # matching public search that happened before the click. This prevents
        # older affiliate click history from inflating a newly deployed search
        # analytics window. Prefer exact product IDs; fall back to query/label.
        matching_refs = []
        for ref in search_refs:
            if ref["category"] != category:
                continue
            searched_at = ref.get("searched_at")
            if clicked_at and searched_at and clicked_at < searched_at:
                continue
            exact_product = bool(product_id and ref["product_id"] and product_id == ref["product_id"])
            matching_query = bool(click_query and click_query in {ref["query"], ref["label"]})
            if exact_product or matching_query:
                matching_refs.append(ref)

        if not matching_refs:
            historical_click_count += 1
            if bool(row.get("affiliate_campaign_present")):
                historical_affiliate_click_count += 1
            continue

        matched_ref = max(
            matching_refs,
            key=lambda ref: ref.get("searched_at") or datetime.min.replace(tzinfo=UTC),
        )
        linked_click_count += 1
        if bool(row.get("affiliate_campaign_present")):
            linked_affiliate_click_count += 1
        category_clicks[category] += 1
        provider_clicks[provider] += 1
        query_stats[matched_ref["key"]]["clicks"] += 1
        if clicked_at:
            daily[clicked_at.date().isoformat()]["clicks"] += 1

    click_count = linked_click_count
    affiliate_click_count = linked_affiliate_click_count

    category_rows = []
    for category, count in category_searches.most_common():
        no_results = category_no_results[category]
        category_rows.append(
            {
                "category": category,
                "searches": count,
                "with_results": count - no_results,
                "no_results": no_results,
                "no_result_rate": _pct(no_results, count),
                "clicks": category_clicks[category],
            }
        )

    top_searches = []
    for (category, product_id, label), stats in sorted(
        query_stats.items(),
        key=lambda item: (item[1]["searches"], item[1]["clicks"]),
        reverse=True,
    )[:15]:
        top_searches.append(
            {
                "category": category,
                "product_id": product_id or None,
                "label": label,
                **stats,
            }
        )

    lines = [
        f"PriceSift analytics — last {days} days",
        f"Searches: {search_count}",
        f"Resolved catalog/ISBN searches: {resolved_count} ({_pct(resolved_count, search_count) or 0}%)",
        f"Searches with results: {with_results_count} ({_pct(with_results_count, search_count) or 0}%)",
        f"No-result searches: {no_result_count} ({_pct(no_result_count, search_count) or 0}%)",
        f"Unresolved catalog/ISBN searches: {unresolved_count} ({_pct(unresolved_count, search_count) or 0}%)",
        f"Verified listing clicks: {click_count}",
        f"Verified search-to-click rate: {_pct(click_count, search_count) or 0}%",
        f"Verified clicks not linked to a recorded search: {historical_click_count}",
        f"US-only searches: {us_only_count} ({_pct(us_only_count, search_count) or 0}%)",
    ]
    if category_rows:
        lines.append("Top categories:")
        for row in category_rows[:10]:
            lines.append(
                f"- {row['category']}: {row['searches']} searches, {row['no_results']} no-results, {row['clicks']} clicks"
            )
    if top_searches:
        lines.append("Top searches:")
        for row in top_searches[:10]:
            lines.append(
                f"- {row['label']} ({row['category']}): {row['searches']} searches, {row['no_results']} no-results, {row['clicks']} clicks"
            )
    if top_unresolved_searches:
        lines.append("Top unresolved searches:")
        for row in top_unresolved_searches[:10]:
            lines.append(
                f"- {row['query']} ({row['category']}): {row['searches']} unresolved searches"
            )
    if provider_clicks:
        lines.append("Provider clicks: " + ", ".join(f"{name} {count}" for name, count in provider_clicks.most_common()))

    return {
        "days": days,
        "search_count": search_count,
        "resolved_count": resolved_count,
        "with_results_count": with_results_count,
        "no_result_count": no_result_count,
        "no_result_rate": _pct(no_result_count, search_count),
        "unresolved_count": unresolved_count,
        "unresolved_rate": _pct(unresolved_count, search_count),
        "us_only_count": us_only_count,
        "us_only_rate": _pct(us_only_count, search_count),
        "click_count": click_count,
        "affiliate_click_count": affiliate_click_count,
        "total_click_count": total_click_count,
        "historical_click_count": historical_click_count,
        "historical_affiliate_click_count": historical_affiliate_click_count,
        "approximate_click_rate": _pct(click_count, search_count),
        "category_rows": category_rows,
        "top_searches": top_searches,
        "top_unresolved_searches": top_unresolved_searches,
        "provider_shown_counts": dict(provider_shown.most_common()),
        "provider_click_counts": dict(provider_clicks.most_common()),
        "daily": [{"date": day, **daily[day]} for day in sorted(daily)],
        "summary_text": "\n".join(lines),
        "privacy_note": "No IP addresses, accounts, or cookies are stored. This admin-only report includes the search text users entered.",
    }
