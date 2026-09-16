# Phase 73 — SC#1 Fence Invariants (unpublished-shaped tree)

Recorded inside this plan's isolated worktree (`worktree-agent-a347b03dff012a923`), after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`.

## Observation 1 of 2

```
OBS1_AT = 2026-09-16T09:57:35Z
```

This timestamp opens the section so the separation from observation 2 (owned by plan 73-06, two
waves and one CI dispatch later) is measurable rather than asserted.

### Version-line probe

```
$ sed -n 7p pyproject.toml
version = "0.9.2"
```

Key line:

```
VERSION_LINE = version = "0.9.2"
```

`pyproject.toml:7` still reads `0.9.2` — no version bump has landed in this milestone.

### Local tag probe (with positive control)

```
$ git tag -l 'v0.9*'
v0.9.0
v0.9.2

$ git tag -l 'v0.9.3'
(no output)

$ git tag -l 'v0.9.4'
(no output)

$ git tag -l 'v0.9.5'
(no output)
```

Key lines:

```
LOCAL_V093_TAGS = 0
LOCAL_V094_TAGS = 0
LOCAL_V095_TAGS = 0
```

**Positive control:** `v0.9.0` and `v0.9.2` are both present locally, proving `git tag -l` reaches
real tag data rather than an empty/broken tag database. **Negative assertion:** no `v0.9.3`,
`v0.9.4` or `v0.9.5` tag exists locally.

### Remote tag probe (unfiltered, with positive control)

A bare `git ls-remote --tags origin 'v0.9.3'` is deliberately NOT used — its silence would be
indistinguishable from a network failure. Instead the unfiltered listing is fetched once and four
counts are derived from that single fetch:

```
$ git ls-remote --tags origin
375e6a5a54eef042193f56dc29d8d0dd5646d88d	refs/tags/v0.1.0b1
6ca477b53f00baec532686008947ee17c2f307d5	refs/tags/v0.1.0b1^{}
f0309a2ed8f8241ee693d31c46db5eeb712b5de4	refs/tags/v0.2.0
d22590e05854e33470ea1bea2b793f530f22cb58	refs/tags/v0.2.1
d4fc5df65b986e7fd16f0b0436ae0068d6181f8f	refs/tags/v0.2.2
c1e2db714cfacd8ef96759ccdebf6e09f5c9152a	refs/tags/v0.2.2^{}
7df99929c9e490506cc7ef1eb6af3e4298856b1c	refs/tags/v0.3.0
28a80a6cc13288eb8c75612693d34a25ae865142	refs/tags/v0.3.0^{}
25778f58c42c7fb0c6b4aa6515269c12d8659611	refs/tags/v0.4.0
08aeb4b3cfba2293103aefa201b85c89397f50f3	refs/tags/v0.4.0^{}
fb47d6930e24e5071f9911e6f6fee30f8b7f7040	refs/tags/v0.4.1
0ed33d10acbee8fa935850bcf77404d55832edc9	refs/tags/v0.4.1^{}
e19b0eb202ee7e6131f9aca6687b1272bb2709d8	refs/tags/v0.4.2
445af8c4b8a30d924d30341bd87b476fa7d0b486	refs/tags/v0.4.2^{}
415498a8cfa7dc21aa09871d4d3b061ed7ba48a2	refs/tags/v0.4.3
d299dd7007b529b7b197a62f6c4ab2630b5217c7	refs/tags/v0.4.4
dae500a1f2065691972e03cc70a9bf73a90cd26f	refs/tags/v0.4.4^{}
fc78e1daa02317b34f5cd448ec036bff78a02755	refs/tags/v0.5.0
ea153bfca933b92ea23fdfa72efba2afb100f29b	refs/tags/v0.5.0^{}
a3b7fad1645374fe17dc84dc1967949c9282f6dd	refs/tags/v0.6.0
cc26b4723f671c0ac0dfdae687b6bee722aa6dd0	refs/tags/v0.6.0^{}
06f45470f79c9e67cf057c61f46669dd67bd8fe1	refs/tags/v0.6.1
27e77403f1d62ebec9f36c2c4a9b7c8e16067fc9	refs/tags/v0.6.1^{}
87d929ef74c1f19a435ff0bedb6ecb0f530ac9a3	refs/tags/v0.6.2
54b8fc90df0359b049a1cd9936f03c76d1169f74	refs/tags/v0.6.2^{}
0d823c5ab8cb2e5b86dbe97a6d795b6c55b50b09	refs/tags/v0.6.3
7f6db629351aa1229a2a07614b6a6f201001ad80	refs/tags/v0.6.3^{}
ee06fee074510f18c127fece68302e683897ba4c	refs/tags/v0.6.4
2bf6ef318773b239e4ab20b41fbe40ce91337584	refs/tags/v0.6.4^{}
bd4096b966d213756ad3fbe1055c35d79d560347	refs/tags/v0.6.5
839d77f38ffa67f18696265b361f7dcef92f679b	refs/tags/v0.6.5^{}
7327d0160571519d8b7c8c4ef56a19ca55756e31	refs/tags/v0.7.0
75fd8ed55f4fca206474f9e3aa934921588b52d5	refs/tags/v0.7.0^{}
a8afd6549448e9f6e7635f0573d7efc04179dbd4	refs/tags/v0.7.1
48bf135428bb093a77a432d93d16088ce6930342	refs/tags/v0.7.1^{}
d9523ea43d884f9ce6763da0f7f8e690fe859eb4	refs/tags/v0.8.0
78e01e53641433a34c1bd8834b6252187fcae4ba	refs/tags/v0.8.0^{}
ada0b845cf1f5a495dc7c522b80e79ed5c76004d	refs/tags/v0.9.0
68b92e24e6ca3df410ca0435d226629ef7ef1e2e	refs/tags/v0.9.0^{}
8797b1783df23187bdce3eec231f0578dcdb9ecb	refs/tags/v0.9.2
45962faad21520c72ac9f1e14c7f684050826bb6	refs/tags/v0.9.2^{}

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.2$'
1

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.3'
0

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.4'
0

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.5'
0
```

