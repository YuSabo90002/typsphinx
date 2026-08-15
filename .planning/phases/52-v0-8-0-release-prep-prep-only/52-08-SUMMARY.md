---
phase: 52-v0-8-0-release-prep-prep-only
plan: 08
subsystem: testing
tags: [pytest, locale, ruff, ci, windows, ntpath, sphinx]

# Dependency graph
requires:
  - phase: 52-04
    provides: the RED CI authority run (31855486993) that root-caused defects A/B/C and stopped at
      its declared one-file scope
provides:
  - "Locale-independent TestNoLostDiagnostics warning-baseline anchoring (defect A fixed)"
  - "repr()-correct rehome-warning assertion in test_builder.py (defect B fixed, verified on
     Python 3.12 windows-latest; still red on 3.13 for an unrelated, newly-discovered reason)"
  - "Sorted import block in test_builder.py resolving ruff I001 (defect C fixed, CI-confirmed)"
  - "Second CI run (31856929828) appended to 52-CI-EVIDENCE.md alongside the first, unmodified"
  - "A fourth, previously-unknown defect (WINDOWS.md id 6): Python 3.13's ntpath.isabs() no longer
     reports a driveless-absolute Windows path as absolute, so
     TypstBuilder._track_image()'s rehome branch is skipped entirely on
     Test Python 3.13 on windows-latest"
affects: [52-ship, release-prep, ci-authority]

# Actuals (#2632)
actuals:
  tokens: 5650
  tasks: 4
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Locale-invariant assertion anchoring: reduce a captured, translated warning string to its
       untranslated file:line/tag anchors instead of asserting the full localized message"

key-files:
  created: []
  modified:
    - tests/test_state_guard_shapes_gate.py
    - tests/test_builder.py
    - .planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md
    - .planning/WINDOWS.md

key-decisions:
  - "Task 4 step 3's own instruction ('if any job still fails, record it honestly and STOP with a
     checkpoint rather than iterating silently') was followed literally when an 11th-hour,
     previously-unmeasured fourth defect surfaced on Test Python 3.13 on windows-latest -- no
     blind fourth fix was attempted, and the ledger was NOT closed"
  - "Ledger entry 3 (Windows backslash-doubling) was left open rather than marked fixed, even
     though the specific assertion it names now passes on the 3.12 lane, because the SAME test on
     the SAME lane class is still red for a different reason -- closing it would misrepresent the
     ledger"

requirements-completed: []

coverage:
  - id: D1
    description: "TestNoLostDiagnostics warning baselines pass under both LC_ALL=C and the
      default (Japanese) locale, via locale-invariant anchors instead of full localized strings"
    requirement: REL-07
    verification:
      - kind: unit
        ref: "tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved -- 7 passed under LC_ALL=C, 7 passed under default locale"
        status: pass
    human_judgment: false
  - id: D2
    description: "Rehome-warning assertion in test_builder.py corrected to match the product's
      deliberate repr() formatting instead of the raw path"
    requirement: REL-07
    verification:
      - kind: unit
        ref: "tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -- 1 passed locally (POSIX); Test Python 3.12 on windows-latest CI run 31856929828 success"
        status: pass
    human_judgment: false
  - id: D3
    description: "Import block sort fixing ruff I001 in test_builder.py"
    requirement: REL-07
    verification:
      - kind: other
        ref: "CI run 31856929828, job 'Lint and Format Check' -- success (cannot run ruff locally, NixOS)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Second CI authority run dispatched and recorded, all 12 jobs green"
    requirement: REL-07
    verification: []
    human_judgment: true
    rationale: "NOT achieved -- 11 of 12 jobs succeeded; Test Python 3.13 on windows-latest failed
      on a newly-discovered, unfixed fourth defect. Requires an owner decision on disposition
      before a third CI run can be attempted; not something this plan's own gates can auto-pass."

# Metrics
duration: 21min
completed: 2026-08-15
status: blocked
---

# Phase 52 Plan 08: Fix Three CI-Found Defects and Re-Prove Green — Summary

**Three of three declared defects fixed and CI-confirmed (11/12 jobs green); a fourth, previously-unknown Python-3.13-on-Windows defect surfaced and blocks full green — plan stops at a checkpoint per its own instruction rather than attempting a blind fourth fix.**

## Performance

- **Duration:** 21 min
- **Started:** 2026-08-15T01:26:15Z (base commit `9cfd6402`)
- **Completed:** 2026-08-15T01:46:57Z (this summary)
- **Tasks:** 4 of 4 attempted; 3 fully successful, Task 4 partially successful (push/dispatch/record
  done, ledger-close NOT done)
- **Files modified:** 4

## Accomplishments

- Defect A (locale-dependent warning baseline in `TestNoLostDiagnostics`) fixed with a real local
  RED (`2 failed, 5 passed` under `LC_ALL=C LANG=C LANGUAGE=C`) proven against the unmodified tree,
  then GREEN under both `LC_ALL=C` and the machine's default Japanese locale (`7 passed` each) after
  reducing baseline comparisons to locale-invariant anchors (the untranslated `file:line: WARNING:`
  prefix and the untranslated bracketed diagnostic tag) instead of the full localized message.
