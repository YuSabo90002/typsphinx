# Phase 43 Plan 04 — Gate Evidence (TBL-05 + QUA-01)

All commands and outputs below were executed in this session, in this worktree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a92a92c2bb9894c76`),
against the unfixed translator before any `typsphinx/` change (Task 1), then
re-measured against the fixed translator (Task 2), then re-measured again
after the QUA-01 docstring correction (Task 3). Nothing below is transcribed
from a planning document.

## Task 1 — RED baseline (unfixed translator)

### Doctree probe (measured 2026-08-04, via a real Sphinx `-b typst` build,
`app.env.get_doctree("index")`, NOT bare `docutils.core.publish_doctree` —
the latter under-measures: it returned `ids: ['tbl-target']` with no `id1`,
because docutils' own `make_id`/target-propagation machinery only assigns
the second auto id `id1` when running under Sphinx's full environment. The
Sphinx-driven probe below is the one that matches this fixture's real build
path and is what is recorded as authoritative.)

```
Number of tables found: 2
--- Table 0 ---
ids: ['id1', 'tbl-target']
names: ['tbl-target']
title astext(): '<span></span>'
title children types: ['raw']
title.children[0] repr: <raw: <#text: '<span></span>'>>
--- Table 1 ---
ids: ['tec-real-name']
names: ['tec-real-name']
title astext(): 'TECREALCAP'
title children types: ['Text']
title.children[0] repr: <#text: 'TECREALCAP'>
```

This confirms D-07 directly, in this session: the first table's title child
is a single `raw` node whose `astext()` is `'<span></span>'` — non-empty —
while `visit_raw` raises `SkipNode` for a non-typst `format`, so the
*rendered* content is empty. Any `astext()`-based structural pre-check would
misclassify this table as non-captioned; the actual pre-check
(`isinstance(node.children[0], nodes.title)`) correctly classifies it as
captioned regardless of rendered content, which is exactly D-07's point:
the pre-check must stay structural, and the divergence is genuine.

### Command and exit status

```
$ .venv/bin/python -m sphinx -b typstpdf -E tests/fixtures/table_empty_caption_anchor_render_gate /tmp/tecarg-red
EXIT: 2
```

### Full stderr / build log (`/tmp/tecarg-red.log`)

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
preparing documents... Template written to /tmp/tecarg-red/_template.typ
done
writing output... [index] done
Compiling 1 master document(s) to PDF...
Typst compilation failed at /tmp/tecarg-red/index.typ: TypstError: label `<index:tbl-target>` does not exist in the document
ERROR: Failed to compile /tmp/tecarg-red/index.typ: Typst compilation failed: TypstError: label `<index:tbl-target>` does not exist in the document
Location: /tmp/tecarg-red/index.typ
Details: label `<index:tbl-target>` does not exist in the document

Extension error!
...
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: label `<index:tbl-target>` does not exist in the document
Location: /tmp/tecarg-red/index.typ
Details: label `<index:tbl-target>` does not exist in the document
```

The literal `TypstError` is present, confirming the classic-compile-fatal RED
class this plan's `<verify>` block checks for.

### PDF produced?

```
$ ls -la /tmp/tecarg-red/
total 8
drwxr-xr-x  .doctrees
-rw-r--r--  _template.typ
-rw-r--r--  index.typ
```

**No `index.pdf` was produced.** The build aborted at Typst's semantic
label-resolution pass before any PDF was written.

### Emitted `index.typ` (RED, full contents)

```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Table Empty Caption Anchor Render Gate",
  authors: ("typsphinx tests",),
  date: "0.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Table Empty Caption Anchor Render Gate")}) <index:table-empty-caption-anchor-render-gate>]

par({text("This fixture reproduces TBL-05 (Phase 43): a captioned table whose title renders to the empty string anchors its ids on NEITHER ")
raw("visit_table")
text("’s structural pre-check nor ")
raw("depart_table")
text("’s rendered-caption truthiness check, leaving a propagated target’s anchor unemitted and a same-document ")
raw("​:ref:")
text(" dangling – aborting the whole ")
raw("typst.compile()")
text(" at Typst’s semantic label-resolution pass.")})

[#heading(level: 2, {text("Empty-rendered caption")}) <index:empty-rendered-caption>]

table(
  columns: (7fr, 7fr),
  {par({text("TEC1A")})},
  {par({text("TEC1B")})},
)

par({text("See ")
link(<index:tbl-target>, 
text("the table"))
text(".")})


[#heading(level: 2, {text("Real-caption numbering control")}) <index:real-caption-numbering-control>]

par({text("This section is the D-05 control: if the empty-rendered-caption table above were figure-wrapped it would consume a table number and this table would render as “Table 2” instead of “Table 1”.")})

[#figure(
table(
  columns: (7fr, 7fr),
  {par({text("TEC2A")})},
  {par({text("TEC2B")})},
),
  caption: {text("TECREALCAP")},
  kind: table
) <index:tec-real-name>]

par({text("See ")
link(<index:tec-real-name>, 
text("Table 1"))
text(" for the real-caption table’s own cross-reference.")})



}
```

