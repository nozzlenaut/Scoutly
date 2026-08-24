from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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


def _set_query_parameter(url: str, name: str, value: str) -> str:
    parts = urlsplit(url)
    query = [
        (key, existing_value)
        for key, existing_value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() != name.lower()
    ]
    query.append((name, value))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _tracked_outbound_url(url: str, *, click_ref: str | None = None) -> str:
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
        return _set_query_parameter(tracked_url, "customid", click_ref) if click_ref else tracked_url

    if outbound_kind == "awin" and click_ref:
        return _set_query_parameter(url, "clickref", click_ref)

    # Awin feed links and Amazon links are already publisher-tagged before
    # they reach this route. Preserve them byte-for-byte when there is no
    # browser-generated per-click reference to add.
    return url


@router.get("/out")
def outbound_link(
    url: str = Query(..., min_length=1),
    click_ref: str | None = Query(None, max_length=50, pattern=r"^[A-Za-z0-9_-]+$"),
) -> RedirectResponse:
    """Redirect without treating crawler or link-checker requests as human clicks."""

    return RedirectResponse(
        _tracked_outbound_url(url, click_ref=click_ref),
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/out/click", status_code=status.HTTP_204_NO_CONTENT)
def record_outbound_click(
    url: str = Query(..., min_length=1),
    provider: str | None = Query(None),
    category: str | None = Query(None),
    product_id: str | None = Query(None),
    q: str | None = Query(None),
    title: str | None = Query(None),
    price: float | None = Query(None, ge=0),
    currency: str | None = Query(None, min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$"),
    source_page: str | None = Query(None, max_length=500),
    click_ref: str | None = Query(None, max_length=50, pattern=r"^[A-Za-z0-9_-]+$"),
) -> Response:
    """Record a browser-confirmed click separately from the redirect request."""

    tracked_url = _tracked_outbound_url(url, click_ref=click_ref)
    log_outbound_click(
        url=url,
        tracked_url=tracked_url,
        provider=provider,
        category=category,
        product_id=product_id,
        query=q,
        title=title,
        listing_price=price,
        currency=currency.upper() if currency else None,
        source_page=source_page,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
