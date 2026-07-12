# Scoutly v0.4.9 — Consoles + testing UX

This update adds a lab console category and makes result testing easier.

## Included

- Consoles category: Xbox, PlayStation, and Nintendo starter catalog.
- eBay console category filtering.
- Up to 3 safe Buy It Now result cards for the resolved item.
- Existing up-to-3 auction comparison remains separate.
- Homepage explanation of what Scoutly does and how referral links support it.
- New cleanup rules from reported bad results:
  - LEGO cartridge-only listings.
  - LEGO minifigure/person/code listings that reference a set.
  - GPU listings with missing fan notes.
  - Console parts/accessories/partial listings.

## Validation

- Backend tests: `80 passed`
- Frontend build: not run in this sandbox because `node_modules` is not installed.

## Apply

```bash
cd ~/Scoutly
git add -A
git commit -m "Add console category and testing UX"
git push
```
