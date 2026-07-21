from __future__ import annotations

import os
import secrets
from contextvars import ContextVar, Token
from typing import Any

from fastapi import HTTPException, status


_header_admin_token: ContextVar[str | None] = ContextVar(
    "pricesift_header_admin_token",
    default=None,
)


def bind_header_admin_token(token: str | None) -> Token[str | None]:
    return _header_admin_token.set(token)


def reset_header_admin_token(context_token: Token[str | None]) -> None:
    _header_admin_token.reset(context_token)


def require_admin_token(query_token: str | None = None) -> None:
    configured_token = os.getenv("SCOUTLY_ADMIN_TOKEN", "").strip()
    if not configured_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access is not configured.",
        )

    supplied_token = (_header_admin_token.get() or query_token or "").strip()
    if not supplied_token or not secrets.compare_digest(supplied_token, configured_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid admin token.",
        )


class AdminAuthorizationMiddleware:
    """Make a Bearer token available without copying it into a URL."""

    def __init__(self, app: Any):
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        bearer_token: str | None = None
        for raw_name, raw_value in scope.get("headers", []):
            if raw_name.lower() != b"authorization":
                continue
            authorization = raw_value.decode("latin-1").strip()
            scheme, separator, credentials = authorization.partition(" ")
            if separator and scheme.lower() == "bearer":
                bearer_token = credentials.strip() or None
            break

        context_token = bind_header_admin_token(bearer_token)
        try:
            await self.app(scope, receive, send)
        finally:
            reset_header_admin_token(context_token)
