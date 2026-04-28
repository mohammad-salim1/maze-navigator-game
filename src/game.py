"""
game.py
-------
Contains the GameState class, which is the single source of truth for the
maze game.  All mutation of game data (player position, path, win condition)
goes through this class.  Neither main.py nor gui.py should duplicate this
logic.
"""

from pathlib import Path
from pathfinding import load_grid, find_start_and_goal, move_player, find_path, is_walkable


# Mapping from direction keys to human-readable names used in status messages
DIRECTION_NAMES = {
    "w": "up",
    "s": "down",
    "a": "left",
    "d": "right",
}


class GameState:
    """
    Holds all mutable state for one play session:
      - grid        : 2-D list of characters (the maze)
      - start       : (row, col) of the S cell
      - goal        : (row, col) of the G cell
      - player_pos  : current (row, col) of the player
      - path        : ordered list of (row, col) returned by BFS, or []
      - won         : True once the player reaches G
      - status_msg  : human-readable string describing the last action
    """

    def __init__(self, level_path):
        """Load the level file and initialise all state fields."""
        # Load the raw grid from disk
        self.grid = load_grid(level_path)

        # Locate S and G; find_start_and_goal returns None if either is absent
        self.start, self.goal = find_start_and_goal(self.grid)

        # Player begins at the start cell
        self.player_pos = self.start

        # No path is shown at startup
        self.path = []

        # Win flag; checked by the UI after every move
        self.won = False

        # Initialise the status bar with a welcome hint
        self.status_msg = "Use arrow keys (or w/a/s/d) to move. Press P to show the shortest path."

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def is_valid(self):
        """Return True if the level contains exactly one S and one G."""
        return self.start is not None and self.goal is not None

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def move(self, direction):
        """
        Attempt to move the player one step in `direction` (w/a/s/d).

        Updates player_pos, clears any displayed path, and sets status_msg
        to explain what happened (moved, blocked by wall, blocked by boundary).
        Also sets self.won = True if the player reaches the goal.
        """
        row, col = self.player_pos
        dir_name = DIRECTION_NAMES.get(direction, direction)

        # Compute the candidate cell without committing to it
        delta = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}
        if direction not in delta:
            self.status_msg = f"Unknown direction '{direction}'."
            return

        dr, dc = delta[direction]
        new_row, new_col = row + dr, col + dc

        # Check boundary first, then wall
        rows, cols = len(self.grid), len(self.grid[0])
        if new_row < 0 or new_row >= rows or new_col < 0 or new_col >= cols:
            self.status_msg = f"Can't move {dir_name} — that's outside the maze boundary."
            return

        if self.grid[new_row][new_col] == "#":
            self.status_msg = f"Can't move {dir_name} — there's a wall in the way."
            return

        # Move is valid: update position and clear old path highlight
        self.player_pos = (new_row, new_col)
        self.path = []  # Clear path whenever the player moves

        if self.player_pos == self.goal:
            self.won = True
            self.status_msg = "You reached the goal! 🎉"
        else:
            self.status_msg = f"Moved {dir_name}."

    # ------------------------------------------------------------------
    # Pathfinding
    # ------------------------------------------------------------------

    def compute_path(self):
        """
        Run BFS from the current player position to the goal and store the
        result in self.path.  Updates status_msg with the outcome.
        """
        self.path = find_path(self.grid, self.player_pos, self.goal)

        if self.path:
            steps = len(self.path) - 1  # Number of moves, not cells
            self.status_msg = f"Shortest path found: {steps} step{'s' if steps != 1 else ''} to the goal."
        else:
            self.status_msg = "No path exists from your current position to the goal."

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self):
        """Return the player to the start cell and clear path and win flag."""
        self.player_pos = self.start
        self.path = []
        self.won = False
        self.status_msg = "Game reset. Use arrow keys to move."


# ---------------------------------------------------------------------------
# Terminal rendering helper — reads state only, never mutates it
# ---------------------------------------------------------------------------

def print_grid(state):
    """
    Print the current maze to stdout.

    Symbols:
      P  — player position
      o  — BFS path cell (not overwriting S or G)
      #  — wall
      .  — empty floor
      S  — start
      G  — goal
    """
    path_set = set(state.path)  # Convert to set for O(1) membership test

    for row_idx, row in enumerate(state.grid):
        for col_idx, cell in enumerate(row):
            pos = (row_idx, col_idx)
            if pos == state.player_pos:
                print("P", end=" ")
            elif pos in path_set and cell not in ("S", "G"):
                print("o", end=" ")  # Path marker; never hides S or G
            else:
                print(cell, end=" ")
        print()  # End of row

    print()  # Blank line after grid


# ---------------------------------------------------------------------------
# Text-mode game loop — called by main.py as the sole entry point
# ---------------------------------------------------------------------------

def run_text_mode():
    """
    Full text-mode game loop.

    Loads level1.txt, then repeatedly:
      1. Renders the grid via print_grid.
      2. Prints the status message (explains blocked moves, path length, etc.).
      3. Reads one command and dispatches it to GameState.

    Commands: w/a/s/d = move, p = show path, q = quit.
    """
    project_root = Path(__file__).resolve().parents[1]
    level_path = project_root / "examples" / "level1.txt"

    state = GameState(level_path)

    if not state.is_valid():
        print("Error: level must contain exactly one S and one G.")
        return

    print("=== Maze Navigator (Text Mode) ===")
    print("Controls: w=up  s=down  a=left  d=right  p=show path  q=quit\n")

    while True:
        print_grid(state)
        print(f"  {state.status_msg}\n")  # Status bar explains every outcome

        if state.won:
            break

        command = input("Move (w/a/s/d / p / q): ").strip().lower()

        # Pure dispatch — no logic here, everything delegated to GameState
        if command == "q":
            print("Game ended.")
            break
        elif command == "p":
            state.compute_path()
        elif command in ("w", "a", "s", "d"):
            state.move(command)
        else:
            state.status_msg = f"Unknown command '{command}'. Use w/a/s/d, p, or q."
