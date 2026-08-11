import uuid
from datetime import UTC, datetime

import pytest

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


class TestTaskCreation:
    def test_default_valid_task(self):
        task = _make_task()
        assert task.status == "pending"
        assert task.priority == "medium"
        assert task.due_date is None

    def test_task_with_due_date(self):
        task = _make_task(due_date="2025-12-24")
        assert task.due_date == "2025-12-24"

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="status must be one of"):
            _make_task(status="invalid")

    def test_invalid_priority_raises(self):
        with pytest.raises(ValueError, match="priority must be one of"):
            _make_task(priority="critical")

    def test_invalid_due_date_format_raises(self):
        with pytest.raises(ValueError, match="due_date must be YYYY-MM-DD"):
            _make_task(due_date="24.12.2025")

    def test_invalid_due_date_missing_parts_raises(self):
        with pytest.raises(ValueError, match="due_date must be YYYY-MM-DD"):
            _make_task(due_date="2025-12")

    def test_done_status_accepted(self):
        task = _make_task(status="done")
        assert task.status == "done"

    def test_all_priority_values_accepted(self):
        for prio in ("low", "medium", "high"):
            task = _make_task(priority=prio)
            assert task.priority == prio


class TestToDict:
    def test_to_dict_has_all_keys(self):
        task = _make_task(due_date="2025-01-01")
        d = task.to_dict()
        assert set(d.keys()) == {
            "id",
            "description",
            "status",
            "priority",
            "due_date",
            "created_at",
            "updated_at",
        }

    def test_to_dict_none_due_date(self):
        task = _make_task(due_date=None)
        d = task.to_dict()
        assert d["due_date"] is None


class TestFromDict:
    def test_roundtrip(self):
        task = _make_task(description="Roundtrip test", due_date="2026-01-01")
        d = task.to_dict()
        restored = Task.from_dict(d)
        assert restored.id == task.id
        assert restored.description == task.description
        assert restored.status == task.status
        assert restored.priority == task.priority
        assert restored.due_date == task.due_date
        assert restored.created_at == task.created_at
        assert restored.updated_at == task.updated_at

    def test_from_dict_missing_optional_due_date(self):
        d = {
            "id": str(uuid.uuid4()),
            "description": "No due date",
            "status": "pending",
            "priority": "low",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        task = Task.from_dict(d)
        assert task.due_date is None

    def test_from_dict_missing_required_field_raises(self):
        d = {
            "id": str(uuid.uuid4()),
            "description": "No status",
            "priority": "low",
        }
        with pytest.raises(KeyError):
            Task.from_dict(d)

    def test_from_dict_invalid_data_raises(self):
        d = {
            "id": str(uuid.uuid4()),
            "description": "Bad priority",
            "status": "pending",
            "priority": "invalid",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        with pytest.raises(ValueError):
            Task.from_dict(d)

    def test_from_dict_missing_updated_at_falls_back_to_created_at(self):
        created = datetime.now(UTC).isoformat()
        d = {
            "id": str(uuid.uuid4()),
            "description": "No updated_at",
            "status": "pending",
            "priority": "medium",
            "created_at": created,
        }
        task = Task.from_dict(d)
        assert task.updated_at == created
