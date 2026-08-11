import click

from todo.commands.add import add
from todo.commands.done import done
from todo.commands.due_date import due_date
from todo.commands.edit import edit
from todo.commands.export import export
from todo.commands.import_cmd import import_cmd
from todo.commands.list_cmd import filter_cmd, list_cmd, sort_cmd
from todo.commands.priority import priority
from todo.commands.remove import remove
from todo.commands.search import search
from todo.commands.stats import stats


@click.group()
def cli():
    pass


cli.add_command(add)
cli.add_command(list_cmd, name="list")
cli.add_command(filter_cmd, name="filter")
cli.add_command(sort_cmd, name="sort")
cli.add_command(done)
cli.add_command(remove)
cli.add_command(edit)
cli.add_command(priority)
cli.add_command(due_date)
cli.add_command(search)
cli.add_command(export)
cli.add_command(import_cmd, name="import")
cli.add_command(stats)


if __name__ == "__main__":
    cli()
