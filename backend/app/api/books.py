
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.services.admin_auth import require_admin_token as _require_admin_token
from app.services.analytics_store import SearchEvent, log_search_event
from app.services.book_isbn import books_lab_status, search_used_books_by_isbn
from app.services.goodreads_analytics_store import (
    GoodreadsSearchEvent,
    log_goodreads_search_event,
)

router = APIRouter(tags=["Books lab"])


@router.get("/books/search")
async def search_books_public(
    isbn: str = Query(..., min_length=10, max_length=32),
    limit: int = Query(default=35, ge=3, le=100),
    us_only: bool = Query(False),
    analytics: bool = Query(False),
    source: Literal["public", "goodreads"] = Query("public"),
    batch_id: str | None = Query(default=None, min_length=8, max_length=80),
    shelf: str | None = Query(default=None, max_length=80),
    imported_count: int = Query(default=0, ge=0, le=100_000),
    searchable_count: int = Query(default=0, ge=0, le=100_000),
    digital_count: int = Query(default=0, ge=0, le=100_000),
    missing_isbn_count: int = Query(default=0, ge=0, le=100_000),
    expected_title: str | None = Query(default=None, max_length=300),
    expected_author: str | None = Query(default=None, max_length=200),
) -> dict:
    try:
        result = await search_used_books_by_isbn(
            isbn,
            limit=limit,
            item_location_country="US" if us_only else None,
            expected_title=expected_title,
            expected_author=expected_author,
        )
        if analytics:
            normalized = (
                result.get("isbn", {}).get("isbn13")
                or result.get("isbn", {}).get("normalized")
                or isbn
            )
            result_count = len(result.get("top_results") or [])
            candidate_count = int(result.get("candidate_count") or 0)
            eligible_count = int(result.get("eligible_count") or 0)
            filtered_count = max(0, candidate_count - eligible_count)

            if source == "goodreads":
                if not batch_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Goodreads analytics require a batch_id.",
                    )
                log_goodreads_search_event(
                    GoodreadsSearchEvent(
                        batch_id=batch_id,
                        isbn=str(normalized),
                        shelf=shelf,
                        imported_count=imported_count,
                        searchable_count=searchable_count,
                        digital_count=digital_count,
                        missing_isbn_count=missing_isbn_count,
                        result_count=result_count,
                        candidate_count=candidate_count,
                        filtered_count=filtered_count,
                        us_only=us_only,
                    )
                )
            else:
                log_search_event(
                    SearchEvent(
                        category="books",
                        query=str(normalized),
                        product_id=(
                            f"book-isbn:{normalized}" if normalized else None
                        ),
                        product_label=(
                            f"ISBN {normalized}"
                            if normalized
                            else "Book ISBN search"
                        ),
                        resolved=bool(result.get("isbn", {}).get("valid")),
                        result_count=result_count,
                        provider_counts=(
                            {"eBay": result_count} if result_count else {}
                        ),
                        candidate_count=candidate_count,
                        filtered_count=filtered_count,
                        no_inventory=result_count == 0,
                        us_only=us_only,
                    )
                )
        return result
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/books/lab/status")
def get_books_lab_status(token: str | None = Query(default=None)) -> dict:
    _require_admin_token(token)
    return books_lab_status()


@router.get("/books/lab/search")
async def search_books_lab(
    isbn: str = Query(..., min_length=10, max_length=32),
    token: str | None = Query(default=None),
    limit: int = Query(default=35, ge=3, le=100),
) -> dict:
    _require_admin_token(token)
    try:
        return await search_used_books_by_isbn(isbn, limit=limit)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
