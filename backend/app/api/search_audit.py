from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.providers.ebay import EbayProvider
from app.services.admin_auth import require_admin_token as _require_admin_token


router = APIRouter(tags=["Search Audit"])


def _listing_payload(listing) -> dict:
    return {
        "title": listing.title,
        "price": listing.price,
        "shipping": listing.shipping,
        "total_price": listing.total_price,
        "condition": listing.condition,
        "url": str(listing.url),
        "image_url": str(listing.image_url) if listing.image_url else None,
        "item_location": listing.item_location,
        "marketplace_item_id": listing.marketplace_item_id,
    }


@router.get("/search-audit/ebay")
async def get_raw_ebay_sample(
    q: str = Query(..., min_length=2, max_length=240),
    limit: int = Query(15, ge=1, le=30),
    token: str | None = Query(None),
) -> dict:
    """Return eBay's first Best Match candidates without PriceSift filtering.

    The entered query is sent to eBay unchanged. This endpoint deliberately
    skips catalog resolution, category IDs, include/exclude terms, local
    rejection rules, scoring, deduplication, and PriceSift ranking.
    """
    _require_admin_token(token)
    query = q.strip()

    try:
        listings = await EbayProvider().search(
            query,
            category=None,
            buying_option="fixed_price",
            item_location_country="US",
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Raw eBay audit search failed: {type(error).__name__}",
        ) from error

    selected = listings[:limit]
    return {
        "query": query,
        "returned": len(selected),
        "method": {
            "condition": "Used",
            "location": "US",
            "purchase_format": "Buy It Now",
            "sort_order": "Best Match",
            "pricesift_filters_applied": False,
        },
        "listings": [_listing_payload(listing) for listing in selected],
    }
