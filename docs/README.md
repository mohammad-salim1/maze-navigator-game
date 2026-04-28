# Maze Navigator Game

## Overview
A grid-based maze game in Python where a player navigates from **S** (start) to **G** (goal) while avoiding walls. The game includes a text-mode interface for testing, a tkinter GUI, and shortest-path visualisation using Breadth-First Search (BFS).

## Project Structure
```
maze_project/
├── src/
│   ├── pathfinding.py   # Core logic: grid loading, movement, BFS pathfinding
│   ├── main.py          # Text-mode driver (w/a/s/d controls)
│   └── gui.py           # tkinter GUI
├── tests/
│   └── test_game.py     # Unit tests for core functions
├── examples/
│   ├── level1.txt       # Easy maze
│   ├── level2.txt       # Medium maze
│   └── level3.txt       # Hard maze
└── docs/
    └── README.md        # This file
```

## Dependencies
- Python 3.8+
- `tkinter` (included in standard Python on Windows/macOS; on Linux: `sudo apt install python3-tk`)

No third-party packages required.

## How to Run

### Text Mode
```bash
cd src
python main.py
```
Controls: `w` up · `s` down · `a` left · `d` right · `p` show path · `q` quit

### GUI Mode
```bash
cd src
python gui.py
```
Controls: Arrow keys to move · **P** key or button to show path · **R** key or button to reset

### Run Tests
```bash
cd tests
python test_game.py
```

## Pathfinding Algorithm — BFS
Breadth-First Search (BFS) is used because all grid moves have equal cost (1 step). BFS explores cells in order of distance from the start, which guarantees the shortest path in terms of number of steps.

**Key properties:**
- Time complexity: O(rows × cols)
- Space complexity: O(rows × cols)
- Completeness: always finds a path if one exists
- Optimality: always returns the shortest path on an unweighted grid

## Code Architecture
The project is split into three modules to separate concerns:

| Module | Responsibility |
|---|---|
| `pathfinding.py` | Grid I/O, movement validation, BFS — no UI code |
| `main.py` | Text-mode loop; imports from `pathfinding` |
| `gui.py` | tkinter GUI; reuses all functions from `pathfinding` |

The GUI never reimplements game logic — it only calls functions from `pathfinding.py`. This makes the core logic independently testable and reusable.
