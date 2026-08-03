# Phase 42 Gate Evidence 02 — SC#2 (Figure-side answer + permanent gate)

**Plan:** 42-02
**Worktree:** `agent-a310b732ec039ba7f` (base `19a6378e6b12ec086e3e3af11f93e736a30c0cb3`)
**Date:** 2026-08-03

## 1. THE QUESTION

`.planning/ROADMAP.md` § Phase 42, success criterion 2, quoted verbatim:

> Whether captioned figures exhibit the same drop is answered either way, with
> the measurement recorded.

**Answer, up front:** Captioned figures do **NOT** exhibit the propagated-target
drop. A captioned figure immediately preceded by a standalone target emits
BOTH its own self-anchor and the propagated target's anchor, and the document
compiles cleanly. The measurement backing this answer is recorded below, taken
in this worktree, not transcribed from `42-RESEARCH.md` or `42-CONTEXT.md`.

## 2. THE MEASUREMENT

Command actually run in this worktree:

```
$ uv run python -m sphinx -b typstpdf -q -E tests/fixtures/figure_propagated_target_render_gate <build-dir>
```

**Exit status:** `0`

**stdout:** empty (no output was printed — the `-q` flag suppresses Sphinx's
normal build-progress output, and no error occurred).

**stderr:** empty. In particular:

```
$ grep -c "does not exist in the document" <stderr-capture>
0
$ grep -c "Typst compilation failed" <stderr-capture>
0
```

Neither the dangling-label fatal (`label ... does not exist in the document`)
nor a general Typst compilation failure was reported.

### Emitted `.typ` excerpts, one per D-10 shape

D-10 shape 1 — a `:name:`-carrying figure with a preceding target
(`.. _fig-target:` then `.. figure:: image.png` `:name: fig-name`).
Both the figure's own self-anchor postfix (carrying `ids[0]`, the
`:name:`-derived id) and the propagated target's `metadata(none)` anchor are
present:

```typst
[#figure(
  image("image.png"),
  caption: {text("Caption with sentinel FIGTGTNAMEDSENTINEL present.")}
) <index:fig-name>]


[#metadata(none) <index:fig-target>]
```

D-10 shape 2 — a figure with no `:name:` option and a preceding target
(`.. _fig-target-noname:` then a bare `.. figure:: image.png`). The
figure self-anchors on docutils' own auto-generated id (`index:id1` in this
build — its exact spelling is not asserted anywhere, per the plan's
`planner_assumptions`), and the propagated target's anchor is present:

```typst
[#figure(
  image("image.png"),
  caption: {text("Caption with sentinel FIGTGTNONAMESENTINEL present.")}
) <index:id1>]


[#metadata(none) <index:fig-target-noname>]
```

D-10 shape 3 — a `:name:`-carrying figure inside a bullet-list item, preceded
by a target inside the same list item
(`.. _fig-target-li:` then `.. figure:: image.png` `:name: fig-name-li`).
Both anchor forms are present and the in-list-item bookkeeping does not
interfere with either:

```typst
list({
parbreak()

text("Lead-in text for the list item.")

[#figure(
  image("image.png"),
  caption: {text("Caption with sentinel FIGTGTLISTSENTINEL present.")}
) <index:fig-name-li>]



[#metadata(none) <index:fig-target-li>]

})
```

### Produced PDF

```
$ ls -la <build-dir>/index.pdf
-rw-r--r-- 1 yuta users 44381  8月  3 23:23 <build-dir>/index.pdf
$ python3 -c "print(open('<build-dir>/index.pdf','rb').read(4))"
b'%PDF'
```

`index.pdf` size: **44381 bytes**. First four bytes: **`%PDF`** — a valid PDF
was produced; the compile did not abort.

## 3. THE CODE-LEVEL REASON

Re-derived here from the live tree in this worktree (`typsphinx/translator.py`,
line numbers as observed in this build, not copied from any other document).

`add_text` (lines 423–437):

```python
def add_text(self, text: str) -> None:
    """
    Add text to the output body or table cell content.

    Args:
        text: The text to add
    """
    if (
        hasattr(self, "in_table")
        and self.in_table
        and hasattr(self, "table_cell_content")
    ):
        self.table_cell_content.append(text)
    else:
        self.body.append(text)
```

`self.in_table` is the **only** flag this method consults. There is no
`self.in_figure` branch anywhere in `add_text` — a call made while
`self.in_figure` is `True` (or `False`) is routed identically, straight to
`self.body`, unless `self.in_table` happens to also be set (which it is not,
inside `depart_figure`).

`depart_figure`'s trailing anchor call, together with the line that clears
`self.in_figure` (lines 2513–2522):

```python
        # A captioned figure self-anchors ONLY ids[0] (its own caption/numref
        # id) in the ``) <label>]`` postfix above. A PROPAGATED explicit target
        # (``.. _t:`` before ``.. figure::``) lands a DIFFERENT id in ids[1:]
        # that would otherwise dangle -- anchor the remainder, skipping ids[0]
        # so it is not defined twice. Empty/single-id figures -> no-op.
        self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))

        self._figure_block_width = None

        self.in_figure = False
        self.figure_content = []
        self.figure_caption = ""
```

