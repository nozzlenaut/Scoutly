# Scoutly v0.6.4 / PriceSift Nintendo Switch Standard search fix

- Makes `Standard Switch (V1/V2)` search the common seller identities separately: V1, V2, HAC-001, HAC-001(-01), Standard, and generic Nintendo Switch console listings.
- Merges and deduplicates valid results from all Standard Switch queries.
- Accepts legitimate Standard Switch titles that identify a console/system or revision even when the title does not explicitly mention Joy-Cons or a dock.
- Continues rejecting OLED, Lite, Switch 2, tablet-only, dock-only, Joy-Con-only, game-only, and other accessory/incomplete listings.
- Renames the builder option to `Standard Switch (V1/V2)` for clarity.
- Keeps internal Scoutly infrastructure unchanged.
