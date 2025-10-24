import hashlib
import os
import tempfile
import zipfile
from zipfile import ZipInfo

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization


def get_raw_fingerprint(pubkey_path):
  with open(pubkey_path, "rb") as f:
    key_data = f.read()
  pubkey = serialization.load_pem_public_key(key_data, backend=default_backend())
  der = pubkey.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
  )
  digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
  digest.update(der)
  return digest.finalize().hex()


def hash_file(path, algo="sha256"):
  h = hashlib.new(algo)
  with open(path, "rb") as f:
    for chunk in iter(lambda: f.read(8192), b""):
      h.update(chunk)
  return h.hexdigest()


def deterministic_zip(zip_path, file_path, arcname=None):
  with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    info = ZipInfo(arcname or file_path)
    info.date_time = (1980, 1, 1, 0, 0, 0)  # Fixed timestamp
    with open(file_path, "rb") as f:
      zf.writestr(info, f.read())


def test_archive_is_deterministic(archiving):
  # Create a temp file to archive, with consistent content
  with tempfile.NamedTemporaryFile(delete=False) as tmp:
    tmp.write(b"some bytes")
    tmp_path = tmp.name

  zip1 = tempfile.NamedTemporaryFile(delete=False).name
  zip2 = tempfile.NamedTemporaryFile(delete=False).name

  deterministic_zip(zip1, tmp_path)
  deterministic_zip(zip2, tmp_path)

  with open(zip1, "rb") as f1, open(zip2, "rb") as f2:
    assert f1.read() == f2.read()

  os.remove(tmp_path)
  os.remove(zip1)
  os.remove(zip2)
