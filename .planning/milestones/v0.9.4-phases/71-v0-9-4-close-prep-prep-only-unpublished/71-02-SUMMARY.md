---
phase: 71-v0-9-4-close-prep-prep-only-unpublished
plan: 02
subsystem: release-prep
tags: [requirements-fence, sha256, gh-cli, pypi-probe, api-coverage]

requires:
  - phase: 70-typing-modernization-and-its-behaviour-identity-evidence
    provides: 'PHASE_BASE_SHA (697a1132…), the converted-file list, and the CODE_FREEZE_ANCHOR/PUSHED_SHA this plan's D-11 part 1 anchors against'
provides:
  - '71-CLOSEOUT-GUARD.md: phase-head REL-13 checksum/line-count/hit-count baseline, taken after D-02''s AMENDED commit, with both phase.complete-family entry points named and the revert-and-report operator procedure'
  - '71-SC1-INVARIANTS.md: SC#1 observation 1 (unpublished-shape probes with positive controls) plus the milestone fences and D-11 part 1 code-freeze check at phase head'
  - 'COVERAGE.md: reasoned no-external-API declaration that the seal-time api-coverage.verify-pre gate accepts'
affects: [71-03, 71-04, 71-05, 71-06, 71-07]

actuals:
  tokens: 8223
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns: [checksum-fenced requirement checkbox (D-09, reused from 61/69), positive-controlled remote negative probes (D-11, reused from 69), reasoned api-coverage declaration (Pitfall 8, reused from 61/69)]

key-files:
  created:
    - .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CLOSEOUT-GUARD.md
    - .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-SC1-INVARIANTS.md
    - .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/COVERAGE.md
  modified: []

key-decisions:
  - "Baseline values (digest 4d98e028…5636, 80 lines, 4 REL-13 hits) matched the plan's planning-time census exactly; kept the freshly-measured worktree values as the baseline per the plan's own instruction, rather than reusing the census numbers."
  - "Fixed CODE_FREEZE_ANCHOR's key-line format mid-task after Task 2's own automated verify caught it embedded in a backtick-quoted prose sentence instead of a bare KEY = value line (Rule 1 auto-fix, see Deviations)."

requirements-completed: []

coverage:
  - id: D1
    description: "REL-13 closeout guard baseline recorded at phase head, after D-02's AMENDED commit, with both phase.complete-family entry points named"
    requirement: REL-13
    verification:
      - kind: other
        ref: "71-02-PLAN.md Task 1 <verify><automated> (full shell predicate over 71-CLOSEOUT-GUARD.md)"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#1 observation 1: unpublished-shape probes with a positive control on every remote negative, plus the milestone fences and D-11 part 1 code freeze at phase head"
    requirement: REL-13
    verification:
      - kind: other
        ref: "71-02-PLAN.md Task 2 <verify><automated> (full shell predicate over 71-SC1-INVARIANTS.md, live gh/curl/git re-checks)"
        status: pass
    human_judgment: false
  - id: D3
    description: "COVERAGE.md reasoned no-external-API declaration; api-coverage.verify-pre passes"
    requirement: REL-13
    verification:
      - kind: other
        ref: "71-02-PLAN.md Task 3 <verify><automated>; live gsd-tools.cjs check api-coverage.verify-pre run"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-13
status: complete
---

# Phase 71 Plan 02: REL-13 Closeout Guard, SC#1 Observation 1, and COVERAGE.md Summary

**PHASE_BASE_SHA=f1f7d54a, AMENDED_COMMIT=5292a85b, REQ_SHA256_BASE=4d98e028…5636, REQ_LINES_BASE=80, REL13_HITS_BASE=4, OBS1_AT=2026-09-13T08:31:24Z, MILESTONE_BASE=d14ca458, CODE_FREEZE_ANCHOR=e721ff89**

Recorded the phase-head fence baseline for REL-13, proved the tree unpublished-shaped with a
positive control on every remote negative, confirmed no code changed since Phase 70's final
commit, and satisfied the api-coverage seal-time gate with a reasoned declaration — three
read-only planning documents, zero product-tree or requirement-state changes.

## Performance

- **Duration:** 8 min (measured from the closeout-guard commit to the COVERAGE.md commit;
  reading and worktree provisioning preceded this window)
- **Started:** 2026-09-13T08:29:16Z (GUARD_AT, first recorded probe)
- **Completed:** 2026-09-13T08:36:37Z (last commit)
- **Tasks:** 3
- **Files modified:** 3 (all newly created)

## Accomplishments
- `71-CLOSEOUT-GUARD.md`: phase-head baseline for REL-13's SHA-256/line-count/hit-count fence,
  taken after D-02's AMENDED commit landed, with the four `grep -n 'REL-13'` hits classified
  state-bearing vs. informational and both `phase.complete`-family entry points named with a
  revert-and-report operator procedure.
