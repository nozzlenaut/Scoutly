# Changelog

## v0.6.35

- Groups every current KEH camera-body title into a searchable model and publishes those models through a public `/cameras` directory.
- Gives catalog-matched cameras eBay + KEH coverage while hard-blocking eBay and auctions for additional KEH-native models.
- Adds stable, indexable `/cameras/[slug]` model pages with current KEH inventory, canonical metadata, and dynamic sitemap entries; arbitrary `/search` pages remain `noindex`.
- Keeps directory payloads compact while model pages expose the three lowest-priced current KEH copies.
- Adds an optional delivery-ZIP lookup for the visible eBay listings when “US listings only” is active.
- Sends the ZIP only in a POST body, strips eBay’s echoed destination from the response, and does not save it in analytics, URLs, logs, or browser storage.
- Adds exact eBay marketplace item IDs to result payloads so delivery checks never broaden or rerun the product search.
- Adds KEH provider-boundary, camera grouping, stable discovery, and public delivery privacy regressions; 235 backend tests and the Next.js production build pass.

## v0.6.34

- Expands the fixed-price eBay candidate pool from 65 to 100 for PlayStation 5-family, PlayStation 4 Slim, Xbox Series S, and Xbox Series X searches that were still exhausting every candidate.
- Keeps other console searches at 65 candidates, all other fixed-price categories at 35, auctions at 25, and the public result maximum at three.
- Preserves every existing identity and quality filter; this change searches deeper instead of admitting lower-quality listings.

## v0.6.33

- Rejects listings labeled `defective` even when eBay reports their condition as Used.
- Preserves the existing warning and ranking penalty for otherwise-clean `read description` listings.
- Expands the console-only fixed-price candidate pool from 50 to 65 so filtering the defective result does not end the search at the same depth.

## v0.6.32

- Expands fixed-price eBay console searches from 35 to 50 candidates so exact-model filters can search past the unusually dense accessory, wrong-model, incomplete, and broken console listings.
- Keeps the 35-candidate limit for every other category and leaves all existing quality filters unchanged.

## v0.6.31

- Completes the KEH camera and public KEH-only lens release after the prior commit added only the new lens page, component, and tests.
- Publishes confidently matched KEH inventory across the active camera-body catalog and keeps public eBay lens search disabled.
- Wires the public lens endpoint, frontend API helper, category routing, admin wording, and release tests together.
- Adds deterministic pytest isolation so local production credentials cannot turn unit tests into live eBay or database tests.
- Stops pytest and Python cache files from repeatedly dirtying the repository.
- Replaces stale status text with a concise living project status, decisions log, and working agreement.
- Keeps delivery manual: review, test, commit, and push from a clean Git working tree.

## v0.6.29

- Converts Recent clicks, Recently filtered listings, Feedback inbox, and Active bad-result reports into collapsed admin dropdown sections.
- Shows a live entry count in each dropdown header while leaving summary analytics and live filter controls visible.
- Replaces the accidental R-shaped PriceSift icon with an unmistakable P-shaped mark while preserving the existing dark-blue and teal styling.
- Requires no database migration or new environment variables.

## v0.6.28

- Standardizes recent admin activity timestamps in Eastern Time and labels the displayed timezone.
- Treats legacy offset-free activity timestamps as UTC before display, preventing future-looking click and feedback times.
- Promotes public beta feedback into a clearly linked admin feedback inbox.
- Shows the source page for each feedback submission and confirms the storage destination in the admin UI.
- Requires no database migration or new environment variables.

## v0.6.27

- Corrects light-analytics click attribution.
- Counts a click toward search analytics only when it can be linked to a matching public search that occurred before the click.
- Excludes older affiliate click history from search-to-click rates, category click totals, and provider click totals.
- Shows older or unlinked clicks separately so historical records remain visible without distorting current usage.
- Keeps the existing privacy model: no IP addresses, cookies, accounts, or personal identifiers.
- Requires no new environment variables or database changes.
- Brings the backend suite to 216 passing tests; the production Next.js build passes.

