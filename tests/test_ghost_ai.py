"""Tests for the ghosts' chase targets and movement."""

from src.ghost_ai import Blinky, Clyde, Inky, Pinky
from src.utils.maze import EAST, NORTH, SOUTH, WEST, Maze

ALL = NORTH | EAST | SOUTH | WEST


class GridMaze(Maze):
    """A Maze built from a hand-made grid, without the generator."""

    def __init__(self, grid: list[list[int]]) -> None:
        """Store the grid.

        Args:
            grid: Maze grid, indexed as ``grid[y][x]``.
        """
        self.grid = grid

    def get_maze(self) -> list[list[int]]:
        """Return the hand-made grid."""
        return self.grid


def open_maze(size: int = 20) -> GridMaze:
    """Build a square maze with no inner walls."""
    return GridMaze([[0] * size for _ in range(size)])


def test_blinky_targets_pacman() -> None:
    """Blinky aims straight at Pac-Man."""
    blinky = Blinky((19, 0), open_maze())
    assert blinky.chase_target((5, 5), (1, 0)) == (5, 5)


def test_pinky_targets_ahead() -> None:
    """Pinky aims 4 cells in front of Pac-Man."""
    pinky = Pinky((0, 0), open_maze())
    assert pinky.chase_target((5, 5), (0, -1)) == (5, 1)
    assert pinky.chase_target((5, 5), (1, 0)) == (9, 5)


def test_pinky_target_clamped() -> None:
    """Pinky's target stays inside the maze."""
    pinky = Pinky((0, 0), open_maze())
    assert pinky.chase_target((1, 1), (-1, 0)) == (0, 1)


def test_inky_doubles_blinky_vector() -> None:
    """Inky aims at Blinky's vector to the pivot, doubled."""
    maze = open_maze()
    blinky = Blinky((19, 0), maze)
    blinky.position = (4, 4)
    inky = Inky((19, 19), maze, blinky)
    # Pivot = (6, 6) + 2 * (1, 0) = (8, 6); target = 2 * pivot - blinky.
    assert inky.chase_target((6, 6), (1, 0)) == (12, 8)


def test_clyde_shy_when_close() -> None:
    """Clyde goes back to his corner when near Pac-Man."""
    clyde = Clyde((0, 19), open_maze())
    clyde.position = (5, 5)
    assert clyde.chase_target((7, 7), (0, 0)) == (0, 19)


def test_clyde_chases_when_far() -> None:
    """Clyde chases Pac-Man when far away."""
    clyde = Clyde((0, 19), open_maze())
    assert clyde.chase_target((15, 2), (0, 0)) == (15, 2)


def test_next_step_is_neighbour() -> None:
    """The ghost moves one cell towards its target."""
    blinky = Blinky((0, 0), open_maze())
    step = blinky.next_step((0, 5), (0, 0))
    assert step == (0, 1)


def test_next_step_unreachable_stays() -> None:
    """A ghost that cannot reach anything stays in place."""
    blinky = Blinky((0, 0), GridMaze([[ALL, ALL], [ALL, ALL]]))
    assert blinky.next_step((1, 1), (0, 0)) == (0, 0)
