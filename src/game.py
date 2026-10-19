"""Pygame window and main game object."""

import os

import pygame
from src.constants import (
    DOWN,
    EAT_FREEZE_TIME,
    FPS,
    LEFT,
    PACMAN_FRAMES_PER_CELL,
    RIGHT,
    UP,
    Direction,
)
from src.ghost_ai import Blinky, Clyde, Ghost, GhostState, Inky, Pinky
from src.renderer.ghost_renderer import GhostRenderer
from src.renderer.maze_renderer import MazeRenderer
from src.renderer.pacman_renderer import PacmanRenderer
from src.utils.collision import is_colliding
from src.utils.maze import Maze
from src.models.config import Config
from src.renderer.pacgum_renderer import PacgumRenderer
from src.models.pacgum import Pacgum
from src.renderer.hud_renderer import HudRenderer

# SDL tries to create an OpenGL (GLX) context to accelerate the window
# surface. On some machines (broken/missing GL drivers, remote X) this
# triggers a fatal X11 error that kills the process before Python can
# catch it. Forcing the plain software framebuffer avoids GLX entirely.
# Must be set before pygame initialises the display.
os.environ.setdefault("SDL_FRAMEBUFFER_ACCELERATION", "0")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


WIDTH_SIZE = 1920
HEIGHT_SIZE = 1080

# Seconds the ghosts stay edible after a super-pacgum is eaten.
FRIGHTEN_TIME: float = 7.0

# Keys that move Pac-Man: arrows and WASD.
KEY_TO_DIRECTION: dict[int, Direction] = {
    pygame.K_UP: UP,
    pygame.K_w: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d: RIGHT,
}


