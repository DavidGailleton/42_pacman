"""Tests for the collision test between two characters."""

from src.utils.collision import is_colliding


def test_same_position_collides() -> None:
    """Two characters on the same spot collide."""
    assert is_colliding((3.0, 4.0), (3.0, 4.0))


def test_distance_on_one_axis() -> None:
    """Below 0.5 cell they collide, from 0.5 cell on they do not."""
    assert is_colliding((3.0, 4.0), (3.4, 4.0))
    assert not is_colliding((3.0, 4.0), (3.5, 4.0))
    assert not is_colliding((3.0, 4.0), (4.0, 4.0))


def test_distance_on_diagonal() -> None:
    """The real distance is used, not the distance on each axis."""
    assert is_colliding((3.0, 4.0), (3.3, 4.3))
    assert not is_colliding((3.0, 4.0), (3.4, 4.4))


def test_order_does_not_matter() -> None:
    """Swapping the two positions gives the same answer."""
    assert is_colliding((3.4, 4.0), (3.0, 4.0))
    assert not is_colliding((4.0, 4.0), (3.0, 4.0))
