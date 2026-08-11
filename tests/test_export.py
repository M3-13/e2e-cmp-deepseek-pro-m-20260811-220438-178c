import json
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from click.testing import CliRunner

from todo.cli import cli
from todo.models import Task


def _make_task(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Export test task",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestExport:
    def test_export_to_stdout(self, temp_storage_dir, monkeypatch):
        tasks = [
            _make_task(description="Task 1", priority="high"),
            _make_task(description="Task 2", status="done"),
        ]
        monkeypatch.setattr("todo.commands.export.load_tasks", lambda: tasks)

        runner = CliRunner()
        result = runner.invoke(cli, ["export"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert parsed[0]["description"] == "Task 1"
        assert parsed[0]["priority"] == "high"
        assert parsed[1]["description"] == "Task 2"
        assert parsed[1]["status"] == "done"

    def test_export_empty(self, temp_storage_dir, monkeypatch):
        monkeypatch.setattr("todo.commands.export.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["export"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert isinstance(parsed, list)
        assert len(parsed) == 0

    def test_export_to_file(self, temp_storage_dir, monkeypatch):
        tasks = [
            _make_task(description="Task A"),
            _make_task(description="Task B"),
        ]
        monkeypatch.setattr("todo.commands.export.load_tasks", lambda: tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "backup.json"

            runner = CliRunner()
            result = runner.invoke(cli, ["export", "--output", str(output_path)])
            assert result.exit_code == 0

            assert output_path.exists()
            content = output_path.read_text(encoding="utf-8")
            parsed = json.loads(content)
            assert isinstance(parsed, list)
            assert len(parsed) == 2
            assert parsed[0]["description"] == "Task A"
            assert parsed[1]["description"] == "Task B"

    def test_export_valid_json_contains_all_fields(self, temp_storage_dir, monkeypatch):
        tasks = [
            _make_task(
                id="550e8400-e29b-41d4-a716-446655440000",
                description="Test task",
                status="pending",
                priority="high",
                due_date="2025-12-24",
                created_at="2025-01-01T00:00:00+00:00",
                updated_at="2025-01-02T00:00:00+00:00",
            )
        ]
        monkeypatch.setattr("todo.commands.export.load_tasks", lambda: tasks)

        runner = CliRunner()
        result = runner.invoke(cli, ["export"])
        assert result.exit_code == 0

        parsed = json.loads(result.output)
        assert len(parsed) == 1
        task = parsed[0]
        assert task["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert task["description"] == "Test task"
        assert task["status"] == "pending"
        assert task["priority"] == "high"
        assert task["due_date"] == "2025-12-24"
        assert task["created_at"] == "2025-01-01T00:00:00+00:00"
        assert task["updated_at"] == "2025-01-02T00:00:00+00:00"

    def test_export_file_write_error(self, temp_storage_dir, monkeypatch):
        tasks = [_make_task()]
        monkeypatch.setattr("todo.commands.export.load_tasks", lambda: tasks)

        runner = CliRunner()
        result = runner.invoke(cli, ["export", "--output", "/nonexistent/path/file.json"])
        assert result.exit_code == 1
        assert "Fehler" in result.stderr or "Fehler" in result.output
