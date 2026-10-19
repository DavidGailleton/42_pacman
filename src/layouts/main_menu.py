from src.layouts.layout import Layout
from src.layouts.menu import Menu
from src.layouts.game import Game
from src.models.config import Config
import pygame


class MainMenu(Layout):
    def __init__(self, screen_size: tuple[int, int], config: Config) -> None:
        self.screen_size = screen_size
        self.config = config
        self.menu = Menu(
            options=[
                "Start Game",
                "View HighScores",
                "Instructions",
                "Exit"
            ]
        )

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        choice = self.menu.handle_event(event)
        if choice == "Start Game":
            return Game(
                config=self.config,
                screen_size=self.screen_size
            )
        return None

    def draw(self, screen: pygame.Surface) -> None:
        screen_menu = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        screen_menu.fill((0, 0, 0))
        screen.blit(screen_menu, (0, 0))
        self.menu.draw(screen=screen)
