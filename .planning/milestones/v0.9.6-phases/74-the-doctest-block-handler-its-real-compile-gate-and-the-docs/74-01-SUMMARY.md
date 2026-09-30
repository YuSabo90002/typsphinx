---
phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs
plan: 01
subsystem: docs-evidence
tags: [sphinx, docutils, qua-14, doctest_block, evidence, ci]

# Dependency graph
requires: []
provides:
  - PHASE_BASE_SHA (8ea10273265e3966b6e650bad43cf90c9598ed65), proven product-tree-identical to the
    milestone base 6cc44f22 outside .planning/
  - the clean C-locale base -b typst build of docs/source, with BASE_WARNING_COUNT=5 and
    BASE_DOCTEST_UNKNOWN_COUNT=2 as SC1's positive controls
  - the verbatim api/index.typ collapsed example region (compute_content_include_path at :811,
    compute_template_import_path at :867)
  - the QUA-14 whole-log census (raw + attributed + probe-attributed) and its derived FIX_LIST
  - the phase-head remote reads 74-07 compares at phase close (required status checks, branch
    census, reference CI job set)
affects: [74-03, 74-04, 74-05, 74-06, 74-07]

actuals:
  tokens: 4420
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "napoleon-plus-docutils scratch probe (never committed) to attribute unattributed
      docutils system-message census lines to a named docstring by (line, message class)"

key-files:
  created:
    - .planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-BASE-EVIDENCE.md
  modified: []

key-decisions:
  - "Base build confirms planning-time measurement exactly: build succeeded, 5 warnings; 2
    doctest_block unknown-node warnings; 0 terms.item calls in api/index.typ (D-06 amendment
    holds)."
  - "QUA-14 raw census is 10 lines (6 Unexpected indentation + 4 Block quote ends), only 3
    attributed by file:line; the docstring probe attributes all 7 remaining terse lines to two
    docstrings: typsphinx.pathfmt.quote_path and typsphinx.translator.TypstTranslator.visit_toctree
    (BASE_UNATTRIBUTED_UNMATCHED=0)."
  - "FIX_LIST = typsphinx.pathfmt.quote_path|typsphinx.translator.TypstTranslator.visit_toctree
    (D-07) — quote_path is included solely because the probe attributes lines to it, not because
    the build log names it with a file:line attribution."
  - "No probe-only rows: every docstring the probe flags corresponds to a line the build log
    already reported. No other typsphinx docstring raises either QUA-14 message class."

patterns-established:
  - "Evidence file KEY = value convention with a top-of-file key block plus section-by-section
    narrative and verbatim transcripts, verified programmatically with a `sed -n 's/^KEY = //p'`
    reader function."

requirements-completed: [TRN-01, QUA-14]

coverage:
  - id: D1
    description: "PHASE_BASE_SHA recorded before any commit; product tree outside .planning/ proven
      identical to the milestone base 6cc44f22"
    requirement: TRN-01
    verification:
      - kind: other
        ref: "74-BASE-EVIDENCE.md Task 1 verify block (automated, re-run before commit)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Clean C-locale base -b typst build recorded with SC1's three base facts: build
      succeeded/N warnings line, doctest_block unknown-node count, verbatim api/index.typ example
      region"
    requirement: TRN-01
    verification:
      - kind: other
        ref: "74-BASE-EVIDENCE.md Task 1 verify block (automated)"
        status: pass
    human_judgment: false
  - id: D3
    description: "QUA-14 whole-log census (raw + attributed), every unattributed line matched to a
      named docstring via a scratch napoleon-plus-docutils probe, FIX_LIST derived"
    requirement: QUA-14
    verification:
      - kind: other
        ref: "74-BASE-EVIDENCE.md Task 2 verify block (automated)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Phase-head remote reads recorded for 74-07: required status checks, branch
      census, origin main head, reference CI job set"
    verification:
      - kind: other
        ref: "74-BASE-EVIDENCE.md Task 3 verify block (automated)"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-19
status: complete
---

# Phase 74 Plan 01: Base Evidence Summary

**PHASE_BASE_SHA=8ea10273, base `-b typst` build (5 warnings, 2 doctest_block unknown-node
warnings, both positive controls), and the QUA-14 whole-log census with FIX_LIST =
`typsphinx.pathfmt.quote_path|typsphinx.translator.TypstTranslator.visit_toctree`.**

## Key Facts

- `PHASE_BASE_SHA` = `8ea10273265e3966b6e650bad43cf90c9598ed65`
- `BASE_WARNING_COUNT` = `5`
- `BASE_DOCTEST_UNKNOWN_COUNT` = `2`
- `BASE_RAW_TOTAL` = `10`
- `BASE_ATTRIBUTED_COUNT` = `3`
- `FIX_LIST` = `typsphinx.pathfmt.quote_path|typsphinx.translator.TypstTranslator.visit_toctree`
- Probe-only rows (docstrings the probe flags but the build log never reported): **none**.

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-19T22:04:18Z
- **Completed:** 2026-09-19T22:12:13Z
- **Tasks:** 3
- **Files modified:** 1 (`74-BASE-EVIDENCE.md`, built incrementally across all three tasks)

