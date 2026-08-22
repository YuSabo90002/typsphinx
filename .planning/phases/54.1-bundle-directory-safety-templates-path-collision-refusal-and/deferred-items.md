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

**RESOLVED — 2026-08-16, at the Wave 2 post-merge gate (orchestrator).** No separate fix was
needed. `54.1-04` appended 13 test methods to this same file and, in doing so, wrote it back in
`black`-normalized form; that content merged at `a5bdefe1`. Measured on the merged tree, the exact
CI command is clean:

```
$ uv run black --check .
All done! 331 files would be left unchanged.        # exit 0
$ uv run mypy typsphinx/                            # Success: no issues found in 8 source files
$ nix run nixpkgs#ruff -- check .                   # All checks passed!
```

The orchestrator independently reproduced the original failure on the pre-Wave-2 tree
(`would reformat .../tests/test_templates_path_collision_gate.py`, exit 1) before Wave 2 merged,
so `54.1-03`'s report was accurate at the time it was filed — the item is closed as fixed in
passing, not as a false positive. No action remains for `54.1-05`.
