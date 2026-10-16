"""Collision test between two characters of the maze."""

from src.constants import COLLISION_DISTANCE


def is_colliding(first: tuple[float, float],
                 second: tuple[float, float]) -> bool:
    """Tell if two characters are close enough to collide.

    Positions are in cells, as floats, like ``Ghost.float_position``.
    Distances are compared squared: same result as with a square root,
    without computing it.

    Args:
        first: Position (x, y) of the first character.
        second: Position (x, y) of the second character.

    Returns:
        True if their centers are closer than ``COLLISION_DISTANCE``.
    """
    dx = first[0] - second[0]
    dy = first[1] - second[1]
    return dx * dx + dy * dy < COLLISION_DISTANCE * COLLISION_DISTANCE
