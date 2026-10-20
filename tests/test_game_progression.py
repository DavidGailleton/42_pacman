"""Tests for winning levels and carrying lives and score over."""

import os

# No real window during tests: must be set before pygame opens one.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.constants import MAX_LEVEL  # noqa: E402
from src.layouts.end_screen import EndScreen  # noqa: E402
from src.layouts.game import Game  # noqa: E402
from src.models.config import Config  # noqa: E402

SCREEN_SIZE = (800, 600)


def make_game() -> Game:
    """Build a game, with pygame ready for the end screen fonts.

    Returns:
        A new game at level 1.
    """
    pygame.init()
    return Game(Config(), SCREEN_SIZE)


def test_time_up_wins_level() -> None:
    """Surviving until the end of the timer goes to the next level."""
    game = make_game()
    game.lives -= 1
    game.score = 120
    game._update(game.config.level_max_time + 1)
    assert game.level == 2
    assert game.lives == game.config.lives - 1
    assert game.score == 120
    assert game.time_left == game.config.level_max_time
    assert not game.game_over


def test_all_pacgums_eaten_wins_level() -> None:
    """Eating the last pacgum goes to the next level."""
    game = make_game()
    game.pacgum.pacgum.clear()
    game.pacgum.super_pacgum = {game.pacman_cell}
    game._eat_pacgum()
    assert game.level == 2
    assert game.score == game.config.point_per_super_pacgum


def test_last_level_wins_game() -> None:
    """Winning the last level shows the victory screen."""
    game = make_game()
    game.level = MAX_LEVEL
    game._next_level()
    screen = game._update(0.0)
    assert isinstance(screen, EndScreen)
    assert screen.win


def test_last_life_lost_loses_game() -> None:
    """Losing the last life shows the game over screen."""
    game = make_game()
    game.lives = 1
    game._lose_life()
    screen = game._update(0.0)
    assert isinstance(screen, EndScreen)
    assert not screen.win
