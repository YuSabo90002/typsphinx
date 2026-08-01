---
phase: 38-structural-indentation-info-fields
plan: 05
subsystem: api
tags: [sphinx, typst, translator, docutils, indentation]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields (38-01, 38-03, 38-04)
    provides: the RED gate module (test_desc_content_indent_render_gate.py), the D-10 conjunction
      gate, the buffer-swap fixture, and the authoritative test census this plan migrates against
provides:
  - "visit_desc_content/depart_desc_content wrap the description body in pad(left: SHARED_INDENT_STEP, { ... }) (IND-01/02/03/05, no depth counter, D-01)"
  - "D-10's marker-propagation fix: depart_desc_content propagates the SIG-08 suppression marker through its own close so a nested desc still emits exactly one parbreak()"
  - "The folded buffer-swap todo closed: _desc_break_marker is now a (id(self.body), len(self.body)) pair, not a bare position integer"
  - "tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ hand-migrated to the post-wrapper byte-identity shape"
affects: [38-06, 38-07, 38-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "desc_content wraps its body using the same pad(left:, {...}) shape and self.add_text discipline as visit_block_quote/visit_field_list -- reused, not reinvented"
    - "Emission-position suppression markers that must survive a self.body buffer swap are recorded as (id(buffer), position) pairs, not bare positions"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ

key-decisions:
  - "field_list wrapping (FLD-01) is explicitly out of scope for this plan, per the plan's own acceptance criteria (git diff must not touch visit_field_list/depart_field_list) and the phase's test census (owned by 38-06, running in parallel this wave); test_fld01_field_list_deeper_than_method_body stays RED by design"
  - "The two Phase-34 PDF-text goldens (test_block_math_pdf_text_is_invariant_across_the_math02_fix) are census row A3's documented joint-ownership exception -- reached and re-measured to confirm the diff matches the predicted line-wrap shift exactly, but not migrated here; 38-06 is the closing owner per the census's migration strategy"
  - "visit_desc_content's leading list-item separator guard mirrors block_quote/field_list byte-for-byte even though it is provably redundant for the signature->content_content transition (depart_desc_signature already ends in an unconditional newline) -- consistency with the established block-visitor pattern over a byte-count-minimal implementation"

requirements-completed: [IND-01, IND-02, IND-03, IND-04, IND-05]

coverage:
  - id: D1
    description: "desc_content body wrapped in pad(left: SHARED_INDENT_STEP, {...}), routed through self.add_text, composing with no depth counter (IND-01/02/03/05)"
    requirement: "IND-01"
    verification:
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind01_structural_wrapper_token_and_position"
        status: pass
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind01_body_indented_past_signature"
        status: pass
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind02_nested_body_deeper_and_resumed_body_returns"
        status: pass
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind03_nested_signature_equals_parent_body_column"
        status: pass
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind05_sibling_top_level_returns_to_margin"
        status: pass
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_fld01_empty_ind01_empty_bodyless_confval_siblings"
        status: pass
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_structural_shared_step_value_at_new_sites"
        status: pass
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_d11_sig09_page_boundary_signature_body_and_continuation_indent"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-10 SIG-08 marker propagated through depart_desc_content's close; nested desc still emits exactly one parbreak(); depart_desc's docstring premise corrected"
    verification:
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_wrapper_present_and_break_count_still_eight"
        status: pass
      - kind: unit
        ref: "tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix"
        status: pass
    human_judgment: false
  - id: D3
    description: "Folded buffer-swap todo closed: SIG-08 marker is a (id(self.body), len(self.body)) pair, no per-site guard added"
    verification:
      - kind: unit
        ref: "tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_glossary_nested_pair_gets_exactly_one_break"
        status: pass
      - kind: integration
        ref: "tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapCompileGate::test_fixture_compiles_via_real_typst_compile"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ hand-migrated to the post-wrapper shape and confirmed by rebuild"
    verification:
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-01
status: complete
---

# Phase 38 Plan 05: desc_content Body Wrapper + D-10 Marker Propagation Summary

**Gave `visit_desc_content`/`depart_desc_content` real bodies (`pad(left: 2.5em, {...})`, no depth counter), propagated the SIG-08 break-suppression marker through the new wrapper's close, made that marker buffer-identifying to close a folded todo, and hand-migrated the one golden byte-identity file this change breaks.**

## Performance

- **Duration:** ~35 min (approximate — start timestamp was not captured at session start)
- **Tasks:** 3 completed
- **Files modified:** 2 (`typsphinx/translator.py`, `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`)

## Accomplishments

- `visit_desc_content`/`depart_desc_content` (both `pass` pre-phase) now wrap a description body in `pad(left: SHARED_INDENT_STEP, { ... })`, emitted through `self.add_text` (never `self.body.append`, D-12), landing IND-01 (body indents past its own signature), IND-02 (cumulative with nesting depth), IND-03 (a nested member's own signature aligns with its parent's body and gets no further step), and IND-05 (depth cannot leak to a following sibling) — all with **zero** depth-tracking state, per D-01.
- D-10's consequence owned: `depart_desc_content` records whether the SIG-08 suppression marker still matches immediately before emitting its close, then re-advances the marker past those bytes if it did — so a nested `desc`'s duplicate `parbreak()` is still correctly suppressed even though the wrapper's close is now a real byte sequence appended between the two departures. `depart_desc`'s ~50-line docstring premise is corrected in the same edit (section 6.3) to state why the wrapper's closing bytes count as "nothing" for the comparison without actually being absent.
- The folded buffer-swap todo closed: `self._desc_break_marker` is now a `(id(self.body), len(self.body))` pair rather than a bare position integer, so the suppression can no longer compare a position against a different emission buffer after one of the five `self.body` reassignment sites fires. No sixth per-site guard added.
- `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` hand-migrated by applying contract §2's rules directly to the existing file (never regenerated from the build's own output) and confirmed by rebuild.

