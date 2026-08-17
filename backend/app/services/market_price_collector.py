from __future__ import annotations

import asyncio
import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from app.providers.ebay import ebay_config_from_env
from app.services import search_service
from app.services.price_store import price_overview
from app.services.product_discovery import resolve_discoverable_product
from app.services.qa_store import load_qa_cases

logger = logging.getLogger(__name__)

DEFAULT_TRACKED_CATEGORIES = ("consoles", "gpus", "cpus")
DEFAULT_BATCH_SIZE = 5
DEFAULT_INTERVAL_SECONDS = 60 * 60
DEFAULT_MIN_AGE_HOURS = 20
DEFAULT_START_DELAY_SECONDS = 45
SNAPSHOT_SOURCE = "scheduled_tracker"


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        logger.warning("Ignoring invalid integer %s=%r", name, raw)
        return default
    return max(minimum, min(maximum, value))


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    logger.warning("Ignoring invalid boolean %s=%r", name, raw)
    return default


def tracked_categories() -> tuple[str, ...]:
    raw = os.getenv("SCOUTLY_PRICE_TRACKING_CATEGORIES", "").strip()
    if not raw:
        return DEFAULT_TRACKED_CATEGORIES
    categories = tuple(
        dict.fromkeys(part.strip().lower() for part in raw.split(",") if part.strip())
    )
    return categories or DEFAULT_TRACKED_CATEGORIES


def price_tracking_enabled() -> bool:
    if not _env_bool("SCOUTLY_PRICE_TRACKING_ENABLED", True):
        return False
    # Existing search code only persists real eBay observations. Do not start a
    # background collector when the deployment cannot make live eBay requests.
    return ebay_config_from_env() is not None


