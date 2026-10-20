"""Tests for the ghosts' chase targets and movement."""

from src.ghost_ai import Blinky, Clyde, GhostState, Inky, Pinky
from src.constants import (
    DOWN,
    EAST,
    GHOST_FRAMES_PER_CELL,
    LEFT,
    NORTH,
    RIGHT,
    SOUTH,
    WEST,
)
from src.models.config import Config
from src.utils.maze import Maze

ALL = NORTH | EAST | SOUTH | WEST
CONFIG = Config()


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
    blinky = Blinky((19, 0), open_maze(), CONFIG)
    assert blinky.chase_target((5, 5), (1, 0)) == (5, 5)


def test_pinky_targets_ahead() -> None:
    """Pinky aims 4 cells in front of Pac-Man."""
    pinky = Pinky((0, 0), open_maze(), CONFIG)
    assert pinky.chase_target((5, 5), (0, -1)) == (5, 1)
    assert pinky.chase_target((5, 5), (1, 0)) == (9, 5)


def test_pinky_target_clamped() -> None:
    """Pinky's target stays inside the maze."""
    pinky = Pinky((0, 0), open_maze(), CONFIG)
    assert pinky.chase_target((1, 1), (-1, 0)) == (0, 1)


def test_inky_doubles_blinky_vector() -> None:
    """Inky aims at Blinky's vector to the pivot, doubled."""
    maze = open_maze()
    blinky = Blinky((19, 0), maze, CONFIG)
    blinky.position = (4, 4)
    inky = Inky((19, 19), maze, blinky, CONFIG)
    # Pivot = (6, 6) + 2 * (1, 0) = (8, 6); target = 2 * pivot - blinky.
    assert inky.chase_target((6, 6), (1, 0)) == (12, 8)


def test_clyde_shy_when_close() -> None:
    """Clyde goes back to his corner when near Pac-Man."""
    clyde = Clyde((0, 19), open_maze(), CONFIG)
    clyde.position = (5, 5)
    assert clyde.chase_target((7, 7), (0, 0)) == (0, 19)


def test_clyde_chases_when_far() -> None:
    """Clyde chases Pac-Man when far away."""
    clyde = Clyde((0, 19), open_maze(), CONFIG)
    assert clyde.chase_target((15, 2), (0, 0)) == (15, 2)


def test_next_step_is_neighbour() -> None:
    """The ghost moves one cell towards its target."""
    blinky = Blinky((0, 0), open_maze(), CONFIG)
    step = blinky.next_step((0, 5), (0, 0))
    assert step == (0, 1)


def test_next_step_unreachable_stays() -> None:
    """A ghost that cannot reach anything stays in place."""
    blinky = Blinky((0, 0), GridMaze([[ALL, ALL], [ALL, ALL]]), CONFIG)
    assert blinky.next_step((1, 1), (0, 0)) == (0, 0)


def test_no_u_turn_when_target_behind() -> None:
    """In the open, a ghost does not turn back toward its target."""
    blinky = Blinky((0, 0), open_maze(), CONFIG)
    blinky.position = (5, 5)
    blinky.direction = RIGHT
    assert blinky._choose_direction((2, 5), (0, 0)) != LEFT


def test_dead_end_turns_back() -> None:
    """In a dead end, going back is the only way and is taken."""
    # Corridor (0, 0) - (1, 0), the right cell is a dead end.
    grid = [[NORTH | WEST | SOUTH, NORTH | EAST | SOUTH]]
    blinky = Blinky((0, 0), GridMaze(grid), CONFIG)
    blinky.position = (1, 0)
    blinky.direction = RIGHT
    assert blinky._choose_direction((0, 0), (0, 0)) == LEFT


def test_single_exit_is_taken() -> None:
    """In a bend, the only exit is taken whatever the target."""
    # (1, 0) -> (0, 0) -> (0, 1): (0, 0) opens east and south only.
    grid = [
        [NORTH | WEST, NORTH | EAST | SOUTH],
        [WEST | EAST | SOUTH, ALL],
    ]
    blinky = Blinky((1, 1), GridMaze(grid), CONFIG)
    blinky.position = (0, 0)
    blinky.direction = LEFT
    # Pac-Man is behind, but the bend only allows going down.
    assert blinky._choose_direction((1, 0), (0, 0)) == DOWN


def test_corner_turn_when_frightened() -> None:
    """A frightened ghost turns toward the inside in its corner."""
    maze = open_maze()
    pinky = Pinky((19, 0), maze, CONFIG)
    pinky.state = GhostState.FRIGHTENED
    pinky.direction = RIGHT
    assert pinky._choose_direction((5, 5), (0, 0)) == DOWN
    clyde = Clyde((0, 19), maze, CONFIG)
    clyde.state = GhostState.FRIGHTENED
    clyde.direction = DOWN
    assert clyde._choose_direction((5, 5), (0, 0)) == RIGHT


def test_move_one_cell_in_frames() -> None:
    """A ghost reaches the next cell after GHOST_FRAMES_PER_CELL."""
    blinky = Blinky((0, 0), open_maze(), CONFIG)
    for _ in range(GHOST_FRAMES_PER_CELL // 2):
        blinky.move((0, 10), (0, 0))
    assert blinky.float_position() == (0.0, 0.5)
    for _ in range(GHOST_FRAMES_PER_CELL // 2):
        blinky.move((0, 10), (0, 0))
    assert blinky.position == (0, 1)
    assert blinky.step == 0


def test_false_wall_keeps_maze_intact() -> None:
    """The false wall is only added to a copy of the grid."""
    maze = open_maze()
    blinky = Blinky((0, 0), maze, CONFIG)
    blinky.position = (5, 5)
    blinky.direction = RIGHT
    grid = blinky._grid_with_wall_behind()
    assert grid[5][5] & WEST
    assert maze.get_maze()[5][5] == 0
