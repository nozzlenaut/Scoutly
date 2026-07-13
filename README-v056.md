# Scoutly v0.5.6 — Regression and trust fixes

This update addresses the latest production test report without changing the core search flow.

- Fixes repeat searches leaving the Search button stuck on `Searching…`.
- Requires positive completeness clues for full-size Nintendo Switch/OLED listings.
- Treats eBay seller sentinel values such as `0% / -1 feedback` as unavailable history.
- Adds Sony A1 II / ILCE-1M2 to the camera catalog.
- Prevents generation-specific queries such as `Sony A1 II` from falling back to the prior generation.
- Makes GPU modifier and storage clues stricter when the user types them explicitly.
- Improves selected Active/Lab badge contrast.
- Uses “affiliate links” consistently on the homepage.
- Makes auction empty-state copy distinguish resolved products from unmatched queries.
- Confirms common LEGO entries 10333 Barad-dûr and 75313 UCS AT-AT resolve by number/name.

Validation:

- Backend tests: 103 passed.
- Frontend production build: passed.
- Catalog total: 680 products (141 cameras, 177 GPUs, 318 LEGO, 18 consoles, 26 retained lenses).
