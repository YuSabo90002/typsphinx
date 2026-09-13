---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 02
subsystem: testing
tags: [ruff, mypy, pytest, baseline, evidence, uv]

# Dependency graph
requires: []
provides:
  - "70-BASELINE-EVIDENCE.md with PHASE_BASE_SHA, interpreter record, fresh UP006/UP035 census, SC#2 base counts, and the before sides of QUA-12 legs (b) and (e)"
affects: [70-04, 70-05, 70-06, 70-07, 70-08, 70-09, 70-10, 70-11, 70-12, 70-13]

# Actuals (#2632)
actuals:
  tokens: 1582
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: ["evidence-key-line convention (`KEY = value`, explanation on next line) reused from v0.9.3 Phase 68"]

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-BASELINE-EVIDENCE.md
  modified: []

key-decisions:
  - "No copying of research/roadmap-time numbers — every key was measured fresh in this worktree at PHASE_BASE_SHA, confirming (but not reusing) the 113/93/20 figures recorded at discussion time."
  - "PYTEST_WARNINGS_BEFORE recorded as 0 (informational only) since the recorded run's output carried no warnings summary section."

patterns-established:
  - "Evidence keys are bare `KEY = value` lines with any explanation on the following line, so downstream plans can extract with `sed -n \"s/^KEY = //p\"`."

requirements-completed: [QUA-09, QUA-12]

coverage:
  - id: D1
    description: "PHASE_BASE_SHA, interpreter (VENV_HOME/VENV_VERSION_INFO), ruff version and the fresh repo-wide UP006/UP035 census recorded and cross-checked against the ten files the conversion plans own"
    requirement: "QUA-09"
    verification:
      - kind: other
        ref: "manual re-derivation: `uv run ruff check . --select UP006,UP035 --output-format=concise | grep -cE ': UP0(06|35) '` = 113, matching UP_TOTAL_BASE"
        status: pass
      - kind: other
        ref: "file-set comparison: distinct files in the fresh census sorted-diff empty against the ten planned files (UP_FILES_MATCH_PLAN = YES)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#2 base counts (FUTURE_ANNOTATIONS_BASE, OPTIONAL_BASE, UNION_BASE, PIPE_NONE_BASE) recorded via git grep at PHASE_BASE_SHA"
    requirement: "QUA-09"
    verification:
      - kind: other
        ref: "re-run of each `git grep -hoE '<pattern>' <SHA> -- 'typsphinx/*.py' 'tests/*.py' | wc -l` matches the recorded key"
        status: pass
    human_judgment: false
  - id: D3
    description: "mypy typsphinx/ before-side stdout hash (leg e) recorded stdout-only, stderr excluded"
    requirement: "QUA-12"
    verification:
      - kind: other
        ref: "`uv run mypy typsphinx/ 2>/dev/null | sha256sum` re-run matches MYPY_STDOUT_SHA256_BEFORE; MYPY_EXIT_BEFORE = 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "pytest collected/result before side (leg b) recorded under LC_ALL=C with --extra dev --extra docs, with skip reasons quoted"
    requirement: "QUA-12"
    verification:
      - kind: other
        ref: "re-run of the unanchored collect extraction (1548) and the `-rs` full-suite run (1547 passed, 1 skipped, exit 0) match the recorded keys; tokens sum to the collected count"
        status: pass
    human_judgment: false

# Metrics
duration: 6min
completed: 2026-09-13
status: complete
---

# Phase 70 Plan 02: Pre-conversion Baseline Summary

