# Phase 33: v0.6.4 Release Prep — Publish & Owner-Manual Handoff Checklist

This document is the explicit hand-off for the half of REL-02 this phase structurally cannot
satisfy. It is written in English directly (not translated after the fact), because it is a phase
deliverable that merges to a public branch — D-05 establishes English as the register for
publicly-visible planning documents.

## What this phase satisfied, and what it did not

REL-02 reads: *"`typsphinx 0.6.4` is published to PyPI, its `Documentation` metadata points at
Read the Docs, and both `/en/stable/` and `/ja/stable/` serve that same released version."*

**Satisfied by this phase (33-01 through 33-04):**
- The version literal is bumped to `0.6.4` across `pyproject.toml`, `README.md`, and `uv.lock`
  (SC#1, plan 33-01).
- The `## [0.6.4]` CHANGELOG entry is curated and the tail release/compare link block is updated
  (SC#2, plan 33-02).
- The `Documentation` metadata URL is confirmed by a real, freshly-taken HTTP fetch on the
  prepared tree — see `33-RELEASE-EVIDENCE.md` § SC#3 (this plan, Task 1).
- The three milestone invariants are asserted over the **full** milestone diff with verbatim
  command output — see `33-RELEASE-EVIDENCE.md` § SC#4 (this plan, Task 2).

**Not satisfied by this phase, and structurally out of reach here:**
`typsphinx 0.6.4` live on PyPI, and `/en/stable/` **and** `/ja/stable/` both serving that released
version, both require the `v0.6.4` git tag. This phase deliberately creates no tag — see the
"Proof the fence held" section below. Until the tag exists, is pushed, and `release.yml` runs
against it, neither half of that claim can be true. **This is recorded here as an unmet criterion
handed off to `/gsd-complete-milestone` and the owner, not as a formality, and not as something
this phase is claiming to have effectively done.**

## Checklist

Each item names its owner (the `/gsd-complete-milestone` command, or a human/owner-manual step)
and any ordering dependency on the items before it.

### 1. Mark pull request #124 ready for review and merge it

**Owner:** `/gsd-complete-milestone`.
**Ordering:** first — everything below depends on the milestone branch reaching `main`.
PR #124 currently carries this milestone's full diff (Phases 29 through 33). Marking it ready and
merging it is the action that makes `main` the tree everything else below operates on.

### 2. Push the `v0.6.4` tag

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 1 (the tag should point at the merged `main`, not the pre-merge branch).
Pushing `v0.6.4` fires `release.yml`, which publishes `typsphinx==0.6.4` to PyPI (wheel + sdist)
and creates the GitHub Release. The Release body's single source is the `## [0.6.4]` CHANGELOG
entry authored by plan 33-02 — no separate release-notes drafting step is needed.

### 3. Bump the submodule and push a matching tag in `typsphinx-doc-translations`

**Owner:** `/gsd-complete-milestone` (or owner, if the milestone-close command does not yet
automate cross-repository tagging).
**Ordering:** alongside item 2, before item 5.
This is REL-02's standing cost added by Phase 30's D-07: `/ja/stable/` resolves against the
**translations** repository's own tags, not this repository's. From this release onward, every
`typsphinx` release tags **two** repositories, not one — the parent (this repository) and
`typsphinx-doc-translations`. Omitting this step leaves `/ja/stable/` unresolvable (404 or stuck
on a stale version) while `/en/stable/` works fine, which is exactly the kind of partial-success
failure mode this milestone's invariants exist to catch.

### 4. Perform the three owed post-merge Read the Docs / repository flips

**Owner:** human (owner-manual — no automated acceptance criterion is possible; RTD project
settings have no `.readthedocs.yaml` representation).
**Ordering:** after item 1 (these flips assume `main` now carries the merged milestone tree).

- Flip the parent (English) Read the Docs project's **Default branch** setting from the milestone
  branch (`gsd/v0.6.4-read-the-docs-migration`) to `main`.
- Flip the Japanese Read the Docs project's **Default branch** setting to `main` as well.
- Flip `.gitmodules`' `branch` value (the `typsphinx-doc-translations` submodule pin) from the
  milestone branch to `main`.

These are Phase 30.1 carry-forwards (`PD-02`). The submodule currently tracks the milestone branch
because, at the time Phase 30.1 ran, `main` had neither `.readthedocs.yaml` nor the
`_resolve_language()` seam that makes the Japanese build resolve correctly — pointing at `main`
then would have built a tree without the RTD machinery this milestone adds. Now that the milestone
is merged, all three should point at `main`.

### 5. Flip Default Version to `stable` — only after the tag build is green

**Owner:** human (owner-manual).
**Ordering:** strictly after item 2, and only once the `v0.6.4` tag's RTD build has actually
completed and shows green. Do not perform this step preemptively.

- Flip the **English** project's Default Version from `latest` to `stable`.
- Then re-confirm the **Japanese** project's independent version activation: translation projects
  do not inherit the parent's activated-version list (this is why RTD-04's Owner-Manual Steps #4
  calls this a re-check, not an assumption). Verify that `/ja/stable/` resolves to the **same**
  tag as `/en/stable/` — i.e. the translations-repository tag pushed in item 3 above, not a stale
  or missing one.

Until the tag builds green, Default Version must stay `latest` — RTD's root redirect follows the
Default Version setting even when the target version does not exist yet, so flipping early would
break the root redirect for every visitor until the build catches up.

### 6. Close GitHub issue #119

**Owner:** human (owner review required before posting).
**Ordering:** after item 1 (closing while `main` still served the old dead links would promise an
undelivered fix — Phase 31's D-15).
Use the reply draft already prepared at
`.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-ISSUE-119-REPLY-DRAFT.md`. Post
it (after owner review of the wording) and close the issue.

### 7. Re-confirm `origin/gh-pages` does not exist

**Owner:** human or `/gsd-complete-milestone` (recommended, not blocking).
**Ordering:** any time after item 1, ideally before or shortly after the merge.
Run `git ls-remote --heads origin gh-pages` and confirm empty output. Phase 32's teardown is
reversible by accident: a push to `main` before the milestone merge could let the retired
`peaceiris/actions-gh-pages` deploy action recreate the branch (the gh-pages revival hazard
documented in `.planning/phases/32-github-pages-teardown-irreversible/32-CONTEXT.md`). This item
is a recommended safety re-check, not a blocking gate.

### 8. Move the two resolved todos out of `.planning/todos/pending/`

**Owner:** human or `/gsd-complete-milestone`.
**Ordering:** any time; purely administrative, no functional dependency.
- `github-io-doc-links-404-missing-en-prefix` — resolved by Phase 31.
- `docs-usage-installation-orphan-class` — resolved by Phase 30.

Both already carry `status: resolved` / `resolves_phase:` frontmatter; this step is filing
cleanup, not re-verification.

## Not done in this phase, by design

This phase (and no other plan within Phase 33) performs any of the following. The scope fence is
absolute — every one of these belongs to `/gsd-complete-milestone` or to the owner, never to a
prep-only release phase:

- No `git tag v0.6.4` (or any tag) was created.
- No release workflow (`release.yml`) was triggered.
- Nothing was published to PyPI.
- No GitHub Release was created.
- Pull request #124 was not marked ready for review and was not merged.
- GitHub issue #119 was not closed.
- No Read the Docs setting was changed — Default Version, Default branch, or otherwise.

## Proof the fence held

Both checks below were run at the end of this plan's execution and both must be empty for the
fence to hold:

Command:
```
$ git tag -l v0.6.4
```
Verbatim output:
```
(empty)
```

Command:
```
$ git ls-remote --tags origin v0.6.4
```
Verbatim output:
```
(empty)
```

No file was created under `.git/refs/tags/` during this phase. Both results confirm this phase
leaves zero irreversible published state — if this phase (or any earlier plan in it) were
interrupted or only partially merged, there is no tag, no PyPI release, and no GitHub Release to
unwind. The repository's git-tag state is exactly as it was before Phase 33 began.
