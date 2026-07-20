from datetime import UTC, datetime, timedelta
from collections import Counter

from app.catalog.catalog import match_product, normalize_category
from app.catalog.normalizer import normalize_text
from app.catalog.ram import ram_provider_query
from app.catalog.cpus import cpu_provider_query
from app.catalog.consoles import console_provider_queries, console_search_products
from app.models.listing import Listing
from app.models.product import Product, ProductMatch
from app.models.search import PriceContext, SearchDiagnostics
from app.providers.ebay import EbayProvider, ebay_config_from_env
from app.providers.mock import MockAmazonProvider, MockEbayProvider
from app.ranking.scorer import best_listing, is_bad_listing, rejection_reasons, score_listing, top_listings
from app.services.feedback_store import filter_reported_listings, log_filtered_listings
from app.services.keh_feed import public_keh_listings
from app.services.price_store import build_price_context, record_price_snapshot
from app.services.product_discovery import resolve_discoverable_product


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


def _provider_queries_for_product(query: str, product: Product | None) -> list[str]:
    if product is None:
        return [query]
    if product.category == "ram":
        return [ram_provider_query(product)]
    if product.category == "consoles":
        return console_provider_queries(product)
    if product.category == "cpus":
        return [cpu_provider_query(product)]
    return [product.display_name]


def _provider_query_for_product(query: str, product: Product | None) -> str:
    """Backward-compatible single-query helper used by older tests/callers."""
    return _provider_queries_for_product(query, product)[0]


def _search_product_scopes(product: Product | None) -> list[Product | None]:
    if product is not None and product.metadata.get("builder") == "consoles":
        expanded = list(console_search_products(product))
        aligned: list[Product] = []
        seen: set[str] = set()
        for scoped_product in expanded:
            # Family searches must use the same exact-product identity and
            # matching rules as selecting that model directly in the builder.
            # Otherwise a generated Series X child can be filtered differently
            # from a direct Series X search backed by the static catalog.
            direct_match = match_product(scoped_product.display_name, "consoles")
            resolved_product = direct_match.product if direct_match is not None else scoped_product
            if resolved_product.id in seen:
                continue
            seen.add(resolved_product.id)
            aligned.append(resolved_product)
        return aligned or expanded
    return [product]


def _listing_identity(listing: Listing) -> str:
    return str(listing.url).split("?", 1)[0]


def _listing_title_identity(listing: Listing) -> str:
    # Different marketplace item IDs can still represent duplicate listings
    # with the exact same visible title. Normalize punctuation/casing so those
    # duplicates cannot occupy every slot in the buyer-facing top three.
    return normalize_text(listing.title, strip_filler=False)


def _top_scored_listings_with_stats(
    listings: list[Listing],
    limit: int = 3,
) -> tuple[list[Listing], int]:
    selected: list[Listing] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    duplicates_removed = 0

    for listing in sorted(listings, key=lambda item: item.score, reverse=True):
        url_key = _listing_identity(listing)
        title_key = _listing_title_identity(listing)
        if url_key in seen_urls or (title_key and title_key in seen_titles):
            duplicates_removed += 1
            continue
        seen_urls.add(url_key)
        if title_key:
            seen_titles.add(title_key)
        if len(selected) < max(1, limit):
            selected.append(listing)

    return selected, duplicates_removed


def _top_scored_listings(listings: list[Listing], limit: int = 3) -> list[Listing]:
    selected, _duplicates_removed = _top_scored_listings_with_stats(listings, limit=limit)
    return selected


def _unique_eligible_listings(
    listings: list[Listing],
    product: Product | None,
) -> list[Listing]:
    eligible: list[Listing] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    for listing in listings:
        if rejection_reasons(listing, product):
            continue
        url_key = _listing_identity(listing)
        title_key = _listing_title_identity(listing)
        if url_key in seen_urls or (title_key and title_key in seen_titles):
            continue
        seen_urls.add(url_key)
        if title_key:
            seen_titles.add(title_key)
        eligible.append(listing)
    return eligible


