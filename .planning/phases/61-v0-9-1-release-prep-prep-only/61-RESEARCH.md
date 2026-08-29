# Phase 61: v0.9.1 Release Prep (prep-only) - Research

**Researched:** 2026-08-29
**Domain:** Milestone close-out procedure (no version bump, no publish) — CHANGELOG authoring under
`## [Unreleased]`, live-run green proof, fence-proof mechanics, and a standalone handoff for a
publish that does not happen this milestone.
**Confidence:** HIGH — every finding below is either a direct read of a canonical-ref file this
session, a live command run against the current tree this session, or an explicit quote from
`61-CONTEXT.md` (already authoritative per the assignment). No finding required speculation.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

D-01 through D-13, verbatim intent (full text in `61-CONTEXT.md`, not re-quoted here to avoid
drift — this research treats them as binding and cites them by number):

- **D-01**: No version bump. `pyproject.toml:7` stays `0.9.0`; `README.md:347` stays
  `Stable (v0.9.0)`; `uv.lock` untouched.
- **D-02**: v0.9.1 is never published. Next published release is 0.9.2.
- **D-03**: The three defect families are authored under the existing `## [Unreleased]` heading,
  not a new `## [0.9.1]` heading. `## [Unreleased]` currently holds zero real bullets.
- **D-04**: The tail link-reference block is not touched — no `[0.9.1]` line, `[Unreleased]` stays
  `v0.9.0...HEAD`.
- **D-05**: No public-surface disclosure of the inline-image blocker (no README Known Limitations
  entry, no CHANGELOG `### Known Limitations`, no docs note).
- **D-06**: The inline-image blocker is a pre-existing defect (not a v0.9.1 regression) — measured
  via `git diff v0.9.0..HEAD -- typsphinx/translator.py`.
- **D-07**: The blocker fix belongs to v0.9.2, not this milestone.
- **D-08**: REL-09 carries forward unmet, wording unchanged (including its literal `v0.9.1` string).
- **D-09**: SC#3's live-run green proof retained in full, re-anchored to the milestone-final tree.
  One CI dispatch is the default; a second only if a plan lands a code-affecting change mid-phase.
- **D-10**: SC#4's fence proof retained in full — tag/publish probes twice at separated times,
  `git diff` no unintended `typsphinx/` change, `REQUIREMENTS.md` checksum guard.
- **D-11**: The explicit ROADMAP-to-CONTEXT mapping — SC#1 DROPPED, SC#2 REWORDED, SC#3 RETAINED
  (re-anchored), SC#4 RETAINED in full, SC#5 RETAINED (re-aimed at what v0.9.2 inherits).
- **D-12**: `/gsd-complete-milestone` runs but performs no publish step for this milestone.
- **D-13**: `61-HANDOFF.md` preserves the three standing publish steps as an inheritance record
  (with version left as a placeholder), not as instructions to execute now.

### Claude's Discretion

- Exact wording of `## [Unreleased]` bullets, their `### Added`/`### Changed`/`### Fixed` section
  assignment, and granularity — including whether `typsphinx/pathfmt.py` or MSG-01's test-side
  decoupling earn a bullet at all. Requirement IDs in trailing parentheses is settled house style.
- Whether the new bullets sit above or below `### Planned for Future Releases` (leave that
  subsection untouched either way).
- Whether a `### Verified` subsection is authored now or left for v0.9.2 (latter is cheaper).
- Plan decomposition/ordering; how the docs warning baselines for SC#3 are established (reuse a
  prior recorded baseline vs. fresh measurement).
- The mechanical form of the `REQUIREMENTS.md` checksum guard and where the two separated fence
  probes are recorded.
- Format/heading structure of `61-HANDOFF.md`; where live-run evidence is recorded — subject to the
  reserved-name constraint: never name an evidence file `61-VERIFICATION.md`.
- Whether a milestone-diff sweep anchored at `v0.9.0` is worth running given no `### Verified`
  claims are authored this phase; if run, its positive control must be real.

### Deferred Ideas (OUT OF SCOPE)

- Rewriting ROADMAP.md's Phase 61 entry to match CONTEXT.md (owner declined — D-11 exists instead).
- Publishing v0.9.1 after all (foreclosed by D-02 for this milestone).
- Disclosing the inline-image blocker on any public surface (foreclosed by D-05 for this phase;
  natural place is the v0.9.2 release-prep phase as a `### Fixed` bullet).
- Any `typsphinx/` behaviour change, including the inline-image fix and the fourth-module hardcoded
  delimiter todo — both belong to v0.9.2.
- Adding `"0.9.1"` to `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py` — no `0.9.1` section
  for that gate to find.
- A `Migrating from 0.9.0 to 0.9.1` guide — no release, nothing to migrate.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-09 | `[ ]` (unmet, wording unchanged): "v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version bumped as the sole literal in `pyproject.toml` with `uv.lock` and `README.md` in lockstep, and the GitHub Release body sourced from `scripts/extract_changelog_section.py`" — `.planning/REQUIREMENTS.md:127-129`. **Per D-08 this phase does not attempt to satisfy this text** — it stays `[ ]`, carries forward unmet into v0.9.2 with its literal `v0.9.1` wording, and no plan touches its checkbox. The phase's actual work (CHANGELOG-under-Unreleased authoring, live-run green proof, fence proof, handoff) is what CONTEXT.md's D-11 mapping substitutes for ROADMAP's original SC#1/SC#2 in service of a not-REL-09-closing milestone close-out. | § "The `## [Unreleased]` authoring shape" and § "SC#4 fence-proof mechanics" below supply the mechanics; the requirement itself is not closed here (D-08). |
</phase_requirements>

