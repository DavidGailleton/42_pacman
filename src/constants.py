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
WHITE_COLOR: Color = (255, 255, 255)

# Body color of each ghost, in chase mode.
BLINKY_COLOR: Color = (255, 0, 0)
PINKY_COLOR: Color = (255, 184, 255)
INKY_COLOR: Color = (0, 255, 255)
CLYDE_COLOR: Color = (255, 184, 82)

# Body and face colors of a frightened (edible) ghost.
FRIGHTENED_COLOR: Color = (33, 33, 255)
FRIGHTENED_FACE_COLOR: Color = (255, 184, 174)

GHOST_EYE_COLOR: Color = (255, 255, 255)
GHOST_PUPIL_COLOR: Color = (33, 33, 222)

# Pac-Man radius, as a fraction of a cell size.
PACMAN_RADIUS_RATIO: float = 0.3

# Half-angle of the mouth when fully open, in degrees.
PACMAN_MOUTH_MAX_ANGLE: float = 45.0

# Mouth open/close cycles per second.
PACMAN_MOUTH_SPEED: float = 3.0

# Ghost radius, as a fraction of a cell size.
GHOST_RADIUS_RATIO: float = 0.3

# Opacity of an eaten ghost's body: 0 = invisible, 1 = opaque.
GHOST_EATEN_ALPHA: float = 0.35

# Skirt wiggle cycles per second.
GHOST_SKIRT_SPEED: float = 4.0

# Frames per second the game loop is locked to.
FPS: int = 60

# Frames Pac-Man needs to go from one cell center to the next.
# At 60 FPS, 10 frames per cell = 6 cells per second.
PACMAN_FRAMES_PER_CELL: int = 10

# Frames a ghost needs to go from one cell center to the next.
# A bit slower than Pac-Man, so he can escape.
GHOST_FRAMES_PER_CELL: int = 12

# Pac-Man and a ghost collide when their centers are closer than this,
# in cells. Both radii are 0.4 cell, so they touch at 0.8: 0.5 waits
# until they visibly overlap, which is fairer for the player.
COLLISION_DISTANCE: float = 0.5

# Seconds the game freezes when Pac-Man eats a ghost.
EAT_FREEZE_TIME: float = 0.2

# Const hud
HUD_MARGIN: int = 20

# SIZE SCREEN
WIDTH_SIZE = 1920
HEIGHT_SIZE = 1080
