executor worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout is never touched.

BASE_SHA = 6181768f64b4cee62a77ac4e26c60c3c976cbb6e
MILESTONE_COMMIT = e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931
CONFIG_BLOB = a58ea1e25254138ff6967438feb948c1a0cc7064
PR_BRANCH = chore/dependabot-uv-ecosystem
PR_COMMIT = 7cc85d28c6946434aa4fb14a0b9b5555d29275ef
PUSH_AT = 2026-09-12T10:18:32Z
PR_NUMBER = 137
PR_URL = https://github.com/YuSabo90002/typsphinx/pull/137
PR_RUN_ID = 34688116389

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1bcb56644df5723

$ git rev-parse --abbrev-ref HEAD
worktree-agent-ae1bcb56644df5723

$ git log --oneline -1
de5a54ed docs(66): mark phase 66 executing (wave 1 of 4)
```

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.60ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1bcb56644df5723
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae1bcb56644df5723
Prepared 1 package in 447ms
Installed 81 packages in 49ms
 ... (81 packages, including uv==0.12.13, tox==4.56.1, pytest==9.1.1)
```

The provisioning line ran verbatim (CLAUDE.md, "Worktree-isolated execution"). This plan only ever
runs `git` and `gh` afterward.

```
$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

## Baseline

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git rev-parse origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e
```

```
$ git diff --stat origin/main HEAD -- .github/dependabot.yml
(empty)
```

The two copies were identical before the edit.

```
$ git show origin/main:.github/dependabot.yml | sed -n 4p
  - package-ecosystem: "pip"

$ git ls-tree origin/main .github/dependabot.yml
100644 blob 8c52c39999651b88f79fe186ad242c2fb495b219	.github/dependabot.yml
```

Line 4 is the pip line, and the mode is `100644`. No `## HALT` — the baseline had not moved.

## Milestone-branch commit

With the Edit tool, only the quoted value on line 4 of `.github/dependabot.yml` was changed from
`"pip"` to `"uv"`. Everything else — the comment above it, indentation, and every other line —
was left untouched.

```
$ git show "6181768f64b4cee62a77ac4e26c60c3c976cbb6e:.github/dependabot.yml" | sed '4s/"pip"$/"uv"/' | cmp - .github/dependabot.yml; echo "exit:$?"
exit:0

$ git diff --numstat -- .github/dependabot.yml
1	1	.github/dependabot.yml
```

```
$ git add .github/dependabot.yml
$ git commit -m "chore(66-01): switch dependabot Python updates from pip to uv ..."
[worktree-agent-ae1bcb56644df5723 e8c0e56f] chore(66-01): switch dependabot Python updates from pip to uv
 1 file changed, 1 insertion(+), 1 deletion(-)
```

```
$ git rev-parse HEAD
e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931

$ git rev-parse HEAD:.github/dependabot.yml
a58ea1e25254138ff6967438feb948c1a0cc7064

$ git show --name-only --format= e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931
.github/dependabot.yml
```

`MILESTONE_COMMIT = e8c0e56f07a189adc8b3e021a9caaa5e0fcb6931`, `CONFIG_BLOB` equals
`git rev-parse HEAD:.github/dependabot.yml`, and the commit touches exactly one file.

## Main-bound commit

Built from `BASE_SHA`'s tree with `.github/dependabot.yml` replaced by `CONFIG_BLOB`, via a
scratch index — the worktree's own HEAD never moved off `MILESTONE_COMMIT`.

```
$ mkdir -p /tmp/gsd-66-01-scratch

$ GIT_INDEX_FILE=/tmp/gsd-66-01-scratch/index git read-tree 6181768f64b4cee62a77ac4e26c60c3c976cbb6e
(no output)

$ GIT_INDEX_FILE=/tmp/gsd-66-01-scratch/index git update-index --cacheinfo 100644,a58ea1e25254138ff6967438feb948c1a0cc7064,.github/dependabot.yml
(no output)

$ GIT_INDEX_FILE=/tmp/gsd-66-01-scratch/index git write-tree
697748ca51baa26aa36c37c3147064827be12536
```

Commit message written to `/tmp/gsd-66-01-scratch/msg`: subject `chore(deps): switch dependabot
Python updates from pip to uv`, a blank line, then the session's attribution trailers.

