# Scoutly v0.5.1 Performance pass

This update makes normal searches faster by keeping auctions optional.

- Normal search now loads only Buy It Now listings by default.
- The search page still shows up to 3 Buy It Now options.
- Auctions are now loaded only after clicking **View ending-soon auctions**.
- Auction searches still show up to 3 ending-soon comparisons when requested.
- eBay fixed-price candidate limit reduced from 50 to 35.
- eBay auction candidate limit reduced from 50 to 25.
- Result cards are now laid out as a desktop-friendly grid while staying single-column on mobile.
- Result images lazy-load to reduce mobile/desktop rendering work.

Validation:

- Backend tests: 85 passed.
- Frontend build was attempted but could not run in this sandbox because `node_modules` is not installed (`next: not found`).
