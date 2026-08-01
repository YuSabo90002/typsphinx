---
phase: 38-structural-indentation-info-fields
verified: 2026-08-02T00:00:00Z
status: human_needed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 7/8
  gaps_closed:
    - "FLD-02: A field body with multiple values renders as a bulleted list; a single-value body stays inline prose (list-item nesting case)"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: >
      Read ROADMAP.md's Phase 38 Success Criterion #4 ("One named indent constant drives desc
      nesting, field lists, and block quotes — a repo-wide grep over typsphinx/ finds no second
      independent indent literal at those sites") and REQUIREMENTS.md's IND-04 text ("One shared
      indent constant drives every indent context — desc nesting, field lists, and block quotes —
      rather than independent magic numbers per node type") side by side with 38-CONTEXT.md's D-04
      decision and the shipped code (visit_block_quote/depart_block_quote, translator.py, and
      test_ind04_d04_block_quote_not_converted).
    expected: >
      A human decision on whether the ROADMAP/REQUIREMENTS prose should be corrected to match D-04's
      narrower, deliberately-scoped reading (SHARED_INDENT_STEP drives desc_content and field_list
      only; block_quote is an intentional non-consumer using Typst's own quote() default spacing),
      or whether the prose's literal claim that the constant "drives ... block quotes" was meant to
      hold and the implementation is out of compliance with the roadmap's own wording.
    why_human: >
      This is a values/scope judgment already made once by the project owner during context-gathering
      (D-04 records it as deliberate and says "so verify-time does not re-open it"), but the
      ROADMAP.md and REQUIREMENTS.md prose was never edited to reflect the narrower scope the way
      FLD-02's REQUIREMENTS.md parenthetical was corrected in this same phase. A grep-only check
      cannot decide whether "drives ... block quotes" is now stale documentation or an unmet
      criterion — that is a call about what the roadmap author intended, not something derivable from
      the codebase alone. Not treated as a gap because the narrower reading is a recorded, reasoned
      owner decision and the code review does not flag it as a defect; flagged instead because
      re-verification must not silently resolve the tension in either direction.
---

# Phase 38: Structural Indentation + Info Fields Verification Report

**Phase Goal:** The page shows structure. A description body sits one indent step inside its own
signature, indentation accumulates with nesting depth so a method's membership in its class is
visually recoverable, a nested member's own signature aligns with its parent's body rather than
over-indenting, and the field-list block follows the same single constant instead of a private
magic number.
**Verified:** 2026-08-02
**Status:** human_needed
**Re-verification:** Yes — after gap closure (plan 38-09, wave 6)

## Summary

This is a re-verification against the current tree (HEAD `d921ba5`). The prior `38-VERIFICATION.md`
(2026-08-01) returned `gaps_found` at 7/8 must-haves: FLD-02's single-value label/value join worked at
top level but silently regressed to the pre-Phase-38 defect whenever the enclosing `desc` was
documented inside a bullet or enumerated list item, because `visit_paragraph`/`depart_paragraph`
checked `self.in_list_item` before `self._field_body_unwrapped_paragraph`.

Plan 38-09 closed that gap with a branch reorder (no new state, no new helper, no new constant). This
pass independently re-verifies all 8 must-haves — not just the closed one — against the current
codebase, using fresh builds and direct code reading, not inherited SUMMARY/REVIEW claims.

**Independent reproduction of the closed gap** (built directly in this verification pass, not from the
test suite, using the exact fixture the prior verification's gap report used):

```rst
#. First step.

   .. py:function:: field_double_break_verify()

      :returns: A short stable value.
```

Emitted `.typ` (fresh `sphinx-build -b typst`, this pass):

```
pad(left: 2.5em, {strong(text("Returns") + text(": "))
text("A short stable value.")
})
})
```

No `parbreak()` between the label and the value — the defect the prior verification reproduced
(`strong(text("Returns") + text(": "))` followed by `parbreak()` then the value on its own line) is
gone. Confirmed by direct code reading: `visit_paragraph` now checks `self._field_body_unwrapped_paragraph`
BEFORE `self.in_list_item` (translator.py, `visit_paragraph` docstring and branch), with a docstring
specifically citing `38-VERIFICATION.md gap 1` / `38-REVIEW.md CR-01` as the reason the order is
load-bearing. `depart_paragraph` mirrors the same order.

Also independently re-measured in this pass with a fresh 3-level-nesting fixture and a real
`-b typstpdf` compile (`pypdf` `extraction_mode="layout"` column reconstruction — this codebase's own
documented technique, since `visitor_text`'s per-glyph x/y reports 0,0 on Typst-compiled PDFs):

```
class Widget(name, size=10)                              <- col 0 (signature, page margin)
      A widget class body paragraph.                      <- col 6 (class body, +1 step)

      resize(width, height)                                <- col 6 (nested sig == class body, no extra step)
                    Parameters: width (int) - the width    <- col 20 (+2 steps: body + field-list)
                    Returns: nothing                        <- col 20, SAME line as label (FLD-02 inline)
                    Return type: None                        <- col 20, SAME line as label
             A method body paragraph.                       <- col 13 (method body, +2 steps total)

             inner                                           <- col 13 (nested sig == method body)
                    An inner attribute body.                 <- col 19 (+3 steps)
      Class body continues here.                             <- col 6 (RESUMES class-body level, no leak)

toplevel(a)                                                  <- col 0 (sibling desc, margin, no leak)
      A sibling top-level function.                          <- col 6 (one step, not accumulated)
```

This single fresh fixture independently reproduces IND-01, IND-02, IND-03 (at two nesting levels),
IND-05 (both the resumed-parent-level and sibling-reset cases), FLD-01, and FLD-02's inline half, all
in this verification pass — not carried forward from 38-VERIFICATION.md's or 38-09's own numbers.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | IND-01 — `desc_content` body indented one step past its own `desc_signature` | ✓ VERIFIED | Fresh build above: signature col 0, body col 6 (one step). |
| 2 | IND-02 — indentation cumulative with nesting depth | ✓ VERIFIED | Fresh build above: class body col 6, method body col 13, inner-attribute body col 19 — three distinct, increasing levels. |
| 3 | IND-03 — nested member's own signature aligns with parent body, no extra step | ✓ VERIFIED | Fresh build above: `resize(...)` signature col 6 == class body col 6; `inner` signature col 13 == method body col 13. Verified at two nesting depths. |
| 4 | IND-04 — one shared indent constant; no second independent indent literal | ✓ VERIFIED | `awk '!/^[[:space:]]*#/' typsphinx/translator.py \| grep -nE '"[0-9.]+em"'` returns exactly one hit: `SHARED_INDENT_STEP = "2.5em"`. `grep -n 'pad(left:' typsphinx/translator.py` shows exactly 2 executable call sites (field_list, desc_content — both `f"pad(left: {SHARED_INDENT_STEP}, {{"`); `visit_block_quote`/`depart_block_quote` contain no `pad(` and no numeric literal. See **Documentation-vs-scope finding** below — the mechanical grep property holds, but ROADMAP SC#4's and REQUIREMENTS.md IND-04's own prose ("drives ... block quotes") is not literally true of the shipped design and needs a human call. |
| 5 | IND-05 — depth does not leak across sibling `desc` nodes | ✓ VERIFIED | Fresh build above: after the 3-level nest closes, class body resumes at col 6 (not col 19); the sibling `toplevel(a)` signature is at col 0 (page margin, not accumulated), and its own body is at col 6 (one step, not three). |
| 6 | FLD-01 — field list indented one step beyond the surrounding desc body | ✓ VERIFIED | Fresh build above: `Parameters:` at col 20 vs. method body at col 13 (+1 step). Emitted `.typ`: `pad(left: 2.5em, {pad(left: 2.5em, {...` — field_list pad nested inside desc_content pad. |
| 7 | FLD-02 — multi-value field body bulleted; single-value field body stays inline prose, **in every reachable nesting context including inside a list item** | ✓ VERIFIED | Top level: fresh build above, `Returns:`/`nothing` and `Return type:`/`None` share one line each. **List-item case (the closed gap):** independently reproduced above with a real `sphinx-build -b typst` — no `parbreak()` between label and value inside an enumerated list item. Test suite: `uv run pytest tests/test_field_body_typography_render_gate.py -k list_item -v` — 5/5 pass (`test_fld02_list_item_bullet_single_value_pdf_adjacency_matches_pinned_string`, `..._enum_...`, `..._emits_no_forced_break...`, `..._lone_field_has_no_trailing_inter_field_break`, `..._consecutive_fields_stay_on_separate_lines`), re-run directly in this pass. Multi-value (`:param:` × 2, top level and elsewhere) unaffected — the existing pinned adjacency/bulleted tests were confirmed unmodified (`test_fld02_single_value_pdf_adjacency_matches_pinned_string`, `test_fld02_consecutive_single_value_fields_stay_on_separate_lines` both still present and green). |
| 8 | FLD-03 — field-body parameter name/type carry monospace treatment distinct from the plain-bold label | ✓ VERIFIED | Fresh build's emitted `.typ`: `strong(raw("width"))` (bold monospace name), `emph(raw("int"))` (italic monospace type), label unchanged `strong(text("Parameters") + text(": "))` (proportional `text`, not `raw`). Matches D-05 variant A. |

**Score:** 8/8 truths verified (the prior PARTIAL is now fully closed and independently reproduced,
not merely trusted from SUMMARY.md).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::visit_paragraph`/`depart_paragraph` | `_field_body_unwrapped_paragraph` checked BEFORE `in_list_item` | ✓ VERIFIED | Read directly: both branches reordered, mirror docstrings updated citing the gap. Exactly one occurrence of each branch (moved, not duplicated) — confirmed by reading the method bodies in full. |
| `typsphinx/translator.py::visit_field_body`/`depart_field_body` | Single-paragraph field body skips `par({`/`})`; compensating break for consecutive fields | ✓ VERIFIED | Read directly: `depart_field_body`'s D-07/D-08 compensating `parbreak()` fires on a doctree-derived following-sibling check (`node.parent.next_node(descend=False, siblings=True)`), independent of `in_list_item` — confirmed no double-provision (measured exactly 1 `parbreak()` between consecutive fields inside the enumerated list-item construct, per 38-09-SUMMARY.md's own measurement, spot-checked via the passing `test_fld02_list_item_consecutive_fields_stay_on_separate_lines`). |
| `typsphinx/translator.py::visit_desc_content`/`depart_desc_content` | `pad(left: SHARED_INDENT_STEP, {...})` wrapper, no depth counter | ✓ VERIFIED | Confirmed via fresh emitted `.typ` and column measurements above. |
| `typsphinx/translator.py::visit_field_list`/`depart_field_list` | Nested `pad(left: SHARED_INDENT_STEP, {...})` | ✓ VERIFIED | Confirmed via fresh emitted `.typ`; nested inside the body wrapper. |
| `typsphinx/translator.py::visit_literal_strong`/`depart_literal_strong`, `visit_literal_emphasis`/`depart_literal_emphasis` | De-delegated, emit `strong(raw(...))`/`emph(raw(...))` directly | ✓ VERIFIED | Confirmed via fresh emitted `.typ` (`strong(raw("width"))`, `emph(raw("int"))`). |
| `tests/test_desc_content_indent_render_gate.py` | Imports `SHARED_INDENT_STEP` by name, zero hardcoded `2.5em` copies (WR-02) | ✓ VERIFIED | `grep -c '2\.5em' tests/test_desc_content_indent_render_gate.py` returns 0; `from typsphinx.translator import SHARED_INDENT_STEP` present. |
| `tests/test_desc_content_indent_render_gate.py::...::test_wr01_bodyless_desc_and_plain_field_list_in_table_cell_compile` | Positive regression for the table-cell `add_text` conversions | ✓ VERIFIED | `uv run pytest tests/test_desc_content_indent_render_gate.py -k wr01 -v` — 1 passed, re-run directly in this pass. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `visit_paragraph`/`depart_paragraph` | `_field_body_unwrapped_paragraph` (FLD-02 reflow) | conditional branch, now ordered BEFORE `in_list_item` | ✓ WIRED | The link fires whenever the field body's sole child is one paragraph, regardless of `in_list_item` — confirmed by direct code reading and the fresh list-item build reproduction above. |
| `depart_field_body` | doctree-based following-sibling check | `node.parent.next_node(descend=False, siblings=True)` | ✓ WIRED | Independent of `in_list_item`; confirmed correct for the empty-edge case (lone field, no trailing break) via the passing `test_fld02_list_item_lone_field_has_no_trailing_inter_field_break`. |
| `visit_desc_content`/`depart_desc_content` | `SHARED_INDENT_STEP` | f-string interpolation | ✓ WIRED | Confirmed, IND-04 grep above. |
| `visit_field_list`/`depart_field_list` | `SHARED_INDENT_STEP` | same interpolation pattern | ✓ WIRED | Confirmed. |
| `visit_block_quote`/`depart_block_quote` | `SHARED_INDENT_STEP` | **deliberately NOT linked (D-04)** | N/A by design | See Documentation-vs-scope finding below. |

### Data-Flow Trace (Level 4)

Not applicable — this phase is a docutils-doctree-to-Typst-text translator, not a component rendering
dynamic application state.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Single-value field body renders inline, inside a list item (the closed gap) | Fresh `sphinx-build -b typst` of a hand-written fixture, this pass, independent of the test suite | No `parbreak()` between label and value | ✓ PASS |
| Structural indent columns match D-01/D-03's measured shape at 3 nesting levels | Fresh `sphinx-build -b typstpdf` + `pypdf` layout-mode extraction, this pass | col 0 → 6 → 13 → 19, with sibling-reset to 0/6 | ✓ PASS |
| FLD-03 monospace treatment | grep of fresh emitted `.typ` | `strong(raw(...))`/`emph(raw(...))` present, proportional `text(...)`-wrapped label unchanged | ✓ PASS |
| FLD-02 list-item gate module (5 node ids) | `uv run pytest tests/test_field_body_typography_render_gate.py -k list_item -v` | 5 passed | ✓ PASS |
| WR-01 table-cell positive regression | `uv run pytest tests/test_desc_content_indent_render_gate.py -k wr01 -v` | 1 passed | ✓ PASS |
| Adjacent regression modules (field-list-in-list-item, D-13 pinned shape, break-marker, signature break/arrow) | `uv run pytest tests/test_field_body_typography_render_gate.py tests/test_desc_content_indent_render_gate.py tests/test_field_list_in_list_item_render_gate.py tests/test_inline_math_after_text_render_gate.py tests/test_desc_break_marker_buffer_swap_gate.py tests/test_signature_break_and_arrow_gate.py -q` | 61 passed | ✓ PASS |
| Whole-suite regression | `uv run pytest -q` | 734 passed, 1 skipped, 0 failed | ✓ PASS |
| Lint/type trio | `uv run black --check .`, `uv run mypy typsphinx/` | both clean (ruff skipped per environment note — dynamic-linker failure on this NixOS sandbox for compiled binaries under `uv run`) | ✓ PASS (ruff: SKIPPED, known sandbox limitation) |
| Debt markers | `grep -nE "TBD\|FIXME\|XXX"` over all 7 files this plan touched | none found | ✓ PASS |

### Probe Execution

Not applicable — no `scripts/*/tests/probe-*.sh` exist in this project and none are referenced by
this phase's PLAN/SUMMARY/REQUIREMENTS.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| IND-01 | 38-01, 38-05 | `desc_content` body indented one step past its own signature | ✓ SATISFIED | Fresh column measurement, above. |
| IND-02 | 38-01, 38-05 | Cumulative indentation with nesting depth | ✓ SATISFIED | Fresh column measurement, above (col 6 → 13 → 19). |
| IND-03 | 38-01, 38-05 | Nested signature aligns with parent body, no extra step | ✓ SATISFIED | Fresh column measurement at two nesting levels, above. |
| IND-04 | 38-01, 38-04, 38-05, 38-06, 38-09 | One shared constant, no second indent literal | ✓ SATISFIED (mechanically) | Repo-wide grep, above. See Documentation-vs-scope finding for the unresolved prose question. |
| IND-05 | 38-01, 38-03, 38-05 | Depth resets correctly across sibling `desc` nodes | ✓ SATISFIED | Fresh sibling-boundary measurement, above. |
| FLD-01 | 38-01, 38-02, 38-04, 38-06 | Field list indented one step beyond desc body | ✓ SATISFIED | Fresh column measurement, above. |
| FLD-02 | 38-02, 38-04, 38-06, 38-09 | Multi-value bulleted; single-value inline, in every nesting context | ✓ SATISFIED | Top level AND list-item case both independently reproduced in this pass. REQUIREMENTS.md's `[x]` "Complete" status (lines 95, 280) is now accurate — the stale "Partially met after Phase 38" note is confirmed removed. |
| FLD-03 | 38-02, 38-04, 38-07 | Name/type monospace, distinct from label | ✓ SATISFIED | Fresh emitted `.typ`, above. |

No orphaned requirements — all 8 IDs (`IND-01..05`, `FLD-01..03`) appear in at least one plan's
`requirements:` frontmatter (38-01 through 38-09) and REQUIREMENTS.md's phase-mapping table (lines
274-281), which now reads `Complete` for all 8.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/translator.py` | 23-29 (`SHARED_INDENT_STEP` header comment) | Stale comment claims Phase 38 "reuses this SAME constant for desc_content, field_list **and block_quote**" | ⚠️ Warning (from fresh `38-REVIEW.md`, independently confirmed present in current tree, not fixed by 38-09) | This is the ROOT of the Documentation-vs-scope finding below: the comment directly contradicts D-04 and its own regression test (`test_ind04_d04_block_quote_not_converted`). A maintainer reading only this comment (a likely first stop) could "fix" `visit_block_quote` to match it and silently break D-04. Not a functional defect — `visit_block_quote`/`depart_block_quote` are confirmed untouched (no `pad(`, no `SHARED_INDENT_STEP` reference). |
| `typsphinx/translator.py` | `depart_desc`/`depart_desc_content`, `_desc_break_marker` comparison (`id(self.body), len(self.body)`) | Identity check via bare `id()` is theoretically unsound if the referenced list is GC'd and its address reused | ℹ️ Info→Warning (from fresh `38-REVIEW.md`, independently confirmed present, not fixed by 38-09) | Not currently reachable — every real `self.body` reassignment site keeps the previous list alive via a stack/attribute for the whole swap duration (confirmed by the review's own tracing, and by `tests/test_desc_break_marker_buffer_swap_gate.py`'s own candid docstring that its fixture doesn't exercise a genuine cross-buffer comparison). No must-have depends on this; recorded for completeness since the phase's own review flagged it as a class of bug that's "hard to detect in review." |
| `typsphinx/translator.py` | `visit_field_list`, `list_item_needs_separator = False` reset | Inert reset that diverges from the `block_quote`/`desc_content` sibling idiom with no stated reason | ℹ️ Info (from fresh `38-REVIEW.md`, confirmed present) | Traced by the review to have zero observable effect (removing it produces byte-identical output for every construct in the suite). Not a functional issue. |
| — | — | Debt markers (`TBD`/`FIXME`/`XXX`) | — | None found in any of the 7 files this plan (or the whole phase) touched. |

**None of the three items above are must-have failures** — they are pre-existing-phase code-quality
notes from the fresh `38-REVIEW.md` (dated after 38-09, re-reviewing the current tree), rated
warning/info, not critical, and none touches an IND/FLD requirement's behavior. They are carried here
for visibility, not as gaps.

### Documentation-vs-scope finding (not resolved either way — human decision requested)

**ROADMAP.md, Phase 38, Success Criterion #4:**
> "One named indent constant drives desc nesting, field lists, and block quotes — a repo-wide grep
> over `typsphinx/` finds no second independent indent literal at those sites."

**REQUIREMENTS.md, IND-04:**
> "One shared indent constant drives every indent context — desc nesting, field lists, and block
> quotes — rather than independent magic numbers per node type."

**38-CONTEXT.md, D-04 (locked decision, recorded 2026-08-01, before any plan was written):**
> "`visit_block_quote` / `depart_block_quote` are NOT touched. This is the binding reading of IND-04,
> recorded so verify-time does not re-open it. ... IND-04's purpose is to forbid per-node magic
> numbers, not to force every indent context onto one visual depth."

**What is actually shipped**, confirmed by direct code reading in this pass:
`visit_block_quote`/`depart_block_quote` emit `quote(block: true, {...})` with **no** `pad(left:
SHARED_INDENT_STEP, ...)` wrapper and **no** reference to the constant at all — block quotes get
their indent entirely from Typst's own `quote()` default (measured at 1em/11.0pt in 38-CONTEXT.md,
versus the shared step's 27.5pt). `tests/test_desc_content_indent_render_gate.py::test_ind04_d04_block_quote_not_converted`
exists specifically to pin this as a **non**-conversion, and is green.

**The tension:** the mechanical, grep-checkable half of both SC#4 and IND-04 ("a repo-wide grep finds
no second independent indent literal") is genuinely satisfied — confirmed by grep in this pass, above.
But the plain-language half of both sentences ("[the constant] drives ... block quotes") is not
literally true of the shipped design: block quotes are not driven by `SHARED_INDENT_STEP` at all, by
deliberate choice. `38-CONTEXT.md` argues this reading is intentional and non-negotiable ("do not
re-open"), and the code review (independently, post-38-09) does not flag the *behavior* as wrong —
only the *stale header comment* that still asserts block_quote is a consumer (see Anti-Patterns
above).

This verification does **not** resolve the tension in either direction:
- It does not fail IND-04 as a gap, because the grep-checkable criterion holds and D-04 is a
  recorded, reasoned, owner-level decision from this phase's own context-gathering.
- It does not silently accept the ROADMAP/REQUIREMENTS prose as accurate either, because "drives ...
  block quotes" is not true of the code as shipped, and — unlike FLD-02's stale parenthetical, which
  38-09 explicitly corrected — the SC#4/IND-04 prose was never updated to reflect D-04's narrower
  scope.

Routed to human verification (see frontmatter) rather than decided here.

### Human Verification Required

1. **Documentation-vs-scope: does ROADMAP SC#4 / REQUIREMENTS IND-04's "drives ... block quotes"
   prose need correcting to match D-04's narrower, shipped scope, or was block_quote participation
   actually intended and the implementation is the thing that needs to change?**
   - **Test:** Read the finding above (also in frontmatter `human_verification`).
   - **Expected:** A decision — either accept D-04's reading and edit the two prose sentences (the
     same treatment FLD-02's stale parenthetical got in this phase), or treat this as a real,
     unmet SC#4/IND-04 clause and open a follow-up.
   - **Why human:** Values/scope call already made once by the project owner (D-04), but never
     reconciled with the roadmap/requirements wording it reinterprets; not something a grep or a
     test can adjudicate.

## Gaps Summary

No gaps. The one gap the prior verification recorded (FLD-02's list-item nesting regression) is
closed and independently reproduced in this pass, both structurally (`.typ` inspection of a
fresh, hand-written fixture never seen by the test suite) and via the phase's own test gate (5/5
list-item node ids, re-run directly). All 8 requirement IDs are `Complete` in REQUIREMENTS.md, the
whole suite is green (734 passed / 1 skipped / 0 failed, confirmed by direct re-run in this pass,
not inherited from SUMMARY.md), and the lint/type trio is clean.

The phase is held at `human_needed` rather than `passed` solely because of the one open
documentation-vs-scope tension above (SC#4/IND-04 prose vs. D-04's shipped, narrower reading), which
is a wording/values question outside what code inspection can resolve on its own.

---

_Verified: 2026-08-02_
_Verifier: Claude (gsd-verifier)_
