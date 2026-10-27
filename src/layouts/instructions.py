from src.layouts.layout import Layout
from src.models.config import Config
from src.constants import BLACK_COLOR, PACMAN_COLOR, WHITE_COLOR
import pygame

LINE_SPACING = 50


class Instructions(Layout):
    def __init__(self, screen_size: tuple[int, int], config: Config) -> None:
        self.screen_size = screen_size
        self.config = config
        self.title_font = pygame.font.Font(None, 120)
        self.section_font = pygame.font.Font(None, 56)
        self.font = pygame.font.Font(None, 40)

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            from src.layouts.main_menu import MainMenu

            return MainMenu(screen_size=self.screen_size, config=self.config)
        return None

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BLACK_COLOR)
        center_x = self.screen_size[0] // 2
        self._draw_text(
            screen, self.title_font, "INSTRUCTIONS", PACMAN_COLOR,
            (center_x, 120),
        )
        y = 250
        for title, lines in self._sections():
            self._draw_text(
                screen, self.section_font, title, PACMAN_COLOR, (center_x, y)
            )
            y += LINE_SPACING + 10
            for line in lines:
                self._draw_text(
                    screen, self.font, line, WHITE_COLOR, (center_x, y)
                )
                y += LINE_SPACING
            y += LINE_SPACING // 2
        self._draw_text(
            screen,
            self.font,
            "Press ESCAPE back to the MAIN MENU",
            PACMAN_COLOR,
            (center_x, self.screen_size[1] - 80),
        )

    def _sections(self) -> list[tuple[str, list[str]]]:
        """Build the instruction texts, with the points of the config.

        Returns:
            A list of (section title, lines) pairs.
        """
        return [
            (
                "CONTROLS",
                [
                    "Move: ARROW KEYS or W A S D",
                    "Pause: ESCAPE",
                ],
            ),
            (
                "GOAL",
                [
                    "Eat every pacgum of the maze before the time runs out",
                    f"You have {self.config.lives} lives and "
                    f"{self.config.level_max_time} seconds per level",
                    "Touching a ghost costs you a life",
                ],
            ),
            (
                "POINTS",
                [
                    f"Pacgum: {self.config.point_per_pacgum}",
                    f"Super pacgum: {self.config.point_per_super_pacgum}"
                    " - ghosts become blue and edible",
                    f"Ghost: {self.config.point_per_ghost}",
                ],
            ),
        ]

    @staticmethod
    def _draw_text(
        screen: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        center: tuple[int, int],
    ) -> None:
        image = font.render(text, True, color)
        screen.blit(image, image.get_rect(center=center))
