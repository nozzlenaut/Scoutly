from app.services import data_migrations


def test_file_click_reset_runs_only_once(monkeypatch, tmp_path):
    monkeypatch.setenv("SCOUTLY_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(data_migrations, "database_configured", lambda: False)

    clicks_path = tmp_path / "outbound_clicks.json"
    clicks_path.write_text('[{"provider": "Amazon"}]\n', encoding="utf-8")

    data_migrations.apply_data_migrations()

    assert clicks_path.read_text(encoding="utf-8") == "[]\n"
    marker = tmp_path / f".{data_migrations.CLICK_RESET_MIGRATION}.done"
    assert marker.exists()

    clicks_path.write_text('[{"provider": "eBay"}]\n', encoding="utf-8")
    data_migrations.apply_data_migrations()

    assert '"eBay"' in clicks_path.read_text(encoding="utf-8")
