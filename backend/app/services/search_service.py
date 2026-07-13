from datetime import UTC, datetime, timedelta

from app.catalog.catalog import match_product
from app.models.listing import Listing
from app.models.product import Product, ProductMatch
from app.providers.ebay import EbayProvider, ebay_config_from_env
from app.providers.mock import MockAmazonProvider, MockEbayProvider
from app.ranking.scorer import best_listing, is_bad_listing, rejection_reasons, score_listing, top_listings
from app.services.feedback_store import filter_reported_listings, log_filtered_listings


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


def _parse_ebay_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _filter_auction_window(listings: list[Listing], max_hours: int) -> list[Listing]:
    if max_hours <= 0:
        return listings

    now = datetime.now(UTC)
    cutoff = now + timedelta(hours=max_hours)
    filtered: list[Listing] = []
    for listing in listings:
        ends_at = _parse_ebay_dt(listing.item_end_date)
        if ends_at is None:
            # Keep auctions with missing end dates rather than hiding potentially useful tests.
            filtered.append(listing)
            continue
        if now <= ends_at <= cutoff:
            filtered.append(listing)
    return filtered


def best_auction_listings(
    listings: list[Listing],
    product: Product | None = None,
    max_hours: int = 24,
    limit: int = 3,
) -> list[Listing]:
    valid = [listing for listing in listings if not is_bad_listing(listing, product)]
    valid = _filter_auction_window(valid, max_hours)
    if not valid:
        return []

    for listing in valid:
        listing.score = score_listing(listing, product)

    def auction_sort_key(listing: Listing) -> tuple[datetime, float]:
        ends_at = _parse_ebay_dt(listing.item_end_date) or datetime.max.replace(tzinfo=UTC)
        return (ends_at, listing.total_price)

    return sorted(valid, key=auction_sort_key)[: max(1, limit)]


async def _search_provider(
    *,
    provider_key: str,
    provider_query: str,
    category: str | None,
    product: Product | None,
    buying_option: str,
) -> list[Listing]:
    provider = PROVIDERS.get(provider_key.lower())
    if provider is None:
        return []

    try:
        listings = await provider.search(provider_query, category, buying_option=buying_option)
    except Exception:
        # One provider should not take the entire search down. We will add
        # structured provider errors in a later sprint once the live API is
        # stable.
        return []

    filtered_by_report = filter_reported_listings(
        listings,
        product_id=product.id if product else None,
        category=product.category if product else category,
    )

    filtered_records: list[dict] = []
    for listing in filtered_by_report:
        reasons = rejection_reasons(listing, product)
        if reasons:
            filtered_records.append(
                {
                    "url": str(listing.url),
                    "title": listing.title,
                    "provider": listing.provider,
                    "category": product.category if product else category,
                    "product_id": product.id if product else None,
                    "query": provider_query,
                    "listing_type": listing.listing_type,
                    "reasons": reasons,
                }
            )

    log_filtered_listings(filtered_records)
    return filtered_by_report


async def search_best_deals(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
) -> tuple[ProductMatch | None, list[Listing]]:
    product_match = match_product(query, category)
    provider_query = product_match.product.display_name if product_match else query
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    results: list[Listing] = []

    for provider_key in provider_keys:
        listings = await _search_provider(
            provider_key=provider_key,
            provider_query=provider_query,
            category=search_category,
            product=product,
            buying_option="fixed_price",
        )
        best = best_listing(listings, product)
        if best is not None:
            results.append(best)

    return product_match, sorted(results, key=lambda item: item.total_price)


async def search_best_deals_with_auctions(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
    include_auctions: bool = True,
    auction_hours: int = 24,
) -> tuple[ProductMatch | None, list[Listing], list[Listing]]:
    product_match = match_product(query, category)
    provider_query = product_match.product.display_name if product_match else query
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    fixed_results: list[Listing] = []
    auction_results: list[Listing] = []

    for provider_key in provider_keys:
        fixed_listings = await _search_provider(
            provider_key=provider_key,
            provider_query=provider_query,
            category=search_category,
            product=product,
            buying_option="fixed_price",
        )
        fixed_results.extend(top_listings(fixed_listings, product, limit=3))

        if include_auctions and provider_key.lower() == "ebay":
            auction_listings = await _search_provider(
                provider_key=provider_key,
                provider_query=provider_query,
                category=search_category,
                product=product,
                buying_option="auction",
            )
            auction_best = best_auction_listings(auction_listings, product, max_hours=auction_hours, limit=3)
            auction_results.extend(auction_best)

    return (
        product_match,
        sorted(fixed_results, key=lambda item: item.total_price),
        sorted(auction_results, key=lambda item: item.item_end_date or ""),
    )


async def search_auction_deals(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
    auction_hours: int = 24,
) -> tuple[ProductMatch | None, list[Listing]]:
    product_match = match_product(query, category)
    provider_query = product_match.product.display_name if product_match else query
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    auction_results: list[Listing] = []

    for provider_key in provider_keys:
        if provider_key.lower() != "ebay":
            continue
        auction_listings = await _search_provider(
            provider_key=provider_key,
            provider_query=provider_query,
            category=search_category,
            product=product,
            buying_option="auction",
        )
        auction_results.extend(best_auction_listings(auction_listings, product, max_hours=auction_hours, limit=3))

    return (
        product_match,
        sorted(auction_results, key=lambda item: item.item_end_date or ""),
    )