class Game:
    """Own the pygame window, the clock and Pac-Man's movement.

    Pac-Man's position is stored as the last cell center reached
    (``pacman_cell``) plus the number of frames already done toward the
    next cell (``pacman_step``). Storing whole steps instead of a float
    avoids rounding drift: after ``PACMAN_FRAMES_PER_CELL`` frames
    Pac-Man is exactly on the next cell center.
    """

    def __init__(self, config: Config) -> None:
        """Initialise pygame, open the game window and place Pac-Man."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH_SIZE, HEIGHT_SIZE))
        self.clock = pygame.time.Clock()
        self.running = False
        self.score = 0
        self.maze = Maze(config=config)
        self.pacgum = Pacgum(self.maze, config)
        self.maze_renderer = MazeRenderer(self.maze, self.screen.get_size())
        self.pacman_renderer = PacmanRenderer(
            self.maze, self.screen.get_size()
        )
        self.ghost_renderer = GhostRenderer(self.maze, self.screen.get_size())
        self.ghosts: list[Ghost] = self._make_ghosts(config)

        self.pacgum_renderer = PacgumRenderer(self.pacgum,
                                              self.screen.get_size(),
                                              self.maze)
        self.hud_renderer = HudRenderer(self.maze, self.screen.get_size())

        self.pacman_cell: tuple[int, int] = self._find_start_cell()
        self.pacman_step: int = 0
        # Move being done, and move waiting until it becomes possible.
        self.current_move: Direction | None = None
        self.next_move: Direction | None = None
        # Direction drawn, kept when Pac-Man stops.
        self.pacman_facing: Direction = RIGHT

        # A chasing ghost caught Pac-Man: nothing moves anymore.
        self.game_over: bool = False
        # Seconds of freeze left after Pac-Man ate a ghost, and that
        # ghost, sent to its corner when the freeze ends.
        self.freeze_timer: float = 0.0
        self.eaten_ghost: Ghost | None = None

    def __del__(self) -> None:
        """Shut pygame down when the game object is destroyed."""
        pygame.quit()

    def run(self) -> None:
        """Run the main loop until the window is closed."""
        self.running = True
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)
            self._update(dt)
            self._draw()

    def _update(self, dt: float) -> None:
        """Advance the game by one frame.

        Nothing moves after a game over, nor during the short freeze
        that follows eating a ghost.

        Args:
            dt: Seconds since the last frame.
        """
        if self.game_over:
            return
        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0 and self.eaten_ghost is not None:
                self.score += self.eaten_ghost.eat()
                self.eaten_ghost = None
            return
        self._update_pacman()
        for ghost in self.ghosts:
            ghost.update_state(dt)
            ghost.move(self.pacman_cell, self.pacman_facing)
        if self.current_move is not None:
            self.pacman_renderer.update(dt)
        self.ghost_renderer.update(dt)
        self._handle_collisions()
        self._eat_pacgum()

    def _draw(self) -> None:
        """Draw the maze, pacgums, Pac-Man and ghosts, then show it."""
        self.maze_renderer.draw(self.screen)
        self.hud_renderer.draw(screen=self.screen, lives=3, score=self.score,
                               time_left=0, lvl=0)
        self.pacgum_renderer.draw(self.screen)
        self.pacman_renderer.draw(
            self.screen, self._pacman_position(), self.pacman_facing
        )
        for ghost in self.ghosts:
            self.ghost_renderer.draw(
                self.screen,
                ghost.float_position(),
                ghost.color,
                ghost.state,
            )
        pygame.display.flip()

    def _handle_collisions(self) -> None:
        """React to Pac-Man touching ghosts.

        A chasing ghost ends the game. A frightened ghost is eaten: the
        game freezes a moment, then the ghost goes to its corner. Eaten
        ghosts are ignored (see ``_colliding_ghosts``).
        """
        ghosts = self._colliding_ghosts()
        # Chasers first: touching one loses, even if a frightened
        # ghost is touched on the same frame.
        if any(ghost.state is GhostState.CHASE for ghost in ghosts):
            self.game_over = True
            return
        for ghost in ghosts:
            if ghost.state is GhostState.FRIGHTENED:
                # One ghost per freeze: another one still touching is
                # caught on the frame after this freeze ends.
                self.eaten_ghost = ghost
                self.freeze_timer = EAT_FREEZE_TIME
                return

    def _make_ghosts(self, config: Config) -> list[Ghost]:
        """Place one ghost in each corner of the maze.

        Returns:
            The four ghosts.
        """
        width, height = self.maze.get_shape()
        blinky = Blinky((0, 0), self.maze, config)
        pinky = Pinky((width - 1, 0), self.maze, config)
        inky = Inky((0, height - 1), self.maze, blinky, config)
        clyde = Clyde((width - 1, height - 1), self.maze, config)
        return [blinky, pinky, inky, clyde]

    def _colliding_ghosts(self) -> list[Ghost]:
        """List the ghosts Pac-Man is touching.

        Eaten ghosts are skipped: they only wait in their corner.

        Returns:
            The ghosts colliding with Pac-Man, maybe none.
        """
        pacman = self._pacman_position()
        return [
            ghost
            for ghost in self.ghosts
            if ghost.state is not GhostState.EATEN
            and is_colliding(pacman, ghost.float_position())
        ]

    def _eat_pacgum(self) -> None:
        superman, point = self.pacgum.eat(self.pacman_cell)
        self.score += point
        if superman:
            for ghost in self.ghosts:
                ghost.frighten(FRIGHTEN_TIME)
        if self.pacgum.is_empty():
            pass

    def _find_start_cell(self) -> tuple[int, int]:
        """Find the cell closest to the maze center that can be entered.

        The center may be a closed cell (four walls, e.g. in the "42"
        pattern). Cells are sorted by Manhattan distance to the center
        and the first one that is not closed is used.

        Returns:
            The start cell (x, y), or (0, 0) if every cell is closed.
        """
        width, height = self.maze.get_shape()
        center_x, center_y = width // 2, height // 2
        cells = [(x, y) for y in range(height) for x in range(width)]
        cells.sort(
            key=lambda cell: abs(cell[0] - center_x) + abs(cell[1] - center_y)
        )
        for cell in cells:
            if not self.maze.is_closed(cell):
                return cell
        return (0, 0)

    def _handle_key(self, key: int) -> None:
        """Remember the move asked by a key press.

        The move replaces any move already in memory. It is applied by
        ``_update_pacman`` as soon as it is possible.

        Args:
            key: Pygame key code of the pressed key.
        """
        if key in KEY_TO_DIRECTION:
            self.next_move = KEY_TO_DIRECTION[key]

    def _update_pacman(self) -> None:
        """Move Pac-Man by one frame."""
        # Turning back is always possible, even between two cells:
        # restart from the cell we were heading to.
        if (
            self.current_move is not None
            and self.next_move is not None
            and self._is_opposite(self.current_move, self.next_move)
            and self.pacman_step > 0
        ):
            self.pacman_cell = self._neighbour(
                self.pacman_cell, self.current_move
            )
            self.pacman_step = PACMAN_FRAMES_PER_CELL - self.pacman_step
            self.current_move = self.next_move
            self.next_move = None

        if self.pacman_step == 0:
            # On a cell center: the only place where a turn can happen.
            if self.next_move is not None and self.maze.can_move(
                self.pacman_cell, self.next_move
            ):
                self.current_move = self.next_move
                self.next_move = None
            if self.current_move is not None and not self.maze.can_move(
                self.pacman_cell, self.current_move
            ):
                # Wall ahead and nothing usable in memory: stop.
                self.current_move = None

        if self.current_move is None:
            return
        self.pacman_facing = self.current_move
        self.pacman_step += 1
        if self.pacman_step == PACMAN_FRAMES_PER_CELL:
            self.pacman_cell = self._neighbour(
                self.pacman_cell, self.current_move
            )
            self.pacman_step = 0

    def _pacman_position(self) -> tuple[float, float]:
        """Compute Pac-Man's position in cells, as floats.

        Returns:
            The cell position plus the fraction of the way already done
            toward the next cell.
        """
        x, y = self.pacman_cell
        if self.current_move is None:
            return float(x), float(y)
        dx, dy = self.current_move
        progress = self.pacman_step / PACMAN_FRAMES_PER_CELL
        return x + dx * progress, y + dy * progress

    @staticmethod
    def _neighbour(
        cell: tuple[int, int], direction: Direction
    ) -> tuple[int, int]:
        """Return the cell next to ``cell`` in ``direction``.

        Args:
            cell: Starting cell (x, y).
            direction: Move, as (dx, dy).

        Returns:
            The neighbouring cell (x, y).
        """
        return cell[0] + direction[0], cell[1] + direction[1]

    @staticmethod
    def _is_opposite(first: Direction, second: Direction) -> bool:
        """Tell if two directions are opposite (e.g. LEFT and RIGHT).

        Args:
            first: A direction, as (dx, dy).
            second: Another direction, as (dx, dy).

        Returns:
            True if ``second`` goes back the way ``first`` goes.
        """
        return first[0] == -second[0] and first[1] == -second[1]
