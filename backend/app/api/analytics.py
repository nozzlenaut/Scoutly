from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.admin_auth import require_admin_token as _require_admin_token
from app.services.analytics_forensics import analytics_forensics
from app.services.analytics_store import (
    _normalize_unresolved_query,
    _now,
    _parse_dt,
    _read_events,
    analytics_digest,
)
from app.services.beta_feedback_store import list_beta_feedback
from app.services.database import database_configured, database_connection
from app.services.feature_settings import (
    ai_console_review_status,
    set_ai_console_review_enabled,
)
from app.services.feedback_store import (
    active_bad_result_reports,
    analytics_summary,
    delete_bad_result_report,
    recent_filtered_listings,
    recent_outbound_clicks,
)
from app.services.filter_rules import (
    ManualFilterRule,
    add_manual_filter_rule,
    delete_manual_filter_rule,
    list_manual_filter_rules,
)
from app.services.goodreads_analytics_store import goodreads_analytics_digest

router = APIRouter(tags=["Analytics"])


class ManualFilterRuleRequest(BaseModel):
    phrase: str = Field(min_length=2, max_length=120)
    category: str | None = Field(default=None, max_length=80)
    product_id: str | None = Field(default=None, max_length=160)
    except_phrases: list[str] = Field(default_factory=list, max_length=12)
    note: str | None = Field(default=None, max_length=240)
    source_title: str | None = Field(default=None, max_length=300)
    source_item_id: str | None = Field(default=None, max_length=80)


class ManualFilterRuleResponse(BaseModel):
    id: str
    phrase: str
    category: str | None = None
    product_id: str | None = None
    except_phrases: list[str] = Field(default_factory=list)
    note: str | None = None
    source_title: str | None = None
    source_item_id: str | None = None
    enabled: bool = True
    created_at: str


class AIConsoleBetaToggleRequest(BaseModel):
    enabled: bool


def _pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 1)


def _seo_page_origin_rows(days: int) -> list[dict[str, Any]]:
    """Return non-counted markers for searches launched from curated /used pages."""

    cutoff = _now() - timedelta(days=days)
    raw_rows: list[dict[str, Any]] = []

    if database_configured():
        try:
            with database_connection() as connection:
                rows = connection.execute(
                    """
                    SELECT searched_at, category, query, product_label, result_count
                    FROM scoutly_search_events
                    WHERE searched_at >= %s AND source = 'origin:seo_page'
                    ORDER BY searched_at ASC
                    """,
                    (cutoff,),
                ).fetchall()
            raw_rows = [dict(row) for row in rows]
        except Exception:
            raw_rows = []

    if not raw_rows:
        raw_rows = [
            row
            for row in _read_events()
            if row.get("source") == "origin:seo_page"
            and (_parse_dt(row.get("searched_at")) or cutoff) >= cutoff
        ]

    grouped: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {"searches": 0, "no_results": 0}
    )
    for row in raw_rows:
        category = str(row.get("category") or "unknown")
        label = str(row.get("product_label") or row.get("query") or "").strip()
        normalized = _normalize_unresolved_query(label)
        if not normalized:
            continue
        key = (category, normalized)
        grouped[key]["category"] = category
        grouped[key]["label"] = label
        grouped[key]["normalized_label"] = normalized
        grouped[key]["searches"] += 1
        if int(row.get("result_count") or 0) <= 0:
            grouped[key]["no_results"] += 1

    rows = list(grouped.values())
    rows.sort(key=lambda row: (row["searches"], row["label"]), reverse=True)
    return rows


