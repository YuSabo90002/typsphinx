# Phase 57: v0.9.0 Release Prep (prep-only) - Research

**Researched:** 2026-08-16
**Domain:** Release engineering for a prep-only milestone-close phase (version bump, curated
CHANGELOG, a new migration guide, live-green post-bump evidence, mechanical invariant/fence sweep,
publish handoff) - no `typsphinx/` production-code change.
**Confidence:** HIGH - this is the sixth iteration of an established pattern (Phases 23, 28, 33, 35,
41, 46, 52 all did this exact shape) and every mechanism cited below was either read from the live
source this session or executed live against the current tree.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Four bullets carry `**Breaking:**`, not two. SC#2's "exactly the two" is read as a floor
  on the two currently-missing named changes (the `_template.typ` relocation, the
  `typst_template_assets` removal), not a cap - the two `## [Unreleased]` bullets already marked
  Breaking (OUT-04 shadow-route relocation; WR-01/CR-01 pre-write validation) stay marked. -
  Reversible.
- **D-02:** The seven existing `## [Unreleased]` bullets are promoted substantially as written, and
  the three missing ones (registry headline, `typst_template_assets` removal, output relocation) are
  authored at the same granularity. Final entry roughly `### Changed` 5 + `### Fixed` 5 +
  `### Removed` 1. - Reversible.
- **D-03:** The `typst_template_assets` removal is a `### Removed` bullet, following the `## [0.7.1]`
  `typst_authors` precedent, keeping its `**Breaking:**` prefix, one-sentence reason, cross-reference
  to the output-relocation bullet, and a statement that a warning shim exists (`config-inited`
  detection). - Reversible.
