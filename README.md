# Scoutly v0.5.6

Scoutly is a cleaner exact-item eBay search tool for used products. It resolves a search to a catalog item, filters obvious broken/partial/accessory listings, and returns up to three Buy It Now options while auctions load afterward.

## Current category status

- **Cameras:** Active
- **GPUs:** Lab, currently reliable in testing
- **Consoles:** Lab, active testing
- **LEGO:** Lab / early set-number prototype
- **Lenses:** Paused

## Included in v0.5.6

- Repeat-search loading-state fix
- Stricter Nintendo Switch/OLED completeness checks
- Seller-history sentinel cleanup
- Sony A1 II catalog entry and strict generation matching
- Improved selected badge contrast
- Consistent affiliate-link wording
- Resolved/unresolved auction empty-state copy

See `README-v056.md` for details.

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
