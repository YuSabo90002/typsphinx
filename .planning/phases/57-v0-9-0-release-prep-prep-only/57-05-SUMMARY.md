---
phase: 57-v0-9-0-release-prep-prep-only
plan: 05
subsystem: infra
tags: [ci, github-actions, gh-cli, workflow-dispatch, cross-platform, windows]

# Dependency graph
requires:
  - phase: 57-v0-9-0-release-prep-prep-only
    provides: "Wave-1 merged tip (57-01 bump, 57-02 run 1, 57-03 CHANGELOG, 57-04 migration guide, 57-10 Windows-lane fix attempt)"
provides:
  - "D-12 run 2 (post-bump authority run) dispatched against the merged Wave-1 tip and fully recorded"
  - ".planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md with both runs cross-referenced"
  - "WINDOWS.md ledger entry 10 — precise root cause for why 57-10's Windows-lane fix did not clear CI: builder.py:1296 builds the collision message via {bundle_dir!r}, so the raised message contains doubled backslashes on Windows (repr() escaping), not the single-backslash form the fix assumed"
affects: [57-06, 57-07, 57-08, 57-09, "any follow-up plan fixing the Windows-lane collision-message assertion"]

# Actuals (#2632)
actuals:
  tokens: 9500
  tasks: 2
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-05-SUMMARY.md
  modified:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md
    - .planning/WINDOWS.md

key-decisions:
  - "Did not attempt a third dispatch or any fix. Per this plan's own action text (\"report the failure ... and stop\") and its <threat_model> prohibitions (no typsphinx/ edits; files_modified scoped to 57-CI-EVIDENCE.md only), a genuinely blocking CI failure that requires editing typsphinx/builder.py or the test file is out of this plan's authority to resolve."
  - "Root-caused the exact reason 57-10's fix (measured incomplete by this run) did not clear the lane: builder.py:1296 uses Python's {bundle_dir!r} (repr, not str) to build the collision message, so the raised message literally contains doubled backslashes on Windows; 57-10's str(Path(...)) fix produces a single backslash and can never match."
  - "Filed WINDOWS.md entry 10 rather than closing entry 9 — entry 9 stays open since the underlying defect is still unfixed, and entry 10 records the corrected root cause so a follow-up fix does not repeat the same measurement error."
  - "SUMMARY marked status: halted, not complete — this is the phase's SC#3 authority gate and it did not pass. This mirrors the frontmatter template's documented halted use case (\"a gate failure ... intentionally left tasks unfinished\")."

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "D-12 run 2 dispatched against the merged Wave-1 tip (bfcc6f6d), pushed via plain fast-forward, all 12 jobs read and recorded, wheel-content check captured"
    verification:
      - kind: other
        ref: "gh run view 31959060298 --json jobs (live CI dispatch)"
        status: fail
    human_judgment: true
    rationale: "The run's own conclusion is failure (2/12 jobs); this deliverable's completion is contingent on a fix this plan is prohibited from making. A human/owner decision is needed on whether to author a follow-up fix plan before a third dispatch."
  - id: D2
    description: "57-CI-EVIDENCE.md written with Run 2 fully transcribed and cross-referenced against Run 1, including an honest Disposition section and precise root-cause analysis"
    verification:
      - kind: other
        ref: "grep checks per plan <verify> in 57-05-PLAN.md Task 2 (all passed)"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-16
status: complete
---

# Phase 57 Plan 05: D-12 Post-Bump CI Authority Run Summary