**No matching anchor for `<index:tbl-target>` anywhere in the file.** The
`link(<index:tbl-target>, ...)` call at line "See the table." has no
corresponding `metadata(none) <index:tbl-target>` anchor block — the table's
ids are anchored on NEITHER `visit_table`'s structural path (skipped because
`is_captioned` is `True`) NOR `depart_table`'s rendered-caption path (skipped
because `self.table_caption` is the empty-string-stripped `""`, falsy).

### RED commit SHA

`de018926ed49f114d260d368ed7cf63794d3cfee` (fixture + render gate test,
`typsphinx/translator.py` untouched — verified via
`git diff --stat HEAD~1 HEAD -- typsphinx/translator.py` returning empty).

*(Recorded as an evidence-only follow-up commit, mirroring plans 43-01/43-03's
established precedent: the evidence file cannot record its own commit's SHA
without a forbidden amend, so the RED artifacts are committed first and this
file records that commit's SHA in a small follow-up commit.)*

---

## Task 2 — GREEN (post-fix translator)

### Fix commit SHA

`0b6cbbc7610ff06d7989dd95bcefc3c6659df0a2` — `typsphinx/translator.py`
(`_table_is_captioned` init + `_push_table_state`/`_pop_table_state` snapshot
entries + `visit_table`/`depart_table` split) plus a test-file NBSP-matching
fix (`tests/test_table_empty_caption_anchor_render_gate.py`, unrelated to the
translator's behaviour — Typst emits a non-breaking space between "Table" and
the figure number, which the initial assertion did not account for).

### Command and exit status

```
$ .venv/bin/python -m sphinx -b typstpdf -E tests/fixtures/table_empty_caption_anchor_render_gate /tmp/tecarg-green
EXIT: 0
```

### Full build log (`/tmp/tecarg-green.log`)

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
preparing documents... Template written to /tmp/tecarg-green/_template.typ
done
writing output... [index] done
Compiling 1 master document(s) to PDF...
Generated PDF: /tmp/tecarg-green/index.pdf
build succeeded.
```

`index.pdf` exists: 36847 bytes.

### Emitted `index.typ` (GREEN, full contents)

```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Table Empty Caption Anchor Render Gate",
  authors: ("typsphinx tests",),
  date: "0.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Table Empty Caption Anchor Render Gate")}) <index:table-empty-caption-anchor-render-gate>]

par({text("This fixture reproduces TBL-05 (Phase 43): a captioned table whose title renders to the empty string anchors its ids on NEITHER ")
raw("visit_table")
text("’s structural pre-check nor ")
raw("depart_table")
text("’s rendered-caption truthiness check, leaving a propagated target’s anchor unemitted and a same-document ")
raw("​:ref:")
text(" dangling – aborting the whole ")
raw("typst.compile()")
text(" at Typst’s semantic label-resolution pass.")})

