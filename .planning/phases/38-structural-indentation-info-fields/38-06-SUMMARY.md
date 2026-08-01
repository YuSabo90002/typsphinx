---
phase: 38-structural-indentation-info-fields
plan: 06
subsystem: api
tags: [sphinx, typst, translator, docutils, field-list, indentation]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields (38-02, 38-04, 38-05)
    provides: the RED gate module and FLD-01/FLD-02 test evidence (38-02),
      the authoritative test census (38-04), and the desc_content body
      wrapper this plan's field-list wrapper nests inside (38-05)
provides:
  - "visit_field_list/depart_field_list wrap the field list in pad(left: SHARED_INDENT_STEP, {...}), nested inside desc_content's own wrapper with no depth counter (FLD-01, D-03)"
  - "visit_field_body's classification gains a single-paragraph-unwrapped case reusing the existing inline-concat context; visit_paragraph/depart_paragraph skip the block-level par(...) wrapper for it (FLD-02, D-07)"
  - "depart_field_body emits a real parbreak() between consecutive single-value fields, re-derived from the doctree (no second new instance attribute), closing the D-08 trap where the FID-09 separator would otherwise merge them onto one line"
  - "The field-list family's five pre-existing self.body.append(...) sites, plus depart_desc_signature's two anchor/spacing sites, converted to self.add_text(...) -- a field list or desc signature inside a table cell no longer aborts the compile (D-12)"
  - "Both Phase-34 PDF-text goldens re-measured and hand-verified as the predicted Construct C line-wrap consequence only (census row A3, closing owner)"