## Summary

Phase 61 is not a version-bump release-prep phase — CONTEXT.md's D-01 through D-13 override
ROADMAP's Phase 61 shape entirely. It is a **milestone close-out** phase: author three defect-family
bullets under the CHANGELOG's already-existing, currently-empty `## [Unreleased]` heading; prove the
milestone-final tree green on live runs (full pytest, `black`/`ruff`/`mypy`, both docs tox
environments against a **reusable, already-current** warning baseline, and one fresh 3-OS CI
dispatch); prove the no-irreversible-action fence held (tag/publish probes twice, a scoped
`typsphinx/` diff, a `REQUIREMENTS.md` checksum guard); and write a `61-HANDOFF.md` that inverts the
seven-milestone habit by opening with the negative ("this milestone publishes nothing") before
listing what v0.9.2 inherits.

Every mechanical piece this phase needs has a direct precedent already on disk: Phase 52
(`52-*-EVIDENCE.md`, `52-SC4-INVARIANTS.md`, `52-HANDOFF.md`) is the "author CHANGELOG bullets from
scratch against an empty `## [Unreleased]`" precedent (identical shape to this phase, since Phase 57
had seven pre-written bullets to promote and this phase has zero). Phase 57
(`57-SC4-INVARIANTS.md`, `57-CLOSEOUT-GUARD.md`, `57-CI-EVIDENCE-RUN3.md`, `57-HANDOFF.md`) is the
most recent, most complete fence-proof and CI-dispatch precedent, including the `uv.lock`-before-
dispatch sequencing rule (D-13 AMENDED, 10 `--locked` steps across 4 workflows) and the exact `gh`
command sequence. The docs warning baseline this phase needs — **3 warnings for `docs-html`, 5 for
`docs-pdf`** — was measured at the Phase 56 close, re-confirmed byte-identical at the Phase 57
close (post-bump), and this session's own `git log` check confirms **zero commits have touched
`docs/source/` or `CHANGELOG.md` since** the Phase 60 CI-authority commit (`130f614e`) — so the
baseline is current, not stale, but **a fresh doc build must still run this phase** (after the
`## [Unreleased]` bullets are authored) to confirm the CHANGELOG edit itself introduces no new
warning, exactly as `57-GREEN-TREE-EVIDENCE.md`'s "Baseline comparison" section did.

