---
phase: 35-v0-6-5-release-prep
plan: 03
subsystem: release
tags: [uv, pyproject, versioning, release-prep]

# Dependency graph
requires:
  - phase: 35-v0-6-5-release-prep (plan 01)
    provides: Phase 34 gate-test additions (green suite) that this plan's regression run measures against
provides:
  - pyproject.toml [project] version bumped 0.6.4 -> 0.6.5
  - README.md Status line bumped in lockstep
  - uv.lock typsphinx self-entry regenerated to 0.6.5 with a one-line diff
  - editable-install metadata regenerated so typsphinx.__version__ reports 0.6.5
affects: [35-04, 35-05]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - pyproject.toml
    - README.md
    - uv.lock

key-decisions:
  - "Ran `uv lock` then `uv sync --extra dev --locked` as two separate commits (Task 1: pyproject.toml + README.md; Task 2: uv.lock) per the plan's task boundaries, so the single-line lock diff stays attributable to the version regeneration alone."

patterns-established: []

requirements-completed: [REL-03]

coverage:
  - id: D1
    description: "pyproject.toml [project] version bumped from 0.6.4 to 0.6.5 as the sole hard-coded package-version literal; no dependency/classifier/URL surface touched"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "grep -c '^version = \"0.6.5\"$' pyproject.toml -> 1; grep -c '^version = \"0.6.4\"$' pyproject.toml -> 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "README.md Status line bumped to Stable (v0.6.5), asserted equal to pyproject.toml's version by tests/test_readme_version_sync.py"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject"
        status: pass
    human_judgment: false
  - id: D3
    description: "uv.lock typsphinx self-entry regenerated to 0.6.5 with an exactly one-insertion/one-deletion diff (no transitive dependency re-resolution), uv sync --extra dev --locked exits 0, and typsphinx.__version__ reports 0.6.5"
    requirement: "REL-03"
    verification:
      - kind: integration
        ref: "uv sync --extra dev --locked (exit 0); uv run python -c \"import typsphinx; print(typsphinx.__version__)\" -> 0.6.5"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both version-sync guard tests green, and the four @preview declaration surfaces (writer.py, template_engine.py, templates/base.typ, examples/**/*.typ) remain untouched"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "tests/test_readme_version_sync.py, tests/test_preview_version_sync.py -q -> 4 passed"
        status: pass
      - kind: unit
        ref: "git diff --name-only -- typsphinx/ examples/ docs/ .github/ -> empty"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-07-29
status: complete
---

# Phase 35 Plan 03: Version bump to 0.6.5 Summary

**pyproject.toml/README.md/uv.lock all moved 0.6.4 -> 0.6.5 in lockstep; `uv.lock`'s diff is exactly one line (no transitive dependency re-resolved) and `typsphinx.__version__` confirms the editable-install metadata was regenerated.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-07-29T01:00:00+09:00 (approx, after worktree provisioning)
- **Completed:** 2026-07-29T01:03:20+09:00
- **Tasks:** 2 completed
- **Files modified:** 3 (`pyproject.toml`, `README.md`, `uv.lock`)

