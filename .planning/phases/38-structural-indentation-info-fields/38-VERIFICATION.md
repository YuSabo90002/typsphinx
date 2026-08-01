---
phase: 38-structural-indentation-info-fields
verified: 2026-08-01T00:00:00Z
status: gaps_found
score: 7/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "FLD-02: A field body with multiple values renders as a bulleted list; a single-value body stays inline prose."
    status: partial
    reason: >
      visit_paragraph/depart_paragraph (typsphinx/translator.py, visit_paragraph ~L868-885,
      depart_paragraph ~L901-915) check `if self.in_list_item:` BEFORE checking
      `if self._field_body_unwrapped_paragraph:`. Nothing resets in_list_item for a
      field_list/field/field_body/paragraph nested inside a list item, so the pre-existing
      in-list-item branch (D-13's forced parbreak()) fires first and unconditionally
      reintroduces a paragraph break between a single-value field's label and its value,
      even though _field_body_unwrapped_paragraph is True for that same paragraph. This
      reproduces the exact pre-Phase-38 defect FLD-02/D-07 was built to remove, but only
      for desc nodes documented inside a bullet/enumerated list item -- a directly relevant,
      previously-tested nesting shape (tests/test_field_list_in_list_item_render_gate.py
      exists specifically for field lists nested inside list items, but its own fixture
      only exercises collapsed-inline/literal field bodies, never a single-paragraph one,
      so the interaction is untested). Independently reproduced in this verification pass
      with a real sphinx-build -b typst (see evidence below) -- not accepted on the code
      review's word alone.

      Outside a list item (the common case: top-level desc, or a desc nested only inside
      another desc/class body), the fix is correct and independently confirmed via a real
      compiled PDF's pypdf-extracted glyph coordinates: label and value land on the exact
      same y-coordinate (adjacent, one line), and this holds through a 3-level class/method/
      attribute nest. ROADMAP SC#5 and REQUIREMENTS.md FLD-02 state the property with no
      list-item qualifier, so the requirement is not met in full -- it is met for the
      primary/common code path and silently regresses in a reachable, adjacent-tested
      nesting context. Judgment: PARTIALLY MET, not a documented/accepted limitation --
      no CONTEXT.md decision (D-07/D-08) scopes FLD-02 to exclude list items, and no
      VERIFICATION override was added.
    artifacts:
      - path: "typsphinx/translator.py"
        issue: "visit_paragraph (~L868-885) and depart_paragraph (~L901-915): the `if self.in_list_item:` branch is checked before `if self._field_body_unwrapped_paragraph:`, so the list-item branch short-circuits the single-value field-body unwrap whenever both are true simultaneously."
    missing:
      - "Reorder the two checks in both visit_paragraph and depart_paragraph so _field_body_unwrapped_paragraph is checked before (or takes priority over) in_list_item, per CR-01's own suggested fix in 38-REVIEW.md."
      - "A new fixture construct: a field list with a single-paragraph field body (e.g. a py:function:: with a :returns: whose value is one sentence) nested inside a bullet or enumerated list item, asserting the label and value share one line/one PDF text-extraction line in that context too."
      - "38-REVIEW.md also flags (WR-01, WR-02, non-blocking) that two table-cell add_text fixes this phase shipped have no positive regression test, and that test_desc_content_indent_render_gate.py hardcodes '2.5em' instead of importing SHARED_INDENT_STEP. Not required to close this gap but should be swept up in the same fix if convenient."
---

# Phase 38: Structural Indentation + Info Fields Verification Report

**Phase Goal:** The page shows structure. A description body sits one indent step inside its own
signature, indentation accumulates with nesting depth so a method's membership in its class is
visually recoverable, a nested member's own signature aligns with its parent's body rather than
over-indenting, and the field-list block follows the same single constant instead of a private
magic number.
**Verified:** 2026-08-01
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

All measurements below were taken independently in this verification pass — a fresh
`sphinx-build -b typst` / `-b typstpdf` of hand-written fixtures, real `typst.compile()`, and real
`pypdf.PdfReader` text/coordinate extraction — never inherited from SUMMARY.md, 38-REVIEW.md, or
38-GATE-EVIDENCE.md claims without reproduction. Fixture: a `py:class:: Widget(name, size=10)`
containing a `py:method:: resize(width, height)` (with a full `:param:`/`:type:`/`:returns:`/
`:rtype:` field list) containing a `py:attribute:: inner`, followed by a sibling top-level
`py:function:: toplevel(a)` — plus a separate list-item fixture for the CR-01 reproduction.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | IND-01 — `desc_content` body indented one step past its own `desc_signature` | ✓ VERIFIED | pypdf glyph x-coordinates from a real compiled PDF: class signature `class Widget(...)` at x=70.87pt; class body `"A widget class body paragraph."` at x=98.37pt. Delta = 27.5pt = 2.5em @ 11pt, matching `SHARED_INDENT_STEP`. |
| 2 | IND-02 — indentation cumulative with nesting depth | ✓ VERIFIED | Method body `"A method body paragraph."` at x=125.87pt vs. its own signature `resize(...)` at x=98.37pt (delta 27.5pt, one further step than the class). Class body resumes at x=98.37pt (`"Class body continues here."`) after the nested member closes — correctly returns to its own level, not the method's. |
| 3 | IND-03 — nested member's own signature aligns with parent body, no extra step | ✓ VERIFIED | `resize(...)` signature x=98.37pt == class body x=98.37pt exactly. Verified at a second nesting level too: `inner` (attribute signature) x=125.87pt == method body x=125.87pt exactly. |
| 4 | IND-04 — one shared indent constant; no second independent indent literal | ✓ VERIFIED | `awk` + `grep -vE '^[[:space:]]*#'` over `typsphinx/translator.py` for an `em`-suffixed numeric literal returns exactly one line: `29: SHARED_INDENT_STEP = "2.5em"`. `grep -n 'pad(' typsphinx/translator.py` shows exactly 2 call sites (`desc_content` L5234, `field_list` L5548), both interpolating `SHARED_INDENT_STEP` by name. `visit_block_quote`/`depart_block_quote` (L2920-2985) contain no `pad(` and no `SHARED_INDENT_STEP` reference — confirmed untouched, as D-04 requires. |
| 5 | IND-05 — depth does not leak across sibling `desc` nodes | ✓ VERIFIED | After the 3-level nest closes, the sibling `toplevel(a)` signature is at x=70.87pt — identical to the class's own signature x, not accumulated from the nested nesting. Its own body (`"A sibling top-level function."`) sits at x=98.37pt, exactly one step in, not three. This is genuine sibling-boundary depth-reset evidence (measured position after a real nest closes), not merely "the test suite passes" — confirms the CONTEXT.md D-01/IND-05 "asserted, not implemented" framing is honest: there is no counter to leak, and the measured PDF proves it doesn't. |
| 6 | FLD-01 — field list indented one step beyond the surrounding desc body | ✓ VERIFIED | `Parameters:` label at x=153.37pt vs. method body x=125.87pt (delta 27.5pt). Matches `38-CONTEXT.md`'s own D-03 measurement pattern (nested `pad` inside the body's `pad`). |
| 7 | FLD-02 — multi-value field body bulleted; single-value field body stays inline prose | ⚠ PARTIAL (gap) | Multi-value (`:param:` × 2) renders as `list({...}, {...})` bullets — confirmed and unaffected. Single-value (`:returns:`/`:rtype:`) at top level/non-list-item nesting: confirmed same-line (`Returns:` and `nothing` share pypdf y-coordinate 615.88; `Return type:` and `None` share y=595.45) — the fix works correctly here. **But** independently reproduced with a real build: a `py:function::` with a `:returns:` field nested inside an enumerated list item emits `strong(text("Returns") + text(": "))` followed by `parbreak()` then the value on its own line/paragraph — the exact pre-phase defect, silently reintroduced by `visit_paragraph`'s `in_list_item` branch firing before the `_field_body_unwrapped_paragraph` branch. See gap in frontmatter. |
| 8 | FLD-03 — field-body parameter name/type carry monospace treatment distinct from the plain-bold label | ✓ VERIFIED | Emitted `.typ`: `strong(raw("width"))` (bold monospace name), `emph(raw("int"))` (italic monospace type), label unchanged as `strong(text("Parameters") + text(": "))` (proportional). Matches D-05 variant A exactly. `tests/test_field_body_typography_render_gate.py`'s 20 `test_fld03_*` node ids re-run directly in this pass, all pass. |