[#heading(level: 2, {text("Empty-rendered caption")}) <index:empty-rendered-caption>]

table(
  columns: (7fr, 7fr),
  {par({text("TEC1A")})},
  {par({text("TEC1B")})},
)


[#metadata(none) <index:id1>]

[#metadata(none) <index:tbl-target>]
par({text("See ")
link(<index:tbl-target>, 
text("the table"))
text(".")})


[#heading(level: 2, {text("Real-caption numbering control")}) <index:real-caption-numbering-control>]

par({text("This section is the D-05 control: if the empty-rendered-caption table above were figure-wrapped it would consume a table number and this table would render as “Table 2” instead of “Table 1”.")})

[#figure(
table(
  columns: (7fr, 7fr),
  {par({text("TEC2A")})},
  {par({text("TEC2B")})},
),
  caption: {text("TECREALCAP")},
  kind: table
) <index:tec-real-name>]

par({text("See ")
link(<index:tec-real-name>, 
text("Table 1"))
text(" for the real-caption table’s own cross-reference.")})



}
```

**The propagated `tbl-target` anchor is now present**: both
`[#metadata(none) <index:id1>]` and `[#metadata(none) <index:tbl-target>]`
appear right after the bare (NOT figure-wrapped) `table(...)` call for the
empty-rendered-caption table -- the `link(<index:tbl-target>, ...)` reference
now resolves. The second table (real caption) is still figure-wrapped with
`kind: table` and its own `<index:tec-real-name>` label, unchanged.

### PDF-extracted text (GREEN, via `pypdf`)

```
Table Empty Caption Anchor Render Gate
typsphinx tests
0.0.0
1
1 Contents
Contents
2 Table Empty Caption Anchor Render Gate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2.1 Empty-rendered caption . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2.2 Real-caption numbering control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2
2 Table Empty Caption Anchor Render Gate
This fixture reproduces TBL-05 (Phase 43): a captioned table whose title renders to the empty string
anchors its ids on NEITHER visit_table's structural pre-check nor depart_table's rendered-
caption truthiness check, leaving a propagated target's anchor unemitted and a same-document
:ref: dangling – aborting the whole typst.compile() at Typst's semantic label-resolution pass.
2.1 Empty-rendered caption
TEC1A TEC1B
See the table.
2.2 Real-caption numbering control
This section is the D-05 control: if the empty-rendered-caption table above were figure-wrapped it
would consume a table number and this table would render as "Table 2" instead of "Table 1".
TEC2A TEC2B
Table 1: TECREALCAP
See Table 1 for the real-caption table's own cross-reference.
3
```

**D-05 numbering control confirmed**: the real-caption table renders as
`Table 1: TECREALCAP`, NOT `Table 2` -- the empty-rendered-caption table
above it consumed no table number, proving it is not figure-wrapped.

### Warning diff (D-06)

```
$ grep -i "warning" /tmp/tecarg-red.log || echo "NO WARNING IN RED LOG"
NO WARNING IN RED LOG

$ grep -i "warning" /tmp/tecarg-green.log || echo "NO WARNING IN GREEN LOG"
NO WARNING IN GREEN LOG
```

**Empty diff**: neither the RED nor the GREEN build emits any `WARNING` --
the pre-fix failure is a Typst compile FATAL (an `ExtensionError` wrapping a
`TypstError`), never a Sphinx-level warning about the caption, and the fix
introduces no new warning either. D-06 satisfied.

### Full suite + lint/type gates (GREEN, this session)

```
$ .venv/bin/python -m pytest tests/test_table_empty_caption_anchor_render_gate.py -x -q
2 passed in 0.69s

$ .venv/bin/python -m pytest tests/test_captioned_table_propagated_target_render_gate.py tests/test_nested_table_render_gate.py tests/test_nested_figure_render_gate.py -q
22 passed in 4.54s

$ .venv/bin/python -m pytest -q
836 passed, 1 skipped in 77.65s (834 baseline + 2 new)

$ .venv/bin/python -m black --check .
All done! 217 files would be left unchanged.

$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/python -m mypy typsphinx/
Success: no issues found in 6 source files

$ git diff --stat pyproject.toml uv.lock
(empty -- no new runtime dependency)
```

---

## Task 3 — QUA-01 docstring correction

Re-grepped in THIS session, in THIS worktree, AFTER waves 1-3 of this phase
(43-01 TBL-04, 43-03 FIG-01, and this plan's own Task 2 TBL-05 fix) had all
landed -- per D-08's explicit instruction not to trust the todo's/CONTEXT's
recorded counts, and per the plan's requirement to re-derive them at fix
time since this phase changes the file.

### `grep -n '_emit_id_anchors(' typsphinx/translator.py`

```
528:    def _emit_id_anchors(
900:        self._emit_id_anchors(node)
931:            self._emit_id_anchors(node)
1007:        self._emit_id_anchors(node)
1824:        self._emit_id_anchors(node)
1879:        self._emit_id_anchors(node)
1957:        self._emit_id_anchors(node)
2008:        self._emit_id_anchors(node)
2180:        self._emit_id_anchors(node)
2599:        self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
3458:            self._emit_id_anchors(node)
3767:            self._emit_id_anchors(node, skip_ids=skip_ids)
3965:        self._emit_id_anchors(node)
4077:            self._emit_id_anchors(node)
5247:        self._emit_id_anchors(node)
5335:        self._emit_id_anchors(node)
5570:            self._emit_id_anchors(node)
5602:            self._emit_id_anchors(node)
5743:        self._emit_id_anchors(node)
5769:        self._emit_id_anchors(node)
5880:        self._emit_id_anchors(node)
6825:        self._emit_id_anchors(node)
```

**Total call-site count: 21** (line 528 is the `def`, not a call; the
remaining 21 lines are all calls).

### `grep -n 'skip_ids' typsphinx/translator.py`

```
529:        self, node: nodes.Node, skip_ids: set[str] | None = None
562:        ``skip_ids`` lets a caller that ALREADY anchors one of the node's ids
567:        would otherwise dangle -- so the figure passes ``skip_ids={ids[0]}`` to  [pre-edit; see below]
574:            skip_ids: Raw docutils ids to NOT anchor here (already anchored by
580:        skip = skip_ids or set()
2599:        self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
3444:        # skip_ids={ids[0]} AFTER emitting the figure's own <label>.
3766:            skip_ids = set(node.get("ids", [])[:1]) if was_captioned else set()
3767:            self._emit_id_anchors(node, skip_ids=skip_ids)
```

**`skip_ids` caller count: exactly 2** — line 2599, inside `depart_figure`
(function defined at line 2561), and line 3767, inside `depart_table`
(function defined at line 3557), confirmed by:

```
$ awk 'NR==2599{print NR": "$0} /^    def /{fn=$0; fnline=NR} NR==2599{print "  in function (line "fnline"): "fn}' typsphinx/translator.py
2599:         self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
  in function (line 2561):     def depart_figure(self, node: nodes.figure) -> None:

$ awk 'NR==3767{print NR": "$0} /^    def /{fn=$0; fnline=NR} NR==3767{print "  in function (line "fnline"): "fn}' typsphinx/translator.py
3767:             self._emit_id_anchors(node, skip_ids=skip_ids)
  in function (line 3557):     def depart_table(self, node: nodes.table) -> None:
```

**No discrepancy against D-08's expectation**: still exactly the two callers
named there (`depart_figure`, `depart_table`), no third caller introduced by
this phase. `depart_table`'s call site now reads `skip_ids=skip_ids` (a local
computed on the preceding line) rather than the inline expression it used
before Task 2's fix — the plan 43-04 Task 2 fix made the `skip_ids` value
CONDITIONAL (`set(node.get("ids", [])[:1]) if was_captioned else set()`)
rather than unconditionally always `{ids[0]}`, but the CALLER remains
`depart_table` either way.

### Docstring rewrite

The `_emit_id_anchors` docstring's `skip_ids` paragraph was rewritten to name
both `depart_figure` and `depart_table` by name, state the shared rationale
once (self-anchored `ids[0]` -> duplicate-label fatal; propagated `ids[1:]`
-> dangling reference), note `depart_table`'s TBL-05 refinement (an empty
`skip_ids` when the table did not actually figure-wrap), and point at the
inline comments at `depart_table`'s own call site for the Phase 42 / TBL-03
firing-order constraint rather than restating them. The word "sole" no
longer appears in the docstring, and no exhaustive list of all 21 call sites
was added (D-08: an exhaustive list is exactly what rotted into this
requirement in the first place).

### Verification (comment-only diff)

```
$ git diff --stat
 typsphinx/translator.py | 28 ++++++++++++++++++++--------
 1 file changed, 20 insertions(+), 8 deletions(-)

$ git diff --stat -- typsphinx/  (this task's own commit, isolated)
 typsphinx/translator.py | ... (docstring only)

$ awk '/def _emit_id_anchors/,/def visit_document/' typsphinx/translator.py | grep -c 'depart_figure'
1
$ awk '/def _emit_id_anchors/,/def visit_document/' typsphinx/translator.py | grep -c 'depart_table'
2
$ awk '/def _emit_id_anchors/,/def visit_document/' typsphinx/translator.py | grep -c 'The sole'
0

$ .venv/bin/python -m pytest -q
836 passed, 1 skipped in 76.56s (0:01:16)

$ .venv/bin/python -m black --check .
All done! 217 files would be left unchanged.

$ .venv/bin/ruff check .
All checks passed!

$ .venv/bin/python -m mypy typsphinx/
Success: no issues found in 6 source files
```

No behaviour change (comment-only diff), suite still green.
