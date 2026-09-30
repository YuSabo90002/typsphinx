# Phase 64: FHS Wrapper and Command Shims in `flake.nix` - Pattern Map

**Mapped:** 2026-09-03
**Files analyzed:** 1 source file (edited), several evidence-markdown files (created)
**Analogs found:** 1 / 1 for the source edit; 4 / 4 for the evidence-file convention

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `flake.nix` (edited in place) | config (Nix flake outputs — devShell/derivation definitions) | transform (declarative build-graph construction, no runtime request/response) | `flake.nix` itself (pre-edit state) | exact — this phase edits its own existing structure, it does not create a sibling file |
| `.planning/phases/64-.../64-<NAME>-EVIDENCE.md` (one or more, per D-05) | test / evidence (verbatim command-transcript record, no code) | batch (record-and-append, not executed by any program) | `.planning/milestones/v0.9.2-phases/63-*/63-CI-EVIDENCE.md`, `63-GREEN-TREE-EVIDENCE.md`, `62-*/62-RED-EVIDENCE.md` | exact — same convention family, same milestone-adjacent project |

Only one tracked source file is in scope (`flake.nix`, git-tracked: confirmed via `git ls-files -- flake.nix` → non-empty). No `.nix` module split, no `scripts/`, no `tests/` file — D-05 and the discretion item both keep everything inline. The evidence file(s) are markdown, not source, but are listed here because the orchestrator notes require them and the planner needs a concrete naming/structure convention to assign to plans.

## Pattern Assignments

### `flake.nix` (config, transform — edited in place)

**Analog:** `flake.nix`'s own current 40-line body (self-analog; there is no second Nix file in this repository to compare against).

**Current full structure** (all 40 lines — this is the base the edit lands on):
```nix
{
  description = "typsphinx development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.nodejs
              pkgs.pnpm
              pkgs.git
              # Python toolchain: uv for fast dependency/venv management.
              pkgs.python3
              pkgs.uv
            ];
          };
        }
      );
    };
}
```

**Per-system structure to hang the Linux guard off** (lines 21-38, `forAllSystems` + inner `let pkgs = pkgsFor system;`): this is the exact seam CONTEXT/RESEARCH point to — `lib.optionals stdenv.hostPlatform.isLinux (...)` wraps the shim-list expression at the point it is spliced into `packages`, and the `fhsRun`/`findVenvBin`/`venvShims`/`uvShim` bindings go in the same inner `let` block (line 23-25) that already holds `pkgs = pkgsFor system;`, so Nix's laziness keeps them unforced on darwin. No restructuring of `forAllSystems`/`pkgsFor` (lines 17-18) is needed — RESEARCH.md's Code Context section states this explicitly.

