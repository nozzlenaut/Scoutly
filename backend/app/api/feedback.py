from pydantic import BaseModel, Field, HttpUrl
from fastapi import APIRouter

from app.services.feedback_store import BadResultReport, report_bad_result

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
