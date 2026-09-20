---
phase: 75-v0-9-6-release-prep-prep-only
plan: 07
subsystem: release
tags: [changelog, requirements-fence, ci, release-prep, handoff, sc5]

# Dependency graph
requires:
  - phase: 75-01 through 75-06
    provides: the REQUIREMENTS fence baseline and SC5 observation 1, the version bump and curated
      CHANGELOG, local green-tree evidence (amended linkcheck reading), the trial merge and
      Dependabot census, and the push plus dispatched CI run this plan re-verifies and rolls up
provides:
  - REQUIREMENTS.md fence re-verified at phase close (MATCH against the 75-01 baseline)
  - SC5 probe observation 2 of 2, separated from observation 1 by three waves of recorded work
  - the scope fence on both the milestone range and this phase's own range, each with a
    non-vacuous control
  - 75-HANDOFF.md, the standalone ordered procedure /gsd-complete-milestone executes
  - the REL-16 settlement record and the five-row SC1-SC5 roll-up (PHASE_VERDICT = MET)
affects: [/gsd-complete-milestone, future release-prep phases needing the same handoff shape]

# Actuals (#2632)
actuals:
  tokens: 9625
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Line-scoped REQUIREMENTS.md fence (SHA-256 digest, line count, two diff forms, byte-identical grep transcript) that watches only the requirement expected to stay unchecked, so a sibling requirement's legitimate same-phase completion cannot be mistaken for the guarded flip"
    - "Two-observation SC5 pattern (phase head, phase close) plus a written-but-not-executed third-observation protocol for the operator, each observation carrying the same positive-controlled probes"

key-files:
  created:
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-HANDOFF.md
  modified:
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-CLOSEOUT-GUARD.md
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-SC5-INVARIANTS.md

key-decisions:
  - "REL-16's candidate defect set for the ### Known Limitations entry is NUM-01 alone (the AMENDED correction): the converted-image rehome collision and the typst_documents duplicate-target cluster were both measured closed in v0.8.0, so naming them in a v0.9.6 disclosure would misrepresent the current codebase"
  - "75-CLOSEOUT-GUARD.md's third-observation protocol is extended in place rather than duplicated, so the file ends with exactly one authoritative copy an operator can trust"

requirements-completed: []  # REL-15 stays unchecked (checked only at /gsd-complete-milestone); REL-16 closes via phase-completion tooling, never a plan.

coverage:
  - id: D1
    description: "REQUIREMENTS.md fence re-verified at phase close (MATCH) and SC5 probe observation 2 of 2 with its scope fence, both with controls"
    requirement: REL-15
    verification:
      - kind: other
        ref: "task 1 <verify> automated shell assertion (75-07-PLAN.md), re-run manually before commit"
        status: pass
    human_judgment: false
  - id: D2
    description: "75-HANDOFF.md written as a standalone, ordered /gsd-complete-milestone procedure with every required check, SHA, run id and digest inlined"
    requirement: REL-15
    verification:
      - kind: other
        ref: "task 2 <verify> automated shell assertion (75-07-PLAN.md), re-run manually before commit"
        status: pass
    human_judgment: false
  - id: D3
    description: "REL-16 settlement record (anchored Known Limitations grep, decision-record agreement, entry pasted verbatim) and the SC1-SC5 roll-up, PHASE_VERDICT = MET"
    requirement: REL-16
    verification:
      - kind: other
        ref: "task 3 <verify> automated shell assertion (75-07-PLAN.md), re-run manually before commit"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-20
status: complete
---

# Phase 75 Plan 07: Fence Observation 2, Scope Fence, and the Standalone Release Handoff Summary

**REL-15's REQUIREMENTS fence held a second time at phase close, the SC5 probes stayed empty at
observation 2 with every control present, and 75-HANDOFF.md now gives `/gsd-complete-milestone` a
standalone seven-item release checklist with every check, SHA, run id and digest inlined.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-20T11:25:58Z
- **Completed:** 2026-09-20T11:34:07Z
- **Tasks:** 3 completed
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- Re-ran the REQUIREMENTS.md fence at phase close: digest, line count, both diff forms, and the
  byte-identical REL-15 grep transcript all MATCH the 75-01 baseline; REL-15's checkbox still
  reads unchecked and its traceability row still reads `Pending`, read directly out of the file.
  REL-16 has not yet moved (as expected — no plan edits the file).
- Diffed `.planning/ROADMAP.md` and `.planning/STATE.md` against 75-01's scratch backups: only
  expected per-plan progress-tracking changes, no unwarranted rewrite.
- Recorded SC5 probe observation 2 of 2 (tags, PyPI, GitHub Release, `release.yml` run census,
  decoy branch, open PRs against the branch, version-bump commit count) — every probe from
  observation 1 repeated with the same `v0.9.2` positive controls still present, and `SEPARATION`
  citing the four intervening evidence-file keys structurally (bump commit, green-tree runs, trial
  merge, push and dispatched CI) rather than by wall-clock luck.
