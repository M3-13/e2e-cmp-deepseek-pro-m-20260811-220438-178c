import re
from datetime import UTC, datetime

import click

from todo.storage import load_tasks, save_tasks

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as err:
        raise ValueError(f"Ungültiges Datum: '{date_str}'. Erwartet: YYYY-MM-DD.") from err


@click.command()
@click.argument("id")
@click.argument("date", required=False)
@click.option("--clear", is_flag=True, default=False)
def due_date(id: str, date: str | None, clear: bool) -> None:
    if clear and date is not None:
        click.echo("Fehler: --clear und date schließen sich gegenseitig aus.", err=True)
        raise SystemExit(1)
    if not clear and date is None:
        click.echo("Fehler: entweder date oder --clear angeben.", err=True)
        raise SystemExit(1)

    if date is not None:
        if not _DATE_PATTERN.match(date):
            click.echo(f"Ungültiges Datum: '{date}'. Erwartet: YYYY-MM-DD.", err=True)
            raise SystemExit(1)
        try:
            _parse_date(date)
        except ValueError as exc:
            click.echo(str(exc), err=True)
            raise SystemExit(1) from None

    tasks = load_tasks()
    matched = [t for t in tasks if t.id.startswith(id)]
    if not matched:
        click.echo(f"Keine Aufgabe mit ID-Präfix '{id}' gefunden.", err=True)
        raise SystemExit(1)
    if len(matched) > 1:
        click.echo(f"ID-Präfix '{id}' passt auf mehrere Aufgaben.", err=True)
        raise SystemExit(1)

    task = matched[0]

    if clear:
        task.due_date = None
        click.echo(f"Fälligkeitsdatum von Aufgabe {task.id[:8]} entfernt.")
    else:
        task.due_date = date
        click.echo(f"Fälligkeitsdatum von Aufgabe {task.id[:8]} auf '{date}' gesetzt.")

    task.updated_at = datetime.now(UTC).isoformat()
    save_tasks(tasks)
