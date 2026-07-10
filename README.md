# Scoutly

Scoutly helps users find the best used deals across multiple online marketplaces by intelligently comparing listings and surfacing the best option from each retailer.

## Current status

- **GPU search added**
- **eBay live pricing pending** until API credentials are approved
- CPU and camera search are planned future categories

## Included in this sprint

Sprint 3A adds the public product-status layer:

- Homepage "What's added" panel
- Future-ready category tabs
- GPU marked as the active supported category
- eBay live pricing marked as coming soon
- Release/status tag documentation

## Project structure

```text
Scoutly/
├── frontend/
├── backend/
└── docs/
```

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
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


## v0.2.1

Adds expanded GPU catalog matching and homepage autocomplete. Free-text searches still work; the dropdown is only there to help users choose exact products.
