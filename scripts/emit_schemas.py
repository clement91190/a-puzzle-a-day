"""Emit parameters.schema.json for every @cadbuildr_project in the lego package.

Run from the lego package root::

    uv run python scripts/emit_schemas.py

Output is written into ``cadbuildr_projects/lego/parameters/`` so it ships
inside the wheel and is reachable from the SDK at runtime.
"""

from __future__ import annotations

from pathlib import Path

from cadbuildr.foundation.parameters.schema import emit_schemas_for_module

PROJECT_MODULE = "cadbuildr_projects.lego"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "cadbuildr_projects" / "lego" / "parameters"


def main() -> None:
    written = emit_schemas_for_module(PROJECT_MODULE, OUTPUT_DIR)
    if not written:
        raise SystemExit(f"No @cadbuildr_project entries found in {PROJECT_MODULE}.")
    print(f"Wrote {len(written)} schema(s) under {OUTPUT_DIR}:")
    for path in written:
        print(f"  - {path.relative_to(OUTPUT_DIR.parent.parent.parent)}")


if __name__ == "__main__":
    main()
