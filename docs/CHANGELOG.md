# Changelog

## v0.3.4 - Catalog expansion and lens filter cleanup

- Expands the camera-body catalog across Sony, Canon, Nikon, Fujifilm, and Panasonic.
- Expands the lens catalog across Sony, Canon RF, Nikon Z, Fujifilm X, Sigma, and Tamron.
- Adds more AMD, Intel, and NVIDIA GPUs for broader search testing.
- Tightens lens accessory rejection for ring adapters, lens coats/skins, gear rings, and cap/hood-only listings.

## 0.3.1 - Search query and camera filter hotfix

- Fixes deployed Next.js search pages reading default category queries instead of URL search params.
- Rejects camera-body repair parts and model-crossmatches such as A7R IV parts when searching A7 IV.
- Keeps public npm registry config for Vercel builds.

## v0.3.0 - eBay marketplace integration

- Adds eBay Browse API OAuth client credentials flow.
- Adds live eBay provider for used item searches.
- Normalizes eBay item summaries into Scoutly listing cards.
- Uses eBay images and seller feedback when available.
- Keeps mock eBay fallback when local credentials are not configured.
- Defaults search to eBay only so the public site does not mix live eBay results with mock Amazon results.

## v0.2.4 - eBay notification endpoint

- Adds Marketplace Account Deletion notification verification endpoint for eBay developer compliance.

## v0.2.3 - Vercel autocomplete CORS fixed

- Allows browser calls from deployed Vercel domains while Scoutly is in MVP development.

## v0.2.2 - Category search added

- Adds category-based search for Cameras, Lenses, and GPUs.
- Converts the catalog from GPU-only to generic products.

## v0.2.1 - Product catalog autocomplete added

- Adds expanded GPU catalog matching and homepage autocomplete.

## v0.2.0 - GPU search added

- Adds status UI and early category direction.

## v0.3.2 - Dropdown and camera accessory filtering

- Keeps autocomplete suggestions above the catalog description/status cards.
- Rejects camera-body accessory listings such as bayonet mount rings and replacement parts.
- Adds tests for A7 III accessory false positives.


## v0.3.3 - Search quality filters

- Adds stricter global rejection terms like box only, please read, read description, as-is, and untested.
- Adds camera, lens, and GPU accessory/parts filters.
- Keeps eBay searches conservative by avoiding fallback searches without condition filtering.
