---
phase: 38-structural-indentation-info-fields
plan: 09
subsystem: api
tags: [sphinx, typst, translator, docutils, field-list, list-item, verification-gap-closure]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields (38-02, 38-04, 38-06, 38-08)
    provides: the RED gate module and FLD-01/FLD-02 test evidence (38-02), the authoritative
      test census (38-04), the field_list indent wrapper and single-value field-body reflow
      this plan reorders (38-06), and the phase-closeout re-measurement/verification that
      surfaced this gap (38-08, 38-VERIFICATION.md)
provides:
  - "visit_paragraph/depart_paragraph check _field_body_unwrapped_paragraph BEFORE in_list_item -- a single-value field body's label and value now share one line inside a bullet list item, an enumerated list item, and at top level (FLD-02, closes 38-VERIFICATION.md gap 1 / 38-REVIEW.md CR-01)"
  - "A body-less desc and a plain field list inside list-table cells now have a positive regression test proving the table-cell self.body.append -> self.add_text conversions 38-06 shipped actually compile (WR-01)"
  - "tests/test_desc_content_indent_render_gate.py imports SHARED_INDENT_STEP by name; zero copies of its literal value remain in the module, in assertions or in prose (WR-02)"
  - "FLD-02 reads Complete in both places in REQUIREMENTS.md, backed by the new list-item construct's own recorded RED-then-GREEN evidence"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Branch-order load-bearing comment convention: when two mutually-exclusive early-return checks in the same visitor can BOTH be true simultaneously, the docstring states which check must be evaluated first and WHY, so a future 'tidy-up' cannot silently invert the order"
    - "depart_desc's own FID-06 unconditional post-desc parbreak() is a DIFFERENT mechanism from depart_field_body's D-07/D-08 following-sibling-gated compensating parbreak() -- a test asserting the absence of the field-level break must scope its search window to end before the desc-level break, or it will always find one"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/fixtures/field_body_typography_render_gate/index.rst
    - tests/test_field_body_typography_render_gate.py
    - tests/fixtures/desc_content_indent_render_gate/index.rst
    - tests/test_desc_content_indent_render_gate.py
    - .planning/REQUIREMENTS.md
    - .planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md

key-decisions:
  - "depart_field_body's D-07/D-08 compensating parbreak() needed NO additional in_list_item guard -- measured exactly one forced break between consecutive single-value fields inside the enumerated list-item construct (matching the top-level shape), because the compensating break's own following-sibling check is doctree-based, not in_list_item-based, and the branch reorder alone removes the list-item fast-path's double provision for field-body paragraphs. No guard added; the reorder alone is sufficient (as the plan's own 'expected finding' predicted)."
  - "The WR-01 table construct's added vertical space caused an unpredicted page-reflow regression in test_d11_sig09_page_boundary_signature_body_and_continuation_indent, root-caused to a pypdf extraction_mode='layout' reconstruction limitation (a continuation page with no un-indented anchor content loses its reconstructed indent) rather than a translator defect. Fixed by trimming 2 of the Page-Boundary Desc section's 20 filler paragraphs, documented inline with a 38-09 re-tuning note, rather than by weakening the D-11 test's own assertion."
  - "A scoping bug in this plan's own test_fld02_list_item_lone_field_has_no_trailing_inter_field_break test was found and fixed during Task 2: the original 'after value' window extended past depart_field_body's own closing bytes into depart_desc's unconditional FID-06 parbreak(), which always fires after a desc closes regardless of field siblings. Rescoped to stop at the field_list/desc_content pad-closing tokens so the test asserts only the field-level property under test."

requirements-completed: [FLD-02, IND-04]

