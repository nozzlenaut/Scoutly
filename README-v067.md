# Scoutly v0.6.7 / Search QA workbench

- Adds a private `/admin/qa` workbench for repeatable live-search testing.
- Seeds 36 high-value console and LEGO test cases covering exact models, aliases, hardware codes, duplicate set names, and common listing-quality traps.
- Compares the expected catalog item with Scoutly's resolved product and confidence.
- Shows the top three live Buy It Now results without routing QA clicks through normal outbound analytics.
- Records Pass, Top-3 only, Fail, or No inventory outcomes with issue tags and notes.
- Preserves evaluation history and attempt counts using PostgreSQL in production or JSON file fallback locally.
- Adds aggregate tested/pass/fail/top-three metrics and category/status filters.
- Adds three QA backend tests; the full backend suite now contains 152 passing tests.

No new environment variables are required. The workbench uses the existing `SCOUTLY_ADMIN_TOKEN` and `DATABASE_URL` configuration.
