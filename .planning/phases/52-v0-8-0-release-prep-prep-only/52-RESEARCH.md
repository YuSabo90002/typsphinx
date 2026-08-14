# Phase 52: v0.8.0 Release Prep (prep-only) - Research

**Researched:** 2026-08-15
**Domain:** Release engineering for a prep-only milestone-close phase (version bump, curated
CHANGELOG, live-green evidence, mechanical invariant sweep, publish handoff) — no `typsphinx/` code
change.
**Confidence:** HIGH — this is the fifth iteration of an established pattern (Phases 23, 28, 33, 35,
41, 46 all did this exact shape), and every mechanism cited below was either read from the live
source this session or executed live.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** The four minor defects this milestone's own reviews filed ship in v0.8.0 unfixed and
  disclosed internally only. Records stay in `todos/pending/`, named in `52-HANDOFF.md`; no
  `### Known Limitations` CHANGELOG section, no GitHub issue. — Reversible.
- **D-02:** The two behaviours Phase 49 measured and Phase 51 documented are written into the
  descriptive bullets, not into a limitations section: (a) a content file compiled standalone yields
  only its own body, its state-guarded children absent, no error/warning; (b) a document reachable
  from several masters renders once in each master's PDF, heading level varying per master. —
  Reversible.
- **D-03:** The four defects plus the `:numref:` record are carried forward as todos, not promoted to
  the ROADMAP backlog. — Reversible.
- **D-04:** Breaking changes marked two ways — lead-paragraph declaration plus `**Breaking:**` prefix
  on each affected bullet. Three bullets carry the prefix: wrapper/content split, target-as-path
  reversal, collision hard error. No `### Removed` section (zero `add_config_value` diff). —
  Reversible.
- **D-05:** The lead paragraph's axis is the milestone goal itself — a `typst_documents`
  configuration declaring more than one master now produces a complete PDF for each of them. The
  breaking-change declaration lives in the second half of the same paragraph. — Reversible.
- **D-06:** `### Verified` carries the same three items as 0.7.0 and 0.7.1, unchanged. SC#4's config
  invariant and SC#3's round-trip evidence are recorded in the phase's own evidence artifacts, not
  promoted into `### Verified`.
- **D-07** *(derived, carried from 46-CONTEXT D-05)*: bullets cut at user-visible-change granularity
  with requirement IDs in trailing parentheses — house style since Phase 33 D-09. ~8-9 bullets;
  planner owns the final cut and section assignment.
- **D-08** *(derived, following 46-CONTEXT D-11)*: the dispatched CI run on the post-bump commit is
  the authority for pytest/lint/type; the full-corpus gate and both docs builds run locally. Pushing a
  branch and dispatching a workflow are not irreversible; opening a PR is, and stays out of scope.
- **D-09** *(derived)*: SC#4's invariant sweep is anchored at the `v0.7.1` tag (`48bf135`). Three
  mechanical assertions: zero new runtime dependencies, `@preview` count still four with no new
  lockstep site, no new `typst_*` config value. The positive control must be real, not a restatement.
- **D-10** *(derived, following 51-CONTEXT D-10)*: the goal-claim evidence is a new permanent gate
  test under `tests/`, reusing the existing multi-master fixture family
  (`tests/fixtures/state_guard_three_master_gate/`). Must add the PDF-level assertion SC#3 names —
  each master's PDF opened via `pypdf`, with specific text and page assertions — beyond the existing
  `typst.query` structural assertions. Planner owns whether the fixture is reused as-is or extended.

### Claude's Discretion

- The exact wording of the `## [0.8.0]` entry, the lead paragraph's phrasing, which 8-9 bullets D-07
  resolves to, and how requirement IDs are attached.
- Which requirements land in `### Added` versus `### Changed` versus `### Fixed`. No assignment fixed
  by decision — `### Removed` has no candidate (D-04).
- Plan decomposition and ordering, and the `uv.lock` regeneration procedure (acceptance:
  `uv sync --extra dev --locked` green).
- The mechanical method for D-09's invariant sweep, and what the positive control is.
- Whether `"0.8.0"` is added to `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py:49-63` in
  this phase — must not land before the CHANGELOG entry exists.
- The name and shape of D-10's new gate module and whether it extends
  `state_guard_three_master_gate` or adds a sibling fixture.
- The format and heading structure of `52-HANDOFF.md`, and where live-run evidence is recorded —
  subject to the reserved-name constraint: do **not** name any evidence file `52-VERIFICATION.md`
  (46-CONTEXT D-15; the verifier owns that name and will clobber it).
- Whether the CI dispatch is one run or two (here there is no separate repair to check first, so one
  run is the likely shape).

### Deferred Ideas (OUT OF SCOPE)

- Fixing any of the four minor defects in this phase — declined by D-01 and the prep-only fence.
- A `### Known Limitations` CHANGELOG section and public GitHub issues for the four defects —
  declined by D-01.
- Promoting the deferred defects to ROADMAP backlog items `999.3`+ — declined by D-03 in favour of the
  todo ledger.
- The `:numref:` divergence — excluded from every published surface by 51-CONTEXT D-07 (owner
  override, 2026-08-14). `resolves_phase` is `null`; a later milestone picks it up as a bug.
