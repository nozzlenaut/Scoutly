# Scoutly v0.5.9

Scoutly is a cleaner exact-item eBay search tool for used products. It resolves a search to a catalog item, filters obvious broken/partial/accessory listings, and returns up to three Buy It Now options while auctions load afterward.

## Current category status

- **Cameras:** Active
- **GPUs:** Lab, currently reliable in testing
- **Consoles:** Lab, active testing
- **LEGO:** Lab / early set-number prototype
- **Lenses:** Paused

## Included in v0.5.9

- Clickable listing images and titles using the tracked outbound link
- Full page navigation for each new search to prevent stale result merging
- Seller-defined variation-group rejection for consoles and GPUs
- Multi-model GPU and reported accessory/part cleanup
- Nintendo handheld filtering improvements
- Wii U temporarily paused

See `README-v059.md` for details.

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
