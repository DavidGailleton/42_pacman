"""Draw the maze walls."""

from src.constants import BLACK_COLOR, MAZE_COLOR, Color
from src.renderer.draw_utils import compute_layout, fill_circle, fill_rect
from src.utils.maze import Maze
import pygame


class MazeRenderer:
    """Draw the maze walls, pre-rendered once on a surface."""

    def __init__(self, maze: Maze, screen_size: tuple[int, int]) -> None:
        """Build the maze surface.

        Args:
            maze: Maze to draw.
            screen_size: Screen size in pixels, as (width, height).
        """
        self.screen_size = screen_size
        self.set_maze(maze)

    def set_maze(self, maze: Maze) -> None:
        """Change the maze and rebuild its surface.

        Args:
            maze: New maze to draw.
        """
        self.maze = maze
        self.cell_size, self.offset = compute_layout(maze.get_shape(),
                                                     self.screen_size)
        self.surface = self._build_surface()

    def draw(self, screen: pygame.Surface) -> None:
        """Blit the pre-rendered maze on the screen.

        Args:
            screen: Surface to draw on.
        """
        screen.blit(self.surface, (0, 0))

    def _build_surface(self) -> pygame.Surface:
        """Draw every wall on a new surface the size of the screen.

        Returns:
            The surface with the maze drawn on it.
        """
        screen = pygame.Surface(self.screen_size)
        screen.fill(BLACK_COLOR)
        first_thickness = self.cell_size // 3
        second_thickness = first_thickness - 6
        segments = self._get_segments()
        for segment in segments:
            half = first_thickness // 2
            self._draw_wall(screen, segment, first_thickness,
                            half, MAZE_COLOR)
        for segment in segments:
            half = second_thickness // 2
            self._draw_wall(screen, segment, second_thickness,
                            half, BLACK_COLOR)
        return screen

    def _draw_wall(self, screen: pygame.Surface,
                   segment: tuple[tuple[int, int], tuple[int, int]],
                   thickness: int, half: int, color: Color
                   ) -> None:
        """Draw one wall segment with rounded ends.

        Args:
            screen: Surface to draw on.
            segment: Start and end points of the wall, in pixels.
            thickness: Wall thickness, in pixels.
            half: Radius of the rounded ends, in pixels.
            color: Wall color.
        """
        (x1, y1), (x2, y2) = segment
        if y1 == y2:
            fill_rect(screen, (x1, y1 - half), (x2 - x1, thickness), color)
        else:
            fill_rect(screen, (x1 - half, y1), (thickness, y2 - y1), color)
        fill_circle(screen, half, (x1, y1), color)
        fill_circle(screen, half, (x2, y2), color)

    def _get_segments(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """List the wall segments of the maze, in pixels.

        Each wall shared by two cells is listed once: a cell gives its
        north and west walls, plus its east / south walls on the border.

        Returns:
            The segments, as (start point, end point).
        """
        start_x, start_y = self.offset
        cols, rows = self.maze.get_shape()
        size_c = self.cell_size
        segments: list[tuple[tuple[int, int], tuple[int, int]]] = []

        for x in range(cols):
            for y in range(rows):
                top = start_y + y * size_c
                bottom = top + size_c
                left = start_x + x * size_c
                right = left + size_c
                coord_maze = (x, y)

                if self.maze.is_north_wall(coord_maze):
                    segments.append(((left, top), (right, top)))
                if self.maze.is_west_wall(coord_maze):
                    segments.append(((left, top), (left, bottom)))
                if x == cols - 1 and self.maze.is_east_wall(coord_maze):
                    segments.append(((right, top), (right, bottom)))
                if y == rows - 1 and self.maze.is_south_wall(coord_maze):
                    segments.append(((left, bottom), (right, bottom)))
        return segments
