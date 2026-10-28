from src.models.config import Config
from src.utils.maze import Maze


class Pacgum:
    """Pacgums and super-pacgums left in the current maze.

    Super-pacgums are in the 4 corners. Pacgums are in every other open
    cell, except Pac-Man's start cell.
    """
    def __init__(self, maze: Maze, config: Config) -> None:
        """Place the pacgums and super-pacgums in the maze.

        Args:
            maze: Maze of the current level.
            config: Game configuration, giving the points of each pacgum.
        """
        self.maze = maze
        self.points = config.point_per_pacgum
        self.super_point = config.point_per_super_pacgum
        self.super_pacgum = self._place_corner(maze)
        self.pacgum = self._place_pacgum(maze)

    def _place_corner(self, maze: Maze) -> set[tuple[int, int]]:
        """Place the super-pacgums in the 4 corners of the maze.

        Args:
            maze: Maze of the current level.

        Returns:
            The 4 corner cells (x, y).
        """
        w, h = maze.get_shape()
        return {(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)}

    def _place_pacgum(self, maze: Maze) -> set[tuple[int, int]]:
        """Place a pacgum in every open cell.

        Closed cells, corners and Pac-Man's start cell are skipped.

        Args:
            maze: Maze of the current level.

        Returns:
            The cells (x, y) holding a pacgum.
        """
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
        """Eat the pacgum or super-pacgum on a cell, if any.

        Args:
            cell: Cell (x, y) where Pac-Man is.

        Returns:
            (True if it was a super-pacgum, points won).
        """
        if cell in self.pacgum:
            self.pacgum.remove(cell)
            return (False, self.points)
        if cell in self.super_pacgum:
            self.super_pacgum.remove(cell)
            return (True, self.super_point)
        return (False, 0)

    def is_empty(self) -> bool:
        """Tell if every pacgum and super-pacgum has been eaten.

        Returns:
            True if nothing is left to eat.
        """
        return not self.super_pacgum and not self.pacgum

    def get_pacgum(self) -> set[tuple[int, int]]:
        """Return the cells that still hold a pacgum.

        Returns:
            The pacgum cells (x, y).
        """
        return self.pacgum

    def get_super_pacgum(self) -> set[tuple[int, int]]:
        """Return the cells that still hold a super-pacgum.

        Returns:
            The super-pacgum cells (x, y).
        """
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
