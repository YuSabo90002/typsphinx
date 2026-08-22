# Phase 57: v0.9.0 Release Prep (prep-only) — Publish & Owner-Manual Handoff Checklist

This document is the standalone publish checklist `/gsd-complete-milestone` reads for this
milestone. It is written in English directly, as a phase deliverable that merges to a public
branch, following the `52-HANDOFF.md` / `46-HANDOFF.md` precedent. A reader with only this file and
the repository can execute the publish without opening a PLAN or SUMMARY file.

## What this phase satisfied, and what it did not

**REL-08**, quoted verbatim from `.planning/REQUIREMENTS.md`:

> - [ ] **REL-08**: v0.9.0 is published — PyPI wheel + sdist, GitHub Release carrying the curated
>       `## [0.9.0]` CHANGELOG section, the second-repository tag on `typsphinx-doc-translations`,
>       and Read the Docs `stable` serving 0.9.0 on both projects
>
>       *Added at roadmap creation 2026-08-15, mirroring v0.8.0's REL-07. It is the requirement of
>       the prep-only final phase (57), which takes zero irreversible action — REL-08 closes at
>       `/gsd-complete-milestone`, on the publish, not on the prep. It stays `[ ]` through every
>       plan of Phase 57; the `phase.complete` auto-flip has fired against this requirement shape
>       at four consecutive release-prep closes and must be caught and reverted there.*

Citing each success-criterion's own evidence artifact and section, not restating it:

- **SC#1** (version moves atomically to 0.9.0) — **MET**. `57-BUMP-EVIDENCE.md` § "SC#1 —
  version-literal lockstep" and § "Guard tests".
- **SC#2** (the CHANGELOG entry is curated, not generated) — **MET**. `57-CHANGELOG-EVIDENCE.md`
  § "SC#2 — the release body, in both directions", § "Breaking-mark census (D-01)", and § "Tail
  link block".
