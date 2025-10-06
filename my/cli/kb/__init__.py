"""
Manage my personal knowledge base.
"""

import typer

APP_ID = "779c8ae5-87da-41bc-85a4-6bbe364e36ab"

app = typer.Typer(no_args_is_help=True, help=__doc__)


@app.command()
def add(item: str):
  """Add a new item to the knowledge base."""
  typer.echo(f"Adding '{item}' to the knowledge base...")


@app.command()
def list():
  """List all items in the knowledge base."""
  typer.echo("Listing all items in the knowledge base...")
