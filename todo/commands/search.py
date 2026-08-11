import click

from todo.display import format_table
from todo.storage import load_tasks


@click.command()
@click.argument("query")
def search(query: str):
    tasks = load_tasks()
    query_lower = query.lower()
    matches = [t for t in tasks if query_lower in t.description.lower()]
    if not matches:
        click.echo("Keine Treffer.")
    else:
        click.echo(format_table(matches))
