"""Main entry point for the project."""
from mazegenerator import MazeGenerator
from utils import Maze


def greet(name: str) -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A formatted greeting string.
    """
    return f"Hello, {name}!"


def main() -> int:
    """Run the main program.

    Returns:
        Exit status code.
    """
    maze = MazeGenerator()
    maze.generate()
    cells = Maze(maze.maze)
    cells.get_walls((0, 0))


if __name__ == "__main__":
    raise SystemExit(main())
