---
phase: 52-v0-8-0-release-prep-prep-only
plan: 07
subsystem: docs
tags: [release-prep, roll-up, handoff, requirements-guard]

# Dependency graph
requires:
  - phase: 52-01
    provides: "52-BUMP-EVIDENCE.md (SC#1)"
  - phase: 52-02
    provides: "the curated ## [0.8.0] CHANGELOG entry (SC#2), cited via 52-02-SUMMARY.md"
  - phase: 52-03
    provides: "52-GOAL-CLAIM-EVIDENCE.md (SC#3 goal-claim half)"
  - phase: 52-04
    provides: "52-CI-EVIDENCE.md's first (RED) CI authority section (SC#3 toolchain half)"
  - phase: 52-05
    provides: "52-GREEN-TREE-EVIDENCE.md (SC#3 local half)"
  - phase: 52-06
    provides: "52-SC4-INVARIANTS.md (SC#4)"
  - phase: 52-08
    provides: "52-CI-EVIDENCE.md's second (11/12) CI run section, three of four defects fixed"
  - phase: 52-09
    provides: "52-CI-EVIDENCE.md's third (12/12, accepted) CI run section; the fifth deferred todo"
provides:
  - "52-RELEASE-EVIDENCE.md: one verdict per ROADMAP SC#1-SC#5, citing rather than restating sibling
     evidence, with SC#3's honest three-run CI history (RED -> 11/12 -> GREEN) recorded in full"
  - "52-HANDOFF.md: the standalone publish checklist /gsd-complete-milestone reads, the deferred-
     defect register (all five records named with real todos/pending/ filenames), and the closeout
     guard pinning REL-07's still-Pending state with a REQUIREMENTS.md checksum"
affects: [complete-milestone, ship]

# Actuals (#2632)
actuals:
  tokens: 11815
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Cite-not-restate roll-up: each SC section quotes at most one verdict line from its sibling
       evidence file and attributes any repeated figure, rather than re-deriving or re-measuring it"

key-files:
  created:
    - .planning/phases/52-v0-8-0-release-prep-prep-only/52-RELEASE-EVIDENCE.md
    - .planning/phases/52-v0-8-0-release-prep-prep-only/52-HANDOFF.md
  modified: []

key-decisions:
  - "SC#3's roll-up records all three CI dispatches (RED 8/12, 11/12, GREEN 12/12) in full rather
     than presenting only the accepted third run, per this plan's own must_have that a roll-up cites
     rather than restates and per the orchestrator's explicit instruction that the honest RED-then-
     fixed shape is more valuable than a fabricated clean one"
  - "The fifth deferred item (typsphinx/builder.py's isabs() drive-awareness gap, surfaced by 52-09
     mid-phase) is named individually in the handoff's deferred-defect register with the same
     treatment as the four defects enumerated in the plan's own must_haves, since the plan's own
     reasoning for naming those four (no second surface once D-01/D-03 remove every other channel)
     applies identically to this fifth item"
  - "The REL-04 todo's todos/pending/ vs. todos/completed/ placement question, flagged but not
     decided in 52-CONTEXT.md, is carried forward flagged rather than resolved here -- resolving it
     is a ledger-triage act outside this plan's declared scope (write two roll-up artifacts, take no
     irreversible action)"

requirements-completed: []  # REL-07 deliberately stays Pending until /gsd-complete-milestone

coverage:
  - id: D1
    description: "52-RELEASE-EVIDENCE.md gives one verdict per SC#1-SC#5, citing all five sibling
      evidence artifacts by name, and proves the accepted CI authority SHA (6924a0be) covers the
      whole source delta"
    verification:
      - kind: other
        ref: "grep -c '^## Phase verdict' / '^## SC#5' both 1; git diff --name-only 6924a0be..HEAD -- . ':(exclude).planning' empty; all five sibling evidence filenames cited"
        status: pass
    human_judgment: false
  - id: D2
    description: "52-HANDOFF.md is a standalone 7-item publish checklist naming validate/build/
      publish-pypi/create-release in order, the typsphinx-doc-translations second tag, and the RTD
      stable measurement on both projects"
    verification:
      - kind: other
        ref: "grep -c 'REL-07 remains open' == 1; 7 numbered ### checklist items present in order; 'create-release' and 'typsphinx-doc-translations' both present"
        status: pass
    human_judgment: false
  - id: D3
    description: "All five deferred records named with real todos/pending/ filenames that exist on disk"
    verification:
      - kind: other
        ref: "10 filenames extracted from 52-HANDOFF.md via grep -oE, each confirmed present via ls against .planning/todos/pending/"
        status: pass
    human_judgment: false
  - id: D4
    description: "REL-07's checkbox and Traceability row pinned unchanged, with a REQUIREMENTS.md checksum and revert instruction"
    verification:
      - kind: other
        ref: "grep -qE '^- \\[ \\] \\*\\*REL-07\\*\\*' and '^\\| REL-07 \\| Phase 52 \\| Pending \\|' both match; git diff --name-only -- .planning/REQUIREMENTS.md empty"
        status: pass
    human_judgment: false
  - id: D5
    description: "Nothing under typsphinx/ changed by this plan; no reserved 52-VERIFICATION.md filename; no v0.8.0 tag locally or on origin"
    verification:
      - kind: other
        ref: "git diff --name-only -- typsphinx/ empty (checked after every task); ls phase dir shows no 52-VERIFICATION.md; git tag -l v0.8.0 and git ls-remote --tags origin v0.8.0 both empty"
        status: pass
    human_judgment: false

