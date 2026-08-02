---
phase: 40-citations-full-round-trip
plan: 04
subsystem: testing
tags: [sphinx, typst, docutils, citations, pytest, corpus-gate, non-regression]

requires:
  - phase: 40-citations-full-round-trip (plan 01)
    provides: "tests/test_citation_render_gate.py and 40-GATE-EVIDENCE-01.md's original classic-RED record, re-proven fresh in this plan"
  - phase: 40-citations-full-round-trip (plan 02)
    provides: "the restored examples/charged-ieee/ samples and 40-GATE-EVIDENCE-02.md's RED record, re-run GREEN in this plan"
  - phase: 40-citations-full-round-trip (plan 03)
    provides: "typsphinx/translator.py's visit_citation/depart_citation/visit_label and the D-14 guarded anchor -- the merged translator this plan's gates measure against"
  - phase: 40-citations-full-round-trip (plan 05)
    provides: "tests/test_citation_render_gate.py's six corrected assertions (40-GATE-EVIDENCE-01.md Section 8) -- the 9/9-green module this plan re-proves fresh, replacing the plan's own stale 'assertions unchanged' premise"
provides:
  - "tests/test_corpus_gate.py -m slow actually run: the D-14 phase gate (test_corpus_compiles_with_no_fatal_error) executed and PASSED against the real cached Sphinx v9.1.0 doc/ corpus -- not a skip"
  - "40-NONREGRESSION.md: whole-phase diffstat, the full-corpus gate's verbatim passed/skipped breakdown, a fresh 9/9 GREEN + 9/9 RED-against-8b22bf6 re-proof of tests/test_citation_render_gate.py (superseding the plan's stale 'assertions unchanged' clause with 40-05's six documented amendments), the CIT-05 GREEN flip, the D-14 corpus byte-diff restated, every milestone invariant with its proving command, and the closed-out 40-VALIDATION.md ten-row verification map"
  - "Confirmation that tests/test_desc_break_marker_buffer_swap_gate.py's Phase-40 forward-reference comment is still accurate and needs no edit, and that tests/test_corpus_gate.py's two citation mentions remain synthetic warning-parser strings needing no change"
affects: []

tech-stack:
  added: []
  patterns:
    - "Non-regression evidence composed of independent proofs sitting side by side rather than one being substituted for another: the full-corpus compile gate (this plan), the corpus byte-diff (40-03), and the render-gate's own RED/GREEN pair (this plan, reproduced fresh rather than trusted from a prior plan's record)"

key-files:
  created:
    - .planning/phases/40-citations-full-round-trip/40-NONREGRESSION.md
  modified: []

key-decisions:
  - "Task 1's file (tests/test_desc_break_marker_buffer_swap_gate.py) is left unmodified: its Phase-40 forward-reference comment is written entirely in the present tense and its claim (Phase 40 is the milestone's sole classic-RED exception) is confirmed true against ROADMAP.md binding constraint #3 and this plan's own fresh RED re-proof -- an unmodified file is the plan's own declared valid outcome, not a shortfall."
  - "40-NONREGRESSION.md explicitly supersedes 40-04-PLAN.md's own stale verification claim ('assertions unchanged from the RED recorded in 40-GATE-EVIDENCE-01.md') with the stronger, freshly-reproduced claim from 40-05: 9/9 green against the merged translator and 9/9 RED against 8b22bf6, with all six of 40-05's corrections named plus a selector-by-selector map showing which of the nine were touched."
  - "The full-corpus gate's two slow-marked tests are distinguished explicitly: test_corpus_compiles_with_no_fatal_error (D-14's actual gate) executed and PASSED; test_empty_url_before_after skipped for an unrelated, by-design env-var reason (Phase 15/SC#3 reporting, TYPSPHINX_CORPUS_REPORT=1) that was never D-14's evidence -- recorded so neither skip is mistaken for the phase gate skipping."

