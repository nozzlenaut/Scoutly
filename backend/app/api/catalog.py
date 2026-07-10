from fastapi import APIRouter, Query

from app.catalog.catalog import list_products, match_product
from app.models.product import Product, ProductMatch

router = APIRouter()


@router.get("/products", response_model=list[Product])
def products(category: str | None = Query("gpu")) -> list[Product]:
    return list_products(category)


@router.get("/products/resolve", response_model=ProductMatch | None)
def resolve_product(q: str = Query(..., min_length=2)) -> ProductMatch | None:
    return match_product(q)
