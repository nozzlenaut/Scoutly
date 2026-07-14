# Scoutly v0.6.3 / PriceSift console family search fix

Scoutly remains the internal project name. This patch makes an unrefined console family search run one exact marketplace search per active model, merge the valid results, remove duplicates, and rank the combined set.

## Included

- `All models` now truly searches every active model in the selected console family.
- Exact model selections still perform only one model-specific search.
- Storage refinements only search compatible models.
- Family-level fixed-price and auction results are merged and deduplicated.
- Console listings containing `controller`/`controllers` require the word `console`.
- Listings containing `service` are rejected globally.
- Builder labels and explanatory copy now describe the combined-search behavior.

No Railway, PostgreSQL, Vercel, domain, or environment changes are required.

## Run locally

### Backend

```bash
cd backend
py -3.12 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
