from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from app.models.listing import Listing
from app.providers.ebay import EbayProvider, ebay_config_from_env

ISBN_CLEAN_RE = re.compile(r"[^0-9Xx]")
TITLE_TOKEN_RE = re.compile(r"[a-z0-9]+")
USED_CONDITION_WORDS = (
    "used",
    "pre-owned",
    "preowned",
    "like new",
    "very good",
    "good",
    "acceptable",
)


# These phrases identify a secondary product about the requested book rather
# than the exact edition itself. Keep the patterns contextual so a legitimate
# title containing a generic word such as "analysis" is not rejected blindly.
BOOK_DERIVATIVE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bstudy\s+guide\b", re.IGNORECASE), "Study guide or companion material"),
    (re.compile(r"\b(?:book\s+)?summary\b", re.IGNORECASE), "Summary or analysis product"),
    (re.compile(r"\bsummary\s*(?:and|&)\s*analysis\b", re.IGNORECASE), "Summary or analysis product"),
    (re.compile(r"\banalysis\s+(?:of|for)\b", re.IGNORECASE), "Summary or analysis product"),
    (re.compile(r"\bworkbook\s+(?:for|to|companion)\b", re.IGNORECASE), "Workbook or companion material"),
    (re.compile(r"\bcompanion\s+(?:guide|workbook|to)\b", re.IGNORECASE), "Workbook or companion material"),
    (re.compile(r"\b(?:sparknotes|cliffsnotes|cliff\s+notes)\b", re.IGNORECASE), "Study guide or companion material"),
)

BOOK_BUNDLE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:book|books|volume|volumes)\s+lot\b", re.IGNORECASE),
    re.compile(r"\blot\s+of\s+\d+\s+(?:books?|volumes?)\b", re.IGNORECASE),
    re.compile(r"\bbundle\b", re.IGNORECASE),
    re.compile(r"\bset\s+of\s+\d+\s+(?:books?|volumes?)\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*[- ]?(?:book|volume)\s+(?:set|lot|bundle)\b", re.IGNORECASE),
    re.compile(r"\b\d+\s+(?:books?|volumes?)\b", re.IGNORECASE),
    re.compile(r"\b(?:two|three|four|five)\s+(?:books?|volumes?)\b", re.IGNORECASE),
    re.compile(r"\bbooks?\s*\d+\s*(?:and|&|\+)\s*\d+\b", re.IGNORECASE),
)


BOOK_COLLECTIBLE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:author\s+)?signed\b", re.IGNORECASE),
    re.compile(r"\bautograph(?:ed)?\b", re.IGNORECASE),
    re.compile(r"\bdeluxe\b", re.IGNORECASE),
    re.compile(r"\bcollector'?s?\s+edition\b", re.IGNORECASE),
    re.compile(r"\blimited\s+edition\b", re.IGNORECASE),
    re.compile(r"\bspecial\s+edition\b", re.IGNORECASE),
    re.compile(r"\bfirst\s+(?:edition|printing)\b", re.IGNORECASE),
    re.compile(r"\bnumbered\s+(?:copy|edition)\b", re.IGNORECASE),
    re.compile(r"\bleather[-\s]?bound\b", re.IGNORECASE),
)

EDITION_YEAR_RE = re.compile(
    r"\b(?:(?:19|20)\d{2}\s+edition|edition\s+(?:19|20)\d{2})\b",
    re.IGNORECASE,
)

# Words that can appear across unrelated book listings and therefore should not
# be treated as proof that eBay returned one coherent title/edition.
BOOK_TITLE_STOPWORDS = {
    "a",
    "an",
    "and",
    "author",
    "book",
    "books",
    "copy",
    "edition",
    "english",
    "fiction",
    "hardback",
    "hardcover",
    "international",
    "mass",
    "new",
    "novel",
    "of",
    "paperback",
    "preowned",
    "printing",
    "read",
    "series",
    "softcover",
    "the",
    "trade",
    "used",
    "very",
    "volume",
    "vol",
    "with",
}


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

    # ISBN-13 is the primary lookup whenever it is available. ISBN-10 is only a
    # fallback now; blindly merging both result sets caused eBay catalog drift.
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


