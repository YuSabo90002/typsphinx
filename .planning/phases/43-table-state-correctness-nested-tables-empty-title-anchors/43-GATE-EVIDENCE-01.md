# Phase 43 Plan 01 — GATE-01 Evidence (TBL-04)

All command output below was executed in this task's own session, in this worktree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a6bb86c0b7e8dd195`), against
this repository's HEAD at the time (`7bdaf40ee131a63dc5cf9789d90668c54948a117`). Nothing
here is transcribed from `43-RESEARCH.md`/`43-CONTEXT.md`/the source todo — those documents
measured a similar shape with different sentinel names on the main tree in an earlier
session; this file re-measures the same defect, in this worktree, against this plan's own
7-section fixture.

## RED — measured against the UNFIXED translator

`typsphinx/translator.py` was **not modified** at the time this RED was captured
(`git status --short typsphinx/translator.py` printed nothing).

Command:

```
uv run python -m sphinx -b typstpdf -E tests/fixtures/nested_table_render_gate <build>
```

Full stdout (Japanese locale — this environment's default Sphinx locale, unrelated to the
defect):

```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typstpdf]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to <build>/_template.typ
done
writing output... [index] done
Compiling 1 master document(s) to PDF...
Generated PDF: <build>/index.pdf
build succeeded.
```

- **Exit status: 0.**
- **No warnings, no errors.** ("build succeeded." with no trailing warning count.)
- **A real, well-formed PDF was produced.** This is the defining shape of TBL-04's RED per
  RESEARCH: the broken output compiles cleanly with no downstream error surface at all — the
  RED signal is the ABSENCE of outer-table sentinels from the emitted `.typ` and extracted
  PDF text, not a nonzero exit code or a `TypstError`.

### Emitted `index.typ` (verbatim, full table-bearing body — RED)

```typst
[#heading(level: 2, {text("Section 1: list-table in list-table")}) <index:section-1-list-table-in-list-table>]

figure(
table(
  columns: (50fr, 50fr),
  {par({text("NT1INNERA")})},
  {par({text("NT1INNERB")})},
),
  caption: {text("NT1OUTERCAP")},
  kind: table
)


[#heading(level: 2, {text("Section 2: grid table in list-table")}) <index:section-2-grid-table-in-list-table>]

figure(
table(
  columns: (11fr, 11fr),
  {par({text("NT2INNERA")})},
  {par({text("NT2INNERB")})},
),
  caption: {text("NT2OUTERCAP")},
  kind: table
)


[#heading(level: 2, {text("Section 3: list-table in grid table")}) <index:section-3-list-table-in-grid-table>]

figure(
table(
  columns: (50fr, 50fr),
  {par({text("NT3INNERA")})},
  {par({text("NT3INNERB")})},
),
  caption: {text("NT3OUTERCAP")},
  kind: table
)

par({text("NT3OUTERD")})


[#heading(level: 2, {text("Section 4: three-level nest")}) <index:section-4-three-level-nest>]

figure(
table(
  columns: (50fr, 50fr),
  {par({text("NT4L3A")})},
  {par({text("NT4L3B")})},
),
  caption: {text("NT4L1CAP")},
  kind: table
)


[#heading(level: 2, {text("Section 5: nested table inside a header cell")}) <index:section-5-nested-table-inside-a-header-cell>]

table(
  columns: (100fr),
  table.header(
    {par({text("NT5INNERHEAD")})},
  ),
  {par({text("NT5INNERBODY")})},
)

par({text("NT5HEADB")})

par({text("NT5BODYA")})

par({text("NT5BODYB")})


[#heading(level: 2, {text("Section 6: adjacency, empty cell, and sibling tables")}) <index:section-6-adjacency-empty-cell-and-sibling-tables>]

table(
  columns: (100fr),
  {par({text("NT6INNERA")})},
)

par({text("NT6ROWTWO")})

table(
  columns: (100fr),
  {par({text("NT7SIBA")})},
)

table(
  columns: (100fr),
  {par({text("NT7SIBB")})},
)


[#heading(level: 2, {text("Section 7: top-level control")}) <index:section-7-top-level-control>]

par({text("This section must stay byte-unchanged by the TBL-04 fix – a caption-less top-level table with no nested table anywhere in it.")})

table(
  columns: (50fr, 50fr),
  {par({text("NT8CTRLA")})},
  {par({text("NT8CTRLB")})},
)
```

### Extracted PDF text (verbatim, `pypdf.PdfReader(...).pages[i].extract_text()` — RED)

