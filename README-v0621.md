# PriceSift v0.6.21

## Private Books ISBN lab

- Adds `/admin/books` as a private ISBN-first Books test page.
- Uses exact eBay GTIN/ISBN catalog search rather than loose title keywords.
- Accepts ISBN-10 or ISBN-13 and automatically tests the equivalent format when available.
- Rejects invalid ISBN check digits before making any marketplace request.
- Requests used Buy It Now inventory only and defensively rejects non-used conditions.
- Deduplicates repeated marketplace item URLs while preserving separate used copies from different sellers.
- Shows the intended top three delivered-price results plus expandable additional eligible listings.
- Keeps Books completely private and out of public categories, QA, price history, and navigation.
- Adds an admin-dashboard shortcut to the Books lab.
- Adds five focused regressions, bringing the backend suite to 198 passing tests.
