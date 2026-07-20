---
phase: 15-full-corpus-validation
plan: 02
subsystem: testing
tags: [pytest, sphinx, git-worktree, corpus-validation, xref, translator]

# Dependency graph
requires:
  - phase: 15-full-corpus-validation
    provides: "tests/test_corpus_gate.py scaffolding (corpus_doc_dir fixture, wire_typsphinx_into_corpus_conf, _run_corpus_sphinx_build) from Plan 01"
provides:
  - "count_empty_url_warnings(stderr_text) -- SC#3 empty-URL warning counter, unit-tested"
  - "checkout_pre_xref01_translator(repo_root, worktree_dir) -- isolated git-worktree helper that reproduces pre-XREF-01 depart_term behavior on top of current HEAD via a targeted in-worktree source patch"
  - "test_empty_url_before_after -- env-gated (TYPSPHINX_CORPUS_REPORT=1), @pytest.mark.slow SC#3 measurement function, both sides -b typst"
affects: [15-03 (consumes these helpers to populate 15-CORPUS-REPORT.md)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "git worktree + targeted in-place source patch (not a whole-commit checkout) to isolate a single historical code-behavior variable from an otherwise-evolved codebase"
    - "env-var gating (not a new pytest marker) to keep an expensive one-time measurement out of the routine slow suite while remaining git-tracked and reproducible"

key-files:
  created: []
  modified:
    - tests/test_corpus_gate.py

key-decisions:
  - "METHODOLOGY ADJUSTMENT (deviation, see below): the 'before' translator is HEAD with only depart_term's XREF-01 label-anchor block disabled via a worktree-at-HEAD + in-place patch, NOT a checkout of 79c9d45~1 -- isolates the XREF-01 variable from 55 intervening campaign-fix commits"
  - "FIX_COMMIT (79c9d45) retained as a documentation constant naming the reverted behavior, no longer passed to git worktree add directly"
  - "Both before/after builds use -b typst only (never typstpdf) per RESEARCH Pitfall 2, so the reverted depart_term's dangling :term: glossary label cannot fatally abort the measurement"

patterns-established:
  - "Verbatim-string-match-or-raise patching: checkout_pre_xref01_translator raises ValueError loudly if translator.py's depart_term is refactored so the match no longer applies, rather than silently no-op'ing and measuring before==after"

requirements-completed: [GATE-02]

coverage:
  - id: D1
    description: "Empty-URL warning counter (count_empty_url_warnings) correctly counts the literal 'Reference node has empty URL' signature"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "tests/test_corpus_gate.py::test_count_empty_url_warnings"
        status: pass
    human_judgment: false
  - id: D2
    description: "git-worktree pre-XREF-01 translator helper (checkout_pre_xref01_translator) creates an isolated worktree at HEAD and disables only depart_term's id-anchor block, leaving the main tree untouched"
    requirement: "GATE-02"
    verification:
      - kind: integration
        ref: "ad hoc sanity script this session: worktree created, depart_term block absent post-patch, git worktree remove --force cleaned up, git status showed no main-tree translator.py diff"
    human_judgment: false
  - id: D3
    description: "Env-gated SC#3 before/after measurement (test_empty_url_before_after) runs both builds -b typst, asserts after <= before, stays out of routine pytest -m slow"
    requirement: "GATE-02"
    verification:
      - kind: integration
        ref: "TYPSPHINX_CORPUS_REPORT=1 pytest tests/test_corpus_gate.py::test_empty_url_before_after -m slow -v -s (this session, network available) -- passed, before=1 after=1 delta=0"
      - kind: unit
        ref: "pytest tests/test_corpus_gate.py --collect-only -q (confirms the function collects without import errors and is NOT selected by plain -m slow without the env var)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-13
status: complete
---

# Phase 15 Plan 02: SC#3 Empty-URL Before/After Measurement Machinery Summary

**Git-worktree-isolated depart_term XREF-01 revert + env-gated before/after empty-URL warning counter, both builds translate-phase-only (`-b typst`), added to `tests/test_corpus_gate.py`**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-13T00:56Z (approx, session-local)
- **Tasks:** 2
- **Files modified:** 1 (`tests/test_corpus_gate.py`)

## Accomplishments

- `count_empty_url_warnings(stderr_text)` — a plain, fast substring counter for the literal `Reference node has empty URL` warning signature (unit-tested with 3-occurrence and 0-occurrence synthetic stderr).
- `checkout_pre_xref01_translator(repo_root, worktree_dir)` — creates an isolated `git worktree add --detach <dir> HEAD`, then applies a verbatim-matched, fail-loud in-place source patch removing exactly `depart_term`'s XREF-01 label-anchor block, reproducing pre-XREF-01 `depart_term` behavior on top of all current code (Phases 11–14 + this phase's 25 campaign fixes). Never mutates the main working tree.
- `test_empty_url_before_after` — `@pytest.mark.slow`, env-gated behind `TYPSPHINX_CORPUS_REPORT=1` (no new pytest marker, per `--strict-markers`), runs the "before" build with `PYTHONPATH` shadowed to the worktree and the "after" build as-installed, both `-b typst` only, asserts `after <= before`, prints both counts + delta, and cleans up the worktree in a `finally` block.
- Sanity-verified the full mechanism end-to-end this session (network available): the worktree patch correctly strips the id-anchor block, and a real `TYPSPHINX_CORPUS_REPORT=1` run against the cached Sphinx `doc/` corpus passed with `before=1, after=1, delta=0` against the corpus/translator state at commit `629d10e`.

