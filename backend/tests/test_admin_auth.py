from fastapi import HTTPException

from app.services.admin_auth import (
    bind_header_admin_token,
    require_admin_token,
    reset_header_admin_token,
)


def test_admin_header_token(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "header-secret")
    context = bind_header_admin_token("header-secret")
    try:
        require_admin_token()
    finally:
        reset_header_admin_token(context)


def test_query_token_remains_a_temporary_fallback(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "query-secret")
    require_admin_token("query-secret")


def test_invalid_admin_token_is_rejected(monkeypatch):
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "correct-secret")
    try:
        require_admin_token("wrong-secret")
    except HTTPException as error:
        assert error.status_code == 401
    else:
        raise AssertionError("Invalid token was accepted")