**Primary recommendation:** Follow the Phase 52 CHANGELOG-authoring shape (write from scratch, not
promote), the Phase 57 fence-proof/CI-dispatch mechanics (most recent, most complete, and explicitly
named by `61-CONTEXT.md`'s canonical refs as the precedent to follow), and reuse the 3/5
docs-warning baseline as the comparison target for a fresh, in-phase doc rebuild.

## Architectural Responsibility Map

This phase touches no runtime architecture — it is planning-and-release-surface work only. For
completeness:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CHANGELOG content authoring | Documentation / release surface | Docs build (Sphinx via `myst_parser`) | `CHANGELOG.md` is included wholesale into `docs/source/changelog.rst`, so edits there are simultaneously a release artifact and a published docs page — malformed MyST shows up as a docs-build warning, which is exactly what this phase's SC#3 warning-baseline check polices. |
| Live-run green proof (pytest/lint/type/docs/CI) | CI / Build tooling | — | No product-tier component; this is process verification over `.github/workflows/ci.yml` and local `tox` environments. |
| Fence proof (no tag, no publish) | Release machinery (`.github/workflows/release.yml`, `gh` CLI) | Git (`git tag`, `git ls-remote`) | Read-only probes against GitHub's release/tag surface; no write action is taken. |
| Handoff document | Documentation / project planning | — | `61-HANDOFF.md` lives under `.planning/`, not the product tree; it is read by a future `/gsd-complete-milestone` invocation, not by any runtime component. |

## Standard Stack

No new library, package, or runtime dependency is introduced by this phase (D-01, D-08's "no new
runtime dependency" milestone framing carries forward unchanged — this phase adds nothing to
`pyproject.toml`). All tooling used is already installed and already exercised by prior phases:

### Core

| Tool | Version (verified) | Purpose | Why Standard |
|------|---------------------|---------|---------------|
| `tox` | pinned via `tox-uv-bare~=1.35` (`CLAUDE.md`) | Runs `docs-html`/`docs-pdf`/lint/type/cov envs | Project's standing task runner (`tox.ini` `env_list`) |
| `uv` | project-pinned via `uv.lock` | Dependency sync, `uv run` | Mandatory per-worktree provisioning (`CLAUDE.md` § Worktree-isolated execution) |
| `gh` CLI | whatever is on `$PATH` (verified functional this session: `gh run list`, `gh release list`, `gh tag` probes all returned live data) | CI dispatch, run inspection, tag/release probing | Used at every prior release-prep close (Phases 46, 52, 57) for the identical purpose |
| `scripts/extract_changelog_section.py` | in-repo, pytest-covered since Phase 41 | Extracts a `## [X.Y.Z]` section verbatim | Named in `61-HANDOFF.md` per D-13 but **not exercised** this phase — there is no `## [0.9.1]` section to extract (out of scope, see CONTEXT `<domain>` "Out of scope") |

### Package Legitimacy Audit

**Not applicable.** This phase installs no external packages — `pyproject.toml`'s dependency array
and `[project.optional-dependencies]` extras are untouched by every decision in `61-CONTEXT.md`
(D-01 pins `pyproject.toml:7` and nothing else moves). No `npm view` / `pip index versions` / `cargo
search` verification is needed; skipping this section's table per the "Required whenever this phase
installs external packages" gate condition, which does not apply here.

## Architecture Patterns

### System Architecture Diagram

Not applicable in the conventional sense — this phase has no data-flow pipeline. The "flow" this
phase produces is a **documentation and evidence artifact** flow:

```
Three defect families (MSG-01..05, PATH-01, IMG-04..07, from Phases 58-60's own SUMMARY/VERIFICATION
files)
        |
        v
Authored as new bullets under CHANGELOG.md's existing "## [Unreleased]" heading
        |
        +----> docs/source/changelog.rst (`.. include::`) --> tox -e docs-html / docs-pdf
        |         (warning count checked against the 3/5 baseline)
        |
        v
Full pytest + black + ruff + mypy (local) ----+
                                                |
Fresh `gh workflow run ci.yml --ref <branch>`  +--> all evidence transcribed into
  --> 3-OS matrix, both windows-latest lanes        {padded_phase}-{TOPIC}-EVIDENCE.md files
        |
        v
Fence probes (git tag -l v0.9.1 / git ls-remote --tags origin v0.9.1 / gh release list /
  gh run list --workflow=release.yml), each run TWICE at separated timestamps
        |
        v
REQUIREMENTS.md sha256sum recorded at phase head, re-verified at phase close
  (catches the phase.complete auto-flip, 5-for-5 fired at prior release-prep closes)
        |
        v
61-HANDOFF.md — opens with the negative ("this milestone publishes nothing"), then the
  publish-step inheritance record (second-repo tag, RTD stable measurement, byte-identical
  GitHub Release body), version left as a placeholder for v0.9.2 to fill in
```

### Recommended Evidence-File Structure

Following the `{padded_phase}-{TOPIC}-EVIDENCE.md` naming precedent (see "Don't Hand-Roll" and the
worked file census below), a plan decomposition roughly mirroring this shape is well supported by
precedent:

```
.planning/phases/61-v0-9-1-release-prep-prep-only/
├── 61-CHANGELOG-EVIDENCE.md      # the authored bullets, before/after CHANGELOG.md excerpt,
│                                  # docs-html/docs-pdf warning-count comparison against 3/5
├── 61-GREEN-TREE-EVIDENCE.md     # full pytest, black/ruff/mypy transcripts
├── 61-CI-EVIDENCE.md             # the single (or, if triggered, dual) 3-OS dispatch transcript
├── 61-SC4-INVARIANTS.md          # fence proof: tag/publish probes x2, scoped typsphinx/ diff
├── 61-CLOSEOUT-GUARD.md          # REQUIREMENTS.md baseline checksum + guarded line quotes,
│                                  # recorded EARLY (phase head), re-verified at close
├── 61-HANDOFF.md                 # the standalone, negative-first publish-inheritance checklist
└── (NOT 61-VERIFICATION.md — reserved for the phase verifier)
```

### Pattern 1: Author CHANGELOG bullets under an already-empty `## [Unreleased]`

**What:** When `## [Unreleased]` holds zero real bullets (as measured this session — only
`### Planned for Future Releases`), write fresh bullets directly from the requirements each landed
phase satisfied, not by promoting pre-existing prose (contrast Phase 57, which promoted seven
already-written bullets).

**When to use:** This phase's exact situation — three defect families (PATH-01; IMG-04/05/06/07;
MSG-01/02/03/04/05) with **zero** existing `## [Unreleased]` prose to draw from.

**Example, the house style measured directly from `CHANGELOG.md`'s own `## [0.9.0]` `### Fixed`
section** (`CHANGELOG.md:81-124`, quoted verbatim, the closest-precedent bullet — landed by Phase
57's plan 57-11 for the *same class* of Windows `repr()`-escaping defect this milestone's MSG-family
requirements also address):

```markdown
- **On Windows, the template-path refusal messages introduced above no longer double every
  backslash in a reported path.** The `typst_document_templates` collision refusals — a template
  bundle colliding with Sphinx's own `templates_path`, a template resolving to an ancestor of the
  source directory, or two registry keys resolving to the same bundle destination — used to quote
  the offending path with Python's `repr()`, which escapes each backslash; on Windows the message
  a user read carried two literal backslashes where the platform's own single separator belongs.
  The path is now quoted without escaping, so the reported path matches what actually appears on
  disk.
```

Note this exact bullet carries **no** trailing requirement-ID parenthesis, because it landed as an
unplanned mid-phase fix before Phase 61's MSG-family requirements existed. Every other `### Fixed`
bullet in the same section **does** carry one (`(XREF-05)`, `(BLD-07)`, `(BLD-08)`, `(BLD-09)`,
`(IMG-03)`) — confirming CONTEXT.md's "Requirement IDs in trailing parentheses is the settled house
style since Phase 33" claim directly against the file. Phase 61's bullets, each backed by a real
REQ-ID (PATH-01, IMG-04..07, MSG-01..05), should carry the parenthesis form.

### Pattern 2: The `### Verified` section is a comparable, standing three-item list