- Defect B (naive `repr()`-unaware assertion in `test_post_process_images_rehome_escape_relocates_with_warning`)
  fixed by asserting `repr(abs_uri) in message` instead of the raw path — matches the product's
  deliberate `!r` formatting on both POSIX and Windows. CI-confirmed on `Test Python 3.12 on
  windows-latest` (full pass, was previously one of that lane's three failures).
- Defect C (`ruff I001` unsorted import block) fixed blind — cannot run `ruff` on this machine
  (NixOS ELF issue) — by reordering the local import block to match the third-party-then-first-party,
  straight-import-before-from-import convention already used elsewhere in this codebase
  (`tests/test_whole_document_xref_unit.py:47-55`). CI-confirmed: `Lint and Format Check` job is now
  `success` (was the sole failure driver for that job).
- Pushed the four fix commits as a plain fast-forward (`aaeec804..21eb4398`) to
  `origin/gsd/v0.8.0-multi-master-composition` and dispatched a second `ci.yml` `workflow_dispatch`
  run (id `31856929828`).
- **11 of 12 jobs report `success`**: `Build Package`, `Code Coverage`, both `Integration Test`
  jobs, `Lint and Format Check`, all four non-Windows test-matrix lanes, `Test Python 3.12 on
  windows-latest`, and `Type Check`.
- Appended a full second section to `52-CI-EVIDENCE.md` — the first (red) run's section is
  untouched, verbatim.
- **NEW finding, not fixed:** `Test Python 3.13 on windows-latest` still fails, but on a different,
  earlier assertion (`test_builder.py:547`, `img["uri"]` completely unrewritten) than the one this
  plan's Task 2 fixed. Confirmed by direct log comparison this is NOT defect B recurring — the
  first run's Windows failure for this same test was one assertion later (line 555), proving
  `img["uri"]` had been correctly rewritten in the first run. Confirmed Python-3.13-specific by
  comparing against the passing `Test Python 3.12 on windows-latest` sibling job on the identical
  commit and OS. Read (not independently executed — cannot reproduce `ntpath` behavior on this
  POSIX host) as a Python 3.13 stdlib change to `ntpath.isabs()`, which now requires a drive
  letter/UNC prefix for a Windows path to count as absolute — the test fixture's driveless
  `os.path.join(os.sep, "typsphinx_test_50_03_escape_root", "chart.png")` no longer satisfies
  `path.isabs()` under CPython 3.13.15, so `TypstBuilder._track_image()`'s entire rehome/warn
  branch (`typsphinx/builder.py`) is skipped.
- Filed as `.planning/WINDOWS.md` entry 6 (`open_count` now `4`, was `3`) rather than closing
  entries 3/4/5 blind. Entries 4 (locale) and 5 (`ruff I001`) are conclusively discharged by this
  run's own evidence, but entry 3 (Windows backslash-doubling) names the same lane class
  (`Test Python 3.X on windows-latest`) that is still red — for a different reason than entry 3's
  own description — so closing it now would misrepresent the ledger. Left `open` pending the
  owner's decision on the new finding.

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix defect A (locale-dependent baseline), proven by a local RED → GREEN** -
   `c0df09a6` (fix)
2. **Task 2: Fix defect B (repr escaping) without touching the product** - `681e15ed` (fix)
3. **Task 3: Fix defect C (ruff I001) blind, and re-run the full suite** - `21eb4398` (fix)
4. **Task 4: Re-push, re-dispatch, record both runs** - `f525414d` (docs) — **partially complete**:
   push and dispatch and evidence-recording done; ledger-close (step 4) NOT done because CI did not
   come back fully green (step 3's own stop condition fired).

**Plan metadata:** this SUMMARY's own commit (below) — no separate `docs: complete plan` commit,
since the plan's declared success criteria are not fully met (see Deviations).

## Files Created/Modified

- `tests/test_state_guard_shapes_gate.py` - Locale-invariant anchor extraction for
  `TestNoLostDiagnostics`'s warning-baseline comparison
- `tests/test_builder.py` - `repr()`-correct rehome-warning assertion; sorted import block
  (`ruff I001` fix)
- `.planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md` - Second CI run section
  appended, first run's section untouched
- `.planning/WINDOWS.md` - New entry 6 filed for the fourth, unfixed defect; entries 3/4/5 left as
  recorded by the first run (NOT marked fixed)

## Decisions Made

- Followed Task 4 step 3's own explicit instruction to stop and record honestly rather than
  attempt a blind fourth fix when `Test Python 3.13 on windows-latest` failed on an assertion this
  plan did not anticipate or measure at planning time.
- Left ledger entries 3/4/5 untouched (not marked `fixed`) rather than closing the two that are
  individually discharged (4, 5) and reopening 3 under a new description — the ledger's `id 3`
  literally names the still-red lane class, and partial closure would misrepresent the state more
  than leaving all three as recorded by the first run.
- Filed the new defect with `--kind stub` (the closest available vocabulary term to hand at
  filing time); it is conceptually closer to `todo`, matching entries 3-5's classification. The
  `windows` CLI has no edit verb to reclassify after append — noted here for whoever picks this up,
  the `kind` field is cosmetic to the blocking behavior (`status: open` drives `open_count`), but
  worth correcting if the tool gains an edit path.

## Deviations from Plan

### Auto-fixed Issues

None — Tasks 1-3 were executed exactly as the plan specified, with the mechanism choices (locale-
invariant anchoring for defect A; `repr()`-aware assertion for defect B; import reordering matching
existing codebase convention for defect C) left to this executor's own judgment, as the plan
explicitly authorized ("Decide the mechanism yourself from the code").

### Plan-Level Deviation: Task 4 stopped short of its declared final state

**1. [Plan's own Task 4 step 3 instruction] New, unmeasured defect blocks the ledger close and
"all 12 jobs success" acceptance criterion**
- **Found during:** Task 4 (re-dispatch, watching the second CI run)
- **Issue:** The plan's `<context>` measured and named exactly three defects (A, B, C). All three
  are conclusively fixed and CI-confirmed. But the second run surfaced an 11/12 result, not 12/12
  — `Test Python 3.13 on windows-latest` fails on a DIFFERENT assertion than the one this plan's
  Task 2 addressed, for what reads as a fourth, previously-unknown Python-3.13-specific defect in
  `typsphinx/builder.py`'s absolute-path detection.
- **Action taken:** Recorded the full finding (log excerpts, cross-lane/cross-version comparison,
  root-cause hypothesis) honestly in `52-CI-EVIDENCE.md`'s second section. Filed
  `.planning/WINDOWS.md` entry 6. Did NOT attempt to fix it (would require either touching
  `typsphinx/builder.py`, which this plan's must_haves explicitly forbid, or widening the test
  fixture beyond what this plan measured/authorized at planning time — both are Rule 4
  architectural-scope questions this executor cannot decide unilaterally). Did NOT close ledger
  entries 3/4/5, since `open_count` returning to `0` is one of this plan's own must_haves and is
  not met.
- **Files modified:** `.planning/phases/52-v0-8-0-release-prep-prep-only/52-CI-EVIDENCE.md`,
  `.planning/WINDOWS.md`
- **Verification:** Direct log comparison (`gh run view --job <id> --log-failed`) between the
  first run's Windows failures, this run's `Test Python 3.13 on windows-latest` failure, and the
  passing `Test Python 3.12 on windows-latest` sibling job — see `52-CI-EVIDENCE.md`'s "NEW
  finding" subsection for the full evidence chain.
- **Committed in:** `f525414d`

---

**Total deviations:** 1 (plan-level, not a Rule 1/2/3 auto-fix — a newly-discovered defect outside
this plan's declared scope, handled per the plan's own explicit stop-and-record instruction)
**Impact on plan:** This plan's must_haves are **NOT** fully met: `open_count` is `4`, not `0`, and
the second CI run reports `11/12`, not `12/12`. Three of the four must_haves that are within this
plan's control (locale RED→GREEN proof, repr-escaping fix without touching product code, ruff
import-sort fix) ARE met. The two must_haves that depend on full green (`all 12 jobs report
success`, `open_count returns to 0`) are NOT met, pending an owner decision on the newly-discovered
fourth defect.

## Issues Encountered

See "Deviations from Plan" above — the one substantive issue encountered (the fourth defect) is
documented there in full, since it is simultaneously a deviation and the reason this plan stops
short of its declared final state.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**NOT ready for `/gsd-ship`.** `.planning/WINDOWS.md` `open_count` is `4` (was `3` before this
plan; two of the three original entries are individually discharged by evidence but were left
`open` rather than closed, per the Decisions section above, and one new entry was filed).

**Owner decision needed** before any further CI dispatch is attempted: how to resolve the newly-
found Python 3.13 / Windows `ntpath.isabs()` gap in `TypstBuilder._track_image()` (product-side
fix, outside this phase's zero-`typsphinx/`-lines fence) versus fixing the test fixture to
construct a genuinely drive-absolute Windows path (test-side, would stay within a
`tests/test_builder.py`-scoped follow-up plan). See `52-CI-EVIDENCE.md`'s "Escalation" subsection
under the second run's section for the full framing.

Once resolved and a THIRD CI run reports `12/12`, the remaining work is exactly what this plan's
Task 4 step 4 already specifies: `gsd-tools windows fixed 3`, `4`, `5` (and whatever id the new
finding's fix lands on), confirming `open_count` returns to `0`.

---
*Phase: 52-v0-8-0-release-prep-prep-only*
*Completed: 2026-08-15*

## Self-Check: PASSED

- FOUND: .planning/phases/52-v0-8-0-release-prep-prep-only/52-08-SUMMARY.md
- FOUND commits: c0df09a6, 681e15ed, 21eb4398, f525414d, 346b84c9
