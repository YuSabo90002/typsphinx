# ADM-04 Sign-off: Greyscale Distinguishability

**Date:** 2026-08-02
**Plan:** 39-07
**Status: MET — distinguishable by icon shape. Luminance is uniform and carries no
signal (explicit recorded caveat), consistent with ADM-04's own wording that the
distinction must be carried by icon and border, not hue.**

## 1. Requirement under judgement

Quoted verbatim from `.planning/REQUIREMENTS.md` (lines 120-122):

> - [ ] **ADM-04** [V]: Admonition types stay distinguishable **in greyscale**. The four
>   title-band tints are all mid-high-luminance pastels and desaturate to similar greys, so
>   the distinction must be carried by icon and border, not hue alone.

`[V]` marks this as REQUIREMENTS.md's own human-only, visual-UAT verification class. **No
automated assertion exists anywhere in this plan or its tooling (plan 39-04) for ADM-04
itself, and none was offered as a stand-in for the owner's judgement** — consistent with
this plan's `must_haves.prohibitions` and D-06/D-08 (`39-CONTEXT.md`).

## 2. Artifact provenance

- **Artifact:** `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png`
- **Committed at:** `dedae01` (this worktree, branch `worktree-agent-ae3a0b4df278d4085`,
  based on `d20b09c` which carries plan 39-05's bucket-routing commits `a6c04ea` and
  `ecf5ab7`)
- **PPI used:** 150 (the script's own default — `scripts/render_admonition_greyscale.py`'s
  `DEFAULT_PPI`; not overridden, since the default render was legible for icon shape at
  normal viewing size: 1240x1754px, mode `L`)
- **Probe fixture:** `tests/fixtures/admonition_greyscale_probe/` (one box per bucket:
  note / tip / seealso / warning / error / attention)
- **Bucket-routing precondition:** `uv run pytest tests/test_admonition_bucket_render_gate.py -x`
  was run in this worktree and confirmed green (10/10 passed) **before** the render was
  taken, confirming the render evidences post-phase bucket assignments (39-05), not
  pre-phase ones (T-39-10 mitigation).

## 3. Desaturation caveat (restated)

The sign-off below was made **against the rendered artifact**, never against
`39-CONTEXT.md`'s D-06 luminance table. That table was computed with the ITU-R **BT.709**
relative-luminance weights (`0.2126R + 0.7152G + 0.0722B`), while the artifact's
desaturation used Pillow's `Image.convert("L")`, which applies the ITU-R **BT.601** luma
weights (`0.299R + 0.587G + 0.114B`). The two are close but not identical, so the rendered
greys do not exactly match the table's predicted percentages — that mismatch is expected,
not a defect, and is precisely why the table is analytical scaffolding rather than a
render target (D-06).

## 4. Owner's answer (verbatim, with English rendering)

The owner's response was relayed through the orchestrator across three parts, in the
order given. All three are quoted character-for-character below, each followed by an
accurate English rendering that preserves the nuance rather than paraphrasing it away.
The first two record the owner's initial deliberation; the third is the owner's
clarification and is the **operative, recorded verdict** (see the note at the end of
this section).

**Part 1 — initial reaction:**

> 「見分けられんが、もう仕方ない感ある」

English rendering: *"I can't tell them apart, but there's a sense that it just can't be
helped."*

**Part 2 — first framing, before clarification:**

> 「見た感じ4バケットどころか全部一緒なので、グレースケールで区別がつくという
> requirementはハナから無理な可能性が出てきた。したがって、受容する」

English rendering: *"From what I can see, not just the four buckets but everything reads
as the same, so it's starting to look like the requirement that they be distinguishable
in greyscale may have been impossible from the outset. Therefore, I accept [the current
state]."*

**Part 3 — clarification, the corrected and operative verdict:**

> 「アイコンは異なるため区別はつく、明度は一緒として記録せよ」

English rendering: *"Because the icons differ, [the kinds] are distinguishable — record
the brightness/luminance as uniform."*

**Reconciling Parts 1-2 with Part 3:** the owner's first pass ("全部一緒") was a
description of what the *title-band luminance* looks like — uniform, carrying no
distinguishing signal — not a verdict that the boxes are indistinguishable overall. Part
3 clarifies that the icon shapes, which are a separate visual channel from the title-band
luminance, do carry the distinction, and instructs that the luminance-uniformity
observation be recorded as a caveat rather than as the reason ADM-04 fails. **The
recorded verdict in §5 below is Part 3, not Parts 1-2.**

**Date recorded:** 2026-08-02

## 5. Outcome

**ADM-04 is MET.** The owner can distinguish the four kinds in the greyscale render, and
the distinguishing signal is the icon shape (`info`/`tip`/`warning`/`crossmark` icons
differ by shape and are baked-in raster fills, unaffected by desaturation) — which is
exactly the channel ADM-04 itself names ("the distinction must be carried by icon and
border, not hue alone").

**Explicit recorded caveat: luminance is uniform and carries no distinguishing signal.**
The owner separately observed that the title-band brightness reads as the same across
boxes in this render ("明度は一緒") — consistent with D-06's measured 5.4-percentage-point
band spread being too narrow to serve as a usable greyscale signal on its own. This is
recorded as a fact about the render, not as a defect: ADM-04 does not require luminance to
carry the distinction, only that *some* non-hue channel does, and the icon shape channel
does.

Consequences:

- **No styling change is made.** `git diff --stat -- typsphinx/` is empty for this plan's
  commits (verified below) — consistent with D-06's no-styling-change decision, now
  confirmed sufficient rather than merely attempted.
- **No fallback lever is chosen.** Neither the per-bucket border-thickness lever nor the
  per-bucket header-band-colour lever (§6 below) was needed or selected.
- **No pending todo is filed.** Since ADM-04 is met, there is no follow-up work to defer;
  filing a todo would misrepresent a met requirement as open.
- **ADM-04 is recorded as met**, on icon-shape grounds, with the uniform-luminance
  observation carried forward as an explicit caveat for any future reader — so that
  "luminance doesn't distinguish the buckets" is understood as an accepted, recorded
  property of this design rather than a latent defect someone rediscovers later. Plan
  39-08's phase-close and `REQUIREMENTS.md` reconciliation should mark ADM-04 complete on
  this basis.

## 6. Levers considered before the decision

Two styling levers were presented to the owner before the decision, per D-06/D-08
(`39-CONTEXT.md`), so the owner could choose against the actual render rather than a
lever pre-agreed in advance, in case the render failed to distinguish the kinds:

1. **Per-bucket border (stroke) thickness** — increasing `clue()`'s left-edge thickness
   per bucket to widen the luminance/contrast spread between buckets' left strokes.
2. **Per-bucket header-band colour** — an explicit `header-color:` override per bucket,
   independent of the `accent-color` the icon/stroke derive from.

**A dashed left border does not exist as an option.** Verified against the pinned
gentle-clues 1.3.1 sources (`~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/clues.typ`):
`clue()`'s left edge takes only a thickness, a paint, and a cap — no dash pattern
parameter exists on that edge.

Neither lever was needed: the icon-shape channel alone satisfied ADM-04, per the owner's
verdict in §5.

## Verification of this plan's non-styling scope

```
$ git diff --stat -- typsphinx/ tests/
(empty)
```

No file under `typsphinx/` or `tests/` was modified by this plan's commits, consistent
with ADM-04 being met without any styling change.
