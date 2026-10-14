from mazegenerator import MazeGenerator
from src.models.config import Config

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


class Maze:
    def __init__(self, config: Config) -> None:
        self.config = config
        try:
            self.maze = MazeGenerator(
                size=config.shape,
                seed=config.seed,
                perfect=False
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
