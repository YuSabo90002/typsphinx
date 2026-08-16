# Phase 54.1 — Deferred Items

## `tests/test_templates_path_collision_gate.py` fails `black --check .`

**Found during:** `54.1-03` Task 3's repo-wide `black --check .` verification pass.

**Scope:** Out of scope for `54.1-03` — this file was authored entirely by `54.1-01` (Wave 1,
a sibling worktree) and is untouched by any of `54.1-03`'s three commits
(`git diff --stat -- tests/test_templates_path_collision_gate.py` against `54.1-03`'s base commit
`86bfc39055e5e27b686be6afb4c004c8cc35625b` is empty).

**Measured:** `uv run black --check` on the file's content AT `86bfc39055e5e27b686be6afb4c004c8cc35625b`
(`54.1-03`'s own worktree base, i.e. before this plan's first commit) already reports "would
reformat" — the defect predates this plan and is not a regression it caused. Per the executor
scope boundary ("only auto-fix issues DIRECTLY caused by the current task's changes"), this was
not fixed here.

**Action:** Whoever runs `54.1-05` (cross-kind aggregation / phase-boundary green gate) or the
phase's merge/post-merge step should run `uv run black tests/test_templates_path_collision_gate.py`
once, or fold it into `54.1-01`'s own worktree before merge, whichever lands first.
