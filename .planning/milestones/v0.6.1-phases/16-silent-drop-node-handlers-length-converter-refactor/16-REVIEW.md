---
phase: 16-silent-drop-node-handlers-length-converter-refactor
reviewed: 2026-07-16T13:09:44Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_pdf_render_gate.py
  - tests/test_corpus_gate.py
  - tests/fixtures/todo_render_gate/conf.py
  - tests/fixtures/todo_render_gate/index.rst
  - tests/fixtures/manpage_render_gate/conf.py
  - tests/fixtures/manpage_render_gate/index.rst
  - tests/fixtures/figure_length_render_gate/index.rst
  - tests/fixtures/table_width_render_gate/conf.py
  - tests/fixtures/table_width_render_gate/index.rst
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: issues_found
---

# Phase 16: Code Review Report

**Reviewed:** 2026-07-16T13:09:44Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the diff against `3b361bb..HEAD` for `typsphinx/translator.py` (new
`visit_todo_node`/`depart_todo_node`, new `visit_manpage`/`depart_manpage`
delegation, and the `_convert_length_to_typst` wiring into
`visit_figure`/`depart_figure` (`:figwidth:`) and `depart_table` (`:width:`)
via `block(width: ...)[...]` wrappers), plus the new/extended render-gate
tests and fixtures, and the intentionally-flipped `unknown_visit` catalogue
assertion in `tests/test_corpus_gate.py`.

`ruff`, `black --check`, and `mypy` are all clean on the changed files, and
the full fast suite (`pytest -m "not slow"`, 477 tests) and the new/extended
slow render-gate tests all pass. I additionally ran the real
`sphinx-build -b typst` → `typst.compile()` pipeline by hand against several
combinations not covered by the new fixtures (manpage in a table cell/term/
adjacent-paragraph context; todo/figure/table inside list items; figure with
`:figwidth:` and no caption). Most of these confirmed the new code is
correct and robust. One combination reproduces a real, verified Typst
compile-abort: **a `:figwidth:` figure that is a non-first element inside a
list item's content block** (see CR-01). This is the only correctness
BLOCKER found. The `test_corpus_gate.py` assertion flip was independently
re-validated by running the real (already-cloned) Sphinx `doc/` corpus
through the full pipeline — it passes, confirming the catalogue really is
empty post-fix. The `todo_node`/`manpage`/table-width changes themselves are
sound and well-tested; the gaps are in *figure* width-wrapper coverage.

## Critical Issues

### CR-01: `:figwidth:` figure inside a list item aborts the whole Typst compile

**File:** `typsphinx/translator.py:1945-1946`
**Issue:** The new LEN-01 `block(width: ...)[#figure(` emission in
`visit_figure` is added directly via `self.add_text(...)` with **no**
in-list-item separator check, unlike every other block-level construct in
this file (`visit_table`, `visit_bullet_list`, `visit_enumerated_list`,
`_visit_admonition` all explicitly emit a `"\n"` before their opening call
when `self.in_list_item and self.list_item_needs_separator`). When a
`:figwidth:`-carrying figure is *not* the first element inside a list
item's `{ ... }` content block, the emitted source juxtaposes the prior
sibling expression directly against `block(width: ...)[...]` with no
separator, e.g.:

```
list({
text("List item with a figure:")block(width: 40%)[#figure(
  image("image.png"),
  ...
)]
})
```

I verified this by hand (`sphinx-build -b typst` → `typst.compile()`) with
this exact fixture; the compile fails with:

```
FAIL: expected semicolon or line break
```

This is a hard parse error that aborts the *entire* document compile, not
just the affected figure — a `TypstCompilationError` for `typstpdf` builds.
Note this is worse than the pre-existing gap: a figure *without* `:figwidth:`
in the same position already lacked the separator too (verified on the
`3b361bb` base commit, same missing-check), but there the emitted
`text("...")[#figure(...)]` at least *parses* (Typst reads it as a trailing
content-block argument to the preceding call) and only fails later at
type-check time (`unexpected argument`) — same net breakage, but the new
`block(width: ...)[...]` shape removes even that accidental parse-level
grace, and is a code path this phase specifically introduces and tests
(just not in this position). None of the new `TestFigureFigwidthRenderGate`/
`TestTableWidthRenderGate` fixtures place the wrapped figure/table as a
non-first list-item element, so this gap slipped past the new tests (the
table counterpart is fine — `visit_table` already has the separator check,
independent of the width wrapper).

