---
phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish
plan: 03
subsystem: infra
tags: [pypi, trusted-publishing, oidc, sigstore, github-actions, release]

# Dependency graph
requires:
  - phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish (76-01)
    provides: "release.yml's publish-pypi step with password: removed, proving the OIDC/Trusted Publishing path is live on the dispatched ref"
  - phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish (76-02)
    provides: "MSG-06's translator.py quote_path routing, present on the same dispatched SHA (unrelated to this plan's outcome but proven co-present)"
provides:
  - "One `workflow_dispatch` run of release.yml (tag v0.9.6, ref gsd/v0.9.7-trusted-publishing-and-release) exercised the real OIDC token exchange against production PyPI and Sigstore, and was turned away at the upload step as a duplicate file — never as an unknown publisher"
  - "76-ATT-EVIDENCE.md's full ATT-02 record: pre-dispatch baselines, the owner checkpoint, the exactly-one dispatch guard, the two-stage wait, run conclusion, SC #4 control-paired greps, post-dispatch capture proving PyPI's served state and the v0.9.6 GitHub Release are unchanged, the Sigstore side-effect statement, and the rehearsal-is-not-ATT-04 boundary sentence"
affects: [release, pypi-publish, phase-77-handoff]

actuals:
  tokens: 10123
  tasks: 3
  commits: 20
  plan_head_before: 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78
  plan_head_after: 8cdc79574c4d73c58878a1948f7a2806853cbbdd

tech-stack:
  added: []
  patterns:
    - "Tracer task (Task 1) proves every read-only observation path — pushed ref, CI on its exact SHA, validate-only local checks, control-run greps, PyPI/Release baselines — before the one irreversible dispatch, so the dispatch task (Task 3) only has to compare against already-recorded expectations rather than discover them live"
    - "Exactly-one-dispatch guard: before/after `gh run list` diffed via `comm -13` on sorted ids, with a write-ahead DISPATCH_ATTEMPTED marker committed before the dispatch command runs, so an interrupted attempt still leaves the marker and never gets silently re-dispatched"

key-files:
  created: []
  modified:
    - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-ATT-EVIDENCE.md

key-decisions:
  - "Followed the plan's checkpoint protocol literally: stopped at Task 2's blocking-human checkpoint after Task 1 completed and its automated-only tracer <verify> re-ran clean (row 3 of the tracer feedback gate — interactive, human_verify_mode=end-of-phase — so no synthesized checkpoint was added on top of the plan's own Task 2). Resumed only after the orchestrator relayed the owner's explicit 'dispatch' answer, recorded verbatim as OWNER_CHECKPOINT_CHOICE before any Task 3 action."
  - "Never approved, rejected or otherwise called the pypi environment's pending_deployments endpoint — GET only, once, at the first observed 'waiting' status. The approvals transcript (github-actions[bot] wait_timer completion + YuSabo90002 reviewer approval) is recorded as-is; APPROVAL_POSTS_BY_EXECUTOR = 0 is a procedural statement, not something the API can itself prove given the shared gh identity."
  - "Retroactively created the #3968 plan-commit ledger (gsd-plan-head-before-76-03) after noticing it was missed at Task 1 start, using the same base SHA already recorded as BASE_76_03/ORIGIN_REF_SHA — the ledger and the evidence file's own BASE_76_03 key agree, so the measured commit count is trustworthy despite the late creation."

requirements-completed: [ATT-02, ATT-01]

coverage:
  - id: D1
    description: "Exactly one workflow_dispatch run of release.yml (36321530105) exercised the OIDC exchange against production PyPI and was rejected as a duplicate file (HTTPError 400, 'File already exists'), with zero invalid-publisher/invalid-pending-publisher occurrences — proving the D-05 Trusted Publisher registration matches on all four fields."
    requirement: "ATT-02"
    verification:
      - kind: other
        ref: "76-ATT-EVIDENCE.md ## ATT-02 run conclusion — job table + fenced Publish to PyPI error lines"
        status: pass
      - kind: other
        ref: "Task 3 <verify> automated command (git rev-list/gh run view/gh release view live re-check), executed this session"
        status: pass
    human_judgment: false
  - id: D2
    description: "PyPI's served state and the v0.9.6 GitHub Release are unchanged after the rehearsal (same file count, sorted filelist hash, both 0.9.6 provenance values null, same asset fingerprint and body hash); the rehearsal's own build artifact sha256 differs from PyPI's served hashes, proving the identical-hash 200-OK branch was never reached."
    requirement: "ATT-02"
    verification:
      - kind: other
        ref: "76-ATT-EVIDENCE.md ## ATT-02 post-dispatch capture — pre/post hash comparison, empty diff, artifact download and hash"
        status: pass
      - kind: other
        ref: "Task 3 <verify> automated command, executed this session"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC #4: the rehearsal log carries zero occurrences of 'disabling Trusted Publishing' and 'attestations input is ignored', each read against the non-zero control (run 35730551619, which read 1/1 for both) — a zero reading only counts as evidence because its own control is non-zero (D-08 AMENDED)."
    requirement: "ATT-02"
    verification:
      - kind: other
        ref: "76-ATT-EVIDENCE.md ## SC #4 — annotation greps against the control"
        status: pass
    human_judgment: false
  - id: D4
    description: "With 76-01's password: deletion proven present on the dispatched SHA (REF_PYPI_SECRET_REFS = 0), and this run actually taking the OIDC/Sigstore path (not the token path) rather than failing at the OIDC exchange, ATT-01's rehearsal half is closed together with ATT-02."
    requirement: "ATT-01"
    verification:
      - kind: other
        ref: "76-ATT-EVIDENCE.md ## ATT-02 pre-dispatch — the pushed ref (D-06) and ## ATT-02 verdict's closing sentence"
        status: pass
    human_judgment: false
  - id: D5
    description: "The rehearsal-is-not-ATT-04 boundary is stated verbatim in the evidence, and no ATT-03/ATT-04/ATT-05 checkbox was touched — this run's clean reading must not be laundered into a later phase's evidence."
    requirement: "ATT-02"
    verification:
      - kind: other
        ref: "76-ATT-EVIDENCE.md ## Rehearsal is not ATT-04"
        status: pass
    human_judgment: false

