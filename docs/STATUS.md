# Scoutly Category Status

The homepage category selector should show what users can search now without turning the page into a large status board.

## Current categories

| Group | Category | Status | Notes |
| --- | --- | --- | --- |
| Photography | Cameras | Active | Starter camera body catalog is available. |
| Photography | Lenses | Coming soon | Lens catalog is retained but hidden while lens-part results are being improved. |
| PC Parts | GPUs | Lab | Catalog exists, but the public MVP is shifting toward category-based search. |

## Status meanings

- **Active** means users can search this category in the current UI.
- **Lab** means the category works for testing but is not the main launch focus.
- **Planned** means the category is not live yet.

## Grouping direction

For now, the selector can show specific categories like:

```text
Cameras | Lenses | GPUs
```

If the list grows, condense categories into groups:

```text
Photography | PC Parts | Gaming | Collectibles
```

Then show item types inside the selected group.


## v0.3.4

- Catalog expanded for broader Cameras, Lenses, and GPUs testing.
- Lens accessory filters tightened.


## v0.3.5

Tightens lens accessory filtering so rubber zoom/focus rings, bayonet mount rings, rear mount rings, and metal replacement rings are rejected while real used lens listings can still pass.


## v0.3.7A

Catalog accuracy expansion complete: 61 cameras, 97 GPUs, 26 retained lenses. Lenses remain paused from the public UI.


## v0.4.0

Autocomplete now closes on submit, exact 100% matches, and focus exit. eBay affiliate tracking is supported once ePN campaign variables are configured.
