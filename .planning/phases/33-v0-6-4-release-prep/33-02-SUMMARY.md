---
phase: 33-v0-6-4-release-prep
plan: 02
subsystem: docs
tags: [changelog, keep-a-changelog, release-notes, markdown]

# Dependency graph
requires:
  - phase: 29-32 (RTD build, i18n machinery removal, translations repo, URL cutover, Pages teardown)
    provides: the user-visible facts this CHANGELOG entry summarizes (RTD-01..RTD-04, I18N-01..I18N-03, DOC-08..DOC-10, CI-04, CI-05)
provides:
  - "A curated `## [0.6.4]` CHANGELOG.md entry (five subsections: Added, Changed, Removed, Fixed, Verified) summarizing the milestone's user-visible hosting migration"
  - "The tail release/compare link block carried forward: `[0.6.4]:` release-tag link inserted above `[0.6.3]:`, `[Unreleased]:` compare base moved to `v0.6.4...HEAD`"
affects: [33-04 (release close, cites this entry as SC#2 evidence and as the GitHub Release body source), gsd-complete-milestone (publishes this entry's body verbatim as the Release description)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CHANGELOG entries with zero BREAKING labels when no packaged (typsphinx/) behavior changed, even when the milestone made user-visible hosting/repo-operations changes (D-01)"
    - "A fifth `### Verified` subsection restricted to invariants a git diff can mechanically prove (D-03), distinct from Added/Changed/Removed/Fixed"

key-files:
  created: []
  modified:
    - CHANGELOG.md

key-decisions:
  - "D-01: no BREAKING label anywhere in the [0.6.4] entry — nothing under typsphinx/ changed; the user-visible loss (github.io 404s, lost browser-language auto-redirect) is disclosed in the Removed section body instead of a label."
  - "D-02: the Japanese documentation site is announced with no translation-coverage percentage and no partial-translation hedge."
  - "D-03: the Verified section lists only three git-diff-provable invariants (zero new runtime deps, no @preview version bump, zero typsphinx/ changes) — no corpus-gate triple, no live-hosting observation."
  - "D-04: requirement IDs cited in parens at the end of each bullet's bold lead-in, matching the 0.6.3 entry's established citation style."

requirements-completed: [REL-02]

coverage:
  - id: D1
    description: "CHANGELOG.md contains exactly one `## [0.6.4]` heading, positioned between `## [Unreleased]` and `## [0.6.3]`, with five subsections in order Added/Changed/Removed/Fixed/Verified, zero BREAKING labels, and zero translation-coverage figures"
    requirement: "REL-02"
    verification:
      - kind: other
        ref: "grep/awk acceptance-criteria commands from 33-02-PLAN.md Task 1 <verify>, run live during execution — output: ENTRY_OK"
        status: pass
    human_judgment: false
  - id: D2
    description: "Tail release/compare link block updated: [0.6.4]: release-tag link above [0.6.3]:, and the file's final line is the Unreleased compare line rebased to v0.6.4...HEAD, with no v0.6.4 tag created"
    requirement: "REL-02"
    verification:
      - kind: other
        ref: "grep/awk acceptance-criteria commands from 33-02-PLAN.md Task 2 <verify>, run live during execution — output: TAIL_OK equivalent checks all passed individually"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-07-28
status: complete
---

# Phase 33 Plan 02: v0.6.4 CHANGELOG Entry Summary

**Curated `## [0.6.4] - 2026-07-28` CHANGELOG entry (Added/Changed/Removed/Fixed/Verified) documenting the GitHub Pages → Read the Docs hosting migration, with the tail release/compare link block carried forward to the 0.6.4 tag.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-07-27T20:54:49Z
- **Completed:** 2026-07-27T20:56:40Z
- **Tasks:** 2 completed
- **Files modified:** 1 (CHANGELOG.md)

## Accomplishments
- Inserted a single, correctly positioned `## [0.6.4] - 2026-07-28` entry between `## [Unreleased]` and `## [0.6.3]`, with five subsections in the mandated order (Added, Changed, Removed, Fixed, Verified) and zero `BREAKING` labels (D-01).
- Wrote the Japanese-site Added bullet and hosting-migration Changed bullet with no translation-coverage figure or hedging qualifier (D-02), and a Removed bullet stating in-body that old `github.io` URLs now 404 with no redirect and that browser-language auto-redirection is gone (D-01/D-04).
- Restricted the new `### Verified` subsection to the three invariants a `git diff` can mechanically prove — zero new runtime dependencies, no `@preview` version bump across the four-surface sync guard, and zero changes under `typsphinx/` (D-03).
- Carried the tail link block forward: inserted `[0.6.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4` immediately above `[0.6.3]:`, and rewrote the final `[Unreleased]:` line's compare base from `v0.6.3...HEAD` to `v0.6.4...HEAD`. No `v0.6.4` tag was created (confirmed empty `git tag -l v0.6.4`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Insert the curated [0.6.4] entry between Unreleased and 0.6.3** - `abb8eb6` (feat)
2. **Task 2: Update the tail release/compare link block** - `ad123fa` (feat)

**Plan metadata:** committed at final metadata-commit step (worktree mode — orchestrator will merge and record the phase-level commit).

## Files Created/Modified
- `CHANGELOG.md` - Added the `## [0.6.4] - 2026-07-28` entry (five subsections, no BREAKING labels) and updated the tail reference-link block (new `[0.6.4]:` release link, `[Unreleased]:` compare base moved forward)

## Decisions Made
- Used the pre-drafted entry text from `33-RESEARCH.md`'s `## Code Examples` section verbatim as the base text, per the plan's explicit instruction not to re-derive structure from scratch. No wording deviations were needed — the draft had already been fact-checked against PROJECT.md's Phase 29–32 Key Decisions.
- Resolved `<DATE>` via `date -I` at execution time (`2026-07-28`), not by copying a date from any planning document, per the plan's explicit instruction.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' automated `<verify>` commands passed on the first attempt with no auto-fixes required (no Rule 1/2/3 triggers encountered).

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required. This plan only edits `CHANGELOG.md`.

## Next Phase Readiness

- The `[0.6.4]` entry's body is ready to serve as the GitHub Release body that `/gsd-complete-milestone` will publish verbatim.
- The `[0.6.4]:` tail link intentionally returns 404 until the `v0.6.4` tag is cut — this is the same accepted transient state v0.6.1/0.6.2/0.6.3 each passed through, not a defect.
- Plan 33-04 (release close) can cite this SUMMARY as SC#2 evidence: the resolved date (`2026-07-28`) and the verbatim tail-block diff are both recorded above under Accomplishments and in the Task Commits' underlying `git diff CHANGELOG.md` output (1 insertion + 1 modification, verified during Task 2 execution).
- No blockers or concerns for downstream plans in this phase.

---
*Phase: 33-v0-6-4-release-prep*
*Completed: 2026-07-28*
