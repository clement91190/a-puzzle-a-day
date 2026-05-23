"""A single puzzle piece — one polyomino-outline polygon, extruded once."""

from __future__ import annotations

from typing import Iterable

from cadbuildr.foundation import (
    Extrusion,
    Line,
    Part,
    Point,
    Polygon,
    Sketch,
)

from ..solver.grid import trace_polyomino_outline
from .calendar_board import BOARD_SLAB_HEIGHT_MM, POCKET_DEPTH_MM
from .geometry import dedupe_collinear, grid_corner_to_mm

PIECE_HEIGHT_MM: float = POCKET_DEPTH_MM
"""Match the pocket so pieces sit flush with the slab top."""

PIECE_INSET_MM: float = 0.6
"""Shrink each piece toward its centroid so neighbours don't share faces."""


class PuzzlePiece(Part):
    """One polyomino piece. ``cells`` are absolute board ``(row, col)`` positions."""

    def __init__(
        self,
        cells: Iterable[tuple[int, int]],
        color: str,
        inset_mm: float = PIECE_INSET_MM,
    ):
        super().__init__()
        self._cells = list(cells)
        if not self._cells:
            raise ValueError("PuzzlePiece needs at least one cell")
        self._inset_mm = inset_mm
        self._build_extrusion()
        self.paint(color)

    def _build_extrusion(self) -> None:
        outline_grid = trace_polyomino_outline(self._cells)
        if len(outline_grid) < 3:
            raise ValueError(f"piece outline degenerate for cells={self._cells}")

        centroid_x = sum(c for _, c in self._cells) / len(self._cells) + 0.5
        centroid_y = sum(r for r, _ in self._cells) / len(self._cells) + 0.5
        cx_mm, cy_mm = grid_corner_to_mm(centroid_x, centroid_y)
        pull = self._inset_mm * 0.5

        mm_points: list[tuple[float, float]] = []
        for gc, gr in outline_grid:
            x, y = grid_corner_to_mm(gc, gr)
            dx, dy = cx_mm - x, cy_mm - y
            norm = max((dx * dx + dy * dy) ** 0.5, 1e-6)
            mm_points.append((x + dx / norm * pull, y + dy / norm * pull))

        mm_points = dedupe_collinear(mm_points)

        sketch = Sketch(self.xy())
        sk_points = [Point(sketch, x, y) for x, y in mm_points]
        lines = [
            Line(sk_points[i], sk_points[(i + 1) % len(sk_points)])
            for i in range(len(sk_points))
        ]
        polygon = Polygon(lines)
        pocket_floor = BOARD_SLAB_HEIGHT_MM - POCKET_DEPTH_MM
        self.add_operation(
            Extrusion(polygon, pocket_floor, pocket_floor + PIECE_HEIGHT_MM)
        )
