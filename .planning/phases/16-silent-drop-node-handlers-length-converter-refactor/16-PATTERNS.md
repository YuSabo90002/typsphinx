# Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor - Pattern Map

**Mapped:** 2026-07-16
**Files analyzed:** 6 (1 modified source file with 4 distinct edit-sites + 3-4 new/extended test fixtures + 1 modified test file)
**Analogs found:** 6 / 6

## File Classification

All source changes land in the single existing file `typsphinx/translator.py` (no new source files
— this is a "wire existing machinery to more node types" phase, not new architecture). Each
edit-site below is classified independently since they follow different existing patterns.

| New/Modified File (or edit-site) | Role | Data Flow | Closest Analog | Match Quality |
|-----------------------------------|------|-----------|-----------------|---------------|
| `typsphinx/translator.py::visit_todo_node`/`depart_todo_node` (NEW methods) | translator (node-visitor) | transform (doctree node → Typst text) | `typsphinx/translator.py::visit_hint`/`depart_hint` (:3755-3765) | exact |
| `typsphinx/translator.py::visit_manpage`/`depart_manpage` (NEW methods) | translator (node-visitor) | transform | `typsphinx/translator.py::visit_emphasis`/`depart_emphasis` (:950-1027) | exact (via delegation) |
| `typsphinx/translator.py::visit_figure`/`depart_figure` (MODIFIED, add figwidth wiring) | translator (node-visitor) | transform | `typsphinx/translator.py::visit_image`/`depart_image` (:2472-2531, the width/height wiring reference) | role-match (image not figure, but same helper call shape) |
| `typsphinx/translator.py::visit_table`/`depart_table` (MODIFIED, add width wiring) | translator (node-visitor) | transform | `typsphinx/translator.py::visit_image`/`depart_image` (:2472-2531) | role-match |
| `tests/fixtures/todo_render_gate/{conf.py,index.rst}` (NEW) | test fixture (Sphinx project) | file-I/O (fixture read by pytest) | `tests/fixtures/figure_length_render_gate/{conf.py,index.rst}` | exact |
| `tests/fixtures/manpage_render_gate/{conf.py,index.rst}` (NEW) | test fixture | file-I/O | `tests/fixtures/figure_length_render_gate/{conf.py,index.rst}` | exact |
| `tests/fixtures/figure_length_render_gate/index.rst` (EXTENDED with figwidth cases) | test fixture | file-I/O | itself (extend in place) | exact |
| `tests/fixtures/table_width_render_gate/{conf.py,index.rst}` (NEW, or extend an existing table fixture) | test fixture | file-I/O | `tests/fixtures/figure_length_render_gate/{conf.py,index.rst}` | exact |
| `tests/test_pdf_render_gate.py` (MODIFIED, add fixture-dir fixtures + new test classes/functions) | test | request-response (build → compile → assert) | `tests/test_pdf_render_gate.py::TestFigureLengthRenderGate::test_figure_length_pdf_converts_px_and_drops_unknown_unit` (:236-286) | exact |

## Pattern Assignments

### `visit_todo_node`/`depart_todo_node` (translator, transform)

**Analog:** `visit_hint`/`depart_hint`, `typsphinx/translator.py:3755-3765` (also see `visit_important`/`visit_seealso` for the `custom_title=` shape, :3731-3753)

**Core pattern** (exact template to copy, lines 3755-3765):
```python
def visit_hint(self, node: nodes.hint) -> None:
    """Visit a hint admonition (converts to #tip[]).

    gentle-clues 1.3.1 has no dedicated `hint` clue; `tip` is the
    verified closest semantic analog (see RESEARCH.md D-06 mapping).
    """
    self._visit_admonition(node, "tip")

def depart_hint(self, node: nodes.hint) -> None:
    """Depart a hint admonition."""
    self._depart_admonition()
```

New code (per D-01/Pattern 1 in RESEARCH.md), same shape, with `custom_title`:
```python
def visit_todo_node(self, node) -> None:
    """Visit a todo_node (sphinx.ext.todo). Converts to #task[] (gentle-clues).

    Note: todo_node carries its own nodes.title child (Sphinx inserts it at
    parse time), which visit_title's admonition-aware branch buffers and
    _depart_admonition prefers over custom_title -- the static "Todo" below
    is an inert fallback for the non-i18n case, not the actual title source.
    """
    self._visit_admonition(node, "task", custom_title="Todo")

def depart_todo_node(self, node) -> None:
    """Depart a todo_node."""
    self._depart_admonition()
```

**Shared helper it depends on** — `_visit_admonition`/`_depart_admonition`,
`typsphinx/translator.py:3643-3706` (title precedence logic, `{clue_type}({` code-mode block open,
id-anchor emission, list-item separator handling — all reused unmodified).

