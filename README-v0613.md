# Scoutly v0.6.13 / Stable QA baseline

Scoutly keeps the six-category foundation and closes the final known bad-first pattern from the 88-case QA sweep.

## Included

- Rejects LEGO PAC-MAN Arcade `10323` listings that sell named ghost/display sub-builds such as Blinky, Clyde, Pinky, or Inky without clearly identifying the full arcade machine.
- Keeps genuine arcade-machine/cabinet listings and complete sets eligible, including complete sets that mention the included ghosts.
- Preserves all 88 QA case IDs and saved evaluation history.
- Treats the current 88-case matrix as the stable periodic regression baseline.
- All 168 backend tests pass and the Next.js production build completes successfully.

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

Open `/admin/qa` to rerun PAC-MAN first. After that, use the unchanged 88-case suite for periodic regression checks rather than rerunning it after every unrelated feature change.
