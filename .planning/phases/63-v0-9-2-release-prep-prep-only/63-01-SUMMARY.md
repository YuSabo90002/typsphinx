---
phase: 63-v0-9-2-release-prep-prep-only
plan: 01
subsystem: release-prep
tags: [changelog, version-bump, uv-lock, release-versions, pytest]

requires:
  - phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate
    provides: the visit_image() separator fix (IMG-08/09/10) and its 62-VERIFICATION.md TEST-05
      gate result, which this plan's new Fixed bullet and third Verified bullet cite
provides:
  - the tree bumped to 0.9.2 across pyproject.toml, uv.lock, and README.md in one commit
  - a curated ## [0.9.2] CHANGELOG section (### Fixed + ### Verified only) covering both the
    Windows-path work and the inline-image separator fix, with the never-published version named
    nowhere
  - the extractor's own verbatim stdout and a byte-for-byte identity proof (with the 0.6.5 positive
    control) recorded in 63-CHANGELOG-EVIDENCE.md
  - RELEASE_VERSIONS extended to 16 entries, proven by a docs-extra pytest run with zero skipped
affects: [63-02, 63-03, 63-04, gsd-complete-milestone]

actuals:
  tokens: 5210
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "CHANGELOG four-step structural edit: relocate scratch block under a fresh empty
      [Unreleased] BEFORE renaming the old heading, so the position-based extractor never
      captures the scratch block"
    - "byte-identity proof pattern: awk-slice + blank-line-trim + diff against extractor stdout,
      validated by running the identical pipeline against a known-good prior section as a positive
      control"

key-files:
  created:
    - .planning/phases/63-v0-9-2-release-prep-prep-only/63-CHANGELOG-EVIDENCE.md
  modified:
    - pyproject.toml
    - uv.lock
    - README.md
    - CHANGELOG.md
    - tests/test_changelog_page_gate.py

key-decisions:
  - "The new IMG-08/09/10 Fixed bullet's parenthetical citation was moved onto the bold lead's
    first line (rather than wrapping to the second) so it satisfies the same first-line grep
    pattern the plan's own automated verify block applies to it — matching the house style already
    used by the existing IMG-04..07 bullet."
  - "The three pre-existing Fixed bullets (PATH-01, IMG-04..07, MSG-02..05) were promoted 100%
    verbatim with no trim — no clause in the new lead paragraph made any of their existing prose
    literally redundant."

patterns-established:
  - "Release-prep evidence files record every command with its literal output, never a summary or
    a recalled prior run — this plan's 63-CHANGELOG-EVIDENCE.md follows that discipline
    end-to-end (pre-edit measurements, the lockstep transcript, the extractor run-and-read, the
    milestone-invariant sweep, and the byte-identity proof with its positive control)."

requirements-completed: []

