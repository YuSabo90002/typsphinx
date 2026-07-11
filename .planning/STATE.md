---
gsd_state_version: 1.0
milestone: v0.5.0
milestone_name: — forward-ecosystem
current_phase: 08.1
current_phase_name: admonition rendering fix — translator markup/code-mode mismatch
status: executing
stopped_at: Completed 08.1-03-PLAN.md
last_updated: "2026-07-11T04:41:11.642Z"
last_activity: 2026-07-11
last_activity_desc: Phase 08.1 execution started
progress:
  total_phases: 6
  completed_phases: 3
  total_plans: 9
  completed_plans: 8
  percent: 50
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-09)

**Core value:** The `typst`/`typstpdf` builders produce correct output and every CI job stays green on the current ecosystem — Sphinx 9 and typst 0.15+ — with the runtime pins raised forward and the bundled `@preview` packages compiling cleanly (no `kai`-class breaks).
**Current focus:** Phase 08.1 — admonition rendering fix — translator markup/code-mode mismatch

## Current Position

Phase: 08.1 (admonition rendering fix — translator markup/code-mode mismatch) — EXECUTING
Plan: 4 of 4
Status: Ready to execute
Last activity: 2026-07-11 — Phase 08.1 execution started

Progress: [██████░░░░] 60%

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
| 08 | 3 | - | - |
| 9 | TBD | - | - |
| 10 | TBD | - | - |

**Recent Trend:**

- Last 5 plans (v0.4.4): 3min, 3min, 20min, 12min, 40min
- Trend: — (new milestone, no plans executed yet)

*Updated after each plan completion*
| Phase 06 P01 | 20 | 2 tasks | 7 files |
| Phase 07 P01 | 12min | 3 tasks | 6 files |
| Phase 08 P01 | 8min | 2 tasks | 2 files |
| Phase 08 P02 | 3min | 2 tasks | 4 files |
| Phase 08 P03 | 2min | 2 tasks | 1 files |
| Phase 08.1 P01 | 1min | 2 tasks | 2 files |
| Phase 08.1 P02 | 6min | 3 tasks | 2 files |
| Phase 08.1 P03 | 6min | 2 tasks | 2 files |

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
- [Phase 08]: Scoped strictly to the plan's locked boundary: only template_engine.py traverse->findall and test_translator.py's 3 OptionParser->frontend.get_default_settings sites landed; the remaining 4 deprecation-fix sites and the filterwarnings guard are reserved for Plans 08-02/08-03. — Preserves D-02 ordering constraint: guard must land after the full sweep, not before.
- [Phase 08-02]: Test-assertion-only fixes for builder.app and writer_name deprecations; no runtime source touched, no compatibility branching added.
- [Phase 08-03]: Escalated both error::DeprecationWarning and error::PendingDeprecationWarning in the permanent pytest filterwarnings guard (D-02) — a documented deviation-with-rationale from CONTEXT.md's literal DeprecationWarning-only text, required to catch Sphinx's RemovedInSphinxNNWarning family which subclasses PendingDeprecationWarning.
- [Phase 08-03]: Skipped the optional multi-<term> definition-list hardening (Task 2) as forward-looking-only — no current docutils 0.22.4 rST syntax produces a multi-<term> definition_list_item; deferred as a documented follow-up, not silently dropped.
- [Phase ?]: [Phase 08.1-01]: pypdf's SUS supply-chain legitimacy flag (too-new/unknown-downloads) was human-confirmed as a false positive before install via the blocking-human checkpoint protocol.
- [Phase ?]: Kept _visit_admonition's custom_title parameter unchanged (stashed on self._custom_admonition_title) so the six existing per-type visit_*/depart_* call sites needed zero changes
- [Phase ?]: Used a dedicated _saved_body_for_admonition_title field instead of reusing the definition-list saved_body field, to avoid state collisions between the two buffer-swap use sites
- [Phase ?]: Static custom_title (Important/See Also) stays a plain string argument; only the dynamic node-derived title uses the buffered code-block form
- [Phase ?]: [Phase 08.1-03]: Used the research-verified D-06 clue mapping exactly: hint->tip, error->error, danger->danger, attention->warning, generic admonition->base clue()
- [Phase ?]: [Phase 08.1-03]: Generic admonition handler passes no custom_title - directive-supplied title flows through the existing visit_title/depart_title buffer-swap path automatically

### Pending Todos

None yet.

### Blockers/Concerns

Carried forward from research (SUMMARY.md / PITFALLS.md) — must be resolved during execution:

- [Phase 7]: The `kai` root-cause attribution to `mitex` `0.2.6+` is MEDIUM confidence (strong CHANGELOG evidence, not independently reproduced). Phase 7 must confirm via a real `docs-pdf` compile, not changelog inference. If `kai` persists after the mitex bump, bisect package-by-package.
- [Phase 7]: `codly` `1.3.0` is already at the Typst Universe registry ceiling — no newer version exists as a fallback. If it breaks under typst 0.15, escalate to a source-level workaround/patch/replacement.
- [Phase 7]: The 3-way version-sync hazard — `test_preview_version_sync.py` proves the three files *agree*, not that the versions *compile correctly*. The empirical `docs-pdf` compile (and Phase 9's smoke test) is the real gatekeeper.
- [Phase 8]: Sphinx 9 changelog audit found no load-bearing API breaks, but re-verify empirically against the resolved deps (runtime AttributeError/TypeError may surface); spot-check the docutils 0.22 multi-`<term>` definition-list edge case.
- [Phase 07 follow-up]: docs-pdf now compiles clean but exposes a pre-existing (predates Phase 7) translator bug: .. note:: admonitions render literal unevaluated Typst source (par({text(...)})) instead of typeset prose in 4 spots, due to a markup/code-mode mismatch in translator.py::_visit_admonition. Logged in .planning/phases/07-bump-preview-packages-typst-0-15-kai-fix/deferred-items.md; needs a dedicated fix phase.

### Roadmap Evolution

- Phase 08.1 inserted after Phase 8: admonition rendering fix — translator markup/code-mode mismatch (URGENT)

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | FWD-03 → CFG-01: user-configurable `@preview` versions | Deferred to v2 | v0.4.4 close / v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v2 | v0.5.0 scoping |

## Session Continuity

Last session: 2026-07-11T04:41:11.637Z
Stopped at: Completed 08.1-03-PLAN.md
Resume file: 
None