- All 9 records in `.planning/todos/pending/` are reviewed-but-not-folded — see 52-CONTEXT.md
  `<deferred>` for the per-record disposition reasoning; none is folded into this phase's scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REL-07 | v0.8.0 is released to PyPI with a curated CHANGELOG entry calling out the output-shape change and the target-as-path reversal — **prep half only**; the requirement itself closes at `/gsd-complete-milestone`, not in this phase | Pattern 1 (version bump), Pattern 2 (CHANGELOG curation + extraction mechanism), Pattern 3 (D-10's goal-claim gate test), Pattern 4 (CI dispatch/authority split), Pattern 5 (SC#4 invariant sweep + positive control), Pattern 6 (prep/publish fence command list) — together these cover ROADMAP Phase 52's five success criteria end to end |

</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Worktree-isolated execution is mandatory, not conditional**, for every executor on this project
  (owner decision, 2026-07-20, reaffirmed standing as of the current milestone): before any command,
  run `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` inside the worktree, then run
  every subsequent command through `uv run`. This applies even to low-parallelism plans/waves — do not
  degrade to sequential main-tree execution. The only automatic fallbacks are a non-`claude` runtime, a
  plan touching a git-submodule path, or a genuine `worktree base-check` degrade signal.
- **`tox-uv-bare~=1.35`, not `tox-uv`** — deliberate; the plain `tox-uv` meta package bundles a PyPI
  `uv` wheel whose generic-linux ELF cannot exec on NixOS. Do not "simplify" this back.
- **Do not modernize typing imports** (`Dict`/`List` → `dict`/`list`) until the filed todo lands —
  irrelevant to this phase's file set (no `typsphinx/` code is touched) but binding project-wide.
- **Line length 88 (black); `E501` ignored in ruff** since black owns wrapping — relevant only if this
  phase's new test-module content is formatted; run `black` (not `ruff`, per Pitfall 3/D-08) locally.
- **CI matrix (py312-py313 + lint + type + cov) is the authority this phase must dispatch and read**,
  per D-08 — `.github/workflows/ci.yml` is exercised (`workflow_dispatch`), never edited.
- **The `@preview` version-sync hazard**: `codly`/`codly-languages`/`mitex`/`gentle-clues` versions
  must stay in lockstep across `writer.py`/`template_engine.py`/`templates/base.typ`; this phase
  changes none of them (SC#4's own invariant), so `tests/test_preview_version_sync.py` is a spot-check,
  not new work.

## Summary

This phase has no new technology to research — it is a repeat of Phase 46's own mechanism, adapted
to a milestone that (unlike v0.7.1) needs no `origin/main` merge, no pre-existing Windows CI defect
to repair, and no REL-04-shaped "in-phase precondition, structurally-owed evidence" split. What it
does add beyond Phase 46's shape is D-10: a new permanent PDF-level gate test that discharges the
milestone's own goal claim ("a `typst_documents` configuration declaring more than one master now
produces a complete PDF for each of them") on generated evidence, not on the strength of unit
fixtures passing. Research located the exact fixture and — critically — an **already-existing test
class** (`tests/test_state_guard_shapes_gate.py::TestThreeMasterGate`) that already does most of what
D-10 asks for, on the exact fixture D-10 names, but was never surfaced in 52-CONTEXT.md's own
discussion. This is this research's single most load-bearing finding and is detailed in Pitfall 1
below — the planner must decide, with this fact in hand, whether to extend it or add a sibling.

Every version-literal site, every guard test, every CHANGELOG structural convention, and every
invariant-sweep command was verified directly against the live tree this session (not merely quoted
from `52-CONTEXT.md`) and matches `52-CONTEXT.md`'s own measurements exactly. The one CONTEXT figure
that has moved since context-gathering: the branch is now **157** commits ahead of
`origin/gsd/v0.8.0-multi-master-composition` (CONTEXT said 155; two more commits landed between
context-gathering and this research pass — expected drift, not a discrepancy to flag).

**Primary recommendation:** Follow Phase 46's five-evidence-file, six-plan, four-wave shape almost
verbatim (`46-BUMP-EVIDENCE.md` / `46-CI-EVIDENCE.md` / `46-GREEN-TREE-EVIDENCE.md` /
`46-SC4-INVARIANTS.md` / roll-up + handoff), but drop the two plans this milestone doesn't need
(the `origin/main` merge tracer and the REL-04 precondition-and-exercise plan), and insert one new
plan for D-10's gate test — landed and committed **before** the CI-dispatch plan runs, so the
dispatched authority CI run also proves the new test green on every OS lane.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version-literal bump (`pyproject.toml`, `README.md`, `uv.lock`) | Release tooling (`uv`) | — | Pure packaging metadata; no application tier touched |
| Editable-install metadata regeneration | Release tooling (`uv sync`) | Python runtime (`importlib.metadata`) | `typsphinx.__version__` reads installed `.dist-info`, not the literal |
| CHANGELOG curation | Documentation / release notes | CI (`release.yml` `validate` job reads it) | Human-authored prose consumed mechanically downstream |
| D-10's new PDF-level gate test | Test / verification tier | Builder (`typsphinx/builder.py`) + Translator (indirectly, via compiled output) | New permanent regression proof; touches no production code |
| CI dispatch and authority run | CI/CD (GitHub Actions) | — | Lint/type/matrix authority lives here per D-08, not locally |
| Invariant sweep (SC#4) | Release tooling / git | — | Pure `git diff`/`grep` over the milestone diff; no runtime component |
| Publish handoff (`52-HANDOFF.md`) | Planning artifact | `/gsd-complete-milestone` (consumer) | Describes the publish, does not perform it |

This phase touches no browser/frontend/API/database tier — it is release engineering + one new test
module. `ui.plan-gate` and `api-coverage.verify-pre` are both expected to false-positive here per the
project's own standing notes (STATE.md); override both if they fire.

## Standard Stack

No new library is introduced by this phase. Every tool used is already in `pyproject.toml`'s `dev`
extra or is system tooling (`git`, `gh`).

### Core (already installed, reused as-is)

| Library | Version (measured) | Purpose | Why standard here |
|---------|---------|---------|--------------|
| `uv` | on PATH, bare (not `.venv/bin/uv`) | Lockfile regen, editable install, `uv run` | `CLAUDE.md`'s mandated worktree-isolation runner |
| `pypdf` | already a `dev`-extra dependency | PDF text/page extraction for D-10's gate | Used in 20+ existing gate modules `[VERIFIED: tests/test_state_guard_shapes_gate.py:37-50, tests/test_state_guard_composition_gate.py:57-62]` |
| `typst-py` (`typst` import) | already a `dev`-extra dependency | Compile + `typst.query()` for heading-level/label assertions | Same pattern as above |
| `pytest` | already a `dev`-extra dependency | Test runner, `@pytest.mark.slow` marker | Standing convention |

### Alternatives Considered

None — this phase adds no dependency by design (ROADMAP binding invariant, re-verified this session:
`git diff v0.7.1..HEAD -- pyproject.toml` is empty `[VERIFIED: git diff output, this session]`).

**Installation:** none needed — `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
provisions everything already pinned in `uv.lock`.

**Version verification:** not applicable — no package version claim is made by this phase beyond
`typsphinx` itself, whose bump mechanism is documented below (Pattern 1).

## Package Legitimacy Audit

**Not applicable.** This phase installs no new package (npm/pip/cargo or otherwise); it only bumps
`typsphinx`'s own version literal and regenerates `uv.lock` against the *existing* dependency set.
`gsd-tools query package-legitimacy check` was not run because there is no candidate package name to
check — this mirrors Phase 46's own recorded disposition (`46-*-PLAN.md` threat registers: "RESEARCH.md
records the Package Legitimacy Gate as not applicable"). If a plan's `uv lock` run produces an
unexpected new transitive dependency, treat that as a red flag requiring `checkpoint:human-verify`
before proceeding — SC#4's invariant 1 exists precisely to catch this.

## Architecture Patterns

### System flow — this phase's evidence pipeline

```
┌─────────────────────┐     ┌──────────────────────┐     ┌───────────────────────┐
│ 1. Version bump      │     │ 2. CHANGELOG curation │     │ 3. D-10 gate test      │
│ pyproject.toml:7     │     │ CHANGELOG.md          │     │ (new, permanent)       │
│ README.md:347        │     │ docs/.../changelog.rst│     │ tests/test_*_gate.py   │
│ uv.lock (uv lock)     │     │ RELEASE_VERSIONS      │     │ over an existing 3-    │
│ uv sync --locked      │     │ (only after heading   │     │ master fixture         │
│ → __version__=0.8.0  │     │  exists)               │     │                        │
└──────────┬───────────┘     └──────────┬────────────┘     └───────────┬────────────┘
           │                            │                              │
           └────────────┬───────────────┴──────────────┬───────────────┘
                         ▼                              ▼
              ┌────────────────────┐         ┌─────────────────────────┐
              │ 4. Push + dispatch  │         │ 5. Local green-tree half │
              │ gh workflow run     │         │ tox -e docs-html/pdf     │
              │ ci.yml on branch    │         │ test_corpus_gate.py       │
              │ (workflow_dispatch) │         │ ruff via CI only (D-08)   │
              │ → matrix + lint +   │         └─────────────┬─────────────┘
              │   type authority    │                       │
              └──────────┬──────────┘                       │
                         │                                  │
                         └───────────────┬──────────────────┘
                                         ▼
                          ┌──────────────────────────────┐
                          │ 6. SC#4 invariant sweep        │
                          │ git diff v0.7.1..HEAD          │
                          │ (deps / @preview / typst_*)     │
                          │ + positive control              │
                          └───────────────┬─────────────────┘
                                         ▼
                          ┌──────────────────────────────┐
                          │ 7. Roll-up + handoff            │
                          │ 52-RELEASE-EVIDENCE.md          │
                          │ 52-HANDOFF.md (7-item checklist) │
                          │ fence: git tag -l v0.8.0 empty   │
                          │ (2 independent observations)     │
                          └──────────────────────────────┘
```

Read top-to-bottom: 1/2/3 can run in parallel (disjoint files — CHANGELOG.md is untouched by 1 and 3;
the new gate test's fixture directory is untouched by 1 and 2). 3 must complete and commit *before*
4, so the dispatched CI run also proves the new gate green across the OS matrix. 4 and 5 are the two
halves of SC#3 and can run in parallel with each other, but both need 1/2/3 merged back first. 6 needs
only the merged tree, not the CI result. 7 needs everything.

### Recommended plan/wave decomposition (derived from Phase 46's precedent, minus what this milestone doesn't need)

```
Wave 1 (parallel, disjoint files):
  52-01  Version bump (pyproject.toml, README.md, uv.lock) + guard-test evidence   [= 46-02 shape]
  52-02  CHANGELOG curation (CHANGELOG.md, changelog.rst is ALREADY DONE by Phase 51 --
         only RELEASE_VERSIONS append + verifying the migration section still agrees)  [= 46-03 shape, thinner]
  52-03  D-10's new PDF-level multi-master gate test (new test module, or extend
         TestThreeMasterGate -- see Pitfall 1)                                          [NEW -- no 46 analog]

Wave 2 (depends on wave 1 merging back):
  52-04  Push + dispatch CI authority run + record job table                            [= 46-04 task 1]
  52-05  Local green-tree half: docs-html, docs-pdf, corpus gate                        [= 46-04 tasks 2-3, minus D-12's ja-build --
                                                                                            no CONF-12-shaped requirement this milestone]
  52-06  SC#4 invariant sweep (deps / @preview / typst_* config) with a REAL positive control  [= 46-05 task 1 shape, REL-04 task dropped]

Wave 3 (depends on wave 2):
  52-07  Roll-up (52-RELEASE-EVIDENCE.md) + 52-HANDOFF.md + todo disposition (9 records)  [= 46-06 shape]
```

Unlike Phase 46, there is **no D-20 merge tracer plan** — `origin/main` is already an ancestor of HEAD
(re-verify at the head of wave 1: `git merge-base --is-ancestor origin/main HEAD`), and no
**REL-04-precondition plan** — REL-04 does not exist as a v0.8.0 requirement; only REL-07 does, and it
is entirely publish-gated, with no in-phase precondition share to discharge. This makes the plan count
smaller (7, versus Phase 46's 6 across a heavier scope) but the wave count similar (3 vs Phase 46's 4,
because there is no serial tracer wave here).

### Pattern 1: Version-literal bump and editable-install metadata regeneration

**What:** Move `0.7.1` → `0.8.0` in `pyproject.toml:7` and `README.md:347`
(`**Status**: Stable (v0.7.1) - Production ready`), then regenerate the lockfile and reinstall so
`typsphinx.__version__` — which is derived, not literal — actually reports the new value.

**Verified this session (not merely quoted from CONTEXT.md):**
```
$ sed -n '7p' pyproject.toml
version = "0.7.1"
$ sed -n '347p' README.md
**Status**: Stable (v0.7.1) - Production ready
$ grep -A3 'name = "typsphinx"' uv.lock
name = "typsphinx"
version = "0.7.1"
source = { editable = "." }
dependencies = [
```
`[VERIFIED: pyproject.toml:7, README.md:347, uv.lock:1466-1469 — read this session]`

**The mechanism** (unchanged since Phase 46, re-confirm the exact command sequence at plan-write time
by reading `46-02-PLAN.md` Task 1 rather than re-deriving):
1. `git diff v0.7.1..HEAD -- pyproject.toml` is empty this session `[VERIFIED: git diff output, this session]` — confirms no accidental second literal has appeared.
2. Edit `pyproject.toml:7`, `README.md:347`.
3. `uv lock` — regenerates `uv.lock`'s own `typsphinx` block.
4. `uv sync --extra dev --locked` — `--locked` fails loudly on any lock/manifest disagreement, and this is the step that actually regenerates the `.dist-info`/`.pth` editable-install metadata; editing the literal alone does **not** move `importlib.metadata.version("typsphinx")`'s return value.
5. `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → expect `0.8.0`.

**Guard tests that must stay green (all three named and located this session):**
- `tests/test_extension.py::test_version_matches_pyproject_toml` — parses `pyproject.toml` via `tomllib` independently of `importlib.metadata`, a genuine drift guard rather than a tautology `[VERIFIED: tests/test_extension.py:79-93, read this session]`.
- `tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject` — regex-parses README's Status line and compares against `tomllib`'s parse of `pyproject.toml`, never against a hardcoded literal `[VERIFIED: tests/test_readme_version_sync.py, read in full this session]`.
- `tests/test_preview_version_sync.py` (three test functions: `test_preview_versions_identical_across_declaration_sites`, `test_all_four_packages_declared`, `test_example_templates_match_canonical_versions`) — the four-surface `@preview` lockstep guard `[VERIFIED: tests/test_preview_version_sync.py:63-146, read this session]`. This bump changes no template/import code, so this guard is a spot-check, not the invariant sweep's own authority (that's SC#4's job).

**Do not run `tox -e py312` locally** — on this NixOS machine `uv venv -p cpython3.12` downloads a
standalone CPython whose ELF the stub loader rejects, exit 127 (Phase 46 RESEARCH Pitfall 1,
unchanged). Use `uv run pytest` directly for a local spot-check; CI is the matrix authority (D-08).

### Pattern 2: CHANGELOG curation — this time, the migration guide is already written

**Verified this session:** `## [0.7.1]` is the current top-most dated entry, immediately preceded by
`## [Unreleased]` (whose body is only `### Planned for Future Releases`, five items, matching
CONTEXT's measurement exactly) `[VERIFIED: CHANGELOG.md:1-96, read this session]`. `## [0.7.1]`'s
structure is the model to copy: lead paragraph (2-4 sentences, states the breaking-change fact in its
second half) → `### Added` → `### Changed` (bullets prefixed `**Breaking:**` where applicable) →
`### Fixed` → `### Removed` (only when there's a candidate — v0.7.1 had one; **v0.8.0 measured to
have none**, per D-04: `git diff v0.7.1..HEAD -- typsphinx/__init__.py | grep add_config_value` is
empty `[VERIFIED: git diff output, this session]`) → `### Verified` (exactly three items, unchanged
wording across three consecutive releases) → tail link-block insertion.

**The tail link block, verified this session:**
```
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.7.1...HEAD
```
`[VERIFIED: CHANGELOG.md tail block, read this session]`. This phase's edit: insert
`[0.8.0]: .../releases/tag/v0.8.0` immediately above the `[0.7.1]:` line, and change the final line's
compare base to `v0.8.0...HEAD`. This is a **new-tag-link + compare-rollover**, identical mechanism to
Phase 46's own rollover (`46-03-PLAN.md` Task 1), just with `0.8.0`/`0.7.1` substituted for
`0.7.1`/`0.7.0`.

**The one structural difference from every prior curation: the migration guide already exists.**
Phase 51 already wrote `docs/source/changelog.rst`'s "Migrating from 0.7.x to 0.8.0" section
`[VERIFIED: docs/source/changelog.rst:1-40, read this session — the heading text, the two verified
breaking-change items (output shape, target-as-path reversal) with `.. code-block:: text` before/after
fragments, quoted verbatim below]`:
```
Migrating from 0.7.x to 0.8.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This release carries three breaking changes to what typsphinx writes to disk. Each item below
shows the ``conf.py`` fragment you have today -- unchanged -- and what it now produces...

- **Breaking:** the output shape. One ``typst_documents`` entry now writes TWO files instead of
  one. With ``typst_documents = [("index", "manual.typ", "Title", "Author", "typst")]``, v0.7.x
  wrote ``manual.typ`` containing the whole document; v0.8.0 writes ``manual.typ`` as a thin
  wrapper (template application plus one include) and ``index.typ`` as the document body...

- **Breaking:** the target-as-path reversal. A target containing a path separator was rejected in
  v0.7.x ... and is honoured as-is relative to the output directory in v0.8.0. With
  ``typst_documents = [("index", "manuals/guide.typ", "Title", "Author", "typst")]``, v0.7.x wrote
  ``guide.typ`` at the output root; v0.8.0 writes ``manuals/guide.typ``...
```
This means **this phase's job for `docs/source/changelog.rst` is to confirm agreement, not to author
a new section** — the exact opposite of every prior release-prep curation, where the migration section
was the new artifact. Unlike Phase 46 (which had to *write* the migration section as part of the
prep), this phase's `docs/source/changelog.rst` task is closer to a read-and-verify: the CHANGELOG
bullets D-05/D-04 direct must **agree** with the measured filenames/fragments already published there
(e.g. `manual.typ`/`index.typ`, `manuals/guide.typ`) rather than deriving new ones, and no hand edit
to `changelog.rst` is owed unless the third breaking change (the collision hard error, per D-04) turns
out to be unaddressed there — check its presence directly before assuming.

**`scripts/extract_changelog_section.py`'s exact requirement, read in full this session:** purely
positional extraction — first line matching `^## \[(?P<version>[^\]]+)\]` where the captured version
equals the requested string, body runs to (not including) the next such heading line or EOF, stripped
of leading/trailing blank lines; raises `RuntimeError` (exit 1, message on stderr) if no heading
matches or if the body is empty after stripping `[VERIFIED: scripts/extract_changelog_section.py,
read in full this session]`. `release.yml`'s `validate` job calls exactly this script
(`uv run python scripts/extract_changelog_section.py "$VERSION" >/dev/null`) and fails the whole
release before `build`/`publish-pypi` if it exits non-zero
`[VERIFIED: .github/workflows/release.yml:72-79, read this session]`. `create-release`'s "Generate
release notes" step calls the same script a second time to build `release_notes.md`, appending an
"## Installation" `pip install typsphinx==${TAG#v}` block
`[VERIFIED: .github/workflows/release.yml:190-204, read this session]`.

**`tests/test_changelog_page_gate.py:49-63`'s `RELEASE_VERSIONS` tuple, read in full this session:**
currently 13 entries, `"0.4.1"` through `"0.7.1"` `[VERIFIED: tests/test_changelog_page_gate.py:49-64,
read this session — the tuple's literal contents quoted above in full]`. The comment above it
(line 47) already says "13 releases the published page was frozen without (0.4.4 through 0.7.1,
inclusive)" — this comment must move to 14/`0.8.0` alongside the append, matching Phase 46's own
`46-03-PLAN.md` Task 3 acceptance criteria shape (comment-count and tuple content moved together).
**Ordering constraint, re-confirmed:** the append is only valid once `## [0.8.0]` exists in
`CHANGELOG.md` — `TestChangelogPageContentCoverage` and `TestChangelogIncludeCompilesToPdf` are both
gated behind `myst_parser`/`typst` availability and run in a `--extra docs` environment; Phase 46's own
plan discovered that running the module against the plain `dev` `.venv` silently skips those two
classes without ever asserting the tuple reaches the built page — run with
`uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` and check the JUnit
skip count is `0`, not the summary line.

### Pattern 3: D-10's new PDF-level multi-master gate test — the fixture and the (partially) pre-existing test class

**The fixture, read in full this session (`conf.py` and all six `.rst` files):**
`tests/fixtures/state_guard_three_master_gate/` — three `typst_documents` masters (`m1`/`manual1.typ`,
`m2`/`manual2.typ`, `m3`/`manual3.typ`), two shared children (`common_a.rst`, `common_b.rst`, each
carrying only a heading and a bare marker line — `COMMON-A-MARKER`, `COMMON-B-MARKER`), and one
mid-level document (`mid.rst`, a toctree-only pass-through)
`[VERIFIED: tests/fixtures/state_guard_three_master_gate/conf.py:1-43 and *.rst, read in full this
session — quoted verbatim: `common_a.rst` body is "Common A\n========\n\nCOMMON-A-MARKER"`,
`common_b.rst` body is "Common B\n========\n\nCOMMON-B-MARKER"`, `m1.rst` toctree lists `[mid,
common_a]`, `m2.rst` lists `[common_a, common_b]`, `m3.rst` lists `[common_b, mid]`, `mid.rst` lists
`[common_b]`]`. This satisfies SC#3's "≥2 masters and ≥1 shared child" bar exactly as CONTEXT.md
states, with `common_b` reachable from all three masters and `common_a` from two.

**Load-bearing correction to 52-CONTEXT.md's own framing (this is the research finding CONTEXT.md
sent this agent to verify, and it does not land where CONTEXT expected):** CONTEXT.md's D-10 states
"`tests/test_state_guard_composition_gate.py` already satisfies SC#3's bar... [but only makes]
`typst.query` structural assertions... rather than the **PDF-level** assertion SC#3 names". This is
correct as far as it goes — `test_state_guard_composition_gate.py` uses only `state_guard_two_master_gate`
and `state_guard_mirror_pair_gate` (not `state_guard_three_master_gate` at all)
`[VERIFIED: tests/test_state_guard_composition_gate.py:64-66, read this session — `TWO_MASTER_DIR`,
`MIRROR_PAIR_DIR` are the only fixture constants; `state_guard_three_master_gate` does not appear
anywhere in this file]`. **But a separate, sibling module already runs a real PDF-level gate against
the exact `state_guard_three_master_gate` fixture SC#3 asks for**, and 52-CONTEXT.md's own research
priorities never named this module:

`tests/test_state_guard_shapes_gate.py::TestThreeMasterGate::test_three_masters_each_render_shared_children_once`
`[VERIFIED: tests/test_state_guard_shapes_gate.py:437-494, read in full this session]` — builds the
fixture through both `-b typst` and `-b typstpdf`, then for each of the three masters' compiled PDFs:
opens it via `pypdf.PdfReader` and joins every page's `extract_text()` (the same `pdf_text()` helper
`test_state_guard_composition_gate.py` also uses), asserts `COMMON-A-MARKER`/`COMMON-B-MARKER`
occurrence counts (1 in m1/m2 for A, 1 in m1/m2/m3 for B — matching the toctree membership above),
queries resolved heading levels for `common_b`'s label via `typst.query(..., field="level",
root=pdf_dir)` and asserts `[3]`/`[2]`/`[2]` for m1/m2/m3 respectively (nesting position differs
because `common_b` is reached via `mid` in m1 but directly in m2/m3), and asserts the three wrappers'
raw text differ from one another pairwise (proving the state-guard mapping is genuinely per-master).
This is a real, live, `pytest.mark.slow` + `skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE))` gate
already exercising `pypdf` text extraction over a three-master fixture with a shared child — the exact
shape SC#3's goal-claim evidence describes.

**What this existing test does NOT yet do, which the D-10 gate must add or extend for**
(re-derived directly from the fixture's own content, not from any prior test):
1. **No assertion on each master's own unique heading/content, only on the shared children.** The
   fixture has no unique body markers per master beyond the bare headings `M1`/`M2`/`M3`/`Mid`
   themselves — a completeness proof would assert every master's PDF contains its own heading text
   ("M1" in manual1's PDF, etc.) alongside the shared markers, closing the "not silently dropped"
   half of the claim for content that is NOT shared.
2. **No absence assertion.** The existing test proves presence (marker count == 1 where expected) but
   never proves absence where a master should NOT reach a document — e.g. `m3.typ` never toctrees
   `common_a`, so `COMMON-A-MARKER` should occur **0** times in `manual3.pdf`. Asserting this closes
   the complementary "nothing extra leaked in" half, and is a one-line addition
   (`assert _marker_count(m3_text, "COMMON-A-MARKER") == 0`).
3. **No page-count assertion.** SC#3's wording explicitly names "text/page assertions" — the existing
   test asserts text occurrence counts and heading levels (via `typst.query`, not page numbers) but
   never `len(reader.pages)` or a Typst-level page-number query. A page-count sanity check per master
   (e.g. each master's PDF has at least N pages, or the page index a marker's `query()` element
   resolves to) would close this literally.

**Recommendation for the planner (Claude's Discretion per 52-CONTEXT.md, informed by this finding):**
the cheapest, most-consistent-with-precedent path is to **extend**
`TestThreeMasterGate` in `tests/test_state_guard_shapes_gate.py` with the two or three assertions
above, rather than write a wholly new module or a new fixture — the fixture is already load-bearing
and explicitly marked "do NOT touch any of these" in its own header comment
`[VERIFIED: tests/fixtures/state_guard_three_master_gate/conf.py:17-27, read this session]`, so no
fixture edit is implied, only new assertion bodies in the existing test method (or a new sibling test
method in the same class). This keeps D-10's "permanent gate test reusing the existing fixture family"
framing intact while genuinely adding the PDF-level completeness proof CONTEXT.md's own SC#3 language
asks for, and avoids a second three-master fixture existing in the repo for no reason. If the planner
instead judges that a **new module** better fits D-10's "the goal-claim evidence is a new permanent
gate test under `tests/`" phrasing (reading "new... test" literally rather than "new assertions in an
existing test"), that is equally defensible — either way, land it in wave 1 alongside 52-01/52-02 so it
is on the branch before the CI-dispatch wave runs.

### Pattern 4: CI dispatch mechanism (D-08)

**Verified this session, matching CONTEXT.md exactly:** `ci.yml`'s trigger block is
`push: branches: [main, develop]`, `pull_request: branches: [main, develop]`, `workflow_dispatch:`
`[VERIFIED: .github/workflows/ci.yml:1-9, read this session]`. A push to
`gsd/v0.8.0-multi-master-composition` therefore starts nothing but the separate Link Check workflow
— confirmed live: the last 8 runs on this branch are seven `Link Check` successes and one `CI`
`workflow_dispatch` success (`31492380799`, 2026-08-11) plus one earlier `CI` `workflow_dispatch`
failure (`31491228938`) `[VERIFIED: gh run list output, this session, timestamps and IDs quoted
verbatim above]`. This confirms `workflow_dispatch` is genuinely the only trigger this branch can use
without opening a PR.

**Exact command sequence** (same shape as Phase 46's `46-01-PLAN.md`/`46-04-PLAN.md` Task 1, this
time as a standalone step since there is no merge to fold it into):
```bash
git push origin HEAD:refs/heads/gsd/v0.8.0-multi-master-composition   # plain fast-forward, never force
gh workflow run ci.yml --ref gsd/v0.8.0-multi-master-composition
gh run list --workflow=ci.yml --branch gsd/v0.8.0-multi-master-composition \
  --limit 5 --json databaseId,headSha,event,status
