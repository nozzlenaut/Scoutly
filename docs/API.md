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

`GET /api/qa/cases` returns the seeded regression cases, each case's latest saved evaluation, attempt counts, and aggregate summary metrics.

Example evaluation payload:

```json
{
  "case_id": "console-switch-v2",
  "category": "consoles",
  "query": "Nintendo Switch V2",
  "expected_product_id": "console-nintendo-switch-v1-v2",
  "expected_label": "Nintendo Switch V1/V2",
  "resolved_product_id": "console-nintendo-switch-v1-v2",
  "resolved_label": "Nintendo Switch V1/V2",
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
