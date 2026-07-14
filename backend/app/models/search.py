from pydantic import BaseModel, Field

from app.models.listing import Listing
from app.models.product import ProductMatch


class SearchDiagnostics(BaseModel):
    fixed_price_candidates: int = 0
    fixed_price_filtered: int = 0
    auction_candidates: int = 0
    auction_filtered: int = 0


class SearchResponse(BaseModel):
    query: str
    category: str | None = None
    resolved_product: ProductMatch | None = None
    suggested_products: list[ProductMatch] = Field(default_factory=list)
    results: list[Listing]
    auction_results: list[Listing] = Field(default_factory=list)
    diagnostics: SearchDiagnostics = Field(default_factory=SearchDiagnostics)
