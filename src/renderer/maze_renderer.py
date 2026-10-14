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
        self._build_surface()

    def _build_surface(self) -> pygame.Surface:
        paper = pygame.Surface(self.screen_size)
        paper.fill((30, 30, 60))

    def draw(self, screen: pygame.Surface) -> None:
        pass