def _listing_rejection_summary(
    listings: list[Listing],
    product: Product | None,
) -> tuple[int, int, Counter[str]]:
    rejected = 0
    eligible = 0
    reason_counts: Counter[str] = Counter()
    for listing in listings:
        reasons = rejection_reasons(listing, product)
        if reasons:
            rejected += 1
            reason_counts.update(set(reasons))
        else:
            eligible += 1
    return rejected, eligible, reason_counts


def _merge_reason_counts(target: dict[str, int], counts: Counter[str]) -> None:
    for reason, count in counts.items():
        target[reason] = target.get(reason, 0) + count


def _auction_sort_key(listing: Listing) -> tuple[int, datetime, float]:
    ends_at = _parse_ebay_dt(listing.item_end_date) or datetime.max.replace(tzinfo=UTC)
    bundle_rank = 1 if "Bundle / extras included" in listing.warning_labels else 0
    return (bundle_rank, ends_at, listing.total_price)


def _top_combined_auctions_with_stats(
    listings: list[Listing],
    limit: int = 3,
) -> tuple[list[Listing], int]:
    selected: list[Listing] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    duplicates_removed = 0

    for listing in sorted(listings, key=_auction_sort_key):
        url_key = _listing_identity(listing)
        title_key = _listing_title_identity(listing)
        if url_key in seen_urls or (title_key and title_key in seen_titles):
            duplicates_removed += 1
            continue
        seen_urls.add(url_key)
        if title_key:
            seen_titles.add(title_key)
        if len(selected) < max(1, limit):
            selected.append(listing)

    return selected, duplicates_removed


def _top_combined_auctions(listings: list[Listing], limit: int = 3) -> list[Listing]:
    selected, _duplicates_removed = _top_combined_auctions_with_stats(listings, limit=limit)
    return selected


SUPPORTED_CATALOG_CATEGORIES = {"cameras", "gpus", "ram", "cpus", "consoles", "lego"}


def _catalog_product_required_but_missing(category: str | None, product_match: ProductMatch | None) -> bool:
    """Keep public searches inside PriceSift's tuned product catalog.

    An unresolved query must not fall through to a raw marketplace search. That
    would make unsupported products look supported while bypassing the exact-item
    filters that are the point of PriceSift.
    """

    return normalize_category(category) in SUPPORTED_CATALOG_CATEGORIES and product_match is None


def _provider_keys_for_product(provider_keys: list[str], product: Product | None) -> list[str]:
    if product is not None and product.metadata.get("provider_scope") == "keh":
        return []
    return provider_keys


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
    item_location_country: str | None = None,
) -> tuple[list[Listing], int]:
    provider = PROVIDERS.get(provider_key.lower())
    if provider is None:
        return [], 0

    try:
        search_options = {}
        if item_location_country and provider_key.lower() == "ebay":
            search_options["item_location_country"] = item_location_country
        listings = await provider.search(
            provider_query,
            category,
            buying_option=buying_option,
            **search_options,
        )
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
    item_location_country: str | None = None,
) -> tuple[ProductMatch | None, list[Listing]]:
    product_match = resolve_discoverable_product(query, category)
    if _catalog_product_required_but_missing(category, product_match):
        return None, []
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    search_products = _search_product_scopes(product)
    results: list[Listing] = []

    for provider_key in _provider_keys_for_product(provider_keys, product):
        provider_candidates: list[Listing] = []
        for scoped_product in search_products:
            for provider_query in _provider_queries_for_product(query, scoped_product):
                listings, _candidate_count = await _search_provider(
                    provider_key=provider_key,
                    provider_query=provider_query,
                    category=search_category,
                    product=scoped_product,
                    buying_option="fixed_price",
                    item_location_country=item_location_country,
                )
                provider_candidates.extend(top_listings(listings, scoped_product, limit=3))
        best_candidates = _top_scored_listings(provider_candidates, limit=1)
        if best_candidates:
            results.append(best_candidates[0])

    if product is not None:
        keh_candidates = public_keh_listings(product, limit=3)
        if keh_candidates:
            results.append(keh_candidates[0])

    return product_match, sorted(results, key=lambda item: item.total_price)


