"""Screen listing the top 10 highscores."""

from src.layouts.layout import Layout
from src.models.config import Config
from src.score_management import get_scores, Score
from src.renderer.draw_utils import draw_text
from src.constants import BLACK_COLOR, PACMAN_COLOR, WHITE_COLOR
import pygame

# Vertical pixel space between two score rows.
ROW_HEIGHT = 64
# Horizontal pixel distance from the screen center to each column edge.
COLUMN_HALF_WIDTH = 300


class HighscoreScreen(Layout):
    """Show the saved highscores until ESC or ENTER is pressed."""

    def __init__(self, config: Config, screen_size: tuple[int, int]) -> None:
        """Load the scores once, when the screen is opened.

        Args:
            config: Game configuration holding ``highscore_filename``.
            screen_size: Screen size in pixels, as (width, height).
        """
        self.config = config
        self.screen_size = screen_size
        self.scores: list[Score] = get_scores(config)
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
        """Draw the title, the score table and the footer.

        Args:
            screen: Surface to draw on.
        """
        screen.fill(BLACK_COLOR)
        center_x = self.screen_size[0] // 2
        draw_text(
            screen,
            self.title_font,
            "HIGHSCORES",
            PACMAN_COLOR,
            (center_x, 150),
        )
        if not self.scores:
            draw_text(
                screen, self.font, "NO SCORE YET", WHITE_COLOR, (center_x, 450)
            )
        for index, (name, score) in enumerate(self.scores):
            y = 260 + index * ROW_HEIGHT
            self._draw_row(screen, f"{index + 1}. {name}", str(score), y)
        draw_text(
            screen,
            self.font,
            "PRESS ESC TO GO BACK",
            WHITE_COLOR,
            (center_x, self.screen_size[1] - 100),
        )

    def _draw_row(
        self, screen: pygame.Surface, left: str, right: str, y: int
    ) -> None:
        """Draw one table row: name aligned left, score aligned right.

        The default font is not monospaced, so each column is drawn on
        its own to keep the table straight.

        Args:
            screen: Surface to draw on.
            left: Rank and name.
            right: Score.
            y: Vertical pixel center of the row.
        """
        center_x = self.screen_size[0] // 2
        left_image = self.font.render(left, True, WHITE_COLOR)
        screen.blit(
            left_image,
            left_image.get_rect(midleft=(center_x - COLUMN_HALF_WIDTH, y)),
        )
        right_image = self.font.render(right, True, PACMAN_COLOR)
        screen.blit(
            right_image,
            right_image.get_rect(midright=(center_x + COLUMN_HALF_WIDTH, y)),
        )
