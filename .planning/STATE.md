---
gsd_state_version: 1.0
milestone: v0.6.0
milestone_name: — real-world robustness
current_phase: 14
current_phase_name: footnotes-doctree-pre-pass
status: executing
stopped_at: Completed 14-01-PLAN.md
last_updated: "2026-07-12T05:36:54.474Z"
last_activity: 2026-07-12
last_activity_desc: Phase 14 execution started
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 12
  completed_plans: 11
  percent: 60
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-11 — milestone v0.6.0 started)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable output for large real-world documentation sets — Sphinx's own `doc/` tree compiles end-to-end through `typstpdf` with no fatal Typst errors, and the highest-frequency previously-dropped nodes render correctly.
**Current focus:** Phase 14 — footnotes-doctree-pre-pass

## Current Position

Phase: 14 (footnotes-doctree-pre-pass) — EXECUTING
Plan: 2 of 2
Status: Ready to execute
Last activity: 2026-07-12 — Phase 14 execution started

Progress: [██████████] 100%

## Roadmap Summary (v0.6.0 — Phases 11–15)

| Phase | Goal | Requirements |
|-------|------|--------------|
| 11 — Issue #114 Fatal Fixes + Graceful-Degrade Net | Fix px→pt + figure caption/`:target:` buffer-swap + graphviz/inheritance skip; stand up the real-compile gate | FIG-01, FIG-02, DEG-01, DEG-02, GATE-01 |
| 12 — High-Volume Independent Node Handlers | versionmodified, empty-URL/`refid` refs, autodoc `desc_*`, transition/glossary/tabular_col_spec/abbr | XREF-01, VER-01, DESC-01..04, BLK-01, BLK-04, BLK-05, BLK-06 |
| 13 — Shared Dispatch-Point Changes | Generalize `visit_title` for topic + line/line_block, with admonition-title regression fixtures | BLK-02, BLK-03 |
| 14 — Footnotes (doctree pre-pass) | Typst-native `footnote[...]` via id-keyed pre-pass; the only architecturally-new item | FN-01 |
| 15 — Full-Corpus Validation | Real `-b typstpdf` of Sphinx's own `doc/` tree; catalogue warnings + measure empty-URL reduction | GATE-02 |

Standing bar (GATE-01): every node-handler phase (11–14) ships or extends a real `typst.compile()` acceptance fixture — string-agreement asserts alone never suffice.

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 28 (15 in v0.4.4, 13 in v0.5.0)
- v0.6.0 plans completed: 0
- Average duration: — min

**Recent Trend:**

- Last 5 plans (v0.5.0): 3min, 39min, 5min, 5min (Phase 9–10)
- Trend: — (new milestone, no plans executed yet)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Roadmap-shaping decisions for v0.6.0:

