"""Persistent highscore storage (top 10, saved as JSON)."""

import json

from src.models.config import Config

MAX_SCORES: int = 10
MAX_NAME_LENGTH: int = 10

# One highscore entry: (player name, score).
Score = tuple[str, int]


def _is_valid_name(name: object) -> bool:
    """Check that a name is a non-empty string of at most 10 characters.

    Args:
        name: Value to check.

    Returns:
        True if the name only contains letters, digits and spaces.
    """
    return (
        isinstance(name, str)
        and 0 < len(name) <= MAX_NAME_LENGTH
        and all(char.isalnum() or char == " " for char in name)
    )


def _is_valid_score(score: object) -> bool:
    """Check that a score is a non-negative integer.

    Args:
        score: Value to check.

    Returns:
        True if the score is an int (not a bool) greater or equal to 0.
    """
    return (
        isinstance(score, int) and not isinstance(score, bool) and score >= 0
    )


class ScoreException(Exception):
    """Raised when a highscore entry has an invalid name or score.

    The caller (e.g. the name-entry screen) must catch it, since an
    uncaught exception would stop the game.
    """


def get_scores(config: Config) -> list[Score]:
    """Load the highscores from the file named in the config.

    A missing or corrupt file gives an empty list. Invalid entries are
    skipped, so one bad line does not lose the whole table.

    Args:
        config: Game configuration holding ``highscore_filename``.

    Returns:
        At most 10 scores, sorted from best to worst.
    """
    try:
        with open(config.highscore_filename, "r") as file:
            data: object = json.load(file)
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as error:
        print(f"Warning: cannot read highscores ({error}), ignoring file")
        return []

    if not isinstance(data, list):
        print("Warning: highscore file must contain a list, ignoring file")
        return []

    scores: list[Score] = []
    for entry in data:
        if (
            isinstance(entry, dict)
            and _is_valid_name(entry.get("name"))
            and _is_valid_score(entry.get("score"))
        ):
            scores.append((entry["name"], entry["score"]))

    scores.sort(key=lambda item: item[1], reverse=True)
    return scores[:MAX_SCORES]


def add_score(config: Config, name: str, score: int) -> None:
    """Insert a score in the highscore file, keeping only the 10 best.

    The file is created if it does not exist. On equal scores, older
    entries stay ahead of the new one.

    Args:
        config: Game configuration holding ``highscore_filename``.
        name: Player name (letters, digits and spaces, max 10 chars).
        score: Final score, must be a non-negative integer.
    """
    if not _is_valid_name(name) or not _is_valid_score(score):
        raise ScoreException(
            f"Warning: invalid highscore ({name!r}, {score!r}), skipped"
        )

    scores: list[Score] = get_scores(config)
    scores.append((name, score))
    scores.sort(key=lambda item: item[1], reverse=True)
    scores = scores[:MAX_SCORES]

    data: list[dict[str, str | int]] = [
        {"name": entry_name, "score": entry_score}
        for entry_name, entry_score in scores
    ]
    try:
        with open(config.highscore_filename, "w") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        print(f"Warning: cannot save highscores ({error})")
