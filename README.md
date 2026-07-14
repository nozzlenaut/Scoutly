# Scoutly v0.6.6 / PriceSift console direct-search rollback

Scoutly remains the internal project name. PriceSift now uses category-specific search styles: direct exact-item search for Cameras, GPUs, Consoles, and LEGO; a specification builder for RAM.

## Included

- Replaced the Console builder with direct autocomplete search.
- Console suggestions resolve to exact static catalog products.
- Removed family-level builder interception from normal console searches.
- Preserved the original Nintendo Switch aliases and revision marketplace queries:
  - Nintendo Switch / Standard / Original
  - Nintendo Switch V1 / Switch V1 / HAC-001
  - Nintendo Switch V2 / Switch V2 / HAC-001(-01)
- Kept all v0.6.5 precision filters for Digital Edition, older-console parts, GPU failures, LEGO completeness, and mixed-brand RAM.

No Railway, PostgreSQL, Vercel, domain, or environment changes are required.

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
