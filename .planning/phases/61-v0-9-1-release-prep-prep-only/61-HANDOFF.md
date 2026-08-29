# Phase 61: v0.9.1 Release Prep (prep-only) — Milestone Close-Out, No Publish

**This milestone publishes nothing.** `/gsd-complete-milestone` performs no tag (local or
remote), no PyPI publish, no GitHub Release, and no pull request for this milestone. v0.9.1 is
never published — the next published release is 0.9.2 (D-02). Everything below this point is an
inheritance record for the v0.9.2 release-prep phase to read and act on, not a checklist to
execute now, and no item under it should be read as an instruction for this milestone's close.

Seven consecutive prior handoffs (`46-HANDOFF.md` through `57-HANDOFF.md`) opened as a publish
checklist because every prior milestone actually published. This is the first time it does not,
and the inversion is deliberate (D-12, D-13).

## What this phase satisfied, and what it did not

**REL-09**, quoted verbatim from `.planning/REQUIREMENTS.md`:

> - [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
>       bumped as the sole literal in `pyproject.toml` with `uv.lock` and `README.md` in lockstep,
>       and the GitHub Release body sourced from `scripts/extract_changelog_section.py`.

**REL-09 remains open and unmet.** It carries forward to the v0.9.2 milestone with its literal
wording — including its `v0.9.1` version string — unchanged, because the owner explicitly declined
both rewriting it to say `v0.9.2` and closing it as superseded (D-08). The only inconsistency this
leaves behind is a version number inside a requirement that has never been satisfied, which is
accurate, because nothing was released. No plan in this phase touched REL-09's checkbox.

Reporting every ROADMAP success criterion in its D-11-mapped form, citing each one's own evidence
artifact and section rather than restating or re-deriving the verdict:

- **SC#1** (version moves atomically to 0.9.1) — **DROPPED** (D-11, D-01). Stated explicitly rather
  than as met or unmet: this phase performs no version bump at all. `pyproject.toml:7` stays
  `0.9.0`, `README.md:347` stays `Stable (v0.9.0)`, `uv.lock` is not regenerated for a version
  change — measured in `61-GREEN-TREE-EVIDENCE.md` § "Provisioning and tree identity".
- **SC#2** (curated `## [0.9.1]` CHANGELOG entry, tail link rollover, extraction-script
  byte-for-byte reproduction) — **REWORDED** (D-11, D-03, D-04). The curated content is authored
  under the existing `## [Unreleased]` heading instead of a new `## [0.9.1]` section, and the tail
  link-reference block is untouched. See `61-CHANGELOG-EVIDENCE.md` § "The PATH-01 bullet (tracer
  slice)", § "The remaining two defect families (IMG and MSG)", and § "Pure-addition proof" for the
  content itself, and § "Fence assertions over CHANGELOG.md and the version literals" for proof
  that no version literal moved. The extraction-script byte-for-byte reproduction check moves to
  the v0.9.2 release-prep phase along with the versioned section it would extract — see § "What
  this file is NOT" in that same evidence file.
- **SC#3** (the tree is proven green on live runs) — **RETAINED, re-anchored** (D-11, D-09) to the
  milestone-final tree rather than a "bumped tree", since D-01 removes the bump. Local half: full
  pytest suite (1513 passed, 5 skipped), `black --check`, `mypy`, and the version-sync guard family
  — `61-GREEN-TREE-EVIDENCE.md` § "SC#3 — full pytest suite" through § "Executed versus skipped".
  CI half: fresh `workflow_dispatch` run `33260111745`, 12/12 jobs `success` including both
  `windows-latest` lanes — `61-CI-EVIDENCE.md` § "Run" and § "Both windows-latest lanes". Docs
  render comparison against the 3/5 baseline — `61-CHANGELOG-EVIDENCE.md` § "Docs render — full
  comparison against the 3 / 5 baseline".