## Accomplishments
- `pyproject.toml`'s `[project] version` moved from `0.6.4` to `0.6.5` — the sole hard-coded package-version literal in the repo.
- README.md's Status line moved to `Stable (v0.6.5)` in the same commit, keeping `tests/test_readme_version_sync.py` green.
- `uv.lock` regenerated via `uv lock`; the diff is exactly one insertion and one deletion (the typsphinx self-entry's version field) — no transitive dependency silently re-resolved.
- `uv sync --extra dev --locked` exits 0 and `typsphinx.__version__` reports `0.6.5`, proving the editable-install metadata was actually regenerated (not just read back from `pyproject.toml`).
- Both version-sync guard tests (`test_readme_version_sync.py`, `test_preview_version_sync.py`) pass, and the four `@preview` declaration surfaces (`writer.py`, `template_engine.py`, `templates/base.typ`, `examples/**/*.typ`) are untouched.
- Full suite re-run: **649 passed, 1 skipped** — identical to the fork-base baseline, confirming the version bump introduced zero regressions.
- A second `uv lock` + `uv sync --extra dev --locked` invocation, run after committing `uv.lock`, produced no further diff (`git diff --exit-code uv.lock` exits 0) — the bump converges rather than churning.

## Task Commits

Each task was committed atomically:

1. **Task 1: Bump the version literal in pyproject.toml and README.md in a single commit** - `043784b` (feat)
2. **Task 2: Regenerate uv.lock and the editable-install metadata, then prove the runtime version** - `da09c07` (chore)

_No TDD tasks in this plan — both are mechanical release-bookkeeping edits with automated verify commands._

## Files Created/Modified
- `pyproject.toml` - `[project] version` key: `0.6.4` -> `0.6.5` (only line changed)
- `README.md` - Status line: `Stable (v0.6.4)` -> `Stable (v0.6.5)` (only line changed)
- `uv.lock` - typsphinx self-entry `version` field: `0.6.4` -> `0.6.5` (only line changed, regenerated by `uv lock`, never hand-edited)

## Evidence recorded verbatim (cited by plan 35-05 as SC#1/SC#4 evidence)

**`git diff --numstat uv.lock` (measured before commit):**
```
1	1	uv.lock
```

**`uv sync --extra dev --locked` output:**
```
Resolved 88 packages in 0.61ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a677143d46500ca92
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a677143d46500ca92
Prepared 1 package in 406ms
Uninstalled 1 package in 0.26ms
Installed 1 package in 1ms
 - typsphinx==0.6.4 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a677143d46500ca92)
 + typsphinx==0.6.5 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a677143d46500ca92)
```

**`typsphinx.__version__` probe output:**
```
0.6.5
```

**Convergence check (second lock+sync after committing `uv.lock`):**
```
$ uv lock
Resolved 88 packages in 0.66ms
$ uv sync --extra dev --locked
Resolved 88 packages in 0.64ms
Checked 80 packages in 0.40ms
$ git diff --exit-code uv.lock && echo NO_DIFF_CONVERGED
NO_DIFF_CONVERGED
```

## Decisions Made
- Split Task 1 (pyproject.toml + README.md) and Task 2 (uv.lock) into separate commits exactly as the plan specified, so the one-line lock diff stays attributable purely to the version regeneration and not mixed with the source literal edits.
- Ran the second convergence lock+sync pass *after* committing `uv.lock` (rather than before), since "against the committed state" in the plan's action text only makes sense once the file is actually committed — running it beforehand would have compared against an uncommitted working-tree diff instead.

## Deviations from Plan

None - plan executed exactly as written. Both tasks completed with all acceptance criteria met on the first attempt; no auto-fixes, no blocking issues, no architectural questions.

## Issues Encountered

None. The worktree's NixOS `ruff` shim (`.venv/bin/ruff` symlinked to the main tree's already-patched binary) was set up during provisioning but this plan performed no lint-relevant edits, so it was not exercised.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ROADMAP Phase 35 SC#1 is discharged: all three version surfaces agree at 0.6.5, `uv sync --extra dev --locked` is green, `typsphinx.__version__` reports 0.6.5, both guard tests pass, and the four `@preview` surfaces are untouched.
- Plan 35-04 (curated CHANGELOG entry) can now cite `0.6.5` as the confirmed release name.
- Plan 35-05 (final regression sweep + handoff) can cite this SUMMARY's verbatim `numstat`, `uv sync --locked`, and `__version__` evidence directly for SC#1/SC#4.
- No blockers.

## Self-Check: PASSED

- FOUND: `pyproject.toml`
- FOUND: `README.md`
- FOUND: `uv.lock`
- FOUND: `.planning/phases/35-v0-6-5-release-prep/35-03-SUMMARY.md`
- FOUND: commit `043784b` (Task 1)
- FOUND: commit `da09c07` (Task 2)

---
*Phase: 35-v0-6-5-release-prep*
*Completed: 2026-07-29*
