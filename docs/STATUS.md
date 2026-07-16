# PriceSift current status

_Last updated: July 16, 2026_

This is the living project snapshot. Update this file when production behavior, provider coverage, known issues, or the immediate plan changes. Use the changelog only for history.

## Product position

PriceSift is a **results site**, not a general search site.

It helps someone who already knows what they want get a short list of useful current listings without sorting through wrong models, accessories, damaged items, parts-only junk, misleading variations, and duplicate noise.

Production: https://www.pricesift.app/

## Current release

- Release: v0.6.31 stabilization and housekeeping
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

Tests are treated as data. A failure must be classified as related/blocking, related/non-blocking, unrelated existing, or environment-related before deciding whether to ship.

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

Outreach currently in motion:

- r/Cameras moderator request sent
- r/photography Self-Promotion Sunday draft saved
- Reminder set for Sunday, July 19, 2026 at 8:00 AM Eastern

## Known issues and deliberate limits

- Public eBay lens results remain disabled because listing identity and bundle quality are not trustworthy enough yet.
- `/admin/prices` has previously looped or shown `cannot load` after token entry; it is deferred unless price-history administration becomes immediately necessary.
- Traffic is still too small to justify optimizing percentages or adding features based on tiny samples.
- Do not add another category merely because the site is quiet.

## Next three likely moves

1. Respond to moderator feedback and post in the Sunday promotion thread.
2. Review the first real searches, no-results, clicks, and feedback as a group.
3. Ship one small evidence-based batch: matching fixes, missing catalog items, one usability improvement, or one outreach experiment.

## Deliberately deferred

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
