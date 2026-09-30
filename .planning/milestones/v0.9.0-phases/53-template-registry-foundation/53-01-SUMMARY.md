---
phase: 53-template-registry-foundation
plan: 01
subsystem: testing
tags: [sphinx, typst, typst-py, pypdf, evidence, byte-identity]

# Dependency graph
requires: []
provides:
  - "53-RED-EVIDENCE.md: pre-change commit SHA, per-file SHA-256 and PDF page counts across the four existing typst_template/typst_package/typst_template_function/nothing-set configuration shapes"
  - "53-RED-EVIDENCE.md: TPL-04's four-element-vs-fifth-element-\"typst\" equivalence baseline, compared tree-to-tree"
  - "Live-confirmed typst.compile() PDF-compile path is available in this worktree's sandbox as of 2026-08-15 (real .typ file path input, not a raw source string)"
affects: [53-05]

# Actuals (#2632)
actuals:
  tokens: 2855
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: ["one-off evidence artifact (D-12): measure-then-record, no new pytest gate"]

key-files:
  created:
    - .planning/phases/53-template-registry-foundation/53-RED-EVIDENCE.md
    - .planning/phases/53-template-registry-foundation/deferred-items.md
  modified: []

key-decisions:
  - "typst.compile()'s `input=` parameter requires a real file path, not inline Typst source content -- confirmed by reading typsphinx/pdf.py:143/185 after an initial probe attempt with a raw string failed with FileNotFoundError. Once corrected, the live PDF-compile path succeeds in this sandbox, confirming RESEARCH.md's Assumption A1 rather than falling back to the -b typst hash-only path."
  - "A pre-existing, out-of-scope test failure (7 tests in tests/test_state_guard_shapes_gate.py referencing a path the v0.8.0 milestone archival relocated) was logged to deferred-items.md and WINDOWS.md rather than auto-fixed, per the scope-boundary rule -- git merge-base --is-ancestor confirmed the archival commit (2ea4db0f) predates this plan's base commit (222e1b9b)."

requirements-completed: [TPL-03, TPL-04]

coverage:
  - id: D1
    description: "Pre-change baseline for all four existing configuration shapes (typst_template set / typst_package set alone / typst_template_function set alone / nothing set), each with a sorted .typ file list, SHA-256 per file, and a real PDF page count"
    requirement: TPL-03
    verification:
      - kind: other
        ref: "53-RED-EVIDENCE.md sections \"Shape A\"..\"Shape D\" -- measured via sphinx-build -b typstpdf against real fixtures, sha256sum, pypdf.PdfReader"
        status: pass
    human_judgment: false
  - id: D2
    description: "TPL-04's four-element-tuple-vs-explicit-fifth-element-\"typst\" equivalence baseline, compared tree-to-tree"
    requirement: TPL-04
    verification:
      - kind: other
        ref: "53-RED-EVIDENCE.md section \"TPL-04 equivalence (pre-change)\" -- two builds of params_exclusivity_gate/zero_params_default, SHA-256 diffed directly against each other"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-15
status: complete
---

# Phase 53 Plan 01: SC#2 Pre-Change Byte-Identity Evidence Summary

**Captured the pre-change byte-identity baseline for TPL-03/TPL-04 into `53-RED-EVIDENCE.md`: SHA-256 hashes and PDF page counts across all four existing `typst_documents` configuration shapes, plus a direct four-element-vs-fifth-element `"typst"` comparison, using real `sphinx-build -b typstpdf` runs against real fixtures — no code changed.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-15T07:54:00Z
- **Tasks:** 2/2
- **Files modified:** 2 (both new: `53-RED-EVIDENCE.md`, `deferred-items.md`)

## Accomplishments
- Live-probed `typst.compile()` and confirmed the real PDF-compile path is available in this
  worktree's sandbox today (RESEARCH.md Assumption A1 holds; documented the exact usage error
  that caused an initial false-negative reading of that same probe).
- Built all four existing configuration shapes — `typst_template` set (shape A), `typst_package`
  set alone (shape B), `typst_template_function` set alone (shape C), nothing set (shape D) —
  against real fixtures on disk (`tests/fixtures/documented_params_contract_gate`,
  `tests/fixtures/typst_lang_gate/package_no_lang`,
  `tests/fixtures/params_exclusivity_gate/zero_params_default`, `tests/roots/test-basic`), and
  recorded every emitted `.typ` file's SHA-256 plus each compiled PDF's page count.
- Captured TPL-04's own equivalence claim independently: built the same fixture twice (four-
  element tuple as authored, and with an explicit fifth `"typst"` element appended), and
  compared the two resulting `.typ` trees directly against each other — identical.
- Recorded the pre-change commit SHA (`222e1b9b81809ef31b06c897e6eae0efdadf2cf9`) via a live
  `git rev-parse HEAD`, per the plan's prohibition against copying SHAs from planning documents.

## Task Commits

Each task was committed atomically:

1. **Task 1: Probe the environment and capture the pre-change baseline for all four shapes** -
   `d02d6b29` (docs)
