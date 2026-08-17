from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from story_selector import classify_story, select_story

NOW = datetime(2026, 8, 17, 13, 0, tzinfo=UTC)


def signal(product_id: str, label: str, *, story: str = "price_drop", score: float = 60.0, category: str = "gpus"):
    primary = story
    tags = [story]
    move = -12.0 if story == "price_drop" else 15.0
    best = 250.0
    current = 300.0
    if story == "standout_deal":
        move = 1.0
        current = 330.0
        best = 250.0
    return {
        "product_id": product_id,
        "product_label": label,
        "category": category,
        "primary_signal": primary,
        "signal_tags": tags,
        "video_score": score,
        "video_worthy": True,
        "confidence": "high",
        "latest_best_price": best,
        "latest_median_price": current,
        "baseline_median_price": 340.0,
        "latest_eligible_count": 10,
        "median_change_percent": move,
        "inventory_change_percent": 0.0,
    }


def history(product_id: str, *, days_ago: int = 1, story_type: str = "price_drop", category: str = "gpus", status: str = "sent", generated: bool = True):
    when = NOW - timedelta(days=days_ago)
    return {
        "status": status,
        "sent_at": when.isoformat() if status == "sent" else None,
        "created_at": when.isoformat(),
        "product_id": product_id,
        "story_type": story_type,
        "category": category,
        "pricesift_generated": generated,
    }


class StorySelectorTests(unittest.TestCase):
    def test_spike_plus_large_floor_gap_becomes_contradiction_story(self):
        row = signal("a770", "Intel Arc A770", story="price_spike")
        row["latest_median_price"] = 420.0
        row["latest_best_price"] = 299.99
        self.assertEqual(classify_story(row), "price_spike_with_bargain")

    def test_no_noteworthy_signal_means_no_video(self):
        row = signal("one", "One")
        row["video_worthy"] = False
        self.assertIsNone(select_story([row], [], now=NOW))

    def test_same_product_is_blocked_during_30_day_cooldown(self):
        row = signal("one", "One")
        self.assertIsNone(select_story([row], [history("one", days_ago=10)], now=NOW))

    def test_product_becomes_eligible_after_cooldown(self):
        row = signal("one", "One")
        selected = select_story([row], [history("one", days_ago=31)], now=NOW)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["signal"]["product_id"], "one")

    def test_different_product_can_follow_previous_post(self):
        rows = [signal("one", "One", score=90), signal("two", "Two", score=55)]
        selected = select_story(rows, [history("one", days_ago=1)], now=NOW)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["signal"]["product_id"], "two")

    def test_pending_draft_blocks_duplicate_product(self):
        row = signal("one", "One")
        pending = history("one", days_ago=1, status="draft")
        self.assertIsNone(select_story([row], [pending], now=NOW))

    def test_existing_generated_draft_today_stops_second_video(self):
        row = signal("two", "Two")
        existing = {
            "status": "draft",
            "created_at": NOW.isoformat(),
            "product_id": "one",
            "pricesift_generated": True,
        }
        self.assertIsNone(select_story([row], [existing], now=NOW))

    def test_fresher_story_type_can_beat_higher_repetitive_score(self):
        repeated = signal("two", "Two", story="price_drop", score=62)
        fresh = signal("three", "Three", story="inventory_surge", score=58, category="consoles")
        recent = history("one", days_ago=2, story_type="price_drop", category="gpus")
        selected = select_story([repeated, fresh], [recent], now=NOW)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["signal"]["product_id"], "three")


if __name__ == "__main__":
    unittest.main()
