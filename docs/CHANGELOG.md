# v0.5.8 — PriceSift public branding and catalog growth

- Changes all public-facing site, search, disclosure, report, loading, and admin branding from Scoutly to PriceSift while retaining Scoutly for internal repository, package, database, and affiliate identifiers.
- Adds canonical metadata for `https://www.pricesift.app`, Open Graph/Twitter metadata, a web-app manifest, favicon, robots rules, and sitemap.
- Rejects listings whose title ends with a standalone `READ` warning, including auction results.
- Expands the LEGO lab catalog from 318 to 395 sets with 77 additional Star Wars, Winter Village, Icons/vehicles, Ideas, Architecture, Technic, Disney, and collector sets.


## v0.5.5 — Affiliate label and LEGO catalog expansion

- Renames visible result-card label from “Sponsored link” to “Affiliate link” so users do not confuse affiliate links with paid placement.
- Expands the LEGO lab catalog from 192 to 318 sets, adding more Star Wars, Icons, Ideas, Harry Potter, Technic, Speed Champions, Disney, Ninjago, Minecraft, and Architecture sets.


## v0.4.8 — Live filter rules

- Adds admin-managed manual filter rules so bad title phrases can be rejected without redeploying.
- Adds optional category/product scoping and exception phrases for manual rules.
- Adds admin endpoints for listing, creating, and deleting manual rules.
- Adds an admin UI panel for live filter rules.
- Tightens LEGO matching to require the exact set number when a set number exists.
- Rejects LEGO base-only / towers-only / main-build-only style partial listings.
- Rejects GPU problem/issue listings while allowing “no problems” / “no issues” context.

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

## v0.4.1 - Affiliate disclosure and campid fallback

- Adds a casual affiliate disclosure page at `/disclosure`.
- Adds a small affiliate disclosure footer on the home and search pages.
- Keeps result-card disclosure text visible near eBay outbound links.
- Adds affiliate-link status fields to result payloads so the UI can show when a link contains a campaign ID.
- Adds a conservative eBay URL fallback that appends the configured `campid` if eBay returns a partial affiliate URL with `customid`/`toolid` but no visible campaign ID.

## v0.4.2

- Added `/api/out` outbound redirect endpoint for eBay links.
- Result buttons now use the backend redirect so `campid` is applied at click time even if a cached result URL was missing it.
- Outbound redirects are restricted to eBay domains.

## v0.4.3 — Click tracking and bad-result reporting

- Logs outbound eBay clicks through the `/api/out` redirect before sending users to eBay.
- Adds metadata to outbound clicks: query, category, product ID, provider, title, eBay item ID, and whether affiliate campaign tracking was present.
- Adds `POST /api/results/report` so users can flag bad marketplace results such as accessories, straps, parts, or the wrong model.
- Temporarily hides reported eBay item URLs for the matched product/category for 72 hours.
- Auto-prunes report storage to active reports only and caps it at 500 entries.
- Caps click storage at the latest 2,000 click events for lightweight MVP analytics.

## v0.4.4 — Analytics view and auction comparison

- Adds `/admin` so Scoutly's own click tracking can be viewed without waiting on eBay Partner reporting.
- Adds `GET /api/analytics/summary`, `/api/analytics/clicks`, and `/api/analytics/reports`.
- Supports optional `SCOUTLY_ADMIN_TOKEN`; when set, analytics endpoints and `/admin?token=...` require the token.
- Adds eBay auction search as a separate “Auction ending soon” comparison section.
- Keeps Buy It Now as the primary result so auctions do not replace available-now deals.
- Uses eBay `buyingOptions:{AUCTION}` and `sort=endingSoonest` for auction comparison searches.

## v0.4.5 — Search cleanup, filtered-debug admin, and LEGO prototype

- Rejects camera-body listings that are actually filters, UV/CPL/ND filters, or other filter accessories.
- Rejects SXM/SXM2/SXM3/SXM4, mezzanine, and module results for normal Tesla P100/V100 searches so homelab users are steered toward PCIe cards.
- Keeps legitimate PCIe Tesla cards valid, including cards that mention passive heatsinks.
- Changes the search results page to use a more desktop-friendly horizontal result-card layout while staying mobile-friendly.
- Shows up to three eBay auctions ending soon as comparison options instead of only one auction.
- Adds filtered-listing logging so `/admin` can show eBay results that were rejected before ranking, including the reason.
- Adds `GET /api/analytics/filtered` for recent filtered-listing debug records.
- Adds LEGO as a lab category with eBay category filtering and 99 starter sets, focused on exact set-number matching.
- Keeps lenses paused in the active UI.

## v0.4.6 — Match-quality fixes

