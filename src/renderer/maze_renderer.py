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
        paper = pygame.Surface(self.screen_size)
        paper.fill(BLACK_COLOR)
        for x in range(0, max_x):
            tmp_y = start_y
            for y in range(0, max_y):
                self._draw_cell(paper, (tmp_y, tmp_x), (x, y))
                tmp_y += (self.cell_size)
            tmp_x += (self.cell_size)

        return paper

    def _get_offset(self) -> tuple[int, int]:
        w, h = self.screen_size
        nb_cell, _ = self.maze.get_shape()
        maze_dist_middle = int(nb_cell * self.cell_size / 2)
        middle_w = int(w / 2)
        x = middle_w - maze_dist_middle
        y = int(h * (1 - MAZE_SCREEN_RATIO) / 2)
        return (y, x)

    def _draw_cell(self, paper: pygame.Surface, offset: tuple[int, int],
                   coord: tuple[int, int]) -> None:
        tmp_y, tmp_x = offset
        stock_x = tmp_x
        is_close_cell = 0

        if self.maze.is_west_wall(coord):
            self._draw_vertical(paper, (tmp_y, tmp_x))
            is_close_cell += 1

        if self.maze.is_north_wall(coord):
            self._draw_horizental(paper, (tmp_y, tmp_x))
            is_close_cell += 1

        tmp_x += self.cell_size
        if self.maze.is_east_wall(coord):
            self._draw_vertical(paper, (tmp_y, tmp_x))
            is_close_cell += 1

        tmp_y += self.cell_size
        if self.maze.is_south_wall(coord):
            self._draw_horizental(paper, (tmp_y, stock_x))
            is_close_cell += 1

        if is_close_cell == 4:
            self._fill_cell(paper, offset)

    def _fill_cell(self, paper: pygame.Surface, offset: tuple[int, int]
                   ) -> None:
        min_y, min_x = offset
        for y in range(min_y, min_y + self.cell_size):
            self._draw_horizental(paper, (y, min_x))

    def _draw_vertical(self, paper: pygame.Surface, offset: tuple[int, int]
                       ) -> None:
        start_y, start_x = offset
        max_y = start_y + self.cell_size
        for x in range(start_x, start_x + 3):
            for y in range(start_y, max_y):
                paper.set_at((x, y), MAZE_COLOR)

    def _draw_horizental(self, paper: pygame.Surface, offset: tuple[int, int]
                         ) -> None:
        start_y, start_x = offset
        max_x = start_x + self.cell_size
        for y in range(start_y, start_y + 3):
            for x in range(start_x, max_x):
                paper.set_at((x, y), MAZE_COLOR)
