---
phase: 61-v0-9-1-release-prep-prep-only
plan: 03
subsystem: release-prep
tags: [ci, pytest, black, mypy, ruff, uv, github-actions, evidence]

# Dependency graph
requires:
  - phase: 61-01
    provides: the CHANGELOG.md `## [Unreleased]` bullets (PATH-01, IMG-04..07, MSG-02..05) this
      plan dispatches CI against
  - phase: 61-02
    provides: 61-CLOSEOUT-GUARD.md's recorded PHASE_BASE_SHA this plan's product-tree delta
      measurement is anchored at
provides:
  - 61-GREEN-TREE-EVIDENCE.md (local half of SC#3, re-anchored per D-09)
  - 61-CI-EVIDENCE.md (dispatch half of SC#3, re-anchored per D-09)
  - a fresh, phase-own 3-OS CI green run (33260111745) observed on the tip carrying this
    phase's CHANGELOG edit
affects: [61-04, v0.9.2-release-prep]

actuals:
  tokens: 3835
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Evidence-file authority split (52-*-EVIDENCE.md precedent): one file per SC#3 sub-claim,
      each stating explicitly what it is authoritative for and what it defers to a sibling file."
    - "workflow_dispatch as the only route to a 3-OS CI run on a non-main/develop branch
      without opening a PR."

key-files:
  created:
    - .planning/phases/61-v0-9-1-release-prep-prep-only/61-GREEN-TREE-EVIDENCE.md
    - .planning/phases/61-v0-9-1-release-prep-prep-only/61-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "Version checks in this evidence file assert the version literals are UNCHANGED (0.9.0),
    the inverse polarity of Phases 52/57, because D-01 removes the version bump for this phase."
  - "The dispatched ref was this worktree's own agent branch (worktree-agent-a8497ee77be99419f),
    pushed to origin, per the prep_only_fence's explicit permission to push 'THIS worktree's
    branch (or the phase branch)' — not a milestone or feature branch."
  - "ruff check . could not execute on this NixOS host (generic-linux ELF wheel rejected by the
    loader) and is recorded as deferred to CI's `lint` job, never as a pass."
  - "Exactly one CI dispatch was made, per D-09's one-dispatch default (no code-affecting change
    landed mid-phase to justify a second)."

patterns-established:
  - "Positive-control diff measurement: the product-tree delta check is only trusted because it
    is non-empty (CHANGELOG.md, +28/-0) rather than a vacuous empty diff that would look
    identical under a wrong anchor SHA."

requirements-completed: [REL-09]

coverage:
  - id: D1
    description: "The milestone-final tree is proven to be this worktree's own (typsphinx.__file__
      resolves inside the executing worktree, not the main checkout)."
    verification:
      - kind: other
        ref: "uv run python -c \"import typsphinx,os,sys; ...\" — printed absolute __file__ path
          under .claude/worktrees/agent-a8497ee77be99419f/typsphinx/__init__.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Version literals (pyproject.toml:7, README.md:347) are proven UNCHANGED and the
      version-sync guard family is executed by name."
    verification:
      - kind: unit
        ref: "tests/test_readme_version_sync.py, tests/test_preview_version_sync.py,
          tests/test_extension.py::test_version_matches_pyproject_toml"
        status: pass
    human_judgment: false
  - id: D3
    description: "The product-tree delta from PHASE_BASE_SHA is exactly CHANGELOG.md with a
      nonzero insertion count and zero deletions."
    verification:
      - kind: other
        ref: "git diff --stat 5e28fa9d..HEAD -- . ':(exclude).planning' — CHANGELOG.md | 28
          insertions(+)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The full pytest suite, black --check, and mypy are all green on this tree,
      with verbatim tails recorded."
    verification:
      - kind: unit
        ref: "uv run pytest (full suite)"
        status: pass
      - kind: other
        ref: "uv run black --check ."
        status: pass
      - kind: other
        ref: "uv run mypy typsphinx/"
        status: pass
    human_judgment: false
  - id: D5
    description: "The corpus gate's real per-test outcome and the ruff attempt's real outcome are
      both recorded, with no skip or failure presented as a pass."
    verification:
      - kind: unit
        ref: "tests/test_corpus_gate.py -v — 4 passed, 1 skipped (transcribed)"
        status: pass
    human_judgment: false
  - id: D6
    description: "A fresh 3-OS CI run is dispatched on the tip carrying this phase's own
      CHANGELOG edit, with all 12 job conclusions transcribed literally and both windows-latest
      lanes named individually."
    verification:
      - kind: other
        ref: "gh run view 33260111745 --json jobs,headSha,conclusion — conclusion: success,
          headSha matches local tip 14fcb4609, 12/12 jobs success"
        status: pass
    human_judgment: false
  - id: D7
    description: "The recorded CI run's head SHA equals the local tip SHA, and the run is
      genuinely newer than any prior run — not the Phase 60 close's run cited as evidence."
    human_judgment: true
    rationale: "The plan's own <human-check> requires a human to open the recorded run URL and
      independently confirm recency and matching SHAs beyond what a local automated gate can
      assert; this executor's own claim of matching SHAs is evidence toward that confirmation,
      not a substitute for it."

duration: 8min
completed: 2026-08-29
status: complete
---

