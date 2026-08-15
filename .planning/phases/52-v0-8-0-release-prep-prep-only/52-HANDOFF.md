# Phase 52: v0.8.0 Release Prep (prep-only) — Publish & Owner-Manual Handoff Checklist

This document is the standalone publish checklist `/gsd-complete-milestone` reads for this
milestone. It is written in English directly, as a phase deliverable that merges to a public
branch, following the `46-HANDOFF.md` / `41-HANDOFF.md` precedent. A reader with only this file and
the repository can execute the publish without opening a PLAN or SUMMARY file.

## What this phase satisfied, and what it did not

**REL-07**, quoted verbatim from `.planning/REQUIREMENTS.md`:

> - [ ] **REL-07**: v0.8.0 is released to PyPI with a curated CHANGELOG entry calling out the
>       output-shape change and the target-as-path reversal

Citing `52-RELEASE-EVIDENCE.md`'s own phase verdict table for the verdicts, not re-deriving them:

- **SC#1** — version literals move in lockstep (`pyproject.toml` the sole `0.8.0` literal, `uv.lock`
  and `README.md` moved with it, `typsphinx.__version__` reporting `0.8.0`, all three version-sync
  guard tests green). **MET** — `52-RELEASE-EVIDENCE.md` § SC#1.
- **SC#2** — the curated `## [0.8.0]` CHANGELOG entry, both user-visible-change callouts
  (output-shape change, target-as-path reversal) explicitly marked `**Breaking:**`, `:numref:`
  excluded per D-07, tail link block rolled over. **MET** — `52-RELEASE-EVIDENCE.md` § SC#2.
- **SC#3** — the post-bump tree proven green live: CI authority, local half (both docs builds plus
  the full-corpus gate), and the goal-claim half (the multi-master PDF round trip). **MET, on the
  third CI dispatch** — the first run was RED (8/12 failing, three pre-existing defects), the second
  reached 11/12 (a fourth, previously-unknown defect surfaced), and the third reached 12/12. All
  three runs are recorded in full in `52-CI-EVIDENCE.md` and cited, not restated, in
  `52-RELEASE-EVIDENCE.md` § SC#3.
- **SC#4** — the standing milestone invariants (zero new runtime dependencies; `@preview` count
  still four with no new lockstep site; no new `typst_*` config value) asserted mechanically over
  the SHA-anchored full milestone diff, with each detector fire-tested against a real violation.
  **MET** — `52-RELEASE-EVIDENCE.md` § SC#4.
- **SC#5** — no irreversible action taken, and this standalone handoff exists. **MET** (observation
  1 of 2 in `52-RELEASE-EVIDENCE.md` § SC#5; observation 2 of 2 in this document's own § "Proof the
  fence held" below).

**REL-07 remains open.** It closes at `/gsd-complete-milestone`, on the publish, not here. Its
checkbox and its Traceability row in `.planning/REQUIREMENTS.md` are still `Pending` and this phase
did not change them (confirmed: `git diff --name-only -- .planning/REQUIREMENTS.md` is empty over
this phase's entire history — re-confirmed in this plan's own Task 3, § "Closeout guard" below).
**A requirement reported complete on the strength of the code being correct is exactly how v0.7.0
lost REL-04** (lesson 12b) — this handoff states REL-07's open status explicitly, in these words,
rather than leaving it implied, so a later reader does not mistake the silence for an oversight.

**Not satisfied by this phase, and structurally out of reach here:** REL-07's entire publish half —
opening and merging the pull request, pushing the `v0.8.0` tag, `release.yml` firing to publish to
PyPI and create the GitHub Release, and the two-repository tagging cost on
`typsphinx-doc-translations` — belongs to `/gsd-complete-milestone`. Confirming Read the Docs
`stable` is green at `v0.8.0` on both projects is owner-manual and also out of reach here. This is
recorded as a handoff, not as something this phase is claiming to have effectively done.

## Checklist

Each item names its Owner and its Ordering dependency on the items before it.

### 1. Open the pull request against `main` and merge it

**Owner:** `/gsd-complete-milestone`.
**Ordering:** first — every item below depends on the milestone branch
(`gsd/v0.8.0-multi-master-composition`) reaching `main`. `origin/main` (`a97fe73`) is already an
ancestor of this phase's HEAD (confirmed live in `52-SC4-INVARIANTS.md` § "Anchor"), so this PR's
diff against `main` reflects only this milestone's own contribution, not a double-count of any
already-merged content.

