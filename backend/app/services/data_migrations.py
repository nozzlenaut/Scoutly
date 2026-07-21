from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
CLICK_RESET_MIGRATION = "reset_outbound_clicks_for_verified_tracking_v1"


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _apply_file_click_reset() -> bool:
    base = _data_dir()
    marker = base / f".{CLICK_RESET_MIGRATION}.done"
    if marker.exists():
        return False

    clicks_path = base / "outbound_clicks.json"
    if clicks_path.exists():
        clicks_path.write_text("[]\n", encoding="utf-8")
    marker.write_text(datetime.now(UTC).isoformat(), encoding="utf-8")
    return True


def _apply_database_click_reset() -> bool:
    with database_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scoutly_data_migrations (
                name TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        applied = connection.execute(
            """
            INSERT INTO scoutly_data_migrations (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            RETURNING name
            """,
            (CLICK_RESET_MIGRATION,),
        ).fetchone()
        if not applied:
            return False
        connection.execute("DELETE FROM scoutly_outbound_clicks")
        return True


def apply_data_migrations() -> None:
    """Apply one-time data corrections without touching unrelated analytics."""

    try:
        changed = _apply_database_click_reset() if database_configured() else _apply_file_click_reset()
        if changed:
            logger.warning("Reset legacy outbound-click analytics before verified click tracking.")
    except Exception:
        # A failed migration must be retried on the next startup. Do not write a
        # success marker or block the API from serving searches.
        logger.exception("PriceSift data migration failed; it will be retried on restart.")
