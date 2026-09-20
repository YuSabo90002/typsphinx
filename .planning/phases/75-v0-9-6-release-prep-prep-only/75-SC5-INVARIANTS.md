# Phase 75 — SC5 Invariants (zero irreversible action)

## Observation 1 of 2

```
$ date -u +%FT%TZ
2026-09-20T08:41:41Z
```

```
OBS1_AT = 2026-09-20T08:41:41Z
```

Every probe below is recorded with its verbatim command and output. Each expected-empty probe is
paired with a control that must be non-empty, so an empty result cannot come from a broken
command.

### Local tags

```
$ git tag -l 'v0.9.6'
(no output)

$ git tag -l 'v0.9.2'
v0.9.2
```

```
LOCAL_V096_TAGS = 0
LOCAL_V092_TAGS = 1
```

### Remote tags

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
```

```
$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.2$'
1

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.6'
0
```

```
REMOTE_V092_TAG = 1
REMOTE_V096_TAG = 0
```

### PyPI

```
$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.6/json
404

$ curl -sS -o /dev/null -w '%{http_code}' https://pypi.org/pypi/typsphinx/0.9.2/json
200
```

```
PYPI_096_HTTP = 404
PYPI_092_HTTP = 200
```

### GitHub Release

```
$ gh release list --limit 50 --json tagName,isLatest
[{"isLatest":true,"tagName":"v0.9.2"},{"isLatest":false,"tagName":"v0.9.0"},{"isLatest":false,"tagName":"v0.8.0"},{"isLatest":false,"tagName":"v0.7.1"},{"isLatest":false,"tagName":"v0.7.0"},{"isLatest":false,"tagName":"v0.6.5"},{"isLatest":false,"tagName":"v0.6.4"},{"isLatest":false,"tagName":"v0.6.3"},{"isLatest":false,"tagName":"v0.6.2"},{"isLatest":false,"tagName":"v0.6.1"},{"isLatest":false,"tagName":"v0.6.0"},{"isLatest":false,"tagName":"v0.5.0"},{"isLatest":false,"tagName":"v0.4.4"},{"isLatest":false,"tagName":"v0.4.3"},{"isLatest":false,"tagName":"v0.4.2"},{"isLatest":false,"tagName":"v0.4.1"},{"isLatest":false,"tagName":"v0.4.0"},{"isLatest":false,"tagName":"v0.3.0"},{"isLatest":false,"tagName":"v0.2.2"},{"isLatest":false,"tagName":"v0.2.1"},{"isLatest":false,"tagName":"v0.2.0"},{"isLatest":false,"tagName":"v0.1.0b1"}]
```

The `tagName` of the entry whose `isLatest` is true is `v0.9.2`. No entry has `tagName` `v0.9.6`.

```
GH_LATEST = v0.9.2
GH_V096_RELEASES = 0
```

### Release workflow run census

```
$ gh run list --workflow=release.yml --limit 20 --json headBranch,databaseId,createdAt
[{"createdAt":"2026-08-30T15:10:43Z","databaseId":33318905691,"headBranch":"v0.9.2"},{"createdAt":"2026-08-22T07:45:31Z","databaseId":32560457509,"headBranch":"v0.9.0"},{"createdAt":"2026-08-15T03:08:42Z","databaseId":31861043480,"headBranch":"v0.8.0"},{"createdAt":"2026-08-11T05:33:22Z","databaseId":31462027486,"headBranch":"v0.7.1"},{"createdAt":"2026-08-03T20:08:22Z","databaseId":30848860064,"headBranch":"v0.7.0"},{"createdAt":"2026-07-28T20:57:57Z","databaseId":30398631991,"headBranch":"v0.6.5"},{"createdAt":"2026-07-27T22:03:03Z","databaseId":30309278708,"headBranch":"v0.6.4"},{"createdAt":"2026-07-25T10:06:08Z","databaseId":30153888475,"headBranch":"v0.6.3"},{"createdAt":"2026-07-23T11:16:03Z","databaseId":30002480654,"headBranch":"v0.6.2"},{"createdAt":"2026-07-20T03:18:33Z","databaseId":29714380810,"headBranch":"v0.6.1"},{"createdAt":"2026-07-12T22:04:43Z","databaseId":29210840198,"headBranch":"v0.6.0"},{"createdAt":"2026-07-11T13:05:05Z","databaseId":29153718002,"headBranch":"v0.5.0"},{"createdAt":"2026-07-05T06:12:16Z","databaseId":28731646924,"headBranch":"v0.4.4"},{"createdAt":"2026-07-05T06:06:40Z","databaseId":28731518799,"headBranch":"v0.4.4"},{"createdAt":"2025-11-01T03:39:55Z","databaseId":18990823422,"headBranch":"v0.4.3"},{"createdAt":"2025-10-29T12:39:41Z","databaseId":18908167233,"headBranch":"v0.4.2"},{"createdAt":"2025-10-26T06:47:27Z","databaseId":18814341329,"headBranch":"v0.4.1"},{"createdAt":"2025-10-26T06:05:23Z","databaseId":18813905654,"headBranch":"v0.4.0"},{"createdAt":"2025-10-23T14:03:10Z","databaseId":18751004128,"headBranch":"v0.3.0"},{"createdAt":"2025-10-23T12:45:30Z","databaseId":18748785140,"headBranch":"v0.2.2"}]

