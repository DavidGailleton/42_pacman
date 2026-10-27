from src.layouts.layout import Layout
from src.layouts.menu import Menu
from src.layouts.game import Game
from src.layouts.highscore_screen import HighscoreScreen
from src.layouts.instructions_screen import InstructionsScreen
from src.models.config import Config
from src.score_management import get_scores
import pygame


class MainMenu(Layout):
    """First screen: start a game, see scores, read help or quit."""

    def __init__(self, screen_size: tuple[int, int], config: Config) -> None:
        """Build the menu options.

        Args:
            screen_size: Screen size in pixels, as (width, height).
            config: Game configuration, given to the next screens.
        """
        self.screen_size = screen_size
        self.config = config
        self.menu = Menu(
            options=["Start Game", "View HighScores", "Instructions", "Exit"]
        )

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        """Open the screen matching the chosen option.

        Args:
            event: Pygame event to react to.

        Returns:
            The next screen, or None to stay on the menu.
        """
        choice = self.menu.handle_event(event)
        if choice == "Start Game":
            return Game(config=self.config, screen_size=self.screen_size)
        if choice == "View HighScores":
            return HighscoreScreen(
                config=self.config, screen_size=self.screen_size
            )
        if choice == "Instructions":
            return InstructionsScreen(
                config=self.config, screen_size=self.screen_size
            )
        if choice == "Exit":
            # Same path as closing the window: App.run stops on QUIT.
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu on a black background.

        Args:
            screen: Surface to draw on.
        """
        screen.fill((0, 0, 0))
        self.menu.draw(screen=screen)