**Config-gating decision needed (RESEARCH.md Pitfall 1 / Open Question 1):** every official Sphinx
builder gates the todo body on `self.config.todo_include_todos` (default `False`) via
`raise nodes.SkipNode`. No existing analog for this specific gate exists in `translator.py` — the
planner must decide whether to add it. If added, the pattern is a plain `if not
self.config.todo_include_todos: raise nodes.SkipNode` at the top of `visit_todo_node`, before the
`_visit_admonition` call (docutils `SkipNode` is already imported/used elsewhere in this file for
other skip cases — search `raise nodes.SkipNode` for existing precedent, e.g. the `tabularcolumns`
handler at :4045).

---

### `visit_manpage`/`depart_manpage` (translator, transform)

**Analog:** `visit_emphasis`/`depart_emphasis`, `typsphinx/translator.py:950-1027`

**Delegation pattern (recommended, per RESEARCH.md Pattern 2 — DRY, avoids re-implementing the
paragraph-separator / list-item / inline-concat-context state machine):**
```python
def visit_manpage(self, node) -> None:
    """Visit a manpage node (:manpage: role). Renders as italic, Sphinx-HTML-faithful (D-02)."""
    self.visit_emphasis(node)

def depart_manpage(self, node) -> None:
    """Depart a manpage node."""
    self.depart_emphasis(node)
```

**Why delegation is safe:** `visit_emphasis`/`depart_emphasis` perform no `isinstance(node, ...)`
check on their argument (verified by reading the full body, :950-1027, quoted above in full) — they
only read `self.*` state and call `self.add_text`/`self._enter_inline_concat_element` etc. A
`manpage` node duck-types fine.

**Core state machinery reused (do not re-derive):** `self._add_paragraph_separator()`,
`self._enter_inline_concat_element()`/`self._exit_inline_concat_element()`,
`self.in_list_item`/`self.list_item_needs_separator` save-swap-restore, and the
`"#" if self._in_markup_mode else ""` prefix toggle (all inside the analog above — do not hand-copy,
delegate instead).

---

### `visit_figure`/`depart_figure` — figwidth wiring (translator, transform, MODIFIED)

**Analog for the length-conversion call shape:** `visit_image`, `typsphinx/translator.py:2505-2518`
```python
# Add optional attributes. Length values from docutils (:width:/:height:)
# may use CSS units Typst does not understand (e.g. raw "px"), which
# would abort the whole compile (Issue #114, FIG-01). Convert via
# _convert_length_to_typst and drop the dimension entirely when the
# unit is unsupported (D-02) -- never emit a raw unconverted unit.
if "width" in node:
    converted_width = self._convert_length_to_typst(node["width"])
    if converted_width is not None:
        self.add_text(f", width: {converted_width}")
```

**Current figure code being modified** — `typsphinx/translator.py:1868-1932` (`visit_figure`
opens with `self.add_text("[#figure(\n")` or `self.add_text("figure(\n")` depending on `node.get("ids")`;
`depart_figure` closes with `self.add_text("\n) <{label}>]\n\n")` or `self.add_text("\n)\n\n")`).

