# Scoutly v0.6.5 / PriceSift precision pass

Scoutly remains the internal project name. This patch applies the first precision release based on cross-category testing of Cameras, GPUs, Consoles, RAM, and LEGO.

## Included

### PlayStation Digital Edition

- Preserves `Digital Edition` through structured-console parsing and product resolution.
- Keeps `Digital Edition` in the resolved result heading and marketplace query.
- Rejects Disc Edition listings from Digital Edition searches.
- Keeps original PS5, PS5 Slim, and PS5 Pro identities separate.

### LEGO full-set enforcement

- Rejects missing, incomplete, near-complete, almost-complete, and mostly-complete listings.
- Rejects completeness percentages below 100%.
- Rejects taxi-only, driver/minifigure-only, fence, barrier, and other component listings.
- Requires the selected set number in result titles.
- Does not silently resolve an unknown or reissue set number to a different catalog set.
- Allows positive wording such as `100% complete` and `no missing pieces`.

### Older consoles

- Rejects base shells, shell-only listings, mid-frames, heat sinks, optical/disc drives, disc-only games, manuals/box-only packages, MixAmp, and headset accessories.
- Requires positive hardware evidence such as `console`, `system`, `handheld`, `unit`, or a supported authoritative model number for PS4, Xbox One, and Nintendo 3DS XL searches.

### GPUs

- Enforces exact conflicts for XT/non-XT, Super, Ti, and Ti Super variants.
- Rejects explicit failure language including `parts`, `failed`, `ports failed`, and `dead port`.

### RAM

- Rejects mixed-brand kits when a specific brand is selected, including combinations such as SK Hynix plus A-Tech.

### Review warnings

- `read`, `read desc`, `read description`, `see description`, and `please read` now produce a visible `Seller asks you to review the description` warning when the product otherwise matches.
- Explicit defects and parts language still cause rejection.

No Railway, PostgreSQL, Vercel, domain, or environment changes are required.

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