# poll until a workflow_dispatch run's headSha == the pushed SHA; export databaseId as RUN_ID
gh run watch "$RUN_ID"
gh run view "$RUN_ID" --json jobs
```
Job-name set to expect all-`success` on, read from `ci.yml` this session
`[VERIFIED: .github/workflows/ci.yml:12,52,73,94,128,157, read this session]`: the six
`Test Python {3.12,3.13} on {ubuntu,windows,macos}-latest` matrix lanes, `Lint and Format Check`,
`Type Check`, `Code Coverage`, `Build Package`, and `Integration Test - {basic,advanced}`. Record the
run id, its `.../actions/runs/<id>` URL, and the full job table verbatim in `52-CI-EVIDENCE.md` (or
equivalently-named evidence file — Phase 46 named its two runs "run 1"/"run 2"; this phase needs only
one run, since there is no separate Windows-repair check run to prove first).

**D-08's stated reason CI, not local, is lint/type/matrix authority:** `ruff` cannot execute on this
machine at all — `.venv/bin/ruff` is a generic-linux ELF the NixOS stub loader rejects, exit 127
`[VERIFIED: .planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md, read
this session — the transcript quoted therein is itself dated and unchanged]`. This is confirmed
**still open** per the user's own memory index ("ruff の ELF 問題だけ現存" — only the ruff ELF issue
remains, as of 2026-08-14) — the sibling `tox-uv`→`tox-uv-bare` `uv` shim issue this same todo family
once carried was separately resolved and is not relevant here. `tox.ini`'s `env_list` includes `lint`
`[VERIFIED: tox.ini:2, read this session]`, so a bare `tox` invocation dies at that environment;
run each environment individually (`tox -e docs-html`, `tox -e docs-pdf`, direct `pytest`) rather than
a bare `tox`, exactly as Phase 46's `46-04-PLAN.md` Task 2 instructs.

### Pattern 5: SC#4's invariant sweep, and what a real positive control looks like

**All three commands re-run live this session, matching CONTEXT.md's D-09 figures exactly:**
```
$ git diff v0.7.1..HEAD --stat -- . ':(exclude).planning' | tail -1
341 files changed, 15141 insertions(+), 2472 deletions(-)
$ git diff v0.7.1..HEAD -- pyproject.toml
(empty)
$ git diff v0.7.1..HEAD -- typsphinx/__init__.py | grep add_config_value
(empty)
$ grep -c "@preview" typsphinx/templates/base.typ
4
```
`[VERIFIED: git diff / grep output, this session — commands and output quoted verbatim above]`.
`v0.7.1` resolves to `48bf135428bb093a77a432d93d16088ce6930342` and `origin/main` resolves to
`a97fe736a4311cf04109cfafd1154a3e3b95d208`, which **is** `git merge-base origin/main HEAD`
`[VERIFIED: git rev-parse and git merge-base output, this session]` — confirming D-09's anchor
coincidence still holds and the sweep can run at either anchor with the same result.

**What a genuine positive control looks like (the part CONTEXT.md flags as needing actual thought,
not a restatement):** an assertion that would *fail* if the sweep were vacuous must independently
demonstrate the detector's own sensitivity, not merely re-state the invariant. Two concrete, cheap
controls:
1. **For the dependency invariant:** the sweep's own command (`git diff v0.7.1..HEAD -- pyproject.toml`)
   trivially proves emptiness — but an empty diff is also what a *no-op grep on the wrong file* would
   produce. The real control is: (a) confirm the file has non-trivially changed lines *elsewhere* in
   the same milestone (it hasn't — `pyproject.toml`'s diff really is empty end-to-end, so this
   particular invariant has no non-vacuous control available at the file level) — record this
   explicitly as "no dependency was ever proposed or reverted this milestone, so this invariant's
   control is the shortstat's own non-zero file count (341 files) demonstrating the diff mechanism
   itself is live, not that this specific file is watched" — i.e. borrow the shortstat as the sweep's
   own liveness proof, since a `git diff` against a non-existent range or a wrong ref would produce
   an empty *shortstat* too, and 341/15141/2472 is not zero.
2. **For the `@preview` invariant:** a genuine control exists and is cheap — temporarily count
   `@preview` occurrences against a DELIBERATELY WRONG anchor or pattern and show the count differs
   from 4 in a way the detector would catch, e.g. `grep -c "@preview" typsphinx/writer.py` (expect a
   non-zero count reflecting the same four import lines) and cross-check it against
   `tests/test_preview_version_sync.py::test_all_four_packages_declared`'s own pass/fail — that test
   is a genuine mechanical positive control already in the suite: if a fifth package were declared
   in only one of the four surfaces, this specific test would fail (it has done so historically —
   `test_preview_version_sync.py`'s own docstring and Phase 46's evidence record it catching drift at
   the v0.6.3 close, per `STATE.md`'s "custom.typ three milestones behind on its `@preview` pins"
   incident). Citing that historical catch **is** the positive control SC#4 asks for — it is evidence
   the detector fires on a real violation, not merely evidence the current tree is clean.
3. **For the config-value invariant:** run the same `grep add_config_value` command against a known
   *positive* case from history — e.g. `git diff v0.6.2..v0.6.3 -- typsphinx/__init__.py | grep
   add_config_value` should show a real historical addition (CONF-04's `typst_elements` era) if any
   config value was ever added in this project's history, proving the grep pattern itself catches a
   real addition when one exists, rather than being a pattern that would silently match nothing on any
   input. Record whichever historical range demonstrates a non-empty match as the control.

Phase 46's own `46-SC4-INVARIANTS.md` did not attempt this — it recorded figures and reasoning but no
independent liveness-of-the-detector proof; this is a genuine gap in the prior precedent, not
something to copy forward uncritically. The planner should treat SC#4's positive-control ask as new
work for this phase, not "already solved, repeat the pattern."

### Pattern 6: The prep/publish fence — exact command list

**Forbidden (irreversible), verbatim from every prior release-prep phase's own convention, unchanged
here:**
- `git tag v0.8.0` (or any tag) — locally or on `origin`.
- Any trigger of `.github/workflows/release.yml` as a real run (a real tag push, or
  `workflow_dispatch` with a `tag` input against that specific workflow) — static reads and hand-runs
  of the script it calls are fine; triggering the workflow itself is not.
- `pip install --upload` / `twine upload` / any PyPI publish action.
- Creating a GitHub Release (`gh release create`, or `softprops/action-gh-release` firing for real).
- Opening OR merging a pull request (`gh pr create`, `gh pr merge`) — this is explicitly distinct from
  pushing a branch; `ci.yml`'s `pull_request: [main, develop]` trigger means opening a PR would ALSO
  fire CI a second, unwanted way, and merging is definitionally the publish-half's first step.
- Advancing the `typsphinx-doc-translations` submodule pin or pushing a tag there.
- Flipping REL-07's checkbox or Traceability row in `REQUIREMENTS.md` (the `phase.complete`
  auto-flip hazard the project's own memory index names — verify this does not fire, or revert it if
  it does).

**Permitted (reversible), and exercised by this phase:**
- Editing any tracked file (version literals, CHANGELOG, docs, new test module).
- `git commit`, `git push origin HEAD:refs/heads/gsd/v0.8.0-multi-master-composition` (plain
  fast-forward — the branch already exists on `origin` per milestone invariant #5).
- `gh workflow run ci.yml --ref <branch>` — `workflow_dispatch` on `ci.yml`, **not** `release.yml`.
- `uv lock`, `uv sync`, `tox -e <env>`, `pytest`.
- Reading/hand-running `scripts/extract_changelog_section.py` as a subprocess — it has no side
  effects (confirmed by its own docstring: "used ONLY for a string-equality comparison... never
  interpolated into a shell command, never `eval`'d" `[VERIFIED: scripts/extract_changelog_section.py:36-41, read this session]`).

**Verification shape (two independent observations, per the standing `35-HANDOFF.md`/`41-HANDOFF.md`/
`46-HANDOFF.md` convention, re-cite rather than re-derive):** `git tag -l v0.8.0` and
`git ls-remote --tags origin v0.8.0` both empty, measured **twice**, at two separate moments, in two
separate files — the roll-up (`52-RELEASE-EVIDENCE.md`) and the handoff (`52-HANDOFF.md`), each with
its own `date -u` timestamp. Confirmed both empty this session:
```
$ git tag -l v0.8.0
$ git ls-remote --tags origin v0.8.0
```
`[VERIFIED: command output, this session — both silent/empty, exit 0]`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CHANGELOG → GitHub Release body extraction | A second parser or shell one-liner | `scripts/extract_changelog_section.py` (already committed, pytest-covered) | The module docstring itself states this is deliberately "the ONE committed, pytest-covered implementation" so nothing can silently diverge from what CI runs |
| Multi-master PDF fixture | A new fixture from scratch | `tests/fixtures/state_guard_three_master_gate/` | Already satisfies the ≥2-masters/≥1-shared-child bar; its own header comment marks it load-bearing and forbids editing |
| pypdf text-extraction helper | A new extraction function | The `pdf_text()` / `_extract_pdf_text()` idiom already duplicated (deliberately, per each module's own convention) across 20+ gate modules | `reader = pypdf.PdfReader(str(path)); "\n".join(page.extract_text() for page in reader.pages)` — copy this exact idiom, don't invent a variant |
| CI dispatch and polling | A custom polling script | `gh workflow run` + `gh run list --json` + `gh run watch` + `gh run view --json jobs` | Already the established idiom in `46-01-PLAN.md`/`46-04-PLAN.md`; `gh` is authenticated and has dispatched runs on this exact repo before |
| Version-sync guarding | A new ad-hoc script comparing versions | The three existing pytest modules (`test_extension.py`, `test_readme_version_sync.py`, `test_preview_version_sync.py`) | Already exist, already pass, already the acceptance bar for SC#1 |

**Key insight:** every mechanism this phase needs already exists in the repo, proven across four to
six prior release-prep phases. The only genuinely new artifact is D-10's gate-test extension/addition
(Pattern 3), and even that reuses an existing fixture and an existing (partial) test class rather than
building anything from zero.

## Common Pitfalls

### Pitfall 1: Assuming D-10's gate is greenfield when it is 80% already-shipped

**What goes wrong:** A plan that treats "write a new permanent PDF-level gate test" as building from
nothing duplicates `TestThreeMasterGate`'s existing marker-count/heading-level assertions, creating
two near-identical test classes over the same fixture with drift risk between them.
**Why it happens:** 52-CONTEXT.md's own D-10 discussion names `test_state_guard_composition_gate.py`
(which genuinely lacks PDF-level assertions) as "the existing composition gate," and never mentions
`test_state_guard_shapes_gate.py::TestThreeMasterGate`, which already has PDF-level assertions on the
exact fixture SC#3 names.
**How to avoid:** Extend the existing class (Pattern 3's three concrete additions: own-heading
presence, absence-where-not-toctree'd, page-count) rather than writing a parallel module. If a new
module is still judged the better shape, it must import/reuse the fixture path and the `pdf_text()`
idiom, and its docstring must explicitly cross-reference `TestThreeMasterGate` so a later reader
understands why two classes cover overlapping ground.
**Warning signs:** A plan whose `files_modified` proposes a brand-new fixture directory under
`tests/fixtures/` for "the three-master gate" — that fixture already exists and is marked
load-bearing/do-not-touch in its own header comment.

### Pitfall 2: `RELEASE_VERSIONS` ordering dependency (recurring across every prior curation phase)

**What goes wrong:** Appending `"0.8.0"` to `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS`
tuple before `## [0.8.0]` exists in `CHANGELOG.md` makes `TestChangelogPageContentCoverage` fail (the
gate asserts every listed release's content actually appears in the built page).
**Why it happens:** The CHANGELOG plan and the version-bump plan run in the same wave, in parallel,
with the RELEASE_VERSIONS append potentially landing in either.
**How to avoid:** Sequence the append as the LAST sub-step of the CHANGELOG plan, gated on a
`<precondition>` that `## [0.8.0]` already exists — exactly as `46-03-PLAN.md` Task 3 encodes it.
**Warning signs:** `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py` reporting
a failure whose message names a missing heading.