duration: 43min
completed: 2026-09-27
status: complete
---

# Phase 76 Plan 03: ATT-02 PyPI Trusted Publishing rehearsal Summary

**Exactly one `workflow_dispatch` of `release.yml` (run 36321530105, tag `v0.9.6`) exercised the real OIDC exchange and Sigstore signing against production PyPI and was rejected as a duplicate file — never as an unknown publisher — with PyPI's served state and the v0.9.6 GitHub Release provably unchanged.**

## Performance

- **Duration:** 43 min (12:48Z pre-dispatch start → 13:31Z verdict), split across a checkpoint pause for the owner's dispatch/hold decision
- **Started:** 2026-09-27T12:48:07Z
- **Completed:** 2026-09-27T13:31:00Z
- **Tasks:** 3 (tracer, checkpoint:decision, dispatch-and-evidence)
- **Files modified:** 1 (`76-ATT-EVIDENCE.md`, evidence-only — no product code)

## Accomplishments
- Task 1's tracer proved every observation path the rehearsal needed on known inputs before the irreversible dispatch: the pushed milestone-branch SHA carries both wave-1 edits and a green CI run (12/12 jobs), the two `validate`-only checks (`ci.yml` has no equivalent) pass locally, the control run's annotation greps read 1/1/0, and the PyPI/GitHub-Release baselines (38 files, both 0.9.6 provenance `null`, 3 release assets) were captured.
- Task 2's owner checkpoint returned the explicit answer `dispatch`, shown against the measured `ORIGIN_REF_SHA`, a green CI run, and `PRE_DISPATCH_VERDICT = READY` — never inferred.
- Task 3 fired the single `gh workflow run release.yml` dispatch, guarded exactly-once by a before/after `gh run list` diff and a write-ahead `DISPATCH_ATTEMPTED` marker committed before the command ran; watched the run through both the `pypi` environment's reviewer approval and its 15-minute `wait_timer` via two bounded foreground polling calls (never a long single watch, never `run_in_background`), reading `pending_deployments` exactly once with GET only.
- The run concluded exactly as ATT-02 requires: `Validate Release`/`Build Distribution` success, `Publish to PyPI` failure with `HTTPError: 400 Bad Request` / `File already exists` (≥1), `Publish to TestPyPI (Optional)`/`Create GitHub Release` skipped, zero `invalid-publisher`/`invalid-pending-publisher`.
- Post-dispatch capture proved nothing reached PyPI or the v0.9.6 Release: identical file count and sorted filelist hash, both 0.9.6 provenance values still `null`, identical release asset fingerprint and body hash, and the rehearsal's own build artifact sha256 (matching its DSSE attestation subjects) differing from PyPI's served hashes.
- The Sigstore side effect (permanent Fulcio/Rekor records for the two rebuilt 0.9.6 files) and the rehearsal-is-not-ATT-04 boundary are both stated explicitly in the evidence, per D-08.

## Task Commits

Each numbered evidence step was committed atomically as it was written, per the plan's "commit at
the end of each numbered step that records keys" instruction — 20 commits total across the plan
(one write-ahead marker preceding the dispatch command itself, as D-01 requires):