- **D-04** *(derived, fixed by ROADMAP SC#2, not re-asked)*: the lead paragraph names the registry as
  the headline, states the breaking declaration in the second half of the same paragraph, and states
  that the registry itself is additive (no existing `conf.py` needs editing).
- **D-05:** `### Verified` carries the same three items as 0.7.0/0.7.1/0.8.0, unchanged. The
  built-wheel content check is recorded in evidence artifacts, not promoted into `### Verified`. -
  Reversible.
- **D-06:** Phase 57 writes `Migrating from 0.8.x to 0.9.0` in `docs/source/changelog.rst`. -
  Reversible.
- **D-07:** The new migration guide is NOT bound by a test gate (carries forward 56-CONTEXT's DOC-17
  line: history is not policed). - Reversible (a gate can be added later at no structural cost).
- **D-08:** The guide's "before" side is measured by a real build at the `v0.8.0` tag
  (`d9523ea43d884f9ce6763da0f7f8e690fe859eb4`), via `git worktree add`, not derived from records. -
  Reversible.
- **D-09:** `54.1-REVIEW.md` WR-02 ships silent - the CHANGELOG's unconditional wording stays as-is;
  no `### Known Limitations` section, no GitHub issue. - Reversible.
- **D-10:** The two `56-REVIEW.md` documentation findings are fixed in this phase (stale
  `Python 3.9+`/`Sphinx 5.0+` prerequisites across four surfaces; the dead
  `examples/advanced/README.md:270` link); `54.1-REVIEW.md` WR-01 is not. **See Pitfall 1 below - this
  work is already done on the live tree, landed 2026-08-16 in commit `70e24958`, before
  `57-CONTEXT.md`'s own commit.** - Reversible.
- **D-11:** The prerequisites correction is a prose fix only - no version-sync gate added. -
  Reversible.
- **D-12:** CI is dispatched twice - once before the bump (separates "this milestone never touched
  Windows/macOS" from "the bump broke something"), once after (SC#3's authority). - Reversible.
- **D-13** *(derived, following 52-CONTEXT D-08)*: the dispatched CI runs are the authority for
  pytest/lint/type; the gates and both docs builds are run locally. Hard sequencing constraint:
  `uv.lock` must be regenerated and committed **before** either dispatch, because every CI job in
  four workflows opens with `uv sync --extra dev --locked` (or `--locked`). **See Pitfall 2 below -
  the live count is 10 `--locked` steps, not eleven, and ruff now runs locally on this machine; the
  sequencing constraint itself is unaffected.**
- **D-14** *(derived)*: SC#3's multi-template PDF claim is discharged by re-running the existing
  permanent gate `tests/test_two_key_selection_gate.py`, not by authoring a new one.
- **D-15** *(derived, following 52-CONTEXT D-09)*: the milestone-diff sweep behind `### Verified` and
  milestone invariant #11 is anchored at the `v0.8.0` tag. Unlike Phase 52, `pyproject.toml` is not an
  empty diff this time (`[tool.setuptools.package-data]` glob widened) so the "no new runtime
  dependency" claim needs a hunk-level argument, not an empty-diff proof; the "no new `typst_*` config
  value" assertion does NOT carry over (one config value removed, one added this milestone).

### Claude's Discretion

- The exact wording of the `## [0.9.0]` entry and lead paragraph, which bullets D-02's promoted seven
  resolve to, section assignment of the three new bullets, and requirement-ID attachment (trailing
  parentheses).
- The migration guide's heading structure, number of `code-block:: text` pairs, and presentation
  order of the four breaking changes.
- Plan decomposition and ordering, and the `uv.lock` regeneration procedure.
- The mechanical method for D-15's milestone-diff sweep and the "no new runtime dependency" argument.
- Whether `"0.9.0"` is added to `RELEASE_VERSIONS` (`tests/test_changelog_page_gate.py`) in this phase
  - must not land before the CHANGELOG entry exists.
- `57-HANDOFF.md`'s format and where live-run evidence is recorded - subject to the reserved-name
  constraint: **do not name any evidence file `57-VERIFICATION.md`**.
- How many todo records the re-filing in `<specifics>` 9 produces, and the granularity of the
  `REQUIREMENTS.md` checksum.

### Deferred Ideas (OUT OF SCOPE)

- Fixing `54.1-REVIEW.md` WR-02 (the `templates_path` resolved-against-`srcdir`-not-`confdir` gap) -
  declined by D-09 and the prep-only fence.
- Fixing `54.1-REVIEW.md` WR-01 (the tripled "Custom template not found" warning) - declined by D-10;
  needs a `typsphinx/builder.py` change.
- A prerequisites version-sync gate - declined by D-11.
- A test gate over migration guides - declined by D-07.
- A `### Known Limitations` CHANGELOG section and public GitHub issues - declined by D-09, the third
  consecutive release to decline it.
- Promoting deferred items to ROADMAP backlog entries - the todo ledger is the path
  `/gsd-new-milestone` reads instead.
- All nine records currently in `.planning/todos/pending/` are reviewed-but-not-folded (see
  `57-CONTEXT.md` `<deferred>` for per-record disposition); none is folded into this phase's scope,
  including the two builder path-normalization defects filed 2026-08-16
  (`escapes-outdir-isabs-not-backslash-normalized`, `track-image-escape-branch-basename-not-normalized`
  - both `resolves_phase: unassigned`, explicitly deferred to the next milestone per an owner amendment
  recorded in `STATE.md`).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-08 | v0.9.0 is published - PyPI wheel + sdist, GitHub Release carrying the curated `## [0.9.0]` CHANGELOG section, the second-repository tag on `typsphinx-doc-translations`, and Read the Docs `stable` serving 0.9.0 on both projects. **Prep half only in this phase** - stays `[ ]` through every plan; closes at `/gsd-complete-milestone`. | Pattern 1 (version bump + editable-install regen), Pattern 2 (CHANGELOG curation, tail rollover correction, `### Removed`), Pattern 3 (migration-guide worktree-build mechanics), Pattern 4 (two-CI-dispatch procedure), Pattern 5 (SC#3's D-14 gate re-run + built-wheel content check), Pattern 6 (SC#4 invariant sweep with the pyproject.toml hunk argument), Pattern 7 (prep/publish fence + second-repo tag dispatch mechanics for the handoff) - together covering ROADMAP Phase 57's five success criteria end to end |

</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Worktree-isolated execution is the standing mode, mandatory for every executor** (not
  conditional on low parallelism): `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
  inside the executor's own worktree, then every subsequent command through `uv run`.
- **D-08's `v0.8.0`-tag build needs its OWN, second, nested `git worktree add` + its own
  provisioning** - a worktree checked out from within an already-isolated executor worktree is
  ordinary git (worktrees are siblings sharing one object database; there is no true "nesting"
  restriction), but it is a **separate** worktree from the executor's own and needs its own
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` inside it before any
  `sphinx-build` runs there - CLAUDE.md's rule applies again, once per worktree. Do not reuse the
  executor's own `.venv` to build the v0.8.0-tag checkout; that `.venv` has the CURRENT (v0.9.0-era)
  `typsphinx` editable-installed into it, which would build the "before" side with the "after" code.
- **`tox-uv-bare~=1.35`, not `tox-uv`** - deliberate NixOS ELF workaround; do not "simplify" back.
- **Do not modernize typing imports** until the filed todo lands - irrelevant to this phase's file set
  but binding project-wide.
- **Line length 88 (black); `E501` ignored in ruff.**
- **CI matrix (py312-py313 + lint + type + cov) is the authority this phase must dispatch and read**,
  per D-13.
- **The `@preview` version-sync hazard**: `codly`/`codly-languages`/`mitex`/`gentle-clues` across
  `writer.py`/`template_engine.py`/`templates/base.typ` - this phase changes none of them (confirmed
  `[VERIFIED: grep -n "@preview" typsphinx/writer.py typsphinx/template_engine.py
  typsphinx/templates/base.typ, read this session - exactly 4 occurrences in each of the two Python
  files and templates/base.typ, all four version strings identical:
  `codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`]`), so
  `tests/test_preview_version_sync.py` is a spot-check.

## Summary

This phase has no new technology to research - it repeats Phase 46's and Phase 52's own mechanism,
adapted to a milestone whose `## [Unreleased]` block is NOT empty (unlike Phase 52) and whose
`pyproject.toml` is NOT an empty diff against the prior tag (unlike every prior release-prep phase
this session verified). What Phase 57 adds beyond Phase 52's shape is D-06/D-07/D-08: a **new**
migration-guide section, deliberately built from a real `git worktree add` at the `v0.8.0` tag rather
than from records, and D-12's **two** CI dispatches rather than one (this milestone's branch has not
touched the Windows/macOS lanes since Phase 53, four phases ago).

**This research found three load-bearing corrections to `57-CONTEXT.md`'s own measurements, all
reproduced live this session and detailed in the Pitfalls section:**

1. **The CHANGELOG tail link block already carries a `[0.8.0]` line - it is not missing.** CONTEXT.md's
   specifics item 3 and D-15's aside both state "there is no `[0.8.0]` line ... worth checking whether
   the v0.8.0 release-prep phase missed it." This is false: the live tail block's first link line is
   `[0.8.0]: .../releases/tag/v0.8.0`, immediately above `[0.7.1]:` - Phase 52 added it (confirmed by
   reading `52-RESEARCH.md`'s own Pattern 2, which planned exactly this insertion). There is nothing to
   repair; the rollover is a routine insert-above-the-top-line-plus-compare-base-bump, identical in
   shape to every prior release. See Pitfall 1.
2. **D-10's entire documentation-fix task is already complete on the live tree**, landed in commit
   `70e24958` (2026-08-16T22:10:05+09:00) - **before** `57-CONTEXT.md`'s own commit
   (`4dd4997913`, 22:59:30+09:00). All four prerequisite surfaces and the dead link are already
   correct; the todo record is already in `todos/completed/`, not `todos/pending/`. See Pitfall 1.
3. **`ruff` runs locally on this machine now** - `.venv/bin/ruff` is presently a NixOS-compatible ELF
   (`ld-linux` interpreter resolves into `/nix/store/...-glibc-.../ld-linux-x86-64.so.2`, not the
   generic `/lib64/...` the still-open todo describes) and `uv run ruff check .` returns
   "All checks passed!", exit 0. D-13's own CI-is-lint-authority reasoning cites the pending todo as its
   premise; that premise is not currently true, though the underlying sequencing constraint (regenerate
   `uv.lock` before dispatch) and D-12's Windows/macOS reasons for CI dispatch are unaffected. See
   Pitfall 2.

**Primary recommendation:** Follow Phase 52's plan/wave shape (version bump / CHANGELOG curation /
migration-guide worktree-build as parallel Wave 1 plans; two CI dispatches straddling the bump commit
plus local green-tree evidence in Wave 2; SC#4 sweep and roll-up/handoff in Wave 3) with D-12's second
CI dispatch inserted as a Wave 0 (or very early Wave 1) plan that runs BEFORE the bump commit exists,
since its whole purpose is separating "already broken before this phase" from "broken by the bump."

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version-literal bump (`pyproject.toml`, `README.md`, `uv.lock`) | Release tooling (`uv`) | - | Pure packaging metadata; no application tier touched |
| Editable-install metadata regeneration | Release tooling (`uv sync --locked`) | Python runtime (`importlib.metadata`) | `typsphinx.__version__` reads installed `.dist-info`, not the literal |
| CHANGELOG curation + tail rollover | Documentation / release notes | CI (`release.yml`'s `validate` job reads it) | Human-authored prose consumed mechanically downstream |
| New migration guide (D-06/D-07/D-08) | Documentation / release notes | A second, disposable git worktree at `v0.8.0` | The "before" side is measured, not derived - a real build in an isolated checkout |
| Pre-bump CI check dispatch (D-12 run 1) | CI/CD (GitHub Actions) | - | Separates pre-existing platform breakage from bump-caused breakage |
| Post-bump CI authority dispatch (D-12 run 2) | CI/CD (GitHub Actions) | - | SC#3's authority for pytest/lint/type per D-13 |
| SC#3's goal-claim re-run (D-14) | Test / verification tier | Builder (`typsphinx/builder.py`) via compiled output | Re-runs an existing permanent gate; no new production code |
| SC#4 invariant sweep + pyproject.toml hunk argument | Release tooling / git | - | Pure `git diff`/`grep` over the milestone diff |
| Second-repository tag advance (handoff mechanics only, not executed here) | `typsphinx-doc-translations`'s own `update-pin.yml` | `/gsd-complete-milestone` | Advanced by dispatching that repository's own workflow, never by a manual clone/edit/push |
| Publish handoff (`57-HANDOFF.md`) | Planning artifact | `/gsd-complete-milestone` (consumer) | Describes the publish, does not perform it |

This phase touches no browser/frontend/API/database tier - it is release engineering plus one
documentation section. `ui.plan-gate` and `api-coverage.verify-pre` are both expected to
false-positive here per the project's own standing notes; override both if they fire.

## Standard Stack

No new library is introduced by this phase. Every tool used is already in `pyproject.toml`'s `dev`
extra, or is system tooling (`git`, `gh`).

### Core (already installed, reused as-is)

| Tool | Version (measured live this session) | Purpose | Confidence |
|------|---------|---------|--------------|
| `uv` | on PATH, bare | Lockfile regen, editable install, `uv run` | `[VERIFIED: CLAUDE.md worktree section]` |
| `black` | 26.5.1 | Formatting gate | `[VERIFIED: uv run black --version, this session]` |
| `ruff` | 0.15.20 | Lint gate - **runs locally now, see Pitfall 2** | `[VERIFIED: uv run ruff --version and uv run ruff check ., this session - "All checks passed!", exit 0]` |
| `mypy` | (dev extra) | Type-check gate | `[VERIFIED: uv run mypy typsphinx/, this session - "Success: no issues found in 8 source files"]` |
| `pypdf`, `typst-py` | already dev-extra deps | PDF/compile assertions in existing gates | `[VERIFIED: tests/test_two_key_selection_gate.py imports, read this session]` |
| `pytest` | 9.1.1 | Test runner | `[VERIFIED: pytest session header, this session]` |
| `gh` | authenticated (`YuSabo90002`) | CI dispatch, run polling, second-repo workflow dispatch | `[VERIFIED: gh auth status, this session]` |

### Alternatives Considered

None - this phase adds no dependency by design. `git diff v0.8.0..HEAD -- pyproject.toml` shows a
package-data glob change only, no `[project.dependencies]` line touched
`[VERIFIED: git diff output, this session, quoted in full in Pattern 6]`.

**Installation:** none needed - `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
provisions everything already pinned in `uv.lock`.

**Version verification:** not applicable - no third-party package version claim is made by this
phase beyond `typsphinx` itself (Pattern 1).

## Package Legitimacy Audit

**Not applicable.** This phase installs no new package; it only bumps `typsphinx`'s own version
literal and regenerates `uv.lock` against the *existing* dependency set (confirmed empty
`[project.dependencies]` diff above). Mirrors the disposition every prior release-prep phase recorded.
If a plan's `uv lock` run produces an unexpected new transitive dependency, treat that as a
`checkpoint:human-verify` trigger - SC#4's invariant 1 exists precisely to catch this.

## Architecture Patterns

### System flow - this phase's evidence pipeline

```
┌───────────────────┐   ┌────────────────────┐   ┌──────────────────────┐
│ 0. Pre-bump CI     │   │ 1. Version bump     │   │ 2. CHANGELOG curation │
│    check dispatch  │   │ pyproject.toml:7    │   │ CHANGELOG.md          │
│ (D-12 run 1, no    │   │ README.md:347       │   │ (D-01..D-05)          │
│  code change yet)  │   │ uv.lock (uv lock)    │   │ tail link-block       │
│ gh workflow run    │   │ uv sync --locked     │   │ rollover (Pitfall 1:  │
│ ci.yml on branch   │   │ -> __version__=0.9.0 │   │ INSERT above [0.8.0], │
└─────────┬──────────┘   └──────────┬───────────┘   │ NOT a "repair")        │
          │                         │                └───────────┬────────────┘
          │                         └──────────┬──────────────────┘
          │                                    ▼
          │                     ┌──────────────────────────┐   ┌────────────────────┐
          │                     │ 3. Migration guide        │   │ 4. D-14 gate re-run  │
          │                     │ docs/source/changelog.rst  │   │ (existing permanent  │
          │                     │ NEW "before" side from a   │   │  test, no new code)  │
          │                     │ SECOND git worktree at     │   └──────────┬───────────┘
          │                     │ v0.8.0 (d9523ea), own      │              │
          │                     │ uv sync + uv run (D-08)    │              │
          │                     └──────────────┬─────────────┘              │
          │                                    │                             │
          │                                    ▼                             ▼
          │                        ┌─────────────────────────────────────────────┐
          │                        │ [commit: bump + CHANGELOG + migration guide] │
          │                        └───────────────────┬───────────────────────────┘
          │                                            │
          │                                            │ push + dispatch (D-12 run 2 -
          │                                            │ SC#3's authority per D-13)
          │                                            ▼
          │                             CI: pytest/lint/type/build/integration
          │                             x {ubuntu,windows,macos} x {py312,py313}
          │                                            │
          └───── both runs' job tables cross-referenced ┤
                                                          ▼
                              ┌───────────────────────────────────────┐
                              │ 5. Local green-tree half                │
                              │ tox -e docs-html / docs-pdf             │
                              │ test_corpus_gate.py (slow, TYPST_AVAIL) │
                              │ built-wheel content check (from CI's    │
                              │ build job, or re-run locally via uv build) │
                              └───────────────────┬───────────────────────┘
                                                  ▼
                              ┌───────────────────────────────────────┐
                              │ 6. SC#4 invariant sweep + fence proof    │
                              │ git diff v0.8.0..HEAD (deps hunk-level,  │
                              │ @preview, add_config_value +1/-1)        │
                              │ git tag -l v0.9.0 / ls-remote (x2, apart) │
                              │ REQUIREMENTS.md sha256sum baseline        │
                              └───────────────────┬───────────────────────┘
                                                  ▼
                              ┌───────────────────────────────────────┐
                              │ 7. Roll-up + 57-HANDOFF.md                │
                              │ (second-repo update-pin.yml dispatch      │
                              │ mechanics described, NOT executed)         │
                              └───────────────────────────────────────┘
```

Read top-to-bottom: step 0 has no dependency on anything and should run FIRST, before any bump
commit exists - it is the "check run" D-12 needs to be meaningfully separate from the "authority
run." Steps 1/2/3 can run in parallel (disjoint files: `pyproject.toml`/`README.md`/`uv.lock` vs.
`CHANGELOG.md` vs. `docs/source/changelog.rst`); step 3's worktree build has no file dependency on 1
or 2 either. Step 4 (the D-14 gate) is a pure test re-run and can run anywhere after 1 lands, but
must land on the branch before step 0/the-second-dispatch's commit for CI's matrix to prove it too.
Step 5 is local-only and can run in parallel with the post-bump CI dispatch. Step 6 needs the merged
tree, not the CI result. Step 7 needs everything.

### Pattern 1: Version-literal bump and editable-install metadata regeneration

**What:** Move `0.8.0` -> `0.9.0` in `pyproject.toml:7` and `README.md:347`, then regenerate the
lockfile and reinstall so `typsphinx.__version__` (derived via `importlib.metadata`, not literal)
actually reports the new value.

**Verified this session:**
```
$ sed -n '7p' pyproject.toml
version = "0.8.0"
$ sed -n '347p' README.md
**Status**: Stable (v0.8.0) - Production ready
$ grep -A2 'name = "typsphinx"' uv.lock
name = "typsphinx"
version = "0.8.0"
source = { editable = "." }
```
`[VERIFIED: pyproject.toml:7, README.md:347, uv.lock (typsphinx block) - read this session]`

**The mechanism** (unchanged since Phase 46/52 - re-confirm the exact sequence at plan-write time by
reading `52-01-PLAN.md`'s Task 1, or its analogous 46 plan, rather than re-deriving):
1. `git diff v0.8.0..HEAD -- pyproject.toml` is NOT empty this milestone (see Pattern 6) - confirm no
   SECOND accidental version-shaped literal has appeared, not that the file is untouched.
2. Edit `pyproject.toml:7`, `README.md:347`.
3. `uv lock` - regenerates `uv.lock`'s own `typsphinx` block.
4. `uv sync --extra dev --locked` - `--locked` fails loudly on any lock/manifest disagreement; this
   step is what actually regenerates the `.dist-info`/`.pth` editable-install metadata.
5. `uv run python -c "import typsphinx; print(typsphinx.__version__)"` -> expect `0.9.0`.

**Guard tests that must stay green (all three confirmed passing pre-bump this session):**
```
$ uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml \
  tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v
tests/test_extension.py::test_version_matches_pyproject_toml PASSED
tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject PASSED
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED
5 passed in 0.05s
```
`[VERIFIED: command run this session against the pre-bump tree]`. These three modules re-parse
`pyproject.toml`/README via `tomllib`/regex independently of `importlib.metadata`, so they are
genuine drift guards, not tautologies.

**Do not run `tox -e py312` locally** - standalone-CPython-3.12 downloads on this NixOS machine hit
the stub-loader rejection (unchanged from Phase 46/52's own documented pitfall). Use `uv run pytest`
directly for local spot-checks; CI is the matrix authority (D-13).

### Pattern 2: CHANGELOG curation, and the tail-rollover CORRECTION (Pitfall 1)

**Live-read this session, `CHANGELOG.md:1-83`:** `## [Unreleased]` currently holds `### Changed` (2
bullets, OUT-04 shadow-route relocation and WR-01/CR-01 pre-write validation, both already
`**Breaking:**`) and `### Fixed` (5 bullets: XREF-05, BLD-07, BLD-08, BLD-09, IMG-03), followed by
`### Planned for Future Releases` (5 items, unchanged scratch list) - matching `57-CONTEXT.md`'s D-02
measurement exactly, quoted here for the planner's direct use:

```
### Changed

- **Breaking: the `<srcdir>/base.typ` shadow-template route moved to
  `<srcdir>/_typst/base.typ` (OUT-04).** ... there is **no
  build-time warning** for this relocation, so this changelog entry is the only place it is
  announced.

- **Breaking: template layout is now validated before anything is written (WR-01, CR-01).** ...
  If you do nothing, the build fails with a message naming the offending registry key, its resolved
  bundle directory, and the colliding entry ...
```
`[VERIFIED: CHANGELOG.md:9-31, read in full this session]`

**`## [0.8.0]`'s own structure is the model to copy** (lead paragraph -> `### Added`/`### Changed`
(none had a candidate at 0.8.0; this release DOES via `### Removed`) -> `### Fixed` -> `### Verified`
-> tail link block).

**`### Removed`'s exact model, `## [0.7.1]`'s `typst_authors` entry, quoted verbatim
(`[VERIFIED: CHANGELOG.md, sed range for the 0.7.1 section, read this session]`):**
```
### Removed

- **Breaking:** the `typst_authors` config value is removed (CONF-10) -- 0.7.0's documentation
  announced its removal in a future major release; this patch release removes it now.
  `typst_authors` is an unregistered `conf.py` variable that Sphinx ignores without any warning, so
  a project that still sets it loses its author information silently. See the migration guide for
  the `typst_template_function` `params["authors"]` rewrite; there is no deprecation shim.
```
Per D-03, the `typst_template_assets` bullet inverts the last clause - a warning shim DOES exist. The
exact warning text to cite (`[VERIFIED: typsphinx/removed_config.py:34-42, read this session]`):
```python
"typst_template_assets": (
    "'typst_template_assets' was removed in v0.9.0 and is now ignored. "
    "Every used template's bundle directory (the resolved template "
    "file's parent) is copied wholesale to the output tree, so MORE "
    "files now reach the output than the explicit list used to select "
    "-- no asset list is needed any more."
),
```
This message ALREADY says "removed in v0.9.0" - it was written with this exact release in mind - and
the CHANGELOG's `### Removed` bullet should read consistently with it, not restate a different reason
independently.

**`### Verified`'s exact three-item model, unchanged across 0.7.0/0.7.1/0.8.0, quoted verbatim
(`[VERIFIED: CHANGELOG.md:148-153 (the 0.8.0 section), read this session]`):**
```
### Verified

- No new **runtime** dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.
```
D-05 says this stays unchanged wording for 0.9.0 too. The first bullet's supporting evidence is now a
hunk-level argument, not an empty diff - see Pattern 6.

**THE TAIL LINK BLOCK - CONTEXT.md's claim is factually wrong; do not act on it as written.**
Live-read this session, `CHANGELOG.md` tail (`[VERIFIED: tail -30 CHANGELOG.md, read this session]`):
```
[0.8.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
[0.7.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.0
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.8.0...HEAD
```
The `[0.8.0]` line **exists** and is the topmost link line - `57-CONTEXT.md`'s specifics item 3 and
D-15's aside both assert "the tail link block ends at `[0.7.1]`... there is no `[0.8.0]` line...
worth checking whether the v0.8.0 release-prep phase missed it." This is disproven directly: Phase
52's own `52-RESEARCH.md` (read this session) planned exactly this insertion in its Pattern 2
("insert `[0.8.0]: .../releases/tag/v0.8.0` immediately above the `[0.7.1]:` line"), and the live tree
shows it landed. **This phase's actual tail-block task is a plain, routine rollover with nothing to
repair:**
1. Insert `[0.9.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.0` immediately above
   the current `[0.8.0]:` line.
2. Change `[Unreleased]`'s compare base from `v0.8.0...HEAD` to `v0.9.0...HEAD`.

**`scripts/extract_changelog_section.py`'s exact requirement, read in full this session:** purely
positional extraction - first line matching `^## \[(?P<version>[^\]]+)\]` where the captured version
equals the requested string, body runs to (not including) the next such heading or EOF, stripped of
leading/trailing blank lines; raises `RuntimeError` (exit 1, stderr message) if no heading matches or
the body is empty after stripping `[VERIFIED: scripts/extract_changelog_section.py, read in full this
session]`. `release.yml`'s `validate` job calls exactly this script
(`uv run python scripts/extract_changelog_section.py "$VERSION" >/dev/null`) and fails the whole
release before `build`/`publish-pypi` if it exits non-zero
`[VERIFIED: .github/workflows/release.yml:64-71, read this session]`. `create-release`'s "Generate
release notes" step calls the same script a second time to build `release_notes.md`, appending an
"## Installation" `pip install typsphinx==${TAG#v}` block
`[VERIFIED: .github/workflows/release.yml:186-197, read this session]`. Neither job reads
`docs/source/changelog.rst` at all - only `CHANGELOG.md`.

**`tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` tuple, read in full this session:**
currently 14 entries, `"0.4.1"` through `"0.8.0"`
`[VERIFIED: tests/test_changelog_page_gate.py:43-58, read this session]`. The comment above it
(line 41-42) already says "the 14 releases the published page was frozen without (0.4.4 through
0.8.0, inclusive)" - this comment must move to 15/`0.9.0` alongside the append. **Ordering
constraint, re-confirmed:** the append is only valid once `## [0.9.0]` exists in `CHANGELOG.md` -
`TestChangelogPageContentCoverage`/`TestChangelogIncludeCompilesToPdf` are both gated behind
`myst_parser`/`typst` availability and skip silently under a plain `dev`-only environment - run with
`uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` and check the skip
count is `0`.

### Pattern 3: The migration guide's "before" side, D-08's real worktree build

**`docs/source/changelog.rst`'s existing shape to copy** (`Migrating from 0.7.x to 0.8.0`, 343-line
file overall, read in full this session): a three-item before/after `code-block:: text` pattern per
breaking change (output shape; target-as-path reversal; the collision hard error), one item stated
with "no action needed" prose (a fourth, non-breaking behavior fix), and a closing disambiguation
paragraph plus a `:doc:` cross-reference to `/user_guide/output_layout`
`[VERIFIED: docs/source/changelog.rst:1-77, read in full this session, quoted at length above in this
document's tool-call transcript]`. The new `Migrating from 0.8.x to 0.9.0` section is inserted
directly above this one (most-recent-first, matching the existing `0.7.0 to 0.7.1` section's position
below it).

**D-08's exact mechanism, following this project's own precedent idiom
(`tests/test_corpus_gate.py`'s `checkout_pre_fix_translator()` helper,
`[VERIFIED: 15-02-PLAN.md:47, read this session]`; also
`[VERIFIED: 15-02-PLAN.md:109, read this session]`: `git worktree add --detach <dir> <ref>`, never
`git stash`):**
```bash
# From the executor's OWN (already-isolated) worktree:
git worktree add --detach /tmp/typsphinx-v080-before v0.8.0
cd /tmp/typsphinx-v080-before
# THIS is a SEPARATE checkout with its own typsphinx/ source tree at the v0.8.0 tag.
# CLAUDE.md's rule applies AGAIN, here, independently of the executor's own provisioning:
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run sphinx-build -b typst <fixture-source> <build-dir>
# ... record the emitted file tree verbatim (e.g. `find <build-dir> -type f | sort`, and the
# content of the top-level wrapper file) as the "before" side in an evidence artifact ...
cd - && git worktree remove --force /tmp/typsphinx-v080-before
```
**Verified this session, the tag resolves correctly and is an ancestor of the current HEAD:**
```
$ git rev-parse v0.8.0
d9523ea43d884f9ce6763da0f7f8e690fe859eb4
$ git merge-base --is-ancestor v0.8.0 HEAD && echo "v0.8.0 is ancestor"
v0.8.0 is ancestor
```
`[VERIFIED: git rev-parse/merge-base output, this session]`

**Fixture candidate, not fixed by decision (Claude's Discretion), but a strong, verified candidate:**
`tests/roots/test-basic/` is byte-identical between `v0.8.0` and `HEAD`
(`[VERIFIED: git diff v0.8.0..HEAD --stat -- tests/roots/test-basic/, this session - no output; and
`git show v0.8.0:tests/roots/test-basic/conf.py` vs. the live file, both read this session, byte-for-
-byte identical]`). It carries a default (no custom `typst_template`) `typst_documents` entry, which
means a build at `v0.8.0` exercises the OLD default single-shared-`_template.typ` layout, and the same
fixture built at `HEAD` exercises the NEW `_template/<key>/<file>` bundle layout - "the same fixture"
D-08 asks for, literally. This is a recommendation, not a locked choice; the planner may substitute a
purpose-built fixture instead if the migration guide's chosen presentation needs more content than
`test-basic`'s single bare document provides.

**What this pattern is NOT:** it is not a git-archive comparison (the alternative method Phase 43 used
for its own before/after, `[VERIFIED: 43-GATE-EVIDENCE-05.md:603-604, read this session]` - "No
`git worktree add` was used ... the pre/post-fix sides were `git archive` exports"). D-08 explicitly
asks for a worktree, not an archive export, because the migration guide needs a REAL, buildable
checkout (a `git archive` export has no `.git`, so it cannot be `uv sync`'d with the same
editable-install mechanism Pattern 1 depends on).

### Pattern 4: The two-CI-dispatch procedure (D-12), separated and evidenced

**Live measurement of the branch's CI history, this session, matching `57-CONTEXT.md` closely (small,
expected drift - see Pitfall 3):**
```json
[{"conclusion":"success","createdAt":"2026-08-15T12:30:25Z","databaseId":31884774067,
  "event":"workflow_dispatch","headSha":"35ee8a0...","status":"completed"},
 {"conclusion":"success","createdAt":"2026-08-15T08:56:07Z","databaseId":31875707734,
  "event":"workflow_dispatch","headSha":"d1eff100...","status":"completed"},
 {"conclusion":"failure","createdAt":"2026-08-15T08:48:09Z","databaseId":31875380355,
  "event":"workflow_dispatch","headSha":"9172aa1c...","status":"completed"}]
```
`[VERIFIED: gh run list --workflow=ci.yml --branch gsd/v0.9.0-per-document-templates --limit 5 --json
databaseId,headSha,event,status,conclusion,createdAt, this session]`. The most recent full CI run
(`31884774067`, 2026-08-15) predates Phases 54, 54.1, 55, and 56 entirely. Branch-ahead count measured
**190** commits ahead of `origin/gsd/v0.9.0-per-document-templates`
`[VERIFIED: git rev-list --count origin/gsd/v0.9.0-per-document-templates..HEAD, this session - `190`,
vs. CONTEXT.md's `188`: two more commits landed between context-gathering and this research, expected
drift per the same pattern `52-RESEARCH.md` documented for its own branch-ahead figure]`.

**`ci.yml`'s trigger block, unchanged from every prior release-prep phase's own finding:**
```
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
```
`[VERIFIED: .github/workflows/ci.yml:3-8, read this session]` - `workflow_dispatch` is genuinely the
only trigger this branch can use without opening a PR (out of scope, prep/publish fence).

**D-12's two-run shape mirrors `46-CONTEXT.md` D-23 exactly (read this session,
`46-RESEARCH.md:98-101`): "Run 1 carries [pre-bump state] ... Run 2 carries the bump and the CHANGELOG
entry and IS SC#3's authority."** Applied to Phase 57:

- **Run 1 (pre-bump check run) - dispatch as early as possible, before any bump/CHANGELOG/migration-
  guide commit exists on the branch:**
  ```bash
  git push origin HEAD:refs/heads/gsd/v0.9.0-per-document-templates
  gh workflow run ci.yml --ref gsd/v0.9.0-per-document-templates
  gh run list --workflow=ci.yml --branch gsd/v0.9.0-per-document-templates \
    --limit 5 --json databaseId,headSha,event,status
  # poll until a workflow_dispatch run's headSha == the pushed SHA; record RUN_ID_1
  gh run watch "$RUN_ID_1"
  gh run view "$RUN_ID_1" --json jobs
  ```
  Purpose: confirm (or discover a regression in) the Windows/macOS lanes for everything Phases 54,
  54.1, 55, 56 shipped, independent of anything this phase changes.

- **Run 2 (post-bump authority run) - dispatch after Patterns 1-3's commits land:**
  ```bash
  git push origin HEAD:refs/heads/gsd/v0.9.0-per-document-templates
  gh workflow run ci.yml --ref gsd/v0.9.0-per-document-templates
  gh run list --workflow=ci.yml --branch gsd/v0.9.0-per-document-templates \
    --limit 5 --json databaseId,headSha,event,status
  gh run watch "$RUN_ID_2"
  gh run view "$RUN_ID_2" --json jobs
  ```
  Purpose: SC#3's authority for pytest/lint/type per D-13.

**Job-name set to expect all-`success` on (12 jobs total), read this session
(`[VERIFIED: .github/workflows/ci.yml:11-206, read in full this session]`):** `test` (6 matrix lanes -
`{ubuntu,windows,macos}-latest` x `{3.12,3.13}`), `lint` (1), `type-check` (1), `coverage` (1),
`build` (1, includes the "Verify wheel carries the template bundle" step - see Pattern 5), `integration`
(2 lanes - `{basic,advanced}` example builds). Record both run IDs, their URLs, and the full job table
verbatim in evidence, exactly as `52-CI-EVIDENCE.md` did for its (single) run.

Precedent shows this can legitimately take MORE than two attempts if a run goes RED - Phase 52's own
evidence recorded a first RED run (8/12), a second at 11/12, and a third at 12/12 before acceptance
(`[VERIFIED: 52-HANDOFF.md:24-28, read this session]`). Plan for this - do not assume run 2 is
necessarily the final dispatch.

### Pattern 5: SC#3's remaining halves - the D-14 gate re-run and the built-wheel content check

**D-14's exact existing gate, read in full this session:**
`tests/test_two_key_selection_gate.py::TestTwoKeySelectionGate::test_the_two_templates_produce_different_pdfs`
`[VERIFIED: tests/test_two_key_selection_gate.py:145-157, read this session]`:
```python
def test_the_two_templates_produce_different_pdfs(self, build):
    """
    Manual companion check: 54-VALIDATION.md's Manual-Only
    Verifications table names "two visibly different templates"
    (TPL-02) as owner-verified -- a byte comparison cannot judge
    "visibly different" rendering (different fonts/margins), only that
    the bytes themselves differ, which is what this test asserts.
    """
    master_bytes = build["master_pdf"].read_bytes()
    memo_bytes = build["memo_pdf"].read_bytes()
    assert master_bytes != memo_bytes, (...)
```
**Precise nuance for the planner:** this test's own assertion is a byte-inequality check, not a
PDF-metadata (page-size/font-size) assertion. The two-way visual difference is baked into the fixture
templates themselves, quoted verbatim
(`[VERIFIED: tests/fixtures/two_key_selection_gate/_typst/report/base.typ:18-19` and
`tests/fixtures/two_key_selection_gate/_typst/memo/base.typ:26,31, read in full this session]`):
report template sets `paper: "a4"` / `set text(size: 11pt, ...)`; memo template sets
`paper: "us-letter"` / `set text(size: 14pt, ...)`. `sphinx-build -b typstpdf` over this fixture's
`conf.py` (`typst_document_templates = {"report": ..., "memo": ...}`, three `typst_documents` entries
across two keys) produces `master.pdf` (report-templated) and `memo.pdf` (memo-templated) which the
gate proves differ. Re-run this gate on the post-bump tree; record the transcript. The planner owns
whether an additional standalone project transcript is worth the cost on top (D-14 leaves this open).

**The built-wheel content check, SC#3's own name for it, read in full this session:**
```yaml
# .github/workflows/ci.yml, build job, "Verify wheel carries the template bundle" step
# BLD-05/D-13: the editable install used everywhere else in CI cannot detect a narrowed
# package-data glob -- it never packs a wheel...
uv run python -c "
import glob, sys, zipfile
wheel = sorted(glob.glob('dist/*.whl'))[-1]
names = zipfile.ZipFile(wheel).namelist()
target = 'typsphinx/templates/README.md'
if target not in names:
    print(f'FATAL: {target!r} is missing from {wheel!r}. ...'); sys.exit(1)
print(f'OK: {target!r} found in {wheel!r}')
"
```
`[VERIFIED: .github/workflows/ci.yml:127-160, read in full this session]`. This step already runs
inside CI's `build` job (which is part of both dispatches - Pattern 4) - re-running it post-bump is
therefore "already happens for free" as long as run 2's `build` job is inspected and its "Verify
wheel..." step output is captured for evidence, matching SC#3's explicit naming of "Phase 54's
built-wheel content check" as something to re-prove. A local-only re-run (`uv build` then the same
inline zipfile check) is also possible if the plan wants a local-evidence copy in addition to CI's.

