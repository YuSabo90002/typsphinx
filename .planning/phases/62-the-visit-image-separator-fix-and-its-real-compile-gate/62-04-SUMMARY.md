---
phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate
plan: 04
subsystem: core-translator
tags: [ci, github-actions, ruff, phase-close, audit, release-fence]

# Dependency graph
requires:
  - phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate
    provides: "plans 01-03's fix, full 18-master fixture, gate module, RED-first evidence and 10 committed goldens -- audited here, not re-derived"
provides:
  - "62-RED-EVIDENCE.md's SC#5 authority CI run section: run 33302087913, status completed, conclusion success, all 12 jobs (including windows-latest and macos-latest each in two Python versions) named individually, and the ruff verdict quoted verbatim from the Lint and Format Check job's Run lint with tox step"
  - "62-RED-EVIDENCE.md's Phase-close measurements section: D-13/SC#4 (40 tests/ entries, all A), IMG-10/SC#3 (9/0 pure insertion, both in_figure branch bodies unmodified, forbidden predicates absent, two exact-byte figure gates pass), D-09 (CHANGELOG/pyproject/uv.lock/README untouched, no v0.9.2 tag), and a green full-suite/black/mypy baseline on the merged tip"
  - "the canonical milestone branch gsd/v0.9.2-inline-image-blocker-fix-and-release advanced on origin from plan 01's 5a837238 to the phase's final tip 0366eca4 before dispatch"
affects: [63]

# Actuals (#2632)
actuals:
  tokens: 4984
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Measurement-only closing plan: no source file touched, every SC discharged by transcribing a command's own output into the evidence file rather than asserting it"

key-files:
  created: []
  modified:
    - .planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md

key-decisions:
  - "Pushed the canonical branch's local tip (0366eca4) to origin as part of Task 1's action, advancing past plan 01's earlier push (5a837238) which held only through plan 01's own commit -- required so the dispatched CI run compiled and tested the tree actually carrying the fix, the full fixture, the widened gate module and the RED-first evidence, not a stale 3-master tracer-only snapshot."
  - "Recorded the plan action text's phrase 'Run linters' as a paraphrase, not the literal step name -- the actual CI step is titled 'Run lint with tox' (ci.yml's lint job, running tox -e lint, which itself runs black --check . then ruff check .). Quoted the step's own ruff check . output verbatim ('All checks passed!') rather than silently renaming the step in the evidence to match the plan's paraphrase, so a reader can cross-check against the run directly."
  - "Declared requirements-completed for all four phase requirements (IMG-08, IMG-09, IMG-10, TEST-05), not just this plan's own frontmatter subset (IMG-09, IMG-10), per this plan's own <output> directive: 'declare requirements-completed: [IMG-08, IMG-09, IMG-10, TEST-05] only if every acceptance criterion in this plan and in plans 01-03 was met and recorded.' Verified: all three prior plans' Self-Check sections read PASSED and this plan's own two tasks' acceptance criteria all passed, so the full set is declared."

requirements-completed: [IMG-08, IMG-09, IMG-10, TEST-05]