### Pitfall 3: Running a bare `tox` and mistaking the `lint` env's exit 127 for a real CI-parity check

**What goes wrong:** `tox.ini`'s `env_list = py312, py313, lint, type, cov, docs`
`[VERIFIED: tox.ini:2, read this session]` — a bare `tox` invocation attempts the `lint` environment,
which dies at exit 127 on this NixOS machine because `.venv/bin/ruff` is a generic-linux ELF the stub
loader rejects.
**Why it happens:** Muscle memory from other projects, or a plan action that says "run the full test
suite" without specifying individual `-e` targets.
**How to avoid:** Always target environments individually: `tox -e docs-html`, `tox -e docs-pdf`,
direct `pytest` invocations. Never a bare `tox`. This is unchanged from Phase 46's own documented
pitfall and is not specific to this milestone.
**Warning signs:** Exit code 127 from a `tox` invocation with `lint` named in the failure output.

### Pitfall 4: Treating `test_corpus_gate.py`'s skip as a pass

**What goes wrong:** `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`
is `@pytest.mark.slow` and calls `pytest.skip(...)` — never fails — when the corpus (a network clone)
is unavailable `[VERIFIED: tests/test_corpus_gate.py:270-284, read this session]`. A transcript that
says "0 failed" without distinguishing "1 passed" from "1 skipped" is not evidence the gate ran.
**Why it happens:** Summary-line skimming (e.g. "1 passed, 0 failed" superficially looks green even
when the test was actually skipped and a different test in the same module passed).
**How to avoid:** Always capture the per-test PASSED/SKIPPED distinction (`-v`, or a JUnit XML with
explicit `skipped=` count check), exactly as `46-04-PLAN.md` Task 2's acceptance criteria require.
**Warning signs:** An evidence file that quotes a pytest summary line without the individual test's
own PASSED/SKIPPED status.

