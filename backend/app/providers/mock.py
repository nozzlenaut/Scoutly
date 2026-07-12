from app.models.listing import Listing
from app.providers.base import MarketplaceProvider


def _camera_results(provider_name: str, query: str) -> list[Listing]:
    lower = query.lower()
    if "a7 iii" in lower or "a7 3" in lower:
        return [
            Listing(
                provider=provider_name,
                title="Sony Alpha A7 III 24.2MP Mirrorless Camera Body - Used Good",
                price=879.99,
                shipping=0,
                total_price=879.99,
                condition="Used - Good",
                seller_rating=99.1,
                url="https://www.ebay.com/",
                image_url=None,
            ),
            Listing(
                provider=provider_name,
                title="Sony A7III Battery Charger Bundle Only",
                price=39.99,
                shipping=4.99,
                total_price=44.98,
                condition="Used",
                seller_rating=98.8,
                url="https://www.ebay.com/",
                image_url=None,
            ),
        ]
    return [
        Listing(
            provider=provider_name,
            title=f"{query} - Used camera body in good condition",
            price=749.99,
            shipping=12.99,
            total_price=762.98,
            condition="Used",
            seller_rating=98.5,
            url="https://www.ebay.com/",
            image_url=None,
        )
    ]


def _lens_results(provider_name: str, query: str) -> list[Listing]:
    lower = query.lower()
    if "24-70" in lower or "24 70" in lower:
        return [
            Listing(
                provider=provider_name,
                title="Sony FE 24-70mm f/2.8 GM Lens SEL2470GM - Used Excellent",
                price=1099.00,
                shipping=0,
                total_price=1099.00,
                condition="Used - Excellent",
                seller_rating=99.6,
                url="https://www.ebay.com/",
                image_url=None,
            ),
            Listing(
                provider=provider_name,
                title="Sony 24-70 GM Lens Hood Only",
                price=24.99,
                shipping=5.99,
                total_price=30.98,
                condition="Used",
                seller_rating=97.0,
                url="https://www.ebay.com/",
                image_url=None,
            ),
        ]
    return [
        Listing(
            provider=provider_name,
            title=f"{query} lens - Used clean glass",
            price=399.99,
            shipping=0,
            total_price=399.99,
            condition="Used",
            seller_rating=98.2,
            url="https://www.ebay.com/",
            image_url=None,
        )
    ]


def _gpu_results(provider_name: str) -> list[Listing]:
    return [
        Listing(
            provider=provider_name,
            title="EVGA GeForce RTX 3060 XC 12GB GDDR6 Graphics Card",
            price=178.99,
            shipping=0,
            total_price=178.99,
            condition="Used",
            seller_rating=99.4,
            url="https://www.ebay.com/",
            image_url=None,
        ),
        Listing(
            provider=provider_name,
            title="Broken RTX 3060 12GB For Parts Only",
            price=89.99,
            shipping=12.99,
            total_price=102.98,
            condition="For parts",
            seller_rating=98.1,
            url="https://www.ebay.com/",
            image_url=None,
        ),
    ]


class MockEbayProvider(MarketplaceProvider):
    name = "eBay"

    async def search(self, query: str, category: str | None = None, buying_option: str = "fixed_price") -> list[Listing]:
        lower = query.lower()
        if buying_option == "auction":
            return [
                Listing(
                    provider=self.name,
                    title=f"{query} - auction ending soon",
                    price=625.00,
                    shipping=14.99,
                    total_price=639.99,
                    condition="Used",
                    seller_rating=99.0,
                    url="https://www.ebay.com/itm/123456789012",
                    image_url=None,
                    listing_type="auction",
                    buying_options=["AUCTION"],
                    bid_count=12,
                    current_bid_price=625.00,
                    item_end_date="2099-01-01T00:00:00.000Z",
                )
            ]
        if any(term in lower for term in ["sony", "canon", "nikon", "fujifilm", "fuji", "a7", "eos", "z6", "x-t4", "x100v"]):
            if any(term in lower for term in ["24-70", "70-200", "35mm", "50mm", "lens", "fe ", "rf ", "xf "]):
                return _lens_results(self.name, query)
            return _camera_results(self.name, query)
        return _gpu_results(self.name)


class MockAmazonProvider(MarketplaceProvider):
    name = "Amazon"

    async def search(self, query: str, category: str | None = None, buying_option: str = "fixed_price") -> list[Listing]:
        lower = query.lower()
        if "a7 iii" in lower or "a7 3" in lower:
            return [
                Listing(
                    provider=self.name,
                    title="Sony Alpha a7 III Mirrorless Digital Camera Body - Used Very Good",
                    price=929.00,
                    shipping=0,
                    total_price=929.00,
                    condition="Used - Very Good",
                    seller_rating=96.7,
                    url="https://www.amazon.com/",
                    image_url=None,
                )
            ]
        if "24-70" in lower or "24 70" in lower:
            return [
                Listing(
                    provider=self.name,
                    title="Sony FE 24-70mm f/2.8 GM Lens - Used Very Good",
                    price=1149.00,
                    shipping=0,
                    total_price=1149.00,
                    condition="Used - Very Good",
                    seller_rating=96.1,
                    url="https://www.amazon.com/",
                    image_url=None,
                )
            ]
        return [
            Listing(
                provider=self.name,
                title="ASUS Dual NVIDIA GeForce RTX 3060 12GB Used - Very Good",
                price=194.50,
                shipping=0,
                total_price=194.50,
                condition="Used - Very Good",
                seller_rating=96.2,
                url="https://www.amazon.com/",
                image_url=None,
            ),
            Listing(
                provider=self.name,
                title="RTX 3060 Laptop GPU listing - not desktop card",
                price=149.99,
                shipping=0,
                total_price=149.99,
                condition="Used",
                seller_rating=94.0,
                url="https://www.amazon.com/",
                image_url=None,
            ),
        ]
