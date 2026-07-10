# Scoutly Database Notes

Database is not required for Sprint 1.

Future tables:

## products

- id
- category
- brand
- model
- variant
- aliases
- active

## listings

- id
- provider
- external_id
- title
- price
- shipping
- condition
- seller_rating
- url
- image_url
- fetched_at

## price_snapshots

- id
- product_id
- provider
- total_price
- listing_url
- captured_at

## outbound_clicks

- id
- provider
- listing_url
- affiliate_url
- clicked_at
