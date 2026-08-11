from todo.models import Task

_STATUS_GLYPH = {"pending": "\u2717", "done": "\u2713"}


def format_table(tasks: list[Task]) -> str:
    if not tasks:
        return ""

    widths = _compute_widths(tasks)
    header = (
        f"{'ID'.ljust(widths['id'])}  "
        f"{'Status'.ljust(widths['status'])}  "
        f"{'Priorität'.ljust(widths['priority'])}  "
        f"{'Fälligkeit'.ljust(widths['due_date'])}  "
        f"{'Beschreibung'.ljust(widths['description'])}"
    )
    separator = (
        f"{'-' * widths['id']}  "
        f"{'-' * widths['status']}  "
        f"{'-' * widths['priority']}  "
        f"{'-' * widths['due_date']}  "
        f"{'-' * widths['description']}"
    )
    lines = [header, separator]
    for task in tasks:
        lines.append(_format_row(task, widths))
    return "\n".join(lines)


def _compute_widths(tasks: list[Task]) -> dict[str, int]:
    id_width = max(8, max((len(t.id[:8]) for t in tasks), default=8))
    status_width = max(6, max((len(_STATUS_GLYPH.get(t.status, "?")) for t in tasks), default=6))
    priority_width = max(9, max((len(t.priority) for t in tasks), default=9))
    due_date_width = max(
        10,
        max((len(t.due_date) if t.due_date else 0 for t in tasks), default=10),
    )
    desc_width = max(12, max((len(t.description) for t in tasks), default=12))
    return {
        "id": id_width,
        "status": status_width,
        "priority": priority_width,
        "due_date": due_date_width,
        "description": desc_width,
    }


def _format_row(task: Task, widths: dict[str, int]) -> str:
    id_str = task.id[:8]
    status_str = _STATUS_GLYPH.get(task.status, "?")
    due_str = task.due_date if task.due_date else ""
    return (
        f"{id_str.ljust(widths['id'])}  "
        f"{status_str.ljust(widths['status'])}  "
        f"{task.priority.ljust(widths['priority'])}  "
        f"{due_str.ljust(widths['due_date'])}  "
        f"{task.description.ljust(widths['description'])}"
    )
