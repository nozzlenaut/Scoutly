# Scoutly v0.5.10

Scoutly is the internal project name for PriceSift, a cleaner exact-item eBay search tool for used products. It resolves searches to catalog items when possible, filters obvious broken/partial/accessory listings, and returns up to three Buy It Now options while auctions load afterward.

## Current category status

- **Cameras:** Active
- **GPUs:** Lab, currently reliable in testing
- **Consoles:** Lab, active testing
- **LEGO:** Lab / exact set-number prototype
- **Lenses:** Paused

## Included in v0.5.10

- LEGO packaging-only regression filtering
- Clean category/search transitions with stale cards hidden immediately
- Consistent autocomplete behavior across active categories
- Ambiguous GPU variant handling for RTX 3080 10GB versus 12GB
- Separate product-match and listing-check signals
- Bundle labeling and ranking refinement
- Stronger seller-risk ranking
- Clearer item-plus-shipping and inventory-filtered wording
- Improved secondary text contrast

See `README-v0510.md` for details.

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