Key lines:

```
REMOTE_V092_TAG = 1
REMOTE_V093_TAG = 0
REMOTE_V094_TAG = 0
REMOTE_V095_TAG = 0
```

**Positive control:** the count of lines matching the `v0.9.2` tag reference at end-of-line is
exactly `1` — proving the remote was actually reached and the listing is genuinely populated, not
silently empty from an unreachable source. **Negative assertion:** the count of lines mentioning
`v0.9.3`, `v0.9.4` or `v0.9.5` in any form (including `^{}` peeled entries) is `0` for each — no
tag exists on the remote for any of the three unclaimed version numbers.

### PyPI probe (with positive control)

```
$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json
200

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.3/json
404

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.4/json
404

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.5/json
404
```

Key lines:

```
PYPI_092_HTTP = 200
PYPI_093_HTTP = 404
PYPI_094_HTTP = 404
PYPI_095_HTTP = 404
```

**Positive control:** `0.9.2`'s PyPI JSON endpoint returns `200`, proving PyPI itself is reachable
and the prior release is genuinely published there. **Negative assertion:** each of `0.9.3`,
`0.9.4` and `0.9.5`'s endpoints return `404` — nothing is uploaded for any of the three unclaimed
numbers.

### GitHub Release probe (with positive control)

```
$ gh release list --limit 20 --json tagName,isLatest,publishedAt
[{"isLatest":true,"publishedAt":"2026-08-30T15:11:29Z","tagName":"v0.9.2"},{"isLatest":false,"publishedAt":"2026-08-22T07:46:15Z","tagName":"v0.9.0"},{"isLatest":false,"publishedAt":"2026-08-15T03:09:31Z","tagName":"v0.8.0"},{"isLatest":false,"publishedAt":"2026-08-11T05:34:10Z","tagName":"v0.7.1"},{"isLatest":false,"publishedAt":"2026-08-03T20:09:13Z","tagName":"v0.7.0"},{"isLatest":false,"publishedAt":"2026-07-28T20:58:41Z","tagName":"v0.6.5"},{"isLatest":false,"publishedAt":"2026-07-27T22:03:45Z","tagName":"v0.6.4"},{"isLatest":false,"publishedAt":"2026-07-25T10:07:05Z","tagName":"v0.6.3"},{"isLatest":false,"publishedAt":"2026-07-23T11:16:50Z","tagName":"v0.6.2"},{"isLatest":false,"publishedAt":"2026-07-20T03:19:22Z","tagName":"v0.6.1"},{"isLatest":false,"publishedAt":"2026-07-12T22:05:29Z","tagName":"v0.6.0"},{"isLatest":false,"publishedAt":"2026-07-11T13:05:54Z","tagName":"v0.5.0"},{"isLatest":false,"publishedAt":"2026-07-05T06:12:55Z","tagName":"v0.4.4"},{"isLatest":false,"publishedAt":"2025-11-01T03:40:30Z","tagName":"v0.4.3"},{"isLatest":false,"publishedAt":"2025-10-29T12:39:56Z","tagName":"v0.4.2"},{"isLatest":false,"publishedAt":"2025-10-26T06:47:43Z","tagName":"v0.4.1"},{"isLatest":false,"publishedAt":"2025-10-26T06:05:44Z","tagName":"v0.4.0"},{"isLatest":false,"publishedAt":"2025-10-23T14:20:00Z","tagName":"v0.3.0"},{"isLatest":false,"publishedAt":"2025-10-23T12:46:07Z","tagName":"v0.2.2"},{"isLatest":false,"publishedAt":"2025-10-18T05:12:00Z","tagName":"v0.2.1"}]
```

Key lines:

