# Phase 75 — Preflight Evidence (SC4 trial merge and remote reads)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-20T09:00:25Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af6c82e762dca1961

$ test -f .git; echo "exit:$?"
exit:0

$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "shim_check:ok"
shim_check:ok

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Using CPython 3.14.4
Resolved 91 packages in [...]
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-af6c82e762dca1961
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-af6c82e762dca1961
 + typsphinx==0.9.6 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-af6c82e762dca1961)
 [... full dependency set installed cleanly ...]
exit:0
```

BASE_75_05 = 44d22075a77f5b425062b51329b6de1c3b27adbc
SCRATCH_75_05 = /tmp/tmp.9Y714QmfF6
MERGED_TREE_DIR = /tmp/tmp.kY4WVKDe1X

## Tip identity

BUMP_COMMIT_SHA (from `75-BUMP-EVIDENCE.md`) = 84edd348b52f1f7e95073d2b3ebcbcd36417bc15

```
$ git merge-base --is-ancestor 84edd348b52f1f7e95073d2b3ebcbcd36417bc15 HEAD; echo "exit:$?"
exit:0

$ sed -n 7p pyproject.toml
version = "0.9.6"
```

Both checks pass — this worktree's HEAD is the bumped tip. No HALT.

## Trial merge

```
$ git fetch origin
(no output — up to date)

$ git rev-parse origin/main
6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b

$ git log -1 --format='%H %s' origin/main
6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b chore: remove REQUIREMENTS.md for v0.9.5 milestone
```

ORIGIN_MAIN_SHA = 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b

```
$ git merge-base HEAD origin/main
6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b
```

MILESTONE_BASE = 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b

`ORIGIN_MAIN_SHA` equals `MILESTONE_BASE` — `origin/main` has not moved off the milestone base.

MAIN_MOVED = no

```
$ git merge-tree --write-tree HEAD origin/main; echo "exit:$?"
96d8ca9e9317b25a5ca57c76f7bd75ae88e5340f
exit:0
```

MERGE_TREE_EXIT = 0
MERGE_TREE = 96d8ca9e9317b25a5ca57c76f7bd75ae88e5340f

```
$ git merge-tree --write-tree HEAD origin/main
96d8ca9e9317b25a5ca57c76f7bd75ae88e5340f
```

MERGE_TREE_SECOND = 96d8ca9e9317b25a5ca57c76f7bd75ae88e5340f

The two recorded tree SHAs are equal.

MERGE_TREE_IDEMPOTENT = yes

## Merged-tree lock and lint

```
$ git archive --format=tar -o "/tmp/tmp.9Y714QmfF6/p7505_merged.tar" 96d8ca9e9317b25a5ca57c76f7bd75ae88e5340f; echo "exit:$?"
exit:0

$ tar -xf "/tmp/tmp.9Y714QmfF6/p7505_merged.tar" -C "/tmp/tmp.kY4WVKDe1X"; echo "exit:$?"
exit:0

$ uv --directory "/tmp/tmp.kY4WVKDe1X" lock --check; echo "exit:$?"
Using CPython 3.14.4
Resolved 91 packages in 3ms
exit:0
```

MERGED_LOCK_CHECK_EXIT = 0

```
$ uv --directory "/tmp/tmp.kY4WVKDe1X" sync --locked --extra dev --no-install-project -q; echo "exit:$?"
exit:0
```

MERGED_SYNC_EXIT = 0

```
$ uv --directory "/tmp/tmp.kY4WVKDe1X" run --no-sync ruff check .; echo "exit:$?"
All checks passed!
exit:0
```

MERGED_RUFF_EXIT = 0

```
$ uv --directory "/tmp/tmp.kY4WVKDe1X" run --no-sync black --check .; echo "exit:$?"
All done! [check] [cake] [check]
358 files would be left unchanged.
exit:0
```

MERGED_BLACK_EXIT = 0

```
$ uv --directory "/tmp/tmp.kY4WVKDe1X" run --no-sync ruff --version
ruff 0.16.7
```

MERGED_RUFF_VERSION = 0.16.7

This project has had a CI run fail on lint alone while every test lane passed, so recording the
exact ruff version the merged lock resolves — not just a green exit — matters: the CI job that will
run against the real merge will resolve the same lock and therefore the same ruff version.

```
$ grep -m1 '^version = ' "/tmp/tmp.kY4WVKDe1X/pyproject.toml"
version = "0.9.6"
```

MERGED_VERSION = version = "0.9.6"

The merge did not revert the bump.
