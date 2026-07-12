from fastapi import APIRouter, Query

from app.models.search import SearchResponse
from app.services.search_service import search_best_deals_with_auctions

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2),
    category: str | None = Query(None),
    providers: str = Query("ebay"),
    include_auctions: bool = Query(False),
    auction_hours: int = Query(24, ge=1, le=168),
) -> SearchResponse:
    provider_keys = [provider.strip() for provider in providers.split(",") if provider.strip()]
    resolved_product, results, auction_results = await search_best_deals_with_auctions(
        q,
        provider_keys,
        category,
        include_auctions=include_auctions,
        auction_hours=auction_hours,
    )
    return SearchResponse(
        query=q,
        category=category,
        resolved_product=resolved_product,
        results=results,
        auction_results=auction_results,
    )
