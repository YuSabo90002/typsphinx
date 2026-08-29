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

## Observation 2 of 2

Recorded inside this plan's own isolated worktree (`worktree-agent-a85f5e28eb4ad5cb4`), after
`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev`, two waves after observation 1 and
after the full 3-OS CI dispatch recorded in `61-CI-EVIDENCE.md` (run `33260111745`, dispatched at
`2026-08-29T15:23:09Z`, concluded `success` on all 12 jobs).

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-29T15:44:05Z
```

### Local tag probe

```
$ git tag -l 'v0.9.1'
(no output)
```

No local `v0.9.1` tag exists — unchanged from observation 1.

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
```

```
$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.0$'
1

$ git ls-remote --tags origin | grep -c 'refs/tags/v0\.9\.1'
0
```

**Positive control:** the count of lines matching the `v0.9.0` tag reference at end-of-line is
exactly `1` — proving the remote was actually reached and the listing is genuinely populated, not
silently empty from an unreachable source, exactly as in observation 1. **Negative assertion:** the
count of lines mentioning the skipped version's tag reference is `0` — no `v0.9.1` tag exists on the
remote.

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

```
$ gh release list --limit 20 | grep -c 'Latest'
1

$ gh release list --limit 20 | grep -c 'v0\.9\.1'
0
```

**Positive control:** the listing is non-empty and its first row carries the `Latest` marker against
`v0.9.0` — the PRIOR milestone's release — proving the command reached GitHub, exactly as in
observation 1. **Negative assertion:** no row names `v0.9.1`.

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
run is still `32560457509` for `v0.9.0`, dated 2026-08-22, well before this phase. Unchanged from
observation 1.

### Observation 2 verdict — the separation, stated explicitly

**Observation 1 timestamp:** `2026-08-29T15:05:49Z` (`61-SC4-INVARIANTS.md` § "Observation 1 of 2",
plan 61-02, wave 1).

**Observation 2 timestamp (this section):** `2026-08-29T15:44:05Z` (plan 61-04, wave 3).

**Elapsed interval:** 38 minutes 16 seconds. This observation is taken two waves later than
observation 1 and after the full 3-OS CI dispatch recorded in `61-CI-EVIDENCE.md` (run
`33260111745`) has completed all 12 jobs `success` — so the fence is shown to have held across the
phase's real span, not only at its own head. Every probe above repeats observation 1's exact
command and positive control and reproduces the identical result: no local or remote `v0.9.1` tag,
no GitHub Release naming `v0.9.1`, no `release.yml` run for `v0.9.1`. **The fence holds at both
ends of the phase.**

## The typsphinx/ diff (SC#4)

`PHASE_BASE_SHA` read back from `61-CLOSEOUT-GUARD.md` § "Baseline":

```
5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41
```

### The scoped diff (the SC#4 claim)

```
$ git diff 5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41..HEAD -- typsphinx/
(no output)
```

Empty — no line, hunk, or file under `typsphinx/` changed between the recorded phase-head anchor
and this plan's own tip.

### The widened diff (the positive control)

```
$ git diff --stat 5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41..HEAD -- . ':(exclude).planning'
 CHANGELOG.md | 28 ++++++++++++++++++++++++++++
 1 file changed, 28 insertions(+)

$ git diff --name-only 5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41..HEAD -- . ':(exclude).planning'
CHANGELOG.md
```

Exactly one file, `CHANGELOG.md`, with a nonzero insertion count (28) and zero deletions.

**What the pair proves, and why both are needed.** The empty scoped diff is the SC#4 claim itself —
nothing under `typsphinx/` changed. But an empty `git diff` from a wrong or non-existent anchor (a
typo'd SHA, an anchor that does not exist in this history, or an anchor accidentally set equal to
HEAD) would produce the exact same empty output, and would look identical to a genuinely clean
tree — an empty-diff claim with no live control is unfalsifiable. The non-empty widened diff, taken
from the SAME `PHASE_BASE_SHA` anchor, is what makes the emptiness meaningful: it proves the anchor
is real, reachable, and genuinely earlier than HEAD, because a real, non-trivial change (the 28-line
CHANGELOG.md addition plan 61-01 authored) shows up against it. If the scoped diff had been empty
because the anchor was wrong, the widened diff would have been empty too — it is not, so the scoped
diff's emptiness is a real finding about `typsphinx/`, not an artifact of a broken anchor.

**No amended exception exists for this phase.** Unlike Phase 57, where an owner-approved mid-phase
`builder.py` message fix broke this exact fence and had to be argued at hunk level
(`57-SC4-INVARIANTS.md`'s own precedent), Phase 61's `61-CONTEXT.md` `<domain>` "Out of scope"
section states plainly: "Any `typsphinx/` behaviour change. The prep-only fence is absolute in this
phase — there is no Phase-57-style amended exception, and any pressure to create one is a signal to
stop and ask the owner rather than to proceed." No plan in this phase requested or was granted such
an exception. A clean diff is therefore the expected result here, not a fortunate one, and any hit
against it would be a real finding to report — never explained away as an approved exception,
because none exists.

## Commits after the CI dispatch

Dispatched head SHA, read back from `61-CI-EVIDENCE.md` § "Run": `14fcb460919455d8910fff4dece8b948de96ecc4`.

```
$ git log --oneline 14fcb460919455d8910fff4dece8b948de96ecc4..HEAD
3852f651 docs(phase-61): update tracking after wave 2
a7910587 chore: merge executor worktree (worktree-agent-a8497ee77be99419f)
eaf52719 docs(61-03): append self-check results to SUMMARY.md
06da1f18 docs(61-03): complete local green-tree proof and fresh CI dispatch plan
546b8751 docs(61-03): dispatch fresh 3-OS CI run and record all 12 job conclusions

$ git diff --name-only 14fcb460919455d8910fff4dece8b948de96ecc4..HEAD -- . ':(exclude).planning'
(no output)
```

Five commits landed after the dispatched head, and the widened `git diff --name-only` excluding
`.planning/` over that same range produces no output — every one of those five commits touches only
`.planning/` documentation (SUMMARY.md, STATE.md tracking, and this plan's own evidence appends).
This is what keeps `61-CI-EVIDENCE.md`'s green 12/12 result valid at the phase's end: the product
tree CI actually tested (at the dispatched SHA) is byte-identical to the product tree at this plan's
own HEAD, because nothing landed in between that touches it.

---
*Phase: 61-v0-9-1-release-prep-prep-only*
*Plan: 02, 04*
