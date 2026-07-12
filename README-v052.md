# Scoutly v0.5.2 — Search UX + async auctions + cleanup filters

This update focuses on testing speed and quality:

- Search results page now uses the same full search box/category selector pattern as the home page.
- Buy It Now results load first.
- Auctions load asynchronously after the main results, with a loading state.
- Search form shows a spinner/searching state.
- Added route-level loading screen for searches.
- Temporarily paused Nintendo Switch 2 catalog matching because current eBay results are mostly games/accessories.
- Added cleanup filters for recent reports:
  - PS5 external drive / poster-only / face-plate listings
  - console processor/APU/chip parts
  - LEGO cartridge-part listings
  - Tesla P40/P4/P100/V100/K80/M40 multi-model spam listings

Validation:

```text
Backend tests: 87 passed
Frontend build: not run in this sandbox because node_modules is not installed
```

Apply:

```bash
cd ~/Scoutly
git add -A
git commit -m "Improve search UX and async auctions"
git push
```