## v0.6.26

- Adds privacy-friendly public search analytics without storing IP addresses, cookies, accounts, or personal identifiers.
- Records category, resolved product/ISBN, result availability, providers shown, candidate/filter counts, US-only usage, and outbound listing clicks.
- Adds a 7/30/90-day admin analytics digest with category trends, top searches, no-result rates, provider clicks, and a paste-ready summary/JSON export.
- Adds a persistent â€œUS listings onlyâ€ toggle near Search that filters eBay Buy It Now, auctions, and Books ISBN searches by item location while leaving KEH unchanged.
- Preserves the location preference in the browser and in shareable search URLs.
- Excludes US-only searches from broad-market price snapshot storage so domestic filtering does not distort typical-price history.
- Counts approved Awin/KEH outbound links as affiliate-tagged clicks.
- Adds six analytics/location regressions, bringing the backend suite to 215 passing tests.

## v0.6.25

- Fixes `/admin/prices` crashing during server rendering when PostgreSQL `NUMERIC` values arrive as decimal strings.
- Converts backend `Decimal` price fields and decimal arrays into JSON numbers.
- Adds defensive frontend number coercion before currency and percentage formatting.
- Adds a regression test for production-style decimal serialization.

## v0.6.24

- Strengthens Books title-consensus matching so a shared generic word cannot admit an unrelated title into a dominant multi-word cluster.
- Separates multi-book lots, bundles, and sets from normal single-copy Books results.
- Adds bundle counts and private/public bundle inspection sections while keeping the default top three single-copy only.
- Rebuilds `/admin/prices` around server-side initial loading using the same direct Railway API pattern as the working KEH admin page.
- Removes the price dashboard's normal dependency on the browser proxy and adds visible backend error details at the token gate.
- Adds two Books regressions, bringing the backend suite to 208 passing tests.

## v0.6.23

- Promotes Books into the public beta with a simple ISBN-10/ISBN-13 search field.
- Keeps ISBN-13-first lookup with ISBN-10 fallback and coherent-title verification.
- Removes study guides, summaries, workbooks, and companion products from exact-book results.
- Separates signed, deluxe, limited, and collectible copies so price outliers do not replace normal used copies.
- Adds cautions for seller-supplied edition-year wording while preserving exact ISBN matches.
- Keeps the private Books diagnostics page for detailed candidate and rejection review.

## v0.6.22

- Changed Books ISBN lookup to ISBN-13-first with ISBN-10 fallback instead of merging both result sets.
- Added a title-consistency sanity gate for large ISBN result sets so unrelated eBay catalog matches fail safely.
- Added per-query diagnostics to the private Books lab.

## v0.6.21

- Adds a private `/admin/books` ISBN-first test page.
- Uses exact eBay GTIN/ISBN catalog search instead of title-keyword matching.
- Accepts ISBN-10 or ISBN-13 and automatically tests the equivalent format when available.
- Rejects invalid check digits before any marketplace call.
- Limits results to used Buy It Now copies and preserves distinct sellers with identical book titles.
- Shows the intended top three by delivered price plus expandable additional eligible copies.
- Keeps Books private and out of public search, QA, and price history.
- Adds five focused regressions, bringing the backend suite to 198 passing tests.

## v0.6.20

- Polishes `/admin/keh/lenses` into the intended KEH-only guided browsing experience.
- Removes the exact-model search field from the main lens flow.
- Keeps model results hidden until Mount/System, Prime/Zoom, and focal-length group are selected.
- Keeps lens brand optional and shows all matching in-stock models when no brand is selected.
- Adds representative model images, inventory counts, lowest/highest prices, and available KEH grade summaries.
- Expands each model into its three lowest-priced current KEH listings.
- Keeps all lens inventory private and out of public search, QA, auctions, and price history.
- Keeps the backend suite at 193 passing tests and adds richer lens-group assertions.

## v0.6.19

