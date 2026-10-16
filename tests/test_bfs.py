"""Tests for the BFS path search."""

from src.utils.bfs import bfs
from src.constants import EAST, NORTH, SOUTH, WEST

ALL = NORTH | EAST | SOUTH | WEST


def test_same_cell() -> None:
    """A path from a cell to itself is just that cell."""
    assert bfs([[ALL]], (0, 0), (0, 0)) == [(0, 0)]


def test_straight_corridor() -> None:
    """Walk along an open horizontal corridor."""
    grid = [[NORTH | SOUTH | WEST, NORTH | SOUTH, NORTH | SOUTH | EAST]]
    assert bfs(grid, (0, 0), (2, 0)) == [(0, 0), (1, 0), (2, 0)]


def test_goes_around_wall() -> None:
    """A wall between two cells forces a detour."""
    # 2x2 grid, wall between (0, 0) and (1, 0).
    grid = [
        [NORTH | WEST | EAST, NORTH | EAST | WEST],
        [SOUTH | WEST, SOUTH | EAST],
    ]
    assert bfs(grid, (0, 0), (1, 0)) == [(0, 0), (0, 1), (1, 1), (1, 0)]


def test_unreachable() -> None:
    """Closed cells cannot reach each other."""
    assert bfs([[ALL, ALL]], (0, 0), (1, 0)) == []


def test_out_of_grid() -> None:
    """Cells outside the grid give an empty path."""
    assert bfs([[ALL]], (0, 0), (5, 5)) == []
    assert bfs([[ALL]], (-1, 0), (0, 0)) == []
