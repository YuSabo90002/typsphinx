# Phase 67 Plan 02 — #138 (ruff) Disposal Evidence

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aae55fa68ebf933d8
```

`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` ran to completion, installing
`ruff==0.15.20`, `uv==0.12.13`, `typsphinx==0.9.2` (editable, from this worktree) among 91 resolved
packages.

```
$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

BASE_67_02 = 6a687ca9e854d6f4aad16df78585855d85209de5

## Wave-1 gate

Read from `67-PROOF-EVIDENCE.md`:

```
DEP02_VERDICT = MET
PROOF_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7
SC2_BRANCH = can
MECHANICAL_CLOSE = none
```

`grep -c '^## HALT' 67-PROOF-EVIDENCE.md` = 0.

The wave-1 gate is MET with no HALT heading, so this disposal precedes on D-02's proof (constraint 4).

## Pre-merge gate

```
$ git fetch origin main
$ git rev-parse origin/main
293f0c2684641f5d4b2f5ed021b565656e38d48c
```

MAIN_BEFORE_138 = 293f0c2684641f5d4b2f5ed021b565656e38d48c

```
$ gh api repos/YuSabo90002/typsphinx/branches/main/protection --jq '{strict: .required_status_checks.strict, contexts: .required_status_checks.contexts}'
{"contexts":["Test Python 3.12 on ubuntu-latest","Lint and Format Check","Type Check","Code Coverage","Build Package","Test Python 3.13 on ubuntu-latest"],"strict":true}
```

Six required contexts, `strict: true` — matches the Phase 66 census.

```
$ gh pr view 138 --json state,headRefOid,headRefName,author,baseRefName,mergeable,mergeStateStatus,title
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","headRefName":"dependabot/uv/ruff-0.16.6","headRefOid":"88088071e02a7411800f504e06b1ded9d6891cc7","mergeStateStatus":"CLEAN","mergeable":"MERGEABLE","state":"OPEN","title":"chore(deps): bump ruff from 0.15.20 to 0.16.6"}
```

HEAD138 = 88088071e02a7411800f504e06b1ded9d6891cc7

State is OPEN and `mergeStateStatus` is CLEAN — the gate holds.

```
$ git fetch origin refs/pull/138/head
$ git rev-parse FETCH_HEAD
88088071e02a7411800f504e06b1ded9d6891cc7
```

`FETCH_HEAD` equals HEAD138.

```
$ git show --name-only --format='%H%n%an <%ae>%n%s' 88088071e02a7411800f504e06b1ded9d6891cc7
88088071e02a7411800f504e06b1ded9d6891cc7
dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
chore(deps): bump ruff from 0.15.20 to 0.16.6

pyproject.toml
uv.lock
```

The name list is exactly `pyproject.toml` and `uv.lock`, authored by `dependabot[bot]`.

```
$ git show 88088071e02a7411800f504e06b1ded9d6891cc7:uv.lock | awk '/^name = "ruff"$/{getline; print; exit}'
version = "0.16.6"
```

RUFF_VERSION_138 = 0.16.6

HEAD_MOVED = no

HEAD138 equals PROOF_SHA (88088071e02a7411800f504e06b1ded9d6891cc7).

No `gh pr checkout`, `git switch` or `git checkout` was run against the dependabot head — it was
only read via `git show`/`git fetch` fetching the ref, never checked out into the working tree.

## Moved-head branch

not taken: HEAD138 equals PROOF_SHA

## Required checks on HEAD138

```
$ gh api "repos/YuSabo90002/typsphinx/commits/88088071e02a7411800f504e06b1ded9d6891cc7/check-runs?per_page=100" --jq '.check_runs[] | [.name, .status, .conclusion] | @tsv'
Test Python 3.12 on macos-latest	completed	success
Test Python 3.13 on windows-latest	completed	success
Test Python 3.13 on ubuntu-latest	completed	success
build-docs	completed	success
Test Python 3.12 on windows-latest	completed	success
Build Package	completed	success
Test Python 3.13 on macos-latest	completed	success
Lint and Format Check	completed	success
Test Python 3.12 on ubuntu-latest	completed	success
Integration Test - advanced	completed	success
Code Coverage	completed	success
Integration Test - basic	completed	success
Repo-wide link check (advisory)	completed	success
Type Check	completed	success
Repo-wide link check (advisory)	completed	success
```

