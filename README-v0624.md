# PriceSift v0.6.24

This release tightens public Books matching and rebuilds the price-history admin page around the same proven server-rendered API pattern as the working KEH dashboard.

## Books cleanup

- Strengthens title-consensus checks for common-word titles such as *Atomic Habits*.
- Requires two dominant title tokens when a result set has multiple strong identity words.
- Separates multi-book lots, bundles, and sets from normal single-copy price comparisons.
- Shows bundles in a clearly labeled alternative section instead of allowing them into the default top three.
- Keeps collectible separation and edition-year cautions unchanged.

## Price-history admin

- Loads the initial price overview server-side before rendering, matching the working `/admin/keh` pattern.
- Removes the price page's dependency on the browser-to-Vercel proxy for normal loading and refresh actions.
- Shows the actual backend error at the token gate if the Railway price endpoint still rejects or fails.
- Keeps the existing collector and price-history storage unchanged.

## Validation

- 208 backend tests pass.
- Production frontend build passes.
- Local end-to-end smoke test confirmed `/admin/prices?token=...` renders the price dashboard and reads the backend overview.
