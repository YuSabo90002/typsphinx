# Phase 63: v0.9.2 Release Prep (prep-only) - Research

**Researched:** 2026-08-30
**Domain:** Release-prep process (CHANGELOG curation, version-literal lockstep, live-run proof,
irreversible-action fencing) — not product code. No `typsphinx/` behaviour changes in this phase.
**Confidence:** HIGH — every claim below was either read from the live tree this session, executed
as a live command this session, or copied verbatim from `63-CONTEXT.md`'s already-measured D-01..D-21
(which this research re-verified selectively rather than re-deriving), plus a full read of the two
closest precedent phases (`61-*` and `57-*`).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

The owner selected "おすすめ" — all four presented gray areas were delegated at once. Every decision
below is Claude's measured recommendation, accepted en bloc, grounded in a measurement taken during
`/gsd-discuss-phase` against the tree at `dd385436`. Reproduced verbatim from `63-CONTEXT.md`
`<decisions>` (headings retained):

#### The `## [0.9.2]` CHANGELOG entry

- **D-01: The entry opens with a lead paragraph.** Measured across the whole file: every one of the
  last nine released sections — `0.6.1`, `0.6.2`, `0.6.3`, `0.6.4`, `0.6.5`, `0.7.0`, `0.7.1`,
  `0.8.0`, `0.9.0` — opens with one. The closest structural analog is **`## [0.6.5]`**
  (`CHANGELOG.md:381`): a hotfix patch release whose entire content is one compile-blocking
  *separator* defect in `typsphinx/translator.py` (MATH-01) — the same defect class as this
  milestone's IMG-08. Its lead paragraph names the defect, scopes the runtime change to the
  translator, and states "Zero new runtime dependencies; the bundled `@preview` version-sync surface
  is untouched." That is the model to follow. — **Reversibility:** reversible.
- **D-02: The lead paragraph never names "0.9.1".** The entry describes the Windows-path work as
  part of 0.9.2's own content, with no reference to a version that was completed but never
  published. Naming a version a user cannot install, in a document published on Read the Docs via
  `docs/source/changelog.rst:1-2`, contradicts PROJECT.md's core value that a URL the project
  publishes must actually resolve — the same reasoning that produced 61-CONTEXT D-01/D-04. This is
  the prose counterpart of REQUIREMENTS.md's binding ban on a `## [0.9.1]` heading and a `[0.9.1]`
  tail link. — **Reversibility:** reversible.
- **D-03: The inline-image blocker leads the `### Fixed` list; the three path bullets follow in the
  roadmap's own order** (PATH-01 → IMG-04..IMG-07 → MSG-02..MSG-05). Rationale, measured: the image
  defect refuses **every master** of any project containing an image anywhere but first in its
  container — including masters with no image at all, because Typst's `#include()` re-parses the
  included content file (ROADMAP constraint 2, proven by 62's 17-red/1-green aggregate
  `ExtensionError`). Its blast radius is platform-independent and unconditional; the path family's
  is Windows-shaped paths plus any path containing a quote character. Broader blast radius leads.
  — **Reversibility:** reversible.
- **D-04: The three existing `## [Unreleased]` bullets are promoted verbatim, not rewritten.**
  Measured: `CHANGELOG.md:10-36` holds exactly three `### Fixed` bullets (PATH-01;
  IMG-04..IMG-07; MSG-02..MSG-05), authored in Phase 61 specifically for this promotion
  (61-CONTEXT D-03, `61-CHANGELOG-EVIDENCE.md`, 61-HANDOFF § "What v0.9.2 must also pick up"). They
  are already published on RTD `latest`. Rewriting them would create a gratuitous diff between what
  readers already saw and what the release says. The only permitted edit is trimming a clause the
  new lead paragraph makes literally redundant — never re-deriving a technical claim.
  **Specifically preserved:** the MSG bullet's explicit statement that a POSIX path containing an
  apostrophe was affected too (60-CONTEXT D-01 AMENDED: `quote_path()` closes an apostrophe by
  **doubling** it). A lead paragraph calling this release "Windows fixes" would be inaccurate.
  — **Reversibility:** reversible.
