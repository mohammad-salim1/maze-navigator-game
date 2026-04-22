from collections import deque
from pathlib import Path


def get_project_root():
    return Path(__file__).resolve().parents[1]


def load_grid(filename):
    grid = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                grid.append(list(line))
    return grid


def find_start_and_goal(grid):
    start = None
    goal = None

    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == "S":
                start = (row, col)
            elif grid[row][col] == "G":
                goal = (row, col)

    return start, goal


def is_walkable(grid, row, col):
    if row < 0 or row >= len(grid):
        return False
    if col < 0 or col >= len(grid[0]):
        return False
    return grid[row][col] != "#"


def move_player(grid, player_pos, move):
    row, col = player_pos
    new_row, new_col = row, col

    if move == "w":
        new_row -= 1
    elif move == "s":
        new_row += 1
    elif move == "a":
        new_col -= 1
    elif move == "d":
        new_col += 1

    if is_walkable(grid, new_row, new_col):
        return (new_row, new_col)

    return player_pos


def find_path(grid, start, goal):
    if start is None or goal is None:
        return []

    queue = deque([start])
    visited = {start}
    parent = {}

    while queue:
        current = queue.popleft()

        if current == goal:
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            return path

        row, col = current
        neighbors = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]

        for nr, nc in neighbors:
            if is_walkable(grid, nr, nc) and (nr, nc) not in visited:
                visited.add((nr, nc))
                parent[(nr, nc)] = current
                queue.append((nr, nc))

    return []
