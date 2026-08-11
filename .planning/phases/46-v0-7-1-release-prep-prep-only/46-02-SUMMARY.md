---
phase: 46-v0-7-1-release-prep-prep-only
plan: 02
subsystem: release-prep
tags: [uv, packaging, versioning, pytest, release]

# Dependency graph
requires:
  - phase: 46-01
    provides: "Phase 46 planning context and the earlier-wave release-prep artifacts this plan builds on"
provides:
  - "pyproject.toml version literal moved from 0.7.0 to 0.7.1 (the repo's sole version literal)"
  - "README.md Status line moved in lockstep with pyproject.toml"
  - "uv.lock regenerated so its own typsphinx entry and the editable-install metadata (.dist-info / .pth) report 0.7.1"
  - "46-BUMP-EVIDENCE.md recording SC#1's verbatim transcripts, including an honest 'not run locally' statement for tox -e py312"
affects: [46-04, 46-05, gsd-complete-milestone]

# Actuals (#2632)
actuals:
  tokens: 2528
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/46-v0-7-1-release-prep-prep-only/46-BUMP-EVIDENCE.md
  modified:
    - pyproject.toml
    - README.md
    - uv.lock

key-decisions:
  - "None - plan executed exactly as written; no Rule 1-4 deviations were needed."

patterns-established: []

requirements-completed: [REL-06]

coverage:
  - id: D1
    description: "pyproject.toml is the sole 0.7.1 version literal; README.md's Status line and uv.lock's own typsphinx entry moved with it in lockstep"
    requirement: "REL-06"
    verification:
      - kind: unit
        ref: "tests/test_extension.py::test_version_matches_pyproject_toml"
        status: pass
      - kind: unit
        ref: "tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject"
        status: pass
    human_judgment: false
  - id: D2
    description: "typsphinx.__version__ reports 0.7.1 after the editable-install metadata was regenerated via uv sync --extra dev --locked, not merely the literal edited"
    requirement: "REL-06"
    verification:
      - kind: other
        ref: "uv run python -c \"import typsphinx; print(typsphinx.__version__)\" (prints 0.7.1)"
        status: pass
    human_judgment: false
  - id: D3
    description: "uv.lock and pyproject.toml agree under uv sync --extra dev --locked / uv lock --check, and the [project] dependencies block is byte-identical to HEAD's (no dependency added or removed)"
    requirement: "REL-06"
    verification:
      - kind: other
        ref: "uv lock --check (exit 0); uv sync --extra dev --locked (exit 0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The @preview four-package lockstep invariant (writer.py / template_engine.py / templates/base.typ / examples/) is untouched by this plan's diff"
    requirement: "REL-06"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py (3 tests: identical-across-sites, all-four-declared, example-templates-match-canonical)"
        status: pass
    human_judgment: false
  - id: D5
    description: "No irreversible release action was taken (no tag, no tag push, no PyPI upload, no GitHub Release)"
    requirement: "REL-06"
    verification:
      - kind: other
        ref: "git tag -l v0.7.1 (empty); git ls-remote --tags origin v0.7.1 (empty)"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-08-11
status: complete
---

# Phase 46 Plan 02: Version Bump 0.7.0 → 0.7.1 Summary

**Moved the sole `0.7.1` version literal across `pyproject.toml`, `README.md`, and `uv.lock` in lockstep, regenerated the editable-install metadata so `typsphinx.__version__` actually reports `0.7.1`, and recorded all five version-sync guard transcripts as SC#1 evidence.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-08-11T13:06:00+09:00 (approx.)
- **Completed:** 2026-08-11T13:14:49+09:00
- **Tasks:** 2
- **Files modified:** 4 (3 source-of-truth files + 1 new evidence file)

