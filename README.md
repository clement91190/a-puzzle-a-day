# a-puzzle-a-day

Interactive 3D solver for the [Dragon Fjord A-Puzzle-A-Day](https://www.dragonfjord.com/product/a-puzzle-a-day/) calendar puzzle, built with [CADbuildr](https://cadbuildr.com).

Pick a date — eight polyomino pieces, one calendar board, exactly two cells uncovered.
The in-browser solver finds a valid arrangement, then the CADbuildr kernel renders it live.

➡️ **Live demo**: https://clement91190.github.io/a-puzzle-a-day/

## What's in here

```
├── a_puzzle_a_day/
│   ├── solver/     pure-logic: 7×7 grid, piece catalog, exact-cover search
│   └── cad/        foundation Parts + Assembly + mm conversion
├── examples/       runnable scripts (open the folder in CADbuildr Prototype to Play)
├── github-io/      React + R3F demo site (Vite, deploys to GitHub Pages)
└── pyproject.toml  the Python package — installable from this directory
```

The Python package builds the CAD geometry (board + pieces) and ships a solver.
The github-io site loads the Python package via Pyodide, calls
[`@cadbuildr/sdk-react`](https://www.npmjs.com/package/@cadbuildr/sdk-react)
to render the DAG through the CADbuildr kernel-api, and shows the result in
React Three Fiber.

## Run the demo site locally

```sh
cd github-io
npm install
npm run sync-puzzle-wheel    # build the Python wheel into public/local-puzzle/
npm run dev                  # open http://localhost:3008
```

You need a CADbuildr SDK session token (`cbv1.*`) to talk to the kernel-api.
Mint one from the [CADbuildr hub](https://cadbuildr.com) under
*Settings → SDK partner keys*, then put it in `github-io/.env.local`:

```ini
VITE_CADBUILDR_SESSION_TOKEN=cbv1.<jwt>
```

The default kernel-api host is `https://kernel-api.cadbuildr.com` — override
with `VITE_KERNEL_API_BASE_URL` if you're pointing at a dev deployment.

## Run the solver / CAD without the site

```sh
uv sync          # installs cadbuildr-foundation
uv run python examples/today.py    # builds today's solved arrangement
```

If you have [CADbuildr Prototype](https://cadbuildr.com/downloads) (our
desktop app), open this folder and press **Play** on `examples/today.py`
or `examples/board_only.py` to see the geometry in the workbench.

## Credits

- Original physical puzzle: [Dragon Fjord A-Puzzle-A-Day](https://www.dragonfjord.com/product/a-puzzle-a-day/)
- CAD framework: [CADbuildr foundation](https://github.com/cadbuildr/foundation)
- 3D rendering: [@cadbuildr/cad-kernel-r3f](https://github.com/cadbuildr/cad-kernel-r3f)
- Browser Python: [@cadbuildr/cad-pyodide-runtime](https://github.com/cadbuildr/cad-pyodide-runtime)
- React SDK: [@cadbuildr/sdk-react](https://github.com/cadbuildr/sdk-react)

MIT-licensed — see [LICENSE](LICENSE).
