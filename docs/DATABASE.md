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

## Current persistence tables

When `DATABASE_URL` is configured, Scoutly creates its operational tables automatically at API startup. The search QA workbench adds:

### scoutly_qa_evaluations

- id
- case_id
- category
- query
- expected_product_id
- expected_label
- resolved_product_id
- resolved_label
- resolution_correct
- outcome
- issue_tags
- notes
- result_titles
- diagnostics
- created_at

Local development falls back to `qa_evaluations.json` inside `SCOUTLY_DATA_DIR` (or `/tmp/scoutly`).

### scoutly_price_snapshots

Price observations are grouped into six-hour provider/product buckets and upserted so repeated page refreshes do not flood storage.

- id
- snapshot_bucket
- observed_at
- product_id
- category
- product_label
- provider
- query
- source
- candidate_count
- filtered_count
- eligible_count
- lowest_price
- median_price
- p25_price
- p75_price
- sample_prices

The unique key is `(product_id, provider, snapshot_bucket)`. Local development falls back to `price_snapshots.json` inside `SCOUTLY_DATA_DIR` or `/tmp/scoutly`.
