---
phase: 10-version-string-fix-v0-5-0-release
plan: 01
subsystem: packaging
tags: [versioning, importlib-metadata, uv-lock, tomllib, drift-guard, release-prep]

# Dependency graph
requires:
  - phase: 09-green-ci-matrix-smoke-test-guardrails
    provides: "Observed all-green CI on PR #112 (release/v0.5.0 -> main), left unmerged for Phase 10 to add the version-bump commit"
provides:
  - "typsphinx.__version__ single-sourced from installed-distribution metadata (importlib.metadata.version) instead of a hardcoded string, with a PackageNotFoundError -> 'unknown' fallback"
  - "pyproject.toml [project].version bumped 0.4.4 -> 0.5.0 as the sole version literal in the repo"
  - "uv.lock regenerated in lockstep so uv sync --locked (and the ci.yml examples job) stays green"
  - "An independent tomllib-based drift-guard test (test_version_matches_pyproject_toml) that fails CI if the two ever diverge again"
affects: [10-02-changelog, gsd-complete-milestone]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "importlib.metadata.version(dist_name) + except PackageNotFoundError fallback for self-reported package version (mirrors the existing typsphinx/pdf.py::get_typst_version precedent)"
    - "Independent tomllib re-parse of pyproject.toml as a drift guard, distinct from the runtime code path under test (avoids tautological assertions)"

key-files:
  created: []
  modified:
    - typsphinx/__init__.py
    - pyproject.toml
    - uv.lock
    - tests/test_extension.py

key-decisions:
  - "Used the sentinel string \"unknown\" for the PackageNotFoundError fallback (not a version-looking literal), matching typsphinx/pdf.py's existing convention"
  - "Kept test_setup_version_matches unchanged (validates setup() wiring) and added test_version_matches_pyproject_toml as a genuinely independent second check, per plan instruction to keep both"

patterns-established:
  - "Single-source-of-truth versioning: pyproject.toml [project].version is the only place a version literal may live; everything else (including __version__) derives from installed package metadata at runtime"

requirements-completed: [REL-01]

coverage:
  - id: D1
    description: "typsphinx.__version__ derives from importlib.metadata.version(\"typsphinx\") with a PackageNotFoundError -> \"unknown\" fallback; reports 0.5.0 at runtime"
    requirement: "REL-01"
    verification:
      - kind: unit
        ref: "tests/test_extension.py::test_setup_version_matches"
        status: pass
      - kind: other
        ref: "uv run python -c \"import typsphinx; assert typsphinx.__version__ == '0.5.0'\""
        status: pass
    human_judgment: false
  - id: D2
    description: "pyproject.toml [project].version bumped 0.4.4 -> 0.5.0; uv.lock regenerated in lockstep; uv sync --locked exits 0"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "uv sync --extra dev --locked"
        status: pass
    human_judgment: false
  - id: D3
    description: "New independent tomllib-based drift-guard test proves __version__ matches pyproject.toml via a code path separate from the one __version__ itself uses"
    requirement: "REL-01"
    verification:
      - kind: unit
        ref: "tests/test_extension.py::test_version_matches_pyproject_toml"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full suite + black/ruff/mypy stay green on release/v0.5.0 after the version-fix edits"
    verification:
      - kind: unit
        ref: "uv run pytest (413/413 passed)"
        status: pass
      - kind: other
        ref: "uv run black --check . && uv run ruff check . && uv run mypy typsphinx/"
        status: pass
    human_judgment: false

# Metrics
duration: 5min
completed: 2026-07-11
status: complete
---

# Phase 10 Plan 01: Single-Source Version Fix Summary

**`typsphinx.__version__` now derives from `importlib.metadata.version("typsphinx")` with a `PackageNotFoundError` fallback, `pyproject.toml` bumped 0.4.4 -> 0.5.0 as the sole version literal, `uv.lock` regenerated, and a new independent `tomllib` drift-guard test added — closing the root cause of the stale `0.4.3` string.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-07-11T10:58:32Z
- **Completed:** 2026-07-11T11:03:00Z
- **Tasks:** 2/2
- **Files modified:** 4 (`typsphinx/__init__.py`, `pyproject.toml`, `uv.lock`, `tests/test_extension.py`)

## Accomplishments
- Reworked `typsphinx/__init__.py` to compute `__version__` from installed-distribution metadata (`importlib.metadata.version("typsphinx")`) instead of a hardcoded literal, with a `PackageNotFoundError -> "unknown"` fallback mirroring the existing `typsphinx/pdf.py::get_typst_version` pattern
- Bumped `pyproject.toml [project].version` `0.4.4 -> 0.5.0` (now the sole version literal in the repo) and regenerated `uv.lock` in the same task (`uv lock` + `uv sync --extra dev`), confirmed `uv sync --extra dev --locked` exits 0
- Added `tests/test_extension.py::test_version_matches_pyproject_toml`, an independent `tomllib`-based parse of `pyproject.toml` that asserts equality with `typsphinx.__version__` — a genuine (non-tautological) drift guard, distinct from the `importlib.metadata` code path `__version__` itself uses
- Kept the existing `test_setup_version_matches` unchanged; confirmed full suite (413/413) plus `black --check`/`ruff check`/`mypy typsphinx/` all green on `release/v0.5.0`

## Task Commits

Each task was committed atomically:

1. **Task 1: Single-source `__version__` via `importlib.metadata`, bump pyproject 0.4.4 -> 0.5.0, regenerate uv.lock** - `6fffbf2` (feat)
2. **Task 2: Add independent tomllib drift-guard test; keep the tautological one; prove full suite + lint/type green** - `1ca76d9` (test)

