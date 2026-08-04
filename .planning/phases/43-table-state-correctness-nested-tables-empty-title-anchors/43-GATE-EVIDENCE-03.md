# Phase 43 Plan 03 — GATE-01 Evidence (FIG-01)

All command output below was executed in this task's own session, in this worktree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a84cb1cda7db60ab9`), against this
worktree's HEAD at the time (`29c30d04f5ceeee9191660159e2cb7496dcf01c6`, forked from
`gsd/v0.7.1-bug-fix-round` post-Wave-1-merge). Nothing here is transcribed from
`43-RESEARCH.md`/`43-CONTEXT.md` — those documents measured a similar shape on the main tree
in an earlier session with the same sentinel-free hand probe; this file re-measures the same
defect, in this worktree, against this plan's own four-section fixture.

## Docutils measurement: what an explicit `.. legend::` construct actually produces

Before writing the fixture, a direct `publish_doctree` probe was run to confirm docutils'
actual behavior for a legend-with-no-caption shape (the plan's fixture section 4).

**Probe 1 — a bare `.. legend::` RST directive:**

```
rst = '''
.. figure:: img.png

   .. legend::

      NF4LEGENDONLY
'''
```

Result: docutils rejects this outright — `.. legend::` is not a real docutils directive name.
The FIRST body block after a figure's image must be a paragraph or empty comment (docutils
error: "Figure caption must be a paragraph or empty comment"), so this construct never even
reaches a `legend` node.

**Probe 2 — empty comment followed by `.. legend::`:**

```
rst = '''
.. figure:: img.png

   ..

   .. legend::

      NF4LEGENDONLY
'''
```

Result: the empty comment (`..`) IS accepted as the caption placeholder (so this figure has NO
caption), and everything after it becomes the `legend` child — but `.. legend::` inside that
legend is then parsed as an genuinely unknown RST directive (`Unknown directive type "legend"`).
**There is no docutils directive literally named `legend`** — `legend` is a purely STRUCTURAL
classification docutils assigns to whatever body content follows a figure's caption (or, when
there is no caption, follows an empty first-comment placeholder).

**Probe 3 — empty comment followed by a plain paragraph (the actual "legend with no caption"
construct, used in the fixture):**

```
rst = '''
.. figure:: img.png

   ..

   NF4LEGENDONLY
'''
```

`doc.pformat()`:

```
<document source="<string>">
    <figure>
        <image uri="img.png">
        <legend>
            <paragraph>
                NF4LEGENDONLY
```

**This is the correct construct**: a `figure` with an `image` child and a `legend` child that
has NO preceding `caption` sibling at all. Used verbatim as fixture section 4.

## RED — measured against the UNFIXED translator

`typsphinx/translator.py` was **not modified** at the time this RED was captured
(`git status --short` printed only the two new fixture/test paths, confirmed below).

```
$ git status --short
?? tests/fixtures/nested_figure_render_gate/
?? tests/test_nested_figure_render_gate.py
```

### `-b typst` probe (doctree confirmation, no compile)

Command:

```
uv run python -m sphinx -b typst -E tests/fixtures/nested_figure_render_gate /tmp/nfrg-probe
```

Full stderr:

```
WARNING: unknown node type: <legend><figure ids="id2"><image candidates="{'*': 'img.png'}" uri="img.png"/><caption>NF1INNERCAP</caption></figure></legend>
WARNING: unknown node type: <legend><paragraph>NF2LEGENDTEXT</paragraph></legend>
WARNING: unknown node type: <legend><paragraph>NF4LEGENDONLY</paragraph></legend>
```

Three `unknown node type` warnings naming a `legend` node — one per legend-bearing section
(sections 1, 2, 4). Section 3 (image-only control, no legend) emits none. Confirms
`visit_legend`/`depart_legend` do not exist and docutils' `unknown_visit` fires (warn and
continue) exactly as 43-RESEARCH.md Pitfall 4 documents.

