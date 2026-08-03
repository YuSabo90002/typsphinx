---
phase: 38-structural-indentation-info-fields
reviewed: 2026-08-01T14:59:00Z
depth: standard
files_reviewed: 17
files_reviewed_list:
  - tests/fixtures/desc_break_marker_buffer_swap_gate/conf.py
  - tests/fixtures/desc_break_marker_buffer_swap_gate/index.rst
  - tests/fixtures/desc_content_indent_render_gate/conf.py
  - tests/fixtures/desc_content_indent_render_gate/index.rst
  - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
  - tests/fixtures/field_body_typography_render_gate/conf.py
  - tests/fixtures/field_body_typography_render_gate/index.rst
  - tests/fixtures/inline_math_pdf_text_mitex.golden.txt
  - tests/fixtures/inline_math_pdf_text_native.golden.txt
  - tests/test_desc_break_marker_buffer_swap_gate.py
  - tests/test_desc_content_indent_render_gate.py
  - tests/test_desc_rubric_decoupling_render_gate.py
  - tests/test_field_body_typography_render_gate.py
  - tests/test_field_list_in_list_item_render_gate.py
  - tests/test_signature_break_and_arrow_gate.py
  - tests/test_signature_page_boundary_render_gate.py
  - tests/test_signature_typography_multi_signature_page_count_gate.py
  - typsphinx/translator.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 38: Code Review Report (Re-Review)

**Reviewed:** 2026-08-01T14:59:00Z
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

This is a re-review of Phase 38 (structural indentation + info-field typography)
against the CURRENT tree, after plan 38-09's gap closure. The prior `38-REVIEW.md`
findings (CR-01: FLD-02/D-07 bypassed inside list items; WR-01: table-cell
`add_text` fixes had no positive regression test; WR-02: hardcoded `"2.5em"`
literal instead of importing `SHARED_INDENT_STEP`) were all independently
verified fixed below and are **not** carried forward as open findings:

- CR-01: `visit_paragraph`/`depart_paragraph` now check
  `self._field_body_unwrapped_paragraph` **before** `self.in_list_item`
  (translator.py:883, :925), exactly as the prior review's suggested fix
  specified. Confirmed by grep that nothing resets `in_list_item` for a
  `field_list`/`field`/`field_body`/`paragraph` nested inside a list item,
  so the ordering is genuinely load-bearing, and by the new
  `test_field_body_typography_render_gate.py` list-item constructs
  (`_H_LI_BULLET`/`_H_LI_ENUM`) which pin the fixed adjacency via real
  compiled-PDF text extraction.
- WR-01: `test_wr01_bodyless_desc_and_plain_field_list_in_table_cell_compile`
  now exists in `test_desc_content_indent_render_gate.py` and the fixture's
  "Table-Cell CONTROL" comment was rewritten to accurately distinguish the
  sites this phase fixed from the still-unconverted, out-of-scope
  `visit_desc_parameterlist` site.
- WR-02: `test_desc_content_indent_render_gate.py` now imports and uses
  `SHARED_INDENT_STEP` from `typsphinx.translator` throughout, matching
  `test_field_body_typography_render_gate.py`'s existing pattern.

Focus areas verified by direct code reading (not just docstring trust) for
this re-review:

- **`visit_paragraph`/`depart_paragraph` branch order**: confirmed
  load-bearing (see above) and correctly symmetric between visit and
  depart.
- **`depart_field_body`'s trailing-sibling parbreak guard**
  (`node.parent.next_node(descend=False, siblings=True)`): correct, and
  consistent with the pre-existing `depart_desc_parameter`/
  `depart_desc_optional` "does the node I'm departing have a following
  sibling" idiom already used elsewhere in the file. `depart_field`'s own
  `_last_field_body_was_inline` gate correctly excludes the
  single-paragraph-unwrapped case from the FID-09 `text("  ")` separator,
  so the two compensating mechanisms (inter-field `"  "` vs. the
  compensating `parbreak()`) do not double up for any field shape traced
  (collapsed-inline, single-paragraph-unwrapped, multi-value bulleted).
- **`literal_strong`/`literal_emphasis` leaf bodies**
  (`_emit_field_body_monospace_leaf`): correctly mirrors `visit_literal`'s
  leaf-emission shape, uses `escape_typst_string` (not the SIG-07
  dot-injecting signature helper, as the docstring itself argues it
  should not), and composes correctly nested inside a resolved `:type:`'s
  `link(...)` call per
  `test_fld03_resolvable_type_composes_inside_link_unchanged_label`.