coverage:
  - id: D1
    description: "A single-value field body's label and value share one line inside a bullet list item, an enumerated list item, and at top level -- the branch reorder in visit_paragraph/depart_paragraph closes the FLD-02 list-item nesting gap"
    requirement: "FLD-02"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_bullet_single_value_pdf_adjacency_matches_pinned_string"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_enum_single_value_pdf_adjacency_matches_pinned_string"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_single_value_emits_no_forced_break_between_label_and_value"
        status: pass
    human_judgment: false
  - id: D2
    description: "A lone single-value field inside a list item emits no trailing inter-field break; consecutive single-value fields inside a list item stay in source order on separate lines with exactly one break between them"
    requirement: "FLD-02"
    verification:
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_lone_field_has_no_trailing_inter_field_break"
        status: pass
      - kind: unit
        ref: "tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_consecutive_fields_stay_on_separate_lines"
        status: pass
    human_judgment: false
  - id: D3
    description: "WR-01: a body-less desc and a plain field list inside list-table cells compile through a real -b typstpdf build and their sentinels reach the extracted PDF text -- positive regression for the table-cell add_text conversions 38-06 shipped"
    verification:
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_wr01_bodyless_desc_and_plain_field_list_in_table_cell_compile"
        status: pass
    human_judgment: false
  - id: D4
    description: "WR-02: tests/test_desc_content_indent_render_gate.py imports SHARED_INDENT_STEP by name; the hardcoded '2.5em' literal is fully eliminated (11 occurrences before, 0 after) with no behaviour change"
    verification:
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py (whole module, 14 node ids)"
        status: pass
      - kind: other
        ref: "grep -c '2\\.5em' tests/test_desc_content_indent_render_gate.py == 0"
        status: pass
    human_judgment: false
  - id: D5
    description: "FLD-02 flipped to Complete in REQUIREMENTS.md (both the requirement bullet and the phase-mapping table row), gated on the new construct's own recorded RED-then-GREEN evidence"
    requirement: "FLD-02"
    verification:
      - kind: other
        ref: ".planning/REQUIREMENTS.md line 95 ('- [x] **FLD-02**') and line 280 ('| FLD-02 | Phase 38 | Complete |')"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-01
status: complete
---

# Phase 38 Plan 09: FLD-02 List-Item Nesting Gap Closure Summary

**A branch reorder in visit_paragraph/depart_paragraph closes the FLD-02 verification gap (single-value field bodies now join label and value on one line inside bullet and enumerated list items, not just at top level), plus a WR-01 positive table-cell regression test and a WR-02 SHARED_INDENT_STEP import that eliminates all 11 hardcoded "2.5em" copies in the sibling gate module.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 4 of 4 tasks complete, each committed atomically
- **Files modified:** 7 (`typsphinx/translator.py`, 2 fixture files, 2 test files, `REQUIREMENTS.md`, `38-TEST-CENSUS.md`)

## Accomplishments