```
2.1 Section 1: list-table in list-table
NT1INNERA NT1INNERB
Table 1: NT1OUTERCAP
2.2 Section 2: grid table in list-table
NT2INNERA NT2INNERB
Table 2: NT2OUTERCAP
2.3 Section 3: list-table in grid table
NT3INNERA NT3INNERB
Table 3: NT3OUTERCAP
NT3OUTERD
2.4 Section 4: three-level nest
NT4L3A NT4L3B
Table 4: NT4L1CAP
2.5 Section 5: nested table inside a header cell
NT5INNERHEAD
NT5INNERBODY
NT5HEADB
NT5BODYA
NT5BODYB
2.6 Section 6: adjacency, empty cell, and sibling tables
NT6INNERA
NT6ROWTWO
NT7SIBA
NT7SIBB
2.7 Section 7: top-level control
This section must stay byte-unchanged by the TBL-04 fix – a caption-less top-level table with no
nested table anywhere in it.
NT8CTRLA NT8CTRLB
```

### Per-sentinel PRESENT/ABSENT table (RED, measured against the unfixed translator)

| Sentinel | In `index.typ` | In PDF text | Note |
|---|---|---|---|
| NT1OUTERCAP | PRESENT | PRESENT | Wearing the INNER table's body as its `figure(...)` caption — the exact TBL-04 failure shape |
| NT1HEADA | **ABSENT** | **ABSENT** | Outer header cell, entirely dropped |
| NT1HEADB | **ABSENT** | **ABSENT** | Outer header cell, entirely dropped |
| NT1PLAIN | **ABSENT** | **ABSENT** | Outer plain body cell, entirely dropped |
| NT1INNERA | PRESENT | PRESENT | Inner table's own cell — survives, but wearing the outer's caption |
| NT1INNERB | PRESENT | PRESENT | Inner table's own cell |
| NT2OUTERCAP | PRESENT | PRESENT | Same shape as section 1, grid-in-list variant |
| NT2HEADA | **ABSENT** | **ABSENT** | Outer header cell, dropped |
| NT2HEADB | **ABSENT** | **ABSENT** | Outer header cell, dropped |
| NT2PLAIN | **ABSENT** | **ABSENT** | Outer plain body cell, dropped |
| NT2INNERA | PRESENT | PRESENT | Inner grid-table cell |
| NT2INNERB | PRESENT | PRESENT | Inner grid-table cell |
| NT3OUTERCAP | PRESENT | PRESENT | list-in-grid variant, same clobber shape |
| NT3INNERA | PRESENT | PRESENT | Inner list-table cell |
| NT3INNERB | PRESENT | PRESENT | Inner list-table cell |
| NT3OUTERD | PRESENT (leaked) | PRESENT (leaked) | The CONTEXT `<specifics>` §2-predicted ordering edge: emitted as a bare `par({text("NT3OUTERD")})` AFTER the figure, not inside the outer table at all |
| NT4L1CAP | PRESENT | PRESENT | Three-level nest: wearing the INNERMOST (level-3) table's body |
| NT4L1PLAIN | **ABSENT** | **ABSENT** | Level-1's own plain cell, dropped |
| NT4L2PLAIN | **ABSENT** | **ABSENT** | Level-2's own plain cell, dropped |
| NT4L3A | PRESENT | PRESENT | Level-3 (innermost) cell — survives |
| NT4L3B | PRESENT | PRESENT | Level-3 (innermost) cell — survives |
| NT5INNERHEAD | PRESENT | PRESENT | Inner table's own header cell — survives (inside `table.header(...)`) |
| NT5INNERBODY | PRESENT | PRESENT | Inner table's own body-row filler cell (added to satisfy docutils' list-table row-count rule) |
| NT5HEADB | PRESENT (leaked) | PRESENT (leaked) | Outer's SECOND header cell — leaks out as a bare `par({text("NT5HEADB")})` AFTER the surviving inner `table(...)`, not classified as a header cell of any table |
| NT5BODYA | PRESENT (leaked) | PRESENT (leaked) | Outer body-row cell — leaks out as a bare `par(...)`, not inside any `table(...)` |
| NT5BODYB | PRESENT (leaked) | PRESENT (leaked) | Outer body-row cell — leaks out as a bare `par(...)` |
| NT6TEXTBEFORE | **ABSENT** | **ABSENT** | Text preceding the nested table in the SAME cell — entirely dropped, not even leaked |
| NT6INNERA | PRESENT | PRESENT | Inner table's own cell — the ONLY surviving content of the outer table's structure |
| NT6ROWTWO | PRESENT (leaked) | PRESENT (leaked) | Second outer row's first cell — leaks out as a bare `par(...)` after the surviving `table(...)` |
| NT7SIBA | PRESENT | PRESENT | SIBLING top-level table (not nested) — renders correctly, unaffected by the defect |
| NT7SIBB | PRESENT | PRESENT | SIBLING top-level table (not nested) — renders correctly, unaffected by the defect |
| NT8CTRLA | PRESENT | PRESENT | Top-level control table (no nesting anywhere) — renders correctly |
| NT8CTRLB | PRESENT | PRESENT | Top-level control table (no nesting anywhere) — renders correctly |

