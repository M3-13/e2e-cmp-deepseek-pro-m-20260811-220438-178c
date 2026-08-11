import json
import sys

import click

from todo.storage import load_tasks


@click.command()
@click.option(
    "--output",
    default=None,
    type=str,
    help="Ausgabedatei (Standard: stdout)",
)
def export(output: str | None):
    tasks = load_tasks()
    data = [t.to_dict() for t in tasks]
    json_text = json.dumps(data, ensure_ascii=False, indent=2)

    if output is None:
        click.echo(json_text)
    else:
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(json_text)
        except OSError as exc:
            print(f"Error: could not write to '{output}': {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
