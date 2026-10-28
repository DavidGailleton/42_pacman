"""Screen explaining the controls and the rules."""

from src.layouts.layout import Layout
from src.models.config import Config
from src.renderer.draw_utils import draw_text
from src.constants import BLACK_COLOR, PACMAN_COLOR, WHITE_COLOR
import pygame

INSTRUCTIONS: list[str] = [
    "MOVE: ARROW KEYS OR WASD",
    "EAT EVERY PACGUM, OR SURVIVE UNTIL THE TIMER ENDS,",
    "TO CLEAR A LEVEL",
    "SUPER-PACGUMS (CORNERS) MAKE GHOSTS EDIBLE",
    "ESC: PAUSE",
    "C: CHEAT MODE (INVINCIBLE)",
    "WHEN IN CHEAT MODE > N: NEXT LEVEL"
]

# Vertical pixel space between two lines of text.
LINE_HEIGHT = 70


class InstructionsScreen(Layout):
    """Show how to play until ESC or ENTER is pressed."""

    def __init__(self, config: Config, screen_size: tuple[int, int]) -> None:
        """Prepare the fonts.

        Args:
            config: Game configuration, given back to the main menu.
            screen_size: Screen size in pixels, as (width, height).
        """
        self.config = config
        self.screen_size = screen_size
        self.title_font = pygame.font.Font(None, 120)
        self.font = pygame.font.Font(None, 64)

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        """Go back to the main menu on ESC or ENTER.

        Args:
            event: Pygame event to react to.

        Returns:
            The main menu, or None to stay on this screen.
        """
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_ESCAPE,
            pygame.K_RETURN,
        ):
            # Local import: main_menu imports this module.
            from src.layouts.main_menu import MainMenu

            return MainMenu(screen_size=self.screen_size, config=self.config)
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the title, the instruction lines and the footer.

        Args:
            screen: Surface to draw on.
        """
        screen.fill(BLACK_COLOR)
        center_x = self.screen_size[0] // 2
        draw_text(
            screen,
            self.title_font,
            "INSTRUCTIONS",
            PACMAN_COLOR,
            (center_x, 150),
        )
        for index, line in enumerate(INSTRUCTIONS):
            draw_text(
                screen,
                self.font,
                line,
                WHITE_COLOR,
                (center_x, 300 + index * LINE_HEIGHT),
            )
        draw_text(
            screen,
            self.font,
            "PRESS ESC TO GO BACK",
            WHITE_COLOR,
            (center_x, self.screen_size[1] - 100),
        )