2. **Task 2: Capture the TPL-04 four-element-vs-fifth-element equivalence baseline** -
   `d972b467` (docs)

_No plan-metadata commit is included in this list — per the worktree-executor instructions, this
plan runs inside an isolated worktree; the orchestrator applies the final metadata commit after
merge._

## Files Created/Modified
- `.planning/phases/53-template-registry-foundation/53-RED-EVIDENCE.md` - the SC#2 pre-change
  evidence artifact: commit SHA, live `typst.compile()` probe result, four shapes' `.typ`
  inventories with SHA-256 and PDF page counts, and the TPL-04 tree-to-tree comparison.
- `.planning/phases/53-template-registry-foundation/deferred-items.md` - logs one out-of-scope,
  pre-existing test failure discovered during Task 2's verification run (see Deviations).

## Decisions Made
- Corrected an initial probe usage error (passing raw Typst source as `input=` instead of a
  file path) by reading `typsphinx/pdf.py`'s own call shape, rather than concluding the PDF
  path was unavailable and silently falling back to the `-b typst` hash-only procedure. This
  keeps the artifact's PDF-page-count evidence real rather than a needlessly weaker fallback.
- Logged the pre-existing `test_state_guard_shapes_gate.py` failures to `deferred-items.md` and
  the cross-phase `WINDOWS.md` ledger (`unrun-verify`, entry id 7) instead of fixing them in this
  plan — they are unrelated to Phase 53's scope (a `.planning/`-evidence-artifact plan touches no
  `typsphinx/` or `tests/` source) and their root cause (a milestone-archival path move,
  `2ea4db0f`) predates this plan's base commit.

## Deviations from Plan

### Auto-fixed Issues

None — no bug, missing-critical-functionality, or blocking issue was found in this plan's own
scope that required a Rule 1/2/3 fix.

### Noted, Not Auto-fixed (out of scope)

**1. [Scope boundary] Pre-existing `test_state_guard_shapes_gate.py` failures unrelated to this plan**
- **Found during:** Task 2 verification (`uv run pytest tests/ -q`)
- **Issue:** 7 parametrized tests in
  `tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved`
  fail with `FileNotFoundError` reading
  `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-SHAPES-RED-EVIDENCE.md`
  — a path the v0.8.0 milestone archival (`2ea4db0f`) moved to
  `.planning/milestones/v0.8.0-phases/49-.../49-SHAPES-RED-EVIDENCE.md`.
- **Confirmed pre-existing, not caused by this plan:** `git merge-base --is-ancestor 2ea4db0f
  222e1b9b81809ef31b06c897e6eae0efdadf2cf9` returns true — the archival commit is an ancestor of
  this plan's base commit, and this plan touches no `typsphinx/` or `tests/` source file.
- **Action taken:** logged to `deferred-items.md` and to `.planning/WINDOWS.md` (`unrun-verify`,
  entry id 7). Not fixed — out of this plan's scope per the executor's scope-boundary rule.
- **Effect on this plan's stated acceptance criterion:** the plan's own `<verification>` block
  states `uv run pytest tests/ -q` exits 0. It does not (7 failed / 1163 passed / 5 skipped) for
  the reason above, unrelated to any change this plan made. This is recorded here rather than
  silently claimed as met.

---

**Total deviations:** 0 auto-fixed; 1 out-of-scope defect logged and deferred.
**Impact on plan:** None on this plan's own deliverable (`53-RED-EVIDENCE.md` is complete and
accurate). The logged defect is a pre-existing gap in the standing regression net inherited from
the v0.8.0 milestone archival, tracked in `WINDOWS.md` for later resolution.

## Issues Encountered
An initial live probe of `typst.compile()` returned `FileNotFoundError` when passed a raw Typst
source string — resolved by reading `typsphinx/pdf.py`'s own call shape, which showed
`typst.compile()`'s `input=` parameter requires a file path. Not a defect in this plan's own
work; documented in `53-RED-EVIDENCE.md`'s environment note so a future reader does not
misread the same false negative as "PDF compilation unavailable" (RESEARCH.md Assumption A1).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
`53-RED-EVIDENCE.md`'s pre-change section is complete: measured commit SHA, four shapes' `.typ`
SHA-256 inventories and PDF page counts, and the TPL-04 tree-to-tree comparison. Plan 53-05 can
diff its post-change measurements against these recorded values without re-deriving anything.

One open item carried forward, tracked in `WINDOWS.md` (not blocking Phase 53): the 7
pre-existing `test_state_guard_shapes_gate.py` failures caused by the v0.8.0 milestone archival
path move remain unresolved and will continue to fail `uv run pytest tests/ -q` for any later
plan in this phase until a plan explicitly fixes the referenced path.

---
*Phase: 53-template-registry-foundation*
*Completed: 2026-08-15*

## Self-Check: PASSED

- FOUND: `.planning/phases/53-template-registry-foundation/53-RED-EVIDENCE.md`
- FOUND: `.planning/phases/53-template-registry-foundation/deferred-items.md`
- FOUND commit `d02d6b29` (Task 1)
- FOUND commit `d972b467` (Task 2)
