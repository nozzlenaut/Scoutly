# Scoutly v0.5.8

Scoutly is a cleaner exact-item eBay search tool for used products. It resolves a search to a catalog item, filters obvious broken/partial/accessory listings, and returns up to three Buy It Now options while auctions load afterward.

## Current category status

- **Cameras:** Active
- **GPUs:** Lab, currently reliable in testing
- **Consoles:** Lab, active testing
- **LEGO:** Lab / early set-number prototype
- **Lenses:** Paused

## Included in v0.5.8

- Public-facing PriceSift branding for `www.pricesift.app`
- Production metadata, favicon, manifest, robots file, and sitemap
- Standalone title-ending `READ` risk rejection
- LEGO catalog expanded to 395 sets
- Internal Scoutly repository, package, database, and affiliate identifiers retained

See `README-v058.md` for details.

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
