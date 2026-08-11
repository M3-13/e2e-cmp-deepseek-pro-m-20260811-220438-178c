import uuid
from datetime import UTC, datetime

from click.testing import CliRunner

from todo.commands.remove import remove
from todo.models import Task
from todo.storage import load_tasks, save_tasks


def _make_task(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Testaufgabe",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


def test_remove_with_yes_confirmation(temp_storage_dir):
    task = _make_task(description="Einkaufen")
    save_tasks([task])

    runner = CliRunner()
    result = runner.invoke(remove, [task.id], input="y\n")

    assert result.exit_code == 0
    assert "Einkaufen" in result.output
    assert "gelöscht" in result.output

    remaining = load_tasks()
    assert len(remaining) == 0


def test_remove_abort_with_no(temp_storage_dir):
    task = _make_task(description="Putzen")
    save_tasks([task])

    runner = CliRunner()
    result = runner.invoke(remove, [task.id], input="n\n")

    assert result.exit_code == 0
    assert "Abgebrochen" in result.output

    remaining = load_tasks()
    assert len(remaining) == 1
    assert remaining[0].id == task.id


def test_remove_nonexistent_id(temp_storage_dir):
    task = _make_task(description="Lesen")
    save_tasks([task])

    runner = CliRunner()
    result = runner.invoke(remove, ["nonexistent"], input="y\n")

    assert result.exit_code == 0
    assert "Keine Aufgabe" in result.output

    remaining = load_tasks()
    assert len(remaining) == 1
    assert remaining[0].id == task.id


def test_remove_with_id_prefix_match(temp_storage_dir):
    task = _make_task(description="Bügeln")
    save_tasks([task])

    prefix = task.id[:8]
    runner = CliRunner()
    result = runner.invoke(remove, [prefix], input="y\n")

    assert result.exit_code == 0
    assert "Bügeln" in result.output
    assert "gelöscht" in result.output

    remaining = load_tasks()
    assert len(remaining) == 0


def test_remove_ambiguous_prefix(temp_storage_dir):
    prefix = "00000000-0000"
    task1 = _make_task(id=f"{prefix}-0001", description="Erste")
    task2 = _make_task(id=f"{prefix}-0002", description="Zweite")
    save_tasks([task1, task2])

    runner = CliRunner()
    result = runner.invoke(remove, [prefix])

    assert result.exit_code == 0
    assert "nicht eindeutig" in result.output

    remaining = load_tasks()
    assert len(remaining) == 2


def test_remove_default_no_on_empty_input(temp_storage_dir):
    task = _make_task(description="Schlafen")
    save_tasks([task])

    runner = CliRunner()
    result = runner.invoke(remove, [task.id], input="\n")

    assert result.exit_code == 0
    assert "Abgebrochen" in result.output

    remaining = load_tasks()
    assert len(remaining) == 1
    assert remaining[0].id == task.id
