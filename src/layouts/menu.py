import pygame
from src.constants import (
    MENU_FONT_SIZE,
    MENU_LINE_SPACING,
    PACMAN_COLOR,
    WHITE_COLOR,
)


class Menu:
    def __init__(self, options: list[str]):
        self.options = options
        self.selected = 0
        self.font = pygame.font.Font(None, MENU_FONT_SIZE)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key == pygame.K_RETURN:
            return self.options[self.selected]
        return None

    def draw(self, screen: pygame.Surface) -> None:
        center_x = screen.get_width() // 2
        tot_height = (len(self.options) - 1) * MENU_LINE_SPACING
        start_y = screen.get_height() // 2 - tot_height // 2
        for index, option in enumerate(self.options):
            if index == self.selected:
                text = f" > {option} < "
                color = PACMAN_COLOR
            else:
                text = f" = {option} = "
                color = WHITE_COLOR
            image = self.font.render(text, True, color)
            rect = image.get_rect(
                center=(center_x, start_y + index * MENU_FONT_SIZE)
            )
            screen.blit(image, rect)