**Core pattern to add** (from RESEARCH.md Code Examples §1, the `pkgs.steam-run` idiom — one `buildFHSEnv` + N `writeShellScriptBin` shims):
```nix
fhsRun = pkgs.buildFHSEnv {
  name = "typsphinx-fhs-run";
  runScript = "${pkgs.writeShellScript "fhs-passthrough" ''exec "$@"''}";
};

findVenvBin = tool: ''
  dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -x "$dir/.venv/bin/${tool}" ]; then
      echo "$dir/.venv/bin/${tool}"
      exit 0
    fi
    dir="$(dirname "$dir")"
  done
  echo "typsphinx: ${tool}: no .venv/bin/${tool} found walking up from $PWD" >&2
  exit 127
'';

venvShimNames = [ "tox" "ruff" "black" "mypy" "pytest" "sphinx-build" ];
venvShims = map (
  cmd:
  pkgs.writeShellScriptBin cmd ''
    set -euo pipefail
    target="$(${pkgs.writeShellScript "find-${cmd}" (findVenvBin cmd)})"
    exec ${fhsRun}/bin/typsphinx-fhs-run "$target" "$@"
  ''
) venvShimNames;

uvShim = pkgs.writeShellScriptBin "uv" ''
  set -euo pipefail
  if [ -x "$PWD/.venv/bin/uv" ]; then
    target="$PWD/.venv/bin/uv"
  else
    target="${pkgs.uv}/bin/uv"
  fi
  exec ${fhsRun}/bin/typsphinx-fhs-run "$target" "$@"
'';
```
This is a sketch to guide task breakdown (RESEARCH.md's own caveat), not a literal patch — the plan owns the exact not-found message wording and exit code (CONTEXT discretion items).

**`packages` list edit point** (`flake.nix:28-35`, inside the existing `mkShell`):
```nix
packages = [
  pkgs.nodejs
  pkgs.pnpm
  pkgs.git
  # Python toolchain: uv for fast dependency/venv management.
  pkgs.python3
  pkgs.uv
] ++ pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux (
  [ uvShim ] ++ venvShims
) ++ pkgs.lib.optionals (!pkgs.stdenv.hostPlatform.isLinux) [ pkgs.uv ];
```
Note the PATH-ordering finding (RESEARCH.md, verified live this session): earlier `packages` entries win same-named-binary collisions, so `uvShim` must precede any unconditional `pkgs.uv` in the merged list; the darwin branch keeps `pkgs.uv` unconditionally (`packages` byte-identical to today's list per CONTEXT discretion) while Linux drops the unconditional `pkgs.uv` and substitutes the shim.

**No error-handling/try-catch pattern applies** — this is declarative Nix, not imperative application code. The equivalent "error handling" is the shim's own shell-script body: `set -euo pipefail`, the upward `.venv` walk terminating at `/` with a named stderr message and `exit 127` (D-03's hard-fail requirement), versus `uv`'s two-leg fallback to a fixed store path (D-02's sole exception — no other shim gets a second leg).

**No auth/validation pattern applies** — no request boundary exists in this file.

---

### Evidence markdown (`64-*-EVIDENCE.md`, one or more files per D-05)

**Analogs:** `.planning/milestones/v0.9.2-phases/63-*/63-CI-EVIDENCE.md`, `63-GREEN-TREE-EVIDENCE.md`, `.planning/milestones/v0.9.2-phases/62-*/62-RED-EVIDENCE.md`.

