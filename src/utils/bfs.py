"""Shortest path search in the maze grid."""

from collections import deque

from src.constants import EAST, NORTH, SOUTH, WEST

# A maze cell, as (x, y), same convention as ``Maze``.
Cell = tuple[int, int]

# For each wall bit, the (dx, dy) step it blocks.
DIRECTIONS: dict[int, Cell] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}


def _in_grid(grid: list[list[int]], cell: Cell) -> bool:
    """Tell whether a cell is inside the grid.

    Args:
        grid: Maze grid, indexed as ``grid[y][x]``.
        cell: Cell to check, as (x, y).

    Returns:
        True if the cell exists in the grid.
    """
    x, y = cell
    return 0 <= y < len(grid) and 0 <= x < len(grid[y])


def bfs(grid: list[list[int]], start: Cell, goal: Cell) -> list[Cell]:
    """Find the shortest path between two cells of the maze.

    Each value of the grid is a bitmask of the walls around the cell
    (NORTH, EAST, SOUTH, WEST). A move is allowed when the current
    cell has no wall on that side.

    Args:
        grid: Maze grid, indexed as ``grid[y][x]``.
        start: Cell where the path starts, as (x, y).
        goal: Cell where the path ends, as (x, y).

    Returns:
        The cells from ``start`` to ``goal``, both included. An empty
        list if a cell is outside the grid or the goal is unreachable.
    """
    if not _in_grid(grid, start) or not _in_grid(grid, goal):
        return []

    # parent[cell] is the cell we came from; it also marks visited cells.
    parent: dict[Cell, Cell | None] = {start: None}
    queue: deque[Cell] = deque([start])

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        x, y = current
        for wall, (dx, dy) in DIRECTIONS.items():
            neighbour = (x + dx, y + dy)
            if grid[y][x] & wall or neighbour in parent:
                continue
            if not _in_grid(grid, neighbour):
                continue
            parent[neighbour] = current
            queue.append(neighbour)

    if goal not in parent:
        return []

    # Walk back from the goal to the start, then reverse.
    path: list[Cell] = []
    step: Cell | None = goal
    while step is not None:
        path.append(step)
        step = parent[step]
    path.reverse()
    return path
