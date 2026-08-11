import uuid
from datetime import UTC, datetime

from click.testing import CliRunner

from todo.cli import cli
from todo.models import Task


def _make_task(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Test task",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestList:
    def test_list_empty(self, monkeypatch):
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Keine Aufgaben." in result.output

    def test_list_with_tasks(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Task 1",
            status="pending",
            priority="low",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="Task 2",
            status="done",
            priority="high",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t1, t2])

        runner = CliRunner()
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" in result.output
        assert "ID" in result.output
        assert "Status" in result.output

    def test_list_sort_by_priority_asc(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Low",
            priority="low",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="High",
            priority="high",
        )
        t3 = _make_task(
            id="00000000-0000-0000-0000-000000000003",
            description="Medium",
            priority="medium",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t2, t1, t3])

        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--sort", "priority", "--asc"])
        assert result.exit_code == 0
        low_pos = result.output.index("Low")
        medium_pos = result.output.index("Medium")
        high_pos = result.output.index("High")
        assert low_pos < medium_pos < high_pos

    def test_list_sort_by_priority_desc(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Low",
            priority="low",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="High",
            priority="high",
        )
        t3 = _make_task(
            id="00000000-0000-0000-0000-000000000003",
            description="Medium",
            priority="medium",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t2, t1, t3])

        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--sort", "priority", "--desc"])
        assert result.exit_code == 0
        low_pos = result.output.index("Low")
        medium_pos = result.output.index("Medium")
        high_pos = result.output.index("High")
        assert high_pos < medium_pos < low_pos

    def test_list_sort_by_due_asc(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="NoDue",
            due_date=None,
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="Early",
            due_date="2025-01-01",
        )
        t3 = _make_task(
            id="00000000-0000-0000-0000-000000000003",
            description="Later",
            due_date="2025-12-31",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t1, t3, t2])

        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--sort", "due", "--asc"])
        assert result.exit_code == 0
        early_pos = result.output.index("Early")
        later_pos = result.output.index("Later")
        nodue_pos = result.output.index("NoDue")
        assert early_pos < later_pos < nodue_pos

    def test_list_sort_by_created_desc(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Old",
            created_at="2020-01-01T00:00:00+00:00",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="New",
            created_at="2025-01-01T00:00:00+00:00",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t1, t2])

        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--sort", "created", "--desc"])
        assert result.exit_code == 0
        new_pos = result.output.index("New")
        old_pos = result.output.index("Old")
        assert new_pos < old_pos

    def test_list_cli_accessible(self, monkeypatch):
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "list" in result.output


class TestFilter:
    def test_filter_pending(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Pending 1",
            status="pending",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="Done 1",
            status="done",
        )
        t3 = _make_task(
            id="00000000-0000-0000-0000-000000000003",
            description="Pending 2",
            status="pending",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t1, t2, t3])

        runner = CliRunner()
        result = runner.invoke(cli, ["filter", "--status", "pending"])
        assert result.exit_code == 0
        assert "Pending 1" in result.output
        assert "Pending 2" in result.output
        assert "Done 1" not in result.output

    def test_filter_done(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Pending",
            status="pending",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="Done 1",
            status="done",
        )
        t3 = _make_task(
            id="00000000-0000-0000-0000-000000000003",
            description="Done 2",
            status="done",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t1, t2, t3])

        runner = CliRunner()
        result = runner.invoke(cli, ["filter", "--status", "done"])
        assert result.exit_code == 0
        assert "Pending" not in result.output
        assert "Done 1" in result.output
        assert "Done 2" in result.output

    def test_filter_empty(self, monkeypatch):
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["filter", "--status", "pending"])
        assert result.exit_code == 0
        assert "Keine Aufgaben." in result.output

    def test_filter_status_required(self, monkeypatch):
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["filter"])
        assert result.exit_code != 0

    def test_filter_cli_accessible(self, monkeypatch):
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "filter" in result.output


class TestSort:
    def test_sort_by_priority_asc(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Low",
            priority="low",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="High",
            priority="high",
        )
        t3 = _make_task(
            id="00000000-0000-0000-0000-000000000003",
            description="Medium",
            priority="medium",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t2, t1, t3])

        runner = CliRunner()
        result = runner.invoke(cli, ["sort", "--by", "priority", "--asc"])
        assert result.exit_code == 0
        low_pos = result.output.index("Low")
        medium_pos = result.output.index("Medium")
        high_pos = result.output.index("High")
        assert low_pos < medium_pos < high_pos

    def test_sort_by_priority_desc(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Low",
            priority="low",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="High",
            priority="high",
        )
        t3 = _make_task(
            id="00000000-0000-0000-0000-000000000003",
            description="Medium",
            priority="medium",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t2, t1, t3])

        runner = CliRunner()
        result = runner.invoke(cli, ["sort", "--by", "priority", "--desc"])
        assert result.exit_code == 0
        low_pos = result.output.index("Low")
        medium_pos = result.output.index("Medium")
        high_pos = result.output.index("High")
        assert high_pos < medium_pos < low_pos

    def test_sort_by_due_asc(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="NoDue",
            due_date=None,
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="Early",
            due_date="2025-01-01",
        )
        t3 = _make_task(
            id="00000000-0000-0000-0000-000000000003",
            description="Later",
            due_date="2025-12-31",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t1, t3, t2])

        runner = CliRunner()
        result = runner.invoke(cli, ["sort", "--by", "due", "--asc"])
        assert result.exit_code == 0
        early_pos = result.output.index("Early")
        later_pos = result.output.index("Later")
        nodue_pos = result.output.index("NoDue")
        assert early_pos < later_pos < nodue_pos

    def test_sort_by_created_desc(self, monkeypatch):
        t1 = _make_task(
            id="00000000-0000-0000-0000-000000000001",
            description="Old",
            created_at="2020-01-01T00:00:00+00:00",
        )
        t2 = _make_task(
            id="00000000-0000-0000-0000-000000000002",
            description="New",
            created_at="2025-01-01T00:00:00+00:00",
        )
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [t1, t2])

        runner = CliRunner()
        result = runner.invoke(cli, ["sort", "--by", "created", "--desc"])
        assert result.exit_code == 0
        new_pos = result.output.index("New")
        old_pos = result.output.index("Old")
        assert new_pos < old_pos

    def test_sort_empty(self, monkeypatch):
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["sort", "--by", "priority"])
        assert result.exit_code == 0
        assert "Keine Aufgaben." in result.output

    def test_sort_cli_accessible(self, monkeypatch):
        monkeypatch.setattr("todo.commands.list_cmd.load_tasks", lambda: [])

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "sort" in result.output
