---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 03
current_phase_name: modernize-python-floor-3-10-3-13
status: executing
stopped_at: Phase 3 context gathered
last_updated: "2026-07-04T10:55:22.842Z"
last_activity: 2026-07-04
last_activity_desc: Phase 03 execution started
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 7
  completed_plans: 6
  percent: 40
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-04)

**Core value:** Every CI job passes again on `main` — lint, the full test matrix, coverage, and the docs PDF build — with a dependency set that is pinned and reproducible so this rot doesn't silently recur.
**Current focus:** Phase 03 — modernize-python-floor-3-10-3-13

## Current Position

Phase: 03 (modernize-python-floor-3-10-3-13) — EXECUTING
Plan: 2 of 2
Status: Ready to execute
Last activity: 2026-07-04 — Phase 03 execution started

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**

- Total plans completed: 5
- Average duration: - min
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 2 | - | - |
| 02 | 3 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 02 P01 | 5min | 2 tasks | 1 files |
| Phase 02 P02 | 8min | 3 tasks | 1 files |
| Phase 02 P03 | 6min | 4 tasks | 2 files |
| Phase 03 P01 | 6min | 3 tasks | 6 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Pre-Phase 1]: Pin runtime deps to known-good rather than port forward to sphinx 9 / typst 0.15 — fastest, lowest-risk path to green CI in a maintenance cycle.
- [Pre-Phase 1]: Pin `typst` to a 0.14.x line compatible with the bundled `@preview` packages — the exact patch must be empirically confirmed during Phase 1 execution, not assumed.
- [Pre-Phase 1]: Modernize Python floor to 3.10–3.13 (drop EOL 3.9, add 3.13) as an atomic batch in Phase 3, sequenced after the pin fix is confirmed green.
- [Phase 02]: Scoped the @preview version-sync regex to actual #import statements only (not bare text matches) to avoid false-positive divergence from docstring examples — The naive regex matched a docstring example (charged-ieee) unrelated to the four essential imports
- [Phase 02]: Substituted tox -e cov (system Python) for tox -e py311 in the local pre-check — NixOS cannot execute tox-uv's downloaded standalone CPython 3.11 build; unrelated to the Phase 1 pin; GitHub Actions runners are unaffected
- [Phase 02]: Auto-fixed a black-formatting bug in Plan 01's sync-guard test (Rule 1) to unblock the Lint job, but left the pre-existing tox env-name mismatch (py3.10 vs py310, 9/12 matrix jobs) unpatched per D-04, surfacing it as a finding with a ready but unmerged fix on gsd/bugfix/github-ci-tox
- [Phase 02]: Applied the drafted tox-env matrix-mapping fix via git cherry-pick (64cd057) from gsd/bugfix/github-ci-tox rather than reimplementing by hand
- [Phase 02]: Left the CODECOV_TOKEN-absent codecov tokenless-upload failure unaddressed as pre-existing and out of scope (fail_ci_if_error: false keeps the job green)
- [Phase 03]: Ran plain uv lock (no --upgrade); verified the diff was only the <3.10 marker-branch collapse + incidental chardet drop, no unrelated version bumps
- [Phase 03]: black --check . confirmed a no-op both before and after the target-version bump to py310-py313 (D-03 does not trigger); no separate reformat commit needed

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: The exact typst 0.14.x patch that satisfies all four bundled `@preview` packages (codly, codly-languages, mitex, gentle-clues) simultaneously is not yet empirically confirmed — this is Phase 1's core deliverable, not a research-time conclusion. If no single 0.14.x version satisfies all four, the documented fallback is pinning one `@preview` package to an older release instead of moving the typst pin.
- [Phase 1]: Whether the `sphinx<9` / `docutils<0.22` ceilings are load-bearing or purely precautionary is unconfirmed — resolve by testing whether `typst<0.15` alone is sufficient, and document the finding regardless (PIN-06).

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-07-04T10:54:11.866Z
Stopped at: Phase 3 context gathered
Resume file: .planning/phases/03-modernize-python-floor-3-10-3-13/03-CONTEXT.md