**Score:** 7/8 truths verified (FLD-02 partial — see gap)

### Independent Reproduction of the Flagged Defect (CR-01 / FLD-02)

Built directly in this verification pass (`sphinx-build -b typst`, no modification to the repo):

```rst
#. First step.

   .. py:function:: field_double_break()

      :returns: A short stable value.
```

Emitted `.typ` (excerpt, matches CR-01's own reproduction):

```
pad(left: 2.5em, {
pad(left: 2.5em, {strong(text("Returns") + text(": "))

parbreak()
text("A short stable value.")
})
})
```

Compare the same field at top level (same fixture, outside any list item):

```
pad(left: 2.5em, {pad(left: 2.5em, {strong(text("Returns") + text(": "))
text("A short stable value.")
})
})
```

No `parbreak()` between label and value at top level; one inserted between them inside the list
item. Root cause confirmed by reading `typsphinx/translator.py`: `visit_paragraph`'s
`if self.in_list_item:` branch (line ~872) returns before the `if self._field_body_unwrapped_paragraph:`
branch (line ~883) is ever reached.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::visit_desc_content`/`depart_desc_content` | `pad(left: SHARED_INDENT_STEP, {...})` wrapper, no depth counter | ✓ VERIFIED | Confirmed via emitted `.typ` and PDF measurements above; `git diff --name-status` against phase base `1fefe51` shows only `typsphinx/translator.py` modified across the whole phase. |
| `typsphinx/translator.py::visit_field_list`/`depart_field_list` | Nested `pad(left: SHARED_INDENT_STEP, {...})` | ✓ VERIFIED | Confirmed via emitted `.typ`; field list wrapper measured nested inside the body wrapper. |
| `typsphinx/translator.py::visit_field_body`/`visit_paragraph` (FLD-02 reflow) | Single-paragraph field body skips `par({`/`})` | ⚠ PARTIAL | Correct at top level; bypassed inside a list item (see gap). |
| `typsphinx/translator.py::visit_literal_strong`/`depart_literal_strong`, `visit_literal_emphasis`/`depart_literal_emphasis` | De-delegated, emit `strong(raw(...))`/`emph(raw(...))` directly | ✓ VERIFIED | Confirmed via emitted `.typ`; `tests/test_desc_rubric_decoupling_render_gate.py`'s SC#1 over-reach guard (re-run in this pass) confirms no remaining dummy-node delegation for these two handlers. |
| `typsphinx/translator.py::depart_desc` marker (D-10) | Buffer-identifying marker `(id(self.body), len(self.body))` | ✓ VERIFIED (structurally) | `tests/test_desc_break_marker_buffer_swap_gate.py` and `tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate` (8 node ids total) re-run directly in this pass, all pass. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `visit_desc_content`/`depart_desc_content` | `SHARED_INDENT_STEP` (translator.py:29) | f-string interpolation `f"pad(left: {SHARED_INDENT_STEP}, {{"` | ✓ WIRED | Same constant, not a new literal (IND-04 grep, above). |
| `visit_field_list`/`depart_field_list` | `SHARED_INDENT_STEP` | same interpolation pattern | ✓ WIRED | Confirmed. |
| `visit_paragraph`/`depart_paragraph` | `_field_body_unwrapped_paragraph` (FLD-02 reflow) | conditional branch, ordered AFTER `in_list_item` | ⚠ PARTIAL WIRING | The link exists and functions when `in_list_item` is False; when both are True, `in_list_item` wins and the intended link is never reached. This is the CR-01 defect. |
| `visit_literal_strong`/`visit_literal_emphasis` | `escape_typst_string` (not `_escape_signature_text`) | direct call in the new leaf-emission helper | ✓ WIRED | Confirmed no zero-width-space injection in field bodies (`test_fld03_no_zero_width_space_anywhere_in_field_bodies`, re-run, passes). |

### Data-Flow Trace (Level 4)

Not applicable — this phase is a docutils-doctree-to-Typst-text translator, not a component
rendering dynamic application state. The "data" here is the doctree itself, and its flow through
each handler is what Key Link Verification above traces.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `desc_content`/`field_list` wrapper renders at correct indent columns | Real `-b typstpdf` build + `pypdf` glyph-coordinate extraction of a hand-written 3-level nested fixture | x-coordinates match D-01/D-03's measured table (27.5pt/55.0pt/82.5pt steps) | ✓ PASS |
| Single-value field body renders inline (top level) | Same build, y-coordinate adjacency check | `Returns:`/`nothing` share one y-coordinate; `Return type:`/`None` share one y-coordinate | ✓ PASS |
| Single-value field body renders inline (inside a list item) | Real `-b typst` build of a list-item-nested `py:function::` with a `:returns:` field | Label and value split by `parbreak()` — defective | ✗ FAIL (this is the gap) |
| `literal_strong`/`literal_emphasis` emit monospace, not proportional | Real `-b typst` build, grep emitted `.typ` for `strong(raw(` / `emph(raw(` | Both present, `strong({text(` / `emph({text(` (proportional, pre-phase shape) absent from the field body | ✓ PASS |
| IND-04 single-literal grep | `awk`+`grep` over `typsphinx/translator.py` | Exactly one `em`-suffixed literal, at `SHARED_INDENT_STEP`'s own definition | ✓ PASS |
| Whole-suite regression | (already run by orchestrator, re-confirmed by re-running the 5 phase-specific gate modules directly, 52/52 node ids) | `52 passed in 6.89s` | ✓ PASS |

### Probe Execution

Not applicable — no `scripts/*/tests/probe-*.sh` exist in this project and none are referenced by
this phase's PLAN/SUMMARY/REQUIREMENTS.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| IND-01 | 38-01, 38-05 | `desc_content` body indented one step past its own signature | ✓ SATISFIED | Measured PDF coordinates, above. |
| IND-02 | 38-01, 38-05 | Cumulative indentation with nesting depth | ✓ SATISFIED | Measured PDF coordinates, above. |
| IND-03 | 38-01, 38-05 | Nested signature aligns with parent body, no extra step | ✓ SATISFIED | Measured at two nesting levels, above. |
| IND-04 | 38-01, 38-04, 38-05, 38-06 | One shared constant, no second indent literal | ✓ SATISFIED | Repo-wide grep, above; block_quote confirmed untouched. |
| IND-05 | 38-01, 38-03, 38-05 | Depth resets correctly across sibling `desc` nodes | ✓ SATISFIED | Measured sibling-boundary reset, above — genuinely covers the sibling-boundary case, not merely "test passes" (per the independence instruction's specific concern). |
| FLD-01 | 38-01, 38-02, 38-04, 38-06 | Field list indented one step beyond desc body | ✓ SATISFIED | Measured PDF coordinates, above. |
| FLD-02 | 38-02, 38-04, 38-06 | Multi-value bulleted; single-value inline | ⚠ **BLOCKED (partial)** | Multi-value: satisfied. Single-value: satisfied outside list items, defective inside list items — reproduced independently in this pass. REQUIREMENTS.md's `[x]` "Complete" status for FLD-02 (lines 95, 280) is **not fully accurate** as of this verification. |
| FLD-03 | 38-02, 38-04, 38-07 | Name/type monospace, distinct from label | ✓ SATISFIED | Measured emitted `.typ`, above; 20/20 `test_fld03_*` node ids pass. |

No orphaned requirements — all 8 IDs (`IND-01..05`, `FLD-01..03`) appear in at least one plan's
`requirements:` frontmatter and REQUIREMENTS.md's phase-mapping table (lines 274-281, 304).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `typsphinx/translator.py` | `visit_paragraph` ~872, `depart_paragraph` ~906 | Branch-ordering defect: `in_list_item` checked before `_field_body_unwrapped_paragraph` | 🛑 Blocker (this gap) | FLD-02 silently regresses to pre-phase behaviour inside list items — see gap above. |
| `tests/fixtures/desc_content_indent_render_gate/index.rst:88-114` | "Table-Cell CONTROL" comment | Stale comment (WR-01, `38-REVIEW.md`): claims a body-less `desc`/plain `field_list` inside a table cell still aborts compilation, but this phase's own `add_text` conversion fixed exactly that case — no positive regression test added for the fix | ⚠ Warning | Non-blocking; two real fixes this phase shipped (`depart_desc_signature`'s and the field-list family's `self.body.append` → `add_text` conversions) have no positive test proving they resolved the table-cell abort, and the fixture comment now documents a partially-stale state. |
| `tests/test_desc_content_indent_render_gate.py:278,288,315,372,419` | hardcoded `"pad(left: 2.5em, {"` | Hardcoded literal instead of `from typsphinx.translator import SHARED_INDENT_STEP` (WR-02, `38-REVIEW.md`) | ⚠ Warning | Non-blocking drift risk; sibling test module already does this correctly, this one does not. |
| No debt markers | — | `git diff 1fefe51 -- typsphinx/translator.py` grepped for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` | — | None found in added lines (two grep hits are prose referencing the now-closed folded todo file path, not debt markers). |

### Human Verification Required

None. Every truth in this phase is mechanically checkable via `.typ`-source structure and/or
`pypdf`-extracted PDF text/coordinates, and every one was checked that way in this pass (no
"visual only" claims were taken on faith — the phase's own D-08/D-02 aesthetic sign-off in
`38-GATE-EVIDENCE.md` §6 is a `[V]`-tagged requirement not in this phase's 8 `[M]`-tagged IDs, and
is out of this verification's scope).

### Gaps Summary

One gap, tied to requirement **FLD-02** and ROADMAP SC#5's "a single-value body stays inline
prose" clause (no list-item qualifier stated anywhere in ROADMAP.md, REQUIREMENTS.md, or
`38-CONTEXT.md`'s D-07/D-08 decisions).

**Judgment on the flagged defect (CR-01):** FLD-02 is **partially met, not a documented/accepted
limitation.** The core single-paragraph-unwrap mechanism (D-07's real work) is correctly
implemented and independently verified for the common/primary code path — a `desc` at top level or
nested only inside another `desc`'s body. It fails, silently and without any test coverage, for a
`desc` documented inside a bullet or enumerated list item, where the pre-existing `in_list_item`
fast-path (originally written for FID-02, unrelated to this phase) short-circuits the new FLD-02
branch and reintroduces the exact pre-phase label/value line-split defect this phase exists to fix.
This is not flagged anywhere in `38-CONTEXT.md`'s decisions as an accepted scope boundary, and
`tests/test_field_list_in_list_item_render_gate.py` — the one fixture family that specifically
exercises field lists inside list items — happens to only use collapsed-inline (literal) field
bodies in its list-item construct, so the gap was never exercised by any test this phase added or
modified. I independently reproduced the defect with a real `sphinx-build -b typst` build in this
verification pass (not on the code review's word alone); the reproduction matches CR-01's own
findings exactly. `depart_field_body`'s new D-07/D-08 compensating `parbreak()` also fires
unconditionally inside a list item (does not check `in_list_item` either), so the inter-field
separation there is doubly provided while the more visible intra-field label/value split is what a
reader would actually notice — noted in CR-01 and confirmed present, though it is a secondary
symptom of the same root cause rather than a second independent defect.

All other 7 requirements (IND-01 through IND-05, FLD-01, FLD-03) were independently re-derived from
a fresh compiled PDF's measured glyph coordinates and the emitted `.typ` source in this pass — not
inherited from SUMMARY.md or 38-GATE-EVIDENCE.md claims — and hold up under that scrutiny,
including IND-05's sibling-boundary depth-reset property, which was specifically checked for
genuine coverage (not merely "the test suite is green") per this verification's independence
instruction.

The two Warning-level findings from `38-REVIEW.md` (WR-01: stale fixture comment / missing
positive regression test for two `add_text` fixes; WR-02: a hardcoded `"2.5em"` instead of an
imported `SHARED_INDENT_STEP`) are real but non-blocking — they are test/documentation quality
issues, not functional defects, and do not gate phase completion on their own. They are recorded
above for whoever authors the gap-closure plan to sweep up alongside the FLD-02 fix if convenient.

---

_Verified: 2026-08-01_
_Verifier: Claude (gsd-verifier)_
