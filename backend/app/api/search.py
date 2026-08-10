from fastapi import APIRouter, HTTPException, Query, status

from app.models.listing import Listing
from app.models.product import ProductMatch
from app.models.search import SearchDiagnostics, SearchResponse
from app.services.ai_console_review import review_console_listings
from app.services.analytics_store import SearchEvent, log_search_event
from app.services.product_discovery import suggest_discoverable_products
from app.services.search_service import search_auction_deals, search_best_deals_with_auctions

router = APIRouter()


def _reject_public_lens_marketplace_search(category: str | None) -> None:
    if (category or "").strip().lower() in {"lens", "lenses"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public lens results are KEH-only. Use the PriceSift Lens Finder.",
        )


async def _apply_ai_console_beta_review(
    resolved_product: ProductMatch | None,
    results: list[Listing],
    auction_results: list[Listing],
    diagnostics: SearchDiagnostics,
) -> tuple[list[Listing], list[Listing]]:
    if resolved_product is None:
        return results, auction_results

    combined = [*results, *auction_results]
    review = await review_console_listings(combined, resolved_product.product)
    if not review.applied:
        if review.skipped_reason not in {None, "not_target"}:
            diagnostics.ai_review_skipped_reason = review.skipped_reason
        return results, auction_results

    diagnostics.ai_review_applied = True
    diagnostics.ai_review_skipped_reason = None
    kept_object_ids = {id(listing) for listing in review.kept}
    reviewed_results = [listing for listing in results if id(listing) in kept_object_ids]
    reviewed_auctions = [listing for listing in auction_results if id(listing) in kept_object_ids]

    fixed_rejected = len(results) - len(reviewed_results)
    auction_rejected = len(auction_results) - len(reviewed_auctions)
    diagnostics.ai_review_rejected += fixed_rejected + auction_rejected
    if fixed_rejected:
        diagnostics.fixed_price_filtered += fixed_rejected
        diagnostics.fixed_price_eligible = max(
            0, diagnostics.fixed_price_eligible - fixed_rejected
        )
        diagnostics.fixed_price_rejection_reasons["ai console review"] = (
            diagnostics.fixed_price_rejection_reasons.get("ai console review", 0)
            + fixed_rejected
        )
    if auction_rejected:
        diagnostics.auction_filtered += auction_rejected
        diagnostics.auction_eligible = max(
            0, diagnostics.auction_eligible - auction_rejected
        )
        diagnostics.auction_rejection_reasons["ai console review"] = (
            diagnostics.auction_rejection_reasons.get("ai console review", 0)
            + auction_rejected
        )

    return reviewed_results, reviewed_auctions


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
    results, auction_results = await _apply_ai_console_beta_review(
        resolved_product,
        results,
        auction_results,
        diagnostics,
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
        suggested_products=suggest_discoverable_products(q, category, limit=5),
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
    _ignored_results, auction_results = await _apply_ai_console_beta_review(
        resolved_product,
        [],
        auction_results,
        diagnostics,
    )
    return SearchResponse(
        query=q,
        category=category,
        resolved_product=resolved_product,
        suggested_products=suggest_discoverable_products(q, category, limit=5),
        results=[],
        auction_results=auction_results,
        diagnostics=diagnostics,
    )
