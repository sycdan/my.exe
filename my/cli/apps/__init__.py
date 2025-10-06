"""Manage my CLI apps."""

import typer

app = typer.Typer(no_args_is_help=True, help=__doc__)


@app.command()
def add(name: str, desc: str = "", force: bool = False):
  """Add a new app to the CLI."""
  from my.cli.apps.add import add_app, validate_app_name

  add_app(validate_app_name(name, allow_existing=force), desc, force)
