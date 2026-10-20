from src.models.config import Config
from src.layouts.layout import Layout
from src.constants import WIDTH_SIZE, HEIGHT_SIZE, FPS, FRAME_TIME
from src.layouts.main_menu import MainMenu
import pygame


class App:
    def __init__(self, config: Config) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH_SIZE, HEIGHT_SIZE))
        self.clock = pygame.time.Clock()
        self.config = config
        self.layout: Layout | None = MainMenu(
            config=config, screen_size=self.screen.get_size()
        )

    def run(self) -> None:
        while self.layout is not None:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.layout = None
                    break
                next_layout = self.layout.handle_event(event)
                if next_layout is not None:
                    self.layout = next_layout
            if self.layout is None:
                break
            next_layout = self.layout.update(FRAME_TIME)
            if next_layout is not None:
                self.layout = next_layout
            self.layout.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
