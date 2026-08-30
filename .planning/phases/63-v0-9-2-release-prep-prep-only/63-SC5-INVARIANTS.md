# Phase 63 — SC#5 Fence Invariants

**Recorded:** inside this plan's isolated worktree (`worktree-agent-abc32982f68a82498`), after
`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev`.

## Observation 1 of 2

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-30T11:17:14Z
```

This timestamp opens the section so the separation from observation 2 (owned by plan 63-04, two
waves later) is measurable rather than asserted.

### Local tag probe

```
$ git tag -l 'v0.9.2'
(no output)

$ git tag -l 'v0.9.0'
v0.9.0
```

**Positive control:** `v0.9.0` — a tag known to exist — is returned non-empty, proving the local tag
listing mechanism itself works. **The actual assertion:** no local `v0.9.2` tag exists; an empty
result from the first command is only a finding because the second command's non-empty result rules
out a broken `git tag -l` invocation.

### Remote tag probe (unfiltered, with positive control)

A bare `git ls-remote --tags origin 'v0.9.2'` is deliberately NOT used here — its silence would be
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
```

(fetched once, redirected to `/tmp/63-tags.txt`; both counts below are derived from that single
fetch, never from a second network round-trip)

```
$ grep -c 'refs/tags/v0\.9\.0' /tmp/63-tags.txt
2

$ grep -c 'refs/tags/v0\.9\.2' /tmp/63-tags.txt
0
```

**Positive control:** the count of lines matching the `v0.9.0` tag reference is `2` (the lightweight
tag line and its `^{}` dereferenced-commit line) — proving the remote was actually reached and the
listing is genuinely populated, not silently empty from an unreachable source. Note that unlike
`61-SC4-INVARIANTS.md`'s own `refs/tags/v0\.9\.0$` anchored pattern, this grep is unanchored and
correctly counts both lines the tag produces on the remote — both counted as "at least 1", satisfying
the positive-control requirement. **Negative assertion:** the count of lines mentioning the skipped
version's tag reference is `0` — no `v0.9.2` tag exists on the remote.

### Publish probe

```
$ gh release list --limit 20
Release v0.9.0	Latest	v0.9.0	2026-08-22T07:46:15Z
Release v0.8.0		v0.8.0	2026-08-15T03:09:31Z
Release v0.7.1		v0.7.1	2026-08-11T05:34:10Z
Release v0.7.0		v0.7.0	2026-08-03T20:09:13Z
Release v0.6.5		v0.6.5	2026-07-28T20:58:41Z
Release v0.6.4		v0.6.4	2026-07-27T22:03:45Z
Release v0.6.3		v0.6.3	2026-07-25T10:07:05Z
Release v0.6.2		v0.6.2	2026-07-23T11:16:50Z
Release v0.6.1		v0.6.1	2026-07-20T03:19:22Z
Release v0.6.0		v0.6.0	2026-07-12T22:05:29Z
Release v0.5.0		v0.5.0	2026-07-11T13:05:54Z
Release v0.4.4		v0.4.4	2026-07-05T06:12:55Z
Release v0.4.3		v0.4.3	2025-11-01T03:40:30Z
Release v0.4.2		v0.4.2	2025-10-29T12:39:56Z
Release v0.4.1		v0.4.1	2025-10-26T06:47:43Z
Release v0.4.0		v0.4.0	2025-10-26T06:05:44Z
Release v0.3.0		v0.3.0	2025-10-23T14:20:00Z
Release v0.2.2		v0.2.2	2025-10-23T12:46:07Z
Release v0.2.1		v0.2.1	2025-10-18T05:12:00Z
Release v0.2.0		v0.2.0	2025-10-16T13:30:48Z
```

(fetched once, redirected to `/tmp/63-releases.txt`; both counts below are derived from that single
fetch)

```
$ grep -c 'Latest' /tmp/63-releases.txt
1

$ grep -c 'v0\.9\.2' /tmp/63-releases.txt
0
```

**Positive control:** the listing is non-empty and its first row carries the `Latest` marker against
`v0.9.0` — the prior milestone's own release — proving the command reached GitHub. **Negative
assertion:** no row names `v0.9.2`.

```
$ gh release view v0.9.2
release not found
```

Exit code: `1` (non-zero, confirmed separately from the piped commands above).

### Release-workflow probe

