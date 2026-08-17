# PriceSift automated Shorts

This folder is intentionally isolated from the production PriceSift frontend/backend runtime.

## Daily behavior

The GitHub Actions workflow checks around 9:10 AM America/Detroit time.

1. Read current deterministic PriceSift market signals.
2. Read recent PriceSift YouTube posts from Buffer.
3. Do nothing if there is no genuinely video-worthy signal.
4. Enforce one generated draft per Eastern calendar day.
5. Never select the same product as the previous published Short.
6. Enforce a 30-day cooldown for products that were actually published.
7. Penalize recently repeated story types and categories.
8. Generate a 1080x1920 Short with Kokoro narration at 1.25x speed.
9. Validate duration, dimensions, and audio.
10. Upload the MP4 to a stable public Cloudflare R2 URL.
11. Create a YouTube draft in Buffer with a noon Eastern target time.

A Buffer draft never publishes automatically. It must be explicitly scheduled/approved in Buffer.

## Story types

Current reusable story archetypes:

- price spike with a cheaper clean floor
- price drop
- plain price spike
- hidden bargain / large best-vs-market gap
- inventory surge
- inventory squeeze

The scripts only state facts available in PriceSift asking-price history. They do not invent a cause for a price or inventory change.

## GitHub Actions secrets for live mode

The workflow safely skips live automation until every required secret exists:

- `PRICESIFT_BASE_URL`
- `PRICESIFT_ADMIN_TOKEN`
- `BUFFER_API_KEY`
- `BUFFER_ORGANIZATION_ID`
- `BUFFER_YOUTUBE_CHANNEL_ID`
- `PRICESIFT_R2_ACCESS_KEY_ID`
- `PRICESIFT_R2_SECRET_ACCESS_KEY`
- `PRICESIFT_R2_ENDPOINT`
- `PRICESIFT_R2_BUCKET`
- `PRICESIFT_R2_PUBLIC_BASE_URL`

The R2 public base URL must be a stable public HTTPS URL. Buffer requires attached video media to remain publicly reachable until the post publishes.

## Deterministic test render

The branch/push workflow uses `fixtures/a770-signals.json` so selection, narration, generic visuals, render, and validation can be tested without production credentials.

Locally, after dependencies are installed:

```bash
python scripts/prepare_story.py --fixture fixtures/a770-signals.json
python scripts/generate_voice.py
npm run typecheck
npm run render
```

Output: `out/pricesift-short.mp4`
