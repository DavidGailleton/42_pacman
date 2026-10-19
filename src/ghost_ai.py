"""Ghost behaviour shared by the four ghosts."""

from abc import ABC, abstractmethod
from enum import Enum
from src.models.config import Config

from src.constants import (
    BLINKY_COLOR,
    CLYDE_COLOR,
    DOWN,
    GHOST_FRAMES_PER_CELL,
    INKY_COLOR,
    LEFT,
    PINKY_COLOR,
    RIGHT,
    UP,
    Color,
    Direction,
)
from src.utils.bfs import bfs
from src.utils.maze import DIRECTION_TO_WALL, Maze

# A maze cell, as (x, y), same convention as ``Maze``.
Cell = tuple[int, int]

# Seconds an eaten ghost waits in its corner before coming back.
RESPAWN_DELAY: float = 5.0

# How many cells ahead of Pac-Man Pinky aims.
PINKY_LOOKAHEAD: int = 4

# How many cells ahead of Pac-Man Inky takes his pivot.
INKY_LOOKAHEAD: int = 2

# Below this distance to Pac-Man, Clyde goes back to his corner.
CLYDE_SHY_RADIUS: int = 8


class GhostState(Enum):
    """What a ghost is currently doing."""

    CHASE = "chase"
    FRIGHTENED = "frightened"
    EATEN = "eaten"


