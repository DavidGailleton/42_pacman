"""Helpers to read the JSON-with-comments configuration file."""

import json
from typing import Any

from src.models.config import Config


class ConfigError(Exception):
    """Raised when the config file cannot be read or decoded.

    The message is meant to be shown as is to the user.
    """


def strip_comments(text: str) -> str:
    """Remove comment lines from a JSON-with-comments text.

    A comment is any line whose first non-blank character is ``#``.
    Comment lines are replaced by empty lines instead of being removed,
    so the line numbers in ``json.JSONDecodeError`` messages still match
    the original file.

    Args:
        text: Raw content of the configuration file.

    Returns:
        The same text with every comment line emptied.
    """
    lines: list[str] = text.splitlines()
    kept: list[str] = [
        "" if line.lstrip().startswith("#") else line for line in lines
    ]
    return "\n".join(kept)


def load_config(path: str) -> Config:
    """Read, decode and validate the configuration file.

    Invalid values inside a valid file are not errors: ``Config``
    replaces them with defaults. Only problems that prevent reading the
    file at all are reported as ``ConfigError``.

    Args:
        path: Path of the JSON-with-comments configuration file.

    Returns:
        The validated configuration.

    Raises:
        ConfigError: If the file is missing, unreadable, not UTF-8 text
            or not valid JSON. The message explains the problem.
    """
    try:
        with open(path, encoding="utf-8") as file:
            text: str = file.read()
    except FileNotFoundError:
        raise ConfigError(f"config file '{path}' not found")
    except IsADirectoryError:
        raise ConfigError(f"'{path}' is a directory, not a config file")
    except PermissionError:
        raise ConfigError(f"permission denied when reading '{path}'")
    except UnicodeDecodeError:
        raise ConfigError(f"'{path}' is not a UTF-8 text file")
    except OSError as error:
        raise ConfigError(f"cannot read '{path}': {error.strerror}")

    try:
        data: Any = json.loads(strip_comments(text))
    except json.JSONDecodeError as error:
        raise ConfigError(
            f"'{path}' is not valid JSON: {error.msg} "
            f"(line {error.lineno}, column {error.colno})"
        )

    return Config.model_validate(data)