- [Roadmap]: Issue #114 fatal fixes (FIG-01/FIG-02) are Phase 11 (first) — they BLOCK all real-compile validation of everything else, since a single fatal node aborts the whole PDF.
- [Roadmap]: DEG-01/DEG-02 (graphviz/inheritance skip overrides) placed in Phase 11 too — the graceful-degrade net is what makes a full-corpus compile run usable as a feedback tool without aborting on the first out-of-scope node.
- [Roadmap]: GATE-01 mapped to Phase 11 (where the real-compile fixture pattern is first established) and echoed as a standing success criterion across Phases 12–14.
- [Roadmap]: FN-01 (footnotes) gets its own phase (14), sequenced late — it is the only item needing a genuine doctree pre-pass; independent of Phases 12–13.
- [Roadmap]: The shared-dispatch `visit_title` change (BLK-02/BLK-03) is isolated in Phase 13 with admonition-title regression fixtures because it edits a load-bearing method every admonition + heading depends on.
- [Research]: Zero new runtime dependencies / no `@preview` bump — every target node maps to native Typst 0.15 or already-bundled packages; the 3-way version-sync surface stays untouched.
- [Phase 11-01]: Unit dispatch implemented as allow-list (not deny-list) so the full extended docutils CSS3 unit set falls into one generic warn+drop branch (D-02)
- [Phase 11-01]: Confirmed live sphinx.ext.graphviz/inheritance_diagram node-class names before finalizing visit_* method names (resolves RESEARCH.md Assumption A1)
- [Phase 11-02]: Figure caption buffer-swap guarded strictly by if self.in_figure: on both visit/depart, leaving the captioned-code-block SkipNode path (which never calls depart_caption) unaffected
- [Phase 11-02]: refid fallback branch in visit_reference inserted as an early return before the existing empty-URL guard; no sanitization of refid, matching the adjacent #-prefixed refuri branch convention
- [Phase 11-03]: Fixed a third fatal Typst compile bug (label-in-code-mode) discovered while building GATE-01 fixtures: bracket-wrap labeled figure/heading emissions in markup content — Docutils auto-assigns ids to any captioned figure and internal :target: links require section anchors; without this fix neither figure fixture could compile, blocking GATE-01's own success criteria
- [Phase 13]: D-01/D-02/D-05/D-06 and the Pitfall-1 fix landed as one atomic task/commit (Task 1), per RESEARCH.md Pitfall 2's atomicity mandate
- [Phase 13]: Pitfall-1 multi-child-title separator+wrap fix bundled into Plan 01 rather than filed as a separate prerequisite bug fix
- [Phase 13-02]: line_block nesting tracked with a single integer depth counter (not a stack) -- docutils' own visitor recursion provides the nesting stack for free
- [Phase 13-02]: h() indent spacer needs no markup-mode bracket-wrap (unlike Phase 11's <label> anchors) -- plain code-mode stdlib call
- [Phase 13-03]: Rendered the epigraph shape as a plain top-level line_block under a titled section (no .. epigraph:: directive) per Pitfall 4 -- sidesteps a pre-existing block_quote/attribution bug
- [Phase 13-03]: Used a class-scoped GATE-01 fixture to build+compile+extract once per class, shared across three thin assertion-only test methods, avoiding three recompiles
- [Phase 13-03]: Named the admonition-regression test method without an underscore between the three words (test_admonitiontitleregression_multichild) after discovering pytest -k does a contiguous substring match
- [Phase 14-01]: Used self.document.findall(nodes.footnote) instead of the deprecated .traverse() -- traverse() raises DeprecationWarning, escalated to a hard failure by this project's strict pytest filter

### Pending Todos

None yet.

### Blockers/Concerns

Carried forward from research (SUMMARY.md / ARCHITECTURE.md / PITFALLS.md) — resolve during execution:

- [Phase 11]: **One bad node aborts the ENTIRE PDF** — `typst.compile()` is all-or-nothing over the master doc + everything it `#include()`s. Treat "does it compile" as the primary correctness signal for every handler, not "does the string look right." Fixtures must cover edge-case attribute values (`%`, `em`, `px`, `pc`, unitless width; captions containing `_`/`*`/`` ` ``/`[`/`]`).
- [Phase 11]: **Fix `visit_caption`/`depart_caption` via buffer-swap, NOT `astext()`** — `astext()` bypasses both escaping regimes and drops inline markup (the mechanism behind the `link(url,image)text(caption)` leak). Emit the caption as a code-mode `{...}` block, not a markup `[...]` block (the v0.5.0 admonition-bug class).
- [Phase 12]: **`versionmodified` child shape is MEDIUM confidence** — build a throwaway `doctree.pformat()` dump to confirm children are inline-direct vs. nested in a `paragraph` before finalizing the handler.
- [Phase 12]: **Empty-URL reduction must be MEASURED, not assumed** — the ×596 figure is a strong `refid`-gap signal, but the residual genuinely-broken count needs a real before/after build diff (finalized in Phase 15).
- [Phase 14]: **Footnote `refid` cross-link attribute + `label`-child-skip + re-citation syntax are MEDIUM confidence** — confirm all three against a live doctree dump + a real `typst compile` spot-check before locking the pre-pass design.

### Roadmap Evolution

- 2026-07-11: v0.6.0 roadmap created — Phases 11–15, derived from 19 v1 requirements (Issue #114 + high-frequency dropped-node support). Phase numbering continues from v0.5.0 (6–10 + 8.1).

## Deferred Items

Items acknowledged and carried forward from previous milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v2 | v0.5.0 scoping |
| Styling refinements | TODO-01 (`todo_node` styling), MAN-01 (`:manpage:` role), LEN-01 (generalize CSS-length converter) | Deferred to v0.6.x | v0.6.0 scoping |
| Phase 11 P01 | 15min | 3 tasks | 2 files |
| Phase 11 P02 | 10min | 2 tasks | 1 files |
| Phase 11 P03 | ~90min | 2 tasks | 11 files |
| Phase 13 P01 | 5min | 2 tasks | 3 files |
| Phase 13 P02 | 4min | 2 tasks | 2 files |
| Phase 13 P03 | 7min | 2 tasks | 3 files |
| Phase 14 P01 | 5min | 2 tasks | 2 files |

## Session Continuity

Last session: 2026-07-12T05:36:54.469Z
Stopped at: Completed 14-01-PLAN.md
Resume file: 14-02-PLAN.md

## Operator Next Steps

- Plan Phase 11 with `/gsd-plan-phase 11`
