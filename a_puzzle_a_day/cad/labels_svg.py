"""Build the engraved-labels SVG for the calendar board.

Replicad's SVG parser is fast on ``<path>`` data and slow / unsupported on
``<text>`` (the kernel times out at ~30s with 43 text elements). So instead
of letting the kernel rasterize text, we render each character ourselves
as a 5x7 pixel bitmap, emit a single ``<path>`` containing one rectangular
sub-path per ON pixel across all labels, and let the kernel just tessellate
that path.

The font is hand-encoded for the characters that actually appear on the
board: ``J F M A S O N D B R P Y L U C V T G E`` (uppercase month
initials + helpers) plus digits ``0-9``. All-uppercase labels keep the
font table small and the engraving readable at 5 mm character height.
"""

from __future__ import annotations

from .geometry import grid_corner_to_mm
from ..constants import BOARD_CELL_SIZE_MM
from ..solver.grid import label_for_cell, labelled_cells


# ----------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 columns: '#' = on, '.' = off.
# Hand-traced to match common console fonts (vaguely IBM CP437 / minecraft).
# ----------------------------------------------------------------------------


def _decode(rows: tuple[str, ...]) -> tuple[tuple[int, int], ...]:
    out: list[tuple[int, int]] = []
    for ry, row in enumerate(rows):
        for cx, ch in enumerate(row):
            if ch == "#":
                out.append((cx, ry))
    return tuple(out)


FONT_W: int = 5
FONT_H: int = 7