**Structural pattern common to all three** (extracted from the files read in full above):
1. `# Phase <N> — <short label> (<criterion reference, e.g. "SC#4">)` heading.
2. A `## <section>` per logically distinct measurement (e.g. `## Pre-dispatch confirmation`, `## Provisioning and tree identity`, `## RED run (unfixed tree, ...)`).
3. Every shell interaction is a fenced ` ``` ` block using the literal `$ <command>` prompt convention followed by real (not paraphrased) stdout/stderr, e.g.:
   ```
   $ git rev-parse HEAD
   225c6618ffd94ec5e1601de538438c47b4d558a9
   ```
4. Prose immediately after each transcript states *why* the transcript proves what it proves — never a bare dump with no interpretation (see `63-CI-EVIDENCE.md`'s "Exit 0, no drift..." paragraph and `63-GREEN-TREE-EVIDENCE.md`'s "The imported `typsphinx.__file__` real path lies inside this worktree's own directory tree..." paragraph).
5. Machine-specific absolute paths are substituted with a bracketed placeholder (`<BUILD_DIR>`, `<REPO_ROOT>`) when they carry no evidentiary weight, with an explicit sentence stating that the substitution happened and why (see `62-RED-EVIDENCE.md`'s "Two substitutions were made to the transcript below...").
6. Restore/verification commands are stated explicitly before the "real" transcript, e.g. `62-RED-EVIDENCE.md`'s "**Restore command:**" and "**Build command:**" bold-labeled lines.

**Naming convention to follow (D-05's own reference, RESEARCH.md Summary):** avoid the verifier-reserved `64-VERIFICATION.md` name (per `gsd-verifier-clobbers-verification-md` memory and the Phase 63 precedent of `63-CI-EVIDENCE.md` / `63-GREEN-TREE-EVIDENCE.md`, and Phase 62's `62-RED-EVIDENCE.md`). Suggested per-requirement split, mirroring Phase 63's split into a dispatch half and a local-measurement half:
- `64-NIX05-WORKTREE-EVIDENCE.md` (D-04/D-09 — fresh-worktree provisioning + session-PATH inheritance `command -v` check)
- `64-NIX07-RENAME-EVIDENCE.md` (the rename-the-target proof, RESEARCH.md Code Examples §5)
- `64-NIX08-ENV-EVIDENCE.md` (the `$HOME`/`TMPDIR`/`/etc`/locale measurement, RESEARCH.md Code Examples §6, D-08)
- `64-CI-EVIDENCE.md` (SC#5's dispatch + 3-OS lane observation, mirroring `63-CI-EVIDENCE.md`'s structure exactly, including the branch-census / decoy-pair check per the `milestone-branch-decoy-pair` memory)

Exact filenames and split granularity are explicitly left to the planner/executor (CONTEXT discretion item: "Plan split granularity, and the name/location of the evidence file(s) D-05 refers to").

---

## Shared Patterns

### Absolute-path resolution (NIX-07 / Pitfall 1)
**Source:** RESEARCH.md Pattern 1 / Anti-Patterns / Code Examples §5 (no existing codebase Nix analog beyond `flake.nix` itself — this is a new mechanism this phase introduces, not a copy of prior repository code).
**Apply to:** every one of the seven shims. No `command -v <tool>` or bare `exec <tool> "$@"` anywhere inside a shim body — only the upward `.venv` walk's resolved absolute path, or `uv`'s fixed `${pkgs.uv}/bin/uv` store path.

### Evidence-file transcript discipline
**Source:** `63-CI-EVIDENCE.md`, `63-GREEN-TREE-EVIDENCE.md`, `62-RED-EVIDENCE.md` (see full excerpts above).
**Apply to:** every evidence file this phase writes for NIX-05/06/07/08 and SC#5. `$ <command>` / real-output fenced blocks, immediate interpretive prose, explicit placeholder substitution when a path is machine-specific.

### Worktree-isolated execution provisioning line
**Source:** `CLAUDE.md` § "Worktree-isolated execution" (verbatim, load-bearing per D-04/D-06/D-09):
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run pytest   # run ALL subsequent commands via `uv run`
```
**Apply to:** the D-04 verification locus for NIX-01 through NIX-04 (must run in a freshly created worktree, never the main tree) and the D-09 `command -v ruff` / `command -v uv` reachability check that precedes it.

### `tox.ini`'s `changedir = docs` constraint
**Source:** `tox.ini:65,73` — `docs-html`/`docs-pdf` environments run with `changedir = docs`.
**Apply to:** the shim's `.venv` resolution must be an upward walk from `$PWD`, never a bare `$PWD/.venv/bin/<tool>`, or it silently fails whenever `tox` (or a human) invokes a shimmed command from inside `docs/`.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `fhsRun` derivation body / shim shell-script bodies (new Nix expressions within `flake.nix`) | config / utility (shell-script generation) | event-driven (invoked per bare-command call, not on a schedule) | No prior `buildFHSEnv` or `writeShellScriptBin` usage exists anywhere in this repository; RESEARCH.md's own analog is external (`pkgs.steam-run` in nixpkgs itself, not this codebase) — the planner should treat RESEARCH.md's Code Examples §1 sketch as the primary source, not a repository analog |

## Metadata

**Analog search scope:** repository root (`flake.nix`, `.envrc`, `tox.ini`, `CLAUDE.md`), `.planning/milestones/v0.9.2-phases/62-*/`, `.planning/milestones/v0.9.2-phases/63-*/`.
**Files scanned:** `flake.nix` (full, 40 lines), `.envrc` (full, 1 line), `tox.ini` (lines 1-20), `63-CI-EVIDENCE.md` (head), `63-GREEN-TREE-EVIDENCE.md` (head), `62-RED-EVIDENCE.md` (head), plus full read of `64-CONTEXT.md` and `64-RESEARCH.md` (pages 1 through Code Examples §6).
**Tracked-source gate:** `git ls-files -- flake.nix .envrc` confirmed both tracked (non-empty output for both); no gitignored mirror paths were named anywhere in this document.
**Pattern extraction date:** 2026-09-03
