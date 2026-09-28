---
phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
plan: 02
subsystem: release-prep
tags: [changelog, version-bump, uv-lock, pypi-trusted-publishing, pep-740]

# Dependency graph
requires:
  - phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish
    provides: ATT-01/ATT-02 (Trusted Publishing workflow config, rehearsed) and MSG-06's
      quote_path() fix in typsphinx/translator.py, both landed on the milestone branch before
      this plan ran
provides:
  - "pyproject.toml, uv.lock and README.md moved to 0.9.7 in lockstep, proven by a
    regenerated + idempotent lock, uv lock --check, and both --locked syncs"
  - "A curated CHANGELOG.md ## [0.9.7] section (Changed/Fixed/Known Limitations/Verified) with
    Trusted Publishing / PEP 740 wording measured accurate this session, NUM-01 re-disclosed
    byte-identical, and the tail link block moved"
  - "tests/test_changelog_page_gate.py RELEASE_VERSIONS at 18 entries (0.4.1..0.9.7), zero skips
    in the docs-extra environment"
  - "One five-file bump commit (39cb79f9) and scripts/extract_changelog_section.py 0.9.7's
    stdout transcribed and fingerprinted for the handoff's Release-body check"
affects: [77-03, 77-05, 77-07, complete-milestone]

# Actuals (#2632)
actuals:
  tokens: 7742
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Evidence-file-per-task pattern (77-BUMP-EVIDENCE.md, 77-CHANGELOG-EVIDENCE.md), each
      committed alone before the task's product edits, mirroring the Phase 75 precedent"

key-files:
  created:
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-BUMP-EVIDENCE.md
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-CHANGELOG-EVIDENCE.md
  modified:
    - pyproject.toml
    - uv.lock
    - README.md
    - CHANGELOG.md
    - tests/test_changelog_page_gate.py

key-decisions:
  - "PROVENANCE_POINTER_BASIS = integrity-api: the pip project file page returned PyPI's
    bot-mitigation Client Challenge interstitial when fetched live this session (measured, not
    assumed), so the CHANGELOG's one provenance-pointer sentence names only the measured-working
    Integrity API path shape (no URL, no scheme, placeholder-only) rather than describing file-page
    UI wording that could not be measured this session."
  - "The 0.9.7 heading date (2026-09-28) is the prep authoring date, fixed and not corrected at
    tag time, per the Phase 75 precedent carried into Discretion B."

requirements-completed: []
# REL-17 is split (ROADMAP constraint 12): this plan lands the bump and CHANGELOG curation
# (its prep half) but never flips the checkbox; the tag, upload and GitHub Release are checked
# at /gsd-complete-milestone against observed evidence.

