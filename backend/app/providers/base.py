from abc import ABC, abstractmethod

from app.models.listing import Listing


class MarketplaceProvider(ABC):
    name: str

    @abstractmethod
    async def search(self, query: str) -> list[Listing]:
        raise NotImplementedError
