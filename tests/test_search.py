import uuid
from datetime import datetime, timezone

from click.testing import CliRunner

from todo.cli import cli
from todo.models import Task


def _make_task(description: str) -> Task:
    now = datetime.now(timezone.utc).isoformat()
    return Task(
        id=str(uuid.uuid4()),
        description=description,
        status="pending",
        priority="medium",
        due_date=None,
        created_at=now,
        updated_at=now,
    )


class TestSearch:
    def test_search_with_matches(self, monkeypatch):
        tasks = [
            _make_task("Milch kaufen"),
            _make_task("Brot holen"),
            _make_task("Milchshake machen"),
        ]

        monkeypatch.setattr("todo.commands.search.load_tasks", lambda: list(tasks))

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "Milch"])
        assert result.exit_code == 0
        assert "Milch kaufen" in result.output
        assert "Milchshake machen" in result.output
        assert "Brot holen" not in result.output

    def test_search_no_matches(self, monkeypatch):
        tasks = [
            _make_task("Brot holen"),
            _make_task("Wasser kaufen"),
        ]

        monkeypatch.setattr("todo.commands.search.load_tasks", lambda: list(tasks))

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "Milch"])
        assert result.exit_code == 0
        assert "Keine Treffer." in result.output

    def test_search_case_insensitive(self, monkeypatch):
        tasks = [
            _make_task("MILCH kaufen"),
            _make_task("milch holen"),
            _make_task("MiLcHsHaKe"),
        ]

        monkeypatch.setattr("todo.commands.search.load_tasks", lambda: list(tasks))

        runner = CliRunner()
        result = runner.invoke(cli, ["search", "milch"])
        assert result.exit_code == 0
        assert "MILCH kaufen" in result.output
        assert "milch holen" in result.output
        assert "MiLcHsHaKe" in result.output
