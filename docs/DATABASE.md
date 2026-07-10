# Scoutly Database Notes

Database is not required for the current local prototype.

Future tables:

## products

- id
- category
- category_label
- product_type
- brand
- model
- variant
- aliases
- required_terms
- excluded_terms
- metadata
- active

## listings

- id
- product_id
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
