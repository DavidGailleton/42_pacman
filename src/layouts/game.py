from src.layouts.layout import Layout
from src.models.config import Config
from src.utils.maze import Maze
from src.models.pacgum import Pacgum
from src.ghost_ai import Blinky, Clyde, Ghost, GhostState, Inky, Pinky
from src.utils.collision import is_colliding
from src.renderer.maze_renderer import MazeRenderer
from src.renderer.pacman_renderer import PacmanRenderer
from src.renderer.pacgum_renderer import PacgumRenderer
from src.renderer.hud_renderer import HudRenderer
from src.renderer.ghost_renderer import GhostRenderer
from src.layouts.pause_menu import PauseMenu
from src.layouts.end_screen import EndScreen
import pygame
from src.constants import (
    DOWN,
    EAT_FREEZE_TIME,
    LEFT,
    PACMAN_FRAMES_PER_CELL,
    RIGHT,
    UP,
    FRIGHTEN_TIME,
    Direction,
)

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


class Game(Layout):
    """Game screen: maze, Pac-Man, ghosts, pacgums and HUD.

    Keeps the score, lives and level for the whole game and loads a new
    maze for each level.
    """
    def __init__(self, config: Config, screen_size: tuple[int, int]) -> None:
        """Start a new game on the first level.

        Args:
            config: Game configuration (levels, lives, points, timer).
            screen_size: Screen size in pixels, as (width, height).
        """
        # Kept for the whole game: never reset between levels.
        self.config = config
        self.screen_size = screen_size
        self.score = 0
        self.lives = config.lives
        self.level = 1
        self.game_over: bool = False
        self.won: bool = False
        self.cheat_mode: bool = False
        self._load_level()

    def _load_level(self) -> None:
        """Build a new maze and put everything at its start position.

        Level n uses the size of the n-th entry of ``levels``. Level 1
        uses the config seed (always the same maze), the next levels use
        seed 0 so the generator gives a random maze every game.
        Score and lives are not touched: they carry over.
        """
        config = self.config
        level = config.levels[self.level - 1]
        self.time_left: float = config.level_max_time
        self.maze = Maze(
            shape=(level.width, level.height),
            seed=config.seed if self.level == 1 else 0,
        )
        self.pacgum = Pacgum(maze=self.maze, config=config)
        self.maze_renderer = MazeRenderer(
            maze=self.maze, screen_size=self.screen_size
        )
        self.pacgum_renderer = PacgumRenderer(
            pacgum=self.pacgum, screen_size=self.screen_size, maze=self.maze
        )
        self.pacman_renderer = PacmanRenderer(
            maze=self.maze, screen_size=self.screen_size
        )
        self.ghost_renderer = GhostRenderer(
            maze=self.maze, screen_size=self.screen_size
        )
        self.hud_renderer = HudRenderer(
            maze=self.maze, screen_size=self.screen_size
        )
        self.ghosts: list[Ghost] = self._make_ghosts(config=config)
        self.pacman_cell: tuple[int, int] = self._find_start_cell()
        self.pacman_step = 0
        self.current_move: Direction | None = None
        self.next_move: Direction | None = None
        self.pacman_facing: Direction = RIGHT
        self.freeze_timer: float = 0.0
        self.eaten_ghost: Ghost | None = None

    def _next_level(self) -> None:
        """Go to the next level, or win the game after the last one."""
        if self.level >= len(self.config.levels):
            self.won = True
            return
        self.level += 1
        self._load_level()

    def handle_event(self, event: pygame.event.Event) -> Layout | None:
        """React to a key press.

        Esc opens the pause menu, C toggles the cheat mode, N skips the
        level when the cheat mode is on, and the other keys move Pac-Man.

        Args:
            event: Pygame event to react to.

        Returns:
            The pause menu on Esc, else this game.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return PauseMenu(game=self)
            if event.key == pygame.K_c:
                self.cheat_mode = not self.cheat_mode
                return self
            if event.key == pygame.K_n:
                if self.cheat_mode:
                    self._next_level()
                return self

            self._handle_key(event.key)
        return self

    def update(self, dt: float) -> Layout | None:
        """Advance the game by one frame.

        Args:
            dt: Seconds since the last frame.

        Returns:
            The end screen once the game is over, else this game.
        """
        tmp = self._update(dt)
        if tmp is not None:
            return tmp
        return self

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the maze, the pacgums, Pac-Man, the ghosts and the HUD.

        Args:
            screen: Surface to draw on.
        """
        self.maze_renderer.draw(screen=screen)
        self.pacgum_renderer.draw(screen=screen)
        self.pacman_renderer.draw(
            screen=screen,
            position=self._pacman_position(),
            direction=self.pacman_facing,
        )
        for ghost in self.ghosts:
            self.ghost_renderer.draw(
                screen=screen,
                position=ghost.float_position(),
                color=ghost.color,
                state=ghost.state,
            )
        self.hud_renderer.draw(
            screen=screen,
            lives=self.lives,
            score=self.score,
            time_left=self.time_left,
            lvl=self.level,
            cheat_mode=self.cheat_mode,
        )

    def _update(self, dt: float) -> Layout | None:
        """Advance the game by one frame.

        Nothing moves after a game over, nor during the short freeze
        that follows eating a ghost.

        Args:
            dt: Seconds since the last frame.

        Returns:
            The end screen once the game is lost or won, else None.
        """
        if self.game_over or self.won:
            return EndScreen(
                config=self.config,
                screen_size=self.screen_size,
                score=self.score,
                win=self.won,
            )
        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0 and self.eaten_ghost is not None:
                self.score += self.eaten_ghost.eat()
                self.eaten_ghost = None
            return None
        if self._handle_time_left(dt):
            # New level just loaded: start moving on the next frame.
            return None
        self._update_pacman()
        for ghost in self.ghosts:
            ghost.update_state(dt)
            ghost.move(self.pacman_cell, self.pacman_facing)
        if self.current_move is not None:
            self.pacman_renderer.update(dt)
        self.ghost_renderer.update(dt)
        self._handle_collisions()
        self._eat_pacgum()
        return None

    def _handle_key(self, key: int) -> None:
        """Remember the move asked by a key press.

        The move replaces any move already in memory. It is applied by
        ``_update_pacman`` as soon as it is possible.

        Args:
            key: Pygame key code of the pressed key.
        """
        if key in KEY_TO_DIRECTION:
            self.next_move = KEY_TO_DIRECTION[key]

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

    def _handle_time_left(self, dt: float) -> bool:
        """Count down the level timer.

        Surviving until the end of the timer wins the level.

        Args:
            dt: Seconds since the last frame.

        Returns:
            True if the time is up (the level is won).
        """
        self.time_left -= dt
        if self.time_left > 0:
            return False
        self._next_level()
        return True

    def _handle_collisions(self) -> None:
        """React to Pac-Man touching ghosts.

        A chasing ghost ends the game. A frightened ghost is eaten: the
        game freezes a moment, then the ghost goes to its corner. Eaten
        ghosts are ignored (see ``_colliding_ghosts``).
        """
        ghosts = self._colliding_ghosts()
        # Chasers first: touching one loses, even if a frightened
        # ghost is touched on the same frame.
        if any(
            ghost.state is GhostState.CHASE and not self.cheat_mode
            for ghost in ghosts
        ):
            self._lose_life()
            return
        for ghost in ghosts:
            if ghost.state is GhostState.FRIGHTENED:
                # One ghost per freeze: another one still touching is
                # caught on the frame after this freeze ends.
                self.eaten_ghost = ghost
                self.freeze_timer = EAT_FREEZE_TIME
                return

    def _lose_life(self) -> None:
        """Remove a life after a ghost caught Pac-Man.

        With no life left the game is over. Otherwise everyone goes back to
        the start position and the game freezes a moment.
        """
        self.lives -= 1
        if self.lives == 0:
            self.game_over = True
            return
        self._reset_position()
        self.freeze_timer = EAT_FREEZE_TIME

    def _reset_position(self) -> None:
        """Put Pac-Man back at the start cell and the ghosts in their corners.

        The pacgums, the score and the timer are kept.
        """
        self.pacman_cell = self._find_start_cell()
        self.pacman_step = 0
        self.current_move = None
        self.next_move = None
        self.pacman_facing = RIGHT
        self.eaten_ghost = None
        for ghost in self.ghosts:
            ghost.reset()

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
        """Eat the pacgum under Pac-Man, if any.

        Eating the last pacgum wins the level.
        """
        superman, point = self.pacgum.eat(self.pacman_cell)
        self.score += point
        if superman:
            for ghost in self.ghosts:
                ghost.frighten(FRIGHTEN_TIME)
        if self.pacgum.is_empty():
            self._next_level()

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