## Task Commits

1. **Task 1: Empty-URL counter + git-worktree pre-fix-translator helper (D-07, methodology-adjusted)** - `dc986f8` (test)
2. **Task 2: Env-gated before/after measurement function (SC#3, -b typst both sides)** - `629d10e` (test)

**Plan metadata:** (this commit, to follow)

## Files Created/Modified

- `tests/test_corpus_gate.py` — appended `FIX_COMMIT`, `_DEPART_TERM_LABEL_ANCHOR_BLOCK`/`_DEPART_TERM_REVERTED`, `checkout_pre_xref01_translator`, `EMPTY_URL_SIGNATURE`, `count_empty_url_warnings`, `test_count_empty_url_warnings`, and `test_empty_url_before_after`.

## Decisions Made

- **D-07 mechanism adjusted, intent preserved.** See Deviations below — this is the plan's single substantive decision this session, driven by the orchestrator's `<CRITICAL_METHODOLOGY_ADJUSTMENT>`.
- Kept `FIX_COMMIT = "79c9d45"` as a pure documentation constant (no longer passed to `git worktree add`), so the commit that introduced XREF-01 remains traceable in the code even though the worktree now branches from `HEAD`.
- Used a verbatim string-match-or-raise patch strategy (rather than a regex or AST edit) for the in-worktree `depart_term` revert: simplest correct approach for a known, stable block, and it fails loudly (not silently) if `depart_term` is ever refactored again — protecting future re-runs of this measurement from silently comparing "before" == "after".

## Deviations from Plan

### Auto-fixed / Directed Adjustments

**1. [Directed methodology adjustment, per orchestrator's `<CRITICAL_METHODOLOGY_ADJUSTMENT>`] D-07's before/after mechanism changed from "checkout `79c9d45~1` wholesale" to "worktree-at-HEAD + targeted `depart_term` patch"**
- **Found during:** Task 1, before writing any code (flagged explicitly in this executor's prompt context, not discovered independently).
- **Issue:** 15-02-PLAN.md's literal mechanism (`git worktree add --detach <dir> 79c9d45~1`) predates a large in-phase campaign: 55 commits landed after `79c9d45`, fixing 25 pre-existing production bugs across Phases 13–14's node handlers and heavily overhauling `translator.py`'s reference/anchor handling to get GATE-02 green. Checking out the whole `79c9d45~1` tree today would compare a translator missing all of that work against current HEAD, conflating the XREF-01 effect with the entire campaign — violating D-07's stated INTENT ("quantify the reduction delivered by the XREF-01 fix") even though it matched D-07's literal original wording.
- **Fix:** `checkout_pre_xref01_translator` now creates the worktree from `HEAD` (not `79c9d45~1`), then applies a minimal, verbatim-matched in-place edit to the worktree's own `typsphinx/translator.py`, removing exactly the `if node.get("ids"):` label-anchor block `79c9d45` added to `depart_term` (confirmed via `git show 79c9d45 -- typsphinx/translator.py`, then re-verified against the CURRENT source since a later campaign commit wrapped `label_id` in `self._namespace_label(...)`). This keeps Phases 11–14 and all 25 campaign fixes present in BOTH the "before" and "after" builds, varying ONLY the XREF-01 `depart_term` anchor emission — a clean, single-variable isolation.
- **Files modified:** `tests/test_corpus_gate.py` only. No `typsphinx/translator.py` edit ships in the main tree — verified via `git status --short` after every task and again after the sanity run.
- **Verification:** Ran an ad hoc sanity script this session confirming the worktree patch correctly strips the anchor block and `git worktree remove --force` cleans up with no main-tree side effects; then ran the full env-gated measurement (`TYPSPHINX_CORPUS_REPORT=1 pytest ... -m slow -v -s`) against the real cached Sphinx `doc/` corpus — passed (`before=1, after=1, delta=0` at this session's corpus/translator state).
- **Committed in:** `dc986f8` (Task 1), `629d10e` (Task 2).

---

**Total deviations:** 1 directed methodology adjustment (explicitly instructed by the orchestrator, not independently discovered — documented here per the CRITICAL_METHODOLOGY_ADJUSTMENT's own instruction to record it in this Deviations section for Plan 03's report-writing context).
**Impact on plan:** D-07's *intent* (measure the XREF-01-specific empty-URL reduction) is preserved exactly; only the revert *mechanism* changed. No scope creep — `tests/test_corpus_gate.py` is the only file touched, matching the plan's `files_modified` frontmatter.

## Issues Encountered

None beyond the directed methodology adjustment above. `black` reformatted the file after the Task 2 edit (wrapping long lines) — applied and re-verified before committing; no logic change.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `tests/test_corpus_gate.py` now has all three SC#1/SC#2/SC#3 measurement primitives (`TestCorpusRenderGate` from Plan 01, plus this plan's `count_empty_url_warnings`/`checkout_pre_xref01_translator`/`test_empty_url_before_after`) ready for Plan 03 to invoke and transcribe into `15-CORPUS-REPORT.md` per D-06.
- Plan 03 should run `TYPSPHINX_CORPUS_REPORT=1 pytest tests/test_corpus_gate.py::test_empty_url_before_after -m slow -v -s` as the authoritative report-run (this session's `before=1/after=1/delta=0` result is a sanity check, not the final recorded number — the corpus/translator state may differ slightly by the time Plan 03 runs, and Plan 03 owns transcribing whatever the report-run actually measures).
- Plan 03 should also explain in the report that D-07's measurement isolates the XREF-01 `depart_term` anchor specifically (not the full pre-`79c9d45~1` historical state), per the methodology-adjustment note embedded in `tests/test_corpus_gate.py`.
- No blockers.

---
*Phase: 15-full-corpus-validation*
*Completed: 2026-07-13*

## Self-Check: PASSED

- FOUND: tests/test_corpus_gate.py
- FOUND: .planning/phases/15-full-corpus-validation/15-02-SUMMARY.md
- FOUND: dc986f8 (Task 1 commit)
- FOUND: 629d10e (Task 2 commit)
