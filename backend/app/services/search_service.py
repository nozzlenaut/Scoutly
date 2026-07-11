from app.catalog.catalog import match_product
from app.models.listing import Listing
from app.models.product import ProductMatch
from app.providers.ebay import EbayProvider, ebay_config_from_env
from app.providers.mock import MockAmazonProvider, MockEbayProvider
from app.ranking.scorer import best_listing


def _build_providers():
    providers = {
        "amazon": MockAmazonProvider(),
    }

    if ebay_config_from_env() is not None:
        providers["ebay"] = EbayProvider()
    else:
        providers["ebay"] = MockEbayProvider()

    return providers


PROVIDERS = _build_providers()


async def search_best_deals(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
) -> tuple[ProductMatch | None, list[Listing]]:
    product_match = match_product(query, category)
    provider_query = product_match.product.display_name if product_match else query
    results: list[Listing] = []

    for provider_key in provider_keys:
        provider = PROVIDERS.get(provider_key.lower())
        if provider is None:
            continue

        try:
            listings = await provider.search(provider_query, product_match.product.category if product_match else category)
        except Exception:
            # One provider should not take the entire search down. We will add
            # structured provider errors in a later sprint once the live API is
            # stable.
            continue

        best = best_listing(listings, product_match.product if product_match else None)
        if best is not None:
            results.append(best)

    return product_match, sorted(results, key=lambda item: item.total_price)
