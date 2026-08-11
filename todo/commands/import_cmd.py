import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import click

from todo.models import _DATE_PATTERN, _PRIORITY_VALUES, _STATUS_VALUES, Task
from todo.storage import load_tasks, save_tasks


def _read_import_tasks(file_path: str) -> list[Task]:
    path = Path(file_path)
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        click.echo(f"Fehler: Datei '{file_path}' kann nicht gelesen werden: {exc}", err=True)
        raise SystemExit(1) from exc

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        click.echo(f"Fehler: '{file_path}' enthält ungültiges JSON: {exc}", err=True)
        raise SystemExit(1) from exc

    if not isinstance(data, list):
        click.echo(f"Fehler: '{file_path}' enthält kein JSON-Array", err=True)
        raise SystemExit(1)

    tasks: list[Task] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            click.echo(f"Fehler: Eintrag {idx} in '{file_path}' ist kein JSON-Objekt", err=True)
            raise SystemExit(1)
        if "description" not in item or not isinstance(item["description"], str):
            click.echo(
                f"Fehler: Eintrag {idx} in '{file_path}' hat kein gültiges 'description'-Feld",
                err=True,
            )
            raise SystemExit(1)

        now = datetime.now(UTC).isoformat()
        status = item.get("status", "pending")
        if status not in _STATUS_VALUES:
            click.echo(
                f"Warnung: Eintrag {idx} hat ungültigen Status '{status}', verwende 'pending'.",
                err=True,
            )
            status = "pending"

        priority = item.get("priority", "medium")
        if priority not in _PRIORITY_VALUES:
            click.echo(
                f"Warnung: Eintrag {idx} hat ungültige Priorität '{priority}', verwende 'medium'.",
                err=True,
            )
            priority = "medium"

        due_date = item.get("due_date")
        if due_date is not None and (
            not isinstance(due_date, str) or not _DATE_PATTERN.match(due_date)
        ):
            click.echo(
                f"Fehler: Eintrag {idx} in '{file_path}' hat ein ungültiges 'due_date' "
                "(erwartet: YYYY-MM-DD)",
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
