from abc import ABC, abstractmethod

from app.models.listing import Listing


class MarketplaceProvider(ABC):
    name: str

    @abstractmethod
    async def search(
        self,
        query: str,
        category: str | None = None,
        buying_option: str = "fixed_price",
        item_location_country: str | None = None,
    ) -> list[Listing]:
        raise NotImplementedError
