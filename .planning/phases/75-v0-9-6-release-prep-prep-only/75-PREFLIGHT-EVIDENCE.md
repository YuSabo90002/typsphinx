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

Phase 74's close reading (`74-CI-EVIDENCE.md`):

```
REQUIRED_STRICT_CLOSE = true
REQUIRED_CONTEXTS_CLOSE = Build Package|Code Coverage|Lint and Format Check|Test Python 3.12 on ubuntu-latest|Test Python 3.13 on ubuntu-latest|Type Check
```

`PROTECTION_CONTEXTS` above is character-for-character identical to `REQUIRED_CONTEXTS_CLOSE`, and
`PROTECTION_STRICT` (`true`) matches `REQUIRED_STRICT_CLOSE` (`true`).

REQUIRED_CHECKS_UNCHANGED_SINCE_74 = yes

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
43fd7c13 Merge pull request #151 from YuSabo90002/gsd/v0.9.5-docs-link-check-and-navigation
6e2b7899 Merge pull request #146 from YuSabo90002/dependabot/uv/build-1.6.1
96162f3a Merge pull request #148 from YuSabo90002/dependabot/uv/pypdf-6.18.0
5bb304c1 Merge pull request #147 from YuSabo90002/dependabot/uv/ruff-0.16.7
81cc2b3e Merge pull request #149 from YuSabo90002/dependabot/uv/twine-7.0.0

$ git log --first-parent --format='%s' origin/main | grep -c 'Merge pull request #'
103
```

MERGE_PRECEDENT_HITS = 103

Every precedent quoted above (and every one of the 103 counted) landed as `Merge pull request #`,
i.e. a real merge commit, though the repository configuration also allows squash and rebase. The
handoff should therefore expect the release PR to land the same way: `Merge pull request #` as a
merge commit, matching every previous milestone's PR (#132, #136, #143, #145 and #151).

## Branch census

```
$ git ls-remote --heads origin
334b4da7ce20d74b2710c0d0b60d74e11245d114	refs/heads/gsd/v0.9.4-typing-modernization
1d8c76c6d1ac4f00da9b5ef39cf4488a855a6114	refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
e54d47d0b00d77f600d1aa27b0f78a031db055c7	refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b	refs/heads/main
```

REMOTE_BRANCH_COUNT = 4
DEPENDABOT_BRANCHES = 0
MILESTONE_BRANCH_ON_ORIGIN = e54d47d0b00d77f600d1aa27b0f78a031db055c7
DECOY_ON_ORIGIN = 0

This census is measured here, at this plan's own execution time (2026-09-20). It is neither the
nine stale Dependabot branches recorded at discussion time six hours before research ran, nor the
zero measured during research — both are already stale by construction, and this reading (zero
Dependabot branches, zero decoy) is the one the handoff uses.

## Open pull requests

```
$ gh pr list --state open --json number,title,author,headRefName,baseRefName,createdAt
[]
```

OPEN_PRS = 0
DEPENDABOT_OPEN_PRS = 0

```
$ gh pr list --state all --limit 5 --json number,state
[{"number":151,"state":"MERGED"},{"number":150,"state":"MERGED"},{"number":149,"state":"MERGED"},{"number":148,"state":"MERGED"},{"number":147,"state":"MERGED"}]
```

PR_QUERY_CONTROL_ROWS = 5

The all-state control query returns five non-empty rows, proving the `gh pr list` query reaches a
real, non-empty result set — the zero open-PR count above is not a broken query silently returning
nothing.

```
$ gh pr list --head gsd/v0.9.6-doctest-block-rendering-and-release --state all --json number --jq 'length'
0
```

BRANCH_PRS = 0

PR_CENSUS_AT = 2026-09-20T09:03:37Z

`DEPENDABOT_OPEN_PRS` is 0: there is no merge-ordering question at this reading. The handoff
carries the Dependabot-after-milestone ordering rule (the order v0.9.3 used) conditionally, in
case a Dependabot PR opens between this reading and `/gsd-complete-milestone`.

## What the handoff can rely on

In the order `/gsd-complete-milestone` will need them:

1. **The merge is clean.** `git merge-tree --write-tree HEAD origin/main` exits 0, prints the same
   tree SHA on three separate invocations (two recorded, one live in the verify), and the merged
   tree passes `uv lock --check`, a locked sync, `ruff check .` (ruff 0.16.7) and `black --check .`
   in scratch, still carrying `version = "0.9.6"`. `origin/main` has not moved off the milestone
   base (`MAIN_MOVED = no`), so the merge `/gsd-complete-milestone` performs is expected to be a
   fast-forwardable no-op — but this reading is not an assumption for that step; it is what the
   handoff cites.
2. **The required contexts that must be green before merge.** Six contexts, `strict: true`:
   `Build Package`, `Code Coverage`, `Lint and Format Check`, `Test Python 3.12 on ubuntu-latest`,
   `Test Python 3.13 on ubuntu-latest`, `Type Check` — unchanged from Phase 74's close reading.
3. **The merge method.** All three merge methods are allowed on the repository, but every
   precedent PR (103 first-parent hits, including the five most recent milestone PRs) landed as
   `Merge pull request #`, a real merge commit. The release PR should be expected to do the same.
4. **The Dependabot ordering input.** Zero open Dependabot PRs at this reading
   (`PR_CENSUS_AT = 2026-09-20T09:03:37Z`). No ordering action is needed right now; the handoff
   carries the after-milestone rule conditionally in case one opens before the release PR merges.

## Trial merge verdict

All contributing keys:

| Key | Value |
|-----|-------|
| MERGE_TREE_EXIT | 0 |
| MERGED_LOCK_CHECK_EXIT | 0 |
| MERGED_RUFF_EXIT | 0 |
| MERGED_BLACK_EXIT | 0 |
| MERGE_TREE_IDEMPOTENT | yes |
| PROTECTION_CONTEXT_COUNT | 6 (>= 1) |
| BRANCH_PRS | 0 |

Every contributing key meets its threshold.

TRIAL_MERGE_VERDICT = MET
