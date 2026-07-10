from app.models.listing import Listing
from app.providers.mock import MockAmazonProvider, MockEbayProvider
from app.ranking.scorer import best_listing

PROVIDERS = {
    "ebay": MockEbayProvider(),
    "amazon": MockAmazonProvider(),
}


async def search_best_deals(query: str, provider_keys: list[str]) -> list[Listing]:
    results: list[Listing] = []

    for provider_key in provider_keys:
        provider = PROVIDERS.get(provider_key.lower())
        if provider is None:
            continue

        listings = await provider.search(query)
        best = best_listing(listings)
        if best is not None:
            results.append(best)

    return sorted(results, key=lambda item: item.total_price)
