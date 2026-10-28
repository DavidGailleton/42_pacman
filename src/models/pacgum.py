from src.models.config import Config
from src.utils.maze import Maze


class Pacgum:
    def __init__(self, maze: Maze, config: Config) -> None:
        self.maze = maze
        self.points = config.point_per_pacgum
        self.super_point = config.point_per_super_pacgum
        self.super_pacgum = self._place_corner(maze)
        self.pacgum = self._place_pacgum(maze)

    def _place_corner(self, maze: Maze) -> set[tuple[int, int]]:
        w, h = maze.get_shape()
        return {(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)}

    def _place_pacgum(self, maze: Maze) -> set[tuple[int, int]]:
        cols, rows = maze.get_shape()
        pacgum: set[tuple[int, int]] = set()
        center_pos = self._find_start_cell()

        for x in range(cols):
            for y in range(rows):
                if (
                    not maze.is_closed((x, y))
                    and (x, y) not in self.super_pacgum
                    and (x, y) != center_pos
                ):
                    pacgum.add((x, y))
        return pacgum

    def eat(self, cell: tuple[int, int]) -> tuple[bool, int]:
        if cell in self.pacgum:
            self.pacgum.remove(cell)
            return (False, self.points)
        if cell in self.super_pacgum:
            self.super_pacgum.remove(cell)
            return (True, self.super_point)
        return (False, 0)

    def is_empty(self) -> bool:
        return not self.super_pacgum and not self.pacgum

    def get_pacgum(self) -> set[tuple[int, int]]:
        return self.pacgum

    def get_super_pacgum(self) -> set[tuple[int, int]]:
        return self.super_pacgum

    def _find_start_cell(self) -> tuple[int, int]:
        """Find the cell closest to the maze center that can be entered.

        The center may be a closed cell (four walls, e.g. in the "42"
        pattern). Cells are sorted by Manhattan distance to the center
        and the first one that is not closed is used.

        Returns:
            The start cell (x, y), or (0, 0) if every cell is closed.
        """
        width, height = self.maze.get_shape()
        center_x, center_y = width // 2, height // 2
        cells = [(x, y) for y in range(height) for x in range(width)]
        cells.sort(
            key=lambda cell: abs(cell[0] - center_x) + abs(cell[1] - center_y)
        )
        for cell in cells:
            if not self.maze.is_closed(cell):
                return cell
        return (0, 0)
