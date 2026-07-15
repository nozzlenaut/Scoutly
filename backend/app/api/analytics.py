import os
import secrets

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.feedback_store import (
    active_bad_result_reports,
    analytics_summary,
    delete_bad_result_report,
    recent_filtered_listings,
    recent_outbound_clicks,
)
from app.services.filter_rules import ManualFilterRule, add_manual_filter_rule, delete_manual_filter_rule, list_manual_filter_rules
from app.services.beta_feedback_store import list_beta_feedback
from app.services.analytics_store import analytics_digest

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


def _require_admin_token(token: str | None) -> None:
    configured_token = os.getenv("SCOUTLY_ADMIN_TOKEN", "").strip()
    if not configured_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access is not configured.",
        )
    if not token or not secrets.compare_digest(token, configured_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid admin token.",
        )


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
    return analytics_digest(days)


@router.get("/analytics/clicks")
def get_recent_clicks(limit: int = Query(50, ge=1, le=200), token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {"clicks": recent_outbound_clicks(limit)}


@router.get("/analytics/reports")
def get_active_reports(limit: int = Query(50, ge=1, le=200), token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {"reports": active_bad_result_reports(limit)}


@router.get("/analytics/filtered")
def get_recent_filtered(limit: int = Query(50, ge=1, le=200), token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {"filtered": recent_filtered_listings(limit)}


@router.get("/analytics/beta-feedback")
def get_beta_feedback(limit: int = Query(100, ge=1, le=500), token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {"feedback": list_beta_feedback(limit)}


@router.get("/analytics/filter-rules")
def get_manual_filter_rules(token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {"rules": list(reversed(list_manual_filter_rules(include_disabled=True)))}


@router.post("/analytics/filter-rules", response_model=ManualFilterRuleResponse)
def create_manual_filter_rule(payload: ManualFilterRuleRequest, token: str | None = Query(None)) -> dict:
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.delete("/analytics/filter-rules/{rule_id}")
def remove_manual_filter_rule(rule_id: str, token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    deleted = delete_manual_filter_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filter rule not found.")
    return {"status": "deleted", "id": rule_id}


@router.delete("/analytics/reports/{link_key:path}")
def remove_bad_result_report(
    link_key: str,
    token: str | None = Query(None),
    product_id: str | None = Query(None),
    category: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    deleted = delete_bad_result_report(link_key=link_key, product_id=product_id, category=category)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return {"status": "deleted", "link_key": link_key}
