from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

PRODUCT_COOLDOWN_DAYS = 30
STORY_NOVELTY_DAYS = 14
CATEGORY_RECENCY_DAYS = 7
MIN_SELECTION_SCORE = 30.0
EASTERN = ZoneInfo("America/Detroit")


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def classify_story(signal: dict[str, Any]) -> str:
    tags = set(signal.get("signal_tags") or [])
    primary = str(signal.get("primary_signal") or "")
    median_move = float(signal.get("median_change_percent") or 0.0)
    latest_median = float(signal.get("latest_median_price") or 0.0)
    latest_best = float(signal.get("latest_best_price") or 0.0)
    spread = ((latest_best - latest_median) / latest_median * 100.0) if latest_median > 0 and latest_best > 0 else 0.0

    if primary == "price_spike" and ("standout_deal" in tags or spread <= -15.0):
        return "price_spike_with_bargain"
    if primary == "price_drop":
        return "price_drop"
    if primary == "price_spike":
        return "price_spike"
    if primary == "standout_deal" or spread <= -18.0:
        return "hidden_bargain"
    if primary == "inventory_surge":
        return "inventory_surge"
    if primary == "inventory_squeeze":
        return "inventory_squeeze"
    if median_move <= -7.5:
        return "price_drop"
    if median_move >= 10.0:
        return "price_spike"
    return "watch"


def _recent(history: list[dict[str, Any]], *, status: str, after: datetime) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in history:
        if str(item.get("status") or "") != status:
            continue
        when = parse_time(item.get("sent_at") or item.get("created_at") or item.get("due_at"))
        if when is not None and when >= after:
            rows.append(item)
    rows.sort(
        key=lambda item: parse_time(item.get("sent_at") or item.get("created_at") or item.get("due_at")) or datetime.min.replace(tzinfo=UTC),
        reverse=True,
    )
    return rows


def select_story(
    signals: list[dict[str, Any]],
    history: list[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> dict[str, Any] | None:
    now = (now or datetime.now(UTC)).astimezone(UTC)
    sent_30d = _recent(history, status="sent", after=now - timedelta(days=PRODUCT_COOLDOWN_DAYS))
    sent_14d = _recent(history, status="sent", after=now - timedelta(days=STORY_NOVELTY_DAYS))
    sent_7d = _recent(history, status="sent", after=now - timedelta(days=CATEGORY_RECENCY_DAYS))
    pending = [item for item in history if str(item.get("status") or "") in {"draft", "scheduled", "sending", "needs_approval"}]

    # Never create two PriceSift drafts in one Eastern calendar day.
    today = now.astimezone(EASTERN).date()
    for item in history:
        created = parse_time(item.get("created_at"))
        if created is not None and created.astimezone(EASTERN).date() == today and item.get("pricesift_generated"):
            return None

    last_product = str(sent_30d[0].get("product_id") or "") if sent_30d else ""
    cooldown_products = {str(item.get("product_id") or "") for item in sent_30d if item.get("product_id")}
    pending_products = {str(item.get("product_id") or "") for item in pending if item.get("product_id")}
    recent_story_types = {str(item.get("story_type") or "") for item in sent_14d}
    recent_categories = {str(item.get("category") or "") for item in sent_7d}
    last_category = str(sent_30d[0].get("category") or "") if sent_30d else ""

    candidates: list[dict[str, Any]] = []
    for signal in signals:
        if not signal.get("video_worthy"):
            continue
        base_score = float(signal.get("video_score") or 0.0)
        if base_score < MIN_SELECTION_SCORE:
            continue

        product_id = str(signal.get("product_id") or "")
        category = str(signal.get("category") or "")
        story_type = classify_story(signal)
        if not product_id or story_type == "watch":
            continue
        if product_id == last_product or product_id in cooldown_products or product_id in pending_products:
            continue

        adjusted = base_score
        reasons: list[str] = []
        if story_type in recent_story_types:
            adjusted -= 12.0
            reasons.append("recent story type")
        else:
            adjusted += 4.0
            reasons.append("fresh story type")
        if category and category in recent_categories:
            adjusted -= 6.0
            reasons.append("recent category")
        if category and category == last_category:
            adjusted -= 3.0
            reasons.append("same category as last post")
        if story_type in {"price_spike_with_bargain", "hidden_bargain"}:
            adjusted += 5.0
            reasons.append("clear buyer-action contradiction")
        if str(signal.get("confidence") or "") == "high":
            adjusted += 3.0
            reasons.append("high confidence")

        if adjusted < MIN_SELECTION_SCORE:
            continue
        candidates.append(
            {
                "story_type": story_type,
                "selection_score": round(adjusted, 1),
                "selection_reasons": reasons,
                "signal": signal,
            }
        )

    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            -float(item["selection_score"]),
            -float(item["signal"].get("video_score") or 0.0),
            str(item["signal"].get("product_label") or ""),
        )
    )
    return candidates[0]
