import click

from todo.display import format_table
from todo.models import Task
from todo.storage import load_tasks

_PRIORITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def _sort_key_priority(task: Task) -> int:
    return _PRIORITY_ORDER[task.priority]


def _sort_key_due(task: Task) -> tuple[bool, str]:
    return (task.due_date is None, task.due_date or "")


def _sort_key_created(task: Task) -> str:
    return task.created_at


_SORT_KEYS = {
    "priority": _sort_key_priority,
    "due": _sort_key_due,
    "created": _sort_key_created,
}


def _sort_tasks(tasks: list[Task], sort_by: str, asc: bool) -> list[Task]:
    key = _SORT_KEYS.get(sort_by)
    if key is None:
        return tasks
    return sorted(tasks, key=key, reverse=not asc)


@click.command()
@click.option("--sort", "sort_by", type=click.Choice(["priority", "due", "created"]), default=None)
@click.option("--asc/--desc", "ascending", default=True)
def list_cmd(sort_by: str | None, ascending: bool) -> None:
    tasks = load_tasks()
    if sort_by:
        tasks = _sort_tasks(tasks, sort_by, ascending)
    if not tasks:
        click.echo("Keine Aufgaben.")
        return
    click.echo(format_table(tasks))


@click.command()
@click.option("--status", "status", type=click.Choice(["pending", "done"]), required=True)
def filter_cmd(status: str) -> None:
    tasks = load_tasks()
    filtered = [t for t in tasks if t.status == status]
    if not filtered:
        click.echo("Keine Aufgaben.")
        return
    click.echo(format_table(filtered))


@click.command()
@click.option("--by", "sort_by", type=click.Choice(["priority", "due", "created"]), required=True)
@click.option("--asc/--desc", "ascending", default=True)
def sort_cmd(sort_by: str, ascending: bool) -> None:
    tasks = load_tasks()
    tasks = _sort_tasks(tasks, sort_by, ascending)
    if not tasks:
        click.echo("Keine Aufgaben.")
        return
    click.echo(format_table(tasks))
