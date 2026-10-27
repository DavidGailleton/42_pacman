"""Run every fixture of the acceptance test plan through the loaders.

The files live in ``project_management/test_configs/``. Each test checks
the behaviour written in ``project_management/acceptance_test_plan.md``.
"""

import sys
from pathlib import Path

import pytest

from src.__main__ import main
from src.config_loader import ConfigError, load_config
from src.models.config import DEFAULT_LEVELS, Config
from src.score_management import Score, get_scores
from src.utils.maze import Maze

TEST_CONFIGS: Path = Path(__file__).parent.parent / "tests" / "test_configs"

# Written by the manual highscore tests, not a fixture.
GENERATED_FILES: set[str] = {"test_highscores.json"}

INVALID_JSON_FILES: list[str] = ["invalid_json.json", "empty.json"]

# (file, text of the warning, number of warnings)
FAULTY_FILES: list[tuple[str, str, int]] = [
    ("not_object.json", "config root must be a JSON object", 1),
    ("wrong_types.json", "invalid value", 8),
    ("out_of_range.json", "invalid value", 7),
    ("empty_levels.json", "missing key", 7),
]

VALID_FILES: list[str] = [
    "comments.json",
    "unknown_keys.json",
    "highscore_test.json",
]

FULL_RUN_FILE: str = "full_run.json"

# (file, expected scores, text of the warning or "" for none)
HIGHSCORE_FILES: list[tuple[str, list[Score], str]] = [
    ("bad_highscores_broken.json", [], "cannot read highscores"),
    ("bad_highscores_not_list.json", [], "must contain a list"),
    (
        "bad_highscores_entries.json",
        [("VALID ONE", 900), ("VALID TWO", 300)],
        "",
    ),
    (
        "bad_highscores_too_many.json",
        [(f"PLAYER {i}", i * 100) for i in range(15, 5, -1)],
        "",
    ),
]


@pytest.mark.parametrize("name", INVALID_JSON_FILES)
def test_unreadable_config_raises(name: str) -> None:
    """A file that is not valid JSON gives a clear ConfigError."""
    with pytest.raises(ConfigError, match="is not valid JSON"):
        load_config(str(TEST_CONFIGS / name))


@pytest.mark.parametrize(
    "path",
    [str(TEST_CONFIGS / name) for name in INVALID_JSON_FILES]
    + [str(TEST_CONFIGS), str(TEST_CONFIGS / "missing.json")],
)
def test_unreadable_config_exits_cleanly(
    path: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The launcher prints one error line and returns 1, no traceback."""
    monkeypatch.setattr(sys, "argv", ["pac-man.py", path])
    assert main() == 1
    output: str = capsys.readouterr().out
    assert output.startswith("Error:")
    assert "Traceback" not in output


@pytest.mark.parametrize("name, warning, count", FAULTY_FILES)
def test_faulty_config_falls_back(
    name: str, warning: str, count: int, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every faulty value is reported and replaced by its default."""
    config: Config = load_config(str(TEST_CONFIGS / name))
    output: str = capsys.readouterr().out
    assert output.count(warning) == count
    assert config.levels == DEFAULT_LEVELS
    assert config.lives == 3
    assert config.point_per_pacgum == 10
    assert config.highscore_filename == "highscores.json"


@pytest.mark.parametrize("name", VALID_FILES)
def test_valid_config_loads_silently(
    name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Comments and unknown keys are ignored without any message."""
    config: Config = load_config(str(TEST_CONFIGS / name))
    assert capsys.readouterr().out == ""
    assert config.lives == 3
    assert [(level.width, level.height) for level in config.levels] == [
        (15, 15)
    ]


def test_full_run_config() -> None:
    """The playthrough config has 10 levels that can all be generated."""
    config: Config = load_config(str(TEST_CONFIGS / FULL_RUN_FILE))
    assert len(config.levels) == 10
    assert config.level_max_time == 10
    for number, level in enumerate(config.levels, start=1):
        assert (level.width, level.height) == (15, 15)
        Maze((level.width, level.height), config.seed + number - 1)


@pytest.mark.parametrize("name, expected, warning", HIGHSCORE_FILES)
def test_bad_highscores_are_filtered(
    name: str,
    expected: list[Score],
    warning: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A corrupt file or bad entries never stop the highscore loading."""
    config = Config(highscore_filename=str(TEST_CONFIGS / name))
    capsys.readouterr()  # drop the config's missing-key warnings
    assert get_scores(config) == expected
    output: str = capsys.readouterr().out
    if warning:
        assert warning in output
    else:
        assert output == ""


def test_every_fixture_is_covered() -> None:
    """Each file of test_configs/ is used by one of the tests above."""
    tested: set[str] = (
        set(INVALID_JSON_FILES)
        | {name for name, _, _ in FAULTY_FILES}
        | set(VALID_FILES)
        | {FULL_RUN_FILE}
        | {name for name, _, _ in HIGHSCORE_FILES}
    )
    found: set[str] = {
        path.name for path in TEST_CONFIGS.glob("*.json")
    } - GENERATED_FILES
    assert found == tested