_Note: No plan-metadata commit hash yet — the final `docs(10-01): complete plan` commit is created after this SUMMARY is written, per the execution protocol._

## Files Created/Modified
- `typsphinx/__init__.py` - `__version__` reworked from `= "0.4.3"` literal to a try/except around `importlib.metadata.version("typsphinx")`, falling back to `"unknown"` on `PackageNotFoundError`
- `pyproject.toml` - `[project].version` bumped `0.4.4` -> `0.5.0`
- `uv.lock` - regenerated so the embedded `typsphinx` workspace-member version matches `0.5.0`
- `tests/test_extension.py` - new `test_version_matches_pyproject_toml` drift-guard function appended; `test_setup_version_matches` untouched

## Decisions Made
- Chose the sentinel string `"unknown"` (not a version-looking string) for the `PackageNotFoundError` fallback, per research Anti-Patterns guidance and to match the existing `typsphinx/pdf.py` convention
- Kept both version-related tests (`test_setup_version_matches` for `setup()` wiring, `test_version_matches_pyproject_toml` for the genuine drift guard) rather than replacing one with the other, per plan instruction

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `uv sync` (without `--extra dev`) stripped dev dependencies, breaking `pytest`/`ruff` invocation**
- **Found during:** Task 2 (running the full pytest/lint/type gate)
- **Issue:** The plan's Task 1 action said "run `uv sync`"; a plain `uv sync` only installs the base dependency group and removed `pytest`, `ruff`, `black`, `mypy`, `tox`, etc. from `.venv`, causing `uv run pytest`/`uv run ruff check .` to fail with "Failed to spawn". CLAUDE.md documents the correct dev-install command as `uv sync --extra dev`.
- **Fix:** Ran `uv sync --extra dev` (and used `uv sync --extra dev --locked` for all subsequent lockfile-currency checks) to restore dev tooling into `.venv` without touching `uv.lock` (dev extras were already resolved and locked; only the local venv install was affected).
- **Files modified:** None (local `.venv` install state only; `uv.lock` unchanged by this fix)
- **Verification:** `uv sync --extra dev --locked` exits 0; `uv run pytest`/`uv run ruff check .`/`uv run black --check .`/`uv run mypy typsphinx/` all run and pass
- **Committed in:** N/A (no repo file changed; local environment fix only)

**2. [Rule 3 - Blocking] Regenerated `.venv/bin/{uv,uvx,ruff}` lost their NixOS-patched ELF interpreter, causing 45 pre-existing test failures and a `ruff` spawn failure**
- **Found during:** Task 2 (full suite + lint gate)
- **Issue:** `uv lock`/`uv sync` in Task 1 regenerated `.venv`, which reinstalled generic-Linux `uv`/`uvx`/`ruff` binaries with a glibc dynamic-linker interpreter incompatible with NixOS ("Could not start dynamically linked executable"). This is the exact pre-existing, previously-documented sandbox issue from Phase 8.1 (PROJECT.md: "Patched `.venv/bin/uv` ELF interpreter via patchelf... incidentally fixed ~45 pre-existing environment-caused test failures"), reintroduced because `.venv` is gitignored/regenerable and got rebuilt in this task.
- **Fix:** Re-applied the same local, gitignored, no-repo-file-touched `patchelf --set-interpreter <nix-glibc-ld.so> .venv/bin/{uv,uvx,ruff}` fix used previously in Phase 8.1, using the interpreter already baked into the Nix-provided `uv` on `PATH` as the reference.
- **Files modified:** None (gitignored `.venv/` binaries only, not tracked in the repo)
- **Verification:** Full suite went from 45 failed/368 passed to 413/413 passed; `uv run ruff check .` went from a spawn failure to "All checks passed!"
- **Committed in:** N/A (no repo file changed; local environment fix only, consistent with the prior Phase 8.1 precedent)

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking, both local-environment-only, neither touched a tracked repo file)
**Impact on plan:** Both fixes were necessary to actually run the plan's own verification/acceptance commands in this sandbox; neither altered `typsphinx/__init__.py`, `pyproject.toml`, `uv.lock`, or `tests/test_extension.py` beyond what Task 1/Task 2 already specified. No scope creep into release/publish actions (scope fence respected — no tag, no push, no PyPI publish, no merge).

## Issues Encountered
None beyond the two auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `typsphinx.__version__` and `pyproject.toml [project].version` both report `0.5.0`; `uv.lock` is in sync (`uv sync --extra dev --locked` exits 0)
- Full suite (413/413) + `black`/`ruff`/`mypy` all green on `release/v0.5.0`
- Plan 10-02 (CHANGELOG entry) can proceed; PR #112 (`release/v0.5.0 -> main`) remains open and untouched, ready to receive this version-bump commit before re-triggering checks and merging at milestone close
- No tag was created, nothing was pushed to a remote, no PyPI publish occurred, and `main` was not touched — all deferred to `/gsd-complete-milestone` per the scope fence

---
*Phase: 10-version-string-fix-v0-5-0-release*
*Completed: 2026-07-11*

## Self-Check: PASSED

- FOUND: typsphinx/__init__.py
- FOUND: tests/test_extension.py
- FOUND: pyproject.toml
- FOUND: uv.lock
- FOUND: 6fffbf2 (Task 1 commit)
- FOUND: 1ca76d9 (Task 2 commit)
