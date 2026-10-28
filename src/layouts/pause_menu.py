from __future__ import annotations

from typing import TYPE_CHECKING

from src.layouts.layout import Layout
from src.layouts.menu import Menu
import pygame

if TYPE_CHECKING:
    from src.layouts.game import Game


class PauseMenu(Layout):
    """Pause screen drawn over the frozen game."""
    def __init__(self, game: Game) -> None:
        """Pause a game.

        Args:
            game: The game to resume or leave.
        """
        self.game = game
        self.menu = Menu(options=["Resume", "Main menu"])

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        """Resume the game (option or Esc) or go back to the main menu.

        Args:
            event: Pygame event to react to.

        Returns:
            The paused game, the main menu, or None to stay paused.
        """
        choice = self.menu.handle_event(event)
        if event.type != pygame.KEYDOWN:
            return None
        if choice == "Resume" or event.key == pygame.K_ESCAPE:
            return self.game
        if choice == "Main menu":
            # Local import: main_menu -> game -> pause_menu is a cycle.
            from src.layouts.main_menu import MainMenu

            return MainMenu(
                screen_size=self.game.screen_size, config=self.game.config
            )
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the game, a dark layer over it, then the menu.

        Args:
            screen: Surface to draw on.
        """
        self.game.draw(screen=screen)
        self._draw_layout_opacity(screen=screen)
        self.menu.draw(screen=screen)

    def _draw_layout_opacity(self, screen: pygame.Surface) -> None:
        """Darken the whole screen with a half-transparent black layer.

        Args:
            screen: Surface to draw on.
        """
        opac = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        opac.fill((0, 0, 0, 160))
        screen.blit(opac, (0, 0))
