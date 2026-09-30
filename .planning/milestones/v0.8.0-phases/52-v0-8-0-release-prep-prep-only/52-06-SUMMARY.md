---
phase: 52-v0-8-0-release-prep-prep-only
plan: 06
subsystem: release-prep
tags: [sc4-invariants, positive-control, milestone-sweep, measurement-integrity]
dependency graph:
  requires: ["52-02 (CHANGELOG curation)", "52-03 (TestThreeMasterGate PDF gate)"]
  provides: ["52-SC4-INVARIANTS.md — ROADMAP Phase 52 SC#4 evidence"]
  affects: ["/gsd-complete-milestone publish-readiness roll-up"]
tech-stack:
  added: []
  patterns: ["byte-identity array diff", "sorted-set comparison", "scratch-copy positive control"]
key-files:
  created:
    - .planning/phases/52-v0-8-0-release-prep-prep-only/52-SC4-INVARIANTS.md
  modified: []
decisions:
  - "Anchored the sweep at v0.7.1^{commit} (D-09) after re-verifying live that origin/main is both an ancestor of HEAD and the literal merge-base, and that the .planning-excluded shortstat is byte-identical at both anchors (344 files, +15,308/-2,477)."
  - "Invariant 2's raw repo-wide @preview/ file-count proxy grew from 37 to 39 files; both additions were named, content-inspected, and classified as test-assertion consumers of the four canonical version strings (not new production declaration sites), using the same per-file classification methodology 46-SC4-INVARIANTS.md established for its own larger baseline — recorded transparently rather than silently waved through or silently failed."
  - "Control 1 (dependency detector) used a version-bound-tightening commit (63f4284c) rather than an add/remove commit, because this project's runtime dependencies array has never had an entry added or removed in its entire git history — the plan's 'ideal' add/remove candidate does not exist to cite."
metrics:
  duration: ~25min
  completed: 2026-08-15
status: complete
actuals:
  tokens: 8421
  tasks: 2
  commits: 2
---

# Phase 52 Plan 06: SC#4 Milestone-Invariant Sweep with Positive Controls Summary

Mechanically re-verified all three standing v0.8.0 milestone invariants (zero new runtime
dependencies, `@preview` package count still four in lockstep, no new `typst_*` config value) over
a live, SHA-anchored `v0.7.1..HEAD` diff, and — the genuinely new work this plan required — gave each
invariant's detector a real positive control demonstrating it can fire on an actual violation, not
merely restate a clean result.

## What Was Built

`.planning/phases/52-v0-8-0-release-prep-prep-only/52-SC4-INVARIANTS.md`, a single evidence
artifact with:

- **Anchor re-verification**: `v0.7.1^{commit}` peeled correctly (annotated-tag object sha vs. the
  commit it points at), both `git merge-base --is-ancestor` checks passing, and the D-09 anchor
  coincidence confirmed live — `origin/main` and `git merge-base origin/main HEAD` resolve to the
  identical sha, and both anchors' `.planning`-excluded shortstats are byte-identical
  (344 files, +15,308/−2,477).
- **Scale**: 324 commits between `v0.7.1` and HEAD — this sweep's own live count, deliberately not
  matching either the 155 or 157 figures cited (as stale, attributed quotations) from
  `52-CONTEXT.md`/`52-RESEARCH.md`, both of which measured a different range at an earlier point in
  the phase.
- **Invariant 1 (dependencies)**: the `[project] dependencies` array is byte-identical between
  anchors; the entire `pyproject.toml` diff over the milestone is the single version-literal line.
- **Invariant 2 (`@preview`)**: all four package/version pairs agree exactly across
  `writer.py`/`template_engine.py`/`templates/base.typ`; `test_preview_version_sync.py` passes 3/3
  with zero skips. The literal file-count proxy this plan specifies (repo-wide `@preview/` grep) is
  not clean — grew from 37 to 39 files — both named and content-classified below.
- **Invariant 3 (`typst_*` config)**: `typsphinx/__init__.py` is byte-identical between anchors, the
  strongest possible form of the invariant.
- **Three positive controls**, each proven to fire on a real violation:
  1. Dependency detector fires on historical commit `63f4284c`'s real bound-tightening diff.
  2. `@preview` detector fires on a scratch-copy version mutation (never touching tracked files);
     the cross-surface comparison reports a mismatch and names the drifted surface.
  3. Config-value detector fires on historical commit `10100b9d`'s genuine `typst_template_assets`
     addition.
