# PriceSift v0.6.19 — Private KEH lens-builder lab

This release adds a private admin experiment for exploring all current KEH interchangeable-lens inventory without changing public PriceSift results.

## What stays public

The existing KEH public pilot remains limited to:

- Sony A7 III Body
- Sony A7 IV Body
- Sony a6700 Body

No lens appears in normal search, ranking, QA, auctions, or price history.

## Lens test flow

Open:

```text
/admin/keh/lenses
```

The lab follows:

```text
Mount/System → Prime/Zoom → Focal-length group → Lens brand (optional) → searchable exact models
```

Each exact model expands to the cheapest three current KEH copies, including grade, price, image, and tracked Awin link. Duplicate inventory rows are grouped into one model choice.

## After deployment

Run **Sync KEH now** once from `/admin/keh`. Earlier syncs stored only the camera pilot rows; v0.6.19 must perform a fresh sync to retain the full lens inventory for the lab.

No new environment variables are required. Keep the existing Railway values:

```env
AWIN_KEH_FEED_URL=<private Awin feed URL>
KEH_FEED_ENABLED=true
KEH_PUBLIC_RESULTS=true
```

## Also fixed

The main search autocomplete now stays closed after a search/navigation and only reopens after the user actively focuses or edits the field. This prevents the retained query dropdown from covering mobile results.
