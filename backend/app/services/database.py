from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any, Iterator

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - only used when optional local deps are absent
    psycopg = None  # type: ignore[assignment]
    dict_row = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

_LAST_ERROR: str | None = None
_LAST_CONNECTED_AT: str | None = None


def database_url() -> str | None:
    value = os.getenv("DATABASE_URL", "").strip()
    if not value or value.startswith("${{"):
        return None
    return value


def database_configured() -> bool:
    return bool(database_url())


@contextmanager
def database_connection() -> Iterator[Any]:
    global _LAST_CONNECTED_AT, _LAST_ERROR

    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not configured.")
    if psycopg is None:
        raise RuntimeError("psycopg is not installed.")

    try:
        with psycopg.connect(url, connect_timeout=8, row_factory=dict_row) as connection:
            _LAST_CONNECTED_AT = datetime.now(UTC).isoformat()
            _LAST_ERROR = None
            yield connection
    except Exception as error:
        _LAST_ERROR = error.__class__.__name__
        raise


def initialize_database() -> bool:
    """Create Scoutly persistence tables when PostgreSQL is configured.

    The API intentionally keeps file storage as a local-development fallback when
    DATABASE_URL is absent. A configured-but-unreachable database is reported as
    degraded rather than preventing the search API from starting.
    """

    if not database_configured():
        return False

    statements = [
        """
        CREATE TABLE IF NOT EXISTS scoutly_manual_filter_rules (
            id TEXT PRIMARY KEY,
            phrase TEXT NOT NULL,
            category TEXT,
            product_id TEXT,
            except_phrases JSONB NOT NULL DEFAULT '[]'::jsonb,
            note TEXT,
            source_title TEXT,
            source_item_id TEXT,
            enabled BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE UNIQUE INDEX IF NOT EXISTS scoutly_manual_filter_rule_scope_phrase
        ON scoutly_manual_filter_rules (
            LOWER(phrase),
            COALESCE(category, ''),
            COALESCE(product_id, '')
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS scoutly_bad_result_reports (
            id BIGSERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT,
            provider TEXT,
            category TEXT,
            product_id TEXT,
            query TEXT,
            reason TEXT NOT NULL DEFAULT 'wrong_item',
            link_key TEXT NOT NULL,
            ebay_item_id TEXT,
            reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ NOT NULL
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_bad_result_reports_active
        ON scoutly_bad_result_reports (expires_at DESC)
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_bad_result_reports_lookup
        ON scoutly_bad_result_reports (link_key, product_id, category)
        """,
        """
        CREATE TABLE IF NOT EXISTS scoutly_outbound_clicks (
            id BIGSERIAL PRIMARY KEY,
            clicked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            provider TEXT,
            category TEXT,
            product_id TEXT,
            query TEXT,
            title TEXT,
            link_key TEXT,
            ebay_item_id TEXT,
            affiliate_campaign_present BOOLEAN NOT NULL DEFAULT FALSE,
            affiliate_reference TEXT,
            url TEXT NOT NULL,
            tracked_url TEXT NOT NULL
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_outbound_clicks_recent
        ON scoutly_outbound_clicks (clicked_at DESC)
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_outbound_clicks_category
        ON scoutly_outbound_clicks (category, clicked_at DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS scoutly_filtered_listings (
            id BIGSERIAL PRIMARY KEY,
            filtered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            provider TEXT,
            category TEXT,
            product_id TEXT,
            query TEXT,
            title TEXT,
            listing_type TEXT,
            reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
            link_key TEXT,
            ebay_item_id TEXT,
            url TEXT NOT NULL
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_filtered_listings_recent
        ON scoutly_filtered_listings (filtered_at DESC)
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_filtered_listings_product
        ON scoutly_filtered_listings (product_id, filtered_at DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS scoutly_qa_evaluations (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            category TEXT NOT NULL,
            query TEXT NOT NULL,
            expected_product_id TEXT,
            expected_label TEXT,
            resolved_product_id TEXT,
            resolved_label TEXT,
            resolution_correct BOOLEAN NOT NULL DEFAULT FALSE,
            outcome TEXT NOT NULL,
            issue_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
            notes TEXT,
            result_titles JSONB NOT NULL DEFAULT '[]'::jsonb,
            diagnostics JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_qa_evaluations_case_recent
        ON scoutly_qa_evaluations (case_id, created_at DESC)
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_qa_evaluations_recent
        ON scoutly_qa_evaluations (created_at DESC)
        """,
    ]

    try:
        with database_connection() as connection:
            for statement in statements:
                connection.execute(statement)
        return True
    except Exception:
        logger.exception("Scoutly PostgreSQL initialization failed; file fallback remains available.")
        return False


def database_health() -> dict[str, Any]:
    if not database_configured():
        return {
            "configured": False,
            "connected": False,
            "backend": "file",
            "last_connected_at": _LAST_CONNECTED_AT,
            "error": None,
        }

    try:
        with database_connection() as connection:
            connection.execute("SELECT 1").fetchone()
        return {
            "configured": True,
            "connected": True,
            "backend": "postgresql",
            "last_connected_at": _LAST_CONNECTED_AT,
            "error": None,
        }
    except Exception:
        return {
            "configured": True,
            "connected": False,
            "backend": "file_fallback",
            "last_connected_at": _LAST_CONNECTED_AT,
            "error": _LAST_ERROR or "connection_failed",
        }