## Task Commits

Each task was committed atomically:

1. **Task 1: Wrap desc_content in the shared indent step and propagate the break marker** - `3b9564e` (feat)
2. **Task 2: Make the break marker buffer-identifying (folded todo)** - `8db1899` (fix)
3. **Task 3: Hand-migrate this plan's census rows and prove the change is scoped** - `655cff1` (test)

**Plan metadata:** (this commit, forthcoming)

## Files Created/Modified

- `typsphinx/translator.py` — `visit_desc_content`/`depart_desc_content` given real bodies (Task 1); `_desc_break_marker`'s type, initialization, and both read/write sites (`depart_desc`, `depart_desc_content`) converted from a bare position `int` to a `(id, len)` pair (Task 2); `depart_desc`'s docstring premise corrected in both tasks.
- `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` — hand-edited to insert the wrapper pair around each of the fixture's three `desc_content` bodies (`connect`, the sibling-signature `compile`, `--sep`).

## Decisions Made

- **field_list wrapping (FLD-01) is out of scope for this plan.** The plan's own Task 1 acceptance criteria explicitly list only IND-01/02/03/05 and D-11 as the assertions this plan flips green, and its `git diff` acceptance criterion forbids any change to `visit_field_list`/`depart_field_list` ("plan 38-06 owns them"). `38-EMISSION-CONTRACT.md` §7 and `38-TEST-CENSUS.md`'s migration strategy both independently assign the field-list wrapper (§3) to plan 38-06, which runs in parallel this same wave (`wave: 2`, sibling worktree) — touching `visit_field_list` here risks a double-wrap when the two plans' branches merge. `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_fld01_field_list_deeper_than_method_body` therefore stays RED by design; this is a deliberate resolution of a discrepancy between the orchestrator's aggregate wave-1 note ("6 in test_desc_content_indent_render_gate.py … expected to turn green") and the plan document's own, more granular scoping — the plan's explicit per-task acceptance criteria and the census's ownership table take precedence.
- **The two Phase-34 PDF-text goldens are re-measured, not migrated, here.** `38-TEST-CENSUS.md` row A3 documents these as REACHED but jointly owned by 38-05/38-06 with 38-06 as the closing plan (its migration methodology is re-measure-then-verify, only valid once BOTH plans have landed). Re-running `tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix` after this plan's wrapper lands confirms the diff is *exactly* the predicted Construct C line-wrap consequence (one sentence's line break moves from after "normal-paragraph " to after "normal-"), with nothing else changed — matching the census's prediction precisely. The baseline is deliberately left unmigrated for 38-06 to close.
- **The separator-bookkeeping decision (D-12, contract §2.6):** `visit_desc_content` carries the same leading `if self.in_list_item and self.list_item_needs_separator: self.add_text("\n")` guard as `visit_block_quote`/`visit_field_list`, even though it is provably a no-op for the structural signature→content transition (`depart_desc_signature` already unconditionally ends in `"\n"`, and also sets `list_item_needs_separator = True` when in a list item, so the guard's own `"\n"` lands on an already-present newline — a harmless extra blank line, never a Typst parse fatal). Chosen for consistency with the established block-visitor pattern over a byte-count-minimal implementation. Falsified against `tests/fixtures/desc_content_indent_render_gate/index.rst`'s "List-Item Desc CONTROL" section (a `py:function::` nested inside a bullet-list item) and confirmed non-regressing against `tests/test_desc_bodyless_concat_render_gate.py`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Shimmed the worktree's `uv` binary for NixOS**
- **Found during:** Task 3 (whole-suite scope proof)
- **Issue:** `uv sync --extra dev` installs a generic-linux ELF `uv` into `.venv/bin`, which NixOS's stub-ld cannot execute. `uv run <subprocess that shells out to `uv`>` (several integration tests invoke `uv run sphinx-build` as a subprocess) failed with exit 127 (`Could not start dynamically linked executable: uv`), producing 45 spurious failures unrelated to this plan's change (`tests/test_examples_basic.py`, `tests/test_integration_*.py`).
- **Fix:** Symlinked the NixOS-store `uv` (resolved via `command -v uv` from the outer shell) into the worktree's `.venv/bin/uv`, mirroring the `ruff` shim already documented in `CLAUDE.md`/project memory for this exact NixOS-sandbox hazard.
- **Files modified:** none (environment-only; no repository file touched)
- **Verification:** `tests/test_integration_basic.py::TestBasicSphinxProjectBuild::test_sphinx_build_typst_succeeds` and the full `uv run pytest -m "not slow" -q` run both pass after the shim; the 45 spurious failures disappeared, leaving exactly the 17 pre-identified out-of-scope RED node ids.
- **Committed in:** not applicable (no file changed; recorded here for the next executor's awareness)

---

**Total deviations:** 1 auto-fixed (1 blocking, environment-only)
**Impact on plan:** No code or test file changes resulted from this deviation; it only unblocked accurate whole-suite measurement for Task 3's scope proof.

## Issues Encountered

None beyond the environment shim above.

## Whole-Suite Scope Proof (Task 3)

`uv run pytest -m "not slow" -q` final result: **683 passed, 17 failed, 29 deselected**.

**Flipped RED → GREEN by this plan** (all previously RED per `38-GATE-EVIDENCE-01.md`/`38-GATE-EVIDENCE-03.md`):

- `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind01_structural_wrapper_token_and_position`
- `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_structural_shared_step_value_at_new_sites`
- `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_fld01_empty_ind01_empty_bodyless_confval_siblings`
- `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind01_body_indented_past_signature`
- `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind02_nested_body_deeper_and_resumed_body_returns`
- `tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_wrapper_present_and_break_count_still_eight`

**Still RED, all predicted and owned elsewhere (17 total remaining failures):**

- `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_fld01_field_list_deeper_than_method_body` — owned by 38-06 (field_list wrapper, §3), see Decisions above.
- 15× `tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::*` — owned by 38-06/38-07 per the orchestrator's wave-1 finding; not touched, as instructed.
- `tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_block_math_pdf_text_is_invariant_across_the_math02_fix` — census row A3, jointly owned with 38-06 as the closing plan; re-measured (not migrated) here, diff confirmed to match the predicted Construct C line-wrap shift exactly.

No node id flipped outside these two predicted sets in either direction — the 683 passed / 17 failed / 29 deselected total accounts for every previously-RED wave-1 id (either flipped by this plan or explicitly deferred to a named downstream plan) with none silently regressed.

**Lint/type trio**, run after each task and again at the end: `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` — all clean throughout.

**Targeted emission diff** for `tests/fixtures/desc_bodyless_concat_render_gate/` (rebuilt at the parent commit `882eee1` vs. this plan's HEAD `655cff1`, via `-b typst`):

```diff
 block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("coverage_c_path"))}))
 [#metadata(none) <index:confval-coverage_c_path>]
-strong(text("Type") + text(": "))
+pad(left: 2.5em, {strong(text("Type") + text(": "))
 text("Sequence[str]")

 text("  ")
 strong(text("Default") + text(": "))
 raw("()")

+})
 parbreak()
 block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("coverage_c_regexes"))}))
 [#metadata(none) <index:confval-coverage_c_regexes>]
-strong(text("Type") + text(": "))
+pad(left: 2.5em, {strong(text("Type") + text(": "))
 text("dict[str, str]")

 text("  ")
 strong(text("Default") + text(": "))
 raw("{}")

+})
 parbreak()
```

Confirmed: the only difference is the wrapper pair around each `desc_content` body, exactly as required.

**Golden hand-derivation confirmation:** the hand-edited `golden.typ` (Task 3 commit `655cff1`) matched a fresh `-b typst` rebuild on the first attempt — `tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden` passed with no adjustment to the hand-derived bytes.

**Rubric non-interference confirmed:** `git diff` (main-branch parent vs. this plan's HEAD) shows `tests/test_rubric_option_concat_render_gate.py` unmodified (`git diff --stat` empty) and `tests/test_translator.py` unmodified in its entirety (not just the rubric assertion) — the census's Bucket B prediction that all of `test_translator.py`'s desc/field-list/rubric assertions survive the wrapper unchanged (loose substring checks) was confirmed directly by running `uv run pytest tests/test_translator.py -k "desc or field_list or rubric or full_api"` — all 9 pass, no file edit needed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `visit_desc_content`/`depart_desc_content` and the D-10 marker-propagation/buffer-identity mechanism are landed and stable; 38-06 can now build the field_list wrapper (§3) and field-body reflow (§4) directly on top of this wrapper without needing to touch `depart_desc`'s marker bookkeeping again.
- `test_fld01_field_list_deeper_than_method_body`, the 15 `test_field_body_typography_render_gate.py` tests, and the two Phase-34 PDF-text goldens (via `test_block_math_pdf_text_is_invariant_across_the_math02_fix`) are the concrete, confirmed RED handoff to 38-06/38-07 — no other REDs remain unaccounted for in the phase's blast radius.
- No blockers.

---
*Phase: 38-structural-indentation-info-fields*
*Completed: 2026-08-01*
