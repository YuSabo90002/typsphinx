---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 12
subsystem: testing
tags: [pillow, typst-py, greyscale, uat, visual-verification, gap-closure]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 04)
    provides: "scripts/render_admonition_greyscale.py and tests/fixtures/admonition_greyscale_probe/, the render-and-desaturate pipeline this plan reuses unchanged apart from the fixture's box list"
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 07)
    provides: "39-ADM04-SIGNOFF.md, the file this plan appends a dated amendment to; the original 2026-08-02 verdict and its three verbatim Japanese quotations survive intact"
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 11)
    provides: "the routing change that sub-divides the red family into three distinct clue functions (danger/memo/error) -- the precondition this plan's re-render evidences"
provides:
  - "A re-rendered 39-ADM04-GREYSCALE.png (same path, new bytes) showing seven boxes with the red family (error/danger/attention) contiguous and distinct, taken from a worktree proven to carry plan 39-11's routing change"
  - "A dated amendment to 39-ADM04-SIGNOFF.md recording the owner's re-taken, verbatim verdict under gap G-39-1, with the original 2026-08-02 verdict preserved intact below the amendment"
affects: [39-13-plan (phase close-out, which reads this amendment's operative verdict rather than re-deriving the ADM-04 outcome and must not mark the gap closed on a negative verdict -- this one is positive)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A dated AMENDMENT appended below an existing human sign-off artifact, rather than editing or overwriting it, when a requirement's evidence base changes underneath an already-recorded [V]-class verdict"

key-files:
  created: []
  modified:
    - tests/fixtures/admonition_greyscale_probe/index.rst
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md

key-decisions:
  - "Re-render taken only after confirming both routing gates (tests/test_admonition_bucket_render_gate.py, tests/test_admonition_locale_title_precedence_gate.py) green in the same worktree, at the same base commit as the render -- so the artifact evidences the sub-divided red family (D-03-R), not the folded one (D-03)."
  - "The owner's verbatim one-word response (\"approved\") is recorded exactly as given, with the four-question checkpoint text it answered quoted alongside it, rather than being paraphrased, embellished, or expanded into invented per-pair commentary."
  - "The amendment is purely additive to 39-ADM04-SIGNOFF.md: 162 insertions, 0 deletions. The only change above the new section is a one-line pointer added directly under the existing status paragraph."
  - "No styling change made and no fallback lever chosen (D-06/D-08) -- the owner reported no indistinguishable pair in response to the explicit attention/error adjacency question, so no lever question arose."

patterns-established:
  - "For a [V]-class requirement whose evidence artifact is invalidated by a later code change, re-take the sign-off as a dated amendment to the SAME artifact file rather than a new file -- preserving the old verdict's context (why it was correct at the time) alongside the new one (why it is now operative)."

requirements-completed: [ADM-04]

coverage:
  - id: D1
    description: "Greyscale probe extended to seven boxes (note, tip, seealso, warning, then error, danger, attention contiguous), re-rendered from a worktree proven to carry plan 39-11's red-family routing change"
    requirement: "ADM-04"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py tests/test_admonition_locale_title_precedence_gate.py -x (21/21 passed, run before the render, at commit c02d9ec)"
        status: pass
      - kind: other
        ref: "PIL.Image.open(...).mode == 'L', size == (1240, 1754), 36051 bytes (vs. 35570 prior), verified live"
        status: pass
    human_judgment: false
  - id: D2
    description: "Owner's re-taken visual sign-off that the seven-box probe, with error/danger/attention now three distinct clue functions, remains distinguishable in greyscale -- including a named verdict on the attention/error adjacency question -- recorded as a dated amendment to 39-ADM04-SIGNOFF.md"
    requirement: "ADM-04"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md, Amendment 2026-08-02 (gap G-39-1) section -- owner's verbatim one-word response (\"approved\") quoted together with the four-question checkpoint text it answered"
        status: pass
    human_judgment: true
    rationale: "ADM-04 is REQUIREMENTS.md's own [V]-marked (human-only visual UAT) requirement; no automated assertion exists or was offered as a stand-in for the owner's judgement anywhere in this plan (D-06/D-08, this plan's must_haves.prohibitions)."

duration: 40min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 12: ADM-04 Re-taken Under Gap G-39-1 Summary

**Re-rendered the greyscale probe from post-G-39-1 code (seven boxes, red family sub-divided into three distinct clue functions) and recorded the owner's re-taken verdict as a dated amendment to `39-ADM04-SIGNOFF.md`: ADM-04 remains MET, with the owner's one-word "approved" answering an explicit `attention`/`error` adjacency question, and the original 2026-08-02 verdict preserved intact.**

## Performance

- **Duration:** 40 min total across two dispatches — Task 1 (~20 min, prior dispatch, ended at the blocking checkpoint) + Tasks 2-3 (~20 min, this continuation dispatch, after the owner's answer)
- **Started:** 2026-08-02T14:5x (prior dispatch, Task 1)
- **Completed:** 2026-08-02T06:02:51Z (this dispatch)
- **Tasks:** 3 (1 auto, 1 checkpoint, 1 auto)
- **Files modified:** 3 (1 test fixture, 1 binary artifact, 1 sign-off doc)

## Accomplishments

- **Task 1 (executed in a prior dispatch, before the checkpoint):** Extended `tests/fixtures/admonition_greyscale_probe/index.rst` to seven boxes — note, tip, seealso, warning, then error, danger, attention contiguous at the end — confirmed both routing gates (`tests/test_admonition_bucket_render_gate.py`, `tests/test_admonition_locale_title_precedence_gate.py`, 21/21) green in this worktree BEFORE rendering, and re-rendered `39-ADM04-GREYSCALE.png` (mode `L`, 1240x1754, 36051 bytes, up from 35570) at commit `c02d9ec`. Verified in this dispatch: the commit exists in the branch history, the PNG is present at the expected size, and the fixture carries all seven boxes in the required order — no re-render was performed.
- **Task 2 (checkpoint, answered by the owner between dispatches):** The blocking-human checkpoint asked the owner to judge the re-rendered artifact against four questions, including an explicit adjacency question naming the `attention`/`error` pair by name. The owner's verbatim response was recorded as exactly the single word "approved" — no additional commentary, and none invented on their behalf.
- **Task 3 (this dispatch):** Appended a dated amendment ("Amendment 2026-08-02 (gap G-39-1): red-family sub-division re-take") to `39-ADM04-SIGNOFF.md`, containing all seven required elements: the requirement text under judgement, why the sign-off was re-taken (the prior artifact folded the red family onto one function; that verdict remains correct for the phase as it was built and is superseded, not withdrawn), full render provenance (commit `c02d9ec`, PPI 150, mode `L`, 1240x1754, 36051 bytes vs. 35570 prior, seven-box probe, both gates green before render), the restated BT.601-vs-BT.709 desaturation caveat, the owner's verbatim one-word answer alongside the four-question text it answered, the unambiguous positive outcome, and the levers considered (with the dashed-border non-option restated). The amendment is purely additive: 162 insertions, 0 deletions against the pre-existing file.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend the probe to the full red family and re-render from post-change code** — `c02d9ec` (feat) — completed in a prior dispatch, already in this worktree's base
2. **Task 2: Owner sign-off checkpoint** — no commit (checkpoint; per the plan's own instruction, no files are modified for this task — the owner's answer is recorded in this SUMMARY and consumed by Task 3)
3. **Task 3: Record the re-taken sign-off as a dated amendment** — `9bb0281` (docs)

_No TDD tasks in this plan; each auto task is a single commit._

## Files Created/Modified

- `tests/fixtures/admonition_greyscale_probe/index.rst` — extended to seven boxes with the red family contiguous (Task 1, prior dispatch, commit `c02d9ec`)
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png` — re-rendered from post-G-39-1 code (Task 1, prior dispatch, commit `c02d9ec`)
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md` — dated amendment appended recording the re-taken verdict (Task 3, this dispatch, commit `9bb0281`)

## Decisions Made

- **The owner's exact one-word response ("approved") was recorded verbatim, with no embellishment.** The plan's `owner_response` instructions were explicit that fabricating additional owner commentary — including invented Japanese quotations matching the style of the original sign-off — would be a serious integrity defect. The amendment states plainly what made the single word sufficient: the checkpoint's question 2 named the `attention`/`error` pair explicitly, and "approved" answered all four questions as posed, including that one.
- **The amendment is purely additive.** 162 insertions, 0 deletions verified via `git diff --numstat` before committing — stricter than the plan's own acceptance criterion allowing up to 1 deletion. The only change above the new section is a one-line pointer inserted directly under the existing status paragraph.
- **No styling change, no fallback lever chosen.** The owner reported no indistinguishable pair in response to the explicit adjacency question, so neither the per-bucket border-thickness lever nor the per-bucket header-band-colour lever was needed, consistent with D-06/D-08.
- **No pending todo filed.** The outcome is positive (ADM-04 remains MET); the plan's negative-outcome path (filing a todo naming a chosen lever) does not apply.

## Deviations from Plan

None — plan executed exactly as written. Task 1 was completed and verified as landed in a prior dispatch (not re-executed); Task 2's checkpoint was answered by the owner between dispatches; Task 3 recorded that answer per the plan's seven required elements.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- ADM-04 remains recorded as **complete/met** — now under the sub-divided red-family taxonomy (D-03-R). Plan 39-13's phase close-out should read `39-ADM04-SIGNOFF.md`'s amendment section directly (the "Amendment 2026-08-02 (gap G-39-1)" heading and its §A6 outcome) as the now-operative verdict, rather than re-deriving the outcome.
- Gap G-39-1 closes on a **positive** verdict — no pending todo was filed, and none is needed.
- No blockers. No follow-up lever work is queued, since none was needed.

## Self-Check: PASSED

Files verified present on disk:
- `tests/fixtures/admonition_greyscale_probe/index.rst` — FOUND, carries 7 boxes in the required order (verified before this dispatch's work began)
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png` — FOUND, 36051 bytes
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md` — FOUND, contains both the original 2026-08-02 verdict (verbatim, `grep -c` returns 1 for the operative Japanese quotation) and the new amendment

Commit hashes verified present in `git log --oneline`:
- `c02d9ec` — FOUND (Task 1, prior dispatch)
- `9bb0281` — FOUND (Task 3, this dispatch)

Acceptance-criteria greps verified live:
- `grep -q 'G-39-1' 39-ADM04-SIGNOFF.md` — pass
- `grep -qi 'BT.601' 39-ADM04-SIGNOFF.md` — pass
- `git diff --numstat -- 39-ADM04-SIGNOFF.md` — 162 insertions, 0 deletions
- `git diff --stat -- typsphinx/` — empty

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*
