---
phase: 52-v0-8-0-release-prep-prep-only
plan: 01
subsystem: infra
tags: [release, uv, pyproject, semver, changelog-extractor]

# Dependency graph
requires:
  - phase: 51-two-layer-output-documentation
    provides: a green, documented v0.8.0 tree with zero lines changed under typsphinx/ in this plan
provides:
  - pyproject.toml/README.md/uv.lock all reading 0.8.0 in lockstep
  - regenerated editable-install metadata so typsphinx.__version__ reports 0.8.0
  - proof the release machinery's CHANGELOG extractor is live on this tree before 52-02 authors
    the section it will read
  - the first of three fence observations that no v0.8.0 tag exists locally or on origin
affects: [52-02-changelog-curation, 52-04-ci-authority, 52-06-invariant-sweep, 52-07-release-evidence-and-handoff]

# Actuals (#2632)
actuals:
  tokens: 3895
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Release version bump: edit pyproject.toml literal -> uv lock -> uv sync --extra dev --locked
      (regenerates editable-install .dist-info/.pth, the step that actually moves
      typsphinx.__version__) -> read back via importlib.metadata"

key-files:
  created:
    - .planning/phases/52-v0-8-0-release-prep-prep-only/52-BUMP-EVIDENCE.md
    - .planning/phases/52-v0-8-0-release-prep-prep-only/COVERAGE.md
  modified:
    - pyproject.toml
    - README.md
    - uv.lock

key-decisions:
  - "Used the live-measured commits-ahead figure (161) instead of the stale planning-time figures
    (155 in 52-CONTEXT.md, 157 in 52-RESEARCH.md), per the plan's own re-measurement requirement.
    Neither planning document was edited to correct the discrepancy -- out of this plan's scope,
    recorded explicitly in 52-BUMP-EVIDENCE.md so a later reader does not treat it as an error."
  - "Tracer feedback gate fired as an interactive checkpoint (auto mode confirmed inactive via
    gsd-tools query config-get workflow.auto_advance / _auto_chain_active, both false) --
    execution paused after Task 1's commit for orchestrator re-verification before Tasks 2/3 ran."

patterns-established:
  - "Pattern 1 from 52-PATTERNS.md (config/batch version bump) executed verbatim -- exact
    analog to Phase 46's own bump, only the version strings differ."

requirements-completed: []
# REL-07 stays OPEN by design -- it closes at /gsd-complete-milestone, not in this phase
# (52-CONTEXT.md, ROADMAP.md, and this plan's own frontmatter all state this explicitly).
# The plan lists requirements: [REL-07] as the requirement this plan contributes evidence toward,
# but the checkbox/traceability row must not flip here.

coverage:
  - id: D1
    description: "Version literal moved 0.7.1 -> 0.8.0 across pyproject.toml, README.md, and
      uv.lock in one edit set, with the editable-install metadata regenerated so
      typsphinx.__version__ actually reports 0.8.0 (not just the literal)."
    requirement: "REL-07"
    verification:
      - kind: unit
        ref: "tests/test_extension.py::test_version_matches_pyproject_toml"
        status: pass
      - kind: unit
        ref: "tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject"
        status: pass
      - kind: other
        ref: "uv run python -c \"import typsphinx; print(typsphinx.__version__)\" -> 0.8.0"
        status: pass
    human_judgment: false
  - id: D2
    description: "The release machinery's own CHANGELOG extractor (scripts/extract_changelog_section.py)
      proven live on this tree in both directions -- exits 0 with a non-empty body against the
      already-published 0.7.1 section, exits 1 with a stderr message against the nonexistent 9.9.9 --
      before plan 52-02 authors the 0.8.0 section it will read next."
    requirement: "REL-07"
    verification:
      - kind: other
        ref: "uv run python scripts/extract_changelog_section.py 0.7.1 (exit 0) and
          uv run python scripts/extract_changelog_section.py 9.9.9 (exit 1)"
        status: pass
    human_judgment: false
  - id: D3
    description: "All three version-sync guard modules pass with zero skips on the post-bump tree,
      and the phase-head anchors (v0.7.1 commit sha, origin/main merge-base, ancestry, commits-ahead
      count, .planning-excluded shortstat) were re-measured live and recorded in
      52-BUMP-EVIDENCE.md, with the fence (no v0.8.0 tag locally or on origin) observed empty both
      before and after the edit."
    requirement: "REL-07"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py (3 functions, combined JUnit-XML:
          tests=5 skipped=0 failures=0 errors=0)"
        status: pass
      - kind: other
        ref: "git tag -l v0.8.0 && git ls-remote --tags origin v0.8.0 (both empty)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Reasoned, matrix-free external-API coverage declaration (COVERAGE.md) written so
      the seal-time api-coverage.verify-pre re-run over this phase's PLAN bodies does not block on
      the project's standing false-positive shape (gh run view / git ls-remote / release.yml
      prose)."
    verification:
      - kind: other
        ref: "test -f COVERAGE.md && grep -q 'No external API integration:' COVERAGE.md &&
          grep -c '^| ' COVERAGE.md == 0"
        status: pass
    human_judgment: false

