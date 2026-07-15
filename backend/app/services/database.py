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
        """
        CREATE TABLE IF NOT EXISTS scoutly_beta_feedback (
            id TEXT PRIMARY KEY,
            submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            feedback_type TEXT NOT NULL,
            category TEXT,
            message TEXT NOT NULL,
            email TEXT,
            page_url TEXT
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_beta_feedback_recent
        ON scoutly_beta_feedback (submitted_at DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS scoutly_search_events (
            id BIGSERIAL PRIMARY KEY,
            searched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            category TEXT,
            query TEXT NOT NULL,
            product_id TEXT,
            product_label TEXT,
            resolved BOOLEAN NOT NULL DEFAULT FALSE,
            result_count INTEGER NOT NULL DEFAULT 0,
            provider_counts JSONB NOT NULL DEFAULT '{}'::jsonb,
            candidate_count INTEGER NOT NULL DEFAULT 0,
            filtered_count INTEGER NOT NULL DEFAULT 0,
            no_inventory BOOLEAN NOT NULL DEFAULT TRUE,
            us_only BOOLEAN NOT NULL DEFAULT FALSE,
            source TEXT NOT NULL DEFAULT 'public'
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_search_events_recent
        ON scoutly_search_events (searched_at DESC)
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_search_events_category
        ON scoutly_search_events (category, searched_at DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS scoutly_price_snapshots (
            id TEXT PRIMARY KEY,
            snapshot_bucket TIMESTAMPTZ NOT NULL,
            observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            product_id TEXT NOT NULL,
            category TEXT NOT NULL,
            product_label TEXT NOT NULL,
            provider TEXT NOT NULL,
            query TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'search',
            candidate_count INTEGER NOT NULL DEFAULT 0,
            filtered_count INTEGER NOT NULL DEFAULT 0,
            eligible_count INTEGER NOT NULL DEFAULT 0,
            lowest_price NUMERIC(12, 2),
            median_price NUMERIC(12, 2),
            p25_price NUMERIC(12, 2),
            p75_price NUMERIC(12, 2),
            sample_prices JSONB NOT NULL DEFAULT '[]'::jsonb,
            UNIQUE (product_id, provider, snapshot_bucket)
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_price_snapshots_product_recent
        ON scoutly_price_snapshots (product_id, observed_at DESC)
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_price_snapshots_recent
        ON scoutly_price_snapshots (observed_at DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS scoutly_keh_inventory (
            aw_product_id TEXT PRIMARY KEY,
            merchant_product_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            product_type TEXT NOT NULL,
            merchant_category_path TEXT,
            price NUMERIC(12, 2) NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            condition_grade_code TEXT,
            condition_grade_label TEXT,
            affiliate_url TEXT NOT NULL,
            merchant_url TEXT,
            image_url TEXT,
            brand TEXT,
            mpn TEXT,
            upc TEXT,
            in_stock BOOLEAN NOT NULL DEFAULT FALSE,
            is_for_sale BOOLEAN NOT NULL DEFAULT FALSE,
            matched_product_id TEXT,
            matched_product_label TEXT,
            match_confidence NUMERIC(5, 2),
            match_status TEXT NOT NULL DEFAULT 'unmatched',
            match_reason TEXT,
            feed_last_updated TEXT,
            synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            active BOOLEAN NOT NULL DEFAULT TRUE
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_keh_inventory_match
        ON scoutly_keh_inventory (match_status, matched_product_id, price)
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_keh_inventory_active
        ON scoutly_keh_inventory (active, synced_at DESC)
        """,
        """
        CREATE TABLE IF NOT EXISTS scoutly_keh_sync_runs (
            id TEXT PRIMARY KEY,
            started_at TIMESTAMPTZ NOT NULL,
            completed_at TIMESTAMPTZ,
            status TEXT NOT NULL,
            feed_items INTEGER NOT NULL DEFAULT 0,
            scoped_items INTEGER NOT NULL DEFAULT 0,
            matched_items INTEGER NOT NULL DEFAULT 0,
            unmatched_items INTEGER NOT NULL DEFAULT 0,
            ambiguous_items INTEGER NOT NULL DEFAULT 0,
            error_items INTEGER NOT NULL DEFAULT 0,
            etag TEXT,
            last_modified TEXT,
            error_message TEXT
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS scoutly_keh_sync_runs_recent
        ON scoutly_keh_sync_runs (started_at DESC)
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
