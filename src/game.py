"""Pygame window and main game object."""

import math
import os

# SDL tries to create an OpenGL (GLX) context to accelerate the window
# surface. On some machines (broken/missing GL drivers, remote X) this
# triggers a fatal X11 error that kills the process before Python can
# catch it. Forcing the plain software framebuffer avoids GLX entirely.
# Must be set before pygame initialises the display.
os.environ.setdefault("SDL_FRAMEBUFFER_ACCELERATION", "0")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame
from src.constants import LEFT, RIGHT
from src.renderer.maze_renderer import MazeRenderer
from src.renderer.pacman_renderer import PacmanRenderer
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
        self.pacman_renderer = PacmanRenderer(self.maze,
                                              self.screen.get_size())

    def __del__(self) -> None:
        """Shut pygame down when the game object is destroyed."""
        pygame.quit()

    def run(self) -> None:
        """Run the main loop until the window is closed."""
        self.running = True
        # TEMPORARY demo: Pac-Man slides around the maze center until
        # the Pac-Man model and its movement exist.
        width, height = self.maze.get_shape()
        center_x, center_y = width // 2, height // 2
        elapsed: float = 0.0
        while self.running:
            dt = self.clock.tick(60) / 1000
            elapsed += dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            demo_x = center_x + math.sin(elapsed)
            direction = RIGHT if math.cos(elapsed) >= 0 else LEFT
            self.pacman_renderer.update(dt)
            self.maze_renderer.draw(self.screen)
            self.pacman_renderer.draw(self.screen, (demo_x, center_y),
                                      direction)
            pygame.display.flip()
