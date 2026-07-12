import os

from fastapi import APIRouter, HTTPException, Query, status

from app.services.feedback_store import (
    active_bad_result_reports,
    analytics_summary,
    recent_outbound_clicks,
)

router = APIRouter(tags=["Analytics"])


def _require_admin_token(token: str | None) -> None:
    configured_token = os.getenv("SCOUTLY_ADMIN_TOKEN", "").strip()
    if configured_token and token != configured_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid admin token.",
        )


@router.get("/analytics/summary")
def get_analytics_summary(token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return analytics_summary()


@router.get("/analytics/clicks")
def get_recent_clicks(limit: int = Query(50, ge=1, le=200), token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {"clicks": recent_outbound_clicks(limit)}


@router.get("/analytics/reports")
def get_active_reports(limit: int = Query(50, ge=1, le=200), token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {"reports": active_bad_result_reports(limit)}
