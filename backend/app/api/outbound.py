from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.providers.ebay import _ensure_affiliate_campaign_params, ebay_config_from_env
from app.services.feedback_store import log_outbound_click

router = APIRouter(tags=["Outbound"])


def _allowed_outbound_kind(url: str) -> str | None:
    try:
        parts = urlsplit(url)
    except ValueError:
        return None

    if parts.scheme not in {"http", "https"}:
        return None

    hostname = (parts.hostname or "").lower()
    if hostname == "ebay.com" or hostname.endswith(".ebay.com"):
        return "ebay"
    if hostname == "awin1.com" or hostname.endswith(".awin1.com"):
        return "awin"
    return None


@router.get("/out")
def outbound_link(
    url: str = Query(..., min_length=1),
    provider: str | None = Query(None),
    category: str | None = Query(None),
    product_id: str | None = Query(None),
    q: str | None = Query(None),
    title: str | None = Query(None),
) -> RedirectResponse:
    """Redirect through Scoutly so affiliate params and click tracking happen server-side."""

    outbound_kind = _allowed_outbound_kind(url)
    if outbound_kind is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That outbound marketplace link is not supported.",
        )

    if outbound_kind == "ebay":
        config = ebay_config_from_env()
        tracked_url = _ensure_affiliate_campaign_params(
            url,
            affiliate_campaign_id=config.affiliate_campaign_id if config else None,
            affiliate_reference_id=config.affiliate_reference_id if config else None,
        )
    else:
        # The Awin feed already supplies a publisher-tracked deep link. Keep it
        # byte-for-byte intact rather than trying to append eBay parameters.
        tracked_url = url

    log_outbound_click(
        url=url,
        tracked_url=tracked_url,
        provider=provider,
        category=category,
        product_id=product_id,
        query=q,
        title=title,
    )

    return RedirectResponse(tracked_url, status_code=status.HTTP_302_FOUND)
