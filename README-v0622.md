# PriceSift v0.6.22

This patch tightens the private Books ISBN lab after some valid ISBNs produced broad, unrelated eBay catalog results.

## Books lab changes

- ISBN-13 is queried first whenever available.
- ISBN-10 is used only as a fallback when the primary query produces no trustworthy used results.
- Large result sets must contain a coherent shared title identity; unrelated catalog results fail safely.
- The admin lab shows each ISBN attempt, candidate count, verified count, rejection reasons, shared identity tokens, and whether fallback was used.
- Books remains private and does not affect public PriceSift categories.

## Validation

- Full backend test suite passes.
- Production frontend build passes.
