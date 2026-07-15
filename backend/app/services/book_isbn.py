from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.models.listing import Listing
from app.providers.ebay import EbayProvider, ebay_config_from_env

ISBN_CLEAN_RE = re.compile(r"[^0-9Xx]")
USED_CONDITION_WORDS = (
    "used",
    "pre-owned",
    "preowned",
    "like new",
    "very good",
    "good",
    "acceptable",
)


def normalize_isbn(value: str) -> str:
    return ISBN_CLEAN_RE.sub("", value or "").upper()


def is_valid_isbn10(value: str) -> bool:
    isbn = normalize_isbn(value)
    if len(isbn) != 10 or not isbn[:9].isdigit() or not (isbn[-1].isdigit() or isbn[-1] == "X"):
        return False
    total = 0
    for index, character in enumerate(isbn):
        digit = 10 if character == "X" else int(character)
        total += (10 - index) * digit
    return total % 11 == 0


def is_valid_isbn13(value: str) -> bool:
    isbn = normalize_isbn(value)
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = sum(int(character) * (1 if index % 2 == 0 else 3) for index, character in enumerate(isbn[:12]))
    check = (10 - total % 10) % 10
    return check == int(isbn[-1])


def isbn10_to_isbn13(value: str) -> str | None:
    isbn10 = normalize_isbn(value)
    if not is_valid_isbn10(isbn10):
        return None
    stem = f"978{isbn10[:9]}"
    total = sum(int(character) * (1 if index % 2 == 0 else 3) for index, character in enumerate(stem))
    return f"{stem}{(10 - total % 10) % 10}"


def isbn13_to_isbn10(value: str) -> str | None:
    isbn13 = normalize_isbn(value)
    if not is_valid_isbn13(isbn13) or not isbn13.startswith("978"):
        return None
    stem = isbn13[3:12]
    total = sum((10 - index) * int(character) for index, character in enumerate(stem))
    check = (11 - total % 11) % 11
    check_character = "X" if check == 10 else str(check)
    return f"{stem}{check_character}"


def isbn_identity(value: str) -> dict[str, Any]:
    normalized = normalize_isbn(value)
    isbn10: str | None = None
    isbn13: str | None = None
    input_type: str | None = None

    if is_valid_isbn10(normalized):
        input_type = "ISBN-10"
        isbn10 = normalized
        isbn13 = isbn10_to_isbn13(normalized)
    elif is_valid_isbn13(normalized):
        input_type = "ISBN-13"
        isbn13 = normalized
        isbn10 = isbn13_to_isbn10(normalized)

    query_isbns = []
    for candidate in (isbn13, isbn10):
        if candidate and candidate not in query_isbns:
            query_isbns.append(candidate)

    return {
        "input": value,
        "normalized": normalized,
        "valid": bool(input_type),
        "input_type": input_type,
        "isbn10": isbn10,
        "isbn13": isbn13,
        "query_isbns": query_isbns,
    }


def _is_used_condition(condition: str | None) -> bool:
    normalized = (condition or "").strip().lower()
    return any(word in normalized for word in USED_CONDITION_WORDS)


def _listing_key(listing: Listing) -> str:
    # Multiple legitimate used-book sellers commonly reuse the exact same title.
    # Deduplicate only the marketplace item URL so distinct copies remain visible.
    return str(listing.url).split("?", 1)[0].rstrip("/").lower()


def _serialize_listing(listing: Listing) -> dict[str, Any]:
    return listing.model_dump(mode="json")


def books_lab_status() -> dict[str, Any]:
    return {
        "configured": ebay_config_from_env() is not None,
        "public": False,
        "mode": "eBay ISBN shadow test",
    }


async def search_used_books_by_isbn(
    value: str,
    *,
    provider: EbayProvider | None = None,
    limit: int = 35,
) -> dict[str, Any]:
    identity = isbn_identity(value)
    if not identity["valid"]:
        return {
            "isbn": identity,
            "candidate_count": 0,
            "eligible_count": 0,
            "duplicates_removed": 0,
            "rejection_reasons": {"Invalid ISBN check digit or length": 1},
            "top_results": [],
            "results": [],
        }

    if provider is None:
        provider = EbayProvider()

    candidates: list[Listing] = []
    for isbn in identity["query_isbns"]:
        candidates.extend(await provider.search_gtin(isbn, category="books", limit=limit))

    rejection_reasons: Counter[str] = Counter()
    eligible: list[Listing] = []
    seen_urls: set[str] = set()
    duplicates_removed = 0

    for listing in sorted(candidates, key=lambda item: (item.total_price, -item.score)):
        if not _is_used_condition(listing.condition):
            rejection_reasons["Not a used-book condition"] += 1
            continue

        url_key = _listing_key(listing)
        if url_key in seen_urls:
            duplicates_removed += 1
            continue
        seen_urls.add(url_key)
        eligible.append(listing)

    serialized = [_serialize_listing(listing) for listing in eligible[: max(1, min(limit, 100))]]
    return {
        "isbn": identity,
        "candidate_count": len(candidates),
        "eligible_count": len(eligible),
        "duplicates_removed": duplicates_removed,
        "rejection_reasons": dict(rejection_reasons),
        "top_results": serialized[:3],
        "results": serialized,
    }
