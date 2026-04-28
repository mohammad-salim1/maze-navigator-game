import sys
from pathlib import Path

# Allow importing from src/ regardless of where tests are run from
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "src"))

from pathfinding import find_path, move_player, load_grid, find_start_and_goal, is_walkable
from game import GameState


# ---------------------------------------------------------------------------
# find_path tests
# ---------------------------------------------------------------------------

def test_find_path_simple():
    """BFS should find the shortest straight-line path."""
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '.', 'G', '#'],
        ['#', '#', '#', '#', '#']
    ]
    path = find_path(grid, (1, 1), (1, 3))
    assert path == [(1, 1), (1, 2), (1, 3)], f"Unexpected path: {path}"


def test_find_path_no_path():
    """BFS should return an empty list when no path exists."""
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '#', 'G', '#'],
        ['#', '#', '#', '#', '#']
    ]
    path = find_path(grid, (1, 1), (1, 3))
    assert path == [], f"Expected empty list, got: {path}"


def test_find_path_start_equals_goal():
    """If start and goal are the same cell, path should be just that cell."""
    grid = [
        ['#', '#', '#'],
        ['#', 'S', '#'],
        ['#', '#', '#']
    ]
    path = find_path(grid, (1, 1), (1, 1))
    assert path == [(1, 1)], f"Unexpected path: {path}"


def test_find_path_longer_route():
    """BFS must navigate around walls and return a valid shortest path."""
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '#', 'G', '#'],
        ['#', '.', '#', '.', '#'],
        ['#', '.', '.', '.', '#'],
        ['#', '#', '#', '#', '#']
    ]
    path = find_path(grid, (1, 1), (1, 3))
    assert path is not None and len(path) > 0, "Expected a valid path"
    assert path[0] == (1, 1) and path[-1] == (1, 3)


# ---------------------------------------------------------------------------
# move_player tests
# ---------------------------------------------------------------------------

def test_move_player_valid():
    """Player should move right into an empty cell."""
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '.', 'G', '#'],
        ['#', '#', '#', '#', '#']
    ]
    new_pos = move_player(grid, (1, 1), "d")
    assert new_pos == (1, 2), f"Expected (1,2), got {new_pos}"


def test_move_player_blocked_by_wall():
    """Player should not move into a wall; position stays the same."""
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '.', 'G', '#'],
        ['#', '#', '#', '#', '#']
    ]
    new_pos = move_player(grid, (1, 1), "w")
    assert new_pos == (1, 1), f"Expected (1,1), got {new_pos}"


def test_move_player_blocked_by_boundary():
    """Player should not move outside the grid boundaries."""
    grid = [
        ['#', '#', '#'],
        ['S', '.', '#'],
        ['#', '#', '#']
    ]
    new_pos = move_player(grid, (1, 0), "a")
    assert new_pos == (1, 0), f"Expected (1,0), got {new_pos}"


# ---------------------------------------------------------------------------
# Grid loading and scanning tests
# ---------------------------------------------------------------------------

def test_load_grid():
    """Grid loaded from level1.txt should be a 2D list of characters."""
    level_path = project_root / "examples" / "level1.txt"
    grid = load_grid(level_path)
    assert isinstance(grid, list)
    assert all(isinstance(row, list) for row in grid)
    assert all(isinstance(cell, str) and len(cell) == 1 for row in grid for cell in row)


def test_find_start_and_goal():
    """find_start_and_goal should correctly locate S and G."""
    grid = [
        ['#', '#', '#', '#', '#'],
        ['#', 'S', '.', 'G', '#'],
        ['#', '#', '#', '#', '#']
    ]
    start, goal = find_start_and_goal(grid)
    assert start == (1, 1)
    assert goal == (1, 3)


def test_is_walkable_wall():
    """Walls should not be walkable."""
    grid = [['#', '.'], ['.', 'S']]
    assert not is_walkable(grid, 0, 0)


def test_is_walkable_floor():
    """Floor cells and S/G should be walkable."""
    grid = [['#', '.'], ['.', 'S']]
    assert is_walkable(grid, 0, 1)
    assert is_walkable(grid, 1, 1)


def test_is_walkable_out_of_bounds():
    """Out-of-bounds coordinates should not be walkable."""
    grid = [['#', '.'], ['.', 'S']]
    assert not is_walkable(grid, -1, 0)
    assert not is_walkable(grid, 5, 5)


# ---------------------------------------------------------------------------
# GameState tests
# ---------------------------------------------------------------------------

def test_gamestate_loads_level():
    """GameState should load a valid level and report is_valid() == True."""
    state = GameState(project_root / "examples" / "level1.txt")
    assert state.is_valid(), "Expected level1.txt to be valid"
    assert state.player_pos == state.start


def test_gamestate_move_valid():
    """GameState.move() should update player_pos when the move is legal."""
    state = GameState(project_root / "examples" / "level1.txt")
    original = state.player_pos
    # level1 start is (1,1); moving right (d) should reach (1,2)
    state.move("d")
    assert state.player_pos != original, "Player should have moved"
    assert "Moved" in state.status_msg


def test_gamestate_move_blocked_wall():
    """GameState.move() should not change position when blocked by a wall."""
    state = GameState(project_root / "examples" / "level1.txt")
    original = state.player_pos
    state.move("w")  # Moving up from (1,1) hits a wall
    assert state.player_pos == original, "Position should be unchanged"
    assert "wall" in state.status_msg.lower()


def test_gamestate_compute_path():
    """GameState.compute_path() should populate self.path with a valid route."""
    state = GameState(project_root / "examples" / "level1.txt")
    state.compute_path()
    assert len(state.path) > 0, "Expected a non-empty path"
    assert state.path[0] == state.start
    assert state.path[-1] == state.goal


def test_gamestate_reset():
    """GameState.reset() should return player to start and clear path/won."""
    state = GameState(project_root / "examples" / "level1.txt")
    state.move("d")
    state.compute_path()
    state.reset()
    assert state.player_pos == state.start
    assert state.path == []
    assert not state.won


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_find_path_simple()
    test_find_path_no_path()
    test_find_path_start_equals_goal()
    test_find_path_longer_route()
    test_move_player_valid()
    test_move_player_blocked_by_wall()
    test_move_player_blocked_by_boundary()
    test_load_grid()
    test_find_start_and_goal()
    test_is_walkable_wall()
    test_is_walkable_floor()
    test_is_walkable_out_of_bounds()
    test_gamestate_loads_level()
    test_gamestate_move_valid()
    test_gamestate_move_blocked_wall()
    test_gamestate_compute_path()
    test_gamestate_reset()
    print("All tests passed.")