- `71-SC1-INVARIANTS.md`: SC#1's first observation — every remote unpublished-shape probe
  (local/remote tags, PyPI, GitHub Releases, `release.yml` runs, pull requests) paired with a
  positive control from the same source, plus the milestone fences (no version bump, no
  `.github/` change, 10-file code diff) and D-11 part 1 (empty code-freeze diff since Phase 70's
  `e721ff89` anchor, proven real by a non-empty positive-control diff across Phase 70's own
  range, and confirmed identical to Phase 70's CI-tested tip).
- `COVERAGE.md`: a reasoned no-external-API declaration explaining both detector signals (the
  declaration's own required phrase, and the threat_model's read-only Trust Boundaries row);
  `api-coverage.verify-pre` returns `"passed": true`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — record the phase-head REQUIREMENTS.md closeout guard, PHASE_BASE_SHA after the AMENDED commit, and both operator procedures** - `db8bb52b` (docs)
2. **Task 2: SC#1 fence observation 1 of 2 with a positive control on every remote negative, the milestone fences, and D-11 part 1 at phase head** - `aef8a558` (docs), fixed by `9b0dd645` (fix)
3. **Task 3: Write the reasoned no-external-API COVERAGE.md and prove the seal-time gate accepts it** - `7610872f` (docs)

**Plan metadata:** committed separately per worktree-mode git_commit_metadata step (SUMMARY.md only; STATE.md/ROADMAP.md/REQUIREMENTS.md excluded per this phase's D-02/D-09 fence).

## Files Created/Modified
- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CLOSEOUT-GUARD.md` - REL-13 checksum fence baseline and both operator procedures
- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-SC1-INVARIANTS.md` - SC#1 observation 1, milestone fences, D-11 part 1
- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/COVERAGE.md` - reasoned no-external-API declaration

## Decisions Made
- Baseline values matched the plan's planning-time census exactly (digest, line count, hit
  count); kept the freshly-measured values as the recorded baseline anyway, per the plan's own
  instruction to prefer a live measurement over a census transcription even when they agree.
- No architectural decisions were needed; every task followed the plan's exact command sequence.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] CODE_FREEZE_ANCHOR key line embedded in prose instead of a bare KEY = value line**
- **Found during:** Task 2's own `<verify><automated>` run, after the first commit for that task
- **Issue:** `71-SC1-INVARIANTS.md` wrote `` `CODE_FREEZE_ANCHOR = e721ff899a981eafdad696ef1a9c93aaab41ece5` — Phase 70's final code commit, confirmed by measurement: ...`` as one prose sentence with a leading backtick, rather than the bare-key-line format the plan's `<worktree_provisioning>` "Evidence key lines" contract requires (`sed -n "s/^KEY = //p"` must match the line's first character). The verify script's `ks CODE_FREEZE_ANCHOR` call returned empty, failing the check.
- **Fix:** Moved the value onto its own fenced `CODE_FREEZE_ANCHOR = e721ff899a981eafdad696ef1a9c93aaab41ece5` line, matching every other key line in the file, and kept the explanatory sentence as separate prose below it. No value changed.
- **Files modified:** `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-SC1-INVARIANTS.md`
- **Verification:** Re-ran Task 2's full `<verify><automated>` predicate; it now returns `TASK2_VERIFY_PASS` with exit 0.
- **Committed in:** `9b0dd645` (separate fix commit, per the phase's per-task commit-atomicity convention)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 — bug). **Impact:** Caught by the task's own
automated verify before the task was reported complete; the underlying measured value
(`e721ff899a981eafdad696ef1a9c93aaab41ece5`) was correct throughout — only the file's formatting
was wrong. No scope creep.

## Issues Encountered
None beyond the auto-fixed formatting issue above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

- `71-CLOSEOUT-GUARD.md`'s baseline (`PHASE_BASE_SHA = f1f7d54a61d74c3972f1df0508ac994c001dda7e`,
  `REQ_SHA256_BASE = 4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636`) is ready
  for plan 71-07's phase-close re-verification protocol.
- `71-SC1-INVARIANTS.md`'s § "Handoff to observation 2" hands plan 71-06 the exact section to
  append (`## Observation 2 of 2`) after wave 2's push and CI dispatch.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` are byte-unchanged
  in this worktree — confirmed by `git status --porcelain` and `git diff --name-only` against
  `PHASE_BASE_SHA`, both empty.
- No blockers or concerns for wave 2 (71-03, 71-04, 71-05).

---
*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Completed: 2026-09-13*

## Self-Check: PASSED

- `71-CLOSEOUT-GUARD.md`, `71-SC1-INVARIANTS.md`, `COVERAGE.md` all confirmed present on disk.
- Commits `db8bb52b`, `aef8a558`, `9b0dd645`, `7610872f` all confirmed present in `git log`.
- All three tasks' `<verify><automated>` predicates re-ran and returned
  `TASK1_VERIFY_PASS` / `TASK2_VERIFY_PASS` / `TASK3_VERIFY_PASS` with exit 0.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` confirmed
  byte-unchanged (`git status --porcelain` and `git diff --name-only` against `PHASE_BASE_SHA`
  both empty).
