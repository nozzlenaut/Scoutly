from app.catalog.catalog import match_product
from app.models.listing import Listing
from app.models.product import ProductMatch
from app.providers.mock import MockAmazonProvider, MockEbayProvider
from app.ranking.scorer import best_listing

PROVIDERS = {
    "ebay": MockEbayProvider(),
    "amazon": MockAmazonProvider(),
}


async def search_best_deals(query: str, provider_keys: list[str]) -> tuple[ProductMatch | None, list[Listing]]:
    product_match = match_product(query)
    provider_query = product_match.product.display_name if product_match else query
    results: list[Listing] = []

    for provider_key in provider_keys:
        provider = PROVIDERS.get(provider_key.lower())
        if provider is None:
            continue

        listings = await provider.search(provider_query)
        best = best_listing(listings, product_match.product if product_match else None)
        if best is not None:
            results.append(best)

    return product_match, sorted(results, key=lambda item: item.total_price)
