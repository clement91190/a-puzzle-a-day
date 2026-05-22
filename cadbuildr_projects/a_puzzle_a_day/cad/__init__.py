"""CAD subpackage: foundation Parts + Assembly + mm helpers."""

from .assembly import APuzzleADayAssembly, APuzzleADaySolved
from .calendar_board import (
    BOARD_MARGIN_MM,
    BOARD_SLAB_HEIGHT_MM,
    POCKET_DEPTH_MM,
    CalendarBoard,
)
from .geometry import (
    board_origin_offset,
    cell_center_xy,
    dedupe_collinear,
    grid_corner_to_mm,
)
from .puzzle_piece import PIECE_HEIGHT_MM, PIECE_INSET_MM, PuzzlePiece

__all__ = [
    "APuzzleADayAssembly",
    "APuzzleADaySolved",
    "BOARD_MARGIN_MM",
    "BOARD_SLAB_HEIGHT_MM",
    "CalendarBoard",
    "PIECE_HEIGHT_MM",
    "PIECE_INSET_MM",
    "POCKET_DEPTH_MM",
    "PuzzlePiece",
    "board_origin_offset",
    "cell_center_xy",
    "dedupe_collinear",
    "grid_corner_to_mm",
]
