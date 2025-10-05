"""My personal command line tool."""

import typer

from my import REPO_DIR

app = typer.Typer(no_args_is_help=True, help=__doc__)


@app.command()
def version():
  """Show the version of the tool."""
  typer.echo((REPO_DIR / "VERSION").read_text().strip())


if __name__ == "__main__":
  app()
