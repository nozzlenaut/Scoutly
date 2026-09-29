# PriceSift

**Find the best price for what you already want.**

PriceSift is an exact-item results site for used, secondhand, and budget-conscious shopping. It is for the point where someone already knows what they want and needs a short list of useful current options — not a wall of marketplace noise.

Live site: https://www.pricesift.app/

> The public product is **PriceSift**. `Scoutly` is the older/internal repository name that stuck around.

## What PriceSift does

- Resolves a search to an exact catalog product, specification, or ISBN.
- Filters obvious wrong-model, accessory-only, broken, incomplete, parts-only, and misleading listings when detectable.
- Ranks a small set of useful fixed-price results instead of maximizing result count.
- Keeps optional ending-soon auctions separate.
- Shows total price with shipping when available.
- Adds price-history and item pages where they are useful for comparison and search discovery.
- Requires no account for normal searching.
- Uses clearly disclosed affiliate links without changing displayed prices or ranking rules.

## Current category coverage

| Category | Status | Public sources / routes | Search style |
|---|---|---|---|
| Cameras | Active | eBay + KEH | Catalog bodies plus KEH-standardized camera models |
| Lenses | Beta | KEH | Mount, prime/zoom, focal group, optional brand |
| Consoles | Active | eBay | Exact model with grouped variants |
| CPUs | Active | eBay | Specification builder |
| GPUs | Active | eBay | Exact desktop GPU |
| RAM | Active | eBay | Specification builder |
| Books | Active | eBay + Better World Books + Amazon + Audible | ISBN plus book-specific purchase/listening routes |
| LEGO | Beta | eBay | Exact set name or number |

### Books work a little differently

Books are not treated as just another generic marketplace category. A resolved title/ISBN can surface different ways to get the same book depending on availability:

- used or secondhand copies from **Better World Books** and **eBay**
- **Amazon** purchase routes where appropriate
- **Audible** as a listening option for titles with an audiobook version

Those sources do not all expose inventory in the same way, so PriceSift keeps the book flow provider-aware instead of forcing every result into one fake universal listing format.

Better World Books is part of the normal book-result path rather than a hidden fallback, and the broader goal is to make the book page useful whether someone wants the cheapest physical copy or a legitimate alternate format.

## Cameras and shipping

Public eBay lens results remain disabled while lens titles, mounts, bundles, and accessory listings are tested privately.

Current KEH camera titles are automatically grouped into searchable models. A confident PriceSift catalog match can compare eBay and KEH; additional KEH inventory can remain available even when there is not yet a matching eBay catalog item. Stable `/cameras/[slug]` pages expose current inventory without making arbitrary search-result URLs indexable.

When “US listings only” is active, an optional ZIP field appears directly in the search form. Results load first, then shipping totals and delivery windows fill into the matching eBay cards. The ZIP is sent for that lookup and is not intentionally retained as normal analytics data or added to the public search URL.

## Product principles

- PriceSift is a **results site**, not a broad search or browsing site.
- Result quality matters more than result count.
- Search flows should be category-specific when the category actually behaves differently.
- New categories need evidence of demand, strategic value, or a clear audience.
- Trust is the product: exact identity, clear condition, honest totals, and transparent affiliate disclosure.
- The useful answer should stay near the top; details should support the result instead of burying it.

## Project structure

```text
backend/   API, marketplace/provider integrations, filtering, ranking, analytics, and tests
frontend/  Public application and admin tools
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

The frontend runs at `http://localhost:3000`; the backend runs at `http://localhost:8000` during normal local development.

## Production

Production is self-hosted on a Raspberry Pi. GitHub is used for source/history and development work; production is **not** automatically deployed from GitHub.

That separation is intentional: changes are tested before they are pushed to the live Pi.

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