- **Roll-up verdict: SC#4 MET.**

## Deviations from Plan

### Auto-fixed / documented findings

**1. [Rule 1 — measurement-integrity finding, not silently waved through] Invariant 2's raw
file-set proxy grew by two files; classified rather than papered over.**
- **Found during:** Task 1, Step 4(c) (the lockstep-site set comparison).
- **Issue:** The plan's own must-haves define "no new lockstep site" mechanically as "the SET of
  files declaring a `@preview` import has not grown between the two anchors." Measured literally,
  this diff is non-empty: `tests/test_preview_smoke_gate.py` (an existing file, extended during
  Phase 47 with literal `@preview/` import-string assertions) and `tests/test_two_layer_output_gate.py`
  (a genuinely new Phase 47 file) both crossed the repo-wide `@preview/` grep threshold that did not
  match at `v0.7.1`.
- **Resolution:** Applied the same per-file content-classification methodology
  `46-SC4-INVARIANTS.md` established for its own (larger) baseline: both new matches are
  `assert '#import "@preview/<pkg>:<canonical-version>" ...' in content`-shaped test assertions that
  *consume* the four canonical version strings the three real declaration sites emit — they do not
  independently declare a package import Typst itself resolves, and would fail loudly (not silently
  drift) if the canonical versions ever diverged. CLAUDE.md's own canonical definition of
  "lockstep site" — the three production surfaces — did not gain a fourth member. Recorded in full
  in the evidence file: both the raw growth and the content-based resolution, per the plan's explicit
  instruction to name a new file rather than wave it through.
- **Files modified:** None (documentation-only finding; no source file touched).
- **Commit:** `240dd8d7`.

**2. [Rule 1 — plan-suggestion adjustment] Control 1's "add a runtime dependency" example commit
does not exist in this project's history.**
- **Found during:** Task 2, Control 1.
- **Issue:** The plan's action text suggests "a commit that added a runtime dependency is ideal."
  This project's `[project] dependencies` array has held exactly `sphinx`/`docutils`/`typst` since
  the initial commit (`e718ef9b`) — no entry has ever been added or removed.
- **Resolution:** Used the strongest available real violation instead — `63f4284c`, which tightened
  all three entries' version bounds — producing a genuinely non-empty diff across the identical
  extraction-and-diff shape, and named this substitution explicitly in the evidence file rather than
  silently reaching for a different (non-existent) commit.
- **Files modified:** None.
- **Commit:** `514702b5`.

No other deviations. Both tasks executed per plan structure; no checkpoints were hit (plan is fully
autonomous, no `checkpoint:*` tasks).

## Verification Evidence

- `git rev-parse v0.7.1^{commit}` → `48bf135428bb093a77a432d93d16088ce6930342` (40-char commit sha).
- Both `git merge-base --is-ancestor` checks passed; both anchors' shortstats identical.
- `git rev-list --count v0.7.1..HEAD` → `324` (non-zero).
- `[project] dependencies` array diff empty at both anchors (byte-identical).
- `grep -c "@preview" typsphinx/templates/base.typ` → `4`.
- `uv run pytest tests/test_preview_version_sync.py -v` → 3 passed, 0 failed, 0 skipped.
- `add_config_value` registered-name sets diff empty (9-of-10 regex-extracted names identical; whole
  file byte-identical, confirmed as the authoritative superseding evidence).
- Control 1: `63f4284c` vs. parent — non-empty diff, exit 1.
- Control 2: scratch-copy mutation — cross-surface comparison mismatch, exit 1; `git status
  --porcelain` empty; real guard re-runs green.
- Control 3: `10100b9d` vs. parent `e87e852b` — sets differ, exit 1, names `typst_template_assets`.
- `git status --porcelain -- typsphinx/ pyproject.toml tests/` — empty throughout.
- `git tag -l v0.8.0` and `git ls-remote --tags origin v0.8.0` — both empty throughout.

## Self-Check: PASSED

- FOUND: `.planning/phases/52-v0-8-0-release-prep-prep-only/52-SC4-INVARIANTS.md`
- FOUND: commit `240dd8d7` (Task 1)
- FOUND: commit `514702b5` (Task 2)
