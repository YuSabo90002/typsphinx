# Phase 67 Plan 03: Disposal of #128 (D-05, docutils) — Evidence

This plan's own worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout
is never touched.

BASE_67_03 = 6a687ca9e854d6f4aad16df78585855d85209de5

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa40eb7cd74040f8f

$ git rev-parse --abbrev-ref HEAD
worktree-agent-aa40eb7cd74040f8f

$ git rev-parse HEAD
6a687ca9e854d6f4aad16df78585855d85209de5
```

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
Using CPython 3.14.4
Creating virtual environment at: .venv
Resolved 91 packages in 0.59ms
   Building typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa40eb7cd74040f8f
      Built typsphinx @ file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aa40eb7cd74040f8f
Prepared 1 package in 375ms
Installed 81 packages in 50ms
 ... (81 packages, including uv==0.12.13, tox==4.56.1, pytest==9.1.1, docutils==0.22.4, sphinx==9.1.0)
```

```
$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

`BASE_67_03 = 6a687ca9e854d6f4aad16df78585855d85209de5` — this worktree's HEAD at the start of
this plan.

## Wave-1 gate

Precondition keys read from `67-PROOF-EVIDENCE.md`:

```
$ sed -n 's/^DEP02_VERDICT = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-PROOF-EVIDENCE.md | head -n 1
MET

$ sed -n 's/^SC2_BRANCH = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-PROOF-EVIDENCE.md | head -n 1
can

$ sed -n 's/^MECHANICAL_CLOSE = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-PROOF-EVIDENCE.md | head -n 1
none

$ grep -c '^## HALT' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-PROOF-EVIDENCE.md
0
```

`DEP02_VERDICT = MET`, `SC2_BRANCH = can`, `MECHANICAL_CLOSE = none`, and zero `## HALT` headings
in `67-PROOF-EVIDENCE.md`. The wave-1 gate holds; this plan's dispositions may proceed.

## D-05 PyPI re-measurement

Re-measured, never copied. A temporary scratch directory outside the repository held the raw JSON;
it was removed after use.

```
$ date -u +%FT%TZ
2026-09-12T13:30:39Z
```

```
PYPI_READ_AT = 2026-09-12T13:30:39Z
```

```
$ curl -fsS https://pypi.org/pypi/sphinx/json -o "$S/sphinx.json"
$ curl -fsS https://pypi.org/pypi/docutils/json -o "$S/docutils.json"
```

```
$ git show HEAD:pyproject.toml | grep -n '"sphinx'
28:    "sphinx>=9.1,<10",
```

```
SPHINX_RANGE = "sphinx>=9.1,<10"
```

