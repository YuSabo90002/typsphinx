---
phase: 03-modernize-python-floor-3-10-3-13
plan: 02
subsystem: ci
tags: [ruff, black, pyupgrade, tomllib, tomli, github-actions, ci, docs-build, python3.10]

# Dependency graph
requires:
  - phase: 03-modernize-python-floor-3-10-3-13 (Plan 01)
    provides: pyproject.toml requires-python >=3.10, regenerated uv.lock, tox.ini py310-py313, ci.yml/docs.yml/release.yml pinned to the 3.10 floor
provides:
  - A fully green ci.yml + docs.yml CI run on PR #104 proving the Python 3.10-3.13 floor bump is safe
  - typsphinx source modernized to py310+ ruff target (Optional[X] -> X | None, explicit zip strict=)
  - docs/source/conf.py resilient to the 3.10 floor via a tomli backport for tomllib
affects: [any future phase touching typsphinx/translator.py, typsphinx/builder.py, typsphinx/pdf.py, typsphinx/template_engine.py, docs/source/conf.py, or CI workflow floors]

# Tech tracking
tech-stack:
  added: ["tomli>=2.0 (docs optional-dependency, python_version < '3.11' only)"]
  patterns:
    - "try/except ModuleNotFoundError backport pattern for stdlib modules that are version-gated (tomllib 3.11+)"
    - "PEP 604 X | None union syntax replacing typing.Optional across the codebase now that the floor is 3.10+"

key-files:
  created: []
  modified:
    - typsphinx/builder.py
    - typsphinx/pdf.py
    - typsphinx/template_engine.py
    - typsphinx/translator.py
    - tests/test_entry_points.py
    - docs/source/conf.py
    - pyproject.toml
    - uv.lock

key-decisions:
  - "Remediated both RED CI jobs in-batch on the existing PR #104 branch rather than opening a new PR (Option-2 deviation, consistent with the D-01 push->observe / reuse pattern already logged for this plan)"
  - "Applied ruff --fix then --fix --unsafe-fixes in two explicit steps, verifying B905 fixes produced strict=False (not strict=True) since the zipped path-component lists can differ in length"
  - "Declared tomli only in the docs optional-dependency group (not project-wide) since only docs/source/conf.py needs it and only docs.yml installs --extra docs on the 3.10 floor"

requirements-completed: [PYVER-01, PYVER-02, PYVER-03, PYVER-04]

coverage:
  - id: D1
    description: "Ruff target-version py310 unlocks 25 UP045/UP007/B905/UP036 errors, all fixed; ruff check reports 0 errors and black --check stays clean"
    requirement: PYVER-03
    verification:
      - kind: unit
        ref: "nix run nixpkgs#ruff -- check . (All checks passed!)"
        status: pass
      - kind: unit
        ref: "uv run black --check . (50 files would be left unchanged)"
        status: pass
      - kind: unit
        ref: "uv run pytest tests/ -q -m 'not integration and not slow' (402 passed)"
        status: pass
  - id: D2
    description: "docs/source/conf.py builds on the 3.10 floor via tomli backport; tomli declared in docs optional-deps; uv.lock diff is minimal (only the new dependency edge)"
    requirement: PYVER-02
    verification:
      - kind: unit
        ref: "uv run python -c \"import conf; print(conf.version)\" (prints 0.4.3)"
        status: pass
      - kind: other
        ref: "git diff uv.lock (2 lines added: docs group + requires-dist entry, tomli stays pinned 2.4.1, no unrelated bumps)"
        status: pass
  - id: D3
    description: "Full ci.yml matrix (12 test jobs + lint + type-check + coverage + build + 2 integration) and docs.yml build-docs green on PR #104 head caf779d, proving the 3.10-3.13 floor bump is CI-clean"
    requirement: PYVER-02
    verification:
      - kind: e2e
        ref: "gh run view 28709010375 --json jobs -q '[.jobs[].conclusion] | unique' -> [\"success\"]"
        status: pass
      - kind: e2e
        ref: "gh run view 28709010382 --json jobs -q '[.jobs[].conclusion] | unique' -> [\"success\"]"
        status: pass
    human_judgment: true
    rationale: "Phase-gate human-verify checkpoint (Task 3) requires developer confirmation before Phase 3 is marked done and before the PR is merged; not auto-passed even though automated CI signals are green."

duration: ~20min
completed: 2026-07-04
status: complete
---

# Phase 03 Plan 02: CI Remediation and Green Re-observation Summary