def _enrich_demand_analytics(digest: dict[str, Any], days: int) -> None:
    seo_rows = _seo_page_origin_rows(days)
    seo_lookup = {
        (row["category"], row["normalized_label"]): row
        for row in seo_rows
    }
    seo_category_counts: dict[str, int] = defaultdict(int)
    seo_category_no_results: dict[str, int] = defaultdict(int)
    for row in seo_rows:
        seo_category_counts[row["category"]] += int(row["searches"])
        seo_category_no_results[row["category"]] += int(row["no_results"])

    seo_total = sum(int(row["searches"]) for row in seo_rows)
    digest["seo_page_search_count"] = seo_total
    digest["demand_search_count"] = max(0, int(digest.get("search_count") or 0) - seo_total)
    digest["seo_page_searches"] = seo_rows
    digest["seo_origin_tracking_note"] = (
        "SEO-page launch markers are recorded only from this release forward. "
        "Older searches in the selected window remain legacy/unknown and cannot be separated retroactively."
    )

    for row in digest.get("category_rows", []):
        category = str(row.get("category") or "unknown")
        seo_searches = seo_category_counts.get(category, 0)
        seo_no_results = seo_category_no_results.get(category, 0)
        row["seo_page_searches"] = seo_searches
        row["demand_searches"] = max(0, int(row.get("searches") or 0) - seo_searches)
        row["demand_no_results"] = max(0, int(row.get("no_results") or 0) - seo_no_results)

    for row in digest.get("top_searches", []):
        category = str(row.get("category") or "unknown")
        normalized = _normalize_unresolved_query(row.get("label"))
        seo_row = seo_lookup.get((category, normalized), {})
        seo_searches = int(seo_row.get("searches") or 0)
        seo_no_results = int(seo_row.get("no_results") or 0)
        row["seo_page_searches"] = seo_searches
        row["demand_searches"] = max(0, int(row.get("searches") or 0) - seo_searches)
        row["demand_no_results"] = max(0, int(row.get("no_results") or 0) - seo_no_results)

    digest["top_searches"] = sorted(
        digest.get("top_searches", []),
        key=lambda row: (
            int(row.get("demand_searches") or 0),
            int(row.get("clicks") or 0),
            int(row.get("searches") or 0),
        ),
        reverse=True,
    )


def _build_summary_text(digest: dict[str, Any]) -> str:
    search_count = int(digest.get("search_count") or 0)
    demand_value = digest.get("demand_search_count")
    demand_search_count = search_count if demand_value is None else int(demand_value)
    resolved_count = int(digest.get("resolved_count") or 0)
    with_results_count = int(digest.get("with_results_count") or 0)
    no_result_count = int(digest.get("no_result_count") or 0)
    unresolved_count = int(digest.get("unresolved_count") or 0)
    click_count = int(digest.get("click_count") or 0)
    historical_click_count = int(digest.get("historical_click_count") or 0)
    us_only_count = int(digest.get("us_only_count") or 0)
    seo_page_search_count = int(digest.get("seo_page_search_count") or 0)

    lines = [
        f"PriceSift analytics — last {digest['days']} days",
        f"Searches: {search_count}",
        f"Demand searches excluding tracked SEO-page launches: {demand_search_count}",
        f"Tracked SEO-page search launches: {seo_page_search_count}",
        f"Resolved catalog/ISBN searches: {resolved_count} ({_pct(resolved_count, search_count) or 0}%)",
        f"Searches with results: {with_results_count} ({_pct(with_results_count, search_count) or 0}%)",
        f"No-result searches: {no_result_count} ({_pct(no_result_count, search_count) or 0}%)",
        f"Unresolved catalog/ISBN searches: {unresolved_count} ({_pct(unresolved_count, search_count) or 0}%)",
        f"Verified listing clicks: {click_count}",
        f"Verified search-to-click rate: {_pct(click_count, search_count) or 0}%",
        f"Verified clicks not linked to a recorded search: {historical_click_count}",
        f"US-only searches: {us_only_count} ({_pct(us_only_count, search_count) or 0}%)",
    ]

    category_rows = digest.get("category_rows", [])
    if category_rows:
        lines.append("Top categories:")
        for row in category_rows[:10]:
            lines.append(
                f"- {row['category']}: {row.get('demand_searches', row['searches'])} demand searches, "
                f"{row['searches']} total, {row.get('seo_page_searches', 0)} SEO-page launches, "
                f"{row['no_results']} no-results, {row['clicks']} clicks"
            )

    top_searches = digest.get("top_searches", [])
    if top_searches:
        lines.append("Top searches:")
        for row in top_searches[:10]:
            lines.append(
                f"- {row['label']} ({row['category']}): "
                f"{row.get('demand_searches', row['searches'])} demand searches, "
                f"{row['searches']} total, {row.get('seo_page_searches', 0)} SEO-page launches, "
                f"{row['no_results']} no-results, {row['clicks']} clicks"
            )

    unresolved = digest.get("top_unresolved_searches", [])
    if unresolved:
        lines.append("Top unresolved searches:")
        for row in unresolved[:10]:
            lines.append(
                f"- {row['query']} ({row['category']}): {row['searches']} unresolved searches"
            )

    provider_clicks = digest.get("provider_click_counts", {})
    if provider_clicks:
        lines.append(
            "Provider clicks: "
            + ", ".join(
                f"{name} {count}"
                for name, count in sorted(
                    provider_clicks.items(), key=lambda item: item[1], reverse=True
                )
            )
        )

    lines.append(
        "SEO-origin note: source tagging starts with this release; older searches remain legacy/unknown."
    )
    return "\n".join(lines)


