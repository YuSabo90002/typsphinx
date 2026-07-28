---
phase: 35-v0-6-5-release-prep
plan: 02
subsystem: planning
tags: [todos, deferred-work, translator, ci, release-notes]

# Dependency graph
requires:
  - phase: 34-inline-math-after-text-separator-fix
    provides: "the WR-01 review finding and its file/line anchor at translator.py:4079-4088"
provides:
  - "A pending todo recording WR-01 (visit_math_block's redundant blank line in list items) with both candidate fixes and the D-05/D-10 deferral rationale"
  - "A pending todo recording the release.yml release-notes-body rework (D-11), including the measured 308/296/7/5-line breakdown and the corrected Phase 33 CHANGELOG-source claim"
affects: [35-05-release, gsd-complete-milestone, v0.6.6-scoping]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/todos/pending/2026-07-29-visit-math-block-redundant-blank-line-in-list-items.md
    - .planning/todos/pending/2026-07-29-release-notes-body-from-changelog-section.md
  modified: []

key-decisions:
  - "Wrote both todo files in English, deviating from the five pre-existing pending todos (Japanese), per the plan's explicit Language note that English is the standing .planning/ convention."

patterns-established: []

requirements-completed: [REL-03]

coverage:
  - id: D1
    description: "WR-01 deferral todo filed with both candidate fixes and the measured reproduction from the Phase 34 review"
    requirement: "REL-03"
    verification:
      - kind: other
        ref: "plan 35-02 Task 1 <automated> verify: frontmatter keys, ## Problem / ## Solution headers, no typsphinx/tests/.github diff, single new file"
        status: pass
    human_judgment: false
  - id: D2
    description: "release.yml release-notes-body rework todo filed with the measured 308/296/7/5-line breakdown and the corrected Phase 33 CHANGELOG-source claim"
    requirement: "REL-03"
    verification:
      - kind: other
        ref: "plan 35-02 Task 2 <automated> verify: frontmatter keys, ## Problem / ## Solution headers, release.yml + '308' citations, no .github/typsphinx/tests diff, single new file"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-07-29
status: complete
---

# Phase 35 Plan 02: Deferred-Work Todo Filing Summary

**Filed two pending-todo records — WR-01's `visit_math_block` redundant blank line and `release.yml`'s release-notes-body rework — so both deliberate v0.6.5 deferrals (D-05/D-10, D-11) are recorded facts rather than lost ones.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-29T00:50:00+09:00 (approx.)
- **Completed:** 2026-07-29T00:52:01+09:00
- **Tasks:** 2
- **Files modified:** 2 (both new)

## Accomplishments
- `.planning/todos/pending/2026-07-29-visit-math-block-redundant-blank-line-in-list-items.md` — records WR-01: `visit_math_block`'s pre-existing unconditional `"\n\n"` (translator.py:4079) stacking with the new `list_item_needs_separator` flag (translator.py:4087-4088), the empirical Construct E reproduction (two blank lines instead of one) from the Phase 34 review, why it was deferred (D-05: translator change forbidden by milestone invariant #3, forces GATE-01 fixture re-derivation and a full-corpus re-run right before a release), and both candidate fixes named in the review's Fix field.
- `.planning/todos/pending/2026-07-29-release-notes-body-from-changelog-section.md` — records D-11's measured 308-line v0.6.4 release-body breakdown (296 lines commit dump / 7 lines Installation / 5 lines GitHub auto-generated), the measured fact that `release.yml` never reads `CHANGELOG.md` today (correcting the Phase 33 CONTEXT claim that it is the single source), and the design direction: drop the commit-dump block, extract the tag's `## [X.Y.Z]` CHANGELOG section as the body, keep Installation and `generate_release_notes: true`.
- Neither `.github/workflows/release.yml` nor any file under `typsphinx/` changed — both deferrals stay deferred.

## Task Commits

Each task was committed atomically:

1. **Task 1: File the WR-01 deferral todo** - `080c95f` (docs)
2. **Task 2: File the release.yml release-notes-body rework todo** - `8f01b92` (docs)

**Plan metadata:** (this commit, made after SUMMARY.md is written)

## Files Created/Modified
- `.planning/todos/pending/2026-07-29-visit-math-block-redundant-blank-line-in-list-items.md` - WR-01 deferral record (frontmatter: created/title/area/files; `## Problem` / `## Solution`)
- `.planning/todos/pending/2026-07-29-release-notes-body-from-changelog-section.md` - `release.yml` rework deferral record (same shape)

## Decisions Made
- Both files were written in English rather than matching the five pre-existing Japanese-language pending todos, per the plan's explicit Language note: English is the standing `.planning/` convention that postdates those five files, and every Phase 34/35 artifact already follows it. Frontmatter shape (`created`/`title`/`area`/`files`, each `files` entry pairing a path with a parenthetical rationale) and body structure (`## Problem` / `## Solution`) were replicated exactly from `2026-07-22-add-sphinx-linkcheck-ci-job.md`.
- Used today's local date (`2026-07-29`, matching the worktree's system clock, which is already JST) as both the filename prefix and the `created` frontmatter's date component, consistent with the existing files' `YYYY-MM-DD-kebab-case-english-slug.md` convention.

## Deviations from Plan

None - plan executed exactly as written. No package installs, no source/test/workflow file touched, exactly two new files created under `.planning/todos/pending/`.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both deferred-work items (WR-01, `release.yml` rework) are now durable, reconstructible records under `.planning/todos/pending/` — `ls .planning/todos/pending/ | wc -l` returns 7 (5 pre-existing + 2 new).
- Plan 35-05's `35-HANDOFF.md` item 6 can cite these two filenames verbatim to confirm both exist before milestone close.
- Both files are candidates for v0.6.6 backlog scoping.
- No blockers for the remaining Phase 35 plans (version bump, CHANGELOG, live-run evidence, handoff).

---
*Phase: 35-v0-6-5-release-prep*
*Completed: 2026-07-29*
