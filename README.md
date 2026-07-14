# Scoutly v0.6.1

Scoutly is the internal project name for PriceSift, a cleaner exact-item eBay search tool for used products.

## Current category status

- **Cameras:** Active — direct exact-model search
- **Consoles:** Active — guided brand/family/model builder
- **GPUs:** Active — direct exact-model search
- **RAM:** Active — strict DDR3/DDR4/DDR5 specification builder
- **LEGO:** Beta — exact set name or set-number search
- **Lenses:** Paused

## Included in v0.6.1

- Console builder with family-level results and optional refinements
- RAM promoted to Active
- Lab renamed to Beta
- Status-first, alphabetical category ordering
- Empty direct-search fields with category-specific placeholders
- DDR3L compatibility warnings
- Expanded LEGO packaging, incomplete, unauthentic, and bulk/lot exclusions

See `README-v061.md` for details.

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
