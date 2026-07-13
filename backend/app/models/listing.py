from pydantic import BaseModel, Field, HttpUrl


class Listing(BaseModel):
    provider: str
    title: str
    price: float = Field(ge=0)
    shipping: float = Field(ge=0)
    total_price: float = Field(ge=0)
    condition: str
    seller_rating: float | None = None
    seller_feedback_score: int | None = None
    url: HttpUrl
    image_url: HttpUrl | None = None
    affiliate_url_used: bool = False
    affiliate_url_has_campaign_id: bool = False
    score: float = 0
    listing_type: str = "fixed_price"
    buying_options: list[str] = Field(default_factory=list)
    bid_count: int | None = None
    current_bid_price: float | None = None
    item_end_date: str | None = None
    warning_labels: list[str] = Field(default_factory=list)
    item_location: str | None = None
