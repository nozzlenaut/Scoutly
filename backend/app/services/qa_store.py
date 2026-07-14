from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.database import database_configured, database_connection

logger = logging.getLogger(__name__)
MAX_FILE_EVALUATIONS = 5000
ALLOWED_OUTCOMES = {"pass", "top3_only", "fail", "no_inventory"}


def _now() -> datetime:
    return datetime.now(UTC)


def _data_dir() -> Path:
    configured = os.getenv("SCOUTLY_DATA_DIR", "").strip()
    base = Path(configured) if configured else Path("/tmp/scoutly")
    base.mkdir(parents=True, exist_ok=True)
    return base


def _evaluations_path() -> Path:
    return _data_dir() / "qa_evaluations.json"


def _cases_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "qa_cases.json"


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return payload if isinstance(payload, list) else []


def _write_json_list(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(path)


def _serialize_record(record: dict[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in record.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return serialized


def load_qa_cases() -> list[dict[str, Any]]:
    cases = _read_json_list(_cases_path())
    return [case for case in cases if case.get("id") and case.get("query") and case.get("category")]


def _db_or_file_read(db_reader, file_reader):
    if database_configured():
        try:
            return db_reader()
        except Exception:
            logger.exception("PostgreSQL QA read failed; using file fallback.")
    return file_reader()


def _db_write_or_file(db_writer, file_writer) -> None:
    if database_configured():
        try:
            db_writer()
            return
        except Exception:
            logger.exception("PostgreSQL QA write failed; using file fallback.")
    file_writer()


def save_qa_evaluation(payload: dict[str, Any]) -> dict[str, Any]:
    outcome = str(payload.get("outcome") or "").strip().lower()
    if outcome not in ALLOWED_OUTCOMES:
        raise ValueError("Unknown QA outcome.")

    created_at = _now()
    record = {
        "id": str(uuid4()),
        "case_id": str(payload.get("case_id") or "").strip(),
        "category": str(payload.get("category") or "").strip(),
        "query": str(payload.get("query") or "").strip(),
        "expected_product_id": payload.get("expected_product_id") or None,
        "expected_label": payload.get("expected_label") or None,
        "resolved_product_id": payload.get("resolved_product_id") or None,
        "resolved_label": payload.get("resolved_label") or None,
        "resolution_correct": bool(payload.get("resolution_correct")),
        "outcome": outcome,
        "issue_tags": [str(tag).strip() for tag in payload.get("issue_tags") or [] if str(tag).strip()][:12],
        "notes": (str(payload.get("notes") or "").strip() or None),
        "result_titles": [str(title).strip() for title in payload.get("result_titles") or [] if str(title).strip()][:3],
        "diagnostics": dict(payload.get("diagnostics") or {}),
        "created_at": created_at,
    }
    if not record["case_id"] or not record["category"] or not record["query"]:
        raise ValueError("case_id, category, and query are required.")

    def db_write() -> None:
        with database_connection() as connection:
            connection.execute(
                """
                INSERT INTO scoutly_qa_evaluations (
                    id, case_id, category, query, expected_product_id,
                    expected_label, resolved_product_id, resolved_label,
                    resolution_correct, outcome, issue_tags, notes,
                    result_titles, diagnostics, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s::jsonb, %s, %s::jsonb, %s::jsonb, %s
                )
                """,
                (
                    record["id"],
                    record["case_id"],
                    record["category"],
                    record["query"],
                    record["expected_product_id"],
                    record["expected_label"],
                    record["resolved_product_id"],
                    record["resolved_label"],
                    record["resolution_correct"],
                    record["outcome"],
                    json.dumps(record["issue_tags"]),
                    record["notes"],
                    json.dumps(record["result_titles"]),
                    json.dumps(record["diagnostics"]),
                    created_at,
                ),
            )

    def file_write() -> None:
        records = _read_json_list(_evaluations_path())
        records.append(_serialize_record(record))
        _write_json_list(_evaluations_path(), records[-MAX_FILE_EVALUATIONS:])

    _db_write_or_file(db_write, file_write)
    return _serialize_record(record)


def list_qa_evaluations(limit: int = 500) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 5000))

    def db_read() -> list[dict[str, Any]]:
        with database_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, case_id, category, query, expected_product_id,
                       expected_label, resolved_product_id, resolved_label,
                       resolution_correct, outcome, issue_tags, notes,
                       result_titles, diagnostics, created_at
                FROM scoutly_qa_evaluations
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()
        return [_serialize_record(dict(row)) for row in rows]

    def file_read() -> list[dict[str, Any]]:
        return list(reversed(_read_json_list(_evaluations_path())[-limit:]))

    return _db_or_file_read(db_read, file_read)


def qa_cases_with_latest() -> list[dict[str, Any]]:
    evaluations = list_qa_evaluations(limit=5000)
    latest_by_case: dict[str, dict[str, Any]] = {}
    attempts_by_case: dict[str, int] = {}
    for evaluation in evaluations:
        case_id = str(evaluation.get("case_id") or "")
        if not case_id:
            continue
        attempts_by_case[case_id] = attempts_by_case.get(case_id, 0) + 1
        if case_id not in latest_by_case:
            latest_by_case[case_id] = evaluation

    cases: list[dict[str, Any]] = []
    for case in load_qa_cases():
        case_id = str(case["id"])
        cases.append(
            {
                **case,
                "attempt_count": attempts_by_case.get(case_id, 0),
                "latest_evaluation": latest_by_case.get(case_id),
            }
        )
    return cases


def qa_summary() -> dict[str, Any]:
    cases = qa_cases_with_latest()
    counts = {"pass": 0, "top3_only": 0, "fail": 0, "no_inventory": 0, "untested": 0}
    category_counts: dict[str, dict[str, int]] = {}
    for case in cases:
        category = str(case.get("category") or "unknown")
        category_counts.setdefault(
            category,
            {"pass": 0, "top3_only": 0, "fail": 0, "no_inventory": 0, "untested": 0},
        )
        evaluation = case.get("latest_evaluation") or {}
        outcome = evaluation.get("outcome") or "untested"
        if outcome not in counts:
            outcome = "untested"
        counts[outcome] += 1
        category_counts[category][outcome] += 1

    tested = len(cases) - counts["untested"]
    quality_passes = counts["pass"] + counts["top3_only"]
    return {
        "total_cases": len(cases),
        "tested_cases": tested,
        "counts": counts,
        "category_counts": category_counts,
        "quality_rate": round((quality_passes / tested) * 100, 1) if tested else None,
    }
