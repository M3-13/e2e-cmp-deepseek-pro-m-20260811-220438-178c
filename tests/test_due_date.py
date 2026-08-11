import uuid
from datetime import UTC, datetime

from click.testing import CliRunner

from todo.cli import cli
from todo.models import Task


def _make_task(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Due date test task",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestDueDate:
    def test_set_due_date(self, monkeypatch):
        task = _make_task()
        old_updated_at = task.updated_at
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [task])
        saved: list[Task] = []
        monkeypatch.setattr("todo.commands.due_date.save_tasks", lambda ts: saved.extend(ts))

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", task.id[:8], "2025-12-24"])
        assert result.exit_code == 0
        assert saved[0].due_date == "2025-12-24"
        assert "2025-12-24" in result.output
        assert saved[0].updated_at != old_updated_at

    def test_set_due_date_full_id(self, monkeypatch):
        task = _make_task()
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [task])
        saved: list[Task] = []
        monkeypatch.setattr("todo.commands.due_date.save_tasks", lambda ts: saved.extend(ts))

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", task.id, "2025-12-24"])
        assert result.exit_code == 0
        assert saved[0].due_date == "2025-12-24"

    def test_clear_due_date(self, monkeypatch):
        task = _make_task(due_date="2025-12-24")
        old_updated_at = task.updated_at
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [task])
        saved: list[Task] = []
        monkeypatch.setattr("todo.commands.due_date.save_tasks", lambda ts: saved.extend(ts))

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", task.id[:8], "--clear"])
        assert result.exit_code == 0
        assert saved[0].due_date is None
        assert "entfernt" in result.output
        assert saved[0].updated_at != old_updated_at

    def test_invalid_date_format(self, monkeypatch):
        task = _make_task()
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [task])

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", task.id[:8], "not-a-date"])
        assert result.exit_code == 1
        assert "Ungültiges Datum" in result.stderr

    def test_invalid_calendar_date(self, monkeypatch):
        task = _make_task()
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [task])

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", task.id[:8], "2025-02-30"])
        assert result.exit_code == 1
        assert "Ungültiges Datum" in result.stderr

    def test_nonexistent_id(self, monkeypatch):
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", "deadbeef", "2025-12-24"])
        assert result.exit_code == 1
        assert "Keine Aufgabe" in result.stderr

    def test_neither_date_nor_clear(self, monkeypatch):
        task = _make_task()
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [task])

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", task.id[:8]])
        assert result.exit_code == 1
        assert "entweder" in result.stderr or "Fehler" in result.stderr

    def test_both_date_and_clear(self, monkeypatch):
        task = _make_task()
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [task])

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", task.id[:8], "2025-12-24", "--clear"])
        assert result.exit_code == 1
        assert "schließen" in result.stderr

    def test_due_date_cli_accessible(self, monkeypatch):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "due-date" in result.output

    def test_ambiguous_prefix(self, monkeypatch):
        shared_prefix = "abcdef12"
        task_a = _make_task(id=shared_prefix + "-aaaa-bbbb-cccc-000000000001")
        task_b = _make_task(id=shared_prefix + "-aaaa-bbbb-cccc-000000000002")
        monkeypatch.setattr("todo.commands.due_date.load_tasks", lambda: [task_a, task_b])

        runner = CliRunner()
        result = runner.invoke(cli, ["due-date", shared_prefix, "2025-12-24"])
        assert result.exit_code == 1
        assert "mehrere" in result.stderr
