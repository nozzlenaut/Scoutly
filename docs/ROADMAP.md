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

## Later

- Price history
- Deal score
- Saved searches
- Email/Discord alerts
- User accounts
- More marketplaces
