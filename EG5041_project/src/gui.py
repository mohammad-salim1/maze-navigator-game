import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from pathfinding import load_grid, find_start_and_goal, move_player, find_path

CELL_SIZE = 60


class MazeGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Navigator Game")

        project_root = Path(__file__).resolve().parents[1]
        level_path = project_root / "examples" / "level1.txt"

        self.grid = load_grid(level_path)
        self.start, self.goal = find_start_and_goal(self.grid)

        if self.start is None or self.goal is None:
            messagebox.showerror("Error", "Level must contain one S and one G.")
            self.root.destroy()
            return

        self.player_pos = self.start
        self.path = []

        rows = len(self.grid)
        cols = len(self.grid[0])

        self.canvas = tk.Canvas(
            root,
            width=cols * CELL_SIZE,
            height=rows * CELL_SIZE
        )
        self.canvas.pack()

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        path_button = tk.Button(
            button_frame,
            text="Show Shortest Path",
            command=self.show_path
        )
        path_button.pack(side="left", padx=10)

        reset_button = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_game
        )
        reset_button.pack(side="left", padx=10)

        label = tk.Label(root, text="Use arrow keys to move")
        label.pack()

        self.root.bind("<Up>", self.handle_key)
        self.root.bind("<Down>", self.handle_key)
        self.root.bind("<Left>", self.handle_key)
        self.root.bind("<Right>", self.handle_key)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell = self.grid[row][col]
                color = "white"

                if cell == "#":
                    color = "black"
                elif cell == "S":
                    color = "lightgreen"
                elif cell == "G":
                    color = "gold"

                if (row, col) in self.path and cell not in ["S", "G"]:
                    color = "lightblue"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="gray"
                )

                if cell in ["S", "G"]:
                    self.canvas.create_text(
                        x1 + CELL_SIZE // 2,
                        y1 + CELL_SIZE // 2,
                        text=cell,
                        font=("Arial", 18, "bold")
                    )

        pr, pc = self.player_pos
        px = pc * CELL_SIZE + CELL_SIZE // 2
        py = pr * CELL_SIZE + CELL_SIZE // 2

        self.canvas.create_oval(
            px - 18, py - 18,
            px + 18, py + 18,
            fill="red"
        )
        self.canvas.create_text(
            px, py,
            text="P",
            fill="white",
            font=("Arial", 14, "bold")
        )

    def handle_key(self, event):
        key_map = {
            "Up": "w",
            "Down": "s",
            "Left": "a",
            "Right": "d"
        }

        if event.keysym in key_map:
            self.player_pos = move_player(self.grid, self.player_pos, key_map[event.keysym])
            self.path = []
            self.draw_grid()

            if self.player_pos == self.goal:
                messagebox.showinfo("You Win", "You reached the goal!")

    def show_path(self):
        self.path = find_path(self.grid, self.player_pos, self.goal)
        if not self.path:
            messagebox.showinfo("Path", "No path found.")
        self.draw_grid()

    def reset_game(self):
        self.player_pos = self.start
        self.path = []
        self.draw_grid()


if __name__ == "__main__":
    root = tk.Tk()
    app = MazeGameGUI(root)
    root.mainloop()
