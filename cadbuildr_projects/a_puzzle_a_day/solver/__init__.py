"""Solver subpackage: pure logic — board grid, piece catalog, exact-cover search."""

from .grid import (
    board_cells_for_date,
    cell_for_day,
    cell_for_month,
    label_for_cell,
    labelled_cells,
    today_month_day,
    trace_polyomino_outline,
)
from .pieces import PIECES, Piece, PieceCatalog, all_orientations
from .search import (
    Placement,
    Solution,
    find_solution,
    format_solution_for_render,
)

__all__ = [
    "PIECES",
    "Piece",
    "PieceCatalog",
    "Placement",
    "Solution",
    "all_orientations",
    "board_cells_for_date",
    "cell_for_day",
    "cell_for_month",
    "find_solution",
    "format_solution_for_render",
    "label_for_cell",
    "labelled_cells",
    "today_month_day",
    "trace_polyomino_outline",
]
