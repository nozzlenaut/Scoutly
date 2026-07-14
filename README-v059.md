# Scoutly v0.5.9 / PriceSift result-quality cleanup

This release keeps Scoutly as the internal project/repository name and improves PriceSift result interaction, search isolation, and marketplace risk filtering.

## Included

- Listing images and titles now open the same tracked affiliate outbound link as the View deal/View auction button.
- Every submitted search uses a full page navigation so previous Buy It Now or auction results cannot append to the new query.
- Rejects eBay `SELLER_DEFINED_VARIATIONS` groups for consoles and GPUs, preventing cheap accessory/lower-model variations from supplying the displayed price.
- Rejects multi-model GPU titles such as RTX A3000/A4000/A5000 variation spam.
- Adds GPU rejection patterns for GPU core/chip-only, shell-only, no-heatsink/no-cooler, and box-and-insert-only listings.
- Adds camera service-manual and parts-list rejection patterns.
- Adds Nintendo handheld cleanup for pouches, game/manual listings, charger-only listings, and seller-pick/choose-option variation wording while allowing complete systems that include a charger.
- Temporarily pauses Wii U search until complete console + GamePad rules are defined.

## Catalog

- Cameras: 141 active
- GPUs: 177 active
- Consoles: 18 retained / 16 active (Switch 2 and Wii U paused)
- LEGO: 395 active
- Lenses: 26 retained (hidden in the public UI)
- Total catalog records: 757

## Validation

- Backend: 116 tests passed
- Frontend: Next.js production build passed

## Deployment

No Railway, PostgreSQL, Vercel-domain, or environment-variable changes are required.
