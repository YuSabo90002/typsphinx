executor worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout is never touched.

**Measured shape:** the config push to `main` triggered a `uv`-ecosystem Dependabot Updates run within 8 seconds (no wait for the Monday schedule, D-03 = `config-push`-shaped), but that run's overall conclusion is `failure` — one dependency (`docutils`, the `sphinx-typst-stack` group) could not be resolved for the `python_full_version >= '3.15'` split, while five other `uv`-ecosystem dependencies (`mypy`, `pre-commit`, `sphinx-intl`, `tox`, `ruff`) resolved cleanly and opened PRs (#138–#142) in the same job. Per the plan's Task 1 step 5, a non-`success` conclusion halts this task for the owner before Task 2 proceeds.

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a22ffeff982450a46

$ git rev-parse --abbrev-ref HEAD
worktree-agent-a22ffeff982450a46
```

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
... 81 packages installed, including uv==0.12.13, tox==4.56.1

$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002
```

The provisioning line ran verbatim (CLAUDE.md, "Worktree-isolated execution"). This plan only ever
runs `git` and `gh` afterward.

## Wave-2 gate

Keys read from `66-MAIN-PR-EVIDENCE.md`:

```
OWNER_DECISION = merge
MERGE_SHA = 293f0c2684641f5d4b2f5ed021b565656e38d48c
MERGED_AT = 2026-09-12T10:38:30Z
CONFIG_BLOB = a58ea1e25254138ff6967438feb948c1a0cc7064

$ grep -c '^## HALT' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-MAIN-PR-EVIDENCE.md
0
```

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git merge-base --is-ancestor 293f0c2684641f5d4b2f5ed021b565656e38d48c origin/main; echo "exit:$?"
exit:0