### Pitfall 5: Reporting REL-07 (or its Traceability row) complete before the publish

**What goes wrong:** `phase.complete` has a **recorded, repeated habit** of auto-flipping REL rows
against a CONTEXT decision — caught in Phase 41, pre-empted in Phase 42 by `42-CLOSEOUT-GUARD.md`, and
this project's own auto-memory names it as a general hazard ("phase.complete が繰り越し要件を勝手に
フリップする").
**Why it happens:** A generic closeout automation pattern-matches on "requirement fully addressed by
this phase's own success criteria" without understanding the requirement's acceptance evidence is
generated by a LATER command (`/gsd-complete-milestone`).
**How to avoid:** Diff `.planning/REQUIREMENTS.md` after running `phase.complete` and before
committing the close; if REL-07's checkbox or Traceability row changed, revert it and re-apply the
correct (still-Pending) state by hand — exactly as `46-HANDOFF.md` item 6 documents.
**Warning signs:** `git diff --name-only -- .planning/REQUIREMENTS.md` showing a change this phase's
own plans never intended.

## Code Examples

### Version bump, exact sequence (verified against the live tree this session)

```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
# edit pyproject.toml:7  -> version = "0.8.0"
# edit README.md:347     -> **Status**: Stable (v0.8.0) - Production ready
uv lock
uv sync --extra dev --locked
uv run python -c "import typsphinx; print(typsphinx.__version__)"   # expect 0.8.0
uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml \
  tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v
```

