---
phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate
reviewed: 2026-08-30T00:00:00Z
depth: standard
files_reviewed: 30
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_inline_image_separator_render_gate.py
  - tests/fixtures/inline_image_separator_render_gate/conf.py
  - tests/fixtures/inline_image_separator_render_gate/index.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_parent.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_01_sub_mid_sentence.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_02_two_subs_adjacent.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_03_sub_in_list_item.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_04_block_image_second_in_list_item.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_05_image_in_table_cell.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_06_image_in_definition_list_body.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_07_image_in_admonition.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_08_image_in_footnote_body.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_09_image_in_legend_mid_text.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_10_two_images_in_legend.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_11_image_after_inline_literal.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_12_image_after_emphasis.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_13_image_after_reference.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_14_image_in_field_list_body.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_15_image_in_section_title.rst
  - tests/fixtures/inline_image_separator_render_gate/fail_16_image_with_width_mid_sentence.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_a_standalone_block_image.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_b_figure_with_caption.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_c_image_first_in_paragraph.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_d_image_with_dimensions_and_scale_align.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_e_image_with_propagated_target_id.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_f_figure_with_plain_legend.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_g_figure_in_list_item_after_paragraph.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_h_figure_first_in_list_item.rst
  - tests/fixtures/inline_image_separator_render_gate/pass_i_bare_image_first_in_list_item.rst
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 62: Code Review Report

**Reviewed:** 2026-08-30T00:00:00Z
**Depth:** standard
**Files Reviewed:** 30 (1 translator module + 1 test module + 28 fixture files)
**Status:** issues_found

## Summary

The substantive change is confined to `typsphinx/translator.py`'s `visit_image()`/`depart_image()`: the
leading separator triad (`_add_paragraph_separator()` + concat-or-list-item-newline fallback) was hoisted
above the `if self.in_figure:` split, and `depart_image()`'s trailing bookkeeping was made concat-aware
(`_mark_inline_concat_content()` early-return, and `list_item_needs_separator` now set unconditionally on
the non-concat path). I read the diff in isolation (`git diff 6224298e..HEAD -- typsphinx/translator.py`),
traced the new triad against every one of the five inline-concat contexts (`_in_desc_parameter`,
`_in_link`, `_in_term`, `_in_field_body`, `_in_attribution`) and the `in_list_item`/`in_figure` state
machines it now participates in, and ran the full test module plus `black`/`ruff`/`mypy` against the
touched files — all green (30/30 tests, no lint/type findings).

I did not find a missing-separator or double-separator defect that breaks compilation anywhere in the
combinatorics I traced (the fix's own stack-save/restore machinery on the wrapper visitors — `visit_reference`,
`visit_figure`, `_emit_id_anchors` — resets `list_item_needs_separator` for children before they run, which
is what keeps the newly-added `visit_image` triad from double-firing against those callers' own leading
separators). The 25-fixture, 18-master real-`typst.compile()` matrix is a strong gate and none of it is
vacuously passing — the structural `)image(` assertions are backed by a `returncode == 0` real-compile
assertion in the same test method, and the golden-byte-comparison tests do direct file-content diffs.

What I did find: one genuine (if functionally harmless) redundant-separator emission that the test suite
itself pins rather than fixes (worth flagging per the adversarial mandate even though the team already
knows about it), a maintainability gap where the actual fix payload in `depart_image()` carries zero
rationale comment in a file whose established convention is dense per-line rationale, and two untested
state-combinations that I traced by hand and believe are cosmetically redundant but not compile-breaking.

## Warnings

### WR-01: `visit_image()`'s hoisted `_add_paragraph_separator()` call produces a redundant blank line whenever the image is the first paragraph child or a following-sibling inside a concat context

**File:** `typsphinx/translator.py:4750-4754`
**Issue:** The new leading triad calls `self._add_paragraph_separator()` unconditionally, before checking
whether a concat context or `in_list_item` state should own the separator. `_add_paragraph_separator()`
sets `self.paragraph_has_content = True` as a side effect any time `self.in_paragraph` is true — including
when the image is the *first* content of the paragraph. `depart_image()` then unconditionally appends its
own `"\n\n"` (when not in a concat context and not in a figure). The next sibling's own leading separator
call (e.g. `visit_Text`) now sees `paragraph_has_content == True` (set by the image, not by itself) and
emits its own `"\n"` on top of `depart_image`'s `"\n\n"` — three consecutive newlines instead of two.

This is not hypothetical: it is the exact, measured, and *intentionally accepted* delta between
`goldens/pass_c_image_first_in_paragraph.pre_fix.typ` and `goldens/pass_c_image_first_in_paragraph.typ`
(`tests/test_inline_image_separator_render_gate.py::TestInlineImageSeparatorGoldens::test_pass_c_delta_against_unfixed_capture_is_exactly_one_blank_line`
pins it to "exactly one added blank line, zero removed lines" rather than eliminating it). It compounds
per additional leading image (e.g. two adjacent substitution images at the start of a paragraph would each
add one more redundant blank line). It is functionally harmless — Typst's code-mode block only cares about
*a* newline boundary between adjacent bare-expression statements, not how many consecutive blank lines
separate them, which is why the real-compile gate still passes — but it is a real, provable double-emission
of separator state that will recur for every "image-first-in-paragraph" and "image-in-concat-context"
shape going forward, and it silently grows the emitted `.typ` output.

