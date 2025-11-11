import os
import subprocess
import sys
import uuid
from pathlib import Path

APP_NAME = "my.py"
APP_SLUG = "my"
APP_GOOID = uuid.UUID("78b8584e-d6eb-4c35-bbc3-ed88996deb64")
APP_CONFIG_DIR = Path(os.path.expanduser(f"~/.config/{APP_SLUG}.{APP_GOOID}"))
REPO_DIR = Path(__file__).parent.parent
CLI_DIR = REPO_DIR / "my" / "cli"
VERBOSE = os.environ.get("VERBOSE", "0") == "1"
IDENTITY = os.environ.get("IDENTITY", "id_rsa")

if VERBOSE:
  print("App config dir:", APP_CONFIG_DIR)
  print("Repo dir:", REPO_DIR)
  print("CLI dir:", CLI_DIR)
  print("Identity:", IDENTITY)

FINGERPRINT = os.environ.get("FINGERPRINT", "")
if not FINGERPRINT:
  key_path = Path(os.path.expanduser(f"~/.ssh/{IDENTITY}"))
  if VERBOSE:
    print("Reading key:", key_path)
  try:
    output = subprocess.run(
      ["ssh-keygen", "-lf", key_path], check=True, capture_output=True, text=True
    ).stdout.strip()
    # Example output: "2048 SHA256:abc123... user@host (RSA)"
    FINGERPRINT = output.split()[1]
  except subprocess.CalledProcessError as e:
    print("ssh-keygen failed:", e.stderr.strip())
  except FileNotFoundError:
    print("ssh-keygen not found in PATH")

if not FINGERPRINT:
  print("Failed to obtain fingerprint.")
  sys.exit(1)

if VERBOSE:
  print("Fingerprint:", FINGERPRINT)

GOOID = uuid.uuid5(APP_GOOID, FINGERPRINT)

if VERBOSE:
  print("My gooid:", GOOID)
