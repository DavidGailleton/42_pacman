"""Tests for winning levels and carrying lives and score over."""

import os

# No real window during tests: must be set before pygame opens one.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.layouts.end_screen import EndScreen  # noqa: E402
from src.layouts.game import Game  # noqa: E402
from src.models.config import Config, LevelConfig  # noqa: E402
from src.utils.maze import Maze  # noqa: E402

SCREEN_SIZE = (800, 600)


def make_game(config: Config | None = None) -> Game:
    """Build a game, with pygame ready for the end screen fonts.

    Args:
        config: Configuration to use, the default one if None.

    Returns:
        A new game at level 1.
    """
    pygame.init()
    return Game(config or Config(), SCREEN_SIZE)


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
    game.level = len(game.config.levels)
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


def test_next_level_uses_its_size_and_seed() -> None:
    """Level 2 uses the second size of the list and the seed plus 1."""
    config = Config(
        levels=[
            LevelConfig(width=10, height=10),
            LevelConfig(width=14, height=12),
        ]
    )
    game = make_game(config)
    game._next_level()
    assert game.maze.get_shape() == (14, 12)
    expected = Maze((14, 12), config.seed + 1).get_maze()
    assert game.maze.get_maze() == expected


def test_level_count_comes_from_config() -> None:
    """With two levels in the config, winning level 2 wins the game."""
    config = Config(
        levels=[
            LevelConfig(width=10, height=10),
            LevelConfig(width=10, height=10),
        ]
    )
    game = make_game(config)
    game._next_level()
    assert not game.won
    game._next_level()
    assert game.won
