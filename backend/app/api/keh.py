from __future__ import annotations

import os
import secrets

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.services.analytics_store import SearchEvent, log_search_event
from app.services.keh_feed import (
    keh_lens_builder,
    keh_overview,
    keh_public_results_enabled,
    list_keh_inventory,
    sync_keh_feed,
)

router = APIRouter(tags=["KEH"])


def _require_admin_token(token: str | None) -> None:
    configured_token = os.getenv("SCOUTLY_ADMIN_TOKEN", "").strip()
    if not configured_token:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Admin access is not configured.")
    if not token or not secrets.compare_digest(token, configured_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid admin token.")


class KehSyncRequest(BaseModel):
    force: bool = False


@router.get("/keh/overview")
def get_keh_overview(
    token: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
) -> dict:
    _require_admin_token(token)
    return keh_overview(limit=limit)


@router.get("/keh/inventory")
def get_keh_inventory(
    token: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
    match_status: str | None = Query(default=None, pattern="^(matched|unmatched|ambiguous)$"),
    product_id: str | None = Query(default=None, max_length=180),
) -> dict:
    _require_admin_token(token)
    return {"items": list_keh_inventory(limit=limit, status=match_status, product_id=product_id)}




@router.get("/keh/lenses/public")
def get_public_keh_lens_builder(
    mount: str | None = Query(default=None, max_length=80),
    lens_type: str | None = Query(default=None, pattern="^(Prime|Zoom|Other)$"),
    focal_group: str | None = Query(default=None, max_length=80),
    brand: str | None = Query(default=None, max_length=100),
    q: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=100, ge=1, le=250),
    analytics: bool = Query(default=False),
) -> dict:
    if not keh_public_results_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Public KEH results are not enabled.",
        )

    payload = keh_lens_builder(
        mount=mount,
        lens_type=lens_type,
        focal_group=focal_group,
        brand=brand,
        query=q,
        limit=limit,
    )
    if analytics and mount and lens_type and focal_group:
        summary = payload.get("summary") or {}
        label = " · ".join(value for value in [mount, lens_type, focal_group, brand] if value)
        total_listings = int(summary.get("listing_count") or 0)
        filtered_listings = int(summary.get("filtered_listing_count") or 0)
        filtered_models = int(summary.get("filtered_model_count") or 0)
        log_search_event(
            SearchEvent(
                category="lenses",
                query=label,
                product_id=None,
                product_label=label,
                resolved=True,
                result_count=filtered_models,
                provider_counts={"KEH": filtered_listings},
                candidate_count=total_listings,
                filtered_count=max(0, total_listings - filtered_listings),
                no_inventory=filtered_models == 0,
                us_only=False,
            )
        )
    return payload


@router.get("/keh/lenses/builder")
def get_keh_lens_builder(
    token: str | None = Query(default=None),
    mount: str | None = Query(default=None, max_length=80),
    lens_type: str | None = Query(default=None, pattern="^(Prime|Zoom|Other)$"),
    focal_group: str | None = Query(default=None, max_length=80),
    brand: str | None = Query(default=None, max_length=100),
    q: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    _require_admin_token(token)
    return keh_lens_builder(
        mount=mount,
        lens_type=lens_type,
        focal_group=focal_group,
        brand=brand,
        query=q,
        limit=limit,
    )

@router.post("/keh/sync")
def run_keh_sync(
    _payload: KehSyncRequest,
    token: str | None = Query(default=None),
) -> dict:
    _require_admin_token(token)
    result = sync_keh_feed()
    if result.get("status") != "success":
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=result.get("error_message") or "KEH sync failed.")
    return result
