from datetime import UTC, datetime

import click

from todo.storage import load_tasks, save_tasks


@click.command()
@click.argument("id")
@click.argument("description")
def edit(id: str, description: str) -> None:
    tasks = load_tasks()
    matched = [t for t in tasks if t.id.startswith(id)]
    if not matched:
        click.echo(f"Keine Aufgabe mit ID-Präfix '{id}' gefunden.", err=True)
        raise SystemExit(1)
    if len(matched) > 1:
        click.echo(f"ID-Präfix '{id}' passt auf mehrere Aufgaben.", err=True)
        raise SystemExit(1)
    task = matched[0]
    task.description = description
    task.updated_at = datetime.now(UTC).isoformat()
    save_tasks(tasks)
    click.echo(f"Beschreibung von Aufgabe {task.id[:8]} geändert.")