### 2. Push the `v0.8.0` tag on the merge commit

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 1 (the tag should point at the merged `main`, not the pre-merge branch).
Pushing `v0.8.0` fires `.github/workflows/release.yml`. The `validate` job will fail fast if
`CHANGELOG.md` has no usable `## [0.8.0]` section — which it does, per SC#2's own measurement in
`52-RELEASE-EVIDENCE.md` (`grep -c '^## \[0\.8\.0\]' CHANGELOG.md` → `1`).

### 3. Let `release.yml` run to completion: `validate` → `build` → `publish-pypi` → `create-release`

**Owner:** `/gsd-complete-milestone`, with a human approval step on the `pypi` environment
(`publish-pypi`'s `environment: name: pypi` gate, `.github/workflows/release.yml:131-133`).
**Ordering:** after item 2.
**Watch `create-release` succeed and record the run id — this is the job that failed at the v0.7.0
close.** Run `30848860064`'s `create-release` failed at `uv: command not found` (exit 127, the
`astral-sh/setup-uv` step was missing); the workflow was fixed on `main` afterwards (the "Install
uv" / "Set up Python" steps now sit ahead of the "Generate release notes" step,
`.github/workflows/release.yml:162-168`, immediately preceded by the file's own comment naming this
exact history) and was proven end to end for the first time only at the v0.7.1 close (D-23 run 2,
`31458368833`, all twelve jobs `success` including `create-release`). Do not assume this job
succeeds by inspection alone — observe it directly.

### 4. Advance the `typsphinx-doc-translations` pin and push a matching `v0.8.0` tag there

