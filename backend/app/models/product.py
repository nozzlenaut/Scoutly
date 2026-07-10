from pydantic import BaseModel, Field, computed_field


class Product(BaseModel):
    id: str
    category: str
    brand: str
    chipset_brand: str
    model: str
    variant: str | None = None
    generation: str | None = None
    vram_gb: int | None = None
    memory_type: str | None = None
    aliases: list[str] = Field(default_factory=list)
    required_terms: list[str] = Field(default_factory=list)
    excluded_terms: list[str] = Field(default_factory=list)
    active: bool = True

    @computed_field
    @property
    def display_name(self) -> str:
        if self.variant:
            return f"{self.model} {self.variant}"
        return self.model


class ProductMatch(BaseModel):
    product: Product
    confidence: float = Field(ge=0, le=1)
    matched_alias: str | None = None
