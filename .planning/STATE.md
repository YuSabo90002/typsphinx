---
gsd_state_version: 1.0
milestone: v0.6.1
milestone_name: rendering fidelity
current_phase: 17
current_phase_name: rendering-fidelity-audit
status: executing
stopped_at: 17-02 PARTIAL — 44/151 docnames audited; resume from extdev/event_callbacks
last_updated: "2026-07-19T05:40:00.000Z"
last_activity: 2026-07-19
last_activity_desc: 17-02 visual audit in progress (multi-session) — 44/151 docnames, findings F1–F9
progress:
  total_phases: 3
  completed_phases: 1
  total_plans: 7
  completed_plans: 4
  percent: 33
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-16 after Phase 16 complete)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable output for large real-world documentation sets — and now, output that *renders faithfully* to the source, not merely compiles fatal-free.
**Current focus:** Phase 17 — rendering-fidelity-audit

## Current Position

Phase: 17 (rendering-fidelity-audit) — EXECUTING
Plan: 2 of 4 (17-02 IN PROGRESS — multi-session visual audit, NO SUMMARY yet by design)
Status: Executing Phase 17 — 17-02 partial pass
Last activity: 2026-07-19 — 17-02 visual audit: 44/151 docnames audited (findings F1–F9)

**17-02 resume pointer:** Resume the visual pass from the first "🔲 NOT YET AUDITED" entry in
`17-AUDIT-CATALOGUE.md`'s progress tracker = `extdev/event_callbacks` (PDF pp.195–201). Remaining in the
extdev cluster: event_callbacks(195-201), projectapi(202), envapi(203-204), builderapi(205-207),
eventapi(208-209), collectorapi(210), markupapi(211-214), domainapi(215-221), parserapi(222),
nodes(223-228), logging(229), i18n(230-232), utils(233-237), testing(238), deprecated(239-249).
Just-completed batch: docnames 43–44 (extdev/index, extdev/appapi — the 18-page Application API ref).
extdev/appapi confirmed F2+F3+F7+F9 with NO new finding kind across all 18 pages; extdev/index has an
out-of-scope graphviz placeholder (p.174, SC#3). Tables render correctly (positive).
Reusable scratch (baselines + PDF cached, no rebuild needed) at
`/tmp/nix-shell.xfyTmL/claude-1000/-home-yuta-Documents-typsphinx/bb467912-9dc4-4f19-866f-28d8a46238c3/scratchpad/17-audit/`
(index.pdf 15,153,646 B, corpus_html_build/, corpus_text_build/, findings.md, mark.py; corpus rST source at
`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc/`). 9 systemic/candidate findings (F1–F9); **F9 new**
= every intra-paragraph reStructuredText semantic (soft) line break renders as a HARD line break (visible
only where source clauses are short). Also logged a mapping-table boundary note (html_themes/index vs
templating, pp.161–172) in the catalogue — infra, not an AUD-01 finding. Task 2 (out-of-scope classification
+ severity finalize + deterministic re-sort) and 17-02-SUMMARY.md are deferred until all 151 docnames audited.

Progress: [██████░░░░] 57% (3/3 Phase-16 plans; Phases 17–18 plan counts TBD)

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

- Total plans completed (project cumulative): 46 (15 in v0.4.4, 13 in v0.5.0, 15 in v0.6.0, 3 in v0.6.1)
- v0.6.1 plans completed: 3 (Phase 16: 16-01 todo_node 6min, 16-02 manpage 6min, 16-03 length-converter)
- Average duration: ~6min/plan (Phase 16)

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 17 P01 | 13min | 3 tasks | 1 files |

## Accumulated Context

### Decisions

Roadmap-shaping decisions for v0.6.1 (full log in PROJECT.md Key Decisions):

- [Roadmap]: TODO-01/MAN-01/LEN-01 grouped into one early Phase 16 — independent, additive, low-risk translator changes (two new `visit_*` handlers + one converter refactor); they do NOT depend on the audit.
- [Roadmap]: AUD-01 is an isolated **discovery** phase (17) — warnings only surface *dropped* content, so a human-assisted visual audit is the only way to find *silent* mis-renders; its output is a written catalogue artifact.
- [Roadmap]: FID-01 (Phase 18) is sequenced AFTER AUD-01 and is **discovery-sized** — the concrete per-issue fix list is unknown until the audit enumerates it; success criterion is "every high-severity issue fixed with a real-compile fixture," not a fixed count. Plan count TBD until AUD-01 completes.
- [Roadmap]: GATE-03 folded into Phase 18 as its closing success criteria (not a standalone thin gate phase) — it validates the whole milestone: corpus still fatal-free (GATE-02 non-regression) AND `todo_node`/`manpage` gone from the `unknown_visit` catalogue.
- [Roadmap]: Phase 17 depends on Phase 16 — audit the corpus with the new handlers already landed, so the audit surfaces genuinely-silent divergence, not the already-scheduled `todo_node`/`manpage` drops.
- [Phase 16]: `visit_todo_node` gated on `config.todo_include_todos` via `raise nodes.SkipNode`, mirroring every official Sphinx builder — draft notes never leak into published PDFs.
- [Phase 16]: `visit_manpage`/`depart_manpage` = 100% delegation to `visit_emphasis`/`depart_emphasis` (duck-typed, no bespoke state machine); no linkification with `manpages_url` unset.
- [Phase 16]: computed widths on `figure()`/`table()` must use the `block(width: ...)[...]` wrapper — both functions reject a direct `width:` kwarg; convert once at visit, consume at depart (one warning per occurrence).
- [Phase ?]: [Phase 17-01]: Corrected the docname->page mapping to a position-ordered interleaved heading/include walk after the mandated spot-check caught a real misattribution in multi-toctree-group landing pages (index, usage/domains/index, development/html_themes/index, man/index, usage/extensions/index).
- [Phase ?]: [Phase 17-01]: Represented the 5 non-contiguous docnames with multiple page-range fragments per row rather than an artificial single contiguous range.

### Pending Todos

None yet.

### Blockers/Concerns

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

Last session: 2026-07-19T03:21:42.742Z
Stopped at: 17-02 PARTIAL — 44/151 docnames audited; resume from extdev/event_callbacks
Resume file: .planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md (progress tracker = resume boundary)

## Operator Next Steps

- Plan Phase 17 with `/gsd-plan-phase 17` (AUD-01 — rendering-fidelity audit; human-assisted visual corpus diff).