- **Test tautology check**: none of the seven test modules read contain
  self-fulfilling assertions. Page-count constants are honestly named for
  what they measure (`EXPECTED_PAGE_COUNT_CEILING`, used with `<=` and
  correctly renamed off the stale `..._PRE_PHASE` name this same phase
  closed; `EXPECTED_PAGE_COUNT`/`EXPECTED_WRAPPER_COUNT` in the
  multi-signature gate are exact-match constants with an honest
  re-measurement note and a documented sensitivity sweep). The
  `desc_break_marker_buffer_swap_gate` module is unusually candid that its
  own fixture does **not** exercise a genuine cross-buffer marker
  comparison — good practice, but it does mean the
  `(id(self.body), len(self.body))` marker's core claim is currently
  untested by construction (see WR-02 below).
- Re-measured/migrated goldens (`inline_math_pdf_text_*.golden.txt`,
  `desc_rubric_decoupling_render_gate/golden.typ`) were checked against
  their own commit history and content: the diffs are the predicted,
  narrowly-scoped consequences of the new indent wrappers (a line-wrap
  shift, an added `pad(left: 2.5em, {...})` pair), not unexplained drift.

Two findings below are genuine, if narrow, quality/robustness issues in the
newly-added code; neither is a correctness blocker, and the full suite is
independently reported green (734 passed / 1 skipped / 0 failed).

## Warnings

### WR-01: Module-header comment claims `block_quote` reuses `SHARED_INDENT_STEP`, contradicting the phase's own D-04 decision and its regression test

**File:** `typsphinx/translator.py:23-29`
**Issue:** The comment introducing `SHARED_INDENT_STEP` reads:

```python
# Shared cross-phase indent quantum (D-08, 37-EMISSION-CONTRACT.md section 1).
# Phase 37 introduces this as the desc_signature hanging-indent step (SIG-07);
# Phase 38's IND-04 reuses this SAME constant for desc_content, field_list and
# block_quote rather than defining a second indent number -- do not introduce
# another one. Value is the owner's D-06 choice (compiled and compared against
# three renderings; see 37-CONTEXT.md).
SHARED_INDENT_STEP = "2.5em"
```

This was written in Phase 37 (commit `550b04a`), before Phase 38 made its
final decision. Phase 38 explicitly and deliberately did **not** convert
`block_quote` to use `SHARED_INDENT_STEP` — this is D-04
(38-EMISSION-CONTRACT.md section 1.2), enforced by a dedicated
non-regression test:

```python
# tests/test_desc_content_indent_render_gate.py
def test_ind04_d04_block_quote_not_converted(self, desc_content_indent_typ_text):
    """... block_quote must NEVER be wrapped in the shared indent step ..."""
    forbidden_composed = f"pad(left: {SHARED_INDENT_STEP}, {{quote(block: true,"
    assert forbidden_composed not in typ_text, ...
```

and `visit_block_quote`/`depart_block_quote` (translator.py:3001-3064) still
emit their own unmodified `quote(block: true, {...})` form with no
`SHARED_INDENT_STEP` involvement at all. The header comment is now stale and
directly contradicts the shipped, tested behavior — a future maintainer
reading only the header (a very likely place to look when touching this
constant) would reasonably conclude block_quote already participates in the
shared indent, or worse, "fix" `visit_block_quote` to match the comment and
silently violate D-04, breaking `test_ind04_d04_block_quote_not_converted`.

**Fix:** Update the comment to match the actual (and tested) design:

```python
# Shared cross-phase indent quantum (D-08, 37-EMISSION-CONTRACT.md section 1).
# Phase 37 introduces this as the desc_signature hanging-indent step (SIG-07);
# Phase 38's IND-04 reuses this SAME constant at two new sites, desc_content
# and field_list -- do not introduce a second indent number for either.
# block_quote is a deliberate NON-consumer (D-04, 38-EMISSION-CONTRACT.md
# section 1.2): it keeps Typst's own quote() default spacing instead, and
# tests/test_desc_content_indent_render_gate.py::test_ind04_d04_block_quote_not_converted
# pins that as a regression control. Value is the owner's D-06 choice
# (compiled and compared against three renderings; see 37-CONTEXT.md).
SHARED_INDENT_STEP = "2.5em"
```

### WR-02: `_desc_break_marker`'s buffer-swap guard uses `id(self.body)` alone, an identity check that is unsound once the referenced object can be garbage-collected