The six required contexts, all `success`:

| Context | Conclusion |
|---------|------------|
| Test Python 3.12 on ubuntu-latest | success |
| Test Python 3.13 on ubuntu-latest | success |
| Lint and Format Check | success |
| Type Check | success |
| Code Coverage | success |
| Build Package | success |

## SC#3 merits for #138

(a) **dev-extra scope.**

```
$ git show 88088071e02a7411800f504e06b1ded9d6891cc7:pyproject.toml | grep -n 'ruff'
40:    "ruff>=0.15,<0.17",
118:[tool.ruff]
122:[tool.ruff.lint]
```

```
$ git show 88088071e02a7411800f504e06b1ded9d6891cc7:pyproject.toml | awk '/^dependencies = \[/,/^\]/'
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]
```

```
$ git show 88088071e02a7411800f504e06b1ded9d6891cc7:pyproject.toml | awk '/^dev = \[/,/^\]/'
dev = [
    "pytest>=8.4,<10",
    "pytest-cov>=4.0",
    "tox>=4.56,<5",
    "tox-uv-bare>=1.35,<2",
    "black>=26,<27",
    "ruff>=0.15,<0.17",
    "mypy>=1.13,<3.0",
    "pre-commit>=3.0",
    "types-docutils>=0.21",
    "twine>=5.0",
    "build>=1.0",
    "pypdf>=6.14,<7",
    "pillow>=12.3,<13",  # D-07: ADM-04 greyscale render (Image.convert), dev-only
]
dev = [
    "types-docutils>=0.22.2.20251006",
]
```

`ruff` appears in the `dev` extra only; `[project] dependencies` has no ruff entry at all. No
runtime or user-install effect.

(b) **The range change.**

```
$ git show 88088071e02a7411800f504e06b1ded9d6891cc7 -- pyproject.toml
commit 88088071e02a7411800f504e06b1ded9d6891cc7
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Sat Sep 12 10:39:48 2026 +0000

    chore(deps): bump ruff from 0.15.20 to 0.16.6

    Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.20 to 0.16.6.
    - [Release notes](https://github.com/astral-sh/ruff/releases)
    - [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
    - [Commits](https://github.com/astral-sh/ruff/compare/0.15.20...0.16.6)

    ---
    updated-dependencies:
    - dependency-name: ruff
      dependency-version: 0.16.6
      dependency-type: direct:production
      update-type: version-update:semver-minor
    ...

    Signed-off-by: dependabot[bot] <support@github.com>

diff --git a/pyproject.toml b/pyproject.toml
index 9ac02823..fc25883f 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -37,7 +37,7 @@ dev = [
     "tox>=4.56,<5",
     "tox-uv-bare>=1.35,<2",
     "black>=26,<27",
-    "ruff>=0.15,<0.16",
+    "ruff>=0.15,<0.17",
     "mypy>=1.13,<3.0",
     "pre-commit>=3.0",
     "types-docutils>=0.21",
```

(c) **No new violation on main plus #138.** The `Lint and Format Check` conclusion recorded above
is `success`. Its `Run lint with tox` step runs `black --check .` then `ruff check .`
(`tox.ini:44-45`), so #138's own CI already lints `main` + #138 at `RUFF_VERSION_138` clean.

(d) **No new violation on the milestone tip.**

FHS_RUNNER = /nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run

(resolved via `sed -n 's/.*exec "\([^"]*typsphinx-fhs-run\)".*/\1/p' "$(command -v ruff)" | head -n 1`
against the ruff shim at `/nix/store/vxcr1f2x7ywkyvwli0sykhgwsmkg800k-ruff/bin/ruff`)

```
$ /nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run uvx --from "ruff==0.16.6" ruff --version
ruff 0.16.6
$ /nix/store/99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run/bin/typsphinx-fhs-run uvx --from "ruff==0.16.6" ruff check .; echo "exit:$?"
All checks passed!
exit:0
```

