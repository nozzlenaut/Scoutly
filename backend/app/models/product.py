from typing import Any

from pydantic import BaseModel, Field, computed_field


class Product(BaseModel):
    id: str
    category: str
    category_label: str
    product_type: str
    brand: str
    model: str
    variant: str | None = None
    aliases: list[str] = Field(default_factory=list)
    required_terms: list[str] = Field(default_factory=list)
    excluded_terms: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    active: bool = True

    @computed_field
    @property
    def display_name(self) -> str:
        parts = [self.brand, self.model, self.variant]
        return " ".join(part for part in parts if part)


class ProductMatch(BaseModel):
    product: Product
    confidence: float = Field(ge=0, le=1)
    matched_alias: str | None = None
