from src.utils.maze import Maze
import pygame


MAZE_SCREEN_RATIO = 0.8
BLACK_COLOR = (0, 0, 0)
MAZE_COLOR = (33, 33, 222)


class MazeRenderer:
    def __init__(self, maze: Maze, screen_size: tuple[int, int]) -> None:
        self.screen_size = screen_size
        self.set_maze(maze)

    def set_maze(self, maze: Maze) -> None:
        self.maze = maze
        width_x, height_y = maze.get_shape()
        width, height = self.screen_size
        width = int(width * MAZE_SCREEN_RATIO)
        height = int(height * MAZE_SCREEN_RATIO)
        width_cell = width / width_x
        height_cell = height / height_y

        self.cell_size = int(min(width_cell, height_cell))
        self.surface = self._build_surface()

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.surface, (0, 0))

    def _build_surface(self) -> pygame.Surface:
        start_y, start_x = self._get_offset()
        max_x, max_y = self.maze.get_shape()

        tmp_y, tmp_x = (start_y, start_x)
        screen = pygame.Surface(self.screen_size)
        screen.fill(BLACK_COLOR)
        for x in range(0, max_x):
            tmp_y = start_y
            for y in range(0, max_y):
                self._draw_cell(screen, (tmp_y, tmp_x), (x, y))
                tmp_y += (self.cell_size)
            tmp_x += (self.cell_size)

        return screen

    def _get_offset(self) -> tuple[int, int]:
        w, h = self.screen_size
        nb_cell, _ = self.maze.get_shape()
        maze_dist_middle = int(nb_cell * self.cell_size / 2)
        middle_w = int(w / 2)
        x = middle_w - maze_dist_middle
        y = int(h * (1 - MAZE_SCREEN_RATIO) / 2)
        return (y, x)

    def _draw_wall(self, screen: pygame.Surface,
                   segment: tuple[tuple[int, int], tuple[int, int]],
                   thickness: int, half: int, color: tuple[int, int, int]
                   ) -> None:
        (x1, y1), (x2, y2) = segment
        if y1 == y2:
            self._fill_rect(screen, (x1, y1 - half), (x2 - x1, thickness),
                            color)
        else:
            self._fill_rect(screen, (x1 - half, y1), (thickness, y1 - y2),
                            color)
        self._fill_circle(screen, half, (y1, x1), color)
        self._fill_circle(screen, half, (y2, x2), color)

    def _fill_rect(self, screen: pygame.Surface, coord: tuple[int, int],
                   w_h: tuple[int, int], color: tuple[int, int, int]) -> None:
        start_y, start_x = coord
        w, h = w_h
        for x in range(start_x, start_x + w):
            for y in range(start_y, start_y + h):
                screen.set_at((x, y), color)

    def _fill_circle(self, screen: pygame.Surface, radius: int,
                     coord_center: tuple[int, int],
                     color: tuple[int, int, int]) -> None:
        cy, cx = coord_center
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if (dy * dy + dx * dx) <= radius * radius:
                    screen.set_at((cx + dx, cy + dy), color)

    def _get_segments(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        start_y, start_x = self._get_offset()
        rows, cols = self.maze.get_shape()
        size_c = self.cell_size
        segments: list[tuple[tuple[int, int], tuple[int, int]]] = []

        for x in range(cols):
            for y in range(rows):
                top = start_y + y * size_c
                bottom = top + size_c
                left = start_x + x * size_c
                right = left + size_c
                coord_maze = (y, x)

                if self.maze.is_north_wall(coord_maze):
                    segments.append(((top, left), (top, right)))
                if self.maze.is_west_wall(coord_maze):
                    segments.append(((top, left), (bottom, left)))
                if x == cols - 1 and self.maze.is_east_wall(coord_maze):
                    segments.append(((top, right), (bottom, right)))
                if y == rows - 1 and self.maze.is_south_wall(coord_maze):
                    segments.append(((bottom, left), (bottom, right)))

    def _draw_cell(self, screen: pygame.Surface, offset: tuple[int, int],
                   coord: tuple[int, int]) -> None:
        tmp_y, tmp_x = offset
        stock_x = tmp_x
        is_close_cell = 0

        if self.maze.is_west_wall(coord):
            self._draw_vertical(screen, (tmp_y, tmp_x))
            is_close_cell += 1

        if self.maze.is_north_wall(coord):
            self._draw_horizental(screen, (tmp_y, tmp_x))
            is_close_cell += 1

        tmp_x += self.cell_size
        if self.maze.is_east_wall(coord):
            self._draw_vertical(screen, (tmp_y, tmp_x))
            is_close_cell += 1

        tmp_y += self.cell_size
        if self.maze.is_south_wall(coord):
            self._draw_horizental(screen, (tmp_y, stock_x))
            is_close_cell += 1

        if is_close_cell == 4:
            self._fill_cell(screen, offset)

    def _fill_cell(self, screen: pygame.Surface, offset: tuple[int, int]
                   ) -> None:
        min_y, min_x = offset
        for y in range(min_y, min_y + self.cell_size):
            self._draw_horizental(screen, (y, min_x))

    def _draw_vertical(self, screen: pygame.Surface, offset: tuple[int, int]
                       ) -> None:
        start_y, start_x = offset
        max_y = start_y + self.cell_size
        for x in range(start_x, start_x + 3):
            for y in range(start_y, max_y):
                screen.set_at((x, y), MAZE_COLOR)

    def _draw_horizental(self, screen: pygame.Surface, offset: tuple[int, int]
                         ) -> None:
        start_y, start_x = offset
        max_x = start_x + self.cell_size
        for y in range(start_y, start_y + 3):
            for x in range(start_x, max_x):
                screen.set_at((x, y), MAZE_COLOR)
