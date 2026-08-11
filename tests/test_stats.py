import uuid
from datetime import datetime, timezone

from click.testing import CliRunner

from todo.cli import cli
from todo.models import Task


def _make_task(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Stats test task",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestStats:
    def test_stats_empty(self, temp_storage_dir, monkeypatch):
        monkeypatch.setattr("todo.commands.stats.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["stats"])
        assert result.exit_code == 0
        assert "Gesamt: 0" in result.output
        assert "Pending: 0" in result.output
        assert "Done: 0" in result.output
        assert "low: 0" in result.output
        assert "medium: 0" in result.output
        assert "high: 0" in result.output

    def test_stats_with_tasks(self, temp_storage_dir, monkeypatch):
        tasks = [
            _make_task(status="pending", priority="low"),
            _make_task(status="pending", priority="medium"),
            _make_task(status="done", priority="high"),
            _make_task(status="done", priority="high"),
        ]

        monkeypatch.setattr("todo.commands.stats.load_tasks", lambda: tasks)

        runner = CliRunner()
        result = runner.invoke(cli, ["stats"])
        assert result.exit_code == 0
        assert "Gesamt: 4" in result.output
        assert "Pending: 2" in result.output
        assert "Done: 2" in result.output
        assert "low: 1" in result.output
        assert "medium: 1" in result.output
        assert "high: 2" in result.output

    def test_stats_cli_accessible(self, temp_storage_dir, monkeypatch):
        monkeypatch.setattr("todo.commands.stats.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "stats" in result.output
