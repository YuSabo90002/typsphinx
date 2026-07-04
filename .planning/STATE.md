---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 2
current_phase_name: Verify the Green Baseline
status: executing
stopped_at: Phase 1 context gathered
last_updated: "2026-07-04T07:29:25.526Z"
last_activity: 2026-07-04
last_activity_desc: Phase 01 complete, transitioned to Phase 2
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 2
  completed_plans: 2
  percent: 20
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-04)

**Core value:** Every CI job passes again on `main` — lint, the full test matrix, coverage, and the docs PDF build — with a dependency set that is pinned and reproducible so this rot doesn't silently recur.
**Current focus:** Phase 01 — pin-runtime-dependencies-to-known-good

## Current Position

Phase: 2 — Verify the Green Baseline
Plan: Not started
Status: Executing Phase 01
Last activity: 2026-07-04 — Phase 01 complete, transitioned to Phase 2

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**

- Total plans completed: 2
- Average duration: - min
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 2 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Pre-Phase 1]: Pin runtime deps to known-good rather than port forward to sphinx 9 / typst 0.15 — fastest, lowest-risk path to green CI in a maintenance cycle.
- [Pre-Phase 1]: Pin `typst` to a 0.14.x line compatible with the bundled `@preview` packages — the exact patch must be empirically confirmed during Phase 1 execution, not assumed.
- [Pre-Phase 1]: Modernize Python floor to 3.10–3.13 (drop EOL 3.9, add 3.13) as an atomic batch in Phase 3, sequenced after the pin fix is confirmed green.

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

Last session: 2026-07-04T05:36:12.779Z
Stopped at: Phase 1 context gathered
Resume file: .planning/phases/01-pin-runtime-dependencies-to-known-good/01-CONTEXT.md