$ git rev-parse origin/main:.github/dependabot.yml
a58ea1e25254138ff6967438feb948c1a0cc7064
```

`MERGE_SHA` is an ancestor of `origin/main`, and `origin/main:.github/dependabot.yml` equals
`CONFIG_BLOB`. Gate holds.

## Poll 1 (D-03)

```
POLL1_START = 2026-09-12T10:46:10Z
```

Bound: 30 minutes after the later of `MERGED_AT` (`2026-09-12T10:38:30Z`) and `POLL1_START`
(`2026-09-12T10:46:10Z`) — i.e. `2026-09-12T11:16:10Z`. Interval: 60 seconds.

```
$ gh run list --workflow "Dependabot Updates" --limit 20 --json databaseId,displayTitle,headSha,status,conclusion,createdAt
```

Every row from this query whose `createdAt` is later than `MERGED_AT` (`2026-09-12T10:38:30Z`):

| databaseId | displayTitle | headSha | status | conclusion | createdAt |
|---|---|---|---|---|---|
| 34688990474 | github_actions in /. - Update #1572468103 | 293f0c2684641f5d4b2f5ed021b565656e38d48c | completed | success | 2026-09-12T10:38:38Z |
| 34688990228 | uv in /. - Update #1572468102 | 293f0c2684641f5d4b2f5ed021b565656e38d48c | completed | failure | 2026-09-12T10:38:38Z |

Both were already visible on the first query at `POLL1_START` — no additional polling interval was
needed to observe them (they started within 8 seconds of the merge, per 66-02's own last read). The
`uv` run had already reached `status: completed` by the time this poll ran.

```
$ gh pr list --state all --author app/dependabot --limit 50 --json number,title,headRefName,headRefOid,state,labels,createdAt,closedAt
```

Rows whose `headRefName` starts with `dependabot/uv/` (all created after `MERGED_AT`):

| number | title | headRefName | state | createdAt |
|---|---|---|---|---|
| 142 | chore(deps): bump mypy from 2.1.0 to 2.3.1 | dependabot/uv/mypy-2.3.1 | OPEN | 2026-09-12T10:40:18Z |
| 141 | chore(deps): bump pre-commit from 4.6.0 to 4.6.2 | dependabot/uv/pre-commit-4.6.2 | OPEN | 2026-09-12T10:40:11Z |
| 140 | chore(deps): bump sphinx-intl from 2.3.2 to 2.4.0 | dependabot/uv/sphinx-intl-2.4.0 | OPEN | 2026-09-12T10:40:04Z |
| 139 | chore(deps): bump tox from 4.56.1 to 4.61.4 | dependabot/uv/tox-4.61.4 | OPEN | 2026-09-12T10:39:58Z |
| 138 | chore(deps): bump ruff from 0.15.20 to 0.16.6 | dependabot/uv/ruff-0.16.6 | OPEN | 2026-09-12T10:39:49Z |

Five `dependabot/uv/` PRs opened, all inside the `uv in /. - Update #1572468102` job's window
(10:39:49Z–10:40:18Z, before the job's failure at 10:40:54Z). None was touched by this task —
listed only.

```
POLL1_END = 2026-09-12T10:47:46Z
```

## uv update run

```
UV_RUN_ID = 34688990228

$ gh run view 34688990228 --json status,conclusion,displayTitle,headSha,createdAt,url
{"conclusion":"failure","createdAt":"2026-09-12T10:38:38Z","displayTitle":"uv in /. - Update #1572468102","headSha":"293f0c2684641f5d4b2f5ed021b565656e38d48c","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34688990228"}
```

`createdAt` (`2026-09-12T10:38:38Z`) is later than `MERGED_AT`; `headSha` equals `MERGE_SHA`; the
run is the earliest (and only) `uv`-ecosystem run created after the merge.

```
$ gh run view 34688990228 --log | grep -n "Pulling image ghcr.io/dependabot/dependabot-updater-uv"
50:Dependabot	Run Dependabot	2026-09-12T10:38:44.2044610Z Pulling image ghcr.io/dependabot/dependabot-updater-uv:ebbc4f6acba15d63b83f2211074ddc74e979fcfd (attempt 1)...
```

```
UPDATER_UV_IMAGE = ghcr.io/dependabot/dependabot-updater-uv:ebbc4f6acba15d63b83f2211074ddc74e979fcfd
```

```
$ gh run view 34688990228 --log | grep -icE 'error|limit'
11
```

The first 20 (all 11) matching lines, verbatim:

```
70:updater | 2026/09/12 10:39:14 INFO <job_1572468102> Job definition: {"job":{"command":"version","allowed-updates":[{"dependency-type":"direct","update-type":"all"}],... ,"dependency-groups":[{"name":"sphinx-typst-stack","rules":{"patterns":["sphinx*","docutils*","typst*"],"exclude-patterns":["sphinx-autodoc-typehints","sphinx-intl"]}}], ... ,"package-manager":"uv", ... }}
322:  proxy | 2026/09/12 10:39:32 [122] POST /update_jobs/1572468102/record_update_job_error
323:  proxy | 2026/09/12 10:39:32 [122] 204 /update_jobs/1572468102/record_update_job_error
324:updater | 2026/09/12 10:39:32 INFO <job_1572468102> Handled error whilst updating docutils: dependency_file_not_resolvable {message: "× No solution found when resolving dependencies for split (markers:\n  │ python_full_version >= '3.15'):\n  ╰─▶ Because sphinx>=9.1.0 depends on docutils>=0.21,<0.23 and your project\n      depends on docutils==0.23, we can conclude that sphinx>=9.1.0 and your\n      project are incompatible.\n      And because your project depends on sphinx>=9.1 and your project\n      requires typsphinx[dev], we can conclude that your project's\n      requirements are unsatisfiable.\n\nhint: While the active Python version is 3.12, the resolution failed for other Python versions supported by your project. Consider limiting your project's supported Python versions using `requires-python`."}
1682:Dependabot encountered '1' error(s) during execution, please check the logs for more details.
1686:| Dependency | Error Type                     | Error Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
1689:|            |                                |   "message": "× No solution found when resolving dependencies for split (markers:\n  │ python_full_version >= '3.15'):\n  ╰─▶ Because sphinx>=9.1.0 depends on docutils>=0.21,<0.23 and your project\n      depends on docutils==0.23, we can conclude that sphinx>=9.1.0 and your\n      project are incompatible.\n      And because your project depends on sphinx>=9.1 and your project\n      requires typsphinx[dev], we can conclude that your project's\n      requirements are unsatisfiable.\n\nhint: While the active Python version is 3.12, the resolution failed for other Python versions supported by your project. Consider limiting your project's supported Python versions using `requires-python`." |
1692:Failure running container 5b2df41591b6a4d037f4f5f0f30a8dffca7f0b23bed3e5602f59e35f559d7c7a: Error: Command failed with exit code 1: /bin/sh -c $DEPENDABOT_HOME/dependabot-updater/bin/run update_files
1697:##[error]Dependabot encountered an error performing the update
1699:Error: The updater encountered one or more errors.
1702:🤖 ~ finished: error reported to Dependabot ~
```

```
D03_POLL1 = uv-run-seen
```

A `uv`-ecosystem Dependabot Updates run was created within 8 seconds of `MERGED_AT` — no polling
wait was needed, the run and its five successful PR outputs were already visible at `POLL1_START`.

## uv update job conclusion (HALT resolved by owner ruling, AMENDED 2026-09-12)

This heading was originally `## HALT: uv update job failed`. The owner resolved that halt with
this ruling, relayed by the coordinator:

> Owner ruling on your HALT checkpoint: option A (proceed). The owner-approved amendment is
> committed on the milestone branch as `d350d249` (AMENDED 2026-09-12 blocks in `66-03-PLAN.md`
> and `66-04-PLAN.md`).

The body below is unchanged from the original halted text.

`UV_RUN_ID`'s conclusion is `failure`, not `success`. Per the plan's Task 1 step 5, this halts the
task at a blocking-human checkpoint rather than proceeding to Task 2's normal flow.

**What actually happened, measured — more nuanced than a bare "config rejected":** The job
(`command: version`, `package-manager: uv`, dependency-groups including `sphinx-typst-stack`
patterns `sphinx*`/`docutils*`/`typst*`) pulled the updater image successfully
(`UPDATER_UV_IMAGE` above), evaluated dependencies, and:

- **Succeeded** on five individual (ungrouped) dependencies, opening `dependabot/uv/` PRs #138
  (ruff), #139 (tox), #140 (sphinx-intl), #141 (pre-commit), #142 (mypy) — all recorded above under
  "Poll 1 (D-03)".
- **Failed** on `docutils` (part of the `sphinx-typst-stack` group) with `dependency_file_not_resolvable`:

```
× No solution found when resolving dependencies for split (markers:
  │ python_full_version >= '3.15'):
  ╰─▶ Because sphinx>=9.1.0 depends on docutils>=0.21,<0.23 and your project
      depends on docutils==0.23, we can conclude that sphinx>=9.1.0 and your
      project are incompatible.
      And because your project depends on sphinx>=9.1 and your project
      requires typsphinx[dev], we can conclude that your project's
      requirements are unsatisfiable.

hint: While the active Python version is 3.12, the resolution failed for other Python versions
supported by your project. Consider limiting your project's supported Python versions using
`requires-python`.
```

- The job's overall `conclusion` on GitHub Actions is `failure` because of this one dependency error
  (`Dependabot encountered '1' error(s) during execution`), even though five other dependencies in
  the same job succeeded.

**What this is not:** `pyproject.toml` pins `docutils>=0.21,<0.23` (measured:
`grep -n docutils pyproject.toml` line 29) — there is no `docutils==0.23` pin anywhere in this
repository's own `pyproject.toml`. The `python_full_version >= '3.15'` split and the
`docutils==0.23` constraint the error names come from `uv.lock`'s own resolution-marker split
(`requires-python = ">=3.12"`, `python_full_version >= '3.15'` and `< '3.15'` fork markers at
`uv.lock:5-6`) and whatever transitive graph uv computed for the high-Python-version fork — not
from any value this phase, or Phase 66 generally, wrote. Nothing under `typsphinx/` or
`pyproject.toml` was edited to investigate or fix this; the plan's prohibitions and ROADMAP
constraint 13 forbid it, and this plan's scope is observation only.

**Nothing was edited, rerun, cancelled or triggered in reaction to this finding.** The five
succeeded PRs are listed (not touched) above; #123 and #128 are read again in Task 3, unaffected by
this run.

### `UV_RUN_ACCEPTED` — amended acceptance test (AMENDED 2026-09-12)

Per the owner-approved amendment, the run's Actions `conclusion` is recorded but no longer required
to be `success`. `UV_RUN_ACCEPTED = yes` only after verifying all four conditions directly from
`gh`:

```
UV_RUN_CONCLUSION = failure
```

(a) **Title begins `uv in /`:** `displayTitle` = `"uv in /. - Update #1572468102"` — confirmed above
under "uv update run".

(b) **Log names a `dependabot-updater-uv` image:** confirmed above — `UPDATER_UV_IMAGE =
ghcr.io/dependabot/dependabot-updater-uv:ebbc4f6acba15d63b83f2211074ddc74e979fcfd`.

(c) **At least one `dependabot/uv/` PR was opened:** confirmed above — five (#138, #139, #140,
#141, #142), verified again in "uv pull requests" below (branch prefix and author both re-checked
via `gh`).

(d) **Every row of the log's error table is a per-dependency error type, none a configuration
error.** The "Dependencies failed to update" table (quoted above under "uv update run") has exactly
one row:

```
| Dependency | Error Type                     |
| docutils   | dependency_file_not_resolvable |
```

`dependency_file_not_resolvable` is a per-dependency resolution error (uv could not solve a version
constraint), not a configuration-parse error (which would instead show as a job-level
`dependabot.yml`-parsing failure before any dependency processing began — not observed here; the
job reached `Finished job processing` at `10:40:54.2651412Z` and printed a full per-ecosystem
"Changes to Dependabot Pull Requests" table, meaning the config was read and acted on ecosystem-wide).

The "Changes to Dependabot Pull Requests" table, quoted verbatim from the log (11 `created` rows —
more than the 5 PRs that actually exist; see the PR-limit finding below):

```
+----------------------------------------------------------------------+
|                 Changes to Dependabot Pull Requests                  |
+---------+------------------------------------------------------------+
| created | ruff ( from 0.15.20 to 0.16.6 )                            |
| created | tox ( from 4.56.1 to 4.61.4 )                              |
| created | sphinx-intl ( from 2.3.2 to 2.4.0 )                        |
| created | pre-commit ( from 4.6.0 to 4.6.2 )                         |
| created | mypy ( from 2.1.0 to 2.3.1 )                               |
| created | types-docutils ( from 0.22.3.20260518 to 0.23.0.20260827 ) |
| created | sphinx-autodoc-typehints ( from 3.0.1 to 3.13.6 )          |
| created | twine ( from 6.2.0 to 7.0.0 )                              |
| created | tox-uv-bare ( from 1.35.2 to 1.36.0 )                      |
| created | build ( from 1.5.0 to 1.6.0 )                              |
| created | pypdf ( from 6.14.2 to 6.18.0 )                            |
+---------+------------------------------------------------------------+
```

All four conditions hold:

```
UV_RUN_ACCEPTED = yes
```

**DEP-03 grouping observation (recorded, not fixed):** the log lists 11 `create_pull_request`
proxy calls (one per dependency the job decided to update), but only the first 5 (ruff, tox,
sphinx-intl, pre-commit, mypy) resulted in an actual PR (#138–#142) — `types-docutils`,
`sphinx-autodoc-typehints`, `twine`, `tox-uv-bare`, `build` and `pypdf` were not opened. This
matches the owner's Dependabot-tab read below ("Dependabot cannot open any more pull requests ...
Affected #138 and 4 more") and is consistent with `open-pull-requests-limit: 5` in
`.github/dependabot.yml` being honored under the `uv` ecosystem exactly as it was under `pip` —
carried across unchanged, as D-06 specified. This is Phase 67 SC#2 / DEP-03 input: the limit is
observed to bind under `uv`, same as it did for `pip`. The separate `docutils`
`dependency_file_not_resolvable` failure is the `sphinx-typst-stack` group's own resolution
conflict — the same group PR #128 already proposes widening (`<0.23` → `<0.24`) — recorded here as
a live data point for Phase 67's disposal of #128, not resolved by this phase.

## Owner Dependabot-tab read (D-04)

The owner's Task 2 reply, verbatim (written in Japanese; relayed by the coordinator):

> A
> Version update 1572468102 Errored with the message "Dependabot cannot open any more pull
> requests" and 1 other error Affected #138 and 4 more
> ただこれはPRを5以上開こうとしたからのやつだよね

(English gloss of the last line, for record only, not part of the verbatim quote: "but this one is
from trying to open 5 or more PRs, right?")

The owner did not report the "Last checked" text, and did not click "Check for updates".

```
OWNER_TAB_ANNOTATION = Version update 1572468102 Errored with the message "Dependabot cannot open any more pull requests" and 1 other error Affected #138 and 4 more
OWNER_TAB_CONFIG_ERROR = none
CLICKED_AT = no
```

Basis for `OWNER_TAB_CONFIG_ERROR = none`: the annotation names the open-PR-limit error (a
runtime/PR-creation limit, not a config-parse error) plus "1 other error" — the log's own error
table (above) shows that other error is `docutils` `dependency_file_not_resolvable`, also not a
configuration error. Neither of the two errors the owner or the log names is a `dependabot.yml`
parsing/configuration error. Last-checked: not reported by owner.

## Poll 2 (D-03)

Not applicable — `CLICKED_AT = no`; the owner did not click "Check for updates", so no second poll
window runs (Task 1's poll already found the `uv` run).

## D-03 branch

GitHub's own wording is ambiguous here (`about-the-dependabot-yml-file.md:50`, quoted per
`66-RESEARCH.md:521`): dependabot "begins monitoring the specified package ecosystems according to
your defined schedules" when the config changes — wording that could mean either "starts
monitoring going forward, on schedule" or "starts a run right away." Observed here: the latter. The
`uv` run (`UV_RUN_ID = 34688990228`) was created 8 seconds after `MERGED_AT`, with no click from the
owner (`CLICKED_AT = no`).

```
D03_BRANCH = config-push
```

## Post-merge dependabot runs

Every Dependabot Updates run created after `MERGED_AT` (`2026-09-12T10:38:30Z`), all now
`completed`:

```
$ gh run list --workflow "Dependabot Updates" --limit 20 --json databaseId,displayTitle,headSha,status,conclusion,createdAt --jq '[.[] | select(.createdAt > "2026-09-12T10:38:30Z")]'
[{"conclusion":"success","createdAt":"2026-09-12T10:38:38Z","databaseId":34688990474,"displayTitle":"github_actions in /. - Update #1572468103","headSha":"293f0c2684641f5d4b2f5ed021b565656e38d48c","status":"completed"},{"conclusion":"failure","createdAt":"2026-09-12T10:38:38Z","databaseId":34688990228,"displayTitle":"uv in /. - Update #1572468102","headSha":"293f0c2684641f5d4b2f5ed021b565656e38d48c","status":"completed"}]
```

| databaseId | displayTitle | conclusion | createdAt |
|---|---|---|---|
| 34688990474 | github_actions in /. - Update #1572468103 | success | 2026-09-12T10:38:38Z |
| 34688990228 | uv in /. - Update #1572468102 | failure | 2026-09-12T10:38:38Z |

Both runs are `completed`. No run was rerun, cancelled or triggered by this task.

## D-02 post-merge snapshot

Both PRs read only, after the first post-merge dependabot runs completed; neither was commented on,
closed, labeled, or sent an `@dependabot` command.

```
$ date -u +%FT%TZ
2026-09-12T10:58:41Z

$ gh pr view 123 --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null,"comments":[{"id":"IC_kwDOQBRmjM8AAAABLybpkw","author":{"login":"dependabot"},"authorAssociation":"CONTRIBUTOR","body":"### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.","createdAt":"2026-07-27T00:07:03Z","includesCreatedEdit":false,"isMinimized":false,"minimizedReason":"","reactionGroups":[],"url":"https://github.com/YuSabo90002/typsphinx/pull/123#issuecomment-5086046611","viewerDidAuthor":false}],"headRefName":"dependabot/pip/ruff-gte-0.15-and-lt-0.17","headRefOid":"1c905bb80d388465e57280dc104cbd117442e28a","labels":[],"number":123,"state":"OPEN","updatedAt":"2026-08-03T20:09:21Z"}
```

```
$ date -u +%FT%TZ
2026-09-12T10:58:45Z

$ gh pr view 128 --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null,"comments":[{"id":"IC_kwDOQBRmjM8AAAABM56Sgw","author":{"login":"dependabot"},"authorAssociation":"CONTRIBUTOR","body":"### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.","createdAt":"2026-08-03T00:06:15Z","includesCreatedEdit":false,"isMinimized":false,"minimizedReason":"","reactionGroups":[],"url":"https://github.com/YuSabo90002/typsphinx/pull/128#issuecomment-5160997507","viewerDidAuthor":false}],"headRefName":"dependabot/pip/sphinx-typst-stack-12b5b89b5a","headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f","labels":[],"number":128,"state":"OPEN","updatedAt":"2026-09-07T00:07:47Z"}
```

Both PRs are `OPEN`, unchanged from 66-02's pre-merge snapshot (same `headRefOid`, same
`updatedAt`, same single dependabot "labels could not be found" comment each — no new comment
appeared after `MERGED_AT`).

```
$ gh api user --jq .login
YuSabo90002
```

```
ME = YuSabo90002
```

Owner-authored comments on #123/#128 with `createdAt` later than `DECIDED_AT`
(`2026-09-12T10:38:08Z`):

```
$ gh api repos/YuSabo90002/typsphinx/issues/123/events --jq '[.[] | select(.actor.login == "YuSabo90002" and .created_at > "2026-09-12T10:38:08Z")] | length'
0

$ gh api repos/YuSabo90002/typsphinx/issues/128/events --jq '[.[] | select(.actor.login == "YuSabo90002" and .created_at > "2026-09-12T10:38:08Z")] | length'
0
```

Zero owner-authored comments and zero owner-authored timeline events on either PR after
`DECIDED_AT`. **Neither PR was closed.** Any close dependabot might perform in the future is a
mechanical close for Phase 67 to cite as evidence, never DEP-05's disposal on the merits (D-02,
ROADMAP constraint 4) — not applicable this task since neither PR closed.

## uv pull requests

```
$ gh pr list --state all --author app/dependabot --limit 50 --json number,title,headRefName,headRefOid,state,labels,createdAt,closedAt
```

Every dependabot PR created after `MERGED_AT` (`2026-09-12T10:38:30Z`), whatever its ecosystem
prefix:

| number | title | headRefName | state | createdAt |
|---|---|---|---|---|
| 138 | chore(deps): bump ruff from 0.15.20 to 0.16.6 | dependabot/uv/ruff-0.16.6 | OPEN | 2026-09-12T10:39:49Z |
| 139 | chore(deps): bump tox from 4.56.1 to 4.61.4 | dependabot/uv/tox-4.61.4 | OPEN | 2026-09-12T10:39:58Z |
| 140 | chore(deps): bump sphinx-intl from 2.3.2 to 2.4.0 | dependabot/uv/sphinx-intl-2.4.0 | OPEN | 2026-09-12T10:40:04Z |
| 141 | chore(deps): bump pre-commit from 4.6.0 to 4.6.2 | dependabot/uv/pre-commit-4.6.2 | OPEN | 2026-09-12T10:40:11Z |
| 142 | chore(deps): bump mypy from 2.1.0 to 2.3.1 | dependabot/uv/mypy-2.3.1 | OPEN | 2026-09-12T10:40:18Z |

No `dependabot/github_actions/` or other-ecosystem PR was created after `MERGED_AT` in this query
(the `github_actions in /.` run at 10:38:38Z found nothing to update — no PR from it appears in the
list). Only the pre-existing #128 (`dependabot/pip/sphinx-typst-stack-…`) and #123
(`dependabot/pip/ruff-…`) are the other open dependabot PRs, both created well before `MERGED_AT`
and both untouched by this task.

Each `dependabot/uv/` PR tabulated (D-02 / Phase 67 SC#2 input — recorded, not judged): #123's
`closedAt` is `null` and #128's `closedAt` is `null`, so both are still open, and every uv PR below
was created after both — meaning every one opened "while #123 was still open" and "while #128 was
still open":

| number | title | branch | state | labels | createdAt | opened while #123 open | opened while #128 open |
|---|---|---|---|---|---|---|---|
| 138 | bump ruff 0.15.20→0.16.6 | dependabot/uv/ruff-0.16.6 | OPEN | [] | 2026-09-12T10:39:49Z | yes | yes |
| 139 | bump tox 4.56.1→4.61.4 | dependabot/uv/tox-4.61.4 | OPEN | [] | 2026-09-12T10:39:58Z | yes | yes |
| 140 | bump sphinx-intl 2.3.2→2.4.0 | dependabot/uv/sphinx-intl-2.4.0 | OPEN | [] | 2026-09-12T10:40:04Z | yes | yes |
| 141 | bump pre-commit 4.6.0→4.6.2 | dependabot/uv/pre-commit-4.6.2 | OPEN | [] | 2026-09-12T10:40:11Z | yes | yes |
| 142 | bump mypy 2.1.0→2.3.1 | dependabot/uv/mypy-2.3.1 | OPEN | [] | 2026-09-12T10:40:18Z | yes | yes |

Author and branch re-verified individually via `gh` for every candidate:

```
$ gh pr view 138 --json headRefName,author -q '[.headRefName, .author.login] | @tsv'
dependabot/uv/ruff-0.16.6	app/dependabot
$ gh pr view 139 --json headRefName,author -q '[.headRefName, .author.login] | @tsv'
dependabot/uv/tox-4.61.4	app/dependabot
$ gh pr view 140 --json headRefName,author -q '[.headRefName, .author.login] | @tsv'
dependabot/uv/sphinx-intl-2.4.0	app/dependabot
$ gh pr view 141 --json headRefName,author -q '[.headRefName, .author.login] | @tsv'
dependabot/uv/pre-commit-4.6.2	app/dependabot
$ gh pr view 142 --json headRefName,author -q '[.headRefName, .author.login] | @tsv'
dependabot/uv/mypy-2.3.1	app/dependabot
```

Every candidate's `headRefName` starts with `dependabot/uv/` and its author is `app/dependabot`.

```
UV_PR_CANDIDATES = 138 139 140 141 142
```

Non-empty — A-DEP-01 holds. None of these five PRs, nor #123 or #128, was merged, approved, closed,
commented on, labeled, or sent an `@dependabot` command by this phase.

---

*Task 3 complete. `D03_BRANCH = config-push`; `UV_RUN_ACCEPTED = yes`; `OWNER_TAB_ANNOTATION` and
`OWNER_TAB_CONFIG_ERROR = none` recorded from the owner's Task 2 reply; #123/#128 unchanged
post-merge; five open `dependabot/uv/` PRs (#138–#142) available as 66-04's candidates.*

---

# 66-04: SC#1 same-commit read, D-05 legs 1–2, D-06, requirement closure

executor worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout is never
touched.

SC1_PR = 138
SC1_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a6b565b111054d94c
```

`pwd -P` lies under `/home/yuta/Documents/typsphinx/.claude/worktrees/`.

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.58ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a6b565b111054d94c
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a6b565b111054d94c
Prepared 1 package in 455ms
Installed 81 packages in 51ms
 ... (81 packages, including uv==0.12.13, tox==4.56.1, pytest==9.1.1)
```

Provisioning ran verbatim (CLAUDE.md, "Worktree-isolated execution"). Task 2 runs `uv` from this
worktree's own `.venv`.

## Wave-3 gate

```
$ sed -n 's/^UV_PR_CANDIDATES = //p' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md
138 139 140 141 142

$ sed -n 's/^UV_RUN_ID = //p' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md
34688990228

$ sed -n 's/^UPDATER_UV_IMAGE = //p' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md
ghcr.io/dependabot/dependabot-updater-uv:ebbc4f6acba15d63b83f2211074ddc74e979fcfd

$ sed -n 's/^D03_BRANCH = //p' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md
config-push

$ grep -c '^OWNER_TAB_ANNOTATION = ' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md
1

$ grep -c '^## HALT' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md
0

$ grep -c '^## HALT' .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-MAIN-PR-EVIDENCE.md
0
```

All five keys present and non-empty (`UV_PR_CANDIDATES`, `UV_RUN_ID`, `UPDATER_UV_IMAGE`,
`D03_BRANCH`, `OWNER_TAB_ANNOTATION`), and neither evidence file carries a `## HALT` heading. Gate
holds.

## Same-commit classification

Re-listed with 66-03's own query — no `dependabot/uv/` PR is new since 66-03; the five candidates
are exactly `UV_PR_CANDIDATES`:

```
$ gh pr list --state all --author app/dependabot --limit 50 --json number,title,headRefName,headRefOid,state,labels,createdAt,closedAt
```

(full JSON recorded; the five open `dependabot/uv/` rows are #138–#142, unchanged from 66-03's
census; #123 and #128 remain the only other open dependabot PRs, both `pip`-ecosystem, both
unaffected by this task.)

For each open `dependabot/uv/` PR, ascending, `gh pr view` (verbatim JSON), `git fetch
origin refs/pull/<n>/head` with a `FETCH_HEAD` == `headRefOid` assertion, then `git show
--name-only --format='%H%n%an <%ae>%n%s'` on the head commit:

### #138 — `dependabot/uv/ruff-0.16.6`

```
$ gh pr view 138 --json number,title,state,author,headRefName,headRefOid,baseRefName,createdAt,labels,commits,files
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","commits":[{"authoredDate":"2026-09-12T10:39:48Z","oid":"88088071e02a7411800f504e06b1ded9d6891cc7", ...}],"createdAt":"2026-09-12T10:39:49Z","files":[{"path":"pyproject.toml","additions":1,"deletions":1,"changeType":"MODIFIED"},{"path":"uv.lock","additions":22,"deletions":22,"changeType":"MODIFIED"}],"headRefName":"dependabot/uv/ruff-0.16.6","headRefOid":"88088071e02a7411800f504e06b1ded9d6891cc7","labels":[],"number":138,"state":"OPEN","title":"chore(deps): bump ruff from 0.15.20 to 0.16.6"}

$ git fetch origin refs/pull/138/head
 * branch              refs/pull/138/head -> FETCH_HEAD

$ git rev-parse FETCH_HEAD
88088071e02a7411800f504e06b1ded9d6891cc7
```

`FETCH_HEAD` equals `headRefOid`.

```
$ git show --name-only --format='%H%n%an <%ae>%n%s' 88088071e02a7411800f504e06b1ded9d6891cc7
88088071e02a7411800f504e06b1ded9d6891cc7
dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
chore(deps): bump ruff from 0.15.20 to 0.16.6

pyproject.toml
uv.lock
```

Name list: `pyproject.toml`, `uv.lock` — **class BOTH**. One commit.

### #139 — `dependabot/uv/tox-4.61.4`

```
$ gh pr view 139 --json ... commits,files
headRefOid = 49235270a04daaef43c9ec713b73862f5039592e, files: [uv.lock only]

$ git fetch origin refs/pull/139/head; git rev-parse FETCH_HEAD
49235270a04daaef43c9ec713b73862f5039592e   (equals headRefOid)

$ git show --name-only --format='%H%n%an <%ae>%n%s' 49235270a04daaef43c9ec713b73862f5039592e
49235270a04daaef43c9ec713b73862f5039592e
dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
chore(deps): bump tox from 4.56.1 to 4.61.4

uv.lock
```

Name list: exactly `uv.lock` — **class LOCK-ONLY**. One commit.

### #140 — `dependabot/uv/sphinx-intl-2.4.0`

```
$ gh pr view 140 --json ... commits,files
headRefOid = f3ba32992b7e1b5fd128b40897e8b56fe4d09be9, files: [uv.lock only]

$ git fetch origin refs/pull/140/head; git rev-parse FETCH_HEAD
f3ba32992b7e1b5fd128b40897e8b56fe4d09be9   (equals headRefOid)

$ git show --name-only --format='%H%n%an <%ae>%n%s' f3ba32992b7e1b5fd128b40897e8b56fe4d09be9
f3ba32992b7e1b5fd128b40897e8b56fe4d09be9
dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
chore(deps): bump sphinx-intl from 2.3.2 to 2.4.0

uv.lock
```

Name list: exactly `uv.lock` — **class LOCK-ONLY**. One commit.

### #141 — `dependabot/uv/pre-commit-4.6.2`

```
$ gh pr view 141 --json ... commits,files
headRefOid = e94498a515b17047cdc9579c66afee56d7ccb5ab, files: [uv.lock only]

$ git fetch origin refs/pull/141/head; git rev-parse FETCH_HEAD
e94498a515b17047cdc9579c66afee56d7ccb5ab   (equals headRefOid)

$ git show --name-only --format='%H%n%an <%ae>%n%s' e94498a515b17047cdc9579c66afee56d7ccb5ab
e94498a515b17047cdc9579c66afee56d7ccb5ab
dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
chore(deps): bump pre-commit from 4.6.0 to 4.6.2

uv.lock
```

Name list: exactly `uv.lock` — **class LOCK-ONLY**. One commit.

### #142 — `dependabot/uv/mypy-2.3.1`

```
$ gh pr view 142 --json ... commits,files
headRefOid = 7f8737cb0b29985b20aac97a1fe07a8d6d8378b2, files: [uv.lock only]

$ git fetch origin refs/pull/142/head; git rev-parse FETCH_HEAD
7f8737cb0b29985b20aac97a1fe07a8d6d8378b2   (equals headRefOid)

$ git show --name-only --format='%H%n%an <%ae>%n%s' 7f8737cb0b29985b20aac97a1fe07a8d6d8378b2
7f8737cb0b29985b20aac97a1fe07a8d6d8378b2
dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
chore(deps): bump mypy from 2.1.0 to 2.3.1

uv.lock
```

Name list: exactly `uv.lock` — **class LOCK-ONLY**. One commit.

### Classification table

| # | Title | Branch | Head SHA | Commits | Files | Class |
|---|-------|--------|----------|---------|-------|-------|
| 138 | bump ruff 0.15.20→0.16.6 | dependabot/uv/ruff-0.16.6 | 88088071e02a7411800f504e06b1ded9d6891cc7 | 1 | pyproject.toml, uv.lock | BOTH |
| 139 | bump tox 4.56.1→4.61.4 | dependabot/uv/tox-4.61.4 | 49235270a04daaef43c9ec713b73862f5039592e | 1 | uv.lock | LOCK-ONLY |
| 140 | bump sphinx-intl 2.3.2→2.4.0 | dependabot/uv/sphinx-intl-2.4.0 | f3ba32992b7e1b5fd128b40897e8b56fe4d09be9 | 1 | uv.lock | LOCK-ONLY |
| 141 | bump pre-commit 4.6.0→4.6.2 | dependabot/uv/pre-commit-4.6.2 | e94498a515b17047cdc9579c66afee56d7ccb5ab | 1 | uv.lock | LOCK-ONLY |
| 142 | bump mypy 2.1.0→2.3.1 | dependabot/uv/mypy-2.3.1 | 7f8737cb0b29985b20aac97a1fe07a8d6d8378b2 | 1 | uv.lock | LOCK-ONLY |

Every open `dependabot/uv/` PR carries exactly one commit; SC#1 reads the head commit for the one
BOTH-class PR. No PR had more than one commit, so the "when a PR has more than one commit" note in
the plan does not apply here.

## SC#1 selection (D-04)

```
SC1_PR = 138
SC1_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7
```

`SC1_PR` #138 is the lowest-numbered (and only) BOTH PR. Its branch `dependabot/uv/ruff-0.16.6`
starts with `dependabot/uv/`; its author login `app/dependabot` matches `dependabot`; its base is
`main`; it carries exactly one commit, which is `SC1_SHA` itself.

```
$ gh pr view 138 --json headRefName -q '.headRefName | startswith("dependabot/uv/")'
true

$ gh pr view 138 --json author -q '.author.login | test("dependabot")'
true

$ gh pr view 138 --json baseRefName -q .baseRefName
main

$ gh pr view 138 --json commits -q '.commits[].oid'
88088071e02a7411800f504e06b1ded9d6891cc7
```

`SC1_SHA` is the PR's sole commit.

```
$ git show --stat 88088071e02a7411800f504e06b1ded9d6891cc7
commit 88088071e02a7411800f504e06b1ded9d6891cc7
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Sat Sep 12 10:39:48 2026 +0000

    chore(deps): bump ruff from 0.15.20 to 0.16.6
    ...

 pyproject.toml |  2 +-
 uv.lock        | 44 ++++++++++++++++++++++----------------------
 2 files changed, 23 insertions(+), 23 deletions(-)

$ git show 88088071e02a7411800f504e06b1ded9d6891cc7 -- pyproject.toml
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

The range widened from `<0.16` to `<0.17` (D-06 range-behaviour material). The context lines still
show `tox-uv-bare>=1.35,<2` — `main` has not received Phase 65's `tox-uv-bare` → `tox-uv` revert
yet (that lands only at REL-12, per ROADMAP's two-independent-track design; Track A and Track B
share no file). Recorded, not touched.

No `gh pr checkout`, `git switch` or `git checkout` was run against any dependabot head in this
worktree; every read above went through `git show`/`git fetch` only, on this worktree's own
detached-fetch objects, with HEAD never moving off the worktree's own branch.

## D-05 leg 1 documented and source uv versions

**Documentation:**

```
$ gh api repos/github/docs/commits/main --jq .sha
078b5832caa5cde591c2babb389ef447a0ef66eb

$ gh api repos/github/docs/contents/content/code-security/reference/supply-chain-security/dependabot-options-reference.md --jq .content | base64 -d | grep -n '^| uv '
618:| uv           | `uv`             | v0.11 |

$ gh api repos/github/docs/contents/data/reusables/dependabot/supported-package-managers.md --jq .content | base64 -d | grep -n '^uv '
59:uv        | `uv`            | v0.11            | {% octicon "check" aria-label="Supported" %} | {% octicon "check" aria-label="Supported" %} | {% octicon "check" aria-label="Supported" %} | {% octicon "check" aria-label="Supported" %} | Not applicable |
61:uv        | `uv`            | v0.11            | {% octicon "check" aria-label="Supported" %} | {% octicon "x" aria-label="Not supported" %} | {% octicon "check" aria-label="Supported" %} | {% octicon "check" aria-label="Supported" %} | Not applicable |
```

```
DOCS_UV_ROW = v0.11
```

**dependabot-core `main`:**

```
$ gh api repos/dependabot/dependabot-core/commits/main --jq .sha
f7f49928afb51e93a3a4e55d76715e990feed02a

$ gh api repos/dependabot/dependabot-core/contents/uv/Dockerfile --jq .content | base64 -d | grep -n 'astral-sh/uv'
15:FROM ghcr.io/astral-sh/uv:0.12.7 AS uv

$ gh api repos/dependabot/dependabot-core/contents/uv/helpers/requirements.txt --jq .content | base64 -d | grep -n '^uv=='
10:uv==0.12.7
```

```
DEPENDABOT_UV_MAIN = 0.12.7
```

**The deployed image** — `TAG` is the text after the last `:` of `UPDATER_UV_IMAGE`
(`ghcr.io/dependabot/dependabot-updater-uv:ebbc4f6acba15d63b83f2211074ddc74e979fcfd`):

```
$ gh api "repos/dependabot/dependabot-core/commits/ebbc4f6acba15d63b83f2211074ddc74e979fcfd" --jq '[.sha, .commit.committer.date, (.commit.message | split("\n")[0])] | @tsv'
ebbc4f6acba15d63b83f2211074ddc74e979fcfd	2026-09-11T23:20:28Z	Merge 62f3e983a53a7e7689805f445f350070dfb318fd into 4a3779f686e66f43efcb3815691cf3e93ee655ab
```

The tag resolves as a real dependabot-core commit (A-DEP-04 does not fire).

```
$ gh api "repos/dependabot/dependabot-core/contents/uv/Dockerfile?ref=ebbc4f6acba15d63b83f2211074ddc74e979fcfd" --jq .content | base64 -d | grep -n 'astral-sh/uv'
15:FROM ghcr.io/astral-sh/uv:0.12.7 AS uv

$ gh api "repos/dependabot/dependabot-core/contents/uv/helpers/requirements.txt?ref=ebbc4f6acba15d63b83f2211074ddc74e979fcfd" --jq .content | base64 -d | grep -n '^uv=='
10:uv==0.12.7
```

```
DEPENDABOT_UV_DEPLOYED = 0.12.7
```

**Finding.** GitHub's own documentation (`DOCS_UV_ROW = v0.11`) is stale relative to source: both
dependabot-core's `main` branch (`DEPENDABOT_UV_MAIN = 0.12.7`) and the exact image tag dependabot
pulled for `SC1_PR`'s update run (`DEPENDABOT_UV_DEPLOYED = 0.12.7`) agree with each other and both
disagree with the documented `v0.11` — a stale-documentation finding (D-05), not a functional
regression. `.planning/REQUIREMENTS.md`'s DEP-04 wording is not edited; it stays literal.

## D-05 leg 2 lock header

```
$ git show "88088071e02a7411800f504e06b1ded9d6891cc7:uv.lock" | sed -n 1,2p
version = 1
revision = 3

$ git show "293f0c2684641f5d4b2f5ed021b565656e38d48c:uv.lock" | sed -n 1,2p
version = 1
revision = 3
```

Both `SC1_SHA` (the real `uv`-ecosystem PR head) and `MERGE_SHA` (the tip of `main`) read
`version = 1` / `revision = 3` — no divergence. Leg 2(a) holds.

## D-05 leg 2 local lock check

```
$ S="$(mktemp -d)"
S=/tmp/tmp.aDWRG6PjJD

$ git archive -o "$S/head.tar" 88088071e02a7411800f504e06b1ded9d6891cc7; echo "exit:$?"
exit:0

$ tar -x -f "$S/head.tar" -C "$S"; echo "exit:$?"
exit:0
```

From this worktree's own directory (so the `uv` shim on `PATH` is exercised without `cd`ing into
`$S`):

```
$ command -v uv
/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv

$ uv --version
uv 0.12.13 (x86_64-unknown-linux-gnu)
```

```
LOCAL_UV = 0.12.13
```

```
$ uv lock --check --directory "$S"; echo "exit:$?"
Using CPython 3.14.4
Resolved 89 packages in 4ms
exit:0
```

`exit:0` — the exported `SC1_SHA` tree's `uv.lock` is unchanged by a fresh resolve under
`LOCAL_UV`. Never run with the working directory inside `$S`.

```
$ rm -rf "$S"; echo "exit:$?"
exit:0
```

`$S` removed afterwards. The PR branch itself was never written to — only the scratch export.

## D-05 leg 2 CI uv on the PR head

```
$ gh run list --workflow=ci.yml --event pull_request --limit 20 --json databaseId,headSha,headBranch,status,conclusion,createdAt
```

The row whose `headSha` is `SC1_SHA`:

```
{"conclusion":"success","createdAt":"2026-09-12T10:39:53Z","databaseId":34689041575,"headBranch":"dependabot/uv/ruff-0.16.6","headSha":"88088071e02a7411800f504e06b1ded9d6891cc7","status":"completed"}
```

Already `completed` at first query — no wait needed.

```
SC1_RUN_ID = 34689041575

$ gh run view 34689041575 --json status,conclusion,headSha,event,url
{"conclusion":"success","event":"pull_request","headSha":"88088071e02a7411800f504e06b1ded9d6891cc7","status":"completed","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34689041575"}
```

`headSha` equals `SC1_SHA`; `status: completed`.

```
$ gh run view 34689041575 --json jobs -q '.jobs[] | select(.name == "Test Python 3.12 on ubuntu-latest") | .databaseId'
103540970982

$ gh api repos/YuSabo90002/typsphinx/actions/jobs/103540970982 --jq '.steps[] | [.number, .name, .conclusion] | @tsv'
1	Set up job	success
2	Run actions/checkout@v7	success
3	Install uv	success
4	Set up Python 3.12	success
5	Install dependencies	success
6	Run tests with tox	success
7	Upload test results	success
13	Post Install uv	success
14	Post Run actions/checkout@v7	success
15	Complete job	success
```

`Install dependencies` (`uv sync --extra dev --locked`) concludes `success`.

```
$ gh run view --job 103540970982 --log | grep -m1 'Successfully installed uv version'
Test Python 3.12 on ubuntu-latest	Install uv	2026-09-12T10:40:02.5686557Z Successfully installed uv version 0.12.13
```

```
CI_UV_VERSION = 0.12.13
```

**Leg 2 verdict.** (a) lock header held on both `SC1_SHA` and `MERGE_SHA`; (b) the local
`uv lock --check --directory` on the exported copy printed `exit:0`; (c) the SC#1 CI run's
`Install dependencies` step concluded `success`.

```
D05_LEG2 = PASS
```

All three legs held — the fallback custom workflow is not reached; nothing was built or staged.

## DEP-04 comparison

```
$ gh api repos/astral-sh/uv/releases/latest --jq '[.tag_name, .published_at] | @tsv'
0.12.13	2026-09-10T19:27:24Z
```

```
UV_LATEST = 0.12.13
```

| Key | Value |
|---|---|
| `DOCS_UV_ROW` | v0.11 |
| `DEPENDABOT_UV_MAIN` | 0.12.7 |
| `DEPENDABOT_UV_DEPLOYED` | 0.12.7 |
| `CI_UV_VERSION` | 0.12.13 |
| `UV_LATEST` | 0.12.13 |
| `LOCAL_UV` | 0.12.13 |
| `uv.lock` header (`SC1_SHA`, `MERGE_SHA`) | `version = 1` / `revision = 3` (both) |

Comparison is string equality only — no ordering is inferred by lexical or float comparison
(the precision edge). `DOCS_UV_ROW` (`v0.11`) is a distinct literal string from the other five
figures, all of which read `0.12.x`; none is normalized to compare against `v0.11`.

The local-uv figure the ROADMAP SC#2 text carries forward (`0.11.25`, stale per `66-RESEARCH.md`'s
own Summary section) is superseded by `LOCAL_UV = 0.12.13`, measured here, not copied.

Astral's lockfile-versioning statement, quoted from `66-RESEARCH.md` Pitfall 3 as context (not as
evidence for this leg): "The `revision` field of the lockfile is used to track backwards compatible
changes to the lockfile... Changes to the revision will not cause older versions of uv to error,"
while "Any given version of uv can read and write lockfiles with the same schema version, but will
reject lockfiles with a greater schema version." `[CITED: docs.astral.sh/uv/concepts/resolution —
"Lockfile versioning" section]` — this repo's `version = 1` has been unchanged since well before
the v0.11/v0.12 split, consistent with the clean `D05_LEG2 = PASS` measured directly above.

DEP-02 (CI's test/lint/type jobs reaching a conclusion on a real dependabot PR) remains Phase 67's
to judge; this section's `Install dependencies` reading is DEP-04 evidence about lock compatibility
only, not a DEP-02 closure.
