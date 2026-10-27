"""Tests for the ghost renderer (off-screen surfaces, no window)."""

import pygame

from src.constants import BLACK_COLOR, BLINKY_COLOR
from src.ghost_ai import GhostState
from src.models.config import Config
from src.renderer.draw_utils import to_pixel
from src.renderer.ghost_renderer import GhostRenderer
from src.utils.maze import Maze

SCREEN_SIZE = (1920, 1080)


def make_renderer() -> GhostRenderer:
    """Build a renderer for the default 21x21 maze."""
    return GhostRenderer(Maze((21, 21), Config().seed), SCREEN_SIZE)


def body_pixel(renderer: GhostRenderer, state: GhostState) -> tuple[int, ...]:
    """Draw a ghost on black and return a pixel of its body.

    The pixel is between the eyes and the bottom, so it is body only.
    """
    screen = pygame.Surface(SCREEN_SIZE)
    screen.fill(BLACK_COLOR)
    renderer.draw(screen, (5.0, 5.0), BLINKY_COLOR, state)
    cx, cy = to_pixel((5.0, 5.0), renderer.cell_size, renderer.offset)
    return tuple(screen.get_at((cx, cy + renderer.radius // 5)))[:3]


def test_chase_ghost_has_its_color() -> None:
    """A chasing ghost is drawn with its own opaque color."""
    assert body_pixel(make_renderer(), GhostState.CHASE) == BLINKY_COLOR


def test_eaten_ghost_is_see_through() -> None:
    """An eaten ghost on black is darker than its opaque color."""
    pixel = body_pixel(make_renderer(), GhostState.EATEN)
    assert pixel != BLINKY_COLOR
    assert 0 < pixel[0] < BLINKY_COLOR[0]


def test_sprites_are_cached() -> None:
    """Each look is drawn once, then reused; a new maze clears them."""
    renderer = make_renderer()
    screen = pygame.Surface(SCREEN_SIZE)
    renderer.draw(screen, (1.0, 1.0), BLINKY_COLOR, GhostState.CHASE)
    renderer.draw(screen, (2.0, 1.0), BLINKY_COLOR, GhostState.CHASE)
    assert len(renderer._sprites) == 1
    renderer.set_maze(Maze((21, 21), Config().seed))
    assert renderer._sprites == {}


def test_draw_outside_screen_does_not_raise() -> None:
    """A ghost partly or fully off the screen is just clipped."""
    renderer = make_renderer()
    screen = pygame.Surface(SCREEN_SIZE)
    for position in [(-1.0, -1.0), (500.0, 500.0)]:
        renderer.draw(screen, position, BLINKY_COLOR, GhostState.EATEN)
