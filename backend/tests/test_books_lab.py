import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.models.listing import Listing
from app.services.book_isbn import (
    isbn10_to_isbn13,
    isbn13_to_isbn10,
    isbn_identity,
    is_valid_isbn10,
    is_valid_isbn13,
    search_used_books_by_isbn,
)


class _FakeBookProvider:
    def __init__(self):
        self.queries: list[str] = []

    async def search_gtin(self, gtin: str, category: str = "books", limit: int = 35):
        self.queries.append(gtin)
        suffix = "1" if gtin.startswith("978") else "2"
        return [
            Listing(
                provider="eBay",
                title="The Expanse Book One",
                price=8.0 if suffix == "1" else 9.0,
                shipping=0,
                total_price=8.0 if suffix == "1" else 9.0,
                condition="Very Good",
                url=f"https://www.ebay.com/itm/12345{suffix}",
            ),
            Listing(
                provider="eBay",
                title="The Expanse Book One",
                price=8.0,
                shipping=0,
                total_price=8.0,
                condition="Brand New",
                url="https://www.ebay.com/itm/new-copy",
            ),
        ]


def test_isbn_validation_and_conversion():
    assert is_valid_isbn10("0-306-40615-2")
    assert is_valid_isbn13("978-0-306-40615-7")
    assert isbn10_to_isbn13("0306406152") == "9780306406157"
    assert isbn13_to_isbn10("9780306406157") == "0306406152"
    identity = isbn_identity("978-0-306-40615-7")
    assert identity["valid"] is True
    assert identity["isbn10"] == "0306406152"
    assert identity["query_isbns"] == ["9780306406157", "0306406152"]


def test_invalid_isbn_returns_no_marketplace_results():
    provider = _FakeBookProvider()
    payload = asyncio.run(search_used_books_by_isbn("1234567890", provider=provider))
    assert payload["isbn"]["valid"] is False
    assert payload["results"] == []
    assert provider.queries == []


def test_book_lab_searches_both_isbns_and_keeps_used_only():
    provider = _FakeBookProvider()
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert provider.queries == ["9780306406157", "0306406152"]
    assert payload["candidate_count"] == 4
    assert payload["eligible_count"] == 2
    assert payload["duplicates_removed"] == 0
    assert payload["rejection_reasons"]["Not a used-book condition"] == 2
    assert len(payload["top_results"]) == 2


def test_books_admin_endpoints_require_token(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)
    assert client.get("/api/books/lab/status").status_code == 401
    assert client.get("/api/books/lab/status", params={"token": "secret"}).status_code == 200
