---
phase: 75-v0-9-6-release-prep-prep-only
plan: 01
subsystem: release-prep
tags: [requirements-fence, docs-ledger, sc5-probes, release, prep-only]

requires:
  - phase: 74
    provides: the doctest_block handler, its real-compile GATE-01 gate, and the QUA-14 docstring
      fix that made the base documentation build clean (BASE_WARNING_COUNT 5 -> 0,
      BASE_DOCTEST_UNKNOWN_COUNT 2 -> 0)
provides:
  - the line-scoped REL-15 REQUIREMENTS fence baseline (75-CLOSEOUT-GUARD.md), with REL-16
    recorded separately as expected-to-move
  - the clean C-locale docs-html/docs-pdf warning ledger at the phase base (75-BASE-EVIDENCE.md),
    which 75-04 compares the bumped tip against
  - SC5 probe observation 1 of 2 (75-SC5-INVARIANTS.md), every emptiness claim paired with a
    v0.9.2 positive control
affects: [75-03, 75-04, 75-07]

actuals:
  tokens: 8228
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "SHA-256 + wc -l + verbatim grep -n fence on a single requirement ID, line-scoped rather
      than whole-file, because a sibling requirement (REL-16) closes legitimately inside the same
      phase"
    - "Every zero warning/message-class count paired with a synthetic positive-control fixture
      plus a quoted real-build pre-fix control from the prior phase, so the zero is falsifiable"
    - "Every expected-empty remote probe (tag, PyPI, GitHub Release, CI run) paired with a
      v0.9.2 positive control in the same command family"

key-files:
  created:
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-CLOSEOUT-GUARD.md
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-BASE-EVIDENCE.md
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-SC5-INVARIANTS.md
  modified: []

key-decisions:
  - "REL-15's fence is line-scoped (grep -n on lines 22/59 as state-bearing) rather than
    whole-file SHA-256-only, because REL-16 (lines 23/60) legitimately flips to Complete inside
    this same phase at 75-07 — a whole-file digest would false-positive on REL-16's own intended
    completion."
  - "Both docs message-class zeros (BASE_DOCTEST_UNKNOWN, BASE_DOCSTRING_REST) are recorded
    falsifiable: a synthetic control fixture yields >=1 hit per pattern, and Phase 74's own
    pre-fix real-build counts (BASE_WARNING_COUNT=5, BASE_DOCTEST_UNKNOWN_COUNT=2 at 6cc44f22)
    are quoted as the real-build control."

requirements-completed: []

coverage:
  - id: D1
    description: "REL-15 fence baseline recorded, line-scoped to state-bearing lines, with REL-16
      separated as expected-to-move and a three-observation re-verification protocol written for
      the operator"
    requirement: "REL-15"
    verification:
      - kind: other
        ref: "75-01-PLAN.md Task 1 <verify><automated> shell assertion, re-run post-commit"
        status: pass
    human_judgment: false
  - id: D2
    description: "Clean, C-locale docs-html and docs-pdf documentation warning ledger at the
      phase base, both message classes at 0, falsifiable against a synthetic control and Phase
      74's quoted pre-fix real-build measurement"
    requirement: null
    verification:
      - kind: other
        ref: "75-01-PLAN.md Task 2 <verify><automated> shell assertion, re-run post-commit"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC5 probe observation 1 of 2 on the record: no v0.9.6 tag/PyPI release/GitHub
      Release/decoy branch, every emptiness paired with a v0.9.2 positive control"
    requirement: "REL-15"
    verification:
      - kind: other
        ref: "75-01-PLAN.md Task 3 <verify><automated> shell assertion, re-run post-commit"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-20
status: complete
---

# Phase 75 Plan 01: Baseline Fence, Docs Ledger, and SC5 Probe Observation 1 Summary

**Line-scoped REL-15 REQUIREMENTS fence, a clean C-locale docs-html/docs-pdf zero-warning ledger,
and SC5's first zero-irreversible-action probe observation, all recorded at the phase base before
any product edit exists.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-20T08:36:33Z
- **Completed:** 2026-09-20T08:44:20Z
- **Tasks:** 3
- **Files modified:** 3 (all new)

## Accomplishments

- `75-CLOSEOUT-GUARD.md`: `PHASE_BASE_SHA = 526a21d352696cb65c570d07d75ef8c7e3aa96a1`,
  `MILESTONE_BASE = 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b` confirmed via `git merge-base`,
  `REQ_SHA256_BASE`, `REQ_LINES_BASE`, `REL15_HITS_BASE = 4`, `REL16_HITS_BASE = 5` all recorded
  and matched digit-for-digit against the live file and the planning-time census. REL-15's two
  state-bearing lines (checkbox line 22, Traceability row line 59) are transcribed verbatim;
  REL-16's lines are separated into their own "Expected to move" section since REL-16 legitimately
  closes at 75-07. `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md`
  are backed up to `/tmp/tmp.Ea8hUnFA4z` outside the repository. A three-observation
  re-verification protocol (phase head / phase close / after `phase.complete`-family tooling) is
  written inline for the operator.
