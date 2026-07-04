---
phase: 01-pin-runtime-dependencies-to-known-good
plan: 01
subsystem: infra
tags: [uv, uv-lock, typst, sphinx, docutils, tox, dependency-pinning, packaging]

# Dependency graph
requires: []
provides:
  - "Upper-bounded runtime pins in pyproject.toml (typst>=0.14.1,<0.15, sphinx>=5.0,<9, docutils>=0.18,<0.22), floors unchanged"
  - "Regenerated + committed uv.lock (typst 0.14.9) — now tracked as the reproducibility source of truth"
  - "tox.ini ceilings mirrored; dead sphinx-testing removed everywhere"
  - "Empirical local confirmation that docs-pdf builds a PDF with no `kai` error"
affects: [02-cross-os-matrix-verification, 03-python-floor-modernization, 05-lock-currency-enforcement]

# Tech tracking
tech-stack:
  added: []
  removed: [sphinx-testing]
  patterns: ["Committed uv.lock is the single reproducibility source of truth (D-02); pyproject expresses ranges, the lock pins the exact patch"]

key-files:
  created: []
  modified: [pyproject.toml, tox.ini, uv.lock, .gitignore, .planning/PROJECT.md]

key-decisions:
  - "Added upper bounds only (no == pins, floors unchanged) — exact patch carried by uv.lock (D-01/D-02)"
  - "Started tracking uv.lock (removed it from .gitignore) to satisfy PIN-03 — the repo previously gitignored it; flagged for maintainer review"
  - "sphinx<9 / docutils<0.22 ceilings are precautionary, not load-bearing for the kai break (D-03); still applied as guardrails"

patterns-established:
  - "Reproducibility via committed lock: plain `uv sync` in CI no longer silently re-resolves once the lock is tracked"

requirements-completed: [PIN-01, PIN-02, PIN-03, PIN-04, PIN-05, PIN-06]

coverage:
  - id: D1
    description: "pyproject.toml runtime deps carry upper bounds (typst<0.15, sphinx<9, docutils<0.22), floors unchanged, no == pins"
    requirement: "PIN-01"
    verification:
      - kind: automated
        ref: "grep -q 'typst>=0.14.1,<0.15' pyproject.toml && grep -q 'sphinx>=5.0,<9' pyproject.toml && grep -q 'docutils>=0.18,<0.22' pyproject.toml"
        status: pass
    human_judgment: false
  - id: D2
    description: "uv.lock regenerated, resolves cleanly, pins typst to 0.14.9, and is committed (now tracked)"
    requirement: "PIN-03"
    verification:
      - kind: automated
        ref: "uv lock --check (exit 0) && grep -A1 '^name = \"typst\"$' uv.lock | grep -qE 'version = \"0\\.14\\.'"
        status: pass
    human_judgment: false
  - id: D3
    description: "tox.ini [testenv]/[testenv:type] mirror the ceilings; no unbounded runtime declarations remain"
    requirement: "PIN-04"
    verification:
      - kind: automated
        ref: "! grep -nE 'sphinx>=5\\.0[^,]|docutils>=0\\.18[^,]' tox.ini"
        status: pass
    human_judgment: false
  - id: D4
    description: "Dead sphinx-testing dependency removed from pyproject.toml, tox.ini, and uv.lock"
    requirement: "PIN-05"
    verification:
      - kind: automated
        ref: "! grep -rq 'sphinx-testing' pyproject.toml tox.ini uv.lock"
        status: pass
    human_judgment: false
  - id: D5
    description: "docs-pdf builds a PDF with the pinned typst 0.14.9 and no `kai` error (local Linux confirmation)"
    requirement: "PIN-06"
    verification:
      - kind: e2e
        ref: "uv run tox -e docs-pdf -> docs/_build/pdf/index.pdf (2.3MB), exit 0, no 'kai' in output"
        status: pass
    human_judgment: false
  - id: D6
    description: "sphinx/docutils ceiling load-bearing finding recorded in PROJECT.md Key Decisions (precautionary, not load-bearing per D-03)"
    requirement: "PIN-06"
    verification:
      - kind: automated
        ref: "grep -qE '0\\.14\\.[0-9]' .planning/PROJECT.md && grep -qiE 'precautionary|load-bearing' .planning/PROJECT.md"
        status: pass
    human_judgment: false

# Metrics
duration: ~40min (incl. environment diagnosis)
completed: 2026-07-04
status: complete
---

# Phase 01 / Plan 01: Runtime Dependency Pin Summary

**Runtime deps pinned to a known-good set (typst 0.14.9, sphinx 7.4.7/8.1.3, docutils 0.21.2) with a regenerated, now-tracked uv.lock; docs-pdf builds a PDF locally with no `kai` error.**

## Performance