def _title_tokens(title: str) -> set[str]:
    tokens: set[str] = set()
    for token in TITLE_TOKEN_RE.findall((title or "").lower()):
        if token in BOOK_TITLE_STOPWORDS or len(token) < 3 or token.isdigit():
            continue
        # Ignore ISBN-like numbers and common year/printing noise.
        if len(token) >= 8 and token.isdigit():
            continue
        tokens.add(token)
    return tokens


def _identity_tokens(value: str) -> set[str]:
    """Return meaningful title tokens while preserving numeric titles such as 1984."""

    base = (value or "").split("(", 1)[0].strip() or (value or "")
    tokens: set[str] = set()
    for token in TITLE_TOKEN_RE.findall(base.lower()):
        if token in BOOK_TITLE_STOPWORDS or len(token) < 2:
            continue
        if token.isdigit() and len(token) > 4:
            continue
        tokens.add(token)
    return tokens


def _author_anchor(author: str | None) -> str | None:
    tokens = [
        token
        for token in TITLE_TOKEN_RE.findall((author or "").lower())
        if len(token) > 1 and token not in {"jr", "sr", "ii", "iii", "iv"}
    ]
    return tokens[-1] if tokens else None


def _listing_matches_expected_book(
    listing: Listing,
    expected_title: str | None,
    expected_author: str | None,
) -> bool:
    """Reject obvious eBay catalog drift using the Goodreads title as an anchor."""

    expected_tokens = _identity_tokens(expected_title or "")
    if not expected_tokens:
        return True

    listing_tokens = _identity_tokens(listing.title)
    shared = expected_tokens & listing_tokens
    author_anchor = _author_anchor(expected_author)

    if len(expected_tokens) == 1:
        return len(shared) == 1
    if len(shared) >= 2:
        return True
    return bool(len(shared) == 1 and author_anchor and author_anchor in listing_tokens)


def _listing_contains_exact_isbn(
    listing: Listing,
    accepted_isbns: tuple[str, ...],
) -> bool:
    text = f"{listing.title} {listing.description or ''}"
    compact = ISBN_CLEAN_RE.sub("", text).upper()
    return any(isbn and isbn in compact for isbn in accepted_isbns)


def _apply_title_consensus_gate(listings: list[Listing]) -> tuple[list[Listing], int, list[str]]:
    """Reject a large ISBN result set when it has no coherent title identity.

    eBay occasionally returns broad catalog soup for a valid ISBN. With five or
    more used candidates, legitimate copies should share at least one meaningful
    title/author token. Small result sets are left alone because one exact used
    copy is a perfectly valid outcome.
    """
    if len(listings) < 5:
        return listings, 0, []

    token_sets = [_title_tokens(listing.title) for listing in listings]
    frequencies: Counter[str] = Counter(token for tokens in token_sets for token in tokens)
    threshold = max(3, math.ceil(len(listings) * 0.4))
    consensus_tokens = sorted(token for token, count in frequencies.items() if count >= threshold)

    if not consensus_tokens:
        return [], len(listings), []

    consensus_set = set(consensus_tokens)
    anchor_threshold = max(3, math.ceil(len(listings) * 0.7))
    anchor_tokens = {token for token in consensus_tokens if frequencies[token] >= anchor_threshold}

    def matches_consensus(tokens: set[str]) -> bool:
        shared = tokens & consensus_set
        shared_anchors = tokens & anchor_tokens
        # When the ISBN result set has two or more dominant identity tokens
        # (for example, "atomic" + "habits"), require at least two of them.
        # This prevents an unrelated title containing only a generic word such
        # as "habits" from riding the dominant title cluster into the results.
        if len(anchor_tokens) >= 2:
            return len(shared_anchors) >= 2
        # Preserve coherent one-word titles such as Dune or Educated.
        if len(anchor_tokens) == 1:
            return bool(shared_anchors)
        return len(shared) >= 2 or (len(consensus_tokens) == 1 and len(shared) == 1)

    accepted = [listing for listing, tokens in zip(listings, token_sets) if matches_consensus(tokens)]

    # A tiny surviving minority is more likely accidental overlap than a real
    # ISBN identity cluster. Fail safely and let the alternate ISBN try once.
    minimum_cluster = max(2, math.ceil(len(listings) * 0.3))
    if len(accepted) < minimum_cluster:
        return [], len(listings), consensus_tokens

    return accepted, len(listings) - len(accepted), consensus_tokens


