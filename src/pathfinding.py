from collections import deque
from pathlib import Path


def get_project_root():
    """Return the root directory of the project."""
    return Path(__file__).resolve().parents[1]


def load_grid(filename):
    """
    Load a maze grid from a text file.
    Each line becomes a list of characters.
    Returns a 2D list (list of lists of str).
    """
    grid = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                grid.append(list(line))
    return grid


def find_start_and_goal(grid):
    """
    Scan the grid and return the positions of S (start) and G (goal).
    Returns a tuple (start, goal) where each is a (row, col) tuple, or None if missing.
    """
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
    """
    Return True if (row, col) is inside the grid and not a wall (#).
    """
    if row < 0 or row >= len(grid):
        return False
    if col < 0 or col >= len(grid[0]):
        return False
    return grid[row][col] != "#"


def move_player(grid, player_pos, move):
    """
    Attempt to move the player in the given direction (w/a/s/d).
    Returns the new position if the move is valid, otherwise returns the original position.
    """
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
    """
    Find the shortest path from start to goal using Breadth-First Search (BFS).

    grid:  2D list of characters
    start: (row, col) tuple
    goal:  (row, col) tuple

    Returns an ordered list of (row, col) positions from start to goal (inclusive),
    or an empty list if no path exists.

    BFS guarantees the shortest path on an unweighted grid (all steps cost 1).
    """
    if start is None or goal is None:
        return []

    # Queue holds cells to explore next
    queue = deque([start])
    visited = {start}
    # parent maps each cell to the cell it was reached from
    parent = {}

    while queue:
        current = queue.popleft()

        # Goal reached — reconstruct path by tracing parent links
        if current == goal:
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            return path

        row, col = current
        # Explore 4-connected neighbours (up, down, left, right)
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

    # No path found
    return []