**Summary of the RED:** every one of the four table-nesting shapes (sections 1-4) loses the
OUTER table's own header/plain cells entirely, with the outer's caption reattached to the
INNERMOST surviving table. Section 5 (header-cell nest) shows the outer table's structure
collapsing into bare, un-tabled paragraphs. Section 6 shows both a total content loss
(`NT6TEXTBEFORE`) and a leaked, un-tabled cell (`NT6ROWTWO`). Sections 6's sibling tables and
section 7's top-level control table are correctly unaffected, since they never nest — this is
the expected non-regression control the fix must not disturb.

### pytest run against the unfixed translator (RED)

```
$ uv run python -m pytest tests/test_nested_table_render_gate.py -x -q
...
assert 'NT1HEADA' in '...'
tests/test_nested_table_render_gate.py:147: AssertionError
=========================== short test summary info ============================
FAILED tests/test_nested_table_render_gate.py::TestNestedTableRenderGate::test_list_table_in_list_table_preserves_outer_cells_and_caption
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
============================== 1 failed in 0.39s ===============================
```

**RED commit SHA:** `05d49334d80705a4884ae63af9ba6e9e60b20be0` — the commit adding
`tests/fixtures/nested_table_render_gate/{conf.py,index.rst}` and
`tests/test_nested_table_render_gate.py`, with `typsphinx/translator.py` untouched (verified:
`git show --stat 05d49334d80705a4884ae63af9ba6e9e60b20be0` lists only the three test/fixture
files). This SHA is the pre-fix side plan 43-05's two-build byte-invariance proof consumes.

## GREEN — Task 1 (Section 1 only), measured after the fix

The fix (`typsphinx/translator.py`): `visit_table`/`depart_table` now push a full snapshot of
the enclosing table's scalar state onto a private `self._table_state_stack` when a table is
already open (i.e. this table node is NESTED), reset for the inner table's own use, and
pop-and-restore that snapshot in `depart_table` before deciding whether the inner table's
rendered markup goes into the restored enclosing cell's buffer (nested) or `self.body`
(top-level). See `_push_table_state`/`_pop_table_state` docstrings in `typsphinx/translator.py`
for the full eight-scalar snapshot set (`table_cells`, `table_colcount`, `table_colwidths`,
`table_caption`, `table_cell_content`, `in_thead`, `current_morecols`, `current_morerows`).

### pytest run against the FIXED translator (GREEN)

```
$ uv run python -m pytest tests/test_nested_table_render_gate.py -x -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 1 item

tests/test_nested_table_render_gate.py .                                 [100%]

============================== 1 passed in 0.45s ===============================
```

### Regression check: pre-existing table gates still pass (GREEN)

```
$ uv run python -m pytest tests/test_table_in_list_item_render_gate.py tests/test_wide_table_render_gate.py tests/test_captioned_table_propagated_target_render_gate.py -q
collected 11 items
...........                                                              [100%]
============================== 11 passed in 0.99s ===============================
```

### Emitted `index.typ`, Section 1 (verbatim, post-fix — GREEN)

```typst
[#heading(level: 2, {text("Section 1: list-table in list-table")}) <index:section-1-list-table-in-list-table>]

[#figure(
table(
  columns: (50fr, 50fr),
  table.header(
    {par({text("NT1HEADA")})},
    {par({text("NT1HEADB")})},
  ),
  {par({text("NT1PLAIN")})},
  {table(
  columns: (50fr, 50fr),
  {par({text("NT1INNERA")})},
  {par({text("NT1INNERB")})},
)},
),
  caption: {text("NT1OUTERCAP")},
  kind: table
) <index:id1>]
```

The OUTER table's header cells (`NT1HEADA`/`NT1HEADB`, now correctly inside
`table.header(...)`), its plain body cell (`NT1PLAIN`) and its own caption (`NT1OUTERCAP`) are
all present, and the INNER table's own cells (`NT1INNERA`/`NT1INNERB`) render as a nested
`table(...)` call inside the outer's second body cell -- exactly the shape TBL-04 requires.

### Extracted PDF text, Section 1 (verbatim, `pypdf` — GREEN)

