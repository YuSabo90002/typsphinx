# Phase 63: v0.9.2 Release Prep (prep-only) — Publish Checklist Handoff

**This milestone does publish.** The checklist below **is** the sequence `/gsd-complete-milestone`
executes for v0.9.2 — the tag push, the `pypi` GitHub Environment's manual approval, the GitHub
Release body's byte-identity check, the `typsphinx-doc-translations` `update-pin.yml` dispatch and
that repository's own separate tag, and the Read the Docs `en`/`ja` `stable` verification. Nothing
in it was performed during this phase: this phase itself took **zero irreversible action**, proven
by `63-SC5-INVARIANTS.md`'s three fence observations — `## Observation 1 of 2` (phase head, wave 1),
`## Observation 2 of 2` (phase close, wave 3, with the scoped/widened `typsphinx/` diff pair as its
positive control), and `## Observation 3 — post-gap-closure re-probe` (taken after the gap-closure
correction commit `2a0bc3be`, because the first two pre-date it and say nothing about the tree that
exists now).

Seven prior handoffs (`46-HANDOFF.md` through `57-HANDOFF.md`) opened this way because every one of
those milestones actually published. The eighth, `61-HANDOFF.md`, opened with the negative because
v0.9.1 published nothing — the one anomaly in this project's history. This document restores the
standing positive-opening shape; that restoration is the correction D-13 calls for, not an
oversight.

## What this phase satisfied, and what it did not

**REL-09**, quoted verbatim from `.planning/REQUIREMENTS.md`:

> - [ ] **REL-09**: 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, the version
>       bumped as the sole literal in `pyproject.toml` with `uv.lock` and `README.md` in lockstep,
>       and the GitHub Release body sourced from `scripts/extract_changelog_section.py`.

**REL-09 remains open and unmet.** It closes at `/gsd-complete-milestone`, on the actual publish, not
here — the release itself has not happened. No plan in this phase touched its checkbox or
Traceability row.

Reporting each ROADMAP success criterion, citing the evidence file and section it rests on rather
than restating or re-deriving the verdict:

- **SC#1** (the version moves to 0.9.2 in one commit touching all four files) — **MET**.
  `63-CHANGELOG-EVIDENCE.md` § "SC#1 — version-literal lockstep" and the bump commit `10d9d95d`
  (`pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md` together).
