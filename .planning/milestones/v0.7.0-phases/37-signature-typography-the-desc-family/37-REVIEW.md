---
phase: 37-signature-typography-the-desc-family
reviewed: 2026-08-01T00:00:00Z
depth: standard
files_reviewed: 21
files_reviewed_list:
  - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
  - tests/fixtures/inline_math_pdf_text_mitex.golden.txt
  - tests/fixtures/inline_math_pdf_text_native.golden.txt
  - tests/fixtures/signature_break_and_arrow_gate/conf.py
  - tests/fixtures/signature_break_and_arrow_gate/index.rst
  - tests/fixtures/signature_overflow_render_gate/conf.py
  - tests/fixtures/signature_overflow_render_gate/index.rst
  - tests/fixtures/signature_page_boundary_render_gate/conf.py
  - tests/fixtures/signature_page_boundary_render_gate/index.rst
  - tests/fixtures/signature_typography_gate/conf.py
  - tests/fixtures/signature_typography_gate/index.rst
  - tests/test_desc_sig_space_render_gate.py
  - tests/test_desc_signature_concat_render_gate.py
  - tests/test_pdf_render_gate.py
  - tests/test_rubric_option_concat_render_gate.py
  - tests/test_signature_break_and_arrow_gate.py
  - tests/test_signature_overflow_render_gate.py
  - tests/test_signature_page_boundary_render_gate.py
  - tests/test_signature_typography_gate.py
  - tests/test_translator.py
  - typsphinx/translator.py
findings:
  critical: 0
  warning: 1
  info: 4
  total: 5
status: issues_found
---

# Phase 37: Code Review Report

**Reviewed:** 2026-08-01T00:00:00Z
**Depth:** standard
**Files Reviewed:** 21
**Status:** issues_found

## Summary

Reviewed the `desc_*` emission-surface diff in `typsphinx/translator.py` (the new
`in_signature_text` monospace-propagation flag, `_param_name_seen` D-05
discriminator, the `_desc_break_marker` SIG-08 emission-position marker, the
`_emit_signature_leaf_wrapper`/`_escape_signature_text` helpers, and the
delimiter/arrow/optional-group changes) plus every new and updated fixture/test
module for Phase 37.

No critical/blocker-level defect was found. The two areas the review brief
called out as highest-risk both check out under close reading:

- **Escaping/ZWSP order** (`_escape_signature_text`, `typsphinx/translator.py:69-96`):
  escaping runs first via the shared, unmodified `escape_typst_string`, and the
  `\u{200B}` break-opportunity token is injected only afterward, as a literal
  8-character escape sequence rather than a raw invisible byte. Verified there
  is exactly one call path (`visit_Text`'s `in_signature_text` branch and
  `_emit_signature_leaf_wrapper`) so no second escaping helper was introduced.
- **Cross-reference preservation**: every new leaf-emission shortcut
  (`visit_desc_name`, `visit_desc_annotation`, `visit_desc_sig_name` rules 1/2)
  guards with `all(isinstance(child, nodes.Text) for child in node.children)`
  before flattening via `node.astext()` — a subtree containing a `reference`
  fails that check and correctly falls through to per-child dispatch, so
  `visit_reference`'s unmodified `link(...)` wrapping is never bypassed.

The one substantive finding is a genuine, provable robustness gap in the new
`_desc_break_marker` (SIG-08) state machine: it is only proven sound against
`self.in_table`, but every *other* place the translator swap-buffers
`self.body` (most notably `visit_definition`/`depart_definition`) has the
identical hazard and is not guarded at all. See WR-01 for the concrete trace.
The remaining items are lower-severity code-quality/defensive-coding notes.

## Warnings

### WR-01: `_desc_break_marker` (SIG-08) is only proven sound against tables; every other `self.body` buffer-swap has the same unguarded hazard

**File:** `typsphinx/translator.py:4798-4854` (guard also relevant:
`typsphinx/translator.py:2197-2245`, `visit_definition`/`depart_definition`)

