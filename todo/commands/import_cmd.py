import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import click

from todo.models import _DATE_PATTERN, Task
from todo.storage import load_tasks, save_tasks

_VALID_STATUSES = frozenset({"pending", "done"})
_VALID_PRIORITIES = frozenset({"low", "medium", "high"})


def _read_import_tasks(file_path: str) -> list[Task]:
    path = Path(file_path)
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        click.echo(f"Error: cannot read file '{file_path}': {exc}", err=True)
        raise SystemExit(1) from exc

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: '{file_path}' contains invalid JSON: {exc}", err=True)
        raise SystemExit(1) from exc

    if not isinstance(data, list):
        click.echo(f"Error: '{file_path}' does not contain a JSON array", err=True)
        raise SystemExit(1)

    tasks: list[Task] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            click.echo(f"Error: entry {idx} in '{file_path}' is not a JSON object", err=True)
            raise SystemExit(1)
        if "description" not in item or not isinstance(item["description"], str):
            click.echo(
                f"Error: entry {idx} in '{file_path}' is missing a valid 'description' field",
                err=True,
            )
            raise SystemExit(1)

        now = datetime.now(timezone.utc).isoformat()
        status = item.get("status", "pending")
        if status not in _VALID_STATUSES:
            status = "pending"

        priority = item.get("priority", "medium")
        if priority not in _VALID_PRIORITIES:
            priority = "medium"

        due_date = item.get("due_date")
        if due_date is not None and (
            not isinstance(due_date, str) or not _DATE_PATTERN.match(due_date)
        ):
            click.echo(
                f"Error: entry {idx} in '{file_path}' has an invalid 'due_date' "
                "(expected YYYY-MM-DD)",
                err=True,
            )
            raise SystemExit(1)

        task_id = item.get("id", str(uuid.uuid4()))
        created_at = item.get("created_at", now)
        updated_at = item.get("updated_at", now)

        task = Task(
            id=str(task_id),
            description=item["description"],
            status=status,
            priority=priority,
            due_date=due_date,
            created_at=str(created_at),
            updated_at=str(updated_at),
        )
        tasks.append(task)

    return tasks


@click.command()
@click.option("--file", required=True, help="Path to the JSON file to import")
@click.option(
    "--merge",
    is_flag=True,
    default=False,
    help="Merge imported tasks with existing ones (skip duplicates)",
)
def import_cmd(file: str, merge: bool):
    imported = _read_import_tasks(file)

    if merge:
        existing = load_tasks()
        existing_keys = {(t.description, t.status) for t in existing}
        added_count = 0
        for task in imported:
            if (task.description, task.status) not in existing_keys:
                existing.append(task)
                existing_keys.add((task.description, task.status))
                added_count += 1
        save_tasks(existing)
        skipped = len(imported) - added_count
        msg = f"Importiert: {added_count} Aufgabe(n)"
        if skipped:
            msg += f"; übersprungen: {skipped}"
        click.echo(msg)
    else:
        save_tasks(imported)
        click.echo(
            f"Importiert: {len(imported)} Aufgabe(n) (bestehende Aufgaben wurden überschrieben)"
        )
