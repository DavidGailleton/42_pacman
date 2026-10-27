# 42-python-project

42 Python project template using:

- Python 3.10+
- uv
- pytest
- flake8
- mypy

## Setup

```bash
make install

## Packaging

The game is packaged as a standalone Linux executable with
[PyInstaller](https://pyinstaller.org). The build spec is `pac-man.spec`.

```bash
make package
```

This creates `release/pac-man-linux.tar.gz`, which contains:

- `pac-man`: the executable (Python is not needed to run it)
- `config.json`: the configuration file, which you can edit
- `run.sh`: a launcher that runs `./pac-man config.json`
- `INSTRUCTIONS.txt`: how to play

Only a Linux build is provided, because PyInstaller can't cross-compile.

## Project Management

Project management documents are in [`project_management/`](project_management/):

- [Acceptance test plan](project_management/acceptance_test_plan.md):
  every test to run before and during the defense, with ready-made
  config and highscore files in
  [`project_management/test_configs/`](project_management/test_configs/).
