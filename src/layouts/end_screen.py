from src.layouts.layout import Layout
from src.models.config import Config
from src.score_management import add_score, MAX_NAME_LENGTH, ScoreException
from src.renderer.draw_utils import draw_text
from src.constants import BLACK_COLOR, PACMAN_COLOR, BLINKY_COLOR, WHITE_COLOR
import pygame

CURSOR_BLINK_TIME = 0.5


class EndScreen(Layout):
    def __init__(
        self,
        config: Config,
        screen_size: tuple[int, int],
        score: int,
        win: bool,
    ) -> None:
        self.config = config
        self.screen_size = screen_size
        self.score = score
        self.win = win
        self.name: str = ""
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self.title_font = pygame.font.Font(None, 120)
        self.font = pygame.font.Font(None, 64)

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_RETURN:
            try:
                add_score(config=self.config, name=self.name, score=self.score)
            except ScoreException as e:
                print(e)
            from src.layouts.main_menu import MainMenu

            return MainMenu(screen_size=self.screen_size, config=self.config)
        if event.key == pygame.K_BACKSPACE:
            self.name = self.name[-1:]
        elif len(self.name) < MAX_NAME_LENGTH:
            char = self._key_to_char(event.key)
            if char is not None:
                self.name += char
        return None

    def update(self, dt: float) -> Layout | None:
        self.cursor_timer += dt
        if self.cursor_timer >= CURSOR_BLINK_TIME:
            self.cursor_timer = 0.0
            self.cursor_visible = not self.cursor_visible
        return None

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BLACK_COLOR)
        center_x = self.screen_size[0] // 2
        if self.win:
            title = "CONGRATULATION"
            color = PACMAN_COLOR
        else:
            title = "GAME OVER"
            color = BLINKY_COLOR
        cursor = "|" if self.cursor_visible else " "
        draw_text(screen, self.title_font, title, color, (center_x, 250))
        draw_text(
            screen,
            self.font,
            f"SCORE: {self.score}",
            WHITE_COLOR,
            (center_x, 420),
        )
        draw_text(
            screen, self.font, "ENTER YOUR NAME:", WHITE_COLOR, (center_x, 550)
        )
        draw_text(
            screen,
            self.font,
            self.name + cursor,
            PACMAN_COLOR,
            (center_x, 640),
        )
        draw_text(
            screen,
            self.font,
            "PRESS ENTER TO SAVE",
            WHITE_COLOR,
            (center_x, 800),
        )

    @staticmethod
    def _key_to_char(key: int) -> str | None:
        """Turn a key code into a name character, like MLX keycodes."""
        if pygame.K_a <= key <= pygame.K_z or pygame.K_0 <= key <= pygame.K_9:
            return chr(key).upper()
        if key == pygame.K_SPACE:
            return " "
        return None