class Ghost(ABC):
    """Base class for a ghost.

    It holds what every ghost has in common: its home corner, its
    position, its state and the timers that switch between states.
    A concrete ghost only decides which cell it chases, by
    implementing ``chase_target``.

    Attributes:
        color: Body color of the ghost, set by each subclass.
        corner: Cell where the ghost starts and respawns.
        position: Last cell center the ghost reached.
        direction: Move in progress, or None when the ghost stands
            still (just spawned, or stuck in a closed cell).
        step: Frames already done from ``position`` toward the next
            cell, from 0 to ``GHOST_FRAMES_PER_CELL - 1``.
        state: Current state of the ghost.
    """

    color: Color

    def __init__(self, corner: Cell, maze: Maze, config: Config) -> None:
        """Place the ghost in its corner, in chase mode.

        Args:
            corner: Cell where the ghost starts and respawns.
            maze: Maze the ghost moves in.
        """
        self.maze: list[list[int]] = maze.get_maze()
        self.corner: Cell = corner
        self.position: Cell = corner
        self.direction: Direction | None = None
        self.step: int = 0
        self.state: GhostState = GhostState.CHASE
        self._timer: float = 0.0
        self.point = config.point_per_ghost

    @abstractmethod
    def chase_target(self, pacman: Cell, pacman_direction: Cell) -> Cell:
        """Choose the cell to move towards while chasing.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Step Pac-Man would like to take, as
                (dx, dy), e.g. (0, -1) for up.

        Returns:
            The cell the ghost wants to reach.
        """

    def reset(self) -> None:
        self.position = self.corner
        self.direction = None
        self.step = 0
        self.state = GhostState.CHASE
        self._timer = 0.0

    def target(self, pacman: Cell, pacman_direction: Cell) -> Cell:
        """Choose the cell to move towards, depending on the state.

        A frightened ghost runs back to its corner, away from
        Pac-Man. An eaten ghost does not move, so it targets its
        own position.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Step Pac-Man would like to take, as
                (dx, dy), e.g. (0, -1) for up.

        Returns:
            The cell the ghost wants to reach.
        """
        if self.state is GhostState.CHASE:
            return self.chase_target(pacman, pacman_direction)
        if self.state is GhostState.FRIGHTENED:
            return self.corner
        return self.position

    def next_step(self, pacman: Cell, pacman_direction: Cell) -> Cell:
        """Find the next cell to move to, towards the current target.

        If the target cannot be reached (e.g. a closed cell), the
        ghost aims at Pac-Man instead. If even that fails, it stays
        where it is.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Step Pac-Man would like to take, as
                (dx, dy), e.g. (0, -1) for up.

        Returns:
            A neighbour cell of the ghost, or its own position.
        """
        target = self.target(pacman, pacman_direction)
        path = bfs(self.maze, self.position, target)
        if not path:
            path = bfs(self.maze, self.position, pacman)
        # path[0] is the ghost's own cell, path[1] the next one.
        if len(path) < 2:
            return self.position
        return path[1]

    def move(self, pacman: Cell, pacman_direction: Direction) -> None:
        """Move the ghost by one frame.

        A new direction is only chosen on a cell center (``step`` 0),
        so the ghost never turns in the middle of a corridor.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Step Pac-Man would like to take, as
                (dx, dy), e.g. (0, -1) for up.
        """
        if self.state is GhostState.EATEN:
            return
        if self.step == 0:
            self.direction = self._choose_direction(pacman, pacman_direction)
        if self.direction is None:
            return
        self.step += 1
        if self.step == GHOST_FRAMES_PER_CELL:
            dx, dy = self.direction
            self.position = (self.position[0] + dx, self.position[1] + dy)
            self.step = 0

    def float_position(self) -> tuple[float, float]:
        """Compute the ghost's position in cells, as floats.

        Returns:
            The cell position plus the fraction of the way already done
            toward the next cell.
        """
        x, y = self.position
        if self.direction is None:
            return float(x), float(y)
        dx, dy = self.direction
        progress = self.step / GHOST_FRAMES_PER_CELL
        return x + dx * progress, y + dy * progress

    def _choose_direction(self, pacman: Cell,
                          pacman_direction: Direction) -> Direction | None:
        """Choose where to go from the current cell center.

        In order: the forced turn of a frightened ghost in its corner,
        then the only way out if there is just one, then the first step
        of the shortest path to the target. The way back is closed by a
        false wall, so the ghost only turns back in a dead end.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Step Pac-Man would like to take, as
                (dx, dy), e.g. (0, -1) for up.

        Returns:
            The direction to take, or None if the cell is closed.
        """
        corner_turn = self._corner_turn()
        if corner_turn is not None:
            return corner_turn

        grid = self._grid_with_wall_behind()
        exits = self._exits(grid)
        if not exits:
            # Dead end: the false wall is the only way out, remove it.
            exits = self._exits(self.maze)
        if len(exits) <= 1:
            return exits[0] if exits else None

        target = self.target(pacman, pacman_direction)
        path = bfs(grid, self.position, target)
        if len(path) < 2:
            # Already on the target, or the target is only reachable
            # through the false wall: keep going without turning back.
            return exits[0]
        # path[0] is the ghost's own cell, path[1] the next one.
        return (path[1][0] - path[0][0], path[1][1] - path[0][1])

    def _grid_with_wall_behind(self) -> list[list[int]]:
        """Copy the maze grid with a false wall behind the ghost.

        The wall is added on the side of the current cell the ghost
        came from. ``bfs`` only reads the walls of the cell it leaves,
        so this one bit is enough to forbid turning back. Only the
        current row is copied: the real maze is never modified.

        Returns:
            The grid to give to ``bfs``, or the real grid if the ghost
            has no direction yet.
        """
        if self.direction is None:
            return self.maze
        x, y = self.position
        dx, dy = self.direction
        behind = DIRECTION_TO_WALL[(-dx, -dy)]
        grid = list(self.maze)
        grid[y] = list(grid[y])
        grid[y][x] |= behind
        return grid

    def _exits(self, grid: list[list[int]]) -> list[Direction]:
        """List the directions the ghost can take from its cell.

        Args:
            grid: Maze grid to read the walls from, as ``grid[y][x]``.

        Returns:
            The directions with no wall and a cell on the other side.
        """
        x, y = self.position
        height = len(grid)
        width = len(grid[0]) if height else 0
        exits: list[Direction] = []
        for direction in (UP, RIGHT, DOWN, LEFT):
            nx, ny = x + direction[0], y + direction[1]
            if grid[y][x] & DIRECTION_TO_WALL[direction]:
                continue
            if 0 <= nx < width and 0 <= ny < height:
                exits.append(direction)
        return exits

    def _corner_turn(self) -> Direction | None:
        """Give the forced turn of a frightened ghost in its corner.

        The ghost turns toward the inside of the maze, on the other
        axis than the one it arrived on: coming from the left (moving
        right) into the top-right corner, it goes down; coming from
        the top into the bottom-left corner, it goes right. It keeps
        the ghost circling around its corner instead of stopping.

        Returns:
            The forced direction, or None if the rule does not apply
            or a wall blocks that direction.
        """
        if (self.state is not GhostState.FRIGHTENED
                or self.position != self.corner
                or self.direction is None):
            return None
        # Sign of the way toward the inside of the maze, on each axis.
        inward_x = 1 if self.corner[0] == 0 else -1
        inward_y = 1 if self.corner[1] == 0 else -1
        if self.direction[0] != 0:
            turn: Direction = (0, inward_y)
        else:
            turn = (inward_x, 0)
        if turn not in self._exits(self.maze):
            return None
        return turn

    def _clamp(self, cell: Cell) -> Cell:
        """Move a cell back inside the maze if it is outside.

        Args:
            cell: Cell to clamp, as (x, y).

        Returns:
            The closest cell that exists in the maze.
        """
        height = len(self.maze)
        width = len(self.maze[0]) if height else 0
        x = min(max(cell[0], 0), width - 1)
        y = min(max(cell[1], 0), height - 1)
        return (x, y)

    def frighten(self, duration: float) -> None:
        """Make the ghost edible for some time (super-pacgum eaten).

        An eaten ghost is not affected: it is waiting to respawn.

        Args:
            duration: Number of seconds the ghost stays edible.
        """
        if self.state is GhostState.EATEN:
            return
        self.state = GhostState.FRIGHTENED
        self._timer = duration

    def eat(self) -> int:
        """Send the ghost back to its corner after Pac-Man ate it."""
        self.state = GhostState.EATEN
        self.position = self.corner
        self.direction = None
        self.step = 0
        self._timer = RESPAWN_DELAY
        return self.point

    def update_state(self, delta: float) -> None:
        """Count down the current timer and go back to chase mode.

        Args:
            delta: Seconds elapsed since the previous frame.
        """
        if self.state is GhostState.CHASE:
            return
        self._timer -= delta
        if self._timer <= 0:
            self.state = GhostState.CHASE
            self._timer = 0.0


