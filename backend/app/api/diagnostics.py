from __future__ import annotations

import os
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Response

from app.catalog.catalog import GLOBAL_BAD_LISTING_TERMS, list_products
from app.providers.ebay import ebay_config_from_env
from app.ranking.scorer import HARDWARE_DEFECT_PATTERNS
from app.services.database import database_health
from app.services.keh_feed import keh_feed_enabled, keh_public_results_enabled
from app.services.qa_registry import qa_summary
from app.services.qa_store import list_qa_evaluations
from app.version import APP_VERSION

router = APIRouter(tags=["Diagnostics"])


def _commit_sha() -> str | None:
    for name in (
        "GIT_COMMIT_SHA",
        "SOURCE_VERSION",
    ):
        value = os.getenv(name, "").strip()
        if value:
            return value[:12]
    return None


def _safe_storage_status() -> dict[str, Any]:
    health = database_health()
    return {
        "configured": bool(health.get("configured")),
        "connected": bool(health.get("connected")),
        "backend": str(health.get("backend") or "unknown"),
    }


def _catalog_summary() -> dict[str, Any]:
    active_products = [product for product in list_products() if product.active]
    counts = Counter(product.category for product in active_products)
    labels: dict[str, str] = {}
    for product in active_products:
        labels.setdefault(product.category, product.category_label)

    categories = [
        {
            "id": category,
            "label": labels.get(category, category),
            "active_products": count,
        }
        for category, count in sorted(counts.items())
    ]
    return {
        "active_products": len(active_products),
        "categories": categories,
    }


def _provider_summary() -> list[dict[str, Any]]:
    ebay_live = ebay_config_from_env() is not None
    keh_feed = keh_feed_enabled()
    keh_public = keh_public_results_enabled()
    return [
        {
            "id": "ebay",
            "role": "marketplace search",
            "mode": "live" if ebay_live else "mock",
            "live": ebay_live,
        },
        {
            "id": "keh",
            "role": "camera inventory feed",
            "mode": "public" if keh_public else "shadow" if keh_feed else "disabled",
            "live": keh_feed,
        },
        {
            "id": "amazon",
            "role": "book fallback link",
            "mode": "fallback",
            "live": False,
        },
    ]


def _safe_recent_qa(limit: int = 12) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for evaluation in list_qa_evaluations(limit=limit):
        diagnostics = evaluation.get("diagnostics") or {}
        rows.append(
            {
                "case_id": str(evaluation.get("case_id") or ""),
                "category": str(evaluation.get("category") or ""),
                "outcome": str(evaluation.get("outcome") or ""),
                "resolution_correct": bool(evaluation.get("resolution_correct")),
                "created_at": evaluation.get("created_at"),
                "fixed_price_candidates": int(diagnostics.get("fixed_price_candidates") or 0),
                "fixed_price_eligible": int(diagnostics.get("fixed_price_eligible") or 0),
                "fixed_price_filtered": int(diagnostics.get("fixed_price_filtered") or 0),
                "fixed_price_duplicates_removed": int(
                    diagnostics.get("fixed_price_duplicates_removed") or 0
                ),
            }
        )
    return rows


@router.get("/diagnostics/codex")
def codex_diagnostics(response: Response) -> dict[str, Any]:
    """Return a deliberately sanitized, read-only operational snapshot."""

    response.headers["Cache-Control"] = "public, max-age=60"
    return {
        "purpose": "Read-only PriceSift operational summary for Codex and human review.",
        "generated_at": datetime.now(UTC).isoformat(),
        "release": {
            "version": APP_VERSION,
            "commit": _commit_sha(),
        },
        "providers": _provider_summary(),
        "catalog": _catalog_summary(),
        "filters": {
            "global_reject_terms": len(GLOBAL_BAD_LISTING_TERMS),
            "hardware_defect_patterns": len(HARDWARE_DEFECT_PATTERNS),
            "manual_rules_exposed": False,
            "behavior": [
                "Exact catalog identity is checked before ranking.",
                "Category-specific accessory, part, bundle, and model-conflict rules are applied.",
                "Confirmed hardware defects are rejected; warning-only wording may remain visible.",
                "Eligible fixed-price listings are sorted by total buyer price after filtering.",
            ],
        },
        "qa": {
            "summary": qa_summary(),
            "recent_runs": _safe_recent_qa(),
        },
        "storage": _safe_storage_status(),
        "safety": {
            "read_only": True,
            "admin_access_required": False,
            "contains_user_data": False,
            "contains_listing_titles": False,
            "contains_search_queries": False,
            "contains_private_configuration": False,
            "write_actions_available": False,
        },
    }
