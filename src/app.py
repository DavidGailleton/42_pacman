from src.models.config import Config
from src.layouts.layout import Layout
from src.constants import (
    WIDTH_SIZE,
    HEIGHT_SIZE, FPS
)
from src.layouts.game import Game
import pygame


class App:
    def __init__(self, config: Config) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH_SIZE, HEIGHT_SIZE))
        self.clock = pygame.time.Clock()
        self.config = config
        self.layout: Layout | None = Game(
            config=config,
            screen_size=self.screen.get_size()
        )

    def run(self) -> None:
        while self.layout is not None:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.layout = None
                    break
                next_layout = self.layout.handle_event(event)
                if next_layout is not None:
                    self.layout = next_layout
            if self.layout is None:
                break
            next_layout = self.layout.update(dt)
            if next_layout is not None:
                self.layout = next_layout
            self.layout.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
