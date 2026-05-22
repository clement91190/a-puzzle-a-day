"""Calendar board geometry + Dragon Fjord piece shapes.

The Dragon Fjord A-Puzzle-A-Day board is a 7×7 grid with two voids in the
top-right corner (rows 0-1, col 6) and four voids in the bottom row flanking
a centered 29/30/31 notch (row 6, cols 0-1 and 5-6). The 12 month labels fill
rows 0-1 and the 31 day numbers fill the rest:

```
   col 0  1  2  3  4  5  6
r0  Jan Feb Mar Apr May Jun  .       (col 6 missing)
r1  Jul Aug Sep Oct Nov Dec  .       (col 6 missing)
r2  1   2   3   4   5   6   7
r3  8   9   10  11  12  13  14
r4  15  16  17  18  19  20  21
r5  22  23  24  25  26  27  28
r6  .   .   29  30  31  .   .       (cols 0-1 and 5-6 missing)
```

That's 12 + 31 = 43 labelled cells and 6 piece-area voids. The 8 pieces have
a combined area of 41 squares (sum of cell counts below), and on any given
date exactly 2 cells (the month + the day) are uncovered. 49 - 2 - 6 = 41 ✓.

Piece shapes are stored as a list of (row, col) offsets from the piece's
bounding-box top-left. Names follow community convention (variations are
common across Dragon Fjord sets — these match the published canonical set).
"""

from __future__ import annotations


BOARD_GRID: tuple[tuple[bool, ...], ...] = (
    (True,  True,  True,  True,  True,  True,  False),   # Jan-Jun
    (True,  True,  True,  True,  True,  True,  False),   # Jul-Dec
    (True,  True,  True,  True,  True,  True,  True),    # 1-7
    (True,  True,  True,  True,  True,  True,  True),    # 8-14
    (True,  True,  True,  True,  True,  True,  True),    # 15-21
    (True,  True,  True,  True,  True,  True,  True),    # 22-28
    (False, False, True,  True,  True,  False, False),   # 29-31 (centered)
)
"""``True`` = labelled square that a piece can cover. ``False`` = void cell."""


MONTH_LABELS: tuple[str, ...] = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


BOARD_CELL_SIZE_MM: float = 16.0
"""One labelled square; pieces are ``cell_size``-aligned polyominoes."""


BOARD_HEIGHT_MM: float = 4.0
"""Thickness of the wooden board (matches the physical Dragon Fjord set)."""


PIECE_HEIGHT_MM: float = BOARD_HEIGHT_MM
"""Pieces sit flush with the top of the board pocket; render at the same height."""


# ----------------------------------------------------------------------------
# Piece shapes (The Whole Year Puzzle, 9 pieces: 5 pentominoes + 4 tetrominoes).
#
# Each shape is the list of (row, col) cells the piece occupies, measured from
# the top-left of its bounding box. All shapes are normalized so the minimum
# row and column are 0. Names match the standard polyomino references.
# Combined cell count: 5 × 5 + 4 × 4 = 25 + 16 = 41 cells; board has
# 49 - 6 void = 43 fillable cells; minus 2 (month + day) = 41 to cover.
# ----------------------------------------------------------------------------

PIECE_SHAPES: dict[str, tuple[tuple[int, int], ...]] = {
    # ---- Pentominoes (5 pieces × 5 cells = 25 cells) ---------------------
    # X-pentomino — the "plus" / "+" piece.
    "Plus":   ((0, 1), (1, 0), (1, 1), (1, 2), (2, 1)),
    # L-pentomino — 4-tall L with a foot.
    "L":      ((0, 0), (1, 0), (2, 0), (3, 0), (3, 1)),
    # P-pentomino — 2×2 block + tab.
    "P":      ((0, 0), (0, 1), (1, 0), (1, 1), (2, 0)),
    # Y-pentomino — 4-tall column with a bump on the second cell.
    "Y":      ((0, 0), (1, 0), (1, 1), (2, 0), (3, 0)),
    # N-pentomino — offset zig-zag.
    "N":      ((0, 1), (1, 1), (2, 0), (2, 1), (3, 0)),

    # ---- Tetrominoes (4 pieces × 4 cells = 16 cells) ---------------------
    # T-tetromino — 3 in a row + 1 below the middle.
    "TTet":   ((0, 0), (0, 1), (0, 2), (1, 1)),
    # L-tetromino — 3-tall L (J under reflection).
    "LTet":   ((0, 0), (1, 0), (2, 0), (2, 1)),
    # S-tetromino — 2-row zig-zag (Z under reflection).
    "STet":   ((0, 1), (0, 2), (1, 0), (1, 1)),
    # O-tetromino — the 2×2 square.
    "Square": ((0, 0), (0, 1), (1, 0), (1, 1)),
}

PIECE_NAMES: tuple[str, ...] = tuple(PIECE_SHAPES.keys())


# Each piece gets its own vivid colour — same names as the LEGO store palette
# so they resolve via ``cadbuildr.foundation.constants.DEFAULT_COLORS`` with no
# extra registration. Nine pieces → nine hues that read well over a tan board.
DEFAULT_PIECE_COLORS: dict[str, str] = {
    "Plus":   "bright_red",
    "L":      "bright_orange",
    "P":      "bright_yellow",
    "Y":      "bright_green",
    "N":      "bright_blue",
    "TTet":   "medium_azure",
    "LTet":   "lavender",
    "STet":   "coral",
    "Square": "bright_pink",
}

DEFAULT_BOARD_COLOR: str = "tan"
