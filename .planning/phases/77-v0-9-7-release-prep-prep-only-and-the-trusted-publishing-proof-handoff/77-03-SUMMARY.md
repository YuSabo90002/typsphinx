---
phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
plan: 03
subsystem: release-process
tags: [pypi, trusted-publishing, release-prep, rollback, github-actions, provenance]

# Dependency graph
requires:
  - phase: 76
    provides: control run 35730551619 (v0.9.6 publish, token path), rehearsal run 36321530105 (Phase 76 ATT-02, OIDC path), the ATT-04 two-grep pair (D-08 AMENDED), and the efde71a9 credential-deletion commit
provides:
  - "ATT-06: a rollback procedure inside 77-HANDOFF.md's `## Rollback procedure (ATT-06)` section, committed alone while no v0.9.7 tag exists anywhere"
  - "Ten fixed subsections: Measured basis, Failure shapes, Default recovery order, R0-R4, Failures that are not rollback shapes, What never happens on any branch"
  - "77-ATT06-EVIDENCE.md: the rollback commit SHA, its section digest, tag-absence probes against v0.9.6 controls, and the byte-exact efde71a9 restore-block verification"
  - "77-CONTROLS-EVIDENCE.md: measured controls for every read-only publish-half command 77-07 will inline (ATT-04, ATT-03(a)/(b), ATT-05, DOC-25, Release body, translations pin, Read the Docs)"