coverage:
  - id: D1
    description: "Version bumped to 0.9.2 across pyproject.toml, uv.lock, and README.md in one
      commit, with uv lock --check, uv sync --extra dev --locked, and the version-sync guard trio
      all green"
    requirement: "REL-10"
    verification:
      - kind: unit
        ref: "tests/test_extension.py::test_version_matches_pyproject_toml"
        status: pass
      - kind: unit
        ref: "tests/test_readme_version_sync.py (3 tests)"
        status: pass
      - kind: unit
        ref: "tests/test_preview_version_sync.py (3 tests)"
        status: pass
      - kind: other
        ref: "uv lock --check && uv sync --extra dev --locked (exit 0 each)"
        status: pass
    human_judgment: false
  - id: D2
    description: "CHANGELOG.md carries a single curated ## [0.9.2] section (### Fixed + ###
      Verified only) with the IMG-08/09/10 bullet leading three verbatim-promoted bullets, and the
      never-published version named nowhere in the file"
    requirement: "REL-10"
    verification:
      - kind: other
        ref: "grep/awk structural assertions transcribed in 63-CHANGELOG-EVIDENCE.md
          (heading count 23, link-ref count 23, Verified count 10, Known Limitations count 1,
          0.9.1 occurrence count 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The scratch 'Planned for Future Releases' block was relocated under a fresh
      empty placeholder BEFORE the rename, and scripts/extract_changelog_section.py was run for
      real: non-empty stdout, zero scratch-block content, byte-identical to the section on disk
      under a comparison whose soundness is proven by a positive control against the pre-existing
      0.6.5 section"
    requirement: "REL-10"
    verification:
      - kind: other
        ref: "uv run python scripts/extract_changelog_section.py 0.9.2 (exit 0, 4087 bytes) plus
          diff against the awk-sliced section (empty, exit 0) and the 0.6.5 positive control
          (empty, exit 0, 1299 bytes both sides) — 63-CHANGELOG-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D4
    description: "RELEASE_VERSIONS extended to 16 entries with its preceding comment updated,
      proven by a run in which both myst_parser-gated content-coverage test classes actually
      executed (not skipped)"
    verification:
      - kind: unit
        ref: "uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v"
        status: pass
    human_judgment: false
  - id: D5
    description: "Nothing under typsphinx/ was touched, no irreversible action was taken, and
      REL-09's checkbox was neither read as satisfied nor moved"
    requirement: "REL-09"
    verification:
      - kind: other
        ref: "git status --porcelain typsphinx/ docs/ (empty, checked after every task); grep -n
          REL-09 .planning/REQUIREMENTS.md confirms the checkbox is still `- [ ]` and the
          Traceability row is still `Pending`"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-30
status: complete
---

# Phase 63 Plan 01: Version Bump and Curated CHANGELOG Promotion Summary

**Bumped the tree to 0.9.2 in one commit and curated `## [Unreleased]` into a single `## [0.9.2]` CHANGELOG section covering both the Windows-path hardening and the inline-image separator fix, with the extractor run for real and its byte-identity proven against a positive control.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-30T10:58:00Z (approx.)
- **Completed:** 2026-08-30T11:24:37Z
- **Tasks:** 3 (1 tracer + 2 auto)
- **Files modified:** 6 (5 product-tree files + 1 new evidence file)

## Accomplishments

- `pyproject.toml`, `uv.lock`, `README.md`, and `CHANGELOG.md` all bumped to/reference `0.9.2`
  and land in one commit (`10d9d95d`); `uv lock --check`, `uv sync --extra dev --locked`, and the
  version-sync guard trio (5 tests) all green.
- `CHANGELOG.md`'s `## [Unreleased]` content promoted into a curated `## [0.9.2] - 2026-08-30`
  section: a new lead paragraph, a new `IMG-08`/`IMG-09`/`IMG-10` `### Fixed` bullet leading the
  three verbatim-promoted `PATH-01`/`IMG-04..07`/`MSG-02..05` bullets, and a fresh three-bullet
  `### Verified` subsection authored from a milestone-invariant sweep re-measured against the
  `v0.9.0` anchor (not copied from a prior entry).
- `scripts/extract_changelog_section.py 0.9.2` run for real: exit 0, 4087-byte non-empty stdout,
  zero scratch-block leakage, and byte-identical (via `diff`) to the section as it sits in
  `CHANGELOG.md` — proven sound by an identical positive-control comparison against the
  pre-existing `## [0.6.5]` section (also empty diff, 1299 bytes both sides).
- `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py` extended to 16 entries through 0.9.2,
  proven by `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` (6
  passed, 0 skipped) — the only environment in which the two `myst_parser`-gated content-coverage
  test classes actually execute.
- `.planning/phases/63-v0-9-2-release-prep-prep-only/63-CHANGELOG-EVIDENCE.md` created and
  populated end-to-end: pre-edit measurements, the version-literal lockstep transcript, the
  extractor run-and-read plus D-20's three named greps, the milestone-invariant sweep with its
  positive control, the RELEASE_VERSIONS proof, the extractor's complete verbatim stdout, the
  byte-identity comparison with the 0.6.5 positive control, and nine fence assertions over the
  final tree.

## Task Commits

Each task was committed atomically (Task 1's tracer slice split across two commits — the
four-file bump, then its evidence file, to keep the bump commit's file list exactly the required
four):

1. **Task 1: End-to-end release slice (version literal through the extractor's stdout)**
   - `10d9d95d` (feat) — `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md` bump + curation
   - `2c411c10` (docs) — `63-CHANGELOG-EVIDENCE.md` created with Task 1's evidence
2. **Task 2: Milestone-invariant sweep and the `### Verified` subsection** - `e6edb2de` (docs)
3. **Task 3: Extend `RELEASE_VERSIONS` and consolidate byte-identity evidence** - `1129ee1a` (test)

**Plan metadata:** commit follows in the orchestrator's post-merge sync (worktree mode — this
executor does not write `STATE.md`/`ROADMAP.md`).

## Files Created/Modified

- `pyproject.toml` - version literal `0.9.0` → `0.9.2` (line 7, the sole hand-edited version
  literal)
- `uv.lock` - self-package `version` stanza regenerated via `uv lock` (never hand-edited)
- `README.md` - Status line (line 347) `0.9.0` → `0.9.2`; `## Known Limitations` untouched
- `CHANGELOG.md` - four-step structural edit: relocated scratch block, renamed heading to
  `## [0.9.2] - 2026-08-30`, authored lead paragraph + new Fixed bullet + Verified subsection,
  rolled tail link block
- `tests/test_changelog_page_gate.py` - `RELEASE_VERSIONS` extended to 16 entries, comment updated
- `.planning/phases/63-v0-9-2-release-prep-prep-only/63-CHANGELOG-EVIDENCE.md` - new evidence file
  (created)

## Decisions Made

- Moved the new `IMG-08`/`IMG-09`/`IMG-10` bullet's parenthetical citation onto the bold lead
  sentence's first line (rather than its wrapped continuation line) to match the house style of
  the existing `IMG-04..07` bullet and satisfy the plan's own first-line grep check.
- Kept all three pre-existing `### Fixed` bullets 100% verbatim — no trim was made, since no
  clause in the new lead paragraph makes any existing bullet's prose literally redundant.
- Split Task 1's tracer commit into two: the four required bump files in one commit (satisfying
  the plan's `git show --name-only` == exactly-four-files acceptance criterion), then the evidence
  file in a separate `docs` commit immediately after.

## Deviations from Plan

None — plan executed as written. One drafting iteration occurred within Task 1 (see "Decisions
Made" above: the IMG-08 citation's line placement) to satisfy the plan's own pre-specified
automated verify command; this was normal execution of the plan's stated acceptance criteria, not
unplanned scope.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `63-02` can proceed: the bumped tree (0.9.2, one commit) and the curated `CHANGELOG.md` are in
  place for the REL-11 fence baseline and SC#5 observation 1 work.
- `63-03`'s full-suite baseline measurement must re-provision `--extra dev` only (not `--extra
  docs`) — this plan's worktree `.venv` now has `myst_parser` installed from Task 3's proof run,
  so a `pytest -q` in THIS worktree reports 1547 passed / 1 skipped rather than the phase's
  1543-passed / 5-skipped baseline. This is expected per the plan's own `<worktree_provisioning>`
  note and does not affect 63-03, which runs in its own fresh worktree.
- REL-09's checkbox remains unchecked and its Traceability row remains `Pending`, confirmed by
  direct read of `.planning/REQUIREMENTS.md` after all three tasks — no tooling flip occurred.

---
*Phase: 63-v0-9-2-release-prep-prep-only*
*Completed: 2026-08-30*
