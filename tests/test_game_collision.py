"""Tests for what happens when Pac-Man touches a ghost."""

import os

# No real window during tests: must be set before pygame opens one.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from src.constants import EAT_FREEZE_TIME  # noqa: E402
from src.game import Game  # noqa: E402
from src.ghost_ai import Ghost, GhostState  # noqa: E402
from src.models.config import Config  # noqa: E402


def make_game_with_ghost_on_pacman(state: GhostState) -> tuple[Game, Ghost]:
    """Build a game and put its first ghost on Pac-Man.

    Args:
        state: State given to the ghost.

    Returns:
        The game and the ghost touching Pac-Man.
    """
    game = Game(Config())
    ghost = game.ghosts[0]
    ghost.position = game.pacman_cell
    ghost.direction = None
    ghost.step = 0
    ghost.state = state
    return game, ghost


def test_chasing_ghost_ends_game() -> None:
    """A chasing ghost stops the game: nothing moves afterwards."""
    game, ghost = make_game_with_ghost_on_pacman(GhostState.CHASE)
    game._handle_collisions()
    assert game.game_over
    other = game.ghosts[1]
    before = (other.position, other.step)
    game._update(0.1)
    assert (other.position, other.step) == before


def test_frightened_ghost_is_eaten_after_freeze() -> None:
    """A frightened ghost freezes the game, then goes to its corner."""
    game, ghost = make_game_with_ghost_on_pacman(GhostState.FRIGHTENED)
    game._handle_collisions()
    assert not game.game_over
    assert game.freeze_timer == EAT_FREEZE_TIME
    game._update(EAT_FREEZE_TIME / 2)
    assert ghost.state is GhostState.FRIGHTENED
    assert ghost.position == game.pacman_cell
    game._update(EAT_FREEZE_TIME / 2)
    assert ghost.state is GhostState.EATEN
    assert ghost.position == ghost.corner
    assert game.eaten_ghost is None


def test_eaten_ghost_is_ignored() -> None:
    """An eaten ghost on Pac-Man changes nothing."""
    game, ghost = make_game_with_ghost_on_pacman(GhostState.EATEN)
    game._handle_collisions()
    assert not game.game_over
    assert game.freeze_timer == 0.0
