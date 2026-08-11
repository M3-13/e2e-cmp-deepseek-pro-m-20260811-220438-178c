from click.testing import CliRunner

from todo.cli import cli


class TestAdd:
    def test_add_without_options(self, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.add.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.add.save_tasks", fake_save)

        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Milch kaufen"])
        assert result.exit_code == 0
        assert "Aufgabe hinzugefügt:" in result.output
        assert "Milch kaufen" in result.output
        assert len(tasks_backing) == 1
        task = tasks_backing[0]
        assert task.description == "Milch kaufen"
        assert task.status == "pending"
        assert task.priority == "medium"
        assert task.due_date is None

    def test_add_with_priority_and_due(self, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.add.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.add.save_tasks", fake_save)

        runner = CliRunner()
        result = runner.invoke(
            cli, ["add", "Milch kaufen", "--priority", "high", "--due", "2025-12-24"]
        )
        assert result.exit_code == 0
        assert "Aufgabe hinzugefügt:" in result.output
        assert "Milch kaufen" in result.output
        assert len(tasks_backing) == 1
        task = tasks_backing[0]
        assert task.description == "Milch kaufen"
        assert task.priority == "high"
        assert task.due_date == "2025-12-24"
        assert task.status == "pending"

    def test_add_with_invalid_due_date(self, temp_storage_dir, monkeypatch):
        tasks_backing: list = []

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.add.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.add.save_tasks", fake_save)

        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Test", "--due", "not-a-date"])
        assert result.exit_code == 1
        assert "YYYY-MM-DD" in result.output or "YYYY-MM-DD" in result.stderr

    def test_add_appends_to_existing_tasks(self, temp_storage_dir, monkeypatch):
        import uuid
        from datetime import datetime, timezone

        from todo.models import Task

        existing = Task(
            id=str(uuid.uuid4()),
            description="Vorhandene Aufgabe",
            status="pending",
            priority="low",
            due_date=None,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        tasks_backing: list = [existing]

        def fake_load():
            return list(tasks_backing)

        def fake_save(tasks):
            tasks_backing.clear()
            tasks_backing.extend(tasks)

        monkeypatch.setattr("todo.commands.add.load_tasks", fake_load)
        monkeypatch.setattr("todo.commands.add.save_tasks", fake_save)

        runner = CliRunner()
        result = runner.invoke(cli, ["add", "Neue Aufgabe"])
        assert result.exit_code == 0
        assert len(tasks_backing) == 2
        assert tasks_backing[0].id == existing.id
        assert tasks_backing[1].description == "Neue Aufgabe"
