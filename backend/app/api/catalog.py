from fastapi import APIRouter, Query

from app.catalog.catalog import list_products, match_product, suggest_products
from app.models.product import Product, ProductMatch

router = APIRouter()


@router.get("/products", response_model=list[Product])
def products(category: str | None = Query(None)) -> list[Product]:
    return list_products(category)


@router.get("/products/resolve", response_model=ProductMatch | None)
def resolve_product(
    q: str = Query(..., min_length=2),
    category: str | None = Query(None),
) -> ProductMatch | None:
    return match_product(q, category)


@router.get("/products/suggest", response_model=list[ProductMatch])
def product_suggestions(
    q: str = Query(..., min_length=2),
    category: str | None = Query(None),
    limit: int = Query(8, ge=1, le=20),
) -> list[ProductMatch]:
    return suggest_products(q, category, limit)
