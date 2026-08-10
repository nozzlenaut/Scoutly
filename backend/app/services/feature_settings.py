from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
_AI_CONSOLE_BETA_KEY = "ai_console_review_enabled"


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _settings_path() -> Path:
    return _data_dir() / "feature_settings.json"


def _read_file_settings() -> dict[str, Any]:
    path = _settings_path()
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_file_settings(settings: dict[str, Any]) -> None:
    path = _settings_path()
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(settings, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _ensure_database_table(connection: Any) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS scoutly_feature_settings (
            key TEXT PRIMARY KEY,
            value JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )


def ai_console_review_enabled() -> bool:
    if database_configured():
        try:
            with database_connection() as connection:
                _ensure_database_table(connection)
                row = connection.execute(
                    "SELECT value FROM scoutly_feature_settings WHERE key = %s",
                    (_AI_CONSOLE_BETA_KEY,),
                ).fetchone()
            if row is None:
                return False
            value = row.get("value") if isinstance(row, dict) else row[0]
            return bool(value)
        except Exception:
            logger.exception("AI console feature-setting read failed; using file fallback.")

    return bool(_read_file_settings().get(_AI_CONSOLE_BETA_KEY, False))


def set_ai_console_review_enabled(enabled: bool) -> bool:
    value = bool(enabled)
    if database_configured():
        try:
            with database_connection() as connection:
                _ensure_database_table(connection)
                connection.execute(
                    """
                    INSERT INTO scoutly_feature_settings (key, value, updated_at)
                    VALUES (%s, %s::jsonb, NOW())
                    ON CONFLICT (key) DO UPDATE
                    SET value = EXCLUDED.value, updated_at = NOW()
                    """,
                    (_AI_CONSOLE_BETA_KEY, json.dumps(value)),
                )
            return value
        except Exception:
            logger.exception("AI console feature-setting write failed; using file fallback.")

    settings = _read_file_settings()
    settings[_AI_CONSOLE_BETA_KEY] = value
    _write_file_settings(settings)
    return value


def ai_console_review_status() -> dict[str, Any]:
    enabled = ai_console_review_enabled()
    api_key_configured = bool(os.getenv("OPENAI_API_KEY", "").strip())
    model = os.getenv("AI_CONSOLE_REVIEW_MODEL", "gpt-5-nano").strip() or "gpt-5-nano"
    return {
        "enabled": enabled,
        "api_key_configured": api_key_configured,
        "ready": enabled and api_key_configured,
        "model": model,
        "targets": ["Nintendo Wii", "Nintendo 64", "Nintendo Switch 2"],
    }
