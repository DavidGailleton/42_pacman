"""Ghost behaviour shared by the four ghosts."""

from abc import ABC, abstractmethod
from enum import Enum

# A maze cell, as (x, y), same convention as ``Maze``.
Cell = tuple[int, int]

# Seconds an eaten ghost waits in its corner before coming back.
RESPAWN_DELAY: float = 5.0


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

    def __init__(self, corner: Cell) -> None:
        """Place the ghost in its corner, in chase mode.

        Args:
            corner: Cell where the ghost starts and respawns.
        """
        self.corner: Cell = corner
        self.position: Cell = corner
        self.state: GhostState = GhostState.CHASE
        self._timer: float = 0.0

    @abstractmethod
    def chase_target(self, pacman: Cell) -> Cell:
        """Choose the cell to move towards while chasing.

        Args:
            pacman: Cell where Pac-Man currently is.

        Returns:
            The cell the ghost wants to reach.
        """

    def target(self, pacman: Cell) -> Cell:
        """Choose the cell to move towards, depending on the state.

        A frightened ghost runs back to its corner, away from
        Pac-Man. An eaten ghost does not move, so it targets its
        own position.

        Args:
            pacman: Cell where Pac-Man currently is.

        Returns:
            The cell the ghost wants to reach.
        """
        if self.state is GhostState.CHASE:
            return self.chase_target(pacman)
        if self.state is GhostState.FRIGHTENED:
            return self.corner
        return self.position

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
    def __init__(self, corner: Cell) -> None:
        super().__init__(corner)


class Inky(Ghost):
    def __init__(self, corner: Cell) -> None:
        super().__init__(corner)


class Pinky(Ghost):
    def __init__(self, corner: Cell) -> None:
        super().__init__(corner)


class Clyde(Ghost):
    def __init__(self, corner: Cell) -> None:
        super().__init__(corner)
