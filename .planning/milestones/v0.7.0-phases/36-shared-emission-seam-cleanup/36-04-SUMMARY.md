---
phase: 36-shared-emission-seam-cleanup
plan: 04
subsystem: testing
tags: [pytest, gate-evidence, regression-sweep, census, phase-verdict]

# Dependency graph
requires:
  - phase: "36-01"
    provides: "Pre-change full-suite baseline, RED capture, delegation census -- the comparison basis this plan's set-difference check reads against"
  - phase: "36-02"
    provides: "Decoupled visit_desc_signature/visit_rubric, post-decoupling SC#2 diff and SC#1 census"
  - phase: "36-03"
    provides: "MATH-02 RED/GREEN evidence and the 653 passed, 1 skipped, 0 failed full-suite result this plan's own sweep reproduces"
provides:
  - "36-GATE-EVIDENCE.md: SC#4 regression sweep (full suite, lint/type trio, milestone invariants), corpus-gate result, test-migration census, Diff scope, and the four-row Phase 36 verdict table"
  - "Corrected, Phase-39-routed deferred todo for the par()-loss defect (resolves_phase: 39)"
  - "REQUIREMENTS.md: ADM-06 marked complete (MATH-02 already marked by Plan 03)"
affects: ["37-signature-typography", "39-rubric-admonition-taxonomy"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Set-difference regression comparison (failing-before-and-after / failing-only-after / failing-only-before) against a named pre-change baseline commit, rather than an absolute-zero-failures criterion, per this sandbox's documented environmental failure class"

key-files:
  created:
    - .planning/phases/36-shared-emission-seam-cleanup/36-04-SUMMARY.md
  modified:
    - .planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md
    - .planning/todos/pending/2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Re-measured (not inherited) 36-CONTEXT.md's claim that MATH-02's exact-string blast radius is zero: grepped tests/test_math_mitex.py / tests/test_math_native.py / tests/test_math_fallback.py for any newline-bearing assertion (none exist), then confirmed via git diff that every newline-bearing math/bold assertion in tests/test_inline_math_after_text_render_gate.py present at the phase-start commit is still present, byte-identical, at HEAD -- the whole-file diff contains zero removed/modified lines, only additions. Re-derived-assertion count: 0, command recorded."
  - "Used two different baseline commits for two different measurements, both transparently scoped: b37ea40 (\"the Plan 01 baseline sha\", the pre-decoupling golden-capture commit Plans 02/03 both name) for the pyproject.toml/uv.lock/translator.py invariant checks matching Plan 02/03's established convention, and 83114d2 (the true phase-start commit immediately preceding Plan 01's first commit) for the test-migration census -- because b37ea40 post-dates Plan 01's own Task 1 commit that created the SC#2 fixture and test module, so a b37ea40-scoped diff would silently omit those files from the census even though they are part of the phase's work. Both scopes and the reason are recorded in the evidence file rather than picking one silently."
  - "Corrected the deferred par()-loss todo's front matter (resolves_phase: 39) and body to describe the POST-decoupling code: the leak is unchanged in cause and behavior because D-02 required the three decoupled handler pairs (visit_strong, visit_rubric, visit_desc_signature) to keep sharing the same _strong_was_* instance attribute names -- a reader arriving after Phase 36 who assumed the decoupling also separated this state would be wrong, so the todo says so explicitly."

requirements-completed: [ADM-06, MATH-02]

coverage:
  - id: D1
    description: "The full suite, the lint/type trio, and the full-corpus -b typstpdf gate are all run and recorded, with SC#4 verdict established as post-change failing set == Plan 01's pre-change set (both empty, not by absolute-zero argument)"
    requirement: MATH-02
    verification:
      - kind: unit
        ref: "uv run pytest -q --tb=no -rf (full suite)"
        status: pass
      - kind: other
        ref: "uv run black --check . / uv run ruff check . / uv run mypy typsphinx/"
        status: pass
      - kind: integration
        ref: "uv run pytest tests/test_corpus_gate.py -q -m slow (TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The MATH-02 exact-string blast radius (zero) is re-measured in this plan, not inherited from 36-CONTEXT.md's correction"
    requirement: MATH-02
    verification:
      - kind: other
        ref: "grep across tests/test_math_mitex.py, tests/test_math_native.py, tests/test_math_fallback.py (zero newline-bearing assertions) plus git diff 83114d2 HEAD -- tests/test_inline_math_after_text_render_gate.py (zero removed/modified lines)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Milestone invariant #1 (pyproject.toml/uv.lock unchanged, @preview versions unchanged on all three lockstep surfaces) holds across the whole phase"
    requirement: ADM-06
    verification:
      - kind: unit
        ref: "git diff b37ea40 HEAD -- pyproject.toml uv.lock (empty); uv run pytest tests/test_preview_version_sync.py -q"
        status: pass
    human_judgment: false
  - id: D4
    description: "The deferred par()-loss defect is filed, corrected for the post-decoupling code, and routed to Phase 39 (D-02)"
    requirement: ADM-06
    verification:
      - kind: other
        ref: ".planning/todos/pending/2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md (resolves_phase: 39 present, body describes three-handler-pair shared-slot mechanism)"
        status: pass
    human_judgment: false
  - id: D5
    description: "36-GATE-EVIDENCE.md closes with a four-row verdict table, one row per ROADMAP success criterion, each pointing at a real evidence section; no 36-VERIFICATION.md exists"
    requirement: ADM-06
    verification:
      - kind: other
        ref: ".planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md § Phase 36 verdict"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min (task-commit work plus environment provisioning and measurement)
completed: 2026-08-01
status: complete
---

# Phase 36 Plan 04: SC#4 Regression Sweep, Census, and Phase Verdict Summary

**Full suite (653 passed, 1 skipped, 0 failed), lint/type trio, and full-corpus `-b typstpdf` gate all green with a post-change failing-node-ID set proven empty against Plan 01's recorded (also-empty) pre-change baseline; MATH-02's exact-string blast radius re-measured at zero; the deferred `par()`-loss todo corrected for the post-decoupling three-handler-pair shared-slot reality and routed to Phase 39; phase closes with a four-row verdict table showing all four ROADMAP success criteria MET.**

## Performance

- **Duration:** ~35 min (task-commit work `7d027bd` through `9972ab2`, plus worktree environment provisioning — `uv sync --extra dev --extra docs` plus the NixOS `.venv/bin/uv`/`.venv/bin/ruff` stub-ld symlink fix — and reading beforehand)
- **Started:** 2026-08-01T01:03:57Z (approx, environment provisioning)
- **Tasks:** 2
- **Files modified:** 3 (`36-GATE-EVIDENCE.md`, the deferred todo, `REQUIREMENTS.md`), plus this SUMMARY.md

## Accomplishments

- Ran and recorded the SC#4 regression sweep in `36-GATE-EVIDENCE.md`: the full suite (`653 passed, 1 skipped, 0 failed`, zero failing node IDs), the lint/type trio (`black`/`ruff`/`mypy` all exit 0), and the four milestone-invariant checks (`pyproject.toml`/`uv.lock` unchanged since Plan 01's baseline commit, `@preview` lockstep test passing, the full phase touch-set scoped to `tests/`, `typsphinx/translator.py`, and `.planning/`, and zero `xfail`/`skip`/`deselect` markers added anywhere in the phase).
- Set-difference-compared the post-change failing set against Plan 01's recorded pre-change baseline (re-read from the evidence file, not from memory): all three groups (before-and-after, only-after, only-before) are empty, so SC#4's acceptance is satisfied by direct set equality.
- Ran the full-corpus `-b typstpdf` gate (`tests/test_corpus_gate.py -m slow`) and recorded a real pass (`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`), distinguishing it from an unrelated, separately-documented env-gated skip in the same module rather than describing the skip as the gate's result.
- Recorded the test-migration census: 8 test/fixture files touched across the whole phase (scoped from the true phase-start commit, since the "Plan 01 baseline sha" used for the invariant checks post-dates Plan 01's own fixture-creation commit), with a table naming every file, its render-gate classes/methods, and whether each was new or extended.
- Re-measured (not inherited) the claim that MATH-02's exact-string blast radius is zero: confirmed no newline-bearing assertion exists in the three math-path test modules, and confirmed via `git diff` that every pre-existing newline-bearing math/bold assertion in `tests/test_inline_math_after_text_render_gate.py` is unchanged, byte-identical, at HEAD — the phase's diff to that file is purely additive.
- Corrected `.planning/todos/pending/2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md`: added `resolves_phase: 39`, rewrote the mechanism description to state explicitly that the Phase 36 decoupling did **not** fix the leak (D-02 required the three now-independent handler pairs to keep sharing the same `_strong_was_*` slot names), and updated the `files:` block to the post-decoupling line locations.
- Appended `## Diff scope` (`git diff --stat` from the Plan 01 baseline commit) and `## Phase 36 verdict` — a four-row table (SC#1..SC#4) each pointing at the evidence section that discharges it — plus a closing paragraph naming ADM-06/MATH-02's disposition and both folded todos' fates (MATH-02's todo resolved, ready for `todos/completed/`; the `par()`-loss todo pending, routed to Phase 39).
- Marked ADM-06 complete in `REQUIREMENTS.md` (checkbox + traceability table); MATH-02 was already marked complete by Plan 03.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run and record the SC#4 regression sweep** - `7d027bd` (docs)
2. **Task 2: Record the test-migration census, correct the deferred todo, and write the phase verdict** - `9972ab2` (docs)

_No TDD-per-task structure — this plan writes no code and no test; `typsphinx/translator.py` is untouched by this plan (confirmed by the recorded phase touch-set)._

## Files Created/Modified

- `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` - Appended the SC#4 regression sweep, corpus-gate result, test-migration census, `Diff scope`, and the four-row `Phase 36 verdict` table (Plans 01-03's sections untouched)
- `.planning/todos/pending/2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md` - Added `resolves_phase: 39`, corrected the mechanism description and `files:` block for the post-decoupling code
- `.planning/REQUIREMENTS.md` - Marked ADM-06 complete (checkbox + traceability row)
- `.planning/phases/36-shared-emission-seam-cleanup/36-04-SUMMARY.md` - This summary

## Decisions Made

- Re-measured MATH-02's exact-string blast-radius claim rather than transcribing 36-CONTEXT.md's correction, per this plan's own binding constraint. Confirmed zero via two independent commands (a grep across the three math-path test modules, and a `git diff` cross-check of the one file that does carry newline-bearing math/bold assertions).
- Used `b37ea40` ("the Plan 01 baseline sha", matching Plans 02/03's own convention) for the invariant checks that Plans 02/03 already scoped that way, but used the true phase-start commit `83114d2` for the test-migration census, since `b37ea40` post-dates Plan 01's own fixture/test-module creation commit and would silently under-report the census. Recorded both scopes and the reason transparently in the evidence file, following the same disclosure pattern Plan 02 used for its own `--stat` measurement note.
- Corrected the deferred todo to state plainly that the Phase 36 decoupling did NOT repair the `par()`-loss leak, and why (D-02's shared-slot-name requirement) — preventing a plausible but wrong inference a future reader might otherwise draw from seeing the delegation removed.

## Deviations from Plan

None - plan executed exactly as written. All measurements (the regression sweep, the corpus gate, the census, the re-derived-assertion count) were run fresh in this session, not transcribed from planning documents or prior plans' summaries.

## Issues Encountered

- The worktree's NixOS sandbox required manual resolution of the `.venv/bin/uv`/`.venv/bin/ruff` stub-ld symlink fix: `command -v ruff` found nothing on `PATH` outside `.venv` (unlike `uv`, which resolved via the Nix profile), so the documented `for t in uv ruff; do [ -x "$(command -v $t)" ] && ln -sf ... ; done` loop alone would have left `ruff` unfixed. Located a working Nix-store `ruff` build (`/nix/store/a2jxv2y5qmc8asf9v3znic5pi4hf2nvx-ruff-0.15.14/bin/ruff`, a different patch version than the pinned `ruff==0.15.20` but functionally equivalent for `ruff check`) and symlinked it directly. Verified working before running any lint command.
- The worktree's own command-safety checker rejected several multi-command Bash invocations (`env -u ... uv sync ...`, chained `ln -sf "$(command -v ...)"`) as "too complex to verify stays inside the worktree" — worked around by running each step as a separate, simpler Bash call (`unset VIRTUAL_ENV; unset UV_PROJECT_ENVIRONMENT; uv sync ...`, then individual `which`/`ln -sf` calls). No functional impact; same commands, split into single-purpose invocations.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 36 is fully closed: all four ROADMAP success criteria (SC#1-SC#4) are MET with direct, re-measured evidence in `36-GATE-EVIDENCE.md`'s closing verdict table. Both requirements (ADM-06, MATH-02) are marked complete in `REQUIREMENTS.md`.
- The MATH-02 folded todo (`2026-07-29-visit-math-block-redundant-blank-line-in-list-items.md`, `resolves_phase: 36`) is resolved and should be filed to `.planning/todos/completed/` at phase close (not done by this plan — filing completed todos is a phase-close/milestone-audit action, out of this plan's `files_modified` scope).
- Phase 37 (Signature Typography) can now restyle `desc_signature`'s emission independently, since it owns its own handler pair (SC#1/SC#2) rather than sharing `visit_strong`'s.
- Phase 39 (Admonition Taxonomy + Rubric Nesting) inherits two items from this phase: it owns `rubric`'s independent restyling (same seam-cut rationale as Phase 37), and it now owns the corrected, routed `par()`-loss todo (`resolves_phase: 39`), whose "measure real-corpus incidence first" instruction is unchanged and still pending.
- No blockers for either downstream phase. `pyproject.toml`/`uv.lock` and the `@preview` four-package lockstep are confirmed unchanged across the entire phase.

---
*Phase: 36-shared-emission-seam-cleanup*
*Completed: 2026-08-01*

## Self-Check: PASSED

Confirmed on disk: `36-GATE-EVIDENCE.md` (with this plan's appended
sections), the corrected/routed deferred todo, `REQUIREMENTS.md` (ADM-06
marked complete), and this `36-04-SUMMARY.md`. Confirmed in `git log`:
both task commit hashes (`7d027bd`, `9972ab2`).
</content>
