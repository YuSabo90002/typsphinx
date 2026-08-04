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

*(Filled in after the fix lands — see below.)*

---

## Task 3 — QUA-01 docstring correction

*(Filled in after the docstring fix lands — see below.)*
