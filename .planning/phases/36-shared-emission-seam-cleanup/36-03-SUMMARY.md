---
phase: 36-shared-emission-seam-cleanup
plan: 03
subsystem: translator
tags: [translator, math, tdd, byte-diff, pdf-invariance, math-02]

# Dependency graph
requires:
  - phase: "36-02"
    provides: "visit_desc_signature/visit_rubric decoupled from visit_strong (a different handler, untouched by this plan); confirmed this plan's MATH-02 diff never contaminates that decoupling diff (D-07)"
provides:
  - "visit_math_block emits exactly one blank line after block math inside a list item, on both the mitex and native emission paths, for both plain and :label:-carrying equations"
  - "tests/fixtures/inline_math_after_text_render_gate/index.rst: Construct H (block-math single-element edge)"
  - "tests/fixtures/inline_math_pdf_text_{mitex,native}.golden.txt: pre-fix PDF-text baselines for the D-04 invariance guard"
  - "tests/test_inline_math_after_text_render_gate.py: SC#3 boundary assertions (E/G) + Construct H invariance assertion (both existing methods) + new test_block_math_pdf_text_is_invariant_across_the_math02_fix method"
  - "36-GATE-EVIDENCE.md: MATH-02 RED and GREEN sections"
affects: ["36-04-sweep-and-verdict"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "GREEN strings for a byte-changing fix derived BY HAND from RED-captured strings (remove exactly one newline), never from the fixed translator's own output -- milestone invariant #4, recorded in 36-GATE-EVIDENCE.md's 'GREEN string derivation' subsection"
    - "PDF-text invariance guard (compare extracted text against a committed pre-fix baseline, never PDF bytes) as the RED-substitute for a defect whose fix is provably typographically inert"

key-files:
  created:
    - tests/fixtures/inline_math_pdf_text_mitex.golden.txt
    - tests/fixtures/inline_math_pdf_text_native.golden.txt
  modified:
    - tests/fixtures/inline_math_after_text_render_gate/index.rst
    - tests/test_inline_math_after_text_render_gate.py
    - typsphinx/translator.py
    - .planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md

key-decisions:
  - "Formatted Construct H's sole-child block math as \"*\\n  .. math::\" (bullet marker alone on its own line, directive indented on the next line) rather than \"* .. math::\" inline -- verified via docutils.core.publish_doctree that this produces the required list_item > math_block tree with no intervening paragraph, and it satisfies the plan's acceptance criterion that grep '^ *\\.\\. math::' count exactly 3 (Constructs E, G, H)."
  - "Measured (not assumed) that the mitex and native pre-fix PDF-text baselines are byte-identical to each other (cmp exit 0) -- Typst's math typesetting renders both the mitex-converted LaTeX and the native $...$ form through the same Unicode Mathematical Alphanumeric glyph substitution. This contradicts one specific Task 1 acceptance-criteria bullet (\"the two baselines differ from each other... cmp -s exits non-zero\"), which was a planning assumption that this measurement corrects. It has zero functional effect on the D-04 invariance guard, which compares each path's pre-fix baseline against that SAME path's post-fix build, never baseline-vs-baseline. Recorded transparently in 36-GATE-EVIDENCE.md's 'PDF-text baseline capture' subsection rather than silently reconciled."
  - "The GREEN section's 'fix commit SHA' is necessarily self-referential (Task 3 commits the translator.py fix and its own evidence together, per the plan's own HEAD~1-relative acceptance check), so it is recorded as 'this commit' with a pointer to `git log --oneline -1 -- typsphinx/translator.py` rather than a literal SHA that cannot exist before the commit does."

requirements-completed: [MATH-02]

coverage:
  - id: D1
    description: "Block math inside a list item emits exactly one blank line (not two, not zero) after the math call, before the following parbreak(), on both the mitex and native emission paths, for both the plain and :label:-carrying forms -- proven by exact-string boundary assertions recorded RED against the unfixed translator and GREEN after the one-statement fix."
    requirement: MATH-02
    verification:
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_mitex_path"
        status: pass
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_native_path"
        status: pass
    human_judgment: false
  - id: D2
    description: "Block math that is the sole content of a list item (no following sibling) emits byte-identical output before and after the MATH-02 fix -- the single-element edge, where the trailing separator flag has no consumer."
    requirement: MATH-02
    verification:
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_mitex_path (Construct H assertion)"
        status: pass
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_native_path (Construct H assertion)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The compiled PDF's pypdf-extracted text is unchanged by the MATH-02 fix, on both emission paths -- turning the claim 'this whitespace-only change is typographically inert' into a test against committed pre-fix baselines, per D-04."
    requirement: MATH-02
    verification:
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix"
        status: pass
    human_judgment: false

# Metrics
duration: ~9min (task commits span 09:43:01+09:00 to 09:52:20+09:00; environment provisioning and reading beforehand not included)
completed: 2026-08-01
status: complete
---

# Phase 36 Plan 03: Close MATH-02 (block-math redundant blank line) Summary

**`visit_math_block` now clears (rather than arms) the shared list-item separator flag after emitting block math, so a list item's block math is followed by exactly one blank line instead of two -- proven RED-to-GREEN on both the mitex and native paths, both plain and `:label:` forms, with a new PDF-text invariance guard confirming the fix changes zero visible output.**

## Performance

- **Duration:** ~9 min of task-commit work (`ea70913` at 09:43:01+09:00 through `995c78d` at 09:52:20+09:00), plus environment provisioning (worktree `uv sync` + NixOS `uv`/`ruff` symlink fix) and plan/research reading beforehand
- **Tasks:** 3
- **Files modified:** 6 (2 new PDF-text baseline files, 1 fixture, 1 test module, `typsphinx/translator.py`, `36-GATE-EVIDENCE.md`)

## Accomplishments

- Added Construct H to the render-gate fixture: a bullet list item whose sole child is a `.. math::` directive with no following sibling -- the block-math single-element edge, block math's counterpart to Construct F's inline-math edge. Verified via `docutils.core.publish_doctree` that the chosen rST formatting (`*\n  .. math::`) produces the intended `list_item > math_block` tree with no intervening paragraph.
- Captured two pre-fix `pypdf`-extracted PDF-text baselines from real `sphinx-build -b typstpdf` compiles (mitex default, `-D typst_use_mitex=0` native) against the UNFIXED translator: 3 pages, 1939 chars each, written verbatim to `tests/fixtures/inline_math_pdf_text_{mitex,native}.golden.txt`.
- Extended both existing render-gate test methods with SC#3 boundary assertions for Construct E and Construct G on both emission paths: the GREEN one-blank-line string must be present, the pre-fix two-blank-line form must be absent, and a hypothetical zero-blank-line form must also be absent -- a boundary check, not a presence check. Added a Construct H exact-region assertion pinning the single-element edge's emission.
- Derived all four GREEN strings by hand from the pre-fix strings recorded in the same commit -- by removing exactly one newline each, per this plan's critical constraint and milestone invariant #4 -- and wrote the derivation down in `36-GATE-EVIDENCE.md` before applying the fix.
- Recorded RED: both path tests fail on the new Construct E boundary assertion against the unfixed translator (not a collection error, `ImportError`, or skip); the new PDF-text invariance guard passes trivially pre-fix by construction.
- Added `test_block_math_pdf_text_is_invariant_across_the_math02_fix`, comparing each freshly-built PDF's extracted text against the committed pre-fix baseline on both paths, with a `difflib` unified diff in the failure message; PDF byte size/equality are never asserted (Typst embeds a `CreationDate`/`ModDate`, so identical input produces different bytes on every compile).
- Applied the one-statement fix: `visit_math_block`'s trailing bookkeeping now sets `self.list_item_needs_separator = False` instead of `True`, with the guarding comment rewritten to explain why this handler -- uniquely among block-level handlers -- must clear the flag rather than arm it (it already emitted its own unconditional separator above; and the clear must be unconditional because `_emit_id_anchors` may have already armed the flag for a `:label:`-carrying equation).
- Verified GREEN: all three test methods pass; the RED assertions flip to pass; the invariance guard stays green; Construct H's emission is confirmed byte-identical pre- and post-fix by direct string comparison, not just by test pass/fail.
- Confirmed zero collateral damage: `tests/test_desc_rubric_decoupling_render_gate.py` (Plan 02's SC#2 gate) still passes 3/3; the full suite reaches `653 passed, 1 skipped, 0 failed` -- exactly one more pass than Plan 02's recorded `652 passed, 1 skipped, 0 failed` baseline, accounting precisely for the one new invariance test method, with zero regressions elsewhere; `black`/`ruff`/`mypy` all clean.
- Appended `## RED — pre-fix run` and `## GREEN — post-fix run` sections (plus a `### RED → GREEN verdict` table) to `36-GATE-EVIDENCE.md`, leaving Plan 01's and Plan 02's sections untouched, per D-07.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Construct H and capture the pre-fix PDF-text baselines** - `ea70913` (test)
2. **Task 2: Add the SC#3 structural assertions and the D-04 invariance guard, and record RED** - `21df46a` (test)
3. **Task 3: Apply the MATH-02 fix and record GREEN** - `995c78d` (fix)

## Files Created/Modified

- `tests/fixtures/inline_math_after_text_render_gate/index.rst` - added Construct H (Task 1)
- `tests/fixtures/inline_math_pdf_text_mitex.golden.txt` - pre-fix PDF-text baseline, mitex path (Task 1, new file)
- `tests/fixtures/inline_math_pdf_text_native.golden.txt` - pre-fix PDF-text baseline, native path (Task 1, new file)
- `tests/test_inline_math_after_text_render_gate.py` - SC#3 boundary assertions + Construct H invariance assertion on both existing methods, plus the new `test_block_math_pdf_text_is_invariant_across_the_math02_fix` method and `PDF_TEXT_BASELINE_MITEX`/`PDF_TEXT_BASELINE_NATIVE` constants (Task 2)
- `typsphinx/translator.py` - `visit_math_block`'s trailing bookkeeping statement changed from arming to clearing `list_item_needs_separator`, comment rewritten (Task 3)
- `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` - Task 2 appended `## RED — pre-fix run (SC#3, D-04, D-06)`; Task 3 appended `## GREEN — post-fix run (SC#3, D-04, D-06)`

## Decisions Made

- Formatted Construct H's rST as a bullet marker alone on its own line followed by an indented `.. math::` directive on the next line, rather than the directive inline with the bullet on one line -- verified via `docutils.core.publish_doctree` that this produces the intended `list_item > math_block` tree (no intervening paragraph) and satisfies the plan's `grep -c '^ *\. \. math::'` acceptance criterion (exactly 3: Constructs E, G, H).
- Measured that the mitex and native pre-fix PDF-text baselines are byte-identical to each other (not merely similar) -- Typst renders both the mitex-converted LaTeX and the native `$...$` math form through the same Unicode Mathematical Alphanumeric glyph substitution, so extracted text carries no visible difference between the two emission paths for this fixture's math bodies. This contradicts one specific Task 1 acceptance-criteria bullet ("the two baselines differ from each other... `cmp -s` exits non-zero"), which was a planning assumption this measurement corrects; it has zero effect on the D-04 invariance guard itself (which never compares baseline-vs-baseline, only each path's own pre-fix baseline against that same path's post-fix build). Recorded transparently in `36-GATE-EVIDENCE.md` rather than silently reconciled or worked around by fabricating a difference.
- The GREEN section's "fix commit SHA" is recorded as "this commit" with a pointer to `git log --oneline -1 -- typsphinx/translator.py`, rather than a literal SHA -- Task 3's own commit necessarily cannot contain its own hash, and the plan's acceptance criteria checks `git diff HEAD~1` (a fixed one-commit distance from the RED commit), so splitting Task 3 into a translator-only commit plus a separate evidence commit would have broken that check.

## Deviations from Plan

### Measured corrections to plan assumptions (not code bugs, not fixed, documented per the phase's own "measure, don't transcribe" discipline)

**1. Task 1's cross-path PDF-text-differs acceptance criterion is empirically false.**
- **Found during:** Task 1
- **Claim in plan:** "The two baselines differ from each other (the two emission paths typeset math differently): `cmp -s tests/fixtures/inline_math_pdf_text_mitex.golden.txt tests/fixtures/inline_math_pdf_text_native.golden.txt` exits non-zero."
- **Measured:** `cmp` exits `0` -- the two baselines are byte-identical. Both emission paths render math through Typst's own math-typesetting engine (mitex converts LaTeX to Typst math syntax before Typst renders it; the native path is already Typst math syntax), so the extracted glyph sequence is the same regardless of source form.
- **Disposition:** No code to fix -- this is a false assumption in one acceptance-criteria bullet, not a defect. Not "fixed" (nothing to auto-fix); recorded as a measured finding in `36-GATE-EVIDENCE.md`'s "PDF-text baseline capture (pre-fix)" subsection and here, consistent with this phase's own precedent (D-04/D-05 in `36-CONTEXT.md` already corrected two ROADMAP/todo claims the same way). Does not affect the D-04 invariance guard's actual assertions, which never compare the two baselines to each other.
- **Files affected:** none beyond the baseline files already captured as specified.
- **Verification:** all of Task 1's OTHER acceptance criteria (both baselines non-empty, valid UTF-8, contain the prose sentinel, not inside the fixture's Sphinx source dir, `typsphinx/` untouched, existing test module green) pass as written.

---

**Total deviations:** 0 auto-fixed; 1 measured correction to a plan assumption (no code change, documented transparently).
**Impact on plan:** None on functional correctness -- the invariance guard's real contract (each path's own pre/post-fix equality) is unaffected and passes on both paths, pre-fix and post-fix.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 04 (sweep and verdict) has what it needs: the full-suite result (`653 passed, 1 skipped, 0 failed`, exactly one more than Plan 02's `652 passed, 1 skipped, 0 failed`), the MATH-02 RED→GREEN evidence, and confirmation that the SC#2 decoupling gate (`tests/test_desc_rubric_decoupling_render_gate.py`) is unaffected by this plan's math-only change.
- MATH-02 (requirement) is fully closed: block math inside a list item now emits exactly one blank line after the math call, on both emission paths, for both plain and labelled equations, with a PDF-text invariance guard confirming the fix is typographically inert.
- `typsphinx/translator.py`'s only change across this plan is the single trailing-bookkeeping statement in `visit_math_block` (plus its comment); the leading separator check and `_emit_id_anchors` are unchanged, and `tests/test_math_mitex.py`/`tests/test_math_native.py`/`tests/test_math_fallback.py` remain untouched, matching the plan's scope fence exactly.

---
*Phase: 36-shared-emission-seam-cleanup*
*Completed: 2026-08-01*

## Self-Check: PASSED

All modified/created files confirmed present on disk
(`tests/fixtures/inline_math_after_text_render_gate/index.rst`,
`tests/fixtures/inline_math_pdf_text_mitex.golden.txt`,
`tests/fixtures/inline_math_pdf_text_native.golden.txt`,
`tests/test_inline_math_after_text_render_gate.py`,
`typsphinx/translator.py`,
`.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md`,
this `36-03-SUMMARY.md`) and all three task commit hashes (`ea70913`,
`21df46a`, `995c78d`) confirmed present in `git log`.
