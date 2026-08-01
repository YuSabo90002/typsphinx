---
phase: 38-structural-indentation-info-fields
reviewed: 2026-08-01T00:00:00Z
depth: standard
files_reviewed: 18
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_desc_content_indent_render_gate.py
  - tests/test_field_body_typography_render_gate.py
  - tests/test_desc_break_marker_buffer_swap_gate.py
  - tests/test_signature_break_and_arrow_gate.py
  - tests/test_desc_rubric_decoupling_render_gate.py
  - tests/test_field_list_in_list_item_render_gate.py
  - tests/test_signature_page_boundary_render_gate.py
  - tests/test_signature_typography_multi_signature_page_count_gate.py
  - tests/fixtures/desc_content_indent_render_gate/conf.py
  - tests/fixtures/desc_content_indent_render_gate/index.rst
  - tests/fixtures/field_body_typography_render_gate/conf.py
  - tests/fixtures/field_body_typography_render_gate/index.rst
  - tests/fixtures/desc_break_marker_buffer_swap_gate/conf.py
  - tests/fixtures/desc_break_marker_buffer_swap_gate/index.rst
  - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
  - tests/fixtures/inline_math_pdf_text_mitex.golden.txt
  - tests/fixtures/inline_math_pdf_text_native.golden.txt
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: issues_found
---

# Phase 38: Code Review Report

**Reviewed:** 2026-08-01T00:00:00Z
**Depth:** standard
**Files Reviewed:** 18
**Status:** issues_found

## Summary

Reviewed the Phase 38 diff against `typsphinx/translator.py` (the `desc_content`/
`field_list` indent wrappers, the buffer-identifying `_desc_break_marker`, the FLD-02
single-paragraph field-body unwrap, the `self.body.append` → `self.add_text`
conversions, and the `literal_strong`/`literal_emphasis` de-delegation) plus the
associated test/fixture files, at standard depth with targeted empirical verification
(real `sphinx-build`/`typst.compile()`/`pypdf` reproductions for every hypothesis below
— not just static reading).

The buffer-identifying `_desc_break_marker` change, the `add_text` conversions
(verified: both the `depart_desc_signature` and the field_list-family table-cell fixes
now compile where they previously aborted), the `SHARED_INDENT_STEP` interpolation, and
the `literal_strong`/`literal_emphasis` de-delegation are all correct as implemented and
match their documented contracts.

One finding is a genuine, empirically-confirmed correctness defect: the phase's
headline FLD-02/D-07 fix (single-value field label and value share one line) silently
does not apply whenever the enclosing field list is nested inside a list item — a
directly-relevant, previously-tested nesting shape (`test_field_list_in_list_item_
render_gate.py` exists specifically for field-lists-in-list-items, just never with a
single-paragraph field body). Two further findings concern test/fixture quality: a
stale fixture comment plus a missing positive regression test for a fix this phase
itself shipped, and a hardcoded constant that should be imported instead.

## Critical Issues

### CR-01: FLD-02/D-07 single-value field-body fix is bypassed inside list items

**File:** `typsphinx/translator.py:872-885` (`visit_paragraph`), `typsphinx/translator.py:906-915` (`depart_paragraph`)

**Issue:** `visit_paragraph` and `depart_paragraph` check `if self.in_list_item:`
*before* checking `if self._field_body_unwrapped_paragraph:`. `self.in_list_item`
stays `True` for all descendants of a list item, including a `field_list`/`field`/
`field_body`/`paragraph` nested inside it — nothing resets it for that nesting. As a
result, whenever a `desc` (e.g. a `py:function::`) carrying a single-value field (a
`:returns:`/`:param:`/etc. whose body is exactly one `paragraph`) is documented inside
a bullet/enumerated list item, the pre-existing D-13 in-list-item branch fires first
and unconditionally emits `_emit_forced_break("parbreak()")` before the field body's
paragraph content — even though `_field_body_unwrapped_paragraph` is `True` for that
same paragraph. This reintroduces exactly the defect FLD-02/D-07 was built to remove:
the field label and its value land on two separate lines/paragraphs instead of one.

Verified with a real build (`sphinx-build -b typstpdf` + `typst.compile()` +
`pypdf.PdfReader` text extraction) of:

```rst
#. First step.

   .. py:function:: field_double_break()

      :returns: A short stable value that is a full sentence for testing.
      :rtype: str
      :raises ValueError: If something goes wrong in this test scenario.
```

Emitted `.typ` (excerpt):

```
pad(left: 2.5em, {strong(text("Returns") + text(": "))

parbreak()
text("A short stable value that is a full sentence for testing.")
parbreak()

strong(
text("Return type") + text(": "))

parbreak()
text("str")
parbreak()
...
```

pypdf-extracted PDF text:

```
1. First step.
field_double_break()
Returns:
A short stable value that is a full sentence for testing.
Return type:
str
Raises:
ValueError – If something goes wrong in this test scenario.
2. Second step.
```

Every label (`Returns:`, `Return type:`, `Raises:`) is split from its own value onto a
separate line — the exact pre-Phase-38 defect
`test_field_body_typography_render_gate.py::test_fld02_single_value_pdf_adjacency_
matches_pinned_string` proves is fixed at top level (`PINNED_FLD02_ADJACENCY_STRING =
"Returns: A short stable value."`). No test in this phase's suite reaches this
combination: `test_field_list_in_list_item_render_gate.py`'s own list-item-nested
field list uses only collapsed-inline (literal) field bodies, never a single-paragraph
one, so the interaction between D-13 (list-item paragraph handling) and FLD-02/D-07
(single-paragraph field-body unwrap) is untested and broken.