- **D-05: One new `### Fixed` bullet is authored for the image separator, citing IMG-08, IMG-09 and
  IMG-10 in trailing parentheses** (house style since Phase 33). It must describe the user-visible
  shape, not the mechanism: an image node preceded by any sibling content in the same container was
  emitted adjacent to the preceding code-mode expression, so Typst refused the file with
  `expected semicolon or line break` and `-b typstpdf` raised `ExtensionError` and wrote **no PDF
  for any master document in the project**. The sixteen container shapes may be summarized
  ("mid-sentence, in a list item, a table cell, a definition-list body, an admonition, a footnote, a
  field-list body, a section title, or a figure's legend") rather than enumerated.
  — **Reversibility:** reversible.
- **D-06: A `### Verified` subsection is written.** Measured: `### Verified` appears in **nine
  consecutive** released sections — `0.6.1` through `0.9.0` without a single gap. Three bullets,
  each backed by a run recorded in this phase's or Phase 62's evidence — **never carried forward on
  prose**: (1) zero new runtime **and** dev dependencies across the `v0.9.0..HEAD` diff; (2) the four
  bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`); (3) the 16
  previously-failing and 9 must-keep-passing image shapes bound by a real `typst.compile()` gate
  (TEST-05), 18/18 masters compiling. **Explicit warning to the planner:** prior entries' third
  bullet is "The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free." Do
  **not** copy that sentence unless this phase actually runs that corpus — it does not, and D-06
  substitutes a claim this milestone did measure. — **Reversibility:** reversible.
- **D-07: The section vocabulary is `### Fixed` and `### Verified` only.** No `### Added`,
  `### Changed`, `### Removed`, `### Known Limitations`. This is `0.6.5`'s exact shape.
  — **Reversibility:** reversible.

#### How loudly the published-0.9.0 blocker is named

- **D-08: The disclosure is one sentence in the `## [0.9.2]` lead paragraph, and nothing else.** It
  states plainly that a project built with 0.9.0 whose document places an image anywhere but first
  in its container produced no PDF for any master, and that 0.9.0 users should upgrade.
  — **Reversibility:** reversible.
- **D-09: `README.md` is not touched beyond its Status line.** Measured: `README.md:289`'s
  `## Known Limitations` list still holds exactly its two original entries (Bibliography,
  Citations). The only `README.md` edit in this phase is `README.md:347`'s
  `**Status**: Stable (v0.9.0) - Production ready` → `v0.9.2`, which SC#1 requires and
  `tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject` enforces.
  — **Reversibility:** reversible.
- **D-10: No GitHub Security Advisory, no PyPI yank of 0.9.0, no README banner.** Each is an
  outward-facing irreversible action and is excluded by the phase's own fence. Recorded as a
  deferred idea. — **Reversibility:** n/a (a non-action).

#### Guard surfaces around the release

- **D-11: `RELEASE_VERSIONS` gains `"0.9.2"`.** Measured: `tests/test_changelog_page_gate.py:50-66`
  currently ends at `"0.9.0"`; the two build classes assert that **every** listed version string
  appears in the rendered `changelog.html` (line 170) and in the compiled changelog PDF (line 251).
  Precedent measured in `git log`: `dcee0201 feat(57-03): roll over CHANGELOG tail block, extend
  page-gate coverage`, `0c784c48 test(52-02): extend RELEASE_VERSIONS to 14 entries through 0.8.0`,
  `075c07d0 test(46-03): extend RELEASE_VERSIONS to 0.7.1`. The tuple's preceding comment ("The 15
  releases the published page was frozen without (0.4.4 through 0.9.0, inclusive)") is updated in
  the same edit. — **Reversibility:** reversible.
- **D-12: A `Migrating from 0.9.0 to 0.9.2` guide is NOT written.** There is no guide for `0.6.5` —
  the one prior patch release with no breaking change. 0.9.2 breaks nothing.
  — **Reversibility:** reversible.

#### The handoff, and REL-04

- **D-13: `63-HANDOFF.md` follows `61-HANDOFF.md`'s structure with `vX.Y.Z` resolved to `v0.9.2`,
  but opens by stating the POSITIVE.** 61's first line stated the negative precisely because that
  was the anomaly; restoring the standing shape is the correction. The three inherited steps are
  carried in full: the `typsphinx-doc-translations` `update-pin.yml` **dispatch** (a manual dispatch
  — not a side effect of the parent repo's tag push, and advancing the pin and tagging that repo are
  two separate steps); the Read the Docs `en` (`typsphinx`) and `ja` (`typsphinx-ja`) `stable`
  measurement (unauthenticated public API calls); and the GitHub Release body being byte-identical
  to `scripts/extract_changelog_section.py 0.9.2`'s stdout. — **Reversibility:** reversible.
- **D-14: REL-04 is re-offered as a named pre-flight/post-flight observation inside
  `63-HANDOFF.md` — not folded into any plan, and not promoted to a requirement.** Must record four
  things: (a) `release.yml`'s `create-release` job carries explicit `Install uv` steps at HEAD and
  ran green at the **v0.8.0 and v0.9.0 real tag pushes**, so a failure now would be a regression;
  (b) the exact observation to make (`gh run watch` on the release run, then that job's conclusion
  read literally); (c) the response if it fails — fix it inside this release work and re-run the
  job, do not defer; (d) that
  `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` stays in
  `pending/` and is closed only by an observed green `create-release` on a real tag push, which does
  not happen in this phase. — **Reversibility:** reversible.
- **D-15: The `pypi` GitHub Environment's manual approval is named as an EXPECTED gate, in the
  operator's own reading order.** Must be named before the step that triggers it, because a paused
  workflow looks exactly like a failed one to an operator scanning `gh run list`.
  — **Reversibility:** reversible.

#### Mechanics that bind every plan

- **D-16: The fence is `63-CLOSEOUT-GUARD.md`, reusing `61-CLOSEOUT-GUARD.md`'s procedure
  verbatim.** `sha256sum .planning/REQUIREMENTS.md` + `wc -l` + `git rev-parse HEAD` +
  `grep -n 'REL-09' .planning/REQUIREMENTS.md` recorded at phase head; the same commands re-run and
  compared at phase close; **and once more after `phase.complete`-family tooling has run** — that
  third observation is the one that actually catches the flip, because it runs outside any plan's
  reach. The flip is **reverted and reported, never accepted and never committed**
  (`git checkout -- .planning/REQUIREMENTS.md`). Every plan's `SUMMARY.md` frontmatter declares
  `requirements-completed: []` for REL-09 — the v0.9.1 audit found three of Phase 61's four plans
  declaring `[REL-09]` and contradicting the correctly-unmet checkbox. REL-09's state is read
  directly out of `.planning/REQUIREMENTS.md` as `[ ]` at close, never inferred from frontmatter.
  — **Reversibility:** reversible.
- **D-17: `uv lock` runs and is committed BEFORE the CI dispatch.** Every CI job begins with
  `uv sync --extra dev --locked`. Measured now: `uv.lock:1467` reads `version = "0.9.0"` for the
  self-package, independent of `pyproject.toml:7`. Dispatching before regenerating would reproduce
  the exact refusal already killing every dependabot PR, and it would fail at the *install* step of
  `release.yml`'s `validate`/`build` jobs on the real tag push, before any test runs. `uv.lock` is
  regenerated with `uv lock` and **never hand-edited**. — **Reversibility:** reversible.
- **D-18: One CI dispatch, on the phase's final tip, after the bump commit.** Phase 57 ran two
  (pre-bump and post-bump); Phase 61 ran one, since it had no bump to split around. SC#4 names "the
  **bumped** tip", and this phase's only code-affecting change is D-11's one-tuple test edit which
  lands with the release work — so one dispatch on the last commit is the default.
  `gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release`, waited to
  **completion**, with both `windows-latest` lanes and `macos-latest` named individually and every
  job conclusion transcribed literally. `ruff`'s verdict is taken from that run's `Run linters`
  step — never from this machine, where `ruff` is an unrunnable generic-linux ELF in any freshly
  `uv sync`-provisioned worktree venv. A plan that lands a second code-affecting change mid-phase
  adds a second dispatch; that is the only justification for one. — **Reversibility:** reversible.
  **⚠️ Research correction — see `## Contradictions Found` below: `ci.yml` has no step literally
  named "Run linters"; that name belongs to `release.yml`, which this phase must not trigger. The
  correct source in `ci.yml` is the `lint` job ("Lint and Format Check"), whose "Run lint with tox"
  step runs `black --check .` then `ruff check .`.**
- **D-19: Evidence files follow `61-*`'s naming set exactly, and `63-VERIFICATION.md` is
  forbidden.** `{padded_phase}-VERIFICATION.md` is `gsd-verifier`'s reserved output name and a
  plan-authored file there is clobbered at verify time. Suggested set, mirroring Phase 61's:
  `63-CLOSEOUT-GUARD.md`, `63-CHANGELOG-EVIDENCE.md`, `63-GREEN-TREE-EVIDENCE.md`,
  `63-CI-EVIDENCE.md`, `63-SC5-INVARIANTS.md`, `63-HANDOFF.md`. — **Reversibility:** reversible.
- **D-20: The extractor's stdout is transcribed verbatim into `63-CHANGELOG-EVIDENCE.md`, with
  three named greps recorded beside it.** `scripts/extract_changelog_section.py`'s
  `_SECTION_HEADER_RE` matches **every** `## [...]` heading and the algorithm is purely positional —
  first heading naming the requested version, everything up to the next heading of any name. So the
  scratch block at `CHANGELOG.md:38` (`### Planned for Future Releases`) must be relocated under a
  fresh empty `## [Unreleased]` placed **above** `## [0.9.2]` **before** the rename, or it lands
  verbatim in the published GitHub Release body. The three greps: no `## [0.9.1]` heading anywhere;
  no `[0.9.1]:` tail link anywhere; no `Planned for Future Releases` line inside the extracted body.
  REL-10 is closed by reading the script's stdout, not by reasoning that the edit was correct.
  — **Reversibility:** reversible. **Confirmed by this research: `_SECTION_HEADER_RE` (line 59) is
  `r"^## \[(?P<version>[^\]]+)\]"`, matched against every line with no name filtering — the
  purely-positional claim is `[VERIFIED: scripts/extract_changelog_section.py:54-59, 87-116]`.**
- **D-21: The docs warning baseline is taken from a clean build.** `rm -rf docs/_build` before each
  of `tox -e docs-html` and `tox -e docs-pdf`. An incremental rebuild under-reports warnings and
  manufactures a false "baseline match". — **Reversibility:** reversible.

### Claude's Discretion

The owner delegated all four presented gray areas at once ("おすすめ"). Every D-01..D-21 above is
Claude's recommendation. Planning may refine:

- Plan decomposition, ordering and wave assignment; which plan owns which evidence file.
- The exact prose of the lead paragraph and of every CHANGELOG bullet, subject to D-02 (never name
  0.9.1), D-04 (promote verbatim), D-06's warning (no unmeasured `### Verified` claim) and the
  measured framing constraint that this is not a Windows-exclusive fix.
- The mechanical form of the checksum guard and where the two separated SC#5 fence probes are
  recorded — subject to SC#5's requirement that the two observations be separated by **intervening
  waves**, not by wall-clock luck, and that each remote probe carry a **positive control** (an
  assertion that would fail if the probe were vacuous).
- Whether a milestone-diff sweep anchored at the `v0.9.0` tag backs D-06's bullets 1 and 2, or
  whether targeted greps suffice. If a sweep is run, its positive control must be real.
- The heading structure of `63-HANDOFF.md`, provided D-13's positive opening, D-14's four REL-04
  items and D-15's approval-gate note all survive.

Planning may **not** weaken D-02 (no `0.9.1` in prose), D-07 (`### Fixed` + `### Verified` only),
D-16 (the three-observation fence and `requirements-completed: []`), D-17 (`uv lock` before
dispatch), or D-19 (the `63-VERIFICATION.md` ban) without returning to the owner.

### Deferred Ideas (OUT OF SCOPE)

- **A GitHub Security Advisory, a PyPI yank of 0.9.0, or a README upgrade banner** for the blocker
  live in the published 0.9.0. Offered and declined for this phase by D-10.
- **A `Migrating from 0.9.0 to 0.9.2` guide.** Declined by D-12.
- **Running the full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run** so that D-06's third
  `### Verified` bullet could reuse the wording nine prior releases used. Not adopted.
- **Folded Todos:** none. All eight todos matched by `todo.match-phase 63` were reviewed and left in
  `.planning/todos/pending/` (see `63-CONTEXT.md` § "Reviewed Todos (not folded)" for the full list
  and disposition of each: REL-04, CI-01, MSG-06, NUM-01, QUA-09, QUA-08, QUA-10, DOC-18).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-09 | 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, version bumped as sole literal in `pyproject.toml` with `uv.lock`/`README.md` in lockstep, GitHub Release body sourced from `scripts/extract_changelog_section.py`. **Carried for coverage only — closes at `/gsd-complete-milestone`, never in this phase.** | `## Code Examples` § "Version-bump command sequence" gives the exact `uv lock` / `uv sync --extra dev --locked` / guard-test sequence, verified against `57-BUMP-EVIDENCE.md`'s live transcript. `## Common Pitfalls` Pitfall 1 and Pitfall 5 cover the two ways this requirement's *coverage-only* nature gets violated (frontmatter mis-declaration, checkbox flip). |
| REL-10 | The "Planned for Future Releases" scratch block is relocated beneath a fresh empty `## [Unreleased]` before the heading becomes `## [0.9.2]`; extractor output is inspected to confirm no leakage. | `## Code Examples` § "The four-step CHANGELOG edit order" gives the exact edit sequence and the three confirming greps, cross-verified against the live `scripts/extract_changelog_section.py` source (`_SECTION_HEADER_RE` is purely positional — confirmed by direct read this session). `## Common Pitfalls` Pitfall 2. |
| REL-11 | REL-09's checkbox is protected by a SHA-256 of `.planning/REQUIREMENTS.md` recorded at release-phase head, re-verified at phase close and at milestone close, following `61-CLOSEOUT-GUARD.md`. | `## Code Examples` § "The closeout-guard fence" reproduces `61-CLOSEOUT-GUARD.md`'s exact command sequence and this session's own fresh cross-check of the current `.planning/REQUIREMENTS.md` (sha256, line count, the three REL-09 grep hits at lines 70/154/175 — see Pitfall 6, the hit shape differs from 61's). |

</phase_requirements>

## Summary

Phase 63 is the ninth prep-only release phase in this project's history (after Phases 10, 41, 46,
52, 57, 61, and two more implicit in the v0.6.x series) but it is structurally closer to **Phase 57**
than to the immediately preceding **Phase 61**: like 57, it performs a real version bump, authors a
real versioned `## [0.9.2]` CHANGELOG section, and runs the extraction script for real. Like 61, its
*total* scope is narrow — a pure release round with no bundled product fixes — so the plan count
should land near 61's four plans across three waves, not 57's eleven plans across four waves (57's
extra bulk was two bundled defect fixes — a Windows path fix and a message-quoting fix — that do not
exist in this milestone; Phase 62 already delivered and gated the only product fix this milestone
needs).

The mechanical work is well-trodden: a one-commit version bump (`pyproject.toml`, `uv.lock`,
`README.md`, `CHANGELOG.md` together, per SC#1), a four-step CHANGELOG edit (relocate scratch block →
rename heading → tail-link roll → run extractor), a `RELEASE_VERSIONS` tuple extension, a live-run
green proof (full pytest, black, mypy, both docs environments off a **clean** build, one dispatched
3-OS CI run), and a two-observation checksum fence around REL-09's checkbox — all with exact command
shapes recoverable from `57-BUMP-EVIDENCE.md`, `57-CHANGELOG-EVIDENCE.md`, `61-CLOSEOUT-GUARD.md`,
and `61-SC4-INVARIANTS.md`, which this research read in full and reproduces below.