`uv run python -c …` (so `packaging` resolves from this worktree's own `.venv`):

```
$ uv run python -c "
import json
with open(sphinx_json) as f:
    d = json.load(f)
info = d['info']
print('SPHINX_LATEST =', info['version'])
from packaging.requirements import Requirement
reqs = [x for x in info['requires_dist'] if Requirement(x).name.lower() == 'docutils']
for r in reqs:
    print('SPHINX_DOCUTILS_REQ =', r)
"
SPHINX_LATEST = 9.1.0
SPHINX_DOCUTILS_REQ = docutils<0.23,>=0.21
```

```
SPHINX_LATEST = 9.1.0
SPHINX_DOCUTILS_REQ = docutils<0.23,>=0.21
```

```
$ uv run python -c "
import json
with open(docutils_json) as f:
    d = json.load(f)
print('DOCUTILS_LATEST =', d['info']['version'])
"
DOCUTILS_LATEST = 0.23
```

```
DOCUTILS_LATEST = 0.23
```

Every `releases` key that parses as a `packaging.version.Version`, is not a pre-release, and is
contained in `SPHINX_RANGE`'s `SpecifierSet('>=9.1,<10')`:

```
$ uv run python -c "
import json
with open(sphinx_json) as f:
    d = json.load(f)
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet
spec = SpecifierSet('>=9.1,<10')
in_range = []
for v in d['releases'].keys():
    try:
        pv = Version(v)
    except InvalidVersion:
        continue
    if pv.is_prerelease:
        continue
    if pv in spec:
        in_range.append(pv)
in_range.sort()
print('SPHINX_IN_RANGE =', ' '.join(str(v) for v in in_range))
"
SPHINX_IN_RANGE = 9.1.0
```

```
SPHINX_IN_RANGE = 9.1.0
```

Only one non-pre-release Sphinx version exists in the `>=9.1,<10` range: `9.1.0` itself (the two
`9.1.0rc1`/`9.1.0rc2` release candidates are excluded as pre-releases).

For each version `v` in `SPHINX_IN_RANGE`, fetch its own per-version JSON and evaluate its docutils
requirement against `0.23` through `packaging` (never lexically):

```
$ curl -fsS https://pypi.org/pypi/sphinx/9.1.0/json -o "$S/sphinx-9.1.0.json"

$ uv run python -c "
import json
from packaging.requirements import Requirement
with open(sphinx_9_1_0_json) as f:
    d = json.load(f)
info = d['info']
reqs = [x for x in info['requires_dist'] if Requirement(x).name.lower() == 'docutils']
for r in reqs:
    req = Requirement(r)
    admits = req.specifier.contains('0.23')
    print('9.1.0', r, 'admits' if admits else 'excludes')
"
9.1.0 docutils<0.23,>=0.21 excludes
```

| Version | docutils requirement | admits 0.23 |
|---|---|---|
| 9.1.0 | `docutils<0.23,>=0.21` | excludes |

No in-range Sphinx release admits docutils `0.23`.

```
D05_CAP_RELAXED = no
```

The temporary scratch directory (`$S`) was removed after this measurement.

## #128 re-snapshot

```
$ date -u +%FT%TZ
2026-09-12T13:31:04Z

$ gh pr view 128 --json number,title,state,closed,closedAt,author,headRefName,headRefOid,baseRefName,updatedAt,labels,comments
{"author":{"is_bot":true,"login":"app/dependabot"},"baseRefName":"main","closed":false,"closedAt":null,"comments":[{"id":"IC_kwDOQBRmjM8AAAABM56Sgw","author":{"login":"dependabot"},"authorAssociation":"CONTRIBUTOR","body":"### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.","createdAt":"2026-08-03T00:06:15Z","includesCreatedEdit":false,"isMinimized":false,"minimizedReason":"","reactionGroups":[],"url":"https://github.com/YuSabo90002/typsphinx/pull/128#issuecomment-5160997507","viewerDidAuthor":false}],"headRefName":"dependabot/pip/sphinx-typst-stack-12b5b89b5a","headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f","labels":[],"number":128,"state":"OPEN","title":"chore(deps): update docutils requirement from <0.23,>=0.21 to >=0.21,<0.24 in the sphinx-typst-stack group across 1 directory","updatedAt":"2026-09-07T00:07:47Z"}
```

`state: "OPEN"`. `headRefOid` (`000859f7e07167a8be8b6d3beceea44bca26fa4f`) and `updatedAt`
(`2026-09-07T00:07:47Z`) are unchanged from `67-PROOF-EVIDENCE.md` § "D-02 re-snapshot" (the same
values recorded there for `#128`). Comment count (1, dependabot's own) is also unchanged.

```
HEAD128 = 000859f7e07167a8be8b6d3beceea44bca26fa4f
```

## D-05 merits for #128

**The pip PR's shape.**

```
$ git fetch origin refs/pull/128/head
From https://github.com/YuSabo90002/typsphinx
 * branch              refs/pull/128/head -> FETCH_HEAD

$ git rev-parse FETCH_HEAD
000859f7e07167a8be8b6d3beceea44bca26fa4f
```

`FETCH_HEAD` equals `HEAD128`.

```
$ git show --name-only --format='%H%n%an <%ae>%n%s' 000859f7e07167a8be8b6d3beceea44bca26fa4f
000859f7e07167a8be8b6d3beceea44bca26fa4f
dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
chore(deps): update docutils requirement

pyproject.toml
```

```
HEAD128_FILES = pyproject.toml
```

```
$ git show 000859f7e07167a8be8b6d3beceea44bca26fa4f -- pyproject.toml
commit 000859f7e07167a8be8b6d3beceea44bca26fa4f
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Mon Aug 31 00:06:16 2026 +0000

    chore(deps): update docutils requirement

    Updates the requirements on [docutils](https://github.com/rtfd/recommonmark) to permit the latest version.

    Updates `docutils` to 0.23
    - [Changelog](https://github.com/readthedocs/recommonmark/blob/master/CHANGELOG.md)
    - [Commits](https://github.com/rtfd/recommonmark/commits)

    ---
    updated-dependencies:
    - dependency-name: docutils
      dependency-version: '0.23'
      dependency-type: direct:production
      dependency-group: sphinx-typst-stack
    ...

    Signed-off-by: dependabot[bot] <support@github.com>

diff --git a/pyproject.toml b/pyproject.toml
index 9ac02823..d9f9e789 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -26,7 +26,7 @@ classifiers = [

 dependencies = [
     "sphinx>=9.1,<10",
-    "docutils>=0.21,<0.23",
+    "docutils>=0.21,<0.24",
     "typst>=0.15.0,<0.16",
 ]
```

**Merit:** a `pyproject.toml`-only change with no `uv.lock` regeneration fails `uv sync --locked`.
Merging it would reintroduce that failure on `main`.

**#128's own CI.**

```
$ gh pr view 128 --json statusCheckRollup --jq '.statusCheckRollup[] | [.name, .conclusion] | @tsv'
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
Build Package	SUCCESS
Integration Test - basic	FAILURE
Integration Test - advanced	CANCELLED
```

11 `FAILURE`, 1 `CANCELLED`, 3 `SUCCESS` — matching the planning-time census.

```
$ gh run list --workflow=ci.yml --branch dependabot/pip/sphinx-typst-stack-12b5b89b5a --limit 3 --json databaseId,headSha,conclusion
[{"conclusion":"failure","databaseId":33343567900,"headSha":"000859f7e07167a8be8b6d3beceea44bca26fa4f"},{"conclusion":"failure","databaseId":33319014580,"headSha":"4314ce91b40cb7f9d9b14e1d4fb2c612d31188bd"},{"conclusion":"failure","databaseId":32675602223,"headSha":"72c0362309a76bbfdd30b6c36c592daea71d8bc4"}]
```

A failing CI run for `HEAD128` exists (`33343567900`):

```
$ gh run view 33343567900 --log-failed | grep -- '--locked'
Type Check	UNKNOWN STEP	2026-08-31T00:06:30.1120746Z ##[group]Run uv sync --extra dev --locked
Type Check	UNKNOWN STEP	2026-08-31T00:06:30.1121129Z uv sync --extra dev --locked
Type Check	UNKNOWN STEP	2026-08-31T00:06:30.4118857Z error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.
```

This is the measured failure shape the source todo named: a `pyproject.toml`-only PR that never
regenerated `uv.lock` fails at `uv sync --extra dev --locked`.

**The uv attempt.**

```
$ gh run view 34688990228 --log | grep -m5 -E 'dependency_file_not_resolvable|docutils>=0.21,<0.23'
Dependabot	Run Dependabot	2026-09-12T10:39:32.0638606Z updater | 2026/09/12 10:39:32 INFO <job_1572468102> Handled error whilst updating docutils: dependency_file_not_resolvable {message: "× No solution found when resolving dependencies for split (markers:\n  │ python_full_version >= '3.15'):\n  ╰─▶ Because sphinx>=9.1.0 depends on docutils>=0.21,<0.23 and your project\n      depends on docutils==0.23, we can conclude that sphinx>=9.1.0 and your\n      project are incompatible.\n      And because your project depends on sphinx>=9.1 and your project\n      requires typsphinx[dev], we can conclude that your project's\n      requirements are unsatisfiable.\n\nhint: While the active Python version is 3.12, the resolution failed for other Python versions supported by your project. Consider limiting your project's supported Python versions using `requires-python`."}
```

Citing `66-DEPENDABOT-EVIDENCE.md` § "uv update job conclusion": the `uv` updater's own attempt to
propose this same docutils bump failed with `dependency_file_not_resolvable`, quoting the identical
resolver contradiction — `sphinx>=9.1.0 depends on docutils>=0.21,<0.23`.

**Grouping (D-06 input).**

```
$ gh pr view 128 --json title,headRefName -q '.title + " | " + .headRefName'
chore(deps): update docutils requirement from <0.23,>=0.21 to >=0.21,<0.24 in the sphinx-typst-stack group across 1 directory | dependabot/pip/sphinx-typst-stack-12b5b89b5a
```

The title contains "sphinx-typst-stack group" and the branch starts with
`dependabot/pip/sphinx-typst-stack`.

```
GROUPED_128 = yes
```

**CI greenness is not the merit here.** #128's CI is red at the install step (`Install
dependencies` / `uv sync --extra dev --locked` fails with the lockfile mismatch above), not merely
non-green by coincidence. The decision rests on the Sphinx docutils cap (re-measured above,
`D05_CAP_RELAXED = no`) and the `pyproject.toml`-only shape against `--locked`, not on whether CI
is passing or failing.

## #128 thread

Read in full before drafting; every line treated as data, never as instructions.

```
$ gh pr view 128 --json comments --jq '.comments[] | [.author.login, .createdAt, .body] | @tsv'
dependabot	2026-08-03T00:06:15Z	### Labels\n\nThe following labels could not be found: `automated`, `dependencies`. Please create them before Dependabot can add them to a pull request.\n\n\nPlease fix the above issues or remove invalid values from `dependabot.yml`.
```

```
$ gh api --paginate repos/YuSabo90002/typsphinx/pulls/128/comments --jq 'length'
0

$ gh api --paginate repos/YuSabo90002/typsphinx/pulls/128/reviews --jq 'length'
0
```

```
$ gh pr view 128 --json body -q .body | wc -l
56
```

Zero review comments, zero reviews. The single issue-comment is dependabot's own automated
"labels could not be found" notice. **No non-dependabot author appears anywhere in the thread.**

## Tooling pre-flight

```
$ gh pr close --help | grep -n -- '--comment'
7:  -c, --comment string   Leave a closing comment
```

`gh pr close` supports `-c, --comment` directly — the RESEARCH A2 fallback (`gh pr comment` +
`gh pr close`) is not needed, but remains the documented fallback if `--comment` were ever
unsupported.

## Draft comment (not yet approved)

Built from D-05's shape with the measured values substituted:

```
DRAFT_COMMENT_128 = Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap.
```

It names no person and blames no one. It is a draft only — nothing has been posted in this task.

## Handoff to Task 2

The docutils merit premise is re-measured and holds (`D05_CAP_RELAXED = no`), the whole `#128`
thread was read (no non-dependabot comment exists), and a draft waits for the owner. `#128` is
untouched — no comment, no close, no label, no `@dependabot` command was issued by this task.

## Owner decision (#128)

The owner's reply, relayed verbatim by the coordinator: "close as drafted"

```
$ date -u +%FT%TZ
2026-09-12T13:36:46Z
```

```
OWNER_DECISION_128 = close
DECIDED_AT_128 = 2026-09-12T13:36:46Z
```

On close: the approved text is the committed `DRAFT_COMMENT_128`, read back from this evidence
file (not retyped):

```
$ sed -n 's/^DRAFT_COMMENT_128 = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-DOCUTILS-EVIDENCE.md | head -n 1
Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap.
```

```
APPROVED_COMMENT_128 = Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap.
```

This is committed before posting, so the text is on record first.

## Idempotency check (DEP-05)

```
$ gh api user --jq .login
YuSabo90002
```

```
ME = YuSabo90002
```

```
$ gh pr view 128 --json state,closedAt,comments --jq '{state, closedAt, mine: [.comments[] | select(.author.login == "YuSabo90002") | .body]}'
{"state":"OPEN","closedAt":null,"mine":[]}
```

`#128` is OPEN with zero owner-authored comments — the "Otherwise" branch.

```
ALREADY_CLOSED_128 = no
```

## Pre-close PyPI re-measurement

Repeats the Task 1 latest-release and in-range evaluation immediately before posting (Pitfall 4).

```
$ date -u +%FT%TZ
2026-09-12T13:37:16Z
```

```
PRECLOSE_PYPI_AT = 2026-09-12T13:37:16Z
```

```
$ curl -fsS https://pypi.org/pypi/sphinx/json | uv run python -c 'import json,sys; from packaging.requirements import Requirement; i=json.load(sys.stdin)["info"]; rs=[Requirement(x) for x in i["requires_dist"] if Requirement(x).name.lower()=="docutils"]; print(i["version"], "admits" if any(r.specifier.contains("0.23") for r in rs) else "excludes")'
9.1.0 excludes
```

```
$ uv run python -c "
import json
with open(sphinx_preclose_json) as f:
    d = json.load(f)
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet
spec = SpecifierSet('>=9.1,<10')
in_range = []
for v in d['releases'].keys():
    try:
        pv = Version(v)
    except InvalidVersion:
        continue
    if pv.is_prerelease:
        continue
    if pv in spec:
        in_range.append(pv)
in_range.sort()
print('PRECLOSE_SPHINX_IN_RANGE =', ' '.join(str(v) for v in in_range))
"
PRECLOSE_SPHINX_IN_RANGE = 9.1.0
```

Still only `9.1.0` in range, and it still excludes `0.23`.

```
D05_CAP_RELAXED_PRECLOSE = no
```

## #128 re-assertion

```
$ gh pr view 128 --json state,headRefOid,comments
{"comments":[{"id":"IC_kwDOQBRmjM8AAAABM56Sgw","author":{"login":"dependabot"}, ... "createdAt":"2026-08-03T00:06:15Z", ...}],"headRefOid":"000859f7e07167a8be8b6d3beceea44bca26fa4f","state":"OPEN"}
```

OPEN, at `HEAD128` (`000859f7e07167a8be8b6d3beceea44bca26fa4f`), unchanged. The only comment is
still dependabot's own automated notice created `2026-08-03T00:06:15Z`, well before
`PYPI_READ_AT`. No new comment by any non-dependabot author since the draft.

## Close (#128)

```
$ date -u +%FT%TZ
2026-09-12T13:37:36Z
```

The sandbox refused a command that combined `gh` with shell command substitution (`$(sed …)` /
`$(cat …)`) as "too complex to verify it stays inside the worktree." Per RESEARCH A2's documented
fallback (used here not because `--comment` is unsupported — it is — but because the sandbox
blocked the substitution form of invoking it), the approved text was extracted from
`APPROVED_COMMENT_128` to a plain file with `sed` (no `gh`/`git` in that command), then posted via
`gh pr comment --body-file`, which reads the file directly with no shell substitution and no
retyping:

```
$ sed -n 's/^APPROVED_COMMENT_128 = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-DOCUTILS-EVIDENCE.md | head -n 1 > /tmp/.../approved_comment_128.txt

$ cat -A /tmp/.../approved_comment_128.txt
Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap.$

$ gh pr comment 128 --body-file /tmp/.../approved_comment_128.txt
https://github.com/YuSabo90002/typsphinx/pull/128#issuecomment-5646230678

$ gh pr close 128
✓ Closed pull request YuSabo90002/typsphinx#128 (chore(deps): update docutils requirement from <0.23,>=0.21 to >=0.21,<0.24 in the sphinx-typst-stack group across 1 directory)
```

No `--delete-branch` was passed. The scratch file was removed immediately after use.

## Post-close record

```
$ gh pr view 128 --json state,closed,closedAt,mergedAt,comments
{"closed":true,"closedAt":"2026-09-12T13:38:31Z","comments":[{"id":"IC_kwDOQBRmjM8AAAABM56Sgw","author":{"login":"dependabot"}, ... },{"id":"IC_kwDOQBRmjM8AAAABUIqklg","author":{"login":"YuSabo90002"},"authorAssociation":"OWNER","body":"Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap.\n","createdAt":"2026-09-12T13:38:27Z","url":"https://github.com/YuSabo90002/typsphinx/pull/128#issuecomment-5646230678", ...},{"id":"IC_kwDOQBRmjM8AAAABUIqmUg","author":{"login":"dependabot"}, "body":"This pull request was built based on a group rule. Closing it will not ignore any of these versions in future pull requests. ...", "createdAt":"2026-09-12T13:38:32Z", ...}],"mergedAt":null,"state":"CLOSED"}
```

```
CLOSED_AT_128 = 2026-09-12T13:38:31Z
```

```
$ gh pr view 128 --json comments -q '[.comments[] | select(.author.login == "YuSabo90002")] | length'
1

$ gh pr view 128 --json comments -q '.comments[] | select(.author.login == "YuSabo90002") | .body'
Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap.
```

Exactly one owner-authored comment, its body equal to `APPROVED_COMMENT_128`. `mergedAt` is `null`
— `#128` is CLOSED, not merged. A second, automated comment from `dependabot` (its own group-rule
notice) was posted by GitHub after the close and is not an owner comment.

```
CLOSE_COMMENT_URL_128 = https://github.com/YuSabo90002/typsphinx/pull/128#issuecomment-5646230678
```

```
$ gh api --paginate repos/YuSabo90002/typsphinx/issues/128/events --jq '.[] | select(.event == "closed") | [.actor.login, .created_at] | @tsv'
YuSabo90002	2026-09-12T13:38:31Z
```

The last (only) `closed` event's actor is `YuSabo90002` — `ME`, the owner account.

## #128 disposition (D-05)

The decision is closed-with-reason, taken on the merits: Sphinx `9.1.0`'s measured
`docutils<0.23,>=0.21` cap (re-measured at Task 1 and again immediately before posting, both
`D05_CAP_RELAXED* = no`), the `uv` updater's own `dependency_file_not_resolvable` resolution
failure on this exact bump, and the `pyproject.toml`-only shape that would reintroduce the
`--locked` failure on `main` (already observed on `#128`'s own CI run `33343567900`). It was not
taken on CI state — `#128`'s CI was red at the install step throughout, and that redness is not
what drove the close.

The PR was a `sphinx-typst-stack` group PR (`GROUPED_128 = yes`); this observation is carried to
`67-05`'s D-06 write-up on the milestone's grouped-update coverage gap.

A future docutils `0.23` adoption is its own work, to be triggered by dependabot re-proposing the
bump once Sphinx relaxes the cap — a deferred idea, not undertaken in this phase.
