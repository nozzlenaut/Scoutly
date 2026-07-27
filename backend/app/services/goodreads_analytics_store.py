
from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
MAX_FILE_EVENTS = 20_000
DB_MAX_EVENTS = 100_000
_TABLE_READY = False


def _now() -> datetime:
    return datetime.now(UTC)


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _events_path() -> Path:
    return _data_dir() / "goodreads_search_events.json"


def _read_events() -> list[dict[str, Any]]:
    path = _events_path()
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return payload if isinstance(payload, list) else []


def _write_events(records: list[dict[str, Any]]) -> None:
    path = _events_path()
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(records[-MAX_FILE_EVENTS:], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    tmp.replace(path)


def _parse_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 1)


def _ensure_table(connection: Any) -> None:
    global _TABLE_READY
    if _TABLE_READY:
        return

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS scoutly_goodreads_search_events (
            id BIGSERIAL PRIMARY KEY,
            searched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            batch_id TEXT NOT NULL,
            isbn TEXT NOT NULL,
            shelf TEXT,
            imported_count INTEGER NOT NULL DEFAULT 0,
            searchable_count INTEGER NOT NULL DEFAULT 0,
            digital_count INTEGER NOT NULL DEFAULT 0,
            missing_isbn_count INTEGER NOT NULL DEFAULT 0,
            result_count INTEGER NOT NULL DEFAULT 0,
            candidate_count INTEGER NOT NULL DEFAULT 0,
            filtered_count INTEGER NOT NULL DEFAULT 0,
            us_only BOOLEAN NOT NULL DEFAULT FALSE
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS scoutly_goodreads_search_events_recent
        ON scoutly_goodreads_search_events (searched_at DESC)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS scoutly_goodreads_search_events_batch
        ON scoutly_goodreads_search_events (batch_id, searched_at DESC)
        """
    )
    _TABLE_READY = True


@dataclass
class GoodreadsSearchEvent:
    batch_id: str
    isbn: str
    shelf: str | None
    imported_count: int
    searchable_count: int
    digital_count: int
    missing_isbn_count: int
    result_count: int
    candidate_count: int
    filtered_count: int
    us_only: bool = False


def log_goodreads_search_event(event: GoodreadsSearchEvent) -> None:
    now = _now()
    record = {**asdict(event), "searched_at": now.isoformat()}

    if database_configured():
        try:
            with database_connection() as connection:
                _ensure_table(connection)
                connection.execute(
                    """
                    INSERT INTO scoutly_goodreads_search_events (
                        searched_at, batch_id, isbn, shelf, imported_count,
                        searchable_count, digital_count, missing_isbn_count,
                        result_count, candidate_count, filtered_count, us_only
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        now,
                        event.batch_id,
                        event.isbn,
                        event.shelf,
                        max(0, event.imported_count),
                        max(0, event.searchable_count),
                        max(0, event.digital_count),
                        max(0, event.missing_isbn_count),
                        max(0, event.result_count),
                        max(0, event.candidate_count),
                        max(0, event.filtered_count),
                        event.us_only,
                    ),
                )
                connection.execute(
                    """
                    DELETE FROM scoutly_goodreads_search_events
                    WHERE searched_at < NOW() - INTERVAL '365 days'
                    """
                )
                connection.execute(
                    """
                    DELETE FROM scoutly_goodreads_search_events
                    WHERE id NOT IN (
                        SELECT id
                        FROM scoutly_goodreads_search_events
                        ORDER BY searched_at DESC
                        LIMIT %s
                    )
                    """,
                    (DB_MAX_EVENTS,),
                )
            return
        except Exception:
            logger.exception(
                "PostgreSQL Goodreads analytics write failed; using file fallback."
            )

    records = _read_events()
    records.append(record)
    _write_events(records)


