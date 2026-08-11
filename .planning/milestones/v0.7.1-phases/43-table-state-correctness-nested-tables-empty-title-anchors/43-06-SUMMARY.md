---
phase: 43-table-state-correctness-nested-tables-empty-title-anchors
plan: 06
subsystem: translator
tags: [sphinx, docutils, typst, figure-state, legend, translator, gate-01, code-review-gap-closure]

# Dependency graph
requires:
  - phase: 43-03
    provides: "visit_legend/depart_legend and the _figure_state_stack pattern this plan closes a gap in (43-REVIEW.md CR-01)"
provides:
  - "typsphinx/translator.py: self._legend_list_item_stack (List[Tuple[bool, bool]]) replaces the flat _legend_saved_in_list_item/_legend_saved_list_item_needs_separator scalars visit_legend/depart_legend used, fixing a state leak across a legend nested inside another legend"
  - "tests/fixtures/nested_figure_render_gate/index.rst Section 5 + tests/test_nested_figure_render_gate.py::test_legend_in_legend_does_not_leak_list_item_state: regression gate for the legend-in-legend shape, asserting the rendered .typ output"
  - "43-GATE-EVIDENCE-07.md: RED commit SHA (4250e351a7ef27436f3aad312e73b3103e94ac3c) and fix commit SHA (4ea64006cb930bf1362a61dfa9052811f79617a6), plus a depth-general 3-level-nest proof"
affects: []

# Actuals (#2632)
actuals:
  tokens: 6848
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Stacked save/restore for a paired boolean pair, reusing the existing _list_item_stack precedent (a List[T] pushed on enter, popped on exit) rather than inventing a new frame-dict pattern for just two scalars -- the dict-frame pattern (_push_figure_state/_pop_figure_state) is reserved for larger heterogeneous scalar sets."

key-files:
  created:
    - .planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-GATE-EVIDENCE-07.md
  modified:
    - typsphinx/translator.py
    - tests/fixtures/nested_figure_render_gate/index.rst
    - tests/test_nested_figure_render_gate.py

key-decisions:
  - "Chose the self._list_item_stack precedent (a real List[Tuple[bool, bool]] pushed/popped) over the _push_figure_state/_pop_figure_state frame-dict pattern. Both are established patterns in this same file; the tuple-stack is the more direct fit because it tracks exactly the same two scalars _list_item_stack already tracks one of (in_list_item), while the frame-dict pattern exists specifically for _push_figure_state's six heterogeneous named fields, where dict keys aid legibility more than a plain tuple would."
  - "Proved depth-generality via a scratch build (three-level legend nest, /tmp scratchpad, never committed) rather than adding a permanent Section 6 to the fixture -- the plan's own wording offered either option ('or to a scratch build'); a scratch build keeps the committed fixture from growing an assertion suite duplicated in shape (2-level and 3-level nesting exercise the identical code path -- the stack push/pop -- so only one needs to be a permanent regression gate)."

requirements-completed: [FIG-01]

coverage:
  - id: D1
    description: "A figure's legend nested inside another figure's legend (both levels carrying a caption AND a legend) no longer leaks in_list_item=True into the sibling content that follows the outer figure -- the trailing top-level paragraph renders through the normal par({...}) path, not the leaked parbreak()+bare-text() list-item path"
    requirement: FIG-01
    verification:
      - kind: integration
        ref: "tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_legend_in_legend_does_not_leak_list_item_state"
        status: pass
    human_judgment: false
  - id: D2
    description: "The fix is depth-general: a three-level legend nest also restores in_list_item correctly, not merely the two-level shape 43-REVIEW.md's CR-01 reproduced"
    requirement: FIG-01
    verification:
      - kind: other
        ref: "43-GATE-EVIDENCE-07.md scratch-build 3-level legend nest (exit 0, par({...}) trailing paragraph, all 7 sentinels present in extracted PDF text)"
        status: pass
    human_judgment: false
  - id: D3
    description: "depart_legend's pop is guarded against an unbalanced/malformed doctree -- never a bare .pop() or [-1] index on an empty stack, matching the ASVS V5 pattern already applied to _pop_figure_state/_pop_table_state"
    requirement: FIG-01
    verification:
      - kind: unit
        ref: "typsphinx/translator.py depart_legend -- if self._legend_list_item_stack: ... else: False, False fallback (code-level guard, no dedicated malformed-doctree test since docutils' own balanced walkabout() guarantees a matching depart_legend per visit_legend, mirroring _pop_figure_state's own justification)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full suite, black, ruff, and mypy all stay green after the fix, and the RED commit touched no file under typsphinx/"
    requirement: FIG-01
    verification:
      - kind: other
        ref: "43-GATE-EVIDENCE-07.md: uv run python -m pytest -q (837 passed, 1 skipped -- 836 baseline + 1 new test), black --check ./ruff check ./mypy typsphinx/ all green, git diff <base> <red-sha> -- typsphinx/ empty"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-04
