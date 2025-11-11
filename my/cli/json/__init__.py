"""
json utilities
"""

from pathlib import Path

import typer

APP_ID = "975b23f4-18a6-4708-b4e6-e2746ceb238b"

app = typer.Typer(help=__doc__, no_args_is_help=True)


@app.command()
def sort_file(file: Path, list_path: str, key_path: str):
  """Sorts a JSON file by a specific key."""
  from my.cli.json.sort_file import main

  main(file, list_path, key_path)
