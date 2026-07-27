
from datetime import UTC, datetime

from app.services.goodreads_analytics_store import (
    build_goodreads_analytics_digest,
)


def test_goodreads_digest_groups_searches_by_batch() -> None:
    searches = [
        {
            "searched_at": datetime(2026, 7, 27, 15, 0, tzinfo=UTC),
            "batch_id": "batch-one",
            "isbn": "9780063204157",
            "shelf": "to-read",
            "imported_count": 16,
            "searchable_count": 2,
            "digital_count": 1,
            "missing_isbn_count": 4,
            "result_count": 3,
            "candidate_count": 51,
            "filtered_count": 1,
            "us_only": False,
        },
        {
            "searched_at": datetime(2026, 7, 27, 15, 1, tzinfo=UTC),
            "batch_id": "batch-one",
            "isbn": "9780156030083",
            "shelf": "to-read",
            "imported_count": 16,
            "searchable_count": 2,
            "digital_count": 1,
            "missing_isbn_count": 4,
            "result_count": 0,
            "candidate_count": 0,
            "filtered_count": 0,
            "us_only": False,
        },
    ]
    clicks = [
        {"product_id": "goodreads:batch-one:9780063204157"},
        {"product_id": "goodreads-other:batch-one"},
    ]

    digest = build_goodreads_analytics_digest(searches, clicks, 30)

    assert digest["import_count"] == 1
    assert digest["completed_import_count"] == 1
    assert digest["search_count"] == 2
    assert digest["found_count"] == 1
    assert digest["no_result_count"] == 1
    assert digest["exact_success_rate"] == 50.0
    assert digest["candidate_count"] == 51
    assert digest["exact_listing_click_count"] == 1
    assert digest["other_editions_click_count"] == 1
    assert digest["imported_row_count"] == 16
    assert digest["digital_skipped_count"] == 1
    assert digest["missing_isbn_count"] == 4


def test_goodreads_digest_does_not_double_count_import_metadata() -> None:
    searches = [
        {
            "searched_at": "2026-07-27T15:00:00+00:00",
            "batch_id": "batch-one",
            "isbn": f"97800000000{index:02d}",
            "shelf": "read",
            "imported_count": 172,
            "searchable_count": 3,
            "digital_count": 41,
            "missing_isbn_count": 29,
            "result_count": 3,
            "candidate_count": 20,
            "filtered_count": 1,
            "us_only": False,
        }
        for index in range(3)
    ]

    digest = build_goodreads_analytics_digest(searches, [], 30)

    assert digest["import_count"] == 1
    assert digest["imported_row_count"] == 172
    assert digest["searchable_row_count"] == 3
    assert digest["digital_skipped_count"] == 41
    assert digest["missing_isbn_count"] == 29
    assert digest["search_count"] == 3


def test_goodreads_digest_stores_no_book_titles_or_account_data() -> None:
    searches = [
        {
            "searched_at": "2026-07-27T15:00:00+00:00",
            "batch_id": "anonymous-batch",
            "isbn": "9780063204157",
            "shelf": "to-read",
            "imported_count": 1,
            "searchable_count": 1,
            "digital_count": 0,
            "missing_isbn_count": 0,
            "result_count": 3,
            "candidate_count": 51,
            "filtered_count": 1,
            "us_only": False,
        }
    ]

    digest = build_goodreads_analytics_digest(searches, [], 30)
    batch_payload = str(digest["recent_batches"]).lower()

    assert "title" not in batch_payload
    assert "author" not in batch_payload
    assert "email" not in batch_payload
    assert "review" not in batch_payload