**Issue:** `depart_desc`'s new emission-position marker suppresses a
redundant `parbreak()` when `self._desc_break_marker == len(self.body)`,
i.e. "nothing was appended to `self.body` since the last `desc`'s own
break". The implementation explicitly reasons about — and guards against —
exactly one case where this invariant is unsound: table cells, where
`add_text` redirects into `self.table_cell_content` instead of `self.body`
(`not self.in_table` guard at line 4851, documented at lines 4845-4849).

But `self.body` is buffer-swapped at several *other* sites in this same
file, none of which are guarded the same way:

- `visit_definition`/`depart_definition` (`typsphinx/translator.py:2197`,
  `2221`): `self.body = self.current_definition_buffer` for the duration of
  a definition-list `definition` node, which — unlike a table cell — is a
  real body element that can legally contain arbitrary block content,
  including an object-description directive (e.g. a glossary definition
  containing a nested `.. py:function::`).
- The definition/term buffer-swap (`typsphinx/translator.py:2152`), the
  admonition-title buffer-swap (`:652`), and the figure-caption buffer-swap
  (`:2384`/`:2416`) are the same pattern, though titles/captions are
  inline-only in practice and so are not realistic vectors for a nested
  `desc`.

Concretely: if a `desc` node is nested inside a `definition`, its
`depart_desc` call executes with `self.in_table` False, so it takes the
*normal* (non-table) branch and both reads and writes
`self._desc_break_marker` against `len(self.current_definition_buffer)` —
a small, buffer-local length that has nothing to do with the real
document's `self.body`. Once `depart_definition` restores
`self.body = self._saved_body_stack.pop()`, `_desc_break_marker` keeps
holding that small, stale buffer-relative value. If any *later*,
unrelated, non-nested top-level `desc` happens to depart at a point where
`len(self.body)` (the real body, now potentially thousands of elements
long) coincidentally equals that stale value, its own legitimate
`parbreak()` is silently swallowed — the exact "flag that fails to reset
corrupts a later node" failure mode.

In practice an exact `len()` collision after the swap is very unlikely
(the table case does not suffer this in practice either, because
`depart_table` always appends the whole table structure to `self.body` in
one shot before the next node is reached) — this is why the finding is a
WARNING rather than a demonstrated failure — but the *design* is unsound:
`_desc_break_marker` is silently written and read across a buffer swap it
was never reasoned about, whereas the table case is the one buffer-swap
site the implementation actually thought through and guarded.

**Fix:** Either (a) generalize the existing guard to
`if identity_of(self.body) is main_body and marker == len(self.body): return`
by keeping a reference to the true top-level body list (e.g.
`self._main_body`) set once in `__init__` and comparing identity rather
than just length, or (b) explicitly invalidate the marker
(`self._desc_break_marker = None`) on every entry into a `self.body`
buffer-swap (`visit_definition`, `visit_caption`, the admonition-title
swap), mirroring how `_strong_was_*` attributes are saved/restored around
scope changes elsewhere in this file.

## Info

### IN-01: SIG-08 duplicate-`parbreak()` suppression is fully disabled — not merely reasoned-about — for any `desc` nested inside a table cell

**File:** `typsphinx/translator.py:4851`

**Issue:** `if not self.in_table and self._desc_break_marker == len(self.body): return` means that whenever `self.in_table` is True, the SIG-08 fix's suppression never fires at all — every `desc` departure inside a table cell reverts to the pre-Phase-37 unconditional-`parbreak()`-per-`desc` behaviour, including the doubled-break case the fix exists to remove (a nested `py:class::`/`py:method::` pair inside a table cell would still emit two adjacent `parbreak()` tokens). This is explicitly documented as intentional ("retains the pre-phase unconditional behaviour inside tables") and is a defensible scoping decision, not a hidden defect — but it does mean SIG-08 is not actually fixed for a plausible document shape (a Napoleon/parameter-table cell containing a nested object description). Flagging for visibility/tracking rather than requesting a fix in this phase.