@router.get("/analytics/summary")
def get_analytics_summary(token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return analytics_summary()


@router.get("/analytics/digest")
def get_analytics_digest(
    days: int = Query(30, ge=1, le=365),
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    digest = analytics_digest(days)
    _enrich_demand_analytics(digest, days)
    digest["summary_text"] = _build_summary_text(digest)
    forensics = analytics_forensics(days)
    digest["forensics"] = forensics
    digest["summary_text"] = (
        digest["summary_text"]
        + "\nForensic checks:"
        + f"\n- Rapid repeat searches within {forensics['rapid_repeat_window_seconds']}s: "
        + f"{forensics['rapid_repeat_count']} ({forensics['rapid_repeat_rate'] or 0}%)"
        + f"\n- Busiest minute: {forensics['busiest_minute_searches']} searches"
        + f"\n- Minutes with 10+ searches: {forensics['minutes_with_10_or_more_searches']}"
        + f"\n- Minutes with 20+ searches: {forensics['minutes_with_20_or_more_searches']}"
    )
    return digest


@router.get("/analytics/goodreads")
def get_goodreads_analytics_digest(
    days: int = Query(30, ge=1, le=365),
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    return goodreads_analytics_digest(days)


@router.get("/analytics/clicks")
def get_recent_clicks(
    limit: int = Query(50, ge=1, le=200),
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    return {"clicks": recent_outbound_clicks(limit)}


@router.get("/analytics/reports")
def get_active_reports(
    limit: int = Query(50, ge=1, le=200),
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    return {"reports": active_bad_result_reports(limit)}


@router.get("/analytics/filtered")
def get_recent_filtered(
    limit: int = Query(50, ge=1, le=200),
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    return {"filtered": recent_filtered_listings(limit)}


@router.get("/analytics/beta-feedback")
def get_beta_feedback(
    limit: int = Query(100, ge=1, le=500),
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    return {"feedback": list_beta_feedback(limit)}


@router.get("/analytics/ai-console-beta")
def get_ai_console_beta_status(token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return ai_console_review_status()


@router.post("/analytics/ai-console-beta")
def update_ai_console_beta(
    payload: AIConsoleBetaToggleRequest,
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    current = ai_console_review_status()
    if payload.enabled and not current.get("api_key_configured"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configure OPENAI_API_KEY before enabling the AI console beta.",
        )
    set_ai_console_review_enabled(payload.enabled)
    return ai_console_review_status()


@router.get("/analytics/filter-rules")
def get_manual_filter_rules(token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {
        "rules": list(
            reversed(list_manual_filter_rules(include_disabled=True))
        )
    }


@router.post(
    "/analytics/filter-rules",
    response_model=ManualFilterRuleResponse,
)
def create_manual_filter_rule(
    payload: ManualFilterRuleRequest,
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    try:
        return add_manual_filter_rule(
            ManualFilterRule(
                phrase=payload.phrase,
                category=payload.category,
                product_id=payload.product_id,
                except_phrases=payload.except_phrases,
                note=payload.note,
                source_title=payload.source_title,
                source_item_id=payload.source_item_id,
            )
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/analytics/filter-rules/{rule_id}")
def remove_manual_filter_rule(
    rule_id: str,
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    deleted = delete_manual_filter_rule(rule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filter rule not found.",
        )
    return {"status": "deleted", "id": rule_id}


@router.delete("/analytics/reports/{link_key:path}")
def remove_bad_result_report(
    link_key: str,
    token: str | None = Query(None),
    product_id: str | None = Query(None),
    category: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    deleted = delete_bad_result_report(
        link_key=link_key,
        product_id=product_id,
        category=category,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )
    return {"status": "deleted", "link_key": link_key}