**Fix:** Either (a) don't set `paragraph_has_content = True` from an element that never actually needs the
paragraph-level separator for itself (only `_add_paragraph_separator()`'s *read* of the flag matters for the
image; the *write* is what leaks), or (b) make `depart_image`'s trailing `"\n\n"` conditional on `not
self.in_paragraph` (paragraph-internal separation should be owned entirely by the next sibling's own leading
separator call, exactly as it already is for `visit_Text`/`visit_literal`/`visit_emphasis`, none of which
emit a block-level trailing newline of their own). Example for (b):
```python
if not self.in_figure:
    if self._mark_inline_concat_content():
        return
    if self.in_list_item:
        self.list_item_needs_separator = True
    if not self.in_paragraph:
        self.add_text("\n\n")
```

### WR-02: `depart_image()`'s new concat-aware bookkeeping has zero rationale comment, unlike every other line touched in this diff

**File:** `typsphinx/translator.py:4786-4792`
**Issue:** `visit_image()`'s new lines carry a one-line traceability comment (`# IMG-08 (AMENDED D-08):
mirrors visit_Text's in_signature_text triad.`), and the rest of this ~2700-line file is written in a style
of dense, load-bearing rationale comments per changed block (see `_emit_forced_break`, `visit_figure`,
`visit_field_body`/`depart_field_body`, all touched or read during this review — every one of them explains
*why* a given line exists, often citing the exact regression it prevents). `depart_image()`'s new lines have
none:
```python
if not self.in_figure:
    if self._mark_inline_concat_content():
        return
    if self.in_list_item:
        self.list_item_needs_separator = True
    self.add_text("\n\n")
```
This is the actual payload of the bug fix (a block image inside a list item previously never marked itself
as "needs separator" for a following sibling — exactly `fail_04_block_image_second_in_list_item`'s defect).
Read cold, `if self.in_list_item: self.list_item_needs_separator = True` immediately followed by an
unconditional `self.add_text("\n\n")` looks like dead/redundant bookkeeping (the `"\n\n"` already looks like
it "handles" separation), inviting a future contributor to delete the `list_item_needs_separator` line as
a cleanup — silently reintroducing the exact defect this phase fixes for the case where a later sibling in
the same list item is NOT the very next node visited (e.g., separated by additional nested block structure
that reads `list_item_needs_separator` without going through `add_text("\n\n")` itself first, such as a
following `visit_figure` or `_emit_id_anchors` call).

**Fix:** Add a short comment mirroring `visit_image`'s own, e.g.:
```python
# IMG-09: unconditionally mark that a following list-item sibling needs a
# separator (fail_04's root cause: a block image never did this, so a
# subsequent block-level sibling juxtaposed directly against it). The
# _mark_inline_concat_content() early return above is the concat-context
# analogue -- returning skips this trailing "\n\n" too, since the enclosing
# concat expression doesn't want a block-level blank line inside it.
```

## Info

### IN-01: No fixture exercises "propagated target id" combined with "non-first sibling inside a list item"

**File:** `tests/fixtures/inline_image_separator_render_gate/` (matrix), `typsphinx/translator.py:4733-4734` (`_emit_id_anchors` call site)
**Issue:** `_emit_id_anchors()` (called at the top of `visit_image`, before the new triad) has its own
independent `list_item_needs_separator` read/write when the image node carries a propagated `.. _target:`
id. `pass_e_image_with_propagated_target_id` exercises the id-anchor path but only at document top level
(not inside a list item, and not as a non-first sibling), so the composition of `_emit_id_anchors`'s
trailing `list_item_needs_separator = True` with the new triad's own leading `list_item_needs_separator`
read immediately afterward is never exercised end-to-end by the matrix. Manual trace suggests this
composition only produces one more redundant blank line (same class as WR-01), not a missing separator or
compile failure, but it is an untested interaction between two separator-writing sites inside the same
visitor.
**Fix:** Add a fixture (or extend an existing PASS fixture) with a propagated target id on a block image
that is the second-or-later child of a list item, and pin its golden.

### IN-02: No fixture exercises an image wrapped in a hyperlink (`:target:`) inside a paragraph or list item

**File:** `tests/fixtures/inline_image_separator_render_gate/` (matrix)
**Issue:** None of the 25 `.rst` fixtures give an image a `:target:` (which docutils lowers to a `reference`
node wrapping the `image` node, activating the `_in_link`/`_link_has_content` concat context via
`visit_reference` around the image). This is a realistic authoring pattern (a clickable figure/image) and is
the one case where `_add_paragraph_separator()`'s new unconditional call in `visit_image` runs *inside* an
already-open `link(...)` call whose own leading separator already fired once (in `visit_reference`). Manual
trace suggests this, too, only produces a redundant newline (harmless inside a parenthesized argument list,
per Typst's grammar), not a missing separator — but it is untested.
**Fix:** Add a `pass_j`-style fixture: `.. image:: /_static/pic.png\n   :target: https://example.com/` as a
paragraph child, and as a list-item child, with pinned goldens.

---

_Reviewed: 2026-08-30T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
