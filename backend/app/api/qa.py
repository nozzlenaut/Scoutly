import os
import secrets

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.qa_registry import qa_cases_with_latest, qa_summary
from app.services.qa_store import list_qa_evaluations, save_qa_evaluation
from app.services.shipping_qa import run_shipping_probe

router = APIRouter(tags=["QA"])


class QaEvaluationRequest(BaseModel):
    case_id: str = Field(min_length=2, max_length=160)
    category: str = Field(min_length=2, max_length=80)
    query: str = Field(min_length=2, max_length=240)
    expected_product_id: str | None = Field(default=None, max_length=180)
    expected_label: str | None = Field(default=None, max_length=300)
    resolved_product_id: str | None = Field(default=None, max_length=180)
    resolved_label: str | None = Field(default=None, max_length=300)
    resolution_correct: bool = False
    outcome: str = Field(min_length=2, max_length=40)
    issue_tags: list[str] = Field(default_factory=list, max_length=12)
    notes: str | None = Field(default=None, max_length=1200)
    result_titles: list[str] = Field(default_factory=list, max_length=3)
    diagnostics: dict = Field(default_factory=dict)


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


@router.get("/qa/cases")
def get_qa_cases(token: str | None = Query(None)) -> dict:
    _require_admin_token(token)
    return {"cases": qa_cases_with_latest(), "summary": qa_summary()}


@router.get("/qa/evaluations")
def get_qa_evaluations(
    limit: int = Query(200, ge=1, le=1000),
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    return {"evaluations": list_qa_evaluations(limit)}


@router.get("/qa/shipping")
async def get_shipping_qa(
    q: str = Query(..., min_length=2, max_length=240),
    category: str | None = Query("cameras", min_length=2, max_length=80),
    postal_code: str = Query(..., min_length=3, max_length=12),
    country: str = Query("US", min_length=2, max_length=2),
    limit: int = Query(5, ge=1, le=10),
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    try:
        return await run_shipping_probe(q, category, postal_code, country, limit)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"eBay shipping probe failed: {type(error).__name__}",
        ) from error


@router.post("/qa/evaluations")
def create_qa_evaluation(
    payload: QaEvaluationRequest,
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    try:
        return save_qa_evaluation(payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
