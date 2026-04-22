import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "src"))

from pathfinding import find_path, move_player


def test_find_path():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '.', 'G', '#'],
        ['#', '#', '#', '#', '#']
    ]

    start = (1, 1)
    goal = (1, 3)

    path = find_path(grid, start, goal)
    assert path == [(1, 1), (1, 2), (1, 3)]


def test_move_player():
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '.', 'G', '#'],
        ['#', '#', '#', '#', '#']
    ]

    player = (1, 1)
    new_player = move_player(grid, player, "d")
    assert new_player == (1, 2)

    blocked_player = move_player(grid, player, "w")
    assert blocked_player == (1, 1)


if __name__ == "__main__":
    test_find_path()
    test_move_player()
    print("All tests passed.")
