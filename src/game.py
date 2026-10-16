"""Pygame window and main game object."""

import os

# SDL tries to create an OpenGL (GLX) context to accelerate the window
# surface. On some machines (broken/missing GL drivers, remote X) this
# triggers a fatal X11 error that kills the process before Python can
# catch it. Forcing the plain software framebuffer avoids GLX entirely.
# Must be set before pygame initialises the display.
os.environ.setdefault("SDL_FRAMEBUFFER_ACCELERATION", "0")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame
from src.renderer.maze_renderer import MazeRenderer
from src.utils.maze import Maze
from src.models.config import Config


WIDTH_SIZE = 1920
HEIGHT_SIZE = 1080


class Game:
    """Own the pygame window and clock."""

    def __init__(self, config: Config) -> None:
        """Initialise pygame and open the game window."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH_SIZE, HEIGHT_SIZE))
        self.clock = pygame.time.Clock()
        self.running = False
        self.maze = Maze(config=config)
        self.maze_renderer = MazeRenderer(self.maze, self.screen.get_size())

        import time

        time.sleep(2)

    def __del__(self) -> None:
        """Shut pygame down when the game object is destroyed."""
        pygame.quit()

    def run(self) -> None:
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.maze_renderer.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
