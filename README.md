# PriceSift

**Find the best price for what you already want.**

PriceSift is an exact-item results site for used and secondhand products. It is for the point where someone already knows what they want and needs a short list of useful current listings - not a wall of marketplace noise.

Live site: https://www.pricesift.app/

`Scoutly` remains the internal repository and infrastructure name.

## What PriceSift does

- Resolves a search to an exact catalog product, specification, or ISBN.
- Filters obvious wrong-model, accessory-only, broken, incomplete, parts-only, and misleading listings when detectable.
- Ranks a small set of useful fixed-price results.
- Keeps optional ending-soon auctions separate.
- Shows total price with shipping when available.
- Requires no account for normal searching.
- Uses clearly disclosed affiliate links without changing displayed prices or ranking rules.

## Current category coverage

| Category | Status | Public providers | Search style |
|---|---|---|---|
| Cameras | Active | eBay + KEH | Catalog bodies plus KEH-standardized camera models |
| Lenses | Beta | KEH only | Mount, prime/zoom, focal group, optional brand |
| Consoles | Active | eBay | Exact model with grouped variants |
| CPUs | Active | eBay | Specification builder |
| GPUs | Active | eBay | Exact desktop GPU |
| RAM | Active | eBay | Specification builder |
| Books | Beta | eBay | ISBN-10 or ISBN-13 |
| LEGO | Beta | eBay | Exact set name or number |

Public eBay lens results remain disabled while lens titles, mounts, bundles, and accessory listings are tested privately.

Current KEH camera titles are automatically grouped into searchable models. A confident PriceSift catalog match can compare eBay and KEH; every additional model stays KEH-only. Stable `/cameras/[slug]` pages expose current inventory without making arbitrary search-result URLs indexable.

When “US listings only” is active, an optional ZIP field appears directly in the search form. Results load first, then shipping totals and delivery windows fill into the matching eBay cards. The ZIP is sent in a POST body for that one lookup and is not stored, logged in analytics, added to a URL, or saved in browser storage.

## Product principles

- PriceSift is a **results site**, not a broad search or browsing site.
- Result quality matters more than result count.
- Search flows should be category-specific.
- New categories need evidence of demand, strategic value, or a clear audience.
- Trust is the product: exact identity, clear condition, honest totals, and transparent affiliate disclosure.

## Project structure

```text
backend/   FastAPI API, marketplace providers, filtering, ranking, analytics, and tests
frontend/  Next.js application and admin tools
docs/      Current status, decisions, process, architecture, and history
```

## Local development

### Backend

```bash
cd backend
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`; the backend runs at `http://localhost:8000`.

## Deployment

- Vercel deploys the frontend from `main`.
- Railway deploys the backend and scheduled jobs from `main`.
- PostgreSQL stores production analytics, reports, QA evaluations, and price history.
- Railway refreshes the KEH feed every six hours; `/admin/keh` can request a fresh sync after matching changes are deployed.

## Project references

- [Current status](docs/STATUS.md)
- [Product decisions](docs/DECISIONS.md)
- [Working agreement](docs/WORKING_AGREEMENT.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](docs/CHANGELOG.md)
- [Product catalog notes](docs/PRODUCT_CATALOG.md)
- [API notes](docs/API.md)
- [Database notes](docs/DATABASE.md)

## License

Licensed under the [MIT License](LICENSE).
