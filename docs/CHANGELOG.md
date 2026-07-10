# Changelog

## 0.2.2 - Category search added

- Replaced the status-heavy homepage area with a category picker.
- Added Cameras and Lenses as active starter categories.
- Converted the product catalog from GPU-specific fields to a generic category/product model.
- Added starter photography catalog entries for common camera bodies and lenses.
- Added category-specific reject terms for accessories, parts-only listings, broken gear, lens fungus/haze, caps, hoods, and boxes.
- Kept GPUs available as a PC-parts lab category.
- Updated search, autocomplete, and mock results to pass category context through the app.

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

## v0.2.3 - Vercel autocomplete CORS hotfix

- Allows the deployed Vercel frontend to call the Railway backend from the browser.
- Keeps the public API open for MVP development because Scoutly does not use cookies or browser credentials yet.
