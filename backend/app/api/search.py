from fastapi import APIRouter, Query

from app.catalog.catalog import suggest_products
from app.models.search import SearchResponse
from app.services.search_service import search_auction_deals, search_best_deals_with_auctions

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
    resolved_product, results, auction_results, diagnostics, price_context = await search_best_deals_with_auctions(
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
        suggested_products=suggest_products(q, category, limit=5),
        results=results,
        auction_results=auction_results,
        diagnostics=diagnostics,
        price_context=price_context,
    )


@router.get("/search/auctions", response_model=SearchResponse)
async def search_auctions(
    q: str = Query(..., min_length=2),
    category: str | None = Query(None),
    providers: str = Query("ebay"),
    auction_hours: int = Query(24, ge=1, le=168),
) -> SearchResponse:
    provider_keys = [provider.strip() for provider in providers.split(",") if provider.strip()]
    resolved_product, auction_results, diagnostics = await search_auction_deals(
        q,
        provider_keys,
        category,
        auction_hours=auction_hours,
    )
    return SearchResponse(
        query=q,
        category=category,
        resolved_product=resolved_product,
        suggested_products=suggest_products(q, category, limit=5),
        results=[],
        auction_results=auction_results,
        diagnostics=diagnostics,
    )
