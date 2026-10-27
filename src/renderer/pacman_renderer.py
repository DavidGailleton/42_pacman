"""Draw Pac-Man at a float position in the maze."""

import math

import pygame

from src.constants import (
    PACMAN_COLOR,
    PACMAN_MOUTH_MAX_ANGLE,
    PACMAN_MOUTH_SPEED,
    PACMAN_RADIUS_RATIO,
    Direction,
)
from src.renderer.draw_utils import compute_layout, to_pixel
from src.utils.maze import Maze

# Number of mouth openings drawn, from closed to fully open.
MOUTH_FRAMES: int = 8


class PacmanRenderer:
    """Draw Pac-Man, with an animated mouth facing its direction.

    Positions are in cells, as floats: ``(3.0, 2.0)`` is the center of
    cell (3, 2) and ``(3.5, 2.0)`` is halfway to cell (4, 2).

    Drawing pixel by pixel is slow, so each look (direction, mouth
    opening) is drawn once on a small surface, kept in ``_sprites``,
    and only blitted on the following frames.
    """

    def __init__(self, maze: Maze, screen_size: tuple[int, int]) -> None:
        """Compute the layout for this maze.

        Args:
            maze: Maze Pac-Man moves in.
            screen_size: Screen size in pixels, as (width, height).
        """
        self.screen_size = screen_size
        self._phase: float = 0.0
        self.set_maze(maze)

    def set_maze(self, maze: Maze) -> None:
        """Change the maze and recompute the layout.

        Args:
            maze: New maze Pac-Man moves in.
        """
        self.maze = maze
        self.cell_size, self.offset = compute_layout(
            maze.get_shape(), self.screen_size
        )
        self.radius = int(self.cell_size * PACMAN_RADIUS_RATIO)
        # The cell size changed: the old sprites have the wrong size.
        self._sprites: dict[tuple[Direction, int], pygame.Surface] = {}

    def update(self, dt: float) -> None:
        """Advance the mouth animation.

        Args:
            dt: Seconds since the last frame.
        """
        self._phase = (self._phase + dt * PACMAN_MOUTH_SPEED) % 1.0

    def draw(
        self,
        screen: pygame.Surface,
        position: tuple[float, float],
        direction: Direction,
    ) -> None:
        """Draw Pac-Man on the screen.

        Args:
            screen: Surface to draw on.
            position: Position in cells, as floats (x, y).
            direction: Direction Pac-Man faces, as (dx, dy).
        """
        # Triangle wave: fully open at phase 0, closed at 0.5.
        opening = abs(2 * self._phase - 1)
        frame = round(opening * (MOUTH_FRAMES - 1))
        cx, cy = to_pixel(position, self.cell_size, self.offset)
        sprite = self._get_sprite(direction, frame)
        screen.blit(sprite, (cx - self.radius, cy - self.radius))

    def _get_sprite(self, direction: Direction, frame: int) -> pygame.Surface:
        """Return the sprite of a look, drawing it the first time.

        Args:
            direction: Direction Pac-Man faces, as (dx, dy).
            frame: Mouth opening, from 0 (closed) to
                ``MOUTH_FRAMES - 1`` (fully open).

        Returns:
            The sprite, a square surface of side ``2 * radius + 1``.
        """
        key = (direction, frame)
        if key not in self._sprites:
            mouth_angle = PACMAN_MOUTH_MAX_ANGLE * frame / (MOUTH_FRAMES - 1)
            size = 2 * self.radius + 1
            # SRCALPHA: pixels not drawn stay transparent.
            sprite = pygame.Surface((size, size), pygame.SRCALPHA)
            center = (self.radius, self.radius)
            self._fill_pacman(sprite, center, direction, mouth_angle)
            self._sprites[key] = sprite
        return self._sprites[key]

    def _fill_pacman(
        self,
        screen: pygame.Surface,
        center: tuple[int, int],
        direction: Direction,
        mouth_angle: float,
    ) -> None:
        """Fill a disc pixel by pixel, leaving out the mouth wedge.

        Args:
            screen: Surface to draw on.
            center: Center of Pac-Man, in pixels.
            direction: Direction the mouth faces, as (dx, dy).
            mouth_angle: Half-angle of the mouth, in degrees.
        """
        cx, cy = center
        radius = self.radius
        facing = math.degrees(math.atan2(direction[1], direction[0]))
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy > radius * radius:
                    continue
                angle = math.degrees(math.atan2(dy, dx))
                # Difference wrapped to [-180, 180).
                diff = (angle - facing + 180) % 360 - 180
                if abs(diff) < mouth_angle:
                    continue
                screen.set_at((cx + dx, cy + dy), PACMAN_COLOR)
