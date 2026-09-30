---
phase: 44-typst-documents-default-derivation-builder-input-hardening
plan: 04
subsystem: testing
tags: [pytest, sphinx, typst, audit, ci, traceability]

# Dependency graph
requires:
  - phase: 44-01
    provides: "_default_typst_documents(config) + its callable-default registration; the RED commit SHA this plan's PHASE_BASE resolution is anchored to"
  - phase: 44-02
    provides: "the isinstance(docname, str) guard + reworded D-03 opt-out warning, both re-run as part of this plan's full-suite gate"
provides:
  - "44-GATE-EVIDENCE-04.md — the re-measured repo-wide conf.py census (107 files, up from 103 pre-phase), the corrected temp_sphinx_app blast-radius grep (adding write_doc(), the pattern 44-RESEARCH.md's own grep omitted), a per-file CHANGED/VERIFIED-NO-CHANGE verdict table with proof for every row, the phase's complete file inventory mapped to CONF-08/BLD-01, and the full suite + lint/type + manifest phase gate"
  - "Reconciliation of the wave-1 finding: tests/test_builder_requirement13.py's miss is explained (inline multifile_srcdir fixture, invisible to a temp_sphinx_app-only search) and the broader inline-conf.py-fixture sweep this implies was run, surfacing and clearing two more instances of the same fixture class"
  - "SC#1-SC#5 verdict table with evidence-file citations; SC#4 explicitly recorded NOT-MET (44-GATE-EVIDENCE-03.md not visible from this worktree) rather than assumed"
  - "Two findings recorded (not fixed, out of this plan's scope) in the broken-windows ledger: BLD-01 still Pending in REQUIREMENTS.md despite being implemented+evidenced, and SC#4's cross-worktree visibility gap"
affects: [45-documentation-currency, 46-release-prep]

# Actuals (#2632)
actuals:
  tokens: 8585
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Repo-wide fixture census must search BOTH tests/conftest.py's named temp_sphinx_app fixture AND inline write_text(...conf.py...)-style fixtures separately -- the two are structurally invisible to each other's grep."

key-files:
  created:
    - .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-04.md
    - .planning/WINDOWS.md
  modified: []

key-decisions:
  - "SC#4 recorded NOT-MET rather than assumed MET: 44-GATE-EVIDENCE-03.md (plan 44-03's own output) does not exist in this worktree's tree at HEAD, because 44-03 is a concurrent sibling executing in its own worktree in the same wave. Honest-verifier principle applied -- abstain to NOT-MET rather than assert a truth without direct evidence in this tree."
  - "The census methodology gap the wave-1 finding pointed at was closed, not just acknowledged: a broader grep for inline conf.py-writing test modules (not just temp_sphinx_app references) was run, and every module it surfaced was individually checked and proven unaffected or already accounted for."

requirements-completed: []

coverage:
  - id: D1
    description: "Every existing test that encoded the old []-default is accounted for by name with a CHANGED or VERIFIED-NO-CHANGE verdict and its own proof, including the write_doc( pattern the research pass's blast-radius grep omitted and the wave-1-discovered tests/test_builder_requirement13.py"
    requirement: "CONF-08"
    verification:
      - kind: other
        ref: "44-GATE-EVIDENCE-04.md §§1-3 (repo-wide census, corrected blast-radius grep, 11-row per-file verdict table: 2 CHANGED, 9 VERIFIED-NO-CHANGE)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The phase's complete added/changed file inventory is mapped to CONF-08/BLD-01, with the PHASE_BASE resolution and its own scope check recorded"
    verification:
      - kind: other
        ref: "44-GATE-EVIDENCE-04.md §4 (PHASE_BASE = 8bb43d18, 21-row file inventory, every row mapped)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The full suite, the full-corpus -b typstpdf gate (proven selected by node id), black, ruff, and mypy are all green and recorded"
    requirement: "CONF-08"
    verification:
      - kind: unit
        ref: "44-GATE-EVIDENCE-04.md §§5-6 (855 passed/1 skipped; test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error passed; black/ruff/mypy all exit 0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The zero-new-runtime-dependency invariant is measured (empty pyproject.toml/uv.lock diff) and every ROADMAP SC is mapped to MET/NOT-MET evidence rather than assumed"
    verification:
      - kind: other
        ref: "44-GATE-EVIDENCE-04.md §7 (manifests + SC#1-SC#5 verdict table)"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-08-04