```
$ git commit-tree 697748ca51baa26aa36c37c3147064827be12536 -p 6181768f64b4cee62a77ac4e26c60c3c976cbb6e -F /tmp/gsd-66-01-scratch/msg
7cc85d28c6946434aa4fb14a0b9b5555d29275ef
```

`PR_COMMIT = 7cc85d28c6946434aa4fb14a0b9b5555d29275ef`. The four pre-push assertions:

```
$ git rev-parse "$PR_COMMIT^"
6181768f64b4cee62a77ac4e26c60c3c976cbb6e

$ git diff --name-only "$BASE_SHA" "$PR_COMMIT"
.github/dependabot.yml

$ git diff --numstat "$BASE_SHA" "$PR_COMMIT"
1	1	.github/dependabot.yml

$ git rev-parse "$PR_COMMIT:.github/dependabot.yml"
a58ea1e25254138ff6967438feb948c1a0cc7064
```

Parent equals `BASE_SHA`; exactly one file changed, one line each way; the blob equals
`CONFIG_BLOB`. No `git checkout`, `git switch`, `git reset` or `git cherry-pick` was run against
this worktree; its index and HEAD stayed exactly where the milestone commit left them.

## Push and pull request

```
$ git ls-remote --heads origin refs/heads/chore/dependabot-uv-ecosystem
(empty)
```

The branch was absent on origin before the push.

```
$ date -u +%FT%TZ
2026-09-12T10:18:32Z
```

`PUSH_AT = 2026-09-12T10:18:32Z`.

```
$ git push origin 7cc85d28c6946434aa4fb14a0b9b5555d29275ef:refs/heads/chore/dependabot-uv-ecosystem
remote:
remote: Create a pull request for 'chore/dependabot-uv-ecosystem' on GitHub by visiting:
remote:      https://github.com/YuSabo90002/typsphinx/pull/new/chore/dependabot-uv-ecosystem
remote:
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        7cc85d28c6946434aa4fb14a0b9b5555d29275ef -> chore/dependabot-uv-ecosystem
```

No `--force`, no `--tags`, no `-u`, no other refspec.

```
$ git ls-remote --heads origin refs/heads/chore/dependabot-uv-ecosystem
7cc85d28c6946434aa4fb14a0b9b5555d29275ef	refs/heads/chore/dependabot-uv-ecosystem
```

The remote head equals `PR_COMMIT`. The milestone branch itself was not pushed.

Body written to `/tmp/gsd-66-01-scratch/body` — the two prescribed paragraphs plus the
pull-request attribution lines, naming no issue or PR number.

```
$ gh pr create --base main --head chore/dependabot-uv-ecosystem --title "chore(deps): switch dependabot Python updates from pip to uv" --body-file /tmp/gsd-66-01-scratch/body
https://github.com/YuSabo90002/typsphinx/pull/137
```

`PR_NUMBER = 137`, `PR_URL = https://github.com/YuSabo90002/typsphinx/pull/137`. No reviewer,
label or assignee was requested, and auto-merge was not enabled.

## CI run located

```
$ gh run list --workflow=ci.yml --branch chore/dependabot-uv-ecosystem --event pull_request --limit 5 --json databaseId,headSha,status,createdAt,url
[]
```

Empty on the first query — registration lag. Repeated a few seconds later:

```
$ gh run list --workflow=ci.yml --branch chore/dependabot-uv-ecosystem --event pull_request --limit 5 --json databaseId,headSha,status,createdAt,url
[{"createdAt":"2026-09-12T10:18:53Z","databaseId":34688116389,"headSha":"7cc85d28c6946434aa4fb14a0b9b5555d29275ef","status":"in_progress","url":"https://github.com/YuSabo90002/typsphinx/actions/runs/34688116389"}]
```

The row's `headSha` equals `PR_COMMIT`, and its `createdAt` (`2026-09-12T10:18:53Z`) is later than
`PUSH_AT` (`2026-09-12T10:18:32Z`).

`PR_RUN_ID = 34688116389`, URL = `https://github.com/YuSabo90002/typsphinx/actions/runs/34688116389`.