**Owner:** `/gsd-complete-milestone` plus human.
**Ordering:** after item 1 (the translations-repo tag should point at content matching the merged
`main`; it does not need to wait for item 3's PyPI/GitHub Release publish, only for the merge).
This is the standing two-repository tagging cost adopted at v0.6.4 (D-07, `.planning/STATE.md`
§ "Accumulated Context") and carried through v0.6.5, v0.7.0, and v0.7.1. ROADMAP Phase 52 SC#5 names
this step explicitly — it stays, and this item does not drop it.

### 5. Confirm Read the Docs `stable` is green and reports `0.8.0` on BOTH projects (`en` and `ja`)

**Owner:** human, via the RTD public API or real fetches (no authentication needed — this project's
prior closes at v0.6.4, v0.6.5, v0.7.0, and v0.7.1 all confirmed RTD's public version/build/flyout
endpoints work unauthenticated against a public project).
**Ordering:** after items 3 and 4 have actually completed and show green — do not perform this step
preemptively.
Measure through RTD's unauthenticated public API and a real fetch of each project's PDF, as the last
several closes did — not by asking. Both projects' Default Versions were already flipped to `stable`
at the v0.6.4 close and reconfirmed still `stable` at every subsequent close (`STATE.md`: "No owner
setting flips were needed" at v0.6.5, v0.7.0, and v0.7.1) — no setting flip is expected this time
either. Confirm both projects report `0.8.0` and both serve their PDFs (`application/pdf`), the same
shape the v0.7.1 close established (`en` identifier `75fd8ed5`, `ja` identifier `a2150b1f`, at that
close — this close's own identifiers will differ, matching the new merge commit and translations-repo
tag).

### 6. Flip REL-07's checkbox and its Traceability row in `.planning/REQUIREMENTS.md`

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 3 actually succeeded — the tag/publish is what makes REL-07's "v0.8.0 is
released to PyPI" language fully true. **Only after item 3 actually succeeded.**
`.planning/REQUIREMENTS.md` currently has REL-07 at `- [ ]`, with its Traceability row reading
`Pending` (confirmed unedited by this entire phase — see this document's own § "Closeout guard"
below).

**Standing warning, carried from `46-HANDOFF.md` item 6 and `41-HANDOFF.md` item 6:**
`phase.complete` has a recorded, repeated habit of auto-flipping REL rows against a CONTEXT decision
— caught in Phase 41, pre-empted in Phase 42 by `42-CLOSEOUT-GUARD.md`. Diff `REQUIREMENTS.md`
before committing the close: run `git diff --name-only -- .planning/REQUIREMENTS.md` after running
`phase.complete` and before committing; if it shows a change to REL-07's line that was not intended
by this specific checklist item, revert it and re-apply the flip by hand instead.

### 7. Re-date the `## [0.8.0]` CHANGELOG heading if needed, and re-confirm the extractor

**Owner:** `/gsd-complete-milestone`.
**Ordering:** immediately before item 2's tag push (the CHANGELOG content and heading date must be
final before the tag that triggers `release.yml`'s `validate`/`create-release` reads them).
Re-date the `## [0.8.0]` CHANGELOG heading if the publish lands on a different UTC day than
2026-08-15 (the date this phase wrote, confirmed in `52-RELEASE-EVIDENCE.md` § SC#2). Confirm
`uv run python scripts/extract_changelog_section.py 0.8.0` still returns the intended body — exit
0, non-empty, the curated section verbatim — before the tag is pushed, exactly as this phase's own
`52-BUMP-EVIDENCE.md` § "Release-machinery consumer path" already ran it once (idempotent, so
re-running it at close is safe and cheap).

## Not done in this phase, by design

This phase (and no plan within it) performed any of the following. The scope fence is absolute —
every one of these belongs to `/gsd-complete-milestone` or to the owner, never to a prep-only
release phase:

- No `git tag v0.8.0` (or any tag) was created, locally or on the remote.
- No release workflow (`release.yml`) was triggered or executed as a real workflow run.
- Nothing was published to PyPI.
- No GitHub Release was created.
- No pull request was opened or merged by this phase (`gh pr list --head
  gsd/v0.8.0-multi-master-composition --json number,state` → `[]` throughout).
- No Read the Docs setting was changed — Default Version, Default branch, or otherwise.
- No `.planning/REQUIREMENTS.md` checkbox or Traceability row was flipped — `git diff --name-only --
  .planning/REQUIREMENTS.md` is empty over every commit in this phase.
- **No file under `typsphinx/` changed** — the four minor defects this milestone's own reviews
  filed (see below) ship unfixed per D-01. `git diff --name-only -- typsphinx/` is empty across this
  entire phase.
- Two `ci.yml` `workflow_dispatch` pushes were made (plans 52-04, 52-08, 52-09, culminating in the
  accepted authority run `31858016832`) and one plain fast-forward branch push each time — both
  explicitly named in-scope by D-08 (pushing a branch and dispatching a workflow are reversible;
  opening a PR and pushing a tag are not, and neither occurred).

## Deferred by decision, not oversight

**This is the section with no second surface.** D-01 and D-03 (this phase's `52-CONTEXT.md`) remove
every other surface for these findings — no `### Known Limitations` CHANGELOG section, no GitHub
issue, no ROADMAP backlog item — so this handoff and `.planning/todos/pending/` together are the
complete record. All five records named below are transcribed verbatim from
`.planning/todos/pending/` (10 files present, confirmed by directory listing) — enumerated from the
directory itself, not from a remembered list.

### The four minor defects this milestone's own reviews filed (D-01)

All four are `severity: minor`, `resolves_phase: null`, and are **new** failure classes created by
features this milestone shipped (Phase 48's compile-time xref guard, Phase 49's include graph,
Phase 50's image relocation) — the distinction the owner had on the table when deciding D-01, unlike
the v0.7.1 D-27 pair this decision otherwise mirrors.

1. **`2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`** — needs one docname
   to sanitize to the same label string another docname produces via `/` → `_u2f_`, e.g. docnames
   `a/b` and `a_u2f_b` coexisting. A reference to the absent one renders as a working link to the
   decoy instead of degrading to plain text. Ships unfixed.

2. **`2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide.md`** — needs a docname
   containing a literal `#` or `>`; `make_include_edge_key` does not escape its own separators.
   Ships unfixed.

3. **`2026-08-14-unbounded-recursion-in-derive-master-edge-keys.md`** — needs an include chain
   deeper than Python's 1000-frame limit; Sphinx's own 154-document `doc/` corpus does not reach it.
   The failure is a raw `RecursionError`, not a named `ExtensionError`. Ships unfixed.

4. **`2026-08-14-escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide.md`**
   — needs two escaping absolute image URIs in different directories sharing a basename; the escape
   branch keys on `basename` while the collision branch keys on the full `rel_uri`, so they collide
   onto one key. Ships unfixed.

**D-01 keeps all four to internal disclosure only.** No `### Known Limitations` section is added to
the CHANGELOG and no GitHub issue is filed (`gh issue list --state open --limit 20` shows only the
pre-existing, unrelated issue #91 — none filed by this phase). This is the v0.7.1 D-27 shape applied
a second time, with the one distinction the owner had on the table when deciding: all four here are
NEW failure classes created by features this milestone shipped, which was not true of the v0.7.1
pair (two pre-existing `TypstBuilder._track_image()` defects).

### The `:numref:` divergence

**`2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`** —
excluded from every published surface by `51-CONTEXT.md` D-07 (owner override, extended to this
phase's CHANGELOG on 2026-08-14). Its record's `resolves_phase` is `null`; it is classified as a bug
for a later milestone to pick up, not as a published limitation.

### A fifth deferred item, surfaced by this phase's own CI-authority chase (not enumerated in the
original plan, added here because the same reasoning applies)

**`2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md`** — CPython 3.13 narrowed
`ntpath.isabs()` so a driveless leading-separator path is no longer absolute on Windows.
`typsphinx/builder.py:910`'s `_track_image()` gates its entire rehome/relocate/warn branch on bare
`path.isabs(resolved_uri)`, so a driveless-absolute Windows image URI is silently NOT rehomed under
Python 3.13 — the identical input was correctly rehomed under Python 3.12 on the same OS. The
sibling function `_escapes_outdir()` (`typsphinx/builder.py:105-112`) already avoids exactly this
trap via `posixpath.isabs(stem) or _is_drive_qualified(stem)`; `_track_image()` is the one caller
still trusting the OS-native `path.isabs()`. Reachability is low — requires a third-party Sphinx
extension to write an absolute image URI outside `<doctreedir>` in the specific driveless-absolute
Windows shape, under Python 3.13 specifically. Plan 52-09 fixed only the **test-side** symptom
(drive-qualified the affected fixture) so the accepted CI authority run could reach all-green,
per an explicit owner decision preserving Phase 52's zero-`typsphinx/`-lines fence; the product-side
fix remains outstanding, and this todo exists so that fact survives independently of the test fix
going green.

**All five records above stay in `.planning/todos/pending/` and are NOT promoted to ROADMAP backlog
items (D-03).** They are enumerated here with reasons so a close-side sweep does not mistake any of
them for an oversight of this handoff.

### The remaining reviewed-but-not-folded todos

`todo.match-phase 52` returned all 9 candidates in the pending ledger at planning time as keyword
noise against a release-prep phase; none was folded into this phase's own scope. Four of those nine
are the defects/numref record enumerated above. The remaining four, transcribed from `52-CONTEXT.md`
§ "Reviewed Todos (not folded)":

- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — Future requirement LNK-01; `links.yml`'s
  repo-wide lychee check already covers the links this release adds.
- **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`** — forbidden by `CLAUDE.md`
  and by the milestone's own binding constraint until the todo itself lands. Doubly deliberate.
- **`2026-08-04-release-create-job-missing-uv-verify-end-to-end.md`** — REL-04's own record;
  **already closed at the v0.7.1 publish** (`create-release` completed `success` on run
  `31462027486`). **Flagged, not decided, in `52-CONTEXT.md`: this record may belong in
  `todos/completed/` rather than `pending/`.** Re-confirmed present in `todos/pending/` at this
  plan's own execution (directory listing, 10 files) — the question remains open for whoever next
  triages the ledger; this handoff does not resolve it, consistent with `52-CONTEXT.md`'s own
  "flagged for the planner, not decided here" framing, now carried one step further.
- **`2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`** — a `flake.nix`-side toolchain
  repair (Future requirement QUA-06). Does not block SC#3, which takes lint from CI (D-08) — the
  accepted third CI run's `Lint and Format Check` job reports `success`.

## Proof the fence held

Two independent observations, at two separate moments, is `35-HANDOFF.md`'s, `41-HANDOFF.md`'s, and
`46-HANDOFF.md`'s own standing convention — the fence's proof is an absence, and an absence is proven
more robustly by two probes taken apart in time than by one.

**Observation 1 of 2** is recorded in `52-RELEASE-EVIDENCE.md` § "SC#5: no irreversible action
taken — the fence, observation 1 of 2", timestamped **2026-08-15T02:20:22Z**: `git tag -l v0.8.0`,
`git ls-remote --tags origin v0.8.0`, `gh pr list --head gsd/v0.8.0-multi-master-composition`, and
`gh run list --workflow=release.yml` all returned the expected empty/pre-existing-only results.

**Observation 2 of 2**, taken independently in this document, at a separate moment:

**Timestamp:** 2026-08-15T02:24:28Z (elapsed gap from observation 1: **4 minutes 6 seconds**).

Command:
```
$ git tag -l v0.8.0
```
Verbatim output:
```
(empty)
```
Exit code: 0.

Command:
```
$ git ls-remote --tags origin v0.8.0
```
Verbatim output:
```
(empty)
```
Exit code: 0.

Both probes are EMPTY on both observations, taken 4 minutes 6 seconds apart. No file was created
under `.git/refs/tags/` between the two observations, and no push occurred against `origin` between
them. This confirms this phase leaves zero irreversible published state — if this phase (or any
earlier plan within it) had been interrupted or only partially merged at any point between these two
observations, there would still be no tag, no PyPI release, and no GitHub Release to unwind. The
repository's git-tag state for `v0.8.0` is exactly as it was before this phase's Task 1 ran, and
remains exactly that at this document's own close.

## Closeout guard — REL-07 must stay Pending

Recorded BEFORE anything else in this plan's Task 3 ran, so a later diff has something to compare
against.

**REL-07's two lines in `.planning/REQUIREMENTS.md`, verbatim, with their line numbers:**

```
103:- [ ] **REL-07**: v0.8.0 is released to PyPI with a curated CHANGELOG entry calling out the
```
```
268:| REL-07 | Phase 52 | Pending |
```

**Checksum of the whole file:**

```
$ sha256sum .planning/REQUIREMENTS.md
566859ead9c24a37281f81c96fcec0d6702424637add5f7b2346d156dab4682e  .planning/REQUIREMENTS.md
```

**REL-07's checkbox must read `- [ ]` and its Traceability row must read `Pending` at phase close.**
`.planning/REQUIREMENTS.md` is expected to appear in NO diff produced by this phase.

### The phase's own closing fence checks, run and recorded (never asserted from memory)

Command:
```
$ git diff --name-only -- .planning/REQUIREMENTS.md
```
Verbatim output:
```
(empty)
```

Command:
```
$ grep -n 'REL-07' .planning/REQUIREMENTS.md
```
Verbatim output:
```
103:- [ ] **REL-07**: v0.8.0 is released to PyPI with a curated CHANGELOG entry calling out the
268:| REL-07 | Phase 52 | Pending |
279:(REL-07).
```
Checkbox still `- [ ]`, Traceability row still `Pending` — unchanged.

Command:
```
$ git diff --name-only -- typsphinx/
```
Verbatim output:
```
(empty)
```

Command:
```
$ ls .planning/phases/52-v0-8-0-release-prep-prep-only/
```
No `52-VERIFICATION.md` present in the listing (30 files: PLAN/SUMMARY pairs for plans 01-09,
`52-BUMP-EVIDENCE.md`, `52-CI-EVIDENCE.md`, `52-CONTEXT.md`, `52-DISCUSSION-LOG.md`,
`52-GOAL-CLAIM-EVIDENCE.md`, `52-GREEN-TREE-EVIDENCE.md`, `52-HANDOFF.md`, `52-PATTERNS.md`,
`52-RELEASE-EVIDENCE.md`, `52-RESEARCH.md`, `52-SC4-INVARIANTS.md`, `52-VALIDATION.md`,
`COVERAGE.md`).

Command:
```
$ git status --porcelain
```
Verbatim output (immediately before this task's own commit):
```
(empty)
```
The working tree is at rest — no uncommitted change of any kind — before this task's own
`52-HANDOFF.md` edit is staged.

### Instruction for whoever runs the phase close

**Diff `.planning/REQUIREMENTS.md` after any closeout automation runs and before committing the
close.** If REL-07's checkbox or Traceability row changed, revert that change by hand and re-apply
the correct still-`Pending` state, then record the revert. `phase.complete` has a recorded, repeated
habit of auto-flipping REL rows against a CONTEXT decision — caught in Phase 41, pre-empted in
Phase 42 by `42-CLOSEOUT-GUARD.md`, and documented again at the v0.7.1 close (`46-HANDOFF.md` item
6, same procedure). This has happened before on this exact class of phase and must not be assumed
not to recur.