def tracked_price_cases(cases: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return one high-priority QA query per tracked market product.

    Reusing the curated QA registry keeps the scheduler on exact products whose
    matching/filtering behavior is already covered by PriceSift's test surface.
    The default market intentionally starts narrow: consoles, GPUs, and CPUs.
    """

    source_cases = load_qa_cases() if cases is None else cases
    categories = set(tracked_categories())
    unique: dict[str, dict[str, Any]] = {}

    for case in source_cases:
        category = str(case.get("category") or "").strip().lower()
        product_id = str(case.get("expected_product_id") or "").strip()
        query = str(case.get("query") or "").strip()
        priority = str(case.get("priority") or "").strip().lower()
        if category not in categories or priority != "high":
            continue
        if not product_id or not query:
            continue
        unique.setdefault(product_id, case)

    return sorted(
        unique.values(),
        key=lambda case: (
            str(case.get("category") or ""),
            str(case.get("expected_label") or case.get("query") or ""),
        ),
    )


def _parse_observed_at(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def due_tracked_price_cases(
    cases: list[dict[str, Any]],
    overview: dict[str, Any],
    *,
    now: datetime | None = None,
    min_age_hours: int | None = None,
) -> list[dict[str, Any]]:
    observed_now = (now or datetime.now(UTC)).astimezone(UTC)
    age_hours = min_age_hours if min_age_hours is not None else _env_int(
        "SCOUTLY_PRICE_TRACKING_MIN_AGE_HOURS",
        DEFAULT_MIN_AGE_HOURS,
        6,
        168,
    )
    cutoff = observed_now - timedelta(hours=age_hours)

    last_by_product: dict[str, datetime] = {}
    for product in overview.get("products", []):
        product_id = str(product.get("product_id") or "").strip()
        observed_at = _parse_observed_at(product.get("last_observed_at"))
        if product_id and observed_at is not None:
            last_by_product[product_id] = observed_at

    due: list[dict[str, Any]] = []
    for case in cases:
        product_id = str(case.get("expected_product_id") or "").strip()
        last_observed = last_by_product.get(product_id)
        if last_observed is None or last_observed <= cutoff:
            due.append(case)

    # Products never observed come first. After that, rotate through the oldest
    # observations so small hourly batches spread API load naturally.
    return sorted(
        due,
        key=lambda case: (
            last_by_product.get(str(case.get("expected_product_id") or "")) is not None,
            last_by_product.get(str(case.get("expected_product_id") or ""))
            or datetime.min.replace(tzinfo=UTC),
            str(case.get("category") or ""),
            str(case.get("query") or ""),
        ),
    )


async def collect_tracked_price_batch(
    *,
    limit: int | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    batch_size = limit if limit is not None else _env_int(
        "SCOUTLY_PRICE_TRACKING_BATCH_SIZE",
        DEFAULT_BATCH_SIZE,
        1,
        20,
    )
    batch_size = max(1, min(20, int(batch_size)))

    if not price_tracking_enabled():
        return {
            "enabled": False,
            "live_ebay": False,
            "tracked_count": 0,
            "due_count": 0,
            "attempted_count": 0,
            "collected_count": 0,
            "skipped_identity_count": 0,
            "collected": [],
        }

    cases = tracked_price_cases()
    overview = price_overview(days=3650, limit=2000)
    due = due_tracked_price_cases(cases, overview, now=now)
    selected = due[:batch_size]

    collected: list[dict[str, Any]] = []
    skipped_identity_count = 0
    for case in selected:
        query = str(case.get("query") or "")
        category = str(case.get("category") or "")
        expected_product_id = str(case.get("expected_product_id") or "")

        # Refuse to collect if the curated query no longer resolves to the
        # expected exact product. This keeps a future catalog regression from
        # silently polluting historical market data.
        preflight = resolve_discoverable_product(query, category)
        if preflight is None or preflight.product.id != expected_product_id:
            skipped_identity_count += 1
            logger.warning(
                "Skipping scheduled price snapshot for %s: expected %s, resolved %s",
                query,
                expected_product_id,
                preflight.product.id if preflight is not None else None,
            )
            continue

        resolved, results, _auctions, diagnostics, price_context = (
            await search_service.search_best_deals_with_auctions(
                query,
                ["ebay"],
                category,
                include_auctions=False,
                snapshot_source=SNAPSHOT_SOURCE,
            )
        )
        resolved_product_id = resolved.product.id if resolved is not None else None
        if resolved_product_id != expected_product_id:
            skipped_identity_count += 1
            logger.warning(
                "Scheduled price search changed identity for %s: expected %s, got %s",
                query,
                expected_product_id,
                resolved_product_id,
            )
            continue

        collected.append(
            {
                "query": query,
                "category": category,
                "product_id": expected_product_id,
                "result_count": len(results),
                "eligible_count": diagnostics.fixed_price_eligible,
                "snapshot_count": price_context.snapshot_count,
                "last_observed_at": price_context.last_observed_at,
            }
        )

    return {
        "enabled": True,
        "live_ebay": True,
        "tracked_count": len(cases),
        "due_count": len(due),
        "attempted_count": len(selected),
        "collected_count": len(collected),
        "skipped_identity_count": skipped_identity_count,
        "collected": collected,
    }


async def run_tracked_price_collector() -> None:
    """Continuously collect small, due-only market batches for price history."""

    start_delay = _env_int(
        "SCOUTLY_PRICE_TRACKING_START_DELAY_SECONDS",
        DEFAULT_START_DELAY_SECONDS,
        0,
        3600,
    )
    interval_seconds = _env_int(
        "SCOUTLY_PRICE_TRACKING_INTERVAL_SECONDS",
        DEFAULT_INTERVAL_SECONDS,
        300,
        24 * 60 * 60,
    )

    if start_delay:
        await asyncio.sleep(start_delay)

    while True:
        try:
            result = await collect_tracked_price_batch()
            if result["collected_count"] or result["skipped_identity_count"]:
                logger.info(
                    "Scheduled price tracking: collected=%s due=%s tracked=%s skipped_identity=%s",
                    result["collected_count"],
                    result["due_count"],
                    result["tracked_count"],
                    result["skipped_identity_count"],
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            # Background collection must never take the buyer-facing API down.
            logger.exception("Scheduled price tracking batch failed.")

        await asyncio.sleep(interval_seconds)
