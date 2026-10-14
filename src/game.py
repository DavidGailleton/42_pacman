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


class Game:
    """Own the pygame window and clock."""

    def __init__(self) -> None:
        """Initialise pygame and open the game window."""
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()
        self.running = False

        import time

        time.sleep(2)

    def __del__(self) -> None:
        """Shut pygame down when the game object is destroyed."""
        pygame.quit()
