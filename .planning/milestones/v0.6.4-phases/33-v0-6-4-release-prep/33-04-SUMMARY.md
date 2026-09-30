---
phase: 33-v0-6-4-release-prep
plan: 04
subsystem: release
tags: [changelog, readthedocs, evidence, handoff, milestone-invariants, honest-verifier]

# Dependency graph
requires:
  - phase: 33-01
    provides: version bump to 0.6.4 (pyproject.toml/README.md/uv.lock) — cited as SC#1 evidence
  - phase: 33-02
    provides: curated ## [0.6.4] CHANGELOG entry + tail link block — cited as SC#2 evidence
  - phase: 33-03
    provides: English-ized top-level planning docs (D-05), independent file set, no dependency for this plan's content
provides:
  - "33-RELEASE-EVIDENCE.md: SC#3 real-HTTP re-verification of pyproject.toml's Documentation URL (302 -> 200 at /en/latest/) and SC#4 milestone-invariant assertion over the full main..HEAD diff (merge-base 771ec56f, 279 commits), with verbatim command output for every claim"
  - "33-HANDOFF.md: the SC#5 8-item publish + owner-manual checklist naming owner and ordering for each item, an explicit not-done-in-this-phase scope-fence section, and verbatim proof (empty git tag -l / git ls-remote --tags) that no irreversible state was created"
