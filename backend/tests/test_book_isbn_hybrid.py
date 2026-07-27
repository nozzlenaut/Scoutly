from __future__ import annotations

import asyncio

from app.models.listing import Listing
from app.services.book_isbn import search_used_books_by_isbn


def listing(
    title: str,
    *,
    description: str | None = None,
    item_id: str = "1",
) -> Listing:
    return Listing(
        provider="eBay",
        title=title,
        description=description,
        price=5.0,
        shipping=0.0,
        total_price=5.0,
        condition="Very Good",
        url=f"https://www.ebay.com/itm/{item_id}",
        marketplace_item_id=item_id,
    )


class FakeProvider:
    def __init__(
        self,
        *,
        gtin_results: dict[str, list[Listing]] | None = None,
        keyword_results: dict[str, list[Listing]] | None = None,
    ) -> None:
        self.gtin_results = gtin_results or {}
        self.keyword_results = keyword_results or {}
        self.keyword_calls: list[str] = []

    async def search_gtin(
        self,
        gtin: str,
        category: str = "books",
        limit: int = 35,
        item_location_country: str | None = None,
    ) -> list[Listing]:
        return list(self.gtin_results.get(gtin, []))

    async def search(
        self,
        query: str,
        category: str | None = None,
        buying_option: str = "fixed_price",
        item_location_country: str | None = None,
    ) -> list[Listing]:
        self.keyword_calls.append(query)
        return list(self.keyword_results.get(query, []))


def test_hybrid_search_rejects_gtin_catalog_drift_and_recovers_verified_keyword() -> None:
    isbn13 = "9780553803709"
    provider = FakeProvider(
        gtin_results={
            isbn13: [
                listing(
                    "Completely Unrelated Paperback",
                    item_id="wrong",
                )
            ]
        },
        keyword_results={
            isbn13: [
                listing(
                    "I, Robot by Isaac Asimov ISBN 9780553803709",
                    description="ISBN-10 0553803700",
                    item_id="correct",
                )
            ]
        },
    )

    result = asyncio.run(
        search_used_books_by_isbn(
            isbn13,
            provider=provider,
            expected_title="I, Robot (Robot, #0.1)",
            expected_author="Isaac Asimov",
        )
    )

    assert result["selected_match_method"] == "keyword_isbn_verified"
    assert result["top_results"][0]["marketplace_item_id"] == "correct"
    assert (
        result["rejection_reasons"]["Listing title does not match Goodreads book"]
        == 1
    )


def test_hybrid_search_keeps_valid_gtin_result_without_keyword_call() -> None:
    isbn13 = "9780063204157"
    provider = FakeProvider(
        gtin_results={
            isbn13: [
                listing(
                    "Remarkably Bright Creatures by Shelby Van Pelt",
                    item_id="gtin",
                )
            ]
        }
    )

    result = asyncio.run(
        search_used_books_by_isbn(
            isbn13,
            provider=provider,
            expected_title="Remarkably Bright Creatures",
            expected_author="Shelby Van Pelt",
        )
    )

    assert result["selected_match_method"] == "gtin_title_verified"
    assert result["top_results"][0]["marketplace_item_id"] == "gtin"
    assert provider.keyword_calls == []


def test_keyword_fallback_requires_visible_exact_isbn() -> None:
    isbn13 = "9781250275035"
    provider = FakeProvider(
        keyword_results={
            isbn13: [
                listing(
                    "Mickey7 by Edward Ashton",
                    description="A clean hardcover copy.",
                    item_id="unverified",
                )
            ],
            "1250275032": [],
        }
    )

    result = asyncio.run(
        search_used_books_by_isbn(
            isbn13,
            provider=provider,
            expected_title="Mickey7 (Mickey7 #1)",
            expected_author="Edward Ashton",
        )
    )

    assert result["top_results"] == []
    assert result["selected_match_method"] is None
    assert result["rejection_reasons"]["Exact ISBN not visible in listing"] == 1


def test_numeric_goodreads_title_can_verify_gtin_result() -> None:
    isbn13 = "9780451524935"
    provider = FakeProvider(
        gtin_results={
            isbn13: [
                listing(
                    "1984 by George Orwell Paperback",
                    item_id="numeric",
                )
            ]
        }
    )

    result = asyncio.run(
        search_used_books_by_isbn(
            isbn13,
            provider=provider,
            expected_title="1984",
            expected_author="George Orwell",
        )
    )

    assert result["selected_match_method"] == "gtin_title_verified"
    assert result["top_results"][0]["marketplace_item_id"] == "numeric"