- **SC#2** (the extractor was run and its output inspected) — **MET, after a correction.**
  `63-CHANGELOG-EVIDENCE.md`'s original extractor run-and-read section found the structural set
  clean, but a false blanket claim survived that inspection in the extracted body's intro paragraph
  ("The runtime changes are confined to `typsphinx/translator.py`, with no other file under
  `typsphinx/` touched") — falsified by that same file's own milestone-invariant-sweep diff showing
  five files changed. `63-REVIEW.md` CR-01 (Critical) and `63-VERIFICATION.md` SC#2's `gaps:` block
  both caught this independently. The gap closure (`63-05-PLAN.md`, commit `2a0bc3be`) deleted the
  blanket sentence and re-scoped a narrower, measured version into the IMG-08/IMG-09/IMG-10 bullet —
  the one fix it is actually true for. The structural set and the byte-identity proof were then
  re-run against the corrected text: `scripts/extract_changelog_section.py 0.9.2` exit 0, **4083**-byte
  non-empty stdout, zero scratch-block leakage, byte-identical to the section on disk (proven by a
  positive-control comparison against the pre-existing `## [0.6.5]` section). See
  `63-CHANGELOG-EVIDENCE.md` § "Post-correction re-run (gap closure, SC#2)" for the full re-run, and
  `63-SC5-INVARIANTS.md` § "Correction: § \"Commits after the CI dispatch\" is superseded" for the
  related evidence-integrity annotation.
- **SC#3** (the release-checkbox fence is proven held by a recorded SHA-256) — **MET**.
  `63-CLOSEOUT-GUARD.md` § "Baseline" (phase head) and § "Re-verification at phase close" (this
  plan) — both a MATCH on the SHA-256 digest, `wc -l`, the name-only diff, and the `REL-09` grep
  hits, with the third and decisive observation still owed, per that file's own
  § "For the operator running phase.complete" section (pointed at again below).
- **SC#4** (the bumped tree is proven green on runs executed in this phase) — **MET**.
  `63-GREEN-TREE-EVIDENCE.md` (full pytest suite 1543 passed / 5 skipped, `black --check .` and
  `mypy typsphinx/` both exit 0, both documentation builds from a removed `docs/_build` reporting
  `3 warnings.` / `5 warnings.`) and `63-CI-EVIDENCE.md` (one dispatched `ci.yml` run, `33309565005`,
  all 12 jobs `success` including both `windows-latest` and both `macos-latest` lanes, `ruff`'s
  verdict read from the `Lint and Format Check` job's own `Run lint with tox` step).
- **SC#5** (zero irreversible action, probed three times, and the handoff is standalone) — **MET**.
  `63-SC5-INVARIANTS.md` § "Observation 1 of 2" and § "Observation 2 of 2" for the two
  waves-separated fence probes taken before the gap-closure correction, § "Observation 3 —
  post-gap-closure re-probe" for the third probe taken after commit `2a0bc3be` (necessary because
  the first two say nothing about the tree that exists now), § "The typsphinx/ diff (SC#5)" and its
  post-correction re-take in Observation 3 for the empty scoped diff paired with the non-empty
  five-file widened positive control, and this document itself for the standalone handoff half.

**Not satisfied by this phase, and structurally out of reach here:** the entire publish half — the
`v0.9.2` tag push, `release.yml` firing to publish to PyPI and create the GitHub Release, and the
two-repository tagging cost on `typsphinx-doc-translations` — belongs to
`/gsd-complete-milestone`. Confirming Read the Docs `stable` is green on both projects at `0.9.2` is
also out of reach here. This is a handoff, not a claim that any of it has already happened.

## The publish checklist

Every step below is recorded as what `/gsd-complete-milestone` executes. **None of it was performed
in this phase** — the prohibitions block in `63-04-PLAN.md`, carried forward unchanged by the
gap-closure plans `63-05-PLAN.md` and `63-06-PLAN.md`, forbids every one of these actions across the
whole phase including the closure, and the fence assertions above confirm none occurred.

### Before the tag push — the `pypi` Environment approval is an EXPECTED gate

`.github/workflows/release.yml`'s `publish-pypi` job runs behind the `pypi` GitHub Environment,
which carries a **manual approval requirement**. Name this ahead of the step that triggers it,
because a workflow **paused** on that approval looks exactly like a **failed** workflow to an
operator scanning `gh run list` — a paused row and a failed row are visually indistinguishable
without opening the run. Meet this warning before the surprise: after pushing the tag (next
section), watch the run and expect it to sit waiting at `publish-pypi` until the approval is given
in the GitHub UI (or via `gh run review` naming the `pypi` environment).

### 1. Push the release tag on the merge commit

Owner: `/gsd-complete-milestone`. This is the action that fires `.github/workflows/release.yml`.
Nothing in this phase or its predecessor plans was irreversible — pushing the milestone branch and
dispatching `ci.yml` (both already done, both reversible) are the only remote-affecting actions
taken before this point. The tag push is the first irreversible one.

```bash
git tag -a v0.9.2 -m "Release v0.9.2" <merge-commit-sha>
git push origin v0.9.2
```

`release.yml`'s `validate` job runs `scripts/extract_changelog_section.py 0.9.2` as a real
precondition check and aborts the whole release before any upload if the section is missing or
empty — it is not, per SC#2 above.

### 2. Watch the release workflow to completion, job by job

Owner: `/gsd-complete-milestone`, with the owner-manual approval from the step above.
`.github/workflows/release.yml`'s job sequence: `validate` → `build` → `publish-pypi` (the `pypi`
Environment gate) → `create-release`.

#### REL-04's re-offer — a named observation, not a requirement of this milestone

REL-04 ("The `create-release` job proven end to end") is re-offered here exactly as
`61-HANDOFF.md` § "What v0.9.2 must also pick up" instructed, and is **not folded into any plan and
not promoted to a requirement** of this milestone:

(a) **Why a failure now would be a regression, not the known defect that REL-04 tracks.**
    `release.yml`'s `create-release` job carries explicit `Install uv` / `Set up Python` steps at
    HEAD, and it ran green at the **v0.8.0** (`31861043480`) and **v0.9.0** (`32560457509`) real tag
    pushes. The original defect — `uv: command not found`, exit 127, run `30848860064` at the
    v0.7.0 close — is fixed and has stayed fixed across two subsequent real releases.

(b) **The exact observation to make.** `gh run watch` on the dispatched `release.yml` run, then read
    the `create-release` job's own conclusion literally — do not assume success from the overall
    run status alone; observe the job directly.

(c) **The response if it fails.** Fix it inside this release work and re-run the job. Do not defer
    it to a future milestone a third time.

(d) **The todo stays open until proven, and REL-04 stays out of this milestone's requirement set.**
    `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` stays in
    `pending/` and closes only on an observed green `create-release` at a real tag push — which does
    not happen in this phase, only at the milestone close this document hands off to. REL-04 is not
    folded into any plan and is not promoted to a requirement of this milestone.

### 3. Verify the GitHub Release body's byte-identity

Owner: owner-manual, after item 2 shows `create-release` green.

```bash
uv run python scripts/extract_changelog_section.py 0.9.2 > /tmp/expected-notes.md
gh release view v0.9.2 --json body -q .body > /tmp/actual-notes.md
diff /tmp/expected-notes.md <(head -n "$(wc -l < /tmp/expected-notes.md)" /tmp/actual-notes.md)
```

