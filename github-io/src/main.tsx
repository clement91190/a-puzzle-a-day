import React from "react";
import ReactDOM from "react-dom/client";
import { format } from "date-fns";
import { AnimatePresence, motion } from "framer-motion";
import {
  Calendar as CalendarIcon,
  ExternalLink,
  Github,
  Puzzle,
  Sparkles,
  Sun,
} from "lucide-react";
import { DayPicker } from "react-day-picker";
import "react-day-picker/dist/style.css";

import { type KernelDag } from "@cadbuildr/cad-kernel-r3f";
import {
  initializeCadPyodideRuntime,
  runCadPythonCode,
  type PyodideLike,
} from "@cadbuildr/cad-pyodide-runtime";
import { CadbuildrProvider, CadbuildrViewer } from "@cadbuildr/sdk-react";

import { resolveKernelApiBaseUrl } from "./kernelApiEnv";
import { LOCAL_PUZZLE_URL_SEGMENT, LOCAL_PUZZLE_WHEEL_FILE } from "./puzzleLocal";
import "./styles.css";

const FOUNDATION_IMPORT_PATH =
  (import.meta.env.VITE_FOUNDATION_IMPORT_PATH as string | undefined) ?? "cadbuildr.foundation";
const FOUNDATION_PACKAGE_NAME =
  (import.meta.env.VITE_FOUNDATION_PACKAGE_NAME as string | undefined) ?? "cadbuildr-foundation";
const FOUNDATION_VERSION =
  (import.meta.env.VITE_FOUNDATION_VERSION as string | undefined) ?? "^0.2.0";
const FOUNDATION_DAG_UTILS_PATH = `${FOUNDATION_IMPORT_PATH}.dag_utils`;

const PUZZLE_IMPORT_PATH =
  (import.meta.env.VITE_PUZZLE_IMPORT_PATH as string | undefined) ??
  "cadbuildr_projects.a_puzzle_a_day";

const PUZZLE_PACKAGE_REQUIREMENT =
  (import.meta.env.VITE_PUZZLE_PACKAGE_REQUIREMENT as string | undefined) ?? "";

function resolvePuzzleWheelUrl(): string {
  const fromEnv = (import.meta.env.VITE_PUZZLE_PACKAGE_WHEEL_URL as string | undefined)?.trim();
  if (fromEnv) return fromEnv;
  if (typeof window === "undefined") return "";
  return new URL(
    `${LOCAL_PUZZLE_URL_SEGMENT}/${LOCAL_PUZZLE_WHEEL_FILE}`,
    window.location.origin + import.meta.env.BASE_URL,
  ).href;
}

const SCENE_BG = "#141a1c";
const MESH_SCENE_POSITION: [number, number, number] = [0, 0, 0];
const CAD_Z_UP_TO_Y_UP: [number, number, number] = [-Math.PI / 2, 0, 0];

const PIECE_SHAPES: Record<string, ReadonlyArray<readonly [number, number]>> = {
  // Pentominoes (5 cells each)
  Plus: [[0, 1], [1, 0], [1, 1], [1, 2], [2, 1]],
  L: [[0, 0], [1, 0], [2, 0], [3, 0], [3, 1]],
  P: [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0]],
  U: [[0, 0], [0, 2], [1, 0], [1, 1], [1, 2]],
  Z: [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]],
  // Tetrominoes (4 cells each)
  TTet: [[0, 0], [0, 1], [0, 2], [1, 1]],
  LTet: [[0, 0], [1, 0], [2, 0], [2, 1]],
  STet: [[0, 1], [0, 2], [1, 0], [1, 1]],
  Square: [[0, 0], [0, 1], [1, 0], [1, 1]],
};

// CSS swatch approximations for each piece (legend only). The 3D render uses
// the foundation `paint` named colors from the Python constants.
const PIECE_SWATCH_HEX: Record<string, string> = {
  Plus: "#C91A09",
  L: "#E87724",
  P: "#F2CD37",
  U: "#2DB6BD",
  Z: "#7A3F9F",
  TTet: "#36AEBF",
  LTet: "#C58FE8",
  STet: "#E89BAD",
  Square: "#FFBCD1",
};

const PIECE_NAMES = Object.keys(PIECE_SHAPES);

