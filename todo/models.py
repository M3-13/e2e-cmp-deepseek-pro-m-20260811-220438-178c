import re
from dataclasses import dataclass

_PRIORITY_VALUES = frozenset({"low", "medium", "high"})
_STATUS_VALUES = frozenset({"pending", "done"})
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_priority(value: str) -> None:
    if value not in _PRIORITY_VALUES:
        raise ValueError(f"priority must be one of low, medium, high; got '{value}'")


def _validate_due_date(value: str | None) -> None:
    if value is not None and not _DATE_PATTERN.match(value):
        raise ValueError(f"due_date must be YYYY-MM-DD or None; got '{value}'")


@dataclass
class Task:
    id: str
    description: str
    status: str
    priority: str
    due_date: str | None
    created_at: str
    updated_at: str

    def __post_init__(self):
        if self.status not in _STATUS_VALUES:
            raise ValueError(f"status must be one of pending, done; got '{self.status}'")
        _validate_priority(self.priority)
        _validate_due_date(self.due_date)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        return cls(
            id=d["id"],
            description=d["description"],
            status=d["status"],
            priority=d["priority"],
            due_date=d.get("due_date"),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
        )
