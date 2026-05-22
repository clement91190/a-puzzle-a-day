"""The labelled calendar board — solid wooden slab with a single pocket cut.

Follows the lego ``LegoBrick`` shape: one ``__init__`` that calls a small set
of ``_build_*`` helpers, one *Extrusion* operation per helper. Label engraving
is intentionally a single SVG operation (commented out for now — re-enable
once the basic geometry is validated).
"""

from __future__ import annotations

from cadbuildr.foundation import (
    Extrusion,
    Line,
    Part,
    Point,
    Polygon,
    Rectangle,
    Sketch,
    SVGShape,
)

from ..constants import BOARD_CELL_SIZE_MM, BOARD_GRID, DEFAULT_BOARD_COLOR
from ..solver.grid import label_for_cell, labelled_cells, trace_polyomino_outline
from .geometry import dedupe_collinear, grid_corner_to_mm

BOARD_MARGIN_MM: float = 8.0
"""Wood border around the labelled playing field."""

BOARD_SLAB_HEIGHT_MM: float = 8.0
"""Full slab thickness."""

POCKET_DEPTH_MM: float = 4.0
"""Depth the pocket is cut into the slab. Pieces sit flush at this depth."""

ENGRAVE_DEPTH_MM: float = 0.5
"""Depth of the engraved text cut into the pocket floor."""


class CalendarBoard(Part):
    """Solid slab + single polygonal pocket sized to the 43 labelled cells."""

    def __init__(
        self,
        color: str = DEFAULT_BOARD_COLOR,
        engrave: bool = True,
        engrave_limit: int | None = None,
    ):
        """``engrave_limit`` engraves only the first N labelled cells; useful for
        benchmarking the kernel cost vs label count. ``None`` = all 43 cells."""
        super().__init__()
        self._build_slab()
        self._build_pocket()
        if engrave:
            self._engrave_labels(limit=engrave_limit)
        self.paint(color)

    def _build_slab(self) -> None:
        rows = len(BOARD_GRID)
        cols = len(BOARD_GRID[0])
        sketch = Sketch(self.xy())
        slab = Rectangle.from_center_and_sides(
            Point(sketch, 0.0, 0.0),
            cols * BOARD_CELL_SIZE_MM + 2 * BOARD_MARGIN_MM,
            rows * BOARD_CELL_SIZE_MM + 2 * BOARD_MARGIN_MM,
        )
        self.add_operation(Extrusion(slab, BOARD_SLAB_HEIGHT_MM))

    def _build_pocket(self) -> None:
        """One cut for the whole playing field. Polygon outline traces around the
        43 labelled cells — naturally skips the 6 corner voids."""
        outline_grid = trace_polyomino_outline(labelled_cells())
        outline_mm = dedupe_collinear(
            [grid_corner_to_mm(gc, gr) for gc, gr in outline_grid]
        )
        sketch = Sketch(self.xy())
        points = [Point(sketch, x, y) for x, y in outline_mm]
        lines = [
            Line(points[i], points[(i + 1) % len(points)])
            for i in range(len(points))
        ]
        polygon = Polygon(lines)
        pocket_floor = BOARD_SLAB_HEIGHT_MM - POCKET_DEPTH_MM
        self.add_operation(
            Extrusion(polygon, pocket_floor, BOARD_SLAB_HEIGHT_MM, cut=True)
        )

    def _engrave_labels(self, limit: int | None = None) -> None:
        """One ``<text>`` element per labelled cell — precise per-cell
        positioning (text-anchor middle at cell centre) at the cost of more
        per-element overhead in replicad's text processor.

        Geometry: replicad's ``parseSVG`` mirrors the imported drawing across
        the x-axis (svg y-down → CAD y-up). So we feed svg-y directly:
        row 0 = small svg-y → high CAD y after the mirror → top of the board.
        """
        rows = len(BOARD_GRID)
        cols = len(BOARD_GRID[0])
        canvas_w = cols * BOARD_CELL_SIZE_MM + 2 * BOARD_MARGIN_MM
        canvas_h = rows * BOARD_CELL_SIZE_MM + 2 * BOARD_MARGIN_MM

        cells = list(labelled_cells())
        if limit is not None:
            cells = cells[:limit]

        svg_texts: list[str] = []
        for row, col in cells:
            label = label_for_cell(row, col)
            x_mm = BOARD_MARGIN_MM + (col + 0.5) * BOARD_CELL_SIZE_MM
            y_mm = BOARD_MARGIN_MM + (row + 0.5) * BOARD_CELL_SIZE_MM
            font_size = "6" if len(label) > 2 else "7"
            svg_texts.append(
                f'<text x="{x_mm:.2f}" y="{y_mm:.2f}" '
                f'font-size="{font_size}" font-family="Arial" '
                f'text-anchor="middle" dominant-baseline="middle">{label}</text>'
            )

        svg_content = (
            f'<svg viewBox="0 0 {canvas_w:.2f} {canvas_h:.2f}" '
            f'xmlns="http://www.w3.org/2000/svg">\n'
            + "\n".join(svg_texts) + "\n"
            + "</svg>"
        )

        sketch = Sketch(self.xy())
        svg_shape = SVGShape(sketch, svg_content, scale=1.0)
        engrave_floor = BOARD_SLAB_HEIGHT_MM - POCKET_DEPTH_MM
        self.add_operation(
            Extrusion([svg_shape], engrave_floor - ENGRAVE_DEPTH_MM, engrave_floor, cut=True)
        )
