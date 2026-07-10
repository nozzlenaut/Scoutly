# Scoutly

Scoutly helps users find the best used deals across multiple online marketplaces by intelligently comparing listings and surfacing the best option from each retailer.

## Sprint 1

This starter app includes:

- Next.js frontend with TypeScript and Tailwind CSS
- FastAPI backend with a mock `/api/search` endpoint
- Provider-style backend architecture ready for eBay/Amazon integrations
- Basic ranking logic
- Planning docs for roadmap, API, database, and project vision

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

## Current status

The app currently uses mock used-GPU results. The next milestone is replacing the mock eBay provider with the real eBay Browse API.
