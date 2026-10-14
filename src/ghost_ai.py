"""Ghost behaviour shared by the four ghosts."""

from abc import ABC, abstractmethod
from enum import Enum

from src.utils.bfs import bfs
from src.utils.maze import Maze

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
        corner: Cell where the ghost starts and respawns.
        position: Cell where the ghost currently is.
        state: Current state of the ghost.
    """

    def __init__(self, corner: Cell, maze: Maze) -> None:
        """Place the ghost in its corner, in chase mode.

        Args:
            corner: Cell where the ghost starts and respawns.
            maze: Maze the ghost moves in.
        """
        self.maze: list[list[int]] = maze.get_maze()
        self.corner: Cell = corner
        self.position: Cell = corner
        self.state: GhostState = GhostState.CHASE
        self._timer: float = 0.0

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

    def eat(self) -> None:
        """Send the ghost back to its corner after Pac-Man ate it."""
        self.state = GhostState.EATEN
        self.position = self.corner
        self._timer = RESPAWN_DELAY

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

    def __init__(self, corner: Cell, maze: Maze, blinky: Blinky) -> None:
        """Place Inky in its corner and remember Blinky.

        Args:
            corner: Cell where the ghost starts and respawns.
            maze: Maze the ghost moves in.
            blinky: The Blinky ghost used to compute the target.
        """
        super().__init__(corner, maze)
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