affects: [38-07, 38-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "field_list wraps its body using the same pad(left:, {...}) + self.add_text discipline as visit_desc_content/visit_block_quote -- reused, not reinvented"
    - "A field-body classification (single-paragraph-unwrapped vs. docutils-collapsed-inline) is distinguished by ONE instance attribute (_field_body_unwrapped_paragraph), consumed by visit_paragraph's wrapper-skip AND by excluding it from _last_field_body_was_inline so depart_field's FID-09 separator stays correctly scoped"
    - "Inter-sibling paragraph breaks that need doctree-derived 'is there a following sibling' logic are re-derived from node.parent.next_node(...) at the point state is still live, rather than adding a second field-level flag to survive to a later handler"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/test_field_list_in_list_item_render_gate.py
    - tests/fixtures/inline_math_pdf_text_mitex.golden.txt
    - tests/fixtures/inline_math_pdf_text_native.golden.txt

key-decisions:
  - "The field-list wrapper's separator bookkeeping (bug #4 leading guard, list_item_needs_separator on close) mirrors visit_desc_content's own decision from 38-05 byte-for-byte, for consistency with the established block-visitor pattern -- falsified against tests/test_field_list_in_list_item_render_gate.py, which is this handler's own named falsifier per the emission contract."
  - "The D-07/D-08 trap is closed by excluding _field_body_unwrapped_paragraph from _last_field_body_was_inline in depart_field_body, rather than modifying depart_field itself -- zero code change needed to the FID-09 separator's own gate, since the flag it reads is now correctly scoped by construction."
  - "Consecutive single-value fields' parbreak() is emitted from depart_field_body (using node.parent.next_node(...) to check for a following field sibling), not from depart_field re-deriving the classification -- this keeps the diff to exactly ONE new instance attribute for the whole plan, per the plan's own acceptance criterion."
  - "depart_desc_signature's two remaining self.body.append(...) sites (the per-id anchor loop and the trailing spacing newline) were also converted to self.add_text(...), beyond this plan's own files_modified/task scope -- explicitly authorized by the orchestrator's wave-3 findings as the second pre-existing table-cell compile defect 38-01 discovered, assigned to this plan alongside the field_list family's own five sites."
  - "Census row A3's two Phase-34 PDF-text goldens were migrated here as the closing owner (jointly owned with 38-05), per the orchestrator's explicit scope-extension authorization -- re-measured against a fresh build and hand-verified byte-for-byte identical to the currently-committed baseline outside the one predicted Construct C line-wrap hunk before being applied."

requirements-completed: [FLD-01, FLD-02, IND-04]

coverage:
  - id: D1
    description: "field_list gets its own pad(left: SHARED_INDENT_STEP, {...}) indent step, nested inside desc_content's own wrapper with no depth counter, driven by the same shared constant (FLD-01, D-03, IND-04)"
    requirement: "FLD-01"
    verification:
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_fld01_field_list_deeper_than_method_body"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld01_field_list_wrapper_nested_inside_desc_content_wrapper"
        status: pass
      - kind: integration
        ref: "tests/test_field_list_in_list_item_render_gate.py::TestFieldListInListItemRenderGate::test_typstpdf_separates_field_list_in_list_item_and_produces_pdf"
        status: pass
    human_judgment: false
  - id: D2
    description: "A single-value field body (the ordinary :param:/:returns:/:rtype: docstring shape) renders inline with its label instead of on the next visual line; consecutive single-value fields still occupy separate paragraphs; the multi-value bulleted rendering and the docutils-collapsed confval case are unaffected (FLD-02, D-07, D-08)"
    requirement: "FLD-02"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_value_returns_no_block_paragraph_wrapper"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_value_pdf_adjacency_matches_pinned_string"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_entry_param_renders_inline_prose_never_bulleted"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_consecutive_single_value_fields_stay_on_separate_lines"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_bulleted_multi_value_non_regression_control"
        status: pass
      - kind: unit
        ref: "tests/test_confval_field_spacing_render_gate.py::TestConfvalFieldSpacingRenderGate::test_pdf_extracted_text_matches_pinned_sc3_string"
        status: pass
      - kind: unit
        ref: "tests/test_confval_field_body_render_gate.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "The field-list family's five pre-existing self.body.append(...) sites plus depart_desc_signature's two remaining sites converted to self.add_text(...), fixing a desc or field list inside a table cell aborting the Typst compile (D-12)"
    verification:
      - kind: manual_procedural
        ref: "Ad hoc fixture (a py:attribute:: signature and a genuine RST field list, each inside its own list-table cell), built via -b typstpdf: both compile to a real, non-empty PDF where they previously aborted with 'expected semicolon or line break'."
        status: pass
    human_judgment: false
  - id: D4
    description: "The two Phase-34 PDF-text goldens (inline_math_pdf_text_mitex.golden.txt / inline_math_pdf_text_native.golden.txt) re-measured and confirmed to differ from the prior baseline only by the predicted Construct C line-wrap consequence"
    verification:
      - kind: unit
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix"
        status: pass
    human_judgment: false

# Metrics
duration: ~30min
completed: 2026-08-01
status: complete
---

# Phase 38 Plan 06: field_list Indent Wrapper + Single-Value Field-Body Reflow Summary

**field_list gets its own SHARED_INDENT_STEP pad nested inside desc_content's wrapper (FLD-01), and a single-value field body (:returns:/:rtype:/:param:) now renders inline with its label via a real parbreak() between consecutive fields instead of the block-level par() wrapper it used to get for free (FLD-02, D-07/D-08).**

## Performance

- **Duration:** ~30 min (commit-timestamp span; exact session start was not captured)
- **Tasks:** 3 planned tasks + 1 auto-fixed deviation, each committed atomically
- **Files modified:** 4 (`typsphinx/translator.py`, `tests/test_field_list_in_list_item_render_gate.py`, and the two PDF-text golden fixtures)

## Accomplishments

- `visit_field_list`/`depart_field_list` wrap the field list in `pad(left: SHARED_INDENT_STEP, {...})`, landing FLD-01: a field list nested inside a description body now renders one step beyond its surrounding body via pure composition with plan 38-05's `desc_content` wrapper -- no depth counter, no second constant.
- `visit_field_body`'s classification gains a second case: a body whose only child is exactly one `nodes.paragraph` (the ordinary `:param:`/`:returns:`/`:rtype:` docstring shape) now reuses the SAME inline-concat context (`_in_field_body`/`_field_body_has_content`) the docutils-collapsed-inline case already exercises, and `visit_paragraph`/`depart_paragraph` gain a matching branch that skips the block-level `par({`/`})` wrapper for it -- landing FLD-02's inline half.
- The D-07/D-08 trap is closed: the one new instance attribute (`_field_body_unwrapped_paragraph`) is excluded from `_last_field_body_was_inline`, so `depart_field`'s FID-09 inter-field separator stays correctly scoped to the genuinely collapsed-inline case (e.g. a confval's `:type:`/`:default:`) and never fires between newly-inlined single-value fields -- with zero code change to `depart_field` itself. Consecutive single-value fields instead get a real `parbreak()` from `depart_field_body`, re-derived from the doctree's own next-sibling check rather than a second new instance attribute.
- The field-list family's five pre-existing `self.body.append(...)` sites (`depart_field_list`, `depart_field`, `visit_field_name`, `depart_field_name`, `depart_field_body`) are converted to `self.add_text(...)`, fixing a field list inside a table cell that misrouted today -- byte-identical outside a table.
- A second, orchestrator-authorized deviation: `depart_desc_signature`'s two remaining `self.body.append(...)` sites (the per-id anchor loop and the trailing spacing newline) are also converted, closing the other table-cell compile defect 38-01 discovered.
- Both Phase-34 PDF-text goldens (`inline_math_pdf_text_mitex.golden.txt`, `inline_math_pdf_text_native.golden.txt`) are re-measured as this plan's closing-owner responsibility (census row A3) and hand-verified to differ from the prior baseline by exactly the predicted Construct C line-wrap movement, nothing else.

