import uuid
from datetime import UTC, datetime

from click.testing import CliRunner

from todo.cli import cli
from todo.models import Task


def _make_task(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Priority test task",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestPriority:
    def test_change_to_low(self, monkeypatch):
        task = _make_task(priority="high")
        monkeypatch.setattr("todo.commands.priority.load_tasks", lambda: [task])
        saved: list[Task] = []
        monkeypatch.setattr("todo.commands.priority.save_tasks", lambda ts: saved.extend(ts))

        runner = CliRunner()
        result = runner.invoke(cli, ["priority", task.id[:8], "low"])
        assert result.exit_code == 0
        assert saved[0].priority == "low"
        assert "low" in result.output

    def test_change_to_medium(self, monkeypatch):
        task = _make_task(priority="low")
        monkeypatch.setattr("todo.commands.priority.load_tasks", lambda: [task])
        saved: list[Task] = []
        monkeypatch.setattr("todo.commands.priority.save_tasks", lambda ts: saved.extend(ts))

        runner = CliRunner()
        result = runner.invoke(cli, ["priority", task.id[:8], "medium"])
        assert result.exit_code == 0
        assert saved[0].priority == "medium"
        assert "medium" in result.output

    def test_change_to_high(self, monkeypatch):
        task = _make_task(priority="low")
        monkeypatch.setattr("todo.commands.priority.load_tasks", lambda: [task])
        saved: list[Task] = []
        monkeypatch.setattr("todo.commands.priority.save_tasks", lambda ts: saved.extend(ts))

        runner = CliRunner()
        result = runner.invoke(cli, ["priority", task.id[:8], "high"])
        assert result.exit_code == 0
        assert saved[0].priority == "high"
        assert "high" in result.output

    def test_nonexistent_id(self, monkeypatch):
        monkeypatch.setattr("todo.commands.priority.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["priority", "deadbeef", "low"])
        assert result.exit_code == 1
        assert "Keine Aufgabe" in result.stderr

    def test_ambiguous_prefix(self, monkeypatch):
        shared_prefix = "abcdef12"
        task_a = _make_task(id=shared_prefix + "-aaaa-bbbb-cccc-000000000001")
        task_b = _make_task(id=shared_prefix + "-aaaa-bbbb-cccc-000000000002")
        monkeypatch.setattr("todo.commands.priority.load_tasks", lambda: [task_a, task_b])

        runner = CliRunner()
        result = runner.invoke(cli, ["priority", shared_prefix, "low"])
        assert result.exit_code == 1
        assert "mehrere" in result.stderr

    def test_priority_cli_accessible(self, monkeypatch):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "priority" in result.output

    def test_updated_at_changes(self, monkeypatch):
        old_timestamp = "2020-01-01T00:00:00+00:00"
        task = _make_task(priority="high", updated_at=old_timestamp)
        monkeypatch.setattr("todo.commands.priority.load_tasks", lambda: [task])
        saved: list[Task] = []
        monkeypatch.setattr("todo.commands.priority.save_tasks", lambda ts: saved.extend(ts))

        runner = CliRunner()
        result = runner.invoke(cli, ["priority", task.id[:8], "low"])
        assert result.exit_code == 0
        assert saved[0].updated_at != old_timestamp
