# Phase 41: v0.7.0 Release Automation + Release Prep — Publish & Owner-Manual Handoff Checklist

This document is the explicit hand-off for the half of REL-05 this phase structurally cannot
satisfy. It is written in English directly, as a phase deliverable that merges to a public branch,
following the `35-HANDOFF.md` precedent.

## What this phase satisfied, and what it did not

**REL-04**, quoted verbatim from `.planning/REQUIREMENTS.md`:

> - [ ] **REL-04** [M]: The GitHub Release body is the **curated `## [X.Y.Z]` CHANGELOG section**,
>       not the `git log --pretty` commit dump `release.yml` generates today (the v0.6.4 body was
>       308 lines, of which 296 were that dump). `release.yml` does not read `CHANGELOG.md` at all
>       today.

**REL-05**, quoted verbatim:

> - [ ] **REL-05** [M]: v0.7.0 is released — version bumped as the sole literal in `pyproject.toml`
>       with `uv.lock` and `README.md` in lockstep, a curated CHANGELOG entry written, and the
>       publish executed at `/gsd-complete-milestone` (tag → `release.yml` → PyPI + GitHub Release,
>       plus the standing second tag on `typsphinx-doc-translations`).

**Satisfied by this phase's plans**, mapped to each of ROADMAP Phase 41's five success criteria via
`41-RELEASE-EVIDENCE.md`'s own phase verdict table (not re-derived here):

- **SC#1** — `release.yml` builds the release body from `CHANGELOG.md`'s curated `## [X.Y.Z]`
  section, with the `git log --pretty` commit dump removed rather than fenced. **PROVEN** — plan
  41-01, evidenced in `41-REL04-EVIDENCE.md`, cited in `41-RELEASE-EVIDENCE.md` § SC#1.
- **SC#2** — the version reads `0.7.0` as the sole literal in `pyproject.toml`, with `uv.lock` and
  `README.md` in lockstep and `typsphinx.__version__` reporting it, plus a curated `## [0.7.0]`
  CHANGELOG entry with the tail link block rolled over. **PROVEN** — plan 41-02, measured directly
  in `41-RELEASE-EVIDENCE.md` § SC#2 (no sibling evidence file owns this criterion).
- **SC#3** — the post-bump tree is green across the full suite, the lint/type trio, the full-corpus
  `-b typstpdf` gate, and both docs dogfooding builds, including a re-run of the `ja` build's
  four-check glyph bar. **PROVEN** — plans 41-04 (the `ja` glyph bar) and 41-05 (the mechanical
  half), evidenced in `41-GREEN-TREE-EVIDENCE.md` + `41-JA-GLYPH-BAR.md` +
  `41-JA-GLYPHBAR-SIGNOFF.md`, cited in `41-RELEASE-EVIDENCE.md` § SC#3.
