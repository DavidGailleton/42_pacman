from src.utils.maze import Maze
from src.constants import WHITE_COLOR, HUD_MARGIN
import pygame


class HudRenderer:
    def __init__(self, maze: Maze, screen_size: tuple[int, int]) -> None:
        self.cell_size = maze.get_shape()
        self.screen_size = screen_size
        self.font = pygame.font.Font(None, 48)

    def draw(self, screen: pygame.Surface, lives: int, score: int,
             time_left: float, lvl: int) -> None:
        text = (f"LEVEL: {lvl} || SCORE: {score} || LIVES : {lives}"
                f" || TIMER: {int(time_left)}")
        image = self.font.render(text, True, WHITE_COLOR)
        rect = image.get_rect(midtop=(self.screen_size[0] // 2, HUD_MARGIN))
        screen.blit(image, rect)
