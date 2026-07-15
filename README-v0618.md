# PriceSift v0.6.18 — KEH Sony public pilot

This release keeps the full KEH/Awin inventory integration in place and publishes KEH listings for only three exact camera products:

- Sony A7 III Body
- Sony A7 IV Body
- Sony a6700 Body

Every other KEH match remains visible only in `/admin/keh`.

## Railway variables

Keep the existing private feed settings and change the public flag:

```env
AWIN_KEH_FEED_URL=<private Create-a-Feed URL>
KEH_FEED_ENABLED=true
KEH_PUBLIC_RESULTS=true
```

The default public whitelist is already restricted to the three Sony pilot models. Optionally set it explicitly:

```env
KEH_PUBLIC_PRODUCT_IDS=camera-sony-a7-iii-body,camera-sony-a7-iv-body,camera-sony-a6700-body
```

Do not add the feed URL to Vercel or GitHub. It belongs on Railway only.

## How the pilot behaves

- KEH fixed-price listings merge with eBay Buy It Now candidates.
- The final buyer-facing result set still contains at most three listings.
- KEH grades appear as the listing condition.
- Awin tracked links remain intact and are click-tracked through PriceSift.
- KEH remains excluded from auctions and historical price snapshots during the pilot.
- Non-whitelisted KEH matches remain admin-only.

## Test after deployment

1. Let Railway restart.
2. Open PriceSift searches for Sony A7 III, Sony A7 IV, and Sony a6700.
3. Confirm KEH appears only when it ranks in the top three.
4. Open each KEH result and confirm it reaches the correct KEH product through the Awin link.
5. Search another matched camera model and confirm it remains eBay-only.

## Automatic feed refresh

Use the existing Railway cron service:

```bash
python -m app.services.keh_sync_runner
```

Schedule:

```text
0 */6 * * *
```
