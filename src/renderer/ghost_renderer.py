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
        self.cell_size, self.offset = compute_layout(maze.get_shape(),
                                                     self.screen_size)
        self.radius = int(self.cell_size * GHOST_RADIUS_RATIO)

    def update(self, dt: float) -> None:
        """Advance the skirt animation.

        Args:
            dt: Seconds since the last frame.
        """
        self._phase = (self._phase + dt * GHOST_SKIRT_SPEED) % 1.0

    def draw(self, screen: pygame.Surface, position: tuple[float, float],
             color: Color, state: GhostState) -> None:
        """Draw one ghost on the screen.

        Args:
            screen: Surface to draw on.
            position: Position in cells, as floats (x, y).
            color: Body color of the ghost (``Ghost.color``).
            state: Current state, which picks the look of the ghost.
        """
        center = to_pixel(position, self.cell_size, self.offset)
        if state is GhostState.FRIGHTENED:
            self._fill_body(screen, center, FRIGHTENED_COLOR, 1.0)
            self._draw_frightened_face(screen, center)
        elif state is GhostState.EATEN:
            self._fill_body(screen, center, color, GHOST_EATEN_ALPHA)
            self._draw_eyes(screen, center)
        else:
            self._fill_body(screen, center, color, 1.0)
            self._draw_eyes(screen, center)

    def _is_in_body(self, dx: int, dy: int) -> bool:
        """Tell if a pixel, relative to the center, is in the body.

        The body is a half disc on top of a square, whose bottom rows
        are cut into ``SKIRT_BUMPS`` triangular bumps (the skirt).

        Args:
            dx: Horizontal distance to the center, in pixels.
            dy: Vertical distance to the center, in pixels (down > 0).

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
        shift = period // 2 if self._phase >= 0.5 else 0
        u = (dx + r + shift) % period
        # 0 at a bump's tip, 1 between two bumps.
        notch = abs(2 * u / period - 1)
        return depth >= skirt_height * notch

    def _fill_body(self, screen: pygame.Surface, center: tuple[int, int],
                   color: Color, alpha: float) -> None:
        """Fill the ghost's body pixel by pixel.

        With ``alpha`` below 1, each pixel is mixed with the pixel
        already on the screen, which makes the body see-through.

        Args:
            screen: Surface to draw on.
            center: Center of the ghost, in pixels.
            color: Body color.
            alpha: Opacity of the body, from 0 (invisible) to 1.
        """
        cx, cy = center
        r = self.radius
        bounds = screen.get_rect()
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if not self._is_in_body(dx, dy):
                    continue
                pixel = (cx + dx, cy + dy)
                # get_at raises outside the surface: never go there.
                if not bounds.collidepoint(pixel):
                    continue
                if alpha >= 1.0:
                    screen.set_at(pixel, color)
                else:
                    under = screen.get_at(pixel)
                    screen.set_at(pixel, _blend(under, color, alpha))

    def _draw_eyes(self, screen: pygame.Surface,
                   center: tuple[int, int]) -> None:
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

    def _draw_frightened_face(self, screen: pygame.Surface,
                              center: tuple[int, int]) -> None:
        """Draw the small eyes and zigzag mouth of a frightened ghost.

        Args:
            screen: Surface to draw on.
            center: Center of the ghost, in pixels.
        """
        cx, cy = center
        r = self.radius
        eye_y = cy - r // 5
        for side in (-1, 1):
            fill_circle(screen, max(1, r // 7),
                        (cx + side * (r * 2 // 5), eye_y),
                        FRIGHTENED_FACE_COLOR)
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


def _blend(under: pygame.Color, over: Color, alpha: float) -> Color:
    """Mix a color over another one, as if it were see-through.

    Args:
        under: Color already on the screen.
        over: Color drawn on top.
        alpha: Opacity of ``over``, from 0 (invisible) to 1.

    Returns:
        The mixed RGB color.
    """
    return (
        int(under.r * (1 - alpha) + over[0] * alpha),
        int(under.g * (1 - alpha) + over[1] * alpha),
        int(under.b * (1 - alpha) + over[2] * alpha),
    )