coverage:
  - id: D1
    description: "A CI run dispatched with gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release reached completed status with conclusion success; windows-latest and macos-latest are each named individually (two Python versions each) with their own recorded success conclusion, alongside ubuntu-latest, Lint and Format Check, Type Check, Code Coverage, Integration Test - basic/advanced and Build Package"
    requirement: null
    verification:
      - kind: other
        ref: "gh run view 33302087913 --json status,conclusion,jobs (status completed, conclusion success, 12/12 jobs success); transcribed into 62-RED-EVIDENCE.md § 'SC#5 - authority CI run'"
        status: pass
    human_judgment: false
  - id: D2
    description: "ruff's verdict for this phase is taken exclusively from the dispatched run's Lint and Format Check job's Run lint with tox step (ruff check . -> All checks passed!), never from this machine, where ruff is an unrunnable generic-linux ELF in this freshly provisioned worktree venv"
    requirement: "TEST-05"
    verification:
      - kind: other
        ref: "gh run view --job 99232013129 --log, the ruff check . invocation's own output quoted verbatim in 62-RED-EVIDENCE.md § 'SC#5 - authority CI run'"
        status: pass
    human_judgment: false
  - id: D3
    description: "Exactly one 0.9.2 branch exists locally (the canonical config-derived name), no v0.9.2 tag exists locally or on origin, and no PyPI upload, GitHub Release or PR was created -- the release half belongs to Phase 63"
    requirement: null
    verification:
      - kind: other
        ref: "git branch --list 'gsd/v0.9.2*' | wc -l (1); git tag -l 'v0.9.2*' and git ls-remote --tags origin 'v0.9.2*' (both empty); gh pr list --head gsd/v0.9.2-inline-image-blocker-fix-and-release (empty)"
        status: pass
    human_judgment: false
  - id: D4
    description: "git diff --name-status over the phase range scoped to tests/ shows only A entries (40/40); no M entry exists to report as an over-reach signal; tests/test_translator.py is absent from the diff entirely"
    requirement: "IMG-08"
    verification:
      - kind: other
        ref: "git diff --name-status 5a837238..HEAD -- tests/ (40 A entries, 0 M); transcribed in 62-RED-EVIDENCE.md § 'Phase-close measurements' -> D-13/SC#4"
        status: pass
    human_judgment: false
  - id: D5
    description: "The phase diff over typsphinx/translator.py is a pure 9/0 insertion in which both in_figure branch bodies are textually unchanged, and none of the three line-boundary-predicate spellings ROADMAP SC#3 enumerates appears in the file"
    requirement: "IMG-10"
    verification:
      - kind: other
        ref: "git diff --numstat 5a837238..HEAD -- typsphinx/translator.py (9 0); full diff transcribed; grep -F for the three forbidden spellings (no match, exit 1) -- all in 62-RED-EVIDENCE.md § 'Phase-close measurements' -> IMG-10/SC#3"
        status: pass
    human_judgment: false
  - id: D6
    description: "The two exact-byte figure assertions in tests/test_nested_figure_render_gate.py and tests/test_pdf_render_gate.py pass and neither file was edited in this phase"
    requirement: "IMG-10"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_nested_figure_render_gate.py tests/test_pdf_render_gate.py -q (38 passed)"
        status: pass
    human_judgment: false
  - id: D7
    description: "CHANGELOG.md, pyproject.toml, uv.lock and README.md are untouched by the entire phase range, and no v0.9.2 tag exists anywhere -- the prep-only fence held"
    requirement: null
    verification:
      - kind: other
        ref: "git diff --name-only 5a837238..HEAD -- CHANGELOG.md pyproject.toml uv.lock README.md (empty); 62-RED-EVIDENCE.md § 'Phase-close measurements' -> D-09"
        status: pass
    human_judgment: false
  - id: D8
    description: "The final measurement was taken on the merged phase tip (this worktree's HEAD, which includes plans 01-03 plus this plan's own Task 1 commit), not on any individual pre-merge worktree, so a tests/ modification introduced by one plan and reverted by another could not hide from the measurement"
    requirement: null
    verification: []
    human_judgment: true
    rationale: "This is a backstop property about the measurement's vantage point, not a single command's output -- the plan itself designates it 'verification: backstop'. Confirmed by construction (this worktree forked from the merged wave-3 tip 0366eca4, and all commands ran after that fork) but left human_judgment: true because the property is structural, not independently re-derivable from one test run."

# Metrics
duration: ~14min
completed: 2026-08-30
status: complete
---

# Phase 62 Plan 04: The Single Authority CI Run and Phase-Close Measurements Summary

**Dispatched the one authority CI run against the phase's final code tip (all 12 jobs green, including both `windows-latest` and `macos-latest` in two Python versions each, with `ruff`'s verdict quoted verbatim from CI's `Run lint with tox` step) and recorded every SC#3/SC#4/D-09 phase-close measurement as a command transcript in `62-RED-EVIDENCE.md`, closing all four of Phase 62's requirements.**

## Performance

