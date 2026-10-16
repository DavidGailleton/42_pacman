import pygame
from src.models.pacgum import Pacgum
from src.utils.maze import Maze


MAZE_SCREEN_RATIO = 0.8
WHITE_COLOR = (255, 255, 255)


class PacgumRenderer:
    def __init__(self, pacgum: Pacgum, screen_size: tuple[int, int],
                 maze: Maze) -> None:
        self.screen_size = screen_size
        self.shape = maze.get_shape()
        self.set_pacgum(pacgum)

    def set_pacgum(self, pacgum: Pacgum) -> None:
        self.pacgum = pacgum
        width_x, height_y = self.shape
        width, height = self.screen_size
        width = int(width * MAZE_SCREEN_RATIO)
        height = int(height * MAZE_SCREEN_RATIO)
        width_cell = width / width_x
        height_cell = height / height_y
        self.cell_size = int(min(width_cell, height_cell))
        self.half = self.cell_size // 2
        self.super_radius = self.cell_size // 4
        self.radius = self.cell_size // 10
        self.offset = self._get_offset()
        self.dot = self._make_dot(self.radius)
        self.super_dot = self._make_dot(self.super_radius)

    def draw(self, screen: pygame.Surface) -> None:
        for cell in self.pacgum.get_pacgum():
            screen.blit(self.dot, self._dot_position(cell, self.radius))
        for cell in self.pacgum.get_super_pacgum():
            screen.blit(self.super_dot,
                        self._dot_position(cell, self.super_radius))

    def _make_dot(self, radius: int) -> pygame.Surface:
        size = 2 * radius + 1
        dot = pygame.Surface((size, size), pygame.SRCALPHA)
        self._fill_circle(dot, radius, (radius, radius), WHITE_COLOR)
        return dot

    def _dot_position(self, cell: tuple[int, int],
                      radius: int) -> tuple[int, int]:
        add_y, add_x = self.offset
        px, py = cell
        cx = px * self.cell_size + self.half + add_x
        cy = py * self.cell_size + self.half + add_y
        return (cx - radius, cy - radius)

    def _fill_circle(self, screen: pygame.Surface, radius: int,
                     coord_center: tuple[int, int],
                     color: tuple[int, int, int]) -> None:
        cx, cy = coord_center
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if (dy * dy + dx * dx) <= radius * radius:
                    screen.set_at((cx + dx, cy + dy), color)

    def _get_offset(self) -> tuple[int, int]:
        w, h = self.screen_size
        nb_cell, _ = self.shape
        maze_dist_middle = int(nb_cell * self.cell_size / 2)
        middle_w = int(w / 2)
        x = middle_w - maze_dist_middle
        y = int(h * (1 - MAZE_SCREEN_RATIO) / 2)
        return (y, x)