### CHANGELOG extraction and validation-job precondition check

```bash
uv run python scripts/extract_changelog_section.py 0.8.0    # exit 0, non-empty body
uv run python scripts/extract_changelog_section.py 9.9.9    # exit 1, stderr message -- empty-input control
```

### CI dispatch and read

```bash
git push origin HEAD:refs/heads/gsd/v0.8.0-multi-master-composition
gh workflow run ci.yml --ref gsd/v0.8.0-multi-master-composition
gh run list --workflow=ci.yml --branch gsd/v0.8.0-multi-master-composition \
  --limit 5 --json databaseId,headSha,event,status
gh run watch "$RUN_ID"
gh run view "$RUN_ID" --json jobs
```

### SC#4 invariant sweep

```bash
git diff v0.7.1..HEAD --stat -- . ':(exclude).planning'
git diff v0.7.1..HEAD -- pyproject.toml                                  # expect empty
git diff v0.7.1..HEAD -- typsphinx/__init__.py | grep add_config_value   # expect empty
grep -c "@preview" typsphinx/templates/base.typ                          # expect 4
uv run pytest tests/test_preview_version_sync.py -v
```

### D-10 gate-test extension pattern (idiom to copy, from `test_state_guard_shapes_gate.py`)

```python
# Source: tests/test_state_guard_shapes_gate.py:125-128 (existing helper, quote the exact idiom)
def pdf_text(self, target: str) -> str:
    pdf_path = self.pdf_dir / target.replace(".typ", ".pdf")
    reader = pypdf.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() for page in reader.pages)

# New assertion shape to add (own-heading presence + absence-where-not-reachable):
m3_text = build.pdf_text("manual3.typ")
assert "M3" in m3_text                                    # own heading present
assert _marker_count(m3_text, "COMMON-A-MARKER") == 0      # not reachable from m3 -- must be absent
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| One CHANGELOG curation phase authors the migration guide from scratch | Phase 51 already authored the migration guide; this phase verifies agreement | Phase 51, 2026-08-15 | The CHANGELOG plan's `docs/source/changelog.rst` task shrinks from "write" to "confirm" |
| SC#3's goal claim proved by a one-off transcript | SC#3's goal claim proved by a permanent gate test (D-10, following 51-CONTEXT D-10's own precedent) | This phase, per Phase 51's own precedent | The evidence keeps proving itself on every future CI run, not just at this phase's close |
| Release-prep phases include a REL-04-shaped "in-phase precondition, evidence owed at publish" split | Not applicable this milestone — REL-07 has no such split; it is entirely publish-gated | v0.8.0 roadmap, 2026-08-11 | One fewer plan/evidence-file pair than Phase 46 needed |

**Deprecated/outdated:** none — every mechanism cited is the current, live state of the tooling.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The exact final wave/plan decomposition (7 plans / 3 waves) is a recommendation derived from Phase 46's precedent, not a verified requirement — the planner may reasonably choose a different split (e.g. folding 52-06's invariant sweep into the roll-up plan) | Architecture Patterns § Recommended plan/wave decomposition | Low — this is explicitly framed as a recommendation, and CONTEXT.md leaves "plan decomposition and ordering" to Claude's Discretion |
| A2 | The recommendation to *extend* `TestThreeMasterGate` rather than write a new module (Pattern 3) is this researcher's judgment call, not a locked decision — CONTEXT.md's D-10 explicitly leaves "whether the fixture is reused as-is or extended" to the planner | Pattern 3 | Low — flagged explicitly as a recommendation with reasoning, and the alternative (new module) is stated as equally defensible |
| A3 | SC#4's "positive control" proposals (Pattern 5, items 1-3) are this researcher's own derivation of what a non-vacuous control looks like — no prior phase's evidence file attempted this rigorously, so there is no precedent to cite as authoritative | Pattern 5 | Medium — if the planner disagrees with this framing, SC#4's acceptance criterion for "a real positive control" needs independent resolution at plan-write time, not blind adoption of this research's proposal |

## Open Questions

1. **Does the third breaking change (the collision hard error, D-04) already have text in
   `docs/source/changelog.rst`'s migration guide?**
   - What we know: Phase 51 wrote exactly two breaking-change items into that section (output shape,
     target-as-path reversal) — confirmed by reading the section's opening sentence ("carries three
     breaking changes") against only two items visible in the first ~40 lines read this session.
   - What's unclear: whether a third item continues past line 40 (not read this session — the read
     was capped) or whether Phase 51 deliberately deferred the third item to this phase.
   - Recommendation: the CHANGELOG-curation plan's `<read_first>` must read
     `docs/source/changelog.rst` in FULL (not just its first 40 lines) before deciding whether that
     file needs a third item added, or whether the collision-error breaking change is instead expected
     to live only in `CHANGELOG.md` per D-04's bullet list.

2. **Exact wording/placement decisions D-07 leaves open (8-9 bullets, section assignment) are
   Claude's Discretion** — this research does not resolve them; the planner and/or the executing plan
   authors that content directly against `52-CONTEXT.md`'s own specifics section and the milestone's
   24 v1 requirements.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` (bare, on PATH) | version bump, all `uv run` invocations | ✓ | on PATH per `CLAUDE.md` | — |
