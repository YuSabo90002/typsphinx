---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 3
current_phase_name: 3.10-3.13
status: verifying
stopped_at: Completed 02-03-PLAN.md
last_updated: "2026-07-04T09:52:12.551Z"
last_activity: 2026-07-04
last_activity_desc: Phase 02 complete, transitioned to Phase 3
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 5
  completed_plans: 5
  percent: 40
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-04)

**Core value:** Every CI job passes again on `main` — lint, the full test matrix, coverage, and the docs PDF build — with a dependency set that is pinned and reproducible so this rot doesn't silently recur.
**Current focus:** Phase 02 — verify-the-green-baseline

## Current Position

Phase: 3 — Modernize Python Floor (3.10-3.13)
Plan: Not started
Status: Phase complete — ready for verification
Last activity: 2026-07-04 — Phase 02 complete, transitioned to Phase 3

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

Last session: 2026-07-04T09:45:48.624Z
Stopped at: Completed 02-03-PLAN.md
Resume file: None
