# Phase 71 — SC#1 Fence Invariants (unpublished-shaped tree)

Recorded inside this plan's isolated worktree (`worktree-agent-a571bab6fc41395dc`), after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`.

## Observation 1 of 2

```
OBS1_AT = 2026-09-13T08:31:24Z
```

This timestamp opens the section so the separation from observation 2 (owned by plan 71-06, two
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
```

Key lines:

```
LOCAL_V093_TAGS = 0
LOCAL_V094_TAGS = 0
```

**Positive control:** `v0.9.0` and `v0.9.2` are both present locally, proving `git tag -l` reaches
real tag data rather than an empty/broken tag database. **Negative assertion:** no `v0.9.3` or
`v0.9.4` tag exists locally.

### Remote tag probe (unfiltered, with positive control)

A bare `git ls-remote --tags origin 'v0.9.3'` is deliberately NOT used — its silence would be
indistinguishable from a network failure. Instead the unfiltered listing is fetched once and three
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

$ git ls-remote --tags origin | grep -cE 'refs/tags/v0\.9\.[34]'
0
```

Key lines:

```
REMOTE_V092_TAG = 1
REMOTE_V093_TAG = 0
REMOTE_V094_TAG = 0
```

**Positive control:** the count of lines matching the `v0.9.2` tag reference at end-of-line is
exactly `1` — proving the remote was actually reached and the listing is genuinely populated, not
silently empty from an unreachable source. **Negative assertion:** the count of lines mentioning
`v0.9.3` or `v0.9.4` in any form (including `^{}` peeled entries) is `0` — no `v0.9.3` or `v0.9.4`
tag exists on the remote.

### PyPI probe (with positive control)

```
$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json
200

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.3/json
404

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.4/json
404
```

Key lines:

```
PYPI_092_HTTP = 200
PYPI_093_HTTP = 404
PYPI_094_HTTP = 404
```

**Positive control:** `0.9.2`'s PyPI JSON endpoint returns `200`, proving PyPI itself is reachable
and the prior release is genuinely published there. **Negative assertion:** `0.9.3`'s and
`0.9.4`'s endpoints both return `404` — nothing is uploaded for either number.

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
```

**Positive control:** `v0.9.2` carries `isLatest: true` — proving `gh release list` reached
GitHub and the prior release genuinely holds the Latest marker. **Negative assertion:** no entry's
`tagName` is `v0.9.3` or `v0.9.4`.

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

**Positive control:** run `33318905691` (the v0.9.2 release, `2026-08-30`, `success`) is present
in the listing — proving `gh run list` reached GitHub's Actions API. **Negative assertion:** no run
in this 20-row listing was created after `2026-08-31` or carries `headBranch: v0.9.3` or
`headBranch: v0.9.4` — the newest run in the entire listing is still `33318905691` at
`2026-08-30T15:10:43Z`, itself before the cutoff.

### Pull-request probe (with positive control)

```
$ gh pr list --state all --limit 5 --json number
[{"number":144},{"number":143},{"number":142},{"number":141},{"number":140}]

$ gh pr list --head gsd/v0.9.4-typing-modernization --state all --json number,state
[]
```

Key line:

```
BRANCH_PRS = 0
```

**Positive control:** the unscoped `gh pr list` returns five real PR numbers (#140–#144) —
proving the command reached GitHub and the repository genuinely has PR history. **Negative
assertion:** scoped to `gsd/v0.9.4-typing-modernization` as head branch, the listing is empty — no
pull request exists from the milestone branch.

### Observation 1 verdict

**The fence holds at phase head:**

- `pyproject.toml:7` still reads `version = "0.9.2"` — no version bump landed.
- No `v0.9.3` or `v0.9.4` tag exists locally or on origin (`LOCAL_V093_TAGS = 0`,
  `LOCAL_V094_TAGS = 0`, `REMOTE_V093_TAG = 0`, `REMOTE_V094_TAG = 0`), each paired with a
  positive-controlled probe of the same source (`v0.9.0`/`v0.9.2` locally, `v0.9.2`'s remote tag
  reference for the ls-remote listing).
- v0.9.2 is still the latest published release (`GH_LATEST = v0.9.2`) and nothing is on PyPI
  (`PYPI_093_HTTP = 404`, `PYPI_094_HTTP = 404`) or GitHub Releases (`GH_V093_RELEASES = 0`,
  `GH_V094_RELEASES = 0`) for either number.
- No `release.yml` run has been created since `2026-08-31` or on a `v0.9.3`/`v0.9.4` ref
  (`RELEASE_RUNS_SINCE_V092 = 0`), against the positive control that run `33318905691` (the v0.9.2
  release) is present in the same listing.
- No pull request exists from the milestone branch (`BRANCH_PRS = 0`), against the positive
  control that an unscoped `gh pr list` returns real PR numbers.

D-08 records both `0.9.3` and `0.9.4` as unclaimed, not decided, and this phase creates no tag,
consistent with every probe above.

## Milestone fences

```
$ git fetch origin main
From https://github.com/YuSabo90002/typsphinx
 * branch              main       -> FETCH_HEAD

$ git merge-base HEAD origin/main
d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d

$ git rev-parse origin/main
d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```

Key lines:

```
MILESTONE_BASE = d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
ORIGIN_MAIN_SHA_OBS1 = d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```

`MILESTONE_BASE` equals `ORIGIN_MAIN_SHA_OBS1` — the branch carries no `main` commit HEAD lacks
(HEAD is entirely ahead of `main`, not diverged).

```
$ git log --format=%h -G '^version = ' d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d..HEAD -- pyproject.toml
(no output)
```

Key line:

```
VERSION_BUMP_COMMITS = 0
```

```
$ git diff --name-only d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d HEAD -- .github/
(no output)
```

Key line:

```
WORKFLOW_DIFF_FILES = 0
```

Constraint 12: no workflow file is edited.

```
$ git diff --name-only d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d HEAD -- typsphinx/ tests/
tests/conftest.py
tests/test_bundle_layout_sweep_gate.py
tests/test_include_edge_derivation_unit.py
tests/test_include_ledger_removal_gate.py
typsphinx/__init__.py
typsphinx/builder.py
typsphinx/template_engine.py
typsphinx/template_registry.py
typsphinx/translator.py
typsphinx/writer.py
```

Key line:

```
MILESTONE_CODE_FILES = 10
```

Exactly Phase 70's ten converted files.

## Code freeze since Phase 70 (D-11 part 1), observation 1

```
$ git log --format='%H %s' -1 -- typsphinx/ tests/
e721ff899a981eafdad696ef1a9c93aaab41ece5 chore: merge executor worktree (worktree-agent-a9a3a29e4a793db3b)
```

Key line:

```
CODE_FREEZE_ANCHOR = e721ff899a981eafdad696ef1a9c93aaab41ece5
```

Phase 70's final code commit, confirmed by measurement: the live `git log` above prints exactly
this SHA, so no commit touched code after Phase 70.

```
$ git merge-base --is-ancestor e721ff899a981eafdad696ef1a9c93aaab41ece5 HEAD; echo "exit:$?"
exit:0
```

```
$ git diff --stat e721ff899a981eafdad696ef1a9c93aaab41ece5 HEAD -- typsphinx/ tests/
(no output)
```

Key line:

```
CODE_FREEZE_DIFF_FILES = 0
```

The positive control:

```
$ git diff --name-only 697a113221a8a267d7e8c6dd1f2b95672f9454d2 e721ff899a981eafdad696ef1a9c93aaab41ece5 -- typsphinx/ tests/
tests/conftest.py
tests/test_bundle_layout_sweep_gate.py
tests/test_include_edge_derivation_unit.py
tests/test_include_ledger_removal_gate.py
typsphinx/__init__.py
typsphinx/builder.py
typsphinx/template_engine.py
typsphinx/template_registry.py
typsphinx/translator.py
typsphinx/writer.py
```

Key line:

```
ANCHOR_CONTROL_FILES = 10
```

`697a1132…` is Phase 70's `PHASE_BASE_SHA`, read from `70-BASELINE-EVIDENCE.md`. It lists the
same ten files as § "Milestone fences". The same pathspec is non-empty across Phase 70's own
range, so an empty result after the anchor is not a broken pathspec or a wrong anchor.

The Phase 70 CI cross-check: `PUSHED_SHA` read from `70-CI-EVIDENCE.md` is
`e70e31fba9039133a153a5bba16577d7b2f889c1`.

```
$ git merge-base --is-ancestor e721ff899a981eafdad696ef1a9c93aaab41ece5 e70e31fba9039133a153a5bba16577d7b2f889c1; echo "exit:$?"
exit:0

$ git diff --quiet e721ff899a981eafdad696ef1a9c93aaab41ece5 e70e31fba9039133a153a5bba16577d7b2f889c1 -- typsphinx/ tests/; echo "exit:$?"
exit:0
```

Key line:

```
PHASE70_CI_TIP_SAME_CODE = yes
```

The code on this branch is the code Phase 70's CI run tested.

## Handoff to observation 2

Observation 2 of 2, the phase-scoped `typsphinx/`/`tests/` diff from `PHASE_BASE_SHA`
(`f1f7d54a61d74c3972f1df0508ac994c001dda7e`, recorded in `71-CLOSEOUT-GUARD.md` § "Baseline"), the
post-dispatch check, D-11 part 1 on the close tip, and D-11 part 2 (the masked-AST re-run), are
owned by **plan 71-06**. It runs two waves and one CI dispatch later than this plan — wave 2
(71-03, 71-04, 71-05) sits between this observation and that one, with 71-04 dispatching the
phase's only push and CI run — so the two `OBS*_AT` stamps are genuinely separated rather than
collapsed into one command run. Plan 71-06 appends its findings under a new `## Observation 2 of
2` section in this same file, together with the phase-scoped diff, the post-dispatch commit
check, the D-11 part 1 close-tip re-verification, and the D-11 part 2 masked-AST re-run.

## Observation 2 of 2

Recorded inside plan 71-06's own isolated worktree (`worktree-agent-a0a3bf0ed4ab836a4`), after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13`,
two waves and one full CI dispatch after observation 1.

### Head check and provisioning

```
$ date -u +%FT%TZ
2026-09-13T09:11:31Z

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a0a3bf0ed4ab836a4

$ test -f .git; echo "exit:$?"
exit:0

$ grep -c typsphinx-fhs-run "$(command -v uv)"
2

$ git rev-parse HEAD
9c66a8505e36af774af9d6c4260206a697a7b0d4
```

```
BASE_71_06 = 9c66a8505e36af774af9d6c4260206a697a7b0d4
```

```
SCRATCH_71_06 = /tmp/tmp.Q2KAowP2ae
```

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-09-13T09:11:36Z
```

```
OBS2_AT = 2026-09-13T09:11:36Z
```

`OBS1_AT` (`71-SC1-INVARIANTS.md` § "Observation 1 of 2") is `2026-09-13T08:31:24Z`.
Elapsed interval: 40 minutes 12 seconds, spanning wave 2 in full — the local green-tree proof
(71-03), the phase's only push and CI dispatch (71-04, run `34748483361`, 12/12 jobs `success`,
with a cancelled surplus dispatch `34748491771` recorded and read per the owner's AMENDED decision
in `71-CI-EVIDENCE.md`), and the D-05 trial-merge pre-flight (71-05).

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

$ git tag -l 'v0.9.4'
(no output)
```

```
OBS2_LOCAL_V093_TAGS = 0
OBS2_LOCAL_V094_TAGS = 0
```

**Positive control:** `v0.9.0` and `v0.9.2` are both still present locally. **Negative assertion:**
no `v0.9.3` or `v0.9.4` tag exists locally.

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

$ git ls-remote --tags origin | grep -cE 'refs/tags/v0\.9\.[34]'
0
```

```
OBS2_REMOTE_V092_TAG = 1
OBS2_REMOTE_V093_TAG = 0
OBS2_REMOTE_V094_TAG = 0
```

**Positive control:** the count of lines matching the `v0.9.2` tag reference at end-of-line is
exactly `1`, identical to observation 1. **Negative assertion:** the count of lines mentioning
`v0.9.3` or `v0.9.4` in any form is `0`.

### PyPI probe (with positive control)

```
$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json
200

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.3/json
404

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.4/json
404
```

```
OBS2_PYPI_092_HTTP = 200
OBS2_PYPI_093_HTTP = 404
OBS2_PYPI_094_HTTP = 404
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
OBS2_GH_V094_RELEASES = 0
```

**Positive control:** `v0.9.2` still carries `isLatest: true`. **Negative assertion:** no entry's
`tagName` is `v0.9.3` or `v0.9.4`.

### Release-workflow probe (with positive control)

```
$ gh run list --workflow=release.yml --limit 20 --json databaseId,createdAt,headBranch,event,conclusion
[{"conclusion":"success","createdAt":"2026-08-30T15:10:43Z","databaseId":33318905691,"event":"push","headBranch":"v0.9.2"},{"conclusion":"success","createdAt":"2026-08-22T07:45:31Z","databaseId":32560457509,"event":"push","headBranch":"v0.9.0"},{"conclusion":"success","createdAt":"2026-08-15T03:08:42Z","databaseId":31861043480,"event":"push","headBranch":"v0.8.0"},{"conclusion":"success","createdAt":"2026-08-11T05:33:22Z","databaseId":31462027486,"event":"push","headBranch":"v0.7.1"},{"conclusion":"failure","createdAt":"2026-08-03T20:08:22Z","databaseId":30848860064,"event":"push","headBranch":"v0.7.0"},{"conclusion":"success","createdAt":"2026-07-28T20:57:57Z","databaseId":30398631991,"event":"push","headBranch":"v0.6.5"},{"conclusion":"success","createdAt":"2026-07-27T22:03:03Z","databaseId":30309278708,"event":"push","headBranch":"v0.6.4"},{"conclusion":"success","createdAt":"2026-07-25T10:06:08Z","databaseId":30153888475,"event":"push","headBranch":"v0.6.3"},{"conclusion":"success","createdAt":"2026-07-23T11:16:03Z","databaseId":30002480654,"event":"push","headBranch":"v0.6.2"},{"conclusion":"success","createdAt":"2026-07-20T03:18:33Z","databaseId":29714380810,"event":"push","headBranch":"v0.6.1"},{"conclusion":"success","createdAt":"2026-07-12T22:04:43Z","databaseId":29210840198,"event":"push","headBranch":"v0.6.0"},{"conclusion":"success","createdAt":"2026-07-11T13:05:05Z","databaseId":29153718002,"event":"push","headBranch":"v0.5.0"},{"conclusion":"success","createdAt":"2026-07-05T06:12:16Z","databaseId":28731646924,"event":"push","headBranch":"v0.4.4"},{"conclusion":"failure","createdAt":"2026-07-05T06:06:40Z","databaseId":28731518799,"event":"push","headBranch":"v0.4.4"},{"conclusion":"success","createdAt":"2025-11-01T03:39:55Z","databaseId":18990823422,"event":"push","headBranch":"v0.4.3"},{"conclusion":"success","createdAt":"2025-10-29T12:39:41Z","databaseId":18908167233,"event":"push","headBranch":"v0.4.2"},{"conclusion":"success","createdAt":"2025-10-26T06:47:27Z","databaseId":18814341329,"event":"push","headBranch":"v0.4.1"},{"conclusion":"success","createdAt":"2025-10-26T06:05:23Z","databaseId":18813905654,"event":"push","headBranch":"v0.4.0"},{"conclusion":"success","createdAt":"2025-10-23T14:03:10Z","databaseId":18751004128,"event":"push","headBranch":"v0.3.0"},{"conclusion":"success","createdAt":"2025-10-23T12:45:30Z","databaseId":18748785140,"event":"push","headBranch":"v0.2.2"}]
```

```
OBS2_RELEASE_RUNS_SINCE_V092 = 0
```

**Positive control:** run `33318905691` (the v0.9.2 release, `2026-08-30`, `success`) is still
present in the listing. **Negative assertion:** no run in this 20-row listing was created after
`2026-08-31` or carries `headBranch: v0.9.3` or `headBranch: v0.9.4` — the newest run in the entire
listing is still `33318905691` at `2026-08-30T15:10:43Z`, itself before the cutoff. This 20-row
listing continues to not surface the phase's own `ci.yml` dispatches, because those dispatches
targeted `ci.yml`, never `release.yml` — confirmed separately below in § "Commits after the CI
dispatch".

### Pull-request probe (with positive control)

```
$ gh pr list --state all --limit 5 --json number
[{"number":144},{"number":143},{"number":142},{"number":141},{"number":140}]

$ gh pr list --head gsd/v0.9.4-typing-modernization --state all --json number,state
[]
```

```
OBS2_BRANCH_PRS = 0
```

**Positive control:** the unscoped `gh pr list` still returns five real PR numbers (#140–#144).
**Negative assertion:** scoped to `gsd/v0.9.4-typing-modernization` as head branch, the listing is
still empty.

### Observation 2 verdict

**The fence held across the whole phase, including after 71-04's push and dispatch:**

- `pyproject.toml:7` still reads `version = "0.9.2"`.
- No `v0.9.3` or `v0.9.4` tag exists locally or on origin (`OBS2_LOCAL_V093_TAGS = 0`,
  `OBS2_LOCAL_V094_TAGS = 0`, `OBS2_REMOTE_V093_TAG = 0`, `OBS2_REMOTE_V094_TAG = 0`), each paired
  with the same positive controls as observation 1.
- v0.9.2 is still the latest published release (`OBS2_GH_LATEST = v0.9.2`) and nothing is on PyPI
  (`OBS2_PYPI_093_HTTP = 404`, `OBS2_PYPI_094_HTTP = 404`) or GitHub Releases
  (`OBS2_GH_V093_RELEASES = 0`, `OBS2_GH_V094_RELEASES = 0`) for either number.
- No `release.yml` run has been created since `2026-08-31` or on a `v0.9.3`/`v0.9.4` ref
  (`OBS2_RELEASE_RUNS_SINCE_V092 = 0`).
- No pull request exists from the milestone branch (`OBS2_BRANCH_PRS = 0`).

Every probe reproduces observation 1's exact command, positive control and result — including the
one push (`PUSHED_SHA`, `7a42bf99…`) and the CI dispatch (`RUN_ID` `34748483361`, 12/12 `success`,
plus the cancelled surplus run `34748491771`, per `71-CI-EVIDENCE.md`'s AMENDED reading) that
happened in between. Both unpublished numbers, `0.9.3` and `0.9.4`, remain unclaimed (D-08).

## The phase-scoped product diff

`PHASE_BASE_SHA` read from `71-CLOSEOUT-GUARD.md`:

```
$ sed -n "s/^PHASE_BASE_SHA = //p" .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CLOSEOUT-GUARD.md
f1f7d54a61d74c3972f1df0508ac994c001dda7e
```

```
$ git diff f1f7d54a61d74c3972f1df0508ac994c001dda7e HEAD -- typsphinx/ tests/
(no output)
```

```
PHASE_CODE_DIFF = empty
```

```
$ git diff --numstat f1f7d54a61d74c3972f1df0508ac994c001dda7e HEAD -- . ':(exclude).planning'
10	0	CHANGELOG.md
```

```
PHASE_PRODUCT_FILES = CHANGELOG.md
```

**Why both are needed.** The empty scoped diff is the claim: nothing under `typsphinx/` or
`tests/` changed across the whole phase, from its own head to this plan's own tip. But an empty
diff from a wrong or non-existent anchor would look identical to a genuinely clean tree —
unfalsifiable on its own. The widened `--numstat` diff, taken from the exact same
`PHASE_BASE_SHA` anchor, proves the anchor is real and genuinely earlier than HEAD: one file,
`CHANGELOG.md`, with 10 additions and 0 deletions — the CHANGELOG bullet insertion `71-01`
authored in wave 1. If the scoped diff had been empty because the anchor was wrong, the widened
diff would have been empty too — it is not, so the scoped diff's emptiness is a real finding about
`typsphinx/` and `tests/`, not an artifact of a broken anchor.

## Commits after the CI dispatch

`PUSHED_SHA` read from `71-CI-EVIDENCE.md`:

```
$ sed -n "s/^PUSHED_SHA = //p" .planning/phases/71-v0-9-4-close-prep-prep-only-unpublished/71-CI-EVIDENCE.md
7a42bf996b1aaca24a8b17346be78459e6d41e2b
```

```
$ git merge-base --is-ancestor 7a42bf996b1aaca24a8b17346be78459e6d41e2b HEAD; echo "exit:$?"
exit:0
```

```
$ git log --oneline 7a42bf996b1aaca24a8b17346be78459e6d41e2b..HEAD
9c66a850 docs(phase-71): update tracking after wave 2, mark wave 3 executing
40756fed docs(phase-71): record the owner-approved reading of 71-04's dispatch count
d6258bc7 chore: merge executor worktree (worktree-agent-a506a8049f151539c)
441d1cad chore: merge executor worktree (worktree-agent-a43d13d9aa59679b9)
6bd414a6 chore: merge executor worktree (worktree-agent-a7407c28186c095e6)
f96b9a0d docs(71-04): complete plan summary, flag duplicate-dispatch anomaly for owner decision
8afdb899 docs(71-04): transcribe the completed 12-job CI run and ruff's verdict
030fce91 docs(71-03): complete local green-tree evidence plan
ebd7690e docs(71-03): docs builds match baseline, executed-vs-skipped table, SC#3 local verdict MET
ad9309e7 feat(71-04): decoy census, fast-forward push and one CI dispatch on the phase tip
5916b65e docs(71-03): LC_ALL=C suite, format/type/lint, version-sync family, changelog gate
c5d2a9f0 docs(71-05): complete REL-13 update-step pre-flight plan
0545556c feat(71-05): merged-tree lint clean, main protection and merge-method precedent, PR census
c4321ab1 docs(71-03): tree identity, product delta and D-05 non-absorption, full pytest suite
f6b170e3 feat(71-05): trial merge of origin/main proven conflict-free and reproducible, merged lock valid
```

```
$ git diff --name-only 7a42bf996b1aaca24a8b17346be78459e6d41e2b HEAD -- . ':(exclude).planning'
(no output)
```

```
POST_DISPATCH_PRODUCT_FILES = 0
```

```
$ gh run list --workflow=release.yml --limit 20 --json headSha
```
(20 rows, none matching `7a42bf996b1aaca24a8b17346be78459e6d41e2b` — the most recent is
`45962faad21520c72ac9f1e14c7f684050826bb6`, the v0.9.2 release tag commit; verified with the
verify's own scoped query below.)

```
$ gh run list --workflow=release.yml --limit 20 --json headSha --jq '[.[] | select(.headSha == "7a42bf996b1aaca24a8b17346be78459e6d41e2b")] | length'
0
```

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha,createdAt
[{"createdAt":"2026-09-13T08:47:58Z","headSha":"7a42bf996b1aaca24a8b17346be78459e6d41e2b"},{"createdAt":"2026-09-13T08:47:28Z","headSha":"7a42bf996b1aaca24a8b17346be78459e6d41e2b"},{"createdAt":"2026-09-13T06:09:27Z","headSha":"e70e31fba9039133a153a5bba16577d7b2f889c1"}]
```

**Verbatim, as the project briefing requires — the literal count at `PUSHED_SHA` is `2`, not the
`1` the plan's own automated verify asserts:**

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha --jq '[.[] | select(.headSha == "7a42bf996b1aaca24a8b17346be78459e6d41e2b")] | length'
2
```

This is `71-CI-EVIDENCE.md`'s own recorded `DISPATCH_COUNT = 2` and its "AMENDED 2026-09-13 —
dispatch count" addendum, re-measured here on the close tip rather than transcribed: two
`workflow_dispatch` runs carry `PUSHED_SHA`, `34748483361` (the run created by an attempt using the
plan's exact literal dispatch command, chronologically first, concluded `success`) and
`34748491771` (a later alias-form retry, since cancelled). Per the owner's AMENDED reading, this is
read as "exactly one run at `PUSHED_SHA` concluded `success` and it is `RUN_ID`; the only other run
at `PUSHED_SHA` is the cancelled `34748491771`" — re-measured here:

```
$ gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha,conclusion,databaseId -q '[.[] | select(.headSha == "7a42bf996b1aaca24a8b17346be78459e6d41e2b" and .conclusion == "success")] | length'
1

$ gh run list --workflow=ci.yml --branch gsd/v0.9.4-typing-modernization --event workflow_dispatch --limit 50 --json headSha,conclusion,databaseId -q '[.[] | select(.headSha == "7a42bf996b1aaca24a8b17346be78459e6d41e2b" and .conclusion != "success")] | map(.databaseId) | join(",")'
34748491771
```

The AMENDED-form check (one success run, and the sole non-success run is exactly the cancelled
`34748491771`) passes; the plan's literal `= 1` verify assertion on the raw count does not, and is
recorded as an owner-approved AMENDED reading rather than a defect — see the plan's own Deviations
section in this plan's SUMMARY.

**The D-10 reading.** The single intended dispatch ran on the tip carrying every product-tree
change of the phase, and every later commit is `.planning/`-only, which no CI job reads
(`POST_DISPATCH_PRODUCT_FILES = 0`). D-10 permits a second dispatch only for a code-affecting
change; none was warranted or deliberately made here — the surplus run was an unintended side
effect of GitHub's dispatch API returning false-failure responses to retries of the same single
intended dispatch, per `71-CI-EVIDENCE.md` § "D-10 final tip" — so the post-dispatch commits are
not a stale-tip violation.

## Code freeze on the close tip (D-11 part 1)

`CODE_FREEZE_ANCHOR` and `MILESTONE_BASE`, read from observation 1's sections:

```
CODE_FREEZE_ANCHOR = e721ff899a981eafdad696ef1a9c93aaab41ece5
MILESTONE_BASE = d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```

```
$ git log --format='%H %s' -1 -- typsphinx/ tests/
e721ff899a981eafdad696ef1a9c93aaab41ece5 chore: merge executor worktree (worktree-agent-a9a3a29e4a793db3b)
```

The printed SHA equals `CODE_FREEZE_ANCHOR` — no commit has touched code since Phase 70, even on
the close tip.

```
$ git diff --stat e721ff899a981eafdad696ef1a9c93aaab41ece5 HEAD -- typsphinx/ tests/
(no output)
```

```
CLOSE_CODE_FREEZE_DIFF_FILES = 0
```

The positive control, the same pathspec across Phase 70's own range:

```
$ git diff --name-only 697a113221a8a267d7e8c6dd1f2b95672f9454d2 e721ff899a981eafdad696ef1a9c93aaab41ece5 -- typsphinx/ tests/
tests/conftest.py
tests/test_bundle_layout_sweep_gate.py
tests/test_include_edge_derivation_unit.py
tests/test_include_ledger_removal_gate.py
typsphinx/__init__.py
typsphinx/builder.py
typsphinx/template_engine.py
typsphinx/template_registry.py
typsphinx/translator.py
typsphinx/writer.py
```

```
CLOSE_ANCHOR_CONTROL_FILES = 10
```

Ten files, exactly Phase 70's converted-file set — the same pathspec is non-empty across Phase 70's
own range, so the empty result above is not a broken pathspec or a wrong anchor.

```
$ git fetch origin main
$ git merge-base HEAD origin/main
d14ca458fd8cd6cd1374fb9de3b5f45d3a17cc2d
```

Equal to `MILESTONE_BASE` — no `main` commit was absorbed since observation 1.

```
CLOSE_MAIN_ABSORBED = no
```

---
*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Plan: 02, 06*
