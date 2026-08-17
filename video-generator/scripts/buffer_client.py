from __future__ import annotations

import json
import urllib.request
from datetime import UTC, datetime, timedelta
from typing import Any

BUFFER_API_URL = "https://api.buffer.com"


def graphql(api_key: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        BUFFER_API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "PriceSift-Video/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("errors"):
        raise RuntimeError(f"Buffer GraphQL error: {payload['errors']}")
    return payload.get("data") or {}


def _story_from_title(title: str) -> str | None:
    lowered = title.lower()
    if "jumped" in lowered and "catch" in lowered:
        return "price_spike_with_bargain"
    if "used prices just dropped" in lowered or "used prices dropped" in lowered:
        return "price_drop"
    if "used prices jumped" in lowered:
        return "price_spike"
    if "way below" in lowered or "recent used median" in lowered:
        return "hidden_bargain"
    if "inventory" in lowered and "jumped" in lowered:
        return "inventory_surge"
    if "inventory" in lowered and "dropped" in lowered:
        return "inventory_squeeze"
    return None


def recent_pricesift_history(
    *,
    api_key: str,
    organization_id: str,
    channel_id: str,
    signals: list[dict[str, Any]],
    days: int = 45,
) -> list[dict[str, Any]]:
    query = """
    query RecentPriceSiftPosts($organizationId: OrganizationId!, $channelId: ChannelId!, $startDate: DateTime!) {
      posts(first: 100, input: {
        organizationId: $organizationId,
        filter: {
          channelIds: [$channelId],
          startDate: $startDate,
          status: [draft, needs_approval, scheduled, sending, sent]
        }
      }) {
        edges {
          node {
            id
            status
            text
            createdAt
            sentAt
            dueAt
            metadata {
              ... on YoutubePostMetadata { title }
            }
          }
        }
      }
    }
    """
    start = (datetime.now(UTC) - timedelta(days=days)).isoformat().replace("+00:00", "Z")
    data = graphql(
        api_key,
        query,
        {"organizationId": organization_id, "channelId": channel_id, "startDate": start},
    )
    edges = ((data.get("posts") or {}).get("edges") or [])
    history: list[dict[str, Any]] = []
    for edge in edges:
        node = edge.get("node") or {}
        metadata = node.get("metadata") or {}
        title = str(metadata.get("title") or "")
        text = str(node.get("text") or "")
        haystack = f"{title}\n{text}".casefold()
        matched: dict[str, Any] | None = None
        for signal in signals:
            label = str(signal.get("product_label") or "").strip()
            if label and label.casefold() in haystack:
                matched = signal
                break
        history.append(
            {
                "buffer_post_id": node.get("id"),
                "status": node.get("status"),
                "created_at": node.get("createdAt"),
                "sent_at": node.get("sentAt"),
                "due_at": node.get("dueAt"),
                "title": title,
                "pricesift_generated": "pricesift tracks clean used listings" in text.casefold(),
                "product_id": matched.get("product_id") if matched else None,
                "product_label": matched.get("product_label") if matched else None,
                "category": matched.get("category") if matched else None,
                "story_type": _story_from_title(title),
            }
        )
    return history
