---
phase: 57-v0-9-0-release-prep-prep-only
plan: 03
subsystem: docs
tags: [changelog, release-prep, keep-a-changelog, test-gate]

# Dependency graph
requires:
  - phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
    provides: OUT-04/05/06/07, BLD-05/06, CONF-19 — the bundle-copy behavior and typst_template_assets removal this section describes
  - phase: 54.1-bundle-directory-safety-templates-path-collision-refusal-and
    provides: WR-01/CR-01 pre-write template-layout validation, promoted verbatim from Unreleased
  - phase: 55-v0-8-0-derived-defects
    provides: XREF-05, BLD-07, BLD-08, BLD-09, IMG-03 — the five Fixed bullets promoted verbatim
provides:
  - The curated `## [0.9.0] - 2026-08-17` CHANGELOG section (headline registry lead, exactly four `**Breaking` bullets each with a migration sentence, `### Removed` bullet agreeing with the shipped warning shim)
  - Rolled-over CHANGELOG tail link block (`[0.9.0]` tag line + advanced `[Unreleased]` compare base)
  - `RELEASE_VERSIONS` extended to 15 entries in the published-page coverage gate
  - `57-CHANGELOG-EVIDENCE.md` — SC#2's evidence artifact
affects: [57-04-migration-guide, 57-08-sc4-sweep, 57-09-handoff, gsd-complete-milestone]

# Actuals (#2632)
actuals:
  tokens: 6381
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Keep a Changelog section promotion: Unreleased bullets moved substantially as written into the new release section rather than re-authored (D-02)"
    - "### Removed bullet model (D-03, following the 0.7.1 typst_authors precedent), inverted to state a config-inited warning shim exists"

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-CHANGELOG-EVIDENCE.md
  modified:
    - CHANGELOG.md
    - tests/test_changelog_page_gate.py

key-decisions:
  - "Followed the plan's D-01..D-05/D-09 decisions exactly as specified; no new decisions required during execution"

patterns-established:
  - "The output-relocation and typst_template_assets-removal bullets both cite OUT-04/CONF-19 alongside the promoted shadow-route bullet's own OUT-04 citation, since requirement IDs map to underlying behavior rather than to exactly one bullet"

requirements-completed: [REL-08]

coverage:
  - id: D1
    description: "Curated ## [0.9.0] CHANGELOG section: registry-headline lead paragraph, seven promoted bullets, three authored bullets, exactly four Breaking marks, one Removed heading, unchanged three-item Verified section"
    requirement: "REL-08"
    verification:
      - kind: unit
        ref: "scripts/extract_changelog_section.py 0.9.0 (manual invocation, non-empty exit-0 body)"
        status: pass
      - kind: other
        ref: "awk-bounded grep census: 4 **Breaking marks, 1 ### Removed, 3 ### Verified bullets, 1 residual ### Planned for Future Releases heading"
        status: pass
    human_judgment: true
    rationale: "Editorial quality (curated prose vs. generated dump) is a manual verification listed in 57-VALIDATION.md, discharged at end-of-phase UAT — not machine-checkable."
  - id: D2
    description: "CHANGELOG tail link block rolled over (new [0.9.0] tag line, advanced [Unreleased] compare base) and RELEASE_VERSIONS extended to include 0.9.0"
    requirement: "REL-08"
    verification:
      - kind: unit
        ref: "tests/test_changelog_page_gate.py (6 passed, 0 skipped, 0 failed, 0 errors, --extra dev --extra docs)"
        status: pass
    human_judgment: false
  - id: D3
    description: "57-CHANGELOG-EVIDENCE.md records SC#2's evidence: both extractor directions, Breaking census, section census, tail block, page-gate transcript, D-09 decline"
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "grep presence checks for all seven required headings plus skipped=\"0\" literal"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-08-17
status: complete
---

# Phase 57 Plan 03: Curated v0.9.0 CHANGELOG Summary

**Authored the `## [0.9.0]` CHANGELOG release section — promoting seven existing bullets, authoring three new ones (registry Added, output-relocation Breaking Changed, typst_template_assets Breaking Removed) — rolled over the tail link block, extended the published-page coverage gate to 15 releases, and recorded SC#2's evidence.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-08-17T00:38:00+09:00 (approx.)
- **Completed:** 2026-08-17T00:43:26+09:00
- **Tasks:** 3
- **Files modified:** 3 (1 new)

