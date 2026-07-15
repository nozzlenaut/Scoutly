# PriceSift v0.6.23

This release promotes the exact-ISBN Books search into the public beta.

## Books beta

- Search by ISBN-10 or ISBN-13 from the normal PriceSift category picker.
- Uses exact eBay GTIN/ISBN lookup with ISBN-13-first and ISBN-10 fallback behavior.
- Shows up to three standard used Buy It Now copies.
- Filters study guides, summaries, workbooks, and companion products.
- Separates signed, deluxe, limited, and collectible copies from standard price comparison.
- Warns about seller-supplied edition-year wording without rejecting otherwise exact matches.
- Keeps `/admin/books` available for detailed diagnostics.

## Validation

- Full backend test suite passes.
- Production frontend build passes.
