---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 02
subsystem: testing
tags: [sphinx, typst, translator, rubric, gate-01, render-gate]

# Dependency graph
requires:
  - phase: 36-shared-emission-seam-cleanup
    provides: "the desc_signature/rubric decoupling (D-01/D-02) whose shared _strong_was_* save slots this plan's RED exercises"
  - phase: 38-structural-indentation-info-fields
    provides: "the pad(left: SHARED_INDENT_STEP, ...) wrapper that already carries the rubric's indent (measured, not re-derived, in this plan)"
provides:
  - "This phase's classic GATE-01 RED (D-13): a document-wide par() wrapper drop after a rubric with an inline strong child"
  - "The D-11 double-blank-line wart RED, asserted on the existing desc_rubric_decoupling fixture"
  - "39-GATE-EVIDENCE-02.md recording both REDs, hand-derived, against the untouched translator"
affects: [39-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Document-wide RED proven by asserting THREE paragraphs (adjacent + two separated by section headings), not one, to forbid a fix that only papers over the immediately-next paragraph"
    - "CONTROL constructs placed BEFORE a document-wide-corrupting defect in fixture source order, not after, when the defect's corruption never resets within the document"

key-files:
  created:
    - tests/fixtures/rubric_strong_nesting_render_gate/conf.py
    - tests/fixtures/rubric_strong_nesting_render_gate/index.rst
    - tests/test_rubric_strong_nesting_render_gate.py
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-02.md
  modified:
    - tests/test_desc_rubric_decoupling_render_gate.py

key-decisions:
  - "CONTROL rubric+paragraph placed BEFORE the defect rubric in the new fixture's document order (not after, as the plan's prose literally listed), because D-13's state corruption never resets within a document -- placing the CONTROL after would make its own paragraph-wrap assertion RED too, contradicting the plan's own must_haves (CONTROL asserted GREEN in both directions)."
  - "The defect rubric sits inside its own section heading (\"Defect Rubric Section\") purely as a fixture-authoring necessity: without an enclosing section boundary to close first, the very first heading following the D-13-corrupted paragraph collides with Typst's trailing-content-block call sugar (text(\"...\")[#heading(...)] parses as an extra positional argument to text()) and aborts the compile-sanity leg with a real TypstError, unrelated to D-13 itself."

requirements-completed: [ADM-05]

coverage:
  - id: D1
    description: "Document-wide GATE-01 RED for D-13 (rubric+strong nesting): three paragraphs after the defect rubric, including two separated by section headings, lose their par() wrapper"
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_paragraph_immediately_after_defect_rubric_loses_par_wrapper"
        status: fail
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_second_later_paragraph_still_loses_par_wrapper"
        status: fail
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_third_later_paragraph_still_loses_par_wrapper"
        status: fail
    human_judgment: false
  - id: D2
    description: "CONTROLs isolating D-13 to the nested-inline-child case: a markup-free rubric's own paragraph stays wrapped, and the defect rubric's own bold-wrapper bytes are unchanged"
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_control_paragraph_after_markup_free_rubric_stays_wrapped"
        status: pass
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_control_defect_rubrics_own_emission_is_unchanged"
        status: pass
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_fixture_compiles_to_valid_typst"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-11 double-blank-line wart RED on the existing desc_rubric_decoupling fixture: the newline run between a propagated-target anchor and the rubric's wrapper open measures 3, hand-derived post-fix expectation is 1"
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_propagated_target_rubric_separator_run_is_not_yet_one"
        status: fail
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_control_non_propagated_target_rubrics_keep_current_byte_shape"
        status: pass
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 02: Rubric-Half GATE-01 RED (D-11/D-13) Summary

**Recorded this phase's classic GATE-01 RED (D-13: a rubric with a real inline strong child clobbers the shared `_strong_was_*` save slots, so every subsequent paragraph in the document loses its `par()` wrapper) plus the D-11 double-blank-line wart, both hand-derived and both proven against the untouched translator with zero changes to `typsphinx/`.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-02
- **Tasks:** 3
- **Files modified:** 4 created, 1 modified

## Accomplishments
- Built `tests/fixtures/rubric_strong_nesting_render_gate/` and `tests/test_rubric_strong_nesting_render_gate.py`: three RED assertions proving D-13's `par()`-wrapper drop is document-wide (an adjacent paragraph plus two more separated by section headings), two CONTROLs proving the defect is isolated to a rubric with a real inline `strong` child, and a compile-sanity leg confirming both the defect and control constructs compile perfectly today.
- Extended `tests/test_desc_rubric_decoupling_render_gate.py` with a newline-run assertion measuring the D-11 double-blank-line wart (today: 3 newlines between a propagated-target anchor and the rubric's wrapper open; hand-derived post-fix expectation: 1) plus a CONTROL over the fixture's two non-propagated-target rubrics, without touching the fixture's `index.rst` or `golden.typ`.
- Wrote `39-GATE-EVIDENCE-02.md` recording both REDs verbatim against the plan-start commit, with a call-by-call/newline-by-newline hand derivation for each, citations to both folded defects (the pending todo and `visit_rubric`'s own docstring), and D-12's position that ADM-05's own indentation property already holds and is not red-able.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the rubric-with-inline-markup fixture and its document-wide RED gate** - `dd8a4a6` (test)
2. **Task 2: Assert the D-11 double-blank-line wart on the existing decoupling fixture** - `8cbe730` (test)
3. **Task 3: Record the rubric RED evidence against a named commit** - `7a94066` (docs)

## Files Created/Modified
- `tests/fixtures/rubric_strong_nesting_render_gate/conf.py` - Minimal Sphinx config for the new fixture, cloned from the decoupling fixture's own `conf.py`
- `tests/fixtures/rubric_strong_nesting_render_gate/index.rst` - CONTROL rubric+paragraph first, then the defect rubric (inside its own section) with three cascading paragraphs proving the document-wide RED
- `tests/test_rubric_strong_nesting_render_gate.py` - Six tests: three RED (document-wide `par()` drop), two CONTROL, one compile-sanity leg
- `tests/test_desc_rubric_decoupling_render_gate.py` - Two new test methods: the D-11 RED newline-run assertion and its CONTROL, added without touching the module's pre-existing tests or the fixture directory
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-02.md` - Evidence file recording both REDs, hand derivations, folded-defect citations, and the D-12 position

## Decisions Made
- **CONTROL-before-DEFECT fixture ordering (deviation from the plan's literal prose order — see below).**
- **Defect rubric wrapped in its own section heading** so the compile-sanity leg reaches a valid PDF (fixture-authoring necessity, not part of the measured defect — see below).
- Expected `par({text("...")})` and newline-run-of-1 values were derived by reading `visit_paragraph`/`visit_Text`/`depart_paragraph`/`_emit_id_anchors`/`visit_rubric` line by line, never by running a candidate fix and copying its output (the plan's `must_haves.prohibitions`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reordered the new fixture so the CONTROL construct precedes the defect construct**
- **Found during:** Task 1, while verifying the fixture's build output against the plan's stated acceptance criterion that "the two CONTROL assertions ... pass against the untouched translator"
- **Issue:** The plan's `<action>` prose lists the fixture's constructs "in this order": defect rubric, three cascading paragraphs, THEN the CONTROL rubric+paragraph. D-13's corruption is document-wide and never resets (confirmed by direct measurement of the untouched translator's real build output), so placing the CONTROL *after* the defect construct made the CONTROL's own paragraph-wrap assertion RED too — directly contradicting the plan's own `must_haves.truths` ("A CONTROL rubric ... is asserted GREEN in both directions") and the acceptance criterion quoted above.
- **Fix:** Placed the CONTROL rubric and its paragraph FIRST in `index.rst`, before the defect rubric, so the CONTROL's assertion is measured against genuinely unbroken state. All of the plan's other ordering-independent acceptance criteria (exactly two rubrics each labelled by a comment, four distinct paragraphs in the stated relationships) are still satisfied.
- **Files modified:** `tests/fixtures/rubric_strong_nesting_render_gate/index.rst`
- **Verification:** `uv run pytest tests/test_rubric_strong_nesting_render_gate.py -v` reports exactly three failures (the defect's cascading paragraphs) and the CONTROL assertion passes, matching the plan's stated acceptance criterion.
- **Committed in:** `dd8a4a6` (Task 1 commit)

**2. [Rule 1 - Bug] Wrapped the defect rubric in its own section heading to keep the compile-sanity leg green**
- **Found during:** Task 1, while running the plan's own `<verify>` command (`sphinx-build -b typst ... && python -c "import typst; typst.compile(...)"`)
- **Issue:** With the defect rubric and its three cascading paragraphs sitting directly under the fixture's top-level heading (no enclosing subsection), the FIRST subsequent section heading landed with ZERO separating bytes after the corrupted paragraph's `text("...")` call — `text("...")[#heading(...)]` — which Typst parses as its trailing-content-block call sugar, turning the heading into an extra (illegal) positional argument to `text()`. `typst.compile()` aborted with a genuine `unexpected argument` `TypstError`, an unrelated, real compile fatal that would have made the plan's own compile-sanity acceptance criterion fail.
- **Fix:** Added one intervening section heading ("Defect Rubric Section") immediately before the defect rubric. `depart_section`'s own unconditional trailing newline (unrelated to D-13/D-11) then supplies the missing separator at every subsequent heading boundary, so the fixture compiles cleanly while the document-wide `par()`-wrapper defect itself is unchanged and still measured identically.
- **Files modified:** `tests/fixtures/rubric_strong_nesting_render_gate/index.rst`
- **Verification:** `uv run python -m sphinx -b typst tests/fixtures/rubric_strong_nesting_render_gate /tmp/... && uv run python -c "import typst; typst.compile(...)"` exits 0 with no exception; `test_fixture_compiles_to_valid_typst` passes.
- **Committed in:** `dd8a4a6` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — fixture-construction bugs discovered by direct measurement, not translator changes)
**Impact on plan:** Both deviations are test-fixture authoring corrections that preserve every stated acceptance criterion and `must_haves` invariant; `typsphinx/` and the pre-existing `desc_rubric_decoupling_render_gate` fixture remain completely untouched (verified via `git diff --stat`). No scope creep.

## Issues Encountered
- The plan's literal construct ordering for the new fixture (defect, then CONTROL) was internally inconsistent with its own required outcome (CONTROL green today) given D-13's document-wide, non-resetting corruption — resolved by reordering (see Deviations above).
- A second, unrelated real compile fatal (Typst's trailing-content-block call sugar colliding with the corrupted state's missing separator at the first following heading) would have blocked the compile-sanity leg — resolved by adding one section boundary (see Deviations above), which supplies a separator through an entirely different, pre-existing mechanism (`depart_section`'s own unconditional newline) unrelated to either D-11 or D-13.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 39-06 (the rubric fix plan) has both REDs it needs to turn GREEN, with hand-derived post-fix expectations recorded in `39-GATE-EVIDENCE-02.md`: D-13's `par({text("...")})` wrapper for every paragraph, and D-11's newline-run-of-1 at the propagated-target anchor/rubric boundary.
- Both new CONTROL assertions in this plan's tests will fail if 39-06's fix over-corrects (e.g. stops wrapping paragraphs after every rubric, or strips separators indiscriminately) or under-corrects (alters the rubric's own bold-wrapper emission instead of its state bookkeeping) — they should stay green through the fix.
- No blockers. `typsphinx/` remains untouched by this plan; the module's pre-existing byte-identity golden test (`test_emitted_typ_is_byte_identical_to_golden`) stays green, confirming this plan changed zero emitted bytes.

## Self-Check: PASSED

- FOUND: `tests/fixtures/rubric_strong_nesting_render_gate/conf.py`
- FOUND: `tests/fixtures/rubric_strong_nesting_render_gate/index.rst`
- FOUND: `tests/test_rubric_strong_nesting_render_gate.py`
- FOUND: `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-02.md`
- FOUND commit `dd8a4a6` (Task 1)
- FOUND commit `8cbe730` (Task 2)
- FOUND commit `7a94066` (Task 3)

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*
