---
phase: 42-captioned-table-drops-preceding-target-label
reviewed: 2026-08-03T15:08:03Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_captioned_table_propagated_target_render_gate.py
  - tests/test_figure_propagated_target_render_gate.py
  - tests/fixtures/captioned_table_propagated_target_render_gate/conf.py
  - tests/fixtures/captioned_table_propagated_target_render_gate/index.rst
  - tests/fixtures/figure_propagated_target_render_gate/conf.py
  - tests/fixtures/figure_propagated_target_render_gate/index.rst
  - CHANGELOG.md
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 42: Code Review Report

**Reviewed:** 2026-08-03T15:08:03Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the single call-site change in `depart_table` (`typsphinx/translator.py`) that moves the
propagated-remainder-id `_emit_id_anchors` call to fire after `self.in_table` is cleared, plus the
two new render-gate test modules and their fixtures, plus the CHANGELOG entry.

I did not just read the diff — I reproduced the bug and the fix empirically:

- Built a throwaway git worktree at the pre-fix commit (`19a6378`), copied the new test file and
  fixture onto it, and ran the table gate: 7 of 9 tests failed with the exact fatal the phase
  describes (`TypstError: label \`<index:tbl-target>\` does not exist in the document`). Confirms
  the RED state is real, not asserted-into-existence.
- Ran both new gate suites against the current (fixed) tree: 16/16 pass, including a real
  `typst.compile()` to a valid `%PDF`-prefixed PDF for every shape (A/B/C/D + 3 figure shapes).
- Ran the full test suite (`793 passed, 29 deselected`), `ruff check`, `black --check`, and `mypy`
  on the changed files — all clean.
- Manually inspected the emitted `.typ` for the "two consecutive targets" shape (D) to confirm
  `ids[0]` really is the `:name:`-derived id (not one of the two propagated target ids), which is
  what makes `skip_ids=set(node.get("ids", [])[:1])` correct rather than accidentally swallowing
  one of the two propagated anchors the test checks for.
- Verified `was_captioned = self.table_colcount > 0 and bool(self.table_caption)` is a byte-exact
  reproduction of the guard the removed call sat inside (`if self.table_colcount > 0: ... if
  self.table_caption: ... <call>`), by diffing against the pre-move source directly.
- Confirmed (against both the pre-fix and post-fix trees) that a table nested inside a
  `list-table` cell already silently drops the *entire* outer table structure, independent of
  this diff (see IN-02 below; scoped as pre-existing, not attributable to Phase 42).

The fix itself is correct and well-verified. Findings below are secondary: one stale docstring
this phase's own change makes more misleading, one dead test fixture, and one pre-existing
(unrelated to this diff) nested-table data-loss bug surfaced while specifically chasing the
review prompt's "consider nested tables" instruction.

## Warnings

### WR-01: `_emit_id_anchors`'s docstring claims a "sole user" that has been wrong since Phase 25, and this phase's own extensive commenting elsewhere didn't fix it

**File:** `typsphinx/translator.py:515-523`
**Issue:** The docstring for the `skip_ids` parameter of `_emit_id_anchors` states:

> `skip_ids` lets a caller that ALREADY anchors one of the node's ids by another mechanism
> suppress a duplicate definition here. **The sole user is `depart_figure`**: a captioned figure
> self-anchors `ids[0]` inside its own `[#figure(...) <label>]` markup block, but a PROPAGATED
> explicit target lands a DIFFERENT id in `ids[1:]`...

This was already factually inaccurate before Phase 42: `depart_table` has called
`_emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` with the identical pattern since
Phase 25/TBL-02 (visible in the pre-fix source at `19a6378:typsphinx/translator.py:3336`). Phase
42 is entirely *about* that second call site — it moves it, adds ~25 lines of new commentary
around it (lines 3344-3370), and the new test suites in this same diff exist specifically to prove
it now works — yet the shared helper's own docstring, sitting a few thousand lines away, still
tells the next reader there is only one caller. A future maintainer who trusts this docstring and
"simplifies" `_emit_id_anchors` on the assumption `depart_figure` is the only caller of the
`skip_ids` path risks silently breaking `depart_table`'s propagated-target anchoring again — the
exact class of bug this phase just spent a whole plan fixing.

**Fix:**
```python
``skip_ids`` lets a caller that ALREADY anchors one of the node's ids
by another mechanism suppress a duplicate definition here. Two callers
use it today: ``depart_figure`` and ``depart_table`` (TBL-02/TBL-03) --
both self-anchor ``ids[0]`` inside their own figure-wrap ``<label>``
postfix, and both pass ``skip_ids={ids[0]}`` here to anchor only a
PROPAGATED remainder id landing in ``ids[1:]``. When every id is
skipped the method is a no-op (list-item bookkeeping is untouched),
keeping output byte-for-byte identical.
```

## Info

### IN-01: Unused pytest fixture `captioned_table_propagated_target_render_gate_dir`

**File:** `tests/test_captioned_table_propagated_target_render_gate.py:48-55`
**Issue:** This module-scoped fixture is defined but never referenced by any test method or other
fixture in the file — the class-scoped `captioned_table_propagated_target_artifacts` fixture
(lines 106-123) independently re-derives the identical `Path(__file__).parent / "fixtures" /
"captioned_table_propagated_target_render_gate"` expression instead of depending on it. Dead code;
duplicated path-construction logic that could drift if one copy is edited and the other isn't
(neither currently is used for anything besides the copy at line 113-117, so today they happen to
agree, but nothing enforces that).
**Fix:** Either delete the unused fixture, or have `captioned_table_propagated_target_artifacts`
take it as a parameter and reuse `source_dir = captioned_table_propagated_target_render_gate_dir`
instead of restating the path.

### IN-02: Nested `table` inside a `list-table` cell silently drops the entire outer table (pre-existing, not caused by this diff)

**File:** `typsphinx/translator.py:3149-3394` (`visit_table`/`depart_table`), `423-437` (`add_text`)
**Issue:** Surfaced while specifically investigating the review prompt's "consider nested tables"
instruction. `self.in_table`/`self.table_cell_content` are scalar translator attributes, not a
stack. When a `.. table::`/`.. list-table::` is nested inside a `list-table` cell, the inner
table's `depart_table` unconditionally does `self.in_table = False` and `del
self.table_cell_content`, clobbering the OUTER table's in-progress state. Empirically reproduced
(both pre-fix commit `19a6378` and the current tree, byte-identical output on both — confirming
this is not something Phase 42 introduced or worsened): a `list-table` with a nested `list-table`
in one cell emits the inner table correctly but the OUTER table's own `table(...)` wrapper and its
other cells (e.g. the header row text) vanish from the output entirely, with no warning or error —
silent structural data loss, not merely a cosmetic issue.
**Fix:** Out of scope for this phase (this diff only moved one call site within `depart_table` and
did not touch table-nesting state). Flagging for a future phase: convert `self.in_table` /
`self.table_cell_content` into a stack (e.g. `self._table_stack: list[TableState]`) so a nested
table's `depart_table` restores rather than clobbers the enclosing table's in-progress state.

---

_Reviewed: 2026-08-03T15:08:03Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
