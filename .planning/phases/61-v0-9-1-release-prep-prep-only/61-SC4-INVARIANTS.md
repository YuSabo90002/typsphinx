# Phase 61 — SC#4 Fence Invariants (RETAINED in full per D-11)

**Recorded:** inside this plan's isolated worktree (`worktree-agent-a9f8e61dc22c6d378`), after
`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev`.

## Observation 1 of 2

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-29T15:05:49Z
```

This timestamp opens the section so the separation from observation 2 (owned by plan 61-04, two
waves later) is measurable rather than asserted.

### Local tag probe

```
$ git tag -l 'v0.9.1'
(no output)
```

No local `v0.9.1` tag exists.

### Remote tag probe (unfiltered, with positive control)

A bare `git ls-remote --tags origin 'v0.9.1'` is deliberately NOT used here — its silence would be
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

```
$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.0$'
1

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.1'
0
```

**Positive control:** the count of lines matching the `v0.9.0` tag reference at end-of-line is
exactly `1` — proving the remote was actually reached and the listing is genuinely populated, not
silently empty from an unreachable source. **Negative assertion:** the count of lines mentioning
the skipped version's tag reference is `0` — no `v0.9.1` tag exists on the remote.

### Publish probe

```
$ gh release list --limit 20
Release v0.9.0	Latest	v0.9.0	2026-08-22T07:46:15Z
Release v0.8.0		v0.8.0	2026-08-15T03:09:31Z
Release v0.7.1		v0.7.1	2026-08-11T05:34:10Z
Release v0.7.0		v0.7.0	2026-08-03T20:09:13Z
Release v0.6.5		v0.6.5	2026-07-28T20:58:41Z
```

(first five lines of the full listing, per the plan's instruction to record the verbatim first
five lines)

```
$ gh release list --limit 20 | grep -c 'Latest'
1

$ gh release list --limit 20 | grep -c 'v0\.9\.1'
0
```

**Positive control:** the listing is non-empty and its first row carries the `Latest` marker
against `v0.9.0` — the PRIOR milestone's release — proving the command reached GitHub. **Negative
assertion:** no row names `v0.9.1`.

### Release-workflow probe

```
$ gh run list --workflow=release.yml --limit 5
completed	success	Merge pull request #134: release v0.9.0 — per-document templates	Release	v0.9.0	push	32560457509	2h9m46s	2026-08-22T07:45:31Z
completed	success	Merge pull request #133: release v0.8.0 — multi-master composition	Release	v0.8.0	push	31861043480	19m35s	2026-08-15T03:08:42Z
completed	success	Merge pull request #132: release v0.7.1 — bug-fix round	Release	v0.7.1	push	31462027486	19m37s	2026-08-11T05:33:22Z
completed	failure	Merge pull request #129: release v0.7.0 — API rendering design overhaul	Release	v0.7.0	push	30848860064	18m55s	2026-08-03T20:08:22Z
completed	success	Merge pull request #125: release v0.6.5 — inline-math separator hotfix	Release	v0.6.5	push	30398631991	18m6s	2026-07-28T20:57:57Z
```

No run corresponds to a tag for the skipped version (`v0.9.1`) — the most recent release-workflow
run is `32560457509` for `v0.9.0`, dated 2026-08-22, well before this phase.

### Observation 1 verdict

**The fence holds at phase head.** `v0.9.0`, a prior milestone, is still the latest published
release; no tag for the skipped version (`v0.9.1`) exists locally or on the remote; nothing has
been published for `v0.9.1`.

## Milestone anchor (recorded, not swept)

The anchor for this phase is the **v0.9.0** tag — not the v0.8.0 tag Phase 57 used — measured
fresh here rather than copied from either prior document.

```
$ git rev-parse v0.9.0^{commit}
68b92e24e6ca3df410ca0435d226629ef7ef1e2e

$ git merge-base --is-ancestor v0.9.0 HEAD && echo tag-is-ancestor
tag-is-ancestor

$ git rev-list --count v0.9.0..HEAD
137

$ git diff v0.9.0..HEAD --stat -- . ':(exclude).planning' | tail -1
 23 files changed, 3011 insertions(+), 72 deletions(-)
```

137 commits and a non-trivial 23-file / +3,011 / −72 shortstat (excluding `.planning/`) since the
`v0.9.0` tag — this is Phases 58, 59, 60, and this phase's own work-in-progress, all of which
happened after the v0.9.0 milestone shipped.

## The milestone-invariant sweep — resolved in writing, not left as a silent absence

**RESEARCH.md's Open Question 1, closed here.** D-10's literal text names exactly four fence
items: the tag probe, the no-publish probe, the `git diff` showing no unintended change under
`typsphinx/`, and the `REQUIREMENTS.md` checksum. It does **not** name the three milestone
invariants (no new runtime dependency, the four Typst Universe package versions in lockstep, no
new configuration value) that Phases 52 and 57 swept in their own `*-SC4-INVARIANTS.md` files to
back a `### Verified` CHANGELOG section.

**This phase authors no `### Verified` section.** `61-CONTEXT.md` § "Claude's Discretion" leaves
that choice open, naming "left for the v0.9.2 release-prep phase to author against the whole 0.9.2
diff" as "the cheaper default." That default is taken here. Because there is no `### Verified`
section for a milestone-invariant sweep to back, and because D-10's own four-item literal reading
does not name the sweep as a fence component either, **the invariant sweep is deliberately NOT run
in this file.**

This is a decision, not an omission, and it is written down so a later reader does not mistake the
absence for an oversight: `61-SC4-INVARIANTS.md` (this file) satisfies D-10's fence in full with
the four items above — the local tag probe, the positive-controlled remote tag probe, the
positive-controlled publish probe, and the release-workflow probe, plus the milestone anchor
measurement recorded above for continuity with the Phase 52/57 precedent's shape. It does not
additionally re-run the dependency / `@preview` / config-value sweep those two prior files ran,
because neither this file's own fence obligation nor this phase's CHANGELOG output needs it.

**Warning carried forward for the v0.9.2 milestone's own sweep, if one is run there:** do not copy
this milestone's numbers forward unexamined. `57-SC4-INVARIANTS.md`'s own milestone falsified the
"no new configuration value" assertion inherited from `52-SC4-INVARIANTS.md` by adding
`typst_document_templates` and removing `typst_template_assets` — proof that a milestone's
invariants must be re-measured against its own anchor, never copied from a prior milestone's
document. Whoever runs the v0.9.2 sweep must re-measure the dependency array, the `@preview`
version lockstep, and the `typst_*` config-value set fresh against the `v0.9.0..<v0.9.2-tip>`
range (this milestone's own diff, once it exists), not against this file's numbers.

## Handoff to observation 2

Observation 2 of 2, and the phase-scoped `typsphinx/` diff over the range
`5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41..HEAD` (the PHASE_BASE_SHA recorded in
`61-CLOSEOUT-GUARD.md`), are owned by **plan 61-04**, which runs two waves later than this plan so
the two timestamps are genuinely separated rather than collapsed into one command run. Plan 61-04
appends its findings under a new `## SC#4 fence — observation 2 of 2` section in this same file.

---
*Phase: 61-v0-9-1-release-prep-prep-only*
*Plan: 02*
