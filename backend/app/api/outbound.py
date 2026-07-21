from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Query, Response, status
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
    if hostname == "amazon.com" or hostname.endswith(".amazon.com"):
        return "amazon"
    return None


def _tracked_outbound_url(url: str) -> str:
    outbound_kind = _allowed_outbound_kind(url)
    if outbound_kind is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That outbound marketplace link is not supported.",
        )

    if outbound_kind == "ebay":
        config = ebay_config_from_env()
        return _ensure_affiliate_campaign_params(
            url,
            affiliate_campaign_id=config.affiliate_campaign_id if config else None,
            affiliate_reference_id=config.affiliate_reference_id if config else None,
        )

    # Awin feed links and Amazon links are already publisher-tagged before
    # they reach this route. Preserve them byte-for-byte.
    return url


@router.get("/out")
def outbound_link(url: str = Query(..., min_length=1)) -> RedirectResponse:
    """Redirect without treating crawler or link-checker requests as human clicks."""

    return RedirectResponse(_tracked_outbound_url(url), status_code=status.HTTP_302_FOUND)


@router.post("/out/click", status_code=status.HTTP_204_NO_CONTENT)
def record_outbound_click(
    url: str = Query(..., min_length=1),
    provider: str | None = Query(None),
    category: str | None = Query(None),
    product_id: str | None = Query(None),
    q: str | None = Query(None),
    title: str | None = Query(None),
) -> Response:
    """Record a browser-confirmed click separately from the redirect request."""

    tracked_url = _tracked_outbound_url(url)
    log_outbound_click(
        url=url,
        tracked_url=tracked_url,
        provider=provider,
        category=category,
        product_id=product_id,
        query=q,
        title=title,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
