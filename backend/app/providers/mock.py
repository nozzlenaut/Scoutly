from app.models.listing import Listing
from app.providers.base import MarketplaceProvider


class MockEbayProvider(MarketplaceProvider):
    name = "eBay"

    async def search(self, query: str) -> list[Listing]:
        return [
            Listing(
                provider=self.name,
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
                provider=self.name,
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


class MockAmazonProvider(MarketplaceProvider):
    name = "Amazon"

    async def search(self, query: str) -> list[Listing]:
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
