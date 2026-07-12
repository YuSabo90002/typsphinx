---
phase: 12-high-volume-independent-node-handlers
plan: 02
subsystem: translator
tags: [typst, sphinx, xref, glossary, docutils-labels, render-gate]

# Dependency graph
requires:
  - phase: 12-01
    provides: visit_versionmodified/visit_inline classed-dispatch pattern and the shared test_pdf_render_gate.py file this plan appends to (file-ownership sequencing only, per D-03 wave note)
provides:
  - "depart_term bracket-wrap <label> anchor emission, closing the fatal dangling-:term:-anchor bug"
  - "Confirmed-and-covered visit_reference refid branch (D-03: not modified, only verified)"
  - "xref_refid_render_gate fixture (:ref: section anchor + :term: glossary ref, both resolving)"
  - "TestXrefRefidRenderGate real-compile must-fail-until-fixed acceptance gate"
affects: [13-shared-dispatch-point-changes, 14-footnotes, 15-full-corpus-validation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bracket-wrap markup-mode <label> anchor attachment on a buffer-swapped node (visit_title/depart_title precedent, now also depart_term) -- never +-join a bare label(...) onto content"

key-files:
  created:
    - tests/fixtures/xref_refid_render_gate/conf.py
    - tests/fixtures/xref_refid_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_pdf_render_gate.py

key-decisions:
  - "Reused the exact 'Widget' term name from 12-RESEARCH.md's live typst.compile() proof session for fixture/test continuity with the documented investigation"
  - "Logged the pre-existing 'unknown node type: <glossary>' warning (no visit_glossary handler; content still renders correctly via base-class warn-and-continue) as an out-of-scope deferred item rather than adding a new handler not requested by this plan"

patterns-established:
  - "depart_term now mirrors depart_title's bracket-wrap label-anchor idiom -- any future buffer-swapped node needing a docutils-id-derived Typst anchor should follow the same form: term_content = f\"[#{{{term_content}}} <{label_id}>]\""

requirements-completed: [XREF-01]

coverage:
  - id: D1
    description: "depart_term emits a Typst <label> anchor via the bracket-wrap markup form when the term node has docutils ids, closing the fatal dangling-:term:-anchor bug"
    requirement: "XREF-01"
    verification:
      - kind: unit
        ref: "tests/test_translator.py (glossary/term suite, 8 tests) -- grep confirms node[\"ids\"][0] usage, no regression"
        status: pass
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestXrefRefidRenderGate::test_xref_refid_pdf_has_working_links_and_no_empty_link"
        status: pass
    human_judgment: false
  - id: D2
    description: "visit_reference refid branch confirmed-and-covered (not rebuilt): already emits link(<refid>, ...) for :ref:/:term:, with the empty-URL guard confirmed to never emit link(\"\", ...)"
    requirement: "XREF-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestXrefRefidRenderGate -- asserts link(< present and link(\"\", absent in generated .typ"
        status: pass
    human_judgment: false
  - id: D3
    description: "xref_refid_render_gate fixture with a resolving :ref: section anchor and a resolving :term: glossary reference, both reaching the translator with no cross-reference-resolution warning"
    requirement: "XREF-01"
    verification:
      - kind: integration
        ref: "python -m sphinx -b typst tests/fixtures/xref_refid_render_gate <tmp> -- exit 0, index.typ emitted, no 'Failed to create a cross reference'"
        status: pass
    human_judgment: false
  - id: D4
    description: "TestXrefRefidRenderGate real-compile class proves both cross-references resolve to working PDF links (sentinel + link-text presence) with no TypstCompilationError and no LEAK_SIGNATURES token"
    requirement: "XREF-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestXrefRefidRenderGate::test_xref_refid_pdf_has_working_links_and_no_empty_link"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-07-12
status: complete
---

# Phase 12 Plan 02: Xref/Refid Render-Gate Fix (depart_term Anchor) Summary

**Fixed the fatal dangling-`:term:`-anchor bug by emitting a bracket-wrap Typst `<label>` in `depart_term`, confirmed `visit_reference`'s refid branch was already correct, and proved both fixes with a real-compile `TestXrefRefidRenderGate` gate that would abort without them.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-07-12T02:00:28Z (first task commit)
- **Completed:** 2026-07-12T02:03:12Z (last task commit)
- **Tasks:** 3
- **Files modified:** 3 (1 modified, 2 created)

## Accomplishments

- `depart_term` now emits the bracket-wrap markup-mode `<label>` anchor (`[#{...} <term-id>]`) for any docutils-id-bearing glossary term, so a same-document `:term:` reference's `link(<term-id>, ...)` resolves instead of aborting the entire PDF compile with `label <term-id> does not exist` -- this was a currently-live fatal bug before this plan.
- Confirmed (not rebuilt, per D-03) that `visit_reference`'s refid branch (`translator.py:2119`) already emits `link(<refid>, ...)` for `:ref:`/`:term:` cross-references, and that the adjacent empty-URL guard never emits `link("", ...)` -- both contracts held before and after this plan's change.
- Added a minimal `xref_refid_render_gate` fixture with a labeled target section (`:ref:`) and a `.. glossary::` entry (`:term:` "Widget"), both resolving cleanly during `sphinx-build` (no cross-reference-resolution warning), reaching the translator's refid branch.
- Added `TestXrefRefidRenderGate`, a real `sphinx-build -> typst.compile() -> pypdf` acceptance test with an uncaught `typst.compile()` call -- the must-fail-until-fixed guard for the anchor bug -- proving both the `:ref:` and `:term:` cross-references render as working links with visible text in the compiled PDF, and no `link("", ...)` leak.

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix depart_term to emit a bracket-wrap label anchor; confirm the refid branch (XREF-01, D-03/D-04)** - `79c9d45` (fix)
2. **Task 2: Create the xref_refid_render_gate fixture (must include :ref: AND :term:) (XREF-01, D-04, SC#5)** - `5d4e8d7` (test)
3. **Task 3: Add TestXrefRefidRenderGate real-compile class — must-fail-until-fixed on the :term: anchor (XREF-01, GATE-01, D-04, SC#5)** - `8e81603` (test)

_Note: no separate plan-metadata commit — orchestrator owns STATE.md/ROADMAP.md writes after all worktree agents in the wave complete; this SUMMARY.md itself is committed as part of the parallel-executor protocol._

## Files Created/Modified

- `typsphinx/translator.py` - `depart_term` now wraps the joined buffered term content in the bracket-wrap markup `<label>` form when `node.get("ids")` is present
- `tests/fixtures/xref_refid_render_gate/conf.py` - Minimal Sphinx config (project/author/release, `extensions = ["typsphinx"]`, `typst_documents` master tuple for "index")
- `tests/fixtures/xref_refid_render_gate/index.rst` - Labeled target section, `.. glossary::` with a "Widget" term, and a paragraph with both a resolving `:ref:` and a resolving `:term:` cross-reference, each with a sentinel word
- `tests/test_pdf_render_gate.py` - New `xref_refid_render_gate_dir` fixture and `TestXrefRefidRenderGate` class (must-fail-until-fixed acceptance gate)

## Decisions Made

- Reused the exact term name "Widget" from 12-RESEARCH.md's documented live `typst.compile()` proof session, keeping the fixture/test traceable to the original investigation that discovered the bug.
- Logged the pre-existing `unknown node type: <glossary ...>` warning (there is no `visit_glossary`/`depart_glossary` handler; the base `SphinxTranslator` warns and continues, and the wrapped `definition_list`/`term`/`definition` content still renders correctly) as an out-of-scope deferred item rather than adding a new handler -- the `glossary` wrapper node was never in this plan's scope, and neither of Task 2's acceptance criteria (no "Failed to create a cross reference" warning; a `link(<` anchor present) require it.

## Deviations from Plan

None - plan executed exactly as written. `depart_term` was the only code change (confirmed via `git diff typsphinx/translator.py` showing edits only inside that method); `visit_reference`'s refid branch and empty-URL guard are unchanged.

## Issues Encountered

- `black --check tests/` initially flagged `tests/test_pdf_render_gate.py` for a quote-style normalization in the new test's assertion messages (double- vs. single-quote escaping). Ran `black` (not `--check`) to auto-format, re-verified the diff touched only quote style (no logic change), and re-ran the full test suite + `ruff check .` + `mypy typsphinx/` to confirm still green.
- `pytest -m "not slow" -q` shows the same 45 pre-existing environmental failures documented in `deferred-items.md` (Plan 12-01) -- `subprocess.run(["uv", "run", "sphinx-build", ...])`-based integration tests hitting the NixOS dynamic-linking PATH-shadowing hazard. Confirmed unrelated: none of the 4 failing files were touched by this plan, and the 374 passing tests include the full glossary/definition-list/reference unit suite (8 tests specifically re-run and green).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The GATE-01 standing bar is extended: 6 render-gate classes now pass in `tests/test_pdf_render_gate.py`, including this plan's `TestXrefRefidRenderGate` proving the `:ref:`/`:term:` refid path resolves in a real compile.
- `typsphinx/translator.py` and `tests/test_pdf_render_gate.py` were both files-modified in this plan and in 12-01 (file-ownership sequencing, D-03 wave note) -- no logical dependency, but the two plans' diffs to these shared files are now both landed on this wave's branch.
- No blockers for Phase 12's remaining plans (DESC-01..04, BLK-01/04/05/06) or Phase 13 (shared `visit_title` generalization) -- `depart_term`'s bracket-wrap fix is isolated to the `term` node and does not touch `visit_title`/`visit_figure`.

---
*Phase: 12-high-volume-independent-node-handlers*
*Completed: 2026-07-12*

## Self-Check: PASSED

All claimed files exist (`typsphinx/translator.py`, `tests/fixtures/xref_refid_render_gate/conf.py`, `tests/fixtures/xref_refid_render_gate/index.rst`, `tests/test_pdf_render_gate.py`) and all 4 task/summary commit hashes (`79c9d45`, `5d4e8d7`, `8e81603`, `6112ae0`) are present in git log.
