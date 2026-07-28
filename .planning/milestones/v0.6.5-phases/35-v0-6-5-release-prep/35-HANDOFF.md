# Phase 35: v0.6.5 Release Prep — Publish & Owner-Manual Handoff Checklist

This document is the explicit hand-off for the half of REL-03 this phase structurally cannot
satisfy. It is written in English directly (the standing `.planning/` convention that postdates the
five pre-existing Japanese-language pending todos), because it is a phase deliverable that merges to
a public branch — following the `33-HANDOFF.md` precedent.

## What this phase satisfied, and what it did not

REL-03 reads: *"v0.6.5 release prepared — `pyproject.toml` bumped to `0.6.5` as the sole version
literal with `uv.lock` in lockstep, plus a curated `## [0.6.5]` CHANGELOG entry with the tail
link-block rollover (`[0.6.5]:` tag link added, `[Unreleased]:` compare advanced). The publish half
executes at `/gsd-complete-milestone`."*

**Satisfied by this phase's plans:**
- ROADMAP Phase 35 **SC#1** — the version literal is bumped to `0.6.5` across `pyproject.toml`,
  `README.md`, and `uv.lock` in lockstep, `typsphinx.__version__` reports `0.6.5`, and both
  version-sync guard tests are green (plan 35-03, re-confirmed fresh in `35-RELEASE-EVIDENCE.md` §
  SC#1).
- **SC#2** — the curated `## [0.6.5]` CHANGELOG entry (lead paragraph + `### Fixed` + `### Verified`)
  is inserted and the tail link block is rolled over (plan 35-04, cited in `35-RELEASE-EVIDENCE.md` §
  SC#2).
- **SC#3** — the post-bump tree is proven green end to end on a live run: the full pytest suite,
  `black`/`ruff`/`mypy`, the full-corpus `-b typstpdf` regression gate, and (per D-12) both docs
  dogfooding builds `tox -e docs-html` / `tox -e docs-pdf` (this plan, Task 1; see
  `35-RELEASE-EVIDENCE.md` § SC#3).
- **SC#4** — the milestone invariants are asserted mechanically over the full milestone diff
  (SHA-anchored on merge-base `eb696bb`, never on a commit count): zero new runtime dependencies, no
  `@preview` version bump, and the `typsphinx/`-tree change confined to exactly
  `typsphinx/translator.py` (this plan, Task 2; see `35-RELEASE-EVIDENCE.md` § SC#4).
- **SC#5** — no irreversible action was taken: `git tag -l v0.6.5` and
  `git ls-remote --tags origin v0.6.5` both print nothing (this plan, Task 2; independently re-proven
  fresh below in "Proof the fence held").
- Adjacent to REL-03's own scope but completed in this phase: the three test-side Phase 34 review
  Warnings WR-02/WR-03/WR-04 closed (plan 35-01), and the two deliberate deferrals (WR-01, the
  `release.yml` release-notes-body rework) filed as pending todos (plan 35-02).

**Not satisfied by this phase, and structurally out of reach here:** the entire publish half —
pushing the `v0.6.5` tag, `release.yml` firing to publish to PyPI and create the GitHub Release,
opening and merging the pull request, and the two-repository tagging cost on
`typsphinx-doc-translations` — belongs to `/gsd-complete-milestone`. The Read the Docs confirmation
that `stable` is green at `v0.6.5` for both projects is owner-manual and also out of reach here. This
is recorded as a handoff, not as something this phase is claiming to have effectively done.

## Checklist

Each item names its owner and any ordering dependency on the items before it.

### 1. Open the pull request and merge it

**Owner:** `/gsd-complete-milestone`.
**Ordering:** first — every item below depends on the milestone branch reaching `main`.
This phase's own branch (and the two phases before it, 34 and 35) carries the full v0.6.5 milestone
diff. Opening it for review and merging is the action that makes `main` the tree everything below
operates on.

### 2. Push the `v0.6.5` tag

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 1 (the tag should point at the merged `main`, not the pre-merge branch).
Pushing `v0.6.5` fires `.github/workflows/release.yml`, which publishes `typsphinx==0.6.5` to PyPI
(wheel + sdist) and creates the GitHub Release. Note that the release body will still carry the
hand-rolled commit-dump bloat this workflow's "Generate release notes" step produces (a `git log
$PREV_TAG..$TAG --pretty="- %s (%h)"` block, ~296 lines in the v0.6.4 precedent) — reworking it to
extract the `## [X.Y.Z]` CHANGELOG section instead was deliberately deferred by D-11 and filed as the
todo `2026-07-29-release-notes-body-from-changelog-section.md`. This is an accepted, recorded cost
for this release, not an oversight.

### 3. Bump the submodule and push a matching `v0.6.5` tag in `typsphinx-doc-translations`

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 2 (the translations-repo tag should point at content matching the parent
tag's release).
This is the standing two-repository tagging cost carried forward from v0.6.4 (D-08, itself the v0.6.4
D-07 precedent): the Japanese documentation's `stable` path resolves against the
`typsphinx-doc-translations` repository's own tags, not this repository's — RTD's translation-project
model means `/ja/stable/` and `/en/stable/` are served from two independent repositories, each with
its own version-tag resolution. Measured at this phase's context-gathering: that repository currently
carries only the tag `v0.6.4`. Although this milestone changed nothing under `docs/` (`docs/` is
untouched — see the "Not done in this phase, by design" list below), so the translated content is
byte-identical to what `v0.6.4` already serves, omitting the second tag would make `/ja/stable/`
report a stale version number while `/en/stable/` reports `v0.6.5` — a version-string mismatch
between the two language sites even though the content itself did not diverge. No exception: bump
the submodule and tag `v0.6.5` in that repository as well.

### 4. Confirm the stable version is green at `v0.6.5` for both Read the Docs projects

**Owner:** human (owner-manual — no automated acceptance criterion is possible; RTD project version
activation has no `.readthedocs.yaml` representation).
**Ordering:** after both tag builds (items 2 and 3) have actually completed and show green — do not
perform this step preemptively.
Both projects' Default Versions were already flipped to `stable` at the v0.6.4 close (recorded in
`STATE.md`'s Blockers/Concerns section: "both RTD Default Versions → `stable`"), so **no setting flip
is expected this time** — this is a re-check that the existing `stable` alias now resolves to the new
tag's content, not a configuration change. The Read the Docs public API needs no authentication for
this check (confirmed by this project's own prior measurement: `curl` against RTD's version/build
endpoints and the flyout API all work unauthenticated against a public project).

### 5. Flip REL-03's checkbox and its Traceability row in `.planning/REQUIREMENTS.md`

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 2 (the tag/publish is what makes the requirement's "prepared... publish
half executes at `/gsd-complete-milestone`" language fully true).
`.planning/REQUIREMENTS.md` currently has REL-03 at `[ ]` with its Traceability row reading
"Pending" — measured directly in this phase (unchanged from the state `35-CONTEXT.md` recorded).
Per D-10: prep completion is not itself a publish, so the flip belongs on the close side, exactly as
v0.6.4's REL-02 was flipped only at that milestone's own `/gsd-complete-milestone` run, not during its
release-prep phase. This phase (35) does not flip it, and did not edit `.planning/REQUIREMENTS.md` in
any of its plans.

### 6. Confirm the two todo files this phase filed are present under `.planning/todos/pending/`

**Owner:** `/gsd-complete-milestone`.
**Ordering:** any time; purely administrative, no functional dependency on the items above.
Both filenames, verbatim from `35-02-SUMMARY.md`:
- `.planning/todos/pending/2026-07-29-visit-math-block-redundant-blank-line-in-list-items.md` — WR-01
  (`visit_math_block`'s pre-existing unconditional `"\n\n"` doubling with the new
  `list_item_needs_separator` flag, one redundant blank line in list-item block math; deferred by
  D-05 because fixing it now would force re-deriving the GATE-01 fixture's expected strings and
  re-running the full-corpus gate immediately before a release).
- `.planning/todos/pending/2026-07-29-release-notes-body-from-changelog-section.md` — the
  `release.yml` release-notes-body rework (D-11; see item 2 above for the measured 308/296/7/5-line
  breakdown this todo records).

Both are candidates for v0.6.6 backlog scoping, alongside the five pre-existing pending todos.

## Not done in this phase, by design

This phase (and no plan within it) performed any of the following. The scope fence is absolute —
every one of these belongs to `/gsd-complete-milestone` or to the owner, never to a prep-only
release phase:

- No `git tag v0.6.5` (or any tag) was created, locally or on the remote.
- No release workflow (`release.yml`) was triggered.
- Nothing was published to PyPI.
- No GitHub Release was created.
- No pull request was opened or merged.
- No Read the Docs setting was changed — Default Version, Default branch, or otherwise.
- No edit was made to `.github/workflows/release.yml` (the release-notes-body rework is deferred to
  v0.6.6+ per D-11, filed as a todo, item 6 above).
- No edit was made under `docs/` (this milestone's `docs/` diff is empty — confirmed by
  `git diff --name-only eb696bb..HEAD -- docs/` printing nothing).
- No change was made under `typsphinx/` beyond the two math-visitor edits in `translator.py` that
  Phase 34 already landed before this phase began (`35-RELEASE-EVIDENCE.md` § SC#4 proves the
  confinement); this phase's own three plans (35-01 through 35-04) touched only test fixtures, test
  assertions, `pyproject.toml`, `README.md`, `uv.lock`, and `CHANGELOG.md`.
- `.planning/REQUIREMENTS.md` was not edited (item 5 above stays on the close side).

## Proof the fence held

Both checks below were re-run fresh at the moment this section was written (after Task 2's own
"Proof the fence held" section in `35-RELEASE-EVIDENCE.md` — two independent observations at two
separate moments is the point):

Command:
```
$ git tag -l v0.6.5
```
Verbatim output:
```
(empty)
```

Command:
```
$ git ls-remote --tags origin v0.6.5
```
Verbatim output:
```
(empty)
```

No file was created under `.git/refs/tags/` during this phase. Both results confirm this phase
leaves zero irreversible published state — if this phase (or any earlier plan in it) were interrupted
or only partially merged, there is no tag, no PyPI release, and no GitHub Release to unwind. The
repository's git-tag state is exactly as it was before Phase 35 began.
