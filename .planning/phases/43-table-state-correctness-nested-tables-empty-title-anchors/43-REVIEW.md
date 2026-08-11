---
phase: 43-table-state-correctness-nested-tables-empty-title-anchors
reviewed: 2026-08-04T01:36:27Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_nested_table_render_gate.py
  - tests/test_nested_figure_render_gate.py
  - tests/test_table_empty_caption_anchor_render_gate.py
  - tests/fixtures/nested_table_render_gate/conf.py
  - tests/fixtures/nested_table_render_gate/index.rst
  - tests/fixtures/nested_figure_render_gate/conf.py
  - tests/fixtures/nested_figure_render_gate/index.rst
  - tests/fixtures/table_empty_caption_anchor_render_gate/conf.py
  - tests/fixtures/table_empty_caption_anchor_render_gate/index.rst
findings:
  critical: 1
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 43: Code Review Report

**Reviewed:** 2026-08-04T01:36:27Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the TBL-04 (nested-table state stack), FIG-01 (nested-figure state
stack + `visit_legend`/`depart_legend`), and TBL-05 (structural vs. rendered
caption anchoring split) changes in `typsphinx/translator.py`, plus the three
new render-gate test files and their fixtures.

`_push_table_state`/`_pop_table_state` and `_push_figure_state`/
`_pop_figure_state` are both correctly guarded against popping an empty
stack, and I traced push/pop symmetry through 2-level and 3-level nesting
for both tables and figures (including `current_morecols`/
`current_morerows`, `in_thead`, and the new `_table_is_captioned` snapshot
entry) without finding a leak in either stack itself. I empirically verified
(by reverting `typsphinx/translator.py` to the pre-phase commit while
keeping the new tests/fixtures, in a throwaway git worktree) that all three
new gate test files genuinely fail against the unfixed translator and pass
against the current one — these are real regression gates, not tautologies.

However, the two new `visit_legend`/`depart_legend` methods (FIG-01) do
**not** join either state stack. They save the pre-existing
`in_list_item`/`list_item_needs_separator` flags into flat, non-stacked
instance attributes (`_legend_saved_in_list_item`/
`_legend_saved_list_item_needs_separator`) — exactly the anti-pattern
`_push_table_state`/`_push_figure_state` were written this same phase to
eliminate, and that the codebase already solves correctly elsewhere via a
real stack (`self._list_item_stack`, used by `visit_list_item`). A figure
whose legend contains a nested figure that *itself* has a legend clobbers
these two attributes, leaking `in_list_item = True` into every subsequent
sibling in the document after the outer figure closes — a real, empirically
reproduced output-correctness bug (CR-01 below). A related warning:
none of the three new test suites exercise this double-nesting shape, so
the gate that should have caught it doesn't.

## Critical Issues

### CR-01: `visit_legend`/`depart_legend` use non-stacked save/restore, leaking `in_list_item` state past a doubly-nested figure

**File:** `typsphinx/translator.py:2697-2750` (`visit_legend`/`depart_legend`)

**Issue:** `visit_legend` saves `self.in_list_item` /
`self.list_item_needs_separator` into flat instance attributes
(`self._legend_saved_in_list_item` / `self._legend_saved_list_item_needs_separator`,
lines 2731-2732) before forcing both to `True`, and `depart_legend` restores
them from those same flat attributes (lines 2748-2749). This is the exact
clobber shape `_push_table_state`/`_push_figure_state` were added this phase
to fix, but `visit_legend`/`depart_legend` were never wired into either
stack (`_push_figure_state`'s own docstring, `typsphinx/translator.py:3383-3395`,
enumerates the scalar set it covers and `visit_legend`'s state is not among
them).

A figure `A` with a legend `L1` that contains a nested figure `B` which
*itself* has a caption + legend `L2` (fully legal RST — a `.. figure::`
directive's legend is arbitrary body content, and the existing
`nested_figure_render_gate` fixture already proves single-level figure-in-
legend nesting works) reproduces the leak:

1. `visit_legend(L1)` saves `_legend_saved_in_list_item = <value before A>`
   (e.g. `False` for a top-level figure) and forces
   `in_list_item = True`.
