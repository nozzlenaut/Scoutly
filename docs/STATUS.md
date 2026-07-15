# PriceSift status

- Cameras: Active — direct exact-model search; eBay plus a controlled KEH public pilot for Sony A7 III, A7 IV, and a6700
- Consoles: Active — core-model search with storage, color, drive, and revision variants grouped underneath
- CPUs: Active — exact consumer-desktop model builder with suffix-safe matching
- GPUs: Active — direct exact-model search
- RAM: Active — strict DDR3/DDR4/DDR5 specification builder
- LEGO: Beta — exact set-number/name search with conservative completeness filtering
- Lenses: Admin lab — private KEH-only inventory builder using live feed models; nothing is public

Scoutly remains the internal repository and infrastructure name.

## Current validation phase

- Search QA workbench: Active at `/admin/qa`
- Seed suite: 88 cases across Cameras, GPUs, RAM, CPUs, Consoles, and LEGO
- Outcome tracking: Pass, Top-3 only, Fail, No inventory
- Persistence: PostgreSQL production storage with local JSON fallback
- Current build: v0.6.19 private KEH lens-builder lab
- Next milestone: Test mount/type/focal-group parsing and unique-model grouping in the KEH lens lab before deciding on a public lens category
