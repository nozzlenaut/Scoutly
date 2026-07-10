# Scoutly API

## GET /health

Returns service status.

## GET /api/search

Query parameters:

| Name | Type | Required | Description |
|---|---|---:|---|
| q | string | yes | Search query, e.g. RTX 3060 12GB |
| providers | string | no | Comma-separated provider list, e.g. ebay,amazon |

Example:

```text
/api/search?q=rtx%203060%2012gb&providers=ebay,amazon
```