- **SC#4** — the milestone invariants are proven mechanically over the SHA-anchored full milestone
  diff: zero new runtime dependencies, the `@preview` package count still four with no new
  version-lockstep site, and every node-handler change carrying its recorded-RED GATE-01 fixture.
  **PROVEN** (with two stated, non-breaching qualifications — see `41-RELEASE-EVIDENCE.md` § SC#4) —
  plan 41-06, evidenced in `41-SC4-INVARIANTS.md`.
- **SC#5** — no irreversible action has been taken at phase close, and a standalone handoff
  checklist records exactly what `/gsd-complete-milestone` will execute. **PROVEN** (observation 1
  of 2 in `41-RELEASE-EVIDENCE.md` § SC#5; observation 2 of 2 in this document's own § "Proof the
  fence held" below) — this plan (41-07), and this document is the checklist SC#5 itself requires.

Adjacent to REL-04/REL-05's own scope but completed in this phase: the one `typsphinx/` change this
phase takes (D-12's `visit_desc_sig_name` docstring escape, plan 41-03) and D-13's planning-record
hygiene (two already-fixed todos re-verified and filed to `todos/completed/`, PROJECT.md's two
unterminated HTML comments terminated).

**Not satisfied by this phase, and structurally out of reach here:** REL-05's entire publish half —
pushing the `v0.7.0` tag, `release.yml` firing to publish to PyPI and create the GitHub Release,
opening and merging the pull request, and the two-repository tagging cost on
`typsphinx-doc-translations` — belongs to `/gsd-complete-milestone`. Confirming Read the Docs
`stable` is green at `v0.7.0` on both projects is owner-manual and also out of reach here. This is
recorded as a handoff, not as something this phase is claiming to have effectively done.

## Checklist

Each item names its Owner and its Ordering dependency on the items before it.

### 1. Open the pull request and merge it to `main`

**Owner:** `/gsd-complete-milestone`.
**Ordering:** first — every item below depends on the milestone branch reaching `main`.
This phase's own branch (and the six phases before it in this milestone, 36 through 40.1) carries
the full v0.7.0 milestone diff. Opening it for review and merging is the action that makes `main`
the tree everything below operates on. Note the CI expectation: `release.yml`'s `validate` job now
also runs the new "Verify CHANGELOG has a section for this version" step plan 41-01 added
(`41-REL04-EVIDENCE.md` § D-09) — so a tag push after this merge is the first moment that check
exercises in anger, since it has never run against a real tag push before now.

### 2. Push the `v0.7.0` tag on the merge commit

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 1 (the tag should point at the merged `main`, not the pre-merge branch).
Pushing `v0.7.0` fires `.github/workflows/release.yml`. Note that the `validate` job will fail fast
if `CHANGELOG.md` has no usable `## [0.7.0]` section — which it does, per SC#2's own measurement in
`41-RELEASE-EVIDENCE.md` (the heading is present at line 10, non-empty, and the extractor's real
hand-run against it in `41-REL04-EVIDENCE.md` exits 0 with the curated section on stdout).

### 3. Let `release.yml` run to completion: `validate` → `build` → `publish-pypi` → `create-release`

**Owner:** `/gsd-complete-milestone`, with a human approval step on the `pypi` environment (the same
gate the v0.6.5 release exercised, per `STATE.md`'s own record of that run).
**Ordering:** after item 2.
Record the expectation, discharged for the first time by this release: the GitHub Release body is
now the curated `## [0.7.0]` CHANGELOG section (via `scripts/extract_changelog_section.py`) plus the
Installation block plus GitHub's own auto-generated portion (`generate_release_notes: true` stays
enabled per D-08, appended rather than replacing the curated body). This is REL-04's first
real-world exercise and the first release in this project's history where the body is not a
`git log` commit dump — the v0.6.4 body was 308 lines, 296 of them the dump; this release's body is
the curated section instead.

### 4. Advance the `typsphinx-doc-translations` submodule pin and push a matching `v0.7.0` tag there

**Owner:** `/gsd-complete-milestone` plus human.
**Ordering:** after item 1 (the translations-repo tag should point at content matching the merged
`main`; it does not need to wait for item 3's PyPI/GitHub Release publish, only for the merge).
This is the standing two-repository tagging cost adopted at v0.6.4 and carried through v0.6.5
(`STATE.md` § "Shipped Milestone (v0.6.5 — archived)": pin advanced, tagged `v0.6.5` at `1891a09`) —
`/ja/stable/` resolves against that repository's own tags, not this repository's. Measured this
phase (`41-JA-GLYPH-BAR.md` § "Provenance"): the clone's submodule pin (`5888ee0...`) was
byte-identical to that repository's live `main` tip at the moment of measurement, and `docs/`
carries zero line changes this entire milestone (`git diff --stat 51e02b6..HEAD -- docs/` empty,
confirmed independently in both `41-SC4-INVARIANTS.md` and `41-JA-GLYPH-BAR.md`) — so the
translated content this tag points at is unchanged from what `v0.6.5` already serves there. Omitting
this second tag would still make `/ja/stable/` report a stale version number while `/en/stable/`
reports `v0.7.0`, exactly the mismatch v0.6.5's own handoff (`35-HANDOFF.md` item 3) named. No
exception: bump the submodule and tag `v0.7.0` in that repository as well.

### 5. Confirm Read the Docs `stable` is green at `v0.7.0` on BOTH projects (en and ja)

**Owner:** human, via the RTD public API or real fetches (no authentication needed for this check —
`35-HANDOFF.md` item 4 and this project's own prior measurement both confirm RTD's public
version/build/flyout endpoints work unauthenticated against a public project).
**Ordering:** after items 3 and 4 have actually completed and show green — do not perform this step
preemptively.
Both projects' Default Versions were already flipped to `stable` at the v0.6.4 close and reconfirmed
still `stable` at the v0.6.5 close (`STATE.md`: "No owner setting flips were needed this time") — no
setting flip is expected this time either. Confirm both projects report `0.7.0` and both serve their
PDFs, the same shape `35-HANDOFF.md` item 4 and its v0.6.5-close fulfillment (`STATE.md`: "en
identifier `839d77f38ffa`, ja identifier `1891a0905322`... both reporting `0.6.5`, both PDFs served")
already established as the pattern.

### 6. Flip REL-04's and REL-05's checkboxes and their Traceability rows in `.planning/REQUIREMENTS.md`

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 3 (the tag/publish is what makes REL-05's "the publish executed at
`/gsd-complete-milestone`" language fully true; REL-04's body swap is exercised for the first time
by that same tag push).
`.planning/REQUIREMENTS.md` currently has REL-04 and REL-05 both at `[ ]`, with Traceability rows
reading "Pending" (measured directly by this phase: § "Release and CI (REL)" lines 190/194, and the
Traceability table lines 316-317 — unchanged from the state `41-CONTEXT.md` recorded). Per this
phase's own scope decision: release-prep completion is not itself a publish, so the flip belongs on
the close side, exactly as v0.6.5's REL-03 was flipped only at that milestone's own
`/gsd-complete-milestone` run.

**Known hazard, stated explicitly:** `phase.complete` has been observed auto-flipping a deferred
requirement's checkbox against a CONTEXT decision on a prior occasion in this project's history.
Check `git diff --name-only -- .planning/REQUIREMENTS.md` after running `phase.complete` and before
committing; if it shows a change to REL-04's or REL-05's line that was not intended by this specific
checklist item (or any change made outside of this deliberate, ordered step), revert it and re-apply
the flip by hand instead.

### 7. File the two todos this phase's own code work resolved

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 3 (both are release-record housekeeping, not blocking, but are grouped here
with the REQUIREMENTS.md flip since both are close-side record work this phase deliberately left
for the close).
Move both from `.planning/todos/pending/` to `.planning/todos/completed/`, confirmed present at
`.planning/todos/pending/` by directory listing during this phase's own execution:

- ~~`2026-07-29-release-notes-body-from-changelog-section.md`~~ — this **is** REL-04; delivered end
  to end by plan 41-01 (`41-REL04-EVIDENCE.md`). **ALREADY DONE — no action needed at close.**
  See the amendment below.
- `2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md` — D-12; delivered by
  plan 41-03 (confirmed fixed and reaching the published API reference with zero warning
  occurrences in `41-GREEN-TREE-EVIDENCE.md` § "Step 7b"). **Still to do at close.**

**Amendment (2026-08-03, at phase close).** The first of the two was moved during the phase's own
close-out, not at `/gsd-complete-milestone`. Cause: it carries `resolves_phase: 41` in its
frontmatter, and `execute-phase`'s automatic `close_phase_todos` step moves every pending todo
tagged with the completing phase — so the deferral this item describes was not actually available for
that file. The move is factually correct (REL-04's workflow change landed in plan 41-01), so it was
allowed to stand rather than being reverted to preserve the ordering. The second file has
`resolves_phase: null` and was therefore untouched, so it remains genuine close-side work exactly as
written above.

Note the asymmetry with D-13's two already-fixed todos (`2026-08-01-desc-break-marker-stale-...md`
and `2026-08-01-expected-page-count-...md`), which this phase already moved to
`todos/completed/` directly during plan 41-03's own execution — those were record-only (the code fix
predated Phase 41 and was merely re-verified), whereas these two are todos this phase's own code work
resolved for the first time, so their filing is deliberately left for the close side alongside the
REQUIREMENTS.md flip they describe.

## Not done in this phase, by design

This phase (and no plan within it) performed any of the following. The scope fence is absolute —
every one of these belongs to `/gsd-complete-milestone` or to the owner, never to a prep-only
release phase:

- No `git tag v0.7.0` (or any tag) was created, locally or on the remote.
- No release workflow (`release.yml`) was triggered or executed as a real workflow run — every claim
  about its behavior in this phase's evidence is either a direct hand-run of the script it calls, or
  a static read of its YAML structure (`41-REL04-EVIDENCE.md`'s own "Explicit non-execution
  statement").
- Nothing was published to PyPI.
- No GitHub Release was created.
- No pull request was opened or merged.
- No Read the Docs setting was changed — Default Version, Default branch, or otherwise.
- No `.planning/REQUIREMENTS.md` checkbox or Traceability row was flipped — `git diff --name-only --
  .planning/REQUIREMENTS.md` is empty over every commit in this plan.
- No change was made under `docs/` — measured: zero lines changed this entire milestone
  (`git diff --stat 51e02b6..HEAD -- docs/` empty, confirmed independently in both
  `41-SC4-INVARIANTS.md` and `41-JA-GLYPH-BAR.md`); touching it would drag in gettext-catalog
  follow-up in the `typsphinx-doc-translations` repository (Phase 28 D-04 / Phase 33 / Phase 35
  rule).
- No `typsphinx/` change beyond D-12's docstring escape (`visit_desc_sig_name`'s unbalanced-asterisk
  fix, a comment/docstring-only edit with no emitted-`.typ` shape change — classified explicitly in
  `41-SC4-INVARIANTS.md` § "This phase's own translator change (D-12 classification)").
- No revisiting of the version number itself — `0.7.0` is fixed by ROADMAP SC#2 and was not
  reconsidered anywhere in this phase.

## Deferred by decision, not oversight (D-14)

Four pending todos are deferred to v0.7.1+ by explicit owner decision (`41-CONTEXT.md` D-14), not
because they were overlooked. Each is named here so a close-side sweep does not mistake any of them
for an oversight of this handoff:

1. **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — a `sphinx-build -b linkcheck` CI job. Weighed
   and declined for this release specifically: `.github/workflows/links.yml`'s existing advisory
   repository-wide lychee check already covers the one new link this release adds
   (`CHANGELOG.md`'s tail `[0.7.0]:` link-reference line, added by plan 41-02).
2. **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`** — the non-`str` docname
   `TypeError` in `TypstPDFBuilder.finish()`. A builder-side behaviour change unrelated to
   REL-04/REL-05; deferred rather than bundled into a release-prep phase's scope.
3. **`2026-07-25-derive-typst-lang-duplicated-warning-block.md`** — `derive_typst_lang()`'s
   duplicated warning block. A refactor with no release bearing; deferred.
4. **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`** — the typing-imports
   modernization (dropping the `UP006`/`UP035` ruff ignores). Deferred to v0.7.1+ per D-14, and
   **independently held back by this project's own `CLAUDE.md`**, which explicitly instructs: "Don't
   'modernize' typing imports until that todo lands" — so this deferral is doubly deliberate, not a
   single owner call.

None of the four relates to REL-04 or REL-05, and none blocks this release.

## Proof the fence held

Two independent observations, at two separate moments, is `35-HANDOFF.md`'s own convention (and this
phase's own T-41-30 mitigation) — the fence's proof is an absence, and an absence is proven more
robustly by two probes taken apart in time than by one.

**Observation 1 of 2** is recorded in `41-RELEASE-EVIDENCE.md` § "SC#5: no irreversible action taken
— the fence, observation 1 of 2", timestamped **2026-08-03T12:12:29Z**: both `git tag -l v0.7.0` and
`git ls-remote --tags origin v0.7.0` returned empty, exit 0 on both.

**Observation 2 of 2**, taken independently in this document, at a separate moment:

**Timestamp:** 2026-08-03T12:15:13Z (elapsed gap from observation 1: **2 minutes 44 seconds**).

Command:
```
$ git tag -l v0.7.0
```
Verbatim output:
```
(empty)
```
Exit code: 0.

Command:
```
$ git ls-remote --tags origin v0.7.0
```
Verbatim output:
```
(empty)
```
Exit code: 0.

Both probes are EMPTY on both observations, taken 2 minutes 44 seconds apart. No file was created
under `.git/refs/tags/` between the two observations, and no push occurred against `origin` between
them. This confirms this phase leaves zero irreversible published state — if this phase (or any
earlier plan within it) were interrupted or only partially merged at any point between these two
observations, there would still be no tag, no PyPI release, and no GitHub Release to unwind. The
repository's git-tag state for `v0.7.0` is exactly as it was before this phase's Task 1 ran, and
remains exactly that at this document's own close.
