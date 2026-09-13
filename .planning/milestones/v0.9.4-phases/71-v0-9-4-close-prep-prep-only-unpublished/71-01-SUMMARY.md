---
phase: 71-v0-9-4-close-prep-prep-only-unpublished
plan: 01
subsystem: release-prep
tags: [changelog, myst, docs-build, typing-modernization]

requires:
  - phase: 70-typing-modernization-and-its-behaviour-identity-evidence
    provides: "the QUA-09/QUA-11/QUA-12/DOC-22/DOC-23 evidence this bullet describes (byte-identical .typ output, project count, API-reference diff)"
provides:
  - "The fourth ## [Unreleased] -> ### Changed CHANGELOG bullet for the v0.9.4 typing-modernization work"
  - "71-CHANGELOG-EVIDENCE.md: base, pre-edit measurements, Phase 70 figures cited, clean-build docs baselines (pre- and post-edit), pure-addition proof, fence and content assertions"
affects: [71-03, 71-05, 71-07]

actuals:
  tokens: 6255
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CHANGELOG-EVIDENCE.md
  modified:
    - CHANGELOG.md

key-decisions:
  - "Bullet lead sentence: 'Type annotations in typsphinx's source now use builtin generics' — carries a verb, avoiding the bare-noun-phrase defect 69-REVIEW.md WR-01 flagged."
  - "The bullet's only numeral (167) is the live CORPUS_PROJECT_COUNT read from 70-CORPUS-DOCS-BASE-EVIDENCE.md at execution time, not copied from any planning document."
  - "No Japanese-site wording, no pytest/mypy figures, no QUA-12 leg enumeration, per D-02/D-03."

requirements-completed: []

coverage:
  - id: D1
    description: "Fourth CHANGELOG bullet added under the existing ## [Unreleased] -> ### Changed heading, citing QUA-09, QUA-11, QUA-12, DOC-22, DOC-23, with the Dict[str, Any] -> dict[str, Any] example and the byte-identical evidence sentence"
    requirement: REL-13
    verification:
      - kind: other
        ref: "71-CHANGELOG-EVIDENCE.md Task 1 automated verify (region heading order, 4 bold bullets, ID span, no-effect phrase, version-literal absence)"
        status: pass
      - kind: other
        ref: "71-CHANGELOG-EVIDENCE.md Task 2 automated verify (pure-addition proof, fence assertions, bullet content assertions)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both docs environments (docs-html, docs-pdf), built clean before and after the edit, report equal warning counts and equal WARNING line sets; the PDF starts with %PDF-"
    requirement: REL-13
    verification:
      - kind: other
        ref: "rm -rf docs/_build && LC_ALL=C uv run tox -e docs-html / docs-pdf, run twice (pre-edit baseline, post-edit)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The bullet's factual claims are traced, claim by claim, to named Phase 70 evidence files and sections"
    requirement: REL-13
    verification: []
    human_judgment: true
    rationale: "Whether the accuracy-basis mapping in 71-CHANGELOG-EVIDENCE.md is a faithful, non-overstated account of Phase 70's evidence is an editorial judgment no automated check fully covers."

duration: 9min
completed: 2026-09-13
status: complete
---

# Phase 71 Plan 01: v0.9.4 CHANGELOG Bullet Summary

**Added the fourth `## [Unreleased]` -> `### Changed` CHANGELOG bullet describing the typing-modernization work (`Dict[str, Any]` -> `dict[str, Any]`), proven pure addition against a clean pre-edit tree and reproduced byte-for-byte across `docs-html`/`docs-pdf` warning counts before and after the edit.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-13T08:27:54Z
- **Completed:** 2026-09-13T08:37:09Z
- **Tasks:** 2
- **Files modified:** 2 (`CHANGELOG.md`, `71-CHANGELOG-EVIDENCE.md`)

## First section — key facts