- Adds a private `/admin/keh/lenses` builder lab backed by the live KEH/Awin feed.
- Retains all active KEH interchangeable-lens rows during sync while leaving lenses completely out of public search.
- Adds cascading Mount/System, Prime/Zoom, focal-length group, and optional brand filters.
- Normalizes duplicate KEH copies into unique model groups and exposes the lowest three actual listings for each model.
- Adds exact-model text search across the narrowed current inventory.
- Keeps the existing three-camera KEH public pilot unchanged.
- Closes autocomplete suggestions after navigation and prevents the result-page query from reopening the dropdown until the user actively focuses or types.
- Adds three KEH lens regressions, bringing the backend suite to 193 passing tests.

## v0.6.18

- Publishes KEH/Awin fixed-price listings for a three-product Sony camera pilot: A7 III, A7 IV, and a6700.
- Keeps every other KEH match shadow-only behind the admin dashboard.
- Merges eligible KEH listings into the existing top-three Buy It Now ranking.
- Preserves Awin tracked deep links through PriceSift outbound click logging.
- Displays KEH condition grades and retailer identity without marketplace-seller warnings.
- Keeps KEH out of auctions and historical price snapshots during the pilot.
- Adds three KEH public-pilot and Awin redirect regressions, bringing the backend suite to 190 passing tests.

## v0.6.17

- Added KEH Camera/Awin feed ingestion in private shadow mode.
- Added `/admin/keh` matching and sync diagnostics.
- Added Railway cron-compatible KEH sync runner.
- Added KEH grade parsing and tracked-link storage.
- Changed homepage promise to â€œFree to use. Always.â€
- KEH remains excluded from public results and price history.


## v0.6.16

- Prevents unresolved public queries from falling through to raw marketplace searches.
- Shows a clear unsupported-product state with close catalog suggestions when available.
- Makes zero fixed-price or auction provider calls for unsupported catalog queries.
- Routes `/admin/prices` overview and collection requests through same-origin Vercel handlers before reaching Railway.
- Adds detailed price-proxy error output and an optional server-only `API_URL` frontend environment variable.
- Adds three public-search guard tests, bringing the backend suite to 182 passing tests.

## v0.6.15

- Fixes the `/admin/prices` page with client-side overview loading and visible retry/error handling.
- Rejects clear GPU fan/cooling defects while preserving explicitly negated safe phrases.
- Honors explicit PlayStation Disc/Digital edition wording without splitting grouped core-model catalog IDs.
- Adds visible `read description` cautions and ranking penalties across all categories.
- Adds shareable search controls using the native share sheet or clipboard fallback.
- Marks PriceSift as a public beta and adds clear no-signup testing instructions.
- Adds a persistent public beta-feedback form and private admin review table.
- Adds four focused regression areas, bringing the backend suite to 179 passing tests.

## v0.6.13

- Adds a narrow PAC-MAN Arcade `10323` sub-build rule for named ghosts such as Blinky, Clyde, Pinky, and Inky.
- Rejects ghost/display builds that reuse the parent set number and PAC-MAN wording without evidence of the full arcade machine.
- Keeps full arcade-machine/cabinet titles and complete sets eligible, even when they mention included ghosts.
- Adds a focused regression test, bringing the backend suite to 168 passing tests.
- Freezes the existing 88-case QA matrix as the stable cross-category baseline.

## v0.6.12

- Rejects faulty and partially functional electronics, including single-working-port GPU listings.
- Rejects mixed/conflicting-speed RAM kits for exact-speed searches.
- Requires LEGO set numbers to agree meaningfully with the canonical set name.
- Rejects LEGO sub-builds, instruction-manual sets, and small individual-brick listings.
- Separates inventory-adjusted QA quality from safe no-inventory and overall outcome rates.
- Adds four focused regression tests, bringing the backend suite to 167 passing tests.

## v0.6.11

