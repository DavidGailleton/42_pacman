from src.utils.maze import Maze
import pygame


MAZE_SCREEN_RATIO = 0.8


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
        paper = pygame.Surface(self.screen_size)
        paper.fill((30, 30, 60))
        for x in range(0, max_x):
            tmp_y = start_y
            for y in range(0, max_y):
                self._draw_cell(paper, (tmp_y, tmp_x), (x, y))
                tmp_y += self.cell_size
            tmp_x += self.cell_size

        return paper

    def _get_offset(self) -> tuple[int, int]:
        w, h = self.screen_size
        x = int(w * (1 - MAZE_SCREEN_RATIO) / 2)
        y = int(h * (1 - MAZE_SCREEN_RATIO) / 2)
        return (y, x)

    def _draw_cell(self, paper: pygame.Surface, offset: tuple[int, int],
                   coord: tuple[int, int]) -> None:
        tmp_y, tmp_x = offset
        stock_x = tmp_x

        if self.maze.is_west_wall(coord):
            self._draw_vertical(paper, (tmp_y, tmp_x))

        if self.maze.is_north_wall(coord):
            self._draw_horizental(paper, (tmp_y, tmp_x))

        tmp_x += self.cell_size
        if self.maze.is_east_wall(coord):
            self._draw_vertical(paper, (tmp_y, tmp_x))

        tmp_y += self.cell_size
        if self.maze.is_south_wall(coord):
            self._draw_horizental(paper, (tmp_y, stock_x))

    def _draw_vertical(self, paper: pygame.Surface, offset: tuple[int, int]
                       ) -> None:
        start_y, start_x = offset
        max_y = start_y + self.cell_size
        for y in range(start_y, max_y):
            paper.set_at((start_x, y), (255, 0, 0))

    def _draw_horizental(self, paper: pygame.Surface, offset: tuple[int, int]
                         ) -> None:
        start_y, start_x = offset
        max_x = start_x + self.cell_size
        for x in range(start_x, max_x):
            paper.set_at((x, start_y), (255, 0, 0))
