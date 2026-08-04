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

## GREEN — appended after Task 1's fix commit, below (not yet measured at this point in the
## file's history -- see the "Task 1 GREEN" section further down, added after the fix lands).