**What:** `## [0.9.0]`'s `### Verified` (`CHANGELOG.md:136-141`) carries exactly three items across
every recent release: no new runtime dependency, the four `@preview` package versions in lockstep,
and the full-corpus gate remaining fatal-free. `61-CONTEXT.md`'s Claude's Discretion explicitly
allows deferring this section's authorship to v0.9.2 (against the whole 0.9.2 diff) as "the cheaper
default."

**When to use:** Only if the phase's own plan decomposition decides authoring it now is cheaper than
deferring — Phase 61 is not required to write one.

### Pattern 3: SC#4 fence proof — probe twice, at genuinely separated timestamps

**What:** `57-SC4-INVARIANTS.md` and `57-HANDOFF.md` together perform **three** total fence
observations across the phase (`57-BUMP-EVIDENCE.md` obs. 1, `57-SC4-INVARIANTS.md` obs. 2,
`57-HANDOFF.md` obs. 3 — six days then twelve minutes apart). `52-RELEASE-EVIDENCE.md` +
`52-HANDOFF.md` did two, four minutes six seconds apart. CONTEXT.md D-10 asks for "twice at
separated times" for Phase 61 — the Phase 52 two-observation shape, not necessarily Phase 57's
three, is the minimum bar to match.

**Example command block** (from `57-SC4-INVARIANTS.md`, directly reusable):

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ"
git tag -l v0.9.1
git ls-remote --tags origin v0.9.1
gh release list --limit 5
gh run list --workflow=release.yml --limit 5
```

Live-verified this session (v0.9.1 substituted for v0.9.0/v0.8.0 in the precedent commands):

```
$ git tag -l v0.9.1
(no output)
$ git ls-remote --tags origin v0.9.1
(no output)
$ gh release list --limit 5
Release v0.9.0	Latest	v0.9.0	2026-08-22T07:46:15Z
Release v0.8.0		v0.8.0	2026-08-15T03:09:31Z
Release v0.7.1		v0.7.1	2026-08-11T05:34:10Z
Release v0.7.0		v0.7.0	2026-08-03T20:09:13Z
Release v0.6.5		v0.6.5	2026-07-28T20:58:41Z
```

Confirms the fence currently holds: `v0.9.0` (a *prior* milestone) is the latest published release;
no `v0.9.1` tag or release exists locally or on the remote.

### Anti-Patterns to Avoid

- **Copying Phase 52's or Phase 57's "no new `typst_*` config value" assertion forward unexamined.**
  `52-SC4-INVARIANTS.md` explicitly warns against this: Phase 57's own milestone added
  `typst_document_templates` and removed `typst_template_assets`, so the assertion was **not** true
  for that milestone and had to be re-measured, not copied. Phase 61's milestone (v0.9.1) adds zero
  config values per the REQUIREMENTS.md "Out of Scope" table ("Any new `typst_*` config value" —
  explicitly excluded), so the assertion likely *is* true here — but it must be measured fresh
  against `v0.9.0..HEAD` (the actual milestone diff anchor for Phase 61, not `v0.8.0..HEAD`), not
  asserted from either prior phase's document.
- **Treating a `pytest.skip` as evidence.** `tests/test_corpus_gate.py`'s full-corpus gate is
  `@pytest.mark.slow` and skips when the corpus is unavailable — both `52-SC4-INVARIANTS.md` and
  `57-CI-EVIDENCE-RUN3.md` explicitly point to the `Outcome: PASSED` line, not merely "ran without
  error," as the acceptance bar.
- **Restating a green CI run's job list as proof lint/type/test authority is honored, without
  quoting the raw `gh run view ... --json jobs` output.** Every precedent file (`57-CI-EVIDENCE-
  RUN3.md`, `52-SC4-INVARIANTS.md`) transcribes the literal 12-job list; a paraphrase ("all jobs
  passed") is a weaker artifact.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dispatching CI on a branch with no PR | A custom webhook or manual re-trigger | `gh workflow run ci.yml --ref <branch>` | `ci.yml`'s `on:` block is `push: [main, develop]` + `pull_request: [main, develop]` + `workflow_dispatch` (verified `.github/workflows/ci.yml:4-8`) — the milestone branch is in neither push/PR list, so `workflow_dispatch` is the only route without opening a PR (which is itself out of scope, D-02/D-12). |
| Detecting the `phase.complete` REL-09 auto-flip | Manual eyeballing of a diff at close | The checksum-guard pattern (`57-CLOSEOUT-GUARD.md`) | Fired at **five consecutive** release-prep closes per `61-CONTEXT.md` D-10 — a `sha256sum .planning/REQUIREMENTS.md` recorded at phase head, plus a `git diff --name-only -- .planning/REQUIREMENTS.md` re-check at close, is the mechanism every prior phase used successfully. |
| Extracting the release-body-source CHANGELOG section | Hand-copying markdown | `scripts/extract_changelog_section.py` | Already exists, pytest-covered since Phase 41 — but **not invoked this phase** (no `## [0.9.1]` section exists to extract; D-13 names it only as an inheritance record for v0.9.2). |
| Advancing the `typsphinx-doc-translations` pin | A hand-made clone/edit/push | Dispatching that repository's own `update-pin.yml` | `57-RESEARCH.md` § "Pattern 7" confirmed this working live; `61-CONTEXT.md` D-13 explicitly names this as the mechanism to preserve in the handoff, not to execute now. |

**Key insight:** every mechanical piece Phase 61 needs already has a working, previously-exercised
implementation somewhere in `.planning/milestones/{v0.8.0,v0.9.0}-phases/{52,57}-*/`. The work in
this phase is composition and fresh measurement against the current tree, not invention.