requirements-completed: [CIT-01, CIT-03, CIT-04, CIT-05]

coverage:
  - id: D1
    description: "The full-corpus -b typstpdf gate (test_corpus_compiles_with_no_fatal_error) actually executed against the real cached Sphinx v9.1.0 doc/ corpus and passed -- not a skip"
    requirement: "CIT-03"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_corpus_gate.py -m slow -v -- TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_citation_render_gate.py reproduced fresh: 9/9 green against the merged translator, 9/9 RED against the pre-40-03 translator (8b22bf6) -- the module's ability to discriminate is verified, not assumed"
    requirement: "CIT-01"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_citation_render_gate.py -v -- 9 passed"
        status: pass
      - kind: manual_procedural
        ref: "git checkout 8b22bf6 -- typsphinx/translator.py && pytest -v -- 9 failed, then git checkout HEAD -- typsphinx/translator.py restoring a clean tree"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_examples_charged_ieee_gate.py re-run green (CIT-05), module provably unedited across the whole phase"
    requirement: "CIT-05"
    verification:
      - kind: integration
        ref: "uv run pytest tests/test_examples_charged_ieee_gate.py -v -- 2 passed"
        status: pass
    human_judgment: false
  - id: D4
    description: "Milestone invariants re-proven: zero new dependencies, @preview count stays four across all three sites, lint/type trio clean, full suite green"
    verification:
      - kind: integration
        ref: "git diff --stat -- pyproject.toml uv.lock (empty); uv run pytest tests/test_preview_version_sync.py -v (3 passed); uv run black --check . / ruff check . / mypy typsphinx/ (all clean); uv run pytest -q (783 passed, 1 skipped)"
        status: pass
    human_judgment: false
  - id: D5
    description: "All ten of 40-VALIDATION.md's Per-Task Verification Map rows carry a fresh executed command and a real status"
    verification:
      - kind: other
        ref: ".planning/phases/40-citations-full-round-trip/40-NONREGRESSION.md Section 7"
        status: pass
    human_judgment: false
  - id: D6
    description: "The one stale-forward-reference candidate (tests/test_desc_break_marker_buffer_swap_gate.py's Phase-40 comment) is re-checked against the finished phase and confirmed still accurate"
    verification:
      - kind: other
        ref: ".planning/phases/40-citations-full-round-trip/40-NONREGRESSION.md Section 8 -- quoted sentence, cross-checked against ROADMAP.md binding constraint #3"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-02
status: complete
---

# Phase 40 Plan 04: Citations Full Round-Trip — Phase Close-Out Summary