def _records_for_days(
    days: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cutoff = _now() - timedelta(days=days)

    if database_configured():
        try:
            with database_connection() as connection:
                _ensure_table(connection)
                search_rows = connection.execute(
                    """
                    SELECT searched_at, batch_id, isbn, shelf, imported_count,
                           searchable_count, digital_count, missing_isbn_count,
                           result_count, candidate_count, filtered_count, us_only
                    FROM scoutly_goodreads_search_events
                    WHERE searched_at >= %s
                    ORDER BY searched_at ASC
                    """,
                    (cutoff,),
                ).fetchall()
                click_rows = connection.execute(
                    """
                    SELECT clicked_at, product_id
                    FROM scoutly_outbound_clicks
                    WHERE clicked_at >= %s
                      AND (
                        product_id LIKE 'goodreads:%%'
                        OR product_id LIKE 'goodreads-other:%%'
                      )
                    ORDER BY clicked_at ASC
                    """,
                    (cutoff,),
                ).fetchall()
            return [dict(row) for row in search_rows], [dict(row) for row in click_rows]
        except Exception:
            logger.exception(
                "PostgreSQL Goodreads analytics digest failed; using file fallback."
            )

    search_rows = [
        row
        for row in _read_events()
        if (_parse_dt(row.get("searched_at")) or datetime.min.replace(tzinfo=UTC))
        >= cutoff
    ]

    try:
        from app.services.feedback_store import recent_outbound_clicks

        click_rows = [
            row
            for row in recent_outbound_clicks(5000)
            if (
                str(row.get("product_id") or "").startswith("goodreads:")
                or str(row.get("product_id") or "").startswith("goodreads-other:")
            )
            and (
                _parse_dt(row.get("clicked_at"))
                or datetime.min.replace(tzinfo=UTC)
            )
            >= cutoff
        ]
    except Exception:
        click_rows = []

    return search_rows, click_rows


def build_goodreads_analytics_digest(
    searches: list[dict[str, Any]],
    clicks: list[dict[str, Any]],
    days: int,
) -> dict[str, Any]:
    batches: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "batch_id": "",
            "shelf": None,
            "imported_count": 0,
            "searchable_count": 0,
            "digital_count": 0,
            "missing_isbn_count": 0,
            "searched_count": 0,
            "found_count": 0,
            "no_result_count": 0,
            "candidate_count": 0,
            "filtered_count": 0,
            "us_only": False,
            "started_at": None,
            "completed_at": None,
        }
    )

    for row in searches:
        batch_id = str(row.get("batch_id") or "").strip()
        if not batch_id:
            continue

        batch = batches[batch_id]
        batch["batch_id"] = batch_id
        batch["shelf"] = row.get("shelf") or batch["shelf"]
        batch["imported_count"] = max(
            batch["imported_count"], int(row.get("imported_count") or 0)
        )
        batch["searchable_count"] = max(
            batch["searchable_count"], int(row.get("searchable_count") or 0)
        )
        batch["digital_count"] = max(
            batch["digital_count"], int(row.get("digital_count") or 0)
        )
        batch["missing_isbn_count"] = max(
            batch["missing_isbn_count"], int(row.get("missing_isbn_count") or 0)
        )
        batch["searched_count"] += 1

        result_count = int(row.get("result_count") or 0)
        if result_count > 0:
            batch["found_count"] += 1
        else:
            batch["no_result_count"] += 1

        batch["candidate_count"] += int(row.get("candidate_count") or 0)
        batch["filtered_count"] += int(row.get("filtered_count") or 0)
        batch["us_only"] = batch["us_only"] or bool(row.get("us_only"))

        searched_at = _parse_dt(row.get("searched_at"))
        if searched_at:
            if not batch["started_at"] or searched_at < batch["started_at"]:
                batch["started_at"] = searched_at
            if not batch["completed_at"] or searched_at > batch["completed_at"]:
                batch["completed_at"] = searched_at

    batch_rows = list(batches.values())
    batch_rows.sort(
        key=lambda row: row.get("completed_at")
        or datetime.min.replace(tzinfo=UTC),
        reverse=True,
    )

    search_count = sum(row["searched_count"] for row in batch_rows)
    found_count = sum(row["found_count"] for row in batch_rows)
    no_result_count = sum(row["no_result_count"] for row in batch_rows)
    candidate_count = sum(row["candidate_count"] for row in batch_rows)
    filtered_count = sum(row["filtered_count"] for row in batch_rows)
    completed_batch_count = sum(
        1
        for row in batch_rows
        if row["searchable_count"] > 0
        and row["searched_count"] >= row["searchable_count"]
    )

    exact_listing_click_count = sum(
        1
        for row in clicks
        if str(row.get("product_id") or "").startswith("goodreads:")
    )
    other_editions_click_count = sum(
        1
        for row in clicks
        if str(row.get("product_id") or "").startswith("goodreads-other:")
    )

    recent_batches = []
    for row in batch_rows[:20]:
        recent_batches.append(
            {
                **{
                    key: value
                    for key, value in row.items()
                    if key not in {"started_at", "completed_at"}
                },
                "started_at": (
                    row["started_at"].isoformat() if row["started_at"] else None
                ),
                "completed_at": (
                    row["completed_at"].isoformat()
                    if row["completed_at"]
                    else None
                ),
                "complete": (
                    row["searchable_count"] > 0
                    and row["searched_count"] >= row["searchable_count"]
                ),
            }
        )

    summary_lines = [
        f"Goodreads import analytics — last {days} days",
        f"Imports started: {len(batch_rows)}",
        f"Completed imports: {completed_batch_count}",
        f"Exact-edition searches: {search_count}",
        f"Exact editions with results: {found_count} ({_pct(found_count, search_count) or 0}%)",
        f"No listing for exact edition: {no_result_count}",
        f"Candidates reviewed: {candidate_count}",
        f"Candidates filtered: {filtered_count}",
        f"Exact listing clicks: {exact_listing_click_count}",
        f"Search other editions clicks: {other_editions_click_count}",
    ]

    return {
        "days": days,
        "import_count": len(batch_rows),
        "completed_import_count": completed_batch_count,
        "search_count": search_count,
        "found_count": found_count,
        "no_result_count": no_result_count,
        "exact_success_rate": _pct(found_count, search_count),
        "candidate_count": candidate_count,
        "filtered_count": filtered_count,
        "exact_listing_click_count": exact_listing_click_count,
        "other_editions_click_count": other_editions_click_count,
        "average_searches_per_import": (
            round(search_count / len(batch_rows), 1) if batch_rows else None
        ),
        "imported_row_count": sum(row["imported_count"] for row in batch_rows),
        "searchable_row_count": sum(row["searchable_count"] for row in batch_rows),
        "digital_skipped_count": sum(row["digital_count"] for row in batch_rows),
        "missing_isbn_count": sum(
            row["missing_isbn_count"] for row in batch_rows
        ),
        "recent_batches": recent_batches,
        "summary_text": "\n".join(summary_lines),
        "privacy_note": (
            "Goodreads CSV files, book titles, authors, reviews, ratings, and account "
            "identifiers are not stored. Analytics retain aggregate import counts, "
            "random batch IDs, and the ISBNs already used for marketplace searches."
        ),
    }


def goodreads_analytics_digest(days: int = 30) -> dict[str, Any]:
    days = max(1, min(days, 365))
    searches, clicks = _records_for_days(days)
    return build_goodreads_analytics_digest(searches, clicks, days)