- **Duration:** ~14 min
- **Started:** 2026-08-30 (Task 1's branch push, ~08:38 UTC)
- **Completed:** 2026-08-30T08:52:44Z
- **Tasks:** 2
- **Files modified:** 1 (`62-RED-EVIDENCE.md`, appended twice)

## Accomplishments

- Re-measured `git branch -vv` per D-12: no decoy `gsd/v0.9.2-milestone` present, exactly one `0.9.2` branch, at the local worktree's tip `0366eca47c483e7a1ee735e737a015fc094e7091` -- ahead of `origin`'s copy, which still held plan 01's earlier push at `5a837238`. Pushed the canonical branch's current tip to `origin` so the dispatched run would compile and test the tree that actually carries the fix, the full 27-document/18-master fixture, the widened gate module and the RED-first evidence -- not the 3-master tracer snapshot plan 01 pushed.
- Dispatched exactly one authority CI run (D-11): `gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release`, run id `33302087913`. Waited to `completed` via `gh run watch --exit-status`. Final `conclusion: success` across all 12 jobs: `Type Check`, `Lint and Format Check`, six `Test Python {3.12,3.13} on {ubuntu,windows,macos}-latest` jobs (both `windows-latest` and `macos-latest` lanes named individually, per SC#5's explicit requirement), `Code Coverage`, `Integration Test - basic`, `Integration Test - advanced`, `Build Package`.
- `ruff`'s verdict recorded from the run's `Lint and Format Check` job's `Run lint with tox` step (the literal CI step name; the plan's own action text says "Run linters" as a paraphrase, documented as such in the evidence) -- `tox -e lint` runs `black --check .` then `ruff check .`; the step's own log shows `ruff check .` returned `All checks passed!`. This is the sole source of the phase's lint verdict, explicitly stated in the evidence with the reason (`ruff` is an unrunnable generic-linux ELF in a freshly `uv sync`-provisioned worktree venv on this host).
- Recorded the release fence at the CI-dispatch observation point: exactly one local `0.9.2` branch, no `v0.9.2` tag locally or on `origin`, no PR against the branch, only this one CI run on record for the branch.
- Task 2 recorded all phase-close measurements against the merged tip: `git diff --name-status` over `tests/` shows 40 entries, all `A`, zero `M` (D-13/SC#4 -- no over-reach signal to report); `git diff --numstat` over `typsphinx/translator.py` shows a pure `9/0` insertion with the full diff transcribed, showing both `in_figure` branch bodies textually unchanged (IMG-10/SC#3); a repo-wide grep for the three forbidden line-boundary-predicate spellings finds nothing; the two exact-byte figure gate tests (38 total) pass and are absent from the phase's `tests/` diff; `CHANGELOG.md`/`pyproject.toml`/`uv.lock`/`README.md` are untouched and no `v0.9.2` tag exists anywhere (D-09); the full suite (1543 passed, 5 skipped), `black --check .` and `mypy typsphinx/` are all green on the merged tip, with an explicit statement that no local `ruff` verdict is claimed.
- Cross-checked both of plan 01's amendments by a direct read of the final shipped source (`typsphinx/translator.py:4718-4800`): the leading separator triad still sits above the `in_figure`/`else` split (AMENDED D-08, needed for the two legend shapes), and `depart_image()`'s trailing half still consults `_mark_inline_concat_content()` before its unconditional trailing newlines (needed for the field-list-body shape).
- All four of Phase 62's requirements (IMG-08, IMG-09, IMG-10, TEST-05) are declared complete: every acceptance criterion across plans 01, 02, 03 and this plan's own two tasks was met and recorded, per this plan's explicit `<output>` instruction.

## Task Commits

Each task was committed atomically:

1. **Task 1: Dispatch the single authority CI run and record all three OS lanes** - `e75ba3d0` (docs)
2. **Task 2: Phase-close measurements - zero test edits, branch bodies untouched, release fence held** - `c46d413d` (docs)

**Plan metadata:** SUMMARY commit follows separately per worktree convention.

## Files Created/Modified

- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md` - gained `## SC#5 - authority CI run` (Task 1) and `## Phase-close measurements` (Task 2) sections; no source file touched anywhere in this plan

## Decisions Made

- Pushed the canonical branch's local tip to `origin` before dispatch (Task 1's own first action) rather than trusting plan 01's earlier push to still be current -- measured that `origin` was 19 commits behind before pushing, confirming the push was necessary rather than redundant.
- Recorded the CI step's actual name (`Run lint with tox`) alongside the plan's paraphrase (`Run linters`) rather than silently treating them as identical, so the evidence file is independently auditable against the live run.
- Declared `requirements-completed: [IMG-08, IMG-09, IMG-10, TEST-05]` (the full phase set) rather than this plan's own frontmatter subset (`IMG-09, IMG-10`), per the plan's explicit closing-plan `<output>` instruction and the shared-ID readiness gate (`requirements.ready-ids` confirmed all four ready -- no sibling plan blocking).

## Deviations from Plan

None - plan executed exactly as written. Both tasks' acceptance criteria were met on the first attempt with no auto-fixes required.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All four of Phase 62's requirements (IMG-08, IMG-09, IMG-10, TEST-05) are complete, evidenced end to end: the separator fix, the full 16-FAIL/9-PASS/18-master real-compile matrix, the RED-first choreography with 10 committed goldens, and now the single authority CI run plus every phase-close structural measurement.
- Phase 63 (v0.9.2 Release Prep) can proceed: `CHANGELOG.md`, `pyproject.toml`, `uv.lock` and `README.md` remain untouched by this phase, and the canonical milestone branch `gsd/v0.9.2-inline-image-blocker-fix-and-release` is on `origin` at the phase's final tip with a completed, all-green CI run on record.
- No blockers.

---
*Phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate*
*Completed: 2026-08-30*

## Self-Check: PASSED

- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md` - FOUND (contains both `## SC#5 - authority CI run` and `## Phase-close measurements`, confirmed via grep)
- Commit `e75ba3d0` - FOUND in `git log --oneline`
- Commit `c46d413d` - FOUND in `git log --oneline`
- All task `<acceptance_criteria>` re-verified: PASS (CI run `33302087913` completed/success with `windows-latest`/`macos-latest` named individually and the `Run lint with tox` step's `ruff check .` output quoted; exactly one local `0.9.2` branch, no tag, no PR; `tests/` diff 40/40 `A` entries; `typsphinx/translator.py` diff `9/0`, forbidden predicates absent; two exact-byte figure gates pass; prep-only fence untouched; full suite 1543 passed/5 skipped, black + mypy clean)