```
$ gh run list --workflow=release.yml --limit 5
completed	success	Merge pull request #134: release v0.9.0 — per-document templates	Release	v0.9.0	push	32560457509	2h9m46s	2026-08-22T07:45:31Z
completed	success	Merge pull request #133: release v0.8.0 — multi-master composition	Release	v0.8.0	push	31861043480	19m35s	2026-08-15T03:08:42Z
completed	success	Merge pull request #132: release v0.7.1 — bug-fix round	Release	v0.7.1	push	31462027486	19m37s	2026-08-11T05:33:22Z
completed	failure	Merge pull request #129: release v0.7.0 — API rendering design overhaul	Release	v0.7.0	push	30848860064	18m55s	2026-08-03T20:08:22Z
completed	success	Merge pull request #125: release v0.6.5 — inline-math separator hotfix	Release	v0.6.5	push	30398631991	18m6s	2026-07-28T20:57:57Z
```

This is a READ-ONLY listing — no command in this plan dispatches `release.yml`, by tag push or by
`workflow_dispatch`. No run corresponds to a tag for the target version (`v0.9.2`) — the most recent
release-workflow run is `32560457509` for `v0.9.0`, dated 2026-08-22, well before this phase.

### Observation 1 verdict

**The fence holds at phase head.** `v0.9.0`, a prior milestone, is still the latest published
release; no tag for the target version (`v0.9.2`) exists locally or on the remote; nothing has been
published for `v0.9.2`; `release.yml` has not been dispatched by this phase. This observation was
taken in **wave 1** (plan 63-02).

## Milestone anchor (recorded, not swept)

The anchor for this milestone is the **v0.9.0** tag — measured fresh here rather than copied from
`61-SC4-INVARIANTS.md`'s own anchor measurement.

```
$ git rev-parse v0.9.0
ada0b845cf1f5a495dc7c522b80e79ed5c76004d
```

Note: `v0.9.0` is a lightweight tag, so `git rev-parse v0.9.0` returns the commit id directly (no
separate `^{commit}` dereference is needed, unlike an annotated tag).

```
$ git rev-list --count v0.9.0..HEAD
223

$ git diff --stat v0.9.0..HEAD -- typsphinx/ | tail -3
 typsphinx/translator.py        |  33 ++++-
 typsphinx/writer.py            |   6 +-
 5 files changed, 408 insertions(+), 58 deletions(-)
```

223 commits and a non-trivial 5-file / +408 / −58 shortstat under `typsphinx/` since the `v0.9.0`
tag — this is Phases 58, 59, 60, 62, and this phase's own work-in-progress, all of which happened
after the v0.9.0 milestone shipped. This establishes the milestone anchor is real and
non-trivially distant, which is the precondition for every scoped diff in this phase (plan 63-04's
`typsphinx/` diff against `PHASE_BASE_SHA`) being a finding rather than an artifact.

## The milestone-invariant sweep — resolved in writing, not left as a silent absence

`61-SC4-INVARIANTS.md` § "The milestone-invariant sweep — resolved in writing, not left as a silent
absence" explicitly deferred to Phase 63 the question of which plan runs the sweep backing the
release entry's dependency and `@preview` claims, warning explicitly against copying its own
milestone's numbers forward unexamined.

**Resolved here, in writing:** the sweep (no new runtime/dev dependency, the four `@preview` package
versions in lockstep across `writer.py`/`template_engine.py`/`templates/base.typ`, no new `typst_*`
configuration value) is owned by **plan 63-01 Task 2**, run as four targeted measurements against
the `v0.9.0` anchor with a widened-scope positive control, and recorded in
`63-CHANGELOG-EVIDENCE.md` under its own milestone-invariant-sweep heading.

**This plan does not re-run the sweep and does not assert its result.** Plan 63-01 executes in the
same wave (wave 1) as this plan, in a separate worktree, and its artifact (`63-CHANGELOG-EVIDENCE.md`)
is not readable from this worktree. Recording an unmeasured result here would be exactly the
inherited-evidence failure this phase's `<threat_model>` and `must_haves.prohibitions` forbid: "MUST
NOT record inherited, paraphrased, recalled or fabricated evidence as this phase's own."

## Handoff to observation 2

Observation 2 of 2 belongs to **plan 63-04**, which runs in **wave 3** — two waves later than this
plan's wave 1 — so the two observations are separated by intervening waves (SC#5's own explicit
requirement) rather than by wall-clock luck alone.

Observation 2 additionally carries the scoped `typsphinx/` diff against `PHASE_BASE_SHA` (recorded
in `63-CLOSEOUT-GUARD.md` § "Baseline") paired with a same-anchor widened diff as its positive
control. The widened diff's expected non-empty result for **this** phase is **the five files the
bump commit and the tuple edit touch** — `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`,
and `tests/test_changelog_page_gate.py` — not Phase 61's single-file (`CHANGELOG.md`-only) result,
because Phase 63 performs an actual version bump where Phase 61 did not.

---
*Phase: 63-v0-9-2-release-prep-prep-only*
*Plan: 02, 04*