MILESTONE_RUFF_CHECK = pass

The version line read `ruff 0.16.6`, the output contains `All checks passed!`, and it printed `exit:0`.

(e) **Upstream.**

```
$ curl -fsS https://pypi.org/pypi/ruff/json | python3 -c 'import json,sys; print(json.load(sys.stdin)["info"]["version"])'
0.16.7
```

RUFF_PYPI_LATEST = 0.16.7

One patch release ahead of RUFF_VERSION_138 (0.16.6). Dependabot may move #138's head to 0.16.7
before the merge (Pitfall 3). This is not a gate; Task 3 re-asserts the head before merging.

(f) **No other file names the milestone's ruff version.**

```
$ git grep -n "0.15.20" HEAD -- ':!.planning' ':!uv.lock'; echo "exit:$?"
exit:1
```

Empty, as required (RUFF_VERSION_MILESTONE = 0.15.20, set in the NIX-01 section below).

## REL-12 merge simulation

```
$ git merge-tree --write-tree --name-only HEAD 88088071e02a7411800f504e06b1ded9d6891cc7; echo "exit:$?"
f084c0227cf859fbd6a65377bd722f4bb847d2f1
exit:0
```

REL12_SIM_EXIT = 0
REL12_SIM_TREE = f084c0227cf859fbd6a65377bd722f4bb847d2f1

The merged tree was exported with `git archive` into a scratch directory and extracted.

```
$ uv --version
uv 0.12.13 (x86_64-unknown-linux-gnu)
$ uv lock --check --directory <scratch>/x; echo "exit:$?"
Using CPython 3.14.4
Resolved 91 packages in 4ms
exit:0
```

REL12_LOCK_CHECK_EXIT = 0

```
$ grep -n 'ruff\|tox-uv' <scratch>/x/pyproject.toml
38:    "tox-uv>=1.35,<2",
40:    "ruff>=0.15,<0.17",
118:[tool.ruff]
122:[tool.ruff.lint]
```

