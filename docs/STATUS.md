# PriceSift current status

_Last updated: July 19, 2026_

This is the living project snapshot. Update this file when production behavior, provider coverage, known issues, or the immediate plan changes. Use the changelog only for history.

## Product position

PriceSift is a **results site**, not a general search site.

It helps someone who already knows what they want get a short list of useful current listings without sorting through wrong models, accessories, damaged items, parts-only junk, misleading variations, and duplicate noise.

Production: https://www.pricesift.app/

## Current release

- Release: v0.6.31 stabilization and observation, plus a private shipping QA experiment
- Internal repository name: Scoutly
- Deployment: Vercel frontend + Railway backend from `main`
- Storage: PostgreSQL in production, local JSON fallback for development
- Accounts: None required for normal use
- Revenue model: Disclosed outbound affiliate links

## Public category coverage

| Category | Status | Providers | Notes |
|---|---|---|---|
| Cameras | Active | eBay + KEH | Exact camera bodies; KEH uses confidently matched active catalog models |
| Lenses | Beta | KEH only | Public eBay lens search intentionally blocked |
| Consoles | Active | eBay | Core models with storage, drive, color, and revision variants |
| CPUs | Active | eBay | Consumer desktop specification builder with suffix-safe matching |
| GPUs | Active | eBay | Exact desktop graphics-card matching |
| RAM | Active | eBay | DDR3/DDR4/DDR5 specification builder |
| Books | Beta | eBay | Exact ISBN with derivative-book filtering and collectible separation |
| LEGO | Beta | eBay | Exact set number/name with conservative completeness filtering |

## Validation snapshot

- QA cases reviewed: 106
- Pass: 85
- Top-3 only: 3
- Safe no-inventory: 18
- Clear failures: 0
- Camera/lens expansion: 49 latest cases, 45 pass, 2 top-3, 2 no-inventory, 0 fail
- Private Shipping ZIP Lab added to `/admin/qa` to test buyer-specific deliverability, shipping cost, method/speed, delivery windows, and import-charge coverage before exposing any of it publicly

Tests are treated as data. A failure must be classified as related/blocking, related/non-blocking, unrelated existing, or environment-related before deciding whether to ship.

## First outside product feedback

The first unsolicited feedback arrived on the r/SideProject post four days after publication. The commenter asked about three practical shopping concerns:

1. Condition thresholds and whether a buyer could save a preferred minimum condition.
2. ZIP-specific shipping cost, delivery time, import charges, and regional availability.
3. What happens when a listing sells, becomes confusing, or is unavailable after the PriceSift handoff.

The questions are useful even if the commenter did not fully test the site because they identify the trust gaps a new visitor notices immediately.

Current response and likely approach:

- **Condition:** PriceSift remains used-focused. Explore category-aware condition thresholds rather than one universal scale, then store the buyer's choice locally so it persists across searches.
- **Shipping:** eBay's Browse API supports `deliveryCountry`, `deliveryPostalCode`, and buyer contextual location. Test actual field coverage privately first; only promote ZIP entry publicly if shipping totals and delivery estimates are consistently useful.
- **Unavailable listings:** Keep live search and manual reporting, then investigate a lightweight pre-click availability recheck. If a listing has ended, remove it and promote the next ranked eligible option instead of leaving the user at a dead end.

## Current observation period

The site should now sit long enough to generate real evidence.

Watch for:

- Completed searches by category
- No-result searches
- Merchant clicks and click-through rate
- Feedback reports
- Missing products
- Bad matches or useful listings filtered out
- Search flows people start but do not finish
- Shipping field coverage by category and ZIP in the private lab

Outreach currently in motion:

- First outside feedback received from the r/SideProject post
- r/Cameras moderator request sent
- r/photography Self-Promotion Sunday draft remains prepared for the next suitable thread

## Known issues and deliberate limits

- Public eBay lens results remain disabled because listing identity and bundle quality are not trustworthy enough yet.
- `/admin/prices` has previously looped or shown `cannot load` after token entry; it is deferred unless price-history administration becomes immediately necessary.
- Delivery dates and shipping methods may be missing for some listings even when cost and ZIP deliverability are returned.
- The Shipping ZIP Lab is private and diagnostic; it does not yet save a buyer ZIP or alter public ranking.
- Traffic is still too small to justify optimizing percentages or adding features based on tiny samples.
- Do not add another category merely because the site is quiet.

## Next three likely moves

1. Run Shipping ZIP Lab tests across cameras, GPUs, consoles, books, and a few domestic/international listings; record how often cost, method, dates, and import charges are returned.
2. Review the first real searches, no-results, clicks, and feedback as a group before deciding whether ZIP-based shipping or saved condition thresholds deserve the next public release.
3. Prototype the smallest stale-listing recovery flow: recheck availability before outbound redirect and automatically offer the next ranked option when practical.

## Deliberately deferred

- Public ZIP collection until the private shipping tests show reliable value
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