```
2.1 Section 1: list-table in list-table
NT1HEADA NT1HEADB
NT1PLAIN NT1INNERA NT1INNERB
Table 1: NT1OUTERCAP
```

**Per-sentinel result (Section 1, GREEN):** `NT1OUTERCAP`, `NT1HEADA`, `NT1HEADB`, `NT1PLAIN`,
`NT1INNERA`, `NT1INNERB` are all PRESENT in both the emitted `index.typ` and the
`pypdf`-extracted PDF text -- confirming the fix closes Task 1's scoped defect (Section 1).
Sections 2-7 remain in their RED state recorded above until Tasks 2 and 3 extend the test
coverage and, where measurement shows it necessary, extend the fix.

**Acceptance-criteria checks, measured this session:**

```
$ grep -c '_table_state_stack' typsphinx/translator.py
6
$ grep -c 'def _push_table_state' typsphinx/translator.py
1
$ grep -c 'def _pop_table_state' typsphinx/translator.py
1
$ awk '/def _pop_table_state/,/def visit_tgroup/' typsphinx/translator.py | grep -c 'if not self._table_state_stack'
1
```

## GREEN — Task 2 (Sections 2, 3, 4), measured after re-verifying the SAME fix generalizes

Task 1's fix (no additional code change was needed for Task 2 -- the same save/restore stack
already generalizes over shape and depth by construction, one push per nesting level with no
per-depth special case). Three new test methods were added to
`tests/test_nested_table_render_gate.py`:
`test_grid_table_in_list_table_preserves_outer_cells_and_caption` (section 2),
`test_list_table_in_grid_table_keeps_leaked_cell_inside_outer_table` (section 3, the ordering
edge, with a POSITIONAL assertion), and
`test_three_level_nest_preserves_every_levels_own_cells` (section 4, the depth edge, with a
POSITIONAL assertion that the three `table(` calls nest in strictly increasing source order).

### pytest run, all four tests (GREEN)

```
$ uv run python -m pytest tests/test_nested_table_render_gate.py -x -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 4 items

tests/test_nested_table_render_gate.py ....                              [100%]

============================== 4 passed in 1.37s ===============================
```

### Emitted `index.typ`, Section 3 (verbatim, post-fix — GREEN, the ordering edge)

```typst
[#heading(level: 2, {text("Section 3: list-table in grid table")}) <index:section-3-list-table-in-grid-table>]

[#figure(
table(
  columns: (34fr, 11fr),
  {table(
  columns: (50fr, 50fr),
  {par({text("NT3INNERA")})},
  {par({text("NT3INNERB")})},
)},
  {par({text("NT3OUTERD")})},
),
  caption: {text("NT3OUTERCAP")},
  kind: table
) <index:id3>]
```

`NT3OUTERD` is now the outer table's SECOND cell, emitted INSIDE the outer `table(...)` call
(right after the nested inner table's own cell) -- not leaking out as a bare `par(...)` after
the closing `figure(...)`, which is what the unfixed translator did (see the RED section
above). The positional assertion in the test (`NT3OUTERD`'s offset < `kind: table`'s offset,
within this section's own slice of the document) confirms this ordering directly.

### Emitted `index.typ`, Section 4 (verbatim, post-fix — GREEN, the depth edge)

```typst
[#heading(level: 2, {text("Section 4: three-level nest")}) <index:section-4-three-level-nest>]

[#figure(
table(
  columns: (50fr, 50fr),
  {par({text("NT4L1PLAIN")})},
  {table(
  columns: (50fr, 50fr),
  {par({text("NT4L2PLAIN")})},
  {table(
  columns: (50fr, 50fr),
  {par({text("NT4L3A")})},
  {par({text("NT4L3B")})},
)},
)},
),
  caption: {text("NT4L1CAP")},
  kind: table
) <index:id4>]
```

All three levels' own cells are present, and the three `table(` calls visibly nest (level 3
inside level 2 inside level 1) -- the fix's one-push-per-level design generalizes to
arbitrary depth with no per-depth branch, confirmed by
`grep -Ec 'depth *[=<>]=? *[23]' typsphinx/translator.py` == 0.

**Acceptance-criteria checks, measured this session:**

```
$ grep -c 'def test_' tests/test_nested_table_render_gate.py
4
$ grep -c 'NT2INNERA' tests/test_nested_table_render_gate.py
2
$ grep -c 'NT3OUTERD' tests/test_nested_table_render_gate.py
6
$ grep -c 'NT4L3B' tests/test_nested_table_render_gate.py
1
$ grep -Ec 'depth *[=<>]=? *[23]' typsphinx/translator.py
0
```

