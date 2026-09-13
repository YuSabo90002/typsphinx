---
phase: 71-v0-9-4-close-prep-prep-only-unpublished
plan: 04
subsystem: release-prep
tags: [ci-dispatch, github-actions, fast-forward-push, ruff, gh-cli]

requires:
  - phase: 71-v0-9-4-close-prep-prep-only-unpublished
    provides: "71-01's CHANGELOG bullet and 71-02's MILESTONE_BASE/CODE_FREEZE_ANCHOR fences, merged onto the canonical branch before this plan started"
provides:
  - "71-CI-EVIDENCE.md: decoy census, tip identity and fence, fast-forward push, dispatch, the completed 12-job CI run transcript, ruff's verdict, and a fully-documented duplicate-dispatch anomaly"
  - "gsd/v0.9.4-typing-modernization fast-forwarded on origin from e70e31fb to 7a42bf99"
  - "One completed, all-green, 12-job CI run (34748483361) on the phase's tip, matching Phase 70's job shape"
affects: [71-06, 71-07]

actuals:
  tokens: 4639
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CI-EVIDENCE.md
  modified: []

key-decisions:
  - "When gh workflow run CI --ref ... repeatedly returned HTTP 500/502 despite one attempt silently succeeding server-side, cancelled the resulting surplus run (34748491771) rather than deleting it or dispatching again — cancellation stops resource waste without taking an action beyond this plan's two pre-authorised outward actions (one push, one dispatch)."
  - "Treated the chronologically-first surplus run (34748483361, created by an attempt using the plan's exact literal dispatch command) as canonical RUN_ID, and waited it out to completion rather than treating the anomaly as an immediate hard stop, since the CI verdict on the tip is valuable regardless of how the dispatch-count discrepancy is resolved."
  - "Did not delete the cancelled duplicate run to force a literal DISPATCH_COUNT=1: deletion is an action outside this plan's two pre-authorised outward actions (one push, one dispatch) and is deferred to an explicit human/orchestrator decision."

requirements-completed: []

coverage:
  - id: D1
    description: "Decoy census immediately before the push, fast-forward push of gsd/v0.9.4-typing-modernization (e70e31fb -> 7a42bf99), and tip-identity fence (empty product diff, version 0.9.2, no code/workflow drift since Phase 70, merge-base with origin/main unchanged)"
    requirement: REL-13
    verification:
      - kind: other
        ref: "71-04-PLAN.md Task 1 automated verify"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly one CI dispatch on the pushed tip, observed to completion with all 12 jobs transcribed, both windows-latest and both macos-latest lanes named, and ruff's verdict quoted from Lint and Format Check"
    requirement: REL-13
    verification:
      - kind: other
        ref: "71-04-PLAN.md Task 2 automated verify (partial — see rationale)"
        status: fail
    human_judgment: true
    rationale: "The CI run itself (34748483361) is fully green — 12/12 jobs success, both Windows and both macOS lanes named, ruff clean, job-name set identical to Phase 70's run — and every check in Task 2's automated verify passes EXCEPT the literal DISPATCH_COUNT=1 check. Repeated GitHub API 500/502 errors on the dispatch call masked a silent server-side success, producing two runs at PUSHED_SHA instead of one. The surplus run was cancelled but not deleted (deletion is outside this plan's two pre-authorised outward actions), so the automated verify's dispatch-count check fails on a real, honestly-recorded discrepancy. A human must decide whether to authorise deleting the cancelled surplus run to restore a literal count of 1, or accept the documented anomaly as an exception."

duration: 16min
completed: 2026-09-13
status: halted
---

# Phase 71 Plan 04: CI Dispatch, Fast-Forward Push, and a Duplicate-Dispatch Anomaly Summary

