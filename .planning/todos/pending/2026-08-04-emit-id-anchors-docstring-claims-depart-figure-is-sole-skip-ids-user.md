---
created: 2026-08-04T01:20:00+09:00
title: "`_emit_id_anchors`'s docstring still calls `depart_figure` the \"sole user\" of `skip_ids`, false since Phase 25 and now actively misleading after Phase 42"
area: translator
severity: warning
resolves_phase: null
roadmap_entry: null
source: "Phase 42 / 42-REVIEW.md WR-01 (2026-08-03) -- captioned-table-drops-preceding-target-label; provenance dated by the orchestrator 2026-08-04"
files:
  - typsphinx/translator.py (`_emit_id_anchors` docstring at lines 515-523 -- the false paragraph; "The sole" is line 516, "user is ``depart_figure``" is line 517)
  - typsphinx/translator.py (`depart_figure` at line 2480 -- skip_ids caller #1, the call at line 2518)
  - typsphinx/translator.py (`depart_table` at line 3249 -- skip_ids caller #2, the call at line 3370)
---

## Problem

`_emit_id_anchors`'s docstring states, at lines 515-523:

> ``skip_ids`` lets a caller that ALREADY anchors one of the node's ids by another mechanism
> suppress a duplicate definition here. **The sole user is ``depart_figure``**: a captioned figure
> self-anchors ``ids[0]`` inside its own ``[#figure(...) <label>]`` markup block, ...

There are **two** `skip_ids` callers, not one. Both pass the identical expression
`skip_ids=set(node.get("ids", [])[:1])`:

| Caller | Defined at | Call site |
|---|---|---|
| `depart_figure` | line 2480 | line 2518 |
| `depart_table` | line 3249 | line 3370 |

(Measured 2026-08-04: `grep -n '_emit_id_anchors(' typsphinx/translator.py` returns 21 call sites,
of which exactly those two pass `skip_ids`.)

### Provenance — dated, not guessed

- The "sole user" wording was written at **`2a9fc5d` (Phase 15, 2026-07-13)**, where it was
  **true**: that tree had exactly one `skip_ids=` call site.
- It became **false** at **`ac5c4a8` (Phase 25, 2026-07-24)**, `feat(25-01): figure-wrap captioned
  tables with kind: table + single label` — which added `depart_table` as the second caller while
  leaving the docstring's claim untouched. The stale sentence is visible at lines 366-368 of that
  commit's version of the file.
- So the claim has been wrong for the whole of v0.6.3, v0.6.4, v0.6.5 and v0.7.0.

### Why this is worth fixing now rather than filing and forgetting

Ordinarily a stale docstring is cosmetic. This one is not, for a specific reason: **Phase 42's
entire diff is about the caller the docstring denies exists.** TBL-03 moved `depart_table`'s
`skip_ids` call past `self.in_table = False` because the anchor was being diverted into a deleted
buffer. A maintainer who reads this docstring to understand `skip_ids` is told, in the authoritative
shared-contract location, that the table path does not use it — which is precisely the wrong mental
model for the code that was just changed, and precisely the reader most likely to touch it next.

## Status

Surfaced by Phase 42's code review as WR-01 and deliberately **not** fixed there. The reason was
sequencing, not disagreement: `42-GATE-EVIDENCE-05.md` (SC#4 caption-less byte-invariance) and
`42-SC4-INVARIANTS.md` (SC#6 milestone-invariant sweep) had both already been recorded over a SHA
range ending at the fix commit `e5575f3`. Adding another `typsphinx/translator.py` commit after
those artifacts were written would put a production change outside the range they measured, which
is a worse outcome than a docstring being stale for one more phase.

That constraint expires the moment v0.7.0 is closed. This is a comment-only change with no output
effect, so it needs no GATE-01 fixture (milestone invariant #4 covers node-handler *behaviour*
changes; nothing here alters emitted `.typ`).

## Solution

Rewrite the paragraph to describe both callers. The two cases are genuinely parallel and can share
one explanation — do not simply append "and `depart_table`", because the interesting part is *why*
both need it and *when* the table one fires:

- **Both** wrap their content in a Typst `figure(...)` that self-anchors `ids[0]` as its own
  `<label>`, so re-anchoring `ids[0]` here would define the label twice — a Typst
  "label ... occurs multiple times" compile fatal.
- **Both** still need `ids[1:]` anchored, because docutils' `PropagateTargets` lands an immediately
  preceding `.. _target:`'s id there, and a `:ref:` to it would otherwise dangle.
- **The table caller additionally has a firing-order constraint the figure caller does not** (Phase
  42 / TBL-03): it must run *after* `self.in_table` is cleared, because `add_text` diverts on that
  flag into a buffer that `depart_table` deletes. The inline comments at lines 3344-3370 already
  explain this; the docstring should point at that constraint rather than restate it.

Worth considering while in there: the identical `set(node.get("ids", [])[:1])` expression appearing
at two call sites is a small duplication that a named helper (or a documented constant) would make
self-describing. Optional — the todo's requirement is only that the docstring stop being false.

## Acceptance

- [ ] The `skip_ids` paragraph names both `depart_figure` and `depart_table` and no longer contains
      the word "sole"
- [ ] The shared rationale (self-anchored `ids[0]` → duplicate-label fatal; propagated `ids[1:]` →
      dangling reference) is stated once rather than duplicated per caller
- [ ] The table caller's post-`in_table`-reset firing-order constraint is referenced, pointing at
      the inline comments rather than restating them
- [ ] `grep -c 'skip_ids' typsphinx/translator.py` and the docstring's caller list agree — re-derive
      the list at fix time rather than trusting this todo's table, in case a third caller has
      appeared since 2026-08-04
- [ ] Output is unchanged: comment-only diff, no GATE-01 fixture required, suite still green
