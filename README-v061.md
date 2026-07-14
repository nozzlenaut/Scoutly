# Scoutly v0.6.1 / PriceSift console builder and category polish

This release keeps Scoutly as the internal repository/project name while expanding the public PriceSift search experience.

## Included

- Adds the first Console builder:
  - Brand
  - Family / generation
  - Results at the family level
  - Optional model, storage, and edition/drive refinements
- Family-level searches intentionally support multiple valid models, such as Xbox Series X and Series S, when the user does not narrow further.
- Console refinements update the search after each selection.
- Keeps Switch 2 and Wii U paused.
- Marks RAM as Active after successful structured-search testing.
- Renames Lab status to Beta and keeps LEGO in Beta.
- Sorts searchable categories by status, then alphabetically.
- Removes example autofill from fresh direct-search categories.
- Adds category-specific placeholder text:
  - Cameras: Search by camera model
  - GPUs: Search by GPU model
  - LEGO: Search by set name or set number
- Adds DDR3L compatibility warnings for RAM searches and listings.
- Expands LEGO exclusions for packaging-only, instructions-only, missing-minifigure, unauthentic/compatible-brick, loose-brick, lot, and bulk listings.

## Validation

- Backend: 134 tests passed
- Frontend: Next.js production build passed
- Static catalog records: 757

## Deployment

No Railway, PostgreSQL, Vercel, domain, or environment-variable changes are required.
