---
phase: 57-v0-9-0-release-prep-prep-only
plan: 07
subsystem: testing
tags: [pytest, pypdf, typst, release-prep, goal-claim-evidence]

# Dependency graph
requires:
  - phase: 57-01
    provides: the post-bump tree (typsphinx.__version__ == 0.9.0)
provides:
  - "57-GOAL-CLAIM-EVIDENCE.md: SC#3's multi-template goal-claim half, re-proven on the post-bump tree"
affects: [57-08, 57-09, complete-milestone]

actuals:
  tokens: 2574
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns: ["re-run an existing permanent gate as post-bump re-proof rather than authoring a new one (D-14)"]

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-GOAL-CLAIM-EVIDENCE.md
  modified: []

key-decisions:
  - "D-14 discharged by re-running tests/test_two_key_selection_gate.py rather than authoring a new gate; no test module, class, function or fixture was added or edited."
  - "The committed gate's assertion is a byte-inequality check only; a standalone pypdf page-geometry read-back (transcript, not a gate) closes the gap to SC#3's literal 'differently typeset' wording."

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "SC#3's multi-template goal claim re-proven on the post-bump tree: the existing permanent gate tests/test_two_key_selection_gate.py passes with zero skips, and a pypdf page-geometry read-back shows the report-keyed PDF (A4, 595.28x841.89pt) and memo-keyed PDF (US Letter, 612x792pt) differ in page geometry in the direction the fixture's two templates dictate."
    requirement: REL-08
    verification:
      - kind: unit
        ref: "tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate (6 tests, all passed, skipped=0)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-16
status: complete
---

# Phase 57 Plan 07: Goal-Claim Evidence Summary

**Re-ran the existing permanent multi-template gate (`tests/test_two_key_selection_gate.py`) on the post-bump 0.9.0 tree with zero skips, then closed the gap between its byte-inequality assertion and SC#3's "differently typeset" wording with a one-off `pypdf` page-geometry read-back showing report-keyed (A4) vs memo-keyed (US Letter) PDFs differ.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-16T16:18:00Z (approx)
- **Completed:** 2026-08-16T16:38:12Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments

- Confirmed `typsphinx.__version__ == "0.9.0"` and `typsphinx.__file__` resolves inside this worktree — verified this is a genuine post-bump re-proof, not an inherited pre-bump result.
- Re-ran `tests/test_two_key_selection_gate.py` (the existing permanent D-14 gate) on the post-bump tree: 6/6 passed, `skipped="0"`, `failures="0"`, `errors="0"` — the PDF-producing class is availability-gated and ran for real (`typst-py` importable in this worktree's provisioned `.venv`).
- Ran a standalone `sphinx-build -b typstpdf` over the same fixture and read back both produced PDFs' page-1 mediaboxes with `pypdf`: `master.pdf`/`manuals/guide.pdf` (report key) = 595.2756×841.8898pt (A4); `memos/memo.pdf` (memo key) = 612.0×792.0pt (US Letter) — confirmed different, matching the fixture templates' `paper: "a4"` / `paper: "us-letter"` declarations exactly.
- Captured the emitted `.typ` tree, showing `_template/report/` and `_template/memo/` bundle directories published under the output tree.
- Wrote `57-GOAL-CLAIM-EVIDENCE.md` recording all of the above, plus an honest statement of exactly what the committed gate's byte-inequality assertion does and does not prove.
- Confirmed `git diff --name-only -- typsphinx/ tests/` produced no output throughout — no test module, class, function or fixture was added or edited; D-14's re-run-not-reauthor discipline held.

## Task Commits

Task 1 (re-running the gate and measuring page geometry) produced no file changes of its own — it is a pure measurement/transcript-gathering step whose output feeds Task 2's write. Task 2's write was committed atomically:

1. **Task 1 + Task 2: Re-run gate, measure PDF geometry, write goal-claim evidence** - `7a5ee7e8` (docs)

**Plan metadata:** committed together with the evidence write above; no separate `docs({phase}-{plan}): complete plan` metadata commit was needed since this was the plan's only file.

## Files Created/Modified

- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-GOAL-CLAIM-EVIDENCE.md` - SC#3's multi-template goal-claim evidence: the claim, D-14's rationale, the post-bump gate re-run transcript, an honest account of what the byte-inequality assertion proves, the page-geometry measurement transcript, and division of authority against 57-CI-EVIDENCE.md / 57-GREEN-TREE-EVIDENCE.md.

## Decisions Made

- Followed D-14 exactly: no new gate authored. The plan's own read-first instructions and prohibitions were unambiguous on this, and were honored — `git diff --name-only -- tests/` stayed empty throughout.
- Read the two fixture templates' `paper:`/`set text(size: ...)` lines directly this session (lines 26 and 31 in both `_typst/report/base.typ` and `_typst/memo/base.typ`) rather than transcribing from `57-RESEARCH.md`, which cited slightly different line numbers (18-19) for the report template — an artifact of how that earlier research counted lines, not a discrepancy in file content. This plan's own direct read is authoritative per the plan's own prohibition against transcribing planning-document figures.

## Deviations from Plan

None - plan executed exactly as written. No auto-fixes were needed; nothing under `typsphinx/` or `tests/` required correction, and no architectural questions arose.

## Issues Encountered

None. The build, gate re-run, and geometry measurement all succeeded on the first attempt with no RED encountered.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

SC#3's multi-template goal-claim half is on disk as generated, post-bump evidence. The toolchain half of SC#3 (full pytest, black/ruff/mypy, docs tox environments, built-wheel content check) is carried separately by `57-CI-EVIDENCE.md` (57-05) and `57-GREEN-TREE-EVIDENCE.md` (57-06), both dispatched in the same wave. No blockers for Wave 3 (`57-08`, SC#4 sweep) or Wave 4 (`57-09`, handoff). `typsphinx/` and `tests/` remain untouched by this plan, so the tree's fence and green-bar status carried into this wave by 57-01/57-10 are unaffected.

## Self-Check: PASSED

- `FOUND: .planning/phases/57-v0-9-0-release-prep-prep-only/57-GOAL-CLAIM-EVIDENCE.md`
- `FOUND: .planning/phases/57-v0-9-0-release-prep-prep-only/57-07-SUMMARY.md`
- `FOUND: 7a5ee7e8` (evidence-file commit)

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-16*
