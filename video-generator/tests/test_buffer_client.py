from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from buffer_client import discover_youtube_target


class BufferTargetDiscoveryTests(unittest.TestCase):
    @patch("buffer_client.graphql")
    def test_prefers_pricesift_youtube_channel(self, graphql):
        graphql.side_effect = [
            {"account": {"organizations": [{"id": "org-1", "name": "Main"}]}},
            {
                "channels": [
                    {"id": "yt-other", "name": "Repair Lab", "displayName": "Repair Lab", "service": "youtube", "isDisconnected": False, "isLocked": False},
                    {"id": "yt-pricesift", "name": "PriceSift", "displayName": "PriceSift", "service": "youtube", "isDisconnected": False, "isLocked": False},
                ]
            },
        ]
        self.assertEqual(discover_youtube_target("key"), ("org-1", "yt-pricesift"))

    @patch("buffer_client.graphql")
    def test_uses_only_connected_youtube_channel(self, graphql):
        graphql.side_effect = [
            {"account": {"organizations": [{"id": "org-1", "name": "Main"}]}},
            {
                "channels": [
                    {"id": "yt-1", "name": "Channel", "displayName": "Channel", "service": "youtube", "isDisconnected": False, "isLocked": False},
                    {"id": "x-1", "name": "Other", "displayName": "Other", "service": "twitter", "isDisconnected": False, "isLocked": False},
                ]
            },
        ]
        self.assertEqual(discover_youtube_target("key"), ("org-1", "yt-1"))

    @patch("buffer_client.graphql")
    def test_multiple_unmatched_youtube_channels_fail_safe(self, graphql):
        graphql.side_effect = [
            {"account": {"organizations": [{"id": "org-1", "name": "Main"}]}},
            {
                "channels": [
                    {"id": "yt-1", "name": "One", "displayName": "One", "service": "youtube", "isDisconnected": False, "isLocked": False},
                    {"id": "yt-2", "name": "Two", "displayName": "Two", "service": "youtube", "isDisconnected": False, "isLocked": False},
                ]
            },
        ]
        with self.assertRaisesRegex(RuntimeError, "multiple YouTube channels"):
            discover_youtube_target("key")


if __name__ == "__main__":
    unittest.main()
