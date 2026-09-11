# Phase 64 — Milestone Branch Push and 3-OS CI Evidence (SC#5)

## Branch census

Re-measured per constraint 9 — never trusted from the RESOLVED note.

```
$ git branch --list 'gsd/v0.9.3*' -v
+ gsd/v0.9.3-toolchain-and-dependency-update-repair 7afbf5b2 docs(64): mark phase 64 wave 3 executing

$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5

$ git ls-remote --heads origin | grep -c '0\.9\.3'
0
```

No `gsd/v0.9.3-milestone` decoy branch exists in this worktree's local branch list — only the
canonical `gsd/v0.9.3-toolchain-and-dependency-update-repair`. No `merge-base --is-ancestor` check
or deletion was needed; nothing decoy-shaped to correct this time. The pre-push origin count for
`0.9.3` is 0, confirmed above.

## Tip identity and lock check

```
$ git rev-parse HEAD
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5

$ git rev-parse gsd/v0.9.3-toolchain-and-dependency-update-repair
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5
```

HEAD and the canonical branch pointer are identical before this plan's own commits — this worktree
was cut from the canonical tip after waves 1 and 2 merged, and no commit had yet been made in this
plan at the moment of measurement.

**`PUSHED_SHA = 7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`**

```
$ git log --oneline -1
7afbf5b2 docs(64): mark phase 64 wave 3 executing

$ grep -c typsphinx-fhs-run flake.nix
3
```

`flake.nix` carries 3 matches of `typsphinx-fhs-run` — the Phase 64 wave 1 deliverable is present on
this tip.

Pre-dispatch lock check (every `ci.yml` job's first substantive step):

```
$ uv sync --extra dev --locked
Resolved 89 packages in 0.69ms
Checked 79 packages in 0.60ms
$ echo "exit:$?"
exit:0
```

Exit 0, no drift — the lockfile is consistent, so none of the twelve CI lanes will fail at the
install step before any test/lint/type signal exists.

## Push

Pushed the canonical branch, and only it, with tracking, from this worktree:

```
$ git push -u origin gsd/v0.9.3-toolchain-and-dependency-update-repair
remote:
remote: Create a pull request for 'gsd/v0.9.3-toolchain-and-dependency-update-repair' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/gsd/v0.9.3-toolchain-and-dependency-update-repair
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.3-toolchain-and-dependency-update-repair -> gsd/v0.9.3-toolchain-and-dependency-update-repair
branch 'gsd/v0.9.3-toolchain-and-dependency-update-repair' set up to track 'origin/gsd/v0.9.3-toolchain-and-dependency-update-repair'.
```

GitHub's "Create a pull request" hint appeared, as it does on every first push of a new branch. It
was **not** acted on — no pull request was opened, per this plan's binding prohibition. No `--force`,
no `--tags`, no other ref was pushed.

Tracking verification:

```
$ git rev-parse --abbrev-ref 'gsd/v0.9.3-toolchain-and-dependency-update-repair@{upstream}'
origin/gsd/v0.9.3-toolchain-and-dependency-update-repair

$ git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5	refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair
```

The upstream branch name is exactly `origin/gsd/v0.9.3-toolchain-and-dependency-update-repair`, and
origin's head SHA for that ref equals `PUSHED_SHA`.

## Dispatch

`ci.yml`'s `push`/`pull_request` triggers are scoped to `main`/`develop`, so the push alone ran
nothing. Dispatched exactly once:

```
$ gh workflow run CI --ref gsd/v0.9.3-toolchain-and-dependency-update-repair
https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267
```

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --limit 1 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-11T15:52:41Z","databaseId":34618719267,"headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5","status":"queued","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267"}]
```

- **Run id:** `34618719267`
- **Run URL:** https://github.com/YuSabo90002/typsphinx/actions/runs/34618719267
- **Dispatched head SHA (from the run's own JSON):** `7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`
- **`PUSHED_SHA`:** `7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5`

The two are equal, and the run was created after the push completed (both within the same
provisioning session). No tag points at the pushed tip (`git tag --points-at
7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5` returned empty), and origin carries no decoy branch
(`git ls-remote --heads origin | grep -c 'gsd/v0.9.3-milestone'` = 0). No `release.yml` route was
touched by any command in this task.

## Baseline framing

`flake.nix` is invisible to CI (ROADMAP constraint 10 — no workflow references `nix` or `flake`),
so this run's value is not proving the FHS wrapper works in CI; it is putting the milestone branch
on `origin` with a known pre-revert baseline. This plan's own evidence commit (this file) lands on
the worktree branch **after** the push recorded above — it is `.planning/`-only, which no `ci.yml`
job reads, so it does not need a second dispatch to be covered by this run's result.

The pushed tip (`7afbf5b2`) is the phase's code-bearing tip **as of this push**. A later
`flake.nix`-only gap-closure commit (addressing 64-02's recorded `libz.so.1` finding) is anticipated
by owner decision (2026-09-12, recorded in `STATE.md`) and will land after this evidence file, on
this same worktree branch, before merge. Since `flake.nix` carries zero CI coverage either way, this
dispatched run remains a valid pre-revert baseline for Phase 65's TOX-04 regardless of that later
commit — the claim made here is scoped to *this push*, not to phase finality.