- **SC#3** (the bumped tree is proven green on live runs) — **MET, across three surfaces**.
  CI authority: `57-CI-EVIDENCE-RUN3.md` § "Job conclusions — all 12" (the fresh authority
  dispatch, run `32557477023`, 12/12 success including both `windows-latest` lanes — the successor
  record that discharges `57-05`'s halted toolchain half). Local half: `57-GREEN-TREE-EVIDENCE.md`
  § "SC#3 — full pytest suite" through § "SC#3 — built-wheel content check (local copy)".
  Multi-template goal claim: `57-GOAL-CLAIM-EVIDENCE.md` § "Post-bump re-proof".
- **SC#4** (the fence is proven held) — **MET**. `57-SC4-INVARIANTS.md` § "SC#4 fence — this
  phase's own diff" and § "SC#4 fence — observation 2 of 3" for the milestone-diff sweep and the
  second fence probe; this document's own § "Closeout guard" below takes the third and final probe.
- **SC#5** (the handoff checklist is standalone and complete) — **MET** by this document itself,
  citing `57-RESEARCH.md` § "Pattern 7" for the second-repository dispatch mechanics and
  `.github/workflows/release.yml` for the job sequence the § "Checklist" below walks.

**REL-08 remains open.** It closes at `/gsd-complete-milestone`, on the publish, not here — with
the confirmation that `git diff --name-only -- .planning/REQUIREMENTS.md` is empty over this
phase's entire history and that `sha256sum .planning/REQUIREMENTS.md` still matches
`57-CLOSEOUT-GUARD.md`'s baseline. Run live in this plan's own worktree, moments before this
sentence was written:

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(empty)

$ sha256sum .planning/REQUIREMENTS.md
503efc7acb10642cee5f7d171bd66e15f4420b8610f7d0a22483424c17567d94  .planning/REQUIREMENTS.md
```

This matches `57-CLOSEOUT-GUARD.md`'s baseline digest
(`503efc7acb10642cee5f7d171bd66e15f4420b8610f7d0a22483424c17567d94`) byte-for-byte. The full
re-verification, including the phase-range commit-log check and the byte-identity of REL-08's own
guarded lines, is repeated and expanded in § "Closeout guard" below.

**Not satisfied by this phase, and structurally out of reach here:** REL-08's entire publish half —
opening and merging the pull request, pushing the `v0.9.0` tag, `release.yml` firing to publish to
PyPI and create the GitHub Release, and the two-repository tagging cost on
`typsphinx-doc-translations` — belongs to `/gsd-complete-milestone`. Confirming Read the Docs
`stable` is green at `v0.9.0` on both projects is owner-manual and also out of reach here. This is
recorded as a handoff, not as something this phase is claiming to have effectively done.

## Checklist

Each item names its Owner and its Ordering dependency on the items before it.

### 1. Open the pull request against the default branch and merge it

**Owner:** `/gsd-complete-milestone`.
**Ordering:** first — everything below depends on the merge commit existing. The branch
(`gsd/v0.9.0-per-document-templates`) is already pushed to `origin` (required by the `ci.yml`
`workflow_dispatch` runs D-12 needed), but no pull request has been opened against it
(`gh pr list --head gsd/v0.9.0-per-document-templates --json number,state` → `[]`, confirmed live
this session — see § "Closeout guard" for the full third fence probe).

### 2. Push the release tag on the merge commit

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after item 1.
This is the action that fires `.github/workflows/release.yml`. Nothing before this point in the
milestone was irreversible — pushing a branch and dispatching `ci.yml` twice (D-12) are both
reversible actions this phase and its predecessors already took; the tag push is the first
irreversible one. The `validate` job will fail fast if `CHANGELOG.md` has no usable `## [0.9.0]`
section — which it does, per SC#2's own measurement in `57-CHANGELOG-EVIDENCE.md`.

### 3. Watch the release workflow to completion, job by job

**Owner:** `/gsd-complete-milestone`, with an owner-manual approval step.
**Ordering:** after item 2.
`.github/workflows/release.yml`'s job sequence: `validate` → `build` → `publish-pypi` (gated behind
the `pypi` environment's required approval — the human-in-the-loop step) → `create-release`. The
`validate` job runs `scripts/extract_changelog_section.py` against the new version and will abort
the whole release before any upload if the section is missing or empty (this is a real
precondition check, not a formality — it is the same script the checklist's item 4 re-runs against
the published body).

**Watch `create-release` closely — it is the job that failed at the v0.7.0 close** (run
`30848860064`, `uv: command not found`, exit 127, `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md`).
It has since completed successfully at both the v0.7.1 and v0.8.0 closes (runs `31462027486` and
`31861043480`, both `success`), but do not assume success by inspection alone — observe the job
directly.

### 4. Verify the package index and the GitHub Release

**Owner:** owner-manual.
**Ordering:** after item 3.
The byte-identity check SC#5 requires: the published Release body's leading lines must be
byte-identical to `uv run python scripts/extract_changelog_section.py 0.9.0`'s stdout. Exact
comparison command shape:

```bash
uv run python scripts/extract_changelog_section.py 0.9.0 > /tmp/expected-notes.md
gh release view v0.9.0 --json body -q .body > /tmp/actual-notes.md
diff /tmp/expected-notes.md <(head -n "$(wc -l < /tmp/expected-notes.md)" /tmp/actual-notes.md)
```

A **non-empty `diff` output is a failure, not a formatting difference** — `release.yml`'s
`create-release` job appends an `## Installation` block plus GitHub's own `generate_release_notes:
true` auto-notes after the extractor's output, so the comparison above intentionally truncates the
actual body to the extractor's own line count before diffing; a mismatch inside that truncated
window means the curated section itself diverged, which SC#5 treats as a hard failure.

The Release should carry **three assets**: the wheel (`typsphinx-0.9.0-py3-none-any.whl`), the
sdist (`typsphinx-0.9.0.tar.gz`), both from `release.yml`'s `build` job's `dist/*` upload, and
`typsphinx.pdf`, attached separately by `docs.yml`'s own "Upload PDF to Release" step
(`if: startsWith(github.ref, 'refs/tags/v')`), which fires from the same tag push.

### 5. Advance the second repository's pin, then tag it

**Owner:** `/gsd-complete-milestone` for the dispatch, owner-manual for the tag timing.
**Ordering:** after item 3.
The pin is advanced by dispatching that repository's **own** `update-pin.yml` workflow — confirmed
working live this milestone (`57-RESEARCH.md` § "Pattern 7": `gh run list --repo
YuSabo90002/typsphinx-doc-translations --workflow=update-pin.yml --limit 5` shows both scheduled
and `workflow_dispatch`-triggered runs completing `success` regularly) — and **not** by a manual
clone, edit and push, so the same reviewed catalog-regeneration and no-content-free-commit logic
applies every time. Command shape:

```bash
gh workflow run update-pin.yml --repo YuSabo90002/typsphinx-doc-translations
gh run list --repo YuSabo90002/typsphinx-doc-translations --workflow=update-pin.yml --limit 1
gh run watch --repo YuSabo90002/typsphinx-doc-translations <run-id>
```

The workflow does **not** itself create a tag on that repository — advancing the pin and tagging
are two separate steps. Once the pin commit lands (the workflow's own commit, pushed to that
repository's tracked branch), push a `v0.9.0` tag there pointing at that commit.

### 6. Measure Read the Docs `stable` on both projects

**Owner:** owner-manual — **this is outside `/gsd-complete-milestone`'s own reach.**
**Ordering:** after items 3 and 4 have actually completed and show green — do not perform this
step preemptively.
Measure through RTD's unauthenticated public API and a real fetch of each project's PDF, as every
prior close has (`en` project `typsphinx`, `ja` project `typsphinx-ja`). What to measure: that the
root URL resolves to the stable path (`https://typsphinx.readthedocs.io/` → `/en/stable/`); the
`stable` version identifier on each project (expected to match the v0.9.0 merge commit for `en` and
the translations repo's own `v0.9.0`-tagged commit for `ja`); that both report the new version
(`0.9.0`); and that both PDFs are served (`application/pdf`). Both projects' Default Versions have
been `stable` since the v0.6.4 close and have needed no re-flip at every subsequent close — none is
expected here either, but this step confirms rather than assumes it.

## Deferrals carried forward

### WR-02 (`54.1-REVIEW.md`)

The pre-write validation (`typsphinx/builder.py:1107-1114`, `_validate_used_template_paths()`)
resolves Sphinx's `templates_path` against `self.srcdir` rather than `self.confdir` — the
directory Sphinx's own documentation names for that config value. A project using `-c`/`--confdir`
still walks into the republication hole `_copy_used_template_bundles()` has no `templates_path`
awareness of its own either. **D-09 shipped this SILENT: no CHANGELOG carve-out, no `###
Known Limitations` section, no GitHub issue.** The reviewer's own recommended minimum remediation
was exactly the CHANGELOG carve-out sentence that was declined — `54.1-REVIEW.md` § WR-02's "Fix:"
paragraph literally suggested "mention the `-c`/confdir carve-out in the CHANGELOG's new
breaking-change entry", and D-09's counter-case put that recommendation on the table explicitly
before declining it. The shipped `## [0.9.0]` CHANGELOG sentence ("template layout is now validated
before anything is written") therefore reads as **unconditional**, which is a stronger consequence
than merely omitting a caveat — an over-broad true-sounding claim, not a true claim with a missing
footnote. This is the **third consecutive release** to decline a limitations section (v0.7.1's
D-27, v0.8.0's D-01, and now v0.9.0's D-09 all took the same silent-internal-disclosure shape).

### WR-01 (`54.1-REVIEW.md`)

The "Custom template not found" warning fires **three** times instead of two for one narrow
configuration shape (a synthesized `"typst"` key whose `typst_template` names a nonexistent path).
It needs a `typsphinx/builder.py` behaviour change and stays behind the prep-only fence (D-10). Not
fixed this phase, by design.

### The pending todo ledger — ten records, one disposition line each

Censused by `ls -1 .planning/todos/pending/ | sort` in this plan's own Task 1 (directory listing,
not a content grep). **Ten records are present**, one more than the nine `57-CONTEXT.md`
anticipated at discussion time (2026-08-16) — plan `57-11`, landed mid-execution, filed a new record
after this phase's own CONTEXT was written; its presence is itself an instance of this project's
"discovery is run-time, file lists are floors" rule, not a defect in the census.

| Record | Disposition |
|---|---|
| `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` | **Annotated and kept open** (this plan's Task 1). Live re-measurement today (2026-08-22) shows the stub-loader rejection **reproduces again**, directly contradicting the 2026-08-16 in-milestone measurement that found `ruff` working — an environment-dependent recurrence that is exactly why the owner decided to keep this open rather than close it. `## Acceptance` section byte-unchanged. |
| `2026-08-17-repr-escaped-paths-in-remaining-user-facing-messages.md` | Filed by plan `57-11` (not this plan) for the `!r`-path-escaping defect SHAPE at sites `57-11` deliberately left unchanged (the v0.8.0-era output-path collision family, bundle-copy I/O failure messages, docname/image warning and debug logs, and `template_registry.py`'s declared-template validation failures) — widening `57-11`'s one owner-approved fix into a codebase-wide rewrite during release prep was explicitly declined as a larger, differently-shaped risk. Stays in `pending/`; no `typsphinx/` change made by this plan. |
| `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` (REL-04's own record) | **Settling measurement attached (this plan's Task 1, Step 3); disposition left to the owner.** `STATE.md`'s v0.7.1 close record states `create-release` completed `success` on run `31462027486` and the published body was measured byte-identical (lines 1-77) to `scripts/extract_changelog_section.py 0.7.1`'s output — i.e. REL-04's own `## Acceptance` criteria were fully met at the v0.7.1 publish. This flag was raised, unactioned, at the v0.8.0 close (`52-CONTEXT.md`, then `52-HANDOFF.md` § "The remaining reviewed-but-not-folded todos") and is raised again here with the measurement that would settle it, rather than repeated as an open question a third time. This plan does not move it — moving ledger records except the one annotated above is out of this plan's scope, and this phase does not decide a prior milestone's closure on its own authority. |
| `2026-07-22-add-sphinx-linkcheck-ci-job.md` | Future requirement LNK-01; `links.yml`'s repo-wide lychee check already covers the links this release adds. |
| `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` | Forbidden by `CLAUDE.md` and by the milestone's own binding constraint until the todo itself lands. |
| `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` | `:numref:` excluded from every published surface by owner override (`51-CONTEXT.md` D-07), carried forward unchanged to this CHANGELOG. |
| `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` | CI/tooling, `severity: major`; its measured `--locked` census is what made this phase's D-13 sequencing constraint concrete. Fixing dependabot's own workflow is not this phase's work. |
| `2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md` | A `builder.py` path predicate; a code defect, prep-only fence applies. |
| `2026-08-16-track-image-escape-branch-basename-not-normalized.md` | Same class as the above. |
| `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md` | An HTML sidebar defect in this project's own docs `index.rst`. Real, but neither a release surface nor part of REL-08. |

**56-REVIEW's filing, confirmed present in `completed/` by a filename match** (`ls -1
.planning/todos/completed/ | grep stale-version-prerequisites-and-dead-config-link-in-published-docs`
→ 1 hit) — the check named is the one this plan actually ran, not a content grep. The 2026-08-16
discuss-session's original "this record exists nowhere on disk" claim was a method artifact: a
content grep cannot see a slug that appears only in the filename and never in the body
(`57-CONTEXT.md` `<specifics>` item 9's RETRACTED block). Every existence claim in this section and
in this plan's Task 1 was settled by a directory listing, never by grepping content.

## Closeout guard

### The third fence observation

Recorded live, at a moment demonstrably separated from the earlier two observations:

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-22T07:04:01Z

$ git tag -l v0.9.0
(no output)

$ git ls-remote --tags origin v0.9.0
(no output)

$ gh release list --limit 5
Release v0.8.0	Latest	v0.8.0	2026-08-15T03:09:31Z
Release v0.7.1		v0.7.1	2026-08-11T05:34:10Z
Release v0.7.0		v0.7.0	2026-08-03T20:09:13Z
Release v0.6.5		v0.6.5	2026-07-28T20:58:41Z
Release v0.6.4		v0.6.4	2026-07-27T22:03:45Z

$ gh run list --workflow=release.yml --limit 5
completed	success	Merge pull request #133: release v0.8.0 — multi-master composition	Release	v0.8.0	push	31861043480	19m35s	2026-08-15T03:08:42Z
completed	success	Merge pull request #132: release v0.7.1 — bug-fix round	Release	v0.7.1	push	31462027486	19m37s	2026-08-11T05:33:22Z
completed	failure	Merge pull request #129: release v0.7.0 — API rendering design overhaul	Release	v0.7.0	push	30848860064	18m55s	2026-08-03T20:08:22Z
completed	success	Merge pull request #125: release v0.6.5 — inline-math separator hotfix	Release	v0.6.5	push	30398631991	18m6s	2026-07-28T20:57:57Z
completed	success	Merge pull request #124: release v0.6.4 — Read the Docs migration	Release	v0.6.4	push	30309278708	18m12s	2026-07-27T22:03:03Z
```

Both tag probes produce no output, no release exists for v0.9.0, and the release workflow shows no
run for it — the most recent release-workflow run remains `31861043480` for `v0.8.0`, dated
2026-08-15, well before this phase.

This is observation **3 of 3**. Observation 1 was taken by plan `57-01` at phase head
(`57-BUMP-EVIDENCE.md` § "SC#4 — fence observation 1 of 3"), timestamped **2026-08-16T15:35:48Z**.
Observation 2 was taken by plan `57-08` (`57-SC4-INVARIANTS.md` § "SC#4 fence — observation 2 of
3"), timestamped **2026-08-22T06:51:54Z**. This third observation's timestamp
(**2026-08-22T07:04:01Z**) is roughly six days after observation 1 and about twelve minutes after
observation 2 — separated in time from both, at the natural end of this phase's own execution.

### The final `REQUIREMENTS.md` closeout-guard verification

```
$ sha256sum .planning/REQUIREMENTS.md
503efc7acb10642cee5f7d171bd66e15f4420b8610f7d0a22483424c17567d94  .planning/REQUIREMENTS.md
```

Matches `57-CLOSEOUT-GUARD.md`'s baseline digest
(`503efc7acb10642cee5f7d171bd66e15f4420b8610f7d0a22483424c17567d94`) byte-for-byte.

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)
```

Empty — no change against the tree's own HEAD.

```
$ git log --oneline 78bd595d344f46c6e1f5a18bce0e24da1f66a9ee..HEAD -- .planning/REQUIREMENTS.md
(no output)
```

No commit in this phase's own SHA range (phase-start SHA `78bd595d344f46c6e1f5a18bce0e24da1f66a9ee`,
quoted from `57-BUMP-EVIDENCE.md` § "Phase-head anchor re-measurement", through this plan's own
HEAD) touched `.planning/REQUIREMENTS.md`.

```
$ grep -n 'REL-08' .planning/REQUIREMENTS.md
128:- [ ] **REL-08**: v0.9.0 is published — PyPI wheel + sdist, GitHub Release carrying the curated
133:      prep-only final phase (57), which takes zero irreversible action — REL-08 closes at
212:| REL-08 | Phase 57 | Pending |
218:- v1 requirements: 26 total (25 defined 2026-08-15 + REL-08 added at roadmap creation)
```

Line 128 (`- [ ] **REL-08**: v0.9.0 is published — PyPI wheel + sdist, GitHub Release carrying the
curated`) and line 212 (`| REL-08 | Phase 57 | Pending |`) are byte-identical to the guarded quotes
in `57-CLOSEOUT-GUARD.md` § "The lines under guard". **The `phase.complete` auto-flip — which has
fired at four consecutive release-prep closes per this project's history — did NOT fire during this
phase.** No incident, no revert was needed at any point in Phase 57's own history.

**The phase is complete when this file is written.** REL-08 is still open, and the next action is
`/gsd-complete-milestone`, which executes the checklist above. Nothing in this phase may be read as
having performed any checklist item.

## What this phase deliberately did not do

- No `git tag v0.9.0` (or any tag) was created, locally or on the remote.
- No release workflow (`release.yml`) was triggered or executed as a real workflow run.
- Nothing was uploaded to PyPI.
- No GitHub Release was created.
- No pull request was opened or merged.
- No tag was created on `typsphinx-doc-translations`, its pin was not advanced, and its
  `update-pin.yml` was not dispatched by this phase.
- No `.planning/REQUIREMENTS.md` checkbox or Traceability row was flipped.

**The two reversible remote actions this phase's predecessor plans took** — a fast-forward push of
the milestone branch to `origin` (required before `ci.yml`'s `workflow_dispatch` could run at all)
and two `ci.yml` workflow dispatches (D-12: one pre-bump, one post-bump-authority, plus the
successor third dispatch that discharged `57-05`'s halt, `57-CI-EVIDENCE-RUN3.md`) — are named
in-scope by this phase's own D-12 decision and are not part of the publish. Pushing a branch and
dispatching a CI workflow are reversible; opening a PR and pushing a release tag are not, and
neither of the latter two occurred.
