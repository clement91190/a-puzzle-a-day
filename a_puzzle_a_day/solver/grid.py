"""Board grid topology — date ↔ cell mapping + polyomino-outline trace.

Pure logic: depends only on ``constants``. Safe to import from anywhere,
including tests and the in-browser solver. No CAD primitives in scope.
"""

from __future__ import annotations

from datetime import date as _date
from typing import Iterable

from ..constants import BOARD_GRID, MONTH_LABELS


# ----------------------------------------------------------------------------
# Date ↔ cell mapping
# ----------------------------------------------------------------------------


def cell_for_month(month: int) -> tuple[int, int]:
    """Map 1..12 to the (row, col) of the month label (rows 0-1, cols 0-5)."""
    if not 1 <= month <= 12:
        raise ValueError(f"month must be in 1..12, got {month}")
    idx = month - 1
    return (idx // 6, idx % 6)


def cell_for_day(day: int) -> tuple[int, int]:
    """Map 1..31 to the (row, col) of the day cell (rows 2-6).

    Days 1..28 fill rows 2-5 left-to-right. Days 29, 30, 31 sit in the
    centered notch of row 6 at columns 2, 3, 4.
    """
    if not 1 <= day <= 31:
        raise ValueError(f"day must be in 1..31, got {day}")
    if day <= 28:
        idx = day - 1
        return (2 + idx // 7, idx % 7)
    return (6, day - 27)


def board_cells_for_date(month: int, day: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """The two cells that must remain UNCOVERED on the given date."""
    return cell_for_month(month), cell_for_day(day)


def label_for_cell(row: int, col: int) -> str:
    """Human-readable label for a board cell ('Jan', '7', ...) or '' for voids."""
    if row < 2:
        idx = row * 6 + col
        if idx < len(MONTH_LABELS):
            return MONTH_LABELS[idx]
        return ""
    if row == 6:
        if not 2 <= col <= 4:
            return ""
        return str(27 + col)
    return str((row - 2) * 7 + col + 1)


def today_month_day() -> tuple[int, int]:
    today = _date.today()
    return today.month, today.day


# ----------------------------------------------------------------------------
# All labelled (non-void) cells on the canonical board.
# ----------------------------------------------------------------------------


def labelled_cells() -> tuple[tuple[int, int], ...]:
    """The 43 (row, col) cells where labels live — board minus the 6 voids."""
    return tuple(
        (r, c)
        for r, row in enumerate(BOARD_GRID)
        for c, ok in enumerate(row)
        if ok
    )


# ----------------------------------------------------------------------------
# Polyomino outline trace (consumed by the board pocket + each piece).
# ----------------------------------------------------------------------------


def trace_polyomino_outline(
    cells: Iterable[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Trace the boundary of a polyomino in lattice coords.

    Each cell ``(row, col)`` occupies the unit square ``[col, col+1] × [row, row+1]``.
    The boundary is the set of cell edges that have no cell on the inside. We
    emit them in CW-in-grid order, which becomes CCW after the y flip in
    ``cad.geometry.grid_corner_to_mm``.

    Returns lattice corners (no collinear dedupe — do that at use-site).
    """
    cellset = set(cells)
    by_start: dict[tuple[int, int], tuple[int, int]] = {}
    for r, c in cellset:
        if (r - 1, c) not in cellset:
            by_start[(c + 1, r)] = (c, r)               # top edge: TR → TL
        if (r, c - 1) not in cellset:
            by_start[(c, r)] = (c, r + 1)               # left edge: TL → BL
        if (r + 1, c) not in cellset:
            by_start[(c, r + 1)] = (c + 1, r + 1)       # bottom edge: BL → BR
        if (r, c + 1) not in cellset:
            by_start[(c + 1, r + 1)] = (c + 1, r)       # right edge: BR → TR

    if not by_start:
        return []

    start = min(by_start.keys())
    path: list[tuple[int, int]] = [start]
    cur = by_start[start]
    safety = 4 * len(cellset) + 4
    while cur != start and safety > 0:
        path.append(cur)
        cur = by_start[cur]
        safety -= 1
    return path
