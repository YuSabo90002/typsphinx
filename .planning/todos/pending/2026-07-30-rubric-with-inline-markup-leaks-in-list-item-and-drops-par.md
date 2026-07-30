---
created: 2026-07-30T00:00:00+09:00
title: A rubric containing inline markup leaks in_list_item and drops par() for the rest of the document
area: translator, tests
files:
  - typsphinx/translator.py (`visit_strong` / `depart_strong`, the three single-slot save attributes at lines 1244-1275)
  - typsphinx/translator.py (`visit_rubric` / `depart_rubric`, lines 5034-5076, the dummy-node caller that loses its restore)
  - tests/ (no fixture covers a rubric with an inline-markup child today)
---

## Problem

`visit_strong` saves the caller's state into three **single-slot instance attributes** —
`_strong_was_in_paragraph`, `_strong_was_in_list_item`, `_strong_was_list_item_needs_separator` —
and `depart_strong` restores from them and then `delattr`s them
(`typsphinx/translator.py:1244-1275`). `visit_rubric` / `depart_rubric` reach that same code through
the dummy-`nodes.strong()` delegation (`typsphinx/translator.py:5047, 5065`), so they share those
slots.

When a rubric contains a real `strong` child — `.. rubric:: **強調** 入り見出し` — the nesting is
`rubric(dummy strong) > strong`. The inner `depart_strong` consumes and deletes all three slots
first, so the outer `depart_rubric`'s dummy depart finds nothing to restore. `visit_strong` sets
`self.in_list_item = True` for its children, so after the failed restore `in_list_item` stays `True`
at top level for the **rest of the document**, and every subsequent handler takes the list-item
branch.

Measured 2026-07-30 with a real `sphinx-build -b typst` run:

```rst
.. rubric:: 強調なし見出し

後続の段落A。

.. rubric:: **強調** 入り見出し

後続の段落B。

さらに次の段落C。
```

```typst
strong({text("強調なし見出し")})
linebreak()
par({text("後続の段落A。")})          ← correct

strong({strong({text("強調")})
text(" 入り見出し")})
linebreak()
parbreak()
text("後続の段落B。")                 ← par() wrapper gone
parbreak()
text("さらに次の段落C。")             ← and stays gone for the rest of the document
```

This is a rendering defect, not diff noise: the affected paragraphs are no longer emitted as
paragraphs. It is untracked — no existing fixture covers a rubric with an inline-markup child.

The same class of leak is structurally available to any other dummy-`strong` caller that can contain
a real `strong` child; `desc_signature` is the other one, though its children are `desc_*` nodes
rather than `strong` in the common case. Not measured.

## Not fixed in Phase 36 (deliberate)

Phase 36's only acceptance criterion (ROADMAP SC#2) is that the `desc_signature` / `rubric`
decoupling produces a **byte-identical** `.typ`. Giving each handler its own slot names would repair
this leak as a side effect, but it changes emitted bytes for this construct and would force an
exception into that criterion. Owner decision 2026-07-30, recorded as D-02 in
`.planning/phases/36-shared-emission-seam-cleanup/36-CONTEXT.md`: file this todo, keep the shared
slot names, keep the diff at zero.

## Solution

Give each dummy-`strong` caller its own save slots (`_rubric_was_*`, `_desc_sig_was_*`), or convert
the three attributes to a stack so nesting cannot collide. Either way the fix changes output for the
"rubric containing inline markup" construct, so it needs its own recorded-RED fixture — the RED
assertion being that the paragraph following such a rubric is emitted **without** a `par({…})`
wrapper before the fix.

Natural home: **Phase 39** (Admonition Taxonomy + Rubric Nesting), which owns `rubric` and is
already going to change its emission, so the byte-change is expected there rather than exceptional.

**Measure first when picked up:** real-corpus incidence has not been measured. Count rubrics
carrying inline markup in Sphinx's own `doc/` tree and in this repo's `docs/` before sizing the
work.
</content>
