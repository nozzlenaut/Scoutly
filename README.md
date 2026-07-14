# Scoutly v0.6.4 / PriceSift Nintendo Switch Standard search fix

Scoutly remains the internal project name. This patch fixes the Console builder's Standard Nintendo Switch option, which previously resolved to a single marketplace query for `Nintendo Switch V1/V2` and could return no results.

## Included

- `Standard Switch (V1/V2)` now runs separate searches for:
  - Nintendo Switch V1
  - Nintendo Switch V2
  - HAC-001
  - HAC-001(-01)
  - Nintendo Switch Standard
  - generic Nintendo Switch console listings
- Valid results are merged and deduplicated before ranking.
- Standard Switch titles can qualify through V1/V2/HAC/Standard or normal console/system identity.
- OLED, Lite, Switch 2, tablet-only, dock-only, Joy-Con-only, game-only, and accessory listings remain excluded.
- The frontend label now reads `Standard Switch (V1/V2)`.

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
