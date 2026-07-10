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
