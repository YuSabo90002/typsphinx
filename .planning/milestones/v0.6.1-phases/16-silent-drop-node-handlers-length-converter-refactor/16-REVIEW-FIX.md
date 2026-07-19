---
phase: 16-silent-drop-node-handlers-length-converter-refactor
fixed_at: 2026-07-16T13:45:00Z
review_path: .planning/phases/16-silent-drop-node-handlers-length-converter-refactor/16-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 2
skipped: 1
status: partial
---

# Phase 16: Code Review Fix Report

**Fixed at:** 2026-07-16T13:45:00Z
**Source review:** .planning/phases/16-silent-drop-node-handlers-length-converter-refactor/16-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope (critical_warning): 3 (CR-01, WR-01, WR-02)
- Fixed: 2
- Skipped: 1

## Fixed Issues

### CR-01: `:figwidth:` figure inside a list item aborts the whole Typst compile

**Files modified:** `typsphinx/translator.py`, `tests/fixtures/figure_length_render_gate/index.rst`, `tests/test_pdf_render_gate.py`
**Commit:** ef17c69
**Applied fix:** Added the same in-list-item leading-separator check every
other block-level visitor in `translator.py` uses (`visit_table`,
`visit_bullet_list`, `visit_enumerated_list`, `_visit_admonition`) to the
top of `visit_figure` — a `"\n"` is now emitted before the opening
`block(width: ...)[#figure(` / `[#figure(` / `figure(` call whenever
`self.in_list_item and self.list_item_needs_separator`, and
`list_item_needs_separator` is cleared immediately after. `depart_figure`
now also sets `self.list_item_needs_separator = True` when
`self.in_list_item`, mirroring `depart_table`'s trailing-block marking, so
a subsequent sibling in the same list item stays correctly separated.

Added a regression test,
`TestFigureFigwidthRenderGate::test_figwidth_figure_as_list_item_non_first_element_compiles`,
which extends the `figure_length_render_gate` fixture with a bullet-list
item whose second element is a `:figwidth: 40%` figure
(`FIGURELISTSENTINEL2R6`). The test asserts (via regex on the generated
`.typ` source) that a newline separates the preceding list-item text from
`block(width: 40%)[#figure(`, and then performs a real, un-caught
`typst.compile()` call. Verified the test fails with the exact reviewer-
reported symptom (`assert ... not in typ_source` catching the juxtaposed
`FIGURELISTSENTINEL2R6:")block(width: 40%)[#figure(` shape) when run
against the pre-fix `translator.py` via a temporary `git stash`, and
passes cleanly with the fix restored.

**Verification:** `black --check`, `ruff check`, `mypy typsphinx/translator.py`
all clean; `pytest -m "not slow"` (477 tests) and the full
`tests/test_pdf_render_gate.py` suite (24 tests, real `typst.compile()`
calls) all pass.

### WR-01: No render-gate coverage for the figwidth-without-caption `depart_figure` branch

**Files modified:** `tests/fixtures/figure_length_render_gate/index.rst`, `tests/test_pdf_render_gate.py`
**Commit:** 0286b79
**Applied fix:** Added a captionless `:figwidth: 60%` figure to the
`figure_length_render_gate` fixture (no caption paragraph, so docutils
assigns it no `ids`, forcing `depart_figure`'s `elif
self._figure_block_width is not None:` no-label branch — previously
unreached by any fixture case). Extended
`TestFigureFigwidthRenderGate::test_figwidth_pdf_wraps_block_and_compiles`
with an assertion that the generated source contains the exact no-label
shape `block(width: 60%)[#figure(\n  image("image.png")\n)]` (no trailing
`<label>`), reusing the test's existing real `typst.compile()` call to
prove it also compiles.

**Verification:** `black --check`, `ruff check` clean; the extended test
and the full `tests/test_pdf_render_gate.py` suite pass.

## Skipped Issues

### WR-02: `visit_todo_node`/`visit_manpage` type hints avoid importing their real node classes, weakening static checking

**File:** `typsphinx/translator.py:3854, 3882` (pre-fix line numbers; shifted by +20 after the CR-01 edit)
**Reason:** The review's own Fix section states "No action required" — this
is an intentional, documented design trade-off (avoiding an import of
`sphinx.ext.todo.todo_node` to keep the handler independent of that
optional extension), not a functional bug. The review explicitly defers
any tightening to a future maintainer decision about whether importing
`sphinx.ext.todo` is judged safe. No code change applied.
**Original issue:** `visit_todo_node`/`depart_todo_node` are typed as
`node: nodes.Element` rather than the precise `sphinx.ext.todo.todo_node`
type that `visit_manpage`/`depart_manpage` use for their own real node
class (`addnodes.manpage`), so mypy cannot catch a future typo like
`node.get("nonexistent_attr")` on the todo handlers. Legitimate
inconsistency, but explicitly non-blocking per the reviewer.

---

_Fixed: 2026-07-16T13:45:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