2. `visit_figure(B)` correctly pushes/resets via `_push_figure_state`
   (that stack is fine).
3. `visit_legend(L2)` **overwrites** `_legend_saved_in_list_item` with the
   *current* value, which is `True` (L1's own forced value) — not the
   original pre-`A` value.
4. `depart_legend(L2)` restores `in_list_item = True` (harmless here, since
   L1 still wants `True`).
5. `depart_legend(L1)` restores `in_list_item` from
   `self._legend_saved_in_list_item`, which step 3 clobbered — so it
   restores `True` instead of the true original value, permanently leaking
   `in_list_item = True` (and `list_item_needs_separator = True`) into
   every sibling that follows figure `A` for the rest of the document.

I reproduced this concretely with a minimal fixture (figure A: caption
`OUTERCAP`, legend containing figure B: caption `INNERCAP` + legend text
`INNERLEGENDTEXT`, followed by a top-level paragraph `After Paragraph`).
Building with `-b typst`:

- Control (single-level nesting, inner figure has no legend of its own):
  `After Paragraph` emits correctly as `par({text("After Paragraph")})`.
- Double-nested-legend case above: `After Paragraph` incorrectly emits as
  `parbreak()\n\ntext("After Paragraph")` — the leaked `in_list_item=True`
  routes it through the list-item/legend paragraph path instead of the
  normal top-level paragraph path. Every subsequent block-level sibling in
  the document is affected for the remainder of the build (the leak is
  never cleared by anything downstream — a genuine bullet list further down
  would even push/pop `self._list_item_stack` on top of the already-wrong
  `True`, perpetuating it after that list closes too).

This is silent, incorrect Typst output for content that has nothing to do
with the figure/legend that caused it — no compile fatal, no warning,
just wrong document structure from that point forward.

**Fix:** Give `visit_legend`/`depart_legend` their own real stack, mirroring
`self._list_item_stack` (already used by `visit_list_item`/`depart_list_item`,
`typsphinx/translator.py:1947-1991`) instead of flat scalars:

```python
# in __init__, alongside self._list_item_stack:
self._legend_list_item_stack: List[Tuple[bool, bool]] = []

def visit_legend(self, node: nodes.legend) -> None:
    self._legend_list_item_stack.append(
        (self.in_list_item, self.list_item_needs_separator)
    )
    self.in_list_item = True
    self.list_item_needs_separator = True

def depart_legend(self, node: nodes.legend) -> None:
    self.add_text("\n}")
    if self._legend_list_item_stack:
        self.in_list_item, self.list_item_needs_separator = (
            self._legend_list_item_stack.pop()
        )
```

Also add a regression fixture/test covering a figure whose legend contains
a nested figure that itself has a legend (two legend levels), asserting
that content *after* the outer figure renders via the normal top-level
paragraph path (`par({...})`), not the list-item path
(`parbreak()`/bare `text(...)`) — none of the three new gate suites in this
phase currently exercise this shape (see WR-01).

## Warnings

### WR-01: No regression test for legend-in-legend (double-nested-figure) shape

**File:** `tests/test_nested_figure_render_gate.py`,
`tests/fixtures/nested_figure_render_gate/index.rst`

**Issue:** The `nested_figure_render_gate` fixture covers a figure nested in
another figure's legend (Section 1), a plain-text legend with no nesting
(Section 2), an image-only control (Section 3), and a legend with no caption
(Section 4) — but never a figure whose legend contains a nested figure that
*itself* has a legend. That is exactly the shape that triggers CR-01, and
because it's untested, the render gate this phase added to prevent FIG-01
regressions does not detect FIG-01's own incomplete fix.

**Fix:** Add a "Section 5" to the fixture nesting a legend inside a legend
(outer figure -> legend -> inner figure with its own caption + legend), and
assert (a) the build still exits 0, (b) a plain paragraph placed
immediately after the outer figure's directive block renders as
`par({text(...)})` rather than a `parbreak()`-prefixed form, proving
`in_list_item` was correctly restored to its pre-figure value.

---

_Reviewed: 2026-08-04T01:36:27Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
