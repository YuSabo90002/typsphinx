# Phase 69 — SC#1 Fence Invariants (unpublished-shaped tree)

Recorded inside this plan's isolated worktree (`worktree-agent-abe1318883a64e327`), after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`.

## Observation 1 of 2

```
OBS1_AT = 2026-09-12T22:35:11Z
```

This timestamp opens the section so the separation from observation 2 (owned by plan 69-06, two
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
```

Key line:

```
LOCAL_V093_TAGS = 0
```

**Positive control:** `v0.9.0` and `v0.9.2` are both present locally, proving `git tag -l` reaches
real tag data rather than an empty/broken tag database. **Negative assertion:** no `v0.9.3` tag
exists locally.

### Remote tag probe (unfiltered, with positive control)

A bare `git ls-remote --tags origin 'v0.9.3'` is deliberately NOT used — its silence would be
indistinguishable from a network failure. Instead the unfiltered listing is fetched once and two
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
```

Key lines:

```
REMOTE_V092_TAG = 1
REMOTE_V093_TAG = 0
```

**Positive control:** the count of lines matching the `v0.9.2` tag reference at end-of-line is
exactly `1` — proving the remote was actually reached and the listing is genuinely populated, not
silently empty from an unreachable source. **Negative assertion:** the count of lines mentioning
`v0.9.3` in any form (including `^{}` peeled entries) is `0` — no `v0.9.3` tag exists on the remote.

### PyPI probe (with positive control)

```
$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json
200

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.3/json
404
```

Key lines:

```
PYPI_092_HTTP = 200
PYPI_093_HTTP = 404
```

**Positive control:** `0.9.2`'s PyPI JSON endpoint returns `200`, proving PyPI itself is reachable
and the prior release is genuinely published there. **Negative assertion:** `0.9.3`'s endpoint
returns `404` — nothing is uploaded for `0.9.3`.

### GitHub Release probe (with positive control)

```
$ gh release list --limit 20 --json tagName,isLatest,publishedAt
[{"isLatest":true,"publishedAt":"2026-08-30T15:11:29Z","tagName":"v0.9.2"},{"isLatest":false,"publishedAt":"2026-08-22T07:46:15Z","tagName":"v0.9.0"},{"isLatest":false,"publishedAt":"2026-08-15T03:09:31Z","tagName":"v0.8.0"},{"isLatest":false,"publishedAt":"2026-08-11T05:34:10Z","tagName":"v0.7.1"},{"isLatest":false,"publishedAt":"2026-08-03T20:09:13Z","tagName":"v0.7.0"},{"isLatest":false,"publishedAt":"2026-07-28T20:58:41Z","tagName":"v0.6.5"},{"isLatest":false,"publishedAt":"2026-07-27T22:03:45Z","tagName":"v0.6.4"},{"isLatest":false,"publishedAt":"2026-07-25T10:07:05Z","tagName":"v0.6.3"},{"isLatest":false,"publishedAt":"2026-07-23T11:16:50Z","tagName":"v0.6.2"},{"isLatest":false,"publishedAt":"2026-07-20T03:19:22Z","tagName":"v0.6.1"},{"isLatest":false,"publishedAt":"2026-07-12T22:05:29Z","tagName":"v0.6.0"},{"isLatest":false,"publishedAt":"2026-07-11T13:05:54Z","tagName":"v0.5.0"},{"isLatest":false,"publishedAt":"2026-07-05T06:12:55Z","tagName":"v0.4.4"},{"isLatest":false,"publishedAt":"2025-11-01T03:40:30Z","tagName":"v0.4.3"},{"isLatest":false,"publishedAt":"2025-10-29T12:39:56Z","tagName":"v0.4.2"},{"isLatest":false,"publishedAt":"2025-10-26T06:47:43Z","tagName":"v0.4.1"},{"isLatest":false,"publishedAt":"2025-10-26T06:05:44Z","tagName":"v0.4.0"},{"isLatest":false,"publishedAt":"2025-10-23T14:20:00Z","tagName":"v0.3.0"},{"isLatest":false,"publishedAt":"2025-10-23T12:46:07Z","tagName":"v0.2.2"},{"isLatest":false,"publishedAt":"2025-10-18T05:12:00Z","tagName":"v0.2.1"}]
```

Key lines:

```
GH_LATEST = v0.9.2
GH_V093_RELEASES = 0
```

**Positive control:** `v0.9.2` carries `isLatest: true` — proving `gh release list` reached GitHub
and the prior release genuinely holds the Latest marker. **Negative assertion:** no entry's
`tagName` is `v0.9.3`.

### Release-workflow probe (with positive control)

```
$ gh run list --workflow=release.yml --limit 20 --json databaseId,createdAt,headBranch,event,conclusion
[{"conclusion":"success","createdAt":"2026-08-30T15:10:43Z","databaseId":33318905691,"event":"push","headBranch":"v0.9.2"},{"conclusion":"success","createdAt":"2026-08-22T07:45:31Z","databaseId":32560457509,"event":"push","headBranch":"v0.9.0"},{"conclusion":"success","createdAt":"2026-08-15T03:08:42Z","databaseId":31861043480,"event":"push","headBranch":"v0.8.0"},{"conclusion":"success","createdAt":"2026-08-11T05:33:22Z","databaseId":31462027486,"event":"push","headBranch":"v0.7.1"},{"conclusion":"failure","createdAt":"2026-08-03T20:08:22Z","databaseId":30848860064,"event":"push","headBranch":"v0.7.0"},{"conclusion":"success","createdAt":"2026-07-28T20:57:57Z","databaseId":30398631991,"event":"push","headBranch":"v0.6.5"},{"conclusion":"success","createdAt":"2026-07-27T22:03:03Z","databaseId":30309278708,"event":"push","headBranch":"v0.6.4"},{"conclusion":"success","createdAt":"2026-07-25T10:06:08Z","databaseId":30153888475,"event":"push","headBranch":"v0.6.3"},{"conclusion":"success","createdAt":"2026-07-23T11:16:03Z","databaseId":30002480654,"event":"push","headBranch":"v0.6.2"},{"conclusion":"success","createdAt":"2026-07-20T03:18:33Z","databaseId":29714380810,"event":"push","headBranch":"v0.6.1"},{"conclusion":"success","createdAt":"2026-07-12T22:04:43Z","databaseId":29210840198,"event":"push","headBranch":"v0.6.0"},{"conclusion":"success","createdAt":"2026-07-11T13:05:05Z","databaseId":29153718002,"event":"push","headBranch":"v0.5.0"},{"conclusion":"success","createdAt":"2026-07-05T06:12:16Z","databaseId":28731646924,"event":"push","headBranch":"v0.4.4"},{"conclusion":"failure","createdAt":"2026-07-05T06:06:40Z","databaseId":28731518799,"event":"push","headBranch":"v0.4.4"},{"conclusion":"success","createdAt":"2025-11-01T03:39:55Z","databaseId":18990823422,"event":"push","headBranch":"v0.4.3"},{"conclusion":"success","createdAt":"2025-10-29T12:39:41Z","databaseId":18908167233,"event":"push","headBranch":"v0.4.2"},{"conclusion":"success","createdAt":"2025-10-26T06:47:27Z","databaseId":18814341329,"event":"push","headBranch":"v0.4.1"},{"conclusion":"success","createdAt":"2025-10-26T06:05:23Z","databaseId":18813905654,"event":"push","headBranch":"v0.4.0"},{"conclusion":"success","createdAt":"2025-10-23T14:03:10Z","databaseId":18751004128,"event":"push","headBranch":"v0.3.0"},{"conclusion":"success","createdAt":"2025-10-23T12:45:30Z","databaseId":18748785140,"event":"push","headBranch":"v0.2.2"}]
```

Key lines:

```
RELEASE_POSITIVE_CONTROL = 33318905691
RELEASE_RUNS_SINCE_START = 0
```

**Positive control:** run `33318905691` (the v0.9.2 release, `2026-08-30`, `success`) is present in
the listing — proving `gh run list` reached GitHub's Actions API. **Negative assertion:** no run in
this 20-row listing was created after `2026-09-02` or carries `headBranch: v0.9.3` — the newest run
in the entire listing is still `33318905691` at `2026-08-30T15:10:43Z`, itself before the cutoff.

### Pull-request probe (with positive control)

```
$ gh pr list --state all --limit 5 --json number
[{"number":142},{"number":141},{"number":140},{"number":139},{"number":138}]

$ gh pr list --head gsd/v0.9.3-toolchain-and-dependency-update-repair --state all --json number,state
[]
```

Key line:

```
BRANCH_PRS = 0
```

**Positive control:** the unscoped `gh pr list` returns five real PR numbers (#138–#142, the
dependabot `uv`-ecosystem PRs from Phases 66/67) — proving the command reached GitHub and the
repository genuinely has PR history. **Negative assertion:** scoped to
`gsd/v0.9.3-toolchain-and-dependency-update-repair` as head branch, the listing is empty — no pull
request exists from the milestone branch.

### Observation 1 verdict

**The fence holds at phase head:**

- `pyproject.toml:7` still reads `version = "0.9.2"` — no version bump landed.
- No `v0.9.3` tag exists locally or on origin (`LOCAL_V093_TAGS = 0`, `REMOTE_V093_TAG = 0`), each
  paired with a positive-controlled probe of the same source (`v0.9.0`/`v0.9.2` locally,
  `v0.9.2`'s remote tag reference for the ls-remote listing).
- v0.9.2 is still the latest published release (`GH_LATEST = v0.9.2`) and nothing is on PyPI
  (`PYPI_093_HTTP = 404`) or GitHub Releases (`GH_V093_RELEASES = 0`) for 0.9.3.
- No `release.yml` run has been created since `2026-09-02` or on a `v0.9.3` ref
  (`RELEASE_RUNS_SINCE_START = 0`), against the positive control that run `33318905691` (the v0.9.2
  release) is present in the same listing.
- No pull request exists from the milestone branch (`BRANCH_PRS = 0`), against the positive control
  that an unscoped `gh pr list` returns real PR numbers.

D-11 records the `0.9.3` number as unclaimed, not decided — whether the next published release is
`0.9.3` or skips it belongs to the next milestone's scoping — and this phase creates no tag,
consistent with every probe above.

## The typsphinx/ fence (constraint 13)

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git merge-base HEAD origin/main
6181768f64b4cee62a77ac4e26c60c3c976cbb6e
```

Key line:

```
MILESTONE_BASE = 6181768f64b4cee62a77ac4e26c60c3c976cbb6e
```

### The scoped diff (the constraint-13 claim)

```
$ git diff --stat 6181768f64b4cee62a77ac4e26c60c3c976cbb6e HEAD -- typsphinx/
(no output)
```

Key line:

```
TYPSPHINX_DIFF_FILES = 0
```

Empty — no line, hunk, or file under `typsphinx/` changed between the milestone base and this
plan's own tip.

### The widened diff (the positive control)

```
$ git diff --name-only 6181768f64b4cee62a77ac4e26c60c3c976cbb6e HEAD -- . ':(exclude).planning' ':(exclude)CHANGELOG.md'
.github/dependabot.yml
.gitignore
CLAUDE.md
flake.nix
pyproject.toml
tests/test_pdf_render_gate.py
tests/test_toolchain_config_gate.py
tox.ini
uv.lock
```

Key line:

```
WIDENED_DIFF_FILES = 9
```

`CHANGELOG.md` is excluded because 69-01 edits it in parallel, in this same wave.

### The version-bump probe

```
$ git log --format=%h -G '^version = ' 6181768f64b4cee62a77ac4e26c60c3c976cbb6e..HEAD -- pyproject.toml
(no output)
```

Key line:

```
VERSION_BUMP_COMMITS = 0
```

No commit in the milestone range touched a `version = ` line in `pyproject.toml`.

**Why the widened diff makes the empty scoped diff meaningful.** A wrong or non-existent anchor (a
typo'd SHA, an anchor accidentally equal to HEAD, or an anchor that predates the repository's
history) would also produce an empty `git diff --stat ... -- typsphinx/` — an empty-diff claim with
no live control is unfalsifiable, because it looks identical whether the tree is genuinely
unchanged under `typsphinx/` or the anchor itself is broken. The widened diff, taken from the exact
same `MILESTONE_BASE` anchor, proves the anchor is real, reachable and genuinely earlier than HEAD:
nine real files changed against it (`.github/dependabot.yml`, `.gitignore`, `CLAUDE.md`,
`flake.nix`, `pyproject.toml`, two test files, `tox.ini`, `uv.lock`) — the Track A (`flake.nix`,
`tox.ini`, the two toolchain-config test files) and Track B (`.github/dependabot.yml`) work from
Phases 64–68, plus the derivative `pyproject.toml`/`uv.lock`/`.gitignore` edits those phases made.
If the scoped diff had been empty because the anchor was wrong, the widened diff would have been
empty too — it is not, so the scoped diff's emptiness is a real finding about `typsphinx/`, not an
artifact of a broken anchor.

## Handoff to observation 2

Observation 2 of 2, and the phase-scoped `typsphinx/` diff from `PHASE_BASE_SHA`
(`2db4e803d36d5f7a5db0a92b08cac4988fa88957`, recorded in `69-CLOSEOUT-GUARD.md` § "Baseline"), are
owned by **plan 69-06**, which runs two waves and one CI dispatch later than this plan — wave 2
(69-03, 69-04, 69-05) sits between this observation and that one, with 69-04 dispatching the
phase's only push and CI run — so the two `OBS*_AT` stamps are genuinely separated rather than
collapsed into one command run. Plan 69-06 appends its findings under a new
`## Observation 2 of 2` section in this same file, together with the post-dispatch commit check
(confirming no commit landed between the CI-dispatched SHA and 69-06's own HEAD that touches the
product tree outside `.planning/`).

## Observation 2 of 2

Recorded inside plan 69-06's own isolated worktree (`worktree-agent-a6a7396dafbb4f7c5`), after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, two waves and one full CI
dispatch after observation 1.

### Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-12T23:01:12Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a6a7396dafbb4f7c5

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2
```

```
$ git rev-parse HEAD
db8751febb2bb68b38641d8c51189ed8d43bef91
```

```
BASE_69_06 = db8751febb2bb68b38641d8c51189ed8d43bef91
```

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-09-12T23:01:58Z
```

```
OBS2_AT = 2026-09-12T23:01:58Z
```

`OBS1_AT` (`69-SC1-INVARIANTS.md` § "Observation 1 of 2") = `2026-09-12T22:35:11Z`. Elapsed
interval: **26 minutes 47 seconds**, spanning wave 2 in full — the local green-tree proof (69-03),
the phase's only push and CI dispatch (69-04, run `34723677990`, 12/12 jobs `success`), and the D-07
trial-merge pre-flight (69-05).

### Version-line probe

```
$ sed -n 7p pyproject.toml
version = "0.9.2"
```

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
```

```
OBS2_LOCAL_V093_TAGS = 0
```

**Positive control:** `v0.9.0` and `v0.9.2` are both still present locally. **Negative assertion:**
no `v0.9.3` tag exists locally.

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
```

```
OBS2_REMOTE_V092_TAG = 1
OBS2_REMOTE_V093_TAG = 0
```

**Positive control:** the count of lines matching the `v0.9.2` tag reference at end-of-line is
exactly `1`, identical to observation 1. **Negative assertion:** the count of lines mentioning
`v0.9.3` in any form is `0`.

### PyPI probe (with positive control)

```
$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json
200

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.3/json
404
```

```
OBS2_PYPI_092_HTTP = 200
OBS2_PYPI_093_HTTP = 404
```

Unchanged from observation 1.

### GitHub Release probe (with positive control)

```
$ gh release list --limit 20 --json tagName,isLatest,publishedAt
[{"isLatest":true,"publishedAt":"2026-08-30T15:11:29Z","tagName":"v0.9.2"},{"isLatest":false,"publishedAt":"2026-08-22T07:46:15Z","tagName":"v0.9.0"},{"isLatest":false,"publishedAt":"2026-08-15T03:09:31Z","tagName":"v0.8.0"},{"isLatest":false,"publishedAt":"2026-08-11T05:34:10Z","tagName":"v0.7.1"},{"isLatest":false,"publishedAt":"2026-08-03T20:09:13Z","tagName":"v0.7.0"},{"isLatest":false,"publishedAt":"2026-07-28T20:58:41Z","tagName":"v0.6.5"},{"isLatest":false,"publishedAt":"2026-07-27T22:03:45Z","tagName":"v0.6.4"},{"isLatest":false,"publishedAt":"2026-07-25T10:07:05Z","tagName":"v0.6.3"},{"isLatest":false,"publishedAt":"2026-07-23T11:16:50Z","tagName":"v0.6.2"},{"isLatest":false,"publishedAt":"2026-07-20T03:19:22Z","tagName":"v0.6.1"},{"isLatest":false,"publishedAt":"2026-07-12T22:05:29Z","tagName":"v0.6.0"},{"isLatest":false,"publishedAt":"2026-07-11T13:05:54Z","tagName":"v0.5.0"},{"isLatest":false,"publishedAt":"2026-07-05T06:12:55Z","tagName":"v0.4.4"},{"isLatest":false,"publishedAt":"2025-11-01T03:40:30Z","tagName":"v0.4.3"},{"isLatest":false,"publishedAt":"2025-10-29T12:39:56Z","tagName":"v0.4.2"},{"isLatest":false,"publishedAt":"2025-10-26T06:47:43Z","tagName":"v0.4.1"},{"isLatest":false,"publishedAt":"2025-10-26T06:05:44Z","tagName":"v0.4.0"},{"isLatest":false,"publishedAt":"2025-10-23T14:20:00Z","tagName":"v0.3.0"},{"isLatest":false,"publishedAt":"2025-10-23T12:46:07Z","tagName":"v0.2.2"},{"isLatest":false,"publishedAt":"2025-10-18T05:12:00Z","tagName":"v0.2.1"}]
```

```
OBS2_GH_LATEST = v0.9.2
OBS2_GH_V093_RELEASES = 0
```

**Positive control:** `v0.9.2` still carries `isLatest: true`. **Negative assertion:** no entry's
`tagName` is `v0.9.3`.

### Release-workflow probe (with positive control)

```
$ gh run list --workflow=release.yml --limit 20 --json databaseId,createdAt,headBranch,event,conclusion
[{"conclusion":"success","createdAt":"2026-08-30T15:10:43Z","databaseId":33318905691,"event":"push","headBranch":"v0.9.2"},{"conclusion":"success","createdAt":"2026-08-22T07:45:31Z","databaseId":32560457509,"event":"push","headBranch":"v0.9.0"},{"conclusion":"success","createdAt":"2026-08-15T03:08:42Z","databaseId":31861043480,"event":"push","headBranch":"v0.8.0"},{"conclusion":"success","createdAt":"2026-08-11T05:33:22Z","databaseId":31462027486,"event":"push","headBranch":"v0.7.1"},{"conclusion":"failure","createdAt":"2026-08-03T20:08:22Z","databaseId":30848860064,"event":"push","headBranch":"v0.7.0"},{"conclusion":"success","createdAt":"2026-07-28T20:57:57Z","databaseId":30398631991,"event":"push","headBranch":"v0.6.5"},{"conclusion":"success","createdAt":"2026-07-27T22:03:03Z","databaseId":30309278708,"event":"push","headBranch":"v0.6.4"},{"conclusion":"success","createdAt":"2026-07-25T10:06:08Z","databaseId":30153888475,"event":"push","headBranch":"v0.6.3"},{"conclusion":"success","createdAt":"2026-07-23T11:16:03Z","databaseId":30002480654,"event":"push","headBranch":"v0.6.2"},{"conclusion":"success","createdAt":"2026-07-20T03:18:33Z","databaseId":29714380810,"event":"push","headBranch":"v0.6.1"},{"conclusion":"success","createdAt":"2026-07-12T22:04:43Z","databaseId":29210840198,"event":"push","headBranch":"v0.6.0"},{"conclusion":"success","createdAt":"2026-07-11T13:05:05Z","databaseId":29153718002,"event":"push","headBranch":"v0.5.0"},{"conclusion":"success","createdAt":"2026-07-05T06:12:16Z","databaseId":28731646924,"event":"push","headBranch":"v0.4.4"},{"conclusion":"failure","createdAt":"2026-07-05T06:06:40Z","databaseId":28731518799,"event":"push","headBranch":"v0.4.4"},{"conclusion":"success","createdAt":"2025-11-01T03:39:55Z","databaseId":18990823422,"event":"push","headBranch":"v0.4.3"},{"conclusion":"success","createdAt":"2025-10-29T12:39:41Z","databaseId":18908167233,"event":"push","headBranch":"v0.4.2"},{"conclusion":"success","createdAt":"2025-10-26T06:47:27Z","databaseId":18814341329,"event":"push","headBranch":"v0.4.1"},{"conclusion":"success","createdAt":"2025-10-26T06:05:23Z","databaseId":18813905654,"event":"push","headBranch":"v0.4.0"},{"conclusion":"success","createdAt":"2025-10-23T14:03:10Z","databaseId":18751004128,"event":"push","headBranch":"v0.3.0"},{"conclusion":"success","createdAt":"2025-10-23T12:45:30Z","databaseId":18748785140,"event":"push","headBranch":"v0.2.2"}]
```

```
OBS2_RELEASE_POSITIVE_CONTROL = 33318905691
OBS2_RELEASE_RUNS_SINCE_START = 0
```

**Positive control:** run `33318905691` (the v0.9.2 release) is still present. **Negative
assertion:** no run in this listing was created after `2026-09-02` or carries `headBranch: v0.9.3` —
the newest run is still `33318905691` at `2026-08-30T15:10:43Z`. This 20-row listing continues to
not surface the phase's own `ci.yml` dispatch, because that dispatch targeted `ci.yml`, never
`release.yml` — confirmed separately below in § "Commits after the CI dispatch".

### Pull-request probe (with positive control)

```
$ gh pr list --state all --limit 5 --json number
[{"number":142},{"number":141},{"number":140},{"number":139},{"number":138}]

$ gh pr list --head gsd/v0.9.3-toolchain-and-dependency-update-repair --state all --json number,state
[]
```

```
OBS2_BRANCH_PRS = 0
```

**Positive control:** the unscoped listing still returns five real PR numbers (#138–#142).
**Negative assertion:** scoped to the milestone branch as head, the listing is still empty.

### Observation 2 verdict

**The fence held across the whole phase, including after the push and the CI dispatch in 69-04:**

- `pyproject.toml:7` still reads `version = "0.9.2"`.
- No `v0.9.3` tag exists locally or on origin (`OBS2_LOCAL_V093_TAGS = 0`,
  `OBS2_REMOTE_V093_TAG = 0`), each paired with the same positive controls as observation 1.
- v0.9.2 is still the latest published release (`OBS2_GH_LATEST = v0.9.2`) and nothing is on PyPI
  (`OBS2_PYPI_093_HTTP = 404`) or GitHub Releases (`OBS2_GH_V093_RELEASES = 0`) for 0.9.3.
- No `release.yml` run has been created since `2026-09-02` or on a `v0.9.3` ref
  (`OBS2_RELEASE_RUNS_SINCE_START = 0`).
- No pull request exists from the milestone branch (`OBS2_BRANCH_PRS = 0`).

Every probe reproduces observation 1's exact command, positive control and result — including the
one push (`becd70c3` → origin) and one `ci.yml` dispatch (`34723677990`, 12/12 `success`) that
happened in between, per `69-CI-EVIDENCE.md`.

## The phase-scoped typsphinx/ diff

`PHASE_BASE_SHA` read from `69-CLOSEOUT-GUARD.md`:

```
$ sed -n "s/^PHASE_BASE_SHA = //p" 69-CLOSEOUT-GUARD.md
2db4e803d36d5f7a5db0a92b08cac4988fa88957
```

```
$ git diff "2db4e803d36d5f7a5db0a92b08cac4988fa88957" HEAD -- typsphinx/
(no output)
```

```
PHASE_TYPSPHINX_DIFF = empty
```

```
$ git diff --numstat "2db4e803d36d5f7a5db0a92b08cac4988fa88957" HEAD -- . ':(exclude).planning'
25	0	CHANGELOG.md
```

```
PHASE_PRODUCT_FILES = CHANGELOG.md
```

**Why both are needed.** The empty scoped diff is the claim: nothing under `typsphinx/` changed
across the whole phase, from its own head to plan 69-06's own tip. But an empty diff from a wrong or
non-existent anchor (a typo'd SHA, or an anchor accidentally equal to HEAD) would look identical to a
genuinely clean tree — unfalsifiable on its own. The widened `--numstat` diff, taken from the exact
same `PHASE_BASE_SHA` anchor, proves the anchor is real and genuinely earlier than HEAD: one file,
`CHANGELOG.md`, with 25 additions and 0 deletions — the exact bullet insertion `69-01` authored in
wave 1 (`69-CHANGELOG-EVIDENCE.md` § "Pure-addition proof"). If the scoped diff had been empty
because the anchor was wrong, the widened diff would have been empty too — it is not, so the scoped
diff's emptiness is a real finding about `typsphinx/`, not an artifact of a broken anchor. This phase
has no amended exception to the `typsphinx/` fence (`69-CONTEXT.md` § "Phase Boundary": "Zero
irreversible action" and no `typsphinx/` change is listed among this phase's canonical references).

## Commits after the CI dispatch

`PUSHED_SHA` read from `69-CI-EVIDENCE.md`:

```
$ sed -n "s/^PUSHED_SHA = //p" 69-CI-EVIDENCE.md
becd70c31bfed573dc10cdc20dcf7a30d57edd57
```

```
$ git merge-base --is-ancestor "becd70c31bfed573dc10cdc20dcf7a30d57edd57" HEAD; echo "exit:$?"
exit:0
```

```
$ git log --oneline becd70c31bfed573dc10cdc20dcf7a30d57edd57..HEAD
db8751fe docs(phase-69): update tracking after wave 2, mark wave 3 executing
45fb9fab chore: merge executor worktree (worktree-agent-a8d6f435633123829)
51a3fef7 chore: merge executor worktree (worktree-agent-a69047240a759c44b)
2fdf2680 chore: merge executor worktree (worktree-agent-a598531089ee1b8e7)
c1e94a50 docs(69-04): complete CI push and dispatch plan
5ad42770 docs(69-03): complete Local Green-Tree Evidence (SC#3, local half) plan
3908f89a docs(69-04): observe CI run to completion, all 12 jobs green, SC#3 MET
eafc47ec feat(69-03): docs clean-build match, executed-versus-skipped table, SC#3 MET
51365fcf feat(69-03): LC_ALL=C full suite, black/mypy/ruff, version-sync family, changelog page gate
2b37fced docs(69-05): complete D-07 REL-12 update-step pre-flight plan
d499486a docs(69-05): merged-tree lint, main protection, merge-method precedent, dependabot census
c53f81cb feat(69-03): tracer — tree identity, product delta, D-06 non-absorption, and green full pytest suite
5c72cb18 docs(69-05): D-07 trial-merge pre-flight — clean merge, valid merged lock
d2315aef docs(69-04): D-14 census, tip fence, fast-forward push and CI dispatch
```

```
$ git diff --name-only becd70c31bfed573dc10cdc20dcf7a30d57edd57 HEAD -- . ':(exclude).planning'
(no output)
```

```
POST_DISPATCH_PRODUCT_FILES = 0
```

```
$ gh run list --workflow=release.yml --limit 20 --json headSha
[{"headSha":"45962faad21520c72ac9f1e14c7f684050826bb6"},{"headSha":"68b92e24e6ca3df410ca0435d226629ef7ef1e2e"},{"headSha":"78e01e53641433a34c1bd8834b6252187fcae4ba"},{"headSha":"48bf135428bb093a77a432d93d16088ce6930342"},{"headSha":"75fd8ed55f4fca206474f9e3aa934921588b52d5"},{"headSha":"839d77f38ffa67f18696265b361f7dcef92f679b"},{"headSha":"2bf6ef318773b239e4ab20b41fbe40ce91337584"},{"headSha":"7f6db629351aa1229a2a07614b6a6f201001ad80"},{"headSha":"54b8fc90df0359b049a1cd9936f03c76d1169f74"},{"headSha":"27e77403f1d62ebec9f36c2c4a9b7c8e16067fc9"},{"headSha":"cc26b4723f671c0ac0dfdae687b6bee722aa6dd0"},{"headSha":"ea153bfca933b92ea23fdfa72efba2afb100f29b"},{"headSha":"dae500a1f2065691972e03cc70a9bf73a90cd26f"},{"headSha":"a2aca47b367b6a4320be6785202cacffad937c5e"},{"headSha":"415498a8cfa7dc21aa09871d4d3b061ed7ba48a2"},{"headSha":"445af8c4b8a30d924d30341bd87b476fa7d0b486"},{"headSha":"0ed33d10acbee8fa935850bcf77404d55832edc9"},{"headSha":"08aeb4b3cfba2293103aefa201b85c89397f50f3"},{"headSha":"28a80a6cc13288eb8c75612693d34a25ae865142"},{"headSha":"c1e2db714cfacd8ef96759ccdebf6e09f5c9152a"}]
```

No entry's `headSha` equals `PUSHED_SHA` — no `release.yml` run at `becd70c3`, confirming
`69-CI-EVIDENCE.md` § "Dispatch count and no release run".

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.3-toolchain-and-dependency-update-repair --event workflow_dispatch --limit 50 --json headSha,createdAt
[{"createdAt":"2026-09-12T22:47:18Z","headSha":"becd70c31bfed573dc10cdc20dcf7a30d57edd57"},{"createdAt":"2026-09-12T07:55:42Z","headSha":"d9c7555323e843b5a389ed4354ce656d2fd05ca2"},{"createdAt":"2026-09-11T15:52:41Z","headSha":"7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5"}]
```

Exactly one row carries `headSha` equal to `PUSHED_SHA` (`becd70c31bfed573dc10cdc20dcf7a30d57edd57`)
— this phase's single dispatch (`69-CI-EVIDENCE.md`'s run `34723677990`). The other two rows are
Phase 65's dispatch (`d9c75553…`) and Phase 64's dispatch (`7afbf5b2…`), neither belonging to this
phase.

**The D-13 reading.** The single dispatch ran on the tip carrying every product-tree change of the
phase — `PUSHED_SHA` equals `BASE_69_04` from `69-CI-EVIDENCE.md`, and that file's own § "Tip
identity and fence" showed the pushed tree byte-identical to that worktree's HEAD, which carried
wave 1's merged CHANGELOG edit and nothing else. Every commit landing after `PUSHED_SHA` — thirteen
commits, listed above — touches only `.planning/`, which no CI job reads
(`POST_DISPATCH_PRODUCT_FILES = 0`). D-13 permits a second dispatch only for a code-affecting
change; no such change has occurred anywhere in this phase, so the post-dispatch commits are not a
stale-tip violation, and no second dispatch is warranted.

---
*Phase: 69-v0-9-3-close-prep-prep-only-unpublished*
*Plan: 02, 06*
