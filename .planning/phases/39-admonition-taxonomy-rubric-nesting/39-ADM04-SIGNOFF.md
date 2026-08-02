# ADM-04 Sign-off: Greyscale Distinguishability

**Date:** 2026-08-02
**Plan:** 39-07
**Status: MET — distinguishable by icon shape. Luminance is uniform and carries no
signal (explicit recorded caveat), consistent with ADM-04's own wording that the
distinction must be carried by icon and border, not hue.**

**Amended 2026-08-02 under gap G-39-1 — see "Amendment 2026-08-02 (gap G-39-1):
red-family sub-division re-take" below for the now-operative verdict.**

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

---

## Amendment 2026-08-02 (gap G-39-1): red-family sub-division re-take

**Date:** 2026-08-02
**Plan:** 39-12
**Status: MET — re-taken and confirmed. The three red-family kinds (`error`, `danger`,
`attention`), now three distinct clue functions rather than one, remain distinguishable
in the greyscale render. No styling change was made and no fallback lever was needed.**

This section is an amendment, appended below the 2026-08-02 plan-39-07 verdict. Nothing
above this line has been edited, reworded, renumbered or deleted, apart from the one-line
pointer added directly under the status paragraph at the top of this file.

### A1. Requirement under judgement

Quoted verbatim from `.planning/REQUIREMENTS.md` (lines 134–140), as it reads after plan
39-10's amendments:

> - [x] **ADM-04** [V]: Admonition types stay distinguishable **in greyscale**. The four
>   title-band tints are all mid-high-luminance pastels and desaturate to similar greys, so
>   the distinction must be carried by icon and border, not hue alone. **Met on icon-shape
>   grounds** — the owner's recorded sign-off (`39-ADM04-SIGNOFF.md`) confirms the four
>   kinds are distinguishable via icon shape in the greyscale render; the title-band
>   luminance itself is uniform and carries no distinguishing signal, recorded as an
>   explicit caveat, not a defect, since the requirement only needs *some* non-hue channel
>   to carry the distinction and icon shape does.

`[V]` marks this as REQUIREMENTS.md's own human-only, visual-UAT verification class, exactly
as it did for the original sign-off above. **No automated assertion exists or was offered
as a stand-in for the owner's judgement anywhere in plan 39-12**, consistent with that
plan's `must_haves.prohibitions` and with D-06/D-08 (`39-CONTEXT.md`).

### A2. Why the sign-off was re-taken

The artifact the 2026-08-02 (plan 39-07) verdict above was taken against showed `attention`,
`danger` and `error` folded onto a single clue function (`error(...)`), per then-current
decision D-03. That artifact was a faithful picture of the phase as it was built at the time
and the verdict above **remains the correct verdict for that build** — it is not being
withdrawn or corrected as an error.

