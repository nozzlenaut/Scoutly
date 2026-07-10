from pydantic import BaseModel, Field, HttpUrl


class Listing(BaseModel):
    provider: str
    title: str
    price: float = Field(ge=0)
    shipping: float = Field(ge=0)
    total_price: float = Field(ge=0)
    condition: str
    seller_rating: float | None = None
    url: HttpUrl
    image_url: HttpUrl | None = None
    score: float = 0
