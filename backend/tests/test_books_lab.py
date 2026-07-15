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


def _listing(title: str, url_suffix: str, *, condition: str = "Very Good", price: float = 8.0) -> Listing:
    return Listing(
        provider="eBay",
        title=title,
        price=price,
        shipping=0,
        total_price=price,
        condition=condition,
        url=f"https://www.ebay.com/itm/{url_suffix}",
    )


class _FakeBookProvider:
    def __init__(self, responses: dict[str, list[Listing]] | None = None):
        self.queries: list[str] = []
        self.responses = responses or {}

    async def search_gtin(self, gtin: str, category: str = "books", limit: int = 35):
        self.queries.append(gtin)
        if gtin in self.responses:
            return self.responses[gtin]
        return [
            _listing("The Expanse Book One", f"12345-{gtin}", price=8.0),
            _listing("The Expanse Book One", f"new-{gtin}", condition="Brand New", price=9.0),
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
    assert payload["query_attempts"] == []
    assert provider.queries == []


def test_books_lab_uses_isbn13_first_and_does_not_merge_fallback_when_primary_is_clean():
    provider = _FakeBookProvider()
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert provider.queries == ["9780306406157"]
    assert payload["candidate_count"] == 2
    assert payload["eligible_count"] == 1
    assert payload["rejection_reasons"]["Not a used-book condition"] == 1
    assert payload["selected_query_isbn"] == "9780306406157"
    assert payload["fallback_used"] is False
    assert len(payload["top_results"]) == 1


def test_books_lab_uses_isbn10_only_when_primary_has_no_eligible_results():
    provider = _FakeBookProvider(
        {
            "9780306406157": [_listing("Theoretical Physics", "new-only", condition="Brand New")],
            "0306406152": [_listing("Theoretical Physics", "used-copy")],
        }
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert provider.queries == ["9780306406157", "0306406152"]
    assert payload["selected_query_isbn"] == "0306406152"
    assert payload["fallback_used"] is True
    assert payload["eligible_count"] == 1


def test_books_lab_rejects_mass_nonsense_and_uses_coherent_fallback_cluster():
    random_titles = [
        "Gardening for Beginners",
        "The Complete Cookbook",
        "World Atlas Revised",
        "Mystery at the Manor",
        "Introduction to Algebra",
        "A History of Michigan",
    ]
    coherent_titles = [
        "Red Rising by Pierce Brown",
        "Red Rising Book One Pierce Brown",
        "Red Rising Paperback Pierce Brown",
        "Pierce Brown Red Rising Novel",
        "Red Rising The Red Rising Saga",
    ]
    provider = _FakeBookProvider(
        {
            "9780306406157": [_listing(title, f"random-{index}") for index, title in enumerate(random_titles)],
            "0306406152": [_listing(title, f"red-{index}") for index, title in enumerate(coherent_titles)],
        }
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert provider.queries == ["9780306406157", "0306406152"]
    assert payload["fallback_used"] is True
    assert payload["eligible_count"] == 5
    assert payload["rejection_reasons"]["Unverified or inconsistent title identity"] == 6
    assert all("Red Rising" in result["title"] or "red rising" in result["title"].lower() for result in payload["results"])


def test_books_lab_fails_safely_when_both_isbn_queries_are_incoherent():
    random_titles = [
        "Gardening for Beginners",
        "The Complete Cookbook",
        "World Atlas Revised",
        "Mystery at the Manor",
        "Introduction to Algebra",
        "A History of Michigan",
    ]
    provider = _FakeBookProvider(
        {
            "9780306406157": [_listing(title, f"primary-{index}") for index, title in enumerate(random_titles)],
            "0306406152": [_listing(title, f"fallback-{index}") for index, title in enumerate(reversed(random_titles))],
        }
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert provider.queries == ["9780306406157", "0306406152"]
    assert payload["eligible_count"] == 0
    assert payload["top_results"] == []
    assert payload["selected_query_isbn"] is None


def test_books_lab_accepts_a_coherent_single_word_title_cluster():
    provider = _FakeBookProvider(
        {
            "9780306406157": [
                _listing("Dune by Frank Herbert", "dune-1"),
                _listing("Dune Paperback", "dune-2"),
                _listing("Frank Herbert Dune", "dune-3"),
                _listing("Dune Movie Tie-In", "dune-4"),
                _listing("Dune", "dune-5"),
            ]
        }
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert provider.queries == ["9780306406157"]
    assert payload["eligible_count"] == 5
    assert "dune" in payload["query_attempts"][0]["consensus_tokens"]


def test_books_admin_endpoints_require_token(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)
    assert client.get("/api/books/lab/status").status_code == 401
    assert client.get("/api/books/lab/status", params={"token": "secret"}).status_code == 200