### `-b typstpdf` build (the classic-TypstError RED)

Command:

```
uv run python -m sphinx -b typstpdf -E tests/fixtures/nested_figure_render_gate /tmp/nfrg-red
```

**Exit status: 2.**

Full stdout:

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
preparing documents... Template written to /tmp/nfrg-red/_template.typ
done
writing output... [index] done
Copying 1 image file(s)...
Compiling 1 master document(s) to PDF...
```

Full stderr:

```
WARNING: unknown node type: <legend><figure ids="id2"><image candidates="{'*': 'img.png'}" uri="img.png"/><caption>NF1INNERCAP</caption></figure></legend>
WARNING: unknown node type: <legend><paragraph>NF2LEGENDTEXT</paragraph></legend>
WARNING: unknown node type: <legend><paragraph>NF4LEGENDONLY</paragraph></legend>
Typst compilation failed at /tmp/nfrg-red/index.typ: TypstError: expected comma
ERROR: Failed to compile /tmp/nfrg-red/index.typ: Typst compilation failed: TypstError: expected comma
Location: /tmp/nfrg-red/index.typ
Details: expected comma

Extension error!

Versions
========

* Platform:         linux; (Linux-6.18.40-x86_64-with-glibc2.42)
* Python version:   3.13.13 (CPython)
* Sphinx version:   9.1.0
* Docutils version: 0.22.4
* Jinja2 version:   3.1.6
* Pygments version: 2.20.0

Last Messages
=============

    完了
    整合性をチェック中...
    完了
    preparing documents...
    Template written to /tmp/nfrg-red/_template.typ
    done
    writing output... [index]
     done
    Copying 1 image file(s)...
    Compiling 1 master document(s) to PDF...

Loaded Extensions
=================

* sphinx.ext.mathjax (9.1.0)
* alabaster (1.0.0)
* sphinxcontrib.applehelp (2.0.0)
* sphinxcontrib.devhelp (2.0.0)
* sphinxcontrib.htmlhelp (2.1.0)
* sphinxcontrib.serializinghtml (2.0.0)
* sphinxcontrib.qthelp (2.0.0)
* typsphinx (0.7.0)

Traceback
=========

      File ".../typsphinx/builder.py", line 965, in finish
        raise ExtensionError(
            f"typstpdf: {len(failures)} master document(s) failed: {summary}"
        )
    sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: expected comma
    Location: /tmp/nfrg-red/index.typ
    Details: expected comma