**Fix:** No action required for this phase; consider filing a follow-up todo noting SIG-08 inside table cells is an explicitly out-of-scope, still-reproducible case, so a future table-content phase does not assume it was covered here.

### IN-02: Leaf-detection via `all()` is vacuously true for a childless node, so an anomalous empty `desc_name`/`desc_annotation`/`desc_sig_name` emits `strong(raw(""))`/`emph(raw(""))` instead of contributing zero bytes

**File:** `typsphinx/translator.py:98-128` (`_emit_signature_leaf_wrapper`), call sites at `typsphinx/translator.py` `visit_desc_annotation`, `visit_desc_name`, `visit_desc_sig_name`

**Issue:** All three call sites guard with `all(isinstance(child, nodes.Text) for child in node.children)`. Python's `all()` over an empty iterable returns `True`, so a node with **zero** children is treated as a text-only leaf and unconditionally emits a wrapped empty string (`strong(raw(""))` / `emph(raw(""))`) via `node.astext()` (which is `""` for no children). Contrast with `visit_desc_addname`, which is a deliberate no-op specifically so an empty `desc_addname` "must contribute zero bytes" (SIG-02, tested by `test_sig02_empty_addname_emits_zero_bytes`). If any domain ever produces an empty `desc_name`/`desc_annotation`/leaf-eligible `desc_sig_name` (not observed in the fixtures reviewed here, but not structurally impossible), this diverges from the "empty contributes zero bytes" convention established elsewhere in the same emission surface — it would still be valid Typst (a harmless empty `raw("")` expression), so this is a low-severity defensive-coding gap rather than a rendering defect.

**Fix:** Guard the three call sites with `node.children and all(...)` (or check `node.astext()` for truthiness before calling `_emit_signature_leaf_wrapper`) to mirror `visit_desc_addname`'s explicit "empty is zero bytes" contract.

### IN-03: `EXPECTED_PAGE_COUNT_PRE_PHASE` holds a post-phase value

**File:** `tests/test_signature_page_boundary_render_gate.py:109`

**Issue:** The constant name says "pre-phase" but its value (7) is the post-Wave-3, corrected-wrapper page count; the in-file comment explains the amendment in full and the constant is not silently wrong — but the name itself is now misleading to a future reader who does not read the surrounding comment. Per the phase context this is already filed as a known todo, so no action is requested here — noting it for completeness of the review record only.

**Fix:** Rename to something like `EXPECTED_PAGE_COUNT_CEILING` or `PINNED_PAGE_COUNT` in the already-filed follow-up todo; no change requested in this review.

### IN-04: `visit_desc_sig_name`'s two rules are independent `if` statements whose mutual exclusion is enforced only by `raise nodes.SkipNode`, not by control-flow structure

**File:** `typsphinx/translator.py:5636-5698` (`visit_desc_sig_name`)

**Issue:** Rule 1 (`parent is desc_annotation/desc_name` + leaf) and Rule 2 (`parent is desc_parameter` + leaf + `not self._param_name_seen`) are written as two sequential `if` blocks rather than `if`/`elif`. They are safe today only because a node has exactly one parent (so the two `isinstance(parent, ...)` conditions are naturally mutually exclusive) and because `_emit_signature_leaf_wrapper` unconditionally raises `nodes.SkipNode`, so the second `if` is never reached once the first fires. This is correct as written, but the safety property is implicit (an exception aborting the function) rather than structurally guaranteed — a future edit that changes `_emit_signature_leaf_wrapper` to not raise (e.g. to support a non-terminal use) would silently allow both wrapper calls to fire for the same node.

**Fix:** Optional: convert to `if ...: ...; elif ...: ...` (or add a comment at the top of the function noting the SkipNode dependency explicitly, which is already partially done in the docstring) to make the mutual exclusion structurally obvious rather than exception-dependent. Not required before shipping.

---

_Reviewed: 2026-08-01T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