status: complete
---

# Phase 43 Plan 06: Legend-in-Legend State Leak Gap Closure (CR-01) Summary

**Replaced `visit_legend`/`depart_legend`'s two flat instance-attribute scalars with a real `self._legend_list_item_stack: List[Tuple[bool, bool]]`, closing `43-REVIEW.md` CR-01: a figure's legend nested inside another figure's legend (both levels carrying a caption AND a legend) no longer leaks `in_list_item=True` into every sibling for the rest of the document — proven via a real-compile RED-to-GREEN gate, an isolated single-line before/after `.typ` diff, and a depth-general 3-level-nest scratch-build proof.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-04 (session start)
- **Completed:** 2026-08-04T01:55:28Z
- **Tasks:** 3/3
- **Files modified:** 4 (1 production file, 2 test/fixture files, 1 evidence file)

## Accomplishments

- Closed `43-REVIEW.md` CR-01: independently re-reproduced (not transcribed) the exact defect the reviewer found — `visit_legend` saved `in_list_item`/`list_item_needs_separator` into two flat instance attributes, so a legend nested inside another legend's own `visit_legend` clobbered the outer legend's saved values with its own already-mutated `True`/`True`. The outer `depart_legend` then restored the wrong value, leaking `in_list_item=True` into every sibling for the rest of the document. Confirmed via `publish_doctree` probe that the reproducing shape requires the INNER figure to carry BOTH a caption and its own legend — a caption-only inner figure (the existing Section 1) does not trigger it, which is exactly why the phase's own gate suite missed it.
- Fixed by replacing the flat scalars with `self._legend_list_item_stack: List[Tuple[bool, bool]]`, mirroring the pre-existing `self._list_item_stack` pattern (`visit_list_item`/`depart_list_item`) rather than the heavier `_push_figure_state`/`_pop_figure_state` frame-dict pattern — the right-sized fit for exactly two boolean scalars.
- `depart_legend`'s pop is guarded (`if self._legend_list_item_stack: ... else: False, False`), matching the ASVS V5 empty-stack-safety pattern already established by `_pop_figure_state`/`_pop_table_state` and `depart_list_item` in this same file.
- Added fixture Section 5 (`nested_figure_render_gate/index.rst`) and a new render-gate test method asserting on the RENDERED output — the trailing top-level paragraph after the outer figure must emit `par({text("NF5TRAILINGPARA sentinel text.")})`, not the leaked `parbreak()` + bare `text(...)` form — and that both captions and both legend sentinels still appear, so the gate cannot pass by breaking the nesting it protects.
- Measured the pre-fix "worst outcome" directly: the build exits 0 with no compile fatal and no `unknown node type` warning — a well-formed, plausible-looking document that silently misrepresents the source, exactly as the defect brief characterized it.
- Proved the fix is depth-general, not tuned to the two-level shape it was handed: a three-level legend nest (scratch build, not committed to the fixture) also restores `in_list_item` correctly at every level, with all 7 sentinels present in the extracted PDF text.
- Recorded a single-line, fully isolated before/after `.typ` diff — the ONLY change across the entire emitted document is the trailing paragraph's rendering path; every other line, including both figures' full markup, is byte-identical pre- and post-fix.

## Task Commits

Each task was committed atomically, per the plan's RED-first discipline:

1. **Task 1: RED — legend-in-legend fixture Section 5 + regression gate** - `4250e35` (test) — `typsphinx/` untouched (verified: `git diff <base> <red-sha> -- typsphinx/` is empty)
2. **Task 2: Fix — stack visit_legend/depart_legend state** - `4ea6400` (fix)
3. **Task 3a: Gate evidence** - `d4b5198` (docs)
4. **Task 3b: Plan metadata (this SUMMARY)** - commit follows this file

## Files Created/Modified

