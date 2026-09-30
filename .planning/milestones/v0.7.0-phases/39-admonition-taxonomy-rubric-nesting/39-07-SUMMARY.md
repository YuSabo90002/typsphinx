---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 07
subsystem: testing
tags: [pillow, typst-py, greyscale, uat, visual-verification]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 04)
    provides: "scripts/render_admonition_greyscale.py and tests/fixtures/admonition_greyscale_probe/, the render-and-desaturate pipeline this plan drives"
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 05)
    provides: "the bucket-routing fix (five admonition types re-routed to their new buckets) that makes this plan's render evidence of post-phase, not pre-phase, buckets"
provides:
  - "39-ADM04-GREYSCALE.png: the committed, single-channel (Pillow mode 'L') render of the post-fix six-box admonition probe, the first committed binary artifact under .planning/ in this project"
  - "39-ADM04-SIGNOFF.md: the owner's recorded verdict that ADM-04 is met on icon-shape grounds, with the title-band-luminance-is-uniform finding recorded as an explicit caveat"
affects: [39-08-plan (phase-close requirement reconciliation reads this SIGNOFF rather than re-deriving the ADM-04 outcome)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Owner sign-off recorded as a phase artifact (39-ADM04-SIGNOFF.md) rather than as an ephemeral chat exchange, quoting the owner verbatim in the original language plus an English rendering, for a [V]-class requirement with no mechanical stand-in"

key-files:
  created:
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md
  modified: []

key-decisions:
  - "Rendered at the render pipeline's own default PPI (150) — legible for icon shape at normal viewing size without needing an override."
  - "ADM-04 recorded as MET: the owner's operative verdict (relayed in three parts, with a coordinator-issued correction superseding the first two) is that the four kinds ARE distinguishable via icon shape, with title-band luminance recorded as uniform and non-distinguishing — an explicit caveat, not a defect, since ADM-04 only requires some non-hue channel to carry the distinction."
  - "No styling change made and no fallback lever chosen — consistent with D-06/D-08, and now confirmed unnecessary rather than merely deferred, since the requirement is met without either lever."
  - "No pending todo filed. The plan's own acceptance criteria describe filing a todo naming a chosen lever on a NEGATIVE outcome; this plan's actual outcome is positive (met), so that path does not apply."

patterns-established:
  - "For a [V]-class (human-only) requirement, the SIGNOFF artifact records the owner's full verbatim deliberation — including an initial framing that was later corrected — rather than only the final verdict, so a future reader can see how the judgement was reached and that a correction occurred, not just its outcome."

requirements-completed: [ADM-04]

coverage:
  - id: D1
    description: "Post-fix greyscale render of the four-bucket admonition probe, produced from a worktree verified green against the bucket-routing gate before rendering"
    requirement: "ADM-04"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py -x (10/10 passed, run before the render)"
        status: pass
      - kind: other
        ref: "PIL.Image.open(...).mode == 'L' and size == (1240, 1754), verified live"
        status: pass
    human_judgment: false
  - id: D2
    description: "Owner's visual sign-off that the four admonition kinds remain distinguishable in greyscale without hue, carried by icon shape, with title-band luminance recorded as uniform"
    requirement: "ADM-04"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md (owner's verbatim verdict, quoted with English rendering)"
        status: pass
    human_judgment: true
    rationale: "ADM-04 is REQUIREMENTS.md's own [V]-marked (human-only visual UAT) requirement; no automated assertion exists or was offered for it anywhere in this plan (D-06/D-08, this plan's must_haves.prohibitions)."

duration: 20min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 07: ADM-04 Owner Sign-off Summary

**Rendered the post-fix ADM-04 greyscale probe and recorded the owner's sign-off: the four admonition kinds are distinguishable by icon shape, with title-band luminance recorded as uniform (an explicit caveat, not a defect) — ADM-04 is met with no styling change.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-08-02T11:31:27+09:00 (base commit `d20b09c`)
- **Completed:** 2026-08-02T11:51:23+09:00
- **Tasks:** 3 (1 checkpoint, resolved via owner input relayed through the orchestrator across two rounds — an initial verdict and a superseding correction; 2 auto)
- **Files modified:** 2 created, 0 modified

## Accomplishments

- **Task 1:** Confirmed `tests/test_admonition_bucket_render_gate.py -x` green (10/10 passed) in this worktree **before** rendering, verifying the bucket-routing fix (plan 39-05, commits `a6c04ea`/`ecf5ab7`) is present so the render evidences post-phase buckets. Rendered `tests/fixtures/admonition_greyscale_probe/` via `scripts/render_admonition_greyscale.py` at the script's default PPI (150) to `39-ADM04-GREYSCALE.png` — verified Pillow mode `L`, size `1240x1754`, non-empty, showing all six boxes. Produced (but did not commit) a colour reference render to a scratchpad path for optional post-judgement comparison. This task explicitly produced evidence only; it did not verify ADM-04.
- **Task 2 (checkpoint):** Stopped at the blocking-human checkpoint and presented the render, D-06's measured luminance context, and the two available styling levers to the owner without self-approving or pre-selecting a lever. The owner's response arrived in three parts across two coordinator messages: an initial framing suggesting the boxes read as uniform and the requirement might be infeasible, followed by a **coordinator-issued correction** conveying the owner's clarified, operative verdict — the icons differ and DO carry the distinction; luminance is uniform and should be recorded as a caveat, not as the reason for failure.
- **Task 3:** Wrote `39-ADM04-SIGNOFF.md` recording, in order: the ADM-04 requirement text and its `[V]` marking with an explicit no-automated-assertion statement; the artifact's full provenance (path, commit `dedae01`, PPI 150, probe fixture path, and the pre-render green-test confirmation); the BT.601-vs-BT.709 desaturation caveat; the owner's full verbatim deliberation (all three parts, each with an accurate English rendering) with a note reconciling the initial framing against the corrected, operative verdict; the outcome (ADM-04 **MET**, on icon-shape grounds, with the luminance-uniformity finding recorded as an explicit caveat); and the two levers that were presented but ultimately not needed, including the confirmed non-existence of a dashed-border option.

## Task Commits

Each task was committed atomically:

1. **Task 1: Render the committed greyscale artifact from post-fix code** — `dedae01` (feat)
2. **Task 2: Owner sign-off checkpoint** — no commit (checkpoint; the render from Task 1 and the SIGNOFF from Task 3 are the artifacts, per the plan's own instruction that no files are modified for this task)
3. **Task 3: Record the sign-off as a phase artifact** — `06cb608` (docs)

_No TDD tasks in this plan; each auto task is a single commit._

## Files Created/Modified

- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png` — the committed single-channel (mode `L`, 1240x1754px) desaturated render of the post-fix six-box admonition probe. The first committed binary artifact anywhere under `.planning/` in this project.
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md` — the recorded owner sign-off: requirement text, artifact provenance, the BT.601-vs-BT.709 caveat, the owner's full verbatim deliberation (three parts, each with an English rendering) with the corrected verdict called out as operative, the MET outcome with the luminance-uniformity caveat, and the two considered-but-unneeded styling levers.

## Decisions Made

- **PPI 150 (the pipeline's own default) was used without override** — the render was legible for icon shape at normal viewing size, so no higher-resolution re-render was needed.
- **ADM-04 recorded as MET, not as "accepted-as-is."** The checkpoint response arrived in two rounds: the first (relayed via the orchestrator) reported the owner could not distinguish the kinds at all and had accepted that state without choosing a lever; a second, coordinator-issued correction then conveyed the owner's clarification that the icons DO carry the distinction and that the earlier "everything reads the same" remark was specifically about title-band luminance, not about overall distinguishability. The corrected, operative verdict — MET via icon shape, with luminance uniformity recorded as a caveat — is what `39-ADM04-SIGNOFF.md` records; the initial framing is preserved in the SIGNOFF as deliberation history, explicitly marked as superseded, so a future reader sees both what was first reported and what was ultimately decided.
- **No pending todo filed.** The plan's acceptance criteria describe filing a todo naming a chosen lever only on a **negative** outcome (owner cannot distinguish the kinds). Since the corrected outcome is positive (ADM-04 met), that path does not apply — there is no lever to name and no follow-up work to defer.

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing functionality, or blocking issues were encountered in this plan's own tasks.

### Process Note (not a Rule 1-4 deviation, but worth recording explicitly)

**Checkpoint resolution required two coordinator messages, the second correcting the first.** The plan anticipated a single owner response resolving cleanly to either "met" or "not met, with a chosen lever, filed as a todo." What was actually relayed was: (1) an initial verdict describing the boxes as indistinguishable and the requirement as possibly infeasible, with acceptance and no lever chosen; then (2) an explicit correction stating the initial relay was wrong on the central point — the kinds ARE distinguishable via icon shape — and providing the actual operative verdict. This executor did not choose between the two accounts; it followed the corrected, later instruction as authoritative (the coordinator explicitly labeled it "CORRECTION — supersedes my previous message") and rewrote the SIGNOFF content that had already been drafted under the first framing before committing anything reflecting the superseded version. No SIGNOFF commit was made under the pre-correction framing — the rewrite happened before the first `git commit` for Task 3, so git history for this plan shows only the corrected verdict.

---

**Total deviations:** 0 auto-fixed. One process note documenting a mid-execution correction to the relayed checkpoint answer, handled without self-judgment by treating the coordinator's explicit correction as authoritative.
**Impact on plan:** None on scope — no styling change, no lever, no todo in either account of the owner's answer. The only difference between the two accounts is the ADM-04 outcome itself (met vs. accepted-as-is-but-not-met), which is exactly the information this checkpoint exists to capture, and the corrected account is what is recorded.

## Issues Encountered

None beyond the checkpoint-answer correction noted above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- ADM-04 is recorded as **complete/met** in this plan's artifacts. Plan 39-08's phase-close and any `REQUIREMENTS.md` reconciliation should read `39-ADM04-SIGNOFF.md`'s status line directly (`MET — distinguishable by icon shape...`) rather than re-deriving the outcome, and should check ADM-04's box in `REQUIREMENTS.md`.
- The uniform-luminance finding is recorded as a caveat in the SIGNOFF for any future reader (e.g., a later phase considering a colour or contrast change) — it is an accepted, documented property of the current design, not an open item.
- No blockers. No follow-up lever work is queued, since none was needed.

## Self-Check: PASSED

Both claimed files verified present on disk:
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png` — FOUND (35570 bytes, mode `L`, 1240x1754)
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md` — FOUND

Both task commit hashes verified present in `git log --oneline`:
- `dedae01` — FOUND
- `06cb608` — FOUND

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*
