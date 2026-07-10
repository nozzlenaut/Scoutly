# Scoutly

Scoutly helps users find the best used deals across multiple online marketplaces by resolving messy searches into exact products, then surfacing the best option from each retailer.

## Current status

- **Category-based search added**
- **Cameras and lenses are the primary starter categories**
- **GPU catalog remains available as a PC-parts lab category**
- **Live eBay pricing is pending** until API credentials are approved

## Included in v0.2.2

- Replaces the old status-heavy section with a real category picker
- Adds Cameras and Lenses as active starter categories
- Converts the backend catalog from GPU-only to a generic product catalog
- Adds starter photography products and filters
- Keeps GPU autocomplete working under the GPUs category
- Keeps free-text typing working while encouraging exact autocomplete selection

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

Create `backend/.env` later when API keys are added.
