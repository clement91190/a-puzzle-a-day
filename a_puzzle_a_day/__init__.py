"""Dragon Fjord A-Puzzle-A-Day.

Split into two subpackages so a host that only needs the search (e.g. a
puzzle solver running on a server) can avoid pulling foundation in:

- ``solver/`` — pure logic: board grid, piece catalog, backtracking search.
- ``cad/``    — foundation Parts + Assembly + mm conversion.

Top-level re-exports keep the common API one ``import`` away.
"""

from .constants import (
    BOARD_CELL_SIZE_MM,
    BOARD_GRID,
    BOARD_HEIGHT_MM,
    DEFAULT_BOARD_COLOR,
    DEFAULT_PIECE_COLORS,
    MONTH_LABELS,
    PIECE_NAMES,
    PIECE_SHAPES,
)
from .solver import (
    PIECES,
    Piece,
    PieceCatalog,
    Placement,
    Solution,
    all_orientations,
    board_cells_for_date,
    cell_for_day,
    cell_for_month,
    find_solution,
    format_solution_for_render,
    label_for_cell,
    labelled_cells,
    today_month_day,
    trace_polyomino_outline,
)
from .cad import (
    APuzzleADayAssembly,
    APuzzleADaySolved,
    BOARD_MARGIN_MM,
    BOARD_SLAB_HEIGHT_MM,
    CalendarBoard,
    PIECE_HEIGHT_MM,
    PIECE_INSET_MM,
    POCKET_DEPTH_MM,
    PuzzlePiece,
    board_origin_offset,
    cell_center_xy,
    dedupe_collinear,
    grid_corner_to_mm,
)

# Parameter-decorated entry points need the new foundation symbols
# (Color/Int/Enum/cadbuildr_project). Older pypi foundations don't ship them
# yet — make the import best-effort so the package stays usable in Pyodide.
try:
    from .projects import puzzle_for_date, puzzle_today  # type: ignore[assignment]
except ImportError:
    puzzle_for_date = puzzle_today = None  # type: ignore[assignment]

__all__ = [
    "APuzzleADayAssembly",
    "APuzzleADaySolved",
    "BOARD_CELL_SIZE_MM",
    "BOARD_GRID",
    "BOARD_HEIGHT_MM",
    "BOARD_MARGIN_MM",
    "BOARD_SLAB_HEIGHT_MM",
    "CalendarBoard",
    "DEFAULT_BOARD_COLOR",
    "DEFAULT_PIECE_COLORS",
    "MONTH_LABELS",
    "PIECE_HEIGHT_MM",
    "PIECE_INSET_MM",
    "PIECE_NAMES",
    "PIECE_SHAPES",
    "PIECES",
    "POCKET_DEPTH_MM",
    "Piece",
    "PieceCatalog",
    "Placement",
    "PuzzlePiece",
    "Solution",
    "all_orientations",
    "board_cells_for_date",
    "board_origin_offset",
    "cell_center_xy",
    "cell_for_day",
    "cell_for_month",
    "dedupe_collinear",
    "find_solution",
    "format_solution_for_render",
    "grid_corner_to_mm",
    "label_for_cell",
    "labelled_cells",
    "puzzle_for_date",
    "puzzle_today",
    "today_month_day",
    "trace_polyomino_outline",
]
