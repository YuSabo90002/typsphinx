---
phase: 73-v0-9-5-close-prep-prep-only-unpublished
plan: 01
subsystem: docs
tags: [changelog, keep-a-changelog, myst-parser, sphinx, docs-build]

requires:
  - phase: 72-tox-e-linkcheck-and-root-toctree-deduplication
    provides: "tox -e linkcheck environment (QUA-13, DOC-24) and the sidebar toctree dedup fix (DOC-18), both now cited by this plan's two CHANGELOG bullets"
provides:
  - "Two new CHANGELOG.md subsections under the existing ## [Unreleased] heading: ### Added (linkcheck bullet) and ### Fixed (sidebar dedup bullet)"
  - "73-CHANGELOG-EVIDENCE.md recording the plan base, pre/post-edit measurements, clean docs-html/docs-pdf baselines with the multiple-toctrees census, the pure-addition proof, and the changelog page gate result"
affects: [74-release-prep, complete-milestone]

actuals:
  tokens: 5935
  tasks: 2
  commits: 4
plan_head_before: c6bc641aa1745e6413b4f33c4d0c572a962da430

tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CHANGELOG-EVIDENCE.md
  modified:
    - CHANGELOG.md

key-decisions:
  - "Both bullets' lead sentences carry a verb (checks / now lists) to avoid the Phase 69 bare-noun-phrase house-style defect."
  - "REL-14 is not cited in either bullet — it governs the close-prep process itself and closes at /gsd-complete-milestone, never inside a bullet (D-08)."
  - "The Fixed bullet uses only the 'no longer reports multiple toctrees' evidence sentence, omitting the PDF-inclusion point, to stay scoped to the HTML sidebar surface it discusses."

requirements-completed: []

coverage:
  - id: D1
    description: "CHANGELOG.md gains ### Added (linkcheck, QUA-13/DOC-24) and ### Fixed (sidebar dedup, DOC-18) subsections under ## [Unreleased], in Keep a Changelog order, as pure addition with zero deletions"
    requirement: REL-14
    verification:
      - kind: other
        ref: "73-CHANGELOG-EVIDENCE.md automated verify (Task 1 and Task 2 <verify><automated> blocks, both run to exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both docs environments (docs-html, docs-pdf) rebuilt clean from an empty docs/_build, before and after the edit, report identical warning counts and zero multiple-toctrees lines, against Phase 72's positive control"
    requirement: REL-14
    verification:
      - kind: integration
        ref: "uv run tox -e docs-html / docs-pdf, logged to p7301_html-base.log, p7301_pdf-base.log, p7301_html-tracer.log, p7301_html-post.log, p7301_pdf-post.log"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_changelog_page_gate.py runs on the edited tree with the docs extra provisioned: 6 passed, 0 skipped, 0 failed"
    requirement: REL-14
    verification:
      - kind: unit
        ref: "tests/test_changelog_page_gate.py -v -rs -p no:cacheprovider"
        status: pass
    human_judgment: false

duration: 68min
completed: 2026-09-16
status: complete
---

# Phase 73 Plan 01: CHANGELOG Added/Fixed Subsections Summary

**Added two CHANGELOG.md subsections under `## [Unreleased]` — `### Added` for the new `tox -e linkcheck` environment and `### Fixed` for the docs sidebar dedup — as pure addition, proven by clean docs-html/docs-pdf rebuilds and the changelog page gate.**

## Performance

- **Duration:** 68 min
- **Started:** 2026-09-16T09:53:50Z
- **Completed:** 2026-09-16T10:03:20Z (approx, from commit timestamps)
- **Tasks:** 2 completed
- **Files modified:** 2 (CHANGELOG.md, 73-CHANGELOG-EVIDENCE.md created)

## Accomplishments

- `CHANGELOG.md`'s `## [Unreleased]` region now reads `### Added`, `### Changed`, `### Fixed`,
  `### Planned for Future Releases` in that order — the house order of the released `[0.9.0]` and
  `[0.8.0]` sections — with six bold-lead bullets total (four carried, two new).
- `### Added` bullet cites `(QUA-13, DOC-24)`: describes the new `tox -e linkcheck` environment,
  names its anchor-checking and network requirement, states it is not part of a plain `tox` run,
  and calls itself contributor tooling — with no CI-job, schedule or required-check claim.
