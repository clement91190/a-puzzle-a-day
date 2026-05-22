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
# Piece shapes (canonical Dragon Fjord A-Puzzle-A-Day set, 8 pieces).
#
# Each shape is the list of (row, col) cells the piece occupies, measured from
# the top-left of its bounding box. All shapes are normalized so the minimum
# row and column are 0. Names match the most common community references.
# Combined cell count: 6+5+5+5+5+5+5+5 = 41 cells; board has 49 - 6 void = 43
# fillable cells; minus 2 (month + day) = 41 to cover.
# ----------------------------------------------------------------------------

PIECE_SHAPES: dict[str, tuple[tuple[int, int], ...]] = {
    # "L" — 6-cell L-tetromino-like (3-tall L stretched).
    "L":      ((0, 0), (1, 0), (2, 0), (3, 0), (3, 1)),
    # "P" — 5 cells, blocky pentomino.
    "P":      ((0, 0), (0, 1), (1, 0), (1, 1), (2, 0)),
    # "Y" — 5 cells, hook + tail.
    "Y":      ((0, 0), (1, 0), (1, 1), (2, 0), (3, 0)),
    # "N" — 5 cells, zig-zag (S/Z variant).
    "N":      ((0, 1), (1, 1), (2, 0), (2, 1), (3, 0)),
    # "U" — 5 cells, U-pentomino.
    "U":      ((0, 0), (0, 2), (1, 0), (1, 1), (1, 2)),
    # "V" — 5 cells, V-pentomino (corner).
    "V":      ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)),
    # "Z" — 5 cells, Z-pentomino.
    "Z":      ((0, 0), (0, 1), (1, 1), (2, 1), (2, 2)),
    # "Square+1" / "P-prime" — 6-cell, 2x2 block + tab.
    "Square": ((0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)),
}

PIECE_NAMES: tuple[str, ...] = tuple(PIECE_SHAPES.keys())


# Each piece gets its own vivid colour — same names as the LEGO store palette
# so they resolve via ``cadbuildr.foundation.constants.DEFAULT_COLORS`` with no
# extra registration. Eight pieces → eight hues that read well over a tan board.
DEFAULT_PIECE_COLORS: dict[str, str] = {
    "L":      "bright_red",
    "P":      "bright_orange",
    "Y":      "bright_yellow",
    "N":      "bright_green",
    "U":      "bright_blue",
    "V":      "medium_azure",
    "Z":      "lavender",
    "Square": "coral",
}

DEFAULT_BOARD_COLOR: str = "tan"