async def search_best_deals_with_auctions(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
    include_auctions: bool = True,
    auction_hours: int = 24,
    snapshot_source: str = "search",
    item_location_country: str | None = None,
) -> tuple[ProductMatch | None, list[Listing], list[Listing], SearchDiagnostics, PriceContext]:
    product_match = resolve_discoverable_product(query, category)
    if _catalog_product_required_but_missing(category, product_match):
        return None, [], [], SearchDiagnostics(), PriceContext()
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    search_products = _search_product_scopes(product)
    fixed_results: list[Listing] = []
    auction_results: list[Listing] = []
    diagnostics = SearchDiagnostics()
    provider_price_candidates: dict[str, list[Listing]] = {}
    provider_candidate_counts: dict[str, int] = {}
    provider_filtered_counts: dict[str, int] = {}

    for provider_key in _provider_keys_for_product(provider_keys, product):
        provider_fixed_candidates: list[Listing] = []
        provider_auction_candidates: list[Listing] = []
        provider_price_candidates.setdefault(provider_key.lower(), [])
        provider_candidate_counts.setdefault(provider_key.lower(), 0)
        provider_filtered_counts.setdefault(provider_key.lower(), 0)

        for scoped_product in search_products:
            for provider_query in _provider_queries_for_product(query, scoped_product):
                fixed_listings, fixed_candidate_count = await _search_provider(
                    provider_key=provider_key,
                    provider_query=provider_query,
                    category=search_category,
                    product=scoped_product,
                    buying_option="fixed_price",
                    item_location_country=item_location_country,
                )
                diagnostics.fixed_price_candidates += fixed_candidate_count
                provider_candidate_counts[provider_key.lower()] += fixed_candidate_count
                report_filtered = max(0, fixed_candidate_count - len(fixed_listings))
                rejected, eligible, reason_counts = _listing_rejection_summary(fixed_listings, scoped_product)
                diagnostics.fixed_price_filtered += report_filtered + rejected
                diagnostics.fixed_price_eligible += eligible
                provider_filtered_counts[provider_key.lower()] += report_filtered + rejected
                if report_filtered:
                    reason_counts["reported listing filter"] += report_filtered
                _merge_reason_counts(diagnostics.fixed_price_rejection_reasons, reason_counts)
                provider_fixed_candidates.extend(top_listings(fixed_listings, scoped_product, limit=3))
                provider_price_candidates[provider_key.lower()].extend(
                    _unique_eligible_listings(fixed_listings, scoped_product)
                )

                if include_auctions and provider_key.lower() == "ebay":
                    auction_listings, auction_candidate_count = await _search_provider(
                        provider_key=provider_key,
                        provider_query=provider_query,
                        category=search_category,
                        product=scoped_product,
                        buying_option="auction",
                        item_location_country=item_location_country,
                    )
                    diagnostics.auction_candidates += auction_candidate_count
                    report_filtered = max(0, auction_candidate_count - len(auction_listings))
                    rejected, eligible, reason_counts = _listing_rejection_summary(auction_listings, scoped_product)
                    diagnostics.auction_filtered += report_filtered + rejected
                    diagnostics.auction_eligible += eligible
                    if report_filtered:
                        reason_counts["reported listing filter"] += report_filtered
                    _merge_reason_counts(diagnostics.auction_rejection_reasons, reason_counts)
                    provider_auction_candidates.extend(
                        best_auction_listings(
                            auction_listings,
                            scoped_product,
                            max_hours=auction_hours,
                            limit=3,
                        )
                    )

        provider_fixed_results, fixed_duplicates = _top_scored_listings_with_stats(provider_fixed_candidates, limit=3)
        diagnostics.fixed_price_duplicates_removed += fixed_duplicates
        fixed_results.extend(provider_fixed_results)

        provider_auction_results, auction_duplicates = _top_combined_auctions_with_stats(provider_auction_candidates, limit=3)
        diagnostics.auction_duplicates_removed += auction_duplicates
        auction_results.extend(provider_auction_results)

    if product is not None:
        keh_candidates = public_keh_listings(product)
        if keh_candidates:
            diagnostics.fixed_price_candidates += len(keh_candidates)
            diagnostics.fixed_price_eligible += len(keh_candidates)
            fixed_results.extend(keh_candidates)
            provider_price_candidates["keh"] = keh_candidates
            provider_candidate_counts["keh"] = len(keh_candidates)
            provider_filtered_counts["keh"] = 0

    final_fixed_results, fixed_duplicates = _top_scored_listings_with_stats(fixed_results, limit=3)
    diagnostics.fixed_price_duplicates_removed += fixed_duplicates
    final_auction_results, auction_duplicates = _top_combined_auctions_with_stats(auction_results, limit=3)
    diagnostics.auction_duplicates_removed += auction_duplicates

    current_prices: list[float] = []
    if product is not None:
        for provider_key, candidates in provider_price_candidates.items():
            unique_candidates = _unique_eligible_listings(candidates, None)
            prices = [listing.total_price for listing in unique_candidates]
            current_prices.extend(prices)
            # Never persist mock-provider data. Production eBay credentials are
            # the signal that these are real marketplace observations.
            if (
                provider_key == "ebay"
                and ebay_config_from_env() is not None
                and item_location_country is None
            ):
                record_price_snapshot(
                    product_id=product.id,
                    category=product.category,
                    product_label=product.display_name,
                    provider=provider_key,
                    query=query,
                    prices=prices,
                    candidate_count=provider_candidate_counts.get(provider_key, 0),
                    filtered_count=provider_filtered_counts.get(provider_key, 0),
                    source=snapshot_source,
                )
        price_context = PriceContext(**build_price_context(product_id=product.id, current_prices=current_prices))
    else:
        price_context = PriceContext()

    return (
        product_match,
        final_fixed_results,
        sorted(final_auction_results, key=lambda item: item.item_end_date or ""),
        diagnostics,
        price_context,
    )


