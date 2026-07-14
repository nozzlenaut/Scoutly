# PriceSift status

- Cameras: Active — direct exact-model search
- Consoles: Active — core-model search with storage, color, drive, and revision variants grouped underneath
- GPUs: Active — direct exact-model search
- RAM: Active — strict DDR3/DDR4/DDR5 specification builder
- LEGO: Beta — exact set-number/name search with conservative completeness filtering
- Lenses: Paused — accessory and replacement-part ambiguity remains too high

Scoutly remains the internal repository and infrastructure name.
## Current validation phase

- Search QA workbench: Active at `/admin/qa`
- Seed suite: 16 Console cases and 20 LEGO cases
- Outcome tracking: Pass, Top-3 only, Fail, No inventory
- Persistence: PostgreSQL production storage with local JSON fallback
- Current build: v0.6.10 standard Switch completeness and result-title deduplication
- Next milestone: Rerun and save the unchanged 16 core-model Console cases, then decide whether Consoles can move to ongoing tuning