# Phase 61 Plan 03: Local Green-Tree Proof and Fresh 3-OS CI Dispatch Summary

**Full pytest suite (1513 passed, 5 skipped), black/mypy green, and a fresh workflow_dispatch CI
run (33260111745) all 12/12 green — including both windows-latest lanes — observed on the
milestone-final tip carrying Phase 61's own CHANGELOG edit, with ruff honestly recorded as
unexecutable on this host and deferred to CI's `lint` job.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-08-29T15:23:09Z (approx, first substantive command)
- **Completed:** 2026-08-29T15:31:13Z
- **Tasks:** 3
- **Files modified:** 2 (both newly created evidence files)

## Accomplishments

- Proved the tree under measurement is this worktree's own: `typsphinx.__file__` resolved inside
  `.claude/worktrees/agent-a8497ee77be99419f/`, not the main checkout — the load-bearing
  anti-stale-editable-install proof CLAUDE.md's worktree section warns about.
- Confirmed both version-literal surfaces (`pyproject.toml:7`, `README.md:347`) are UNCHANGED at
  `0.9.0`, the inverted assertion polarity D-01 requires for this phase, and ran the full
  version-sync guard family by name (`test_readme_version_sync.py`, `test_preview_version_sync.py`,
  `test_extension.py::test_version_matches_pyproject_toml`) rather than reasoning it un-failable.
- Measured the product-tree delta from `PHASE_BASE_SHA` (`5e28fa9d`) as exactly `CHANGELOG.md`
  (+28/-0) — a real positive control, not a vacuous empty-diff claim.
- Ran the full pytest suite (1513 passed, 5 skipped), `black --check .` (green, 353 files
  unchanged), and `mypy typsphinx/` (green, 9 source files) — all with verbatim tails recorded.
- Transcribed the corpus gate's real per-test outcome (4 passed, 1 skipped — the skip is the
  deliberately env-gated `test_empty_url_before_after`) and `ruff check .`'s real failure
  (NixOS ELF rejection), recording the latter as deferred to CI's `lint` job rather than as a
  pass or a silent omission.
- Pushed this worktree's own branch to `origin` and dispatched `ci.yml` via
  `workflow_dispatch` (the only route to a 3-OS run on this branch without opening a PR, which
  the fence forbids) — run `33260111745` completed `success` with the dispatched head SHA
  (`14fcb4609`) equal to the local tip, all 12 job conclusions transcribed literally, and both
  `windows-latest` lanes (Python 3.12 and 3.13) named individually as `success`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Prove tree identity and run the full pytest suite on the milestone-final tree** -
   `521d6622` (docs)
2. **Task 2: Run the format, type and version-sync gates and record the lint authority split
   honestly** - `14fcb460` (docs)
3. **Task 3: Dispatch a fresh 3-OS CI run on the tip carrying this phase's CHANGELOG edit and
   record all 12 job conclusions** - `546b8751` (docs)

**Plan metadata:** committed together with this SUMMARY per worktree-mode git_commit_metadata
(STATE.md/ROADMAP.md excluded; orchestrator owns those centrally).

## Files Created/Modified

- `.planning/phases/61-v0-9-1-release-prep-prep-only/61-GREEN-TREE-EVIDENCE.md` - local-run
  half of SC#3: tree identity, product-tree delta, full pytest suite, format/type/version-sync
  gates, honest ruff deferral
- `.planning/phases/61-v0-9-1-release-prep-prep-only/61-CI-EVIDENCE.md` - dispatch half of
  SC#3: pre-dispatch confirmation, the push and `workflow_dispatch` commands, the run's 12
  per-job conclusions, both windows-latest lanes, and the 12-job census derived from `ci.yml`

## Decisions Made

- Dispatched against `worktree-agent-a8497ee77be99419f` (this worktree's own branch), not a
  milestone or feature branch — the `prep_only_fence` explicitly permits pushing "THIS
  worktree's branch (or the phase branch)", and this branch already carries every merged wave-1
  commit including 61-01's CHANGELOG edit.
- Recorded `ruff check .`'s NixOS ELF-rejection failure verbatim and named the CI `lint` job
  ("Lint and Format Check") as the authority that holds — per the standing project convention —
  rather than treating the local unrunnability as a green or omitting it.
- Made exactly one CI dispatch, per D-09's one-dispatch default: no code-affecting change landed
  mid-phase (the prep-only fence excludes `typsphinx/` changes absolutely), so there is no
  pre-bump/post-bump split to justify a second run.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. All three tasks' `<verify>` and `<acceptance_criteria>` blocks passed on first attempt;
no auto-fixes, no blocking issues, no architectural questions.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `61-GREEN-TREE-EVIDENCE.md` and `61-CI-EVIDENCE.md` are both committed and available for
  61-04's fence-observation work and for the phase verifier.
- The `<human-check>` on Task 3's `<verify>` block still needs a human to independently open
  https://github.com/YuSabo90002/typsphinx/actions/runs/33260111745 and confirm recency and
  matching SHAs beyond this executor's own automated claim — surfaced above in `coverage: D7`
  as `human_judgment: true`.
- REL-09 remains untouched at `[ ]` per D-08; this plan cites it for coverage purposes only and
  does not close it, consistent with the phase's must_haves.

---
*Phase: 61-v0-9-1-release-prep-prep-only*
*Completed: 2026-08-29*