## Runtime State Inventory

Not applicable — Phase 61 makes no rename, refactor, or migration change. No stored data,
live-service config, OS-registered state, secrets/env vars, or build artifacts are affected. The
only state this phase writes is documentation (`CHANGELOG.md`'s `## [Unreleased]` block) and
`.planning/`-scoped evidence files.

## Common Pitfalls

### Pitfall 1: Treating REL-09's Phase 61 close as "satisfied enough" and flipping its checkbox

**What goes wrong:** `phase.complete`-family tooling has auto-flipped the release requirement
against its own phase's CONTEXT decision at **five consecutive** release-prep closes (per
`61-CONTEXT.md` D-10/D-08, and independently corroborated by `57-CLOSEOUT-GUARD.md`'s "four
consecutive" count one milestone earlier — the count has grown by one each time this project closes
a prep-only phase).

**Why it happens:** Generic close-tooling likely pattern-matches "the phase named in a requirement's
Traceability row completed" and flips the checkbox, without reading the phase's own CONTEXT.md for
an explicit "stays `[ ]`" instruction.

**How to avoid:** Record `sha256sum .planning/REQUIREMENTS.md` and the exact byte content of REL-09's
checkbox line + Traceability row **at phase head**, before any plan runs. Re-verify both at phase
close. If either the checksum has moved or `git diff --name-only -- .planning/REQUIREMENTS.md` shows
a change touching those specific lines, revert by hand (`git checkout -- .planning/REQUIREMENTS.md`)
and report it — do not commit the flip.

**Warning signs:** A closing `git status` or `git diff` that includes `.planning/REQUIREMENTS.md` at
all, when no plan in this phase's own task list should ever touch that file.

### Pitfall 2: Reusing a stale CI run instead of dispatching fresh

**What goes wrong:** Citing the Phase 60 close's CI run (`33252336287`, headSha `130f614e`) as this
phase's own SC#3 evidence, on the reasoning that "nothing under `typsphinx/` has changed since."

**Why it happens:** The reasoning is *almost* correct — this session confirmed zero commits under
`docs/source/` or `CHANGELOG.md` have landed since `130f614e` either — but D-09 is explicit: "SC#3's
whole point is that the green is observed here, not inherited," and CI has never run against a tree
that includes this phase's own CHANGELOG edit.

**How to avoid:** Dispatch fresh, on the tip that **includes** the authored `## [Unreleased]`
bullets. `git log --oneline 130f614e..HEAD` returning nothing (verified this session — the four
commits since are documentation-only) proves the *pre-Phase-61* tree is unchanged, not that
Phase 61's own work has been through CI.

**Warning signs:** A plan's evidence file that quotes run `33252336287`'s job list without also
recording a *new* run id for this phase's own tip.

### Pitfall 3: Confusing the docs-warning-baseline reuse with skipping the doc build entirely

**What goes wrong:** Reading D-09's "against their measured warning baselines" language as licence
to skip running `tox -e docs-html` / `tox -e docs-pdf` this phase, since the baseline (3/5) is
already known and unchanged.

**Why it happens:** The baseline being *stable* (unchanged since Phase 56/57) is easy to conflate
with the build being *unnecessary* this phase.

**How to avoid:** The `## [Unreleased]` bullets are new prose reaching a published docs page via
`docs/source/changelog.rst`'s `.. include::` (verified `docs/source/changelog.rst:1-2`). A malformed
MyST bullet (bad nesting, an unescaped special character) is exactly the kind of defect that shows up
as a *new* docs-build warning. `57-GREEN-TREE-EVIDENCE.md`'s own "Baseline comparison" section
explicitly re-ran both `tox` environments post-CHANGELOG-edit and compared the counts (3 and 5) to
the recorded baseline, rather than skipping the run because the baseline was already known.

**Warning signs:** An evidence file that states the baseline numbers without also transcribing a
literal `build succeeded, N warnings` line from a build run **after** this phase's own CHANGELOG
edit landed.

### Pitfall 4: Writing `61-HANDOFF.md` in the standing "here is what to publish now" voice

**What goes wrong:** Following the Phase 46/52/57 `*-HANDOFF.md` template mechanically produces a
document whose first line assumes a publish is imminent — the seven-milestone habit CONTEXT.md's
specific-idea #3 calls out.

**Why it happens:** Every prior `*-HANDOFF.md` this project has produced opens with "This document
is the standalone publish checklist `/gsd-complete-milestone` reads for this milestone" followed
immediately by checklist items 1-6 (open PR, push tag, watch release workflow, ...) — because every
prior milestone *did* publish.

**How to avoid:** D-12/D-13 require the opening line to state the negative explicitly: this
milestone's `/gsd-complete-milestone` performs no tag, no PyPI publish, no GitHub Release; the
checklist that follows is an **inheritance record** for the v0.9.2 release-prep phase, with the
version left as a placeholder rather than hard-coded.

**Warning signs:** A `61-HANDOFF.md` draft whose "Checklist" section reads as if `Owner:
/gsd-complete-milestone` items are to be executed at *this* milestone's close.

## Code Examples

### The exact CI dispatch-and-capture sequence (verified working, Phase 57 and Phase 60 both used
this shape)

