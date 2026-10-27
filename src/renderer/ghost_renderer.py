"""Draw a ghost at a float position in the maze."""

import pygame

from src.constants import (
    FRIGHTENED_COLOR,
    FRIGHTENED_FACE_COLOR,
    GHOST_EATEN_ALPHA,
    GHOST_EYE_COLOR,
    GHOST_PUPIL_COLOR,
    GHOST_RADIUS_RATIO,
    GHOST_SKIRT_SPEED,
    Color,
)
from src.ghost_ai import GhostState
from src.renderer.draw_utils import (
    compute_layout,
    fill_circle,
    fill_rect,
    to_pixel,
)
from src.utils.maze import Maze

# Number of bumps at the bottom of the ghost's skirt.
SKIRT_BUMPS: int = 4


class GhostRenderer:
    """Draw ghosts: normal, frightened, or eaten (see-through).

    One renderer draws every ghost: ``draw`` is called once per ghost
    with its position, color and state. Positions are in cells, as
    floats, like for ``PacmanRenderer``.

    Like for ``PacmanRenderer``, each look (color, state, skirt shift)
    is drawn once on a small surface, kept in ``_sprites``, and only
    blitted on the following frames.
    """

    def __init__(self, maze: Maze, screen_size: tuple[int, int]) -> None:
        """Compute the layout for this maze.

        Args:
            maze: Maze the ghosts move in.
            screen_size: Screen size in pixels, as (width, height).
        """
        self.screen_size = screen_size
        self._phase: float = 0.0
        self.set_maze(maze)

    def set_maze(self, maze: Maze) -> None:
        """Change the maze and recompute the layout.

        Args:
            maze: New maze the ghosts move in.
        """
        self.maze = maze
        self.cell_size, self.offset = compute_layout(
            maze.get_shape(), self.screen_size
        )
        self.radius = int(self.cell_size * GHOST_RADIUS_RATIO)
        # The cell size changed: the old sprites have the wrong size.
        self._sprites: dict[tuple[Color, GhostState, bool], pygame.Surface]
        self._sprites = {}

    def update(self, dt: float) -> None:
        """Advance the skirt animation.

        Args:
            dt: Seconds since the last frame.
        """
        self._phase = (self._phase + dt * GHOST_SKIRT_SPEED) % 1.0

    def draw(
        self,
        screen: pygame.Surface,
        position: tuple[float, float],
        color: Color,
        state: GhostState,
    ) -> None:
        """Draw one ghost on the screen.

        Args:
            screen: Surface to draw on.
            position: Position in cells, as floats (x, y).
            color: Body color of the ghost (``Ghost.color``).
            state: Current state, which picks the look of the ghost.
        """
        cx, cy = to_pixel(position, self.cell_size, self.offset)
        # The skirt has only two looks: shifted every other half cycle.
        sprite = self._get_sprite(color, state, self._phase >= 0.5)
        screen.blit(sprite, (cx - self.radius, cy - self.radius))

    def _get_sprite(
        self, color: Color, state: GhostState, shifted: bool
    ) -> pygame.Surface:
        """Return the sprite of a look, drawing it the first time.

        Args:
            color: Body color of the ghost (``Ghost.color``).
            state: State of the ghost, which picks its look.
            shifted: True to shift the skirt bumps by half a bump.

        Returns:
            The sprite, a square surface of side ``2 * radius + 1``.
        """
        key = (color, state, shifted)
        if key not in self._sprites:
            self._sprites[key] = self._make_sprite(color, state, shifted)
        return self._sprites[key]

    def _make_sprite(
        self, color: Color, state: GhostState, shifted: bool
    ) -> pygame.Surface:
        """Draw one look of a ghost on a new transparent surface.

        Args:
            color: Body color of the ghost (``Ghost.color``).
            state: State of the ghost, which picks its look.
            shifted: True to shift the skirt bumps by half a bump.

        Returns:
            The new sprite, with the ghost centered on it.
        """
        size = 2 * self.radius + 1
        # SRCALPHA: pixels not drawn stay transparent.
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (self.radius, self.radius)
        if state is GhostState.FRIGHTENED:
            self._fill_body(sprite, center, FRIGHTENED_COLOR, 1.0, shifted)
            self._draw_frightened_face(sprite, center)
        elif state is GhostState.EATEN:
            self._fill_body(sprite, center, color, GHOST_EATEN_ALPHA, shifted)
            self._draw_eyes(sprite, center)
        else:
            self._fill_body(sprite, center, color, 1.0, shifted)
            self._draw_eyes(sprite, center)
        return sprite

    def _is_in_body(self, dx: int, dy: int, shifted: bool) -> bool:
        """Tell if a pixel, relative to the center, is in the body.

        The body is a half disc on top of a square, whose bottom rows
        are cut into ``SKIRT_BUMPS`` triangular bumps (the skirt).

        Args:
            dx: Horizontal distance to the center, in pixels.
            dy: Vertical distance to the center, in pixels (down > 0).
            shifted: True to shift the bumps by half a bump.

        Returns:
            True if the pixel is part of the ghost's body.
        """
        r = self.radius
        if dy <= 0:
            return dx * dx + dy * dy <= r * r
        skirt_height = max(1, r // 3)
        depth = r - dy
        if depth >= skirt_height:
            return True
        period = max(1, 2 * r // SKIRT_BUMPS)
        # Half a bump shift every other half cycle makes it wiggle.
        shift = period // 2 if shifted else 0
        u = (dx + r + shift) % period
        # 0 at a bump's tip, 1 between two bumps.
        notch = abs(2 * u / period - 1)
        return depth >= skirt_height * notch

    def _fill_body(
        self,
        screen: pygame.Surface,
        center: tuple[int, int],
        color: Color,
        alpha: float,
        shifted: bool,
    ) -> None:
        """Fill the ghost's body pixel by pixel.

        With ``alpha`` below 1, the pixels are only partly opaque: when
        the sprite is blitted, they are mixed with what is under them,
        which makes the body see-through.

        Args:
            screen: Surface to draw on (needs SRCALPHA for ``alpha``).
            center: Center of the ghost, in pixels.
            color: Body color.
            alpha: Opacity of the body, from 0 (invisible) to 1.
            shifted: True to shift the skirt bumps by half a bump.
        """
        cx, cy = center
        r = self.radius
        pixel_color = (*color, int(255 * alpha))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if self._is_in_body(dx, dy, shifted):
                    screen.set_at((cx + dx, cy + dy), pixel_color)

    def _draw_eyes(
        self, screen: pygame.Surface, center: tuple[int, int]
    ) -> None:
        """Draw the two eyes of a normal or eaten ghost.

        Args:
            screen: Surface to draw on.
            center: Center of the ghost, in pixels.
        """
        cx, cy = center
        r = self.radius
        eye_y = cy - r // 5
        for side in (-1, 1):
            eye_x = cx + side * (r * 2 // 5)
            fill_circle(screen, r * 3 // 10, (eye_x, eye_y), GHOST_EYE_COLOR)
            fill_circle(screen, r // 7, (eye_x, eye_y), GHOST_PUPIL_COLOR)

    def _draw_frightened_face(
        self, screen: pygame.Surface, center: tuple[int, int]
    ) -> None:
        """Draw the small eyes and zigzag mouth of a frightened ghost.

        Args:
            screen: Surface to draw on.
            center: Center of the ghost, in pixels.
        """
        cx, cy = center
        r = self.radius
        eye_y = cy - r // 5
        for side in (-1, 1):
            fill_circle(
                screen,
                max(1, r // 7),
                (cx + side * (r * 2 // 5), eye_y),
                FRIGHTENED_FACE_COLOR,
            )
        # Zigzag: small squares, alternately high and low.
        step = max(1, r // 5)
        mouth_y = cy + r * 2 // 5
        x = cx - r * 3 // 5
        high = True
        while x < cx + r * 3 // 5:
            y = mouth_y - step if high else mouth_y
            fill_rect(screen, (x, y), (step, step), FRIGHTENED_FACE_COLOR)
            x += step
            high = not high