affects: [gsd-complete-milestone (consumes 33-HANDOFF.md's checklist directly), 33-MILESTONE-CLOSE (if it exists, cites 33-RELEASE-EVIDENCE.md as the SC#3/SC#4 record)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Evidence file assembled incrementally across two tasks in one file (SC#3 section, then an appended SC#4 section), each task's commit independently satisfying its own automated <verify> grep checks before the next task appends."
    - "Positive-control pattern for empty-diff assertions: an empty git diff --stat result is only recorded as a genuine PASS when paired with a non-empty control diff over a known-changed pathspec in the same evidence block, so the check's own machinery is provably functioning."

key-files:
  created:
    - .planning/phases/33-v0-6-4-release-prep/33-RELEASE-EVIDENCE.md
    - .planning/phases/33-v0-6-4-release-prep/33-HANDOFF.md
  modified: []

key-decisions:
  - "Neither deliverable is named 33-VERIFICATION.md, per the plan's explicit filename constraint — that name is reserved by /gsd-verify-work, which overwrites it wholesale."
  - "The commit count is recorded as re-measured at execution time (279), not carried forward from any planning document's cached figure (254 at discussion, 256 at research, 258 at planning) — the drift across this phase's own artifacts is the concrete instance of Milestone Invariant #4."
  - "The live RTD HTTP observation (SC#3) is deliberately kept out of CHANGELOG.md per D-03: it has no standing re-verification mechanism, so it is recorded only in the dated evidence file, not asserted as a durable fact."
  - "33-HANDOFF.md states plainly that REL-02's PyPI-publish and /en+/ja stable-serving half is NOT satisfied by this phase and is structurally out of reach without the v0.6.4 tag — no language implying it is 'effectively done' or 'likely satisfied'."

patterns-established: []

requirements-completed: [REL-02]

coverage:
  - id: D1
    description: "pyproject.toml's Documentation URL is re-verified over real HTTP on the prepared tree: parsed via tomllib, fetched with curl (un-followed 302 + followed terminal 200), ISO-8601 timestamped, and recorded verbatim in 33-RELEASE-EVIDENCE.md."
    requirement: "REL-02"
    verification:
      - kind: other
        ref: "Live curl fetch during this task: https://typsphinx.readthedocs.io/ -> 302 Location: https://typsphinx.readthedocs.io/en/latest/ -> 200. Recorded in 33-RELEASE-EVIDENCE.md SC#3 section."
        status: pass
    human_judgment: false
  - id: D2
    description: "The three milestone invariants (zero new runtime deps, no @preview version bump across 4 surfaces, zero typsphinx/ changes) are asserted over the full main..HEAD diff (merge-base 771ec56f, 279 commits) with verbatim git diff output and a working positive control, plus the full pytest suite green at baseline (647 passed / 1 skipped / 0 failed)."
    requirement: "REL-02"
    verification:
      - kind: integration
        ref: "git diff main..HEAD --stat -- typsphinx/ (empty, PASS) + positive control git diff main..HEAD --stat -- pyproject.toml (non-empty); uv run python -m pytest -q -> 647 passed, 1 skipped. Recorded in 33-RELEASE-EVIDENCE.md SC#4 section."
        status: pass
    human_judgment: false
  - id: D3
    description: "33-HANDOFF.md enumerates all 8 publish/owner-manual items with owner and ordering, states the unmet half of REL-02 explicitly, and proves via verbatim empty git tag -l v0.6.4 / git ls-remote --tags origin v0.6.4 that no tag or publish action occurred in this phase."
    requirement: "REL-02"
    verification:
      - kind: other
        ref: "grep -cP CJK-regex 33-HANDOFF.md == 0; git tag -l v0.6.4 (empty); git ls-remote --tags origin v0.6.4 (empty). All re-run during this task."
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-28
status: complete
---

# Phase 33 Plan 04: Evidence + Handoff (SC#3, SC#4, SC#5) Summary

**Real-HTTP re-verification of the Read the Docs `Documentation` URL (302→200), the three milestone invariants re-asserted with verbatim evidence over the full 279-commit `main..HEAD` diff, and an 8-item English publish/owner-manual handoff checklist proving via empty `git tag`/`git ls-remote` that no irreversible state was created.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-27T21:14:00Z (approx.)
- **Completed:** 2026-07-27T21:39:00Z (approx.)
- **Tasks:** 3 completed
- **Files modified:** 2 (both new)

## Which success criteria are MET vs. HANDED OFF

**MET in this phase:**
- **SC#1** (version bump — plan 33-01, cited here as evidence): `pyproject.toml`/`README.md`/`uv.lock` all read `0.6.4`; `typsphinx.__version__` proven `0.6.4`.
- **SC#2** (CHANGELOG — plan 33-02, cited here as evidence): curated `## [0.6.4]` entry + tail link block landed, resolved date `2026-07-28`.
- **SC#3** (this plan, Task 1): the `Documentation` metadata URL, parsed live from the prepared tree, was fetched over real HTTP and terminates at a 2xx status (`302` → `200` at `/en/latest/`).
- **SC#4** (this plan, Task 2): all three milestone invariants hold over the full milestone diff, evidenced with verbatim `git diff` output, a working positive control, and a green full test suite (647 passed / 1 skipped / 0 failed).

**HANDED OFF, not met, by design:**
- **REL-02's remaining half** — `typsphinx 0.6.4` live on PyPI, and `/en/stable/` **and** `/ja/stable/` both serving that released version — is **not satisfied** by this phase. It structurally cannot be: both require the `v0.6.4` git tag, and this phase creates no tag. This is recorded as an explicit unmet criterion in `33-HANDOFF.md` (SC#5), transferred to `/gsd-complete-milestone` and the owner, not asserted as done or "effectively" done.

**REL-02 overall is NOT reported as satisfied by this phase** — only its half-satisfiable portion (SC#1-4) is MET; the publish half is HANDED OFF per the plan's explicit `<output>` instruction.

## Accomplishments
- Parsed `pyproject.toml`'s `[project.urls] Documentation` value programmatically via `tomllib` on the prepared tree (`https://typsphinx.readthedocs.io/`), then fetched it with `curl` both un-followed (302 → `Location: .../en/latest/`) and followed (terminal 200, effective URL `https://typsphinx.readthedocs.io/en/latest/`), recording both commands and their verbatim output with an ISO-8601 timestamp (`2026-07-27T21:15:32Z`) in `33-RELEASE-EVIDENCE.md`.
- Re-measured the milestone diff range at execution time — `git merge-base main HEAD` = `771ec56fa3e9a863ac0bca865476bdc423fbb3e7`, `git log --oneline main..HEAD | wc -l` = `279` — rather than trusting any planning document's cached count, per Milestone Invariant #4. The count had already drifted from 258 (recorded at planning) to 279 as this phase's own task commits landed.
- Asserted Invariant 1 (zero `typsphinx/` changes) with an empty `git diff main..HEAD --stat -- typsphinx/` plus a non-empty `pyproject.toml` positive control proving the pathspec machinery genuinely ran rather than silently matching nothing.
- Asserted Invariant 2 (zero new runtime deps) by recording the full two-hunk `pyproject.toml` diff (version bump + Phase 31's pre-existing `Documentation` URL edit — no dependency-array line touched) and the single-line `uv.lock` self-entry diff.
- Asserted Invariant 3 (no `@preview` version bump) by inspecting the non-empty `examples/` diff (three `README.md`/`index.rst` files, all URL-rewrite prose from Phase 31, zero `.typ` files) and running `tests/test_preview_version_sync.py` (3 passed).
- Ran the full test suite via `uv run` in the provisioned worktree-local venv: 647 passed / 1 skipped / 0 failed — matching the research-session baseline exactly.
- Wrote `33-HANDOFF.md`: an English-language checklist naming all 8 publish/owner-manual items with owner (`/gsd-complete-milestone` vs. human) and ordering dependency, an explicit "not done in this phase, by design" scope-fence section, and verbatim proof that `git tag -l v0.6.4` and `git ls-remote --tags origin v0.6.4` both return empty.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-verify the Documentation metadata URL over real HTTP and record SC#3 evidence** - `f667d3d` (docs)
2. **Task 2: Assert the milestone invariants over the full diff and record SC#4 evidence** - `578de4d` (docs)
3. **Task 3: Write the SC#5 publish and owner-manual handoff checklist** - `ec7e8c9` (docs)

**Plan metadata:** committed at final metadata-commit step (worktree mode — orchestrator will merge and record the phase-level commit; STATE.md/ROADMAP.md are not touched by this plan per its worktree-mode instructions).

## Files Created/Modified
- `.planning/phases/33-v0-6-4-release-prep/33-RELEASE-EVIDENCE.md` - New file. SC#3 section (real HTTP fetch evidence, ISO-8601 timestamped) + SC#4 section (three milestone invariants asserted over the full `main..HEAD` diff with verbatim `git diff`/`pytest` output, plus SC#1/SC#2 evidence cited from plans 33-01/33-02).
- `.planning/phases/33-v0-6-4-release-prep/33-HANDOFF.md` - New file. The SC#5 8-item publish/owner-manual handoff checklist, the explicit unmet-REL-02-half statement, a "not done in this phase, by design" scope-fence section, and verbatim empty-tag proof.

## Decisions Made
- Neither new file is named `33-VERIFICATION.md`, per the plan's explicit constraint — that name is reserved by `/gsd-verify-work`, which overwrites it wholesale on every verification run.
- The evidence file's SC#4 commit count (279) is recorded as the freshly re-measured figure, explicitly noted as having drifted from every earlier cached count in this phase's own planning artifacts (254/256/258) — Milestone Invariant #4 made re-measurement mandatory rather than optional.
- `33-HANDOFF.md` opens by stating which half of REL-02 is unmet and why, before listing the checklist — per the plan's explicit instruction to state this "as an unmet criterion handed off, not as a formality."

## Deviations from Plan

None - plan executed exactly as written. All three tasks' `<action>`, `<verify>`, and `<acceptance_criteria>` blocks were followed literally; every command cited in `33-RELEASE-EVIDENCE.md` and `33-HANDOFF.md` was actually run during this plan's execution, not copied from `33-CONTEXT.md`/`33-RESEARCH.md`/`33-PATTERNS.md`.

## Issues Encountered

None. The environment was already provisioned per CLAUDE.md's worktree-isolated execution mode (`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev`, all commands run through `uv run`), and no auto-fix (Rule 1/2/3) was triggered.

## User Setup Required

None - no external service configuration required. This plan only creates two evidence/handoff documents and runs read-only verification commands (curl, git diff, pytest).

## Next Phase Readiness

- `33-RELEASE-EVIDENCE.md` and `33-HANDOFF.md` are the complete, self-contained citable record for ROADMAP Phase 33's SC#3, SC#4, and SC#5 — `/gsd-complete-milestone` can consume `33-HANDOFF.md`'s 8-item checklist directly without re-deriving context.
- All milestone invariants confirmed holding over the full diff at phase-33-plan-04 execution time; the full test suite is green (647 passed / 1 skipped / 0 failed).
- `git tag -l v0.6.4` and `git ls-remote --tags origin v0.6.4` are both empty — the milestone's irreversible-publish scope fence held through this phase with no tag or publish action performed.
- REL-02's PyPI-publish and `/en/stable/`+`/ja/stable/` half remains genuinely unmet and is now explicitly the responsibility of `/gsd-complete-milestone` plus the owner-manual steps enumerated in `33-HANDOFF.md`. No blockers for the orchestrator's wave-2 merge.

---
*Phase: 33-v0-6-4-release-prep*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: .planning/phases/33-v0-6-4-release-prep/33-RELEASE-EVIDENCE.md
- FOUND: .planning/phases/33-v0-6-4-release-prep/33-HANDOFF.md
- FOUND: .planning/phases/33-v0-6-4-release-prep/33-04-SUMMARY.md
- FOUND: f667d3d (Task 1 commit)
- FOUND: 578de4d (Task 2 commit)
- FOUND: ec7e8c9 (Task 3 commit)
- FOUND: 476aee9 (SUMMARY.md commit)