This research found and confirms one factual defect in the phase description's own SC#4/D-18
wording: **the CI dispatch's `ruff` verdict cannot be read from a step named "Run linters"**, because
no such step exists in `ci.yml` — that name belongs to `release.yml`'s `validate` job, which this
phase is explicitly forbidden from triggering. See `## Contradictions Found` below; the plan must
read `ruff`'s verdict from `ci.yml`'s `lint` job ("Lint and Format Check"), whose own step is named
"Run lint with tox".

**Primary recommendation:** decompose into 4 plans across 3 waves, closely mirroring Phase 61's wave
shape (wave 1: bump+CHANGELOG plan and closeout-guard-baseline plan, run in parallel; wave 2:
green-tree-and-CI plan, depends on both wave-1 plans; wave 3: fence-observation-2-and-handoff plan,
depends on wave-2 plan) — but insert the `RELEASE_VERSIONS`/`tests/test_changelog_page_gate.py` edit
and its docs-extra proof into the bump+CHANGELOG plan (Phase 57 owned this in a separate plan,
57-03, but Phase 57 had ten other plans contending for wave slots; Phase 63 does not).

## Architectural Responsibility Map

This phase touches no runtime architecture — it is release-surface and process-verification work
only. For completeness, mapped against the tiers the framework asks for:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version-literal lockstep (`pyproject.toml` / `uv.lock` / `README.md`) | Build tooling (`uv`) | — | `uv lock` regenerates the lockfile's self-package stanza from `pyproject.toml`'s literal; `README.md`'s Status line is guarded by a dedicated pytest module, not by build tooling. |
| CHANGELOG content authoring | Documentation / release surface | Docs build (Sphinx via `myst_parser`) | `CHANGELOG.md` is included wholesale into `docs/source/changelog.rst`, so edits there are simultaneously a release artifact and a published docs page — malformed MyST shows up as a docs-build warning, exactly what D-21's clean-build check polices. |
| Live-run green proof (pytest/lint/type/docs/CI) | CI / Build tooling | — | No product-tier component; this is process verification over `.github/workflows/ci.yml` and local `tox` environments. |
| Fence proof (checksum guard, no tag, no publish) | Release machinery (`.github/workflows/release.yml`, `gh` CLI) | Git (`git tag`, `git ls-remote`) | Read-only probes against GitHub's release/tag surface and a read-only checksum comparison; no write action against release infrastructure is taken. |
| Handoff document | Documentation / project planning | — | `63-HANDOFF.md` lives under `.planning/`, not the product tree; it is read by a future `/gsd-complete-milestone` invocation, not by any runtime component. |

## Standard Stack

No new library, package, or runtime dependency is introduced by this phase. All tooling used is
already installed and already exercised by Phases 57/61:

### Core

| Tool | Version (verified this session) | Purpose | Why Standard |
|------|-------------------|---------|---------------|
| `uv` | `0.11.25` (`uv --version`, this session) | Dependency resolution, lockfile regeneration, `uv run`/`uv sync` execution wrapper | Project's sole package manager since inception; `uv lock` is the ONLY sanctioned way to update `uv.lock`'s self-package version (D-17). |
| `gh` (GitHub CLI) | `2.98.0` (`gh --version`, this session) | `workflow_dispatch` CI trigger, `gh run watch`/`gh run view`, `gh release list`, `gh ls-remote`-adjacent probes | Standing tool for every prior release-prep phase's CI dispatch and fence probes. |
| `git` | `2.54.0` (`git --version`, this session) | Tag/remote-tag probes, `git diff` scoping, commit boundary tracking | Standing tool. |
| `tox` (via `uv run tox`) | pinned `tox-uv-bare~=1.35,<2` (`pyproject.toml`) | `docs-html`, `docs-pdf`, `lint`, `type` environment orchestration | Already the project's task runner; `tox -e docs-html`/`docs-pdf` is D-21's clean-build harness. |
| `pytest` | per `pyproject.toml` `[tool.pytest.ini_options]`, `pytest>=8.4,<10` | Full suite, version-sync guard family, `test_changelog_page_gate.py` | Standing test runner; current suite is **1543 passed, 5 skipped** as of Phase 62's close (`62-VERIFICATION.md` line 66) — this is the pre-phase baseline, not this phase's own measurement, and must be re-run fresh. |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `scripts/extract_changelog_section.py` | Extracts a single `## [X.Y.Z]` section body from `CHANGELOG.md`, purely positionally | REL-10's inspection step; also the GitHub Release body's future source at `/gsd-complete-milestone`. |
| `myst_parser` (`docs` extra) | Renders `CHANGELOG.md` (via `.. include::`) into `changelog.rst`'s published HTML/PDF | Required for `tests/test_changelog_page_gate.py`'s two `@pytest.mark.slow` build classes to run at all — see Pitfall 3. |

### Alternatives Considered

Not applicable — this phase makes no library or tool selection decision. Every command shape below
is inherited unmodified from Phases 57 and 61's own established precedent.

**Installation:** none. `uv sync --extra dev` (mandatory per-worktree, per `CLAUDE.md`) provisions
everything the `dev` extra needs; the `docs` extra must be added explicitly wherever the
`RELEASE_VERSIONS` proof is executed — see Pitfall 3.

## Package Legitimacy Audit

Not applicable. This phase installs, adds, or upgrades **zero** packages — D-01/D-06's "zero new
runtime and dev dependencies" claim is exactly what this phase must prove, not violate.
`pyproject.toml`'s `[project.dependencies]` and `[project.optional-dependencies]` blocks are read
by this phase (to confirm the milestone diff added nothing) but never edited.

**Packages removed due to `[SLOP]` verdict:** none — no packages were evaluated for installation.
**Packages flagged as suspicious `[SUS]`:** none.

## Architecture Patterns

### System Architecture Diagram

Not a runtime system — this is a linear release-prep pipeline. Data flow through the phase's own
process:

```
CONTEXT.md (D-01..D-21)
        │
        ▼
[Plan A: bump + CHANGELOG]──────────────┐
  pyproject.toml (hand-edit line 7)     │
  uv lock (regenerates uv.lock)         │
  README.md (hand-edit line 347)        │
  CHANGELOG.md 4-step edit:             │
    1. relocate scratch block           │
       under fresh empty                │
       "## [Unreleased]"                │
    2. rename old heading                │
       "## [Unreleased]" → "## [0.9.2]" │
    3. tail-link roll                    │
    4. run extractor, read stdout       │
  tests/test_changelog_page_gate.py:    │
    RELEASE_VERSIONS += "0.9.2"         │
        │                                │
        ▼                                ▼
   one bump commit               [Plan B: closeout-guard baseline]
   (all 4 files together,          sha256/wc-l/HEAD/grep REL-09
    per SC#1)                       recorded at phase head
        │                                │
        └────────────┬───────────────────┘
                      ▼
        [Plan C: green-tree proof + CI dispatch]
          uv sync --extra dev --locked (confirm clean)
          full pytest, black --check, mypy
          rm -rf docs/_build; tox -e docs-html / docs-pdf
             (compare warning counts against last-recorded 3/5 baseline)
          push branch; gh workflow run CI --ref <actual-pushed-branch>
          gh run watch <run-id>; gh run view --json jobs
          transcribe all 12 job conclusions; both windows-latest lanes named
          ruff verdict read from the "lint" job's "Run lint with tox" step
                      │
                      ▼
        [Plan D: fence observation 2 + handoff]
          re-run closeout-guard commands; compare to Plan B baseline
          git tag -l 'v0.9.2' / git ls-remote --tags origin (+ positive control)
          gh release list (+ positive control) / gh run list --workflow=release.yml
          scoped git diff <PHASE_BASE_SHA>..HEAD -- typsphinx/  (expect empty)
          widened git diff --stat (positive control; expect exactly the bump-commit's files)
          63-HANDOFF.md authored (D-13/D-14/D-15)
```

### Recommended Project Structure

No new files under the product tree. Evidence files land under
`.planning/phases/63-v0-9-2-release-prep-prep-only/`:

```
.planning/phases/63-v0-9-2-release-prep-prep-only/
├── 63-CONTEXT.md              # already written (input to this research)
├── 63-RESEARCH.md             # this file
├── 63-CLOSEOUT-GUARD.md       # D-16/D-19: fence baseline + close-time re-verification
├── 63-CHANGELOG-EVIDENCE.md   # D-20: extractor stdout, tail-link block, RELEASE_VERSIONS proof
├── 63-GREEN-TREE-EVIDENCE.md  # SC#4: pytest/black/mypy/docs-build transcripts
├── 63-CI-EVIDENCE.md          # SC#4: dispatch + 12-job conclusion table
├── 63-SC5-INVARIANTS.md       # SC#5: tag/publish probes, observation 1 and 2, scoped+widened diff
├── 63-HANDOFF.md              # D-13/D-14/D-15: the milestone-close checklist
└── COVERAGE.md                # external-API-detector declaration (gh-heavy prose)
```

`63-VERIFICATION.md` MUST NOT appear in this list — it is `gsd-verifier`'s reserved output name
(D-19; confirmed by both `61-CONTEXT.md` and `61-VALIDATION.md`'s "Evidence-File Naming Constraint"
section).

### Pattern 1: The one-commit version-literal lockstep

**What:** `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md` land in exactly one commit, so
`git show --name-only` on it lists all four together (SC#1's exact ask, and the shape that is
currently killing every dependabot PR when violated).

**When to use:** Every version bump in this project, going forward — this is the standing lesson
from `.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` (CI-01).

