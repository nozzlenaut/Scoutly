from pydantic import BaseModel

from app.models.listing import Listing
from app.models.product import ProductMatch


class SearchResponse(BaseModel):
    query: str
    resolved_product: ProductMatch | None = None
    results: list[Listing]
