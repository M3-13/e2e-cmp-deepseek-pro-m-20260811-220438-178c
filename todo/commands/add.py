import re
import sys
import uuid
from datetime import datetime, timezone

import click

from todo.models import Task
from todo.storage import load_tasks, save_tasks

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
        print(
            f"Error: due date must be YYYY-MM-DD, got '{due}'",
            file=sys.stderr,
        )
        raise SystemExit(1)

    now = datetime.now(timezone.utc).isoformat()
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
