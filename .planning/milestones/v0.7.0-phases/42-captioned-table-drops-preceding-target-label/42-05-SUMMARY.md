---
phase: 42-captioned-table-drops-preceding-target-label
plan: 05
subsystem: testing
tags: [typst, sphinx-extension, evidence, worktree-isolation, byte-invariance]

# Dependency graph
requires:
  - phase: 42-04
    provides: "The TBL-03 call-ordering fix (typsphinx/translator.py, commit e5575f3) and its
      GREEN evidence (42-GATE-EVIDENCE-04.md)"
  - phase: 42-01
    provides: "The RED-recording commit (d28f2c8) used as the pre-fix side, and the
      captioned_table_propagated_target_render_gate fixture used as one of the two
      caption-less builds"
provides:
  - "42-GATE-EVIDENCE-05.md — the recorded empty two-build diff discharging ROADMAP SC#4"
affects: [42-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-throwaway-worktree byte-invariance proof (Phase 36's SC#2 method), reused verbatim:
      git worktree add --detach at each named SHA, per-worktree uv sync --extra dev, a uv
      Nix-store shim, a positive typsphinx.__file__ isolation check per side, then a real
      sphinx-build -b typst diff."

key-files:
  created:
    - .planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-05.md
  modified: []

key-decisions:
  - "For the captioned_table_propagated_target_render_gate fixture, diffed only the isolated
    caption-less control section (located by its surrounding heading anchors) rather than the
    whole file — the whole file is EXPECTED to differ post-fix (that is SC#3, not SC#4), and a
    whole-file diff was recorded first as positive proof the two throwaway worktrees really ran
    different depart_table code before the isolated-section empty diff is presented as the SC#4
    proof itself."
  - "No ruff Nix-store package exists in this sandbox (measured: ls /nix/store found no
    *-ruff* entry); this task never invokes ruff, so the missing shim is recorded transparently
    in the evidence file rather than blocking the proof, which rests on the uv shim and the two
    distinct typsphinx.__file__ paths."

patterns-established: []

requirements-completed: [TBL-03]

coverage:
  - id: D1
    description: "Caption-less table path proven byte-for-byte unchanged by the TBL-03 fix via
      an empty diff between two real sphinx-build -b typst runs at named pre-fix (d28f2c8) and
      post-fix (e5575f3) commits, each built from its own throwaway, independently-provisioned
      git worktree"
    requirement: "TBL-03"
    verification:
      - kind: other
        ref: "42-GATE-EVIDENCE-05.md § 4a/4c — diff exit 0, verbatim empty output, recorded
          against two real sphinx-build invocations"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-08-03
status: complete
---

# Phase 42 Plan 05: Caption-less byte invariance (SC#4) Summary

**Empty two-build diff over two throwaway worktrees at d28f2c8 (pre-fix) and e5575f3 (post-fix)
proves the caption-less table path is untouched by the TBL-03 fix.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2
- **Files modified:** 1 (evidence file only — no code, no fixture, no golden)

## Accomplishments
- Created and independently provisioned two throwaway git worktrees at the named pre-fix
  (`d28f2c8`) and post-fix (`e5575f3`) commits, each proven isolated via a distinct
  `typsphinx.__file__` resolution path.
- Built both caption-less shapes from each worktree with a real `sphinx-build -b typst`: the
  pre-existing `table_in_list_item_render_gate` fixture (whole-file empty diff) and the
  caption-less control section of `captioned_table_propagated_target_render_gate` (isolated-
  section empty diff, after first recording the expected non-empty whole-file diff over the
  captioned regions as positive proof the two sides ran different code).
- Isolated the production-code diff to `typsphinx/translator.py` alone with a `typsphinx/`
  pathspec, and recorded why the unscoped `git diff --stat` over the same two commits is larger
  (unrelated plan 42-02/42-03 commits sit between them).
- Removed both throwaway worktrees; `git worktree list` confirms none remain.
- Wrote `42-GATE-EVIDENCE-05.md`, discharging ROADMAP SC#4.

## Task Commits

Both tasks land in a single commit because Task 1 (the build/diff work) produces no
repository-tracked artifact of its own — only the throwaway worktrees under the scratchpad,
which are removed at the end of the task — and Task 2 writes the one file both tasks target.

1. **Task 1 + Task 2: Build caption-less fixtures from a pre-fix/post-fix worktree pair, diff
   them, and write 42-GATE-EVIDENCE-05.md** - `0c167c1` (docs)

## Files Created/Modified
- `.planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-05.md` -
  Two named commits, per-worktree isolation proof (uv Nix-store shim + `typsphinx.__file__`),
  every build command with its exit status, the empty pairwise `.typ` diffs at exit 0, the
  pathspec-isolated production diff, and the SC#4 verdict row.

## Decisions Made
- Diffed the isolated caption-less control section of `captioned_table_propagated_target_render_gate`
  rather than the whole file, because the whole file legitimately differs post-fix (the captioned
  shapes gain their propagated-anchor lines — that is SC#3's job). The whole-file diff was recorded
  first, non-empty as expected, as evidence the two throwaway worktrees genuinely ran different
  code before presenting the isolated-section empty diff as the SC#4 proof.
- No `ruff` Nix-store package exists in this sandbox (`ls /nix/store | grep -i '^[a-z0-9]*-ruff'`
  returned nothing). This task never runs `ruff` — only `uv run python -m sphinx -b typst` builds
  — so the missing shim does not weaken the isolation proof, which rests on the `uv` shim plus two
  distinct `typsphinx.__file__` paths (recorded, not silently omitted).

## Deviations from Plan

None - plan executed exactly as written. Both throwaway worktrees, both fixture builds, the
isolated-section diff, and the pathspec-scoped production diff all match the plan's action text
and acceptance criteria.

## Issues Encountered
None. The sandbox's Bash tool rejected a few multi-command chained invocations (`env -u ... &&`,
`for t in uv ruff; do ... done`) as "too complex to verify" against the worktree-isolation guard;
each was split into individual single-purpose commands (one `ln -sf`, one `readlink -f`, etc.),
which worked without changing the underlying provisioning steps or their recorded evidence.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
SC#4 is discharged. Plan 42-06 (SC#6 reconciliation: CHANGELOG TBL-03 line, re-measured Phase 41
SC#4 invariant sweep, REL-04/REL-05 checkbox-flip guard) can proceed — it is the only remaining
plan in this phase's wave 3.

---
*Phase: 42-captioned-table-drops-preceding-target-label*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-05.md`
- FOUND: `.planning/phases/42-captioned-table-drops-preceding-target-label/42-05-SUMMARY.md`
- FOUND: commit `0c167c1` (evidence file)
- FOUND: commit `ca5efb2` (this summary)
