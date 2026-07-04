---
phase: 01-pin-runtime-dependencies-to-known-good
plan: 02
subsystem: infra
tags: [black, ruff, lint, formatting, code-style]

# Dependency graph
requires: []
provides:
  - "Tree is black-clean (black --check . exits 0)"
  - "Tree is ruff-clean (ruff check . exits 0)"
affects: [02-cross-os-matrix-verification]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Lint/format changes land as standalone commits, separate from dependency/config changes (D-04)"]

key-files:
  created: []
  modified: [docs/build_multilang.py, tests/test_config_other_options.py, tests/test_config_toctree_defaults.py]

key-decisions:
  - "ruff verified locally with nixpkgs ruff 0.15.14 (NixOS-patched) because the pinned 0.15.20 wheel is a native binary that cannot run on this host; CI runs the exact 0.15.20 (authoritative)"

patterns-established:
  - "Formatting confined to the 3 drifted files; [tool.black]/[tool.ruff] config untouched (target-version stays py39)"

requirements-completed: [LINT-01, LINT-02]

coverage:
  - id: D1
    description: "black --check . exits 0 on the full tree; exactly the 3 research-named files reformatted, 46 unchanged"
    requirement: "LINT-01"
    verification:
      - kind: automated
        ref: "black --check . -> exit 0 (49 files unchanged after reformatting 3)"
        status: pass
    human_judgment: false
  - id: D2
    description: "ruff check . exits 0 on the full tree (no findings; config not loosened)"
    requirement: "LINT-02"
    verification:
      - kind: automated
        ref: "ruff check . -> 'All checks passed!' exit 0 (local: nixpkgs ruff 0.15.14; CI: pinned 0.15.20)"
        status: pass
    human_judgment: false

# Metrics
duration: ~10min
completed: 2026-07-04
status: complete
---

# Phase 01 / Plan 02: Lint-Clean Tree Summary

**Tree is now black- and ruff-clean: black reformatted exactly the 3 drifted files, ruff reports zero findings — landed as a style commit separate from the pin change.**

## Performance

- **Duration:** ~10 min
- **Completed:** 2026-07-04
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- `black .` reformatted exactly the 3 research-named files (`docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`); 46 files unchanged. `black --check .` exits 0.
- `ruff check .` reports **All checks passed** (zero findings) — LINT-02 already satisfied, no fixup commit needed.
- Kept the reformat separate from the 01-01 pin change (D-04) for clean `git blame` and an unambiguous red/green CI signal.

## Task Commits

1. **Task 1: Apply the black reformat** - `f17c3d9` (style)
2. **Task 2: Confirm ruff is clean** - no commit (zero findings)

## Files Created/Modified
- `docs/build_multilang.py` - blank line inserted between module docstring and first import
- `tests/test_config_other_options.py` - multi-line `write_text(...)` calls collapsed to black's hugged-paren style
- `tests/test_config_toctree_defaults.py` - multi-line `write_text(...)` calls collapsed

## Decisions Made
- Verified `ruff` locally with **nixpkgs ruff 0.15.14** (NixOS-patched, runs on this host) because the pinned `ruff 0.15.20` wheel is a standalone native binary that cannot start on this NixOS box (no working ELF loader). Both are 0.15.x and read the same `[tool.ruff]` config, so the local check faithfully mirrors CI; the authoritative `0.15.20` run happens on `ubuntu-latest` in CI.

## Deviations from Plan

### 1. [Environment] ruff run via nixpkgs binary instead of the venv wheel
- **Found during:** Task 2 (ruff check).
- **Issue:** `uv run ruff` / `.venv/bin/ruff` is the PyPI native binary (0.15.20) which cannot execute on NixOS (stub-ld, no `NIX_LD`).
- **Fix:** Ran `nix run nixpkgs#ruff -- check .` (0.15.14, NixOS-patched). Same rule set, clean result.
- **Impact:** None on committed code (no fixups were needed anyway). CI runs the exact pinned ruff.

**Total deviations:** 1 (environment-only; no code impact).

## Issues Encountered
- None for the reformat itself. The only friction was the NixOS native-binary limitation on ruff, handled via the nixpkgs stand-in.

## Next Phase Readiness
- Lint gate is green locally; CI (`tox -e lint` on ubuntu-latest) will confirm with the pinned ruff 0.15.20.
- Combined with 01-01, the tree is pinned + lint-clean — ready for Phase 2's full cross-OS × Python matrix verification.

---
*Phase: 01-pin-runtime-dependencies-to-known-good*
*Completed: 2026-07-04*