- **The gap is closed.** `visit_paragraph`/`depart_paragraph` now check `self._field_body_unwrapped_paragraph` BEFORE `self.in_list_item` -- a pure reorder, no new state, no new helper, no new constant, no change to either branch's own emitted bytes. `in_list_item` remains True for a `field_list`/`field`/`field_body`/`paragraph` nested inside a list item (nothing resets it), so before this fix D-13's forced `parbreak()` fast-path always won and reintroduced the pre-Phase-38 label/value split for a `desc` documented inside a bullet or enumerated list item.
- **Five new list-item tests, recorded RED then GREEN.** `tests/fixtures/field_body_typography_render_gate/index.rst` gained two new sections -- a bullet-list `py:function::` with a lone `:returns:` (adjacency + empty edge) and an enumerated-list `py:function::` with `:returns:`/`:rtype:`/`:raises:` (ordering edge). All five new node ids failed against the unfixed translator (Task 1's commit) and all five pass after the reorder (Task 2's commit).
- **`depart_field_body`'s D-07/D-08 compensating break needed no extra guard.** Measured exactly one `parbreak()` between consecutive single-value fields inside the enumerated list-item construct (`Returns:` -> `Return type:`), matching the top-level shape -- the reorder alone removed the list-item branch's double provision for field-body paragraphs, confirmed by measurement rather than assumed.
- **D-13's own pinned shape is unchanged.** `tests/test_inline_math_after_text_render_gate.py`'s 3 node ids (which pin the ordinary list-item paragraph break's exact form) stay green throughout.
- **WR-01 landed:** a second `list-table` ("Table With Desc And Field List") proves a body-less `py:attribute::` and a plain `:note:`/`:warning:` field list, each in their own table cell, compile through a real `-b typstpdf` build where they previously aborted -- one new test asserts the build's return code, the absence of both compile-failure signatures from stderr, `index.pdf`'s existence/size, and all three sentinels in the extracted PDF text.
- **WR-02 landed:** `tests/test_desc_content_indent_render_gate.py` now imports `SHARED_INDENT_STEP` from `typsphinx.translator` and every one of the 11 pre-existing hardcoded `"2.5em"` occurrences (5 executable assertions, one the compound block-quote non-conversion form, 6 docstring/message mentions) is replaced with an interpolated or by-name reference. Behaviour unchanged -- every assertion evaluates the same expected string as before.
- **FLD-02 reads Complete in both places in `REQUIREMENTS.md`.** The requirement bullet's checkbox flips to `[x]` and its "Partially met after Phase 38" italic note is removed in full; the phase-mapping row changes from "Gap -- partially met (list-item nesting)" to "Complete", gated strictly on Tasks 1-3's own recorded RED-then-GREEN evidence per the plan's own prohibition, never on a green suite alone.
- **`38-TEST-CENSUS.md`** gained a "Post-verification gap closure (38-09)" section naming every new construct, confirming no pre-existing expected string in any module was migrated (zero Bucket A blast radius from the reorder), and honestly recording the WR-01-caused page-reflow miss (below) rather than folding it silently into the new-construct list.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the list-item single-value field construct to the FLD-02 gate and record it RED** - `5693e92` (test)
2. **Task 2: Give the single-paragraph field-body case priority over the list-item paragraph branch** - `e7a27ab` (feat)
3. **Task 3: Prove the table-cell add_text fixes positively (WR-01) and de-hardcode the indent literal (WR-02)** - `92caeb9` (test)
4. **Task 4: Flip FLD-02 to Complete and reconcile the new constructs against the test census** - `ab4cdf4` (docs)

**Plan metadata:** (this commit, forthcoming)

## Files Created/Modified

- `typsphinx/translator.py` -- `visit_paragraph`/`depart_paragraph` reordered so the FLD-02 branch is checked before the list-item fast-path; docstrings rewritten to state the order is load-bearing, not incidental. No new module-level constant, no new instance attribute -- confirmed by `git diff` grep.
- `tests/fixtures/field_body_typography_render_gate/index.rst` -- two new sections, "List Item Bullet Single Value Field" and "List Item Enumerated Consecutive Fields".
- `tests/test_field_body_typography_render_gate.py` -- `_H_LI_BULLET`/`_H_LI_ENUM` section constants, two hand-derived pinned adjacency strings, five new tests (Task 1), one test rescoped for a discovered assertion bug (Task 2, see Deviations).
- `tests/fixtures/desc_content_indent_render_gate/index.rst` -- a second `list-table` in the Table-Cell CONTROL section (WR-01); the section's comment rewritten to describe measured reality; the Page-Boundary Desc section's filler-paragraph count trimmed from 20 to 18 (see Deviations).
- `tests/test_desc_content_indent_render_gate.py` -- `SHARED_INDENT_STEP` import (WR-02), all 11 hardcoded `2.5em` occurrences replaced, one new WR-01 test, a new `_run_sphinx_build_typstpdf` helper.
- `.planning/REQUIREMENTS.md` -- FLD-02's checkbox and phase-mapping row flipped to Complete; its stale italic note removed.
- `.planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md` -- "Post-verification gap closure (38-09)" section appended.

## Decisions Made

See `key-decisions` in the frontmatter for the full list; the two most consequential:

- **The reorder alone is sufficient for the inter-field break; no `in_list_item` guard added to `depart_field_body`.** Measured directly: exactly one `parbreak()` sits between the enumerated construct's `Returns:` value and the following `Return type:` label, matching the top-level interval D-08 measured. `depart_field_body`'s own compensating break is gated on the parent field's doctree-derived following-sibling check, not on `in_list_item`, so it behaves identically inside or outside a list item once the list-item branch stops double-providing separation for field-body paragraphs.
- **The WR-01/D-11 page-reflow interaction is a measurement-technique artifact, not a translator defect, and was fixed by re-tuning the fixture, not by weakening the assertion.** `pypdf`'s `extraction_mode="layout"` reconstructs left-edge indentation from RELATIVE column positions on a given page; a page containing ONLY indented continuation text (no un-indented anchor content) reconstructs everything as column 0. The WR-01 table's added vertical space happened to push the "No-Desc, No-Field-List CONTROL" heading off the continuation sentinel's page, removing that anchor. The underlying `.typ` wrapper at the page-boundary construct is byte-unchanged; the fix trims 2 filler paragraphs to restore the pre-38-09 page split.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Rescoped test_fld02_list_item_lone_field_has_no_trailing_inter_field_break's own assertion window**

- **Found during:** Task 2 (branch reorder verification)
- **Issue:** The Task 1 commit's version of this test scanned from the lone field's value all the way to the next section heading for a `parbreak()`, but that window also crosses `depart_desc`'s own unconditional FID-06 `parbreak()` -- a DIFFERENT mechanism (fires after every `desc` closes, regardless of field siblings) than the field-level D-07/D-08 compensating break the test is meant to check. After the Task 2 reorder, the test correctly failed on `depart_desc`'s always-present break, which is not the property under test.
- **Fix:** Rescoped the "after value" window to end at the field_list/desc_content pad-closing tokens (the literal `})\n})` that immediately follows `depart_field_body`'s own trailing newline), which is strictly before `depart_desc`'s own break. Verified the fix by confirming the enumerated construct's (non-empty-edge) sibling case still shows exactly one `parbreak()` in the equivalent window.
- **Files modified:** `tests/test_field_body_typography_render_gate.py`
- **Verification:** `uv run pytest tests/test_field_body_typography_render_gate.py -k list_item -q` -- 5 passed.
- **Committed in:** `e7a27ab` (Task 2 commit)

**2. [Rule 1 - Bug] Fixed a page-reflow regression WR-01 caused in a previously-passing D-11/SIG-09 test**

- **Found during:** Task 3 (after adding the WR-01 table construct)
- **Issue:** `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_d11_sig09_page_boundary_signature_body_and_continuation_indent` started failing (`continuation_col=0` vs `first_line_col=7`) after the WR-01 table's added content shifted where the Page-Boundary Desc construct's multi-page body paragraph splits across compiled pages, robbing the continuation sentinel's own page of any un-indented anchor content `pypdf`'s layout-mode extraction needs to reconstruct relative indentation.
- **Fix:** Iteratively measured the minimal compensating trim (a small standalone script built the fixture and checked the reconstructed column at several trim depths) and trimmed 2 of the section's 20 filler paragraphs, restoring the pre-38-09 page split. Documented inline in the fixture with a "38-09 re-tuning note" explaining the mechanism so a future reader does not mistake the trim for an unexplained content change.
- **Files modified:** `tests/fixtures/desc_content_indent_render_gate/index.rst`
- **Verification:** `uv run pytest tests/test_desc_content_indent_render_gate.py -q` -- 14 passed, 0 failed.
- **Committed in:** `92caeb9` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 bug fixes, both discovered and resolved while completing this plan's own tasks -- no scope creep beyond what closing the FLD-02 gap and landing WR-01/WR-02 required)
**Impact on plan:** Both fixes were necessary to keep the plan's own acceptance criteria (a fully green, correctly-scoped test suite) true. Neither weakens any existing assertion's property; both make the assertions measure exactly what they claim to measure.

## Issues Encountered

- **RED evidence (Task 1, quoted from the actual pytest run against the unfixed translator):**

  ```
  FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_bullet_single_value_pdf_adjacency_matches_pinned_string
  FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_enum_single_value_pdf_adjacency_matches_pinned_string
  FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_single_value_emits_no_forced_break_between_label_and_value
  FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_lone_field_has_no_trailing_inter_field_break
  FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_consecutive_fields_stay_on_separate_lines
  ========================= 5 failed, 20 deselected in 0.48s =======================
  ```

  All five failed against the unfixed translator -- the plan noted tests 4 and 5 (the empty-edge and ordering-edge structural checks) "may already pass"; measured honestly, all five were RED, because the lone-field trailing-break assertion's own scoping (before its Task 2 fix) also caught the pre-existing D-13 stray break at the head of every list item, and the ordering test's pinned enum adjacency string wasn't present yet either (it depends on the same adjacency fix).

- **GREEN evidence (Task 2, after the branch reorder):**

  ```
  tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_single_value_emits_no_forced_break_between_label_and_value PASSED [ 60%]
  tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_lone_field_has_no_trailing_inter_field_break FAILED [ 80%]
  tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_list_item_consecutive_fields_stay_on_separate_lines PASSED [100%]
  ================== 1 failed, 4 passed, 20 deselected in 0.75s ==================
  ```

  (4/5 passed immediately after the reorder; the 5th failure was Deviation #1 above -- a scoping bug in the test itself, not the translator. After the Deviation #1 fix:)

  ```
  tests/test_field_body_typography_render_gate.py .....                    [100%]
  ======================= 5 passed, 20 deselected in 0.44s =======================
  ```

- **Measured forced-break count between consecutive fields inside the enumerated list item: exactly 1** (`parbreak()` between `text("fld02 listitem enum returns sentinel.")` and the `Return type` label), matching the top-level shape D-08 measured. Decision: the reorder alone is sufficient; `depart_field_body` needed no additional `in_list_item` guard.

- **`grep -c '2\.5em' tests/test_desc_content_indent_render_gate.py`: 11 before this plan, 0 after.**

- **No pre-existing expected string in any test module was migrated by this plan.** Confirmed via `git diff` over every file this plan touched: only insertions against test/fixture bodies and the branch-reorder diff in `typsphinx/translator.py`; no existing pinned string, golden file, or previously-committed assertion was edited or deleted anywhere in the suite.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Phase 38 is now fully closed: all 8 requirements (IND-01..IND-05, FLD-01..FLD-03) read Complete in `REQUIREMENTS.md`, with FLD-02 backed by this plan's own recorded RED-then-GREEN evidence rather than a green suite alone.
- Whole suite: 734 passed, 1 skipped, 0 failed (baseline 728 passed / 1 skipped at plan start; +5 list-item tests + 1 WR-01 test, net +6).
- CI trio (`black --check .`, `ruff check .`, `mypy typsphinx/`) all clean.
- `grep -c 'Phase 38 | Complete' .planning/REQUIREMENTS.md` returns 8 (IND-01..05, FLD-01..03) -- every Phase 38 requirement now maps to Complete. Note: the plan's own acceptance criterion stated this count as 9, which appears to be an arithmetic slip in the plan text (5 IND + 3 FLD = 8, not 9); the actual measured state (8/8, all Complete) fully satisfies the criterion's stated intent ("every Phase 38 requirement now maps to Complete").
- Out-of-scope items recorded, not silently dropped: `visit_desc_parameterlist`/`depart_desc_parameterlist`'s still-unconverted `self.body.append` calls (a `py:function::` WITH a parameter list inside a table cell still aborts the compile -- a later phase's work); `tests/test_field_list_in_list_item_render_gate.py` still hardcodes the indent literal in 2 places (WR-02's owner scoped only the sibling module).
- No blockers.

---
*Phase: 38-structural-indentation-info-fields*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: typsphinx/translator.py
- FOUND: tests/fixtures/field_body_typography_render_gate/index.rst
- FOUND: tests/test_field_body_typography_render_gate.py
- FOUND: tests/fixtures/desc_content_indent_render_gate/index.rst
- FOUND: tests/test_desc_content_indent_render_gate.py
- FOUND: .planning/REQUIREMENTS.md
- FOUND: .planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md
- FOUND: commit 5693e92 (Task 1)
- FOUND: commit e7a27ab (Task 2)
- FOUND: commit 92caeb9 (Task 3)
- FOUND: commit ab4cdf4 (Task 4)
