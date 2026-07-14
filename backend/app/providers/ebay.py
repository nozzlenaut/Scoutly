import os
import time
from dataclasses import dataclass
from typing import Any
import re
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

import httpx

from app.models.listing import Listing
from app.providers.base import MarketplaceProvider

EBAY_OAUTH_SCOPE = "https://api.ebay.com/oauth/api_scope"
PRODUCTION_API_BASE = "https://api.ebay.com"
SANDBOX_API_BASE = "https://api.sandbox.ebay.com"
PRODUCTION_AUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SANDBOX_AUTH_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"

# eBay US category IDs used to keep exact-item searches out of nearby parts/accessory categories.
# Digital Cameras: https://www.ebay.com/b/Digital-Cameras/31388/bn_779
# Camera Lenses: https://www.ebay.com/b/Camera-Lenses/3323/bn_732
# Graphics/Video Cards: https://www.ebay.com/b/Graphics-Video-Cards/27386/bn_661796
# LEGO Complete Sets & Packs: eBay US category 19006
# Video Game Consoles: eBay US category 139971
EBAY_US_CATEGORY_IDS = {
    "cameras": "31388",
    "lenses": "3323",
    "gpus": "27386",
    "lego": "19006",
    "consoles": "139971",
    # Computer Memory (RAM)
    "ram": "170083",
}


@dataclass
class EbayConfig:
    client_id: str
    client_secret: str
    marketplace_id: str = "EBAY_US"
    environment: str = "production"
    delivery_country: str = "US"
    delivery_postal_code: str | None = None
    affiliate_campaign_id: str | None = None
    affiliate_reference_id: str | None = None

    @property
    def api_base(self) -> str:
        return SANDBOX_API_BASE if self.environment == "sandbox" else PRODUCTION_API_BASE

    @property
    def auth_url(self) -> str:
        return SANDBOX_AUTH_URL if self.environment == "sandbox" else PRODUCTION_AUTH_URL


def ebay_config_from_env() -> EbayConfig | None:
    client_id = os.getenv("EBAY_CLIENT_ID", "").strip()
    client_secret = os.getenv("EBAY_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return None

    return EbayConfig(
        client_id=client_id,
        client_secret=client_secret,
        marketplace_id=os.getenv("EBAY_MARKETPLACE_ID", "EBAY_US").strip() or "EBAY_US",
        environment=os.getenv("EBAY_ENV", "production").strip().lower() or "production",
        delivery_country=os.getenv("EBAY_DELIVERY_COUNTRY", "US").strip() or "US",
        delivery_postal_code=os.getenv("EBAY_DELIVERY_POSTAL_CODE", "").strip() or None,
        affiliate_campaign_id=os.getenv("EBAY_AFFILIATE_CAMPAIGN_ID", "").strip() or None,
        affiliate_reference_id=os.getenv("EBAY_AFFILIATE_REFERENCE_ID", "").strip() or None,
    )


def _money_value(value: Any) -> float:
    if isinstance(value, dict):
        raw = value.get("value", 0)
    else:
        raw = value or 0
    try:
        return round(float(raw), 2)
    except (TypeError, ValueError):
        return 0.0


def _best_shipping(item: dict[str, Any]) -> float:
    shipping_options = item.get("shippingOptions") or []
    costs: list[float] = []
    for option in shipping_options:
        shipping_cost = option.get("shippingCost")
        if shipping_cost is not None:
            costs.append(_money_value(shipping_cost))
    return min(costs) if costs else 0.0


def _query_params(url: str) -> dict[str, str]:
    try:
        return dict(parse_qsl(urlsplit(url).query, keep_blank_values=True))
    except ValueError:
        return {}


def _url_has_campaign_id(url: str) -> bool:
    return bool(_query_params(url).get("campid"))


def _ensure_affiliate_campaign_params(
    url: str,
    affiliate_campaign_id: str | None = None,
    affiliate_reference_id: str | None = None,
) -> str:
    """Add missing ePN tracking params when eBay returns a partial affiliate URL.

    eBay normally returns itemAffiliateWebUrl when the affiliate header is sent.
    In practice, some returned URLs can contain customid/toolid but omit campid,
    so we add the configured campaign ID as a conservative fallback.
    """
    if not affiliate_campaign_id or "ebay.com" not in url:
        return url

    try:
        parts = urlsplit(url)
    except ValueError:
        return url

    params = dict(parse_qsl(parts.query, keep_blank_values=True))
    if not params.get("campid"):
        params["campid"] = affiliate_campaign_id
    if affiliate_reference_id and not params.get("customid"):
        params["customid"] = affiliate_reference_id

    # These are standard ePN link params. Keep existing values if eBay supplied them.
    params.setdefault("mkevt", "1")
    params.setdefault("mkcid", "1")
    params.setdefault("mkrid", "711-53200-19255-0")
    params.setdefault("toolid", "10049")

    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), parts.fragment))



