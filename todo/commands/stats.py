from collections import Counter

import click

from todo.storage import load_tasks


@click.command()
def stats():
    tasks = load_tasks()
    total = len(tasks)
    pending = sum(1 for t in tasks if t.status == "pending")
    done = sum(1 for t in tasks if t.status == "done")
    priority_counts: Counter[str] = Counter(t.priority for t in tasks)

    click.echo(f"Gesamt: {total}")
    click.echo(f"Pending: {pending}")
    click.echo(f"Done: {done}")
    click.echo()
    click.echo("Nach Priorität:")
    for prio in ("low", "medium", "high"):
        click.echo(f"  {prio}: {priority_counts.get(prio, 0)}")
