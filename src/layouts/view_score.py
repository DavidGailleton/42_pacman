from src.layouts.layout import Layout
from src.models.config import Config
import pygame
from src.score_management import Score
from src.constants import MENU_LINE_SPACING, WHITE_COLOR


FONT_SIZE = 35


class ViewScores(Layout):
    def __init__(self, screen_size: tuple[int, int], config: Config,
                 scores: list[Score]) -> None:
        self.screen_size = screen_size
        self.config = config
        self.scores = scores
        self.font = pygame.font.Font(None, FONT_SIZE)

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        if event.key == pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            from src.layouts.main_menu import MainMenu
            return MainMenu(
                screen_size=self.screen_size,
                config=self.config
            )
        return None

    def draw(self, screen: pygame.Surface) -> None:
        tmp_index = 0
        tips_text = "Press ESCAPE back to the MAIN MENU"
        screen_menu = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        screen_menu.fill((0, 0, 0))
        screen.blit(screen_menu, [0, 0])
        center_x = screen.get_width() // 2
        tot_height = (len(self.scores)) * MENU_LINE_SPACING
        start_y = (screen.get_height() // 2 - tot_height // 2
                   - FONT_SIZE * len(self.scores) // 2)
        for index, (name, score) in enumerate(self.scores):
            tmp_index = index
            text = f"{index + 1}.{name} : {score}"
            color = WHITE_COLOR
            image = self.font.render(text, True, color)
            rect = image.get_rect(
                center=(center_x, start_y + index * FONT_SIZE)
            )
            screen.blit(image, rect)
        image = self.font.render(tips_text, True, color)
        rect = image.get_rect(
            center=(center_x, start_y + (tmp_index + 3) * FONT_SIZE)
        )
        screen.blit(image, rect)