- `BASE_71_01 = f1f7d54a61d74c3972f1df0508ac994c001dda7e`
- `DOCS_HTML_WARN_BASE = 3`, `DOCS_HTML_WARN_POST = 3`
- `DOCS_PDF_WARN_BASE = 5`, `DOCS_PDF_WARN_POST = 5`
- Bullet count in the `## [Unreleased]` -> `### Changed` region: 4 (was 3)
- `BULLET_NUMERALS = 167` (equals the live `CORPUS_PROJECT_COUNT` read from Phase 70's evidence)
- Bullet's bold lead: **Type annotations in typsphinx's source now use builtin generics (QUA-09, QUA-11, QUA-12, DOC-22, DOC-23).**

No `## HALT` heading was written; both tasks' automated verify commands passed on every run.

## Accomplishments

- Appended the fourth `### Changed` bullet, pure addition (one hunk, zero deletions, one added
  blank line) from `BASE_71_01`, citing QUA-09, QUA-11, QUA-12, DOC-22 and DOC-23, naming the
  `Dict[str, Any]` -> `dict[str, Any]` API-reference change and the byte-identical `.typ` output
  over 167 test-fixture projects.
- Recorded pre-edit measurements (heading count, link-reference count, bold-bullet count, version
  literal count, `Planned` block digest) and re-verified all of them unchanged after the edit.
- Took `docs-html` and `docs-pdf` clean-build baselines (`rm -rf docs/_build` immediately before
  each) both before and after the edit; both counts and their `WARNING` line sets matched exactly,
  and the compiled PDF starts with `%PDF-` on both sides.
- Traced every factual claim in the bullet to a named Phase 70 evidence file and section in
  `## Accuracy basis`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — pre-edit measurements, Phase 70 figures, clean-build docs baselines, then the bullet carried through MyST into a rendered page** - `4fedeeab` (feat)
2. **Task 2: Pure-addition proof, fence and content assertions, both docs environments rebuilt clean** - `1c6876a8` (test)

**Plan metadata:** committed separately after this SUMMARY (see final commit).

## Files Created/Modified

- `CHANGELOG.md` - appended the fourth `### Changed` bullet under `## [Unreleased]`, pure addition
- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CHANGELOG-EVIDENCE.md` - the plan
  base, pre-edit measurements, Phase 70 figures cited, both clean-build docs baselines, the bullet
  and its accuracy basis, the pure-addition proof, fence and content assertions, and the post-edit
  docs counts

## Decisions Made

- Bullet lead sentence carries a verb ("...now use builtin generics") rather than a bare noun
  phrase, following the `tox-uv` bullet's shape and avoiding the `69-REVIEW.md` WR-01 defect.
- The one evidence sentence cites the project count (167) transcribed live from
  `70-CORPUS-DOCS-BASE-EVIDENCE.md` at execution time, per D-03 — never copied from a planning
  document.
- No Japanese-site wording (D-02), no pytest/mypy figures, no QUA-12 leg enumeration, no version
  number (D-01).

## Deviations from Plan

None - plan executed exactly as written. One transient authoring slip was caught and corrected
before commit: the first draft of five `KEY = value` evidence lines in
`71-CHANGELOG-EVIDENCE.md`'s Fence assertions and Docs render sections carried a trailing
`(equals ...)` explanation on the same line as the value — the exact Phase 69 defect the plan
itself warns against. Caught by re-running the plan's own `^[A-Z][A-Z0-9_]* = .*[(]` check before
committing Task 2, and fixed by moving each explanation to its own line. No code or CHANGELOG.md
change was involved; this was a self-caught authoring correction to the evidence file, not a
deviation from the plan's instructions, and is recorded here only because the "Total deviations"
line below must account for it truthfully.

**Total deviations:** 0 auto-fixed (Rules 1-3 did not apply; one self-caught pre-commit authoring
correction to the evidence file's formatting, described above).
**Impact on plan:** None on the product tree or the plan's outcome — the correction landed inside
the Task 2 commit before it was ever pushed or reviewed.

## Issues Encountered

None. Both tasks' automated `<verify>` commands passed on the live tree; no `## HALT` heading was
needed in the evidence file.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 71-02 (phase-head fence baseline and closeout guard) — disjoint files, no
  cross-plan evidence dependency in this wave.
- `71-CHANGELOG-EVIDENCE.md`'s `DOCS_HTML_WARN_BASE`/`DOCS_PDF_WARN_BASE` keys are recorded for
  71-03's final-tree docs builds to compare against.
- No blockers or concerns for downstream plans.

## Self-Check: PASSED

- `CHANGELOG.md` exists: FOUND
- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CHANGELOG-EVIDENCE.md` exists: FOUND
- Commit `4fedeeab` (Task 1) exists in `git log --oneline --all`: FOUND
- Commit `1c6876a8` (Task 2) exists in `git log --oneline --all`: FOUND

---
*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Completed: 2026-09-13*