- Adds an active CPU builder covering 161 consumer desktop processors across AMD AM4/AM5 and Intel LGA1151/LGA1200/LGA1700/LGA1851.
- Keeps CPU suffix variants exact while grouping the selection flow by manufacturer, socket, generation, and final model.
- Filters CPU bundles, accessories, lots, full systems, engineering/qualification samples, damaged chips, and model/suffix conflicts.
- Adds eBay US Computer Processors category `164`.
- Expands the QA suite to 88 cases across Cameras, GPUs, RAM, CPUs, Consoles, and LEGO.
- Makes QA category filters dynamic and preserves existing Console/LEGO case IDs and evaluation history.
- Adds seven CPU/provider/QA regression tests, bringing the backend suite to 163 passing tests.

## v0.6.10

- Requires standard Nintendo Switch results to show explicit complete-system language or both Joy-Con and dock evidence.
- Rejects bare HAC-001 / tested-working titles that may describe tablet-only hardware.
- Deduplicates final results by marketplace URL and normalized visible title so repeated listings cannot occupy the full top three.
- Adds duplicate-collapsed diagnostics to the QA workbench.
- Adds exact Switch-completeness and duplicate-title regression cases, bringing the backend suite to 156 passing tests.

## v0.6.9

- Adds a stricter console listing-eligibility layer for standalone drives, shells, frames, cooling parts, cases, packaging/manual-only listings, docks, and incomplete hardware.
- Rejects `Console Edition` game listings and Xbox 360 titles that collide with Xbox Series S/X wording.
- Rejects HEG-001/OLED hardware from standard Nintendo Switch searches and strengthens PlayStation Pro hardware evidence.
- Keeps `READ`-caveated listings eligible but heavily demotes them below clean tested hardware.
- Fixes the final fixed-price result order so quality scores are preserved instead of re-sorting the selected top three by lowest price.
- Adds QA diagnostics for eligible listings and categorized filter-reason counts.
- Adds exact regression cases from the v0.6.8 console QA report, bringing the backend suite to 155 passing tests.

## v0.6.8

- Groups console storage, color, drive, revision, and bundle variants under 16 core-model catalog products.
- Makes PlayStation 4/5, Slim, Pro, Xbox Series S/X, Xbox One S/X, Switch, Switch OLED/Lite/2, Wii U, and 3DS XL the active searchable identities.
- Keeps old variant-specific wording as aliases while using broad marketplace queries such as `Xbox Series S console`.
- Removes storage and Disc/Digital controls from the Console builder until a later narrowing release.
- Replaces the 16 Console QA cases with versioned core-model cases so Console testing resets without erasing the 20 saved LEGO evaluations.
- Activates Switch 2 and Wii U as core-model QA targets.
- Adds grouped-variant regression coverage, bringing the backend suite to 153 passing tests.

## v0.6.7

- Adds a private `/admin/qa` live-search workbench for repeatable console and LEGO validation.
- Seeds 36 exact-item cases covering aliases, model revisions, storage/edition distinctions, duplicate LEGO set names, and common accessory/partial-item traps.
- Records Pass, Top-3 only, Fail, and No inventory outcomes with issue tags, notes, expected/resolved product IDs, result-title snapshots, diagnostics, and attempt counts.
- Persists QA evaluations to PostgreSQL with local JSON fallback.
- Adds aggregate quality metrics and filters for category, untested cases, and cases needing review.
- Adds three QA tests, bringing the backend suite to 152 passing tests.

## v0.6.4

- Fixes Standard Nintendo Switch searches that could return no results because the marketplace query used the uncommon combined phrase `Nintendo Switch V1/V2`.
- Searches V1, V2, HAC-001, HAC-001(-01), Standard, and generic Nintendo Switch console wording separately, then merges and deduplicates valid listings.
- Relaxes positive title evidence for Standard Switch consoles while retaining strict tablet-only, dock-only, Joy-Con-only, OLED, Lite, Switch 2, game, and accessory exclusions.
- Labels the builder option `Standard Switch (V1/V2)`.

## v0.6.1

