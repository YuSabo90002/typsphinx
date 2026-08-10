# Phase 46: v0.7.1 Release Prep (prep-only) - Context

**Gathered:** 2026-08-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Prep-only release work for v0.7.1: bump the version in lockstep, curate the `## [0.7.1]` CHANGELOG
entry, prove the post-bump tree green live, discharge REL-04's in-phase share, and hand off a
checklist — with **zero irreversible action taken**. Requirements: **REL-06** (prep half only) and
**REL-04** (verification-and-handoff share only; the requirement itself does not close here).

**In scope:**

- `pyproject.toml:7` — `version = "0.7.0"` → `"0.7.1"` (measured this session: still the sole
  version literal), with `uv.lock` and `README.md:342` (`**Status**: Stable (v0.7.0) - Production
  ready`) moved in lockstep and the editable-install metadata regenerated so
  `typsphinx.__version__` reports `0.7.1`.
- A curated `## [0.7.1]` entry in `CHANGELOG.md` per D-05..D-10, **plus the tail link-block
  rollover** — add the `[0.7.1]` release-tag line and advance `[Unreleased]` to `v0.7.1...HEAD`.
- The matching edit to `docs/source/changelog.rst` — which is a **new "Migrating from 0.7.0 to
  0.7.1" section**, not a release entry (D-09; the page `.. include::`s `CHANGELOG.md`, so the
  release history is already automatic).
- SC#3 live-run evidence on the post-bump tree per D-11..D-13.
- SC#4's invariant proof over the SHA-anchored full milestone diff (merge-base `87f242a`..HEAD).
- REL-04's in-phase share: verify `release.yml`'s `create-release` job carries the
  `astral-sh/setup-uv` + `Set up Python` steps (**already confirmed this session** at
  `release.yml:162-168`), and run `scripts/extract_changelog_section.py` against the new
  `## [0.7.1]` section — both recorded as *preconditions*, never as acceptance.
- SC#5 handoff: a standalone `46-HANDOFF.md` following the `41-HANDOFF.md` precedent.
- Closing-record hygiene per D-16/D-17.

**Out of scope:**

- **Any publish or otherwise irreversible action** — `git tag v0.7.1`, triggering `release.yml`,
  PyPI, the GitHub Release, opening or merging the PR. `git tag -l v0.7.1` and
  `git ls-remote --tags origin v0.7.1` must both be empty at phase close. The prep/publish fence is
  absolute (Phase 33/35/41 precedent).
- **Any `typsphinx/` code change**, including a deprecation shim for the removed `typst_authors`
  (D-03) — the prep-only fence is held even though the silent-failure mode is real.
- **The `tox-uv` → `tox-uv-bare` dependency repair** — routed to a newly inserted **Phase 45.2**
  (D-18). Inserting that phase into `ROADMAP.md` / `REQUIREMENTS.md` is a separate `/gsd-phase`
  action and is **NOT** Phase 46 work (the Phase 41 D-11 precedent for Phase 40.1).
- **PR #131 / Issue #130** — the absolute-image-URI fix stays out of v0.7.1 (D-17).
- The 10 pending todos (D-16).
- Revisiting the version number — `0.7.1` is locked by D-01.
- Editing historical CHANGELOG entries.

</domain>

<decisions>
## Implementation Decisions

Every measured value below was taken **this session (2026-08-10)** against the live tree, not from
recall. Where a measurement contradicts a prior artifact, the contradiction is stated explicitly
rather than silently corrected.

### Version number and how breakage is framed

- **D-01: The release ships as `0.7.1`.** ROADMAP SC#1 fixes it and the owner declined `v0.8.0` on
  2026-08-04. The counter-argument was stated in full before the decision and rejected: that
  2026-08-04 judgment was made when CONF-08's filename rename was the only user-visible change,
  whereas CONF-10/CONF-11/CONF-12 were added on 2026-08-10; that this project's precedent for
  breaking config removal in a patch release (`typst_output_dir` / `typst_author_params` in 0.6.2,
  `typst_toctree_defaults` in 0.6.3) covered only **inert** values, while `typst_authors` is live
  and CONF-11 changes rendering with no error at all; and that Phase 44.2 published a notice
  promising removal in a future **major** release. Owner reaffirmed `0.7.1` with all three facts on
  the table. Consequence, and the reason D-02 exists: the version number carries no warning, so the
  CHANGELOG is the only surface that can.