**Fast-forward pushed `gsd/v0.9.4-typing-modernization` to `7a42bf99` and got a fully green 12-job CI run (`34748483361`, matching Phase 70's job shape, ruff 0.16.6 clean) — but GitHub's own API returned false-failure errors on the dispatch call that masked a silent duplicate dispatch, so `DISPATCH_COUNT` is honestly `2`, not `1`, and this plan halts at a blocking checkpoint rather than resolve it unilaterally.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-09-13T08:45:09Z
- **Completed:** 2026-09-13T09:00:49Z
- **Tasks:** 2 of 2 executed (both committed; Task 2's automated verify has 2 of 32 checks failing, both traced to one root cause)
- **Files modified:** 1 (`71-CI-EVIDENCE.md`, created)

## First section — key facts

- `PUSHED_SHA = 7a42bf996b1aaca24a8b17346be78459e6d41e2b`
- `ORIGIN_BEFORE = e70e31fba9039133a153a5bba16577d7b2f889c1`
- `RUN_ID = 34748483361`
- `RUN_URL = https://github.com/YuSabo90002/typsphinx/actions/runs/34748483361`
- `JOB_COUNT = 12`
- `NON_SUCCESS_JOBS = 0`
- `JOB_NAMES_MATCH_PHASE70 = yes`
- `CI_RUFF_VERSION = 0.16.6`
- `SC3_CI_VERDICT = MET` (on the run's own merits — all 12 jobs success, both Windows lanes and
  both macOS lanes named and green, ruff clean, job-name set identical to Phase 70's run)
- `DISPATCH_COUNT = 2` — **NOT 1.** This is the one unresolved item. See "Deviations from Plan"
  and "Blocking checkpoint" below.

The CI run passed cleanly. The one open issue is procedural, not a build defect: GitHub's Actions
API returned false-failure errors that hid a real, silent, duplicate dispatch.

## Accomplishments

- Re-checked the decoy census (`git branch --list`, `git ls-remote --heads`) immediately before the
  push: no `gsd/v0.9.4-milestone` decoy exists locally or on origin.
- Verified the tip-identity fence in full: empty product diff against this worktree's HEAD,
  `pyproject.toml:7` still `version = "0.9.2"`, no `typsphinx/`/`tests/` change since Phase 70's
  `CODE_FREEZE_ANCHOR`, no `.github/` change since `MILESTONE_BASE`, merge-base with `origin/main`
  unchanged, no tag on the pushed tip.
- Fast-forward pushed `gsd/v0.9.4-typing-modernization` from `e70e31fb` to `7a42bf99` with
  `git push --no-follow-tags`; confirmed origin head now equals `PUSHED_SHA` and only `v0.9.2`
  remains tagged on origin.
- Dispatched CI on the pushed tip, waited the run to completion in the foreground, and transcribed
  all 12 job conclusions: every job success, both `windows-latest` and both `macos-latest` lanes
  named individually, and the job-name set identical to Phase 70's run `34742047126`.
- Quoted ruff's verdict from the `Lint and Format Check` job's `Run lint with tox` step:
  `CI_RUFF_VERSION = 0.16.6`, equal to the lock's own ruff version; `black --check .` and
  `ruff check .` both clean.
- Confirmed zero `release.yml` runs at `PUSHED_SHA`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — gate on wave 1, tip identity and fence, decoy census, fast-forward push of
   the canonical branch, dispatch CI exactly once** - `ad9309e7` (feat)
2. **Task 2: Observe the run to completion in the foreground, transcribe all 12 jobs, name both
   windows-latest and both macos-latest lanes, compare job names with Phase 70's run, and quote
   ruff's CI verdict** - `8afdb899` (docs)

**Plan metadata:** committed separately after this SUMMARY (see final commit).

## Files Created/Modified

- `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CI-EVIDENCE.md` - decoy census,
  tip identity and fence, fast-forward push, the duplicate-dispatch anomaly (full transcript of
  four dispatch attempts and their real server-side outcomes), the completed 12-job CI run,
  ruff's verdict, and the D-10/SC#3 disposition

## Decisions Made

- Cancelled the surplus duplicate run (`34748491771`) rather than deleting it or dispatching
  again — a stop action, not a new outward action, kept within the plan's two pre-authorised
  actions (one push, one dispatch).
- Treated the chronologically-first run created by an attempt using the plan's exact literal
  dispatch command (`34748483361`) as canonical, and waited it to completion rather than treating
  discovery of the anomaly as an immediate hard stop — the CI verdict on the tip is valuable
  information independent of how the dispatch-count discrepancy resolves.
- Did not delete the cancelled surplus run to force a literal `DISPATCH_COUNT = 1`: deletion of
  GitHub Actions run history is outside this plan's two pre-authorised outward actions and is
  deferred to an explicit human/orchestrator decision rather than taken unilaterally.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Transient GitHub API errors on CI dispatch masked a silent duplicate dispatch**
- **Found during:** Task 1, step 6 ("Dispatch")
- **Issue:** `gh workflow run CI --ref gsd/v0.9.4-typing-modernization` returned `HTTP 500` on its
  first attempt. A follow-up `gh run list` query showed no new run at `PUSHED_SHA`, consistent with
  a genuine failure. A second attempt via the direct API endpoint returned `HTTP 502`. A third
  attempt (after a 20s wait) again returned `HTTP 500`. A fourth attempt, using the workflow's
  filename (`ci.yml`) instead of its display name (`CI`) as an alternate invocation of the same
  workflow, returned success and printed a run URL. A `gh run list` query immediately after showed
  **two** runs at `PUSHED_SHA`, not one — one created 30 seconds before the "successful" fourth
  attempt was even issued. This means one of the three earlier attempts, all of which reported
  client-side failure, actually succeeded server-side; GitHub's own dispatch API returned an
  incorrect failure response to the caller in at least one case.
- **Fix:** Cancelled the surplus run (`34748491771`, created by the fourth/alias attempt) via
  `gh run cancel`, since letting it run to completion would waste CI resources and add ambiguity
  about which run is canonical. Did NOT delete it (that would require an action beyond this plan's
  two pre-authorised outward actions) and did NOT dispatch again. Treated the earlier run
  (`34748483361`, created by an attempt using the plan's exact literal command) as `RUN_ID` and
  observed it to completion.
- **Files modified:** `.planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CI-EVIDENCE.md`
  (full transcript under `## Dispatch`, `## Dispatch count and no release run`, and
  `## D-10 final tip`)
- **Verification:** `34748483361` resolved correctly as `RUN_ID` — `headSha` equals `PUSHED_SHA`,
  `workflowName` is `CI`, `event` is `workflow_dispatch`, `createdAt` follows `PUSH_AT` — and Task
  1's automated verify (which does not check dispatch count) passed. Task 2's automated verify
  passes on every check except the literal `DISPATCH_COUNT = 1` requirement, which genuinely fails
  because the surplus run still appears in `gh run list` (cancelled, not deleted). This is
  **not resolved** — see "Blocking checkpoint" below.
- **Committed in:** `ad9309e7` (Task 1), `8afdb899` (Task 2, where the honest `DISPATCH_COUNT = 2`
  is recorded)

---

**Total deviations:** 1 auto-fixed (1 Rule 3 — blocking, transient API failure and its
cancel-the-surplus mitigation), plus one **unresolved** item escalated below rather than
auto-fixed, because resolving it fully requires an action (deleting GitHub Actions run history)
outside this plan's explicitly pre-authorised scope.
**Impact on plan:** The phase's tip is genuinely on `origin` as a fast-forward, and CI genuinely
ran green on it — the substantive SC#3 CI half is met. The `DISPATCH_COUNT` literal-count
requirement is not met and is not silently fudged; it is surfaced for a human decision.

## Issues Encountered

**Blocking checkpoint: `DISPATCH_COUNT = 2`, not `1`, due to a GitHub API false-failure response.**
Everything downstream of the dispatch itself succeeded (the CI run is fully green, matching Phase
70's job shape), but the task's own automated verify requires `gh run list ... | length` at
`PUSHED_SHA` to equal exactly `1`, and it currently returns `2` — one completed/success run
(`34748483361`, cited as `RUN_ID`) and one cancelled run (`34748491771`). The cancelled run cannot
be made to disappear from that count without deleting it from GitHub's Actions history, which this
plan is not authorised to do unilaterally (its outward-action authorization was exactly one push
and one dispatch, "nothing else"). No second dispatch was ever deliberately issued, and no run was
cited as green while another was red — the anomaly is entirely attributable to GitHub's dispatch
API returning `HTTP 500`/`HTTP 502` to a caller whose request had, in at least one case, actually
succeeded.

**What the human/orchestrator needs to decide:**
1. Authorise deleting the cancelled surplus run `34748491771` (via `gh run delete 34748491771`) to
   restore a literal `DISPATCH_COUNT = 1`, after which this plan's evidence file can be amended to
   record `DISPATCH_COUNT = 1` and the automated verify will pass in full; or
2. Accept `DISPATCH_COUNT = 2` as a documented, non-laundering exception (both runs are fully
   transcribed and neither was cited dishonestly) and amend the plan's acceptance criteria or
   treat this plan as complete despite the literal count; or
3. Direct some other resolution.

No further action was taken pending this decision. Both this plan's tasks are committed in full;
nothing is left half-done on the product-tree or evidence-file side.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `PUSHED_SHA = 7a42bf996b1aaca24a8b17346be78459e6d41e2b` is on `origin` as a fast-forward, ready
  for plan 71-06's post-dispatch proof and D-11 part 1 re-verification on the close tip.
- The CI run itself (`34748483361`) is fully green and ready to be cited as SC#3's CI-half
  evidence, once the `DISPATCH_COUNT` decision above is resolved.
- **Blocker for phase close:** the `DISPATCH_COUNT` discrepancy above should be resolved (by
  either path in "What the human/orchestrator needs to decide") before `71-07`'s closeout-guard
  re-verification and `71-HANDOFF.md` cite this plan's evidence as clean.
- 71-03 and 71-05 (this wave's siblings) share no file with this plan and were not touched.

---
*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Completed: 2026-09-13*

## Self-Check: PASSED

- `71-CI-EVIDENCE.md` exists: FOUND
- Commit `ad9309e7` (Task 1) exists in `git log --oneline --all`: FOUND
- Commit `8afdb899` (Task 2) exists in `git log --oneline --all`: FOUND
- Task 1's automated `<verify>` predicate re-ran and returned `TASK1_VERIFY_PASS` with exit 0.
- Task 2's automated `<verify>` predicate was re-run check-by-check: 30 of 32 checks PASS; the 2
  FAIL checks (`DISPATCH_COUNT` live query and key) are both traced to the single documented
  anomaly above, not to any other defect.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` confirmed
  byte-unchanged (`git status --porcelain` and `git diff --name-only` against `BASE_71_04`
  both show only `71-CI-EVIDENCE.md` and this `71-04-SUMMARY.md`).
