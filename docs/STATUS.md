# PriceSift status

- Cameras: Active — direct exact-model search
- Consoles: Active — direct exact-model search with original Switch V1/V2/HAC aliases
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
- Next milestone: Run the seeded suite, review failure patterns, and tune filters/catalog coverage before adding another category

