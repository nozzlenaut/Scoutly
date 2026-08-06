from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field

from app.providers.ebay import EbayProvider
from app.services.admin_auth import require_admin_token as _require_admin_token
from app.services.buffer_drafts import (
    BufferDraftError,
    DuplicateBufferDraft,
    create_buffer_draft,
    get_share_image,
)


router = APIRouter(tags=["Search Audit"])


class BufferDraftPayload(BaseModel):
    audit_id: str = Field(min_length=1, max_length=200)
    post_text: str = Field(min_length=1, max_length=300)
    alt_text: str = Field(min_length=1, max_length=2000)
    image_data_url: str = Field(min_length=32, max_length=6_000_000)


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

@router.post("/search-audit/buffer-draft")
async def create_audit_buffer_draft(
    payload: BufferDraftPayload,
    request: Request,
    token: str | None = Query(None),
) -> dict:
    _require_admin_token(token)
    public_base_url = os.getenv("PUBLIC_API_BASE_URL", "").strip() or str(request.base_url).rstrip("/")
    try:
        return await create_buffer_draft(
            audit_id=payload.audit_id,
            post_text=payload.post_text,
            alt_text=payload.alt_text,
            image_data_url=payload.image_data_url,
            public_base_url=public_base_url,
        )
    except DuplicateBufferDraft as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(error),
                "status": error.status,
                "buffer_post_id": error.buffer_post_id,
            },
        ) from error
    except BufferDraftError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Buffer draft failed: {type(error).__name__}",
        ) from error


@router.get("/search-audit/share-image/{image_token}.png")
def get_audit_share_image(image_token: str) -> Response:
    try:
        image = get_share_image(image_token)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Audit image storage unavailable: {type(error).__name__}",
        ) from error
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit image not found.")
    return Response(
        content=image,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
