# Product Catalog

Scoutly uses a product catalog to turn messy user searches into canonical products.

Example:

- User searches: `3060 12gb`
- Scoutly resolves it to: `RTX 3060 12GB`
- Providers search with the canonical product name
- Ranking rejects bad matches like `RTX 3060 Ti`, `RTX 3060 Laptop`, and `Broken RTX 3060`

## Current V1 Scope

The first catalog is GPU-only, but the shape is category-neutral.

Each product includes:

- `id`
- `category`
- `brand`
- `chipset_brand`
- `model`
- `variant`
- `generation`
- `vram_gb`
- `memory_type`
- `aliases`
- `required_terms`
- `excluded_terms`

## API Endpoints

```txt
GET /api/products?category=gpu
GET /api/products/resolve?q=3060+12gb
GET /api/search?q=3060+12gb
```

## Next Catalog Improvements

- Add more NVIDIA GPUs
- Add more AMD GPUs
- Add more Intel Arc GPUs
- Add manufacturer board partner aliases like EVGA, ASUS, MSI, Sapphire, XFX
- Add launch dates and typical used-price ranges
- Move JSON data into PostgreSQL once the catalog stabilizes
