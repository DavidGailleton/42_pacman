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
            self._fill_rect(screen, (x1 - half, y1), (thickness, y2 - y1),
                            color)
        self._fill_circle(screen, half, (x1, y1), color)
        self._fill_circle(screen, half, (x2, y2), color)

    def _fill_rect(self, screen: pygame.Surface, coord: tuple[int, int],
                   w_h: tuple[int, int], color: tuple[int, int, int]) -> None:
        start_x, start_y = coord
        w, h = w_h
        for x in range(start_x, start_x + w):
            for y in range(start_y, start_y + h):
                screen.set_at((x, y), color)

    def _fill_circle(self, screen: pygame.Surface, radius: int,
                     coord_center: tuple[int, int],
                     color: tuple[int, int, int]) -> None:
        cx, cy = coord_center
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