affects: [77-07 (writes the ordered publish-half sequence above this rollback section, using these controls as each step's expected output), 77-08 (phase-close scope fence and handoff audit)]

# Actuals (#2632)
actuals:
  tokens: 7142
  tasks: 2
  commits: 3
  plan_head_before: 3984b231e30fbb76ba156d2f9b2abe475231bccf
  plan_head_after: 2fff30bfe2babda7718d61e8a1d7a09c61951245

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Handoff commands write to a named file under /tmp/p77close/ and read it back, rather than using shell command substitution — negative-checked with `grep -qF '$('`."
    - "Every evidence KEY = value line carries the bare value only; explanatory parentheticals go on the following line so downstream sed readers (77-06/77-07/77-08) never break on an embedded '('."

key-files:
  created:
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-HANDOFF.md
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-ATT06-EVIDENCE.md
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-CONTROLS-EVIDENCE.md
  modified: []

key-decisions:
  - "None beyond what 77-CONTEXT.md already settled (D-01 to D-04) — this plan wrote those decisions into their final form, verbatim, with no re-interpretation."

requirements-completed: [ATT-06]

coverage:
  - id: D1
    description: "ATT-06 rollback procedure (credential restore, 0.9.8 bump, local+remote tag deletion, cheaper same-run re-run tried first) written inside 77-HANDOFF.md and committed alone while no v0.9.7 tag exists anywhere"
    requirement: ATT-06
    verification:
      - kind: other
        ref: "77-03-PLAN.md Task 1 <verify><automated> (re-run live, exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every read-only publish-half command (ATT-04's two greps, ATT-03(a)/(b)'s Simple JSON and Integrity API reads, ATT-05's name-only secret listings, DOC-25's target line, the Release-body prefix match, translations pin and Read the Docs identifiers) rehearsed against known controls in 77-CONTROLS-EVIDENCE.md"
    requirement: null
    verification:
      - kind: other
        ref: "77-03-PLAN.md Task 2 <verify><automated> (re-run live, exit 0)"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-09-28
status: complete
---

# Phase 77 Plan 03: ATT-06 Rollback Procedure and Publish-Half Controls Summary

**Wrote the ATT-06 rollback procedure into `77-HANDOFF.md` while no `v0.9.7` tag existed anywhere, and rehearsed every read-only publish-half command (ATT-04/ATT-03/ATT-05/DOC-25) against measured controls so 77-07 can inline each with a proven expected output.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-28T13:09:46Z
- **Completed:** 2026-09-28T13:18:27Z
- **Tasks:** 2
- **Files modified:** 3 (all new)

## Accomplishments

- `77-HANDOFF.md` now carries the standalone framing sentence and a `## Rollback procedure
  (ATT-06)` section with exactly its ten fixed subsections in order: Measured basis, Failure
  shapes, Default recovery order, R0 (before the tag), R1 (same-run re-run), R2 (0.9.8 tag
  deletion, D-02), R3 (HALT on shape 3, D-01), R4 (owner-gated credential restore, D-03),
  Failures that are not rollback shapes, and What never happens on any branch.
- The section committed alone in `fe4e87638220ec8c7574f73050e336e0fe28110b`, touching only
  `77-HANDOFF.md`. Probed immediately after: `git tag -l 'v0.9.7'` empty locally, no
  `refs/tags/v0.9.7` on `origin`, `v0.9.6` present as a positive control on both sides, and no tag
  points at the rollback commit. ATT-06 closes on this evidence.
- The R4 restore block is byte-identical to the two lines `efde71a9` removed
  (`        with:` / `          password: ${{ secrets.PYPI_API_TOKEN }}`), verified with
  `grep -xF` against a live `git show efde71a9` re-read rather than retyped.
- `77-CONTROLS-EVIDENCE.md` rehearses every publish-half read command the handoff prescribes:
  the ATT-04 two-grep pair reads 1/1 on control run `35730551619` and 0/0 on rehearsal run
  `36321530105`; the Simple JSON API reads `null,null` for the 0.9.6 files and a URL-string
  `provenance` for an attested `pip` wheel; the Integrity API reads 404 for the 0.9.6 wheel and
  200 with one bundle and the `GitHub|pypa/pip|release.yml|pypi` publisher for `pip`; the
  name-only secret listings, DOC-25's target line, the v0.9.6 Release-body prefix match, and the
  translations/Read the Docs identifiers are all recorded and reproduced live.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — measure release.yml's anchors, write the handoff's rollback section,
   commit it alone, and record ATT-06's evidence** - two commits:
   - `fe4e8763` (docs) — the rollback section inside `77-HANDOFF.md`, committed alone
   - `fd73a7c2` (docs) — `77-ATT06-EVIDENCE.md`, appended and committed separately after the
     rollback commit's SHA and probes were captured
2. **Task 2: Rehearse every read-only publish-half command against known controls** - `2fff30bf`
   (docs) — `77-CONTROLS-EVIDENCE.md`

**Plan metadata:** committed with this SUMMARY.

## Files Created/Modified

- `.planning/phases/77-.../77-HANDOFF.md` - standalone handoff framing plus the complete
  `## Rollback procedure (ATT-06)` section
- `.planning/phases/77-.../77-ATT06-EVIDENCE.md` - measured `release.yml` anchors, the rollback
  commit SHA and section digest, tag-absence probes, restore-block byte-identity, ATT-06 verdict
- `.planning/phases/77-.../77-CONTROLS-EVIDENCE.md` - measured controls for every publish-half
  read command 77-07 will inline

## Decisions Made

None - plan executed exactly as written. All four rollback decisions (D-01 to D-04) were locked
in `77-CONTEXT.md` before this plan ran; this plan's only job was to write them into their final,
settled form and verify them against live measurements.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' `<verify><automated>` blocks passed on the
first run against the content as authored (after one self-caught fix during drafting: an early
draft of R4's gate sentence split the phrase "Trusted Publishing is being abandoned" across a
markdown line-wrap, which the section-extraction `awk`/line-based `grep -F` term check would have
missed as a false negative before any commit was made — caught and fixed pre-commit via the same
term-check script the plan's own `<verify>` runs, so no deviation entry applies).

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ATT-06 is closed. `77-CONTROLS-EVIDENCE.md`'s `CONTROLS_VERDICT = READY` gives 77-07 a measured
  expected output and control for every publish-half step it will write.
- `77-07-PLAN.md` (SC#4 handoff, wave 4) can now write the twelve ordered publish-half steps above
  this rollback section, each with a rollback pointer into the ten subsections this plan fixed.
- No blockers or concerns. `git diff` over the phase confirms only the three files this plan
  created changed — nothing under `typsphinx/`, `.github/workflows/`, or elsewhere in `.planning/`
  was touched.

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Completed: 2026-09-28*

## Self-Check: PASSED