def _listing_warning_labels(title: str) -> list[str]:
    warnings: list[str] = []
    normalized_title = title.lower()
    bundle_clues = [
        " bundle",
        "with games",
        "games included",
        "with accessories",
        "extra controller",
        "micro sd",
        "microsd",
        "sd card",
        "with monitor",
    ]
    if any(clue in normalized_title for clue in bundle_clues):
        warnings.append("Bundle / extras included")
    shutter_matches = re.findall(r"(?i)(?:shutter\s*(?:count|actuations?)?\s*[:#-]?\s*|)(\d{1,3}(?:,\d{3})+|\d{5,6})\s*(?:shutter|clicks?|actuations?|shots?)", title)
    for raw_count in shutter_matches:
        try:
            count = int(raw_count.replace(",", ""))
        except ValueError:
            continue
        if count >= 200000:
            warnings.append(f"High shutter count: {count:,} shots")
            break
        if count >= 100000:
            warnings.append(f"Elevated shutter count: {count:,} shots")
            break
    return warnings


def _item_location_label(item: dict[str, Any]) -> str | None:
    location = item.get("itemLocation") or {}
    parts = []
    city = location.get("city")
    state = location.get("stateOrProvince")
    country = location.get("country")
    if city:
        parts.append(str(city))
    if state:
        parts.append(str(state))
    if country:
        parts.append(str(country))
    return ", ".join(parts) if parts else None

def ebay_item_to_listing(
    item: dict[str, Any],
    affiliate_campaign_id: str | None = None,
    affiliate_reference_id: str | None = None,
    requested_listing_type: str | None = None,
) -> Listing | None:
    title = item.get("title")
    buying_options = [str(option).upper() for option in item.get("buyingOptions") or []]
    inferred_listing_type = requested_listing_type or ("auction" if "AUCTION" in buying_options else "fixed_price")

    current_bid_price = _money_value(item.get("currentBidPrice"))
    item_price = _money_value(item.get("price"))
    price = current_bid_price if inferred_listing_type == "auction" and current_bid_price > 0 else item_price
    if not title or price <= 0:
        return None

    shipping = _best_shipping(item)
    seller = item.get("seller") or {}
    image = item.get("image") or {}
    raw_affiliate_url = item.get("itemAffiliateWebUrl")
    raw_url = raw_affiliate_url or item.get("itemWebUrl")
    if not raw_url:
        return None

    url = _ensure_affiliate_campaign_params(raw_url, affiliate_campaign_id, affiliate_reference_id)

    seller_rating = seller.get("feedbackPercentage")
    try:
        seller_rating_value = float(seller_rating) if seller_rating is not None else None
    except (TypeError, ValueError):
        seller_rating_value = None
    if seller_rating_value is not None and not (0 < seller_rating_value <= 100):
        seller_rating_value = None

    seller_feedback = seller.get("feedbackScore")
    try:
        seller_feedback_score = int(seller_feedback) if seller_feedback is not None else None
    except (TypeError, ValueError):
        seller_feedback_score = None
    if seller_feedback_score is not None and seller_feedback_score < 0:
        seller_feedback_score = None

    bid_count = item.get("bidCount")
    try:
        bid_count_value = int(bid_count) if bid_count is not None else None
    except (TypeError, ValueError):
        bid_count_value = None

    return Listing(
        provider="eBay",
        title=title,
        price=price,
        shipping=shipping,
        total_price=round(price + shipping, 2),
        condition=item.get("condition") or "Unknown",
        seller_rating=seller_rating_value,
        seller_feedback_score=seller_feedback_score,
        url=url,
        image_url=image.get("imageUrl"),
        affiliate_url_used=bool(raw_affiliate_url) or _url_has_campaign_id(url),
        affiliate_url_has_campaign_id=_url_has_campaign_id(url),
        listing_type=inferred_listing_type,
        buying_options=buying_options,
        bid_count=bid_count_value,
        current_bid_price=current_bid_price if current_bid_price > 0 else None,
        item_end_date=item.get("itemEndDate"),
        warning_labels=_listing_warning_labels(title),
        item_location=_item_location_label(item),
        item_group_type=item.get("itemGroupType"),
    )


