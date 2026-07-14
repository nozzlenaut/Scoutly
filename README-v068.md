# Scoutly v0.6.8 / grouped console models

Scoutly remains the internal project name. PriceSift now treats the core console model as the searchable product and keeps storage, color, drive, and bundle variants grouped underneath it.

## Included

- Replaces 18 variant-specific Console catalog rows with 16 core-model products.
- Examples: Xbox Series S, Xbox Series X, PlayStation 5, PS5 Slim, PS5 Pro, Nintendo Switch, Switch OLED, Switch Lite, Switch 2, and Wii U.
- Queries such as `Xbox Series S 512GB` and `Xbox Series S Carbon Black 1TB` both resolve to `Xbox Series S`.
- Queries such as `PS5 Slim Disc` and `PS5 Slim Digital` both resolve to `PlayStation 5 Slim`.
- Removes storage and Disc/Digital narrowing from the Console builder for now.
- Keeps original variant wording as aliases so old searches and result-page URLs continue to work.
- Replaces the 16 Console QA cases with core-model tests and new case IDs, which leaves existing LEGO evaluations intact while resetting Console QA to untested.
- Activates broad core-model QA coverage for Switch 2 and Wii U.
- All 153 backend tests pass and the Next.js production build completes successfully.

No database migration or new environment variable is required. Existing saved QA rows remain stored; old Console case IDs are simply no longer part of the active benchmark.

## Run locally

### Backend

```bash
cd backend
py -3.12 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
PYTHONPATH=. pytest -q
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `/admin/qa` and rerun the 16 newly reset Console cases. The 20 LEGO cases keep their existing case IDs and latest saved evaluations.
