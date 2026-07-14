# PriceSift v0.6.15 / Public beta and sharing update

This release combines the queued listing-quality fixes with the public-beta flow needed for tester recruitment.

## Included

- Fixes the `/admin/prices` page by loading the price overview client-side with visible retry/error states instead of failing the entire server-rendered page.
- Rejects GPU listings with clear cooling defects such as defective/broken/non-working fans, clicking or grinding fans, fan noise, and overheating while allowing explicitly negated phrases such as `no fan noise`.
- Keeps PlayStation console catalog records grouped by core model, but honors explicit typed `Digital Edition` and `Disc Edition` qualifiers during provider search and listing filtering.
- Labels console result scope clearly: broad model searches show all variants, while explicit edition searches state that results are narrowed.
- Adds universal visible warnings and ranking penalties for `read`, `read description`, `read desc`, `see description`, and `please read` title language without automatically rejecting the listing.
- Adds a buyer-facing **Share search** control using the native share sheet when available and clipboard fallback otherwise. Search URLs retain category/query parameters and are directly shareable.
- Marks PriceSift clearly as a **Public Beta** on the homepage.
- Explains that no signup is required and tells testers how to participate.
- Adds `/feedback` with a general beta-feedback form for bad results, missing products, usability problems, feature ideas, and general comments.
- Stores beta feedback in PostgreSQL with local JSON fallback and displays it in the private admin dashboard.
- Keeps listing-specific **Report bad result** controls for the fastest correction path.

## Storage

PostgreSQL automatically creates `scoutly_beta_feedback`. Local development falls back to `beta_feedback.json` under `SCOUTLY_DATA_DIR` or `/tmp/scoutly`.

No new environment variables are required.

## Validation

- 179 backend tests pass.
- The existing 88-case cross-category QA resolution baseline remains covered.
- The Next.js production build passes, including `/feedback` and `/admin/prices`.
