from mazegenerator import MazeGenerator
from src.constants import (
    DOWN,
    EAST,
    LEFT,
    NORTH,
    RIGHT,
    SOUTH,
    UP,
    WEST,
    Direction,
)
from src.models.config import Config

# Wall that blocks each move.
DIRECTION_TO_WALL: dict[Direction, int] = {
    UP: NORTH,
    RIGHT: EAST,
    DOWN: SOUTH,
    LEFT: WEST,
}

# A cell with all four walls, e.g. a cell of the "42" pattern.
ALL_WALLS: int = NORTH | EAST | SOUTH | WEST


class Maze:
    def __init__(self, config: Config) -> None:
        self.config = config
        try:
            self.maze = MazeGenerator(
                size=config.shape, seed=config.seed, perfect=False
            )
        except Exception as error:
            raise RuntimeError(f"Maze Generation Failed: {error}") from error

    def get_shape(self) -> tuple[int, int]:
        return self.config.shape

    def get_maze(self) -> list[list[int]]:
        grid: list[list[int]] = self.maze.maze
        return grid

    def _has_wall(self, coord: tuple[int, int], wall: int) -> bool:
        x, y = coord
        return bool(self.get_maze()[y][x] & wall)

    def is_north_wall(self, coord: tuple[int, int]) -> bool:
        return self._has_wall(coord, NORTH)

    def is_east_wall(self, coord: tuple[int, int]) -> bool:
        return self._has_wall(coord, EAST)

    def is_south_wall(self, coord: tuple[int, int]) -> bool:
        return self._has_wall(coord, SOUTH)

    def is_west_wall(self, coord: tuple[int, int]) -> bool:
        return self._has_wall(coord, WEST)

    def can_move(self, coord: tuple[int, int], direction: Direction) -> bool:
        """Tell if there is no wall in a direction from a cell.

        Args:
            coord: Cell (x, y) to move from.
            direction: Move to check, as (dx, dy).

        Returns:
            True if no wall blocks the move.
        """
        return not self._has_wall(coord, DIRECTION_TO_WALL[direction])

    def is_closed(self, coord: tuple[int, int]) -> bool:
        """Tell if a cell has its four walls (nothing can enter it).

        Args:
            coord: Cell (x, y) to check.

        Returns:
            True if the cell has all four walls.
        """
        x, y = coord
        return self.get_maze()[y][x] & ALL_WALLS == ALL_WALLS
