# Scoutly v0.6.0

Scoutly is the internal project name for PriceSift, a cleaner exact-item eBay search tool for used products. It resolves searches to catalog items when possible, filters obvious broken/partial/accessory listings, and returns up to three Buy It Now options while auctions load afterward.

## Current category status

- **Cameras:** Active
- **GPUs:** Active
- **Consoles:** Active
- **RAM:** Lab / specification-builder preview
- **LEGO:** Lab / exact set-number prototype
- **Lenses:** Paused

## Included in v0.6.0

- Reusable specification-builder foundation with the first RAM flow
- DDR3, DDR4, and DDR5 desktop/laptop memory-kit searches
- Strict unclear-kit, conflicting-spec, ECC/server, and variation-listing rejection
- Consumer GPU form-factor cleanup for passive/server and external GPU variants
- Stronger LEGO packaging-only and EMPTY-typo filtering
- Transparent empty-result explanations with a broader tracked eBay search option

See `README-v060.md` for details.

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
