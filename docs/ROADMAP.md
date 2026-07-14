# Scoutly Roadmap

## Current MVP direction

The MVP is a simple category-based search flow:

```text
Pick category
↓
Start typing item
↓
Choose exact autocomplete result
↓
Scoutly checks a marketplace
↓
Show the best used result
```

## v0.2.2 - Category Search

- Category picker on the homepage
- Cameras and Lenses as active starter categories
- Generic product catalog model
- Starter photography catalog
- GPU catalog kept as a PC-parts lab category

## v0.3.0 - eBay Provider

- Add eBay Browse API credentials support
- Add eBay provider
- Search eBay using the resolved canonical product
- Filter bad used listings
- Return the best eBay result for Cameras, Lenses, and GPUs

## v0.4.0 - Affiliate Redirects

- Add outbound redirect route
- Track clicks
- Add eBay Partner Network links
- Add affiliate disclosure page

## v0.5.0 - Product Catalog Expansion

- Add more camera bodies
- Add more lenses
- Add grouped categories, such as Photography and PC Parts, if the category bar gets crowded
- Add category-specific metadata and filters


## v0.6.7 - Search QA validation

- Add a repeatable admin QA workbench
- Seed Console and LEGO regression cases
- Track expected resolution, live top-three quality, issue tags, and notes
- Establish measurable category quality before expanding into another product category

## v0.6.8 - Grouped console models

- Make the core console model the searchable identity
- Group storage, color, drive, revision, and bundle variants underneath
- Pause Console variant narrowing until core-model result quality is proven
- Reset the Console QA benchmark while retaining LEGO evaluations

## v0.6.9 - Console listing quality pass

- Filter the accessory, replacement-part, packaging-only, game, and wrong-generation titles found during live Console QA
- Preserve quality-score ordering through the final result list
- Expose eligible counts and rejection-reason diagnostics in the QA workbench
- Rerun the unchanged 16 core-model Console benchmark before adding categories or variant narrowing

## v0.6.10 - Switch completeness and result deduplication

- Require evidence that standard Nintendo Switch listings include a complete V1/V2 system
- Collapse duplicate item URLs and duplicate visible titles before selecting the top three
- Expose duplicate-collapsed counts in QA diagnostics
- Run the final unchanged 16-case Console benchmark before expanding categories

## v0.6.11 - CPU builder and full-category QA

- Add consumer desktop CPUs as an active exact-model category
- Keep meaningful CPU suffix variants separate while presenting them in one final model picker
- Filter bundles, accessories, lots, samples, damaged chips, and mobile/server conflicts
- Expand the QA workbench to Cameras, GPUs, RAM, CPUs, Consoles, and LEGO
- Preserve existing Console and LEGO evaluation history

## v0.6.12 - Cross-category quality cleanup

- Reject faulty/partially functional electronics and mixed-speed RAM kits
- Require LEGO set-number and canonical-name agreement
- Reject LEGO sub-build, manual-only, and individual-brick listings
- Separate inventory-adjusted QA quality from availability and overall outcomes
- Preserve the 88-case regression suite for periodic full sweeps

## Later

- Price history
- Deal score
- Saved searches
- Email/Discord alerts
- User accounts
- More marketplaces
