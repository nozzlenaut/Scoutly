# Scoutly v0.5.8 / PriceSift public rebrand

This release keeps Scoutly as the internal project and repository name while changing the public-facing product to **PriceSift** at `https://www.pricesift.app`.

## Included

- PriceSift branding across the public site and admin UI
- Canonical production-domain metadata, manifest, favicon, robots file, and sitemap
- Standalone title-ending `READ` rejection for Buy It Now and auction listings
- 77 additional LEGO catalog entries
- Internal Scoutly package names, database tables, Railway service names, and affiliate reference IDs left unchanged

## Catalog

- Cameras: 141
- GPUs: 177
- Consoles: 18 total (17 active in data; paused categories are handled by UI/catalog logic)
- LEGO: 395
- Lenses retained: 26
- Total: 757

## Deployment

No Railway or database rename is required. Deploy the frontend normally through Vercel; the configured `pricesift.app`/`www.pricesift.app` domains will use the new public metadata automatically.
