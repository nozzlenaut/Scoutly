from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
_DEFAULT_PER_MINUTE = 20
_DEFAULT_PER_DAY = 300
_FILE_LOCK = threading.Lock()
_MEMORY_BUCKETS: dict[str, int] = {}


@dataclass(frozen=True)
class AIRateLimitDecision:
    allowed: bool
    reason: str | None
    per_minute: int
    per_day: int


def _bounded_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


def ai_console_rate_limits() -> tuple[int, int]:
    return (
        _bounded_int("AI_CONSOLE_REVIEW_MAX_PER_MINUTE", _DEFAULT_PER_MINUTE, 1, 300),
        _bounded_int("AI_CONSOLE_REVIEW_MAX_PER_DAY", _DEFAULT_PER_DAY, 1, 10000),
    )


def _bucket_keys(now: datetime) -> tuple[str, str]:
    minute = now.strftime("%Y%m%d%H%M")
    day = now.strftime("%Y%m%d")
    return f"minute:{minute}", f"day:{day}"


def _ensure_database_table(connection: Any) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS scoutly_ai_rate_limits (
            bucket TEXT PRIMARY KEY,
            call_count INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )


def _increment_bucket(connection: Any, bucket: str, limit: int) -> bool:
    row = connection.execute(
        """
        INSERT INTO scoutly_ai_rate_limits (bucket, call_count, updated_at)
        VALUES (%s, 1, NOW())
        ON CONFLICT (bucket) DO UPDATE
        SET call_count = scoutly_ai_rate_limits.call_count + 1,
            updated_at = NOW()
        WHERE scoutly_ai_rate_limits.call_count < %s
        RETURNING call_count
        """,
        (bucket, limit),
    ).fetchone()
    return row is not None


class _RateLimitExceeded(RuntimeError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _reserve_database(minute_key: str, day_key: str, per_minute: int, per_day: int) -> AIRateLimitDecision:
    try:
        with database_connection() as connection:
            _ensure_database_table(connection)
            if not _increment_bucket(connection, day_key, per_day):
                raise _RateLimitExceeded("daily_limit")
            if not _increment_bucket(connection, minute_key, per_minute):
                # Raising inside the connection context rolls back the daily
                # increment too, so blocked requests do not consume the quota.
                raise _RateLimitExceeded("minute_limit")
            connection.execute(
                "DELETE FROM scoutly_ai_rate_limits WHERE updated_at < NOW() - INTERVAL '2 days'"
            )
        return AIRateLimitDecision(True, None, per_minute, per_day)
    except _RateLimitExceeded as exc:
        return AIRateLimitDecision(False, exc.reason, per_minute, per_day)


def _reserve_memory(minute_key: str, day_key: str, per_minute: int, per_day: int) -> AIRateLimitDecision:
    with _FILE_LOCK:
        if _MEMORY_BUCKETS.get(day_key, 0) >= per_day:
            return AIRateLimitDecision(False, "daily_limit", per_minute, per_day)
        if _MEMORY_BUCKETS.get(minute_key, 0) >= per_minute:
            return AIRateLimitDecision(False, "minute_limit", per_minute, per_day)
        _MEMORY_BUCKETS[day_key] = _MEMORY_BUCKETS.get(day_key, 0) + 1
        _MEMORY_BUCKETS[minute_key] = _MEMORY_BUCKETS.get(minute_key, 0) + 1

        active_prefixes = {minute_key, day_key}
        for key in list(_MEMORY_BUCKETS):
            if key not in active_prefixes:
                del _MEMORY_BUCKETS[key]

    return AIRateLimitDecision(True, None, per_minute, per_day)


def reserve_ai_console_review_call() -> AIRateLimitDecision:
    per_minute, per_day = ai_console_rate_limits()
    minute_key, day_key = _bucket_keys(datetime.now(UTC))

    if database_configured():
        try:
            return _reserve_database(minute_key, day_key, per_minute, per_day)
        except Exception:
            # Search must keep working if the limiter storage has a transient
            # failure. Fall back to a process-local cap instead of allowing an
            # unlimited AI call path.
            logger.exception("AI rate-limit database check failed; using process-local fallback")

    return _reserve_memory(minute_key, day_key, per_minute, per_day)
