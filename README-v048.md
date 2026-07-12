# Scoutly v0.4.8 — Live filter rules

This update adds admin-managed filter rules so bad marketplace title patterns can be blocked without a new code deploy.

## Highlights

- Admin panel section for live filter rules.
- Add/delete rejection phrases from `/admin`.
- Scope rules globally, by category, or by exact product ID.
- Add exception phrases such as `no problems` when blocking risky words like `problem`.
- Backend endpoints for manual rules under `/api/analytics/filter-rules`.
- LEGO now requires exact set number matches when the catalog item has a set number.
- LEGO rejects base-only / towers-only / build-only partials.
- GPU searches reject problem/issue listings but keep `no problems` / `no issues` safe context.

## Suggested manual rule examples

- Category `lego`, phrase `base only`
- Category `lego`, phrase `main build only`
- Category `gpus`, phrase `problem`, unless `no problem, no problems`
- Category `gpus`, phrase `issue`, unless `no issue, no issues`

## Apply

```bash
cd ~/Scoutly
git add -A
git commit -m "Add live filter rules"
git push
```