# Metrics
duration: ~13min execution wall-time (across two sessions, separated by an orchestrator checkpoint
  pause after Task 1's tracer commit; see Deviations)
completed: 2026-08-15
status: complete
---

# Phase 52 Plan 01: v0.8.0 Version Bump and Release-Machinery Liveness Proof Summary

**Version literal moved 0.7.1 -> 0.8.0 across pyproject.toml/README.md/uv.lock with the
editable-install metadata regenerated, the three version-sync guards green at zero skips, and the
CHANGELOG extractor proven live in both directions before plan 52-02 writes the section it reads.**

## Performance

- **Duration:** ~13 min execution wall-time (two sessions: pre-checkpoint through Task 1's commit,
  then post-approval through Tasks 2-3 and this summary)
- **Started:** 2026-08-15T00:41:09Z (first live anchor re-measurement, before any edit)
- **Completed:** 2026-08-15T00:47:02Z
- **Tasks:** 3/3
- **Files modified:** 5 (3 source-tree, 2 new planning artifacts)

## Accomplishments

- All three release-surface version literals moved to `0.8.0` in one edit set, verified byte-exact
  against the pre-bump tree for everything outside those three literals (the `[project]
  dependencies` array is byte-identical to HEAD's).
- `uv lock` + `uv sync --extra dev --locked` regenerated both `uv.lock`'s own `typsphinx` entry and
  the editable-install `.dist-info`/`.pth` metadata, so `typsphinx.__version__` genuinely reports
  `0.8.0` on import rather than only the source literal moving.
- `scripts/extract_changelog_section.py` — the exact reader `release.yml`'s `validate` and
  `create-release` jobs call — proven live on this tree: exit 0 with a real body against the
  published `0.7.1` section, exit 1 with a stderr message against `9.9.9`.
- All three version-sync guard test modules (`test_version_matches_pyproject_toml`,
  `test_readme_version_sync`, `test_preview_version_sync`'s 3 functions) pass with zero skips —
  combined JUnit-XML: `tests="5" skipped="0" failures="0" errors="0"`.
- Every phase-head anchor figure was re-measured live rather than transcribed from planning
  documents: `v0.7.1^{commit}` = `48bf135428bb093a77a432d93d16088ce6930342`, `origin/main`
  merge-base = `a97fe736a4311cf04109cfafd1154a3e3b95d208` (confirmed ancestor), commits-ahead of
  `origin/gsd/v0.8.0-multi-master-composition` = **161** (not the stale 155/157 carried in
  `52-CONTEXT.md`/`52-RESEARCH.md`), `.planning`-excluded shortstat = `341 files changed, 15141
  insertions(+), 2472 deletions(-)`.
- The prep/publish fence was observed empty three times (before Task 1's edit, after Task 1's
  commit for the tracer checkpoint, and again in the `52-BUMP-EVIDENCE.md` SC#5 section): no
  `v0.8.0` tag exists locally or on `origin`.
- Zero lines changed under `typsphinx/` — `git diff --name-only -- typsphinx/` empty at every
  checkpoint, holding the prep-only fence (D-01).

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end release-surface slice — re-measure the fence and anchors, then bump the
   version across all three surfaces and regenerate the editable install** - `1f47b659` (feat)
2. **Task 2: Run the version-sync guard battery and record SC#1's evidence with the live anchor
   re-measurement** - `4d5fa7ab` (docs)
3. **Task 3: Write the reasoned external-API coverage declaration** - `b232cf20` (docs)

_Note: this plan carried no `tdd="true"` tasks; each task is a single atomic commit._

## Files Created/Modified

- `pyproject.toml` - `[project] version` literal, `0.7.1` -> `0.8.0`
- `README.md` - Status line, `Stable (v0.7.1)` -> `Stable (v0.8.0)`
- `uv.lock` - regenerated; its own `typsphinx` block now carries `version = "0.8.0"`; no other line
  moved (dependency set byte-identical to HEAD's)
- `.planning/phases/52-v0-8-0-release-prep-prep-only/52-BUMP-EVIDENCE.md` - SC#1's verbatim
  transcripts, the release-machinery consumer-path proof, the guard-test transcripts, the live
  anchor re-measurement, and the SC#5 fence observation
- `.planning/phases/52-v0-8-0-release-prep-prep-only/COVERAGE.md` - reasoned no-external-API
  declaration for the seal-time `api-coverage.verify-pre` re-run

## Decisions Made

- **Live-measured commits-ahead figure (161) used, not the stale planning-time figures.**
  `52-CONTEXT.md` recorded 155 and `52-RESEARCH.md` recorded 157, both measured against the tree
  as it stood at their own respective write times. Six more commits landed on the branch between
  the `52-RESEARCH.md` measurement and this plan's own re-measurement (this phase's own
  discuss/research/plan/pattern-map commits, plus this plan's Task 1 bump). Per the plan's own
  `must_haves.truths`, every anchor figure had to be re-measured live and never transcribed — 161
  is that live figure, and `52-BUMP-EVIDENCE.md` explicitly notes the discrepancy so a later reader
  does not mistake it for a measurement error. Neither `52-CONTEXT.md` nor `52-RESEARCH.md` was
  edited to reconcile the figures — out of this plan's scope, and the user explicitly declined to
  authorize touching either file when resolving the checkpoint below.
- **Tracer feedback gate observed as an interactive checkpoint.** This plan's Task 1 carries
  `type="tracer"`. Auto mode was confirmed inactive (`gsd-tools query config-get
  workflow.auto_advance` and `workflow._auto_chain_active` both returned `false`), so per the
  executor's tracer-feedback-gate rule, execution stopped immediately after Task 1's commit and
  surfaced a `checkpoint:human-verify` on the proven slice before Tasks 2/3 (the expansion tasks)
  ran. The orchestrator independently re-verified every claim in the checkpoint (worktree base, the
  three-file diff scope, the two version literals, all four anchor figures byte-for-byte, and the
  empty fence) and returned `approved`. See Issues Encountered.

## Deviations from Plan

None - plan executed exactly as written. The tracer feedback gate pause (documented above under
Decisions Made) is standing executor behavior for a `type="tracer"` task under interactive mode,
not a plan deviation — no task content, file scope, or acceptance criterion changed as a result.

## Issues Encountered

**Tracer feedback gate checkpoint (not an error).** After committing Task 1 (`1f47b659`), the
executor's tracer-feedback-gate rule required stopping for human verification before proceeding to
Tasks 2/3, since auto mode was confirmed inactive. The checkpoint reported Task 1's `<verify>`
result (all clauses passing) and the live-measured anchors. The orchestrator independently
re-measured every reported figure against both the worktree and its own tree, confirmed byte-exact
agreement, and returned `approved` — along with two directives (use the live 161 figure rather than
the stale planning-time figures, and re-confirm the per-worktree `uv run` provisioning convention),
both of which this plan's execution already satisfied. Execution then resumed cleanly from Task 2
with no rework of Task 1.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The post-bump tree is ready for plan 52-02 to author the `## [0.8.0]` CHANGELOG entry: the
  extractor's liveness (both success and failure directions) is proven, and the release-surface
  literals are already in lockstep so 52-02 does not need to touch them again.
- Plan 52-04's dispatched CI run is unblocked to establish lint/type/py312/py313/docs matrix
  authority — this plan deliberately took no local authority over that surface (`tox`/`tox -e
  py312` both fail on this NixOS machine for pre-existing, unrelated ELF reasons, recorded in
  `52-BUMP-EVIDENCE.md`'s "Executed versus skipped" section).
- Plan 52-06's full mechanical `@preview`-version-lockstep sweep and prep-only-fence invariant sweep
  are unblocked — this plan's own spot-check (Task 2's Invariant spot-check section) confirms
  `test_preview_version_sync.py` passed and that this plan touched no template/writer/import code,
  but explicitly defers the milestone-wide sweep to 52-06.
- Plan 52-07's `52-RELEASE-EVIDENCE.md`/`52-HANDOFF.md` still owe SC#5's standing **two** required
  fence observations — this plan's own SC#5 section is an additional, third data point, not a
  substitute for either.
- No blockers. REL-07 stays intentionally open per the plan's frontmatter and `52-CONTEXT.md`'s
  D-01/D-03 decisions — it closes at `/gsd-complete-milestone`, not in this phase.

## Self-Check: PASSED

- FOUND: `.planning/phases/52-v0-8-0-release-prep-prep-only/52-BUMP-EVIDENCE.md`
- FOUND: `.planning/phases/52-v0-8-0-release-prep-prep-only/COVERAGE.md`
- FOUND: `pyproject.toml` carries `version = "0.8.0"`
- FOUND: commit `1f47b659` (Task 1)
- FOUND: commit `4d5fa7ab` (Task 2)
- FOUND: commit `b232cf20` (Task 3)

---
*Phase: 52-v0-8-0-release-prep-prep-only*
*Completed: 2026-08-15*
