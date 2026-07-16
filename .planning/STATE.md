---
gsd_state_version: 1.0
milestone: v0.6.1
milestone_name: rendering fidelity
current_phase: 16
current_phase_name: Silent-Drop Node Handlers + Length-Converter Refactor
status: executing
stopped_at: Phase 16 context gathered
last_updated: "2026-07-16T12:27:10.666Z"
last_activity: 2026-07-13
last_activity_desc: v0.6.1 roadmap created (Phases 16–18, continuing from v0.6.0's Phase 15)
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-13 — v0.6.1 rendering-fidelity roadmap created)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable output for large real-world documentation sets — and now, output that *renders faithfully* to the source, not merely compiles fatal-free.
**Current focus:** v0.6.1 (rendering fidelity), Phase 16 — implement the last two silently-dropped nodes (`todo_node`, `manpage`) + generalize the CSS-length converter (LEN-01), before the visual fidelity audit.

## Current Position

Phase: 16 of 18 (Silent-Drop Node Handlers + Length-Converter Refactor)
Plan: — (roadmap approved; ready to plan Phase 16)
Status: Ready to execute
Last activity: 2026-07-13 — v0.6.1 roadmap created (Phases 16–18, continuing from v0.6.0's Phase 15)

Progress: [░░░░░░░░░░] 0%

## Roadmap Summary (v0.6.1 — Phases 16–18)

| Phase | Goal | Requirements |
|-------|------|--------------|
| 16 — Silent-Drop Node Handlers + Length-Converter Refactor | Render `todo_node` (admonition-style) + `manpage` (literal page text); generalize v0.6.0's px→pt converter into one shared, reused helper | TODO-01, MAN-01, LEN-01 |
| 17 — Rendering-Fidelity Audit (discovery) | Human-assisted visual diff of the compiled corpus PDF vs. source → a severity-rated catalogue of *silent* mis-render issues; appends the FID-01a… fix backlog to REQUIREMENTS.md | AUD-01 |
| 18 — Fidelity Fixes + Regression-Gate Close (discovery-sized) | Fix every high-severity AUD-01 issue with a real-compile regression fixture, then close on GATE-03 (corpus still fatal-free; `todo_node`/`manpage` gone from the `unknown_visit` catalogue) | FID-01, GATE-03 |

**Coverage:** 6/6 named v1 requirements mapped (FID-01 expands to FID-01a… after AUD-01). No orphans.

**Standing bar (GATE-01):** every node-handler change (Phases 16, 18) ships or extends a real `typst.compile()` acceptance fixture — string-agreement asserts alone never suffice. Local env can run real compiles (typst 0.15.0; corpus cached at `~/.cache/typsphinx-corpus-gate`).

**Milestone invariant:** zero new runtime deps, no `@preview` bump expected — the 3-way version-sync surface stays untouched. Flag during planning if a phase needs otherwise.

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 43 (15 in v0.4.4, 13 in v0.5.0, 15 in v0.6.0)
- v0.6.1 plans completed: 0
- Average duration: — (new milestone, no plans executed yet)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Roadmap-shaping decisions for v0.6.1 (full log in PROJECT.md Key Decisions):

- [Roadmap]: TODO-01/MAN-01/LEN-01 grouped into one early Phase 16 — independent, additive, low-risk translator changes (two new `visit_*` handlers + one converter refactor); they do NOT depend on the audit.
- [Roadmap]: AUD-01 is an isolated **discovery** phase (17) — warnings only surface *dropped* content, so a human-assisted visual audit is the only way to find *silent* mis-renders; its output is a written catalogue artifact.
- [Roadmap]: FID-01 (Phase 18) is sequenced AFTER AUD-01 and is **discovery-sized** — the concrete per-issue fix list is unknown until the audit enumerates it; success criterion is "every high-severity issue fixed with a real-compile fixture," not a fixed count. Plan count TBD until AUD-01 completes.
- [Roadmap]: GATE-03 folded into Phase 18 as its closing success criteria (not a standalone thin gate phase) — it validates the whole milestone: corpus still fatal-free (GATE-02 non-regression) AND `todo_node`/`manpage` gone from the `unknown_visit` catalogue.
- [Roadmap]: Phase 17 depends on Phase 16 — audit the corpus with the new handlers already landed, so the audit surfaces genuinely-silent divergence, not the already-scheduled `todo_node`/`manpage` drops.

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 16]: `manpage` node child shape / `:manpage:` role output — confirm the literal page-reference text (e.g. `ls(1)`) against a live doctree dump before locking the handler.
- [Phase 16]: LEN-01 is a refactor of load-bearing code (`visit_image`'s px→pt fix from v0.6.0) — the shared helper must be behavior-preserving at the `visit_image` call site; the real-compile figure fixture guards this.
- [Phase 17]: AUD-01 is human-assisted (visual page-by-page inspection). Scope discipline: catalogue only in-scope fidelity bugs typsphinx owns, excluding known out-of-scope degradations (graphviz/inheritance placeholders, non-included-doc xrefs, Sphinx-side autodoc/`py:meth` warnings).

### Roadmap Evolution

- 2026-07-13: v0.6.1 roadmap created — Phases 16–18, derived from 6 named v1 requirements (TODO-01, MAN-01, LEN-01, AUD-01, FID-01, GATE-03). Phase numbering continues from v0.6.0 (ended at Phase 15). A focused 3-phase polish shape: node handlers + LEN-01 → fidelity audit → audit-driven fixes + gate close.
- 2026-07-11: v0.6.0 roadmap created — Phases 11–15, derived from 19 v1 requirements. Continued from v0.5.0.

## Deferred Items

Items acknowledged and carried forward from previous milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.1 | v0.6.1 scoping |

## Session Continuity

Last session: 2026-07-13T13:05:42.076Z
Stopped at: Phase 16 context gathered
Resume file: .planning/phases/16-silent-drop-node-handlers-length-converter-refactor/16-CONTEXT.md

## Operator Next Steps

- Plan Phase 16 with `/gsd-plan-phase 16` (TODO-01 + MAN-01 + LEN-01).
