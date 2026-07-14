from datetime import UTC, datetime, timedelta

from app.catalog.catalog import match_product, normalize_category
from app.catalog.ram import ram_provider_query
from app.catalog.consoles import console_provider_query, console_search_products
from app.models.listing import Listing
from app.models.product import Product, ProductMatch
from app.models.search import SearchDiagnostics
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


def _provider_query_for_product(query: str, product: Product | None) -> str:
    if product is None:
        return query
    if product.category == "ram":
        return ram_provider_query(product)
    if product.metadata.get("builder") == "consoles":
        return console_provider_query(product)
    return product.display_name


def _search_product_scopes(product: Product | None) -> list[Product | None]:
    if product is not None and product.metadata.get("builder") == "consoles":
        return list(console_search_products(product))
    return [product]


def _listing_identity(listing: Listing) -> str:
    return str(listing.url).split("?", 1)[0]


def _top_scored_listings(listings: list[Listing], limit: int = 3) -> list[Listing]:
    deduped: dict[str, Listing] = {}
    for listing in sorted(listings, key=lambda item: item.score, reverse=True):
        deduped.setdefault(_listing_identity(listing), listing)
    return list(deduped.values())[: max(1, limit)]


def _auction_sort_key(listing: Listing) -> tuple[int, datetime, float]:
    ends_at = _parse_ebay_dt(listing.item_end_date) or datetime.max.replace(tzinfo=UTC)
    bundle_rank = 1 if "Bundle / extras included" in listing.warning_labels else 0
    return (bundle_rank, ends_at, listing.total_price)


def _top_combined_auctions(listings: list[Listing], limit: int = 3) -> list[Listing]:
    deduped: dict[str, Listing] = {}
    for listing in sorted(listings, key=_auction_sort_key):
        deduped.setdefault(_listing_identity(listing), listing)
    return list(deduped.values())[: max(1, limit)]


def _structured_product_required_but_missing(category: str | None, product_match: ProductMatch | None) -> bool:
    return normalize_category(category) == "ram" and product_match is None


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

    return sorted(valid, key=_auction_sort_key)[: max(1, limit)]


async def _search_provider(
    *,
    provider_key: str,
    provider_query: str,
    category: str | None,
    product: Product | None,
    buying_option: str,
) -> tuple[list[Listing], int]:
    provider = PROVIDERS.get(provider_key.lower())
    if provider is None:
        return [], 0

    try:
        listings = await provider.search(provider_query, category, buying_option=buying_option)
    except Exception:
        # One provider should not take the entire search down. We will add
        # structured provider errors in a later sprint once the live API is
        # stable.
        return [], 0

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
    return filtered_by_report, len(listings)


async def search_best_deals(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
) -> tuple[ProductMatch | None, list[Listing]]:
    product_match = match_product(query, category)
    if _structured_product_required_but_missing(category, product_match):
        return None, []
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    search_products = _search_product_scopes(product)
    results: list[Listing] = []

    for provider_key in provider_keys:
        provider_candidates: list[Listing] = []
        for scoped_product in search_products:
            provider_query = _provider_query_for_product(query, scoped_product)
            listings, _candidate_count = await _search_provider(
                provider_key=provider_key,
                provider_query=provider_query,
                category=search_category,
                product=scoped_product,
                buying_option="fixed_price",
            )
            provider_candidates.extend(top_listings(listings, scoped_product, limit=3))
        best_candidates = _top_scored_listings(provider_candidates, limit=1)
        if best_candidates:
            results.append(best_candidates[0])

    return product_match, sorted(results, key=lambda item: item.total_price)


async def search_best_deals_with_auctions(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
    include_auctions: bool = True,
    auction_hours: int = 24,
) -> tuple[ProductMatch | None, list[Listing], list[Listing], SearchDiagnostics]:
    product_match = match_product(query, category)
    if _structured_product_required_but_missing(category, product_match):
        return None, [], [], SearchDiagnostics()
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    search_products = _search_product_scopes(product)
    fixed_results: list[Listing] = []
    auction_results: list[Listing] = []
    diagnostics = SearchDiagnostics()

    for provider_key in provider_keys:
        provider_fixed_candidates: list[Listing] = []
        provider_auction_candidates: list[Listing] = []

        for scoped_product in search_products:
            provider_query = _provider_query_for_product(query, scoped_product)
            fixed_listings, fixed_candidate_count = await _search_provider(
                provider_key=provider_key,
                provider_query=provider_query,
                category=search_category,
                product=scoped_product,
                buying_option="fixed_price",
            )
            diagnostics.fixed_price_candidates += fixed_candidate_count
            diagnostics.fixed_price_filtered += max(0, fixed_candidate_count - len(fixed_listings))
            diagnostics.fixed_price_filtered += sum(
                1 for listing in fixed_listings if is_bad_listing(listing, scoped_product)
            )
            provider_fixed_candidates.extend(top_listings(fixed_listings, scoped_product, limit=3))

            if include_auctions and provider_key.lower() == "ebay":
                auction_listings, auction_candidate_count = await _search_provider(
                    provider_key=provider_key,
                    provider_query=provider_query,
                    category=search_category,
                    product=scoped_product,
                    buying_option="auction",
                )
                diagnostics.auction_candidates += auction_candidate_count
                diagnostics.auction_filtered += max(0, auction_candidate_count - len(auction_listings))
                diagnostics.auction_filtered += sum(
                    1 for listing in auction_listings if is_bad_listing(listing, scoped_product)
                )
                provider_auction_candidates.extend(
                    best_auction_listings(
                        auction_listings,
                        scoped_product,
                        max_hours=auction_hours,
                        limit=3,
                    )
                )

        fixed_results.extend(_top_scored_listings(provider_fixed_candidates, limit=3))
        auction_results.extend(_top_combined_auctions(provider_auction_candidates, limit=3))

    return (
        product_match,
        sorted(_top_scored_listings(fixed_results, limit=3), key=lambda item: item.total_price),
        sorted(_top_combined_auctions(auction_results, limit=3), key=lambda item: item.item_end_date or ""),
        diagnostics,
    )


async def search_auction_deals(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
    auction_hours: int = 24,
) -> tuple[ProductMatch | None, list[Listing], SearchDiagnostics]:
    product_match = match_product(query, category)
    if _structured_product_required_but_missing(category, product_match):
        return None, [], SearchDiagnostics()
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    search_products = _search_product_scopes(product)
    auction_results: list[Listing] = []
    diagnostics = SearchDiagnostics()

    for provider_key in provider_keys:
        if provider_key.lower() != "ebay":
            continue
        provider_auction_candidates: list[Listing] = []
        for scoped_product in search_products:
            provider_query = _provider_query_for_product(query, scoped_product)
            auction_listings, auction_candidate_count = await _search_provider(
                provider_key=provider_key,
                provider_query=provider_query,
                category=search_category,
                product=scoped_product,
                buying_option="auction",
            )
            diagnostics.auction_candidates += auction_candidate_count
            diagnostics.auction_filtered += max(0, auction_candidate_count - len(auction_listings))
            diagnostics.auction_filtered += sum(
                1 for listing in auction_listings if is_bad_listing(listing, scoped_product)
            )
            provider_auction_candidates.extend(
                best_auction_listings(
                    auction_listings,
                    scoped_product,
                    max_hours=auction_hours,
                    limit=3,
                )
            )
        auction_results.extend(_top_combined_auctions(provider_auction_candidates, limit=3))

    return (
        product_match,
        sorted(_top_combined_auctions(auction_results, limit=3), key=lambda item: item.item_end_date or ""),
        diagnostics,
    )
