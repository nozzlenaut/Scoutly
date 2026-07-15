# PriceSift v0.6.26

This release adds lightweight, privacy-friendly usage analytics and an optional US-located eBay results filter.

## Light analytics

- Records public searches, resolved catalog product/ISBN, result availability, providers shown, candidate/filter counts, and outbound listing clicks.
- Does not store IP addresses, accounts, cookies, user-agent profiles, or personal identifiers.
- Adds 7-day, 30-day, and 90-day views to `/admin`.
- Shows category usage, no-result rates, popular searches, provider clicks, approximate search-to-click rate, and US-only adoption.
- Includes **Copy summary** and **Copy full JSON** buttons so the output can be pasted into ChatGPT for interpretation.
- Existing eBay and KEH outbound click tracking feeds the same digest.

## US listings only

- Adds a toggle beside Search and beneath the RAM/CPU builders.
- Filters eBay Buy It Now listings, ending-soon auctions, and Books ISBN searches to items physically located in the United States.
- Leaves KEH results unchanged.
- Defaults off and remembers the user's browser preference.
- Adds `us_only=1` to search URLs when active, so shared searches preserve the setting.
- US-only searches do not overwrite broad-market price-history snapshots.

## Deployment

No new environment variables are required. Railway will create the new `scoutly_search_events` table automatically on restart.

## Validation

- 215 backend tests pass.
- Production Next.js build passes.
