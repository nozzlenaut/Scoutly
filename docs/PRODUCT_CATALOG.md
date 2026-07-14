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
- Consoles: core model plus grouped storage, color, drive, revision, and bundle variants

## Current categories

- Cameras: active starter category
- Lenses: paused in the public UI until eBay lens-part filtering is cleaner
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
| Consoles | `Xbox Series S Carbon Black 1TB` | Xbox Series S |
| Consoles | `PS5 Slim Digital` | PlayStation 5 Slim |

## Why free-text and dropdown both exist

The dropdown improves accuracy, but it is not required. Users can still type natural shorthand. The backend resolver decides the canonical product either way.

## Backend endpoints

- `GET /api/products?category=cameras`
- `GET /api/products/resolve?q=a7iii&category=cameras`
- `GET /api/products/suggest?q=sony&category=lenses&limit=8`


## v0.3.4 catalog expansion

The catalog now includes a broader test set across camera bodies, lenses, and GPUs. The product catalog is still curated manually so exact-item matching stays conservative.


## v0.3.7A catalog accuracy expansion

The catalog now contains 184 products total:

- Cameras: 61 active camera bodies
- GPUs: 97 active graphics cards
- Lenses: 26 retained in the backend catalog, but hidden from the active UI for now

This update is catalog-only plus camera matching cleanup. It does not add the bad-result report button yet.

## v0.3.8 catalog expansion

The catalog now contains 343 products total:

- Cameras: 140 active camera bodies and fixed-lens cameras
- GPUs: 177 active graphics cards across consumer, workstation, and datacenter-style listings
- Lenses: 26 retained in the backend catalog, but still hidden from the active UI

The GPU expansion includes more common homelab/LLM search targets such as Tesla P40, Tesla T4, RTX A4000/A5000/A6000, RTX 5000/6000 Ada, Radeon Pro, Instinct, and Arc Pro cards.
