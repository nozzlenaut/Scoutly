# PriceSift v0.6.17 — KEH shadow feed

This release adds a private KEH Camera inventory test through the approved Awin product feed. KEH remains completely excluded from public search results, ranking, QA rates, and price history.

## Added

- Private `/admin/keh` dashboard.
- Automatic Awin CSV, gzip, and zip feed parsing.
- KEH camera-body scope filtering using the structured category path.
- Awin tracked links, current price, image, stock flags, MPN/UPC, and KEH condition-grade parsing.
- Pilot matching against the 12 camera QA products plus Fujifilm X-T2 and Canon EOS M200 from the supplied sample.
- Manual admin sync and Railway cron-compatible sync runner.
- PostgreSQL tables with local JSON fallback.
- Homepage copy: `Free to use. Always.`

## Railway variables

```env
AWIN_KEH_FEED_URL=<private Create-a-Feed URL>
KEH_FEED_ENABLED=true
KEH_PUBLIC_RESULTS=false
```

Do not add the feed URL to Vercel or Git. It belongs on the Railway backend only.

## First test

1. Deploy the backend and frontend.
2. Add the three variables above in Railway.
3. Open `/admin/keh?token=<SCOUTLY_ADMIN_TOKEN>`.
4. Click **Sync KEH now**.
5. Review matched, ambiguous, and unmatched rows.

## Optional Railway cron

Create a Railway cron service from the same repository with the backend as its root directory.

Command:

```bash
python -m app.services.keh_sync_runner
```

Schedule:

```text
0 */6 * * *
```

The cron service needs the same `DATABASE_URL`, `AWIN_KEH_FEED_URL`, and KEH flags as the API service.

## Current limitation

The current PriceSift camera catalog contains camera bodies only. The feed parser recognizes interchangeable lenses, but public or shadow matching for lenses should wait until exact lens catalog records exist.
