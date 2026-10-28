from abc import ABC, abstractmethod
import pygame


class Layout(ABC):
    """Base class of every screen (menu, game, pause, end screen...).

    ``App`` calls ``handle_event``, ``update`` and ``draw`` each frame.
    Returning another layout from the first two switches screen.
    """

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> "Layout | None":
        """React to one pygame event.

        Args:
            event: Pygame event to react to.

        Returns:
            The layout to show next, or None to keep this one.
        """
        pass

    def update(self, dt: float) -> "Layout | None":
        """Advance the screen by one frame. Does nothing by default.

        Args:
            dt: Seconds since the last frame.

        Returns:
            The layout to show next, or None to keep this one.
        """
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the screen.

        Args:
            screen: Surface to draw on.
        """
        pass
