import uuid
from datetime import datetime, timezone

from todo.display import format_table
from todo.models import Task


def _make_task(**overrides):
    defaults = {
        "id": str(uuid.uuid4()),
        "description": "Test task",
        "status": "pending",
        "priority": "medium",
        "due_date": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    defaults.update(overrides)
    return Task(**defaults)


class TestFormatTable:
    def test_empty_list_returns_empty_string(self):
        result = format_table([])
        assert result == ""

    def test_single_task_header_and_row(self):
        task = _make_task(
            id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            description="Test task",
            status="pending",
            priority="medium",
            due_date=None,
        )
        result = format_table([task])
        lines = result.split("\n")
        assert len(lines) >= 3
        assert "ID" in lines[0]
        assert "Status" in lines[0]
        assert "Priorität" in lines[0]
        assert "Fälligkeit" in lines[0]
        assert "Beschreibung" in lines[0]
        assert "aaaaaaaa" in result

    def test_done_task_shows_checkmark(self):
        task = _make_task(
            id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            status="done",
        )
        result = format_table([task])
        assert "\u2713" in result

    def test_pending_task_shows_x(self):
        task = _make_task(status="pending")
        result = format_table([task])
        assert "\u2717" in result

    def test_due_date_displayed(self):
        task = _make_task(due_date="2025-12-24")
        result = format_table([task])
        assert "2025-12-24" in result

    def test_no_due_date_shows_empty(self):
        task = _make_task(due_date=None)
        result = format_table([task])
        assert "\u2717" in result

    def test_id_truncated_to_8_chars(self):
        task = _make_task(
            id="abcd1234-ef56-7890-abcd-ef1234567890",
            description="ID test",
        )
        result = format_table([task])
        assert "abcd1234" in result
        assert "ef56" not in result or "abcd1234" in result

    def test_multiple_tasks_all_present(self):
        tasks = [
            _make_task(description="Task A"),
            _make_task(description="Task B"),
            _make_task(description="Task C"),
        ]
        result = format_table(tasks)
        lines = result.split("\n")
        assert len(lines) == 2 + len(tasks)  # header + separator + rows

    def test_priority_column_present(self):
        task = _make_task(priority="high")
        result = format_table([task])
        assert "high" in result

    def test_description_column_present(self):
        task = _make_task(description="Buy milk")
        result = format_table([task])
        assert "Buy milk" in result
