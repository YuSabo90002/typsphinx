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
