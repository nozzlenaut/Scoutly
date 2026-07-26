from __future__ import annotations

from types import SimpleNamespace

from fastapi import Response

from app.api import diagnostics


def test_codex_diagnostics_is_sanitized_and_read_only(monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "list_products",
        lambda: [
            SimpleNamespace(active=True, category="consoles", category_label="Consoles"),
            SimpleNamespace(active=True, category="consoles", category_label="Consoles"),
            SimpleNamespace(active=True, category="books", category_label="Books"),
            SimpleNamespace(active=False, category="gpus", category_label="GPUs"),
        ],
    )
    monkeypatch.setattr(
        diagnostics,
        "database_health",
        lambda: {
            "configured": True,
            "connected": True,
            "backend": "postgresql",
            "error": "must never be exposed",
        },
    )
    monkeypatch.setattr(
        diagnostics,
        "qa_summary",
        lambda: {
            "total_cases": 2,
            "tested_cases": 2,
            "available_inventory_cases": 2,
            "counts": {"pass": 1, "top3_only": 1, "fail": 0, "no_inventory": 0, "untested": 0},
            "category_counts": {},
            "quality_rate": 100.0,
            "overall_rate": 100.0,
        },
    )
    monkeypatch.setattr(
        diagnostics,
        "list_qa_evaluations",
        lambda limit=12: [
            {
                "case_id": "console-ps5",
                "category": "consoles",
                "query": "private query",
                "notes": "private notes",
                "result_titles": ["private title"],
                "outcome": "top3_only",
                "resolution_correct": True,
                "created_at": "2026-07-26T12:00:00+00:00",
                "diagnostics": {
                    "fixed_price_candidates": 200,
                    "fixed_price_eligible": 91,
                    "fixed_price_filtered": 109,
                    "fixed_price_duplicates_removed": 0,
                },
            }
        ],
    )
    monkeypatch.setattr(diagnostics, "ebay_config_from_env", lambda: None)
    monkeypatch.setattr(diagnostics, "keh_feed_enabled", lambda: True)
    monkeypatch.setattr(diagnostics, "keh_public_results_enabled", lambda: True)

    response = Response()
    payload = diagnostics.codex_diagnostics(response)

    assert response.headers["Cache-Control"] == "public, max-age=60"
    assert payload["safety"]["read_only"] is True
    assert payload["safety"]["admin_access_required"] is False
    assert payload["catalog"]["active_products"] == 3
    assert payload["qa"]["recent_runs"][0]["fixed_price_candidates"] == 200
    assert payload["qa"]["recent_runs"][0]["fixed_price_eligible"] == 91
    assert "query" not in payload["qa"]["recent_runs"][0]
    assert "notes" not in payload["qa"]["recent_runs"][0]
    assert "result_titles" not in payload["qa"]["recent_runs"][0]
    assert "error" not in payload["storage"]