### Pattern 6: SC#4's invariant sweep - the pyproject.toml hunk-level argument (this milestone's new work)

**All commands re-run live this session, matching `57-CONTEXT.md`'s D-15 figures exactly:**
```
$ git diff v0.8.0..HEAD --stat -- . ':(exclude).planning' | tail -1
163 files changed, 11262 insertions(+), 1615 deletions(-)
$ git diff aed773c9..HEAD --stat -- . ':(exclude).planning' | tail -1
163 files changed, 11262 insertions(+), 1615 deletions(-)
$ git rev-list --count v0.8.0..HEAD
272
$ git rev-parse origin/main
aed773c9807ab871468b1b2a7e1ec36b54e82907
$ git merge-base origin/main HEAD
aed773c9807ab871468b1b2a7e1ec36b54e82907
```
`[VERIFIED: git diff/rev-list/rev-parse/merge-base output, this session - identical shortstat at both
anchors, confirming the four intervening commits are planning/docs only]`.

**The `pyproject.toml` hunk (NOT an empty diff this milestone), quoted in full, this session:**
```diff
$ git diff v0.8.0..HEAD -- pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index 8eb0a914..f1cddfc4 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -70,7 +70,11 @@ include = ["typsphinx*"]
 namespaces = false

 [tool.setuptools.package-data]
-"typsphinx" = ["templates/*.typ"]
+# Recursive glob is load-bearing (BLD-05, D-12): a flat `templates/*` would
+# silently drop a future `templates/fonts/x.otf` from the wheel. Narrowing
+# this glob back down is caught by the wheel-content check in
+# .github/workflows/ci.yml's `build` job, not by this comment alone.
+"typsphinx" = ["templates/**/*"]

 [tool.pytest.ini_options]
