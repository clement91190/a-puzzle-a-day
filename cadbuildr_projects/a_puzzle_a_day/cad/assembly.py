"""``CalendarBoard`` + placed ``PuzzlePiece``s for a chosen date."""

from __future__ import annotations

from typing import Iterable

from cadbuildr.foundation import Assembly

from ..constants import DEFAULT_BOARD_COLOR
from ..solver import find_solution, format_solution_for_render
from .calendar_board import CalendarBoard
from .puzzle_piece import PuzzlePiece


class APuzzleADayAssembly(Assembly):
    """Board + already-placed pieces. Solver-agnostic."""

    def __init__(
        self,
        placed_pieces: Iterable[dict],
        board_color: str = DEFAULT_BOARD_COLOR,
    ):
        super().__init__()
        self.add_component(CalendarBoard(color=board_color))
        for entry in placed_pieces:
            self.add_component(
                PuzzlePiece(
                    cells=[tuple(c) for c in entry["cells"]],
                    color=entry["color"],
                )
            )


class APuzzleADaySolved(APuzzleADayAssembly):
    """Solve for (month, day) then place pieces; raises if unsolvable."""

    def __init__(
        self,
        month: int,
        day: int,
        board_color: str = DEFAULT_BOARD_COLOR,
        piece_overrides: dict[str, str] | None = None,
    ):
        solution = find_solution(month, day)
        placed = format_solution_for_render(solution)
        if piece_overrides:
            for entry in placed:
                if entry["name"] in piece_overrides:
                    entry["color"] = piece_overrides[entry["name"]]
        super().__init__(placed_pieces=placed, board_color=board_color)
        self.month = month
        self.day = day
        self.solution = solution