**File:** `typsphinx/translator.py:4962-4968`, `typsphinx/translator.py:5305-5311`
**Issue:** `depart_desc`/`depart_desc_content` suppress a duplicate
`parbreak()` by comparing `self._desc_break_marker == (id(self.body),
len(self.body))`. `id()` only uniquely identifies a *live* Python object —
if the list previously assigned to `self.body` is dropped (no more
references) and garbage-collected before the comparison runs, CPython's
allocator can hand the freed memory address to an unrelated, later-created
list, and `id()` would report the same value for two genuinely different
objects. If that unrelated list's `len()` also happened to coincidentally
match the recorded value, the marker would false-positive and a required
`parbreak()` would be silently dropped (merged paragraphs in the rendered
PDF) — the exact defect class this pair is meant to prevent, reintroduced
through the identity check itself rather than through the bookkeeping logic
around it.

In practice this is not currently reachable: every actual `self.body`
reassignment site (`visit_term`/`visit_definition`'s `_saved_body_stack`,
the admonition-title save/restore, the figure-caption save/restore) keeps
the *previous* list alive via an instance attribute or stack entry for the
whole duration it is swapped out, and `tests/test_desc_break_marker_buffer_swap_gate.py`'s
own docstring honestly documents that the one concretely reachable
nested-desc-inside-a-buffer-swap shape (a `py:class::`/`py:method::` pair
entirely inside one glossary definition) does not actually straddle a live
buffer reassignment — both `depart_desc` calls it compares run against the
*same* buffer object throughout, so no real GC/reuse window exists for that
fixture. The two structurally impossible cases (title/caption text cannot
contain a block-level `desc` directive at the RST grammar level) are
recorded as such in the fixture rather than silently omitted. So the marker
is currently sound by the absence of a reachable adversarial input, not by
construction — and no test in the suite can ever exercise the failure mode
this comparison is theoretically exposed to, since none of the reachable
constructs produce it.

**Fix:** Hold a direct reference to the body object itself (the tuple
already keeps it alive once stored, closing the GC-reuse window for as long
as the marker is retained) and compare with `is` instead of comparing raw
`id()` values:

```python
self._desc_break_marker: tuple[list[Any], int] | None = None
...
if not self.in_table and self._desc_break_marker is not None and (
    self._desc_break_marker[0] is self.body
    and self._desc_break_marker[1] == len(self.body)
):
    return
...
self._desc_break_marker = (self.body, len(self.body))
```

This removes the `id()` proxy entirely — the marker tuple keeps the actual
list object alive for as long as it is the "current" marker, so a later,
unrelated list can never coincidentally reuse its address and produce a
false match. Low priority given the current unreachability, but worth
closing now since it is a one-line change and the class of bug it forecloses
(a silently dropped page break) is otherwise hard to detect in review.

## Info

### IN-01: `visit_field_list`'s `list_item_needs_separator = False` reset has no observable effect and diverges from the sibling block-visitor idiom without a stated reason

**File:** `typsphinx/translator.py:5566-5569`
**Issue:** After emitting the leading separator, `visit_field_list` resets
the flag it just consumed:

```python
if self.in_list_item and self.list_item_needs_separator:
    self.add_text("\n")
    self.list_item_needs_separator = False
self.add_text(f"pad(left: {SHARED_INDENT_STEP}, {{")
```

Every sibling block visitor with the identical leading-guard shape
(`visit_block_quote`, `visit_desc_content`) does **not** reset the flag
after consuming it — it is simply left as-is and unconditionally
overwritten to `True` again in the matching `depart_*` when
`in_list_item`. Tracing every consumer of `list_item_needs_separator`
inside a `field_list` subtree (`visit_field`, `visit_field_name`,
`visit_field_body`, and the shared `_emit_inline_concat_separator`/
`_emit_signature_leaf_wrapper`/`_emit_field_body_monospace_leaf` helpers)
confirms none of them read the flag while a field-body concat context is
active (`_emit_inline_concat_separator` short-circuits the fallback check
whenever `_in_field_body` is set), so this reset is inert: removing it
would produce byte-identical output for every construct exercised by the
suite. It is not a bug, but the divergence from the established pattern
with no accompanying rationale is worth a maintainer's second look — it
reads as though it was meant to prevent something that the
`_inline_concat_context` machinery already prevents by a different route.

**Fix:** Either remove the reset to match the `block_quote`/`desc_content`
precedent (byte-identical output, verified by tracing all consumers), or
add a one-line comment explaining what future case it is defending against
if one is actually intended.

---

_Reviewed: 2026-08-01T14:59:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
