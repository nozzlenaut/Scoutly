from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import httpx

from app.providers.ebay import EbayProvider


POSTAL_CODE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 -]{1,10}[A-Za-z0-9]$")


def _money(value: Any) -> tuple[float | None, str | None]:
    if not isinstance(value, dict):
        return None, None
    try:
        amount = round(float(value.get("value")), 2)
    except (TypeError, ValueError):
        amount = None
    currency = str(value.get("currency") or "").strip() or None
    return amount, currency


def _location_label(item: dict[str, Any]) -> str | None:
    location = item.get("itemLocation") or {}
    parts = [
        str(location.get(key)).strip()
        for key in ("city", "stateOrProvince", "postalCode", "country")
        if location.get(key)
    ]
    return ", ".join(parts) if parts else None


def _shipping_option(option: dict[str, Any]) -> dict[str, Any]:
    cost, currency = _money(option.get("shippingCost"))
    import_charges, import_currency = _money(option.get("importCharges"))
    ship_to = option.get("shipToLocationUsedForEstimate") or {}
    return {
        "cost": cost,
        "currency": currency,
        "cost_type": option.get("shippingCostType"),
        "carrier": option.get("shippingCarrierCode"),
        "service": option.get("shippingServiceCode"),
        "speed": option.get("type"),
        "min_delivery": option.get("minEstimatedDeliveryDate"),
        "max_delivery": option.get("maxEstimatedDeliveryDate"),
        "import_charges": import_charges,
        "import_currency": import_currency,
        "fulfilled_through": option.get("fulfilledThrough"),
        "estimate_country": ship_to.get("country"),
        "estimate_postal_code": ship_to.get("postalCode"),
    }


def _context_header(provider: EbayProvider, country: str, postal_code: str) -> str:
    values: list[str] = []
    config = provider.config
    if config.affiliate_campaign_id:
        values.append(f"affiliateCampaignId={config.affiliate_campaign_id}")
        if config.affiliate_reference_id:
            values.append(f"affiliateReferenceId={config.affiliate_reference_id}")
    location = quote(f"country={country},zip={postal_code}", safe="")
    values.append(f"contextualLocation={location}")
    return ",".join(values)


def _search_params(
    provider: EbayProvider,
    query: str,
    category: str | None,
    country: str,
    postal_code: str,
    limit: int,
) -> dict[str, str]:
    filters = [
        "conditions:{USED}",
        "buyingOptions:{FIXED_PRICE}",
        f"deliveryCountry:{country}",
        f"deliveryPostalCode:{postal_code}",
    ]
    params = {
        "q": query,
        "limit": str(max(1, min(limit, 10))),
        "sort": "price",
        "filter": ",".join(filters),
    }
    category_id = provider._category_id_for(category)
    if category_id:
        params["category_ids"] = category_id
    return params


async def _fetch_item_detail(
    client: httpx.AsyncClient,
    item_href: str | None,
    headers: dict[str, str],
) -> tuple[dict[str, Any], str | None]:
    if not item_href:
        return {}, "No item detail URL returned by eBay."
    try:
        response = await client.get(item_href, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except (httpx.HTTPError, ValueError) as error:
        return {}, type(error).__name__


def _best_option(options: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not options:
        return None
    return min(
        options,
        key=lambda option: option["cost"] if option.get("cost") is not None else float("inf"),
    )


def _merged_best_option(
    summary_options: list[dict[str, Any]],
    detail_options: list[dict[str, Any]],
) -> dict[str, Any] | None:
    summary_best = _best_option(summary_options)
    detail_best = _best_option(detail_options)
    if not summary_best and not detail_best:
        return None
    merged: dict[str, Any] = {}
    for source in (summary_best, detail_best):
        for key, value in (source or {}).items():
            if value is not None:
                merged[key] = value
    return merged


def _item_result(
    summary: dict[str, Any],
    detail: dict[str, Any],
    detail_error: str | None,
) -> dict[str, Any]:
    summary_options = [_shipping_option(option) for option in summary.get("shippingOptions") or []]
    detail_options = [_shipping_option(option) for option in detail.get("shippingOptions") or []]
    options = detail_options or summary_options
    best = _merged_best_option(summary_options, detail_options)
    price, currency = _money(detail.get("price") or summary.get("price"))
    shipping_cost = best.get("cost") if best else None
    total_price = (
        round(price + shipping_cost, 2)
        if price is not None and shipping_cost is not None
        else price
    )
    item_url = (
        detail.get("itemAffiliateWebUrl")
        or summary.get("itemAffiliateWebUrl")
        or detail.get("itemWebUrl")
        or summary.get("itemWebUrl")
    )
    return {
        "item_id": detail.get("itemId") or summary.get("itemId"),
        "title": detail.get("title") or summary.get("title") or "Untitled listing",
        "condition": detail.get("condition") or summary.get("condition") or "Unknown",
        "price": price,
        "currency": currency,
        "shipping_cost": shipping_cost,
        "total_price": total_price,
        "item_location": _location_label(detail) or _location_label(summary),
        "url": item_url,
        "summary_option_count": len(summary_options),
        "detail_option_count": len(detail_options),
        "detail_loaded": bool(detail),
        "detail_error": detail_error,
        "shipping_options": options,
        "best_shipping_option": best,
    }


async def run_shipping_probe(
    query: str,
    category: str | None,
    postal_code: str,
    country: str = "US",
    limit: int = 5,
) -> dict[str, Any]:
    clean_query = query.strip()
    clean_postal = postal_code.strip()
    clean_country = country.strip().upper()
    if len(clean_query) < 2:
        raise ValueError("A search query is required.")
    if len(clean_country) != 2 or not clean_country.isalpha():
        raise ValueError("Country must be a two-letter code.")
    if not POSTAL_CODE_PATTERN.fullmatch(clean_postal):
        raise ValueError("Postal code format is not valid.")

    provider = EbayProvider()
    headers = await provider._request_headers()
    headers["X-EBAY-C-ENDUSERCTX"] = _context_header(provider, clean_country, clean_postal)
    params = _search_params(provider, clean_query, category, clean_country, clean_postal, limit)
    payload = await provider._search_request(headers, params)
    summaries = (payload.get("itemSummaries") or [])[: max(1, min(limit, 10))]

    items: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=20) as client:
        for summary in summaries:
            detail, detail_error = await _fetch_item_detail(client, summary.get("itemHref"), headers)
            items.append(_item_result(summary, detail, detail_error))

    coverage = {
        "shipping_cost": sum(item.get("shipping_cost") is not None for item in items),
        "delivery_window": sum(
            bool((item.get("best_shipping_option") or {}).get("min_delivery"))
            and bool((item.get("best_shipping_option") or {}).get("max_delivery"))
            for item in items
        ),
        "method": sum(
            any(
                (item.get("best_shipping_option") or {}).get(field)
                for field in ("carrier", "service", "speed")
            )
            for item in items
        ),
        "detail_loaded": sum(bool(item.get("detail_loaded")) for item in items),
        "import_charges": sum(
            (item.get("best_shipping_option") or {}).get("import_charges") is not None
            for item in items
        ),
    }

    return {
        "query": clean_query,
        "category": category,
        "country": clean_country,
        "postal_code": clean_postal,
        "availability_filter_applied": True,
        "search_total": payload.get("total"),
        "returned": len(items),
        "coverage": coverage,
        "items": items,
    }
