"""Tests for the configuration comment stripping."""

import json

from src.config_loader import strip_comments


def test_comment_lines_are_ignored() -> None:
    """Lines starting with '#' are dropped, even when indented."""
    text = '# header\n{\n    # lives\n    "lives": 3\n}'
    assert json.loads(strip_comments(text)) == {"lives": 3}


def test_hash_inside_value_is_kept() -> None:
    """A '#' that is not at the start of a line is regular content."""
    text = '{"name": "a#b"}'
    assert json.loads(strip_comments(text)) == {"name": "a#b"}


def test_line_numbers_are_preserved() -> None:
    """Comment lines become empty so error line numbers stay correct."""
    text = "# one\n# two\n{oops}"
    try:
        json.loads(strip_comments(text))
    except json.JSONDecodeError as error:
        assert error.lineno == 3
    else:
        raise AssertionError("invalid JSON was accepted")