- Recorded the scope fence on both the milestone range (`typsphinx/pathfmt.py|typsphinx/translator.py`
  — Phase 74's own diff, unchanged) and this phase's own range (the five bump-commit files exactly),
  each with a non-vacuous pathspec control and a widened-diff control; `POST_DISPATCH_PRODUCT_FILES
  = 0`; `SC5_VERDICT = MET`.
- Wrote `75-HANDOFF.md`: a standalone, seven-item ordered checklist (PR-and-merge, tag push,
  `release.yml`'s four jobs with the `pypi` environment's manual approval, the manual
  `update-pin.yml` dispatch, Read the Docs `stable` confirmation, the REL-15 checkbox flip against
  its four named observations, and the no-re-date fact) — every required-check context, the CI run
  id, the pushed SHA, the bump commit SHA and the requirements digest are all inlined rather than
  linked. States the SC4 linkcheck amendment explicitly, with Class A (the two `v0.9.6`-ref records)
  carried into checklist item 2 as a required re-check once the tag exists, and Class B (the PyPI
  `#history` anchor) named as not carried.
- Recorded the REL-16 settlement: the anchored `### Known Limitations` grep finds exactly 2
  headings, the decision record and the CHANGELOG entry agree (`known-limitations-section`), and
  the entry — pasted verbatim — names NUM-01 alone with a `Workaround:` line, naming neither
  v0.8.0-closed defect nor WR-02/WR-03.
- Rolled up all five success criteria (`PHASE_VERDICT = MET`) and extended (not duplicated)
  `75-CLOSEOUT-GUARD.md`'s existing operator section with `THIRD_OBSERVATION_DOCUMENTED = yes`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — fence observation 2 at phase close, probe observation 2 of 2, and the scope
   fence with its controls** - `376e19a8` (docs)
2. **Task 2: Write 75-HANDOFF.md — the standalone ordered procedure /gsd-complete-milestone
   executes** - `351d0910` (docs)
3. **Task 3: The REL-16 settlement record, the SC roll-up, and the operator's third-observation
   section in the guard** - `53dce1b9` (docs)

No separate plan-metadata commit — this SUMMARY and the state-tracking commit are the final commit
for this worktree, per the parallel-executor contract (STATE.md/ROADMAP.md excluded; the
orchestrator owns those centrally).

## Files Created/Modified

- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-HANDOFF.md` — new; the standalone release
  procedure
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-CLOSEOUT-GUARD.md` — appended the
  re-verification-at-phase-close section and extended the existing operator section
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-SC5-INVARIANTS.md` — appended observation
  2 of 2, the scope fence, the REL-16 settlement, and the SC roll-up

## Decisions Made

- REL-16's `### Known Limitations` candidate set is NUM-01 alone (the AMENDED correction carried
  from `75-CHANGELOG-EVIDENCE.md`): the other two defects REL-16's literal text names were both
  measured closed in v0.8.0, so naming them here would misrepresent the current codebase rather
  than disclose a genuinely carried limitation.
- `75-CLOSEOUT-GUARD.md`'s third-observation protocol is extended in place, not duplicated — the
  file ends with exactly one authoritative `## For the operator running phase.complete` section.

## Deviations from Plan

None - plan executed exactly as written. Three self-caught drafting errors were corrected before
any commit (documented under Issues Encountered below, not as deviations, since none of them
survived into a committed state or required a rule-based auto-fix of unplanned work).

## Issues Encountered

- While drafting Task 1's edit to `75-CLOSEOUT-GUARD.md`, a placeholder `## For the operator
  running phase.complete` heading was mistakenly added, which would have duplicated the
  pre-existing section of the same name (violating Task 3's exactly-once check). Caught before
  committing; removed, leaving the pre-existing section for Task 3 to extend in place.
- The first draft of `SEPARATION` (in `75-SC5-INVARIANTS.md`) used parenthesized evidence-file
  citations, which matched the plan's forbidden key-line pattern
  (`^[A-Z][A-Z0-9_]* = .*[(]`). Caught by re-running the automated `<verify>` before committing;
  rewritten without parentheses.
- The first draft of `75-HANDOFF.md` was missing two required literal terms (`readthedocs` and
  `PUSHED_SHA`'s own SHA value). Caught by re-running the automated `<verify>` before committing;
  both added.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 75 (all 7 plans) is complete. `75-HANDOFF.md` is the standalone artifact
`/gsd-complete-milestone` reads to execute the actual v0.9.6 publish: PR merge, tag push,
`release.yml`'s four jobs (including the `pypi` environment's manual approval), the manual
`typsphinx-doc-translations` `update-pin.yml` dispatch, the Read the Docs `stable` confirmation on
both projects, and finally REL-15's checkbox flip against its four named observations. REL-15
stays unchecked and REL-16 stays unchecked by this plan — both checkboxes are exactly where the
phase-head baseline left them, confirmed by this plan's own re-verification.

Carried obligation from the SC4 linkcheck amendment: once the `v0.9.6` tag and GitHub Release
exist, `tox -e linkcheck` must be re-run to confirm `changelog.rst:8` and `changelog.rst:17` (the
two `v0.9.6`-ref records) have turned green — `75-HANDOFF.md` checklist item 2 carries this as a
required step, not a footnote.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `75-HANDOFF.md` found on disk at the path declared in frontmatter.
- All four commit hashes (`376e19a8`, `351d0910`, `53dce1b9`, `4489c2ed`) found in `git log --oneline`.
- All three tasks' automated `<verify>` blocks re-run against the final committed tree: Task 1
  `ALL PASS`, Task 2 `ALL PASS TASK 2`, Task 3 `ALL PASS TASK 3`.
- Plan-level `<verification>` re-confirmed: fence MATCHes at phase close with REL-15's checkbox
  read directly as unchecked; every SC5 probe at observation 2 is empty/zero with its control
  present; both scope fences hold with controls and `POST_DISPATCH_PRODUCT_FILES = 0`;
  `75-HANDOFF.md` carries every required check/SHA/run-id/digest inline; anchored `### Known
  Limitations` count is 2 with `PHASE_VERDICT = MET`.
- `.planning/REQUIREMENTS.md` unchanged across the whole plan (`git diff --name-only` empty against
  both the plan base and the working tree at every check).
