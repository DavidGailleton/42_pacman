"""Pixel drawing helpers shared by the renderers.

Only ``Surface.set_at`` is used, the pygame equivalent of MLX
``mlx_pixel_put``, so every shape is drawn pixel by pixel.
"""

import pygame

from src.constants import MAZE_SCREEN_RATIO, Color


def fill_rect(
    screen: pygame.Surface,
    coord: tuple[int, int],
    w_h: tuple[int, int],
    color: Color,
) -> None:
    """Fill a rectangle pixel by pixel.

    Args:
        screen: Surface to draw on.
        coord: Top-left corner of the rectangle, in pixels.
        w_h: Width and height of the rectangle, in pixels.
        color: Fill color.
    """
    start_x, start_y = coord
    w, h = w_h
    for x in range(start_x, start_x + w):
        for y in range(start_y, start_y + h):
            screen.set_at((x, y), color)


def fill_circle(
    screen: pygame.Surface,
    radius: int,
    coord_center: tuple[int, int],
    color: Color,
) -> None:
    """Fill a disc pixel by pixel.

    Args:
        screen: Surface to draw on.
        radius: Radius of the disc, in pixels.
        coord_center: Center of the disc, in pixels.
        color: Fill color.
    """
    cx, cy = coord_center
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if (dy * dy + dx * dx) <= radius * radius:
                screen.set_at((cx + dx, cy + dy), color)


def compute_layout(
    maze_shape: tuple[int, int], screen_size: tuple[int, int]
) -> tuple[int, tuple[int, int]]:
    """Compute where the maze is drawn on the screen.

    Every renderer uses this so they all agree on where a cell is.

    Args:
        maze_shape: Maze size in cells, as (width, height).
        screen_size: Screen size in pixels, as (width, height).

    Returns:
        The cell size in pixels, and the pixel offset (x, y) of the
        maze top-left corner. The maze is centered horizontally.
    """
    nb_cell_x, nb_cell_y = maze_shape
    screen_w, screen_h = screen_size
    width_cell = screen_w * MAZE_SCREEN_RATIO / nb_cell_x
    height_cell = screen_h * MAZE_SCREEN_RATIO / nb_cell_y
    cell_size = int(min(width_cell, height_cell))

    offset_x = screen_w // 2 - nb_cell_x * cell_size // 2
    offset_y = int(screen_h * (1 - MAZE_SCREEN_RATIO) / 2)
    return cell_size, (offset_x, offset_y)


def to_pixel(
    position: tuple[float, float], cell_size: int, offset: tuple[int, int]
) -> tuple[int, int]:
    """Convert a float cell position to the pixel of its center.

    Every moving renderer uses this so a position lands on the same
    pixel whatever is drawn there.

    Args:
        position: Position in cells, as floats (x, y).
        cell_size: Size of a cell, in pixels.
        offset: Pixel offset (x, y) of the maze top-left corner.

    Returns:
        The pixel (x, y) of the center of the drawn shape.
    """
    x, y = position
    offset_x, offset_y = offset
    half_cell = cell_size // 2
    # int() keeps whole cells exact: x=3.0 is always 3 cells away
    # from x=0.0, whatever the rounding of the half cell.
    pixel_x = offset_x + half_cell + int(x * cell_size)
    pixel_y = offset_y + half_cell + int(y * cell_size)
    return pixel_x, pixel_y


def draw_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: Color,
    center: tuple[int, int],
) -> None:
    """Draw a line of text centered on a point.

    Args:
        screen: Surface to draw on.
        font: Font used to render the text.
        text: Text to draw.
        color: Text color.
        center: Pixel (x, y) the text is centered on.
    """
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))
