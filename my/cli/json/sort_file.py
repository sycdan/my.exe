import json
import re
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

import json5
from uuid7gen import uuid7

from my import cli

UUID_ON_LINE = (
  r'^\s*"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'
)
"""A regex to match a UUID at the start of a JSON line."""


@dataclass
class Substitution:
  id: uuid.UUID
  original_line: str
  original_line_idx: int

  @property
  def original_line_num(self):
    return self.original_line_idx + 1


def _get_line_idx_from_error(error: str) -> int | None:
  """Extract the line number from an error message.
  e.g. '<string>:2 Unexpected "," at column 55'
  """
  match = re.search(r"<string>:(\d+)", error)
  if match:
    return int(match.group(1)) - 1
  return None


def _try_load(lines: list[str], last_failed_line_idx: int | None):
  """Try to load the current state of the JSON. If it fails, return the error so we can try to fix it."""
  try:
    return json5.loads("\n".join(lines)), None, None
  except ValueError as e:
    failed_line_idx = _get_line_idx_from_error(str(e))
    if last_failed_line_idx == failed_line_idx:
      # We failed to fix the problem, so just stop trying.
      return None
    return None, failed_line_idx, str(e)


def _get_by_path(d: dict, path: str):
  for part in path.split("."):
    d = d.get(part, {})
  return d


def _sort_in_place(data_list: list[dict], key_path: str = "id"):
  def __key(item: dict):
    if isinstance(item, dict):
      key_value = _get_by_path(item, key_path)
      return str(key_value).casefold()
    return ""

  data_list.sort(key=__key)


def _reverse_substitutions(data: dict, subs: dict[uuid.UUID, Substitution]):
  """Reverse the substitutions we made while loading the JSON."""
  sub_lines = json.dumps(data, indent=2).splitlines()
  new_lines = []
  for line in sub_lines:
    if match := re.match(UUID_ON_LINE, line):
      sub_id = uuid.UUID(match.group(1))
      if sub_id in subs:
        sub = subs[sub_id]
        line = sub.original_line
    new_lines.append(line)
  return "\n".join(new_lines)


def _is_commented_line(line: str) -> bool:
  """Check if a entire line is a comment."""
  return line.lstrip().startswith("//")


def _inject_substitution(line: str, sub: Substitution, as_kvp=False) -> str:
  """Inject a substitution UUID into a commented line."""
  line = line.lstrip().lstrip("/").lstrip()
  if line.startswith('"'):
    # This line looks like a JSON value, so we can inject the UUID as a prefix.
    return f'"{sub.id}{line[1:]}'
  # Otherwise, we'll have to guess the line type and fix it later if we're wrong.
  if as_kvp:
    return f'"{sub.id}": null,'
  return f'"{sub.id}",'


def main(file_path: Path, list_path: str, key_path: str, indent: int = 2):
  """Sorts a JSON file by a specific key. Preserves comments."""
  new_lines = []
  subs: dict[uuid.UUID, Substitution] = {}
  subs_by_line_idx: dict[int, Substitution] = {}

  old_lines = file_path.read_text().splitlines()
  for line_idx, line in enumerate(old_lines):
    if _is_commented_line(line):
      sub = Substitution(uuid7(), line, original_line_idx=line_idx)
      subs[sub.id] = sub
      subs_by_line_idx[sub.original_line_idx] = sub
      line = _inject_substitution(line, sub)
    new_lines.append(line)
  del old_lines

  if subs and cli.VERBOSE:
    print("Substitutions:", file=sys.stderr)
    for sub in subs.values():
      print(
        f"{sub.id} (line {sub.original_line_num}): {sub.original_line}",
        file=sys.stderr,
      )

  last_failed_line_idx = None
  while result := _try_load(new_lines, last_failed_line_idx):
    data, failed_line_idx, error_msg = result
    last_failed_line_idx = failed_line_idx
    if not error_msg or failed_line_idx is None:
      break  # Successfully loaded

    if sub := subs_by_line_idx.get(failed_line_idx):
      if 'Unexpected ","' in error_msg:
        # If this was a line we subbed, we got the type wrong. Make it a kvp.
        new_lines[failed_line_idx] = _inject_substitution(
          sub.original_line,
          sub,
          as_kvp=True,
        )
      elif 'Unexpected """' in error_msg:
        # The previous line was probably the last non-commented line in a list and had no trailing comma.
        new_lines[failed_line_idx] = "," + new_lines[failed_line_idx]
  del last_failed_line_idx
  del new_lines

  if error_msg:
    print(f"Failed to load JSON file: {error_msg}", file=sys.stderr)
    return

  if not data:
    print("No data loaded from JSON file.", file=sys.stderr)
    return

  if not isinstance(data, dict):
    print("Top-level JSON data is not an object.", file=sys.stderr)
    return

  data_list = _get_by_path(data, list_path)
  if not isinstance(data_list, list):
    print(f"Data at path '{list_path}' is not a list.", file=sys.stderr)
    return

  _sort_in_place(data_list, key_path)

  if cli.VERBOSE:
    print(f"Sorted {list_path!r} by {key_path!r}:", file=sys.stderr)
    print(json5.dumps(data, indent=indent))

  json_text = _reverse_substitutions(data, subs)

  if cli.VERBOSE:
    print(json_text, file=sys.stdout)

  file_path.write_text(json_text)


if __name__ == "__main__":
  main(
    file_path=Path(sys.argv[1]),
    list_path=sys.argv[2],
    key_path=sys.argv[3],
  )