```
GH_LATEST = v0.9.2
GH_V093_RELEASES = 0
GH_V094_RELEASES = 0
GH_V095_RELEASES = 0
```

**Positive control:** `v0.9.2` carries `isLatest: true` — proving `gh release list` reached
GitHub and the prior release genuinely holds the Latest marker. **Negative assertion:** no entry's
`tagName` is `v0.9.3`, `v0.9.4` or `v0.9.5`.

### Release-workflow probe (with positive control)

```
$ gh run list --workflow=release.yml --limit 20 --json databaseId,createdAt,headBranch,event,conclusion
[{"conclusion":"success","createdAt":"2026-08-30T15:10:43Z","databaseId":33318905691,"event":"push","headBranch":"v0.9.2"},{"conclusion":"success","createdAt":"2026-08-22T07:45:31Z","databaseId":32560457509,"event":"push","headBranch":"v0.9.0"},{"conclusion":"success","createdAt":"2026-08-15T03:08:42Z","databaseId":31861043480,"event":"push","headBranch":"v0.8.0"},{"conclusion":"success","createdAt":"2026-08-11T05:33:22Z","databaseId":31462027486,"event":"push","headBranch":"v0.7.1"},{"conclusion":"failure","createdAt":"2026-08-03T20:08:22Z","databaseId":30848860064,"event":"push","headBranch":"v0.7.0"},{"conclusion":"success","createdAt":"2026-07-28T20:57:57Z","databaseId":30398631991,"event":"push","headBranch":"v0.6.5"},{"conclusion":"success","createdAt":"2026-07-27T22:03:03Z","databaseId":30309278708,"event":"push","headBranch":"v0.6.4"},{"conclusion":"success","createdAt":"2026-07-25T10:06:08Z","databaseId":30153888475,"event":"push","headBranch":"v0.6.3"},{"conclusion":"success","createdAt":"2026-07-23T11:16:03Z","databaseId":30002480654,"event":"push","headBranch":"v0.6.2"},{"conclusion":"success","createdAt":"2026-07-20T03:18:33Z","databaseId":29714380810,"event":"push","headBranch":"v0.6.1"},{"conclusion":"success","createdAt":"2026-07-12T22:04:43Z","databaseId":29210840198,"event":"push","headBranch":"v0.6.0"},{"conclusion":"success","createdAt":"2026-07-11T13:05:05Z","databaseId":29153718002,"event":"push","headBranch":"v0.5.0"},{"conclusion":"success","createdAt":"2026-07-05T06:12:16Z","databaseId":28731646924,"event":"push","headBranch":"v0.4.4"},{"conclusion":"failure","createdAt":"2026-07-05T06:06:40Z","databaseId":28731518799,"event":"push","headBranch":"v0.4.4"},{"conclusion":"success","createdAt":"2025-11-01T03:39:55Z","databaseId":18990823422,"event":"push","headBranch":"v0.4.3"},{"conclusion":"success","createdAt":"2025-10-29T12:39:41Z","databaseId":18908167233,"event":"push","headBranch":"v0.4.2"},{"conclusion":"success","createdAt":"2025-10-26T06:47:27Z","databaseId":18814341329,"event":"push","headBranch":"v0.4.1"},{"conclusion":"success","createdAt":"2025-10-26T06:05:23Z","databaseId":18813905654,"event":"push","headBranch":"v0.4.0"},{"conclusion":"success","createdAt":"2025-10-23T14:03:10Z","databaseId":18751004128,"event":"push","headBranch":"v0.3.0"},{"conclusion":"success","createdAt":"2025-10-23T12:45:30Z","databaseId":18748785140,"event":"push","headBranch":"v0.2.2"}]
```

Key lines:

```
RELEASE_POSITIVE_CONTROL = 33318905691
RELEASE_RUNS_SINCE_V092 = 0
```

**Positive control:** run `33318905691` (the v0.9.2 release, `2026-08-30`, `success`, `push` on
`headBranch: v0.9.2`) is present in the listing — proving `gh run list` reached GitHub's Actions
API and the prior release genuinely ran through `release.yml`. **Negative assertion:** no run in
this 20-row listing was created after `2026-08-31` or carries `headBranch: v0.9.3`, `v0.9.4` or
`v0.9.5` — the newest run in the entire listing is still `33318905691` at
`2026-08-30T15:10:43Z`, itself before the cutoff.

### Pull-request probe (with positive control)

```
$ gh pr list --state all --limit 5 --json number
[{"number":150},{"number":149},{"number":148},{"number":147},{"number":146}]

$ gh pr list --head gsd/v0.9.5-docs-link-check-and-navigation --state all --json number,state
[]
```

Key line:

```
BRANCH_PRS = 0
```

