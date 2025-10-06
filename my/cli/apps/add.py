import shutil
import uuid

import slugify
import typer

from my import CLI_DIR


def _get_app_dir(name: str):
  return CLI_DIR / name


def _app_dir_exists(name: str) -> bool:
  return _get_app_dir(name).exists()


def validate_app_name(name: str, allow_existing: bool = False) -> str:
  slug = slugify.slugify(name)
  if slug != name:
    raise ValueError(f"Invalid app name '{name}'. Must be a slug, e.g.: '{slug}'")
  if _app_dir_exists(slug) and not allow_existing:
    raise ValueError(f"App '{slug}' already exists.")
  return slug


def add_app(name: str, desc: str, overwrite: bool = False):
  if _app_dir_exists(name) and overwrite:
    typer.echo(f"Removing existing app '{name}'...")
    shutil.rmtree(_get_app_dir(name))

  typer.echo(f"Adding new app '{name}'...")
  _get_app_dir(name).mkdir(exist_ok=False)
  init_file = _get_app_dir(name) / "__init__.py"
  lines = [
    f'"""\n{desc or name}\n"""',
    "",
    "import typer",
    "",
    "APP_ID = " + repr(str(uuid.uuid4())),
    "",
    "app = typer.Typer(help=__doc__)",
  ]
  init_file.write_text("\n".join(lines))
  typer.echo(f"Created {init_file}")
