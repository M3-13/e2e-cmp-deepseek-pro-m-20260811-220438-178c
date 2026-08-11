import click

from todo.storage import load_tasks, save_tasks


@click.command()
@click.argument("id")
def remove(id):
    tasks = load_tasks()

    matches = [t for t in tasks if t.id.startswith(id)]

    if not matches:
        click.echo(f"Keine Aufgabe mit ID-Präfix '{id}' gefunden.")
        return

    if len(matches) > 1:
        click.echo(f"ID-Präfix '{id}' ist nicht eindeutig ({len(matches)} Treffer).")
        return

    task = matches[0]

    answer = input(f"Aufgabe {task.description} löschen? [y/N] ")
    if answer.strip().lower() in ("y", "yes"):
        tasks.remove(task)
        save_tasks(tasks)
        click.echo(f"Aufgabe '{task.description}' gelöscht.")
    else:
        click.echo("Abgebrochen.")
