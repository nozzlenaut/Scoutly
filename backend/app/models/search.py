from pydantic import BaseModel, Field

from app.models.listing import Listing
from app.models.product import ProductMatch


class SearchDiagnostics(BaseModel):
    fixed_price_candidates: int = 0
    fixed_price_filtered: int = 0
    fixed_price_eligible: int = 0
    fixed_price_duplicates_removed: int = 0
    fixed_price_rejection_reasons: dict[str, int] = Field(default_factory=dict)
    auction_candidates: int = 0
    auction_filtered: int = 0
    auction_eligible: int = 0
    auction_duplicates_removed: int = 0
    auction_rejection_reasons: dict[str, int] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    category: str | None = None
    resolved_product: ProductMatch | None = None
    suggested_products: list[ProductMatch] = Field(default_factory=list)
    results: list[Listing]
    auction_results: list[Listing] = Field(default_factory=list)
    diagnostics: SearchDiagnostics = Field(default_factory=SearchDiagnostics)
