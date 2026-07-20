---
phase: 14-footnotes-doctree-pre-pass
plan: 01
subsystem: translator
tags: [docutils, typst, footnotes, translator, doctree-pre-pass]

# Dependency graph
requires:
  - phase: 11-issue-114-fatal-fixes-graceful-degrade-net
    provides: the buffer-swap idiom (never node.astext()) and the bracket-wrap-for-label idiom ([#x(...) <label>]) under unified code-mode
  - phase: 13-shared-dispatch-point-changes-topic-line-blocks
    provides: the most recent buffer-swap precedent (visit_title) confirming the pattern's continued applicability
provides:
  - a document-order footnote id -> node pre-pass index built in visit_document
  - visit_footnote suppressing the definition node at its natural docutils location
  - visit_footnote_reference emitting Typst-native footnote() calls at the reference site (definition form on first cite, bare reuse form on repeat cite)
  - a dangling-refid warn+skip guard preventing a fatal Typst compile abort
affects: [14-02 (real-compile GATE-01 render gate for footnotes)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "docutils Node.findall() (not the deprecated .traverse()) for tree-wide node collection under this repo's strict error::DeprecationWarning pytest filter"
    - "footnote pre-pass index built inside visit_document, before body content is visited, to handle definitions positioned after their citing references in source order"

key-files:
  created:
    - tests/test_footnotes.py
  modified:
    - typsphinx/translator.py

key-decisions:
  - "Used self.document.findall(nodes.footnote) instead of the plan's literal .traverse() wording -- .traverse() is deprecated in this repo's pinned docutils and raises under the project's strict error::DeprecationWarning pytest filter (Rule 1 auto-fix)"

patterns-established:
  - "Footnote definition/reuse split via a set() of already-emitted ids, gating a bracket-wrapped definition form vs. a bare reuse form -- mirrors the Phase 11 label-attachment bracket-wrap precedent while showing the reuse form does NOT need the bracket (label as call argument, not markup-mode attachment postfix)"

requirements-completed: [FN-01]

coverage:
  - id: D1
    description: "visit_document builds a document-order {footnote-id: footnote-node} pre-pass index (self._footnote_index) plus an empty self._emitted_footnote_ids set, before any body content is visited"
    requirement: "FN-01"
    verification:
      - kind: unit
        ref: "tests/test_footnotes.py#test_footnote_index_built"
        status: pass
    human_judgment: false
  - id: D2
    description: "visit_footnote raises nodes.SkipNode, emitting nothing at the definition's natural docutils location; an unreferenced footnote is silently dropped"
    requirement: "FN-01"
    verification:
      - kind: unit
        ref: "tests/test_footnotes.py#test_visit_footnote_skips_definition"
        status: pass
    human_judgment: false
  - id: D3
    description: "The first footnote_reference to an id emits the bracket-wrapped definition form [#footnote({body}) <fn-id>], sourcing the body via buffer-swap of the footnote's children after the leading label child"
    requirement: "FN-01"
    verification:
      - kind: unit
        ref: "tests/test_footnotes.py#test_first_reference_definition_form"
        status: pass
    human_judgment: false
  - id: D4
    description: "A repeat footnote_reference to an already-emitted id emits the bare reuse form footnote(<fn-id>) with no bracket-wrap and no re-rendered body"
    requirement: "FN-01"
    verification:
      - kind: unit
        ref: "tests/test_footnotes.py#test_repeat_reference_reuse_form"
        status: pass
    human_judgment: false
  - id: D5
    description: "A dangling footnote_reference (refid absent from the index) logs a logger.warning naming the refid and skips, emitting no footnote(...) call"
    requirement: "FN-01"
    verification:
      - kind: unit
        ref: "tests/test_footnotes.py#test_dangling_reference_warns"
        status: pass
    human_judgment: false
  - id: D6
    description: "Real-compile GATE-01 proof (footnote single/double/markup/list-item render gate) that this string-level emission actually compiles"
    verification: []
    human_judgment: true
    rationale: "Deferred to Plan 14-02 per this plan's explicit scope fence -- this plan only proves the string-assertion tier; the real typst.compile() acceptance gate is a separate, not-yet-executed plan"

# Metrics
duration: 5min
completed: 2026-07-12
status: complete
---

# Phase 14 Plan 01: Footnote Doctree Pre-Pass Handlers Summary

**Typst-native footnote rendering via a document-order pre-pass index in `visit_document`, with `visit_footnote_reference` emitting the compile-proven `[#footnote({body}) <fn-id>]` / `footnote(<fn-id>)` definition/reuse forms and `visit_footnote` suppressing the definition at its natural docutils location.**

## Performance

- **Duration:** ~5 min
- **Completed:** 2026-07-12
- **Tasks:** 2
- **Files modified:** 2 (`typsphinx/translator.py`, `tests/test_footnotes.py`)

## Accomplishments
- Added a document-order `{footnote-id: footnote-node}` pre-pass index (`self._footnote_index`) plus `self._emitted_footnote_ids` set, built in `visit_document` before any body content is visited — required because docutils positions footnote definitions at their literal source location, often after all citing references.
- `visit_footnote` now raises `nodes.SkipNode`, so a footnote definition never emits body text at its own docutils location; a defined-but-never-referenced footnote is silently dropped (D-09), by design.
- `visit_footnote_reference` emits the two compile-proven forms from 14-RESEARCH.md: the bracket-wrapped definition `[#footnote({body}) <fn-id>]` on first citation (body sourced via buffer-swap, skipping the footnote's leading `label` child, never `node.astext()`), and the bare reuse form `footnote(<fn-id>)` on every repeat citation — with numbering owned entirely by Typst's native `footnote()` auto-numbering.
- A dangling `refid` (not present in the pre-pass index) logs a `logger.warning` naming the refid and skips emission entirely, before any `footnote(...)` call is written — closing the fatal "label does not exist in the document" Typst compile-abort this milestone has repeatedly guarded against.
- Five new unit tests (`tests/test_footnotes.py`) exercise all five branches (index / skip / definition / reuse / dangling) at the string-assertion tier; all pass.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write tests/test_footnotes.py (test-first, RED)** - `59a82a6` (test)
2. **Task 2: Implement the three footnote handlers in translator.py (GREEN)** - `633724e` (feat)

_Note: Task 2 was `tdd="true"` but this plan's RED (test) commit landed as Task 1 and GREEN (feat) as Task 2 — no separate REFACTOR commit was needed._

## Files Created/Modified
- `tests/test_footnotes.py` - New unit-test module: 5 test functions covering D-01 (index build), D-05/D-09 (definition suppression + silent drop), D-02/D-03/D-06 (definition-form emission), D-03 (reuse-form emission, no duplicate body), D-08 (dangling-refid warn+skip)
- `typsphinx/translator.py` - `visit_document` gains the D-01 pre-pass index build (inserted before the existing `#{` unified-code-mode wrapper line); new `visit_footnote` (D-05, `SkipNode`); new `visit_footnote_reference` (D-02/D-03/D-04/D-06/D-08, the full definition/reuse/dangling emission logic)

## Decisions Made
- **[Rule 1 - Bug] Used `self.document.findall(nodes.footnote)` instead of the plan's literal `.traverse()` wording.** `Node.traverse()` is deprecated in this repo's pinned docutils (0.22.4) and raises `DeprecationWarning` on every call; this project's `pyproject.toml` escalates `DeprecationWarning` to a hard test failure (`filterwarnings = ["error::DeprecationWarning", ...]`, per the Phase 8 decision log in PROJECT.md). `findall()` is docutils' documented direct replacement with identical semantics for this call (a generator over matching descendant nodes, consumed identically by the dict comprehension). This is the only deviation from the plan's literal Code Examples section; the resulting index shape, behavior, and all five unit-test assertions are unchanged.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `.traverse()` deprecated, replaced with `.findall()`**
- **Found during:** Task 2 (implementing `visit_document`'s pre-pass index)
- **Issue:** The plan's Code Examples section (and 14-RESEARCH.md/14-PATTERNS.md, both sourced from the same research session) specify `self.document.traverse(nodes.footnote)` verbatim. Running the new test suite immediately failed with `DeprecationWarning: nodes.Node.traverse() is obsoleted by Node.findall().`, escalated to a hard `pytest` failure by this project's strict warning filter (`pyproject.toml` `filterwarnings`).
- **Fix:** Replaced `self.document.traverse(nodes.footnote)` with `self.document.findall(nodes.footnote)` — the non-deprecated, semantically identical docutils API for this exact call.
- **Files modified:** `typsphinx/translator.py`
- **Verification:** `tests/test_footnotes.py -x` passes with no `DeprecationWarning`; full 398-test non-integration suite green.
- **Committed in:** `633724e` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug/deprecated-API fix)
**Impact on plan:** Purely mechanical substitution of a non-deprecated API for a deprecated one with identical call-site semantics; no behavioral change to the pre-pass index, the emission logic, or any test expectation. No scope creep.

## Issues Encountered
None beyond the `.traverse()`/`.findall()` deviation documented above.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None. No hardcoded empty values, placeholder text, or unwired data sources were introduced by this plan.

## Threat Flags
None. This plan's only new interpolation point (`f"fn-{refid}"`) uses a docutils-assigned id, matching the plan's own `<threat_model>` T-14-02 disposition (`accept`, no new sanitization needed). No new network endpoints, auth paths, or file-access patterns were introduced.

## Next Phase Readiness
- The three translator handlers and the pre-pass index are in place; `typsphinx/translator.py` and `tests/test_footnotes.py` are ready for Plan 14-02 to add the real `typst.compile()` GATE-01 render-gate fixture (`tests/fixtures/footnote_render_gate/`) and the new `TestFootnoteRenderGate` class in `tests/test_pdf_render_gate.py`, per this plan's explicit scope fence.
- No blockers. `writer.py`, `template_engine.py`, and `templates/base.typ` (the 3-way `@preview` version-sync surface) were untouched, as required.

---
*Phase: 14-footnotes-doctree-pre-pass*
*Completed: 2026-07-12*

## Self-Check: PASSED

- FOUND: tests/test_footnotes.py
- FOUND: typsphinx/translator.py
- FOUND: commit 59a82a6 (test(14-01): add failing tests for footnote pre-pass handlers)
- FOUND: commit 633724e (feat(14-01): implement footnote pre-pass handlers (FN-01))
- Confirmed `_footnote_index`, `visit_footnote`, and `visit_footnote_reference` present in typsphinx/translator.py
