# Product Catalog

Scoutly uses a product catalog so searches can resolve messy user input into a canonical product before marketplace results are ranked.

Examples:

| User input | Resolved product |
|---|---|
| `3060` | RTX 3060 12GB |
| `rtx3060` | RTX 3060 12GB |
| `3060 ti` | RTX 3060 Ti 8GB |
| `rx6700xt` | RX 6700 XT 12GB |
| `a770 16gb` | Arc A770 16GB |

## Why free-text and dropdown both exist

The dropdown improves accuracy, but it is not required. Users can still type natural shorthand. The backend resolver decides the canonical product either way.

## Current category

- GPU: active
- CPU: planned
- Cameras: planned

## Backend endpoints

- `GET /api/products?category=gpu`
- `GET /api/products/resolve?q=3060`
- `GET /api/products/suggest?q=3060&category=gpu&limit=8`