## Accomplishments
- `## [0.9.0] - 2026-08-17` CHANGELOG section: lead paragraph names the `typst_document_templates` registry as the headline, declares the release breaking on two independent axes, and states explicitly that the registry itself is additive
- Exactly four `**Breaking` bullets, each with its own migration sentence: the promoted OUT-04 shadow-route relocation, the promoted WR-01/CR-01 pre-write validation, the newly authored output-relocation bullet, and the newly authored `typst_template_assets` removal
- Seven Unreleased bullets (two Changed, five Fixed — XREF-05, BLD-07, BLD-08, BLD-09, IMG-03) promoted substantially as written; `## [Unreleased]` now holds only its `### Planned for Future Releases` list
- Tail link block rolled over: `[0.9.0]:` release-tag line inserted immediately above the previous topmost `[0.8.0]:` line, `[Unreleased]`'s compare base advanced to `v0.9.0...HEAD`
- `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` extended to 15 entries (added `"0.9.0"`), gate re-run with `--extra dev --extra docs`: 6/6 passed, 0 skipped, 0 failed, 0 errors
- `57-CHANGELOG-EVIDENCE.md` written with all seven required sections: both extractor directions (0.9.0 non-empty, 9.9.9 exit-1 control), the Breaking-mark census, section census, tail-block record, page-gate transcript, and D-09's decline

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the curated `## [0.9.0]` section** - `e74733d8` (feat)
2. **Task 2: Roll over the tail link block and extend the published-page coverage tuple** - `dcee0201` (feat)
3. **Task 3: Record SC#2's evidence** - `5ec81e36` (docs)

_No plan-metadata commit is made in worktree mode — the orchestrator commits STATE.md/ROADMAP.md centrally after merge._

## Files Created/Modified
- `CHANGELOG.md` - New `## [0.9.0]` section (Added/Changed/Fixed/Removed/Verified) and rolled-over tail link block
- `tests/test_changelog_page_gate.py` - `RELEASE_VERSIONS` tuple extended to 15 entries, comment moved
- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-CHANGELOG-EVIDENCE.md` - SC#2 evidence (new file)

## Decisions Made
None - followed the plan's D-01 through D-05 and D-09 decisions exactly as specified. The plan's own guidance (structural model from `## [0.8.0]`, the `### Removed` model from `## [0.7.1]`'s `typst_authors` entry, and the exact warning-shim text from `typsphinx/removed_config.py`) left no open questions during execution.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' `<verify>` automated checks and `<acceptance_criteria>` passed on the first attempt; no auto-fixes, no blocking issues, no architectural changes were needed.

## Issues Encountered

`ruff check` could not run in this NixOS-sandboxed worktree (`Could not start dynamically linked executable: ruff`) — this is a pre-existing, previously-recorded environment limitation (lint authority is CI's Windows/macOS/Linux lanes, not this local sandbox) and not a defect introduced by this plan. `black --check` ran clean on the one modified Python file (`tests/test_changelog_page_gate.py`). `mypy typsphinx/` was not run because this plan touches zero files under `typsphinx/` (confirmed by `git diff --name-only -- typsphinx/` producing no output at every task boundary).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The curated `## [0.9.0]` section is ready to be `scripts/extract_changelog_section.py`'d verbatim as the future GitHub Release body — proven by a real extraction run in `57-CHANGELOG-EVIDENCE.md`.
- Plan 57-04 can now write the `Migrating from 0.8.x to 0.9.0` guide referenced by exact title in this section's lead paragraph.
- `REL-08`'s checkbox and its `.planning/REQUIREMENTS.md` traceability row remain untouched — `git diff --name-only -- .planning/REQUIREMENTS.md` was empty at every task boundary, per the plan's prohibitions.
- No git tag, release, or publish action was taken; `typsphinx/` was never touched.

## Self-Check: PASSED

All created/modified files confirmed present on disk (`CHANGELOG.md`,
`tests/test_changelog_page_gate.py`, `57-CHANGELOG-EVIDENCE.md`,
`57-03-SUMMARY.md`); all four task/plan commits confirmed in `git log`
(`e74733d8`, `dcee0201`, `5ec81e36`, `9bf723c2`).

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-17*
