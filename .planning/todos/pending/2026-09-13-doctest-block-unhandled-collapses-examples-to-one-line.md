---
created: 2026-09-13T01:12:37.506Z
title: "`doctest_block` has no translator handler — `>>>` examples fall through `unknown_visit` and collapse onto one line of plain text"
area: translator
severity: major
source: Issue #91 investigation (2026-09-13) — a real sphinx-autoapi build of typsphinx's own package
files:
  - typsphinx/translator.py:5819  # unknown_visit() — where doctest_block currently lands (warning only, children still visited)
  - typsphinx/translator.py:5832  # unknown_departure()
---

## Problem

`TypstTranslator` has no `visit_doctest_block` / `depart_doctest_block` (`grep -n doctest
typsphinx/translator.py` is empty). docutils emits `doctest_block` for any `>>>` block in reST —
most commonly Google/NumPy-style `Examples:` sections in docstrings rendered by sphinx-autoapi,
`sphinx.ext.autodoc` or napoleon.

The node falls through to `unknown_visit()` (`translator.py:5819`), which logs
`WARNING: unknown node type: <doctest_block ...>` and continues. The children (`Text`) are still
visited, so the text survives, but as ordinary inline text: **every line break is lost** and the
whole example becomes one `text("…")` run. The PDF compiles; the example is unreadable.

**Measured 2026-09-13** (scratchpad project, not committed): `extensions = ["autoapi.extension",
"typsphinx"]`, `autoapi_dirs = [<repo>/typsphinx]`, built with
`LC_ALL=C uv run --with sphinx-autoapi sphinx-build -b typstpdf src out` on `main` @ `4dfdd664`.
Build succeeded, 118-page PDF, 48 warnings of which **17 are `unknown node type: <doctest_block`**
(plus one `<problematic>`, caused by a malformed inline literal in typsphinx's own docstring, not a
translator gap). Example of the emitted Typst (from `autoapi/typsphinx/builder/index.typ`):

```
terms.item(text("Examples:"), {text(">>> _escapes_outdir(\"manuals/guide\") False >>> _escapes_outdir(\"../escape\") True >>> ...")})
```

The source docstring has one `>>>` prompt and one result per line.

Found while re-measuring Issue #91 (a 0.4.3-era report about autoapi output). Both of #91's own
symptoms (footnote not emitted; stray `+` in a union-typed signature) do **not** reproduce on
current `main`; this defect is separate and was not in the report.

## Solution

TBD. Likely shape: treat `doctest_block` like a `literal_block` with language `python` (or
`pycon`) — emit a `raw(block: true, lang: …)` so line breaks and monospace are preserved and codly
styles it like other code blocks — then `raise nodes.SkipNode` so the children are not re-emitted as
text. Check that it respects the same separator discipline as `visit_literal_block` when it sits
inside a definition-list body / field body (the `terms.item(...)` context above), since that is
exactly where autoapi places it.

Gate per the standing GATE-01 bar: a fixture with a `>>>` block in a plain paragraph context and in
a definition-list/field body, recorded RED (line-structure assertion on the emitted `.typ`, plus no
`unknown node type` warning) before the handler lands, and a real `typst.compile()` of the result.
