---
phase: 14-footnotes-doctree-pre-pass
plan: 02
subsystem: testing
tags: [docutils, typst, footnotes, translator, gate-01, real-compile, pypdf]

# Dependency graph
requires:
  - phase: 14-footnotes-doctree-pre-pass (Plan 01)
    provides: the visit_document footnote pre-pass index, visit_footnote SkipNode suppression, and visit_footnote_reference definition/reuse emission handlers this plan proves end-to-end
provides:
  - a real-compile GATE-01 acceptance fixture (tests/fixtures/footnote_render_gate/) combining SC#1-4 in one master document
  - TestFootnoteRenderGate in tests/test_pdf_render_gate.py -- four thin methods sharing one class-scoped real sphinx-build/typst.compile()/pypdf artifact
  - a state-clobbering bug fix in visit_footnote_reference's buffer-swap (save/restore in_paragraph/paragraph_has_content around the nested walkabout)
affects: [15-full-corpus-validation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "class-scoped pytest fixture (topic_line_block_render_gate_pdf_text precedent) shared across N thin assertion-only test methods, avoiding N recompiles"
    - "save/restore in_paragraph + paragraph_has_content around any nested child.walkabout(self) that walks a node containing its own paragraph child -- required whenever a buffer-swap recurses into a full subtree, not just a leaf inline span"

key-files:
  created:
    - tests/fixtures/footnote_render_gate/conf.py
    - tests/fixtures/footnote_render_gate/index.rst
  modified:
    - tests/test_pdf_render_gate.py
    - typsphinx/translator.py

key-decisions:
  - "[Rule 1 - Bug] Fixed a state-clobbering bug in visit_footnote_reference's buffer-swap discovered while building the GATE-01 fixture: the footnote body's own nested paragraph child unconditionally reset self.in_paragraph/self.paragraph_has_content to False on depart, silently dropping the outer paragraph's next-statement separator and producing a FATAL 'expected semicolon or line break' Typst compile abort for any footnote followed by trailing text in the same sentence -- i.e. every realistic footnote citation. Fixed by adopting this file's own established save/restore convention (matches visit_emphasis/visit_strong/visit_subscript/visit_superscript exactly)."

patterns-established:
  - "Any visit_* handler that buffer-swaps and then child.walkabout()s a SUBTREE (not just inline children) must save/restore in_paragraph + paragraph_has_content around the walk -- the existing convention only covered single-level inline spans; footnote bodies are the first case walking a node whose own child is a full paragraph"

requirements-completed: [FN-01]

coverage:
  - id: D1
    description: "The footnote fixture compiles to PDF via an UNCAUGHT real typst.compile() with no TypstCompilationError (GATE-01 empirical bar), covering SC#1-4 in one master document"
    requirement: "FN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFootnoteRenderGate (class-scoped fixture setup)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#1: a footnote referenced ONCE renders its body sentinel exactly once, no floating body at the definition location"
    requirement: "FN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFootnoteRenderGate::test_single_reference_body_once"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#2: a footnote referenced from two paragraphs renders a marker at both sites while its body sentinel appears exactly once (D-03 reuse form does not duplicate the body)"
    requirement: "FN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFootnoteRenderGate::test_double_reference_body_not_duplicated"
        status: pass
    human_judgment: false
  - id: D4
    description: "SC#3: a footnote body with emph/literal and markup-special characters (@ # $ _ * < >) renders correctly, proving the buffer-swap preserved inline markup and escaping"
    requirement: "FN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFootnoteRenderGate::test_body_inline_markup_and_special_chars"
        status: pass
    human_judgment: false
  - id: D5
    description: "SC#4: a footnote cited from inside a bullet-list item compiles cleanly and its body sentinel is present"
    requirement: "FN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFootnoteRenderGate::test_footnote_inside_list_item"
        status: pass
    human_judgment: false
  - id: D6
    description: "No LEAK_SIGNATURES token (par({, text(\", raw(\") appears in the extracted PDF text across every SC method"
    requirement: "FN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFootnoteRenderGate (LEAK_SIGNATURES loop, all four methods)"
        status: pass
    human_judgment: false

# Metrics
duration: 15min
completed: 2026-07-12
status: complete
---

# Phase 14 Plan 02: GATE-01 Real-Compile Acceptance Gate for Footnotes Summary

**A real `typst.compile()` acceptance fixture (`footnote_render_gate`) and `TestFootnoteRenderGate` class prove the Plan 14-01 footnote handlers compile cleanly end-to-end (SC#1-4), and in doing so caught and fixed a genuine paragraph-state-clobbering bug in `visit_footnote_reference`'s buffer-swap that would have made every realistic footnote citation a fatal compile abort.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-07-12
- **Tasks:** 2
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments
- Created `tests/fixtures/footnote_render_gate/` (`conf.py` + `index.rst`), a single-master-document fixture combining all four FN-01 success-criteria shapes: a single-reference footnote (SC#1), a footnote referenced from two separate paragraphs (SC#2), a footnote body with `*emphasis*`/`` `literal` `` and the markup-special-character sequence `@ # $ _ * < >` (SC#3), and a footnote cited from inside a bullet-list item (SC#4). Footnote definitions are placed under a trailing `.. rubric:: Footnotes`, mirroring 14-RESEARCH.md's Verified Mechanism 2 (definitions positioned after their citing references in source order).
- Added `TestFootnoteRenderGate` to `tests/test_pdf_render_gate.py` with a class-scoped `footnote_render_gate_pdf_text` fixture (mirrors `topic_line_block_render_gate_pdf_text` exactly: builds once via `_run_sphinx_build_typst`, compiles the emitted `.typ` with an UNCAUGHT real `typst.compile()`, returns `pypdf`-extracted text) and four thin test methods, one per SC, each closing with the standing `LEAK_SIGNATURES` negative control.
- **Found and fixed a genuine GATE-01-class bug** (Rule 1) while proving Task 1's fixture: `visit_footnote_reference`'s definition-branch buffer-swap walks the footnote node's body children via `child.walkabout(self)` — when that body is a `paragraph` (the normal shape), `visit_paragraph`/`depart_paragraph` unconditionally reset `self.in_paragraph`/`self.paragraph_has_content` to `False`/`False` on depart. Since these are flat instance attributes (not a stack), this silently clobbered the OUTER paragraph's separator state, dropping the `"\n"` statement separator the next sibling (e.g. a trailing `"."`) needed — a FATAL `expected semicolon or line break` Typst compile abort for any footnote followed by trailing text in the same sentence, exactly 14-RESEARCH.md's documented Pitfall 1/t8 failure mode, but never previously exercised end-to-end because Plan 14-01 only verified string-assertion-tier unit tests. Fixed by adopting this file's own established save/restore convention (`was_in_paragraph = self.in_paragraph; ...; self.in_paragraph = was_in_paragraph`), matching `visit_emphasis`/`visit_strong`/`visit_subscript`/`visit_superscript` exactly.
- All four `TestFootnoteRenderGate` methods pass via one real `sphinx-build` + `typst.compile()` per class (0.31s setup, ~0s per subsequent method); the full non-integration suite (402 tests) plus the four previously-flagged integration test files (47 tests, all pass unmodified in this sandbox) — 449 tests total green; `black`/`ruff`/`mypy` clean.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the footnote_render_gate fixture project** - `4875fad` (test, bundled with the required Rule-1 translator.py fix)
2. **Task 2: Add TestFootnoteRenderGate to test_pdf_render_gate.py** - `13f1374` (test)

_Note: Task 1's commit also includes the `typsphinx/translator.py` fix, since the fixture's own `<verify>` step (a real `sphinx-build` + implied compile-safety) could not be proven without it — the two changes are load-bearing for each other and were committed together as one atomic unit, per Rule 1's "fix inline, verify, continue" flow._

## Files Created/Modified
- `tests/fixtures/footnote_render_gate/conf.py` - Minimal single-master Sphinx project (mirrors `topic_line_block_render_gate/conf.py` verbatim, project/title renamed)
- `tests/fixtures/footnote_render_gate/index.rst` - One section per SC, four ALLCAPS sentinels, real docutils footnote syntax (`[#name]_` / `.. [#name]`), definitions under a trailing `.. rubric:: Footnotes`
- `tests/test_pdf_render_gate.py` - New `footnote_render_gate_pdf_text` class-scoped fixture + `TestFootnoteRenderGate` (4 methods) + 4 new module-level sentinel constants
- `typsphinx/translator.py` - `visit_footnote_reference`'s definition branch now saves/restores `self.in_paragraph`/`self.paragraph_has_content` around the footnote body's nested `child.walkabout(self)` calls

## Decisions Made
- **[Rule 1 - Bug]** Fixed the paragraph-state-clobbering bug in `visit_footnote_reference` described above — necessary for the plan's own success criteria (all four SC methods green via a real, uncaught `typst.compile()`) to be achievable at all. See Deviations below.
- Chose auto-numbered, labeled footnotes (`.. [#name]` / `[#name]_`) for all four fixture cases, including the double-reference case (`[#double]_` cited twice) — this is docutils' documented mechanism for a footnote cited more than once from the same auto-numbered id, matching 14-RESEARCH.md's Verified Mechanism 2 doctree shape directly.
- Kept the fixture's special-character sequence (`@ # $ _ * < >`) surrounded by spaces on every side, avoiding accidental RST inline-markup recognition (a bare `*`/`_` with no adjacent whitespace can trigger emphasis/hyperlink-reference parsing) — verified correct via the real build (no unintended markup nodes appeared in the emitted `.typ`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a paragraph-state-clobbering bug in `visit_footnote_reference`'s buffer-swap**
- **Found during:** Task 1 (building the `footnote_render_gate` fixture and proving its `<verify>` step — the real `typst.compile()` check implied by the render-gate's purpose)
- **Issue:** The Plan 14-01 definition-branch buffer-swap (`typsphinx/translator.py::visit_footnote_reference`) walked `footnote_node.children[1:]` via `child.walkabout(self)` with no save/restore of `self.in_paragraph`/`self.paragraph_has_content`. Because every footnote body's top-level child is a `paragraph` node, `visit_paragraph`/`depart_paragraph` unconditionally reset both flags to `False` on depart, clobbering the OUTER paragraph's separator state. The next sibling in the outer paragraph (typically a trailing `"."` `Text` node) then found `self.in_paragraph == False` and skipped its `_add_paragraph_separator()` `"\n"` emission, producing generated Typst source with two adjacent code-mode statements on the same line with no separator (`]text(".")`) — a FATAL `expected semicolon or line break` `typst.TypstError`, aborting the entire compile. This is exactly 14-RESEARCH.md's documented Pitfall 1 / t8 failure mode, but Plan 14-01's unit tests (string-assertion tier only) never exercised a footnote followed by trailing text in the same paragraph, so it went undetected until this plan's real-compile gate.
- **Fix:** Added `was_in_paragraph`/`was_paragraph_has_content` save before the `child.walkabout(self)` loop and restore immediately after, matching the file's own established convention used identically by `visit_emphasis`, `visit_strong`, `visit_subscript`, and `visit_superscript`.
- **Files modified:** `typsphinx/translator.py`
- **Verification:** `sphinx-build -b typst` + a direct `typst.compile()` call on the fixture succeeds (previously raised `typst.TypstError: expected semicolon or line break`); `pytest tests/test_footnotes.py -x` (5/5, unaffected); full non-integration suite (402 tests) + all four previously-flagged integration files (47 tests) green; `black`/`ruff`/`mypy` clean.
- **Committed in:** `4875fad` (Task 1 commit, bundled — the fixture and the fix are load-bearing for each other)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug, discovered by the GATE-01 real-compile gate exactly as designed)
**Impact on plan:** This plan's own `<verification>` section states "No edits to `typsphinx/` runtime code" — a scope fence assuming Plan 14-01's handlers were fully correct as delivered. The real-compile gate (this plan's entire purpose) revealed they were not: the bug above blocks EVERY footnote citation followed by trailing text in the same sentence, i.e. the overwhelming majority of realistic real-world footnote usage, not an edge case. Fixing it was required for this plan's own stated success criteria ("all four SC methods pass via a real, UNCAUGHT `typst.compile()`") to be achievable at all — this is precisely the scenario the plan's own `<threat_model>` (T-14-03, "mitigate": "the UNCAUGHT `typst.compile()`... is the verification that the Plan 14-01... guard[s] hold — any fatal fails the gate loudly") anticipates and requires. No other scope creep: the fix is a 6-line, purely mechanical save/restore matching an established in-file convention, with zero behavioral change to any other node handler.

## Issues Encountered
None beyond the translator.py deviation documented above.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None. No hardcoded empty values, placeholder text, or unwired data sources were introduced by this plan.

## Threat Flags
None. No new network endpoints, auth paths, file-access patterns, or schema changes were introduced. The fixture RST is static, author-controlled test content (not attacker-influenced input), matching this plan's own `<threat_model>` T-14-SC disposition (`accept`, zero new packages).

## Next Phase Readiness
- FN-01 is now fully proven end-to-end: the Plan 14-01 handlers plus this plan's real-compile gate close out the footnotes requirement, with the render-gate suite now 10 classes (9 Phase 11-13 + this plan's `TestFootnoteRenderGate`).
- The `visit_footnote_reference` state-management fix is a general-purpose correctness improvement (any future handler that buffer-swaps into a subtree containing its own paragraph child would hit the identical bug) — no further action needed, but worth noting as a reusable pattern for Phase 15's full-corpus validation if any other node combination surfaces a similar state-clobber.
- No blockers. Phase 14 (footnotes-doctree-pre-pass) is complete; ready for Phase 15 (full-corpus `-b typstpdf` validation of Sphinx's own `doc/` tree, GATE-02).

---
*Phase: 14-footnotes-doctree-pre-pass*
*Completed: 2026-07-12*

## Self-Check: PASSED

- FOUND: tests/fixtures/footnote_render_gate/conf.py
- FOUND: tests/fixtures/footnote_render_gate/index.rst
- FOUND: tests/test_pdf_render_gate.py (TestFootnoteRenderGate class confirmed present)
- FOUND: typsphinx/translator.py
- FOUND: commit 4875fad (test(14-02): add footnote_render_gate fixture project)
- FOUND: commit 13f1374 (test(14-02): add TestFootnoteRenderGate GATE-01 acceptance gate)
