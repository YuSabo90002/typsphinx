# Phase 77 — Preflight Evidence (SC#3 trial merge and remote reads)

## Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-28T13:26:29Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a66a9b7e81a056462

$ test -f .git; echo "exit:$?"
exit:0

$ grep -q typsphinx-fhs-run "$(command -v uv)" && echo "shim_check:ok"
shim_check:ok

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
Using CPython 3.14.4
Resolved 91 packages in [...]
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a66a9b7e81a056462
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a66a9b7e81a056462
 + typsphinx==0.9.7 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a66a9b7e81a056462)
 [... full dependency set installed cleanly ...]
exit:0
```

BASE_77_05 = 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3
SCRATCH_77_05 = /tmp/p7705.XU1iD5
MERGED_TREE_DIR = /tmp/tmp.aAtZm5FEB3

## Tip identity

BUMP_COMMIT_SHA (from `77-BUMP-EVIDENCE.md`) = 39cb79f970c4137d4238023e1df7291c7c282c3a

```
$ git merge-base --is-ancestor 39cb79f970c4137d4238023e1df7291c7c282c3a 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3; echo "exit:$?"
exit:0

$ sed -n 7p pyproject.toml
version = "0.9.7"
```

Both checks pass — `BASE_77_05` is the bumped tip. No HALT.

## Trial merge

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git rev-parse origin/main
eeba55aa9b62aecb208bf7abecb051b476592b66

$ git log -1 --format='%H %s' origin/main
eeba55aa9b62aecb208bf7abecb051b476592b66 Merge pull request #158 from YuSabo90002/dependabot/uv/tox-4.64.2
```

ORIGIN_MAIN_SHA = eeba55aa9b62aecb208bf7abecb051b476592b66

```
$ git merge-base 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3 origin/main
9fa1cb894137933f4dbb49d1668fc193e2ef1bc8
```

MILESTONE_BASE = 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8

`ORIGIN_MAIN_SHA` differs from `MILESTONE_BASE` — `origin/main` has moved past the milestone base,
exactly as the planning-time census recorded (three Dependabot merges: #158 tox 4.64.2, #159 ruff
0.16.9, #160 sphinx-autodoc-typehints 3.13.7).

MAIN_MOVED = yes

```
$ git log --oneline 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8..origin/main
eeba55aa Merge pull request #158 from YuSabo90002/dependabot/uv/tox-4.64.2
034c8427 chore(deps): bump tox from 4.61.5 to 4.64.2
711a8a39 Merge pull request #159 from YuSabo90002/dependabot/uv/ruff-0.16.9
2e88fcd5 chore(deps): bump ruff from 0.16.8 to 0.16.9
e046d51a Merge pull request #160 from YuSabo90002/dependabot/uv/sphinx-autodoc-typehints-3.13.7
0e5704f5 chore(deps): bump sphinx-autodoc-typehints from 3.13.6 to 3.13.7
```

MAIN_MOVED_COMMITS = 6

```
$ git diff --name-only 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8 origin/main
uv.lock
```

MAIN_MOVED_FILES = uv.lock

Three Dependabot pull requests merged into `origin/main` since the milestone base, all changing
`uv.lock` only (27 insertions, 27 deletions per the planning-time census) — no source or config
file moved.

```
$ git merge-tree --write-tree 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3 origin/main; echo "exit:$?"
d41a910e448f7205e395aaba0f1d1c6e642e6190
exit:0
```

MERGE_TREE_EXIT = 0
MERGE_TREE = d41a910e448f7205e395aaba0f1d1c6e642e6190

The merge is taken on `BASE_77_05`, not on HEAD, so the tree is a property of two fixed commits and
does not move when this plan commits its own evidence.

```
$ git merge-tree --write-tree 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3 origin/main
d41a910e448f7205e395aaba0f1d1c6e642e6190
```

MERGE_TREE_SECOND = d41a910e448f7205e395aaba0f1d1c6e642e6190

The two recorded tree SHAs are equal.

MERGE_TREE_IDEMPOTENT = yes

No conflict occurred; the trial merge is clean.

## Merged-tree lock and lint

```
$ git archive --format=tar -o "/tmp/p7705.XU1iD5/p7705_merged.tar" d41a910e448f7205e395aaba0f1d1c6e642e6190; echo "exit:$?"
exit:0

$ tar -xf "/tmp/p7705.XU1iD5/p7705_merged.tar" -C "/tmp/tmp.aAtZm5FEB3"; echo "exit:$?"
exit:0

$ uv --directory "/tmp/tmp.aAtZm5FEB3" lock --check; echo "exit:$?"
Using CPython 3.14.4
Resolved 91 packages in 4ms
exit:0
```

MERGED_LOCK_CHECK_EXIT = 0

```
$ uv --directory "/tmp/tmp.aAtZm5FEB3" sync --locked --extra dev --no-install-project -q; echo "exit:$?"
exit:0
```

MERGED_SYNC_EXIT = 0

```
$ uv --directory "/tmp/tmp.aAtZm5FEB3" run --no-sync ruff check .; echo "exit:$?"
All checks passed!
exit:0
```

MERGED_RUFF_EXIT = 0

```
$ uv --directory "/tmp/tmp.aAtZm5FEB3" run --no-sync black --check .; echo "exit:$?"
All done! ✨ 🍰 ✨
359 files would be left unchanged.
exit:0
```

MERGED_BLACK_EXIT = 0

```
$ uv --directory "/tmp/tmp.aAtZm5FEB3" run --no-sync ruff --version
ruff 0.16.9
```

MERGED_RUFF_VERSION = 0.16.9

This is the ruff version the merged lock resolves — one Dependabot bump ahead of the branch's own
0.16.8 (planning-time census). The release pull request's `Lint and Format Check` job will resolve
this same lock and therefore this same version.

```
$ grep -m1 '^version = ' "/tmp/tmp.aAtZm5FEB3/pyproject.toml"
version = "0.9.7"
```

MERGED_VERSION = version = "0.9.7"

The merge did not revert the bump.

```
$ git show v0.9.6:uv.lock | grep -A1 -xF '[[package]]' | sed -n 's/^name = "\(.*\)"$/\1/p' | LC_ALL=C sort | sha256sum
aafccad7c3f1d4cffdfbb3b5fc2963b2fa9428a56aae2714a5235b52fd66f6bd  -

$ grep -A1 -xF '[[package]]' "/tmp/tmp.aAtZm5FEB3/uv.lock" | sed -n 's/^name = "\(.*\)"$/\1/p' | LC_ALL=C sort | sha256sum
aafccad7c3f1d4cffdfbb3b5fc2963b2fa9428a56aae2714a5235b52fd66f6bd  -
```

The two package-name-set hashes are identical.

MERGED_PACKAGE_SET_MATCHES_V096 = yes

The merged tree adds no new runtime or dev dependency relative to `v0.9.6` — the `### Verified`
CHANGELOG sentence (77-02) survives the merge unchanged.