**Fix:** Add the same separator check `visit_table` already uses, at the top
of `visit_figure`, before emitting the opening call in any of its three
branches:

```python
def visit_figure(self, node: nodes.figure) -> None:
    self.in_figure = True
    self.figure_content = []
    self.figure_caption = ""

    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
        self.list_item_needs_separator = False

    figwidth = node.get("width")
    self._figure_block_width = (
        self._convert_length_to_typst(figwidth) if figwidth else None
    )
    ...
```

and ensure `depart_figure` still marks `list_item_needs_separator = True`
for the following sibling (mirroring `depart_table`'s trailing block). This
fixes both the new `:figwidth:` case and the pre-existing captionless/
figwidth-less case in the same list-item position.

## Warnings

### WR-01: No render-gate coverage for the figwidth-without-caption `depart_figure` branch

**File:** `typsphinx/translator.py:1978-1982`, `tests/fixtures/figure_length_render_gate/index.rst`
**Issue:** `depart_figure`'s `elif self._figure_block_width is not None:` branch
(closing `\n)]\n\n` for a figure that has `:figwidth:` but **no** `ids` — i.e.
no caption, since docutils only auto-assigns a figure id when it has a
caption) is a real, reachable code path, but none of the new/extended
`figure_length_render_gate` fixture cases exercise a figure with
`:figwidth:` and no caption — every fixture figure has a caption (hence
always has `ids`), so the render gate only ever proves the
"`ids` **and** width" branch (`if node.get("ids"):` at
`typsphinx/translator.py:1975`). I manually verified the no-ids/width-only
branch does compile correctly, but this is by construction (my own ad hoc
test), not by the phase's own acceptance gate.
**Fix:** Add one more figure to `figure_length_render_gate/index.rst` with
`:figwidth:` and no caption line, and assert the no-label `block(width:
...)[#figure(\n  image(...)\n)]` shape (no `<label>`) appears/compiles in
`TestFigureFigwidthRenderGate`.

### WR-02: `visit_todo_node`/`visit_manpage` type hints avoid importing their real node classes, weakening static checking

**File:** `typsphinx/translator.py:3854, 3882`
**Issue:** `visit_todo_node`/`depart_todo_node` are typed as
`node: nodes.Element` rather than the actual `sphinx.ext.todo.todo_node`
(a deliberate choice per the docstring, to avoid importing
`sphinx.ext.todo` — a reasonable trade-off since `sphinx.ext.todo` is an
optional extension). This is a legitimate, intentional design decision
(documented), not a functional bug, but it does mean mypy cannot catch a
future typo like `node.get("nonexistent_attr")` being silently accepted as
`Any`-ish `Element.get`. Not blocking, just worth a maintenance note since
`visit_manpage`/`depart_manpage` by contrast *do* import `addnodes` and use
the precise `addnodes.manpage` type — the two new handlers in this same
diff use inconsistent typing strategies for the same underlying trade-off
(avoid vs. accept an import).
**Fix:** No action required; if `sphinx.ext.todo`'s `todo_node` import is
ever judged safe to add (it's a stdlib-bundled Sphinx extension, not a
third-party optional dependency), tighten the type hint for consistency
with `visit_manpage`.

## Info

### IN-01: `test_corpus_gate.py`'s flipped assertion is a strict "zero tolerance" gate going forward

**File:** `tests/test_corpus_gate.py:349-358`
**Issue:** The catalogue assertion was flipped from "non-empty" to
"empty" (`assert not catalogue`). I re-ran this test against the real,
already-cloned Sphinx `v9.1.0` `doc/` corpus and it passes, confirming the
claim that `todo_node`/`manpage` were the last silently-dropped node types
this corpus exercises. This is a legitimate, verified GATE-03 gate, not a
bug — flagging only as a maintenance note: any *future* Sphinx doc-corpus
change (a new directive/role typsphinx doesn't yet handle, or a Sphinx
minor-version bump exercising a previously-unused node type) will now fail
this test outright with zero prior warning tolerance, whereas before it
only required *some* catalogue entries to exist. This is presumably the
intended tightening (GATE-03), just noting the tradeoff for future
maintainers debugging an unrelated corpus-gate failure after a Sphinx
version bump.
**Fix:** No action required; this is by design. Worth a one-line comment
in CLAUDE.md or the test itself if a maintainer is likely to be confused by
a `catalogue.most_common()` failure after an unrelated Sphinx upgrade (the
test's own failure message already prints the catalogue, which is
sufficient for triage).

---

_Reviewed: 2026-07-16T13:09:44Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