```
`[VERIFIED: git diff v0.8.0..HEAD -- pyproject.toml, this session]`. **The hunk-level argument for
`### Verified`'s "no new runtime dependency" bullet:** this is the ENTIRE `pyproject.toml` diff for the
milestone - the change is confined to `[tool.setuptools.package-data]`'s glob pattern, touching zero
lines under `[project] dependencies` or `[project.optional-dependencies]`. State this explicitly (cite
the hunk, note it is the whole diff, note neither section it touches), rather than relying on an
empty-diff claim the way every prior release-prep phase could.

**The `add_config_value` invariant does NOT carry over unexamined - one removed, one added:**
```
$ git diff v0.8.0..HEAD -- typsphinx/__init__.py | grep add_config_value
-    app.add_config_value("typst_template_assets", None, "html", [list, type(None)])
+    app.add_config_value("typst_document_templates", {}, "html", [dict])
```
`[VERIFIED: git diff v0.8.0..HEAD -- typsphinx/__init__.py | grep add_config_value, this session]`.
This is the milestone's own headline feature (the registry), so "no new `typst_*` config value" is
NOT the correct claim to make for 0.9.0's `### Verified` (D-15 explicitly says so); the correct claim
stays the unchanged D-05 three-item list, and this one-removed/one-added fact belongs in the
CHANGELOG's own `### Removed` bullet and lead paragraph instead, not in `### Verified`.

