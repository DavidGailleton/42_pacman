"""Tests for the Maze wrapper around the A-Maze-ing generator."""

from pathlib import Path

import pytest

from src.config_loader import load_config
from src.models.config import Config
from src.utils.maze import EAST, NORTH, SOUTH, WEST, Maze

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


@pytest.fixture
def config() -> Config:
    """Load the project's original configuration file."""
    return load_config(str(CONFIG_PATH))


@pytest.fixture
def maze(config: Config) -> Maze:
    """Build a maze from the original configuration."""
    return Maze(config)


def all_cells(maze: Maze) -> list[tuple[int, int]]:
    """Return every (x, y) coordinate of the maze."""
    width, height = maze.get_shape()
    return [(x, y) for y in range(height) for x in range(width)]


def test_shape_matches_config(maze: Maze, config: Config) -> None:
    """The grid has `height` rows of `width` cells, as set in the config."""
    width, height = config.shape
    grid = maze.get_maze()
    assert maze.get_shape() == config.shape
    assert len(grid) == height
    assert all(len(row) == width for row in grid)


def test_wall_methods_match_bits(maze: Maze) -> None:
    """Each is_*_wall method reads its own bit (N=1, E=2, S=4, W=8)."""
    grid = maze.get_maze()
    for x, y in all_cells(maze):
        value = grid[y][x]
        assert maze.is_north_wall((x, y)) == bool(value & NORTH)
        assert maze.is_east_wall((x, y)) == bool(value & EAST)
        assert maze.is_south_wall((x, y)) == bool(value & SOUTH)
        assert maze.is_west_wall((x, y)) == bool(value & WEST)


def test_top_left_corner(maze: Maze) -> None:
    """The top-left cell is closed on the north and west sides."""
    assert maze.is_north_wall((0, 0))
    assert maze.is_west_wall((0, 0))


def test_outer_border_is_closed(maze: Maze) -> None:
    """The maze is fully surrounded by walls."""
    width, height = maze.get_shape()
    for x in range(width):
        assert maze.is_north_wall((x, 0))
        assert maze.is_south_wall((x, height - 1))
    for y in range(height):
        assert maze.is_west_wall((0, y))
        assert maze.is_east_wall((width - 1, y))


def test_neighbour_walls_are_consistent(maze: Maze) -> None:
    """A wall between two cells is seen from both sides."""
    width, height = maze.get_shape()
    for x, y in all_cells(maze):
        if x + 1 < width:
            assert maze.is_east_wall((x, y)) == maze.is_west_wall((x + 1, y))
        if y + 1 < height:
            assert maze.is_south_wall((x, y)) == maze.is_north_wall(
                (x, y + 1)
            )


def test_no_avoidable_dead_ends(maze: Maze) -> None:
    """With perfect=False, the generator removes every dead end it can.

    A cell with 3 walls is only allowed when none of them can be opened:
    each one is either the outer border or touches the closed '42'
    pattern (cells with value 15), which the generator never carves.
    """
    width, height = maze.get_shape()
    grid = maze.get_maze()
    sides = [
        (maze.is_north_wall, 0, -1),
        (maze.is_east_wall, 1, 0),
        (maze.is_south_wall, 0, 1),
        (maze.is_west_wall, -1, 0),
    ]
    for x, y in all_cells(maze):
        if grid[y][x] == 15:
            continue
        closed = [(dx, dy) for is_wall, dx, dy in sides if is_wall((x, y))]
        if len(closed) < 3:
            continue
        for dx, dy in closed:
            nx, ny = x + dx, y + dy
            on_border = not (0 <= nx < width and 0 <= ny < height)
            assert on_border or grid[ny][nx] == 15, (
                f"avoidable dead end at {(x, y)}"
            )


def test_same_seed_gives_same_maze(config: Config) -> None:
    """The fixed seed of the first level always gives the same maze."""
    assert Maze(config).get_maze() == Maze(config).get_maze()
