import uuid
from datetime import UTC, datetime

import click

from todo.models import _DATE_PATTERN, Task
from todo.storage import load_tasks, save_tasks


@click.command()
@click.argument("description")
@click.option(
    "--priority",
    type=click.Choice(["low", "medium", "high"], case_sensitive=False),
    default="medium",
    help="Priorität der Aufgabe (low, medium, high)",
)
@click.option(
    "--due",
    default=None,
    help="Fälligkeitsdatum (YYYY-MM-DD)",
)
def add(description: str, priority: str, due: str | None):
    if due is not None and not _DATE_PATTERN.match(due):
        click.echo(
            f"Fehler: Fälligkeitsdatum muss YYYY-MM-DD sein, nicht '{due}'.",
            err=True,
        )
        raise SystemExit(1)

    now = datetime.now(UTC).isoformat()
    task = Task(
        id=str(uuid.uuid4()),
        description=description,
        status="pending",
        priority=priority,
        due_date=due,
        created_at=now,
        updated_at=now,
    )
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    click.echo(f"Aufgabe hinzugefügt: {task.id[:8]} - {description}")
