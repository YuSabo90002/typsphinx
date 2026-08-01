---
created: 2026-07-30T00:00:00+09:00
resolves_phase: 39
title: A rubric containing inline markup leaks in_list_item and drops par() for the rest of the document
area: translator, tests
files:
  - typsphinx/translator.py (`visit_strong` / `depart_strong`, the three single-slot save attributes, lines 1203-1280)
  - typsphinx/translator.py (`visit_rubric` / `depart_rubric`, lines 5120-5232, post-Phase-36 owns its own copy of the same save/restore logic under the same attribute names)
  - typsphinx/translator.py (`visit_desc_signature` / `depart_desc_signature`, lines 4669-4779, likewise owns its own copy under the same attribute names since Phase 36)
  - tests/ (no fixture covers a rubric with an inline-markup child today)
---

## Problem

`visit_strong` saves the caller's state into three **single-slot instance attributes** —
`_strong_was_in_paragraph`, `_strong_was_in_list_item`, `_strong_was_list_item_needs_separator` —
and `depart_strong` restores from them and then `delattr`s them (`typsphinx/translator.py:1203-1280`).

**Corrected post-Phase-36 (2026-08-01):** before Phase 36, `visit_rubric` / `depart_rubric` reached
that same code through a dummy-`nodes.strong()` delegation, so the leak below happened because two
*different node handlers* (the dummy delegation and a real inner `strong` child) shared one physical
method's slots. Phase 36 (ADM-06, D-01/D-02) removed the delegation: `visit_rubric` / `depart_rubric`
and `visit_desc_signature` / `depart_desc_signature` now each hold their **own verbatim copy** of
`visit_strong`'s/`depart_strong`'s body (D-01: deliberate triplication, not a refactor). **Per D-02,
that copy was required to keep using the exact same `_strong_was_in_paragraph` /
`_strong_was_in_list_item` / `_strong_was_list_item_needs_separator` attribute names** — renaming them
per handler would have changed emitted bytes for the "rubric containing inline markup" construct and
put an exception into Phase 36's byte-identity acceptance criterion (SC#2). **The decoupling did NOT
fix this leak.** The mechanism is unchanged in cause and unchanged in behavior: three separate handler
pairs (`visit_strong`/`depart_strong`, `visit_rubric`/`depart_rubric`,
`visit_desc_signature`/`depart_desc_signature`) now each read and write the *same* instance-level
slots, so the identical collision the pre-Phase-36 text described still occurs whenever one of these
constructs nests inside another — a rubric containing a real `strong` child is still
`rubric-body(shares slots) > strong(shares slots)`, and the inner `depart_strong` still consumes and
deletes all three slots before the outer `depart_rubric`'s restore runs. `visit_strong` sets
`self.in_list_item = True` for its children, so after the failed restore `in_list_item` stays `True`
at top level for the **rest of the document**, and every subsequent handler takes the list-item
branch. A reader who assumes the Phase 36 decoupling "cut the seam" and therefore also separated this
state would be wrong — the seam that was cut was the delegation *call*, not the shared *attribute
names*, and D-02 chose to keep the names shared specifically to hold Phase 36's diff at zero.

Measured 2026-07-30 with a real `sphinx-build -b typst` run (pre-Phase-36 translator; the emitted
shape below is unaffected by Phase 36's decoupling, since the decoupling changed no bytes):

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

**Post-Phase-36 reality:** the same leak is now reachable through three handler pairs sharing one set
of slots (`visit_strong`, `visit_rubric`, `visit_desc_signature`, each paired with its own depart),
not just through `rubric`'s old dummy-node delegation. `desc_signature`'s children are `desc_*` nodes
rather than `strong` in the common case, so its exposure is structural but not measured; the rubric
case above remains the only measured reproduction.

## Not fixed in Phase 36 (deliberate)

Phase 36's only acceptance criterion (ROADMAP SC#2) was that the `desc_signature` / `rubric`
decoupling produces a **byte-identical** `.typ`. Giving each handler its own slot names would repair
this leak as a side effect, but it changes emitted bytes for this construct and would have forced an
exception into that criterion. Owner decision 2026-07-30, recorded as D-02 in
`.planning/phases/36-shared-emission-seam-cleanup/36-CONTEXT.md`: file this todo, keep the shared
slot names even after the decoupling landed, keep the diff at zero. Phase 36 completed 2026-08-01
with the decoupling applied exactly this way (see `36-GATE-EVIDENCE.md`'s "Post-decoupling diff"
section) — this todo's fix was correctly deferred, not accidentally missed.

## Solution

Give each handler its own save slots (`_rubric_was_*`, `_desc_sig_was_*`, leaving `_strong_was_*` for
`visit_strong`/`depart_strong` itself), or convert the three attributes to a stack so nesting cannot
collide. Either way the fix changes output for the "rubric containing inline markup" construct, so it
needs its own recorded-RED fixture — the RED assertion being that the paragraph following such a
rubric is emitted **without** a `par({…})` wrapper before the fix. Because Phase 36 now gives
`desc_signature` and `rubric` their own independent copies of this logic (rather than one shared
dummy-delegated body), the rename can be done per-handler without touching `visit_strong` itself or
the other decoupled handler — the three copies no longer have to move in lockstep.

Natural home: **Phase 39** (Admonition Taxonomy + Rubric Nesting), which owns `rubric` and is
already going to change its emission, so the byte-change is expected there rather than exceptional.

**Measure first when picked up:** real-corpus incidence has not been measured. Count rubrics
carrying inline markup in Sphinx's own `doc/` tree and in this repo's `docs/` before sizing the
work. This measurement is part of picking the todo up, not already done.
</content>