class EbayTokenService:
    def __init__(self, config: EbayConfig):
        self.config = config
        self._access_token: str | None = None
        self._expires_at = 0.0

    async def get_access_token(self) -> str:
        if self._access_token and time.time() < self._expires_at - 60:
            return self._access_token

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                self.config.auth_url,
                auth=(self.config.client_id, self.config.client_secret),
                data={"grant_type": "client_credentials", "scope": EBAY_OAUTH_SCOPE},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            payload = response.json()

        self._access_token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 7200))
        self._expires_at = time.time() + expires_in
        return self._access_token


class EbayProvider(MarketplaceProvider):
    name = "eBay"

    def __init__(self, config: EbayConfig | None = None):
        if config is None:
            config = ebay_config_from_env()
        if config is None:
            raise RuntimeError("Missing eBay credentials. Set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET.")
        self.config = config
        self.tokens = EbayTokenService(config)

    async def search(self, query: str, category: str | None = None, buying_option: str = "fixed_price") -> list[Listing]:
        token = await self.tokens.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": self.config.marketplace_id,
        }

        enduser_context = self._enduser_context_header()
        if enduser_context:
            headers["X-EBAY-C-ENDUSERCTX"] = enduser_context

        normalized_option = buying_option.strip().lower()
        if normalized_option == "auction":
            params = {
                "q": query,
                # Auctions are loaded only after the user asks for them, so keep
                # this call focused on the first page of ending-soon candidates.
                "limit": "25",
                "sort": "endingSoonest",
                "filter": "conditions:{USED},buyingOptions:{AUCTION}",
            }
            requested_listing_type = "auction"
        else:
            params = {
                "q": query,
                # Fetch fewer candidates now that we have stronger category and
                # title filters. This keeps normal searches faster while still
                # leaving enough inventory to return three good Buy It Now cards.
                "limit": "35",
                "sort": "price",
                # Keep this conservative for now. Removing the condition filter caused
                # eBay to return too many parts/accessory listings. Additional safe
                # conditions can be added once we validate category-specific filters.
                "filter": "conditions:{USED},buyingOptions:{FIXED_PRICE}",
            }
            requested_listing_type = "fixed_price"

        category_id = self._category_id_for(category)
        if category_id is not None:
            params["category_ids"] = category_id

        payload = await self._search_request(headers, params)
        items = payload.get("itemSummaries") or []

        listings: list[Listing] = []
        for item in items:
            listing = ebay_item_to_listing(
                item,
                affiliate_campaign_id=self.config.affiliate_campaign_id,
                affiliate_reference_id=self.config.affiliate_reference_id,
                requested_listing_type=requested_listing_type,
            )
            if listing is not None:
                listings.append(listing)
        return listings


    def _category_id_for(self, category: str | None) -> str | None:
        if self.config.marketplace_id != "EBAY_US" or category is None:
            return None
        return EBAY_US_CATEGORY_IDS.get(category.strip().lower())

    def _enduser_context_header(self) -> str | None:
        values: list[str] = []

        if self.config.affiliate_campaign_id:
            values.append(f"affiliateCampaignId={self.config.affiliate_campaign_id}")
            if self.config.affiliate_reference_id:
                values.append(f"affiliateReferenceId={self.config.affiliate_reference_id}")

        if self.config.delivery_country:
            location = f"country={self.config.delivery_country}"
            if self.config.delivery_postal_code:
                location = f"{location},zip={self.config.delivery_postal_code}"
            values.append(f"contextualLocation={quote(location, safe='')}")

        return ",".join(values) if values else None

    async def _search_request(self, headers: dict[str, str], params: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.config.api_base}/buy/browse/v1/item_summary/search",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()
