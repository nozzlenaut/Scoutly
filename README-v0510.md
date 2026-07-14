# Scoutly v0.5.10 / PriceSift consistency and trust cleanup

This release keeps Scoutly as the internal project/repository name and improves PriceSift search consistency, result transparency, and filtering.

## Included

- Rejects LEGO packaging-only listings such as `Empty outer box`, `Inner Boxes Only`, and numbered inner-box variations.
- Clears old result cards immediately when a search or category change begins.
- Opens a clean category page when changing categories from a results page, preventing old-category cards from remaining visible.
- Shows autocomplete consistently for exact and partial queries across Cameras, GPUs, Consoles, and LEGO.
- Clarifies that catalog suggestions are product matches while raw-text searching remains supported.
- Keeps a bare `RTX 3080` unresolved because 10GB and 12GB variants exist, then offers both exact variants.
- Renames result resolution wording to `Product match confidence`.
- Adds separate automated listing-check status to every result card.
- Allows legitimate console bundles with games or extras, labels them, and ranks equivalent clean-console listings above them.
- Strengthens low-feedback and low-rating seller demotion.
- Changes displayed total wording to `Item + shipping` / `Bid + shipping` and notes that taxes or import charges may apply.
- Distinguishes no active inventory from inventory that PriceSift found but filtered out.
- Improves secondary text contrast while retaining the existing dark/cyan design.

## Validation

- Backend: 120 tests passed
- Frontend: Next.js production build passed
- Catalog records: 757

## Deployment

No Railway, PostgreSQL, Vercel, domain, or environment-variable changes are required.
