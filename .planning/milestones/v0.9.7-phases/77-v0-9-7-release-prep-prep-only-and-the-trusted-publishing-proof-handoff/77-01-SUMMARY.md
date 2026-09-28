---
phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
plan: 01
subsystem: release-prep
tags: [release-checklist, requirements-fence, docs-baseline, linkcheck, pypi-probe, github-cli]

# Dependency graph
requires: []
provides:
  - Line-scoped `.planning/REQUIREMENTS.md` fence (full + guarded-region SHA-256) for ATT-03,
    ATT-04, ATT-05, REL-17, DOC-25, with ATT-06 recorded separately as expected-to-move
  - Clean C-locale docs-html/docs-pdf warning ledger (0/0) and base linkcheck URI set (96/96
    working) with both v0.9.6 tag-link controls, for 77-04 to compare the bumped tip against
  - SC#5 probe observation 1 of 2 — zero irreversible action, every emptiness paired with a
    v0.9.6 positive control
affects: [77-02, 77-03, 77-04, 77-08]

actuals:
  tokens: 10014
  tasks: 3
  commits: 3
  plan_head_before: 3984b231e30fbb76ba156d2f9b2abe475231bccf
  plan_head_after: 344ce657c82f9527208d5ddd51ab0d942bbc0f2b

tech-stack:
  added: []
  patterns:
    - "Line-scoped requirements fence (full + guarded-region SHA-256), carried from Phase 75,
       extended to five simultaneously-guarded IDs with one expected-to-move ID"
    - "Base-vs-tip documentation ledger comparison, clean rm -rf docs/_build + LC_ALL=C builds"
    - "Two-observation SC#5 invariant probe pattern with paired positive controls"

key-files:
  created:
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-CLOSEOUT-GUARD.md
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-BASE-EVIDENCE.md
    - .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-SC5-INVARIANTS.md
  modified: []

key-decisions:
  - "No deviations from plan — all three tasks executed and verified exactly as written."

requirements-completed: []

coverage:
  - id: D1
    description: "Line-scoped REQUIREMENTS.md fence (full SHA-256, guarded-region SHA-256, six
      per-ID hit counts, Discretion A literal-phrase counts) recorded at phase head, with ATT-06
      separated as expected-to-move and REQUIREMENTS/ROADMAP/STATE backed up outside the repo"
    requirement: REL-17
    verification:
      - kind: other
        ref: "77-CLOSEOUT-GUARD.md automated <verify> block (re-run during execution)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Clean C-locale docs-html/docs-pdf warning ledger (0/0) and base linkcheck URI
      set (96/96 working, both v0.9.6 tag-link controls working) for 77-04's comparison"
    requirement: REL-17
    verification:
      - kind: other
        ref: "77-BASE-EVIDENCE.md automated <verify> block (re-run during execution)"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#5 probe observation 1 of 2 — no v0.9.7 tag/PyPI file/GitHub Release/release
      run since the Phase 76 rehearsal, both PYPI_API_TOKEN scopes present, each with a v0.9.6
      positive control"
    requirement: REL-17
    verification:
      - kind: other
        ref: "77-SC5-INVARIANTS.md automated <verify> block (re-run during execution)"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-28
status: complete
---

# Phase 77 Plan 01: Phase-head baselines Summary

**The five-ID line-scoped REQUIREMENTS fence, the clean base documentation ledger, and SC#5's
first zero-irreversible-action probe observation, all recorded before any product edit lands.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-28T13:07:46Z
- **Completed:** 2026-09-28T13:15:33Z
- **Tasks:** 3
- **Files modified:** 3 created, 0 modified

## Accomplishments
- `77-CLOSEOUT-GUARD.md`: full and guarded-region SHA-256 digests over `.planning/REQUIREMENTS.md`
  (`REQ_SHA256_BASE = 35eb6122ef…`, `REQ_SHA256_GUARDED_BASE = fce6cc7d40…`), the six per-ID hit
  counts for ATT-03/04/05/06, REL-17 and DOC-25 all matching the planning-time census exactly, the
  two Discretion A literal-phrase counts (1 in REQUIREMENTS.md, 3 in ROADMAP.md), and
  REQUIREMENTS/ROADMAP/STATE backed up to `/tmp/p7701.p8Y5y6` outside the repository.
- `77-BASE-EVIDENCE.md`: `tox -e docs-html` and `tox -e docs-pdf` each `build succeeded.` (0
  warnings) from a removed `docs/_build`, under `LANG=C LANGUAGE=C LC_ALL=C`; `tox -e linkcheck`
  96/96 `working` in one attempt with a recorded URI-set digest
  (`918f7d0135a6fc047aa88583db7e7da6378638618d16a8a1e36b4af9151b63c1`); both `v0.9.6` tag-referencing
  changelog links resolve `working` on the unbumped tree — the positive control 77-04's bumped-tip
  comparison reads against.
