# PriceSift v0.6.25

This release fixes the deployed `/admin/prices` crash caused by PostgreSQL `NUMERIC` values reaching the Next.js page as decimal strings.

## Price-history admin fix

- Converts PostgreSQL decimal price fields to JSON numbers in the backend.
- Defensively normalizes number-like values in the frontend before formatting them.
- Prevents `.toFixed()` from crashing the server-rendered admin page.
- Keeps the v0.6.24 Books matching and bundle cleanup unchanged.

## Validation

- Backend regression suite passes.
- Production frontend build passes.
- Adds a regression for decimal price serialization.
