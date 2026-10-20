"""Tests for the configuration comment stripping and validation."""

import json

import pytest

from src.config_loader import strip_comments
from src.models.config import DEFAULT_LEVELS, Config


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


def test_levels_are_parsed() -> None:
    """Each entry of 'levels' gives the size of one level, in order."""
    config = Config.model_validate(
        {"levels": [{"width": 12, "height": 10}, {"width": 10, "height": 20}]}
    )
    sizes = [(level.width, level.height) for level in config.levels]
    assert sizes == [(12, 10), (10, 20)]


@pytest.mark.parametrize(
    "levels",
    [
        [],
        "not a list",
        [{"width": 12}],
        [{"width": "12", "height": 12}],
        [{"width": 5, "height": 12}],
        [{"width": 12, "height": 12}, {"width": 12, "height": 500}],
    ],
)
def test_invalid_levels_use_default(
    levels: object, capsys: pytest.CaptureFixture[str]
) -> None:
    """An empty or faulty 'levels' list is reported and replaced."""
    config = Config.model_validate({"levels": levels})
    assert config.levels == DEFAULT_LEVELS
    assert "invalid value" in capsys.readouterr().out
