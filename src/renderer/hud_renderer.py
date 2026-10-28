from src.utils.maze import Maze
from src.constants import WHITE_COLOR, CHEAT_COLOR, HUD_MARGIN
import pygame
import math


class HudRenderer:
    """Draws the score, lives, level and timer above the maze."""
    def __init__(self, maze: Maze, screen_size: tuple[int, int]) -> None:
        """Load the HUD font.

        Args:
            maze: Maze of the current level.
            screen_size: Screen size in pixels, as (width, height).
        """
        self.cell_size = maze.get_shape()
        self.screen_size = screen_size
        self.font = pygame.font.Font(None, 48)

    def draw(
        self,
        screen: pygame.Surface,
        lives: int,
        score: int,
        time_left: float,
        lvl: int,
        cheat_mode: bool,
    ) -> None:
        """Draw the HUD line at the top, and the cheat label if needed.

        Args:
            screen: Surface to draw on.
            lives: Lives left.
            score: Current score.
            time_left: Seconds left in the level.
            lvl: Current level number.
            cheat_mode: When True, "CHEAT MODE" is shown at the bottom.
        """
        seconds = math.ceil(time_left)
        text = (
            f"LEVEL: {lvl} || SCORE: {score} || LIVES : {lives}"
            f" || TIMER: {seconds // 60}:{seconds % 60:02d}"
        )
        image = self.font.render(text, True, WHITE_COLOR)
        rect = image.get_rect(midtop=(self.screen_size[0] // 2, HUD_MARGIN))
        screen.blit(image, rect)
        if cheat_mode:
            cheat = self.font.render("CHEAT MODE", True, CHEAT_COLOR)
            cheat_rect = cheat.get_rect(
                midbottom=(
                    self.screen_size[0] // 2,
                    self.screen_size[1] - HUD_MARGIN,
                )
            )
            screen.blit(cheat, cheat_rect)
