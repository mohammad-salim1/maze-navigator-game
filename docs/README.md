# Maze Navigator Game

## Overview
This project is a small Python maze game that demonstrates player movement on a 2D grid and shortest-path finding using Breadth-First Search (BFS).

## Project Structure
- `src/` contains the source code
- `examples/` contains example level files
- `tests/` contains simple tests
- `docs/` contains project documentation

## Features
- Grid-based maze with walls, start, and goal
- Player movement with collision checking
- Text-mode version for testing
- GUI version built with tkinter
- Shortest-path visualisation using BFS

## How to Run

### Text Mode
Open `src/main.py` and run it in IDLE.

### GUI Mode
Open `src/gui.py` and run it in IDLE.

## Pathfinding Algorithm
The project uses Breadth-First Search (BFS). BFS is suitable because all moves have equal cost, so it correctly returns the shortest path in number of steps.

## Design Choices
The project separates:
- core logic and pathfinding in `pathfinding.py`
- text-mode gameplay in `main.py`
- GUI in `gui.py`

This makes the code easier to understand, test, and reuse.
