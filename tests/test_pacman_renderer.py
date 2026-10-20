"""Tests for the Pac-Man renderer (off-screen surfaces, no window)."""

import pygame

from src.constants import BLACK_COLOR, PACMAN_COLOR, RIGHT
from src.models.config import Config
from src.renderer.draw_utils import to_pixel
from src.renderer.pacman_renderer import PacmanRenderer
from src.utils.maze import Maze

SCREEN_SIZE = (1920, 1080)


def make_renderer() -> PacmanRenderer:
    """Build a renderer for the default 21x21 maze."""
    return PacmanRenderer(Maze(Config()), SCREEN_SIZE)


def test_to_pixel_cell_center() -> None:
    """Integer positions are drawn at the center of their cell."""
    renderer = make_renderer()
    offset_x, offset_y = renderer.offset
    size = renderer.cell_size
    x, y = to_pixel((0.0, 0.0), renderer.cell_size, renderer.offset)
    assert abs(x - (offset_x + size / 2)) <= 0.5
    assert abs(y - (offset_y + size / 2)) <= 0.5


def test_to_pixel_between_cells() -> None:
    """Float positions are interpolated between two cell centers."""
    renderer = make_renderer()
    size = renderer.cell_size
    x0, y0 = to_pixel((2.0, 3.0), renderer.cell_size, renderer.offset)
    x_half, y_half = to_pixel((2.5, 3.0), renderer.cell_size, renderer.offset)
    x1, _ = to_pixel((3.0, 3.0), renderer.cell_size, renderer.offset)
    assert x1 - x0 == size
    assert abs((x_half - x0) - size / 2) <= 1
    assert y_half == y0


def test_draw_mouth_faces_direction() -> None:
    """Facing right with the mouth open: back is yellow, front is not."""
    renderer = make_renderer()
    screen = pygame.Surface(SCREEN_SIZE)
    screen.fill(BLACK_COLOR)
    renderer.draw(screen, (5.0, 5.0), RIGHT)
    cx, cy = to_pixel((5.0, 5.0), renderer.cell_size, renderer.offset)
    half = renderer.radius // 2
    assert tuple(screen.get_at((cx - half, cy)))[:3] == PACMAN_COLOR
    assert tuple(screen.get_at((cx + half, cy)))[:3] == BLACK_COLOR
    assert tuple(screen.get_at((cx, cy - half)))[:3] == PACMAN_COLOR


def test_sprites_are_cached() -> None:
    """Each look is drawn once, then reused; a new maze clears them."""
    renderer = make_renderer()
    screen = pygame.Surface(SCREEN_SIZE)
    renderer.draw(screen, (5.0, 5.0), RIGHT)
    renderer.draw(screen, (6.0, 5.0), RIGHT)
    assert len(renderer._sprites) == 1
    renderer.set_maze(Maze(Config()))
    assert renderer._sprites == {}