## Task Commits

Each task was committed atomically:

1. **Task 1: Give the field list its own indent step** - `16920ba` (feat)
2. **Task 2: Render a single-value field body inline with its label** - `d55df99` (feat)
3. **Task 3: Migrate this plan's census rows and prove the change is scoped** - `edf90a2` (test)
4. **Deviation: route depart_desc_signature's remaining table-cell-unsafe appends through add_text** - `7f7f247` (fix)

**Plan metadata:** (this commit, forthcoming)

## Files Created/Modified

- `typsphinx/translator.py` -- `visit_field_list`/`depart_field_list` given the wrapper pair (Task 1); the family's five `self.body.append` sites converted to `self.add_text` (Task 1); `visit_field_body`/`depart_field_body` gain the single-paragraph-unwrapped classification and its `parbreak()` bookkeeping (Task 2); `visit_paragraph`/`depart_paragraph` gain the matching wrapper-skip branch (Task 2); `depart_desc_signature`'s two remaining sites converted (deviation commit).
- `tests/test_field_list_in_list_item_render_gate.py` -- two assertions hand-migrated: the field list's own newline-separation proof (Task 1, a census miss one assertion upstream of row A4) and the CR-01 Author/Version marker (Task 3, row A4's own predicted break, now using the field name's `strong(...)` call as the range marker since `par({text("Test Author")})` no longer exists).
- `tests/fixtures/inline_math_pdf_text_mitex.golden.txt`, `tests/fixtures/inline_math_pdf_text_native.golden.txt` -- re-measured and hand-applied (census row A3, this plan as closing owner).

## Decisions Made

See `key-decisions` in the frontmatter above for the full list; the two most consequential:

