"""CAD-only helpers: grid lattice → millimetre conversion + collinear dedupe.

Pure functions; no foundation imports needed (they take/return raw tuples).
Kept separate from ``solver.grid`` so the solver stays usable without ever
importing CAD primitives.
"""

from __future__ import annotations

from ..constants import BOARD_CELL_SIZE_MM, BOARD_GRID


def board_origin_offset() -> tuple[float, float]:
    """``(ox, oy)`` such that ``cell_center_xy(r, c) = (ox + col*CELL, …)``."""
    rows = len(BOARD_GRID)
    cols = len(BOARD_GRID[0])
    return (
        -cols * BOARD_CELL_SIZE_MM / 2.0 + BOARD_CELL_SIZE_MM / 2.0,
        -rows * BOARD_CELL_SIZE_MM / 2.0 + BOARD_CELL_SIZE_MM / 2.0,
    )


def cell_center_xy(row: int, col: int) -> tuple[float, float]:
    """Cell center in mm. Row 0 sits at the top of the rendered scene (y flipped)."""
    ox, oy = board_origin_offset()
    return (
        ox + col * BOARD_CELL_SIZE_MM,
        oy + (len(BOARD_GRID) - 1 - row) * BOARD_CELL_SIZE_MM,
    )


def grid_corner_to_mm(grid_col: float, grid_row: float) -> tuple[float, float]:
    """Lattice corner ``(grid_col, grid_row)`` → ``(x, y)`` mm.

    Lattice runs ``grid_col ∈ [0, cols]``, ``grid_row ∈ [0, rows]``. Cell
    ``(r, c)`` has its 4 corners at lattice ``(c, r), (c+1, r), (c+1, r+1), (c, r+1)``.
    """
    ox, oy = board_origin_offset()
    rows = len(BOARD_GRID)
    x = ox - BOARD_CELL_SIZE_MM / 2.0 + grid_col * BOARD_CELL_SIZE_MM
    y = oy + (rows - 0.5 - grid_row) * BOARD_CELL_SIZE_MM
    return x, y


def dedupe_collinear(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Drop intermediate collinear points so an outline has minimal vertices."""
    if len(points) < 3:
        return points
    out: list[tuple[float, float]] = []
    n = len(points)
    for i in range(n):
        prev = points[(i - 1) % n]
        cur = points[i]
        nxt = points[(i + 1) % n]
        cross = (cur[0] - prev[0]) * (nxt[1] - cur[1]) - (cur[1] - prev[1]) * (nxt[0] - cur[0])
        if abs(cross) > 1e-6:
            out.append(cur)
    return out