# Metrics
duration: ~25min
completed: 2026-08-15
status: complete
---

# Phase 52 Plan 07: Roll Up the Evidence and Write the Publish Handoff Summary

**Wrote `52-RELEASE-EVIDENCE.md` (one verdict per SC#1-SC#5, citing five sibling evidence artifacts and recording SC#3's honest three-run CI history — RED, then 11/12, then GREEN) and `52-HANDOFF.md` (the standalone `/gsd-complete-milestone` publish checklist plus a five-item deferred-defect register), then pinned REL-07's still-Pending state against the closeout auto-flip hazard.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3 of 3 completed
- **Files created:** 2 (`52-RELEASE-EVIDENCE.md`, `52-HANDOFF.md`)
- **Files modified:** 0 (Task 3 amends `52-HANDOFF.md`, one of this plan's own new files, not a
  pre-existing tracked file)

## Accomplishments

- **Task 1 — `52-RELEASE-EVIDENCE.md`.** Rolled up all five ROADMAP Phase 52 success criteria,
  citing `52-BUMP-EVIDENCE.md` (SC#1), `52-02-SUMMARY.md` (SC#2), `52-CI-EVIDENCE.md` +
  `52-GREEN-TREE-EVIDENCE.md` + `52-GOAL-CLAIM-EVIDENCE.md` (SC#3, all three parts), and
  `52-SC4-INVARIANTS.md` (SC#4). **SC#3's own section records all three CI dispatches in sequence**
  — the first run (plan 52-04, run `31855486993`) came back RED, 8 of 12 jobs failing on three
  pre-existing defects; the second run (plan 52-08, run `31856929828`) reached 11/12 after fixing
  those three, but surfaced a fourth, previously-unknown Python-3.13-on-Windows defect; the third
  run (plan 52-09, run `31858016832`) reached 12/12 after a test-side fix, and is the run this
  roll-up accepts as SC#3's toolchain authority. Re-measured live, rather than transcribed:
  `git diff --name-only 6924a0be..HEAD -- . ':(exclude).planning'` is empty — every commit since the
  accepted authority SHA touches only `.planning/`, proving the authority run covers this phase's
  entire source delta. Also re-confirmed live: the one `### Known Limitations` heading anywhere in
  `CHANGELOG.md` sits inside the historical `[0.1.0b1]` entry, not `[0.8.0]`.
- **Task 2 — `52-HANDOFF.md`.** Wrote the standalone seven-item publish checklist (merge → tag →
  `release.yml`'s four jobs in order with an explicit instruction to observe `create-release`
  succeed → the `typsphinx-doc-translations` second tag → RTD `stable` on both projects → flip
  REL-07 → re-date the CHANGELOG heading if needed), the "Not done in this phase, by design" fence
  enumeration, and the deferred-defect register. **Named all five deferred records individually**
  with their real `.planning/todos/pending/` filenames (all 10 files in the directory were listed
  and cross-checked — the four D-01 defects, the `:numref:` record, and the fifth item plan 52-09
  surfaced mid-phase, `2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md`), plus the
  four remaining reviewed-but-not-folded todos including the flagged REL-04 `pending/` vs.
  `completed/` question. Stated **`REL-07 remains open`** in those literal words and recorded fence
  observation 2 of 2 (`2026-08-15T02:24:28Z`, 4 minutes 6 seconds after observation 1 in
  `52-RELEASE-EVIDENCE.md`) — both `git tag -l v0.8.0` and `git ls-remote --tags origin v0.8.0`
  empty at both moments.
- **Task 3 — closeout guard.** Recorded REL-07's two `.planning/REQUIREMENTS.md` lines verbatim with
  line numbers (`103`: checkbox `- [ ]`; `268`: Traceability row `Pending`), the file's
  `sha256sum` (`566859ea...`), and the phase's closing fence checks — `git diff --name-only --
  .planning/REQUIREMENTS.md` empty, `git diff --name-only -- typsphinx/` empty, no
  `52-VERIFICATION.md` in the phase directory, `git status --porcelain` clean at rest — as a new
  `## Closeout guard — REL-07 must stay Pending` section appended to `52-HANDOFF.md`, with the
  revert instruction for whoever runs `/gsd-complete-milestone`'s own closeout automation.

## Task Commits

Each task was committed atomically:

1. **Task 1: Roll the evidence up into one verdict per success criterion** — `ccc1f271` (docs)
2. **Task 2: Write the standalone publish checklist and the deferred-defect register** — `be1b7278`
   (docs)
3. **Task 3: Guard REQUIREMENTS.md against the closeout auto-flip and confirm the phase's own
   fences** — `4be9d1c8` (docs)

_No separate plan-metadata commit — worktree mode: STATE.md/ROADMAP.md are excluded per the
orchestrator's centralized post-wave write; this SUMMARY's own commit follows._

## Files Created/Modified

- `.planning/phases/52-v0-8-0-release-prep-prep-only/52-RELEASE-EVIDENCE.md` — SC#1-SC#5 roll-up,
  citing five sibling evidence artifacts; SC#3's honest three-CI-run history; fence observation 1 of
  2.
- `.planning/phases/52-v0-8-0-release-prep-prep-only/52-HANDOFF.md` — standalone publish checklist,
  deferred-defect register (5 records named), fence observation 2 of 2, and the Closeout guard
  section pinning REL-07.

## Decisions Made

- SC#3's roll-up presents all three CI dispatches, not only the accepted third one — the RED-then-
  fixed history is recorded because it is the honest shape and is more valuable than a fabricated
  clean pass, per the orchestrator's explicit instruction accompanying this plan.
- The fifth deferred item (the `isabs()` drive-awareness gap plan 52-09 filed) is treated identically
  to the four defects the plan's own `must_haves` enumerate — same filename citation, same
  reachability-condition transcription, same D-01/D-03 framing — because the plan's own reasoning
  for naming those four (D-01/D-03 remove every other surface) applies without modification to this
  fifth one.
- The REL-04 todo's `pending/` vs. `completed/` placement question (flagged in `52-CONTEXT.md`, not
  decided) is carried forward flagged, not resolved — this plan's scope is two roll-up artifacts and
  a guard section, not ledger triage.

## Deviations from Plan

None — plan executed exactly as written, including the explicit context correction supplied at
spawn time (the SC#3 three-CI-run history and the fifth deferred item, both incorporated as
directed rather than treated as deviations from the plan's own text).

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 52's evidence and handoff are both complete and cite each other consistently:
  `52-RELEASE-EVIDENCE.md` takes fence observation 1 of 2, `52-HANDOFF.md` takes observation 2 of 2
  at a distinct later timestamp.
- `52-HANDOFF.md` is the standalone document `/gsd-complete-milestone` reads for this milestone's
  owner-manual publish steps — merge, tag, `release.yml` (with an explicit `create-release`
  observation instruction), the `typsphinx-doc-translations` second tag, the RTD `stable`
  measurement, and the REL-07 checkbox flip, in that order.
- **REL-07 is NOT closed.** `.planning/REQUIREMENTS.md`'s checkbox (`- [ ]`) and Traceability row
  (`Pending`) are unchanged by this plan (`git diff --name-only -- .planning/REQUIREMENTS.md` empty
  throughout), and this plan does not close it.
- Nothing under `typsphinx/` changed by this plan (`git diff --name-only -- typsphinx/` empty at
  every checkpoint); no `v0.8.0` tag exists locally or on `origin`; no `52-VERIFICATION.md` file
  exists in the phase directory.
- All five deferred defects (four D-01 records plus the fifth `isabs()` finding) and the `:numref:`
  record stay in `.planning/todos/pending/` — not promoted to the ROADMAP backlog, per D-03.

## Self-Check

- FOUND: `.planning/phases/52-v0-8-0-release-prep-prep-only/52-RELEASE-EVIDENCE.md`
- FOUND: `.planning/phases/52-v0-8-0-release-prep-prep-only/52-HANDOFF.md`
- FOUND commit `ccc1f271` (Task 1)
- FOUND commit `be1b7278` (Task 2)
- FOUND commit `4be9d1c8` (Task 3)

## Self-Check: PASSED

---
*Phase: 52-v0-8-0-release-prep-prep-only*
*Completed: 2026-08-15*