async def search_auction_deals(
    query: str,
    provider_keys: list[str],
    category: str | None = None,
    auction_hours: int = 24,
    item_location_country: str | None = None,
) -> tuple[ProductMatch | None, list[Listing], SearchDiagnostics]:
    product_match = resolve_discoverable_product(query, category)
    if _catalog_product_required_but_missing(category, product_match):
        return None, [], SearchDiagnostics()
    product = product_match.product if product_match else None
    search_category = product.category if product else category
    search_products = _search_product_scopes(product)
    auction_results: list[Listing] = []
    diagnostics = SearchDiagnostics()

    for provider_key in _provider_keys_for_product(provider_keys, product):
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
                item_location_country=item_location_country,
            )
            diagnostics.auction_candidates += auction_candidate_count
            report_filtered = max(0, auction_candidate_count - len(auction_listings))
            rejected, eligible, reason_counts = _listing_rejection_summary(auction_listings, scoped_product)
            diagnostics.auction_filtered += report_filtered + rejected
            diagnostics.auction_eligible += eligible
            if report_filtered:
                reason_counts["reported listing filter"] += report_filtered
            _merge_reason_counts(diagnostics.auction_rejection_reasons, reason_counts)
            provider_auction_candidates.extend(
                best_auction_listings(
                    auction_listings,
                    scoped_product,
                    max_hours=auction_hours,
                    limit=3,
                )
            )
        provider_auction_results, auction_duplicates = _top_combined_auctions_with_stats(provider_auction_candidates, limit=3)
        diagnostics.auction_duplicates_removed += auction_duplicates
        auction_results.extend(provider_auction_results)

    final_auction_results, auction_duplicates = _top_combined_auctions_with_stats(auction_results, limit=3)
    diagnostics.auction_duplicates_removed += auction_duplicates

    return (
        product_match,
        sorted(final_auction_results, key=lambda item: item.item_end_date or ""),
        diagnostics,
    )
