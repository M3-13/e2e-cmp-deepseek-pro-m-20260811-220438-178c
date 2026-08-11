import json
import uuid
from datetime import datetime, timezone

from click.testing import CliRunner

from todo.cli import cli
from todo.models import Task

_MOCK_ID1 = str(uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
_MOCK_ID2 = str(uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"))


def _make_task(
    description: str,
    status: str = "pending",
    priority: str = "medium",
    due_date: str | None = None,
) -> Task:
    now = datetime.now(timezone.utc).isoformat()
    return Task(
        id=str(uuid.uuid4()),
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        created_at=now,
        updated_at=now,
    )


class TestImportOverwrite:
    def test_overwrite_replaces_all_tasks(self, tmp_path, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        existing = _make_task("Alte Aufgabe")
        tasks_backing.append(existing)

        import_file = tmp_path / "import.json"
        import_data = [
            {"description": "Neue Aufgabe 1", "priority": "high", "status": "pending"},
            {"description": "Neue Aufgabe 2", "due_date": "2025-12-24", "status": "done"},
        ]
        import_file.write_text(json.dumps(import_data), encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", str(import_file)])
        assert result.exit_code == 0
        assert "Importiert: 2" in result.output
        assert "überschrieben" in result.output
        assert len(tasks_backing) == 2
        assert tasks_backing[0].description == "Neue Aufgabe 1"
        assert tasks_backing[1].description == "Neue Aufgabe 2"


class TestImportMerge:
    def test_merge_adds_without_duplicates(self, tmp_path, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        existing = _make_task("Bleibt erhalten", status="pending")
        tasks_backing.append(existing)

        import_file = tmp_path / "import.json"
        import_data = [
            {"description": "Bleibt erhalten", "status": "pending"},
            {"description": "Neu hinzugefügt", "status": "pending"},
        ]
        import_file.write_text(json.dumps(import_data), encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", str(import_file), "--merge"])
        assert result.exit_code == 0
        assert "Importiert: 1" in result.output
        assert "übersprungen: 1" in result.output
        assert len(tasks_backing) == 2
        descriptions = {t.description for t in tasks_backing}
        assert "Bleibt erhalten" in descriptions
        assert "Neu hinzugefügt" in descriptions

    def test_merge_different_status_not_duplicate(self, tmp_path, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        existing = _make_task("Gleiche Beschreibung", status="pending")
        tasks_backing.append(existing)

        import_file = tmp_path / "import.json"
        import_data = [
            {"description": "Gleiche Beschreibung", "status": "done"},
        ]
        import_file.write_text(json.dumps(import_data), encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", str(import_file), "--merge"])
        assert result.exit_code == 0
        assert "Importiert: 1" in result.output
        assert len(tasks_backing) == 2


class TestImportInvalidJson:
    def test_broken_json_file(self, tmp_path, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        import_file = tmp_path / "import.json"
        import_file.write_text("{invalid json", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", str(import_file)])
        assert result.exit_code == 1
        assert "ungültiges JSON" in result.stderr or "ungültiges JSON" in result.output

    def test_not_a_json_array(self, tmp_path, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        import_file = tmp_path / "import.json"
        import_file.write_text('{"description": "no array"}', encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", str(import_file)])
        assert result.exit_code == 1
        assert "kein JSON-Array" in result.stderr

    def test_missing_description_field(self, tmp_path, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        import_file = tmp_path / "import.json"
        import_data = [
            {"description": "Gültig"},
            {"priority": "high"},
        ]
        import_file.write_text(json.dumps(import_data), encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", str(import_file)])
        assert result.exit_code == 1
        assert "description" in result.stderr

    def test_non_object_entry_in_array(self, tmp_path, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        import_file = tmp_path / "import.json"
        import_data = ["not an object", {"description": "valid"}]
        import_file.write_text(json.dumps(import_data), encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", str(import_file)])
        assert result.exit_code == 1
        assert "kein JSON-Objekt" in result.stderr

    def test_missing_file(self, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", "/nonexistent/path.json"])
        assert result.exit_code == 1
        assert "nicht gelesen" in result.stderr.lower() or "nicht gelesen" in result.output.lower()

    def test_import_preserves_existing_fields(self, tmp_path, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

        import_file = tmp_path / "import.json"
        import_data = [
            {
                "id": _MOCK_ID1,
                "description": "Mit allen Feldern",
                "status": "done",
                "priority": "low",
                "due_date": "2025-06-15",
                "created_at": "2025-01-01T00:00:00+00:00",
                "updated_at": "2025-06-01T00:00:00+00:00",
            }
        ]
        import_file.write_text(json.dumps(import_data), encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["import", "--file", str(import_file)])
        assert result.exit_code == 0
        assert len(tasks_backing) == 1
        t = tasks_backing[0]
        assert t.id == _MOCK_ID1
        assert t.description == "Mit allen Feldern"
        assert t.status == "done"
        assert t.priority == "low"
        assert t.due_date == "2025-06-15"
        assert t.created_at == "2025-01-01T00:00:00+00:00"
        assert t.updated_at == "2025-06-01T00:00:00+00:00"


def test_invalid_due_date_format(tmp_path, temp_storage_dir, monkeypatch):
    tasks_backing: list = []

    def fake_load():
        return list(tasks_backing)

    def fake_save(tasks):
        tasks_backing.clear()
        tasks_backing.extend(tasks)

    monkeypatch.setattr("todo.commands.import_cmd.load_tasks", fake_load)
    monkeypatch.setattr("todo.commands.import_cmd.save_tasks", fake_save)

    import_file = tmp_path / "import.json"
    import_data = [
        {"description": "Gueltig", "due_date": "kein-datum"},
    ]
    import_file.write_text(json.dumps(import_data), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["import", "--file", str(import_file)])
    assert result.exit_code == 1
    assert "due_date" in result.stderr