**Fixed 25 ruff pyupgrade/B905 errors unlocked by the py310 target-version bump and backported tomllib via tomli for docs.yml's 3.10 floor, re-pushed PR #104, and confirmed both ci.yml (18 jobs) and docs.yml conclude green.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-04T14:21:36Z
- **Tasks:** 2 remediation commits + re-push + re-observation (in-batch fix inside the existing 03-02 plan's push->observe flow)
- **Files modified:** 8 (4 source files, 1 test file, conf.py, pyproject.toml, uv.lock)

## Accomplishments

- Ruff `check --fix` (21 safe UP045/UP007 fixes) + `check --fix --unsafe-fixes` (2x B905 `strict=False`, 2x UP036 dead-branch removal) reduced ruff errors from 25 to 0; confirmed `black --check` stayed clean and `pytest` (402 tests, non-integration/non-slow) passed unchanged
- `docs/source/conf.py` now falls back to the `tomli` backport when `tomllib` is unavailable (Python < 3.11), fixing the docs.yml `ModuleNotFoundError` introduced by Plan 01's setup-python 3.11->3.10 floor drop
- `tomli>=2.0; python_version < '3.11'` declared in `pyproject.toml`'s `docs` optional-dependency group (the group docs.yml actually installs); `uv lock` (no `--upgrade`) produced a minimal 2-line diff — tomli stays pinned at 2.4.1, no unrelated version bumps
- Re-pushed the two remediation commits (fast-forward, no force) to PR #104's branch `gsd/phase-2-verify-green-baseline`; both ci.yml and docs.yml re-fired on the new head `caf779d` and concluded green

## Task Commits

1. **Ruff/pyupgrade remediation** - `f2465ff` (style) — `style(03-02): modernize typsphinx for py310 ruff target (UP045/UP007/B905/UP036)`
2. **tomllib->tomli backport** - `caf779d` (fix) — `fix(03-02): backport tomllib via tomli for the 3.10 docs floor`

**Plan metadata:** (this commit, `docs(03-02): ...`) — records the green re-observation

## Files Created/Modified

- `typsphinx/builder.py` - `Optional[str]`/`Optional[Set[str]]` -> `str | None` / `Set[str] | None`
- `typsphinx/pdf.py` - Same UP045 modernization; removed now-unused `Optional` import
- `typsphinx/template_engine.py` - 9 `Optional[X]` params -> `X | None` across `TemplateEngine.__init__` and helper methods
- `typsphinx/translator.py` - `Optional[List[str]]`/`Optional[Any]` -> `X | None`; both `zip()` calls in the path-common-prefix helpers gained explicit `strict=False`
- `tests/test_entry_points.py` - Removed the dead pre-3.10 `entry_points()` fallback branch (UP036), keeping only the 3.10+ `select()` path; unused `sys` import dropped
- `docs/source/conf.py` - `import tomllib` -> try/except backport importing `tomli as tomllib` on ModuleNotFoundError
- `pyproject.toml` - Added `"tomli>=2.0; python_version < '3.11'"` to the `docs` optional-dependencies group
- `uv.lock` - Regenerated via plain `uv lock` (no `--upgrade`); added the `tomli` dependency edge to the `docs` group and `requires-dist`, no other changes

## Decisions Made

- Reused the existing PR #104 / branch `gsd/phase-2-verify-green-baseline` for the remediation rather than opening a new PR — consistent with the plan's already-logged Option-2 deviation (push->observe on the same branch)
- Verified both B905 unsafe-fixes produced `strict=False` (not `strict=True`) before proceeding, per the orchestrator's explicit review — `strict=True` would have been a correctness regression since the zipped path-component lists can differ in length
- Scoped the tomli dependency to the `docs` optional-dependency group only (not project-wide `dependencies`) since only `conf.py` needs it, and only `docs.yml`'s `uv sync --extra dev --extra docs` installs that group on the 3.10 floor

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] 25 ruff errors unlocked by the target-version py39->py310 bump (D-03 contingency, orchestrator pre-reviewed)**
- **Found during:** CI observation on PR #104 (head ee2f9ae) — logged as a blocker in STATE.md before this remediation session
- **Issue:** `[tool.ruff] target-version` moved py39->py310 in Plan 01, unlocking pyupgrade rules (UP045 Optional->X|None x20, UP007 Union->X|Y x1, B905 zip-strict x2, UP036 outdated version-block x2)
- **Fix:** `nix run nixpkgs#ruff -- check --fix .` (21 safe fixes) then `--fix --unsafe-fixes` (4 reviewed fixes); confirmed `strict=False` on both B905 sites; confirmed `black --check` and full non-integration test suite unaffected
- **Files modified:** typsphinx/builder.py, typsphinx/pdf.py, typsphinx/template_engine.py, typsphinx/translator.py, tests/test_entry_points.py
- **Verification:** `nix run nixpkgs#ruff -- check .` -> All checks passed; `uv run black --check .` -> clean; `uv run pytest tests/ -q -m "not integration and not slow"` -> 402 passed
- **Committed in:** f2465ff

