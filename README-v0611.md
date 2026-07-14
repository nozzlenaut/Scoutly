# Scoutly v0.6.11 / CPU builder and full-category QA

Scoutly now includes consumer desktop CPUs as an active exact-model category and expands the private QA workbench across every searchable category.

## Included

- Adds a guided CPU builder: manufacturer → socket → generation/series → exact model.
- Includes 161 consumer desktop CPUs across AMD AM4/AM5 and Intel LGA1151, LGA1200, LGA1700, and LGA1851.
- Keeps CPU suffixes exact: `12700K`, `12700KF`, `5800X`, and `5800X3D` are separate products.
- Accepts CPU-only, OEM/tray, and boxed processors.
- Rejects motherboard/full-system bundles, accessories-only listings, multi-CPU lots, mobile/server conflicts, engineering samples, and damaged processors.
- Adds eBay US Computer Processors category filtering.
- Expands `/admin/qa` from Console/LEGO-only coverage to 88 cases across Cameras, GPUs, RAM, CPUs, Consoles, and LEGO.
- Keeps all existing Console and LEGO QA case IDs so saved evaluation history remains attached.
- Makes QA category filters dynamic, so future searchable categories appear automatically.
- All 163 backend tests pass and the Next.js production build completes successfully.

No database migration or new environment variable is required.

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

Open `/admin/qa` to run the full 88-case suite or filter down to a single category.
