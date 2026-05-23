"""Exact-cover backtracking solver for the A-Puzzle-A-Day calendar puzzle.

For any (month, day) target, the board has 49 cells - 6 voids - 2 uncovered
= 41 cells to fill, which equals the total area of the 8 canonical pieces.
The solver places pieces one at a time, picking the lowest-numbered empty
cell as the anchor and trying every orientation that doesn't overflow the
board or land on an occupied / forbidden cell.

A single solve is usually well under 100 ms in CPython for the 41-cell
board with 8 pieces. The recursion depth is bounded by the piece count (8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from ..constants import BOARD_GRID
from .grid import board_cells_for_date, labelled_cells
from .pieces import Piece, PIECES, all_orientations


@dataclass(frozen=True)
class Placement:
    """A single piece placed at (row, col) in a specific orientation."""

    piece_name: str
    color: str
    cells: tuple[tuple[int, int], ...]  # absolute (row, col) on the board


@dataclass
class Solution:
    placements: list[Placement] = field(default_factory=list)
    month: int = 0
    day: int = 0


def _empty_board_cells(month: int, day: int) -> set[tuple[int, int]]:
    """Cells that must be filled (labelled board cells minus month + day labels)."""
    holes = set(board_cells_for_date(month, day))
    return {cell for cell in labelled_cells() if cell not in holes}


def _next_anchor(empty: set[tuple[int, int]]) -> tuple[int, int]:
    """Pick the lowest (row, col) empty cell as the anchor (row-major)."""
    return min(empty)


def _place(
    piece_cells: tuple[tuple[int, int], ...],
    anchor_r: int,
    anchor_c: int,
) -> tuple[tuple[int, int], ...]:
    """Shift piece so its first cell sits at (anchor_r, anchor_c).

    "First cell" is the lexicographically lowest (row, col), which is what
    ``all_orientations`` normalizes to. This means anchoring fills the
    target anchor cell.
    """
    base_r, base_c = piece_cells[0]
    return tuple((r - base_r + anchor_r, c - base_c + anchor_c) for r, c in piece_cells)


def _fits(absolute_cells: Iterable[tuple[int, int]], empty: set[tuple[int, int]]) -> bool:
    for cell in absolute_cells:
        if cell not in empty:
            return False
    return True


def _backtrack(
    empty: set[tuple[int, int]],
    remaining_pieces: list[Piece],
    placements: list[Placement],
) -> bool:
    if not empty and not remaining_pieces:
        return True
    if not empty or not remaining_pieces:
        return False

    anchor = _next_anchor(empty)
    for piece_idx, piece in enumerate(remaining_pieces):
        for orientation in all_orientations(piece.cells):
            absolute = _place(orientation, anchor[0], anchor[1])
            if not _fits(absolute, empty):
                continue
            placements.append(Placement(piece.name, piece.color, absolute))
            empty -= set(absolute)
            next_pieces = remaining_pieces[:piece_idx] + remaining_pieces[piece_idx + 1:]
            if _backtrack(empty, next_pieces, placements):
                return True
            empty |= set(absolute)
            placements.pop()
    return False


def find_solution(month: int, day: int) -> Solution:
    """Return one valid arrangement, or raise ``RuntimeError`` if none.

    Every valid (month, day) on the Dragon Fjord canonical board has at
    least one solution — many have multiple. We return the first found.
    """
    empty = _empty_board_cells(month, day)
    pieces = list(PIECES)
    solution = Solution(month=month, day=day)
    if _backtrack(empty, pieces, solution.placements):
        return solution
    raise RuntimeError(
        f"No solution found for ({month}, {day}). "
        "This indicates a piece-shape mismatch with the canonical Dragon Fjord set."
    )


def format_solution_for_render(solution: Solution) -> list[dict]:
    """Plain-JSON shape suitable for handing to the React viewer.

    Each entry is ``{name, color, cells: [[r, c], ...]}``. The viewer
    converts to mm via ``BOARD_CELL_SIZE_MM`` and renders one extrusion
    per piece.
    """
    return [
        {
            "name": p.piece_name,
            "color": p.color,
            "cells": [list(cell) for cell in p.cells],
        }
        for p in solution.placements
    ]
