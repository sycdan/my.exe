from pathlib import Path

from setuptools import find_packages, setup

root = Path(__file__).parent
requirements_file = root / "requirements.txt"
requirements_lines = requirements_file.read_text().splitlines()

setup(
  name="my.exe",
  version=(root / "VERSION").read_text().strip(),
  description="Personal commands.",
  author="Dan Stace",
  author_email="dstace@gmail.com",
  packages=find_packages(),
  install_requires=[x for x in requirements_lines if x and not x.startswith("#")],
  entry_points={"console_scripts": ["my=my.cli.__main__:app", "kb=my.cli.kb:app"]},
  python_requires=">=3.8",
  include_package_data=True,
  classifiers=[
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
  ],
)
