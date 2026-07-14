from fastapi.testclient import TestClient

from app.main import app
from app.services.qa_store import load_qa_cases, qa_cases_with_latest, qa_summary, save_qa_evaluation


def _evaluation_payload() -> dict:
    return {
        "case_id": "console-model-v2-switch",
        "category": "consoles",
        "query": "Nintendo Switch",
        "expected_product_id": "console-nintendo-switch",
        "expected_label": "Nintendo Switch",
        "resolved_product_id": "console-nintendo-switch",
        "resolved_label": "Nintendo Switch",
        "resolution_correct": True,
        "outcome": "pass",
        "issue_tags": [],
        "notes": "All three listings were complete systems.",
        "result_titles": ["Nintendo Switch V2 Console Complete"],
        "diagnostics": {"fixed_price_candidates": 12, "fixed_price_filtered": 8},
    }


def test_qa_case_catalog_covers_all_search_categories():
    cases = load_qa_cases()
    categories = {case["category"] for case in cases}
    assert len(cases) >= 80
    assert {"cameras", "gpus", "ram", "cpus", "consoles", "lego"}.issubset(categories)
    assert all(case.get("expected_product_id") for case in cases)


def test_qa_file_fallback_saves_latest_evaluation(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))

    saved = save_qa_evaluation(_evaluation_payload())
    cases = qa_cases_with_latest()
    switch_case = next(case for case in cases if case["id"] == "console-model-v2-switch")
    summary = qa_summary()

    assert saved["outcome"] == "pass"
    assert switch_case["latest_evaluation"]["notes"] == "All three listings were complete systems."
    assert switch_case["attempt_count"] == 1
    assert summary["tested_cases"] == 1
    assert summary["counts"]["pass"] == 1


def test_qa_endpoints_require_token_and_save(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SCOUTLY_ADMIN_TOKEN", "secret")
    client = TestClient(app)

    assert client.get("/api/qa/cases").status_code == 401

    cases = client.get("/api/qa/cases", params={"token": "secret"})
    assert cases.status_code == 200
    assert cases.json()["summary"]["total_cases"] >= 30
    assert cases.json()["summary"]["category_counts"]["consoles"]["untested"] == 16
    assert cases.json()["summary"]["category_counts"]["lego"]["untested"] == 20
    assert cases.json()["summary"]["category_counts"]["cpus"]["untested"] == 16
    assert cases.json()["summary"]["category_counts"]["ram"]["untested"] == 12
    assert cases.json()["summary"]["category_counts"]["gpus"]["untested"] == 12
    assert cases.json()["summary"]["category_counts"]["cameras"]["untested"] == 12

    saved = client.post(
        "/api/qa/evaluations",
        params={"token": "secret"},
        json=_evaluation_payload(),
    )
    assert saved.status_code == 200
    assert saved.json()["resolution_correct"] is True

    refreshed = client.get("/api/qa/cases", params={"token": "secret"})
    switch_case = next(
        case for case in refreshed.json()["cases"] if case["id"] == "console-model-v2-switch"
    )
    assert switch_case["latest_evaluation"]["outcome"] == "pass"


def test_qa_quality_rate_excludes_safe_no_inventory(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))

    passed = _evaluation_payload()
    save_qa_evaluation(passed)

    no_inventory = {
        **_evaluation_payload(),
        "case_id": "console-model-v2-ps5",
        "query": "PlayStation 5",
        "expected_product_id": "console-playstation-5",
        "expected_label": "PlayStation 5",
        "resolved_product_id": "console-playstation-5",
        "resolved_label": "PlayStation 5",
        "outcome": "no_inventory",
        "notes": "Resolved correctly; all live listings were filtered safely.",
        "result_titles": [],
    }
    save_qa_evaluation(no_inventory)

    summary = qa_summary()
    assert summary["tested_cases"] == 2
    assert summary["available_inventory_cases"] == 1
    assert summary["quality_rate"] == 100.0
    assert summary["overall_rate"] == 50.0
