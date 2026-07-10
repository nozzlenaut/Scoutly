# Changelog

## 0.2.1 - Product catalog autocomplete

- Expanded the GPU product catalog with common NVIDIA, AMD, and Intel desktop GPUs.
- Added `/api/products/suggest` for autocomplete-ready product suggestions.
- Improved alias matching for shorthand searches like `3060`, `rtx3060`, and `rx6700xt`.
- Added homepage autocomplete dropdown while keeping free-text search available.
- Pinned Tailwind dependencies to avoid the Tailwind 4/PostCSS mismatch during local setup.


## 0.2.0 - GPU search added

- Added visible category status tags to the homepage.
- Added future-ready category tabs for GPUs, CPUs, and cameras.
- Marked GPU search as added.
- Marked eBay live pricing as pending until API credentials are approved.
- Added `docs/STATUS.md` for release/status tag conventions.

## 0.1.0 - Product catalog added

- Added GPU catalog JSON.
- Added product resolver.
- Added catalog API routes.
- Added tests for GPU product matching and listing filtering.

## 0.0.1 - Foundation added

- Initial Sprint 1 starter app.
- Added Next.js frontend.
- Added FastAPI backend.
- Added mock search results.
- Added basic ranking logic.
