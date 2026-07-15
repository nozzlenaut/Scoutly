from __future__ import annotations

import os
import secrets

from fastapi import APIRouter, HTTPException, Query, status

from app.services.book_isbn import books_lab_status, search_used_books_by_isbn
from app.services.analytics_store import SearchEvent, log_search_event

router = APIRouter(tags=["Books lab"])


def _require_admin_token(token: str | None) -> None:
    configured_token = os.getenv("SCOUTLY_ADMIN_TOKEN", "").strip()
    if not configured_token:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Admin access is not configured.")
    if not token or not secrets.compare_digest(token, configured_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid admin token.")


@router.get("/books/search")
async def search_books_public(
    isbn: str = Query(..., min_length=10, max_length=32),
    limit: int = Query(default=35, ge=3, le=100),
    us_only: bool = Query(False),
    analytics: bool = Query(False),
) -> dict:
    try:
        result = await search_used_books_by_isbn(
            isbn,
            limit=limit,
            item_location_country="US" if us_only else None,
        )
        if analytics:
            normalized = result.get("isbn", {}).get("isbn13") or result.get("isbn", {}).get("normalized") or isbn
            result_count = len(result.get("top_results") or [])
            log_search_event(
                SearchEvent(
                    category="books",
                    query=str(normalized),
                    product_id=f"book-isbn:{normalized}" if normalized else None,
                    product_label=f"ISBN {normalized}" if normalized else "Book ISBN search",
                    resolved=bool(result.get("isbn", {}).get("valid")),
                    result_count=result_count,
                    provider_counts={"eBay": result_count} if result_count else {},
                    candidate_count=int(result.get("candidate_count") or 0),
                    filtered_count=max(0, int(result.get("candidate_count") or 0) - int(result.get("eligible_count") or 0)),
                    no_inventory=result_count == 0,
                    us_only=us_only,
                )
            )
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


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
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