1. **Task 1, step 1 (provisioning)** — `bb78dee6` (docs)
2. **Task 1, step 2 (pushed ref, D-06)** — `ac1c3042` (docs)
3. **Task 1, step 3 (validate-job checks)** — `0772c566` (docs)
4. **Task 1, step 4a (CI write-ahead marker)** — `67d30f10` (docs)
5. **Task 1, step 4b (CI dispatch result)** — `176d09a1` (docs)
6. **Task 1, step 4c (CI conclusion)** — `b951d174` (docs)
7. **Task 1, step 5 (control run greps)** — `d53481df` (docs)
8. **Task 1, steps 6–7 (PyPI + Release baselines)** — `e2b43442` (docs)
9. **Task 1, step 8 (publish-testpypi if: evaluation)** — `22939d62` (docs)
10. **Task 1, step 9 (content non-identity)** — `172b5d5c` (docs)
11. **Task 1, steps 10–11 (rollback secrets + verdict)** — `4d6eab54` (docs)
12. **Task 2 → Task 3 step 0 (owner checkpoint answer)** — `858b776d` (docs)
13. **Task 3, steps 1–2 (resume guard + re-measure)** — `26bbe2f9` (docs)
14. **Task 3, step 3a (write-ahead DISPATCH_ATTEMPTED marker)** — `30d6f067` (docs)
15. **Task 3, step 3b (dispatch result, D-01)** — `f64b8720` (docs)
16. **Task 3, step 4 (two-stage watch, D-02/D-03/D-04)** — `fb9dbf37` (docs)
17. **Task 3, step 5 (run conclusion, SC #2)** — `1ec2fd35` (docs)
18. **Task 3, step 6 (SC #4 control-paired greps)** — `b82a62b7` (docs)
19. **Task 3, step 7 (post-dispatch capture, SC #3)** — `038b42dc` (docs)
20. **Task 3, steps 8–10 (Sigstore, ATT-04 boundary, verdict)** — `8cdc7957` (docs)

**Plan metadata:** this SUMMARY.md and its commit (below).

## Files Created/Modified
- `.planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-ATT-EVIDENCE.md` — appended all ATT-02 sections after 76-01's ATT-01 sections; no product, test, or workflow file touched.

## Decisions Made
- Honored the checkpoint protocol exactly: stopped at Task 2, returned the structured checkpoint, and did not proceed to Task 3 until the orchestrator relayed the owner's explicit "dispatch" answer (recorded as `OWNER_CHECKPOINT_CHOICE`, not inferred from the earlier D-05 owner report).
- Fixed several evidence KEY lines that initially carried an inline parenthetical explanation on the same line as the value (violating the plan's "value alone on its line" rule) — moved the prose to the following line before the first verify run, rather than leaving a latent verify failure.
- Retroactively created the #3968 plan-commit ledger file after noticing at SUMMARY time that it had not been created at Task 1's first commit; used the same `BASE_76_03`/`ORIGIN_REF_SHA` value already on the record, so the retroactive base is provably correct rather than guessed.

## Deviations from Plan

None — plan executed exactly as written, including the checkpoint pause and resumption.

## Issues Encountered

None. The `pending_deployments` read at first `waiting` status showed `wait_timer_started_at` already populated, meaning GitHub's reviewer-approval step had completed before this executor's first poll landed inside the 30-second window — the watch simply continued through the remaining `wait_timer` countdown as designed; no HALT, no retry needed.

## User Setup Required

None — no external service configuration required. (D-05's PyPI Trusted Publisher registration was an owner action completed before this plan started, per the phase's `user_setup` frontmatter, and this plan's Task 2 checkpoint captured the owner's confirmation of it before dispatching.)

## Next Phase Readiness

- `ATT02_VERDICT = MET` and, by the evidence's closing sentence, ATT-01's rehearsal half is also closed. Phase 77's handoff can read `76-ATT-EVIDENCE.md` by its fixed name for both ATT-01 and ATT-02.
- Both `PYPI_API_TOKEN` secrets (repository and `pypi` environment scope) are still present, unchanged by this plan — the rollback path stays open until ATT-03 passes and ATT-05 retires them at `/gsd-complete-milestone`.
- No blockers. The one open item for a later phase, already flagged in this phase's CONTEXT (not this plan's job to fix): ROADMAP SC #4, REQUIREMENTS.md ATT-04, and `77-HANDOFF.md`'s pre-written ATT-04 command all still carry the stale `'attestations input ignored'` grep target this session's research falsified — Phase 77 should align them to the two greps actually used here (`disabling Trusted Publishing`, `attestations input is ignored`) before writing its own ATT-04 reading.

---
*Phase: 76-the-password-free-publish-pypi-rehearsed-against-the-published-v0-9-6-and-msg-06*
*Completed: 2026-09-27*

## Self-Check: PASSED

- `76-ATT-EVIDENCE.md` exists on disk: FOUND
- `76-03-SUMMARY.md` exists on disk: FOUND
- Commit `90ea5695` (SUMMARY.md) present in `git log --oneline --all`: FOUND
- Commit `8cdc7957` (final ATT-02 evidence section) present in `git log --oneline --all`: FOUND
- Task 1 `<verify>` automated command: re-ran, exit 0, `TASK1_VERIFY_PASSED`
- Task 3 `<verify>` automated command: re-ran, exit 0, `TASK3_VERIFY_PASSED`
- All `<acceptance_criteria>` for Tasks 1–3: re-checked against the evidence file, all hold
- Plan-level `<verification>`: both task verify commands exit 0; Task 2 returned the owner's
  explicit answer ("dispatch"), recorded as `OWNER_CHECKPOINT_CHOICE` before any Task 3 action
- Plan-level `<success_criteria>`: ROADMAP Phase 76 SC #2/#3/#4 all `MET` from live readings;
  exactly one `workflow_dispatch` of `release.yml` exists on the milestone branch (count = 1)
