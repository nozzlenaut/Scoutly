# Scoutly v0.6.0 / PriceSift RAM builder preview

This release keeps Scoutly as the internal project name and introduces PriceSift's first reusable specification-builder flow.

## Included

- Adds a RAM Lab category with a wide-to-narrow builder:
  - Desktop or laptop
  - DDR3, DDR4, or DDR5
  - Total capacity
  - Exact stick configuration
  - Optional speed
  - Optional brand
- Creates a structured RAM product at search time rather than requiring a giant static product catalog.
- Requires positive listing evidence for DDR generation, form factor, total capacity, and stick configuration.
- Automatically rejects conflicting DDR generations and desktop/laptop form factors.
- Rejects unclear kit configurations, ECC, RDIMM/LRDIMM, registered/server memory, mixed lots, dummy RAM, accessory-only listings, and seller-defined variation price traps.
- Adds eBay's Computer Memory (RAM) category restriction for RAM searches.
- Promotes Cameras, GPUs, and Consoles to Active status. RAM and LEGO remain Lab categories; Lenses remain paused.
- Rejects passive/server and eGPU/external Gaming Box variants for normal consumer desktop GPU searches.
- Expands LEGO packaging filtering to cover outer/inner boxes, packaging-only listings, and one-edit EMPTY typos such as `EMPRY` when paired with packaging language.
- Adds `salvage` and `no power` to the global broken/incomplete rejection terms.
- Adds a transparent empty-state explanation and a tracked link to broader Buy It Now results on eBay when PriceSift returns no safe fixed-price listings.

## Validation

- Backend: 129 tests passed
- Frontend: Next.js production build passed
- Static catalog records: 757
- RAM configurations: generated dynamically by the specification builder

## Deployment

No Railway, PostgreSQL, Vercel, domain, or environment-variable changes are required.
