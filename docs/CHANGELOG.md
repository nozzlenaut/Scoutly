# Changelog

## v0.4.0 - Dropdown cleanup and eBay affiliate readiness

- Closes the autocomplete dropdown when a search is submitted from the homepage or results page.
- Hides autocomplete suggestions when the current query is already a 100% exact catalog match.
- Closes autocomplete when focus leaves the search form.
- Adds optional eBay Partner Network context headers so Browse API results can return `itemAffiliateWebUrl` after ePN campaign details are configured.
- Marks outgoing marketplace links as sponsored.


## v0.3.8 - Bigger catalog and results-page search

- Expands the active camera catalog to 140 camera bodies and fixed-lens cameras.
- Expands the GPU lab catalog to 177 cards, including more NVIDIA workstation/datacenter GPUs, AMD Radeon Pro/Instinct cards, and Intel Arc Pro cards.
- Adds a compact search form directly to the search results page so users can test another item without returning home.
- Rejects camera accessory-only results like `EOS RP Camera Accessories`.
- Keeps lenses hidden from the active UI while lens-part results are still noisy.


## v0.3.7A - Catalog accuracy expansion

- Expands the active camera catalog to 61 camera bodies.
- Expands the GPU lab catalog to 97 graphics cards across NVIDIA, AMD, and Intel.
- Keeps lenses paused in the public UI while lens-part results are investigated.
- Tightens Sony Alpha generation matching so A7R III does not match original A7R 36.4MP listings.
- Rejects body-only camera searches when eBay returns lens-kit bundles.

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


## v0.3.5

Tightens lens accessory filtering so rubber zoom/focus rings, bayonet mount rings, rear mount rings, and metal replacement rings are rejected while real used lens listings can still pass.

## v0.3.6 — Hide lenses + eBay category IDs

- Temporarily removed lenses from the active search UI while lens-part filtering is validated.
- Added eBay US category IDs for camera-body, lens, and GPU provider searches.
- Camera searches now include `category_ids=31388` for Digital Cameras.
- GPU searches now include `category_ids=27386` for Graphics/Video Cards.
- Lens category support remains in the backend with `category_ids=3323`, but the UI marks lenses as coming soon.

## v0.3.9 - GPU accessory filtering

- Rejects GPU heatsink-only and replacement cooler/fan/accessory listings.
- Specifically covers Tesla V100 heatsink false positives seen in live search testing.
- Keeps legitimate data-center GPU card listings valid when they mention passive heatsinks as part of the full card.
