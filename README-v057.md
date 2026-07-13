# Scoutly v0.5.7 — Persistent storage and protected admin

This update moves Scoutly's testing data from temporary JSON files to PostgreSQL whenever `DATABASE_URL` is configured.

## Persisted data

- manual/live filter rules
- bad-result reports
- outbound click events
- filtered-listing debug records

The API still uses temporary JSON files for local development when `DATABASE_URL` is not present.

## Admin protection

`SCOUTLY_ADMIN_TOKEN` is now required for all `/api/analytics/*` endpoints. Visiting `/admin` without a token shows a token entry screen instead of exposing analytics.

## Railway variables

Backend service:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
SCOUTLY_ADMIN_TOKEN=your_private_token
```

The PostgreSQL service may display an attached volume named `postgres-volume`; the application only needs the resolved `DATABASE_URL` variable.

## After deployment

1. Open `https://scoutly-production-f472.up.railway.app/health`.
2. Confirm the response shows `"backend":"postgresql"` and `"connected":true`.
3. Open `https://scoutly-sandy.vercel.app/admin`.
4. Enter the private admin token.
5. Confirm the dashboard says **PostgreSQL connected**.
6. Add a temporary live filter rule, reload `/admin`, and confirm it remains.

Existing temporary click/report logs may start fresh after this deployment. New data persists across later deployments.

## Retention

- bad-result reports still expire after 72 hours
- outbound clicks retain up to 50,000 events or 180 days
- filtered-listing debug events retain up to 20,000 events or 45 days
- manual rules retain the latest 500 rules

## Validation

- 107 backend tests passed
- frontend production build passed
- catalog remains at 680 products