- **D-02: Breakage is marked three ways.** (a) The lead paragraph states plainly that this patch
  release can break a working configuration; (b) each of CONF-10 / CONF-11 / CONF-12 carries a
  `**Breaking:**` prefix on its bullet; (c) a `### Removed` section is created — the first in this
  CHANGELOG's history — to hold `typst_authors`. Rejected: lead-declaration-only (the Phase 41 D-03
  shape, which was justified there by the measured fact that *nothing* broke, a premise that does
  not hold here), and per-bullet markers without the `### Removed` section (leaves a public config
  value's disappearance without its own heading). `docs/source/changelog.rst`'s migration guide
  already uses `**Breaking:**`, so the two surfaces share vocabulary.

- **D-03: The silent failure of a leftover `typst_authors` is accepted and handled in documentation
  only.** Measured this session: `typst_authors` now returns **zero** hits across `typsphinx/`,
  `docs/source/`, `examples/` and `tests/`, and Sphinx ignores an unregistered `conf.py` variable
  without warning — so a user upgrading with `typst_authors` set loses author information silently.
  A fail-loud shim was offered (re-register the name and raise, matching the `ELEMENTS_ALLOWLIST`
  stance that unknown configuration fails loudly) and declined: Phase 46 takes no code change. The
  shim is kept as the option of record in `<deferred>`. Note this is a *stricter* reading of the
  prep-only fence than Phase 41 took — Phase 41's D-12 accepted one docstring edit — and the
  difference is deliberate, because this one would be a behaviour change.

- **D-04: The published-notice contradiction is stated in both places, split by kind.** The
  **fact** ("0.7.0's documentation announced removal in a future major release; this patch release
  removes it") goes in the CHANGELOG's `### Removed` bullet, which reaches the GitHub Release body.
  The **rationale** (LaTeX parity, per 45.1 D-F) and the rewrite steps go in the migration guide.
  This discharges 45.1 D-F's explicit instruction that "Phase 46's CHANGELOG curation can say so
  plainly".

### The `## [0.7.1]` CHANGELOG entry

- **D-05: Bullets are cut at user-visible-change granularity — 6 to 8 of them — with requirement IDs
  in trailing parentheses.** Direct continuation of Phase 33 D-09 / Phase 41 D-01. Rejected: one
  bullet per requirement (18 bullets, which would put QUA-01's docstring fix and QUA-03's planning-
  document hygiene in release notes), and a phase-level roll-up (7 bullets, but phase boundaries are
  an internal partition users cannot see, and it buries CONF-11 inside "Phase 45.1").

- **D-06: The lead paragraph's axis is "the configuration the documentation promises actually takes
  effect."** It is the project's own core-value sentence and it covers the largest share of the
  milestone's 18 requirements at once — CONF-08 (following the Quick Start now produces a PDF),
  CONF-09 (`typst_documents`' title/author reach the render), DOC-13/CONF-11/CONF-12 (the published
  template contract becomes true). Rejected: "v0.7.0's debts cleared" (the milestone-goal wording —
  accurate but told from the project's side, not the user's), and leading with the breaking-change
  warning (D-02 already places that in the same paragraph; leading with it would bury the fact that
  this release mostly repairs things that were broken).

- **D-07: CONF-08's callout names both measured facts, not just the rename.** Phase 44's SC#4
  handoff (`44-GATE-EVIDENCE-03.md` § 7) records that an unset-`typst_documents` build changes
  **both** its emitted filename (`index.typ` → `quickstartdefaultgate.typ`, derived from `project`)
  **and** its emitted structure (untemplated body → fully templated). ROADMAP SC#2's wording names
  only "the output-filename change"; the entry must carry both. Quote § 7 rather than re-deriving.

- **D-08: `### Verified` carries the same three items as 0.6.5 / 0.7.0, with the dependency claim
  scoped to runtime.** Measured this session: the milestone diff adds `myst-parser` (and transitively
  `mdit-py-plugins`) to the **`docs` extra** in `pyproject.toml:53` — a Phase 45 / DOC-12
  consequence — with no change to `[project] dependencies`. Writing the first item as "No new
  **runtime** dependencies" keeps the claim true and pre-empts a reader who diffs `uv.lock`.
  Rejected: listing `myst-parser` as a fourth item (the section exists to enumerate what did *not*
  change), and dropping the section (the last three releases all carry it).

- **D-09: `docs/source/changelog.rst` gains a "Migrating from 0.7.0 to 0.7.1" section with
  before/after code fragments.** Measured: that page is `.. include:: ../../CHANGELOG.md` with a
  hand-written "Migration Guides" tail, so the migration section is the *only* hand-written surface
  and ROADMAP SC#2's "gains the matching `0.7.1` entry" resolves to it. Three items need fragments:
  `typst_authors` → the `typst_template_function` `params` route; a project that sets `params` today
  must now enumerate all nine parameters (CONF-11's exclusivity); and a custom template that does
  not declare `lang` starts failing with `unexpected argument: lang` (CONF-12). Every existing
  Migrating section is prose bullets only — code fragments enter this page here for the first time.
  Rejected: prose-only (does not convey "write all nine") and omitting the section (incoherent
  immediately after D-02's triple marking).

- **D-10 [derived, not separately asked]: the Keep-a-Changelog section split is `### Added` /
  `### Changed` / `### Fixed` / `### Removed` / `### Verified`.** `### Removed` is new per D-02.
  The planner assigns requirements to sections; the only fixed assignment is `typst_authors`
  (CONF-10) → `### Removed`.

### SC#3 — what "green" means and where the evidence comes from

- **D-11: The branch CI run on the post-bump commit is the authority for pytest / lint / type;
  local `tox` supplies what CI does not run.** The milestone branch is already on `origin`
  (invariant #5), so pushing the post-bump commit and reading its run — including the Windows lanes,
  which caught a real cp1252 defect at the v0.7.0 close — is a **live** result, not an inherited
  one, and therefore satisfies SC#3. The full-corpus `-b typstpdf` gate and both docs builds are run
  locally. **This decision depends on Phase 45.2 landing first (D-18): local `tox` does not
  currently run at all.** Rejected: promoting the local run to the authority (never sees Windows or
  macOS), and requiring both full green runs (largest pre-release wait for the least new
  information).

- **D-12: The `ja` evidence is a single local `SPHINX_LANGUAGE=ja` docs-pdf build, not Phase 41's
  four-check glyph bar.** The bar was justified in Phase 41 by two measured facts about that
  milestone; both were re-measured here and **neither holds**: `raw(` call sites in
  `typsphinx/translator.py` are **41 before and 41 after** (`git show main:` versus the working
  tree), and the milestone diff over `typsphinx/` names no font family. What does warrant touching
  `ja` at all is CONF-12, which changes the route by which `lang` reaches a template. Rejected:
  re-running the full four-check bar (pays Phase 41's cost with none of its triggers), and skipping
  `ja` entirely (CONF-12 would reach a published artifact unexercised).

- **D-13 [correction of record]: there is nothing to remove in `typsphinx-doc-translations`, and
  the `ja` build exercises this repository's own files.** 45.1's `<deferred>` carries "the
  translations repo's copy of the `lang` workaround" as a handoff item. Measured this session via
  the GitHub API: that repository contains **no `conf.py` and no `.typ` template** — its tree is
  `.readthedocs.yaml`, `Makefile`, `locale/ja/**`, and the parent mounted as the submodule
  `typsphinx/`. The `lang` workaround existed only in `docs/source/conf.py`, which 45.1 already
  removed (the file now carries a "do not re-add that workaround" comment). `docs/source/_typst/
  custom_template.typ:64-75` declares all nine parameters including `lang`, so the docs build is
  safe on both languages. The handoff item is retired; the standing **two-repository tagging** cost
  is unaffected.

- **D-14: SC#4's invariant sweep runs over merge-base `87f242a`..HEAD.** Measured: 323 commits, and
  excluding `.planning/` the code delta is 119 files / +10,052 / −847. The `@preview` count and its
  four sync surfaces are asserted mechanically; the dependency assertion is worded per D-08.

- **D-15 [derived]: evidence is NOT written to `46-VERIFICATION.md`.** That name is reserved by the
  verifier and will be clobbered — the Phase 41 D-15/`41-RELEASE-EVIDENCE.md` precedent.

### Close-out disposition

- **D-16: All 10 pending todos are explicitly deferred, each with its reason recorded** — the
  Phase 41 D-14 shape. None relates to REL-04 / REL-06 and none blocks the release. See
  `<deferred>` for the enumerated list.

- **D-17 [correction of record]: PR #131 is NOT in v0.7.1, and `STATE.md` is wrong about it.**
  `STATE.md` states (2026-08-10 entry) that "the review was performed and PR #131 merged". Measured
  via `gh pr view 131`: `state: OPEN`, `mergedAt: null`, one review with state **`CHANGES_REQUESTED`**.
  Independently corroborated — `_track_image` appears in neither `main` nor the milestone branch, and
  the two todos the review filed (`rehomed-converted-image-collides-with-srcdir-images-dir`,
  `track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri`) describe code that exists only in
  the PR. Issue #130 therefore remains open in v0.7.1. Phase 46 corrects the `STATE.md` sentence as
  closing-record hygiene; it does not review, merge, or reopen the PR.

### Routed out of this phase

- **D-18: The `tox-uv` → `tox-uv-bare` dependency repair ships in v0.7.1, in a newly inserted
  Phase 45.2, before Phase 46.** Discovered and fully measured during this discussion; see
  `<specifics>` items 1–6 for the evidence chain. The short form: `pyproject.toml`'s `dev` extra
  depends on `tox-uv`, which is a meta package (`tox-uv-bare==1.35.2` + `uv<1,>=0.9.27`), and the
  PyPI `uv` wheel installs a **generic-linux ELF** at `.venv/bin/uv` that NixOS cannot exec. That one
  file breaks two things at once: `tox` is **completely non-functional locally** (every env exits
  127), and every test that shells out to `["uv", "run", "sphinx-build", …]` fails, because `uv run`
  prepends `.venv/bin` to PATH. Both halves of the repair were measured (items 4 and 5). The owner
  chose to land it **before** the release rather than after, accepting that `pyproject.toml` /
  `tox.ini` / `uv.lock` move shortly before the release phase, because it raises the quality of the
  very evidence SC#3 collects (D-11). **Inserting Phase 45.2 into `ROADMAP.md` and `REQUIREMENTS.md`
  is a separate `/gsd-phase` action and is not Phase 46 work.** — **Reversibility:** reversible —
  a dev-extra dependency name in two files plus the lockfile; no published contract and no runtime
  surface is touched.

- **D-19: Phase 45.2's change gets no `## [0.7.1]` CHANGELOG bullet.** It is confined to the `dev`
  extra and changes nothing for a user *of* typsphinx. Consistent with the 0.6.5-era rule that test
  and verification machinery is not user-visible. Measured mitigating fact: the only person the
  bundled `uv` actually served is someone who installs via `pip install -e ".[dev]"` **and** then
  runs a bare `tox` — `docs/source/contributing.rst:117-128` instructs `uv run tox …` everywhere, so
  the documented path already requires uv independently, and `poetry` appears nowhere in the
  repository. Under `tox-uv-bare` that person gets tox-uv's own three-option error message rather
  than a silent failure.

### Claude's Discretion

- The exact wording of the `[0.7.1]` entry, the lead paragraph's phrasing, which 6–8 bullets D-05
  resolves to, and how requirement IDs are attached.
- Which requirements land in `### Added` versus `### Changed` versus `### Fixed` (D-10 fixes only
  `typst_authors` → `### Removed`).
- The migration section's exact fragments and headings (D-09 fixes only that it exists, and which
  three items it must cover).
- Plan decomposition and ordering, and the `uv.lock` regeneration procedure (acceptance:
  `uv sync --extra dev --locked` green).
- The mechanical method for D-14's invariant sweep over the 119-file diff.
- The format and heading structure of `46-HANDOFF.md`.
- Where live-run evidence is recorded, subject to D-15.
- Whether the `RELEASE_VERSIONS` tuple in `tests/test_changelog_page_gate.py:49-63` gains `"0.7.1"`
  in this phase — the gate asserts each listed release appears in the built page, so adding it is
  mechanical but must not be done before the CHANGELOG entry exists.

### Folded Todos

None. `todo.match-phase 46` returned keyword-noise matches only; see `<deferred>`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's requirements and success criteria

- `.planning/ROADMAP.md` § "Phase 46: v0.7.1 Release Prep (prep-only)" — the five success criteria
  this phase is judged against, plus the milestone's five binding constraints.
- `.planning/REQUIREMENTS.md` § "Release and CI (REL)" — REL-06 and REL-04 verbatim, and the
  traceability rows that stay `Pending` through this phase.
- `.planning/STATE.md` § "Active Milestone (v0.7.1)" — the milestone invariants and the standing
  `--skip-ui` / api-coverage false-positive notes. **Contains one error corrected by D-17.**

### The release-prep precedent to follow

- `.planning/milestones/v0.7.0-phases/41-v0-7-0-release-automation-release-prep/41-CONTEXT.md` —
  the prep/publish fence, the version-literal census, the CHANGELOG-entry decision shape (D-01..D-05),
  and D-11's precedent for routing work into an inserted phase.
- `.planning/milestones/v0.7.0-phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md` —
  the handoff document shape SC#5 asks for.
- `.planning/milestones/v0.7.0-phases/41-v0-7-0-release-automation-release-prep/41-RELEASE-EVIDENCE.md`
  — the evidence-file shape, and the reason it is not named `41-VERIFICATION.md` (D-15).

### CHANGELOG source material handed forward by earlier phases

- `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-03.md`
  § 7 — the quotable CHANGELOG source text for CONF-08, with the measured
  `index.typ` → `quickstartdefaultgate.typ` pair and the untemplated→templated structure change (D-07).
- `.planning/phases/45.1-custom-template-parameter-contract-correction/45.1-CONTEXT.md` § D-F —
  the instruction that Phase 46's CHANGELOG state the early-removal fact plainly (D-04), and
  § `<deferred>`, whose translations-repo handoff item D-13 retires.
- `.planning/phases/44.2-typst-documents-title-and-author-consumption/44.2-CONTEXT.md` — CONF-09's
  entry-resolution work, for the title/author callout.
- `CHANGELOG.md` — the `## [0.7.0]` entry as the structural model, and the tail link block that must
  roll over.
- `docs/source/changelog.rst` — the `.. include::` plus the hand-written "Migration Guides" tail
  (D-09's target).

### REL-04's in-phase share

- `.github/workflows/release.yml:147-190` — the `create-release` job. The `astral-sh/setup-uv` +
  `Set up Python` steps are present at `:162-168` (verified 2026-08-10), with an inline comment
  naming run `30848860064` as the failure they repair.
- `scripts/extract_changelog_section.py` — the extractor to exercise against `## [0.7.1]`.
- `.planning/todos/pending/2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — REL-04's
  own record; stays pending until the publish.

### Version-literal and gate surfaces

- `pyproject.toml:7` — the sole version literal.
- `README.md:342` — `**Status**: Stable (v0.7.0) - Production ready`.
- `tests/test_readme_version_sync.py` — asserts the two agree, so both must move together.
- `tests/test_preview_version_sync.py` — the `@preview` lockstep guard over `writer.py` /
  `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`.
- `tests/test_changelog_page_gate.py:49-63` — the `RELEASE_VERSIONS` tuple.

### Standing project constraints

- `CLAUDE.md` § "Worktree-isolated execution" — mandatory per-worktree `uv sync` + `uv run` for
  every executor. **Read alongside `<specifics>` items 1–5**, which measure why `uv run` is exactly
  what triggers the local test failures until Phase 45.2 lands.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — the surfaces D-14's sweep counts.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `scripts/extract_changelog_section.py` — already committed and pytest-covered (Phase 41 D-06);
  Phase 46 only exercises it, it does not modify it.
- `tests/test_readme_version_sync.py` / `tests/test_preview_version_sync.py` — the established
  "a release-surface fact is pinned by pytest" pattern; both must stay green across the bump.
- `44-GATE-EVIDENCE-03.md` § 7 — pre-written CHANGELOG source text, so CONF-08's figures are quoted,
  not re-derived.
- `.envrc` + `flake.nix` (both git-tracked) — the devshell that provides the working nix-store `uv`.

### Established Patterns

- **Version literals:** `pyproject.toml:7` is the sole literal; `typsphinx.__version__` derives from
  `importlib.metadata`; `README.md:342` carries the human-readable status line; `uv.lock` moves in
  lockstep.
- **CHANGELOG entry shape:** lead paragraph → `### Added` / `### Changed` / `### Fixed` →
  `### Verified` → tail link block. `[0.7.0]`, `[0.6.5]`, `[0.6.4]`, `[0.6.3]` all follow it.
  D-02 inserts `### Removed` into that shape for the first time.
- **Evidence culture:** commands and their output transcribed verbatim; `human_needed` recorded
  honestly; the honest-verifier rule (abstain rather than assert without direct evidence).
- **Test-invocation convention:** newer gate modules invoke Sphinx as `sys.executable -m sphinx`
  and their docstrings state "NEVER `uv run sphinx-build`" with the exit-127 reason. 13 older test
  files still hard-code `["uv", "run", …]` — the inconsistency `<specifics>` item 5 measures.

### Integration Points

- The post-bump commit ↔ the branch CI run — D-11's evidence path. Requires the post-bump commit to
  be pushed, which is not an irreversible action and does not violate the prep/publish fence.
- `CHANGELOG.md` ↔ `docs/source/changelog.rst` ↔ `tests/test_changelog_page_gate.py` — one edit,
  three surfaces. The `.. include::` means the release history propagates automatically; only the
  migration section and the gate's version tuple are hand-maintained.
- `CHANGELOG.md` ↔ `release.yml` — the REL-04 link, live since Phase 41. The `## [0.7.1]` heading
  must exist and be non-empty before a tag is ever pushed, because the `validate` job checks it
  (Phase 41 D-09).
- Phase 46 ↔ Phase 45.2 — a cross-phase dependency introduced by D-18. D-11's local-tox half cannot
  run until 45.2 lands.

</code_context>

<specifics>
## Specific Ideas

Everything below was measured during this discussion (2026-08-10) against the live tree or the
GitHub API, not inferred.

1. **`.venv/bin/uv` is a PyPI wheel binary, and it is unrunnable on this machine.**
   `file .venv/bin/uv` → `ELF 64-bit LSB pie executable, dynamically linked, interpreter
   /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32`. NixOS has no such loader, so any exec of it
   dies with `Could not start dynamically linked executable: uv` (stub-ld), exit 127. The
   dependency chain is `pyproject.toml:33 [project.optional-dependencies] dev` → `tox-uv>=1.35,<2`
   → `tox-uv 1.35.2 requires ['tox-uv-bare==1.35.2', 'uv<1,>=0.9.27']` → the `uv` wheel ships
   `bin/uv` and `bin/uvx`. **The project's recorded diagnosis — "`uv` not on PATH for subprocess
   children", "`uv: command not found`" — is wrong**; `uv` is on PATH, it is the wrong build of it.

2. **`tox` is completely non-functional locally.** `.venv/bin/tox -e lint --notest` →
   `lint: venv> .venv/bin/uv venv …` → `Could not start dynamically linked executable` →
   `lint: FAIL code 127`. `uv.find_uv_bin()` returns `.venv/bin/uv` and consults **no environment
   variable** (its whole source was read: it walks `sysconfig` script directories, `.venv/bin`
   first). So every `tox -e …` command in `CLAUDE.md` and `docs/source/contributing.rst` —
   including `docs-html` and `docs-pdf` — has never run on this machine.

3. **nixpkgs cannot substitute for it.** `nixpkgs#tox` does not exist; `nixpkgs#python3Packages.tox`
   is **4.34.1**, below the project's `tox>=4.56,<5` floor; `nixpkgs#python3Packages.tox-uv` does
   not exist. `tox.ini` requires `tox-uv~=1.35` and sets `runner = uv-venv-lock-runner` on every
   env, so tox alone cannot evaluate the file.

4. **`TOX_UV_PATH` repairs tox without touching the project** — `tox_uv/_venv.py:222-230` reads it
   *before* `find_uv_bin()` and passes it through `shutil.which()`, so an absolute path works.
   Measured: `TOX_UV_PATH=$(command -v uv) .venv/bin/tox -e lint --notest` → all 8 envs report
   `using uv from TOX_UV_PATH: /nix/store/…-uv-0.11.25/bin/uv`, `lint: OK`, `congratulations :)`.
   This is flake.nix-expressible as `TOX_UV_PATH = "${pkgs.uv}/bin/uv";`. **It repairs tox only** —
   it cannot reach the pytest failures, which are PATH resolution inside test subprocesses.

5. **The local test failures are caused by the same file, and removing it fixes them.** Measured
   pair over `tests/test_integration_advanced.py`, `test_integration_basic.py`,
   `test_integration_multi_doc.py`, `test_integration_nested_toctree.py`, both runs under an outer
   `uv run --no-sync pytest`:

   | state | result |
   |---|---|
   | as-is (`.venv/bin/uv` present) | **42 failed, 5 passed** |
   | `.venv/bin/uv` + `uvx` moved aside (= what Phase 45.2 produces) | **47 passed** |

   With the file absent the child process resolves `/nix/store/…-uv-0.11.25/bin/uv`. `uv run`
   prepends `.venv/bin` ahead of everything, which is why wrapping in `nix develop` does **not**
   help — measured: `nix develop -c uv run --no-sync python -c "shutil.which('uv')"` still returns
   `.venv/bin/uv`. Without an outer `uv run`, the same four files pass as-is, which is why the
   `.venv/bin/python -m pytest` habit works in the main tree and why worktrees (where `CLAUDE.md`
   mandates `uv run`) hit the failures.

6. **`tox-uv-bare` alone is sufficient.** Built a scratch venv containing `tox 4.58.0` +
   `tox-uv-bare 1.36.0` with no `uv` distribution and no `bin/uv`; temporarily set
   `tox.ini`'s `requires = tox-uv-bare~=1.35`; ran with `TOX_UV_PATH` unset:
   `lint: uv-sync> /nix/store/…-uv-0.11.25/bin/uv sync --locked …` → `lint: OK` → `EXIT=0`.
   `uv-venv-lock-runner` comes from `tox-uv-bare` (the registered plugin is literally
   `tox-uv-bare-1.35.2`), and `_venv.py`'s fallback branch documents "install tox-uv-bare and ensure
   system uv is in PATH" as a supported configuration. `tox.ini` was restored (`git diff` clean).
   **Limits of this measurement, stated honestly:** the scratch venv resolved versions the project's
   `uv.lock` does not pin; only `-e lint --notest` (the provisioning layer, which is where 127 died)
   was run, not a full `docs-pdf`; and the CI side (`uv run tox` after `astral-sh/setup-uv`) was not
   measured.

7. **`typst_authors` is gone without a trace.** Zero hits across `typsphinx/`, `docs/source/`,
   `examples/`, `tests/` — the input to D-03.

8. **The v0.7.0 → HEAD diff, for D-14.** 323 commits from merge-base `87f242a`; excluding
   `.planning/`, 119 files changed, +10,052 / −847. `pyproject.toml`'s only dependency movement is
   `myst-parser>=5.0` added to the `docs` extra (`:53`); `[project] dependencies` is untouched.

9. **Owner's framing across this discussion.** At every fork the owner chose the option that keeps
   the *release tree* honest over the one that is cheapest: `0.7.1` was kept but paid for with
   triple breakage marking; the `typst_authors` shim was declined specifically to hold the
   prep-only fence; and Phase 45.2 was pulled *into* the release rather than deferred, because a
   noisy local suite degrades the evidence SC#3 rests on.

</specifics>

<deferred>
## Deferred Ideas

- **A fail-loud shim for the removed `typst_authors`** — re-register the name and raise
  `ExtensionError` (or warn) when a `conf.py` still sets it, matching the `ELEMENTS_ALLOWLIST`
  stance that unknown configuration fails loudly rather than being dropped. Declined for v0.7.1 by
  D-03 to hold the prep-only fence. Kept as the option of record; the silent-loss failure mode is
  real and measured.

- **Unifying the 13 test files that hard-code `["uv", "run", "sphinx-build", …]` onto
  `sys.executable -m sphinx`** — the project's own documented convention, already applied to the
  newer gate modules. Phase 45.2 makes those files *work* (item 5) but does not make them
  *consistent*. A follow-up worth filing, not part of 45.2's dependency swap.

- **Raising `v0.8.0` instead of `0.7.1`** — argued in full and declined by D-01. Recorded here so a
  later reader does not mistake the patch number for an oversight.

- **PR #131 / Issue #130 (absolute image URIs from `ImageConverter`/`ImageDownloader`)** — OPEN with
  `CHANGES_REQUESTED` (D-17). Out of v0.7.1. The two todos its review filed describe code that
  exists only in the PR branch, so they cannot be actioned independently of it.

### Reviewed Todos (not folded)

`todo.match-phase 46` returned 7+ candidates, all keyword noise against a release-prep phase. All 10
records in `.planning/todos/pending/` are explicitly deferred per D-16:

- `2026-07-22-add-sphinx-linkcheck-ci-job` — Future requirement LNK-01; `links.yml`'s repo-wide
  lychee check already covers the links this release adds.
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore` — forbidden by `CLAUDE.md` and by
  the milestone's own constraint #6 until the todo itself lands.
- `2026-08-04-documented-custom-template-parameter-contract-is-wrong-and-t` — DOC-13's source
  record; delivered by Phase 45.1. Should be filed to `todos/completed/` rather than deferred —
  flagged for the planner to confirm against 45.1's artifacts.
- `2026-08-04-duplicate-typst-documents-target-silently-drops-a-master` — a `typst_documents`
  defect; note Phase 44's plan `44-05` added a target-name collision guard, so this record's
  current status is worth re-measuring before it is carried again.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end` — this **is** REL-04; stays pending
  until a real tag push runs `create-release` to completion.
- `2026-08-04-typst-documents-title-author-elements-ignored` — CONF-09's source record; delivered
  by Phase 44.2. Same filing question as DOC-13's record above.
- `2026-08-05-a-master-that-is-also-a-toctree-child-is-unrepresentable` — `typst_documents`
  modelling defect, unrelated to release prep.
- `2026-08-05-shared-document-silently-dropped-from-all-but-first-master` — the per-build-not-
  per-master include-dedup ledger defect.
- `2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir` and
  `2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` — both describe
  `TypstBuilder._track_image()`, which exists only in PR #131 (D-17). Not actionable in v0.7.1.

</deferred>

---

*Phase: 46-v0-7-1-release-prep-prep-only*
*Context gathered: 2026-08-10*
