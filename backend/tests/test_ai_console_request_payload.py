import asyncio

import app.services.ai_console_review as ai_console_review
from app.catalog.ai_console_beta import match_ai_console_beta_product
from app.models.listing import Listing


def test_console_review_requests_minimal_reasoning(monkeypatch):
    match = match_ai_console_beta_product("Nintendo Wii", "consoles")
    assert match is not None

    listing = Listing(
        provider="eBay",
        title="Nintendo Wii Console System Tested Working",
        price=49.99,
        shipping=0,
        total_price=49.99,
        condition="Used",
        seller_rating=99.5,
        seller_feedback_score=500,
        url="https://www.ebay.com/itm/test-wii",
    )
    config = ai_console_review._AIReviewConfig(
        api_key="test-key",
        model="gpt-5-nano",
        responses_url="https://api.openai.com/v1/responses",
        timeout_seconds=15.0,
    )
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": '{"decisions":[{"index":0,"keep":true,"reason":"target console"}]}',
                            }
                        ],
                    }
                ]
            }

    class FakeAsyncClient:
        def __init__(self, *, timeout):
            captured["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, *, headers, json):
            captured["url"] = url
            captured["headers"] = headers
            captured["payload"] = json
            return FakeResponse()

    monkeypatch.setattr(ai_console_review.httpx, "AsyncClient", FakeAsyncClient)

    decisions = asyncio.run(
        ai_console_review._request_decisions(config, match.product, [listing])
    )

    assert decisions == {0: (True, "target console")}
    assert captured["payload"]["model"] == "gpt-5-nano"
    assert captured["payload"]["reasoning"] == {"effort": "minimal"}
    assert captured["timeout"] == 15.0