- Adds a guided Console builder: brand â†’ family/generation â†’ results, with optional model, storage, and edition/drive refinements.
- Allows safe family-level console searches when the buyer does not care about storage or a specific model.
- Promotes RAM to Active after precision testing.
- Renames Lab to Beta and keeps LEGO in Beta.
- Sorts categories by status and then alphabetically.
- Removes fresh-page search autofill and adds category-specific placeholders.
- Adds DDR3L voltage-compatibility warnings.
- Expands LEGO packaging-only, incomplete, unauthentic, compatible-brick, loose-brick, lot, and bulk exclusions.

# v0.5.10 â€” Search consistency and trust cleanup

- Rejects LEGO empty outer-box, inner-box-only, and numbered inner-box packaging listings.
- Clears stale result cards immediately when searches or result-page categories change.
- Shows autocomplete consistently across active categories and clarifies catalog selection versus raw-text search.
- Keeps ambiguous RTX 3080 searches unresolved until 10GB or 12GB is selected.
- Separates product-match confidence from automated listing-quality checks.
- Allows and labels legitimate console bundles while ranking equivalent clean listings first.
- Strengthens seller-risk ranking and clarifies item-plus-shipping totals, taxes, and import-charge limitations.
- Distinguishes absent inventory from candidates removed by automated filters.
- Improves secondary text contrast.

# v0.5.8 â€” PriceSift public branding and catalog growth

- Changes all public-facing site, search, disclosure, report, loading, and admin branding from Scoutly to PriceSift while retaining Scoutly for internal repository, package, database, and affiliate identifiers.
- Adds canonical metadata for `https://www.pricesift.app`, Open Graph/Twitter metadata, a web-app manifest, favicon, robots rules, and sitemap.
- Rejects listings whose title ends with a standalone `READ` warning, including auction results.
- Expands the LEGO lab catalog from 318 to 395 sets with 77 additional Star Wars, Winter Village, Icons/vehicles, Ideas, Architecture, Technic, Disney, and collector sets.


## v0.5.5 â€” Affiliate label and LEGO catalog expansion

- Renames visible result-card label from â€œSponsored linkâ€ to â€œAffiliate linkâ€ so users do not confuse affiliate links with paid placement.
- Expands the LEGO lab catalog from 192 to 318 sets, adding more Star Wars, Icons, Ideas, Harry Potter, Technic, Speed Champions, Disney, Ninjago, Minecraft, and Architecture sets.


## v0.4.8 â€” Live filter rules

- Adds admin-managed manual filter rules so bad title phrases can be rejected without redeploying.
- Adds optional category/product scoping and exception phrases for manual rules.
- Adds admin endpoints for listing, creating, and deleting manual rules.
- Adds an admin UI panel for live filter rules.
- Tightens LEGO matching to require the exact set number when a set number exists.
- Rejects LEGO base-only / towers-only / main-build-only style partial listings.
- Rejects GPU problem/issue listings while allowing â€œno problemsâ€ / â€œno issuesâ€ context.


## v0.6.13

- Adds a narrow PAC-MAN Arcade `10323` sub-build rule for named ghosts such as Blinky, Clyde, Pinky, and Inky.
- Rejects ghost/display builds that reuse the parent set number and PAC-MAN wording without evidence of the full arcade machine.
- Keeps full arcade-machine/cabinet titles and complete sets eligible, even when they mention included ghosts.
- Adds a focused regression test, bringing the backend suite to 168 passing tests.
- Freezes the existing 88-case QA matrix as the stable cross-category baseline.

## v0.6.10

- Requires standard Nintendo Switch results to show explicit complete-system language or both Joy-Con and dock evidence.
- Rejects bare HAC-001 / tested-working titles that may describe tablet-only hardware.
- Deduplicates final results by marketplace URL and normalized visible title so repeated listings cannot occupy the full top three.
- Adds duplicate-collapsed diagnostics to the QA workbench.
- Adds exact Switch-completeness and duplicate-title regression cases, bringing the backend suite to 156 passing tests.

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

## v0.3.6 â€” Hide lenses + eBay category IDs

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

## v0.4.3 â€” Click tracking and bad-result reporting

