

class Maze:
    def __init__(self, maze: list[list[int]]) -> None:
        self.maze: list[list[int]] = maze

    def get_walls(self, coord: tuple[int]) -> tuple[int]:
        res_str = bin(self.maze[coord[0]][coord[1]])[2:]
        res = [c for c in res_str]
        print(res)