- Fixes the short-token matching bug where `ti` could match normal words like `edition` or `condition`, causing valid RTX 4070 listings to be rejected.
- Keeps compact matching for real compact product names like `RTX4070Ti`, `A7III`, `RX6700XT`, and `G2`.
- Rejects `SMX` / `SMX2` typo variants for normal Tesla P100/V100 PCIe searches, in addition to SXM/SXM2.
- Rejects LEGO listings that contain the requested set number plus additional modern 5-digit set numbers, since those are usually bundles/lots rather than the exact set.
- Adds regression tests for RTX 4070 false rejects, Tesla P100 SMX2, and LEGO multi-set listings.



## v0.4.7

- Tighten LEGO incomplete/partial listing filters.
- Reject LEGO listings with missing pieces, not complete, partial, parts/pieces-only, and minifigure-only style titles.
- Keep normal piece-count wording valid, such as `1931 Pieces | Complete Set`.
- Allow complete LEGO set listings that mention manuals/instructions, while still rejecting instructions-only/manual-only listings.
- Add `Partial / incomplete` as a report reason in the result card UI.

## v0.4.9 — Consoles + testing UX

- Added Consoles as a lab category covering Xbox, PlayStation, and Nintendo families.
- Added eBay Video Game Consoles category filtering for console searches.
- Search results now return up to three safe Buy It Now options instead of only one while categories are being tuned.
- Homepage now explains Scoutly's goal: complete used items, lowest useful prices, no partials, no broken/parts-only listings when detectable.
- Homepage now includes casual affiliate-link support wording and an incognito/private-search alternative.
- Added console accessory/partial filters for controller-only, dock-only, tablet-only, HDMI-port, power-supply, screen-only, shell-only, and similar listings.
- Added cleanup filters for recent reports: LEGO cartridge-only listings, minifigure-code/person listings, and GPU fan-missing listings.

## v0.5.1 — Performance pass

- Normal search no longer requests auction results by default.
- Search page keeps up to three Buy It Now results visible immediately.
- Adds a **View ending-soon auctions** button that reloads the search with auction comparison enabled.
- Keeps auctions separate from Buy It Now results and still shows up to three ending-soon auction cards when requested.
- Reduces eBay fixed-price search candidate limit from 50 to 35.
- Reduces eBay auction candidate limit from 50 to 25.
- Changes result lists to a responsive card grid so desktop can scan three results side-by-side.
- Adds lazy loading to result images.

## v0.5.3 — Trust and polish pass

- Adds stricter console cleanup for covers, accessory bundles, stick drift, monitor bundles, and game-only noise.
- Adds stricter LEGO cleanup for loose part listings like horses, beds, cartridges, and small lots while still allowing complete sets with normal piece-count wording.
- Demotes low-feedback sellers in ranking and shows a clearer low-feedback warning on result cards.
- Keeps zero-feedback sellers filtered out.
- Simplifies affiliate messaging on result cards to a small Affiliate link label while keeping the disclosure page/footer.
- Improves empty-state copy when a resolved product has no safe Buy It Now listings.
- Adds accessible labels, combobox/listbox roles, keyboard navigation, image alt text, and live status text for search/autocomplete.
- Adds dynamic search page titles like “Xbox Series X deals | Scoutly.”
- Adds Consoles to the admin live-rule category dropdown via dynamic category options.
- Adds report restore/delete support in admin for accidental bad-result flags.
- Adds normalizer caching to speed up catalog matching.

## v0.5.6 — Regression and trust fixes

- Replaces the sticky local submit flag with React transition state and remounts the compact form by category/query, fixing repeat searches that stayed disabled.
- Requires positive Joy-Con/controller/dock/completeness wording for full-size Nintendo Switch and Switch OLED listings.
- Converts invalid eBay seller sentinels (`0%` rating and negative feedback counts) to unavailable seller history.
- Adds Sony A1 II / ILCE-1M2 and prevents explicit generation queries from falling back to earlier camera generations.
- Tightens explicit GPU modifier/storage matching when users type clues such as Ti, XT, or 16GB.
- Improves selected Active/Lab badge contrast.
- Uses “affiliate links” consistently in homepage copy.
- Uses resolved/unresolved-aware auction empty states.
- Adds regression coverage for Sony A1 II, Switch completeness, seller sentinels, and common LEGO set aliases.

## v0.5.9 — Result interaction and variation-price cleanup

- Makes listing images and titles clickable using the same tracked outbound link as the result button.
- Uses a full page navigation for each submitted search so old fixed-price or auction state cannot append to a new query.
- Rejects eBay seller-defined variation groups for consoles and GPUs because the visible price can belong to an accessory or lower-spec option.
- Rejects multi-model GPU titles such as RTX A3000/A4000/A5000 and adds GPU core, no-cooler, shell-only, and box-and-insert-only filters.
- Rejects camera service manuals and parts lists.
- Tightens Nintendo handheld filtering for accessory-only, game/manual, charger-only, and seller-selection listings while preserving complete console bundles that include chargers.
- Pauses Wii U until complete console + GamePad requirements are defined.
- Adds regression coverage for all newly reported titles and eBay variation metadata.
