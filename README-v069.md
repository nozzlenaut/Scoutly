# Scoutly v0.6.9 / console listing quality pass

Scoutly remains the internal project name. PriceSift keeps the grouped core-console catalog introduced in v0.6.8 and now applies a stricter console listing-eligibility and quality-ranking layer before showing marketplace results.

## Included

- Keeps all 16 core console models and grouped storage/color/drive variants unchanged.
- Rejects standalone disc drives, shells, mid-frames, cooling fans, heat sinks, hard cases, packaging/manual-only listings, dock-and-charger listings, and similar accessory/repair results.
- Rejects game titles using phrases such as `Console Edition` when they are not console hardware.
- Adds model-conflict rules for Xbox 360 versus Xbox Series S/X and Nintendo HEG-001/OLED hardware versus the standard Switch.
- Requires stronger hardware evidence for PlayStation Pro listings so accessories that merely mention `PS5 Pro` cannot qualify.
- Keeps `READ` / `please read description` listings eligible but applies a large ranking penalty so clean tested hardware wins.
- Fixes result ordering that previously selected by quality score and then accidentally re-sorted the final top three by lowest price.
- Adds QA diagnostics for eligible candidate counts and the most common rejection reasons.
- Adds regression coverage for the exact console false positives found during the v0.6.8 live QA run.
- All 155 backend tests pass and the Next.js production build completes successfully.

No database migration or new environment variable is required. Existing QA attempts remain saved; rerun and save the same 16 Console cases to compare the new marketplace filtering against the v0.6.8 baseline.

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

Open `/admin/qa`, rerun all 16 Console cases, and save each evaluation. The workbench now shows candidate, eligible, and filtered counts plus the top filter reasons.