def _derivative_rejection_reason(title: str) -> str | None:
    for pattern, reason in BOOK_DERIVATIVE_PATTERNS:
        if pattern.search(title or ""):
            return reason
    return None


def _is_bundle_listing(title: str) -> bool:
    return any(pattern.search(title or "") for pattern in BOOK_BUNDLE_PATTERNS)


def _is_collectible_listing(title: str) -> bool:
    return any(pattern.search(title or "") for pattern in BOOK_COLLECTIBLE_PATTERNS)


def _annotate_book_listing(listing: Listing, *, collectible: bool, bundle: bool = False) -> Listing:
    warnings = list(listing.warning_labels)
    if EDITION_YEAR_RE.search(listing.title):
        warnings.append("Seller lists a specific edition year—verify the ISBN and listing details.")
    if collectible:
        warnings.append("Collectible, signed, or special-edition copy—price may not reflect a standard used copy.")
    if bundle:
        warnings.append("Multi-book lot or bundle—separated from single-copy price results.")
    # Preserve order while avoiding repeated labels from provider metadata.
    warnings = list(dict.fromkeys(warnings))
    return listing.model_copy(update={"warning_labels": warnings})


def _filter_query_candidates(
    candidates: list[Listing],
    *,
    expected_title: str | None = None,
    expected_author: str | None = None,
    required_isbns: tuple[str, ...] = (),
) -> tuple[list[Listing], list[Listing], list[Listing], Counter[str], int, list[str]]:
    rejection_reasons: Counter[str] = Counter()
    eligible: list[Listing] = []
    seen_urls: set[str] = set()
    duplicates_removed = 0

    for listing in sorted(candidates, key=lambda item: (item.total_price, -item.score)):
        if not _is_used_condition(listing.condition):
            rejection_reasons["Not a used-book condition"] += 1
            continue

        derivative_reason = _derivative_rejection_reason(listing.title)
        if derivative_reason:
            rejection_reasons[derivative_reason] += 1
            continue

        if expected_title and not _listing_matches_expected_book(
            listing,
            expected_title,
            expected_author,
        ):
            rejection_reasons["Listing title does not match Goodreads book"] += 1
            continue

        if required_isbns and not _listing_contains_exact_isbn(
            listing,
            required_isbns,
        ):
            rejection_reasons["Exact ISBN not visible in listing"] += 1
            continue

        url_key = _listing_key(listing)
        if url_key in seen_urls:
            duplicates_removed += 1
            continue
        seen_urls.add(url_key)
        eligible.append(listing)

    eligible, consensus_rejected, consensus_tokens = _apply_title_consensus_gate(eligible)
    if consensus_rejected:
        rejection_reasons["Unverified or inconsistent title identity"] += consensus_rejected

    standard: list[Listing] = []
    collectible: list[Listing] = []
    bundles: list[Listing] = []
    for listing in eligible:
        is_bundle = _is_bundle_listing(listing.title)
        is_collectible = _is_collectible_listing(listing.title)
        annotated = _annotate_book_listing(
            listing,
            collectible=is_collectible,
            bundle=is_bundle,
        )
        if is_bundle:
            bundles.append(annotated)
        elif is_collectible:
            collectible.append(annotated)
        else:
            standard.append(annotated)

    return (
        standard,
        collectible,
        bundles,
        rejection_reasons,
        duplicates_removed,
        consensus_tokens,
    )

