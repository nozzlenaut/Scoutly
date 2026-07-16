from fastapi import APIRouter, HTTPException, Query, status

from app.catalog.catalog import suggest_products
from app.models.search import SearchResponse
from app.services.search_service import search_auction_deals, search_best_deals_with_auctions
from app.services.analytics_store import SearchEvent, log_search_event

router = APIRouter()


def _reject_public_lens_marketplace_search(category: str | None) -> None:
    if (category or "").strip().lower() in {"lens", "lenses"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public lens results are KEH-only. Use the PriceSift Lens Finder.",
        )


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2),
    category: str | None = Query(None),
    providers: str = Query("ebay"),
    include_auctions: bool = Query(False),
    auction_hours: int = Query(24, ge=1, le=168),
    us_only: bool = Query(False),
    analytics: bool = Query(False),
) -> SearchResponse:
    _reject_public_lens_marketplace_search(category)
    provider_keys = [provider.strip() for provider in providers.split(",") if provider.strip()]
    resolved_product, results, auction_results, diagnostics, price_context = await search_best_deals_with_auctions(
        q,
        provider_keys,
        category,
        include_auctions=include_auctions,
        auction_hours=auction_hours,
        item_location_country="US" if us_only else None,
    )
    if analytics:
        provider_counts: dict[str, int] = {}
        for listing in results:
            provider_counts[listing.provider] = provider_counts.get(listing.provider, 0) + 1
        log_search_event(
            SearchEvent(
                category=category,
                query=q,
                product_id=resolved_product.product.id if resolved_product else None,
                product_label=resolved_product.product.display_name if resolved_product else None,
                resolved=resolved_product is not None,
                result_count=len(results),
                provider_counts=provider_counts,
                candidate_count=diagnostics.fixed_price_candidates,
                filtered_count=diagnostics.fixed_price_filtered,
                no_inventory=len(results) == 0,
                us_only=us_only,
            )
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
    us_only: bool = Query(False),
) -> SearchResponse:
    _reject_public_lens_marketplace_search(category)
    provider_keys = [provider.strip() for provider in providers.split(",") if provider.strip()]
    resolved_product, auction_results, diagnostics = await search_auction_deals(
        q,
        provider_keys,
        category,
        auction_hours=auction_hours,
        item_location_country="US" if us_only else None,
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
