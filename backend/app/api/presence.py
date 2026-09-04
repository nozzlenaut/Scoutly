from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.database import database_configured, database_connection

router = APIRouter(tags=["Presence"])
_initialized = False


class PresenceHeartbeat(BaseModel):
    session_id: str = Field(min_length=16, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")


def _ensure_table(connection: object) -> None:
    global _initialized
    if _initialized:
        return
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS scoutly_active_sessions (
            session_id TEXT PRIMARY KEY,
            first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS scoutly_active_sessions_recent ON scoutly_active_sessions (last_seen DESC)"
    )
    _initialized = True


@router.post("/presence")
def heartbeat(payload: PresenceHeartbeat) -> dict[str, bool]:
    if not database_configured():
        return {"ok": False}

    with database_connection() as connection:
        _ensure_table(connection)
        connection.execute(
            """
            INSERT INTO scoutly_active_sessions (session_id, first_seen, last_seen)
            VALUES (%s, NOW(), NOW())
            ON CONFLICT (session_id) DO UPDATE SET last_seen = EXCLUDED.last_seen
            """,
            (payload.session_id,),
        )
        connection.execute(
            "DELETE FROM scoutly_active_sessions WHERE last_seen < NOW() - INTERVAL '24 hours'"
        )
    return {"ok": True}