**Measured PHASE_BASE_SHA, the nixpkgs 3.13.13 interpreter, a fresh 113-finding UP006/UP035 census across exactly the ten planned files, SC#2's four base counts, and the before sides of QUA-12 legs (b) pytest and (e) mypy — all fresh, none copied from research or the ROADMAP.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-09-13T04:25:04Z
- **Completed:** 2026-09-13T04:31:07Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments
- Recorded `PHASE_BASE_SHA = 697a113221a8a267d7e8c6dd1f2b95672f9454d2` (this worktree's fork point) and confirmed the worktree tree outside `.planning/` is identical to `main`'s tip.
- Provisioned the worktree with `uv sync --extra dev --extra docs --python 3.13.13` and recorded `VENV_HOME`/`VENV_VERSION_INFO` (3.13.13, matching the main checkout's nixpkgs interpreter path).
- Ran a fresh repo-wide `ruff check . --select UP006,UP035` census: 113 findings (93 UP006, 20 UP035) across exactly the ten files the conversion plans own — the census's file set was diffed against that list and found equal (`UP_FILES_MATCH_PLAN = YES`).
- Recorded the four SC#2 base counts via `git grep` at `PHASE_BASE_SHA`: `FUTURE_ANNOTATIONS_BASE = 0`, `OPTIONAL_BASE = 0`, `UNION_BASE = 0`, `PIPE_NONE_BASE = 82`.
- Recorded leg (e)'s before side: `mypy typsphinx/` stdout-only hash (`MYPY_STDOUT_SHA256_BEFORE`), with `MYPY_EXIT_BEFORE = 0`, capturing stdout separately from `uv run`'s stderr sync chatter (Pitfall 7).
- Recorded leg (b)'s before side under `LC_ALL=C`: `PYTEST_COLLECTED_BEFORE = 1548`, `PYTEST_RESULT_BEFORE = 1547 passed 1 skipped` (sums to the collected count), `PYTEST_EXIT_BEFORE = 0`, and quoted the one env-gated skip reason.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: record PHASE_BASE_SHA, interpreter, ruff version, the fresh UP006/UP035 census against the planned file set, the SC#2 base counts and mypy's before stdout** - `a04f8ca3` (docs)
2. **Task 2: Record leg (b)'s before side: pytest collected count and full-suite result under LC_ALL=C, with skip reasons** - `1fdbc5d5` (docs)

**Plan metadata:** committed alongside this SUMMARY.

## Files Created/Modified
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-BASELINE-EVIDENCE.md` - the pre-conversion baseline evidence file: `PHASE_BASE_SHA`, interpreter record, ruff census (`~~~text up-files` block), SC#2 base counts, mypy before (`~~~text mypy-before` block), and pytest before (`~~~text pytest-skips-before` block)

## Decisions Made
- Every key was measured fresh in this worktree rather than copied from `70-CONTEXT.md`/`70-RESEARCH.md`/`ROADMAP.md`, per constraint 3 and the plan's own prohibition. The fresh numbers happen to match the research-time figures (113/93/20, 1548/1547) exactly, which is expected since no product file has changed yet — it confirms rather than substitutes for the fresh measurement.
- `PYTEST_WARNINGS_BEFORE` recorded as `0` since the `-rs` run's output carried no "warnings summary" section; this key is informational only per the plan.

## Deviations from Plan

None - plan executed exactly as written. Task 1 (type="tracer") was followed by the tracer feedback gate per the executor protocol: `HUMAN_VERIFY_MODE = end-of-phase` (config) and the tracer's `<verify>` carries only `<automated>` (no `<human-check>`), so the gate re-ran the task's verification fresh (re-derived the ruff census count and the mypy stdout hash) rather than emitting a checkpoint; both matched, so execution proceeded directly to Task 2 with no interruption.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `70-BASELINE-EVIDENCE.md` now carries every key `70-04`..`70-13` need to compare against: `PHASE_BASE_SHA`, `VENV_HOME`/`VENV_VERSION_INFO`, `LOCK_RUFF_VERSION`/`RUFF_VERSION_BASE`, the full UP006/UP035 census, the four SC#2 counts, and the before sides of legs (b) and (e).
- No blockers. This plan ran in parallel wave 1 alongside 70-01 (CLAUDE.md rewrite) and 70-03 (leg (d)/DOC-23 baselines); none of this plan's verifies depended on either sibling.

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*
