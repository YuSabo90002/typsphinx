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

## main protection

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq .strict
true
```

PROTECTION_STRICT = true

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '[.contexts[]] | sort | join("|")'
Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

PROTECTION_CONTEXTS = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '.contexts | length'
6
```

PROTECTION_CONTEXT_COUNT = 6

Phase 75's close reading (`75-CI-EVIDENCE.md`):

```
REQUIRED_STRICT_CLOSE_75 = true
REQUIRED_CONTEXTS_CLOSE_75 = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

`PROTECTION_CONTEXTS` above is character-for-character identical to `REQUIRED_CONTEXTS_CLOSE_75`,
and `PROTECTION_STRICT` (`true`) matches `REQUIRED_STRICT_CLOSE_75` (`true`).

REQUIRED_CHECKS_UNCHANGED_SINCE_75 = yes

## Merge method

```
$ gh api repos/YuSabo90002/typsphinx --jq '{allow_merge_commit, allow_squash_merge, allow_rebase_merge}'
{"allow_merge_commit":true,"allow_rebase_merge":true,"allow_squash_merge":true}
```

ALLOW_MERGE_COMMIT = true
ALLOW_SQUASH_MERGE = true
ALLOW_REBASE_MERGE = true

```
$ git log --first-parent --format='%h %s' origin/main | grep 'Merge pull request #' | head -5
eeba55aa Merge pull request #158 from YuSabo90002/dependabot/uv/tox-4.64.2
711a8a39 Merge pull request #159 from YuSabo90002/dependabot/uv/ruff-0.16.9
e046d51a Merge pull request #160 from YuSabo90002/dependabot/uv/sphinx-autodoc-typehints-3.13.7
6fcc5adb Merge pull request #156 from YuSabo90002/gsd/v0.9.6-doctest-block-rendering-and-release
3f084add Merge pull request #155 from YuSabo90002/dependabot/uv/types-docutils-0.23.0.20260917

$ git log --first-parent --format=%s origin/main | grep -c '^Merge pull request #'
111
```

MERGE_PRECEDENT_HITS = 111

Every precedent quoted above (and every one of the 111 counted) landed as `Merge pull request #`,
i.e. a real merge commit, though the repository configuration also allows squash and rebase. The
handoff should therefore expect the release PR to land the same way: `Merge pull request #` as a
merge commit, matching the v0.9.6 release PR precedent (`75-PREFLIGHT-EVIDENCE.md`).

## Branch census

```
$ git ls-remote --heads origin
37b5b472d4c636532e960875db98e7e78929da46	refs/heads/dependabot/uv/types-docutils-0.23.0.20260923
334b4da7ce20d74b2710c0d0b60d74e11245d114	refs/heads/gsd/v0.9.4-typing-modernization
1d8c76c6d1ac4f00da9b5ef39cf4488a855a6114	refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
f1cfedf50d0bd37e4d36ab02c8cea4da467164e2	refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78	refs/heads/gsd/v0.9.7-trusted-publishing-and-release
eeba55aa9b62aecb208bf7abecb051b476592b66	refs/heads/main
```

REMOTE_BRANCH_COUNT = 6
DEPENDABOT_BRANCHES = 1
MILESTONE_BRANCH_ON_ORIGIN = 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78
DECOY_ON_ORIGIN = 0

```
$ git branch --list 'gsd/v0.9.7*'
+ gsd/v0.9.7-trusted-publishing-and-release
```

This census is measured here, at this task's own execution time (2026-09-28T13:28Z), superseding
the planning-time census recorded in this plan's frontmatter table (one Dependabot branch,
`types-docutils`, and no decoy). The local branch listing shows only the milestone branch itself
(the `+` marks the currently checked-out worktree branch for that ref's tracked local — this
worktree is on `worktree-agent-a66a9b7e81a056462`, forked from it).

## Open pull requests

```
$ gh pr list --state open --json number,title,author,headRefName,baseRefName,createdAt
[{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","createdAt":"2026-09-28T00:14:40Z","headRefName":"dependabot/uv/types-docutils-0.23.0.20260923","number":157,"title":"chore(deps-dev): bump types-docutils from 0.23.0.20260917 to 0.23.0.20260923"}]
```

