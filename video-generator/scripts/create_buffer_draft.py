from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from buffer_client import graphql

EASTERN = ZoneInfo("America/Detroit")


def next_noon_eastern() -> str:
    now = datetime.now(EASTERN)
    candidate = now.replace(hour=12, minute=0, second=0, microsecond=0)
    if now.hour >= 11:
        candidate += timedelta(days=1)
    return candidate.astimezone(UTC).isoformat().replace("+00:00", "Z")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: create_buffer_draft.py PUBLIC_VIDEO_URL")
    public_video_url = sys.argv[1]
    project = Path(__file__).resolve().parents[1]
    story = json.loads((project / "work" / "story.json").read_text(encoding="utf-8"))
    target = json.loads((project / "work" / "buffer-target.json").read_text(encoding="utf-8"))

    api_key = os.environ["BUFFER_API_KEY"]
    channel_id = target["channel_id"]
    due_at = next_noon_eastern()

    query = """
    mutation CreatePriceSiftDraft($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post { id status dueAt text }
        }
        ... on MutationError { message }
      }
    }
    """
    variables = {
        "input": {
            "text": story["description"],
            "channelId": channel_id,
            "schedulingType": "automatic",
            "mode": "customScheduled",
            "dueAt": due_at,
            "saveToDraft": True,
            "aiAssisted": True,
            "assets": [{"video": {"url": public_video_url}}],
            "metadata": {
                "youtube": {
                    "title": story["title"],
                    "categoryId": "28",
                    "madeForKids": False,
                    "privacy": "public",
                    "isAiGenerated": True,
                    "embeddable": True,
                    "notifySubscribers": True,
                }
            },
        }
    }
    data = graphql(api_key, query, variables)
    result = data.get("createPost") or {}
    if result.get("message"):
        raise RuntimeError(f"Buffer rejected draft: {result['message']}")
    post = result.get("post")
    if not post:
        raise RuntimeError(f"Buffer returned no draft post: {data}")
    receipt = {
        "buffer_post_id": post.get("id"),
        "status": post.get("status"),
        "due_at": post.get("dueAt"),
        "title": story["title"],
        "video_url": public_video_url,
    }
    (project / "work" / "buffer-receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