| `git` | every task | ✓ | system | — |
| `gh` (authenticated) | CI dispatch, run polling | ✓ — confirmed live this session (`gh run list` succeeded) | — | — |
| `typst`-py / `pypdf` | D-10's gate test, docs-pdf build | ✓ (already dev-extra deps) | — | — |
| `ruff` | `tox -e lint` | ✗ — generic-linux ELF, exit 127 on this NixOS machine | — | CI is lint authority (D-08); local `black --check` / `mypy` still run fine (pure Python) |
| standalone CPython 3.12 (`tox -e py312`) | — | ✗ — ELF the stub loader rejects | — | `tox -e py313` (matches system interpreter) or direct `uv run pytest`; CI covers the full matrix |
| `myst-parser` | `TestChangelogPageContentCoverage` / `TestChangelogIncludeCompilesToPdf` | only under `--extra docs` | — | run with `uv run --extra dev --extra docs pytest ...` |

**Missing dependencies with no fallback:** none — every gap above has a documented, already-exercised
fallback from prior phases.

**Missing dependencies with fallback:** `ruff` (→ CI), `tox -e py312` (→ `tox -e py313` / direct
`pytest`), `myst-parser` (→ `--extra docs`).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), `tox` as task runner |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`), `tox.ini` |
| Quick run command | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` |
| Full suite command | dispatched CI (`gh workflow run ci.yml --ref <branch>`) is the matrix/lint/type authority per D-08; locally, `uv run pytest tests/ -v` plus `tox -e docs-html`/`tox -e docs-pdf`/`uv run pytest tests/test_corpus_gate.py -v` cover what CI does not |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REL-07 (SC#1) | Version literals move in lockstep | unit | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` | ✅ |
| REL-07 (SC#2) | Curated `## [0.8.0]` CHANGELOG entry, extractable, page gate current | integration | `uv run python scripts/extract_changelog_section.py 0.8.0` + `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` | ✅ |
| REL-07 (SC#3, toolchain half) | Post-bump tree green (pytest/lint/type/docs builds/corpus gate) | integration/e2e | dispatched `ci.yml` run + `tox -e docs-html`/`docs-pdf` + `uv run pytest tests/test_corpus_gate.py -v` | ✅ (CI workflow); local envs exist |
| REL-07 (SC#3, goal-claim half) | Multi-master round trip proven on generated PDF evidence | e2e/gate | `uv run pytest tests/test_state_guard_shapes_gate.py::TestThreeMasterGate -v` (extended per D-10) | ✅ Wave 1 extension needed — see Pattern 3 |
| REL-07 (SC#4) | Milestone invariants asserted mechanically with a real positive control | unit/script | the four `git diff`/`grep` commands in Pattern 5 + `uv run pytest tests/test_preview_version_sync.py -v` | ✅ (commands); positive control is new authored work |
| REL-07 (SC#5) | No irreversible action; standalone handoff exists | manual + script | `git tag -l v0.8.0 && git ls-remote --tags origin v0.8.0` (both empty, x2) | ✅ |

### Sampling Rate

- **Per task commit:** the relevant guard-test subset (version-sync trio for the bump plan; page-gate
  module for the CHANGELOG plan; the extended `TestThreeMasterGate` for the gate-test plan).
- **Per wave merge:** `uv run pytest tests/ -v` locally as a spot-check (never presented as authority
  for lint/matrix — that's CI, D-08).
- **Phase gate:** dispatched CI run all-green + both `tox -e docs-*` + `test_corpus_gate.py` (PASSED or
  honestly SKIPPED, never conflated) before `/gsd-verify-work`.

### Wave 0 Gaps

None — every test module and fixture this phase needs already exists in the repository; the only new
test content is additive assertions inside (or a sibling to) an existing, already-passing test class.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | This phase touches no auth surface |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes (narrow) | `scripts/extract_changelog_section.py`'s `version` argument is used only for string-equality comparison, never interpolated into a shell command or `eval`'d `[VERIFIED: scripts/extract_changelog_section.py:36-41, read this session]` — this phase exercises, not modifies, that invariant |
| V6 Cryptography | no | N/A |

### Known Threat Patterns for this stack (release-engineering specific)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A crafted git tag name (backticks, `$()`, quotes) executing shell in a `contents: write` / `id-token: write` job | Tampering / Elevation of privilege | `.github/workflows/release.yml` passes every `${{ }}` through `env:` rather than interpolating into `run:` blocks — an existing, documented invariant `[VERIFIED: .github/workflows/release.yml:38-44,176-181, read this session]`; this phase's job is only to confirm `git diff v0.7.1..HEAD -- .github/workflows/release.yml` shows no unintended change, not to modify the file |
| Reporting a requirement complete on the strength of code correctness rather than generated evidence | Repudiation | Named explicitly in the phase's own goal (lesson 12b) — SC#3's goal-claim half exists precisely to close this gap for the milestone's own core claim; REL-07's checkbox must not flip before the publish (Pitfall 5) |
| A test gate silently weakened (skip guard loosened) to force a green run | Tampering | Every prior phase's acceptance criteria assert `git diff` is confined to the intended lines (e.g. `RELEASE_VERSIONS`'s tuple/comment only) — carry the same discipline into this phase's plans |

## Sources

### Primary (HIGH confidence — read directly this session)

- `pyproject.toml`, `README.md`, `uv.lock`, `CHANGELOG.md`, `docs/source/changelog.rst`,
  `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `scripts/extract_changelog_section.py`,
  `tests/test_extension.py`, `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`,
  `tests/test_changelog_page_gate.py`, `tests/test_corpus_gate.py`,
  `tests/test_state_guard_composition_gate.py`, `tests/test_state_guard_shapes_gate.py`,
  `tests/test_output_layout_docs_gate.py`, `tests/fixtures/state_guard_three_master_gate/*`,
  `tox.ini`, `.planning/todos/pending/*` (9 files), `.planning/REQUIREMENTS.md`, `.planning/STATE.md`,
  `.planning/phases/52-v0-8-0-release-prep-prep-only/52-CONTEXT.md`.
- `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/` — all six `PLAN.md` files,
  `46-HANDOFF.md`, in full.
- Live `git`/`gh` commands executed this session (version diffs, invariant sweep, CI run list, tag
  emptiness).

### Secondary (MEDIUM confidence)

- User's own auto-memory index (`~/.claude/projects/.../memory/MEMORY.md`) — cross-checked the ruff
  ELF hazard's current status ("only the ruff ELF issue remains, as of 2026-08-14"), consistent with
  the live-read todo file.

### Tertiary (LOW confidence)

- None — every claim in this document traces to a file read or a command run this session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new library, every version-sync mechanism read directly from source
- Architecture / plan decomposition: HIGH for the mechanism, MEDIUM for the specific wave/plan split
  (explicitly flagged A1 as a recommendation, not a verified requirement)
- Pitfalls: HIGH — four of five are directly inherited from Phase 46's own documented, executed
  experience; the fifth (D-10 gate discovery) is a fresh finding verified by direct source reads
- SC#4 positive control: MEDIUM — no prior phase attempted this rigorously; this research's proposal
  is reasoned but unprecedented in this project's own evidence-file history (flagged A3)

**Research date:** 2026-08-15
**Valid until:** this phase's own execution (release-prep research is single-use; the live git state
this research is anchored to — `v0.7.1` at `48bf135`, `origin/main` at `a97fe73`, 157 commits ahead of
origin — will have moved by the time any other phase reads this file)