**Positive control:** the unscoped `gh pr list` returns five real PR numbers (#146–#150, the
Dependabot `uv`-ecosystem PRs recorded in `73-CONTEXT.md`'s measured state) — proving the command
reached GitHub and the repository genuinely has PR history. **Negative assertion:** scoped to
`gsd/v0.9.5-docs-link-check-and-navigation` as head branch, the listing is empty — no pull
request exists from the milestone branch.

### Observation 1 verdict

**The fence holds at phase head, for all three unclaimed version numbers:**

- `pyproject.toml:7` still reads `version = "0.9.2"` — no version bump landed.
- No `v0.9.3`, `v0.9.4` or `v0.9.5` tag exists locally or on origin (`LOCAL_V093_TAGS = 0`,
  `LOCAL_V094_TAGS = 0`, `LOCAL_V095_TAGS = 0`, `REMOTE_V093_TAG = 0`, `REMOTE_V094_TAG = 0`,
  `REMOTE_V095_TAG = 0`), each paired with a positive-controlled probe of the same source
  (`v0.9.0`/`v0.9.2` locally, `v0.9.2`'s remote tag reference for the ls-remote listing).
- v0.9.2 is still the latest published release (`GH_LATEST = v0.9.2`) and nothing is on PyPI
  (`PYPI_093_HTTP = 404`, `PYPI_094_HTTP = 404`, `PYPI_095_HTTP = 404`) or GitHub Releases
  (`GH_V093_RELEASES = 0`, `GH_V094_RELEASES = 0`, `GH_V095_RELEASES = 0`) for any of the three.
- No `release.yml` run has been created since `2026-08-31` or on any of the three refs
  (`RELEASE_RUNS_SINCE_V092 = 0`), against the positive control that run `33318905691` (the v0.9.2
  release) is present in the same listing.
- No pull request exists from the milestone branch (`BRANCH_PRS = 0`), against the positive
  control that an unscoped `gh pr list` returns real PR numbers.

D-11 records all three numbers (`0.9.3`, `0.9.4`, `0.9.5`) as unclaimed, not decided — whether the
next published release is one of them, skips them, or is some other number belongs to the next
milestone's scoping — and this phase creates no tag, consistent with every probe above.

## Milestone fences (D-13)

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD
   098a8ff6..6e2b7899  main       -> origin/main

$ git merge-base HEAD origin/main
098a8ff64cf008822eef9dc69f75102ded3f7bc1

$ git rev-parse origin/main
6e2b789922207eb72e7aef3216fdfd924dd4bcd9
```

Key lines:

```
MILESTONE_BASE = 098a8ff64cf008822eef9dc69f75102ded3f7bc1
ORIGIN_MAIN_SHA_OBS1 = 6e2b789922207eb72e7aef3216fdfd924dd4bcd9
MAIN_MOVED_OBS1 = yes
```

`origin/main` has moved past `098a8ff6` (to `6e2b7899`) since the milestone was cut, but the
merge-base of this branch and `origin/main` is still exactly `098a8ff64cf008822eef9dc69f75102ded3f7bc1`
— this branch has not absorbed any of `main`'s later commits, and `main`'s later commits have not
been rebased into this branch's history either. A moved `main` is not a failure here; it is D-07's
case, which plan 73-05's non-committing trial merge measures against the live `origin/main` tip,
not against this fixed `MILESTONE_BASE` anchor.

### The version-bump probe

```
$ git log --format=%h -G '^version = ' 098a8ff64cf008822eef9dc69f75102ded3f7bc1..HEAD -- pyproject.toml
(no output)
```

Key line:

```
VERSION_BUMP_COMMITS = 0
```

No commit in the milestone range touched a `version = ` line in `pyproject.toml`.

### The claim

```
$ git diff --stat 098a8ff64cf008822eef9dc69f75102ded3f7bc1 HEAD -- typsphinx/ .github/workflows/
(no output)
```

Key line:

```
MILESTONE_CODE_WORKFLOW_DIFF = empty
```

Empty — no line, hunk, or file under `typsphinx/` or `.github/workflows/` changed between the
milestone base and this plan's own tip (constraints 2 and 3: no builder change and no workflow
edit in this milestone).

### Pathspec control

```
$ git ls-tree -r --name-only HEAD -- typsphinx/ .github/workflows/ | wc -l
16
```

Key line:

```
PATHSPEC_TRACKED_FILES = 16
```

The pathspec names real tracked files (16 of them at HEAD), so its empty diff is not a typo'd or
non-existent path.

### Widened-diff control

```
$ git diff --name-only 098a8ff64cf008822eef9dc69f75102ded3f7bc1 HEAD -- . ':(exclude).planning' | LC_ALL=C sort | tr '\n' ' '
CLAUDE.md README.md docs/source/contributing.rst docs/source/index.rst tox.ini
```

Key line:

```
MILESTONE_PRODUCT_FILES_OBS1 = CLAUDE.md README.md docs/source/contributing.rst docs/source/index.rst tox.ini
```

This equals `PRODUCT_DIFF_FILES` in `72-GATES-EVIDENCE.md`:

```
$ grep -n 'PRODUCT_DIFF_FILES' .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-GATES-EVIDENCE.md
207:PRODUCT_DIFF_FILES = CLAUDE.md README.md docs/source/contributing.rst docs/source/index.rst tox.ini
```

Phase 72's five product files, byte-identical to the list above.

**Why both controls are needed.** An empty scoped diff from a wrong or non-existent anchor (a
typo'd SHA, an anchor accidentally equal to HEAD, or an anchor that predates the repository's
history) would produce the same empty `git diff --stat ... -- typsphinx/ .github/workflows/`
output — an empty-diff claim with no live control is unfalsifiable, because it looks identical
whether the tree is genuinely unchanged under those paths or the anchor itself is broken. The
pathspec control proves the anchor's pathspec resolves to real tracked files (16 of them), not an
empty or mistyped path. The widened-diff control, taken from the exact same `MILESTONE_BASE`
anchor, proves the anchor is real, reachable and genuinely earlier than HEAD: five real files
changed against it, matching Phase 72's own recorded `PRODUCT_DIFF_FILES` exactly. If the scoped
diff had been empty because the anchor was wrong, the widened diff would have been empty too — it
is not, so the scoped diff's emptiness is a real finding about `typsphinx/` and
`.github/workflows/`, not an artifact of a broken anchor.

This is Phase 69's scoped-plus-widened shape (`69-SC1-INVARIANTS.md` § "The typsphinx/ fence
(constraint 13)"), not Phase 71's masked-AST re-run, because nothing under `typsphinx/` changed in
this milestone (D-13) — Phase 71 needed the heavier masked-AST proof only because Phase 70
rewrote type annotations under `typsphinx/` in that milestone.

## Handoff to observation 2

Observation 2 of 2, the close-tip repeat of the D-13 fences, the phase-scoped diff from
`PHASE_BASE_SHA` (recorded in `73-CLOSEOUT-GUARD.md` § "Baseline"), and the post-dispatch proof
are owned by **plan 73-06**, which runs two waves and one CI dispatch later than this plan — so
the two `OBS*_AT` stamps are genuinely separated rather than collapsed into one command run. Plan
73-06 appends its findings under a new `## Observation 2 of 2` section in this same file, together
with the phase-scoped `typsphinx/` and `.github/workflows/` diff from `PHASE_BASE_SHA`, and a
post-dispatch commit check (confirming no commit landed between the CI-dispatched SHA and 73-06's
own HEAD that touches the product tree outside `.planning/`).

## Observation 2 of 2

Recorded inside plan 73-06's own isolated worktree (`worktree-agent-a8e4a4b993ad882e9`), after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`,
two waves and one full CI dispatch after observation 1.

### Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-16T10:30:15Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8e4a4b993ad882e9

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

```
$ git rev-parse HEAD
b3e05b6e306cad045903bb55c1ff94e45e37b68d
```

Key line:

```
BASE_73_06 = b3e05b6e306cad045903bb55c1ff94e45e37b68d
```

```
$ mktemp -d
/tmp/tmp.8e6IC7n6sI
```

Key line:

```
SCRATCH_73_06 = /tmp/tmp.8e6IC7n6sI
```

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-09-16T10:30:21Z
```

Key line:

```
OBS2_AT = 2026-09-16T10:30:21Z
```

`OBS1_AT` (§ "Observation 1 of 2" above) = `2026-09-16T09:57:35Z`. Elapsed interval: **32 minutes
46 seconds**, spanning wave 2 in full — the local green-tree proof (73-03), the phase's only push
and CI dispatch (73-04, run `35083828156`, 12/12 jobs `success`), and the D-09 trial-merge
pre-flight (73-05).

### Version-line probe

```
$ sed -n 7p pyproject.toml
version = "0.9.2"
```

Key line:

```
OBS2_VERSION_LINE = version = "0.9.2"
```

Unchanged from observation 1.

### Local tag probe (with positive control)

```
$ git tag -l 'v0.9*'
v0.9.0
v0.9.2

$ git tag -l 'v0.9.3'
(no output)

$ git tag -l 'v0.9.4'
(no output)

$ git tag -l 'v0.9.5'
(no output)
```

Key lines:

```
OBS2_LOCAL_V093_TAGS = 0
OBS2_LOCAL_V094_TAGS = 0
OBS2_LOCAL_V095_TAGS = 0
```

**Positive control:** `v0.9.0` and `v0.9.2` are both still present locally. **Negative
assertion:** no `v0.9.3`, `v0.9.4` or `v0.9.5` tag exists locally, unchanged from observation 1.

### Remote tag probe (unfiltered, with positive control)

```
$ git ls-remote --tags origin
375e6a5a54eef042193f56dc29d8d0dd5646d88d	refs/tags/v0.1.0b1
6ca477b53f00baec532686008947ee17c2f307d5	refs/tags/v0.1.0b1^{}
f0309a2ed8f8241ee693d31c46db5eeb712b5de4	refs/tags/v0.2.0
d22590e05854e33470ea1bea2b793f530f22cb58	refs/tags/v0.2.1
d4fc5df65b986e7fd16f0b0436ae0068d6181f8f	refs/tags/v0.2.2
c1e2db714cfacd8ef96759ccdebf6e09f5c9152a	refs/tags/v0.2.2^{}
7df99929c9e490506cc7ef1eb6af3e4298856b1c	refs/tags/v0.3.0
28a80a6cc13288eb8c75612693d34a25ae865142	refs/tags/v0.3.0^{}
25778f58c42c7fb0c6b4aa6515269c12d8659611	refs/tags/v0.4.0
08aeb4b3cfba2293103aefa201b85c89397f50f3	refs/tags/v0.4.0^{}
fb47d6930e24e5071f9911e6f6fee30f8b7f7040	refs/tags/v0.4.1
0ed33d10acbee8fa935850bcf77404d55832edc9	refs/tags/v0.4.1^{}
e19b0eb202ee7e6131f9aca6687b1272bb2709d8	refs/tags/v0.4.2
445af8c4b8a30d924d30341bd87b476fa7d0b486	refs/tags/v0.4.2^{}
415498a8cfa7dc21aa09871d4d3b061ed7ba48a2	refs/tags/v0.4.3
d299dd7007b529b7b197a62f6c4ab2630b5217c7	refs/tags/v0.4.4
dae500a1f2065691972e03cc70a9bf73a90cd26f	refs/tags/v0.4.4^{}
fc78e1daa02317b34f5cd448ec036bff78a02755	refs/tags/v0.5.0
ea153bfca933b92ea23fdfa72efba2afb100f29b	refs/tags/v0.5.0^{}
a3b7fad1645374fe17dc84dc1967949c9282f6dd	refs/tags/v0.6.0
cc26b4723f671c0ac0dfdae687b6bee722aa6dd0	refs/tags/v0.6.0^{}
06f45470f79c9e67cf057c61f46669dd67bd8fe1	refs/tags/v0.6.1
27e77403f1d62ebec9f36c2c4a9b7c8e16067fc9	refs/tags/v0.6.1^{}
87d929ef74c1f19a435ff0bedb6ecb0f530ac9a3	refs/tags/v0.6.2
54b8fc90df0359b049a1cd9936f03c76d1169f74	refs/tags/v0.6.2^{}
0d823c5ab8cb2e5b86dbe97a6d795b6c55b50b09	refs/tags/v0.6.3
7f6db629351aa1229a2a07614b6a6f201001ad80	refs/tags/v0.6.3^{}
ee06fee074510f18c127fece68302e683897ba4c	refs/tags/v0.6.4
2bf6ef318773b239e4ab20b41fbe40ce91337584	refs/tags/v0.6.4^{}
bd4096b966d213756ad3fbe1055c35d79d560347	refs/tags/v0.6.5
839d77f38ffa67f18696265b361f7dcef92f679b	refs/tags/v0.6.5^{}
7327d0160571519d8b7c8c4ef56a19ca55756e31	refs/tags/v0.7.0
75fd8ed55f4fca206474f9e3aa934921588b52d5	refs/tags/v0.7.0^{}
a8afd6549448e9f6e7635f0573d7efc04179dbd4	refs/tags/v0.7.1
48bf135428bb093a77a432d93d16088ce6930342	refs/tags/v0.7.1^{}
d9523ea43d884f9ce6763da0f7f8e690fe859eb4	refs/tags/v0.8.0
78e01e53641433a34c1bd8834b6252187fcae4ba	refs/tags/v0.8.0^{}
ada0b845cf1f5a495dc7c522b80e79ed5c76004d	refs/tags/v0.9.0
68b92e24e6ca3df410ca0435d226629ef7ef1e2e	refs/tags/v0.9.0^{}
8797b1783df23187bdce3eec231f0578dcdb9ecb	refs/tags/v0.9.2
45962faad21520c72ac9f1e14c7f684050826bb6	refs/tags/v0.9.2^{}

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.2$'
1

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.3'
0

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.4'
0

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.5'
0
```

Key lines:

```
OBS2_REMOTE_V092_TAG = 1
OBS2_REMOTE_V093_TAG = 0
OBS2_REMOTE_V094_TAG = 0
OBS2_REMOTE_V095_TAG = 0
```

**Positive control:** the count of lines matching the `v0.9.2` tag reference at end-of-line is
still exactly `1` — the remote is genuinely reached, and the listing is unchanged since
observation 1 (same 40 tag lines, same content). **Negative assertion:** the count of lines
mentioning `v0.9.3`, `v0.9.4` or `v0.9.5` in any form is still `0` for each.

### PyPI probe (with positive control)

```
$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json
200

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.3/json
404

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.4/json
404

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.5/json
404
```

Key lines:

```
OBS2_PYPI_092_HTTP = 200
OBS2_PYPI_093_HTTP = 404
OBS2_PYPI_094_HTTP = 404
OBS2_PYPI_095_HTTP = 404
```

**Positive control:** `0.9.2`'s PyPI JSON endpoint still returns `200`. **Negative assertion:**
each of `0.9.3`, `0.9.4` and `0.9.5`'s endpoints still return `404`.

### GitHub Release probe (with positive control)

```
$ gh release list --limit 20 --json tagName,isLatest,publishedAt
[{"isLatest":true,"publishedAt":"2026-08-30T15:11:29Z","tagName":"v0.9.2"},{"isLatest":false,"publishedAt":"2026-08-22T07:46:15Z","tagName":"v0.9.0"},{"isLatest":false,"publishedAt":"2026-08-15T03:09:31Z","tagName":"v0.8.0"},{"isLatest":false,"publishedAt":"2026-08-11T05:34:10Z","tagName":"v0.7.1"},{"isLatest":false,"publishedAt":"2026-08-03T20:09:13Z","tagName":"v0.7.0"},{"isLatest":false,"publishedAt":"2026-07-28T20:58:41Z","tagName":"v0.6.5"},{"isLatest":false,"publishedAt":"2026-07-27T22:03:45Z","tagName":"v0.6.4"},{"isLatest":false,"publishedAt":"2026-07-25T10:07:05Z","tagName":"v0.6.3"},{"isLatest":false,"publishedAt":"2026-07-23T11:16:50Z","tagName":"v0.6.2"},{"isLatest":false,"publishedAt":"2026-07-20T03:19:22Z","tagName":"v0.6.1"},{"isLatest":false,"publishedAt":"2026-07-12T22:05:29Z","tagName":"v0.6.0"},{"isLatest":false,"publishedAt":"2026-07-11T13:05:54Z","tagName":"v0.5.0"},{"isLatest":false,"publishedAt":"2026-07-05T06:12:55Z","tagName":"v0.4.4"},{"isLatest":false,"publishedAt":"2025-11-01T03:40:30Z","tagName":"v0.4.3"},{"isLatest":false,"publishedAt":"2025-10-29T12:39:56Z","tagName":"v0.4.2"},{"isLatest":false,"publishedAt":"2025-10-26T06:47:43Z","tagName":"v0.4.1"},{"isLatest":false,"publishedAt":"2025-10-26T06:05:44Z","tagName":"v0.4.0"},{"isLatest":false,"publishedAt":"2025-10-23T14:20:00Z","tagName":"v0.3.0"},{"isLatest":false,"publishedAt":"2025-10-23T12:46:07Z","tagName":"v0.2.2"},{"isLatest":false,"publishedAt":"2025-10-18T05:12:00Z","tagName":"v0.2.1"}]
```

Key lines:

```
OBS2_GH_LATEST = v0.9.2
OBS2_GH_V093_RELEASES = 0
OBS2_GH_V094_RELEASES = 0
OBS2_GH_V095_RELEASES = 0
```

**Positive control:** `v0.9.2` still carries `isLatest: true`. **Negative assertion:** no entry's
`tagName` is `v0.9.3`, `v0.9.4` or `v0.9.5`.

### Release-workflow probe (with positive control)

```
$ gh run list --workflow=release.yml --limit 20 --json databaseId,createdAt,headBranch,event,conclusion
[{"conclusion":"success","createdAt":"2026-08-30T15:10:43Z","databaseId":33318905691,"event":"push","headBranch":"v0.9.2"},{"conclusion":"success","createdAt":"2026-08-22T07:45:31Z","databaseId":32560457509,"event":"push","headBranch":"v0.9.0"},{"conclusion":"success","createdAt":"2026-08-15T03:08:42Z","databaseId":31861043480,"event":"push","headBranch":"v0.8.0"},{"conclusion":"success","createdAt":"2026-08-11T05:33:22Z","databaseId":31462027486,"event":"push","headBranch":"v0.7.1"},{"conclusion":"failure","createdAt":"2026-08-03T20:08:22Z","databaseId":30848860064,"event":"push","headBranch":"v0.7.0"},{"conclusion":"success","createdAt":"2026-07-28T20:57:57Z","databaseId":30398631991,"event":"push","headBranch":"v0.6.5"},{"conclusion":"success","createdAt":"2026-07-27T22:03:03Z","databaseId":30309278708,"event":"push","headBranch":"v0.6.4"},{"conclusion":"success","createdAt":"2026-07-25T10:06:08Z","databaseId":30153888475,"event":"push","headBranch":"v0.6.3"},{"conclusion":"success","createdAt":"2026-07-23T11:16:03Z","databaseId":30002480654,"event":"push","headBranch":"v0.6.2"},{"conclusion":"success","createdAt":"2026-07-20T03:18:33Z","databaseId":29714380810,"event":"push","headBranch":"v0.6.1"},{"conclusion":"success","createdAt":"2026-07-12T22:04:43Z","databaseId":29210840198,"event":"push","headBranch":"v0.6.0"},{"conclusion":"success","createdAt":"2026-07-11T13:05:05Z","databaseId":29153718002,"event":"push","headBranch":"v0.5.0"},{"conclusion":"success","createdAt":"2026-07-05T06:12:16Z","databaseId":28731646924,"event":"push","headBranch":"v0.4.4"},{"conclusion":"failure","createdAt":"2026-07-05T06:06:40Z","databaseId":28731518799,"event":"push","headBranch":"v0.4.4"},{"conclusion":"success","createdAt":"2025-11-01T03:39:55Z","databaseId":18990823422,"event":"push","headBranch":"v0.4.3"},{"conclusion":"success","createdAt":"2025-10-29T12:39:41Z","databaseId":18908167233,"event":"push","headBranch":"v0.4.2"},{"conclusion":"success","createdAt":"2025-10-26T06:47:27Z","databaseId":18814341329,"event":"push","headBranch":"v0.4.1"},{"conclusion":"success","createdAt":"2025-10-26T06:05:23Z","databaseId":18813905654,"event":"push","headBranch":"v0.4.0"},{"conclusion":"success","createdAt":"2025-10-23T14:03:10Z","databaseId":18751004128,"event":"push","headBranch":"v0.3.0"},{"conclusion":"success","createdAt":"2025-10-23T12:45:30Z","databaseId":18748785140,"event":"push","headBranch":"v0.2.2"}]
```

Key lines:

```
OBS2_RELEASE_RUNS_SINCE_V092 = 0
```

**Positive control:** run `33318905691` (the v0.9.2 release, `2026-08-30`, `success`, `push` on
`headBranch: v0.9.2`) is still present in the listing — reads byte-identical to
`RELEASE_POSITIVE_CONTROL` recorded in observation 1. **Negative assertion:** no run in this
20-row listing was created after `2026-08-31` or carries `headBranch: v0.9.3`, `v0.9.4` or
`v0.9.5` — the newest run in the entire listing is still `33318905691` at
`2026-08-30T15:10:43Z`, itself before the cutoff, and still before this phase's own CI dispatch
(`35083828156`, `2026-09-16T10:13:43Z`, workflow `ci.yml` not `release.yml`).

### Pull-request probe (with positive control)

```
$ gh pr list --state all --limit 5 --json number
[{"number":150},{"number":149},{"number":148},{"number":147},{"number":146}]

$ gh pr list --head gsd/v0.9.5-docs-link-check-and-navigation --state all --json number,state
[]
```

Key line:

```
OBS2_BRANCH_PRS = 0
```

**Positive control:** the unscoped `gh pr list` still returns five real PR numbers (#146–#150).
**Negative assertion:** scoped to `gsd/v0.9.5-docs-link-check-and-navigation` as head branch, the
listing is still empty — no pull request exists from the milestone branch, even after this
phase's own push in 73-04.

### Observation 2 verdict

**The fence still holds, two waves and a full CI run after observation 1, for all three unclaimed
version numbers:**

- `pyproject.toml:7` still reads `version = "0.9.2"` (`OBS2_VERSION_LINE`) — no version bump
  landed, including through the CI dispatch and the wave-2 merges.
- No `v0.9.3`, `v0.9.4` or `v0.9.5` tag exists locally or on origin (`OBS2_LOCAL_V093_TAGS = 0`,
  `OBS2_LOCAL_V094_TAGS = 0`, `OBS2_LOCAL_V095_TAGS = 0`, `OBS2_REMOTE_V093_TAG = 0`,
  `OBS2_REMOTE_V094_TAG = 0`, `OBS2_REMOTE_V095_TAG = 0`), each paired with the same positive
  control as observation 1.
- v0.9.2 is still the latest published release (`OBS2_GH_LATEST = v0.9.2`) and nothing is on PyPI
  (`OBS2_PYPI_093_HTTP = 404`, `OBS2_PYPI_094_HTTP = 404`, `OBS2_PYPI_095_HTTP = 404`) or GitHub
  Releases (`OBS2_GH_V093_RELEASES = 0`, `OBS2_GH_V094_RELEASES = 0`, `OBS2_GH_V095_RELEASES = 0`)
  for any of the three.
- No `release.yml` run has been created since `2026-08-31` or on any of the three refs
  (`OBS2_RELEASE_RUNS_SINCE_V092 = 0`), even though this phase's own `ci.yml` (not `release.yml`)
  dispatch (`35083828156`) ran and completed between the two observations.
- No pull request exists from the milestone branch (`OBS2_BRANCH_PRS = 0`), even after 73-04's
  push of the phase's final tip to origin.

The fence held across the whole phase, including after 73-04's push and CI dispatch. All three
unclaimed version numbers (`0.9.3`, `0.9.4`, `0.9.5`) remain unclaimed (D-11) at this second,
separately-timestamped observation.

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 02, 06*
