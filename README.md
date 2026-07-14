# Scoutly v0.6.7 / PriceSift search QA workbench

Scoutly remains the internal project name. PriceSift uses category-specific search styles: direct exact-item search for Cameras, GPUs, Consoles, and LEGO; a specification builder for RAM.

## Included

- Private search QA workbench at `/admin/qa`.
- 36 repeatable starter cases for Consoles and LEGO.
- Live expected-versus-resolved product comparison.
- Top-three listing inspection with Pass, Top-3 only, Fail, and No inventory outcomes.
- Issue tags, notes, attempt counts, and persistent evaluation history.
- PostgreSQL production storage with local JSON fallback.
- Existing analytics dashboard now links directly to the QA workbench.
- All 152 backend tests pass and the Next.js production build completes successfully.

The QA workbench uses the existing `SCOUTLY_ADMIN_TOKEN`. No Railway, PostgreSQL, Vercel, domain, or environment changes are required.

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

Open `/admin`, enter the existing admin token, and select **Open search QA**.
