# Scoutly v0.6.10 / Switch completeness and result deduplication

Scoutly keeps the grouped core-console catalog and console quality filters from v0.6.9. This release closes the remaining standard Nintendo Switch QA failure and prevents repeated marketplace titles from filling the buyer-facing top three.

## Included

- Keeps all 16 core console models and grouped storage/color/drive variants unchanged.
- Requires standard Nintendo Switch listings to explicitly claim a complete/full system or show both Joy-Con controls and a dock.
- Rejects bare `HAC-001` / `tested working` tablet-style titles that provide no evidence of a complete V1/V2 system.
- Preserves valid complete-system wording such as `complete system`, `console bundle`, and `with Joy-Con and Dock`.
- Deduplicates final fixed-price and auction results by marketplace URL and normalized visible title.
- Keeps the highest-quality listing when separate item IDs use the same title.
- Adds QA diagnostics showing how many duplicate listings were collapsed.
- Adds regression coverage for the exact standard Switch failure and duplicate-title top-three behavior.
- All 156 backend tests pass and the Next.js production build completes successfully.

No database migration or new environment variable is required. Existing QA attempts remain saved; rerun and save the same 16 Console cases for the final comparable console pass.

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

Open `/admin/qa`, rerun all 16 Console cases, and save each evaluation. The workbench now shows candidate, eligible, filtered, and duplicate-collapsed counts.
