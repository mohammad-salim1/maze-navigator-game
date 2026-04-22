from pathlib import Path
from pathfinding import load_grid, find_start_and_goal, move_player, find_path


def print_grid(grid, player_pos, path=None):
    if path is None:
        path = []

    for row in range(len(grid)):
        for col in range(len(grid[row])):
            pos = (row, col)

            if pos == player_pos:
                print("P", end=" ")
            elif pos in path and grid[row][col] not in ["S", "G"]:
                print("o", end=" ")
            else:
                print(grid[row][col], end=" ")
        print()
    print()


def main():
    project_root = Path(__file__).resolve().parents[1]
    level_path = project_root / "examples" / "level1.txt"

    grid = load_grid(level_path)
    start, goal = find_start_and_goal(grid)

    if start is None or goal is None:
        print("Error: level must contain one S and one G.")
        return

    player_pos = start

    while True:
        print_grid(grid, player_pos)

        if player_pos == goal:
            print("You win!")
            break

        command = input("Enter move (w/a/s/d), p for path, q to quit: ").strip().lower()

        if command == "q":
            print("Game ended.")
            break
        elif command == "p":
            path = find_path(grid, player_pos, goal)
            if path:
                print_grid(grid, player_pos, path)
            else:
                print("No path found.")
        elif command in ["w", "a", "s", "d"]:
            player_pos = move_player(grid, player_pos, command)
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