_GLYPHS_SRC: dict[str, tuple[str, ...]] = {
    "A": (
        ".###.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    "B": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#...#",
        "#...#",
        "####.",
    ),
    "C": (
        ".###.",
        "#...#",
        "#....",
        "#....",
        "#....",
        "#...#",
        ".###.",
    ),
    "D": (
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ),
    "E": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#####",
    ),
    "F": (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "G": (
        ".###.",
        "#...#",
        "#....",
        "#.###",
        "#...#",
        "#...#",
        ".###.",
    ),
    "J": (
        "..###",
        "....#",
        "....#",
        "....#",
        "....#",
        "#...#",
        ".###.",
    ),
    "L": (
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ),
    "M": (
        "#...#",
        "##.##",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
    ),
    "N": (
        "#...#",
        "##..#",
        "##..#",
        "#.#.#",
        "#..##",
        "#..##",
        "#...#",
    ),
    "O": (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "P": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    "R": (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    "S": (
        ".####",
        "#....",
        "#....",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    "T": (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "U": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    "V": (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
    ),
    "Y": (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "0": (
        ".###.",
        "#...#",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        ".###.",
    ),
    "1": (
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ),
    "2": (
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#####",
    ),
    "3": (
        ".###.",
        "#...#",
        "....#",
        "..##.",
        "....#",
        "#...#",
        ".###.",
    ),
    "4": (
        "...#.",
        "..##.",
        ".#.#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ),
    "5": (
        "#####",
        "#....",
        "####.",
        "....#",
        "....#",
        "#...#",
        ".###.",
    ),
    "6": (
        ".###.",
        "#...#",
        "#....",
        "####.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "7": (
        "#####",
        "....#",
        "...#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    "8": (
        ".###.",
        "#...#",
        "#...#",
        ".###.",
        "#...#",
        "#...#",
        ".###.",
    ),
    "9": (
        ".###.",
        "#...#",
        "#...#",
        ".####",
        "....#",
        "#...#",
        ".###.",
    ),
}

GLYPHS: dict[str, tuple[tuple[int, int], ...]] = {
    ch: _decode(rows) for ch, rows in _GLYPHS_SRC.items()
}


# ----------------------------------------------------------------------------
# SVG generation
# ----------------------------------------------------------------------------


def _glyph_pixel_rects(
    ch: str,
    origin_x_mm: float,
    origin_y_mm: float,
    pixel_mm: float,
) -> list[tuple[float, float, float, float]]:
    """List of ``(x, y, w, h)`` rectangles for one glyph's ON pixels."""
    pixels = GLYPHS.get(ch)
    if not pixels:
        return []
    out: list[tuple[float, float, float, float]] = []
    for cx, ry in pixels:
        x = origin_x_mm + cx * pixel_mm
        # SVG y grows downward; align so row 0 is at the top of the glyph.
        y = origin_y_mm + ry * pixel_mm
        out.append((x, y, pixel_mm, pixel_mm))
    return out


def _label_text_for(row: int, col: int) -> str:
    """Uppercase + truncate to the chars the font supports."""
    raw = label_for_cell(row, col).upper()
    return "".join(ch for ch in raw if ch in GLYPHS)


def _format_path_subpaths(rects: list[tuple[float, float, float, float]]) -> str:
    parts: list[str] = []
    for x, y, w, h in rects:
        parts.append(f"M{x:.2f} {y:.2f}h{w:.2f}v{h:.2f}h{-w:.2f}z")
    return "".join(parts)


def build_labels_svg(
    pixel_mm: float = 0.55,
    intercell_gap_mm: float = 0.6,
) -> str:
    """Return a single ``<svg>`` with one ``<path>`` carrying every labelled
    cell's engraving. Coordinates are in board millimetres; the viewBox is
    a 1:1 mm canvas so ``SVGShape(..., scale=1.0)`` plants it flush with
    the board sketch.

    Glyphs are ``FONT_W × FONT_H`` cells at ``pixel_mm`` per cell — so a
    3-character month label like ``JAN`` is roughly
    ``(3 * FONT_W + 2) * pixel_mm`` mm wide. ``intercell_gap_mm`` is the
    spacing between adjacent characters in a label.
    """
    glyph_w_mm = FONT_W * pixel_mm
    glyph_h_mm = FONT_H * pixel_mm
    rects: list[tuple[float, float, float, float]] = []

    for row, col in labelled_cells():
        label = _label_text_for(row, col)
        if not label:
            continue
        n_chars = len(label)
        label_width_mm = n_chars * glyph_w_mm + (n_chars - 1) * intercell_gap_mm

        # Cell centre in board mm — `grid_corner_to_mm` reports CAD coords
        # where ``+y`` is UP. The SVG sketch's y axis is flipped on the way
        # to the kernel, so we generate SVG with ``+y`` down and pass it
        # straight through; the inversion happens inside the kernel.
        cell_corner_x_mm, _cell_corner_y_mm_cad = grid_corner_to_mm(
            col + 0.5, row + 0.5
        )
        # `grid_corner_to_mm` was tuned for the CAD pocket polygon. For SVG
        # we want a y that grows downward as ``row`` grows. Re-derive:
        #   center_x = -cols/2 * cell + (col + 0.5) * cell
        #   center_y =  (row + 0.5 - rows/2) * cell    (svg-y-down)
        # Both are in mm and centred on the slab.
        from ..constants import BOARD_GRID
        rows_total = len(BOARD_GRID)
        cols_total = len(BOARD_GRID[0])
        cx_mm = -cols_total * BOARD_CELL_SIZE_MM / 2.0 + (col + 0.5) * BOARD_CELL_SIZE_MM
        cy_mm = -rows_total * BOARD_CELL_SIZE_MM / 2.0 + (row + 0.5) * BOARD_CELL_SIZE_MM

        # Top-left of the label, centred in the cell.
        origin_x_mm = cx_mm - label_width_mm / 2.0
        origin_y_mm = cy_mm - glyph_h_mm / 2.0

        cursor_x = origin_x_mm
        for ch in label:
            rects.extend(_glyph_pixel_rects(ch, cursor_x, origin_y_mm, pixel_mm))
            cursor_x += glyph_w_mm + intercell_gap_mm

    # ViewBox spans the slab. The actual board polygon may be a bit larger
    # than the cells (slab margin) but the kernel doesn't care — the sketch
    # placement is what positions the engraving.
    half_w = cols_total * BOARD_CELL_SIZE_MM / 2.0
    half_h = rows_total * BOARD_CELL_SIZE_MM / 2.0
    d_attr = _format_path_subpaths(rects)
    return (
        f'<svg viewBox="{-half_w:.2f} {-half_h:.2f} {2*half_w:.2f} {2*half_h:.2f}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<path d="{d_attr}"/>'
        f"</svg>"
    )