## Accomplishments
- `pyproject.toml` line 7 moved `version = "0.7.0"` → `version = "0.7.1"` (the repository's sole version literal)
- `README.md`'s `**Status**` line moved to `Stable (v0.7.1) - Production ready` in the same commit
- `uv lock` regenerated `uv.lock`'s own first-party `typsphinx` entry to `version = "0.7.1"`, and `uv sync --extra dev --locked` regenerated the worktree's installed-package metadata (`.dist-info` / editable `.pth`), confirmed by `uv run python -c "import typsphinx; print(typsphinx.__version__)"` printing `0.7.1`
- All five version-sync guard tests (`test_version_matches_pyproject_toml`, `test_readme_status_version_matches_pyproject`, and all three `test_preview_version_sync.py` tests) pass with zero skips, recorded as a JUnit `testsuite` with `tests="5"`, `skipped="0"`, `failures="0"`, `errors="0"`
- `.planning/phases/46-v0-7-1-release-prep-prep-only/46-BUMP-EVIDENCE.md` written with verbatim before/after values, command transcripts, the invariant spot-check, and an honest "executed versus skipped" statement naming `tox -e py312` as not run (cannot provision on this machine) and CI as the matrix authority per D-11

## Task Commits

Each task was committed atomically:

1. **Task 1: Move the version literal across all three surfaces and regenerate the editable install** - `e0804d7` (chore)
2. **Task 2: Run the version-sync guard battery and record SC#1's evidence** - `b15562a` (docs)

_No plan-metadata commit was made from inside this worktree — STATE.md/ROADMAP.md updates are owned by the orchestrator after wave merge, per the worktree-execution contract._

## Files Created/Modified
- `pyproject.toml` - `version` literal moved `0.7.0` → `0.7.1`
- `README.md` - `**Status**` line moved to `Stable (v0.7.1)` in lockstep
- `uv.lock` - regenerated; its own `typsphinx` entry now reads `version = "0.7.1"`, `source = { editable = "." }`
- `.planning/phases/46-v0-7-1-release-prep-prep-only/46-BUMP-EVIDENCE.md` - new; SC#1's verbatim evidence

## Decisions Made
None - plan executed exactly as written. `0.7.1` was locked by D-01 before this plan started; no architectural or ambiguous decision arose during execution.

## Deviations from Plan

None - plan executed exactly as written. No Rule 1-4 auto-fixes were needed: `pyproject.toml`'s version literal, `README.md`'s Status line, and `uv.lock`'s `typsphinx` entry were all found exactly where the plan's `<read_first>` predicted, and both `uv lock` and `uv sync --extra dev --locked` succeeded on the first attempt.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The tree's version identity (`pyproject.toml`, `README.md`, `uv.lock`, and the installed `.dist-info`) is now fully converged on `0.7.1`, and the guard-test battery that defends this lockstep is green with zero skips. `git tag -l v0.7.1` and `git ls-remote --tags origin v0.7.1` are both confirmed empty — no irreversible release action occurred, consistent with Phase 46 being prep-only.

This plan's own diff touched no template, writer, or import code, so the `@preview` four-package lockstep invariant (T-46-08's mitigation) is untouched by construction. The **full mechanical sweep** of the entire milestone diff for `@preview`/version drift (D-21's anchor at the `v0.7.0` tag) is explicitly deferred to and owned by **plan 46-05** — this evidence file cites that plan rather than duplicating its figures. Plan 46-03 (CHANGELOG work, disjoint files: `CHANGELOG.md`, `docs/source/changelog.rst`, `tests/test_changelog_page_gate.py`) runs as a sibling in the same wave and was not touched by this plan.

No blockers for downstream plans. REL-06's in-phase share for this plan (version-literal lockstep + evidence) is discharged; REL-04's own closure still waits on a real tag push at `/gsd-complete-milestone`, unaffected by this plan.

---
*Phase: 46-v0-7-1-release-prep-prep-only*
*Completed: 2026-08-11*

## Self-Check: PASSED

- FOUND: `pyproject.toml`
- FOUND: `.planning/phases/46-v0-7-1-release-prep-prep-only/46-BUMP-EVIDENCE.md`
- FOUND: `.planning/phases/46-v0-7-1-release-prep-prep-only/46-02-SUMMARY.md`
- FOUND commit: `e0804d7` (Task 1)
- FOUND commit: `b15562a` (Task 2)
- FOUND commit: `1c4efb1` (SUMMARY.md)