## Accomplishments
- Recorded `PHASE_BASE_SHA` before any commit, and proved its product tree outside `.planning/`
  equals the milestone base `6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b` byte-for-byte
  (`git diff --name-only` empty).
- Ran a clean `LANG=C LC_ALL=C -b typst` build of `docs/source` from a fresh worktree venv
  provisioned with `--extra dev --extra docs --python 3.13.13`: `build succeeded, 5 warnings.`,
  exactly matching the roadmap's 2026-09-16 context measurement and the plan's own planning-time
  table. Both doctest_block unknown-node warnings and the collapsed `api/index.typ` example region
  (`compute_content_include_path` at `:811`, `compute_template_import_path` at `:867`) are
  transcribed verbatim as SC1's positive controls.
- Produced the QUA-14 whole-log census over the entire base build output (constraint 6, not
  narrowed to `visit_toctree`): 10 raw lines (6 `Unexpected indentation` + 4 `Block quote ends`),
  only 3 carrying `file:line` attribution (all `visit_toctree`). Wrote and ran a scratch
  napoleon-plus-docutils probe over every typsphinx-defined function/class/method, which attributed
  the remaining 7 unattributed lines to `typsphinx.pathfmt.quote_path` (19 ERROR, 21 WARNING) and
  `typsphinx.translator.TypstTranslator.visit_toctree` (5 ERROR, 6 WARNING, 21 ERROR) —
  `BASE_UNATTRIBUTED_UNMATCHED = 0`. Derived `FIX_LIST` (D-07) including `quote_path` even though
  the build log itself never attributes a `file:line` to it.
- Recorded the phase-head remote reads 74-07 will compare at phase close: `main`'s required status
  checks (strict=true, 6 sorted contexts), the `gsd/*` branch census (no local
  `gsd/v0.9.6-milestone` decoy, no `gsd/v0.9.6*` branch on origin yet), `origin/main` still at the
  milestone base (`MAIN_MOVED=no`), and the reference CI run `35083828156`'s 12-job sorted name set
  from `73-CI-EVIDENCE.md`, with `ci.yml` confirmed unchanged since the milestone base.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer: head check, PHASE_BASE_SHA, and the clean base -b typst build with SC1's base
   records** - `b7d45677` (docs)
2. **Task 2: QUA-14 census over the whole base log (raw and attributed, D-07), attribution of
   every unattributed line, and FIX_LIST** - `9d56a4b5` (docs)
3. **Task 3: Phase-head remote reads: required status checks, branch census, origin main, and the
   reference CI job set** - `2fc82d2b` (docs)

_Note: this plan does not use TDD; all three commits are `docs({phase}-{plan})`, per
`<worktree_provisioning>`'s "Plain git commit" instruction — no GSD commit helper was used._

## Files Created/Modified
- `.planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-BASE-EVIDENCE.md` -
  the phase's base evidence record: head check/provisioning, base identity, the base `-b typst`
  build with its counted warnings, the doctest_block positive control, the `api/index.typ` example
  region, the QUA-14 census (raw/attributed/probe/attribution-table/fix-list), and the phase-head
  remote reads.

## Decisions Made
- Confirmed planning-time measurements hold exactly at execution time: `build succeeded, 5
  warnings.`, `BASE_DOCTEST_UNKNOWN_COUNT=2`, `BASE_API_TERMS_ITEM_COUNT=0` (D-06 amendment's
  falsified-claim-1 reading re-verified), and the expected `FIX_LIST` from the plan's own
  planning-time table matched byte-for-byte.
- No probe-only rows exist: the whole-tree docstring probe found no typsphinx docstring raising
  either QUA-14 message class beyond the two the build log's own census already surfaces
  (`quote_path`, `visit_toctree`). Nothing additional is flagged for the owner.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `74-BASE-EVIDENCE.md` is complete and committed with every key Task 2 (74-03), 74-04, 74-05,
  74-06 and 74-07 read back via `sed`: `PHASE_BASE_SHA`, `FIX_LIST`, `BASE_WARNING_COUNT`,
  `BASE_DOCTEST_UNKNOWN_COUNT`, `BASE_RAW_TOTAL`, `BASE_ATTRIBUTED_COUNT`,
  `REQUIRED_CONTEXTS_HEAD` and `REFERENCE_CI_RUN_ID` are all present and verified.
- No blockers. Ready for 74-02 (the RED-evidence GATE-01 fixtures) per the phase's binding
  ordering (base build first, RED before GREEN).

## Self-Check: PASSED

- `[ -f .planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs/74-BASE-EVIDENCE.md ]` → FOUND
- `git log --oneline --all --grep="74-01"` → 3 commits found (`b7d45677`, `9d56a4b5`, `2fc82d2b`)
- All three tasks' `<verify>` blocks re-run and passing (`ALL PASS` on each) immediately before
  this SUMMARY was written.
- Plan-level `<verification>` re-confirmed: `PHASE_BASE_SHA` recorded pre-commit and product-tree
  identical to `6cc44f22`; base build's positive controls both non-zero; `FIX_LIST` accounts for
  every raw census line (attributed 3 + unattributed 7 = raw total 10, unmatched 0); phase-head
  remote reads present under all three new section headings.

---
*Phase: 74-the-doctest-block-handler-its-real-compile-gate-and-the-docs*
*Completed: 2026-09-19*
