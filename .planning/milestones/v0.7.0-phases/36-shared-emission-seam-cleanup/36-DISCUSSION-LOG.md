# Phase 36: Shared-Emission Seam Cleanup - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-30
**Phase:** 36-Shared-Emission Seam Cleanup
**Areas discussed:** Decoupling shape (helper granularity), MATH-02 RED evidence

---

## Gray area selection

Four areas were offered; the owner selected two.

| Area | Description | Selected |
|------|-------------|----------|
| Decoupling shape (helper granularity) | How to split `visit_strong`'s ~40-line body across `desc_signature` / `rubric` | ✓ |
| MATH-02 fix option | todo option (a) drop the flag vs (b) gate the unconditional `"\n\n"` | |
| MATH-02 RED evidence | ROADMAP SC#3 demands a PDF-extracted-text RED that measurement says is impossible | ✓ |
| Byte-identity proof procedure | Which fixture, how to split plans, where evidence lives | |

The two unselected areas were decided at Claude's discretion (see below).

---

## Decoupling shape

**Clarification round.** The first framing was rejected — the owner asked what `desc_signature`,
`rubric` and `strong` actually are. Answered by building a live fixture through
`sphinx-build -b typst` and showing all three emitting the identical `strong({ … })` wrapper, then
explaining that `visit_desc_signature` / `visit_rubric` construct a throwaway `nodes.strong()` and
call `visit_strong` on it (`translator.py:4684, 4693, 5047, 5065`).

| Option | Description | Selected |
|--------|-------------|----------|
| Parameterised shared helper | `_open_inline_wrapper("strong({")` called by all three; Phase 37 swaps one argument | |
| Un-parameterised shared helper | `_enter_bold_wrapper()` called by all three; parameterisation deferred to Phase 37 | |
| Copy into each handler | No sharing; three independent copies of the state machine | ✓ |

**User's choice:** Copy into each handler.
**Notes:** Maximises freedom for Phases 37 and 39, which will take `desc_signature` and `rubric` in
different directions. Accepted cost is a third copy of the same state machine — the same class of
hazard as the repo's three-place `@preview` version sync.

### Follow-up: the `par()`-loss bug

Surfaced by measurement while working out which state slots the copies should use. `visit_strong`
saves caller state into three single-slot instance attributes and `depart_strong` `delattr`s them,
so a rubric containing a real `strong` child loses the outer restore and leaks `in_list_item = True`
for the rest of the document — every subsequent paragraph loses its `par({…})` wrapper.

| Option | Description | Selected |
|--------|-------------|----------|
| File a todo, don't fix here | Keep the shared slot names, keep the diff at zero | ✓ |
| Fix in Phase 36 | Per-handler slot names; needs an explicit SC#2 carve-out and its own RED fixture | |
| Measure corpus incidence first | Count real rubrics carrying inline markup, then decide | |

**User's choice:** File a todo; do not fix in Phase 36.
**Notes:** Fixing it changes emitted bytes for that construct, which would put an exception into
SC#2 — the phase's only acceptance criterion.

### Follow-up: copy fidelity

A third question (verbatim copy vs pruning branches unreachable from `desc_signature` / `rubric`)
was raised and withdrawn. The owner's reply settled it directly: *"ここでは分離だけ実施して
Phase 39 で本式バグ修正するのだから、ここではとりあえずバイトに差が出ないように分離するだけ"* —
the byte-zero-delta constraint already determines the answer, and the implementation form is a
planner call. Recorded as D-03 rather than re-asked.

---

## MATH-02 RED evidence

**Measurement presented before the question.** A list-item block-math fixture was built through
`sphinx-build -b typst`, the redundant blank line removed by hand from the emitted `.typ`, and both
variants compiled through the real `typst.compile()` and text-extracted with `pypdf`:

| | current | intended post-fix |
|---|---|---|
| PDF bytes | 22,855 | 22,855 (identical) |
| pages | 3 | 3 |
| extracted text | identical | identical |

So SC#3's "recorded RED on the compiled PDF's extracted text" cannot exist — it is green before and
after. Separately, the redundant blank line was measured to be *after* the math, not before, so
SC#3's wording is also inverted.

| Option | Description | Selected |
|--------|-------------|----------|
| `.typ` structural assertion + PDF invariance guard | RED on the emitted `.typ`; PDF asserts text unchanged across the fix | ✓ |
| `.typ` structural assertion only | Drop the PDF condition from SC#3 entirely | |
| Keep SC#3, hunt for a PDF-visible RED | Find a context where the blank line does affect rendering | |

**User's choice:** `.typ` structural assertion + PDF invariance guard.
**Notes:** Turns "this change is inert" from a claim into a test.

### Follow-up: the ROADMAP wording

| Option | Description | Selected |
|--------|-------------|----------|
| Amend ROADMAP via `/gsd-phase` | Correct SC#3 in place | ✓ |
| Record the correction in CONTEXT only | Leave ROADMAP as history | |
| Both | Amend ROADMAP and record the rationale in CONTEXT | |

**User's choice:** Amend ROADMAP via `/gsd-phase`.
**Notes:** The verifier reads ROADMAP success criteria directly; a stale SC re-opens the argument at
verify time.

---

## Claude's Discretion

- **MATH-02 fix option (unselected area).** Take the todo's option (a), and additionally reset
  `list_item_needs_separator` to `False`. Measured basis: option (b) yields zero blank lines rather
  than one, missing SC#3 as corrected; and a naive (a) still leaves two blank lines on the
  `:label:`-carrying path, because `_emit_id_anchors` sets the flag before the math is emitted.
- **Byte-identity proof procedure (unselected area).** Split into two plans and two commits —
  decoupling (byte-identical) first, MATH-02 (byte-changing) second — with SC#2's recorded diff
  taken against the decoupling commit alone.
- **Todo-match noise.** `todo.match-phase 36` returned four keyword false positives alongside the
  one real record; they were not put to the owner as a question, only recorded as reviewed.

## Deferred Ideas

- **`par()` loss after a rubric containing inline markup** — untracked rendering defect, measured
  this session, to be filed as a todo. Natural home is Phase 39, which owns `rubric`. Real-corpus
  incidence not yet measured.
</content>