def _serialize_listing(listing: Listing) -> dict[str, Any]:
    return listing.model_dump(mode="json")


def books_lab_status() -> dict[str, Any]:
    return {
        "configured": ebay_config_from_env() is not None,
        "public": True,
        "mode": "Public beta · exact used eBay ISBN search",
    }


async def search_used_books_by_isbn(
    value: str,
    *,
    provider: EbayProvider | None = None,
    limit: int = 35,
    item_location_country: str | None = None,
    expected_title: str | None = None,
    expected_author: str | None = None,
) -> dict[str, Any]:
    identity = isbn_identity(value)
    if not identity["valid"]:
        return {
            "isbn": identity,
            "candidate_count": 0,
            "eligible_count": 0,
            "standard_count": 0,
            "collectible_count": 0,
            "bundle_count": 0,
            "duplicates_removed": 0,
            "rejection_reasons": {"Invalid ISBN check digit or length": 1},
            "query_attempts": [],
            "selected_query_isbn": None,
            "selected_match_method": None,
            "selected_verification": None,
            "fallback_used": False,
            "top_results": [],
            "results": [],
            "collectible_results": [],
            "bundle_results": [],
        }

    if provider is None:
        provider = EbayProvider()

    query_attempts: list[dict[str, Any]] = []
    aggregate_rejections: Counter[str] = Counter()
    total_candidates = 0
    total_duplicates_removed = 0
    selected_query_isbn: str | None = None
    selected_match_method: str | None = None
    selected_verification: str | None = None
    selected_standard: list[Listing] = []
    selected_collectible: list[Listing] = []
    selected_bundles: list[Listing] = []
    collectible_fallback: tuple[
        str,
        str,
        str,
        list[Listing],
        list[Listing],
    ] | None = None

    search_options: dict[str, str] = {}
    if item_location_country:
        search_options["item_location_country"] = item_location_country

    # First use eBay's structured GTIN lookup. Goodreads title/author data is
    # supplied only for Goodreads imports and protects against catalog drift.
    for index, isbn in enumerate(identity["query_isbns"]):
        candidates = await provider.search_gtin(
            isbn,
            category="books",
            limit=limit,
            **search_options,
        )
        (
            standard,
            collectible,
            bundles,
            rejection_reasons,
            duplicates_removed,
            consensus_tokens,
        ) = _filter_query_candidates(
            candidates,
            expected_title=expected_title,
            expected_author=expected_author,
        )

        total_candidates += len(candidates)
        total_duplicates_removed += duplicates_removed
        aggregate_rejections.update(rejection_reasons)
        query_attempts.append(
            {
                "isbn": isbn,
                "method": "gtin",
                "role": "primary" if index == 0 else "fallback",
                "candidate_count": len(candidates),
                "eligible_count": len(standard) + len(collectible) + len(bundles),
                "standard_count": len(standard),
                "collectible_count": len(collectible),
                "bundle_count": len(bundles),
                "duplicates_removed": duplicates_removed,
                "consensus_tokens": consensus_tokens,
                "rejection_reasons": dict(rejection_reasons),
                "used_as_results": False,
            }
        )

        if standard:
            selected_query_isbn = isbn
            selected_match_method = (
                "gtin_title_verified" if expected_title else "gtin"
            )
            selected_verification = (
                "eBay ISBN catalog match checked against the Goodreads title."
                if expected_title
                else "eBay ISBN catalog match."
            )
            selected_standard = standard
            selected_collectible = collectible
            selected_bundles = bundles
            query_attempts[-1]["used_as_results"] = True
            break

        if (collectible or bundles) and collectible_fallback is None:
            collectible_fallback = (
                isbn,
                "gtin_collectible_only",
                "eBay ISBN catalog returned only collectible or multi-book copies.",
                collectible,
                bundles,
            )

    # eBay's GTIN index has real gaps. When it produces no standard result,
    # search the ISBN as an ordinary keyword and accept only listings where the
    # exact ISBN is visible in the title or description.
    if not selected_standard:
        accepted_isbns = tuple(identity["query_isbns"])
        for index, isbn in enumerate(identity["query_isbns"]):
            candidates = await provider.search(
                isbn,
                category="books",
                buying_option="fixed_price",
                **search_options,
            )
            (
                standard,
                collectible,
                bundles,
                rejection_reasons,
                duplicates_removed,
                consensus_tokens,
            ) = _filter_query_candidates(
                candidates,
                expected_title=expected_title,
                expected_author=expected_author,
                required_isbns=accepted_isbns,
            )

            total_candidates += len(candidates)
            total_duplicates_removed += duplicates_removed
            aggregate_rejections.update(rejection_reasons)
            query_attempts.append(
                {
                    "isbn": isbn,
                    "method": "keyword",
                    "role": "primary" if index == 0 else "fallback",
                    "candidate_count": len(candidates),
                    "eligible_count": len(standard) + len(collectible) + len(bundles),
                    "standard_count": len(standard),
                    "collectible_count": len(collectible),
                    "bundle_count": len(bundles),
                    "duplicates_removed": duplicates_removed,
                    "consensus_tokens": consensus_tokens,
                    "rejection_reasons": dict(rejection_reasons),
                    "used_as_results": False,
                }
            )

            if standard:
                selected_query_isbn = isbn
                selected_match_method = "keyword_isbn_verified"
                selected_verification = (
                    "Exact ISBN found in the listing text"
                    + (
                        " and title checked against Goodreads."
                        if expected_title
                        else "."
                    )
                )
                selected_standard = standard
                selected_collectible = collectible
                selected_bundles = bundles
                query_attempts[-1]["used_as_results"] = True
                break

            if (collectible or bundles) and collectible_fallback is None:
                collectible_fallback = (
                    isbn,
                    "keyword_collectible_only",
                    "Exact ISBN found, but only in collectible or multi-book copies.",
                    collectible,
                    bundles,
                )

    if selected_query_isbn is None and collectible_fallback is not None:
        (
            selected_query_isbn,
            selected_match_method,
            selected_verification,
            selected_collectible,
            selected_bundles,
        ) = collectible_fallback
        selected_method = (
            "keyword"
            if selected_match_method.startswith("keyword")
            else "gtin"
        )
        for attempt in query_attempts:
            if (
                attempt["isbn"] == selected_query_isbn
                and attempt["method"] == selected_method
            ):
                attempt["used_as_results"] = True
                break

    serialized_standard = [
        _serialize_listing(listing)
        for listing in selected_standard[: max(1, min(limit, 100))]
    ]
    serialized_collectible = [
        _serialize_listing(listing)
        for listing in selected_collectible[: max(1, min(limit, 100))]
    ]
    serialized_bundles = [
        _serialize_listing(listing)
        for listing in selected_bundles[: max(1, min(limit, 100))]
    ]
    return {
        "isbn": identity,
        "candidate_count": total_candidates,
        "eligible_count": (
            len(selected_standard)
            + len(selected_collectible)
            + len(selected_bundles)
        ),
        "standard_count": len(selected_standard),
        "collectible_count": len(selected_collectible),
        "bundle_count": len(selected_bundles),
        "duplicates_removed": total_duplicates_removed,
        "rejection_reasons": dict(aggregate_rejections),
        "query_attempts": query_attempts,
        "selected_query_isbn": selected_query_isbn,
        "selected_match_method": selected_match_method,
        "selected_verification": selected_verification,
        "fallback_used": bool(
            selected_match_method
            and (
                selected_match_method.startswith("keyword")
                or selected_query_isbn != identity["query_isbns"][0]
            )
        ),
        "top_results": serialized_standard[:3],
        "results": serialized_standard,
        "collectible_results": serialized_collectible,
        "bundle_results": serialized_bundles,
    }

