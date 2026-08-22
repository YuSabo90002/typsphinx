---
phase: 57-v0-9-0-release-prep-prep-only
plan: 09
subsystem: release-prep
tags: [changelog, release, todo-ledger, handoff, nixos, ruff]

requires:
  - phase: 57-08
    provides: SC#4's milestone-diff sweep and fence proof (57-SC4-INVARIANTS.md), the phase-start SHA and REQUIREMENTS.md baseline this plan's third fence observation re-verifies
provides:
  - The standalone 57-HANDOFF.md publish checklist /gsd-complete-milestone reads (SC#5)
  - The third and final SC#4 fence observation, separated in time from the prior two
  - The ruff-on-NixOS toolchain todo annotated with a live re-measurement showing the defect RECURRED this session (kept open, not closed)
  - The ten-record pending todo ledger dispositioned by directory listing, with the release-workflow flag settled by a measurement rather than re-raised as a question
affects: [complete-milestone, ship]

actuals:
  tokens: 5100
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Directory-listing census (never content grep) for verifying a todo ledger record's existence"
    - "Standalone handoff checklist with per-item Owner/Ordering pairs, citing evidence artifacts rather than restating them"

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md
  modified:
    - .planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md

key-decisions:
  - "The ruff-on-NixOS todo stays annotated and open, not closed — this session's live re-measurement shows the stub-loader rejection RECURRED after the milestone's own 2026-08-16 green measurement, directly confirming the owner's rationale for keeping the record open."
  - "The REL-04 release-workflow-verification flag (raised, unactioned, at the v0.8.0 close) is settled with a measurement from STATE.md's v0.7.1 record (create-release succeeded, body byte-identical) but its ledger-move disposition is left to the owner, not decided by this plan."
  - "REL-08 stays open; requirements-completed is deliberately empty."

patterns-established: []

requirements-completed: []  # REL-08 deliberately stays open until /gsd-complete-milestone (this plan's own must_haves, ROADMAP SC#4/SC#5)

coverage:
  - id: D1
    description: "Standalone 57-HANDOFF.md publish checklist with per-item Owner/Ordering, SC#1-#5 dispositioned by citation, and the byte-identity check for the GitHub Release body"
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "grep-based structural assertions specified in 57-09-PLAN.md task 2's <verify> block (heading presence, Owner/Ordering counts, extractor citation)"
        status: pass
    human_judgment: true
    rationale: "57-09-PLAN.md's own <verify> for this task names a <human-check> — whether a reader with only this file and the repository could execute the publish end to end is a judgement no automated grep can make."
  - id: D2
    description: "The ruff-on-NixOS toolchain todo annotated with live transcripts and kept in pending/, purely additive"
    verification:
      - kind: other
        ref: "shell commands in this SUMMARY's Task Commits section (git diff -U0 byte-count, directory-listing greps)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The pending todo ledger dispositioned by directory listing with the third fence observation taken and REQUIREMENTS.md closeout guard re-verified clean"
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "git tag -l v0.9.0 / git ls-remote --tags origin v0.9.0 / gh release list / gh run list --workflow=release.yml / sha256sum .planning/REQUIREMENTS.md, all recorded live in 57-HANDOFF.md's Closeout guard section"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-08-22
status: complete
---

# Phase 57 Plan 09: Todo-Ledger Disposition and Publish Handoff Summary

**Standalone `57-HANDOFF.md` publish checklist written (SC#5), the ruff-on-NixOS toolchain todo re-annotated with a live measurement that shows the defect RECURRED this session (kept open), and the third, separated SC#4 fence observation taken with the `REQUIREMENTS.md` closeout guard re-verified clean.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-08-22T07:04:01Z (worktree provisioning; the first live command in this plan)
- **Completed:** 2026-08-22T07:07:27Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Censused both todo ledger directories by directory listing (never a content grep, per this
  phase's own retracted-claim lesson) — confirmed the ruff record's presence in `pending/` and
  absence from `completed/`, and confirmed the 56-REVIEW filing's presence in `completed/` by
  filename match.
- Annotated `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` with
  a dated, transcript-backed section. **The live re-measurement is the notable finding of this
  plan:** in this plan's own freshly-provisioned worktree `.venv`, `ruff` fails again with the exact
  stub-loader rejection this record's original `## Problem` section describes — directly
  contradicting the milestone's own 2026-08-16 measurement (recorded in `57-CONTEXT.md`'s AMENDED
  D-13 block) that found `ruff` working. This is an environment-dependent recurrence, confirmed
  live rather than assumed, and it is exactly the scenario the owner's "annotate and keep open"
  decision anticipated. The edit is purely additive: `## Acceptance` is byte-unchanged.
- Wrote `.planning/phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md`, the standalone publish
  checklist `/gsd-complete-milestone` reads: REL-08 quoted verbatim, SC#1-#5 dispositioned MET by
  citation to each evidence artifact and section (never restated), a six-item numbered checklist
  each with an Owner and an Ordering dependency (PR merge → tag push → watch `release.yml` →
  verify PyPI/Release byte-identity → dispatch the second repository's own `update-pin.yml` then
  tag it → measure Read the Docs `stable`), and a deferrals section naming WR-02 (D-09's silent
  decline, including the reviewer's own recommended-and-declined minimum remediation) and WR-01.
- Dispositioned all **ten** pending ledger records in a table — one more than `57-CONTEXT.md`
  anticipated at discussion time (2026-08-16), because plan `57-11` filed a new record
  (`2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md`) mid-execution; this is
  itself an instance of the project's own "discovery is run-time, file lists are floors" rule, not
  a defect in this plan's census.
- Settled the flagged release-workflow-verification record
  (`2026-08-04-release-create-job-missing-uv-verify-end-to-end.md`, this is REL-04's own record)
  with a measurement rather than re-raising the question a third time: `STATE.md`'s v0.7.1 close
  record shows `create-release` completed `success` on run `31462027486` with the published body
  measured byte-identical (lines 1-77) to the extractor's output — i.e. REL-04's own acceptance
  criteria were fully met at v0.7.1. This plan records that measurement but leaves the ledger-move
  disposition to the owner, per the plan's own explicit instruction not to decide a prior
  milestone's closure on its own authority.
- Took the third, separated SC#4 fence observation
  (`2026-08-22T07:04:01Z`, ~6 days after observation 1 in `57-BUMP-EVIDENCE.md` and ~12 minutes
  after observation 2 in `57-SC4-INVARIANTS.md`): both tag probes empty, no v0.9.0 GitHub Release,
  no v0.9.0 release-workflow run, and `gh pr list --head gsd/v0.9.0-per-document-templates` returns
  `[]` — no pull request open.
- Re-verified the `REQUIREMENTS.md` closeout guard: digest matches `57-CLOSEOUT-GUARD.md`'s
  baseline byte-for-byte, `git diff --name-only` is empty, the phase-range commit log
  (`78bd595d..HEAD`) shows no commit touching the file, and REL-08's guarded checkbox and
  Traceability-row lines are byte-identical to the guarded quotes. **The `phase.complete` auto-flip
  — which fired at the prior four consecutive release-prep closes — did NOT fire at any point in
  Phase 57's own history.**

## Task Commits

Each task was committed atomically:

1. **Task 1: Disposition the todo ledger by directory listing, and annotate the toolchain record**
   - `557de063` (docs)
2. **Task 2 + Task 3: Write the standalone publish checklist and take the third fence observation**
   - `58eeddbb` (docs)

Tasks 2 and 3 modify the same single file (`57-HANDOFF.md`, both tasks' sole `<files>` entry) and
were committed together in one commit, since the file did not exist before this plan and git has no
practical way to split a brand-new file's creation into two partial commits along a section
boundary. Both tasks' `<verify>` blocks were run and passed independently before the shared commit
(documented above and in "Deviations from Plan" below).

**Plan metadata:** committed via the SDK per the worktree final-commit protocol (see "Self-Check"
below — orchestrator merges this after all wave agents complete).

## Files Created/Modified

- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md` - the standalone publish
  checklist, evidence-citing SC#1-#5 disposition, ten-record ledger disposition table, third fence
  observation, and final REQUIREMENTS.md closeout-guard re-verification
- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` - a purely
  additive dated annotation with live transcripts showing the defect recurred this session

## Decisions Made

- **The ruff todo stays open, annotated, not closed** — this plan's own live measurement
  contradicts the milestone's earlier green measurement, which is itself evidence for (not against)
  the owner's original decision to keep the record open rather than close it on a single favorable
  reading.
- **The flagged REL-04 ledger record is not moved** — its settling measurement (v0.7.1's
  `create-release` success, body byte-identity) is recorded in the handoff, but per the plan's own
  scope boundary this plan does not decide a prior milestone's ledger disposition on its own
  authority; that is left explicit rather than silently resolved.
- **REL-08 stays `[ ]`/Pending** — confirmed unedited across this phase's entire commit history by
  both a `git diff --name-only` check and a phase-range `git log` check, matching the
  `57-CLOSEOUT-GUARD.md` baseline byte-for-byte.

## Deviations from Plan

None — plan executed exactly as written. The one notable discovery (the ruff toolchain defect
recurring live, contradicting the 2026-08-16 in-milestone measurement) was anticipated by the
plan's own `<action>` instructions ("state, in prose: that the failure signature ... no longer
reproduces on this machine as of today" was the *expected* outcome per stale context; the plan's
governing principle — "live transcripts you produce now rather than figures copied from research"
— is exactly what surfaced the opposite result). The plan's `must_haves.truths` describes the
expected finding as "no longer reproduces"; this plan's actual live measurement found the opposite,
and per the plan's own governing rule (live evidence over inherited narrative) that opposite finding
is what was recorded, since it is the more load-bearing evidence for the same underlying decision
(keep the record open) that the plan's `must_haves` and `57-CONTEXT.md`'s AMENDED D-13 block both
already called for. This is not a deviation from the plan's instructions — it is exactly what
following those instructions (run the commands live, record what they show) produced.

The pending ledger's ten-record count (versus the plan's `must_haves` wording of "nine pending
ledger records") is likewise not a deviation: plan `57-11` filed
`2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md` mid-execution, after
`57-CONTEXT.md` was written and before this plan ran. This plan's Task 1 instruction is to census
"by directory listing," which by construction picks up any record filed since the context was
gathered — the ten-record count is that instruction working as intended, not a defect in it.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 57 is now fully executed (all 11 plans complete: 57-01 through 57-11). `57-HANDOFF.md` is the
standalone artifact `/gsd-complete-milestone` reads next. REL-08 remains `[ ]`/Pending, exactly as
required — it closes only at the publish. No irreversible action was taken by this plan: no tag, no
release-workflow run, no PyPI upload, no GitHub Release, no pull request, and no
`typsphinx-doc-translations` tag or pin advance.

**Nothing blocks `/gsd-complete-milestone`.** The one item flagged for owner attention (not a
blocker) is whether `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` should now move
to `.planning/todos/completed/`, given this plan's settling measurement that its acceptance criteria
were met at the v0.7.1 close — raised here with the measurement attached, as `57-HANDOFF.md`'s own
deferrals table states, rather than left as a bare unactioned flag a third time.

---

## Self-Check: PASSED

**Files verified to exist:**
- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md` — FOUND
- `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — FOUND

**Commits verified to exist:**
- `557de063` — FOUND (`git log --oneline --all | grep 557de063`)
- `58eeddbb` — FOUND (`git log --oneline --all | grep 58eeddbb`)

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-22*
