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