```bash
# 1. Ensure uv.lock is current BEFORE dispatch (D-13 AMENDED sequencing constraint — 10
#    `--locked` steps across ci.yml/release.yml/docs.yml/drift.yml; a stale lock fails every job
#    at `uv sync --locked` before any test/lint/type signal exists)
uv sync --extra dev --locked   # confirm no lockfile drift; if it drifts, regenerate and commit first

# 2. Push the current branch (already on origin per this session's `git status -sb` check —
#    "ahead 2" of origin/gsd/v0.9.1-windows-path-correctness)
git push origin gsd/v0.9.1-windows-path-correctness

# 3. Dispatch — the branch is not in ci.yml's push/PR trigger list, so this is the only route
gh workflow run ci.yml --ref gsd/v0.9.1-windows-path-correctness

# 4. Capture the run id
gh run list --workflow=ci.yml --branch gsd/v0.9.1-windows-path-correctness --limit 1

# 5. Wait for completion
gh run watch <run-id>

# 6. Record full job-conclusion list verbatim (do not paraphrase)
gh run view <run-id> --json jobs --jq '.jobs[] | "\(.conclusion)\t\(.name)"'

# 7. Confirm both windows-latest lanes specifically
gh run view <run-id> --json jobs --jq '.jobs[] | select(.name | contains("windows-latest"))'
```

Source: `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE-RUN3.md`
lines 32-97; `.planning/phases/60-.../60-05-PLAN.md` lines 268-273 (identical shape, independently
authored).

### The 12-job census this project's CI matrix always produces

Verified directly against `.github/workflows/ci.yml` this session (job names extracted from the
workflow file itself, not inferred from a run transcript):

```
test:        Test Python 3.12 on ubuntu-latest / windows-latest / macos-latest   (x2 python vers. = 6)
lint:        Lint and Format Check                                               (1)
type-check:  Type Check                                                          (1)
coverage:    Code Coverage                                                       (1)
build:       Build Package                                                       (1)
integration: Integration Test - basic / Integration Test - advanced              (2)
                                                                        TOTAL = 12
```

Source: `.github/workflows/ci.yml` (job/matrix definitions, read directly this session).

### The `REQUIREMENTS.md` closeout-guard pattern, exact form

```bash
# At phase head — before any plan runs
sha256sum .planning/REQUIREMENTS.md
grep -n 'REL-09' .planning/REQUIREMENTS.md
# record both verbatim in {padded_phase}-CLOSEOUT-GUARD.md

# At phase close — re-run identically
sha256sum .planning/REQUIREMENTS.md   # compare byte-for-byte against the recorded baseline
git diff --name-only -- .planning/REQUIREMENTS.md   # expect: no output
grep -n 'REL-09' .planning/REQUIREMENTS.md   # expect: byte-identical to the recorded quote
```

Live-run this session (current, unmodified tree — for the planner's reference, not as this phase's
own final baseline, since a plan will re-record it at its own phase-head moment):

```
$ sha256sum .planning/REQUIREMENTS.md
4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1  .planning/REQUIREMENTS.md

$ grep -n 'REL-09' .planning/REQUIREMENTS.md
127:- [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
206:| REL-09 | Phase 61 | Pending |
220:Phase 60 → 4 (MSG-02, MSG-03, MSG-04, MSG-05) · Phase 61 → 1 (REL-09).
```