- **SC#4** (the no-irreversible-action fence is proven held) — **RETAINED in full** (D-11, D-10).
  Two fence observations at genuinely separated timestamps (elapsed interval 38m16s, spanning two
  waves and a full 3-OS CI dispatch), each network probe carrying a real positive control, plus the
  scoped `typsphinx/` diff (empty) proven non-vacuous by a live widened positive control (exactly
  `CHANGELOG.md`, +28/−0) — `61-SC4-INVARIANTS.md` § "Observation 1 of 2", § "Observation 2 of 2",
  § "The typsphinx/ diff (SC#4)", and § "Commits after the CI dispatch". The
  `.planning/REQUIREMENTS.md` checksum re-verified at phase close with an explicit MATCH verdict on
  all five comparisons — `61-CLOSEOUT-GUARD.md` § "Re-verification at phase close".
- **SC#5** (a standalone handoff checklist) — **RETAINED and RE-AIMED** (D-11). Re-aimed at what the
  *v0.9.2* release-prep phase and its own `/gsd-complete-milestone` inherit, not at what this
  milestone's `/gsd-complete-milestone` executes — because this milestone's close performs no
  publish (D-02, D-12). Satisfied by this document itself, in the two sections immediately below.

**Not satisfied by this phase, and not intended to be:** any version bump, any `## [0.9.1]`
CHANGELOG section, any tag, any publish, any disclosure of the inline-image blocker on a public
surface (D-05), and any fix for that blocker (D-07). None of these was attempted; all are recorded
here as explicitly out of scope, not as gaps.

## What the v0.9.2 milestone inherits

Three standing publish steps that must survive the milestone boundary because they are easy to
lose and expensive to rediscover across a boundary where, for the first time in this project's
history, the immediately preceding milestone did not exercise them. Each is written with its
version as the placeholder `vX.Y.Z` rather than hard-coded to the skipped `0.9.1`, so a future
reader cannot copy a dead tag name out of this file.

### 1. The second-repository tag for `typsphinx-doc-translations`

Advanced by dispatching **that repository's own `update-pin.yml` workflow** — not by a hand-made
clone, edit, and push, so the same reviewed catalog-regeneration and no-content-free-commit logic
applies every time it runs. Command shape (`vX.Y.Z` is the version being released, not `0.9.1`):

```bash
gh workflow run update-pin.yml --repo YuSabo90002/typsphinx-doc-translations
gh run list --repo YuSabo90002/typsphinx-doc-translations --workflow=update-pin.yml --limit 1
gh run watch --repo YuSabo90002/typsphinx-doc-translations <run-id>
```

The workflow does **not** itself create a tag on that repository — advancing the pin and tagging
are two separate steps. Once the pin commit lands, tag that repository's tracked branch with
`vX.Y.Z`.

### 2. The Read the Docs `stable` measurement for both projects

Doable with unauthenticated public API calls — no credential is needed. Measure, for both `en`
(`typsphinx`) and `ja` (`typsphinx-ja`): that the root URL resolves to the stable path
(`https://typsphinx.readthedocs.io/` → `/en/stable/`); the `stable` version identifier on each
project (expected to match the `vX.Y.Z` merge commit for `en` and the translations repository's own
`vX.Y.Z`-tagged commit for `ja`); that both report the new version; and that both PDFs are served
(`application/pdf`). Both projects' Default Versions have been `stable` since the v0.6.4 close and
have needed no re-flip at any subsequent close.

### 3. The GitHub Release body reproduction check

The GitHub Release body must be byte-identical to `scripts/extract_changelog_section.py`'s stdout
for the released version:

```bash
uv run python scripts/extract_changelog_section.py vX.Y.Z > /tmp/expected-notes.md
gh release view vX.Y.Z --json body -q .body > /tmp/actual-notes.md
diff /tmp/expected-notes.md <(head -n "$(wc -l < /tmp/expected-notes.md)" /tmp/actual-notes.md)
```

A non-empty `diff` is a hard failure, not a formatting difference. This script was deliberately
**not** invoked in this phase — there is no `## [0.9.1]` (or any other new versioned) section for
it to extract, since D-03/D-04 keep this phase's content under `## [Unreleased]`.

## What v0.9.2 must also pick up