- **Duration:** ~40 min (a large share was diagnosing the NixOS toolchain, not the edits)
- **Completed:** 2026-07-04
- **Tasks:** 2
- **Files modified:** 5 (pyproject.toml, tox.ini, uv.lock, .gitignore, PROJECT.md)

## Accomplishments
- Added upper bounds to the three runtime deps (floors unchanged, no `==` pins); mirrored ceilings in `tox.ini` for documentation-truth.
- Removed the dead `sphinx-testing` dependency from `pyproject.toml`, `tox.ini`, and `uv.lock` (+ transitive `roman-numerals`, `six`).
- Regenerated `uv.lock` (typst 0.15.0→0.14.9, docutils→0.21.2, sphinx 9.x→7.4.7/8.1.3); `uv lock --check` passes.
- **Started tracking `uv.lock`** (removed from `.gitignore`) so the committed lock is the reproducibility source of truth (PIN-03).
- Empirically confirmed `docs-pdf` builds `index.pdf` with typst 0.14.9 and no `kai` error; recorded the confirmed patch + D-03 ceiling finding in `PROJECT.md`.

## Task Commits

1. **Task 1: Apply pins, mirror tox ceilings, remove sphinx-testing, regenerate + track lock** - `63f4284` (fix)
2. **Task 2: Confirm docs-pdf builds and record findings in PROJECT.md** - `138b517` (docs)

## Files Created/Modified
- `pyproject.toml` - runtime dep ceilings; removed sphinx-testing from `dev` extra
- `tox.ini` - mirrored ceilings in `[testenv]`/`[testenv:type]`; removed sphinx-testing
- `uv.lock` - regenerated (typst 0.14.9); **now tracked**
- `.gitignore` - un-ignored `uv.lock` (PIN-03)
- `.planning/PROJECT.md` - Key Decisions: confirmed typst patch + ceiling finding

## Decisions Made
- **Un-tracked → tracked `uv.lock`:** the repo gitignored `uv.lock` (never committed) and CI runs plain `uv sync` (silently re-resolves). PIN-03, RESEARCH, and the phase's core value all require the committed lock, so I removed the `.gitignore` line and committed the lock. This is a maintainer-facing convention change for a published library — **flagged for review** (trivially reversible: re-add the ignore line + `git rm --cached uv.lock`).
- Ceilings applied but documented as precautionary (D-03) — the `kai` break is purely the typst compiler version.

## Deviations from Plan

### 1. [Repo-state conflict] `uv.lock` was gitignored — started tracking it
- **Found during:** Task 1 commit (git silently dropped `uv.lock`).
- **Issue:** `.gitignore:81` excluded `uv.lock`; the plan/PIN-03 assume it is committed (planners worked in a scratch copy and didn't see the ignore rule).
- **Fix:** Removed the ignore line; amended the atomic pin commit to include `uv.lock` + `.gitignore`.
- **Verification:** `git ls-files uv.lock` returns the path; commit `63f4284` shows all four files.
- **Impact:** Fulfills PIN-03. Maintainer convention change — surfaced for veto.

### 2. [Environment] NixOS local-execution workarounds (no committed-code impact)
- **Issue:** This NixOS host has no working ELF loader for manylinux binaries (`/lib64/ld-linux` is `stub-ld`, `NIX_LD` unset). The pre-existing `.venv` was built on a uv-downloaded standalone CPython 3.14 that cannot start; `tox-uv` also shells out to a PyPI `uv` binary that cannot start.
- **Fix (local only):** Rebuilt `.venv` on the nix-native python 3.13.13; symlinked `.venv/bin/uv` → nix `uv` so `tox-uv` can provision the docs-pdf env. typst compiles in-process (C-extension via `dlopen`), so the PDF build works under nix-python.
- **Impact:** None on committed artifacts or CI — `.venv` is gitignored, and CI runs on `ubuntu-latest` where the PyPI binaries work natively. These are verification-environment workarounds, not changes to the project.

**Total deviations:** 2 (1 repo-state conflict resolved per PIN-03 + flagged; 1 environment workaround with no code impact).

## Issues Encountered
- Full NixOS toolchain diagnosis: `ruff` (a standalone native binary) genuinely cannot run locally — deferred to plan 01-02's handling (nixpkgs ruff / CI). typst and pure-Python tools DO run under nix-python once the broken venv is rebuilt.

## Next Phase Readiness
- The kai regression is fixed at the source (pyproject ceiling forbids typst 0.15) and pinned exactly via the committed lock.
- Phase 2 (cross-OS × Python matrix) is the authoritative gate for the ceiling/precautionary finding and full green CI — the local confirmation here is Linux-only.
- **Open item for maintainer:** confirm the decision to track `uv.lock` (vs. keeping it gitignored).

---
*Phase: 01-pin-runtime-dependencies-to-known-good*
*Completed: 2026-07-04*
