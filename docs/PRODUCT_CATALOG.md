# Product Catalog

Scoutly uses a product catalog so searches can resolve messy user input into a canonical product before marketplace results are ranked.

## Current model

Products use a generic shape so Scoutly can support more than GPUs:

```text
id
category
category_label
product_type
brand
model
variant
aliases
required_terms
excluded_terms
metadata
active
```

Category-specific facts live in `metadata`.

Examples:

- Cameras: mount, sensor format
- Lenses: mount, focal length, max aperture
- GPUs: chipset brand, VRAM, memory type, generation

## Current categories

- Cameras: active starter category
- Lenses: active starter category
- GPUs: lab category, still useful for testing the PC-parts path

## Example resolutions

| Category | User input | Resolved product |
|---|---|---|
| Cameras | `a7iii` | Sony A7 III Body |
| Cameras | `canon r6` | Canon EOS R6 Body |
| Lenses | `sony 24-70 2.8` | Sony FE 24-70mm f/2.8 GM |
| Lenses | `canon rf 50 1.8` | Canon RF 50mm f/1.8 STM |
| GPUs | `3060` | NVIDIA RTX 3060 12GB |
| GPUs | `rx6700xt` | AMD RX 6700 XT 12GB |

## Why free-text and dropdown both exist

The dropdown improves accuracy, but it is not required. Users can still type natural shorthand. The backend resolver decides the canonical product either way.

## Backend endpoints

- `GET /api/products?category=cameras`
- `GET /api/products/resolve?q=a7iii&category=cameras`
- `GET /api/products/suggest?q=sony&category=lenses&limit=8`
