# PriceSift status

- Cameras: Active — direct exact-model search
- Consoles: Active — core-model search with storage, color, drive, and revision variants grouped underneath
- CPUs: Active — exact consumer-desktop model builder with suffix-safe matching
- GPUs: Active — direct exact-model search
- RAM: Active — strict DDR3/DDR4/DDR5 specification builder
- LEGO: Beta — exact set-number/name search with conservative completeness filtering
- Lenses: Paused — accessory and replacement-part ambiguity remains too high

Scoutly remains the internal repository and infrastructure name.
## Current validation phase

- Search QA workbench: Active at `/admin/qa`
- Seed suite: 88 cases across Cameras, GPUs, RAM, CPUs, Consoles, and LEGO
- Outcome tracking: Pass, Top-3 only, Fail, No inventory
- Persistence: PostgreSQL production storage with local JSON fallback
- Current build: v0.6.13 stable QA baseline
- Next milestone: Add price snapshots and typical-price context while keeping the 88-case QA suite as a periodic regression check

