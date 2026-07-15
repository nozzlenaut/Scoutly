# PriceSift v0.6.27

This release corrects light-analytics click attribution.

## Analytics cleanup

- Counts a click toward search analytics only when it can be linked to a matching public search that occurred before the click.
- Excludes older affiliate click history from search-to-click rates, category click totals, and provider click totals.
- Shows older/unlinked clicks separately so historical records remain visible without distorting current usage.
- Keeps the existing privacy model: no IP addresses, cookies, accounts, or personal identifiers.

## Deployment

No new environment variables or database changes are required.

## Validation

- 216 backend tests pass.
- Production Next.js build passes.