This ordering — `_emit_id_anchors` fires at line 2518, `self.in_figure = False`
does not run until line 2522 — superficially matches `depart_table`'s ordering,
where the analogous `_emit_id_anchors` call (line 3341) also fires before
`self.in_table = False` (line 3351). On the table side that ordering is the
root cause of TBL-03: `_emit_id_anchors` calls `self.add_text` internally,
and while `self.in_table` is still `True`, `add_text` diverts the anchor into
`self.table_cell_content` — a buffer that `depart_table` unconditionally
deletes a few lines later (`del self.table_cell_content`), so the anchor is
silently lost.

On the figure side this same ordering is **harmless**, precisely because
`add_text`'s only gating flag is `self.in_table`, which `depart_figure` never
touches. There is no `in_figure`-gated buffer for `_emit_id_anchors`'s
`add_text` calls to be diverted into — regardless of whether `self.in_figure`
is `True` or `False` at the moment `_emit_id_anchors` runs, the anchor lands
directly in `self.body`, exactly where the figure's own self-anchor postfix
(lines 2502–2504, immediately above) also lands.

## 4. THE PERMANENT GATE (D-09/D-10)

Module: `tests/test_figure_propagated_target_render_gate.py`
Class: `TestFigurePropagatedTargetRenderGate`

Seven test methods, each covering one behavior against a single class-scoped
`-b typstpdf` build of `tests/fixtures/figure_propagated_target_render_gate/`:

1. `test_typstpdf_build_compiles_without_dangling_label` — build exits 0, no
   dangling-label fatal, no compilation-failure log line.
2. `test_shape1_named_figure_with_preceding_target_emits_both_anchors` — D-10
   shape 1: `<index:fig-target>` propagated anchor AND `<index:fig-name>`
   self-anchor.
3. `test_shape2_unnamed_figure_with_preceding_target_emits_anchor` — D-10
   shape 2: `<index:fig-target-noname>` propagated anchor (no assertion on
   the docutils auto id).
4. `test_shape3_figure_in_list_item_emits_both_anchors` — D-10 shape 3:
   `<index:fig-target-li>` propagated anchor AND `<index:fig-name-li>`
   self-anchor.
5. `test_no_duplicate_index_label_definitions` — no `index:`-namespaced label
   is defined twice (negative-lookbehind-on-`link(` scan, `raw("...")`
   segments stripped first).
6. `test_no_dangling_same_document_references` — every `link(<name>, ...)`
   reference has a matching anchor.
7. `test_pdf_compiles_to_valid_pdf` — `index.pdf` exists, is non-empty, and
   starts with the `%PDF` magic bytes.

Verbatim passing output, this worktree, this session:

```
$ uv run pytest tests/test_figure_propagated_target_render_gate.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a310b732ec039ba7f
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 7 items

tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_typstpdf_build_compiles_without_dangling_label PASSED [ 14%]
tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_shape1_named_figure_with_preceding_target_emits_both_anchors PASSED [ 28%]
tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_shape2_unnamed_figure_with_preceding_target_emits_anchor PASSED [ 42%]
tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_shape3_figure_in_list_item_emits_both_anchors PASSED [ 57%]
tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_no_duplicate_index_label_definitions PASSED [ 71%]
tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_no_dangling_same_document_references PASSED [ 85%]
tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate::test_pdf_compiles_to_valid_pdf PASSED [100%]

============================== 7 passed in 0.32s ===============================
```

This gate is **green against UNFIXED production source** — this worktree's
base commit (`19a6378`) predates plan 42-04's table-side fix. The figure path
was already correct; this module is a forward-looking guard (D-09), not a
RED-to-GREEN recording.

## 5. SCOPE NOTE

`tests/fixtures/figure_target_caption_render_gate/` was deliberately **NOT**
reused as this gate's fixture source. Its figures carry the `:target:`
directive OPTION, which docutils wraps as a `reference` node around the
figure (a `visit_reference`/`depart_reference` code path) — a completely
different mechanism that never invokes `PropagateTargets`. Reusing it would
have produced a gate that appeared to cover D-10 while exercising none of
its three shapes.

The two-consecutive-targets shape (D-01's fourth measured-failing shape on
the table side) is deliberately **out of scope** for this figure gate — D-10
explicitly scopes the figure gate to the three shapes above; the fourth
shape was never measured for figures.

## 6. VERDICT

| Criterion | Status | Evidence |
|-----------|--------|----------|
| SC#2 (whether captioned figures share the drop, answered with a recorded measurement) | **MET** | Section 2 — answer NO, live in-repo measurement, not carried-over reference material. |
| D-09 (permanent figure regression gate exists, green against unfixed source) | **MET** | Section 4 — `TestFigurePropagatedTargetRenderGate`, 7/7 passing against this worktree's unfixed base. |
| D-10 (exactly the three measured shapes covered, no fourth) | **MET** | Section 4 — shapes 1–3 each have a dedicated test method; Section 5 records the deliberate fourth-shape exclusion. |