- **The D-07/D-08 trap is closed via exclusion, not a new gate.** Rather than adding a second concat mechanism or teaching `depart_field` a new classification, `_field_body_unwrapped_paragraph` is simply excluded from the existing `_last_field_body_was_inline` flag `depart_field` already reads. This satisfies the plan's "reuse the existing inline-concat context" and "add exactly one new instance attribute" constraints simultaneously.
- **The inter-field `parbreak()` is derived from the doctree, not a second instance attribute.** `depart_field_body` checks `node.parent.next_node(descend=False, siblings=True)` (where `node` is the field_body and `node.parent` is the enclosing `field`) while `_field_body_unwrapped_paragraph` is still live and before the stack pop -- the one place both facts are available at once, with zero new state.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Migrated a census miss in tests/test_field_list_in_list_item_render_gate.py one assertion upstream of row A4's prediction**
- **Found during:** Task 1 (field-list indent wrapper)
- **Issue:** `38-TEST-CENSUS.md` row A4 predicted this file would break at its downstream `par({text("Test Author")})` CR-01 marker (caused by Task 2's field-body reflow), but Task 1's own wrapper landing independently broke an EARLIER assertion in the same test function (line 164, the field list's own newline-separation proof against the preceding "For example:" paragraph) -- a direct, necessary consequence of `pad(left: 2.5em, {` now appearing between them that the census did not separately flag.
- **Fix:** Hand-migrated the assertion from `'text("For example:")\nstrong(text("Organization ID")'` to `'text("For example:")\npad(left: 2.5em, {strong(text("Organization ID")'`, per contract section 3's specified wrapper token.
- **Files modified:** `tests/test_field_list_in_list_item_render_gate.py`
- **Verification:** `uv run pytest tests/test_field_list_in_list_item_render_gate.py -v` passes.
- **Committed in:** `16920ba` (Task 1 commit)

**2. [Rule 1 - Bug] Migrated census row A4's own predicted break**
- **Found during:** Task 3 (whole-suite scope proof)
- **Issue:** Once Task 2 landed, `par({text("Test Author")})` genuinely no longer exists in the emitted `.typ` (the Author/Version field bodies are now single-paragraph-unwrapped, per FLD-02) -- exactly the breakage census row A4 predicted and assigned to this plan.
- **Fix:** Migrated the CR-01 range marker from `typ_text.index('par({text("Test Author")})')` to `typ_text.index('strong(text("Author") + text(": "))')`, preserving the same underlying property (no stray FID-09 `text("  ")` separator between the Author and Version fields).
- **Files modified:** `tests/test_field_list_in_list_item_render_gate.py`
- **Verification:** `uv run pytest tests/test_field_list_in_list_item_render_gate.py -v` passes (both test functions).
- **Committed in:** `edf90a2` (Task 3 commit)

**3. [Rule 2 - Missing Critical] Converted depart_desc_signature's two remaining self.body.append(...) sites to self.add_text(...)**
- **Found during:** After Task 3, per the orchestrator's own wave-3 findings
- **Issue:** `38-GATE-EVIDENCE-01.md` (plan 38-01) recorded that a `desc` inside a table cell aborts the Typst compile with "expected semicolon or line break", caused by `depart_desc_signature`'s two remaining direct `self.body.append(...)` calls (the per-id `[#metadata(none) <id>]` anchor loop and the trailing spacing newline) bypassing table-cell routing. This was originally deferred as out of Phase 38's scope for `desc_signature`, but the orchestrator's wave-3 findings explicitly assigned this fix to this plan alongside the field_list family's own five sites -- both are the SAME class of bug (D-12's `add_text`-not-`append` requirement) and both were found by the same GATE-EVIDENCE-01 investigation.
- **Fix:** Converted both sites to `self.add_text(...)`.
- **Files modified:** `typsphinx/translator.py`
- **Verification:** An ad hoc fixture (a `py:attribute::` signature and a genuine RST field list, each inside its own `list-table` cell) compiles to a real, non-empty PDF via `-b typstpdf` where it previously aborted; the whole-suite run stays at 689 passed / 11 failed / 29 deselected, unchanged.
- **Committed in:** `7f7f247` (deviation commit, separate from the three planned tasks)

---

**Total deviations:** 3 auto-fixed (2 Rule 1 bug fixes, 1 Rule 2 missing-critical-functionality fix, all explicitly authorized either by the census's own "migrate at point of change" convention or by the orchestrator's wave-3 findings)
**Impact on plan:** All three were necessary to keep the plan's own acceptance criteria (a fully green, correctly-scoped test suite; both table-cell defects fixed) true. No scope creep beyond what the census and the orchestrator explicitly authorized.

## Authorized Scope Extension: Golden-File Migration (Census Row A3)

`tests/fixtures/inline_math_pdf_text_mitex.golden.txt` and `tests/fixtures/inline_math_pdf_text_native.golden.txt` are NOT in this plan's `files_modified` frontmatter. `38-TEST-CENSUS.md` row A3 names this plan (38-06) as the closing owner of these two goldens (jointly owned with 38-05, "38-06 is the later, deeper touch"), and the orchestrator's own wave-3 findings explicitly authorized the extension on the census's authority.

Migration method followed the census's own PDF-text-golden exception (re-measure-then-verify, never hand-derive): rebuilt both the mitex and native paths via `-b typstpdf` at this plan's HEAD, extracted PDF text via `pypdf`, and diffed against the currently-committed baseline. The diff was confirmed **byte-for-byte** to be solely the predicted Construct C line-wrap consequence:

```diff
-A description paragraph so the confval also exercises the block field-body and normal-paragraph 
-path.
+A description paragraph so the confval also exercises the block field-body and normal-
+paragraph path.
```

Nothing else in either 41-line extracted text differed. The hand-edited golden files were then verified byte-for-byte identical to the freshly re-measured build output (`python3` byte comparison, not just `difflib`) before being committed.

## Issues Encountered

- **The consecutive-single-value-fields trap materialized exactly as `38-EMISSION-CONTRACT.md` §4.3 property 2 warned.** An early implementation attempt let `_field_body_unwrapped_paragraph` set `_in_field_body = True` without excluding it from `_last_field_body_was_inline`, which would have let `depart_field`'s FID-09 separator fire between `Returns:`/`Return type:`/`Raises:` -- caught immediately by `test_fld02_consecutive_single_value_fields_stay_on_separate_lines` going RED during development (never committed in that state). Resolved per the key-decisions above.
- **A juxtaposition compile fatal during development of the inter-field `parbreak()`.** The first attempt used `_emit_forced_break("parbreak()")`, whose leading-newline guard is conditional on `self.in_list_item` -- outside a list item (the normal field-body case) it emits a bare `parbreak()` directly adjacent to the preceding paragraph's last inline expression with no separating whitespace, producing the exact "expected semicolon or line break" Typst fatal this codebase has hit before. Fixed by emitting an unconditional leading `"\n"` (`self.add_text("\nparbreak()\n")`) instead, documented in `depart_field_body`'s docstring. Never committed in the broken state.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `visit_field_list`/`depart_field_list` and the field-body reflow machinery are landed and stable; the 11 remaining RED tests in `tests/test_field_body_typography_render_gate.py` (all `test_fld03_*`) are exactly and only the FLD-03 monospace-literal work assigned to plan 38-07 -- confirmed by the whole-suite set-difference proof in Task 3's commit.
- `tests/test_desc_rubric_decoupling_render_gate.py`'s SC#1 `RETAINED_DELEGATION_METHODS` delegation guard was NOT touched (per the orchestrator's explicit instruction) and remains 38-07's to invert.
- Both Phase-34 PDF-text goldens are closed out; no further re-measurement of them is expected from 38-07/38-08 unless FLD-03's monospace change itself moves a line-wrap boundary (unlikely, since FLD-03 touches parameter names/types, not the confval Construct C region these goldens pin).
- No blockers.

---
*Phase: 38-structural-indentation-info-fields*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: typsphinx/translator.py
- FOUND: tests/test_field_list_in_list_item_render_gate.py
- FOUND: tests/fixtures/inline_math_pdf_text_mitex.golden.txt
- FOUND: tests/fixtures/inline_math_pdf_text_native.golden.txt
- FOUND: commit 16920ba (Task 1)
- FOUND: commit d55df99 (Task 2)
- FOUND: commit edf90a2 (Task 3)
- FOUND: commit 7f7f247 (deviation)
