import tempfile
from pathlib import Path

import json5
import pytest

LAUNCH_JSON = """
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Zap the thing",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "console": "integratedTerminal",
      "args": [
        "-v",
        // "--debug",
        "zap",
        "${workspaceFolder}/thing",
        // "other"
      ]
    },
    {
      "name": "Attach Debugger",
      "type": "debugpy",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      // "justMyCode": true,
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/code"
        }
      ]
    },
    {
      "name": "Do stuff",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/do.py",
      "django": true,
      "justMyCode": false,
      "args": [
        "stuff",
        // "--skip-checks", // prevents examining all models on startup
        "--random",
        // "--withlogs",
        "--processes=1",
        // -------------------- things
        "Thing1"
        // "Thing2",
        // -------------------- thangs
        // "ThangA",
        // "ThangB",
      ],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    },
    {
      "name": "Parse stuff",
      "type": "debugpy",
      "request": "launch",
      "module": "parse",
      "args": [
        "${workspaceFolder}/stuff.txt",
        // "-k other_stuff",
      ],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src",
        // "COMMENTED_ENV_VAR": "foo"
      },
      "justMyCode": true
    },
  ]
}
""".strip()


def test_launch_json_structure():
  data = json5.loads(LAUNCH_JSON)
  assert isinstance(data, dict)
  assert data.get("version") == "0.2.0"
  configurations = data.get("configurations")
  assert isinstance(configurations, list)
  assert len(configurations) > 1
  assert configurations[0].get("name") == "Zap the thing"
  assert configurations[-1].get("name") == "Parse stuff"


@pytest.fixture
def fake_launch_json_file_path():
  with tempfile.TemporaryDirectory() as tmp_dir_name:
    file_path = Path(tmp_dir_name) / "launch.json"
    file_path.write_text(LAUNCH_JSON)
    yield file_path


def test_sort_launch_json(fake_launch_json_file_path: Path):
  from my import cli
  from my.cli.json.sort_file import main

  cli.VERBOSE = True

  main(fake_launch_json_file_path, "configurations", "name")

  text = fake_launch_json_file_path.read_text()
  lines = text.splitlines()
  data = json5.loads(text)
  assert isinstance(data, dict)
  assert data["configurations"][0]["name"] == "Attach Debugger"
  assert data["configurations"][-1]["name"] == "Zap the thing"
  assert '// "justMyCode": true,' in lines[11]