function buildFoundationCompatibilityScript(foundationImportPath: string): string {
  return `
from importlib import import_module
import sys
import types

foundation = import_module(${JSON.stringify(foundationImportPath)})
_submodules = ("gen", "gen.models", "gen.runtime", "dag_utils", "utils", "helpers", "constants")
for _prefix in ("cad_package", "cadbuildr"):
    legacy_alias = _prefix + ".foundation"
    sys.modules[legacy_alias] = foundation
    _root = sys.modules.get(_prefix)
    if _root is None:
        _root = types.ModuleType(_prefix)
        _root.__path__ = []
        sys.modules[_prefix] = _root
    setattr(_root, "foundation", foundation)
    for _suffix in _submodules:
        try:
            _mod = import_module(${JSON.stringify(foundationImportPath)} + "." + _suffix)
        except ModuleNotFoundError:
            continue
        sys.modules[legacy_alias + "." + _suffix] = _mod
`.trim();
}

function buildFoundationShowRebindScript(foundationImportPath: string): string {
  return `
import builtins
from importlib import import_module

_root = import_module(${JSON.stringify(foundationImportPath)})
_dag_utils = import_module(${JSON.stringify(foundationImportPath)} + ".dag_utils")
_hook = builtins.show
_root.show = _hook
_dag_utils.show = _hook
`.trim();
}

function buildPuzzleInstallScript(args: {
  packageRequirement: string;
  wheelUrl?: string;
  importPath: string;
}): string {
  return `
import importlib
import micropip

wheel_url = ${JSON.stringify(args.wheelUrl ?? "")}
package_requirement = ${JSON.stringify(args.packageRequirement)}
import_path = ${JSON.stringify(args.importPath)}
install_errors = []

try:
    importlib.import_module(import_path)
    _needs_install = False
except Exception:
    _needs_install = True

if _needs_install and wheel_url:
    try:
        await micropip.install(wheel_url, deps=False)
    except Exception as error:
        install_errors.append(f"wheel install failed: {error}")

if _needs_install and package_requirement:
    try:
        await micropip.install(package_requirement, deps=False)
    except Exception as error:
        install_errors.append(f"package install failed: {error}")

try:
    importlib.import_module(import_path)
except Exception as error:
    message = "\\n".join(install_errors) if install_errors else "No install attempt was made."
    raise RuntimeError(
        "Failed to import puzzle package '" + import_path + "'. "
        + message
        + "\\nLocal dev: run uv build in the Python package directory (parent of github-io/). "
        + "Production: copy the wheel to public/local-puzzle/ or set VITE_PUZZLE_PACKAGE_WHEEL_URL."
    ) from error
`.trim();
}

function buildPuzzlePythonScript(month: number, day: number, boardColor: string): string {
  // Avoid the @cadbuildr_project-decorated entry point — older foundation pypi
  // wheels don't ship the Color/Int/Enum descriptors yet. The plain
  // APuzzleADaySolved assembly is descriptor-free and renders fine.
  return `
from ${FOUNDATION_IMPORT_PATH} import show
from ${PUZZLE_IMPORT_PATH} import APuzzleADaySolved

show(APuzzleADaySolved(month=${month}, day=${day}, board_color=${JSON.stringify(boardColor)}))
`.trim();
}

const BOARD_COLORS: Array<{ key: string; label: string; hex: string }> = [
  { key: "tan", label: "Natural tan", hex: "#DBC093" },
  { key: "dark_tan", label: "Dark tan", hex: "#A78D60" },
  { key: "reddish_brown", label: "Mahogany", hex: "#5A3220" },
  { key: "dark_bluish_gray", label: "Slate", hex: "#6C6E68" },
  { key: "black", label: "Black", hex: "#1A1A1A" },
];

