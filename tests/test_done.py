import uuid
from datetime import datetime, timezone

from click.testing import CliRunner

from todo.cli import cli
from todo.models import Task
from todo.storage import save_tasks


def _make_task(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Done test task",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestDone:
    def test_done_marks_task_as_done(self, temp_storage_dir, monkeypatch):
        task = _make_task(status="pending")
        save_tasks([task])

        runner = CliRunner()
        result = runner.invoke(cli, ["done", task.id[:8]])
        assert result.exit_code == 0
        assert "erledigt markiert" in result.output

        from todo.storage import load_tasks

        tasks = load_tasks()
        assert len(tasks) == 1
        assert tasks[0].status == "done"

    def test_done_full_id(self, temp_storage_dir):
        task = _make_task(status="pending")
        save_tasks([task])

        runner = CliRunner()
        result = runner.invoke(cli, ["done", task.id])
        assert result.exit_code == 0
        assert "erledigt markiert" in result.output

        from todo.storage import load_tasks

        tasks = load_tasks()
        assert tasks[0].status == "done"

    def test_done_already_done(self, temp_storage_dir):
        task = _make_task(status="done")
        save_tasks([task])

        runner = CliRunner()
        result = runner.invoke(cli, ["done", task.id[:8]])
        assert result.exit_code == 1
        assert "Bereits erledigt." in result.stderr

    def test_done_nonexistent_id(self, temp_storage_dir):
        task = _make_task(status="pending")
        save_tasks([task])

        runner = CliRunner()
        result = runner.invoke(cli, ["done", "nonexistent"])
        assert result.exit_code == 1
        assert "Keine Aufgabe" in result.stderr

    def test_done_updates_timestamp(self, temp_storage_dir):
        task = _make_task(status="pending")
        old_updated = task.updated_at
        save_tasks([task])

        runner = CliRunner()
        result = runner.invoke(cli, ["done", task.id[:8]])
        assert result.exit_code == 0
        assert "erledigt markiert" in result.output

        from todo.storage import load_tasks

        tasks = load_tasks()
        assert tasks[0].updated_at != old_updated

    def test_done_ambiguous_prefix(self, temp_storage_dir):
        prefix = "abcdef12"
        task_a = _make_task(id=prefix + "-aaaa-bbbb-cccc-000000000001", status="pending")
        task_b = _make_task(id=prefix + "-aaaa-bbbb-cccc-000000000002", status="pending")
        save_tasks([task_a, task_b])

        runner = CliRunner()
        result = runner.invoke(cli, ["done", prefix])
        assert result.exit_code == 1
        assert "mehrere" in result.stderr