**`@preview` count, unchanged:**
```
$ grep -c "@preview" typsphinx/templates/base.typ
4
```
`[VERIFIED: grep output, this session]`.

**A genuine positive control for the `@preview` invariant** (following `52-RESEARCH.md`'s own Pattern
5 reasoning, which this research endorses as still the right shape): cite
`tests/test_preview_version_sync.py::test_all_four_packages_declared`'s own historical catch (the
v0.6.3-era `custom.typ` three-milestones-behind incident, per `STATE.md`) as evidence the detector
fires on a real violation, rather than merely re-stating the current clean count.

**`typsphinx/` production-code diff for the fence proof (SC#4's other half):**
```
$ git diff v0.8.0..HEAD --stat -- typsphinx/ | tail -5
typsphinx/template_registry.py |  529 ++++++++++++++++
typsphinx/templates/README.md  |   33 +
typsphinx/translator.py        |  178 +++++-
typsphinx/writer.py            |  184 ++++--
8 files changed, 2112 insertions(+), 346 deletions(-)
```
`[VERIFIED: git diff v0.8.0..HEAD --stat -- typsphinx/, this session]`. Unlike Phase 52's fence proof
(which asserted `typsphinx/` was UNCHANGED by the release-prep phase's own diff, i.e.
`v0.7.1..HEAD-at-Phase-52`), Phase 57's SC#4 fence proof must be scoped correctly: it is about THIS
PHASE not touching `typsphinx/`, not about the whole milestone (the whole milestone obviously changed
`typsphinx/` extensively - that is the milestone's content). Run
`git diff <phase-57-start-SHA>..HEAD -- typsphinx/` (empty expected) at phase close, not
`git diff v0.8.0..HEAD -- typsphinx/` (which is deliberately non-empty and correct).

### Pattern 7: The prep/publish fence - exact command list, and the second-repository tag's dispatch mechanics for the handoff

**Forbidden (irreversible), unchanged from every prior release-prep phase:**
- `git tag v0.9.0` (or any tag), locally or on `origin`.
- Triggering `.github/workflows/release.yml` as a real run.
- `pip install --upload` / `twine upload` / any PyPI publish action.
- Creating a GitHub Release.
- Opening OR merging a pull request.
- Advancing the `typsphinx-doc-translations` submodule pin or pushing a tag there.
- Flipping REL-08's checkbox or Traceability row in `REQUIREMENTS.md` (the `phase.complete` auto-flip
  hazard - fired at four consecutive release-prep closes per `57-CONTEXT.md`'s own D-05 language;
  verify this does not fire, revert if it does).

**Permitted (reversible), exercised by this phase:** editing tracked files; `git commit`;
`git push origin HEAD:refs/heads/gsd/v0.9.0-per-document-templates` (plain fast-forward);
`gh workflow run ci.yml --ref <branch>` (twice, per D-12); `uv lock`/`uv sync`/`tox -e <env>`/`pytest`;
reading/hand-running `scripts/extract_changelog_section.py` (no side effects, per its own docstring).

**Verification shape (two independent observations, at two separate moments):**
```
$ git tag -l v0.9.0
(empty)
$ git ls-remote --tags origin v0.9.0
(empty)
```
`[VERIFIED: both commands run this session - both silent/empty, exit 0]`. Repeat at a second, later
moment; record both timestamps in two separate evidence files (the roll-up and the handoff), exactly
as every prior release established.

**The `REQUIREMENTS.md` checksum guard SC#4 explicitly asks for**, following `52-HANDOFF.md`'s own
mechanism: record `sha256sum .planning/REQUIREMENTS.md` and REL-08's exact two lines (checkbox +
Traceability row) verbatim, EARLY in this phase - before any closeout automation runs - so a later
diff has something to compare against, and revert-by-hand if `phase.complete` flips it.

