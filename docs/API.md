# Scoutly API

## GET /health

Returns service status.

## GET /api/products

Query parameters:

| Name | Type | Required | Description |
|---|---|---:|---|
| category | string | no | Product category, e.g. `cameras`, `lenses`, `gpus` |

## GET /api/products/suggest

Query parameters:

| Name | Type | Required | Description |
|---|---|---:|---|
| q | string | yes | Search query, e.g. `a7iii` |
| category | string | no | Product category, e.g. `cameras` |
| limit | number | no | Max suggestions to return |

Example:

```text
/api/products/suggest?q=sony%2024-70&category=lenses&limit=8
```

## GET /api/products/resolve

Query parameters:

| Name | Type | Required | Description |
|---|---|---:|---|
| q | string | yes | Search query |
| category | string | no | Product category |

## GET /api/search

Query parameters:

| Name | Type | Required | Description |
|---|---|---:|---|
| q | string | yes | Search query, e.g. `Sony A7 III Body` |
| category | string | no | Product category, e.g. `cameras` |
| providers | string | no | Comma-separated provider list, e.g. `ebay,amazon` |

Example:

```text
/api/search?q=sony%20a7iii&category=cameras&providers=ebay,amazon
```

## Feedback and outbound tracking

### `GET /api/out`

Redirects allowed eBay URLs through Scoutly so affiliate parameters are applied and a lightweight click event is recorded.

Optional metadata query params:

```text
provider=eBay
category=cameras
product_id=camera-sony-a7-iii-body
q=Sony A7 III Body
title=Sony Alpha a7 III
```

### `POST /api/results/report`

Flags a marketplace result as bad for the current product/category. The link is hidden for 72 hours.

```json
{
  "url": "https://www.ebay.com/itm/123456789012",
  "title": "Camera Strap for Sony A7 III",
  "provider": "eBay",
  "category": "cameras",
  "product_id": "camera-sony-a7-iii-body",
  "query": "Sony A7 III Body",
  "reason": "accessory_or_part"
}
```

## Analytics endpoints

These are lightweight MVP endpoints for viewing Scoutly's own outbound click tracking and active bad-result reports.

If `SCOUTLY_ADMIN_TOKEN` is set, include `?token=<token>`.

```text
GET /api/analytics/summary
GET /api/analytics/clicks?limit=50
GET /api/analytics/reports?limit=50
```

## Search with auctions

Search now returns both primary Buy It Now results and a separate auction comparison list.

```text
GET /api/search?q=Sony%20A7%20III%20Body&category=cameras&providers=ebay&include_auctions=true&auction_hours=24
```

Response fields:

```json
{
  "results": [],
  "auction_results": []
}
```

## Search QA endpoints

These private endpoints power the `/admin/qa` workbench and require the existing `SCOUTLY_ADMIN_TOKEN` as `?token=<token>`.

```text
GET /api/qa/cases
GET /api/qa/evaluations?limit=200
POST /api/qa/evaluations
```

`GET /api/qa/cases` returns the seeded regression cases, each case's latest saved evaluation, attempt counts, and aggregate summary metrics. `quality_rate` measures usable top-three results only among cases with eligible inventory; `overall_rate` includes safe no-inventory outcomes, and `available_inventory_cases` exposes the denominator used for quality.

Example evaluation payload:

```json
{
  "case_id": "console-model-v2-switch",
  "category": "consoles",
  "query": "Nintendo Switch",
  "expected_product_id": "console-nintendo-switch",
  "expected_label": "Nintendo Switch",
  "resolved_product_id": "console-nintendo-switch",
  "resolved_label": "Nintendo Switch",
  "resolution_correct": true,
  "outcome": "pass",
  "issue_tags": [],
  "notes": "All three listings were complete systems.",
  "result_titles": ["Nintendo Switch V2 Console Complete"],
  "diagnostics": {
    "fixed_price_candidates": 12,
    "fixed_price_filtered": 8
  }
}
```

## Price history

Resolved live searches include a `price_context` object containing the current eligible-price range and, after enough snapshots exist, a typical recent range and comparison with the recent median.

Private price administration uses the existing `SCOUTLY_ADMIN_TOKEN`:

```text
GET /api/prices/overview?token=<token>&days=30
POST /api/prices/collect/qa?token=<token>
```

Collector payload:

```json
{
  "limit": 5,
  "category": "cpus"
}
```

Public product context is also available for a known product ID:

```text
GET /api/prices/cpu-intel-core-i7-12700k?days=30
```

## Public Books ISBN search

Books use a separate exact-identifier flow rather than the normal product catalog resolver.

```text
GET /api/books/search?isbn=9780345539809&limit=35
```

The endpoint validates ISBN-10/ISBN-13 check digits, tries ISBN-13 first and ISBN-10 only as a fallback, returns standard used copies in `top_results`, and separates signed/deluxe/collectible copies in `collectible_results`. Study guides, summaries, workbooks, companion products, and incoherent catalog matches are rejected.

Private diagnostics remain available with the admin token:

```text
GET /api/books/lab/status?token=<token>
GET /api/books/lab/search?token=<token>&isbn=9780345539809
```
