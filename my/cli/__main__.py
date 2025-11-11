"""
My personal command line tool.

Dynamically loads apps from submodules in `my/cli`.
"""

import importlib

import typer

from my import CLI_DIR, REPO_DIR

app = typer.Typer(no_args_is_help=True, help=__doc__)


def load_my_apps():
  for module_path in CLI_DIR.iterdir():
    if module_path.is_dir() and (module_path / "__init__.py").exists():
      module_name: str = f"my.cli.{module_path.name}"
      try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "app"):
          app.add_typer(mod.app, name=module_path.name)
      except Exception as e:
        typer.echo(f"Failed to load {module_name}: {e}")


@app.command()
def version():
  """Show the version of the tool."""
  typer.echo((REPO_DIR / "VERSION").read_text().strip())


@app.callback()
def verbose_mode(
  verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
):
  """Enable verbose mode."""
  from my import cli

  cli.VERBOSE = verbose


load_my_apps()

if __name__ == "__main__":
  app()
