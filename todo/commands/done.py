import sys
from datetime import datetime, timezone

import click

from todo.storage import load_tasks, save_tasks


@click.command()
@click.argument("id", type=str)
def done(id: str) -> None:
    tasks = load_tasks()

    match = None
    for t in tasks:
        if t.id.startswith(id):
            match = t
            break

    if match is None:
        print("Aufgabe nicht gefunden.", file=sys.stderr)
        raise SystemExit(1)

    if match.status == "done":
        print("Bereits erledigt.", file=sys.stderr)
        raise SystemExit(1)

    match.status = "done"
    match.updated_at = datetime.now(timezone.utc).isoformat()
    save_tasks(tasks)