**Example (reproduced from `57-BUMP-EVIDENCE.md`, this session's own source-of-truth read):**
```bash
# 1. Hand-edit the one literal.
sed -i 's/^version = "0.9.0"$/version = "0.9.2"/' pyproject.toml   # pyproject.toml:7

# 2. Hand-edit README's Status line.
sed -i 's/Stable (v0.9.0) - Production ready/Stable (v0.9.2) - Production ready/' README.md  # README.md:347

# 3. Regenerate uv.lock's self-package stanza (NEVER hand-edit uv.lock).
uv lock
# Expect: "Resolved N packages in Xms" / "Updated typsphinx v0.9.0 -> v0.9.2"

# 4. Reinstall the editable package so importlib.metadata agrees (load-bearing —
#    typsphinx.__version__ derives from installed metadata, not the pyproject literal).
uv sync --extra dev --locked
# Expect an uninstall/install pair: "- typsphinx==0.9.0" / "+ typsphinx==0.9.2"

# 5. Confirm the lockfile is internally consistent before anything else runs.
uv lock --check   # exit 0

# 6. Read back the version through the real import path.
uv run python -c "import typsphinx; print(typsphinx.__version__)"   # -> 0.9.2

# 7. Run the guard-test trio (these three tests are this milestone's whole
#    lockstep-enforcement surface).
uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml \
    tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v

# 8. Confirm the touched-file set BEFORE committing.
git diff --name-only   # expect exactly: README.md pyproject.toml uv.lock (plus CHANGELOG.md
                        # from the parallel CHANGELOG-edit step, committed together per SC#1)
```

### Pattern 2: The four-step CHANGELOG edit order (REL-10)

**What:** REL-10's whole risk is a two-step ordering hazard. `scripts/extract_changelog_section.py`'s
`_SECTION_HEADER_RE` (`r"^## \[(?P<version>[^\]]+)\]"`, confirmed by direct read of
`scripts/extract_changelog_section.py:54-59` this session) matches **every** `## [...]` heading with
no name filtering — extraction is purely positional: first heading naming the requested version,
everything up to the next `## [...]` heading of *any* name (`extract_section()`,
`scripts/extract_changelog_section.py:62-116`). The scratch block currently living inside
`## [Unreleased]` (`CHANGELOG.md:38`, `### Planned for Future Releases`) would therefore be captured
verbatim inside `## [0.9.2]`'s extracted body if the heading were simply renamed in place.

**When to use:** This exact edit, in this exact order, once, in Plan A.

**Example (live-verified against the current tree this session — `CHANGELOG.md` headings measured at
lines 8, 38, 45 via `grep -n "^## \[" CHANGELOG.md` and `grep -n "^### " CHANGELOG.md`):**
```bash
# BEFORE (current live state, confirmed this session):
#   Line 8:  ## [Unreleased]
#   Lines 10-36: ### Fixed  (three bullets: PATH-01; IMG-04..IMG-07; MSG-02..MSG-05)
#   Line 38: ### Planned for Future Releases   (the scratch block — 5 bullet items follow)
#   Line 45: ## [0.9.0] - 2026-08-17           (the terminator the extractor stops at today)

# Step 1 — relocate the scratch block under a FRESH, EMPTY "## [Unreleased]" heading,
#          placed ABOVE the existing heading (which becomes "## [0.9.2]" next).
#          Result shape:
#            ## [Unreleased]
#            <blank>
#            ### Planned for Future Releases
#            - BibTeX/bibliography support
#            ...
#            <blank>
#            ## [Unreleased]          <- OLD heading, about to become 0.9.2's
#            ### Fixed
#            - PATH-01 bullet ...
#            (etc.)

# Step 2 — rename ONLY the second (old) "## [Unreleased]" to "## [0.9.2] - 2026-08-30",
#          add the new lead paragraph above its "### Fixed", add the new IMG-08/09/10
#          bullet FIRST in the ### Fixed list (D-03/D-05), add a "### Verified" section
#          (D-06), remove nothing.

# Step 3 — tail link block: insert "[0.9.2]: .../releases/tag/v0.9.2" immediately above
#          the current topmost "[0.9.0]:" line; advance
#          "[Unreleased]: .../compare/v0.9.0...HEAD" to
#          "[Unreleased]: .../compare/v0.9.2...HEAD". [Unreleased] stays the LAST line.

# Step 4 — run the extractor and READ its stdout (not "reason about" it):
uv run python scripts/extract_changelog_section.py 0.9.2
echo $?   # expect 0

# Confirming greps (D-20's three named checks):
grep -c '^## \[0\.9\.1\]' CHANGELOG.md          # expect 0
grep -c '^\[0\.9\.1\]:' CHANGELOG.md            # expect 0
uv run python scripts/extract_changelog_section.py 0.9.2 | grep -c 'Planned for Future Releases'
                                                  # expect 0
```

**What breaks if steps 1 and 2 swap** (renaming the heading before relocating the scratch block):
the extractor's positional scan would find `## [0.9.2]` first (the renamed heading, formerly
`## [Unreleased]`), and its body would run all the way to the NEXT `## [...]` heading — which is
still `## [0.9.0] - 2026-08-17`, meaning `### Planned for Future Releases` and its five scratch
bullets are still physically located between the renamed heading and `## [0.9.0]`, so they would be
captured verbatim inside the extracted `## [0.9.2]` body and would leak into the GitHub Release body
this milestone eventually publishes. This is exactly the failure REL-10 exists to prevent, and it is
why relocation must happen strictly BEFORE the rename.

### Pattern 3: The `RELEASE_VERSIONS` extension proof, run in the correct environment (D-11)

**What:** `tests/test_changelog_page_gate.py:50-66`'s `RELEASE_VERSIONS` tuple must gain `"0.9.2"`
and its preceding comment must be updated. But the two test classes that actually assert coverage
(`TestChangelogPageContentCoverage`, HTML; the PDF-compiling class) are marked `@pytest.mark.slow`
and additionally SKIP when `myst_parser` is not importable — and `myst_parser` lives in the **`docs`**
extra only (confirmed this session: `pyproject.toml:49-54`), never in `dev`. A worktree provisioned
per `CLAUDE.md`'s mandatory `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
therefore SKIPS both classes silently.

**When to use:** Every time `RELEASE_VERSIONS` (or any docs-page content assertion) changes.

**Example (reproduced from `57-CHANGELOG-EVIDENCE.md`'s own verified command):**
```bash
uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v
```
This is the ONE local command shape that actually exercises the two skip-prone classes — `--extra
docs` in addition to the worktree's mandatory `--extra dev`. The CI `docs` job (via
`tox -e docs-html`/`tox -e docs-pdf`, both of which declare `extras = docs` in `tox.ini:64,72`) also
exercises them for real. **A green worktree `uv run pytest` (dev-only) proves nothing about D-11** —
the plan's own evidence file must state which of the two routes (local `--extra docs` sync, or the
dispatched CI docs job) it used, and must not claim D-11 proven from a bare `uv run pytest tests/
test_changelog_page_gate.py` run.

### Anti-Patterns to Avoid

- **Trusting `git diff --name-only` alone as SC#4's "empty `typsphinx/` diff" proof.** An empty scoped
  diff from a wrong or non-existent anchor SHA looks identical to a genuinely clean tree. Always pair
  it with the widened, same-anchor `git diff --stat -- . ':(exclude).planning'` positive control —
  `61-SC4-INVARIANTS.md` § "The typsphinx/ diff (SC#4)" is the exact template; for Phase 63 the
  widened diff's expected non-empty result is the bump commit's five files (`pyproject.toml`,
  `uv.lock`, `README.md`, `CHANGELOG.md`, `tests/test_changelog_page_gate.py`), not 61's
  single-file `CHANGELOG.md` result.
- **A bare `git ls-remote --tags origin 'v0.9.2'`** as the sole remote-tag probe. Its silence is
  indistinguishable from a network failure. Fetch the unfiltered tag list once and derive both a
  positive control (a `grep -c` against `v0.9.0`, which is known to exist) and the negative
  assertion (`grep -c` against `v0.9.2`, expected 0) from that single fetch — `61-SC4-INVARIANTS.md`
  § "Remote tag probe (unfiltered, with positive control)" is the exact template.
- **Running `tox -e docs-html`/`docs-pdf` without `rm -rf docs/_build` first (D-21).** An incremental
  rebuild only reprocesses pages invalidated by the specific file(s) that changed and can under-report
  warnings carried by unrelated pages — `61-CHANGELOG-EVIDENCE.md` § "Docs render" states this
  explicitly and this is a *repeated* finding across two prior phases, not a theoretical hazard.
