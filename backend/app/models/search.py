from pydantic import BaseModel

from app.models.listing import Listing
from app.models.product import ProductMatch


class SearchResponse(BaseModel):
    query: str
    category: str | None = None
    resolved_product: ProductMatch | None = None
    results: list[Listing]
    auction_results: list[Listing] = []
