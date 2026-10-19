from src.layouts.layout import Layout
from src.layouts.game import Game
from src.layouts.menu import Menu
import pygame


class PauseMenu(Layout):
    def __init__(self, game: Game) -> None:
        self.game = game
        self.menu = Menu(options=["Resume", "Main menu"])

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        choice = self.menu.handle_event(event)
        if choice == "Resume":
            return self.game
        elif choice == "Main menu":
            return None

    def draw(self, screen: pygame.Surface) -> None:
        self.game.draw(screen=screen)
        self._draw_layout_opacity(screen=screen)
        self.menu.draw(screen=screen)

    def _draw_layout_opacity(self, screen: pygame.Surface) -> None:
        opac = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        opac.fill((0, 0, 0, 160))
        screen.blit(opac, (0, 0))
