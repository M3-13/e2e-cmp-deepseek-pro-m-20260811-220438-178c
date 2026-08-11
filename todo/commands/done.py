from datetime import UTC, datetime

import click

from todo.storage import load_tasks, save_tasks


@click.command()
@click.argument("id", type=str)
def done(id: str) -> None:
    tasks = load_tasks()
    matched = [t for t in tasks if t.id.startswith(id)]

    if not matched:
        click.echo(f"Keine Aufgabe mit ID-Präfix '{id}' gefunden.", err=True)
        raise SystemExit(1)

    if len(matched) > 1:
        click.echo(f"ID-Präfix '{id}' passt auf mehrere Aufgaben.", err=True)
        raise SystemExit(1)

    task = matched[0]

    if task.status == "done":
        click.echo("Bereits erledigt.", err=True)
        raise SystemExit(1)

    task.status = "done"
    task.updated_at = datetime.now(UTC).isoformat()
    save_tasks(tasks)
    click.echo(f"Aufgabe {task.id[:8]} als erledigt markiert.")