- **Copying the "`### Verified`" third bullet's wording from `## [0.9.0]` or `## [0.6.5]` verbatim**
  ("The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free"). D-06 explicitly
  forbids this — this milestone did not run that corpus; the substituted claim is the 18/18-masters
  TEST-05 gate result instead.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Extracting a versioned CHANGELOG section for the release body | A new script, a `sed`/`awk` one-off, or hand-copying the section | `scripts/extract_changelog_section.py` (already committed, already pytest-covered via `tests/test_changelog_extraction.py`'s `subprocess.run` exercise) | `release.yml`'s `validate` and `create-release` jobs both call this exact script. A second, independently-written extraction implementation could silently diverge from what CI actually runs — the module docstring names this as the deliberate reason there is only one. |
| Proving the fence held (no tag, no publish) | A single `git tag -l` call, trusted alone | The paired probe-plus-positive-control pattern from `61-SC4-INVARIANTS.md` (local tag list, unfiltered remote tag list with a `grep -c` positive control against `v0.9.0`, `gh release list` with a `Latest`-marker positive control, `gh run list --workflow=release.yml`) | A vacuous "empty" result from an unreachable network endpoint is indistinguishable from a genuinely-empty result without a positive control that would fail loudly if the probe never reached its source. |
| Detecting the `phase.complete` REL-09 auto-flip | A new detection mechanism | The SHA-256 + line-count + verbatim-grep checksum fence from `61-CLOSEOUT-GUARD.md`, reused verbatim per D-16 | This is the ONLY measure that has ever stopped the flip, across five consecutive prior release-prep closes before Phase 61's success. Re-inventing a detector risks missing the exact failure shape the existing one already catches. |
| Regenerating `uv.lock`'s self-package version | Hand-editing `uv.lock`'s `version = "..."` line | `uv lock` | `uv.lock` is a generated artifact; a hand-edit desyncs it from the resolver's own dependency graph in ways `uv lock --check` would then catch as drift — and D-17 explicitly forbids hand-editing it. |

**Key insight:** This phase's entire mechanical surface has already been executed successfully, in
close-to-identical shape, twice (Phase 57 for the bump+extractor mechanics, Phase 61 for the
fence-and-handoff mechanics). Every command shape above is a direct reproduction of a command that
already ran and produced the exact output shown, not a first attempt.

## Runtime State Inventory

Not applicable — Phase 63 makes no rename, refactor, or migration change to any runtime component.
No stored data, live-service config, OS-registered state, secrets/env vars, or build artifacts are
affected. The only state this phase writes is: (1) four product-tree files in one commit
(`pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`), (2) one test file's tuple edit
(`tests/test_changelog_page_gate.py`), and (3) `.planning/`-scoped evidence and handoff documents.

## Common Pitfalls

### Pitfall 1: Declaring `[REL-09]` in a plan's `SUMMARY.md` frontmatter

**What goes wrong:** A plan's generated `SUMMARY.md` frontmatter lists `requirements-completed:
[REL-09]` because the plan's `requirements:` field names REL-09 for coverage purposes, and summary
generation defaults to treating a named requirement as completed.

**Why it happens:** This is exactly what happened at three of Phase 61's four plans — caught by the
v0.9.1 audit and named explicitly in `63-CONTEXT.md` D-16 as the correction this phase must apply.

**How to avoid:** Every plan's `must_haves.truths` (or equivalent) must state explicitly that
`requirements-completed: []` is the required frontmatter value for REL-09 in **every single plan**,
not just the plan that authors the closeout guard. Verify this by grepping every `SUMMARY.md` in the
phase directory after execution: `grep -l 'REL-09' */*-SUMMARY.md` should find nothing inside a
`requirements-completed:` list.

**Warning signs:** Any `*-SUMMARY.md` frontmatter block containing `requirements-completed:
[REL-09]` or `requirements-completed: [REL-09, ...]`.

### Pitfall 2: Renaming the CHANGELOG heading before relocating the scratch block

**What goes wrong:** The `### Planned for Future Releases` scratch block leaks into the extracted
`## [0.9.2]` body and would eventually leak into the published GitHub Release notes.

**Why it happens:** The natural instinct is to rename `## [Unreleased]` → `## [0.9.2]` first (it
"looks like" the primary edit) and add the new empty `## [Unreleased]` placeholder afterward as a
cleanup step — but the extractor's purely-positional algorithm makes the ORDER load-bearing, not
cosmetic (see Pattern 2 above).

**How to avoid:** Follow the exact four-step order in Pattern 2. Run the extractor and grep its
stdout for `Planned for Future Releases` (expect 0 hits) BEFORE considering REL-10 satisfied.

**Warning signs:** `uv run python scripts/extract_changelog_section.py 0.9.2 | grep -c 'Planned for
Future Releases'` returning anything other than `0`.

### Pitfall 3: Treating a `--extra dev`-only pytest run as proof of D-11's `RELEASE_VERSIONS` edit

**What goes wrong:** A worktree-standard `uv sync --extra dev` + `uv run pytest
tests/test_changelog_page_gate.py -v` run reports all tests green (including the two slow classes,
which report as *skipped*, which pytest still counts toward an overall "no failures" exit code) —
and the plan's evidence mistakenly cites this as proof `RELEASE_VERSIONS`' new entry actually reaches
the rendered page.

**Why it happens:** `myst_parser` lives only in the `docs` extra (`pyproject.toml:49-54`,
`tests/test_changelog_page_gate.py:13` docstring, confirmed this session); a `dev`-only sync makes
`MYST_PARSER_AVAILABLE = False` and both content-coverage classes skip via
`@pytest.mark.skipif(not MYST_PARSER_AVAILABLE, ...)`.

**How to avoid:** Run `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v`
(Pattern 3 above) and confirm the transcript shows the two coverage-class tests as `PASSED`, not
`SKIPPED`. Alternatively, cite the dispatched CI `docs` job's own conclusion, which runs via
`tox -e docs-html`/`docs-pdf` and therefore always carries the `docs` extra.

**Warning signs:** A pytest transcript for `tests/test_changelog_page_gate.py` showing any `SKIPPED`
result being cited as evidence for D-11.

### Pitfall 4: Reading `ruff`'s CI verdict from a step named "Run linters"

**What goes wrong:** A plan searches the dispatched `ci.yml` run for a step literally named "Run
linters" (as `63-CONTEXT.md` D-18's own wording suggests) and cannot find one, then either
mis-attributes a different job's verdict to `ruff`, or — worse — triggers `release.yml` (which DOES
have a step named "Run linters", inside its `validate` job) to find one, violating the prep-only
fence's absolute "no trigger of release.yml" prohibition.

**Why it happens:** `63-CONTEXT.md` D-18 copies wording that describes `release.yml`'s step name,
not `ci.yml`'s. This research confirmed the discrepancy by reading both workflow files directly this
session — see `## Contradictions Found` below.

**How to avoid:** Read `ruff`'s verdict from `ci.yml`'s `lint` job (displayed as "Lint and Format
Check" in `gh run view`'s job list — confirmed against `61-CI-EVIDENCE.md`'s own 12-job table, row 5)
— its one step is named "Run lint with tox" and runs `uv run tox -e lint`, which in turn runs
`black --check .` then `ruff check .` (`tox.ini:39-45`). The job's overall conclusion (`success`/
`failure`) is what to transcribe; there is no need to drill into a step name that does not exist.

**Warning signs:** A plan's `must_haves` or evidence file naming a step called "Run linters" as the
source of `ci.yml`'s ruff verdict, or any command that dispatches `release.yml` (`gh workflow run
release.yml`, `gh workflow run Release`) inside this phase.

### Pitfall 5: A stale docs-warning baseline substituted for a fresh clean-build run

**What goes wrong:** The plan cites "3 warnings for docs-html, 5 for docs-pdf" (the figure carried
through Phases 56→57→61) as this phase's own SC#4 evidence without actually re-running
`rm -rf docs/_build && uv run tox -e docs-html`/`docs-pdf` on the bumped-and-curated tree.

**Why it happens:** The number has been stable across three prior phases and it is tempting to treat
it as settled — but Phase 63's CHANGELOG diff is much larger than Phase 61's (a full section rename,
a new lead paragraph, a new bullet, a new `### Verified` subsection, a relocated scratch block, plus
`RELEASE_VERSIONS`' page-content assertions now expecting `"0.9.2"` to appear on the rendered page).
A malformed MyST construct in any of that new prose would be a genuinely NEW warning this phase must
catch, not one the recalled baseline can vouch for.

**How to avoid:** Follow D-21 literally: `rm -rf docs/_build` before each of `tox -e docs-html` and
`tox -e docs-pdf`, on the tree AFTER every phase edit has landed, and record the verbatim tail line
(`build succeeded, N warnings.`) as this phase's own measurement. Compare against 3/5 as the
*last-known* figure, not as an assumed match.

**Warning signs:** An evidence file stating "matches the 3/5 baseline" with no accompanying fresh
command transcript from this phase's own execution.

### Pitfall 6: Assuming REL-09's guarded-lines shape is identical to Phase 61's

**What goes wrong:** The closeout guard's "lines under guard" section is authored by copying
61-CLOSEOUT-GUARD.md's three-hit shape (checkbox line, Traceability row, a terse "phase-totals"
summary line) without re-measuring against the CURRENT `.planning/REQUIREMENTS.md`, which has a
different structure this milestone (only 7 requirements, no phase-totals enumeration line).

**Why it happens:** `61-CLOSEOUT-GUARD.md` is the explicit template to reuse "verbatim" (D-16), and
copying its exact shape without re-running the grep is an easy shortcut.

**How to avoid:** This research already re-ran the check this session against the current tree:
`grep -n 'REL-09' .planning/REQUIREMENTS.md` returns **three hits at lines 70, 154, and 175** — but
line 175 is the FIRST line of a **six-line prose paragraph** ("Phase mapping notes"), not a single
terse summary line like 61's line 220. The plan authoring `63-CLOSEOUT-GUARD.md` must re-run this
grep itself (values will differ again once the CHANGELOG/bump commits land and shift nothing in
REQUIREMENTS.md — but the exact byte content must still be captured fresh, not copied from this
research) and decide explicitly whether the guarded "lines" for the checksum fence are just the two
state-bearing lines (70 checkbox, 154 Traceability row) plus the full sha256 of the whole file (which
already covers line 175's content anyway), following 61's own precedent of treating its third hit as
informational-only, never state-bearing.

**Warning signs:** A `63-CLOSEOUT-GUARD.md` that quotes a "phase-totals line" that does not exist in
the current `REQUIREMENTS.md`, or a re-verification step that only checks two of the three grep hits.

## Code Examples

### The closeout-guard fence (D-16/REL-11), reproduced from `61-CLOSEOUT-GUARD.md`

```bash
# At phase head, inside the plan's own worktree, BEFORE any other plan has run:
sha256sum .planning/REQUIREMENTS.md
wc -l .planning/REQUIREMENTS.md
date -u +"%Y-%m-%dT%H:%M:%SZ"
git rev-parse HEAD          # -> PHASE_BASE_SHA, recorded for later plans to scope diffs against
grep -n 'REL-09' .planning/REQUIREMENTS.md
# This session's own fresh cross-check against the CURRENT tree (2026-08-30):
#   sha256: f0dd4ec377bbc95cd2b8cdb19fe784cfc21bd6d08e2743de6f5b9fc1768f5b33
#   wc -l:  184
#   hits:   70:- [ ] **REL-09**: 0.9.2 released to PyPI with a curated `## [0.9.2]` CHANGELOG entry, the version
#           154:| REL-09 | Phase 63 | Pending |
#           175:- **Phase 63 — v0.9.2 Release Prep (prep-only)** carries the release half. **REL-09 is cited for
#   (line 175 opens a 6-line paragraph — see Pitfall 6 above for why this differs from 61's shape)
# THIS SESSION'S NUMBERS ARE A CROSS-CHECK, NOT THE PLAN'S OWN BASELINE — the plan re-runs every
# one of these commands fresh, inside its own worktree, at its own phase-head moment.

# At phase close, and AGAIN after phase.complete-family tooling has run (the third, decisive
# observation, per D-16):
sha256sum .planning/REQUIREMENTS.md          # compare against the recorded Baseline
git diff --name-only -- .planning/REQUIREMENTS.md   # expect: no output
grep -n 'REL-09' .planning/REQUIREMENTS.md   # expect: byte-identical to the three quoted lines

# If ANY comparison diverges:
git checkout -- .planning/REQUIREMENTS.md
# The flip is reverted and reported, NEVER accepted and NEVER committed.
```

### SC#5's tag/publish probe pair, with positive controls, reproduced from `61-SC4-INVARIANTS.md`

```bash
# Local tag probe
git tag -l 'v0.9.2'                          # expect: (no output)

# Remote tag probe (unfiltered fetch, two counts derived from ONE fetch — never a bare
# filtered `git ls-remote --tags origin 'v0.9.2'`, whose silence is indistinguishable from
# a network failure):
git ls-remote --tags origin > /tmp/tags.txt
grep -c 'refs/tags/v0\.9\.0$' /tmp/tags.txt   # POSITIVE CONTROL — expect 1 (v0.9.0 is known to exist)
grep -c 'refs/tags/v0\.9\.2'  /tmp/tags.txt   # NEGATIVE ASSERTION — expect 0

# Publish probe
gh release list --limit 20 > /tmp/releases.txt
grep -c 'Latest' /tmp/releases.txt            # POSITIVE CONTROL — expect 1 (some release IS marked Latest)
grep -c 'v0\.9\.2' /tmp/releases.txt          # NEGATIVE ASSERTION — expect 0

# Release-workflow probe
gh run list --workflow=release.yml --limit 5
# expect: no run corresponding to a v0.9.2 tag push
```

Run this pair TWICE, separated by intervening waves (D-16/SC#5's explicit requirement) — once at
phase head (paired with the closeout-guard baseline) and once at phase close (paired with the
closeout-guard re-verification), following `61-SC4-INVARIANTS.md`'s own two-observation structure
exactly.

### The scoped-vs-widened `typsphinx/` diff, reproduced from `61-SC4-INVARIANTS.md`

```bash
# PHASE_BASE_SHA read back from 63-CLOSEOUT-GUARD.md's own "Baseline" section.

# The SC#5 claim itself:
git diff <PHASE_BASE_SHA>..HEAD -- typsphinx/
# expect: (no output) -- this phase makes no product-tree behaviour change

# The positive control (same anchor, widened scope) -- proves the anchor is real and
# reachable, so the scoped diff's emptiness is a genuine finding, not an artifact of a
# broken or mistyped SHA:
git diff --stat <PHASE_BASE_SHA>..HEAD -- . ':(exclude).planning'
# expect: exactly the bump commit's five files --
#   README.md | 1 +
#   CHANGELOG.md | N insertions
#   pyproject.toml | 1 +-
#   tests/test_changelog_page_gate.py | N +-
#   uv.lock | N +-
# (This differs from Phase 61's own single-file CHANGELOG.md result -- Phase 63 DOES bump,
#  so the widened diff is wider than 61's was.)
```

### Version-bump command sequence — see Pattern 1 above (§ Architecture Patterns) for the full,
transcript-verified sequence reproduced from `57-BUMP-EVIDENCE.md`.

### The four-step CHANGELOG edit order — see Pattern 2 above for the full sequence.

### CI dispatch, reproduced from `61-CI-EVIDENCE.md` with Phase 63's own corrected step-name reading

```bash
# Confirm the lockfile is clean BEFORE dispatch (D-17) -- every CI job begins with the
# identical `uv sync --extra dev --locked` step; a stale lock fails all 12 lanes on the
# lock itself, before any test/lint/type signal exists.
uv sync --extra dev --locked

# Push whatever branch this plan's worktree actually landed on (confirm with
# `git rev-parse --abbrev-ref HEAD` -- do not assume it is the canonical
# gsd/v0.9.2-inline-image-blocker-fix-and-release branch name; 61-CI-EVIDENCE.md dispatched
# against its OWN worktree-derived branch name, not the milestone's canonical branch, because
# worktree-isolated execution pushes each plan's own branch).
git push origin <actual-current-branch>

gh workflow run ci.yml --ref <actual-current-branch>
gh run list --workflow=ci.yml --branch <actual-current-branch> --limit 1
gh run watch <run-id> --exit-status
gh run view <run-id> --json jobs   # reduce to name + conclusion, transcribe ALL 12 rows literally

# ruff's verdict: read the "Lint and Format Check" job's overall conclusion (its one step,
# "Run lint with tox", runs `uv run tox -e lint` = `black --check .` + `ruff check .`).
# There is NO step literally named "Run linters" in ci.yml -- see Pitfall 4 / Contradictions Found.
```

Expected 12-job census (derived from `.github/workflows/ci.yml` directly, confirmed this session):
6 matrix test jobs (`Test Python {3.12,3.13} on {ubuntu,windows,macos}-latest`) + `Lint and Format
Check` (1) + `Type Check` (1) + `Code Coverage` (1) + `Build Package` (1) + `Integration Test -
{basic,advanced}` (2) = 12.

### Clean-build docs warning proof, reproduced from `61-CHANGELOG-EVIDENCE.md`

```bash
rm -rf docs/_build
uv run tox -e docs-html   # tail: "build succeeded, N warnings."
rm -rf docs/_build
uv run tox -e docs-pdf    # tail: "Generated PDF: .../docs/_build/pdf/typsphinx.pdf" then
                           #       "build succeeded, N warnings."
```

Last-recorded baseline (61's close, 2026-08-29): **3 warnings for `docs-html`, 5 for `docs-pdf`**.
This is a cross-check figure, not a substitute for running the commands above fresh on this phase's
own bumped-and-curated tree (Pitfall 5).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Release-prep bundled unrelated product fixes into the same phase (Phase 57: 11 plans, two bundled defect fixes) | A prep-only phase with zero bundled product work when the milestone's product fix already landed as its own phase (Phase 62 → Phase 63, this milestone) | This milestone (v0.9.2) | Smaller, faster-to-plan phase; closer in shape to Phase 61's 4-plan / 3-wave decomposition than to Phase 57's 11-plan / 4-wave one. |
| Handoff documents opened with the negative ("this milestone publishes nothing") | Handoff documents open with the positive publish-checklist framing, UNLESS the milestone genuinely publishes nothing | Phase 61 → Phase 63 (D-13) | `63-HANDOFF.md` restores the seven-consecutive-prior-handoffs' standard opening polarity; Phase 61's negative opening was the deliberate anomaly, not the new normal. |
| A `### Verified` section's third bullet cited the full-corpus `-b typstpdf` re-run | Substituted with whatever claim the milestone's own work actually measured (D-06) | Established this phase (following the pattern Phase 61 raised as an open question and deferred here) | Prevents an unmeasured claim from being copy-pasted forward across releases; each release's `### Verified` section must be backed by ITS OWN milestone's evidence. |

**Deprecated/outdated:** none — no tool, library, or workflow step used by this phase has been
superseded since Phase 61's close (2026-08-30, same day).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The docs-warning baseline (3 for `docs-html`, 5 for `docs-pdf`) remains the figure this phase's fresh clean-build run will reproduce. | Pitfall 5; Code Examples § "Clean-build docs warning proof" | If a new warning is introduced by this phase's own (much larger than 61's) CHANGELOG edit, the plan must NOT paper over the divergence — it must report the new count and, if the new warning traces to a malformed MyST construct in the authored prose, fix the prose before accepting SC#4. |
| A2 | The canonical branch `gsd/v0.9.2-inline-image-blocker-fix-and-release` will still be the correct dispatch ref by the time the CI-dispatch plan runs, with no decoy `gsd/v0.9.2-milestone` branch interfering. | Code Examples § "CI dispatch" | Measured this session: no decoy branch currently exists (`git branch -vv` shows exactly one `0.9.2`-named branch); `63-CONTEXT.md` specific idea #5 explicitly warns the decoy has reappeared at every prior milestone via commit-helper tooling. If it reappears, the plan must advance the canonical pointer BEFORE deleting the decoy (never delete first — that orphans commits), per the CONTEXT's own instruction. |
| A3 | `release.yml`'s `create-release` job (D-14/REL-04) will run green when actually exercised at `/gsd-complete-milestone`, because it ran green at the v0.8.0 and v0.9.0 real tag pushes. | User Constraints § D-14 | This is a re-offered observation for a FUTURE phase, not something this phase can verify — the risk is scoped entirely to `/gsd-complete-milestone`, not to Phase 63's own execution. |

## Open Questions

1. **Will the docs-warning count change from 3/5?**
   - What we know: the last three measurements (Phase 56 close, Phase 57 close, Phase 61 close) all
     landed at exactly 3 for `docs-html` and 5 for `docs-pdf`.
   - What's unclear: Phase 63's CHANGELOG diff is substantially larger and more structurally complex
     than 61's (a heading rename, a scratch-block relocation, a new lead paragraph, a new bullet, a
     new `### Verified` subsection) — a malformed MyST construct anywhere in the new prose could
     introduce a new warning.
   - Recommendation: run the clean-build commands fresh (Pitfall 5) and treat 3/5 as a cross-check
     figure, never a substitute for execution.

2. **Which plan runs the milestone-invariant sweep (no new dependency, `@preview` lockstep, no new
   `typst_*` config value) for D-06's first two `### Verified` bullets, and against what anchor?**
   - What we know: `61-SC4-INVARIANTS.md` explicitly deferred this decision to Phase 63, warning that
     the sweep must be re-measured fresh against `v0.9.0..<v0.9.2-tip>`, never copied forward from a
     prior milestone's numbers (57-SC4-INVARIANTS.md's own sweep falsified an inherited assumption
     from 52-SC4-INVARIANTS.md).
   - What's unclear: whether a full sweep (dependency array diff, `@preview` version grep across all
     four sync surfaces, `typst_*` config-value census) is run, or whether targeted greps suffice —
     `63-CONTEXT.md` § Claude's Discretion leaves this open explicitly.
   - Recommendation: given that Phase 62 already asserted zero new dependencies and unchanged
     `@preview` versions as part of its own scope (TEST-05's regression gate did not touch
     dependencies), a targeted grep against the `v0.9.0..HEAD` range (this milestone's own anchor,
     confirmed reachable and non-trivial in `61-SC4-INVARIANTS.md`'s own milestone-anchor
     measurement: 137 commits, 23 files, +3011/−72 as of Phase 61's close) is almost certainly
     sufficient and cheaper than a full sweep; whichever route is chosen, its positive control must
     be real (per Claude's Discretion's own stated requirement).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | Version bump, lockfile regen, all `uv run`/`uv sync` invocations | ✓ | `0.11.25` | — |
| `git` | Tag/remote probes, diff scoping, commit boundary tracking | ✓ | `2.54.0` | — |
| `gh` (GitHub CLI) | CI dispatch, `gh run watch`/`gh run view`, `gh release list` | ✓ | `2.98.0` | — |
| `tox` (via `uv run tox`, not on bare PATH) | `docs-html`/`docs-pdf`/`lint`/`type` environments | ✓ (worktree-provisioned) | pinned `tox-uv-bare~=1.35,<2` | — |
| `myst_parser` (docs extra) | `tests/test_changelog_page_gate.py`'s two slow coverage classes; both docs tox environments | ✓ (via `--extra docs` or `docs` tox env's own `extras = docs`) | `>=5.0` (pyproject.toml) | none needed — see Pitfall 3 for the exact invocation shape required. |
| `ruff` (local, generic-linux ELF on this NixOS machine) | Local lint pre-flight (optional, additive only) | ✗ (documented NixOS ELF-exec hazard, `.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`) | — | CI holds lint authority (D-18, QUA-10) — never treat a local `ruff` failure as this phase's own verdict; the dispatched `ci.yml` `lint` job is authoritative. |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** local `ruff` — CI is the authoritative fallback, an
established standing project pattern, not a new accommodation for this phase.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`), orchestrated via `tox` (`env_list = py312, py313, lint, type, cov, docs`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]`; `tox.ini` |
| Quick run command | `uv run pytest -m "not slow"` |
| Full suite command | `uv run pytest` (includes the `@pytest.mark.slow` corpus/docs-build gates) |

**Worktree note (CLAUDE.md § "Worktree-isolated execution", STANDING):** every executor first runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in its own worktree, then runs
every command via `uv run`. The `docs` extra must additionally be synced wherever D-11's proof or the
docs-warning baseline is executed (Pitfall 3).

**Pre-phase baseline (measured at Phase 62's close, 2026-08-30, `62-VERIFICATION.md` line 66):**
`uv run pytest -q` → **1543 passed, 5 skipped** (all 5 pre-existing/unrelated: 4× myst-parser
docs-extra gap, 1× env-gated corpus report). This is NOT this phase's own measurement — Phase 63's
green-tree plan must re-run the full suite fresh on the bumped tree and record its own count, which
should match 1543/5 exactly (or 1543+N/5 if this phase's own edits add test cases, which none of
D-01..D-21 calls for).

**Docs-warning baseline (last measured at Phase 61's close, 2026-08-29):** `tox -e docs-html` →
**3** warnings, `tox -e docs-pdf` → **5** warnings. A fresh, clean-build run is mandatory per D-21 —
see Pitfall 5.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|--------------------|-------------|
| REL-09 (coverage only; never closed by this phase) | Version-literal lockstep across `pyproject.toml`/`uv.lock`/`README.md`; guard-test trio stays green | unit | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` | ✅ exists |
| REL-09 (coverage only) | `uv sync --extra dev --locked` succeeds against the regenerated lockfile | environment/lock | `uv sync --extra dev --locked` (exit 0) | ✅ exists (uv itself) |
| REL-10 | Extractor reproduces the `## [0.9.2]` body byte-for-byte, no `0.9.1` heading/link, no scratch-block leakage | subprocess/integration | `uv run python scripts/extract_changelog_section.py 0.9.2` (exit 0, non-empty stdout); `grep -c '^## \[0\.9\.1\]' CHANGELOG.md` (0); `grep -c '^\[0\.9\.1\]:' CHANGELOG.md` (0); extractor stdout piped through `grep -c 'Planned for Future Releases'` (0) | ✅ exists (`scripts/extract_changelog_section.py`, `tests/test_changelog_extraction.py` exercises it) |
| REL-10 (D-11) | `RELEASE_VERSIONS` gains `"0.9.2"` and the rendered page carries it | docs build (slow, docs-extra-gated) | `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` (all 6 tests PASSED, none SKIPPED) | ✅ exists |
| REL-11 | REL-09's checkbox stays `[ ]` under a SHA-256 fence, re-verified at head/close/post-`phase.complete` | audit (checksum) | `sha256sum .planning/REQUIREMENTS.md` compared across three timestamped observations; `grep -n 'REL-09' .planning/REQUIREMENTS.md` compared line-for-line | ✅ N/A — created by the plan (`63-CLOSEOUT-GUARD.md`) |
| SC#4 (green-tree proof, cross-cutting) | Full suite, black, mypy, both docs builds, all executed IN this phase | full-suite + lint/type + docs build | `uv run pytest`; `uv run black --check .`; `uv run mypy typsphinx/`; `rm -rf docs/_build && uv run tox -e docs-html`; `rm -rf docs/_build && uv run tox -e docs-pdf` | ✅ exists |
| SC#4 (CI authority, cross-cutting) | Fresh 3-OS dispatch on the bumped tip, both `windows-latest` lanes green, `ruff` verdict from the `lint` job | CI | `gh workflow run ci.yml --ref <branch>` → `gh run watch <id> --exit-status` → `gh run view <id> --json jobs` | ✅ `.github/workflows/ci.yml` |
| SC#5 (fence, cross-cutting) | No local/remote tag, no publish, `typsphinx/` diff empty at two waves-separated observations | audit | the paired probe-plus-positive-control commands in `## Code Examples` § "SC#5's tag/publish probe pair" | ✅ N/A — created by the plan (`63-SC5-INVARIANTS.md`) |

*Status column intentionally omitted — this table seeds the planner; task-level ⬜/✓ status is
assigned by the plan itself, following `61-VALIDATION.md`'s own precedent shape.*

### Sampling Rate

- **After every task commit:** no product-behaviour code changes, so there is no per-commit
  product gate beyond the task's own evidence artifact being written and readable.
- **After every plan wave:** `uv run pytest` (full suite) plus
  `uv run black --check . && uv run mypy typsphinx/` (ruff deferred to CI per D-18/QUA-10).
- **After the CHANGELOG edit and the `RELEASE_VERSIONS` edit specifically:**
  `rm -rf docs/_build && uv run tox -e docs-html` and same for `docs-pdf`, warning counts compared
  against the last-recorded 3/5 baseline (Pitfall 5); `uv run --extra dev --extra docs pytest
  tests/test_changelog_page_gate.py -v` for D-11's own proof.
- **Phase gate:** one fresh 3-OS CI dispatch on the phase's final tip (after the bump lands), with
  all 12 jobs green and both `windows-latest` lanes named individually — the milestone's own
  acceptance bar, carried forward unchanged from every prior release-prep phase.
- **Max feedback latency:** local suite minutes; CI dispatch ~7 min wall clock (Phase 61's dispatch,
  run `33260111745`, took roughly 4-4.5 minutes per matrix job, full run concluded within the
  session).

### Wave 0 Gaps

None. Existing infrastructure covers every phase requirement — the full pytest suite, the
`tox` lint/type/docs environments, `ci.yml`'s 3-OS matrix, `scripts/extract_changelog_section.py`
and its pytest coverage (`tests/test_changelog_extraction.py`), and `tests/test_changelog_page_gate.py`
are all already in place and were exercised as recently as CI run `33260111745` (Phase 61's close)
and the local suite run recorded in `62-VERIFICATION.md` (Phase 62's close, 2026-08-30, same day as
this research).

## Security Domain

`security_enforcement` is `true` in `.planning/config.json` (`security_asvs_level: 1`,
`security_block_on: "high"`), so this section is included per the standing instruction — but this
phase introduces no new attack surface: no new input parsing, no new authentication/authorization
path, no new cryptography, no new external-facing endpoint. It edits markdown/TOML/lockfile content
and writes planning documents.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | This phase touches no auth surface. |
| V3 Session Management | No | Not applicable — no runtime session code. |
| V4 Access Control | No | Not applicable. |
| V5 Input Validation | Marginal | The only "input" this phase produces is prose in `CHANGELOG.md` and a version-string literal in `pyproject.toml`/`README.md`, all rendered/consumed by already-existing, already-tested tooling (`myst_parser`, `tomllib`, the version-sync regex family). A docs-build warning (already gated by D-21) is the only realistic failure mode, not a security defect. |
| V6 Cryptography | Marginal | The SHA-256 checksum used by D-16's closeout guard is an **integrity check against accidental tooling mutation**, not a cryptographic security boundary (no secret, no adversarial input, no confidentiality requirement) — `sha256sum` is the correct, already-established tool for this use, not a hand-rolled hash. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A malformed CHANGELOG bullet or MyST construct publishing broken markup to Read the Docs | Tampering (of published content, self-inflicted) | The docs-warning-baseline comparison (D-21's clean-build requirement) is the mitigation — a malformed construct surfaces as a new warning before it reaches a published surface. |
| Accidentally performing an irreversible action (a real `git tag v0.9.2` push, or triggering `release.yml`) | Tampering / Elevation of privilege (of the release pipeline) | The two-observation fence proof itself (D-16/SC#5) is the mitigation, plus the standing, absolute project discipline that opening a PR, pushing a tag, or triggering `release.yml` is out of scope for every plan in this phase — reiterated in every one of Phase 61's four plans' `prohibitions` blocks, and reproduced identically here. |
| `.planning/REQUIREMENTS.md`'s REL-09 checkbox silently flipped by `phase.complete`-family tooling, misrepresenting the release's true state to a future reader or to `/gsd-complete-milestone` | Tampering (of project-state metadata) | D-16's three-observation SHA-256 checksum fence, with the third observation deliberately placed AFTER `phase.complete`-family tooling has run — the moment the flip has historically landed at five consecutive prior release-prep closes before Phase 61 caught it. |

## Contradictions Found

**One factual defect confirmed in this session, in `63-CONTEXT.md` D-18's stated wording (and,
transitively, in the phase description's own SC#4 text as passed to this research).**

**Claim as stated (D-18):** "`ruff`'s verdict is taken from that run's `Run linters` step — never
from this machine..."

**What this research measured (direct read of both workflow files, this session):**

- `.github/workflows/ci.yml` has **no step named "Run linters"**. Its `lint` job (display name
  "Lint and Format Check") has exactly one step, named **"Run lint with tox"**
  (`.github/workflows/ci.yml:69`), which runs `uv run tox -e lint` → `tox.ini:39-45`'s
  `[testenv:lint]` → `black --check .` then `ruff check .`.
- `.github/workflows/release.yml`'s `validate` job **does** have a step literally named
  **"Run linters"** (`.github/workflows/release.yml:84`, running `uv run black --check .` then
  `uv run ruff check .`) — but that job only executes when `release.yml` itself runs (a real tag
  push, or a `workflow_dispatch` naming a `tag` input), and triggering `release.yml` at all is
  explicitly and absolutely forbidden inside this prep-only phase (every plan's `prohibitions`
  block, e.g. `61-01-PLAN.md`: "MUST NOT perform any irreversible action in this phase... no trigger
  of release.yml"; `61-02-PLAN.md`, `61-03-PLAN.md`: same clause verbatim).

**Why this matters:** a planner or executor searching literally for a step named "Run linters"
inside the D-18-dispatched `ci.yml` run will not find one. Two bad outcomes are plausible if this
goes uncorrected: (a) the plan mis-reads a different step's or job's result as `ruff`'s verdict, or
(b) worse, a plan concludes it must dispatch `release.yml` instead — directly violating the
prep-only fence.

**Correction, applied throughout this RESEARCH.md (Pattern 3 / Pitfall 4 / Code Examples § "CI
dispatch"):** read `ruff`'s CI verdict from `ci.yml`'s `lint` job's overall conclusion (displayed as
"Lint and Format Check" in `gh run view`'s job list, per `61-CI-EVIDENCE.md`'s own 12-job table row
5, which recorded this exact job as `success`). There is no need, and no correct way, to drill into a
step named "Run linters" inside `ci.yml` — it does not exist there.

**Everything else in D-01..D-21 was either confirmed live this session (D-11's `RELEASE_VERSIONS`
current end-state and preceding comment; D-17's `uv.lock:1467` current value; D-20's
`_SECTION_HEADER_RE` positional-matching claim; the current CHANGELOG.md heading line numbers
8/38/45; the current `pyproject.toml`/`README.md`/`uv.lock` version literals; the current absence of
a `v0.9.2` tag locally and on the remote) or is process guidance this research had no independent way
to falsify (the wave/plan-ownership recommendations, the prose-authoring guidance) and is reported as
sound.**

## Sources

### Primary (HIGH confidence — direct file reads and live command output this session)

- `.planning/phases/63-v0-9-2-release-prep-prep-only/63-CONTEXT.md` — full read, all 21 decisions
  and both discretion/deferred sections.
- `.planning/REQUIREMENTS.md` — full read, REL-09/REL-10/REL-11's exact text, traceability table,
  phase-mapping notes; live `sha256sum`/`wc -l`/`grep -n 'REL-09'` re-run this session.
- `.planning/STATE.md` — Active Milestone section, branch-decoy history, prior milestone close
  records (v0.9.1, v0.9.0, v0.8.0, v0.7.1, v0.7.0, v0.6.5, v0.6.4, v0.6.3).
- `CHANGELOG.md` — full read of lines 1-60, 375-410 (`## [0.6.5]` template), tail 30 lines; live
  `grep -n "^## \["` / `grep -n "^### "` / `wc -l` this session.
- `scripts/extract_changelog_section.py` — full read; `_SECTION_HEADER_RE` and `extract_section()`
  confirmed purely positional by direct inspection of the regex and loop logic (lines 54-116).
- `pyproject.toml` — lines 1-15 (version literal, line 7) and lines 33-54 (`[project.optional-
  dependencies]`, confirming `myst_parser` lives only in `docs`, never `dev`).
- `README.md` — line 347 (`**Status**` line), confirmed via live grep.
- `uv.lock` — lines 1466-1469 (`typsphinx` self-package stanza), confirmed via live grep.
- `tests/test_changelog_page_gate.py` — lines 1-80, confirming `RELEASE_VERSIONS`' current tuple
  (ending `"0.9.0"`), its preceding comment, the `MYST_PARSER_AVAILABLE`/`TYPST_AVAILABLE` skip
  gating, and the module docstring's own statement of the `docs`-extra hazard.
- `tests/test_readme_version_sync.py` — full read, confirming the exact regex and comparison logic
  D-09/SC#1's test enforcement rests on.
- `.github/workflows/ci.yml` — full read (214 lines), confirming the `test`/`lint`/`type-check`/
  `coverage` job structure, step names, and the absence of any step named "Run linters" (the source
  of the `## Contradictions Found` finding).
- `.github/workflows/release.yml` — lines 1-95, confirming the `validate` job's actual "Run linters"
  step (the step D-18's wording actually describes, in the wrong workflow) and the `create-release`
  job's `Install uv` step (D-14's subject).
- `tox.ini` — `[testenv:lint]` (lines 39-45), `[testenv:docs-html]`/`docs-pdf`/`docs` (lines 61-84),
  confirming exact commands and `extras = docs`/`extras = dev` scoping.
- Live `git` commands this session: `git branch -vv` (confirming current branch state, no decoy
  present at measurement time), `git tag -l 'v0.9.2'` (empty), `git ls-remote --tags origin | grep
  0.9` (only `v0.9.0`), `git log -1`, `git status --porcelain`.
- Live environment probes this session: `uv --version` (0.11.25), `git --version` (2.54.0), `gh
  --version` (2.98.0).
- `.planning/config.json` — confirming `workflow.nyquist_validation: true` and
  `workflow.security_enforcement: true`, both driving this document's required sections.

### Secondary (MEDIUM confidence — prior phase evidence files, read in full this session)

- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-CONTEXT.md`,
  `61-CLOSEOUT-GUARD.md`, `61-HANDOFF.md`, `61-VALIDATION.md`, `61-SC4-INVARIANTS.md`,
  `61-CI-EVIDENCE.md`, `61-CHANGELOG-EVIDENCE.md` (partial, docs-render section) — the primary
  precedent for wave shape, fence mechanics, and CI-dispatch command shapes. All read in full or in
  the specific cited sections this session.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-BUMP-EVIDENCE.md`,
  `57-CHANGELOG-EVIDENCE.md` — the primary precedent for the version-bump command sequence and the
  extractor/RELEASE_VERSIONS/tail-link mechanics. Both read in full this session.
- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-VERIFICATION.md`
  — pytest full-suite count (1543 passed, 5 skipped), cited as this phase's pre-execution baseline,
  not re-derived.
- `.planning/milestones/v0.9.1-phases/61-v0-9-1-release-prep-prep-only/61-01-PLAN.md` through
  `61-04-PLAN.md` — frontmatter (`wave`, `depends_on`, `files_modified`, `must_haves.truths`,
  `prohibitions`) read for all four plans, informing the wave-decomposition recommendation and the
  `requirements-completed: []` frontmatter pattern.
- `.planning/milestones/v0.9.0-phases/57-v0-9-0-release-prep-prep-only/57-0N-PLAN.md` frontmatter
  (all 11 plans) — read for `wave`/`depends_on` structure only, informing the "why 57 had more plans
  than 63 needs" comparison in `## Summary`.

### Tertiary (LOW confidence)

None — every claim in this document traces to either a direct file read, a live command executed
this session, or a verbatim quote from `63-CONTEXT.md`'s already-owner-accepted D-01..D-21.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — no new tooling; every tool version was probed live this session.
- Architecture (wave/plan decomposition): MEDIUM-HIGH — the recommended 4-plan/3-wave shape is a
  reasoned adaptation of Phase 61's exact precedent, not itself independently re-validated by
  execution; the planner retains full discretion per `63-CONTEXT.md`'s own Claude's Discretion note.
- Pitfalls: HIGH — six of six pitfalls are either directly reproduced from a prior phase's own
  documented near-miss (Pitfalls 1, 2, 5, 6) or discovered by this research's own direct-source-read
  cross-check (Pitfalls 3, 4).
- Code examples: HIGH — every command shape is either copied verbatim from a prior phase's own
  successful execution transcript, or newly assembled from a live read of the exact source file it
  targets this session.

**Research date:** 2026-08-30
**Valid until:** 7 days (fast-moving — this phase's own tree state, branch state, and tag/release
state are expected to change within this window; the CHANGELOG line numbers and current version
literals cited throughout this document are point-in-time measurements at research time, not
durable facts, and MUST be re-measured fresh by the plans that consume them).