function App() {
  const [selectedDate, setSelectedDate] = React.useState<Date>(() => new Date());
  const [calendarMonth, setCalendarMonth] = React.useState<Date>(() => new Date());
  const [boardColor, setBoardColor] = React.useState<string>(BOARD_COLORS[0].key);
  const [dag, setDag] = React.useState<KernelDag | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [runtimeReady, setRuntimeReady] = React.useState(false);
  const [isSolving, setIsSolving] = React.useState(false);

  const pyodideRef = React.useRef<PyodideLike | null>(null);
  const runCounterRef = React.useRef(0);

  const kernelApiBaseUrl = React.useMemo(() => resolveKernelApiBaseUrl(), []);
  // Public keyId (Stripe-publishable-key pattern) — safe to ship in the
  // bundle. The CADbuildr SDK mints a short-lived cbv1 session token on
  // mount via hub's /api/v1/sdk/session-tokens browser flow, then refreshes
  // before expiry. The hub enforces the partner's `allowed_origins`
  // allowlist against the browser's `Origin` header so this `keyId` cannot
  // be reused from a different site.
  const sdkKeyId = React.useMemo(
    () =>
      (import.meta.env.VITE_CADBUILDR_SDK_KEY_ID as string | undefined)?.trim() || undefined,
    [],
  );
  // Optional pre-minted server-flow token (kept for parity with the
  // earlier setup; only honored if no `sdkKeyId` is provided).
  const sessionToken = React.useMemo(
    () =>
      sdkKeyId
        ? undefined
        : (import.meta.env.VITE_CADBUILDR_SESSION_TOKEN as string | undefined)?.trim() || undefined,
    [sdkKeyId],
  );
  // Hub URL the SDK calls in keyId mode. Defaults to prod.
  const hubBaseUrl = React.useMemo(
    () =>
      (import.meta.env.VITE_CADBUILDR_HUB_BASE_URL as string | undefined)?.trim() || undefined,
    [],
  );

  React.useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      try {
        setError(null);
        console.info("[puzzle] bootstrap: starting Pyodide");
        const pyodide = await initializeCadPyodideRuntime({
          packages: {
            foundation: FOUNDATION_VERSION,
            foundationPackageName: FOUNDATION_PACKAGE_NAME,
          },
          foundationImportPath: FOUNDATION_IMPORT_PATH,
          foundationDagUtilsPath: FOUNDATION_DAG_UTILS_PATH,
        });
        if (cancelled) return;
        console.info("[puzzle] bootstrap: pyodide loaded, running foundation compat");
        await pyodide.runPythonAsync(buildFoundationCompatibilityScript(FOUNDATION_IMPORT_PATH));
        console.info("[puzzle] bootstrap: foundation compat done, rebinding show");
        await pyodide.runPythonAsync(buildFoundationShowRebindScript(FOUNDATION_IMPORT_PATH));
        console.info("[puzzle] bootstrap: show rebound, installing puzzle wheel", resolvePuzzleWheelUrl());
        await pyodide.runPythonAsync(
          buildPuzzleInstallScript({
            packageRequirement: PUZZLE_PACKAGE_REQUIREMENT,
            wheelUrl: resolvePuzzleWheelUrl(),
            importPath: PUZZLE_IMPORT_PATH,
          }),
        );
        if (cancelled) return;
        console.info("[puzzle] bootstrap: ready");
        pyodideRef.current = pyodide;
        (window as unknown as { __puzzlePyodide?: PyodideLike }).__puzzlePyodide = pyodide;
        setRuntimeReady(true);
      } catch (runtimeError) {
        if (cancelled) return;
        const message =
          runtimeError instanceof Error ? runtimeError.message : String(runtimeError);
        console.error("[puzzle] bootstrap failed:", message);
        setError(message);
      }
    }
    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  React.useEffect(() => {
    console.info("[puzzle] solve effect fired", {
      runtimeReady,
      hasRef: !!pyodideRef.current,
      month: selectedDate.getMonth() + 1,
      day: selectedDate.getDate(),
      boardColor,
    });
    if (!runtimeReady || !pyodideRef.current) return;

    const runId = ++runCounterRef.current;
    let cancelled = false;
    const month = selectedDate.getMonth() + 1;
    const day = selectedDate.getDate();
    const script = buildPuzzlePythonScript(month, day, boardColor);

    async function solve() {
      try {
        setIsSolving(true);
        setError(null);
        console.info("[puzzle] solve: running Python", { runId, month, day });
        const result = await runCadPythonCode(pyodideRef.current as PyodideLike, script, {
          foundationImportPath: FOUNDATION_IMPORT_PATH,
          foundationDagUtilsPath: FOUNDATION_DAG_UTILS_PATH,
        });
        if (cancelled || runId !== runCounterRef.current) {
          console.info("[puzzle] solve: stale run discarded", { runId });
          return;
        }
        const nextDag = (result.dag as KernelDag | null) ?? null;
        console.info("[puzzle] solve: DAG captured", {
          runId,
          hasDag: !!nextDag,
          dagNodeCount: nextDag && typeof nextDag === "object" && "DAG" in nextDag
            ? Object.keys((nextDag as { DAG?: object }).DAG ?? {}).length
            : 0,
        });
        setDag(nextDag);
      } catch (runError) {
        if (cancelled || runId !== runCounterRef.current) return;
        const message = runError instanceof Error ? runError.message : String(runError);
        console.error("[puzzle] solve failed:", message);
        setError(message);
      } finally {
        if (!cancelled && runId === runCounterRef.current) {
          setIsSolving(false);
        }
      }
    }
    void solve();
    return () => {
      cancelled = true;
    };
  }, [boardColor, runtimeReady, selectedDate]);

  const longDate = format(selectedDate, "EEEE, MMMM d");
  const isoDate = format(selectedDate, "yyyy-MM-dd");

  return (
    <div className="page">
      <header className="topbar">
        <span className="brand">
          <span className="dot" /> a puzzle a day
        </span>
        <span className="links">
          <a
            href="https://www.dragonfjord.com/product/a-puzzle-a-day/"
            target="_blank"
            rel="noreferrer"
          >
            The physical puzzle <ExternalLink size={12} style={{ verticalAlign: "-1px" }} />
          </a>
          <a href="https://github.com/clement91190/a-puzzle-a-day" target="_blank" rel="noreferrer">
            <Github size={14} style={{ verticalAlign: "-2px", marginRight: 4 }} />
            Source
          </a>
        </span>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <motion.h1
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            One puzzle, <span className="emph">every day of the year.</span>
          </motion.h1>
          <motion.p
            className="lead"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
          >
            <em>The Whole Year Puzzle</em> hides nine wooden polyomino pieces (5 pentominoes
            + 4 tetrominoes) in a 7×7 calendar grid. For any (month, day), at least one
            arrangement leaves exactly those two cells visible — pick a date below and the
            in-browser solver lays out a valid arrangement, rendered live with the CADbuildr
            kernel.
          </motion.p>
          <div className="badges">
            <span className="badge">9 pieces · 41 squares</span>
            <span className="badge gray">Pyodide → kernel-api → R3F</span>
            <span className="badge gray">CADbuildr SDK demo</span>
          </div>
        </div>

        <motion.aside
          className="today-card"
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.18, duration: 0.5, ease: "easeOut" }}
        >
          <span className="label">
            <Sun size={14} /> Showing
          </span>
          <span className="date">{format(selectedDate, "MMM d")}</span>
          <span className="subdate">{longDate}</span>
          <div className="actions">
            <button
              type="button"
              className="btn primary"
              onClick={() => {
                const today = new Date();
                setSelectedDate(today);
                setCalendarMonth(today);
              }}
            >
              <Sparkles size={14} /> Today
            </button>
            <button
              type="button"
              className="btn ghost"
              onClick={() => {
                const random = randomDate();
                setSelectedDate(random);
                setCalendarMonth(random);
              }}
            >
              Surprise me
            </button>
          </div>
        </motion.aside>
      </section>

      <section className="workspace">
        <div className="panel">
          <h2>
            <CalendarIcon size={18} /> Pick a date
          </h2>
          <p className="panel-hint">
            Months sit on rows 0–1; days fill rows 2–6. The two cells you choose stay
            uncovered.
          </p>
          <DayPicker
            mode="single"
            selected={selectedDate}
            onSelect={(date) => {
              if (date) {
                setSelectedDate(date);
                setCalendarMonth(date);
              }
            }}
            month={calendarMonth}
            onMonthChange={setCalendarMonth}
            showOutsideDays
            captionLayout="dropdown"
            fromYear={1970}
            toYear={2100}
          />

          <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 8 }}>
            <span
              style={{
                fontSize: 12,
                letterSpacing: "0.08em",
                color: "var(--cb-text-soft)",
                textTransform: "uppercase",
              }}
            >
              Board color
            </span>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {BOARD_COLORS.map((c) => (
                <button
                  key={c.key}
                  type="button"
                  className="btn ghost"
                  style={{
                    padding: "8px 10px",
                    background:
                      boardColor === c.key
                        ? "rgba(232, 119, 36, 0.18)"
                        : "rgba(255,255,255,0.03)",
                    borderColor:
                      boardColor === c.key ? "var(--cb-orange)" : "var(--cb-border)",
                  }}
                  onClick={() => setBoardColor(c.key)}
                  aria-pressed={boardColor === c.key}
                  aria-label={`Set board color to ${c.label}`}
                >
                  <span
                    style={{
                      display: "inline-block",
                      width: 16,
                      height: 16,
                      borderRadius: 4,
                      background: c.hex,
                      border: "1px solid rgba(0,0,0,0.18)",
                    }}
                  />
                  <span style={{ fontSize: 12 }}>{c.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="panel viewer-panel">
          <div className="viewer-header">
            <span className="who">
              <Puzzle size={12} /> {format(selectedDate, "MMMM d, yyyy")}
            </span>
            <span className="who">ISO {isoDate}</span>
          </div>

          <AnimatePresence>
            {error ? (
              <motion.div
                key="err"
                className="viewer-status error"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {error}
              </motion.div>
            ) : !runtimeReady ? (
              <motion.div
                key="boot"
                className="viewer-status"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <span className="spinner" /> Booting in-browser Python runtime…
              </motion.div>
            ) : isSolving ? (
              <motion.div
                key="solve"
                className="viewer-status"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <span className="spinner" /> Solving…
              </motion.div>
            ) : null}
          </AnimatePresence>

          <CadbuildrProvider
            baseUrl={kernelApiBaseUrl}
            hubBaseUrl={hubBaseUrl}
            keyId={sdkKeyId}
            sessionToken={sdkKeyId ? undefined : sessionToken}
            projectKey="a-puzzle-a-day"
          >
            <CadbuildrViewer
              dag={dag}
              background={SCENE_BG}
              cameraPosition={[140, 120, 160]}
              fov={42}
              meshPosition={MESH_SCENE_POSITION}
              meshRotation={CAD_Z_UP_TO_Y_UP}
              onRender={() => setError(null)}
              onError={(meshError) => setError(meshError.message)}
            />
          </CadbuildrProvider>
        </div>
      </section>

      <section className="panel">
        <h2>
          <Puzzle size={18} /> The nine pieces
        </h2>
        <p className="panel-hint">
          The Whole Year Puzzle set: 5 pentominoes + 4 tetrominoes. Their combined area is
          exactly 41 squares — what's left after we remove the 6 board voids and the 2
          (month, day) slots.
        </p>
        <div className="pieces">
          {PIECE_NAMES.map((name) => (
            <PieceCard key={name} name={name} />
          ))}
        </div>
      </section>

      <section className="about">
        <div className="panel about-card">
          <h3>
            <Sparkles size={14} /> The math
          </h3>
          <p>
            7 × 7 grid = 49 cells. The board hides 6 voids (top-right pair + centered-notch
            quartet), the date hides 2 more cells, leaving 41 to cover with 9 pieces totalling
            41 cells. There's always a solution; on most dates, many.
          </p>
        </div>
        <div className="panel about-card">
          <h3>
            <Puzzle size={14} /> The solver
          </h3>
          <p>
            Backtracking exact cover. Picks the next empty (row, col) as the anchor and tries
            every rotation + reflection of every remaining piece. Returns the first valid
            arrangement.
          </p>
        </div>
        <div className="panel about-card">
          <h3>
            <CalendarIcon size={14} /> The stack
          </h3>
          <p>
            In-browser Python via Pyodide, rendered through the public CADbuildr kernel-api,
            and presented with the same SDK any partner can embed in their storefront.
          </p>
        </div>
      </section>

      <footer className="foot">
        <a className="powered-by" href="https://cadbuildr.com" target="_blank" rel="noreferrer">
          <span>Powered by</span>
          <img src="cadbuildr-logo.svg" alt="CADbuildr" />
          <span className="cb">CADbuildr</span>
        </a>
        <span className="foot-meta">The Whole Year Puzzle.</span>
      </footer>
    </div>
  );
}

function PieceCard({ name }: { name: string }) {
  const cells = PIECE_SHAPES[name];
  const maxRow = Math.max(...cells.map((c) => c[0])) + 1;
  const maxCol = Math.max(...cells.map((c) => c[1])) + 1;
  const filled = new Set(cells.map((c) => `${c[0]},${c[1]}`));
  const color = PIECE_SWATCH_HEX[name];
  return (
    <div className="piece-card" title={`${name} — ${cells.length} cells`}>
      <span className="name">{name}</span>
      <div
        className="piece-shape"
        style={
          {
            gridTemplateRows: `repeat(${maxRow}, 12px)`,
            gridTemplateColumns: `repeat(${maxCol}, 12px)`,
            ["--piece-color"]: color,
          } as React.CSSProperties
        }
      >
        {Array.from({ length: maxRow * maxCol }).map((_, idx) => {
          const r = Math.floor(idx / maxCol);
          const c = idx % maxCol;
          const isFilled = filled.has(`${r},${c}`);
          return <span key={`${r}-${c}`} className={`cell${isFilled ? " filled" : ""}`} />;
        })}
      </div>
      <span style={{ fontSize: 11, color: "var(--cb-text-soft)" }}>{cells.length} cells</span>
    </div>
  );
}

function randomDate(): Date {
  const month = 1 + Math.floor(Math.random() * 12);
  const maxDay = new Date(new Date().getFullYear(), month, 0).getDate();
  const day = 1 + Math.floor(Math.random() * maxDay);
  const d = new Date();
  d.setMonth(month - 1, day);
  return d;
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(<App />);