- `77-SC5-INVARIANTS.md`: no local or remote `v0.9.7` tag, no 0.9.7 PyPI file (Simple JSON API, 38
  total files), no `v0.9.7` GitHub Release, no `release.yml` run newer than the Phase 76 rehearsal
  (`36321530105`), no `gsd/v0.9.7-milestone` decoy branch on origin, and no version-bump commit yet
  — every emptiness probe paired with a non-empty `v0.9.6` control (local/remote tag, PyPI file
  count, GitHub Release, the rehearsal-run positive control `35730551619` itself resolving). Both
  `PYPI_API_TOKEN` GitHub scopes and `TEST_PYPI_API_TOKEN` (repository scope) confirmed present,
  names only.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — head check, PHASE_BASE_SHA, the five-ID line-scoped fence with ATT-06
   recorded separately, the Discretion A literal counts, and the scratch backups** —
   `19afca87` (docs)
2. **Task 2: The clean base documentation ledger and the base linkcheck URI set, in the C locale**
   — `5495a57f` (docs)
3. **Task 3: SC#5 probe observation 1 of 2** — `344ce657` (docs)

**Plan metadata:** this SUMMARY's own commit (below).

## Files Created/Modified
- `77-CLOSEOUT-GUARD.md` — line-scoped requirements fence, ATT-06 expected-to-move callout,
  re-verification protocol, operator section, scratch backups
- `77-BASE-EVIDENCE.md` — clean docs-html/docs-pdf ledger and base linkcheck URI set
- `77-SC5-INVARIANTS.md` — SC#5 observation 1 of 2

## Decisions Made
None beyond the plan's own instructions — followed as specified. No architectural or scope
questions arose during execution.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' `<automated>` verify blocks were run and
passed before each commit (not merely inspected).

## Issues Encountered

**Documentation-only note (not a deviation from the plan's instructions, but worth recording):**
the plan's Task 2 action prescribes recording the `LCBASE` lines "inside a fenced block" without
specifying they must be independently re-derived rather than composed by hand; a first draft of
that block was typed from memory of a similar prior-phase linkcheck output and did not match the
actual 96-URI set from this run. It was caught by re-deriving the block programmatically from
`$S/p7701_linkcheck_base.json` and diffing against the first draft before running the task's
`<verify>` — the committed file contains only the verified, actual data, and the automated verify
(including the `BASE_LINKCHECK_URISET_SHA256` cross-check between the JSON-derived digest and the
`LCBASE` lines' own digest) passed against it.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Wave 1 siblings 77-02 (0.9.7 bump + CHANGELOG) and 77-03 (ATT-06 rollback section + controls)
  run in parallel worktrees and do not depend on this plan's output directly, but 77-04 (wave 2)
  reads `77-BASE-EVIDENCE.md`'s `BASE_HTML_WARNINGS`, `BASE_PDF_WARNINGS` and `LCBASE` lines, and
  `77-08` (wave 5) re-runs `77-CLOSEOUT-GUARD.md`'s re-verification protocol and repeats
  `77-SC5-INVARIANTS.md`'s probes as observation 2 of 2.
- `.planning/REQUIREMENTS.md` is confirmed byte-identical to its state at `PHASE_BASE_SHA`
  (`git diff --name-only 3984b231e30fbb76ba156d2f9b2abe475231bccf HEAD -- .planning/REQUIREMENTS.md`
  empty), and nothing under `typsphinx/` or any tracked path outside `.planning/` changed
  (`git diff --name-only 3984b231e30fbb76ba156d2f9b2abe475231bccf HEAD -- . ':(exclude).planning'`
  empty) — the prep-only fence and the zero-product-change constraint both hold at this plan's
  close.
- No blockers.

## Self-Check: PASSED

- `test -f .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-CLOSEOUT-GUARD.md` → FOUND
- `test -f .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-BASE-EVIDENCE.md` → FOUND
- `test -f .planning/phases/77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff/77-SC5-INVARIANTS.md` → FOUND
- `git log --oneline --all --grep="77-01"` → matches `19afca87`, `5495a57f`, `344ce657` (FOUND, 3 commits)
- All three tasks' `<automated>` verify blocks re-run and PASSED at commit time (see task narration above)
- Plan-level `<verification>` re-checked: REQUIREMENTS.md byte-identical to `PHASE_BASE_SHA`
  (empty diff); both `77-BASE-EVIDENCE.md` clean builds and 96/96 linkcheck with both v0.9.6
  controls `working`; `77-SC5-INVARIANTS.md` § "Observation 1 of 2" complete with every emptiness
  paired with a control — all confirmed above

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Completed: 2026-09-28*
