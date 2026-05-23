"""Parameter-decorated entry points for the puzzle SDK demo.

Requires the new ``cadbuildr.foundation`` parameter descriptors (Color, Int,
Enum, cadbuildr_project) introduced in PR #713. Older published foundations
do not expose them; the package's ``__init__`` guards this import so the
package stays usable in Pyodide while the new foundation wheel publishes.
"""

from __future__ import annotations

from datetime import date as _date

from cadbuildr.foundation import Color, Int, cadbuildr_project

from .cad import APuzzleADaySolved
from .constants import DEFAULT_BOARD_COLOR, DEFAULT_PIECE_COLORS


BOARD_COLOR_CHOICES: tuple[str, ...] = (
    "tan", "dark_tan", "beige", "plywood", "nougat", "reddish_brown",
    "light_bluish_gray", "dark_bluish_gray", "white", "black",
)


@cadbuildr_project(
    project_id="a_puzzle_a_day",
    title="A-Puzzle-A-Day (Dragon Fjord)",
    description=(
        "Solved Dragon Fjord A-Puzzle-A-Day arrangement for the chosen (month, day). "
        "Adjust the board color to match your storefront palette."
    ),
    parameters=[
        Int("month", default=1, min=1, max=12, step=1, label="Month"),
        Int("day", default=1, min=1, max=31, step=1, label="Day"),
        Color(
            "board_color",
            default=DEFAULT_BOARD_COLOR,
            choices=BOARD_COLOR_CHOICES,
            label="Board color",
        ),
    ],
)
def puzzle_for_date(month: int, day: int, board_color: str) -> APuzzleADaySolved:
    return APuzzleADaySolved(month=month, day=day, board_color=board_color)


def puzzle_today(board_color: str = "tan") -> APuzzleADaySolved:
    """Convenience helper for the github-io 'today' button."""
    today = _date.today()
    return APuzzleADaySolved(
        month=today.month, day=today.day, board_color=board_color
    )


__all__ = ["puzzle_for_date", "puzzle_today"]