**The second-repository tag's dispatch mechanics (for `57-HANDOFF.md`'s checklist item; NOT executed
by this phase):** `typsphinx-doc-translations`'s `update-pin.yml`, read in full this session from its
archived staged copy `[VERIFIED:
.planning/milestones/v0.6.4-phases/30.1-translations-repository-japanese-rtd-site/translations-repo/.github/workflows/update-pin.yml,
read in full this session]`, runs on `schedule: "0 6 * * *"` and `workflow_dispatch: {}`. It advances
the submodule pin to the tracked branch's tip, regenerates the `.pot`/`ja` `.po` catalogs, and
commits+pushes only on a substantive change - it does NOT itself create a `v0.9.0` tag on that
repository; that is a separate, subsequent manual step. **Confirmed live this session that the
`workflow_dispatch` route genuinely works on this exact repository** (not merely documented -
observed recent runs):
```
$ gh run list --repo YuSabo90002/typsphinx-doc-translations --workflow=update-pin.yml --limit 5
completed  success  ...  main  schedule           31932179043  25s  2026-08-16T06:45:21Z
completed  success  ...  main  schedule           31870171225  27s  2026-08-15T06:43:56Z
completed  success  ...  main  workflow_dispatch  31861094950  25s  2026-08-15T03:09:56Z
completed  success  ...  main  schedule           31780647799  25s  2026-08-14T07:37:30Z
completed  success  ...  main  schedule           31678676785  24s  2026-08-13T07:39:36Z
```
`[VERIFIED: gh run list output, this session - both scheduled and workflow_dispatch-triggered runs
succeed regularly]`. `57-HANDOFF.md`'s checklist item for this step should read:
`gh workflow run update-pin.yml --repo YuSabo90002/typsphinx-doc-translations`, then poll/watch the
run the same way as Pattern 4, then separately push a `v0.9.0` tag on that repository once the pin
commit lands - matching the phrasing in the additional_context ("dispatching that repository's own
`update-pin.yml` rather than by hand").

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CHANGELOG -> GitHub Release body extraction | A second parser or shell one-liner | `scripts/extract_changelog_section.py` (already committed, pytest-covered) | The ONE committed implementation both `validate` and `create-release` call |
| Multi-template PDF fixture | A new fixture from scratch | `tests/fixtures/two_key_selection_gate/` | Already satisfies "two differently-typeset PDFs" (a4/11pt vs us-letter/14pt), already permanent, already gated |
| "Before" side of the migration guide | Deriving prose from records/memory | A real `git worktree add --detach <dir> v0.8.0` build (D-08) | This project's own established idiom (`checkout_pre_fix_translator`, Phase 15); records can be stale, a real build cannot |
| CI dispatch and polling | A custom polling script | `gh workflow run` + `gh run list --json` + `gh run watch` + `gh run view --json jobs` | Already the established idiom across four prior release-prep phases |
| Version-sync guarding | A new ad-hoc script | The three existing pytest modules (`test_extension.py`, `test_readme_version_sync.py`, `test_preview_version_sync.py`) | Already exist, already pass pre-bump this session |
| Second-repository pin advance | A manual clone/edit/commit/push | `typsphinx-doc-translations`'s own `update-pin.yml`, dispatched | Confirmed live, working, self-contained in that repository |

**Key insight:** every mechanism this phase needs already exists in the repo or a sibling repository,
proven across five to six prior release-prep phases. The two genuinely new artifacts are the migration
guide's prose (Pattern 3) and the pyproject.toml hunk-level argument (Pattern 6) - both new WRITING,
not new tooling.

## Common Pitfalls

### Pitfall 1: Acting on `57-CONTEXT.md`'s two stale/false measurements as if they were still true

**What goes wrong:** A plan that (a) treats the CHANGELOG tail block as "missing a `[0.8.0]` line to
repair" invents a task that does not exist (the line is already there - inserting a SECOND `[0.8.0]`
line, or investigating a non-existent omission, wastes a task and risks a duplicate-link lint
failure), and (b) treats D-10's documentation fixes as still-open work re-does already-complete,
already-committed work, or worse, silently reverts the already-correct prose back toward what
`57-CONTEXT.md`'s own D-10 discussion describes fixing FROM.

