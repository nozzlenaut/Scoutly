import os
import time
from dataclasses import dataclass
from typing import Any

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
EBAY_US_CATEGORY_IDS = {
    "cameras": "31388",
    "lenses": "3323",
    "gpus": "27386",
}


@dataclass
class EbayConfig:
    client_id: str
    client_secret: str
    marketplace_id: str = "EBAY_US"
    environment: str = "production"
    delivery_country: str = "US"
    delivery_postal_code: str | None = None

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


def ebay_item_to_listing(item: dict[str, Any]) -> Listing | None:
    title = item.get("title")
    price = _money_value(item.get("price"))
    if not title or price <= 0:
        return None

    shipping = _best_shipping(item)
    seller = item.get("seller") or {}
    image = item.get("image") or {}
    url = item.get("itemAffiliateWebUrl") or item.get("itemWebUrl")
    if not url:
        return None

    seller_rating = seller.get("feedbackPercentage")
    try:
        seller_rating_value = float(seller_rating) if seller_rating is not None else None
    except (TypeError, ValueError):
        seller_rating_value = None

    return Listing(
        provider="eBay",
        title=title,
        price=price,
        shipping=shipping,
        total_price=round(price + shipping, 2),
        condition=item.get("condition") or "Unknown",
        seller_rating=seller_rating_value,
        url=url,
        image_url=image.get("imageUrl"),
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

    async def search(self, query: str, category: str | None = None) -> list[Listing]:
        token = await self.tokens.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": self.config.marketplace_id,
        }

        if self.config.delivery_country:
            location = f"country={self.config.delivery_country}"
            if self.config.delivery_postal_code:
                location = f"{location},zip={self.config.delivery_postal_code}"
            headers["X-EBAY-C-ENDUSERCTX"] = f"contextualLocation={location}"

        params = {
            "q": query,
            "limit": "50",
            "sort": "price",
            # Keep this conservative for now. Removing the condition filter caused
            # eBay to return too many parts/accessory listings. Additional safe
            # conditions can be added once we validate category-specific filters.
            "filter": "conditions:{USED},buyingOptions:{FIXED_PRICE}",
        }

        category_id = self._category_id_for(category)
        if category_id is not None:
            params["category_ids"] = category_id

        payload = await self._search_request(headers, params)
        items = payload.get("itemSummaries") or []

        listings: list[Listing] = []
        for item in items:
            listing = ebay_item_to_listing(item)
            if listing is not None:
                listings.append(listing)
        return listings

    def _category_id_for(self, category: str | None) -> str | None:
        if self.config.marketplace_id != "EBAY_US" or category is None:
            return None
        return EBAY_US_CATEGORY_IDS.get(category.strip().lower())

    async def _search_request(self, headers: dict[str, str], params: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.config.api_base}/buy/browse/v1/item_summary/search",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()