- Logs outbound eBay clicks through the `/api/out` redirect before sending users to eBay.
- Adds metadata to outbound clicks: query, category, product ID, provider, title, eBay item ID, and whether affiliate campaign tracking was present.
- Adds `POST /api/results/report` so users can flag bad marketplace results such as accessories, straps, parts, or the wrong model.
- Temporarily hides reported eBay item URLs for the matched product/category for 72 hours.
- Auto-prunes report storage to active reports only and caps it at 500 entries.
- Caps click storage at the latest 2,000 click events for lightweight MVP analytics.

## v0.4.4 â€” Analytics view and auction comparison

- Adds `/admin` so Scoutly's own click tracking can be viewed without waiting on eBay Partner reporting.
- Adds `GET /api/analytics/summary`, `/api/analytics/clicks`, and `/api/analytics/reports`.
- Supports optional `SCOUTLY_ADMIN_TOKEN`; when set, analytics endpoints and `/admin?token=...` require the token.
- Adds eBay auction search as a separate â€œAuction ending soonâ€ comparison section.
- Keeps Buy It Now as the primary result so auctions do not replace available-now deals.
- Uses eBay `buyingOptions:{AUCTION}` and `sort=endingSoonest` for auction comparison searches.

## v0.4.5 â€” Search cleanup, filtered-debug admin, and LEGO prototype

- Rejects camera-body listings that are actually filters, UV/CPL/ND filters, or other filter accessories.
- Rejects SXM/SXM2/SXM3/SXM4, mezzanine, and module results for normal Tesla P100/V100 searches so homelab users are steered toward PCIe cards.
- Keeps legitimate PCIe Tesla cards valid, including cards that mention passive heatsinks.
- Changes the search results page to use a more desktop-friendly horizontal result-card layout while staying mobile-friendly.
- Shows up to three eBay auctions ending soon as comparison options instead of only one auction.
- Adds filtered-listing logging so `/admin` can show eBay results that were rejected before ranking, including the reason.
- Adds `GET /api/analytics/filtered` for recent filtered-listing debug records.
- Adds LEGO as a lab category with eBay category filtering and 99 starter sets, focused on exact set-number matching.
- Keeps lenses paused in the active UI.

## v0.4.6 â€” Match-quality fixes

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

## v0.4.9 â€” Consoles + testing UX

- Added Consoles as a lab category covering Xbox, PlayStation, and Nintendo families.
- Added eBay Video Game Consoles category filtering for console searches.
- Search results now return up to three safe Buy It Now options instead of only one while categories are being tuned.
- Homepage now explains Scoutly's goal: complete used items, lowest useful prices, no partials, no broken/parts-only listings when detectable.
- Homepage now includes casual affiliate-link support wording and an incognito/private-search alternative.
- Added console accessory/partial filters for controller-only, dock-only, tablet-only, HDMI-port, power-supply, screen-only, shell-only, and similar listings.
- Added cleanup filters for recent reports: LEGO cartridge-only listings, minifigure-code/person listings, and GPU fan-missing listings.

## v0.5.1 â€” Performance pass

- Normal search no longer requests auction results by default.
- Search page keeps up to three Buy It Now results visible immediately.
- Adds a **View ending-soon auctions** button that reloads the search with auction comparison enabled.
- Keeps auctions separate from Buy It Now results and still shows up to three ending-soon auction cards when requested.
- Reduces eBay fixed-price search candidate limit from 50 to 35.
- Reduces eBay auction candidate limit from 50 to 25.
- Changes result lists to a responsive card grid so desktop can scan three results side-by-side.
- Adds lazy loading to result images.

## v0.5.3 â€” Trust and polish pass

