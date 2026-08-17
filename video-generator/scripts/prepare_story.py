from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from buffer_client import discover_youtube_target, recent_pricesift_history
from build_story import build_story
from story_selector import select_story


def fetch_pricesift_signals(base_url: str, admin_token: str) -> list[dict]:
    query = urllib.parse.urlencode({"token": admin_token, "days": 90, "limit": 100})
    url = f"{base_url.rstrip('/')}/api/prices/signals?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "PriceSift-Video/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return list(payload.get("signals") or [])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", help="Path to a signal payload fixture for deterministic render testing")
    args = parser.parse_args()

    project = Path(__file__).resolve().parents[1]
    work = project / "work"
    work.mkdir(parents=True, exist_ok=True)

    if args.fixture:
        fixture_path = (project / args.fixture).resolve()
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        signals = list(payload.get("signals") or payload)
        history = list(payload.get("history") or []) if isinstance(payload, dict) else []
    else:
        required = {
            "PRICESIFT_BASE_URL": os.environ.get("PRICESIFT_BASE_URL"),
            "PRICESIFT_ADMIN_TOKEN": os.environ.get("PRICESIFT_ADMIN_TOKEN"),
            "BUFFER_API_KEY": os.environ.get("BUFFER_API_KEY"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Missing live pipeline configuration: {', '.join(missing)}")
        signals = fetch_pricesift_signals(required["PRICESIFT_BASE_URL"], required["PRICESIFT_ADMIN_TOKEN"])
        organization_id, channel_id = discover_youtube_target(required["BUFFER_API_KEY"])
        (work / "buffer-target.json").write_text(
            json.dumps({"organization_id": organization_id, "channel_id": channel_id}, indent=2),
            encoding="utf-8",
        )
        history = recent_pricesift_history(
            api_key=required["BUFFER_API_KEY"],
            organization_id=organization_id,
            channel_id=channel_id,
            signals=signals,
        )

    selection = select_story(signals, history)
    decision = {"selected": bool(selection)}
    if selection is None:
        (work / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
        print("No eligible PriceSift story today. No video will be generated.")
        return

    story = build_story(selection)
    (work / "selection.json").write_text(json.dumps(selection, indent=2), encoding="utf-8")
    (work / "story.json").write_text(json.dumps(story, indent=2), encoding="utf-8")
    decision.update(
        {
            "product_id": story["product_id"],
            "product_label": story["product_label"],
            "story_type": story["story_type"],
            "title": story["title"],
        }
    )
    (work / "decision.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    print(f"Selected: {story['story_type']} | {story['title']}")


if __name__ == "__main__":
    main()