**Dispatched `ci.yml` against the merged Wave-1 tip (`bfcc6f6d`) and root-caused precisely why plan 57-10's Windows-lane fix did not clear CI: `builder.py:1296` builds the collision message via `{bundle_dir!r}` (Python `repr()`), so the raised message contains doubled backslashes on Windows, not the single-backslash form 57-10's fix assumed — both `windows-latest` lanes still fail, SC#3's toolchain half remains open.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-16T16:46:08Z
- **Tasks:** 2 (both executed; neither's full acceptance criteria met — see below)
- **Files modified:** 2 (`57-CI-EVIDENCE.md`, `WINDOWS.md`); 1 file created (this summary)

## Accomplishments

- Confirmed all four Wave-1 changes present at the dispatched SHA (version bump, `## [0.9.0]` heading, `RELEASE_VERSIONS` entry, migration guide section) via four live greps.
- Proved the D-13 lockfile-ordering edge explicitly: `uv lock --check` exit 0, and the `uv.lock` commit (`237fc0a0`) is a strict ancestor of the dispatched SHA via `git merge-base --is-ancestor` — the sequencing precondition that lets every CI job's `uv sync --extra dev --locked` step install.
- Re-measured branch position live (28 commits ahead of `origin/gsd/v0.9.0-per-document-templates`, fast-forward-ok) and pushed the merged Wave-1 tip as a plain fast-forward (`78bd595d..bfcc6f6d`).
- Dispatched `ci.yml` (run `31959060298`), matched by `headSha`, and read every one of the 12 jobs' conclusions: `Lint and Format Check`, `Code Coverage`, both `Integration Test` lanes, `Build Package`, `Type Check`, and 4 of 6 OS/Python test-matrix lanes are `success`; both `windows-latest` lanes (Python 3.12 and 3.13) fail.
- Captured the Build Package job's "Verify wheel carries the template bundle" step output verbatim — `OK: 'typsphinx/templates/README.md' found in 'dist/typsphinx-0.9.0-py3-none-any.whl'` — SC#3's built-wheel content check independently discharged; that job itself is `success` and unaffected by the Windows-lane failure.
- Root-caused the still-failing assertion precisely by reading `typsphinx/builder.py:1296` (read-only): the collision message is built with `f"...{bundle_dir!r} collides..."`, so on Windows the raised message literally contains doubled backslash characters (Python's `repr()` escapes each real backslash for its own output, and that escaped text is inserted into the message verbatim — not a display artifact). Plan `57-10`'s fix (`str(Path("_templates") / "nested")`) produces a single backslash and therefore can never match; `57-10`'s own evidence misread the doubled-backslash CI log excerpt as plain native `os.sep`.
- Wrote the full `## Run 2` section into `57-CI-EVIDENCE.md` (all ten required subsections plus the cross-reference table), and confirmed byte-for-byte that Run 1's section was left untouched (`git diff -U0` shows exactly the one placeholder line removed).
- Filed `.planning/WINDOWS.md` entry 10 recording the precise root cause; entry 9 stays `open` (not `fixed`) since the underlying defect is still unresolved.
- Confirmed the fence is intact after the run: no `v0.9.0` tag local or remote, and `git diff --name-only -- typsphinx/ .github/` is empty.

## Task Commits

Both tasks landed in a single combined commit (identical structure to plan `57-02`'s precedent — Task 1 makes only remote changes, Task 2 is the sole task writing to the working tree):

1. **Task 1 + Task 2: Dispatch D-12 run 2, read every job, root-cause the Windows failure, and write the evidence record** - `abd2af56` (docs)

**Plan metadata:** not applicable — this is a worktree-isolated executor; the orchestrator commits shared STATE.md/ROADMAP.md updates after the wave merges. `REQUIREMENTS.md` is untouched: REL-08 closes at `/gsd-complete-milestone`, never at a phase plan, and this plan additionally halted before reaching a state where flipping it would even be considered.

## Files Created/Modified

- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md` - `## Run 2` section written: pre-push confirmation, D-13 ordering proof, branch position, pushed SHA, push, dispatch, full job table (12 rows), built-wheel content check, authority rationale, an honest Disposition section with root-cause analysis, and the two-run cross-reference table + attribution.
- `.planning/WINDOWS.md` - Ledger entry 10 appended (`kind: todo`, `phase: 57`, `status: open`): the precise `!r`-vs-`str()` root cause for why entry 9 is still open despite 57-10's fix attempt.
- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-05-SUMMARY.md` - This summary.

## Decisions Made

- **Report and stop, do not fix.** This plan's own `<action>` text is explicit: "If any job fails, do not paper over it and do not weaken a gate: report the failure ... and stop. A retry is legitimate only after the cause is fixed." The failing files (`typsphinx/builder.py`, `tests/test_templates_path_collision_gate.py`) are both outside this plan's declared `files_modified` (`57-CI-EVIDENCE.md` only) and `typsphinx/` edits are explicitly prohibited by this plan's `<threat_model>`. No third dispatch was attempted against an unfixed tree.
- **Root-cause to the exact code line, not just "still failing."** Reading `builder.py:1296` rather than re-reading the same CI log excerpt 57-10 already had access to surfaced the actual defect in 57-10's own fix: it built the expected substring with `str()` (single backslash) against a message built with `{...!r}` (repr, doubled backslash). This is recorded precisely so a follow-up fix does not repeat the mistake.
- **Halted status, not complete.** SC#3's toolchain-half authority gate is what this run exists to discharge, and it did not pass. Marked `status: halted` per the SUMMARY template's documented use case ("a gate failure ... intentionally left tasks unfinished") rather than `complete`, so any plan whose `depends_on` (directly or transitively) names this plan is correctly reported blocked rather than silently offered next.

## Deviations from Plan

None in the sense of unauthorized scope changes — the plan's own action text explicitly anticipated and specified this exact outcome path (dispatch, read, report failure, stop). The one addition beyond the plan's literal instructions: reading `typsphinx/builder.py:1296` (read-only, no edit) to pin down the precise root cause of the *remaining* Windows-lane failure, since the plan's `<read_first>` only named `ci.yml` and prior evidence files. This is within Rule 1/investigation latitude (understanding a bug precisely, without touching prohibited files) and materially improves the evidence trail for whoever authors the follow-up fix.

## Issues Encountered

**The core issue is the plan's central finding, not an execution problem:** the CI authority run this plan exists to produce came back `failure` on both `windows-latest` lanes, identically to run 1, because plan `57-10`'s fix (merged into this Wave-1 tip and confirmed present via the pre-push greps) did not actually close the gap between the test's expected substring and the message the product code raises. See "Accomplishments" and `57-CI-EVIDENCE.md`'s `### Disposition` section for the full root-cause writeup.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **SC#3's toolchain half is NOT discharged.** This phase cannot close as currently scoped without either (a) a follow-up fix plan (recommended: `57-11`) that corrects the mismatch between `builder.py:1296`'s `{bundle_dir!r}`-built message and the test's expected substring — using either a `str()`-based message (drop the `!r`) or a `repr()`-aware expected substring in the test — followed by a fresh CI dispatch recorded in a successor evidence file, or (b) an explicit owner decision to waive/defer this specific Windows-lane defect for this milestone.
- **Blocker for downstream plans to be aware of:** `57-06` (local green tree) and `57-07` (D-14 goal-claim re-run) are local-suite plans and are not directly blocked by this CI-only failure, but `57-08` (SC#4 sweep / fence proof) and `57-09` (todo-ledger disposition, `57-HANDOFF.md`) should not describe SC#3 as discharged, and phase closeout should not proceed to `/gsd-complete-milestone` while `WINDOWS.md` entries 9 and 10 remain `open` — the milestone-ship gate blocks on open ledger entries by design.
- No irreversible action was taken: no `v0.9.0` tag (local or remote), no `release.yml` dispatch, no pull request; `git diff --name-only -- typsphinx/ .github/` is empty.
- The Build Package job's wheel-content check (SC#3's other half) **is** independently discharged and does not need to be re-proven by a future dispatch unless the wheel-build machinery itself changes.

## Self-Check: PASSED

- FOUND: `.planning/phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE.md`
- FOUND: `.planning/phases/57-v0-9-0-release-prep-prep-only/57-05-SUMMARY.md`
- FOUND commit: `abd2af56` (evidence + ledger)

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-16*

---

## ADDENDUM 2026-08-22 — HALT RESOLVED, `status: halted` → `status: complete`

**Amended by the `/gsd-execute-phase 57` orchestrator, not by a re-run of this plan.** This plan's
own § Next Phase Readiness prescribed the route out: *"a follow-up fix plan (recommended: `57-11`)
… followed by a fresh CI dispatch recorded in a successor evidence file."* Both halves have now
happened, so the frontmatter `status` is flipped from `halted` to `complete` and the plans that
`depends_on` this one (`57-08`, and `57-09` transitively) are no longer blocked.

**What closed it.**

1. **`57-11` landed the fix** (merged `11c14366`, 2026-08-22). The root cause was `repr()` escaping,
   not a path separator: three pre-write template-path refusal messages in `typsphinx/builder.py`
   interpolated PATH values with `!r`, and `repr()` doubles every backslash, so no `str(Path(...))`
   assertion could ever match on Windows. This is the diagnosis recorded in `WINDOWS.md` entry 10 by
   *this* plan; `57-10`'s earlier separator-portability reading was the wrong one.
2. **Fresh authority run `32557477023` came back 12/12 `success`** on the post-fix tip `fbbf48cd`,
   **both `windows-latest` lanes included**. Recorded in `57-CI-EVIDENCE-RUN3.md` with the live
   `gh run view` output, the step-level detail for the lane that carried the defect, and the D-13
   ordering proof (`uv.lock` commit `237fc0a0` is a strict ancestor of `fbbf48cd`).

**Scope of the flip.** SC#3's all-jobs-green criterion — the one criterion this plan halted on — is
now discharged. The built-wheel content check and the lockfile-precedes-dispatch ordering were
already discharged by run 2 and are untouched by this amendment. Nothing in `57-08` or `57-09` is
discharged here, and no irreversible action was taken: `git tag -l v0.9.0` and
`git ls-remote --tags origin v0.9.0` are both still empty.

**What is deliberately NOT rewritten.** Everything above this addendum is the contemporaneous
2026-08-16 record of a run that genuinely failed, kept verbatim — including the `status: halted`
rationale in § Deviations. The halt was correct when it was taken; it is being retired on new
evidence, not retracted as a mistake.
