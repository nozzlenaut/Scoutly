# Scoutly

Scoutly helps users find the best used deals across multiple online marketplaces by resolving messy searches into exact products, then surfacing the best option from each retailer.

## Current status

- **Category-based search added**
- **Cameras are active; lenses are retained but temporarily hidden while filtering improves**
- **Live eBay marketplace search added**
- **GPU catalog remains available as a PC-parts lab category**

## Included in v0.4.0

- Autocomplete closes after search submit so suggestions do not cover results.
- Autocomplete hides itself when the typed query is already a 100% exact catalog match.
- eBay Partner Network tracking is supported when affiliate campaign environment variables are set.
- Result links use `rel="sponsored"` for affiliate-readiness.

## Project structure

```text
Scoutly/
├── frontend/
├── backend/
└── docs/
```

## Run locally

### Backend

Git Bash:

```bash
cd backend
py -3.12 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Backend runs at:

```text
http://localhost:8000
```

### Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:3000
```

## Environment variables

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `backend/.env` using `backend/.env.example` as the template.

## v0.3.1

Fixes Next.js search parameter handling so deployed searches use the actual query from the URL, and tightens camera-body filtering so A7 IV does not match A7R IV repair parts.


## v0.3.3

Adds stricter search-quality filters to reject box-only, please-read, as-is, parts, accessory, lens-coat, ring-gear, and broken listings.


## v0.3.4

Adds a larger catalog for cameras, lenses, and GPUs, plus another lens accessory filtering pass.


## v0.3.5

Tightens lens accessory filtering so rubber zoom/focus rings, bayonet mount rings, rear mount rings, and metal replacement rings are rejected while real used lens listings can still pass.

## v0.3.6

Temporarily pauses lens search from the public UI and adds eBay US category IDs for camera-body and GPU searches so Scoutly searches inside Digital Cameras and Graphics/Video Cards instead of relying on keywords alone.


## v0.3.7A

Adds a larger camera/GPU catalog for broader test searches without enabling the bad-result reporting UI yet. Also tightens camera generation matching so A7R III does not match original A7R 36.4MP listings.

## v0.3.8

Doubles down on catalog coverage for camera/GPU testing, adds a compact search form to the results page, and rejects camera-accessory listings such as EOS RP accessory-only results.

## v0.3.9

Adds a focused GPU accessory filter for Tesla/data-center GPU searches so heatsink-only, heat-sink-only, replacement cooler, fan, waterblock, and bracket listings do not win over real GPU cards.


## v0.4.0

Closes autocomplete suggestions after searching or when an exact 100% catalog match is typed, and adds optional eBay Partner Network affiliate tracking support through `EBAY_AFFILIATE_CAMPAIGN_ID` and `EBAY_AFFILIATE_REFERENCE_ID`.

## v0.4.1

Adds a casual affiliate disclosure page/footer and makes eBay affiliate URLs safer by adding the configured `campid` when eBay returns a partial affiliate URL with `customid`/`toolid` but no visible campaign ID.

## v0.4.2

Adds a backend outbound redirect endpoint so eBay affiliate campaign parameters are applied at click time. Result buttons now route through `/api/out` before redirecting to eBay.

## v0.4.3

Adds lightweight outbound click tracking and a Report bad result flow. Reported bad eBay items are hidden for the matched product/category for 72 hours so bad accessory or parts listings do not keep showing for the same search.

## v0.4.4

Adds a lightweight `/admin` analytics page for Scoutly click tracking and active bad-result reports. Also adds a separate auction comparison section on search results using eBay auction listings ending soon, while keeping Buy It Now as the primary result.

Optional backend admin token:

```env
SCOUTLY_ADMIN_TOKEN=replace_with_private_admin_token
```

When this is set, view analytics at:

```text
/admin?token=replace_with_private_admin_token
```
