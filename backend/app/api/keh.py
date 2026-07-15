from __future__ import annotations

import os
import secrets

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.services.keh_feed import keh_overview, list_keh_inventory, sync_keh_feed

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
