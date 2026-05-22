# a-puzzle-a-day github-io site

The React + React-Three-Fiber demo at https://cadbuildr.github.io/a-puzzle-a-day/.

## Stack

- **Vite + React 19** — UI shell, date picker, animations
- **Pyodide** — runs the Python `cadbuildr_projects.a_puzzle_a_day` solver in-browser
- **[@cadbuildr/cad-pyodide-runtime](https://www.npmjs.com/package/@cadbuildr/cad-pyodide-runtime)** — bootstraps Pyodide + installs the wheel from `public/local-puzzle/`
- **[@cadbuildr/sdk-react](https://www.npmjs.com/package/@cadbuildr/sdk-react)** — sends the DAG to the CADbuildr kernel-api, returns a mesh, renders it in R3F

## Local dev

```sh
npm install
npm run sync-puzzle-wheel   # one-time: builds ../dist/*.whl and copies into public/local-puzzle/
npm run dev                 # opens http://localhost:3008
```

## Configuration

`.env.local` (gitignored):

```ini
# Kernel-api host (defaults to the hosted CADbuildr kernel-api)
VITE_KERNEL_API_BASE_URL=https://kernel-api.cadbuildr.com

# Short-lived session token minted via /api/v1/sdk/session-tokens on the hub
VITE_CADBUILDR_SESSION_TOKEN=cbv1.<jwt>
```

## Production build

```sh
VITE_APP_BASE_PATH=/a-puzzle-a-day/ npm run build
```

Outputs `dist/`. The repo's GitHub Pages workflow runs that build and pushes
`dist/` to Pages.
