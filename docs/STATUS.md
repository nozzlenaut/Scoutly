# PriceSift current status

_Last updated: July 21, 2026_

This is the living project snapshot. Update this file when production behavior, provider coverage, known issues, or the immediate plan changes. Use the changelog only for history.

## Product position

PriceSift is a **results site**, not a general search site.

It helps someone who already knows what they want get a short list of useful current listings without sorting through wrong models, accessories, damaged items, parts-only junk, misleading variations, and duplicate noise.

Production: https://www.pricesift.app/

## Current release

- Release: v0.6.37 Amazon fallback links and optional ISBN barcode scanning
- Internal repository name: Scoutly
- Deployment: Vercel frontend + Railway backend from `main`
- Storage: PostgreSQL in production, local JSON fallback for development
- Accounts: None required for normal use
- Revenue model: Disclosed outbound affiliate links

## Public category coverage

| Category | Status | Providers | Notes |
|---|---|---|---|
| Cameras | Active | eBay + KEH, Amazon fallback | Catalog matches use eBay + KEH; additional KEH-standardized models stay KEH-only |
| Lenses | Beta | KEH, Amazon fallback | Exact expanded models get Amazon shortcuts; public eBay lens search remains blocked |
| Consoles | Active | eBay, Amazon fallback | Core models with storage, drive, color, and revision variants |
| CPUs | Active | eBay, Amazon fallback | Consumer desktop specification builder with suffix-safe matching |
| GPUs | Active | eBay, Amazon fallback | Exact desktop graphics-card matching |
| RAM | Active | eBay, Amazon fallback | DDR3/DDR4/DDR5 specification builder |
| Books | Beta | eBay, Amazon fallback | Exact ISBN, optional barcode scan, derivative filtering, and collectible separation |
| LEGO | Beta | eBay, Amazon fallback | Exact set number/name with conservative completeness filtering |

Amazon is currently a separate fallback card rather than a ranked PriceSift provider. PriceSift does not display Amazon prices or availability until approved API access is available.

## Validation snapshot

- Automated tests before this release: 235 passing
- v0.6.37 adds an Amazon outbound allowlist and affiliate-tracking regression
- QA cases reviewed: 106
- Pass: 85
- Top-3 only: 3
- Safe no-inventory: 18
- Clear failures: 0
- Camera/lens expansion: 49 latest cases, 45 pass, 2 top-3, 2 no-inventory, 0 fail
- When “US listings only” is active, the optional ZIP travels with the search in temporary memory and each visible eBay card fills in its own delivery estimate. The ZIP is never saved.
- `/cameras` and stable `/cameras/[slug]` pages expose current KEH model inventory and are added to the dynamic sitemap; arbitrary `/search` URLs remain `noindex`.

Tests are treated as data. A failure must be classified as related/blocking, related/non-blocking, unrelated existing, or environment-related before deciding whether to ship.

## First outside product feedback

The first unsolicited feedback arrived on the r/SideProject post four days after publication. The commenter asked about three practical shopping concerns:

1. Condition thresholds and whether a buyer could save a preferred minimum condition.
2. ZIP-specific shipping cost, delivery time, import charges, and regional availability.
3. What happens when a listing sells, becomes confusing, or is unavailable after the PriceSift handoff.

The questions are useful even if the commenter did not fully test the site because they identify the trust gaps a new visitor notices immediately.

Current response and likely approach:

- **Condition:** PriceSift remains used-focused. Explore category-aware condition thresholds rather than one universal scale, then store the buyer's choice locally so it persists across searches.
- **Shipping:** The public lookup is optional, limited to US-only searches and the visible eBay results, and does not persist the ZIP. Missing eBay delivery fields remain an honest “not provided.”
- **Unavailable listings:** Keep live search and manual reporting, then investigate a lightweight pre-click availability recheck. If a listing has ended, remove it and promote the next ranked eligible option instead of leaving the user at a dead end.

## Current observation period

The site should now sit long enough to generate real evidence.

Watch for:

- Completed searches by category
- No-result searches
- Merchant clicks and click-through rate
- Amazon fallback clicks and whether they lead to qualifying sales
- Feedback reports
- Missing products
- Bad matches or useful listings filtered out
- Search flows people start but do not finish
- Public delivery-estimate coverage by category and listing
- ISBN scanner success and browser-support failures

Outreach currently in motion:

- First outside feedback received from the r/SideProject post
- r/Cameras moderator request sent
- r/photography Self-Promotion Sunday draft remains prepared for the next suitable thread

## Known issues and deliberate limits

- Public eBay lens results remain disabled because listing identity and bundle quality are not trustworthy enough yet.
- `/admin/prices` has previously looped or shown `cannot load` after token entry; it is deferred unless price-history administration becomes immediately necessary.
- Delivery dates and shipping methods may be missing for some listings. The public lookup reports that honestly and does not alter ranking.
- KEH-native camera identity depends on KEH’s standardized title. Unmatched models never receive an eBay search until they confidently join the tuned PriceSift catalog.
- Amazon links are tagged fallback searches or exact ISBN-10 product links. They are not price-verified, availability-verified, seller-verified, or ranked with PriceSift listings.
- Used and renewed Amazon links bias the search wording but Amazon may still mix conditions; the card tells shoppers to verify condition and seller.
- ISBN camera scanning depends on the browser's native barcode detector. Unsupported browsers retain manual ISBN entry.
- Traffic is still too small to justify optimizing percentages or adding features based on tiny samples.
- Do not add another category merely because the site is quiet.

## Next three likely moves

1. Observe Amazon fallback clicks, qualifying-sale progress, and whether used/renewed wording reaches useful listings.
2. Observe ISBN scanner success and browser-support errors before adding a heavier cross-browser scanning dependency.
3. Prototype the smallest stale-listing recovery flow: recheck availability before outbound redirect and automatically offer the next ranked option when practical.

## Deliberately deferred

- Amazon price/availability integration until approved API access is available
- Public eBay lenses
- More categories without evidence
- Major homepage redesigns
- Broad deal feeds, trend discovery, or open-ended marketplace search
- Fine-tuning analytics from tiny traffic samples

## Release checklist

1. Start from clean `main`.
2. Review `git status --short` and `git diff --stat`.
3. Run relevant backend tests.
4. Run `npm run build` when frontend files changed.
5. Understand every failure before deciding whether it blocks release.
6. Commit and push manually.
7. Verify Vercel and Railway deploy.
8. Perform a small production smoke test.
9. Run required data syncs.
10. Confirm the working tree is clean, then stop changing things.
