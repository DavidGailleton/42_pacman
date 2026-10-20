from abc import ABC, abstractmethod
import pygame


class Layout(ABC):
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> "Layout | None":
        pass

    def update(self, dt: float) -> "Layout | None":
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass
