---
gsd_state_version: 1.0
milestone: v0.5.0
milestone_name: — forward-ecosystem
current_phase: 8
current_phase_name: Sphinx 9 / docutils 0.22
status: verifying
stopped_at: Completed 07-01-PLAN.md
last_updated: "2026-07-11T00:26:31.416Z"
last_activity: 2026-07-11
last_activity_desc: Phase 07 complete, transitioned to Phase 8
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 2
  completed_plans: 2
  percent: 40
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-09)

**Core value:** The `typst`/`typstpdf` builders produce correct output and every CI job stays green on the current ecosystem — Sphinx 9 and typst 0.15+ — with the runtime pins raised forward and the bundled `@preview` packages compiling cleanly (no `kai`-class breaks).
**Current focus:** Phase 07 — bump-preview-packages-typst-0-15-kai-fix

## Current Position

Phase: 8 — API & Test Compatibility (Sphinx 9 / docutils 0.22)
Plan: Not started
Status: Phase complete — ready for verification
Last activity: 2026-07-11 — Phase 07 complete, transitioned to Phase 8

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 15 (all in v0.4.4)
- v0.5.0 plans completed: 0
- Average duration: — min

**By Phase (v0.5.0):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 06 | 1 | - | - |
| 07 | 1 | - | - |
| 8 | TBD | - | - |
| 9 | TBD | - | - |
| 10 | TBD | - | - |

**Recent Trend:**

- Last 5 plans (v0.4.4): 3min, 3min, 20min, 12min, 40min
- Trend: — (new milestone, no plans executed yet)

*Updated after each plan completion*
| Phase 06 P01 | 20 | 2 tasks | 7 files |
| Phase 07 P01 | 12min | 3 tasks | 6 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v0.5.0 scope]: Latest-only forward port — raise pins to Sphinx 9.1 + typst 0.15+; no Sphinx-8/typst-0.14 compatibility range (version-conditional branching is out of scope).
- [v0.5.0 scope]: Python floor → ≥3.12 — Sphinx 9.1's own `requires-python` forces it; drop 3.10 and 3.11 from the matrix (raise sphinx/docutils/python + lockfile in one atomic PR, Phase 6).
- [v0.5.0 scope]: Bundled `@preview` version bump only — FWD-03 (user-configurable versions) deferred to v2 (CFG-01).
- [Roadmap]: FWD-02 (typst re-pin + no-`kai` compile) grouped with the `@preview` bump in Phase 7, not the pin-raise, because raising typst without the package bump leaves CI red on `kai` — both must land atomically.
- [Phase 06]: Non-matrix CI jobs (lint/type-check/coverage/build/integration, release validate/build, drift-check) move to Python 3.12 (not 3.13) per CONTEXT.md discretion default.
- [Phase 06]: Dropped the dead docs-extra tomli conditional (python_version < '3.11') since it is permanently false at the new 3.12 floor — keeps the PIN-02 grep audit clean.
- [Phase 07]: Bumped typst + all four @preview packages (mitex 0.2.7 / gentle-clues 1.3.1 / codly-languages 0.1.10, codly unchanged at 1.3.0) atomically in one wave per the locked ROADMAP contingency; empirical docs-pdf compile confirmed clean on first attempt, no bisect needed. — Confirms the mitex 0.2.6+ kai attribution from RESEARCH.md and closes FWD-02/PKG-01/PKG-02/PKG-03.

### Pending Todos

None yet.

### Blockers/Concerns

Carried forward from research (SUMMARY.md / PITFALLS.md) — must be resolved during execution:

- [Phase 7]: The `kai` root-cause attribution to `mitex` `0.2.6+` is MEDIUM confidence (strong CHANGELOG evidence, not independently reproduced). Phase 7 must confirm via a real `docs-pdf` compile, not changelog inference. If `kai` persists after the mitex bump, bisect package-by-package.
- [Phase 7]: `codly` `1.3.0` is already at the Typst Universe registry ceiling — no newer version exists as a fallback. If it breaks under typst 0.15, escalate to a source-level workaround/patch/replacement.
- [Phase 7]: The 3-way version-sync hazard — `test_preview_version_sync.py` proves the three files *agree*, not that the versions *compile correctly*. The empirical `docs-pdf` compile (and Phase 9's smoke test) is the real gatekeeper.
- [Phase 8]: Sphinx 9 changelog audit found no load-bearing API breaks, but re-verify empirically against the resolved deps (runtime AttributeError/TypeError may surface); spot-check the docutils 0.22 multi-`<term>` definition-list edge case.
- [Phase 07 follow-up]: docs-pdf now compiles clean but exposes a pre-existing (predates Phase 7) translator bug: .. note:: admonitions render literal unevaluated Typst source (par({text(...)})) instead of typeset prose in 4 spots, due to a markup/code-mode mismatch in translator.py::_visit_admonition. Logged in .planning/phases/07-bump-preview-packages-typst-0-15-kai-fix/deferred-items.md; needs a dedicated fix phase.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | FWD-03 → CFG-01: user-configurable `@preview` versions | Deferred to v2 | v0.4.4 close / v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v2 | v0.5.0 scoping |

## Session Continuity

Last session: 2026-07-11T00:19:40.409Z
Stopped at: Completed 07-01-PLAN.md
Resume file: None