- Adds stricter console cleanup for covers, accessory bundles, stick drift, monitor bundles, and game-only noise.
- Adds stricter LEGO cleanup for loose part listings like horses, beds, cartridges, and small lots while still allowing complete sets with normal piece-count wording.
- Demotes low-feedback sellers in ranking and shows a clearer low-feedback warning on result cards.
- Keeps zero-feedback sellers filtered out.
- Simplifies affiliate messaging on result cards to a small Affiliate link label while keeping the disclosure page/footer.
- Improves empty-state copy when a resolved product has no safe Buy It Now listings.
- Adds accessible labels, combobox/listbox roles, keyboard navigation, image alt text, and live status text for search/autocomplete.
- Adds dynamic search page titles like â€œXbox Series X deals | Scoutly.â€
- Adds Consoles to the admin live-rule category dropdown via dynamic category options.
- Adds report restore/delete support in admin for accidental bad-result flags.
- Adds normalizer caching to speed up catalog matching.

## v0.5.6 â€” Regression and trust fixes

- Replaces the sticky local submit flag with React transition state and remounts the compact form by category/query, fixing repeat searches that stayed disabled.
- Requires positive Joy-Con/controller/dock/completeness wording for full-size Nintendo Switch and Switch OLED listings.
- Converts invalid eBay seller sentinels (`0%` rating and negative feedback counts) to unavailable seller history.
- Adds Sony A1 II / ILCE-1M2 and prevents explicit generation queries from falling back to earlier camera generations.
- Tightens explicit GPU modifier/storage matching when users type clues such as Ti, XT, or 16GB.
- Improves selected Active/Lab badge contrast.
- Uses â€œaffiliate linksâ€ consistently in homepage copy.
- Uses resolved/unresolved-aware auction empty states.
- Adds regression coverage for Sony A1 II, Switch completeness, seller sentinels, and common LEGO set aliases.

## v0.5.9 â€” Result interaction and variation-price cleanup

- Makes listing images and titles clickable using the same tracked outbound link as the result button.
- Uses a full page navigation for each submitted search so old fixed-price or auction state cannot append to a new query.
- Rejects eBay seller-defined variation groups for consoles and GPUs because the visible price can belong to an accessory or lower-spec option.
- Rejects multi-model GPU titles such as RTX A3000/A4000/A5000 and adds GPU core, no-cooler, shell-only, and box-and-insert-only filters.
- Rejects camera service manuals and parts lists.
- Tightens Nintendo handheld filtering for accessory-only, game/manual, charger-only, and seller-selection listings while preserving complete console bundles that include chargers.
- Pauses Wii U until complete console + GamePad requirements are defined.
- Adds regression coverage for all newly reported titles and eBay variation metadata.

## v0.6.0

- Added the first reusable specification-builder flow with strict RAM searches.
- Added DDR3/DDR4/DDR5, desktop/laptop, total-capacity, stick-configuration, optional-speed, and optional-brand choices.
- Added dynamic RAM product resolution and category-specific eBay filtering.
- Added strict RAM conflict, ECC/server, unclear-kit, and seller-variation rejection.
- Promoted GPUs and Consoles to Active alongside Cameras.
- Rejected passive/server and external/eGPU variants for consumer desktop GPU searches.
- Strengthened LEGO packaging-only filtering and common EMPTY typo handling.
- Added transparent empty states with a broader tracked eBay Buy It Now search.

## v0.6.6

- Replaced the Console builder with direct exact-model autocomplete search.
- Removed dynamic console-family products from normal catalog resolution.
- Preserved original Nintendo Switch V1, V2, HAC-001, HAC-001(-01), Standard, and Original aliases.
- Retained multi-query original-Switch coverage and all v0.6.5 precision filters.


## v0.6.14 â€” Price snapshots and typical ranges

- Records live eligible Buy It Now prices in six-hour product/provider snapshots.
- Persists safe no-inventory snapshots for availability analysis.
- Adds current price context to search results and delays typical-range claims until enough history exists.
- Adds `/admin/prices` coverage and history dashboard.
- Adds a small rotating QA price collector while normal searches and QA runs collect automatically.
- Adds `scoutly_price_snapshots` PostgreSQL persistence with JSON-file fallback.
- Keeps all 88 QA cases and product-resolution behavior unchanged.
