"""Piece representation + orientation enumeration.

Pieces are sets of (row, col) cells. ``all_orientations`` returns the deduped
set of rotations + reflections — same piece, all unique placements relative to
its bounding-box top-left.

The solver works on these (row, col) tuples; rendering converts them to mm via
``BOARD_CELL_SIZE_MM`` in ``constants``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..constants import DEFAULT_PIECE_COLORS, PIECE_NAMES, PIECE_SHAPES


Cells = tuple[tuple[int, int], ...]


def _normalize(cells: Iterable[tuple[int, int]]) -> Cells:
    """Translate so the minimum row and column are 0, then sort."""
    items = list(cells)
    min_r = min(r for r, _ in items)
    min_c = min(c for _, c in items)
    return tuple(sorted((r - min_r, c - min_c) for r, c in items))


def _rotate90(cells: Cells) -> Cells:
    """(r, c) → (c, -r); normalize."""
    return _normalize((c, -r) for r, c in cells)


def _reflect(cells: Cells) -> Cells:
    """(r, c) → (r, -c); normalize."""
    return _normalize((r, -c) for r, c in cells)


def all_orientations(cells: Cells) -> tuple[Cells, ...]:
    """Return every unique rotation + reflection of ``cells`` (normalized)."""
    base = _normalize(cells)
    rotations = [base]
    for _ in range(3):
        rotations.append(_rotate90(rotations[-1]))
    reflected = [_reflect(o) for o in rotations]
    seen: set[Cells] = set()
    out: list[Cells] = []
    for orientation in rotations + reflected:
        if orientation in seen:
            continue
        seen.add(orientation)
        out.append(orientation)
    return tuple(out)


@dataclass(frozen=True)
class Piece:
    """A puzzle piece — name, shape, color, and all unique orientations."""

    name: str
    cells: Cells
    color: str

    @property
    def orientations(self) -> tuple[Cells, ...]:
        return all_orientations(self.cells)

    @property
    def size(self) -> int:
        return len(self.cells)


class PieceCatalog:
    """Lookup-by-name catalog of the canonical 8-piece Dragon Fjord set."""

    def __init__(self, pieces: list[Piece]):
        self._by_name = {p.name: p for p in pieces}
        self._ordered = list(pieces)

    def __iter__(self):
        return iter(self._ordered)

    def __len__(self):
        return len(self._ordered)

    def __getitem__(self, name: str) -> Piece:
        return self._by_name[name]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(p.name for p in self._ordered)


PIECES: PieceCatalog = PieceCatalog(
    [
        Piece(name=name, cells=PIECE_SHAPES[name], color=DEFAULT_PIECE_COLORS[name])
        for name in PIECE_NAMES
    ]
)
