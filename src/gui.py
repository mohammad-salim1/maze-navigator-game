"""
gui.py
------
Graphical front-end for the Maze Navigator game using tkinter.

Responsibilities of this file:
  - Build and layout all tkinter widgets (canvas, buttons, status bar).
  - Bind keyboard events and translate them into GameState method calls.
  - Redraw the canvas whenever the state changes.

This file contains NO game logic.  Movement validation, pathfinding, and win
detection all live in GameState (game.py) and pathfinding.py.
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from game import GameState

CELL_SIZE = 60  # Pixel size of each maze cell

# Colour palette — centralised so every cell type is easy to restyle
COLOURS = {
    "wall":   "#2c2c2c",  # Dark grey for walls
    "floor":  "#f0f0f0",  # Light grey for walkable cells
    "start":  "#4caf50",  # Green for the start cell (S)
    "goal":   "#ffc107",  # Amber for the goal cell (G)
    "path":   "#90caf9",  # Light blue for BFS path cells
    "player": "#e53935",  # Red for the player circle
}

# Maps tkinter key symbol names to the w/a/s/d direction codes used by GameState
ARROW_KEY_MAP = {
    "Up":    "w",
    "Down":  "s",
    "Left":  "a",
    "Right": "d",
    # Also accept w/a/s/d letter keys directly
    "w": "w",
    "a": "a",
    "s": "s",
    "d": "d",
}


class MazeGameGUI:
    """
    Tkinter GUI wrapper around a GameState instance.

    Layout:
      [ canvas — the maze grid ]
      [ Show Path button | Reset button ]
      [ status bar label ]
    """

    def __init__(self, root, level_path):
        """Initialise the window, load the level, and draw the first frame."""
        self.root = root
        self.root.title("Maze Navigator Game")

        # GameState is the single source of truth; GUI only reads and renders it
        self.state = GameState(level_path)

        if not self.state.is_valid():
            messagebox.showerror("Error", "Level must contain exactly one S and one G.")
            self.root.destroy()
            return

        rows = len(self.state.grid)
        cols = len(self.state.grid[0])

        # --- Canvas (maze drawing area) ---
        self.canvas = tk.Canvas(
            root,
            width=cols * CELL_SIZE,
            height=rows * CELL_SIZE,
            bg=COLOURS["wall"]
        )
        self.canvas.pack()

        # macOS fix: canvas must explicitly take focus to receive key events.
        # Without this, clicking a button steals focus and w/a/s/d stop working.
        self.canvas.config(takefocus=1)
        self.canvas.focus_set()  # Grab focus on startup
        # Re-grab focus whenever the user clicks anywhere on the canvas
        self.canvas.bind("<Button-1>", lambda e: self.canvas.focus_set())

        # --- Button row ---
        button_frame = tk.Frame(root)
        button_frame.pack(pady=8)

        tk.Button(
            button_frame,
            text="Show Shortest Path  [P]",
            command=self._btn_show_path,  # Wrapper returns focus to canvas
            width=24
        ).pack(side="left", padx=6)

        tk.Button(
            button_frame,
            text="Reset  [R]",
            command=self._btn_reset,      # Wrapper returns focus to canvas
            width=12
        ).pack(side="left", padx=6)

        # --- Status bar: shows why a move was blocked, path length, win message, etc. ---
        self.status_var = tk.StringVar(value=self.state.status_msg)
        status_bar = tk.Label(
            root,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padx=6,
            font=("Arial", 10)
        )
        status_bar.pack(fill="x", padx=4, pady=(0, 4))

        # --- Key bindings (arrow keys + w/a/s/d + p + r) ---
        # Bound on canvas (not root) so macOS focus model works correctly.
        # Buttons re-give focus to canvas via their command wrappers below.
        for key in ("<Up>", "<Down>", "<Left>", "<Right>",
                    "<w>", "<a>", "<s>", "<d>",
                    "<W>", "<A>", "<S>", "<D>"):
            self.canvas.bind(key, self.on_key_move)

        self.canvas.bind("<p>", lambda e: self.on_show_path())
        self.canvas.bind("<P>", lambda e: self.on_show_path())
        self.canvas.bind("<r>", lambda e: self.on_reset())
        self.canvas.bind("<R>", lambda e: self.on_reset())

        self.draw_grid()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw_grid(self):
        """
        Redraw the entire canvas from scratch using the current GameState.
        Called after every state change (move, path, reset).
        """
        self.canvas.delete("all")
        path_set = set(self.state.path)  # Convert list to set for O(1) lookup

        for row in range(len(self.state.grid)):
            for col in range(len(self.state.grid[row])):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell = self.state.grid[row][col]

                # Choose background colour based on cell type and path membership
                if cell == "#":
                    colour = COLOURS["wall"]
                elif cell == "S":
                    colour = COLOURS["start"]
                elif cell == "G":
                    colour = COLOURS["goal"]
                elif (row, col) in path_set:
                    colour = COLOURS["path"]   # BFS path highlight
                else:
                    colour = COLOURS["floor"]

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=colour, outline="#bbb")

                # Draw text labels on S and G so they're easy to spot
                if cell in ("S", "G"):
                    self.canvas.create_text(
                        x1 + CELL_SIZE // 2,
                        y1 + CELL_SIZE // 2,
                        text=cell,
                        font=("Arial", 16, "bold"),
                        fill="white"
                    )

        # Draw the player as a filled circle on top of the grid
        pr, pc = self.state.player_pos
        cx = pc * CELL_SIZE + CELL_SIZE // 2
        cy = pr * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 6

        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                fill=COLOURS["player"], outline="")
        self.canvas.create_text(cx, cy, text="P",
                                fill="white", font=("Arial", 14, "bold"))

        # Sync the status bar label with whatever message GameState set
        self.status_var.set(self.state.status_msg)

    # ------------------------------------------------------------------
    # Event handlers — translate UI events into GameState calls
    # ------------------------------------------------------------------

    def on_key_move(self, event):
        """
        Handle arrow key and w/a/s/d key presses.

        Translates the tkinter key symbol to a direction code (w/a/s/d),
        delegates movement to GameState, then redraws.  The status bar will
        automatically reflect why a move was blocked (wall, boundary, etc.).
        """
        if self.state.won:
            return  # Ignore input after the game is won

        # Normalise to lower-case so W == w, etc.
        direction = ARROW_KEY_MAP.get(event.keysym) or ARROW_KEY_MAP.get(event.keysym.lower())
        if direction is None:
            return

        self.state.move(direction)   # All logic lives in GameState
        self.draw_grid()

        if self.state.won:
            messagebox.showinfo("You Win! 🎉", "You reached the goal!")

    def on_show_path(self):
        """Trigger BFS via GameState and redraw to highlight the path."""
        self.state.compute_path()   # Delegates to GameState.compute_path()
        self.draw_grid()

    def on_reset(self):
        """Reset the game to the start position via GameState and redraw."""
        self.state.reset()          # Delegates to GameState.reset()
        self.draw_grid()

    def _btn_show_path(self):
        """Button wrapper: show path then return keyboard focus to canvas."""
        self.on_show_path()
        self.canvas.focus_set()  # macOS: buttons steal focus, so give it back

    def _btn_reset(self):
        """Button wrapper: reset then return keyboard focus to canvas."""
        self.on_reset()
        self.canvas.focus_set()  # macOS: buttons steal focus, so give it back


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Resolve the level path and launch the tkinter window."""
    project_root = Path(__file__).resolve().parents[1]
    level_path = project_root / "examples" / "level1.txt"

    root = tk.Tk()
    MazeGameGUI(root, level_path)
    root.mainloop()


if __name__ == "__main__":
    main()