The merged `pyproject.toml` carries `tox-uv>=1.35,<2` (from HEAD's Phase 65 revert) and
`ruff>=0.15,<0.17` (from #138). The scratch directory was removed after these reads.

## NIX-01 interaction and D-04 divergence

```
$ git show HEAD:uv.lock | awk '/^name = "ruff"$/{getline; print; exit}'
version = "0.15.20"
```

RUFF_VERSION_MILESTONE = 0.15.20

```
$ ruff --version
ruff 0.15.20
```

SHIM_RUFF_VERSION = 0.15.20

**D-03 statement:** NIX-01 was measured and closed on the milestone branch against its own
`uv.lock` (RUFF_VERSION_MILESTONE = 0.15.20), and stays closed — nothing here reopens it.
NIX-01's binding sense is "the version `uv.lock` pins", so after REL-12 carries #138's `uv.lock`
change into `main` and the milestone branch absorbs it, the maintainer's shim will report whatever
`main`'s lock then pins (RUFF_VERSION_138 = 0.16.6 today, possibly RUFF_PYPI_LATEST = 0.16.7 by
then if dependabot moves the head again). That is consistent with NIX-01, not a regression of it.

**D-04 statement:** Until REL-12, `main`'s CI runs RUFF_VERSION_138 (0.16.6) via #138's own Lint
job, while the local worktree shim reports SHIM_RUFF_VERSION (0.15.20) because this worktree's
`uv.lock` is still the milestone's own, unmerged lock. That divergence is recorded here, not fixed.
No `origin/main` merge into the milestone branch and no main-checkout re-sync happen in this phase.
REL-12's own CI run, in a later phase, is where the merged tree is linted for real (constraint 7).

## Owner decision (#138)

The owner's reply to the Task 2 `checkpoint:decision`, relayed by the coordinator, was the literal
word: `merge`

OWNER_DECISION_138 = merge
DECIDED_AT_138 = 2026-09-12T13:36:41Z

## Idempotency (DEP-05)

```
$ gh pr view 138 --json state,mergeCommit,mergedAt,headRefOid
{"headRefOid":"88088071e02a7411800f504e06b1ded9d6891cc7","mergeCommit":null,"mergedAt":null,"state":"OPEN"}
```

State is OPEN, not MERGED — this is not a resumed run.

ALREADY_MERGED_138 = no

## Gate re-asserted after the decision

```
$ git fetch origin main
$ git rev-parse origin/main
293f0c2684641f5d4b2f5ed021b565656e38d48c
```

`origin/main` still equals MAIN_BEFORE_138.

```
$ gh pr view 138 --json state,headRefOid,mergeStateStatus
{"headRefOid":"88088071e02a7411800f504e06b1ded9d6891cc7","mergeStateStatus":"CLEAN","state":"OPEN"}
```

State OPEN, head still HEAD138, `mergeStateStatus` still CLEAN.

```
$ gh api "repos/YuSabo90002/typsphinx/commits/88088071e02a7411800f504e06b1ded9d6891cc7/check-runs?per_page=100" --jq '.check_runs[] | [.name, .status, .conclusion] | @tsv'
Test Python 3.12 on macos-latest	completed	success
Test Python 3.13 on windows-latest	completed	success
Test Python 3.13 on ubuntu-latest	completed	success
build-docs	completed	success
Test Python 3.12 on windows-latest	completed	success
Build Package	completed	success
Test Python 3.13 on macos-latest	completed	success
Lint and Format Check	completed	success
Test Python 3.12 on ubuntu-latest	completed	success
Integration Test - advanced	completed	success
Code Coverage	completed	success
Integration Test - basic	completed	success
Repo-wide link check (advisory)	completed	success
Type Check	completed	success
Repo-wide link check (advisory)	completed	success
```

All six required contexts still `success`. No difference from Task 1's gate — the merge proceeds.

## Merge (#138)

MERGE_STARTED_AT_138 = 2026-09-12T13:36:56Z

```
$ gh pr merge 138 --merge --match-head-commit "88088071e02a7411800f504e06b1ded9d6891cc7"
(no output; exit 0)
```

No `--admin`, `--auto`, `--squash`, `--rebase` or `--delete-branch` flag was passed.

## Main after the merge

```
$ gh pr view 138 --json state,mergeCommit,mergedAt,headRefOid
{"headRefOid":"88088071e02a7411800f504e06b1ded9d6891cc7","mergeCommit":{"oid":"cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a"},"mergedAt":"2026-09-12T13:37:03Z","state":"MERGED"}
```

MERGE_SHA_138 = cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
MERGED_AT_138 = 2026-09-12T13:37:03Z

```
$ git fetch origin main
   293f0c26..cf3305ce  main       -> origin/main
$ git rev-list --parents -n 1 cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a 293f0c2684641f5d4b2f5ed021b565656e38d48c 88088071e02a7411800f504e06b1ded9d6891cc7
```

Parents are exactly `MERGE_SHA_138 MAIN_BEFORE_138 HEAD138` — a two-parent merge commit.

```
$ git rev-parse origin/main
cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
```

`origin/main` now points at MERGE_SHA_138.

```
$ git diff --name-only 293f0c2684641f5d4b2f5ed021b565656e38d48c cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
pyproject.toml
uv.lock
```

Exactly `pyproject.toml` and `uv.lock` changed.

```
$ git show cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a:uv.lock | awk '/^name = "ruff"$/{getline; print; exit}'
version = "0.16.6"
```

The merged `uv.lock` pins ruff at RUFF_VERSION_138 (0.16.6).

**D-04 checks:**

```
$ git merge-base --is-ancestor cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a HEAD; echo "exit:$?"
exit:1
```

`exit:1` — MERGE_SHA_138 is NOT an ancestor of the milestone branch HEAD. The milestone branch did
not absorb `main`.

```
$ git diff --stat 6a687ca9e854d6f4aad16df78585855d85209de5 HEAD -- pyproject.toml uv.lock
(empty)
```

The milestone branch's own `pyproject.toml`/`uv.lock` are unchanged since BASE_67_02.

```
$ git merge-tree --write-tree --name-only origin/main HEAD; echo "exit:$?"
7419042a89d54461f94ed109714e5b90ae97406a
exit:0
```

REL12_POSTMERGE_EXIT = 0

## Dependabot after the merge

Snapshot taken at 2026-09-12T13:37:30Z, read-only — nothing acted on.

```
$ gh pr list --state open --author app/dependabot --json number,title,headRefName,headRefOid,createdAt,updatedAt
[{"number":142,"title":"chore(deps): bump mypy from 2.1.0 to 2.3.1", ...},
 {"number":141,"title":"chore(deps): bump pre-commit from 4.6.0 to 4.6.2", ...},
 {"number":140,"title":"chore(deps): bump sphinx-intl from 2.3.2 to 2.4.0", ...},
 {"number":139,"title":"chore(deps): bump tox from 4.56.1 to 4.61.4", ...},
 {"number":128,"title":"chore(deps): update docutils requirement from <0.23,>=0.21 to >=0.21,<0.24 in the sphinx-typst-stack group across 1 directory", "headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f", "updatedAt":"2026-09-07T00:07:47Z"},
 {"number":123,"title":"chore(deps-dev): update ruff requirement from <0.16,>=0.15 to >=0.15,<0.17", "headRefOid":"1c905bb80d388465e57280dc104cbd117442e28a", "updatedAt":"2026-08-03T20:09:21Z"}]
```

#138 no longer appears (correctly merged and dropped from the open list). #123 and #128 are both
still present, unchanged from their prior snapshots.

```
$ gh run list --workflow "Dependabot Updates" --limit 10 --json databaseId,displayTitle,status,conclusion,createdAt
[{"conclusion":"success","createdAt":"2026-09-12T10:38:38Z","databaseId":34688990474, ...},
 {"conclusion":"failure","createdAt":"2026-09-12T10:38:38Z","databaseId":34688990228, ...},
 ... (8 more rows, all createdAt before MERGED_AT_138)]
```

No Dependabot Updates run was created after MERGED_AT_138 (2026-09-12T13:37:03Z) at the time of
this snapshot.

```
$ gh run list --workflow=ci.yml --branch main --event push --limit 5 --json databaseId,headSha,status,conclusion
[{"conclusion":"","databaseId":34696925079,"headSha":"cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a","status":"in_progress"}, ...]
```

MERGE_SHA_138's own push-triggered CI run (`34696925079`) is `in_progress` at snapshot time.
Observational only — not waited on.

```
$ gh pr view 123 --json state,headRefOid,updatedAt
{"headRefOid":"1c905bb80d388465e57280dc104cbd117442e28a","state":"OPEN","updatedAt":"2026-08-03T20:09:21Z"}
$ gh pr view 128 --json state,headRefOid,updatedAt
{"headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f","state":"OPEN","updatedAt":"2026-09-07T00:07:47Z"}
```

Both #123 and #128 remain OPEN with unchanged `headRefOid`/`updatedAt`. 67-04 and 67-03 re-snapshot
before acting on either.

## Handoff to 67-04

#138 is merged into `main` at MERGE_SHA_138 = cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a. 67-04 closes
#123 as superseded behind its own `checkpoint:decision`, after reading #123's whole thread. Nothing
in this plan closed, commented on or `@dependabot`-commanded #123, #128 or #139–#142.

---

# Phase 67 Plan 04 — #123 (ruff, superseded by #138) Disposal Evidence

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0
$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3eb0138dbbf5e138
```

`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` ran to completion, installing
`ruff==0.15.20`, `uv==0.12.13`, `typsphinx==0.9.2` (editable, from this worktree) among the
resolved packages — this worktree's own `uv.lock` (the unmerged milestone lock), not `main`'s.

```
$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

BASE_67_04 = 61139be8fce6e83ca16f2f0683fc6e75816cb1f3

## Wave-2 gate

Read from this file's own prior sections (67-02), never from executor memory:

```
$ F=.planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-RUFF-EVIDENCE.md
$ sed -n 's/^OWNER_DECISION_138 = //p' "$F" | head -n 1
merge
$ sed -n 's/^MERGE_SHA_138 = //p' "$F" | head -n 1
cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
$ sed -n 's/^MERGED_AT_138 = //p' "$F" | head -n 1
2026-09-12T13:37:03Z
$ grep -c '^## HALT' "$F"
0
```

Live re-read of #138, not trusted from the file alone:

```
$ gh pr view 138 --json state,mergeCommit,mergedAt
{"mergeCommit":{"oid":"cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a"},"mergedAt":"2026-09-12T13:37:03Z","state":"MERGED"}
```

#138 is MERGED at MERGE_SHA_138 (`cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a`), read live and
matching the recorded key exactly. No `## HALT` heading exists anywhere in this file. This plan
runs entirely from these evidence keys and live GitHub state, never from executor memory of the
67-02 run — so an executor resumed after an interruption between the #138 merge and this #123
close would re-derive the identical facts and proceed the same way (the DEP-05 concurrency edge:
resumability).

## #123 re-snapshot

```
$ date -u +%FT%TZ
2026-09-12T13:47:02Z
```

SNAP_123_AT_67_04 = 2026-09-12T13:47:02Z

```
$ gh pr view 123 --json number,title,state,closed,closedAt,author,headRefName,headRefOid,baseRefName,updatedAt,labels,comments
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","closed":false,"closedAt":null,"comments":[{"id":"IC_kwDOQBRmjM8AAAABLybpkw","author":{"login":"dependabot"},"authorAssociation":"CONTRIBUTOR","body":"### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.","createdAt":"2026-07-27T00:07:03Z","includesCreatedEdit":false,"isMinimized":false,"minimizedReason":"","reactionGroups":[],"url":"https://github.com/YuSabo90002/typsphinx/pull/123#issuecomment-5086046611","viewerDidAuthor":false}],"headRefName":"dependabot/pip/ruff-gte-0.15-and-lt-0.17","headRefOid":"1c905bb80d388465e57280dc104cbd117442e28a","labels":[],"number":123,"state":"OPEN","title":"chore(deps-dev): update ruff requirement from <0.16,>=0.15 to >=0.15,<0.17","updatedAt":"2026-08-03T20:09:21Z"}
```

Compared with `67-PROOF-EVIDENCE.md` § D-02 re-snapshot (`SNAP_123_AT = 2026-09-12T13:20:35Z`):
`headRefOid` (`1c905bb80d388465e57280dc104cbd117442e28a`) — **unchanged**. `updatedAt`
(`2026-08-03T20:09:21Z`) — **unchanged**. Comment count (1, dependabot's own "labels could not be
found" comment) — **unchanged**. State is OPEN, so the "quote the closed-event actor and HALT"
branch does not apply.

HEAD123 = 1c905bb80d388465e57280dc104cbd117442e28a

## D-03 merits for #123

**The pip PR's shape.**

```
$ git fetch origin refs/pull/123/head
From https://github.com/YuSabo90002/typsphinx
 * branch              refs/pull/123/head -> FETCH_HEAD
$ git rev-parse FETCH_HEAD
1c905bb80d388465e57280dc104cbd117442e28a
```

`FETCH_HEAD` equals HEAD123.

```
$ git show --name-only --format='%H%n%an <%ae>%n%s' 1c905bb80d388465e57280dc104cbd117442e28a
1c905bb80d388465e57280dc104cbd117442e28a
dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
chore(deps-dev): update ruff requirement

pyproject.toml
```

The name list is exactly `pyproject.toml` — nothing else.

```
$ git show 1c905bb80d388465e57280dc104cbd117442e28a -- pyproject.toml
commit 1c905bb80d388465e57280dc104cbd117442e28a
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Tue Jul 28 20:59:54 2026 +0000

    chore(deps-dev): update ruff requirement

    Updates the requirements on [ruff](https://github.com/astral-sh/ruff) to permit the latest version.
    - [Release notes](https://github.com/astral-sh/ruff/releases)
    - [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
    - [Commits](https://github.com/astral-sh/ruff/compare/0.15.0...0.16.0)

    ---
    updated-dependencies:
    - dependency-name: ruff
      dependency-version: 0.16.0
      dependency-type: direct:development
    ...

    Signed-off-by: dependabot[bot] <support@github.com>

diff --git a/pyproject.toml b/pyproject.toml
index 82b1efc7..dda6bbaa 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -37,7 +37,7 @@ dev = [
     "tox>=4.56,<5",
     "tox-uv>=1.35,<2",
     "black>=26,<27",
-    "ruff>=0.15,<0.16",
+    "ruff>=0.15,<0.17",
     "mypy>=1.13,<3.0",
     "pre-commit>=3.0",
     "types-docutils>=0.21",
```

**The supersession.**

```
$ git show 1c905bb80d388465e57280dc104cbd117442e28a -- pyproject.toml | grep '^+.*ruff' | sed 's/^+ *//'
"ruff>=0.15,<0.17",
```

RUFF_LINE_123 = "ruff>=0.15,<0.17",

```
$ git show cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a:pyproject.toml | grep 'ruff>=' | sed 's/^ *//'
"ruff>=0.15,<0.17",
```

RUFF_LINE_MAIN = "ruff>=0.15,<0.17",

RUFF_LINE_123 and RUFF_LINE_MAIN are **equal**. `main` now carries exactly #123's proposed range,
with a valid lockfile, through the merged #138.

**#123's own CI.**

```
$ gh pr view 123 --json statusCheckRollup --jq '.statusCheckRollup[] | [.name, .conclusion] | @tsv'
Test Python 3.12 on ubuntu-latest	FAILURE
build-docs	FAILURE
Repo-wide link check (advisory)	SUCCESS
Repo-wide link check (advisory)	SUCCESS
Test Python 3.13 on ubuntu-latest	FAILURE
Test Python 3.12 on windows-latest	FAILURE
Test Python 3.13 on windows-latest	FAILURE
Test Python 3.12 on macos-latest	FAILURE
Test Python 3.13 on macos-latest	FAILURE
Lint and Format Check	FAILURE
Type Check	FAILURE
Code Coverage	FAILURE
Build Package	FAILURE
Integration Test - basic	CANCELLED
Integration Test - advanced	FAILURE
```

12 FAILURE, 1 CANCELLED, 2 SUCCESS (the two advisory link-check jobs) — matching the planning-time
census exactly. A `pyproject.toml`-only change dies at `uv sync --extra dev --locked`, so merging
#123 is not an option on the merits either.

**Back-reference.** See `## SC#3 merits for #138` and `## NIX-01 interaction and D-04 divergence`
above (this same file, 67-02's sections) — not restated here.

"CI is finally green" is not the merit here: #123's own CI is red at the install step, exactly as
it was at planning time. The merit is that `main` already carries #123's proposed `ruff` range,
through the merged #138, with a working lockfile.

## #123 thread

```
$ gh pr view 123 --json comments --jq '.comments[] | [.author.login, .createdAt, .body] | @tsv'
dependabot	2026-07-27T00:07:03Z	### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.
```

```
$ gh api --paginate repos/YuSabo90002/typsphinx/pulls/123/comments --jq 'length'
0
$ gh api --paginate repos/YuSabo90002/typsphinx/pulls/123/reviews --jq 'length'
0
```

One issue comment total (dependabot's own automated "labels could not be found" notice), zero PR
review comments, zero reviews. No non-dependabot author appears anywhere in the thread.

```
$ date -u +%FT%TZ
2026-09-12T13:47:32Z
```

THREAD_READ_AT_123 = 2026-09-12T13:47:32Z

## Tooling pre-flight (#123)

```
$ gh pr close --help | grep -n -- '--comment'
7:  -c, --comment string   Leave a closing comment
```

`--comment` is supported by the installed `gh`; no fallback needed.

## Draft comment for #123 (not yet approved)

DRAFT_COMMENT_123 = Superseded by #138.

One English line, per D-03's shape. Nothing has been posted; #123 remains untouched by this task.

## Owner decision (#123)

The owner's reply to the Task 2 `checkpoint:decision` (`gate="blocking-human"`), relayed verbatim
by the coordinator, was: `close as drafted`

OWNER_DECISION_123 = close
DECIDED_AT_123 = 2026-09-12T13:51:28Z

Per the reply, the approved text is `DRAFT_COMMENT_123` unedited:

APPROVED_COMMENT_123 = Superseded by #138.

This section is committed before any posting.
