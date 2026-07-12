from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.providers.ebay import _ensure_affiliate_campaign_params, ebay_config_from_env

router = APIRouter(tags=["Outbound"])


def _is_allowed_ebay_url(url: str) -> bool:
    try:
        parts = urlsplit(url)
    except ValueError:
        return False

    if parts.scheme not in {"http", "https"}:
        return False

    hostname = (parts.hostname or "").lower()
    return hostname == "ebay.com" or hostname.endswith(".ebay.com")


@router.get("/out")
def outbound_link(url: str = Query(..., min_length=1)) -> RedirectResponse:
    """Redirect through Scoutly so affiliate params are applied at click time.

    This gives us a final backend-side safety net if an old frontend render or
    cached search result contains an eBay URL with customid/toolid but no campid.
    """

    if not _is_allowed_ebay_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only eBay outbound links are supported right now.",
        )

    config = ebay_config_from_env()
    tracked_url = _ensure_affiliate_campaign_params(
        url,
        affiliate_campaign_id=config.affiliate_campaign_id if config else None,
        affiliate_reference_id=config.affiliate_reference_id if config else None,
    )

    return RedirectResponse(tracked_url, status_code=status.HTTP_302_FOUND)
