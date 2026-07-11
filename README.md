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