**2. [Rule 1 - Bug] docs.yml build-docs ModuleNotFoundError: tomllib (D-... setup-python floor drop side effect)**
- **Found during:** CI observation on PR #104 (head ee2f9ae) — logged as a blocker in STATE.md before this remediation session
- **Issue:** Plan 01 lowered docs.yml's `setup-python` from 3.11 to 3.10, but `docs/source/conf.py` imported `tomllib` unconditionally; `tomllib` is stdlib only on Python 3.11+
- **Fix:** try/except backport importing `tomli` as `tomllib` on `ModuleNotFoundError`; declared `tomli>=2.0; python_version < '3.11'` in the `docs` optional-dependency group (the group docs.yml installs); ran plain `uv lock` (no `--upgrade`) producing a minimal 2-line diff
- **Files modified:** docs/source/conf.py, pyproject.toml, uv.lock
- **Verification:** Local `import conf` smoke test passes; docs.yml build-docs job green on re-observation (run 28709010382)
- **Committed in:** caf779d

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs surfaced by Plan 01's config changes, pre-reviewed by the orchestrator before dispatch)
**Impact on plan:** Both fixes were required to make the PR CI-green; no scope creep beyond the two RED jobs identified. No unrelated dependency or version changes rode along (confirmed via `git diff uv.lock`).

## Issues Encountered

None beyond the two pre-identified RED jobs (both remediated; see Deviations above).

## CI Re-observation (Task 2, re-run after remediation)

- **PR:** https://github.com/YuSabo90002/typsphinx/pull/104 (OPEN, base `main`, head branch `gsd/phase-2-verify-green-baseline`)
- **New head SHA:** `caf779da2e891d5a6cbd03a5bc87b802fe83540a`
- **ci.yml run (remediation head, caf779d):** https://github.com/YuSabo90002/typsphinx/actions/runs/28709010375 — conclusion `success`; job-conclusion set `["success"]` across all 18 jobs:
  - 12 test-matrix jobs: Python 3.10/3.11/3.12/3.13 x ubuntu-latest/windows-latest/macos-latest — all `success`, including all three 3.13 lanes (ubuntu, windows, macos) confirming no 3.13 wheel-availability gap
  - Lint and Format Check — `success` (confirms no reformatting regression, D-03 remediation held)
  - Type Check — `success`
  - Code Coverage — `success`
  - Build Package — `success`
  - Integration Test - basic — `success`
  - Integration Test - advanced — `success`
- **docs.yml run (remediation head, caf779d):** https://github.com/YuSabo90002/typsphinx/actions/runs/28709010382 — conclusion `success`; job-conclusion set `["success"]`; `build-docs` job green including the HTML multi-lang build, the PDF build, and the PDF-copy step, all on the Python 3.10 floor (tomli backport confirmed working in CI, not just locally)
- **release.yml:** not exercised by this PR (tag-push only trigger), per plan — validated by diff-read in Plan 01/03-VALIDATION.md, unchanged by this remediation
- **Current PR head (5d8e78a, after the docs-only SUMMARY.md/STATE.md commits):** re-fired both workflows automatically on push; re-confirmed green — ci.yml run https://github.com/YuSabo90002/typsphinx/actions/runs/28709196658 (`["success"]`, all 18 jobs) and docs.yml run https://github.com/YuSabo90002/typsphinx/actions/runs/28709196655 (`["success"]`). The PR's current Checks tab reflects this head.

## PR Diff Scope Note

The PR (`origin/main...caf779d`, code-complete at that commit; `5d8e78a` adds only this SUMMARY.md + STATE.md on top) carries the full Phase 2 + Phase 3 work since it reuses the `gsd/phase-2-verify-green-baseline` branch (previously logged Option-2 deviation). Within Phase 3's own contribution, the touched surfaces are:
- The six Python-floor config surfaces from Plan 01: `pyproject.toml`, `uv.lock`, `tox.ini`, `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/release.yml`
- Plus this plan's in-batch remediation: `typsphinx/builder.py`, `typsphinx/pdf.py`, `typsphinx/template_engine.py`, `typsphinx/translator.py`, `tests/test_entry_points.py`, `docs/source/conf.py` (annotation modernization and the tomli backport — required to make the floor bump CI-green, not scope creep)
No unrelated dependency or GitHub Action version bumps rode along in `uv.lock` (verified via `git diff uv.lock` — only the tomli dependency edge was added).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CI is fully green on PR #104's current head (`5d8e78a`) across the entire 3.10-3.13 matrix plus lint/type-check/coverage/build/integration/docs
- The PR is NOT merged and Phase 3 is NOT marked done — both are gated on the Task 3 human-verify checkpoint (see below)
- Once approved, the developer (not this agent) should merge the PR; `release.yml`'s floor reconciliation only fires on the next real `v*` tag push

## Self-Check: PASSED

All commit hashes (f2465ff, caf779d) verified in `git log --oneline --all`; all 8 modified files plus this SUMMARY.md verified present on disk.

---
*Phase: 03-modernize-python-floor-3-10-3-13*
*Completed: 2026-07-04*
