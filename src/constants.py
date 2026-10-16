"""Constants shared by the maze, the renderers and the game logic."""

# An RGB color.
Color = tuple[int, int, int]

# A unit move in the maze, as (dx, dy). y grows downwards.
Direction = tuple[int, int]

# Wall bits of a maze cell, as produced by the A-Maze-ing generator.
NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

# Directions, same (x, y) convention as the maze cells.
UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)

# Part of the screen (width and height) the maze may use.
MAZE_SCREEN_RATIO: float = 0.8

BLACK_COLOR: Color = (0, 0, 0)
MAZE_COLOR: Color = (33, 33, 222)
PACMAN_COLOR: Color = (255, 255, 0)

# Pac-Man radius, as a fraction of a cell size.
PACMAN_RADIUS_RATIO: float = 0.4

# Half-angle of the mouth when fully open, in degrees.
PACMAN_MOUTH_MAX_ANGLE: float = 45.0

# Mouth open/close cycles per second.
PACMAN_MOUTH_SPEED: float = 3.0

# Frames per second the game loop is locked to.
FPS: int = 60

# Frames Pac-Man needs to go from one cell center to the next.
# At 60 FPS, 10 frames per cell = 6 cells per second.
PACMAN_FRAMES_PER_CELL: int = 10