**Required new shape (per RESEARCH.md Pattern 3 / Pitfall 3 — Typst's `figure()` rejects a direct
`width:` kwarg, verified via real compile):** wrap the WHOLE figure call in `#block(width:
...)[...]`/`block(width: ...)[...]`, not pass `width:` into `figure(...)` itself. Read
`node.get("width")` (docutils' `Figure` directive assigns this from `:figwidth:`), convert via
`self._convert_length_to_typst(figwidth)`, and if not None, emit the `block(width: ...)[` wrapper
before the existing `figure(`/`[#figure(` opening in `visit_figure`, with a matching `]` close added
in `depart_figure` before/after the existing closing text (exact ordering relative to the
`<label>]` markup-mode close is an implementation detail the planner/executor must get right —
`_emit_id_anchors` still needs to run per existing depart_figure logic).

**Underlying helper unchanged:** `_convert_length_to_typst`, `typsphinx/translator.py:3009-3067`
(full body — px=0.75pt, pc=12pt, passthrough units, unknown-unit drop+warn via
`logger.warning`, regex `re.fullmatch(r"(-?[0-9.]+)([a-zA-Zµ%]*)", value)`). Call it exactly as
shown above; do not reimplement.

---

### `visit_table`/`depart_table` — width wiring (translator, transform, MODIFIED)

**Analog for structure:** `visit_table`/`depart_table` themselves, `typsphinx/translator.py:2118-2214`
(existing methods being extended, not replaced). Key excerpt — the `depart_table` emission site
that must be wrapped:
```python
# Generate Typst table() syntax (no # prefix in unified code mode)
if self.table_colcount > 0:
    # Use self.body.append directly to avoid routing to table_cell_content
    self.body.append(f"table(\n  columns: {self.table_colcount},\n")
    ...
    self.body.append(")\n\n")
```

**Analog for the length-conversion call + `block(width:)` wrapper shape:** same as figure — see
`visit_image` excerpt above and RESEARCH.md's verified-by-real-compile constraint: `table()` also
rejects a direct `width:` kwarg (`unexpected argument: width`); wrap in `#block(width:
...)[...]`/`block(width: ...)[...]` instead. `node.get("width")` is set by docutils'
`Table.set_table_width()`, called by all three of `RSTTable`/`CSVTable`/`ListTable` (all converge
on `nodes.table`, so this single wiring covers `.. table::`, `.. csv-table::`, and
`.. list-table::` uniformly — no per-directive-type branching needed).

**Caution:** `depart_table` uses `self.body.append(...)` directly (not `self.add_text`) to avoid
routing into a stale `table_cell_content` buffer (see the inline comment at :2189-2190) — any new
`block(width: ...)[` wrapper emission must follow the same `self.body.append` convention at this
site, not `self.add_text`, to stay consistent with the existing table-emission mechanism.

---

## Shared Patterns

### CSS-length conversion (single source of truth)
**Source:** `_convert_length_to_typst`, `typsphinx/translator.py:3009-3067`
**Apply to:** `visit_image` (existing, unmodified), `visit_figure`/`depart_figure` (new wiring),
`visit_table`/`depart_table` (new wiring). D-03b requires exactly this one implementation — no site
may contain its own px/pc arithmetic.
```python
if "width" in node:
    converted_width = self._convert_length_to_typst(node["width"])
    if converted_width is not None:
        self.add_text(f", width: {converted_width}")
```

### `#block(width: ...)[...]` wrapper (figure/table only, NOT image)
**Source:** verified via real `typst.compile()` this session (see 16-RESEARCH.md "Code Examples" /
Pitfall 3) — no existing codebase analog since this is a new wiring shape; `visit_image` embeds
`width:` directly as an `image()` kwarg (that function DOES accept it), which is why the image
pattern cannot be copied verbatim for figure/table.
```typst
#block(width: 50%)[
  #figure([x], caption: [c])
]
```
**Apply to:** `visit_figure`/`depart_figure`, `visit_table`/`depart_table` only.

### Admonition box machinery (`_visit_admonition`/`_depart_admonition`)
**Source:** `typsphinx/translator.py:3643-3706`
**Apply to:** `visit_todo_node`/`depart_todo_node` only (no other new files this phase).

### GATE-01 real-compile fixture + test pattern
**Source:** `tests/fixtures/figure_length_render_gate/{conf.py,index.rst}` +
`tests/test_pdf_render_gate.py::TestFigureLengthRenderGate` (:236-286)
**Apply to:** all three new/extended fixtures (todo, manpage, table-width) and their corresponding
new test functions in `tests/test_pdf_render_gate.py`.

`conf.py` template (copy verbatim, adjust project name/extensions):
```python
project = "Figure Length Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_documents = [
    ("index", "index", "Figure Length Render Gate", "Test Author"),
]
```
For the todo fixture specifically, `extensions` must additionally include `"sphinx.ext.todo"` and
`conf.py` must set `todo_include_todos = True` explicitly (RESEARCH.md Pitfall 1 — otherwise the
render path is never exercised, matching the real corpus's effective config).

Test class/function template (copy structure, not content) from
`TestFigureLengthRenderGate.test_figure_length_pdf_converts_px_and_drops_unknown_unit`
(:243-286): run `_run_sphinx_build_typst(fixture_dir, temp_build_dir)`, assert `returncode == 0`,
read `index.typ`, assert expected/forbidden substrings, then `typst.compile()` to PDF and assert
the PDF file exists/has the `%PDF` magic bytes. Marked `@pytest.mark.slow` +
`@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)` at the class level, mirroring
the existing class decorator pattern at :231-235.

`LEAK_SIGNATURES = ("par({", 'text("', 'raw("')` (module-level constant, :41) is available for
literal-source-leak checks (e.g. proving the todo body evaluated rather than printing calls as
literal text) — reuse it, don't redefine.

## No Analog Found

None — every planned edit-site and fixture has a directly-matching existing pattern in
`typsphinx/translator.py` or `tests/`. This phase is scoped entirely as "wire existing machinery to
new call sites," so full coverage was expected and confirmed.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (single source file, ~4581 lines — targeted
`grep`+`Read` on specific `def visit_*`/`def depart_*`/`def _*` line ranges, no full-file read);
`tests/test_pdf_render_gate.py` and `tests/fixtures/figure_length_render_gate/` (existing GATE-01
fixture/test convention).
**Files scanned:** 3 (`typsphinx/translator.py`, `tests/test_pdf_render_gate.py`,
`tests/fixtures/figure_length_render_gate/{conf.py,index.rst}`)
**Pattern extraction date:** 2026-07-16
</content>