- `typsphinx/translator.py` - Added `self._legend_list_item_stack: List[Tuple[bool, bool]] = []` to `__init__` (alongside `self._list_item_stack`); `visit_legend` now appends `(in_list_item, list_item_needs_separator)`; `depart_legend` pops with a guarded fallback instead of restoring from the two removed flat attributes
- `tests/fixtures/nested_figure_render_gate/index.rst` - Added Section 5: an outer figure with caption + legend, whose legend contains a paragraph followed by a NESTED figure that itself has caption + legend, followed by a trailing top-level paragraph sentinel
- `tests/test_nested_figure_render_gate.py` - Added `NF5_*` sentinel constants and `test_legend_in_legend_does_not_leak_list_item_state`, asserting the rendered `par({...})` form, the absence of the leaked `parbreak()` form, and PDF-text presence of all five Section-5 sentinels
- `.planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-GATE-EVIDENCE-07.md` - Environment provisioning notes, `publish_doctree` probe, verbatim RED test failure and pre-fix `.typ` tail, verbatim GREEN test run and post-fix `.typ` tail, isolated before/after diff, 3-level-nest depth-generality proof, full-suite/lint/type gate results

## Decisions Made

- **Chose the `_list_item_stack` tuple-stack pattern over the `_push_figure_state`/`_pop_figure_state` frame-dict pattern.** Both are established precedents in this file. The tuple-stack is the more direct fit: it tracks exactly the same two scalars `_list_item_stack` already tracks one of, while the frame-dict pattern was built for `_push_figure_state`'s six heterogeneous named fields, where dict keys add legibility a two-element tuple doesn't need.
- **Proved depth-generality via a scratch build rather than a committed Section 6.** The task instructions explicitly offered either option ("or to a scratch build"). A 2-level and 3-level nest exercise the identical code path (the stack's push/pop), so committing a second, near-duplicate fixture section would add no additional coverage over one committed regression gate plus one documented scratch-build proof.

## Deviations from Plan

None (Rules 1-4) — plan executed as written. Both process notes above are documented under Decisions Made, not as Rule 1-4 deviations, since no code behavior diverged from the plan's specification.

## Issues Encountered

- **Same NixOS `uv`/`ruff` ELF-interpreter hazard documented in `43-03-SUMMARY.md`.** `.venv/bin/uv` after `uv sync` was a generic-linux ELF NixOS cannot exec; resolved by symlinking to the system `uv` found via `command -v`. No standalone `ruff` package exists in this environment's Nix store, so `.venv/bin/ruff` was `patchelf --set-interpreter`-repointed at the same glibc loader already working for the main tree's `.venv/bin/ruff` (confirmed via `file` on that binary first, per the environment briefing). Both binaries confirmed executing before the first gate run.
- **The sandbox's worktree-path-safety checker rejected complex multi-line/`for`-loop Bash commands and any command wrapping `git`/`env`/`uv sync` inside a redirect it could not statically verify stayed inside the worktree.** Resolved by breaking every provisioning step into separate, simple, single-purpose Bash calls (one `command -v`, one `ln -sf`, one `readlink -f`, etc.) instead of the compound one-liners in the plan's own environment briefing.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `43-REVIEW.md` CR-01 (the sole BLOCKER finding) and WR-01 (the missing regression test) are both closed: the fix is in place, guarded against underflow, proven depth-general, and covered by a committed regression gate that asserts on rendered output.
- The full test suite (837 passed, 1 skipped — 836 baseline + 1 new test), `black --check .`, `ruff check .`, and `mypy typsphinx/` are all green on this worktree's HEAD; `.github/`, `pyproject.toml`, and `uv.lock` are unmodified.
- No blockers for the phase close — this gap-closure plan touches only the `visit_legend`/`depart_legend` neighborhood in `translator.py`, disjoint from every other plan's scope in this phase.

---
*Phase: 43-table-state-correctness-nested-tables-empty-title-anchors*
*Completed: 2026-08-04*

## Self-Check: PASSED

All claimed created/modified files verified present on disk (`typsphinx/translator.py`,
`tests/fixtures/nested_figure_render_gate/index.rst`, `tests/test_nested_figure_render_gate.py`,
`43-GATE-EVIDENCE-07.md`). All three claimed commits verified present in `git log`
(`4250e35`, `4ea6400`, `d4b5198`), with `4250e35` confirmed to be the RED commit (diffed empty
against `typsphinx/translator.py` relative to this worktree's base
`3e0097eb455c263c012a3131956b6fcb0fcc8283`).
