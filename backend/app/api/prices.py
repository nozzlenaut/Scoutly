from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.admin_auth import require_admin_token as _require_admin_token
from app.providers.ebay import ebay_config_from_env
from app.services import search_service
from app.services.price_store import build_price_context, price_overview
from app.services.qa_store import load_qa_cases

router = APIRouter(tags=["Prices"])


class PriceCollectionRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=10)
    category: str | None = Field(default=None, max_length=80)


@router.get("/prices/overview")
def get_price_overview(
    token: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=500, ge=1, le=2000),
) -> dict:
    _require_admin_token(token)
    return price_overview(days=days, limit=limit)


@router.get("/prices/{product_id}")
def get_product_price_context(
    product_id: str,
    days: int = Query(default=30, ge=1, le=365),
) -> dict:
    return build_price_context(product_id=product_id, days=days)


@router.post("/prices/collect/qa")
async def collect_qa_price_batch(
    payload: PriceCollectionRequest,
    token: str | None = Query(default=None),
) -> dict:
    _require_admin_token(token)
    live_ebay = ebay_config_from_env() is not None

    overview = price_overview(days=365, limit=2000)
    last_by_product = {
        str(item.get("product_id")): str(item.get("last_observed_at") or "")
        for item in overview.get("products", [])
    }

    cases = load_qa_cases()
    if payload.category:
        cases = [case for case in cases if case.get("category") == payload.category]

    # One representative query per product. Unseen and oldest-observed products
    # come first so repeated batches naturally rotate through the baseline.
    unique_cases: dict[str, dict] = {}
    for case in cases:
        product_id = str(case.get("expected_product_id") or "")
        if product_id and product_id not in unique_cases:
            unique_cases[product_id] = case
    ordered = sorted(
        unique_cases.values(),
        key=lambda case: (
            bool(last_by_product.get(str(case.get("expected_product_id") or ""))),
            last_by_product.get(str(case.get("expected_product_id") or ""), ""),
            str(case.get("category") or ""),
            str(case.get("query") or ""),
        ),
    )

    selected = ordered[: payload.limit]
    collected: list[dict] = []
    for case in selected:
        resolved, results, _auctions, diagnostics, price_context = await search_service.search_best_deals_with_auctions(
            str(case["query"]),
            ["ebay"],
            str(case["category"]),
            include_auctions=False,
            snapshot_source="qa_collector",
        )
        collected.append(
            {
                "case_id": case.get("id"),
                "query": case.get("query"),
                "category": case.get("category"),
                "expected_product_id": case.get("expected_product_id"),
                "resolved_product_id": resolved.product.id if resolved else None,
                "result_count": len(results),
                "eligible_count": diagnostics.fixed_price_eligible,
                "snapshot_count": price_context.snapshot_count,
                "last_observed_at": price_context.last_observed_at,
            }
        )

    return {
        "live_ebay": live_ebay,
        "collected_count": len(collected),
        "remaining_products": max(0, len(ordered) - len(selected)),
        "collected": collected,
    }