- `### Fixed` bullet cites `(DOC-18)`: describes each User Guide and Examples page now appearing
  once in the sidebar, nested under its section — with no page path, no digit, and no claim about
  Read the Docs or its `stable`/`latest` versions.
- Both baselines (docs-html: 3 warnings, docs-pdf: 5 warnings) were taken from clean builds
  (`rm -rf docs/_build` before each) at the phase base under `LANG=C LC_ALL=C`, both with zero
  `document is referenced in multiple toctrees` lines, cross-checked against Phase 72's recorded
  pre-fix positive control of 5 such messages.
- Post-edit clean rebuilds of both environments reproduce the identical warning counts and the
  identical sorted set of `WARNING` lines, and the changelog page gate
  (`tests/test_changelog_page_gate.py`) ran 6 passed / 0 skipped / 0 failed.
- The edit is proven pure addition: 2 diff hunks, 0 removed lines, 4 added blank lines, and the
  `### Changed` and `### Planned for Future Releases` blocks hash identically (SHA-256) to the
  pre-edit tree; heading count, link-reference count and the final `[Unreleased]: .../compare/
  v0.9.2...HEAD` line are all unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — pre-edit measurements, clean-build docs baselines with multiple-toctrees
   census, then both subsections carried through MyST into a rendered page** - `c787d764` (docs)
2. **Task 2: Pure-addition proof, fence and content assertions, both docs environments rebuilt
   clean against the baseline, and the changelog page gate** - `a108cba2` (docs)

_No plan-metadata commit follows in worktree mode — the orchestrator commits STATE.md/ROADMAP.md
centrally after merge._

## Files Created/Modified

- `CHANGELOG.md` - Added `### Added` (linkcheck) and `### Fixed` (sidebar dedup) subsections under
  `## [Unreleased]`, as pure addition; nothing else in the file changed.
- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CHANGELOG-EVIDENCE.md` - Created.
  Records `BASE_73_01`, pre/post-edit fence measurements, clean docs-html/docs-pdf baselines with
  the multiple-toctrees census and its Phase 72 positive control, the pure-addition proof, bullet
  content assertions, and the changelog page gate result.

## Decisions Made

- Both lead sentences carry a verb ("checks" / "now lists") rather than a bare noun phrase,
  avoiding the Phase 69 house-style defect recorded in `71-CHANGELOG-EVIDENCE.md`.
- REL-14 is not cited in either bullet: it governs the close-prep process itself, not a
  user-visible change, and closes at `/gsd-complete-milestone` per D-08.
- The Fixed bullet uses only the "no longer reports multiple toctrees" evidence sentence, leaving
  out the PDF-inclusion point, to stay scoped to the HTML sidebar surface it discusses.

## Deviations from Plan

None - plan executed exactly as written. Both tasks' full `<verify><automated>` blocks were run
to completion (exit 0) with no corrections needed to either bullet.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `CHANGELOG.md`'s `## [Unreleased]` region now carries six bullets across three subsections
  (`### Added`, `### Changed`, `### Fixed`), ready for the next release-prep phase to promote them
  into a versioned `## [X.Y.Z]` section.
- No blockers. This plan took no outward or irreversible action (no tag, PyPI upload, GitHub
  Release, pull request, push, or Dependabot action) — those remain scoped to plan 73-04.
- `.planning/REQUIREMENTS.md` is untouched; `requirements-completed: []` per D-08. REL-14 closes at
  `/gsd-complete-milestone`, never in a plan.

## Self-Check: PASSED

- `CHANGELOG.md` exists on disk: FOUND
- `.planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CHANGELOG-EVIDENCE.md` exists: FOUND
- Task commit `c787d764` (Task 1) present in `git log`: FOUND
- Task commit `a108cba2` (Task 2) present in `git log`: FOUND
- All plan-level `<verification>` items re-run and confirmed passing (region order, bullet count,
  version-literal absence, pure-addition diff, docs baselines, changelog page gate).
- Commit count measured against `plan_head_before` (`c6bc641aa1745e6413b4f33c4d0c572a962da430`):
  4 commits (Task 1, Task 2, initial SUMMARY, this correction commit — the final, stable count).

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 01*
*Completed: 2026-09-16*