**Ran `tests/test_corpus_gate.py -m slow` for real (the full-corpus `-b typstpdf` gate PASSED against the real cached Sphinx `v9.1.0` `doc/` corpus, not a skip), reproduced a fresh 9/9 GREEN + 9/9 RED-against-`8b22bf6` proof of `tests/test_citation_render_gate.py` that supersedes the plan's own stale "assertions unchanged" premise with 40-05's six documented corrections, re-ran the shipped-sample gate green, and recorded all of it plus every milestone invariant and the closed-out ten-row validation map in `40-NONREGRESSION.md` — closing Phase 40 with proof, not assumption.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-08-02T09:35:00Z (approx, worktree provisioning start)
- **Completed:** 2026-08-02T10:30:00Z
- **Tasks:** 2
- **Files modified:** 1 (new: `40-NONREGRESSION.md`); 0 files edited (Task 1's candidate file was confirmed accurate and left untouched)

## Accomplishments

- **Task 1:** Re-read `tests/test_desc_break_marker_buffer_swap_gate.py`'s Phase-40 forward-reference comment against the finished phase and confirmed it is still accurate (present tense throughout, and the "sole exception" claim matches ROADMAP.md binding constraint #3 and this phase's own real classic-RED evidence) — left unmodified, a valid outcome per the plan's own instruction. Independently re-derived that `tests/test_corpus_gate.py`'s two `citation` mentions (lines 217-227 and 503) are synthetic Python string literals feeding the warning-parser's own unit tests, never live-build assertions — confirmed the module needed no change. Re-ran `tests/test_examples_charged_ieee_gate.py` (2 passed) and confirmed via `git diff --stat` it was never edited across the whole phase.
- **Task 2:** Ran `uv run pytest tests/test_corpus_gate.py -m slow -v` for real: `test_corpus_compiles_with_no_fatal_error` (the actual D-14 gate) executed against the locally cached, version-matched Sphinx `v9.1.0` corpus and PASSED — not skipped. The module's second slow test (`test_empty_url_before_after`) did skip, but for an unrelated, by-design env-var reason (`TYPSPHINX_CORPUS_REPORT=1`, a Phase-15/SC#3 reporting concern) that was never D-14's evidence — both facts recorded explicitly so neither skip is mistaken for the phase gate skipping. Reproduced fresh (not merely transcribed) the 9/9 GREEN run of `tests/test_citation_render_gate.py` against the merged translator, then temporarily restored `typsphinx/translator.py` to `8b22bf6` (the last commit byte-identical to the pre-phase translator) and confirmed all 9 tests fail there too, before restoring a clean tree (`git status --porcelain` empty). Wrote `40-NONREGRESSION.md` recording all of the above plus the whole-phase diffstat, the CIT-05 GREEN flip mapped to `40-GATE-EVIDENCE-02.md`, the D-14 corpus byte-diff restated from `40-03-SUMMARY.md`, every milestone invariant with its proving command (zero new dependencies, `@preview` count 4 across 3 sites, lint/type trio, full suite), and the closed-out `40-VALIDATION.md` ten-row verification map with a command run fresh for every row.
- Full suite (`uv run pytest -q`, slow included): 783 passed, 1 skipped (the same by-design env-gated test). `black --check .`, `ruff check .`, `mypy typsphinx/` all clean. `git diff --stat -- typsphinx/ examples/ pyproject.toml uv.lock` across this plan's own commit is empty — this plan touched nothing outside `.planning/`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Settle the stale Phase-40 forward reference and re-run the untouched shipped-sample gate** — no commit (the file was confirmed accurate and left unmodified, per the plan's own declared valid outcome for this task; conclusion recorded in `40-NONREGRESSION.md` Section 8, written as part of Task 2's commit)
2. **Task 2: Run the full-corpus gate for real and record the whole phase's non-regression evidence** - `ae355f6` (docs)

**Plan metadata:** (this commit, following)

## Files Created/Modified

- `.planning/phases/40-citations-full-round-trip/40-NONREGRESSION.md` - New. Nine sections: whole-phase diffstat, the full-corpus gate's verbatim run with an explicit passed-vs-skipped breakdown, the citation render-gate's fresh 9/9 GREEN + 9/9 RED re-proof with a selector-by-selector map and the "assertions unchanged" premise explicitly superseded, the CIT-05 GREEN flip, the D-14 corpus byte-diff restated, milestone invariants with proving commands, the closed-out ten-row `40-VALIDATION.md` map, the stale-comment decision, and an executed-vs-skipped summary table.
- `tests/test_desc_break_marker_buffer_swap_gate.py` - **Not modified.** Re-read and confirmed accurate; see Decisions Made.

## Decisions Made