- `75-BASE-EVIDENCE.md`: `rm -rf docs/_build` then a clean `LANG=C LANGUAGE=C LC_ALL=C tox -e
  docs-html` and `tox -e docs-pdf`, both `build succeeded.` with zero warnings.
  `BASE_DOCTEST_UNKNOWN = 0` and `BASE_DOCSTRING_REST = 0` on the `-b typstpdf` log, each
  falsified against a synthetic control fixture yielding >=1 hit per pattern and against Phase
  74's own pre-fix real-build measurement (`BASE_WARNING_COUNT = 5`,
  `BASE_DOCTEST_UNKNOWN_COUNT = 2` at `6cc44f22`).
- `75-SC5-INVARIANTS.md` § "Observation 1 of 2": no local or remote `v0.9.6` tag (`v0.9.2` present
  as control), PyPI 404 for `0.9.6` / 200 for `0.9.2`, GitHub Release latest is `v0.9.2` with zero
  `v0.9.6` releases, zero `release.yml` runs since the `v0.9.2` publish run (recorded as the
  positive control), zero `gsd/v0.9.6-milestone` decoy branches on origin, zero version-bump
  commits yet at this point in the phase.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: head check, PHASE_BASE_SHA, the line-scoped REL-15 fence with REL-16
   recorded separately, and the scratch backups** - `6dbe7024` (docs)
2. **Task 2: The clean base documentation ledger, in the C locale, with a synthetic grep control
   and Phase 74's pre-fix real-build control** - `479978cd` (docs)
3. **Task 3: SC5 probe observation 1 of 2 - no tag, no PyPI release, no GitHub Release, each with
   a v0.9.2 positive control** - `a1c2969b` (docs)

**Plan metadata:** this SUMMARY's own commit (recorded after this file is written).

## Files Created/Modified

- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-CLOSEOUT-GUARD.md` - REL-15 fence
  baseline, REL-16 expected-to-move record, scratch backups, three-observation protocol
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-BASE-EVIDENCE.md` - clean C-locale
  docs-html/docs-pdf warning ledger with both message-class counts at 0, falsifiable
- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-SC5-INVARIANTS.md` - SC5 probe
  observation 1 of 2, every emptiness paired with a v0.9.2 positive control

## Decisions Made

- REL-15's fence is line-scoped to its two state-bearing lines (checkbox + Traceability row)
  rather than a whole-file SHA-256-only guard, because REL-16 shares the same file and
  legitimately closes inside this phase at 75-07 — a whole-file digest would false-positive on
  REL-16's own intended completion. This is per the plan's own must_haves and ROADMAP constraint 9.
- The synthetic control fixture (`p7501_control.txt`) was written with all three message-class
  shapes in one file rather than three separate files, since the plan's verify script only checks
  each pattern independently against the same fixture path.

## Deviations from Plan

None - plan executed exactly as written. Task 1 (`type="tracer"`) was followed by the tracer
feedback gate per the executor protocol: `workflow.human_verify_mode = end-of-phase` (config
default) and Task 1's `<verify>` carries only `<automated>` content (no `<human-check>`), so the
gate's row 3 applies — re-run the tracer's `<verify>` end-to-end (done, both pre- and post-commit,
both `ALL PASSED`) and continue to Tasks 2/3 without synthesizing a checkpoint. No architectural
changes, no missing critical functionality discovered, no blocking issues encountered.

## Issues Encountered

None. The worktree's fresh `uv sync` resolved a uv-managed CPython 3.14 interpreter rather than
the main checkout's nix-provided 3.13.13 (expected per CLAUDE.md § "NixOS development shell" —
"Interpreters may differ"); recorded as `PYVENV_VERSION_INFO = 3.14` in `75-CLOSEOUT-GUARD.md` for
the record, no functional impact on this plan's read-only evidence gathering.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `75-CLOSEOUT-GUARD.md`'s baseline is ready for 75-07's phase-close re-verification and the
  operator's post-`phase.complete` third observation.
- `75-BASE-EVIDENCE.md`'s zero-warning ledger is ready for 75-04 to compare the bumped tip's docs
  build against (SC4).
- `75-SC5-INVARIANTS.md`'s observation 1 is ready for 75-07 to pair with observation 2 after the
  bump, trial merge and CI dispatch waves.
- No blockers. `.planning/REQUIREMENTS.md` is untouched (byte-identical to `PHASE_BASE_SHA`); no
  tag, PyPI upload, GitHub Release, PR, or `update-pin.yml` dispatch occurred; nothing under
  `typsphinx/` changed.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `test -f .planning/phases/75-v0-9-6-release-prep-prep-only/75-CLOSEOUT-GUARD.md` -> FOUND
- `test -f .planning/phases/75-v0-9-6-release-prep-prep-only/75-BASE-EVIDENCE.md` -> FOUND
- `test -f .planning/phases/75-v0-9-6-release-prep-prep-only/75-SC5-INVARIANTS.md` -> FOUND
- `git log --oneline --all | grep -q 6dbe7024` -> FOUND
- `git log --oneline --all | grep -q 479978cd` -> FOUND
- `git log --oneline --all | grep -q a1c2969b` -> FOUND
- All three tasks' `<acceptance_criteria>` and `<verify><automated>` shell assertions re-run
  post-commit, all `ALL PASSED`.
- Plan-level `<verification>` re-checked: `.planning/REQUIREMENTS.md` byte-identical to
  `PHASE_BASE_SHA` (`git diff --name-only` empty), no product-tree file outside `.planning/`
  changed since `PHASE_BASE_SHA`, working tree clean (`git status --porcelain` empty).
