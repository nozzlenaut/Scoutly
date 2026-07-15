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


def test_books_rejects_study_guides_and_companion_products():
    provider = _FakeBookProvider(
        {
            "9780306406157": [
                _listing("Brave New World by Aldous Huxley", "book", price=7),
                _listing("Brave New World Study Guide and Analysis", "study", price=3),
                _listing("Workbook Companion to Brave New World", "workbook", price=4),
            ]
        }
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert payload["standard_count"] == 1
    assert payload["top_results"][0]["title"] == "Brave New World by Aldous Huxley"
    assert payload["rejection_reasons"]["Study guide or companion material"] == 1
    assert payload["rejection_reasons"]["Workbook or companion material"] == 1


def test_books_separates_collectible_price_outliers_from_default_top_three():
    provider = _FakeBookProvider(
        {
            "9780306406157": [
                _listing("Snow Crash Paperback", "standard", price=9),
                _listing("Snow Crash Signed Deluxe Edition", "signed", price=175),
            ]
        }
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert payload["standard_count"] == 1
    assert payload["collectible_count"] == 1
    assert len(payload["top_results"]) == 1
    assert payload["top_results"][0]["title"] == "Snow Crash Paperback"
    assert "Collectible" in payload["collectible_results"][0]["warning_labels"][0]


def test_books_adds_caution_for_seller_supplied_edition_year():
    provider = _FakeBookProvider(
        {"9780306406157": [_listing("The Great Gatsby 2018 Edition", "gatsby", price=8)]}
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert payload["standard_count"] == 1
    assert any("edition year" in warning.lower() for warning in payload["top_results"][0]["warning_labels"])


def test_public_books_endpoint_does_not_require_admin_token(monkeypatch):
    async def fake_search(*args, **kwargs):
        return {"isbn": {"valid": True}, "top_results": [], "results": [], "collectible_results": []}

    monkeypatch.setattr("app.api.books.search_used_books_by_isbn", fake_search)
    client = TestClient(app)
    response = client.get("/api/books/search", params={"isbn": "9780306406157"})
    assert response.status_code == 200


def test_books_admin_endpoints_require_token(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)
    assert client.get("/api/books/lab/status").status_code == 401
    assert client.get("/api/books/lab/status", params={"token": "secret"}).status_code == 200


def test_books_rejects_unrelated_common_word_from_dominant_title_cluster():
    provider = _FakeBookProvider(
        {
            "9780306406157": [
                _listing("Atomic Habits by James Clear", f"atomic-{index}", price=8 + index)
                for index in range(8)
            ]
            + [_listing("Dr. A's Habits of Health by Wayne Scott Andersen", "wrong-habits", price=4)]
        }
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert payload["standard_count"] == 8
    assert all("Atomic Habits" in result["title"] for result in payload["results"])
    assert payload["rejection_reasons"]["Unverified or inconsistent title identity"] == 1


def test_books_separates_multi_book_lots_from_single_copy_results():
    provider = _FakeBookProvider(
        {
            "9780306406157": [
                _listing("The Name of the Wind Paperback", "single", price=9),
                _listing("The Name of the Wind + Wise Man's Fear 2 Book Lot", "lot", price=14),
                _listing("Heretics of Dune and Chapterhouse Dune Set of 2 Books", "bundle", price=18),
            ]
        }
    )
    payload = asyncio.run(search_used_books_by_isbn("9780306406157", provider=provider))
    assert payload["standard_count"] == 1
    assert payload["bundle_count"] == 2
    assert payload["top_results"][0]["title"] == "The Name of the Wind Paperback"
    assert all("Multi-book" in result["warning_labels"][0] for result in payload["bundle_results"])