class Blinky(Ghost):
    """The red ghost: chases Pac-Man directly."""

    color = BLINKY_COLOR

    def chase_target(self, pacman: Cell, pacman_direction: Cell) -> Cell:
        """Aim straight at Pac-Man.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Unused, Blinky ignores where Pac-Man goes.

        Returns:
            Pac-Man's cell.
        """
        return pacman


class Pinky(Ghost):
    """The pink ghost: ambushes the cells in front of Pac-Man."""

    color = PINKY_COLOR

    def chase_target(self, pacman: Cell, pacman_direction: Cell) -> Cell:
        """Aim a few cells ahead of Pac-Man, in the way he is going.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Step Pac-Man would like to take, as
                (dx, dy), e.g. (0, -1) for up.

        Returns:
            The cell ``PINKY_LOOKAHEAD`` steps ahead of Pac-Man, kept
            inside the maze.
        """
        dx, dy = pacman_direction
        ahead = (
            pacman[0] + PINKY_LOOKAHEAD * dx,
            pacman[1] + PINKY_LOOKAHEAD * dy,
        )
        return self._clamp(ahead)


class Inky(Ghost):
    """The cyan ghost: uses Blinky's position to flank Pac-Man.

    Attributes:
        blinky: The Blinky ghost Inky works with.
    """

    color = INKY_COLOR

    def __init__(self, corner: Cell, maze: Maze, blinky: Blinky,
                 config: Config) -> None:
        """Place Inky in its corner and remember Blinky.

        Args:
            corner: Cell where the ghost starts and respawns.
            maze: Maze the ghost moves in.
            blinky: The Blinky ghost used to compute the target.
        """
        super().__init__(corner, maze, config)
        self.blinky: Blinky = blinky

    def chase_target(self, pacman: Cell, pacman_direction: Cell) -> Cell:
        """Aim at the point symmetric to Blinky around Pac-Man's front.

        Take the pivot cell ``INKY_LOOKAHEAD`` steps ahead of
        Pac-Man, then double the vector from Blinky to that pivot.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Step Pac-Man would like to take, as
                (dx, dy), e.g. (0, -1) for up.

        Returns:
            The flanking cell, kept inside the maze.
        """
        dx, dy = pacman_direction
        pivot_x = pacman[0] + INKY_LOOKAHEAD * dx
        pivot_y = pacman[1] + INKY_LOOKAHEAD * dy
        blinky_x, blinky_y = self.blinky.position
        target = (2 * pivot_x - blinky_x, 2 * pivot_y - blinky_y)
        return self._clamp(target)


class Clyde(Ghost):
    """The orange ghost: chases Pac-Man but flees when too close."""

    color = CLYDE_COLOR

    def chase_target(self, pacman: Cell, pacman_direction: Cell) -> Cell:
        """Chase Pac-Man from afar, go back to the corner when near.

        Args:
            pacman: Cell where Pac-Man currently is.
            pacman_direction: Unused, Clyde ignores where Pac-Man goes.

        Returns:
            Pac-Man's cell if Clyde is far enough, else his corner.
        """
        dx = pacman[0] - self.position[0]
        dy = pacman[1] - self.position[1]
        if dx * dx + dy * dy < CLYDE_SHY_RADIUS * CLYDE_SHY_RADIUS:
            return self.corner
        return pacman