Gap G-39-1 reverses D-03: under D-03-R, the red family sub-divides into three distinct clue
functions (`danger`, `memo`, `error` — see `39-CONTEXT.md`'s "Reversal — recorded 2026-08-02
(gap G-39-1)"). An artifact showing one folded red box cannot evidence a taxonomy in which
there are three, so the question ADM-04 asks had to be asked again against a new render taken
from the tree that actually carries the sub-division. **The verdict below is the one now
operative for the phase as it ships; the verdict above is superseded, not erased.**

### A3. Provenance

- **Artifact:** `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png`
  (same path; re-rendered — the previous artifact's history stays in git)
- **Rendered at commit:** `c02d9ec` (this worktree, branch
  `worktree-agent-a013108e8057e2f1f`), taken at the same base commit
  (`ca946697786c`) the pre-render gate check ran against
- **Render size:** 36051 bytes (the previously committed artifact was 35570 bytes — the
  byte difference is direct evidence that a real re-render occurred, not a re-commit of the
  same picture)
- **PPI used:** 150 (the script's own default — unchanged from the original render), mode
  `L`, dimensions `1240x1754`
- **Probe fixture:** `tests/fixtures/admonition_greyscale_probe/index.rst`, now carrying
  **seven** boxes (note, tip, seealso, warning, then error, danger, attention contiguous at
  the end — one more box than the six the original sign-off's probe carried)
- **Pre-render gate confirmation:** `uv run pytest
  tests/test_admonition_bucket_render_gate.py tests/test_admonition_locale_title_precedence_gate.py -x`
  was run in this worktree and confirmed green (21/21 passed) **before** the render was
  taken, in the same worktree, at the same base commit — confirming the render evidences
  D-03-R's sub-divided red family, not D-03's folded one (mirroring the T-39-10-style
  precondition the original sign-off's §2 recorded).

### A4. Desaturation caveat (restated)

As with the original sign-off, this judgement was made **against the rendered artifact**,
never against `39-CONTEXT.md`'s D-06 luminance table. That table was computed with the
ITU-R **BT.709** relative-luminance weights (`0.2126R + 0.7152G + 0.0722B`), while this
render's desaturation used Pillow's `Image.convert("L")`, which applies the ITU-R **BT.601**
luma weights (`0.299R + 0.587G + 0.114B`). The two are close but not identical, so the
rendered greys do not exactly match any predicted percentage for the new red-family
accents (`danger` peach `#fe640b`, `attention`/`memo` maroon `#e64553`, `error` red
`#d20f39`) — that mismatch is expected, not a defect, for the same reason the original
sign-off recorded it: the table is analytical scaffolding, never a render target.

### A5. The owner's answer (verbatim)

The owner was shown the committed greyscale render (`39-ADM04-GREYSCALE.png`, this
amendment's provenance in §A3) at normal viewing size and asked the following, in order,
per the plan's checkpoint:

1. Without reading body text and without the colour version — can the four groups be told
   apart using only icon shape and the left border?
2. The last three boxes are the red family — `error`, `danger`, `attention`, in that order.
   Do these three read as three separate kinds, or do any two merge? If any two merge, name
   the specific pair — in particular, does the `attention` box's maroon-family title band
   read as separate from, or merge/collide with, the `error` box's red title band? Answer
   for that pair by name, not only for the four groups collectively.
3. Do the unchanged groups still separate — does `seealso` still read as the same kind as
   `tip`, and are all four groups (note / success / warning / red-family) still tellable
   apart?
4. If some pair cannot be distinguished: which pair, and which lever would be considered —
   per-bucket border thickness, or per-bucket header-band colour? (A dashed border is not
   available: the package's box left edge takes only a thickness, a paint and a cap.)

Approval was explicitly defined to the owner as: "if all read as separate, reply approved."

**The owner's verbatim response, in full, was exactly one word:**

> approved

No further commentary was offered by the owner and none is attributed to them here. In
particular: the owner did not volunteer prose naming the `attention`/`error` pair
specifically, nor any other per-pair statement — the single word above is the entirety of
the recorded response. What makes it sufficient for the "name the pair" element of question
2 is that question 2 itself named the `attention`/`error` pair explicitly and by name, and
`approved` was given as the answer to all four questions as posed, including that one. This
record states plainly what was asked and what was answered, and does not imply the owner
said more than they did.

A colour reference render of the same probe was mentioned to the owner as available for
optional comparison after questions 1–3, per the plan's own sequencing (colour should not
prime the greyscale judgement). It was not committed to the repository and no anchoring
prediction or computed number (luminance, contrast ratio or pixel difference) was presented
to the owner before or with this question, consistent with D-06/D-08 and this plan's
prohibitions.

**Date recorded:** 2026-08-02

### A6. Outcome

**ADM-04 remains MET**, now under the sub-divided red-family taxonomy (D-03-R). The owner
approved the render as presented, including the explicit adjacency question naming the
`attention`/`error` pair — no pair was reported as merging or colliding, and the owner
requested no fallback lever.

- **No styling change was made.** `git diff --stat -- typsphinx/` is empty for this plan's
  commits — consistent with D-06 and unchanged from the original sign-off.
- **No fallback lever was chosen.** Neither the per-bucket border-thickness lever nor the
  per-bucket header-band-colour lever (§6 above, restated in §A7 below) was needed or
  selected — the owner reported no indistinguishable pair, so no lever question arose.
- **No pending todo is filed.** The outcome is positive; there is no follow-up work to
  defer under gap G-39-1.
- **The 2026-08-02 (plan 39-07) verdict above is superseded, not erased**, by this
  amendment as the now-operative record for ADM-04.

### A7. Levers considered before the decision

The same two styling levers recorded in §6 above were presented to the owner again before
this decision, per D-06/D-08, in case the sub-divided red-family render failed to
distinguish the kinds:

1. **Per-bucket border (stroke) thickness** — increasing `clue()`'s left-edge thickness
   per bucket.
2. **Per-bucket header-band colour** — an explicit `header-color:` override per bucket.

**A dashed left border remains unavailable as an option**, per the same verification against
the pinned gentle-clues 1.3.1 sources recorded in §6.

Neither lever was needed: the owner's approval of the render, including the explicit
`attention`/`error` adjacency question, satisfied ADM-04 without either.