**Why it happens:** `57-CONTEXT.md` states both as present-tense measurements ("There is no `[0.8.0]`
line"; "The two `56-REVIEW.md` documentation findings are fixed in this phase") taken "this session
(2026-08-16)" - but the fix commit (`70e24958`, 22:10:05+09:00) landed BEFORE `57-CONTEXT.md`'s own
git commit (`4dd4997913`, 22:59:30+09:00)
`[VERIFIED: git log -1 --format="%H %cI %s" -- <each file>, this session - both timestamps quoted
verbatim]`, and the `[0.8.0]` tail-line claim appears to be a plain measurement error (Phase 52's own
`52-RESEARCH.md`, read this session, documents planning exactly that insertion).

**How to avoid:**
- For the tail block: perform ONLY the routine `[0.9.0]` insert-above-top-line + compare-base bump
  described in Pattern 2. Do not add a search for a missing historical entry to the plan.
- For D-10: before writing any task, run
  `grep -n "Python 3\.9\|Sphinx 5\.0" -r --include="*.rst" --include="*.md" .` (excluding
  `.planning/` and `CHANGELOG.md`'s own historical entries) and confirm it returns nothing under
  `docs/source/`, `examples/`. **Confirmed empty this session**
  `[VERIFIED: repo-wide grep, this session - two hits total, both inside `CHANGELOG.md`'s own
  historical `## [0.4.x]`-era prose (lines 1023, 1152), which is explicitly out of scope per
  "Editing historical CHANGELOG entries ... is carried forward unchanged"]`. Also confirm
  `examples/advanced/README.md:270` already reads
  `../../docs/source/user_guide/configuration.rst` (the correct path)
  `[VERIFIED: sed -n '270p' examples/advanced/README.md, this session]`, and that
  `.planning/todos/completed/2026-08-16-stale-version-prerequisites-and-dead-config-link-in-published-docs.md`
  exists (it does) while the matching `todos/pending/` file does NOT (confirmed:
  `[VERIFIED: ls .planning/todos/pending/ | sort, this session - 9 files, none matching this name]`).
  If the planner still wants a task here, frame it as a VERIFICATION step ("confirm D-10's fix already
  holds, cite it as evidence") rather than a fix step.

**Warning signs:** A plan whose `files_modified` includes `docs/source/installation.rst`,
`examples/basic/README.md`, `examples/advanced/README.md`, or `docs/source/contributing.rst` for a
prerequisites-text change - none of these should need editing for D-10's stated purpose (they are
already correct).

### Pitfall 2: Treating `ruff` as unrunnable locally without re-checking, and mis-stating the `--locked` step count

**What goes wrong:** A plan (or evidence file) that repeats "`ruff` cannot execute on this machine"
verbatim from `57-CONTEXT.md`'s D-13 without re-testing misses that this is now measurably false, and
loses a cheap local double-check opportunity ahead of the CI dispatch. Separately, D-13 states
"`--locked` appears in eleven steps across four workflows" - the live count is **10**.

**Why it happens:** The premise traces to a still-open pending todo dated 2026-08-11
(`2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`), and the user's own auto-memory index
still says "ruff の ELF 問題だけ現存" as of 2026-08-14. Both may have been accurate on their own
dates; this session's live re-test contradicts them:
```
$ file .venv/bin/ruff
.venv/bin/ruff: ELF 64-bit LSB pie executable, x86-64, ..., interpreter
/nix/store/8kvxvr3pmsypxiypq4g8zy13glnfr7nx-glibc-2.42-67/lib/ld-linux-x86-64.so.2, ..., stripped
$ uv run ruff check .
All checks passed!
$ echo $?
0
```
`[VERIFIED: file and uv run ruff check . output, this session - the interpreter path is a real
NixOS glibc dynamic linker, NOT the generic `/lib64/ld-linux-x86-64.so.2` the pending todo's own
"Problem" section quotes as the failure signature]`. The pending todo's own file (read in full this
session) is dated 2026-08-11 and was never updated to reflect this; whatever changed between then and
now (a `flake.nix`/devShell update, a fresh `uv sync` pulling a different wheel, etc.) is not
determined by this research. **The `--locked` count, re-measured this session:**
```
$ grep -n "locked" .github/workflows/*.yml | wc -l
10
```
`[VERIFIED: grep across all four workflow files, this session - ci.yml: 6 (lines 37,67,88,109,174,202),
release.yml: 2 (lines 36,113), docs.yml: 1 (line 29), drift.yml: 1 (line 32)]`.

**How to avoid:** Do not assert "ruff cannot run here" as a premise for any plan action without
re-running `uv run ruff check .` first at plan-write or task-execution time (it is a ~1-second check).
This does NOT override D-13's locked decision to make CI the pytest/lint/type authority - D-12's
separate, still-valid reasons for CI dispatch (Windows/macOS lanes, cp1252 and path-separator defect
history) stand regardless of ruff's local runnability - but a plan MAY additionally run
`uv run ruff check .` locally as a cheap pre-dispatch sanity check, and should not claim it is
impossible to do so. Use "10" (not "eleven") if citing the exact `--locked` step count in any evidence
file; the underlying sequencing constraint (`uv.lock` regenerated and committed before either
dispatch) is unaffected by the exact count.

**Warning signs:** An evidence file asserting "ruff could not be run locally, per the known NixOS ELF
issue" without a fresh `uv run ruff check .` transcript backing that specific claim on this specific
day.

### Pitfall 3: `RELEASE_VERSIONS` ordering dependency (recurring across every prior curation phase)

**What goes wrong:** Appending `"0.9.0"` to `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS`
tuple before `## [0.9.0]` exists in `CHANGELOG.md` makes `TestChangelogPageContentCoverage` fail.
**Why it happens:** The CHANGELOG plan and the version-bump plan may run in the same wave, in
parallel.
**How to avoid:** Sequence the append as the LAST sub-step of the CHANGELOG plan, gated on a
precondition that `## [0.9.0]` already exists.
**Warning signs:** `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py` failing
with a message naming a missing heading.

### Pitfall 4: Confusing the executor's own worktree with D-08's second, migration-guide worktree

**What goes wrong:** A plan that builds the "before" side inside the SAME `.venv` the executor's own
worktree provisioned (per CLAUDE.md's standing rule) actually builds the v0.8.0-tag source tree with
the CURRENT (v0.9.0-era) `typsphinx` package still editable-installed - producing a "before" file
tree that is actually the AFTER behavior, defeating the entire point of D-08's real-build requirement.
**Why it happens:** CLAUDE.md's mandatory per-worktree provisioning is phrased once, generically; a
plan author or executor may reasonably (but wrongly) assume "provision once, reuse everywhere."
**How to avoid:** `git worktree add --detach <dir> v0.8.0` creates a SEPARATE working directory with
its OWN `typsphinx/` source tree at the v0.8.0 tag; run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT
uv sync --extra dev` INSIDE that second directory specifically, before any `sphinx-build` there. The
executor's own top-level worktree provisioning does not reach into a nested `git worktree add`
target's own `.venv`.
**Warning signs:** A build transcript for the "before" side whose emitted file tree matches the CURRENT
(bundle-directory) layout rather than the old single-shared-`_template.typ` layout - if this happens,
the wrong `.venv`/`typsphinx` was used.

### Pitfall 5: Reporting REL-08 (or its Traceability row) complete before the publish

**What goes wrong:** `phase.complete` has a recorded, repeated habit of auto-flipping REL rows against
a CONTEXT decision - caught and reverted at four consecutive prior release-prep closes per
`57-CONTEXT.md`'s own D-05 language.
**Why it happens:** A generic closeout automation pattern-matches on "requirement fully addressed by
this phase's own success criteria" without understanding the acceptance evidence is generated by a
LATER command.
**How to avoid:** Record REL-08's exact lines and a `sha256sum .planning/REQUIREMENTS.md` baseline
EARLY (Pattern 7); diff after any closeout automation runs and before committing the close; revert by
hand if changed.
**Warning signs:** `git diff --name-only -- .planning/REQUIREMENTS.md` showing an unintended change.

## Code Examples

### Version bump, exact sequence (verified against the live pre-bump tree this session)

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
# edit pyproject.toml:7  -> version = "0.9.0"
# edit README.md:347     -> **Status**: Stable (v0.9.0) - Production ready
uv lock
uv sync --extra dev --locked
uv run python -c "import typsphinx; print(typsphinx.__version__)"   # expect 0.9.0
uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml \
  tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v
```

### CHANGELOG tail rollover (routine insert, NOT a repair - see Pitfall 1)

```diff
+[0.9.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.0
 [0.8.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0
 [0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
 ...
-[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.8.0...HEAD
+[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD
```

### CHANGELOG extraction and validation-job precondition check

```bash
uv run python scripts/extract_changelog_section.py 0.9.0    # exit 0, non-empty body
uv run python scripts/extract_changelog_section.py 9.9.9    # exit 1, stderr message -- empty-input control
```

### D-08's migration-guide "before" build (a second, disposable worktree)

```bash
git worktree add --detach /tmp/typsphinx-v080-before v0.8.0
cd /tmp/typsphinx-v080-before
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run sphinx-build -b typst tests/roots/test-basic /tmp/typsphinx-v080-before-build
find /tmp/typsphinx-v080-before-build -type f | sort
cd - && git worktree remove --force /tmp/typsphinx-v080-before
```

### Two-CI-dispatch sequence (D-12)

```bash
# Run 1 -- pre-bump check, dispatch first, before any Phase 57 commit lands
git push origin HEAD:refs/heads/gsd/v0.9.0-per-document-templates
gh workflow run ci.yml --ref gsd/v0.9.0-per-document-templates
gh run list --workflow=ci.yml --branch gsd/v0.9.0-per-document-templates \
  --limit 5 --json databaseId,headSha,event,status
gh run watch "$RUN_ID_1"
gh run view "$RUN_ID_1" --json jobs

# ... version bump + CHANGELOG + migration guide land here ...

# Run 2 -- post-bump authority, SC#3
git push origin HEAD:refs/heads/gsd/v0.9.0-per-document-templates
gh workflow run ci.yml --ref gsd/v0.9.0-per-document-templates
gh run list --workflow=ci.yml --branch gsd/v0.9.0-per-document-templates \
  --limit 5 --json databaseId,headSha,event,status
gh run watch "$RUN_ID_2"
gh run view "$RUN_ID_2" --json jobs
```

### SC#4 invariant sweep

```bash
git diff v0.8.0..HEAD --stat -- . ':(exclude).planning'
git diff v0.8.0..HEAD -- pyproject.toml                                   # NOT empty -- hunk-level argument, Pattern 6
git diff v0.8.0..HEAD -- typsphinx/__init__.py | grep add_config_value    # one removed, one added -- Pattern 6
grep -c "@preview" typsphinx/templates/base.typ                           # expect 4
uv run pytest tests/test_preview_version_sync.py -v
```

### Second-repository pin advance dispatch (for `57-HANDOFF.md`'s checklist, not executed here)

```bash
gh workflow run update-pin.yml --repo YuSabo90002/typsphinx-doc-translations
gh run list --repo YuSabo90002/typsphinx-doc-translations --workflow=update-pin.yml --limit 5
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| One CHANGELOG curation phase authors the migration guide from a mix of records and recall | The guide's "before" side is a real, freshly-built worktree checkout at the prior tag (D-08) | This phase, extending 51-CONTEXT's own precedent of writing from measurement | The "before" `code-block:: text` fragments are provably accurate, not reconstructed |
| One CI dispatch per release-prep phase | Two dispatches straddling the bump commit (D-12, reviving 46-CONTEXT D-23) | This phase - the branch has not touched Windows/macOS since Phase 53 | Separates "broken before this phase" from "broken by this phase's own bump" |
| `### Verified`'s "no new runtime dependency" argued by an empty `pyproject.toml` diff | Argued by a hunk-level reading of a non-empty diff (Pattern 6) | This milestone - the package-data glob widened (BLD-05) | The claim is now a positive statement about what the one hunk touches, not a vacuous absence |
| ruff assumed unrunnable locally on this NixOS machine | Runs cleanly locally as of this session (Pitfall 2) | Between 2026-08-11 (the pending todo's date) and 2026-08-16 (this session) - exact cause undetermined | A cheap additional local pre-dispatch check becomes available; CI remains the authority regardless |

**Deprecated/outdated:** the pending todo `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`'s
core claim no longer reproduces on this machine as of this session - flagged for the planner/owner to
consider re-verifying and potentially closing that todo, though doing so is outside this phase's
stated scope (a documentation-and-fence phase, not a toolchain-repair phase).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The exact final wave/plan decomposition is a recommendation derived from Phase 52's precedent, not a verified requirement - CONTEXT.md leaves "plan decomposition and ordering" to Claude's Discretion | Summary, Architecture Patterns system-flow diagram | Low - explicitly framed as a recommendation |
| A2 | `tests/roots/test-basic/` as D-08's fixture candidate is this researcher's judgment, not a locked choice - CONTEXT.md leaves the migration guide's exact content to Claude's Discretion | Pattern 3 | Low - flagged explicitly as a recommendation with a verified byte-identical-fixture rationale, and an equally valid purpose-built-fixture alternative is named |
| A3 | The exact cause of ruff now working locally (flake.nix update? fresh venv? a nixpkgs channel bump?) is NOT determined by this research - only the fact that it now works is verified | Pitfall 2 | Low - the finding is presented as an observed fact with a caveat about its cause, not asserted as a permanent fix |
| A4 | The recommendation to scope the SC#4 "no unintended `typsphinx/` change" fence proof to `<phase-57-start-SHA>..HEAD` rather than `v0.8.0..HEAD` is this researcher's own reading of what the fence criterion must mean (since the whole milestone visibly changed `typsphinx/`) - not explicitly spelled out in CONTEXT.md | Pattern 6 | Medium - if the planner reads SC#4's fence differently, the exact anchor SHA for this specific check needs independent confirmation at plan-write time |

## Open Questions

1. **Does `57-HANDOFF.md`'s second-repository-tag checklist item need to name an exact `gh` command
   sequence, or just describe the mechanism?**
   - What we know: `update-pin.yml`'s `workflow_dispatch` route is confirmed live and working
     (Pattern 7); it does not itself push a `v0.9.0` tag on that repository.
   - What's unclear: whether the handoff should also specify the follow-up tag-push command on
     `typsphinx-doc-translations`, or leave that as an owner-manual step the way `52-HANDOFF.md` did.
   - Recommendation: mirror `52-HANDOFF.md` item 4's shape (owner decides tag timing after the pin
     commit lands), naming the `update-pin.yml` dispatch as the NEW mechanical step this milestone
     adds over prior handoffs' "clone and edit by hand" framing.

2. **Whether the pending todo `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` should be
   updated or closed as part of this phase's todo-ledger disposition work (`<specifics>` 9).**
   - What we know: its core claim does not currently reproduce (Pitfall 2).
   - What's unclear: whether this is a durable fix or an environment-specific fluke that could
     regress on the next `nix flake update` / `uv sync` - re-testing at a later date is the only way
     to know.
   - Recommendation: do not close the todo outright (its "Acceptance" criteria talk about a durable,
     intentional fix such as `pkgs.ruff` in `flake.nix`, which was not what happened here); at most,
     append a dated note that it did not reproduce on 2026-08-16, without changing its status.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` (bare, on PATH) | version bump, all `uv run` invocations | Yes | 0.11.25 (from `PATH`) | - |
| `git` | every task, incl. `git worktree add` | Yes | system | - |
| `gh` (authenticated) | CI dispatch, run polling, second-repo dispatch | Yes - confirmed live (`gh auth status`, `gh run list` against both repos) | - | - |
| `typst`-py / `pypdf` | D-14's gate re-run, docs-pdf build | Yes (dev-extra) | - | - |
| `ruff` | lint gate | Yes as of this session - see Pitfall 2 | 0.15.20 | CI remains authority per D-13 regardless |
| `black` | format gate | Yes | 26.5.1 | - |
| `mypy` | type-check gate | Yes | - (0 issues, 8 source files) | - |
| standalone CPython 3.12 (`tox -e py312`) | - | No - ELF the stub loader rejects | - | `tox -e py313` (matches system interpreter) or direct `uv run pytest`; CI covers the full matrix |
| `myst-parser` | `TestChangelogPageContentCoverage` / `TestChangelogIncludeCompilesToPdf` | Only under `--extra docs` | - | run with `uv run --extra dev --extra docs pytest ...` |

**Missing dependencies with no fallback:** none - every gap has a documented, already-exercised
fallback from prior phases.

**Missing dependencies with fallback:** `tox -e py312` (-> `tox -e py313` / direct `pytest`),
`myst-parser` (-> `--extra docs`).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), `tox` as task runner |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`), `tox.ini` |
| Quick run command | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` |
| Full suite command | dispatched CI (`gh workflow run ci.yml --ref <branch>`, twice per D-12) is the matrix/lint/type authority per D-13; locally, `uv run pytest tests/ -v` plus `tox -e docs-html`/`tox -e docs-pdf`/`uv run pytest tests/test_corpus_gate.py -v` cover what CI does not |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-08 (SC#1) | Version literals move in lockstep | unit | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` | Yes |
| REL-08 (SC#2) | Curated `## [0.9.0]` CHANGELOG entry, `### Removed` bullet, tail rollover, migration guide, `RELEASE_VERSIONS` current | integration | `uv run python scripts/extract_changelog_section.py 0.9.0` + `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` | Yes |
| REL-08 (SC#3, toolchain half) | Post-bump tree green (pytest/lint/type, both docs builds, built-wheel content check) | integration/e2e | two dispatched `ci.yml` runs (Pattern 4) + `tox -e docs-html`/`docs-pdf` | Yes (CI workflow); local envs exist |
| REL-08 (SC#3, goal-claim half) | Multi-template round trip proven on generated PDF evidence | e2e/gate | `uv run pytest tests/test_two_key_selection_gate.py -v` (re-run per D-14, no new gate) | Yes - already permanent |
| REL-08 (SC#4) | Milestone invariants + fence asserted mechanically | unit/script | the `git diff`/`grep` commands in Pattern 6 + `git tag -l v0.9.0` / `git ls-remote --tags origin v0.9.0` (x2) + `REQUIREMENTS.md` checksum | Yes (commands) |
| REL-08 (SC#5) | Standalone handoff exists, REL-08 stays open | manual + script | `git diff --name-only -- .planning/REQUIREMENTS.md` (empty throughout the phase) | Yes |

### Sampling Rate

- **Per task commit:** the relevant guard-test subset (version-sync trio for the bump plan; page-gate
  module for the CHANGELOG plan; `test_two_key_selection_gate.py` for the D-14 re-run task).
- **Per wave merge:** `uv run pytest tests/ -v` locally as a spot-check (never presented as authority
  for lint/matrix - that is CI, D-13); `uv run ruff check .` MAY additionally be run locally per
  Pitfall 2, but is not a substitute for the CI dispatch.
- **Phase gate:** both dispatched CI runs all-green + both `tox -e docs-*` + `test_corpus_gate.py`
  (PASSED or honestly SKIPPED, never conflated) before `/gsd-verify-work`.

### Wave 0 Gaps

None - every test module and fixture this phase needs already exists in the repository. The only new
test-adjacent content is a new prose section (`docs/source/changelog.rst`'s migration guide), which
D-07 deliberately leaves ungated.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | This phase touches no auth surface |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes (narrow) | `scripts/extract_changelog_section.py`'s `version` argument is used only for string-equality comparison, never interpolated into a shell command or `eval`'d `[VERIFIED: scripts/extract_changelog_section.py, read in full this session]` - this phase exercises, not modifies, that invariant |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for this stack (release-engineering specific)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A crafted git tag name executing shell in a `contents: write` / `id-token: write` job | Tampering / Elevation of privilege | `.github/workflows/release.yml` passes every `${{ }}` through `env:`, never interpolated into `run:` blocks `[VERIFIED: .github/workflows/release.yml:38-44,176-181, read this session]` - this phase's job is to confirm no unintended change to this file (Pattern 6), not to modify it |
| Reporting a requirement complete on the strength of code correctness rather than generated evidence | Repudiation | SC#3's goal-claim half and Pattern 5 exist precisely to close this gap; REL-08's checkbox must not flip before the publish (Pitfall 5) |
| A test gate silently weakened to force a green run | Tampering | Every prior phase's acceptance criteria assert `git diff` is confined to the intended lines (e.g. `RELEASE_VERSIONS`'s tuple/comment only) - carry the same discipline forward |
| Advancing a second repository's pin/tag by hand, outside its own reviewed workflow | Tampering | Use `update-pin.yml`'s `workflow_dispatch` (Pattern 7), not a manual clone/edit/push, so the same reviewed catalog-regeneration and no-content-free-commit logic applies every time |

## Sources

### Primary (HIGH confidence - read or executed directly this session)

- `pyproject.toml`, `README.md`, `uv.lock`, `CHANGELOG.md` (head and tail, read in full),
  `docs/source/changelog.rst` (read in full, 343 lines),
  `docs/source/user_guide/configuration.rst` (Removed Configuration Values table),
  `docs/source/installation.rst`, `examples/basic/README.md`, `examples/advanced/README.md`,
  `docs/source/contributing.rst`, `docs/source/examples/advanced.rst`,
  `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `.github/workflows/docs.yml`,
  `.github/workflows/drift.yml`, `scripts/extract_changelog_section.py`,
  `typsphinx/removed_config.py`, `typsphinx/writer.py`, `typsphinx/template_engine.py`,
  `typsphinx/templates/base.typ`, `tests/test_extension.py`, `tests/test_readme_version_sync.py`,
  `tests/test_preview_version_sync.py`, `tests/test_changelog_page_gate.py`,
  `tests/test_corpus_gate.py`, `tests/test_two_key_selection_gate.py`,
  `tests/fixtures/two_key_selection_gate/conf.py` and both `_typst/*/base.typ` templates,
  `tests/roots/test-basic/conf.py` (both at `HEAD` and via `git show v0.8.0:...`),
  `.planning/todos/pending/*` (9 files, directory-listed), `.planning/todos/completed/*` (listed),
  `.planning/REQUIREMENTS.md`, `.planning/STATE.md` (in full),
  `.planning/phases/57-v0-9-0-release-prep-prep-only/57-CONTEXT.md` (in full),
  `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-RESEARCH.md` (in full),
  `.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-HANDOFF.md` (in full),
  `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/46-RESEARCH.md` (D-23
  section), `.planning/milestones/v0.6.0-phases/15-full-corpus-validation/15-02-PLAN.md`,
  `.planning/milestones/v0.7.0-phases/42-.../42-05-PLAN.md`,
  `.planning/milestones/v0.7.1-phases/43-.../43-GATE-EVIDENCE-05.md`,
  `.planning/milestones/v0.6.4-phases/30.1-.../translations-repo/.github/workflows/update-pin.yml`.
- Live `git`/`gh`/`uv` commands executed this session (version diffs, invariant sweep, worktree/tag
  ancestry checks, CI run lists on both `typsphinx` and `typsphinx-doc-translations`, `ruff`/`black`/
  `mypy`/`pytest` spot-runs against the live pre-bump tree).

### Secondary (MEDIUM confidence)

- User's own auto-memory index - cross-checked the ruff ELF hazard's PREVIOUSLY reported status
  ("only the ruff ELF issue remains, as of 2026-08-14"); this session's live re-test contradicts it
  for the current moment (Pitfall 2), so the memory entry is now stale relative to this session's
  measurement, not authoritative for it.

### Tertiary (LOW confidence)

- None - every claim in this document traces to a file read or a command run this session, except
  where explicitly marked `[ASSUMED]` (none used - all provenance in this document is `[VERIFIED]`).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new library; every version-sync mechanism and tool availability check read
  or executed directly this session.
- Architecture / plan decomposition: HIGH for the mechanism, MEDIUM for the specific wave/plan split
  (explicitly flagged A1 as a recommendation).
- CHANGELOG/tail-block/D-10 findings: HIGH - both corrections were independently re-derived from live
  file reads and `git log` timestamps, not merely asserted.
- Pitfalls: HIGH - five of five are either directly inherited from prior phases' documented experience
  or freshly discovered and independently reproduced this session.
- SC#4 hunk-level argument: MEDIUM - no prior phase attempted a non-empty-diff dependency argument;
  this research's proposed framing (Pattern 6) is reasoned but unprecedented in this project's own
  evidence-file history.

**Research date:** 2026-08-16
**Valid until:** this phase's own execution (release-prep research is single-use; the live git state
this research is anchored to - `v0.8.0` at `d9523ea`, `origin/main` at `aed773c9`, 190 commits ahead of
`origin/gsd/v0.9.0-per-document-templates`, HEAD at `53fba67b` - will have moved by the time any other
phase reads this file. In particular, if D-10's already-complete fix or the CHANGELOG tail-block state
is somehow reverted between this research and plan execution, re-verify both before trusting Pitfall
1's conclusions.)
