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


class PriceContext(BaseModel):
    product_id: str | None = None
    window_days: int = 30
    current_eligible_count: int = 0
    current_best_price: float | None = None
    current_median_price: float | None = None
    current_low_price: float | None = None
    current_high_price: float | None = None
    snapshot_count: int = 0
    available_snapshot_count: int = 0
    availability_rate: float | None = None
    history_ready: bool = False
    typical_low_price: float | None = None
    typical_high_price: float | None = None
    historical_median_price: float | None = None
    current_vs_median_percent: float | None = None
    first_observed_at: str | None = None
    last_observed_at: str | None = None


class SearchResponse(BaseModel):
    query: str
    category: str | None = None
    resolved_product: ProductMatch | None = None
    suggested_products: list[ProductMatch] = Field(default_factory=list)
    results: list[Listing]
    auction_results: list[Listing] = Field(default_factory=list)
    diagnostics: SearchDiagnostics = Field(default_factory=SearchDiagnostics)
    price_context: PriceContext = Field(default_factory=PriceContext)
