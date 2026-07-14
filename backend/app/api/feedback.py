from pydantic import BaseModel, Field, HttpUrl
from fastapi import APIRouter

from app.services.feedback_store import BadResultReport, report_bad_result
from app.services.beta_feedback_store import save_beta_feedback

router = APIRouter(tags=["Feedback"])


class BadResultReportRequest(BaseModel):
    url: HttpUrl
    title: str | None = Field(default=None, max_length=300)
    provider: str | None = Field(default=None, max_length=80)
    category: str | None = Field(default=None, max_length=80)
    product_id: str | None = Field(default=None, max_length=160)
    query: str | None = Field(default=None, max_length=200)
    reason: str = Field(default="wrong_item", max_length=80)


class BadResultReportResponse(BaseModel):
    status: str
    hidden_until: str
    link_key: str


@router.post("/results/report", response_model=BadResultReportResponse)
def report_result(payload: BadResultReportRequest) -> dict[str, str]:
    """Temporarily hide a bad marketplace result for the matched product/category."""

    return report_bad_result(
        BadResultReport(
            url=str(payload.url),
            title=payload.title,
            provider=payload.provider,
            category=payload.category,
            product_id=payload.product_id,
            query=payload.query,
            reason=payload.reason,
        )
    )


class BetaFeedbackRequest(BaseModel):
    feedback_type: str = Field(default="general", max_length=40)
    category: str | None = Field(default=None, max_length=80)
    message: str = Field(min_length=5, max_length=2000)
    email: str | None = Field(default=None, max_length=254)
    page_url: str | None = Field(default=None, max_length=500)
    website: str | None = Field(default=None, max_length=200)  # honeypot


class BetaFeedbackResponse(BaseModel):
    status: str
    id: str | None = None


@router.post("/feedback", response_model=BetaFeedbackResponse)
def submit_beta_feedback(payload: BetaFeedbackRequest) -> dict[str, str | None]:
    # Quietly accept bot-filled honeypots without persisting them.
    if payload.website:
        return {"status": "saved", "id": None}
    saved = save_beta_feedback(
        feedback_type=payload.feedback_type,
        category=payload.category,
        message=payload.message,
        email=payload.email,
        page_url=payload.page_url,
    )
    return {"status": "saved", "id": str(saved["id"])}