status: complete
---

# Phase 44 Plan 04: SC#5 Repo-Wide Test Audit + Phase Gate Summary

**Re-measured 107-file `conf.py` census and a corrected `temp_sphinx_app` blast-radius grep (adding the `write_doc(` pattern the research pass's own grep omitted) produce an 11-row per-file CHANGED/VERIFIED-NO-CHANGE verdict table with proof for every row, closing SC#5's traceability half; the full suite (855 passed, 1 skipped), the full-corpus gate, and `black`/`ruff`/`mypy` are all recorded green, closing its gate half — with SC#4 honestly recorded NOT-MET because plan 44-03's evidence file is not visible from this concurrent worktree.**

## Performance

- **Duration:** ~20 min (worktree provisioning + census + suite run + evidence writing)
- **Started:** 2026-08-04 (session start, worktree provisioning)
- **Completed:** 2026-08-04T05:59:42Z
- **Tasks:** 2 (both completed)
- **Files modified:** 2 (both created: the evidence file and the broken-windows ledger)

## Accomplishments
- Re-ran the repo-wide `conf.py` census live: **107** files mention `typst_documents` (not the planning-time **103** — the +4 delta is fully accounted for as this phase's own four new fixtures), with a column-0 assignment check isolating the one deliberate exception (`default_typst_documents_gate/conf.py`) and naming the second intentional exception (`empty_typst_documents_optout_gate/conf.py`) by name, per the plan's action block.
- Re-ran the `temp_sphinx_app` blast-radius grep with the corrected pattern set (`app.build(`, `.translate()`, `builder.write(`, and — the pattern `44-RESEARCH.md`'s own grep omitted — `write_doc(`), confirming by direct re-measurement that adding `write_doc(` is what surfaces `tests/test_builder.py` as the sole affected module among the ten `temp_sphinx_app`-referencing files.
- Reconciled the wave-1 finding rather than merely restating it: explained *why* `tests/test_builder_requirement13.py` was invisible to a `temp_sphinx_app`-only grep (it uses its own inline `multifile_srcdir` fixture), then closed the resulting methodology gap by running a broader sweep for every inline-`conf.py`-writing test module in the repo — surfacing two more instances of the same fixture class (`test_config_template_mapping.py::test_default_typst_template_mapping`, `test_config_other_options.py`), individually checked and proven unaffected.
- Produced an 11-row per-file verdict table (2 `CHANGED`, 9 `VERIFIED-NO-CHANGE`, including the explicitly required `tests/test_config.py` row), every row backed by a real command output from this session — not a restated claim.
- Resolved `PHASE_BASE` as the RED commit's parent (`8bb43d181f95c5c807613bae99f22fe00ea963a0`), verified its own commit subject carries no `44-` scope, and produced a 21-row phase file inventory mapped to `CONF-08`/`BLD-01` with zero unmapped rows.
- Recorded a full green phase gate: `855 passed, 1 skipped` (matching the orchestrator's own reference measurement on the same base commit exactly, no divergence), the full-corpus `-b typstpdf` gate proven selected by node id, `tests/test_preview_version_sync.py` green, and `black`/`ruff`/`mypy` all exit 0 — including an explicit confirmation that `typsphinx/builder.py`'s typing import line is untouched by this phase's diff (`UP006`/`UP035` still ignored per `CLAUDE.md`'s standing prohibition).
- Closed with an SC#1-SC#5 verdict table citing the evidence file/section for each: SC#1/SC#2/SC#3/SC#5 **MET**; SC#4 recorded **NOT-MET** on the honest-verifier principle, because `44-GATE-EVIDENCE-03.md` (plan 44-03's own output) does not exist in this worktree's tree — 44-03 is a concurrent sibling in the same wave, and this plan does not assume its result by proxy.
- Recorded both real, unfixed findings this audit surfaced (BLD-01 still `Pending` in `REQUIREMENTS.md`; SC#4's cross-worktree visibility gap) in `.planning/WINDOWS.md`, the broken-windows ledger, so they stay visible past this SUMMARY rather than being fixed silently or dropped.

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-measure the repo-wide test audit and record a verdict for every affected file** - `5dec449` (docs)
2. **Task 2: Run and record the phase gate — full suite, corpus gate, lint, types, manifests** - `cd1f267` (docs)

**Plan metadata:** _final metadata commit is the orchestrator's responsibility in worktree mode; not made by this executor._

## Files Created/Modified
- `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-04.md` - Sections 1-4 (census, corrected blast-radius grep, per-file verdict table, phase file inventory) written in Task 1; sections 5-7 (full suite, lint/types, manifests + SC#1-SC#5 verdict) appended in Task 2
- `.planning/WINDOWS.md` - Two entries appended to the broken-windows ledger via `gsd-tools windows append`: the SC#4 cross-worktree visibility gap (`unmet-truth`) and the BLD-01 `REQUIREMENTS.md` tracking gap (`deviation`) — neither fixed by this plan, both recorded so a later phase or the ship gate does not miss them

## Decisions Made
- SC#4 recorded `NOT-MET` rather than `MET` by inference from 44-03's SUMMARY frontmatter (which this worktree cannot see either, since 44-03 has not merged yet) — the plan's own instruction is explicit that "a criterion this plan cannot see the evidence for is NOT-MET with the reason stated, never MET by assumption," and this was honored even though it is very likely 44-03 succeeded.
- Treated the wave-1 reconciliation instruction as a mandate to fix the census *methodology*, not just re-state the one file it named: ran a repo-wide sweep for inline-`conf.py`-writing fixtures (a structurally distinct surface from `tests/conftest.py`'s named `temp_sphinx_app` fixture) and individually verified every module it surfaced, rather than treating `tests/test_builder_requirement13.py` as a one-off already closed by wave 1.

## Deviations from Plan

None — plan executed exactly as written. No production code, no test file, and no `.planning/` file outside this plan's declared `files_modified` scope (`44-GATE-EVIDENCE-04.md`) was touched, other than the broken-windows ledger append, which is a standing part of the `execute-plan.md` workflow's `summary_creation` step (not a plan-scope violation) and is itself the mechanism by which this plan's two findings stay visible without being silently fixed out-of-scope.

## Issues Encountered
None. All tests passed on first run; `black`/`ruff`/`mypy` were clean on first run (no formatting or lint drift picked up from waves 1/2's own work).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- SC#5 (traceability + gate) is discharged for CONF-08/BLD-01's shipped surface: every test that could have encoded the old `[]`-default carries a recorded, proven verdict, and the full suite + lint/type trio + full-corpus gate are all green.
- **SC#4 is not yet closed from this worktree's point of view.** Once plan 44-03's worktree merges and `44-GATE-EVIDENCE-03.md` becomes visible, the orchestrator (or a follow-up read) should re-check its content against this file's SC#4 row and flip it to `MET` if 44-03's own evidence supports it — this plan deliberately does not assume that outcome.
- **Two open broken-windows ledger entries** carry forward: (1) `BLD-01` needs its `REQUIREMENTS.md` checkbox/table row flipped to `Complete` — the code and tests are done, only the tracking artifact lags; (2) the SC#4 cross-worktree visibility gap above. Neither blocks Phase 44's own close if 44-03 in fact succeeded (which is expected), but both should be swept before `/gsd-ship` per the standing broken-windows gate.
- No blockers to Phase 44.1/45/46 from this plan's own surface.

---
*Phase: 44-typst-documents-default-derivation-builder-input-hardening*
*Completed: 2026-08-04*

## Self-Check: PASSED

`.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-04.md`
confirmed present on disk (551 lines across both task commits). `.planning/WINDOWS.md`
confirmed present on disk (2 open entries). Both commits (`5dec449`, `cd1f267`)
confirmed present in `git log --oneline`. No missing items.
