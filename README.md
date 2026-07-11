# Scoutly

Scoutly helps users find the best used deals across multiple online marketplaces by resolving messy searches into exact products, then surfacing the best option from each retailer.

## Current status

- **Category-based search added**
- **Cameras and lenses are the primary starter categories**
- **Live eBay marketplace search added**
- **GPU catalog remains available as a PC-parts lab category**

## Included in v0.3.0

- eBay Browse API OAuth support
- Live eBay used-listing provider
- eBay listing normalization into Scoutly result cards
- Image support on result cards
- eBay-only default search so the live site does not mix real eBay data with mock Amazon data
- Mock eBay fallback for local development when credentials are missing

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