Source: `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-CLOSEOUT-GUARD.md`
(the mechanism); values on the right are this session's own live measurement against the current
tree, verified via `Bash` this session.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Every release-prep phase performs a version bump and prepares a publish | This phase performs neither — a milestone can close without publishing if the owner judges the release not worth making | This session (Phase 61, D-01/D-02) | First time in this project's 11-milestone history (v0.6.2 through v0.9.0 tracked in STATE.md) that a milestone's final phase does not lead directly to `/gsd-complete-milestone` publishing. `61-HANDOFF.md` must therefore invert the standing template rather than adapt it (Pitfall 4 above). |
| `phase.complete` auto-flip caught at "four consecutive" release-prep closes (Phase 57's own count) | Now "five consecutive" per `61-CONTEXT.md` D-10 | This session | The pattern has not been fixed at the tooling level across two more milestones; the checksum-guard mitigation remains the only defense, and it must be applied here too. |

**Deprecated/outdated:** Nothing else in the toolchain moved — `tox`, `uv`, `gh`, and
`scripts/extract_changelog_section.py` are all identical in mechanics to the Phase 57 precedent.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The docs-warning baseline (3 for `docs-html`, 5 for `docs-pdf`) remains valid at the moment this phase's plans actually execute (some time after this research was written). | Summary; Pitfall 3 | If a plan lands between this research and phase execution that touches `docs/source/` or introduces a new docstring warning, the baseline would need re-measurement before comparison — but this is self-correcting: the plan's own fresh `tox -e docs-html`/`docs-pdf` run is the actual evidence, and any drift from 3/5 would be visible and explainable at that point, not silently accepted. |
| A2 | No plan in this phase will need a second CI dispatch (D-09's default: one dispatch is sufficient absent a mid-phase code-affecting change). | Pattern 3 / Code Examples | If a plan discovers it must touch a test file's assertion in a way that is itself code-affecting (unlikely — this phase's fence excludes `typsphinx/` changes absolutely, per CONTEXT `<domain>` "Out of scope"), a second dispatch would be needed; D-09 already anticipates and permits this. |

**On the empty table convention:** two items remain because they are genuinely time-dependent
(baseline currency, dispatch count) rather than because they were unverified — every other claim in
this document is `[VERIFIED: <path>]` or a direct `[CITED: 61-CONTEXT.md]` quote.

## Open Questions

1. **Whether a milestone-diff sweep (Phase 52/57's `*-SC4-INVARIANTS.md` shape) is worth running
   given no `### Verified` claims are authored this phase.**
   - What we know: CONTEXT.md leaves this to Claude's Discretion explicitly, noting that if one is
     run, its positive control must be real (an assertion that would fail if the sweep were
     vacuous) — following the `52-SC4-INVARIANTS.md` precedent, which added exactly such controls
     after `46-SC4-INVARIANTS.md` had none.
   - What's unclear: whether SC#4's fence proof (which is retained in full, D-10) requires the
     milestone-invariant sweep (no new dependency / `@preview` lockstep / no new config value) as
     a *component* of the fence proof, or whether the fence proof is narrower (just the
     tag/publish/`typsphinx/`-diff/checksum items D-10 lists explicitly, with no mention of the
     three milestone invariants).
   - Recommendation: re-read D-10's own wording closely at planning time — it lists four items
     (tag probe, no-publish probe, `git diff` on `typsphinx/`, `REQUIREMENTS.md` checksum) and does
     **not** mention the dependency/`@preview`/config-value invariants by name, unlike Phase 57's
     D-15, which explicitly separated "SC#4 is a fence criterion" from the milestone-diff sweep
     that backed `### Verified`. Since Phase 61 authors no `### Verified` section (Discretion item),
     the milestone-diff sweep this phase may skip entirely is likely optional — but the planner
     should confirm this reading against D-10's literal text rather than defaulting to "always run
     it because Phase 52/57 did."

2. **Where exactly the two SC#4 fence-probe observations should sit relative to each other in
   time**, given this phase (unlike Phase 57's near-week span) is likely to execute in a single
   session.
   - What we know: Phase 52's two observations were 4 minutes 6 seconds apart; Phase 57's three
     spanned nearly six days then twelve minutes.
   - What's unclear: whether a same-session, few-minutes-apart gap (the Phase 52 shape) is
     sufficient "separated times" for this phase, or whether the planner should deliberately place
     the two probes in different plans/waves to force a larger gap.
   - Recommendation: the Phase 52 precedent (minutes apart, both plans in the same phase) already
     satisfied "twice at separated times" for that phase's own verifier — treat that as the floor,
     not as insufficient.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI | CI dispatch, run inspection, tag/release probes | Yes — verified this session (`gh run list`, `gh release list`, `git ls-remote` all returned live data) | not queried explicitly, but functional | — |
| `uv` / `tox` | Full pytest, lint, type, docs builds | Yes — every prior phase in this milestone (58, 59, 60) used this successfully per `CLAUDE.md`'s worktree-isolated execution section | project-pinned | — |
| `ruff` (local) | Lint gate | Historically flaky on this maintainer's NixOS host (`QUA-06`, `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`) — re-measured working at the Phase 57 close (2026-08-16) but **reproduced broken again** at that same phase's own later re-check (2026-08-22, `57-HANDOFF.md`'s pending-todo table). Environment-dependent. | Uncertain, alternates | — | CI holds lint authority per standing project convention (`CLAUDE.md`, D-13's original reasoning) — a local `ruff` failure does not block this phase; CI's `Lint and Format Check` job is authoritative. |
| Network access to `github.com` (for `gh` CLI, workflow dispatch) | CI dispatch, fence probes | Yes — verified this session (live `gh run list`/`gh release list` calls succeeded against the real remote) | — | — |

**Missing dependencies with no fallback:** none identified.

**Missing dependencies with fallback:** `ruff` local execution — CI is the standing fallback
authority, already the accepted pattern across Phases 57-60.

## Validation Architecture

`workflow.nyquist_validation` is not set to `false` in `.planning/config.json` (not overridden), so
this section is required per the standing instruction. Note this phase's "validation" is process
verification (green-run proof, fence proof) rather than product-behavior testing — there is no new
`typsphinx/` code this phase, so there are no new unit/integration tests to write. The "tests" this
phase's REQ (implicitly, via SC#3) maps to are the existing suite run in full, plus the docs builds,
plus CI.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (config in `pyproject.toml`), orchestrated via `tox` |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]`; `tox.ini` `env_list = py312, py313, lint, type, cov, docs` |
| Quick run command | `uv run pytest -m "not slow"` |
| Full suite command | `uv run pytest` (full suite, including `@pytest.mark.slow` corpus gate) |

### Phase Requirements → Test Map

Phase 61 satisfies REL-09's *substance* (per D-11's mapping) not by writing new tests, but by
re-running the existing suite and recording live evidence. There is no per-REQ-ID unit test to write
this phase — REL-09 remains formally unmet ([ ], D-08) and no plan targets it directly.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-09 (substance, not the literal text — D-11) | The milestone-final tree passes the full test/lint/type/docs/CI bar | full-suite + CI | `uv run pytest`, `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/`, `uv run tox -e docs-html`, `uv run tox -e docs-pdf`, `gh workflow run ci.yml --ref <branch>` | ✅ — all commands and configs already exist; no Wave 0 gap |

### Sampling Rate

- **Per task commit:** N/A in the usual sense — this phase's "tasks" mostly *are* the full-suite
  runs (there is no incremental unit of product code to gate per-commit).
- **Per wave merge:** full `uv run pytest` + lint/type trio.
- **Phase gate:** the 3-OS CI dispatch (`gh workflow run ci.yml`), both `windows-latest` lanes green,
  is the milestone's own acceptance bar (REQUIREMENTS.md § "Standing constraints" #6), observed here
  per D-09.

### Wave 0 Gaps

None — existing test infrastructure (full pytest suite, `tox` lint/type/docs environments,
`ci.yml`'s 3-OS matrix) covers everything this phase needs to prove. No new test file, fixture, or
framework install is required.

## Security Domain

`security_enforcement` is not explicitly `false` in `.planning/config.json`, so this section is
included per the standing instruction — but this phase introduces no new attack surface: no new
input parsing, no new authentication/authorization path, no new cryptography, no new external-facing
endpoint. It edits a markdown file (`CHANGELOG.md`) and writes planning documents.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | This phase touches no auth surface. |
| V3 Session Management | No | Not applicable — no runtime session code. |
| V4 Access Control | No | Not applicable. |
| V5 Input Validation | No (marginal) | The only "input" this phase produces is prose in `CHANGELOG.md`, rendered by `myst_parser` into published HTML/PDF — a docs-build warning (already gated, see Pitfall 3) is the only failure mode, not a security defect. |
| V6 Cryptography | No | Not applicable. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A malformed CHANGELOG bullet publishing broken markup to Read the Docs | Tampering (of published content, self-inflicted) | The docs-warning-baseline comparison (3/5) this phase's SC#3 already performs is the mitigation — a malformed bullet surfaces as a new warning before it reaches a published surface. |
| Accidentally committing an irreversible action (a real `git tag v0.9.1` push, or triggering `release.yml`) | Tampering / Elevation of privilege (of the release pipeline) | The fence proof itself (tag/publish probes twice, D-10) is the mitigation, plus the standing project discipline that opening a PR or pushing a tag is explicitly out of scope for a prep-only phase (`61-CONTEXT.md` `<domain>` "Out of scope"). |

## Sources

### Primary (HIGH confidence — direct file reads and live command output this session)

- `.planning/phases/61-v0-9-1-release-prep-prep-only/61-CONTEXT.md` — full read, all 13 decisions
  and both discretion/deferred sections.
- `.planning/REQUIREMENTS.md` — full read, REL-09's exact text, traceability table, standing
  constraints.
- `.planning/STATE.md` — partial read (lines 1-586), Phase 60 close record, milestone history.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-CONTEXT.md` — full read.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-SC4-INVARIANTS.md` — full
  read.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-CLOSEOUT-GUARD.md` — full
  read.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-HANDOFF.md` — full read.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-CI-EVIDENCE-RUN3.md` —
  partial read (lines 1-120).
- `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-SC4-INVARIANTS.md` — full
  read.
- `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-HANDOFF.md` — full read.
- `CHANGELOG.md` — full head read (lines 1-50), tail read, and the `## [0.9.0]` `### Fixed` /
  `### Removed` / `### Verified` sections (lines 81-141).
- `docs/source/changelog.rst` — lines 1-10 read directly.
- `.github/workflows/ci.yml` — job/matrix structure read directly (grep against the live file).
- `.github/workflows/links.yml` — the `CHANGELOG.md` exclusion, read directly.
- `tests/test_changelog_page_gate.py` — `RELEASE_VERSIONS` tuple, lines 45-66, read directly.
- Live `gh`/`git` commands this session: `git log --oneline 130f614e..HEAD -- docs/source
  CHANGELOG.md` (empty), `git tag -l v0.9.1` (empty), `git ls-remote --tags origin v0.9.1` (empty),
  `gh release list --limit 5`, `gh run list --workflow=ci.yml --branch
  gsd/v0.9.1-windows-path-correctness --limit 5`, `sha256sum .planning/REQUIREMENTS.md`, `grep -n
  'REL-09' .planning/REQUIREMENTS.md`.
- `.planning/phases/60-one-delimiter-aware-path-quoting-helper-routed-everywhere/60-VERIFICATION.md`
  and `60-05-SUMMARY.md`/`60-05-PLAN.md` — the CI run `33252336287` provenance and the exact `gh`
  dispatch-and-capture command sequence.

### Secondary (MEDIUM confidence)

None used — every claim in this document traces to a primary source above.

### Tertiary (LOW confidence)

None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new tooling; every command verified against a working precedent this
  session.
- Architecture (evidence-file naming, CHANGELOG authoring shape): HIGH — direct reads of the Phase
  52/57 precedent files, plus a direct read of `CHANGELOG.md`'s own `## [0.9.0]` section for house
  style.
- Pitfalls: HIGH — each pitfall is drawn from an explicitly documented, previously-occurring
  incident (the phase.complete auto-flip, five times; the docs-warning-baseline comparison Phase 57
  actually performed) rather than speculation.
- Docs warning baseline currency: HIGH — verified via a live `git log` check this session that zero
  commits touched `docs/source/` or `CHANGELOG.md` since the Phase 60 CI-authority commit.

**Research date:** 2026-08-29
**Valid until:** This research is anchored to a specific commit (`e51e2be1`) and a specific CI run
(`33252336287`). If any commit lands under `docs/source/`, `CHANGELOG.md`, or `typsphinx/` before
this phase's plans execute, the docs-warning baseline and the "zero intervening commits" claims
(Pitfall 2/3) must be re-verified. Otherwise valid for the life of this phase (no external
time-decay component — no third-party API or library version is at risk of moving).