- **`tests/test_desc_break_marker_buffer_swap_gate.py` left unmodified.** Its `TestDescBreakMarkerBufferSwapCompileGate` docstring states: *"milestone invariant #4 requires every node-handler-adjacent fixture in this phase to compile successfully both before and after any translator edit, since the RED/GREEN split in this phase is structural, never a compile fatal (Phase 40's citation work is the sole exception)."* This is written entirely in the present tense (no "will be"/"is planned to be") and its claim matches `.planning/ROADMAP.md`'s binding constraint #3 verbatim ("Phase 40 (citations) is the sole exception and keeps the classic `TypstError` RED") — confirmed true by this plan's own fresh reproduction of that classic RED against `8b22bf6`. An unmodified file is the plan's own declared valid outcome for this scenario, not a shortfall.
- **`40-04-PLAN.md`'s own stale premise superseded, not silently followed.** The plan (authored before 40-05 existed) claims the gate module's "assertions are unchanged from the RED recorded in `40-GATE-EVIDENCE-01.md`." `40-NONREGRESSION.md` Section 3 states plainly that this is no longer literally true, names all six of 40-05's corrections (two `tags=` call sites, a marker-column measurement fix, a concat bracket-wrap tolerance, an anchor-detection regex broadened to a second Typst syntax form, and an unsound single-backref regex), and replaces the claim with the stronger, independently-reproduced one: 9/9 green against the merged translator, 9/9 RED against `8b22bf6`.
- **The full-corpus gate's two slow tests are reported separately, never conflated.** `test_corpus_compiles_with_no_fatal_error` (D-14's gate) executed and passed; `test_empty_url_before_after` skipped for a documented, unrelated, by-design reason. Reporting them as one "1 passed 1 skipped" line without this distinction would risk a reader mistaking the skip for a partial gate failure or the pass for covering both concerns — both are wrong, so the evidence file names each test individually with its own reason.

## Deviations from Plan

None — plan executed exactly as written. Task 1 concluding "no edit needed" is the plan's own explicitly anticipated outcome, not a deviation. `40-04-PLAN.md`'s stale "assertions unchanged" clause was superseded per this plan's own `<plan_specific_notes>` instruction (itself part of the plan as given to this executor), not a deviation from it.

## Issues Encountered

None. The worktree required the standard per-worktree `uv sync --extra dev` provisioning plus re-pointing both `.venv/bin/uv` and `.venv/bin/ruff` at their resolved nix-store paths (the NixOS sandbox hazard this project's `CLAUDE.md` and this plan's own prompt both flag) — completed before any test run, confirmed via `file .venv/bin/uv .venv/bin/ruff` showing genuine symlinks to `/nix/store/...` paths rather than the main checkout's stale generic-linux ELF, and not a deviation from either document's own explicit instructions.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 40 (Citations — Full Round Trip) is closed with proof: the full-corpus `-b typstpdf` gate ran for real and passed, the milestone's sole classic-RED exception (CIT-01) was independently re-proven RED-against-unfixed/GREEN-against-fixed by this plan itself (not merely trusted from 40-03/40-05's own records), and all ten `40-VALIDATION.md` rows carry a fresh command and a real status.
- All six CIT requirements (CIT-01 through CIT-06) are already ticked Complete in `.planning/REQUIREMENTS.md` (CIT-01/CIT-06 by 40-03, CIT-02..CIT-05 by 40-05); `requirements-completed` in this SUMMARY's frontmatter lists the four this plan's own PLAN.md frontmatter names (CIT-01, CIT-03, CIT-04, CIT-05) per this project's summary-authoring convention, though the checkbox flips themselves happened in the earlier plans — this plan's own contribution is closing their non-regression evidence, not the flips.
- `tests/test_desc_break_marker_buffer_swap_gate.py` and `tests/test_corpus_gate.py` remain byte-identical to the phase-start commit — confirmed via `git diff --stat` in `40-NONREGRESSION.md` Section 1.
- No blockers. STATE.md and ROADMAP.md are intentionally left untouched by this plan (worktree mode) — the orchestrator owns those writes after this wave's agents complete.

---
*Phase: 40-citations-full-round-trip*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: .planning/phases/40-citations-full-round-trip/40-NONREGRESSION.md
- FOUND: .planning/phases/40-citations-full-round-trip/40-04-SUMMARY.md
- FOUND commit: ae355f6 (Task 2)
- FOUND commit: 5720d42 (SUMMARY.md)