OPEN_PRS = 1
DEPENDABOT_OPEN_PRS = 1
OPEN_PR_NUMBERS = 157

Dependabot PR #157 bumps `types-docutils` from `0.23.0.20260917` to `0.23.0.20260923` (a dev-only
type-stub package). Per the v0.9.3 precedent, the handoff orders the milestone pull request before
any open Dependabot pull request — #157 may merge into `origin/main` before the close runs, which
is one more reason the close re-reads `origin/main` live rather than trusting this reading.

```
$ gh pr list --state all --limit 5 --json number --jq length
5
```

PR_QUERY_CONTROL_ROWS = 5

The all-state control query returns five non-empty rows, proving the `gh pr list` query reaches a
real, non-empty result set.

```
$ gh pr list --head gsd/v0.9.7-trusted-publishing-and-release --state all --json number --jq length
0
```

BRANCH_PRS = 0

PR_CENSUS_AT = 2026-09-28T13:28:46Z

No pull request of any state exists against the milestone branch — this phase opens none, as
required.

## What the handoff can rely on

In the order `/gsd-complete-milestone` needs them:

1. **The merge is clean at `MERGE_TREE = d41a910e448f7205e395aaba0f1d1c6e642e6190`.**
   `git merge-tree --write-tree` against the bumped tip and `origin/main` exits 0, is idempotent
   across two recorded runs and a third live run, and the extracted tree passes `uv lock --check`,
   a locked `--extra dev` sync, `ruff check .` (ruff 0.16.9) and `black --check .` in scratch while
   still reading `version = "0.9.7"`.

2. **`origin/main` has moved (`MAIN_MOVED = yes`, `MAIN_MOVED_FILES = uv.lock`) and must be re-read
   live at the close**, then merged into the branch with `--no-ff` and re-proven because `strict`
   protection is set. Three Dependabot merges (#158 tox, #159 ruff, #160
   sphinx-autodoc-typehints) landed since the milestone base, touching `uv.lock` only.

3. **The required contexts.** Six contexts, `strict: true`: `Build Package`, `Code Coverage`,
   `Lint and Format Check`, `Test Python 3.12 on ubuntu-latest`, `Test Python 3.13 on
   ubuntu-latest`, `Type Check` — unchanged from Phase 75's close reading
   (`REQUIRED_CHECKS_UNCHANGED_SINCE_75 = yes`).

4. **The merge method.** All three merge methods are allowed on the repository, but every
   first-parent precedent (111 hits, including the three most recent Dependabot merges and the
   v0.9.6 milestone merge) landed as `Merge pull request #`, a real merge commit. The release PR
   should be expected to do the same.

5. **The Dependabot ordering input.** One open Dependabot pull request at this reading (#157,
   `types-docutils`, dev-only). The handoff orders the milestone pull request before it, per the
   v0.9.3 precedent, and notes that #157 may merge before the close runs — another reason the close
   re-reads `origin/main` live rather than trusting this reading.

6. **The merged package set still matches `v0.9.6`** (`MERGED_PACKAGE_SET_MATCHES_V096 = yes`) — the
   `### Verified` "no new dependency" CHANGELOG sentence survives the merge as written.

## Trial merge verdict

All contributing keys:

| Key | Value |
|-----|-------|
| MERGE_TREE_EXIT | 0 |
| MERGE_TREE_IDEMPOTENT | yes |
| MERGED_LOCK_CHECK_EXIT | 0 |
| MERGED_SYNC_EXIT | 0 |
| MERGED_RUFF_EXIT | 0 |
| MERGED_BLACK_EXIT | 0 |
| MERGED_VERSION | version = "0.9.7" |
| PROTECTION_CONTEXT_COUNT | 6 (>= 1) |
| BRANCH_PRS | 0 |
| DECOY_ON_ORIGIN | 0 |

Every contributing key meets its threshold.

TRIAL_MERGE_VERDICT = MET
