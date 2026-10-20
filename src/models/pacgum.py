from src.models.config import Config
from src.utils.maze import Maze


class Pacgum:
    def __init__(self, maze: Maze, config: Config) -> None:
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

        for x in range(cols):
            for y in range(rows):
                if (
                    not maze.is_closed((x, y))
                    and (x, y) not in self.super_pacgum
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