A **non-empty `diff` is a hard failure**, not a formatting difference — `create-release` appends an
`## Installation` block and GitHub's own auto-generated notes after the extractor's output, so the
comparison truncates the actual body to the extractor's own line count before diffing. Plan `63-01`
originally proved the extractor's stdout byte-identical to the section as it sat in `CHANGELOG.md`
at that time; the gap closure (`63-05-PLAN.md`) then corrected a false claim in that same section
and **re-took the byte-identity proof against the corrected text** — `63-CHANGELOG-EVIDENCE.md`
§ "Post-correction re-run (gap closure, SC#2)" § "SC#2's structural set, re-run against the
corrected text" is the evidence this operator's diff must match against, not the pre-correction
proof. This check closes the second half of that same chain, against the *published* body rather
than the file on disk.

### 4. Advance the second repository's pin, then tag it — two separate actions

Owner: `/gsd-complete-milestone` for the dispatch, owner-manual for the tag timing. The pin is
advanced by dispatching **that repository's own** `update-pin.yml` workflow — a **MANUAL dispatch**,
not a side effect of this repository's own tag push:

```bash
gh workflow run update-pin.yml --repo YuSabo90002/typsphinx-doc-translations
gh run list --repo YuSabo90002/typsphinx-doc-translations --workflow=update-pin.yml --limit 1
gh run watch --repo YuSabo90002/typsphinx-doc-translations <run-id>
```

The workflow does **not** itself create a tag on that repository — advancing the pin and tagging are
two separate steps. Once the pin commit lands, tag that repository's tracked branch with `v0.9.2`
pointing at that commit.

### 5. Measure Read the Docs `stable` on both projects

Owner: owner-manual — outside `/gsd-complete-milestone`'s own reach. Doable with unauthenticated
public API calls, no credential needed, for both `en` (project `typsphinx`) and `ja` (project
`typsphinx-ja`): the root URL resolves to the stable path
(`https://typsphinx.readthedocs.io/` → `/en/stable/`); the `stable` version identifier on each
project (expected to match the `v0.9.2` merge commit for `en` and the translations repository's own
`v0.9.2`-tagged commit for `ja`); both pages report `0.9.2`; both PDFs are served
(`application/pdf`). Both projects' Default Versions have been `stable` since the v0.6.4 close and
have needed no re-flip at any subsequent close — none is expected here either, but this step
confirms rather than assumes it.

## Before declaring the milestone closed

Point the operator explicitly at `63-CLOSEOUT-GUARD.md` § "For the operator running phase.complete".
The third and decisive fence observation is owed there, after `phase.complete`-family tooling has
run for Phase 63 — outside any plan's reach, and precisely the moment at which the flip has
historically landed at **five consecutive** prior release-prep closes. Reproduced here in one line
so it is actionable without opening that file:

If `sha256sum .planning/REQUIREMENTS.md`, `git diff --name-only -- .planning/REQUIREMENTS.md`, or
`grep -n 'REL-09' .planning/REQUIREMENTS.md` diverge from `63-CLOSEOUT-GUARD.md`'s Baseline, run
`git checkout -- .planning/REQUIREMENTS.md` and report the divergence — **never accept it, never
commit it.**

## What this phase deliberately did not do

- No `git tag v0.9.2` (or any tag) was created, locally or on the remote — `git tag -l 'v0.9.2'` and
  an unfiltered `git ls-remote --tags origin` both come back empty of it, confirmed fresh in
  `63-SC5-INVARIANTS.md` § "Observation 2 of 2".
- No PyPI upload occurred and no GitHub Release exists for `v0.9.2`.
- No pull request was opened or merged by this phase.
- No `typsphinx-doc-translations` `update-pin.yml` dispatch occurred, its pin was not advanced, and
  no tag was created there by this phase.
- No Read the Docs setting was flipped.
- No `.planning/REQUIREMENTS.md` checkbox or Traceability row was touched — confirmed MATCH at
  phase close, `63-CLOSEOUT-GUARD.md` § "Re-verification at phase close".

**Three outward-facing ideas were considered and declined for this phase (D-10)**, each because it
is irreversible and belongs, if wanted at all, at or after `/gsd-complete-milestone` rather than
inside a prep-only phase: a GitHub Security Advisory for the inline-image blocker, a PyPI yank of
the published `0.9.0`, and a README banner disclosing the defect. Recorded here rather than silently
dropped, so the owner can revisit any of them at the close if desired.

**No `Migrating from 0.9.0 to 0.9.2` guide was written (D-12).** 0.9.2 is a patch release that breaks
nothing and needs no rewrite from anyone — the one prior no-breaking-change patch release (`0.6.5`)
has no migration guide either, so nothing about migration is owed at this close.

---
*Phase: 63-v0-9-2-release-prep-prep-only*
*Plan: 04, 06*
