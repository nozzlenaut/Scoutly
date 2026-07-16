from app.services.qa_registry import load_all_qa_cases


def test_camera_and_lens_qa_expansion_is_loaded_and_well_formed():
    cases = load_all_qa_cases()
    case_ids = [case["id"] for case in cases]

    assert len(case_ids) == len(set(case_ids))

    expansion = [case for case in cases if case.get("suite") == "camera_lens_expansion"]
    camera_cases = [case for case in expansion if case.get("category") == "cameras"]
    lens_cases = [case for case in expansion if case.get("category") == "lenses"]

    assert len(camera_cases) == 18
    assert len(lens_cases) == 31

    for case in lens_cases:
        assert case.get("runner") == "keh_lens"
        filters = case.get("lens_filters") or {}
        assert filters.get("mount")
        assert filters.get("lens_type") in {"Prime", "Zoom"}
        assert filters.get("focal_group")
