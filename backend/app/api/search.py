from fastapi import APIRouter, Query

from app.models.search import SearchResponse
from app.services.search_service import search_best_deals

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2),
    providers: str = Query("ebay,amazon"),
) -> SearchResponse:
    provider_keys = [provider.strip() for provider in providers.split(",") if provider.strip()]
    resolved_product, results = await search_best_deals(q, provider_keys)
    return SearchResponse(query=q, resolved_product=resolved_product, results=results)