```

**`index.pdf` was NOT produced** — build directory listing after the failed run contains only
`.doctrees/`, `_template.typ`, `img.png`, and `index.typ`; no `index.pdf`.

### Emitted `index.typ` (verbatim, full body — RED, byte-identical between the `-b typst` probe
and the `-b typstpdf` build's pre-compile `.typ`)

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
  title: "Nested Figure Render Gate",
  authors: ("typsphinx tests",),
  date: "0.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Nested Figure Render Gate")}) <index:nested-figure-render-gate>]

par({text("This fixture reproduces FIG-01 (Phase 43): a ")
raw("legend")
text(" node (docutils’ name for a figure’s body content beyond its first caption paragraph) has no ")
raw("visit_legend")
text("/")
raw("depart_legend")
text(" handler, so today’s translator emits an ")
raw("image(...)")
text(" call directly juxtaposed against the legend’s unwrapped children – a real ")
raw("typst.compile()")
text(" fatal, not merely a dropped caption (43-RESEARCH.md Pitfall 4).")})

[#heading(level: 2, {text("Figure nested in a figure’s legend")}) <index:figure-nested-in-a-figure-s-legend>]

[#figure(
  image("img.png")[#figure(
  image("img.png"),
  caption: {text("NF1INNERCAP")}
) <index:id2>]


) <index:id1>]


[#heading(level: 2, {text("Plain-text legend, no nested figure")}) <index:plain-text-legend-no-nested-figure>]

par({text("This section is broken TODAY with no nesting involved at all – the root cause is the missing ")
raw("legend")
text(" handler, not the nesting. The fix must not be narrowed to “only when the legend contains a figure” (Pitfall 4).")})

[#figure(
  image("img.png")par({text("NF2LEGENDTEXT")})

,
  caption: {text("NF2CAP")}
) <index:id3>]


[#heading(level: 2, {text("Image-only control")}) <index:image-only-control>]

par({text("This section must stay byte-unchanged by the FIG-01 fix (SC#4). No legend child exists here, so the ")
raw("{...}")
text(" body wrap this phase adds must never apply to it.")})

[#figure(
  image("img.png"),
  caption: {text("NF3CTRLCAP")}
) <index:id4>]


[#heading(level: 2, {text("Legend with no caption")}) <index:legend-with-no-caption>]

par({text("An explicit ")
raw(".. legend::")
text(" RST directive does not exist in docutils – verified this session (")
raw("publish_doctree")
text(" on a bare ")
raw(".. legend::")
text(" block raises “Unknown directive type”). A legend with NO caption is instead produced by an empty comment (")
raw("..")
text(") standing in for the caption slot, followed by a plain paragraph, which docutils then classifies as the figure’s ")
raw("legend")
text(" child with no ")
raw("caption")
text(" sibling at all – verified this session via a direct ")
raw("publish_doctree")
text(" probe (recorded in 43-GATE-EVIDENCE-03.md).")})

figure(
  image("img.png")par({text("NF4LEGENDONLY")})


)



}
```

### Per-sentinel PRESENT/ABSENT table (RED, measured via `grep -c` on the emitted `.typ` above)

| Sentinel | Section | grep -c | Status |
|---|---|---|---|
| `NF1OUTERCAP` | 1 (outer caption) | 0 | **ABSENT** — clobbered: the nested figure's own `visit_figure` resets `self.figure_caption = ""` (a bare scalar), and the inner `depart_figure`'s unconditional teardown resets it again before the outer `depart_figure` ever reads it, so the `if self.figure_caption:` guard is False for the outer figure and no `caption:` argument is emitted at all — confirms CONTEXT's "outer caption disappears entirely" framing IS also true, in addition to the harder compile fatal 43-RESEARCH.md Pitfall 4 measured |
| `NF1INNERCAP` | 1 (inner caption) | 1 | PRESENT |
| `NF2CAP` | 2 (caption) | 1 | PRESENT |
| `NF2LEGENDTEXT` | 2 (legend text) | 1 | PRESENT (streamed unwrapped, but present in the broken `.typ` — the compile still fails on the syntax error, this is a text-search over invalid Typst source, not evidence the document compiles) |
| `NF3CTRLCAP` | 3 (control) | 1 | PRESENT |
| `NF4LEGENDONLY` | 4 (no-caption legend) | 1 | PRESENT (same caveat as `NF2LEGENDTEXT`) |

### Section-3 (image-only control) pre-fix bytes — the byte-invariance control for Task 2

Extracted verbatim from the RED `.typ` above (this exact 4-line span, `sed -n '66,69p'`):

```typst
[#figure(
  image("img.png"),
  caption: {text("NF3CTRLCAP")}
) <index:id4>]
```

Task 2 must reproduce this exact span byte-for-byte after the fix (SC#4).

### RED commit

Committed BEFORE any `typsphinx/` change: `13acf9f24c4afa5de62159dab130471a82e6a79a`
(`git log --format=%H -- tests/fixtures/nested_figure_render_gate` → this SHA;
`git diff <base> 13acf9f24c4afa5de62159dab130471a82e6a79a -- typsphinx/translator.py` is empty).
Recorded via a small follow-up commit that touches only this evidence file, mirroring plan
43-01's precedent for the self-reference problem (the RED commit cannot record its own SHA
without a forbidden amend).

## GREEN — measured after the fix (Task 2)

(Appended by Task 2.)
