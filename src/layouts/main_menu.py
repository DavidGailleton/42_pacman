from src.layouts.layout import Layout
from src.layouts.menu import Menu
from src.layouts.game import Game
from src.models.config import Config
from src.score_management import get_scores
import pygame


class MainMenu(Layout):
    def __init__(self, screen_size: tuple[int, int], config: Config) -> None:
        self.screen_size = screen_size
        self.config = config
        self.menu = Menu(
            options=["Start Game", "View HighScores", "Instructions", "Exit"]
        )

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        choice = self.menu.handle_event(event)
        if choice == "Start Game":
            return Game(config=self.config, screen_size=self.screen_size)
        elif choice == "View HighScores":
            from src.layouts.view_score import ViewScores
            return ViewScores(
                screen_size=self.screen_size,
                config=self.config,
                scores=get_scores(config=self.config)
            )
        elif choice == "Instructions":
            from src.layouts.instructions import Instructions
            return Instructions(
                screen_size=self.screen_size,
                config=self.config
            )
        elif choice == "Exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        return None

    def draw(self, screen: pygame.Surface) -> None:
        screen_menu = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        screen_menu.fill((0, 0, 0))
        screen.blit(screen_menu, (0, 0))
        self.menu.draw(screen=screen)