$ gh run list --workflow=release.yml --limit 20 --json headBranch,databaseId,createdAt --jq '[.[] | select(.createdAt > "2026-08-31")] | length'
0
```

No run has been created since the v0.9.2 publish run (`33318905691`, created `2026-08-30`).

```
RELEASE_RUNS_SINCE_V092 = 0
RELEASE_POSITIVE_CONTROL = 33318905691
```

`RELEASE_POSITIVE_CONTROL` resolves to a real `release.yml` run on the `v0.9.2` ref — the v0.9.2
publish itself, confirming the query above is not returning an empty list because the query is
wrong:

```
$ gh run list --workflow=release.yml --limit 20 --json databaseId,headBranch --jq '[.[] | select(.databaseId == 33318905691 and .headBranch == "v0.9.2")] | length'
1
```

### Decoy branch on origin

```
$ git ls-remote --heads origin
334b4da7ce20d74b2710c0d0b60d74e11245d114	refs/heads/gsd/v0.9.4-typing-modernization
1d8c76c6d1ac4f00da9b5ef39cf4488a855a6114	refs/heads/gsd/v0.9.5-docs-link-check-and-navigation
e54d47d0b00d77f600d1aa27b0f78a031db055c7	refs/heads/gsd/v0.9.6-doctest-block-rendering-and-release
6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b	refs/heads/main

$ git ls-remote --heads origin | grep -c 'gsd/v0\.9\.6-milestone'
0
```

No `gsd/v0.9.6-milestone` decoy branch exists on origin. Only the canonical
`gsd/v0.9.6-doctest-block-rendering-and-release` branch and `main` are present.

```
DECOY_ON_ORIGIN_OBS1 = 0
```

## Version and branch state at observation 1

```
$ sed -n 7p pyproject.toml
version = "0.9.2"
```

The version literal still reads `0.9.2` at this observation.

```
$ git log --format=%h -G '^version = ' 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b..HEAD -- pyproject.toml
(no output)
```

No version-bump commit exists yet at this point in the phase — this plan (75-01) runs before the
version-bump plan (75-03).

```
VERSION_BUMP_COMMITS_OBS1 = 0
```

## Handoff to observation 2

Plan 75-07 repeats every probe above as observation 2 of 2, after waves 2 and 3 have run — so the
two observations are separated by the bump commit (75-03), the local green-tree runs (75-04), the
trial merge and Dependabot census (75-05), the push and the dispatched CI run (75-06), not by
wall-clock luck. At observation 2 the version literal is expected to read `0.9.6` while every probe
above (except the version-bump commit count, which is expected to become 1) is still expected to be
empty/zero, with the same `v0.9.2` controls still present as positive controls.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Plan: 01*
