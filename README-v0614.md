# Scoutly v0.6.14 / Price snapshots and typical-range foundation

Scoutly now turns clean live searches into price-history observations. The existing six-category search and 88-case QA baseline remain unchanged.

## Included

- Automatically stores a fixed-price snapshot whenever a live eBay search resolves to a catalog product.
- QA workbench searches collect price history automatically, so normal regression testing now doubles as data collection.
- Uses six-hour buckets to avoid storing duplicate observations from repeated refreshes.
- Stores both inventory and safe no-inventory snapshots.
- Captures eligible listing count, lowest price, median, quartiles, candidate/filter counts, and a bounded price sample.
- Shows current best price and current eligible range on buyer-facing search pages immediately.
- Waits for at least three inventory snapshots and nine observed prices before showing a **Typical recent range**.
- Compares the current best price with the recent median once enough history exists.
- Adds `/admin/prices` with snapshot coverage, product history readiness, availability, and latest pricing.
- Adds a small admin collector that rotates through the least-recently observed QA products five at a time.
- Adds PostgreSQL table `scoutly_price_snapshots` automatically at API startup.
- Keeps local-development fallback in `price_snapshots.json` inside `SCOUTLY_DATA_DIR` or `/tmp/scoutly`.

No new environment variables are required. Production collection uses the existing eBay credentials, `DATABASE_URL`, and `SCOUTLY_ADMIN_TOKEN`.

## Data behavior

- Mock-provider results are never persisted as price history.
- A product can store at most one observation per provider in each six-hour window; a later search in the same window updates that observation.
- Safe no-inventory observations remain in history so Scoutly can measure availability rather than pretending an empty market never happened.
- Existing QA evaluations did not store listing prices, so historical prices begin after deploying this release.

## Validation

- 175 backend tests pass.
- All 88 seeded QA queries still resolve to their expected product.
- The Next.js production build completes successfully, including `/admin/prices`.

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

Open `/admin/prices?token=<SCOUTLY_ADMIN_TOKEN>` to inspect collection coverage. Running searches through `/admin/qa` automatically records real snapshots after deployment.
