# Scoutly v0.6.12 / Cross-category quality cleanup

Scoutly keeps the six-category foundation from v0.6.11 and applies the seven focused listing-quality fixes found during the first complete 88-case live QA sweep.

## Included

- Rejects faulty and partially functional electronics, including titles such as `Only DisplayPort Works`, `Only HDMI Works`, and `One Port Works`.
- Rejects exact-speed RAM listings that advertise multiple conflicting speeds, including mixed `2666 / 3200` kits.
- Strengthens LEGO identity matching so an exact set number must also agree meaningfully with the canonical set name.
- Rejects LEGO ghost/sub-build listings, instruction-manual sets, and individual brick/plate/tile listings with part dimensions or small quantities.
- Keeps legitimate complete LEGO sets eligible, including shortened but recognizable set-name titles.
- Updates the QA dashboard to separate:
  - usable top-three quality when eligible inventory exists;
  - safe no-inventory outcomes; and
  - overall usable outcomes including no-inventory cases.
- Preserves all 88 QA case IDs and existing saved evaluation history.
- All 167 backend tests pass, all 88 QA queries resolve correctly, and the Next.js production build completes successfully.

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

Open `/admin/qa` to rerun the seven affected cases first, then use the full 88-case suite for periodic regression passes.
