# Scoutly

Scoutly helps users find the best used deals across multiple online marketplaces by resolving messy searches into exact products, then surfacing the best option from each retailer.

## Current status

- **Category-based search added**
- **Cameras and lenses are the primary starter categories**
- **Live eBay marketplace search added**
- **GPU catalog remains available as a PC-parts lab category**

## Included in v0.3.4

- Expanded camera-body catalog for broader photography testing
- Expanded lens catalog across Sony, Canon, Nikon, Fuji, Sigma, and Tamron
- Expanded GPU catalog with more AMD, Intel, and NVIDIA cards
- Tighter lens accessory filters for ring adapters, lens coats, skins, and gear listings

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