- **The inline-image blocker** —
  `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`.
  This is a **pre-existing defect, measured against the v0.9.0 tag, not a regression** introduced
  by this milestone's own work (D-06: `git diff v0.9.0..HEAD -- typsphinx/translator.py` is 25
  lines touching only IMG-05's `escape_typst_string()` call; `visit_image()`'s missing leading
  separator is byte-identical to the `v0.9.0` tag). Its shape in one sentence: an image node
  preceded by sibling content in the same paragraph or list item is emitted adjacent to the
  preceding code-mode expression, so Typst refuses it with `expected semicolon or line break` and
  the `typstpdf` builder raises `ExtensionError`, writing no PDF for any master document in the
  project. This blocker is the reason v0.9.1 is never published (D-02); v0.9.2's requirements pass
  should pick it up directly rather than rediscover it.
- **The `release.yml` `create-release` job todo** —
  `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md`. CONTEXT
  declines to fold it into this phase because with no publish here there is nothing to verify it
  against; it should be **re-offered at the v0.9.2 release-prep phase's own handoff**, where a real
  tag push will finally exercise it.
- **The `## [Unreleased]` bullets this phase authored** (PATH-01, IMG-04 through IMG-07, MSG-02
  through MSG-05 — see `61-CHANGELOG-EVIDENCE.md`) are promoted into the v0.9.2 milestone's own
  `## [0.9.2]` versioned section, together with the inline-image blocker fix's own bullet, when
  that milestone's release-prep phase runs — the same promote-existing-bullets mechanism Phase 57's
  D-02 used for the v0.8.0 → v0.9.0 boundary.

## Before declaring the milestone closed

Reproduced verbatim from `61-CLOSEOUT-GUARD.md` § "For the operator running phase.complete", so an
operator following this handoff reaches the procedure without opening that file. After
`phase.complete`-family tooling has run for Phase 61 — outside any plan's reach, and precisely the
moment at which the flip has historically landed at **five consecutive** prior release-prep
closes — run:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against the Baseline: 4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-09' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   127:- [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
#   206:| REL-09 | Phase 61 | Pending |
#   220:Phase 60 → 4 (MSG-02, MSG-03, MSG-04, MSG-05) · Phase 61 → 1 (REL-09).
```

If any comparison diverges, revert it by hand:

```bash
git checkout -- .planning/REQUIREMENTS.md
```

**The flip is reverted and reported, never accepted and never committed.** This is the rule this
project has followed at every prior release-prep close where the flip was caught: revert first,
report second, never ship the flipped state as part of the milestone's own close.

## Fence observation

Recorded live, at a moment demonstrably separated from `61-SC4-INVARIANTS.md`'s two earlier
observations and `61-CLOSEOUT-GUARD.md`'s close-time re-verification — following the prior
handoffs' practice of placing a final observation inside the handoff itself:

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ sha256sum .planning/REQUIREMENTS.md
4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1  .planning/REQUIREMENTS.md
```

Empty diff, and the digest matches `61-CLOSEOUT-GUARD.md`'s Baseline byte-for-byte. Also confirmed
live at the same moment, closing the fence one last time:

```
$ git tag -l 'v0.9.1'
(no output)

$ git status --porcelain typsphinx/ tests/ CHANGELOG.md pyproject.toml README.md .planning/REQUIREMENTS.md
(no output)
```

**The phase is complete when this file is written.** REL-09 is still open, and the next action is
`/gsd-complete-milestone`, which archives this milestone's phase directories and prepares v0.9.2 —
it does not tag, does not publish to PyPI, and does not create a GitHub Release. Nothing in this
phase, and nothing in this document, may be read as having performed any publish step.

## What this phase deliberately did not do

- No `git tag v0.9.1` (or any tag) was created, locally or on the remote.
- No release workflow (`release.yml`) was triggered as a real tag-triggered run — only `ci.yml` was
  dispatched, twice across this phase's predecessor plans, both reversible actions.
- Nothing was uploaded to PyPI.
- No GitHub Release was created.
- No pull request was opened or merged.
- No tag was created on `typsphinx-doc-translations`, its pin was not advanced, and its
  `update-pin.yml` was not dispatched by this phase.
- No `.planning/REQUIREMENTS.md` checkbox or Traceability row was flipped.
- No public-surface disclosure of the inline-image blocker was made (D-05) — this document is
  `.planning/` documentation, not a published surface.

---
*Phase: 61-v0-9-1-release-prep-prep-only*
*Plan: 04*