coverage:
  - id: D1
    description: "Version literal moved to 0.9.7 across pyproject.toml, a regenerated uv.lock
      and README.md, proven by a locked sync and the version-sync gates (SC#1)"
    requirement: REL-17
    verification:
      - kind: unit
        ref: "tests/test_readme_version_sync.py"
        status: pass
      - kind: unit
        ref: "tests/test_preview_version_sync.py"
        status: pass
      - kind: other
        ref: "uv lock --check (exit 0), uv sync --extra dev --locked (exit 0), uv sync --extra dev --extra docs --locked (exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Curated ## [0.9.7] CHANGELOG section (Discretion B shape, Discretion C
      provenance wording), fresh ## [Unreleased], tail link block moved, RELEASE_VERSIONS at 18
      entries with zero skips (SC#2)"
    requirement: REL-17
    verification:
      - kind: integration
        ref: "tests/test_changelog_page_gate.py (docs-extra environment, -rs, zero skipped)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Five-file bump commit (chore(release): prepare 0.9.7, 39cb79f9) and
      scripts/extract_changelog_section.py 0.9.7's stdout transcribed, digest-equal to the
      CHANGELOG section body"
    requirement: REL-17
    verification:
      - kind: unit
        ref: "tests/test_changelog_extraction.py"
        status: pass
      - kind: other
        ref: "git show --name-only on 39cb79f9 == CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock"
        status: pass
    human_judgment: false

# Metrics
duration: 10min
completed: 2026-09-28
status: complete
---

# Phase 77 Plan 02: 0.9.7 Version Bump and CHANGELOG Curation Summary

**pyproject.toml/uv.lock/README.md moved to 0.9.7 in one proven-derivable lock regeneration, and
CHANGELOG.md gained a curated `## [0.9.7]` section describing PyPI Trusted Publishing / PEP 740
attestations as audit provenance (never an install-time gate) plus the MSG-06 DEBUG-quoting fix,
landed as one five-file commit whose extractor output is fingerprinted for the release handoff.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-09-28T13:09:10Z
- **Completed:** 2026-09-28T13:18:55Z
- **Tasks:** 3
- **Files modified:** 5 product files (`pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`,
  `tests/test_changelog_page_gate.py`) + 2 evidence files created

## Accomplishments

- Version literal moved to `0.9.7` across `pyproject.toml`, a regenerated (twice, idempotent)
  `uv.lock`, and `README.md`'s Status line — `uv lock --check` exits 0 and both `--locked` syncs
  (`--extra dev`, then `--extra dev --extra docs`) exit 0.
- `CHANGELOG.md` gained one curated `## [0.9.7] - 2026-09-28` section in the settled shape: a
  modest-register lead paragraph, `### Changed` (Trusted Publishing / PEP 740, worded as audit
  provenance, never an install-time gate, per a live-measured Integrity API reading), `### Fixed`
  (MSG-06's DEBUG-message quoting), `### Known Limitations` (NUM-01 carried byte-identical from
  `[0.9.6]`), `### Verified` (three fresh measured invariance claims). A fresh `## [Unreleased]`
  and a moved tail-link block (`[0.9.7]` above `[0.9.6]`, `[Unreleased]` comparing
  `v0.9.7...HEAD`) complete the curation.
- `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` gained `"0.9.7"` (18 entries,
  0.4.1..0.9.7) with its comment restated; the page gate ran zero-skip in the docs-extra
  environment (6 passed).
- All five files landed in one commit (`39cb79f9 chore(release): prepare 0.9.7`) — the union
  SC#1 named plus `tests/test_changelog_page_gate.py` carried from Phase 75 — so a
  `pyproject.toml`-only commit (the shape that once stalled dependency pull requests) never
  existed.
- `scripts/extract_changelog_section.py 0.9.7` was executed (not reimplemented), its stdout
  transcribed verbatim and fingerprinted (3132 bytes, 50 lines, SHA-256
  `82f27b346b89163e08e6f64ba7b119c3fcc4ab20d300d06f6cf94d86a96983f6`), digest-equal to the
  `## [0.9.7]` section body read out of `CHANGELOG.md`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — move the version literal end to end** — `31493336` (docs, evidence-only;
   the three product edits stayed uncommitted per the plan's own sequencing)
2. **Task 2: Curate the CHANGELOG, measure the provenance pointer, RELEASE_VERSIONS** —
   `9ce5d535` (docs, evidence-only; `CHANGELOG.md`/`tests/test_changelog_page_gate.py` stayed
   uncommitted)
3. **Task 3: The one five-file commit, then the extractor transcript** — `39cb79f9` (chore, the
   product bump) and `1ee438c2` (docs, evidence update recording the commit shape and extractor
   transcript)

_Note: this plan's evidence-file-then-product-commit sequencing means each task's own product
edits land inside Task 3's single commit, not its own — this is the plan's designed shape (SC#1),
not a TDD red/green split._

## Files Created/Modified

- `.planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-BUMP-EVIDENCE.md` — Task 1's before/after tables, lock regeneration + idempotency transcript, version-sync gate readings, and Task 3's commit-shape record
- `.planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-CHANGELOG-EVIDENCE.md` — Task 2's base census, provenance-pointer measurement, new-section census, zero-skip gate reading, and Task 3's extractor transcript
- `pyproject.toml` — `[project].version` `0.9.6` → `0.9.7`
- `uv.lock` — `typsphinx` stanza regenerated to `0.9.7` (only stanza that moved)
- `README.md` — `**Status**: Stable (v0.9.7) - Production ready`
- `CHANGELOG.md` — new `## [0.9.7]` section, fresh `## [Unreleased]`, moved tail links
- `tests/test_changelog_page_gate.py` — `RELEASE_VERSIONS` gains `"0.9.7"`, comment restated

## Decisions Made

- `PROVENANCE_POINTER_BASIS = integrity-api` — the pip project file page returned PyPI's
  bot-mitigation "Client Challenge" interstitial when fetched live this session, so the
  CHANGELOG's one pointer sentence names only the measured-working PyPI Integrity API path shape
  (in inline code, no scheme, `<project>`/`<version>`/`<filename>` placeholders) rather than
  quoting file-page UI wording that could not be measured this session.
- The `## [0.9.7]` heading date is `2026-09-28`, the prep authoring date — fixed, not corrected
  at tag time (Phase 75 precedent, carried by Discretion B).

## Deviations from Plan

None — plan executed exactly as written. All measured values (base census, dependency-surface
diffs, `@preview` sites, MSG-06 gate) matched the plan's own planning-time census exactly, so no
`## HALT` condition ever fired.

## Issues Encountered

None. One self-correction during execution: the first draft of the `### Changed` bullet wrapped
`(ATT-01,` / `ATT-02)` across two physical lines, which defeated the verify script's single-line
`grep -qF '(ATT-01, ATT-02)'` check; re-wrapped onto one line before the Task 2 commit, then
re-verified.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Ready for `77-03` (ATT-06 rollback section + controls), `77-05` (preflight), and later waves —
  this plan's `BUMP_COMMIT_SHA` (`39cb79f970c4137d4238023e1df7291c7c282c3a`) and
  `EXTRACT_SHA256`/`EXTRACT_MATCHES_SECTION` are the artifacts the handoff (`77-HANDOFF.md`) and
  `/gsd-complete-milestone`'s Release-body check will read.
- No tag, no push, no publish — every irreversible action stays deferred to
  `/gsd-complete-milestone`, per the plan's own prohibitions and this project's standing
  `branching_strategy: milestone` convention.

## Self-Check: PASSED

- `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`, `tests/test_changelog_page_gate.py`
  all found on disk, all reading `0.9.7`.
- `.planning/phases/.../77-BUMP-EVIDENCE.md` and `77-CHANGELOG-EVIDENCE.md` found on disk.
- `git log --oneline --all --grep="77-02"` returns 3 commits
  (`31493336`, `9ce5d535`, `1ee438c2`); the product bump commit `39cb79f9` is named by its full
  SHA in both evidence files and verified an ancestor of `HEAD`.
- All three tasks' own `<verify>` automated blocks re-ran and passed (`TASK1_VERIFY_PASS`,
  `TASK2_VERIFY_PASS`, `TASK3_VERIFY_PASS`).
- `commits: 4` measured via `git rev-list --count 3984b231e30fbb76ba156d2f9b2abe475231bccf..HEAD`.

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Completed: 2026-09-28*