Also note `depart_field_body`'s new D-07/D-08 compensating `parbreak()` (`typsphinx/
translator.py:5736-5738`) fires unconditionally (it does not check `self.in_list_item`
either), so inside a list item the inter-field separation is *doubly* provided — once
by this compensating break and again by the next field's own D-13 paragraph break —
while the far more visible label/value intra-field split above is what a reader would
actually notice.

**Fix:** Give `_field_body_unwrapped_paragraph` priority over the plain `in_list_item`
check in both `visit_paragraph` and `depart_paragraph` (or fold the two cases into one
branch), so a single-value field body's paragraph is recognized before the generic
list-item paragraph handling short-circuits it, e.g.:

```python
def visit_paragraph(self, node: nodes.paragraph) -> None:
    ...
    if self._field_body_unwrapped_paragraph:
        self.in_paragraph = False
        return

    if self.in_list_item:
        self._emit_forced_break("parbreak()")
        self.in_paragraph = False
        return
    ...
```

with the equivalent reorder in `depart_paragraph`, and a new fixture construct (a field
list with a single-paragraph field body nested inside a list item) added to prove the
label/value now share one line in that context too.

## Warnings

### WR-01: Table-cell `add_text` fixes shipped this phase have no positive regression test, and the fixture comment describing them is now stale

**File:** `tests/fixtures/desc_content_indent_render_gate/index.rst:88-114` ("Table-Cell CONTROL")

**Issue:** This fixture section's comment states that a `desc` (of any shape) or a
field list inside a table cell "abort[s] the ENTIRE Typst compile" via
"PRE-EXISTING `self.body.append` bugs...depart_desc_signature is Phase 37's completed
work (not in 38-CONTEXT.md's in-scope handler list)", and deliberately keeps the
section desc-free "as a non-regression baseline" pending "those sites [being] fixed."
However, this same phase's diff *did* convert `depart_desc_signature`'s two
`self.body.append` calls (`typsphinx/translator.py`, anchor-loop + trailing spacing) to
`self.add_text`, along with five field_list-family sites. Verified with a real build: a
body-less/parameterless `.. py:attribute::` inside a `list-table` cell, and a plain
`field_list` (`:note:`/`:warning:`) inside a `list-table` cell, both now compile
successfully — the exact scenario the comment says still aborts. (A `py:function::`
with a parameter list inside a table cell *does* still abort, but from an unrelated,
still-unconverted `self.body.append` in `visit_desc_parameterlist`/
`depart_desc_parameterlist`, out of this phase's scope.)

The net effect: two of the fixes this phase's diff makes (and that the review's own
project invariants call out as significant — "Two such defects were fixed this
phase") have no automated test anywhere in the reviewed scope proving they resolved the
table-cell compile abort, and the one fixture whose comment discusses this exact class
of bug now documents a state that is only partially true.

**Fix:** Add a positive construct to this fixture (or a new one) — a body-less `desc`
and a plain `field_list` inside a table cell, without a parameter list — asserting a
clean compile, and update the "Table-Cell CONTROL" comment to distinguish the sites
this phase fixed (now compile) from the still-broken, out-of-scope
`desc_parameterlist` site.

### WR-02: `test_desc_content_indent_render_gate.py` hardcodes `"2.5em"` instead of importing `SHARED_INDENT_STEP`

**File:** `tests/test_desc_content_indent_render_gate.py:278, 288, 315, 372, 419`

**Issue:** Five assertions hardcode the literal string `"pad(left: 2.5em, {"` to check
for the indent wrapper's presence/position/count. The sibling module
`tests/test_field_body_typography_render_gate.py` (same phase, same review scope)
instead does `from typsphinx.translator import SHARED_INDENT_STEP` and builds the
expected token as `f"pad(left: {SHARED_INDENT_STEP}, {{"`. The two modules are
inconsistent, and the hardcoded version is a silent-drift risk: if
`SHARED_INDENT_STEP`'s value ever changes, this file's five assertions will not track
it automatically and must be found and updated by hand, whereas the sibling module
would not need any edit.

**Fix:** Import `SHARED_INDENT_STEP` from `typsphinx.translator` in
`test_desc_content_indent_render_gate.py` and interpolate it the same way
`test_field_body_typography_render_gate.py` does.

## Info

### IN-01: `_emit_field_body_monospace_leaf` does not mirror `visit_literal`'s table-cell/FID-10 zero-width-space injection

**File:** `typsphinx/translator.py:5060-5099` (`_emit_field_body_monospace_leaf`)

**Issue:** The docstring explicitly scopes this helper to mirror only `visit_literal`'s
leaf-emission *shape* (paragraph separator, concat separator, the call, content
marking) and its escaping (`escape_typst_string` alone, no SIG-07 zero-width-space
injection) — deliberately, not `visit_literal`'s `self.in_table` zero-width-space
injection or its FID-10 leading-punctuation zero-width-space injection. Given
`literal_strong`/`literal_emphasis` are field-body-only leaves and a field list inside
a table cell is an unusual (if now-reachable, per WR-01) construct, this is very likely
an intentional, correctly-scoped omission rather than an oversight, but it is worth
recording: if a field list bearing `literal_strong`/`literal_emphasis` content is ever
exercised inside a table cell, a long unbroken parameter name in that cell will not
wrap the way an equivalent `visit_literal` value would.

**Fix:** No action required unless a future phase puts field-body monospace leaves
inside table cells in scope; if so, this is the site to revisit.

---

_Reviewed: 2026-08-01T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
