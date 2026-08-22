# Phase 57: v0.9.0 Release Prep (prep-only) - Pattern Map

**Mapped:** 2026-08-16
**Files analyzed:** 13 (10 code/doc files to edit, 3 evidence/handoff artifact families to create)
**Analogs found:** 13 / 13

This is a release-prep phase. The dominant analog relationship is **"the same file at the previous
release"** — `CHANGELOG.md`'s own `## [0.8.0]`/`## [0.7.1]` sections, `docs/source/changelog.rst`'s
own `Migrating from 0.7.x to 0.8.0` section, and Phase 52's/46's own plan and evidence artifacts are
all closer analogs than anything found by role/data-flow search in the traditional sense.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pyproject.toml` (version literal, line 7) | config | transform (literal bump) | Same file, `v0.7.1→v0.8.0` bump (`52-01-PLAN.md` Task 1) | exact |
| `README.md` (Status line, line 347) | config/docs | transform | Same file, same prior bump | exact |
| `uv.lock` | config | batch (regenerated) | Same file, same prior bump | exact |
| `CHANGELOG.md` `## [0.9.0]` new section | docs | transform (prose curation) | `CHANGELOG.md`'s own `## [0.8.0]` (structure) + `## [0.7.1]` `### Removed` (D-03 model) | exact |
| `CHANGELOG.md` tail link block (2-line edit) | docs | transform | Same file's tail block, same edit shape at every prior release | exact |
| `tests/test_changelog_page_gate.py` `RELEASE_VERSIONS` (+ comment) | test/config | transform | Same file's own tuple, appended at every prior release | exact |
| `docs/source/changelog.rst` new `Migrating from 0.8.x to 0.9.0` section | docs | transform | Same file's own `Migrating from 0.7.x to 0.8.0` (83 lines) | exact |
| `57-BUMP-EVIDENCE.md` (or similarly named) | test/evidence | batch (transcript capture) | `52-BUMP-EVIDENCE.md` / `46-BUMP-EVIDENCE.md` | exact |
| `57-CI-EVIDENCE.md` | test/evidence | event-driven (CI dispatch + poll) | `52-CI-EVIDENCE.md` / `46-CI-EVIDENCE.md` | exact |
| `57-GREEN-TREE-EVIDENCE.md` | test/evidence | batch | `52-GREEN-TREE-EVIDENCE.md` / `46-GREEN-TREE-EVIDENCE.md` | exact |
| `57-GOAL-CLAIM-EVIDENCE.md` (D-14 gate re-run) | test/evidence | batch | `52-GOAL-CLAIM-EVIDENCE.md` | exact |
| `57-SC4-INVARIANTS.md` (D-15 milestone-diff sweep) | test/evidence | transform (git diff/grep assertions) | `52-SC4-INVARIANTS.md` / `46-SC4-INVARIANTS.md` | exact |
| `57-HANDOFF.md` | docs | request-response (checklist consumed by `/gsd-complete-milestone`) | `52-HANDOFF.md` / `46-HANDOFF.md` | exact |

**Reserved name — do not create:** `57-VERIFICATION.md` is owned by the verifier and will be
clobbered if a plan writes evidence there (per `46-CONTEXT.md` D-15, restated in this phase's own
CONTEXT). The `52-*-EVIDENCE.md` family above is the naming precedent to follow instead.

## Pattern Assignments

### `pyproject.toml` / `README.md` / `uv.lock` (config, transform)

**Analog:** the same three files at the v0.8.0 bump, procedure recorded in
`.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-01-PLAN.md`.

**Current state to edit (read this session):**
```toml
# pyproject.toml:7
version = "0.8.0"
```
```markdown
<!-- README.md:347 -->
**Status**: Stable (v0.8.0) - Production ready
```
```
# uv.lock, the `typsphinx` block
name = "typsphinx"
version = "0.8.0"
source = { editable = "." }
```

**Core pattern — the exact 5-step sequence** (from `52-01-PLAN.md`'s `key_links` + this phase's
`57-RESEARCH.md` Pattern 1, unchanged since Phase 46/52):
```bash
# 1. confirm no second accidental version-shaped literal has appeared
git diff v0.8.0..HEAD -- pyproject.toml
# 2. edit pyproject.toml:7 and README.md:347 -> "0.9.0"
# 3. regenerate the lockfile's own typsphinx block
uv lock
# 4. --locked fails loudly on any lock/manifest disagreement; this is what
#    regenerates the .dist-info/.pth editable-install metadata
uv sync --extra dev --locked
# 5. confirm the version now reads through importlib.metadata, not the literal
uv run python -c "import typsphinx; print(typsphinx.__version__)"  # -> 0.9.0
```

**Guard tests that must stay green** (re-run verbatim, from `57-RESEARCH.md` Pattern 1, already
passing pre-bump this session):
```
tests/test_extension.py::test_version_matches_pyproject_toml
tests/test_readme_version_sync.py::test_readme_status_version_matches_pyproject
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites
tests/test_preview_version_sync.py::test_all_four_packages_declared
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions
```
These re-parse `pyproject.toml`/`README.md` independently via `tomllib`/regex — genuine drift
guards, not tautologies.

**Must-have truths pattern** (copy this shape from `52-01-PLAN.md`'s `must_haves.truths` block —
each is a falsifiable, command-backed claim, not a narrative): sole-literal claim, `__version__`
print claim, `uv sync --locked` + `uv lock --check` exit-0 claim, the three guard-test-modules
green-with-zero-skips claim, `scripts/extract_changelog_section.py` still running against an
already-published version, the fence observation (`git tag -l v0.9.0` / `git ls-remote --tags
origin v0.9.0` both empty), anchor figures re-measured live not transcribed from CONTEXT/RESEARCH,
and "nothing under `typsphinx/` changed in this plan."

---

### `CHANGELOG.md` — the `## [0.9.0]` section (docs, transform)

**Analog 1 — structural model:** `## [0.8.0]` (`CHANGELOG.md:82` onward, read this session): lead
paragraph → `### Added` / `### Changed` → `### Fixed` → `### Verified`. Lead paragraph pattern to
copy (substituting this milestone's headline):
```markdown
## [0.8.0] - 2026-08-15

This release makes multi-master composition work: a `typst_documents` configuration declaring
more than one master now produces a complete PDF for each of them, ... **this minor release can
break a working configuration** — read the `### Changed` section below, and see the "Migrating
from 0.7.x to 0.8.0" guide in the published documentation for the exact rewrite each of the three
breaking changes needs.
```
Per D-04, the 0.9.0 lead must additionally state what is *not* breaking (the registry is additive;
no existing `conf.py` needs editing) — no exact precedent line for this half; author fresh.

**Analog 2 — the `## [Unreleased]` block to promote** (`CHANGELOG.md:8-79`, quoted in full this
session — D-02 says promote substantially as written): two `**Breaking:**` bullets under
`### Changed` (OUT-04 shadow-route relocation; WR-01/CR-01 pre-write validation) and five bullets
under `### Fixed` (XREF-05, BLD-07, BLD-08, BLD-09, IMG-03). Copy verbatim, editing only what
promotion requires (e.g. removing "Unreleased"-only framing if any).

**Analog 3 — the `### Removed` bullet model, D-03's exact precedent** (`CHANGELOG.md:155-165`,
`## [0.7.1]`'s `typst_authors` entry, quoted in full):
```markdown
### Removed

- **Breaking:** the `typst_authors` config value is removed (CONF-10) -- 0.7.0's documentation
  announced its removal in a future major release; this patch release removes it now.
  `typst_authors` is an unregistered `conf.py` variable that Sphinx ignores without any warning, so
  a project that still sets it loses its author information silently. See the migration guide for
  the `typst_template_function` `params["authors"]` rewrite; there is no deprecation shim.
```
D-03 deliberately inverts the last clause — the new `typst_template_assets` bullet must say a
warning shim **does** exist. The exact warning text to cite/paraphrase, already written with this
release in mind (`typsphinx/removed_config.py:35-41`, read in full this session):
```python
"typst_template_assets": (
    "'typst_template_assets' was removed in v0.9.0 and is now ignored. "
    "Every used template's bundle directory (the resolved template "
    "file's parent) is copied wholesale to the output tree, so MORE "
    "files now reach the output than the explicit list used to select "
    "-- no asset list is needed any more."
),
```
The `### Removed` bullet must agree with the "Removed Configuration Values" table already published
at `docs/source/user_guide/configuration.rst:603-640` (Phase 56) — do not restate a different reason
independently.

**Analog 4 — `### Verified`'s exact unchanged three-item model** (`CHANGELOG.md:148-153`, quoted in
full this session — D-05 says keep this wording unchanged for 0.9.0 too):
```markdown
### Verified

- No new **runtime** dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.
```
The first bullet's supporting evidence for 0.9.0 is a hunk-level argument (`pyproject.toml`'s
diff is confined to `[tool.setuptools.package-data]`'s glob, touching zero dependency lines — see
`57-RESEARCH.md` Pattern 6 for the full diff text), not an empty-diff claim.

**Analog 5 — the tail link block, routine two-line edit, exact current state** (`CHANGELOG.md` tail,
read in full this session):
```
[0.8.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
...
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.8.0...HEAD
```
Edit: insert `[0.9.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.0` immediately
above the `[0.8.0]:` line; change `[Unreleased]`'s compare base to `v0.9.0...HEAD`. **Do not** treat
this as a repair — the block is already complete (no missing `[0.8.0]` line, contra an earlier,
retracted CONTEXT.md claim).

---

### `tests/test_changelog_page_gate.py` — `RELEASE_VERSIONS` (test/config, transform)

**Analog:** the tuple's own prior append, same file (`tests/test_changelog_page_gate.py:43-58`,
read in full this session):
```python
# The 14 releases the published page was frozen without (0.4.4 through 0.8.0,
# inclusive) -- shared by both the HTML and PDF content-coverage assertions
# below so the two builders are held to the identical bar.
RELEASE_VERSIONS = (
    "0.4.1", "0.4.2", "0.4.3", "0.4.4", "0.5.0", "0.6.0", "0.6.1", "0.6.2",
    "0.6.3", "0.6.4", "0.6.5", "0.7.0", "0.7.1", "0.8.0",
)
```
Pattern: append `"0.9.0"`, move the comment's release-count and version-range prose to 15/`0.9.0`.
**Ordering constraint** (Claude's Discretion, per CONTEXT.md): this append is only valid once
`## [0.9.0]` exists in `CHANGELOG.md` — land it after the CHANGELOG plan/task, not in the same
commit as the bump. Run with
`uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` and confirm skip
count is 0 (the two build-driving classes are gated on `myst_parser`/`typst` availability).

---

### `docs/source/changelog.rst` — `Migrating from 0.8.x to 0.9.0` (docs, transform)

**Analog:** the same file's own `Migrating from 0.7.x to 0.8.0` section, 83 lines
(`docs/source/changelog.rst:7-89`, read in full this session; header at line 7, next section
`Migrating from 0.7.0 to 0.7.1` at line 90 — new section is inserted directly above the 0.7.x→0.8.0
one, i.e. immediately below the `Migration Guides` heading, most-recent-first).

**Shape to copy — lead-in sentence, then one bullet per breaking change, each with a before/after
`code-block:: text` pair:**
```rst
Migrating from 0.7.x to 0.8.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This release carries three breaking changes to what typsphinx writes to disk. Each item below
shows the ``conf.py`` fragment you have today -- unchanged -- and what it now produces: the
``# v0.7.x`` block is what that fragment used to write, the ``# v0.8.0`` block is what it writes
now.

- **Breaking:** the output shape. ... [prose stating the fragment, old behavior, new behavior,
  and what breaks for tooling that assumed the old shape]

  .. code-block:: text

     # v0.7.x -- manual.typ is the whole document
     $ sphinx-build -b typst source build
     build/manual.typ   <- the complete document body

  .. code-block:: text

     # v0.8.0 -- the same conf.py now writes a wrapper plus a content file
     $ sphinx-build -b typst source build
     build/manual.typ   <- thin wrapper: template application plus one #include("index.typ")
     build/index.typ    <- the document body -- manual.typ is still the file to compile
```
Also copy: a non-breaking item stated with "No action is needed" prose (the same file's fourth
bullet), a closing disambiguation paragraph distinguishing this release's rename from a prior
release's differently-shaped rename, and a closing `:doc:` cross-reference (the 0.7.x→0.8.0 section
closes with `See :doc:`/user_guide/output_layout` for the full current output-layout contract.`).

**D-08's "before" side is a REAL build, not derived from records** — a second, disposable
`git worktree add --detach <dir> v0.8.0` (tag resolves to `d9523ea43d884f9ce6763da0f7f8e690fe859eb4`,
confirmed an ancestor of HEAD), with its own
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` (CLAUDE.md's worktree rule
applies again, once per worktree — do not reuse the executor's own `.venv`, which has the current
v0.9.0-era editable install), then `uv run sphinx-build -b typst <fixture> <build-dir>` and record
the emitted file tree. `tests/roots/test-basic/` is byte-identical between `v0.8.0` and `HEAD`
(confirmed this session) and is the recommended fixture — it exercises the OLD default single
`_template.typ` layout at `v0.8.0` and the NEW `_template/<key>/<file>` bundle layout at HEAD, "the
same fixture" D-08 asks for literally.

**D-07: no test gate over this new section** — `grep -rn "Migrating" tests/*.py` returns zero hits;
this carries forward unbound, matching every prior migration guide.

---

### Evidence artifacts (`57-BUMP-EVIDENCE.md`, `57-CI-EVIDENCE.md`, `57-GREEN-TREE-EVIDENCE.md`, `57-GOAL-CLAIM-EVIDENCE.md`, `57-SC4-INVARIANTS.md`)

**Analogs:** the `52-*-EVIDENCE.md` family and `52-SC4-INVARIANTS.md` in
`.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/`, and the `46-*-EVIDENCE.md`
family in `.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/`.

**Pattern — verbatim command+output transcription, never a narrative summary.** Culture stated
directly in `57-CONTEXT.md`'s own `<code_context>` → Established Patterns: "commands and their
output transcribed verbatim; `human_needed` recorded honestly; abstain rather than assert without
direct evidence. A `pytest.skip` is not evidence." Every evidence file in the 52/46 family follows
this: a fenced `$ command` / output block per claim, cited by the roll-up/handoff, never restated.

**`57-CI-EVIDENCE.md` specifically — two-dispatch shape (D-12), diverging from 52's single-dispatch
precedent** because Phase 52 had no separate pre-existing-breakage check to run first. Copy
`52-CI-EVIDENCE.md`'s per-run job-table transcription format, doubled: one table for the pre-bump
check run, one for the post-bump authority run. Both run IDs, URLs, and full 12-job tables recorded
verbatim (`test`×6 matrix lanes, `lint`, `type-check`, `coverage`, `build`, `integration`×2 lanes).
Precedent shows more than 2 dispatches may be needed (`52-HANDOFF.md`: 8/12 → 11/12 → 12/12 across
three runs) — do not assume dispatch 2 is final.

**`57-GOAL-CLAIM-EVIDENCE.md` — D-14's exact gate to re-run, quoted from
`tests/test_two_key_selection_gate.py:145-157`:**
```python
def test_the_two_templates_produce_different_pdfs(self, build):
    master_bytes = build["master_pdf"].read_bytes()
    memo_bytes = build["memo_pdf"].read_bytes()
    assert master_bytes != memo_bytes, (...)
```
Re-run post-bump; record the transcript. This is a byte-inequality check backed by fixture templates
that differ in paper size (`a4` vs `us-letter`) and text size (`11pt` vs `14pt`) — the concrete
"two differently-typeset PDFs" evidence SC#3 asks for, with no new gate authored.

**`57-SC4-INVARIANTS.md` — the anchor and hunk-level argument, exact commands from
`57-RESEARCH.md` Pattern 6 (re-run live at execution time, never transcribed from RESEARCH.md):**
```bash
git diff v0.8.0..HEAD --stat -- . ':(exclude).planning' | tail -1
git rev-list --count v0.8.0..HEAD
git rev-parse origin/main
git merge-base origin/main HEAD
git diff v0.8.0..HEAD -- pyproject.toml          # hunk-level, NOT empty this milestone
git diff v0.8.0..HEAD -- typsphinx/__init__.py | grep add_config_value   # 1 removed, 1 added
grep -c "@preview" typsphinx/templates/base.typ  # expect 4
git diff <phase-57-start-SHA>..HEAD -- typsphinx/   # the FENCE proof — expect empty
```
Note the fence-proof scope correction versus Phase 52: Phase 52's fence proof asserted `typsphinx/`
unchanged over the *whole milestone* diff (which was true for that phase's context); Phase 57's
fence proof must be scoped to *this phase's own* diff (`<phase-57-start-SHA>..HEAD`), because the
whole-milestone `typsphinx/` diff is deliberately large (this milestone's own content).

---

### `57-HANDOFF.md` (docs, request-response)

**Analog:** `52-HANDOFF.md` (`.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/52-HANDOFF.md`), itself descended from `46-HANDOFF.md`.

**Structure to copy** (quoted from `52-HANDOFF.md`'s opening, read in full this session):
```markdown
# Phase 52: v0.8.0 Release Prep (prep-only) — Publish & Owner-Manual Handoff Checklist

This document is the standalone publish checklist `/gsd-complete-milestone` reads for this
milestone. ... A reader with only this file and the repository can execute the publish without
opening a PLAN or SUMMARY file.

## What this phase satisfied, and what it did not

**REL-07**, quoted verbatim from `.planning/REQUIREMENTS.md`:
> - [ ] **REL-07**: ...

- **SC#1** ... **MET** — cited, not restated.
- **SC#2** ... **MET** — cited, not restated.
...

**REL-07 remains open.** It closes at `/gsd-complete-milestone`, on the publish, not here. ...
(confirmed: `git diff --name-only -- .planning/REQUIREMENTS.md` is empty over this phase's entire
history — re-confirmed in ... § "Closeout guard" below).

## Checklist

Each item names its Owner and its Ordering dependency on the items before it.

### 1. Open the pull request against `main` and merge it
**Owner:** `/gsd-complete-milestone`.
**Ordering:** first — ...
```
Substitute REL-08 for REL-07, SC#1-#5 per this phase's own ROADMAP entry, and the second-repo tag
dispatch item for `typsphinx-doc-translations` (mechanics described in `57-RESEARCH.md` Pattern 7 —
dispatch that repo's own `update-pin.yml`, never a manual clone/edit/push). Explicitly state REL-08
stays `[ ]` through this entire phase, in these words, per the same "narrative is not proof" lesson
`57-CONTEXT.md` records under `<specifics>` item 9.

**Checklist item ordering pattern** (each item names Owner + Ordering dependency): 1) merge PR,
2) push tag (fires `release.yml`), 3) watch `release.yml` to completion (`validate`→`build`→
`publish-pypi`→`create-release`, human-approval gate on `publish-pypi`'s `pypi` environment,
watch `create-release` specifically — it is the job that failed at the v0.7.0 close), 4) verify
PyPI/GitHub Release, 5) dispatch the second-repo tag advance, 6) verify Read the Docs `stable` on
both projects (owner-manual, out of `/gsd-complete-milestone`'s own reach too — flag explicitly).

---

## Shared Patterns

### Evidence-file naming and reservation
**Source:** `57-CONTEXT.md` Claude's Discretion section + `46-CONTEXT.md` D-15.
**Apply to:** every evidence-producing plan in this phase.
Never name a file `57-VERIFICATION.md` — reserved for the verifier, will be clobbered. Use the
`52-*-EVIDENCE.md` naming shape (`57-BUMP-EVIDENCE.md`, `57-CI-EVIDENCE.md`,
`57-GREEN-TREE-EVIDENCE.md`, `57-GOAL-CLAIM-EVIDENCE.md`, `57-SC4-INVARIANTS.md`).

### Worktree-isolated execution, applied twice for D-08
**Source:** `CLAUDE.md` § "Worktree-isolated execution".
**Apply to:** every executor (standing mode) AND, separately, the D-08 v0.8.0-tag build worktree.
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run <command>
```
Run once for the executor's own worktree, and AGAIN inside the separate `git worktree add --detach
<dir> v0.8.0` checkout before any `sphinx-build` runs there — do not reuse the executor's own
`.venv` for the "before" build (it has the current, v0.9.0-era editable install).

### Prep/publish fence — forbidden vs. permitted actions
**Source:** `57-RESEARCH.md` Pattern 7, carried from every prior release-prep phase (33/35/41/46/52).
**Apply to:** every plan in this phase.
Forbidden: `git tag v0.9.0` (anywhere), triggering `release.yml` for real, PyPI/twine upload,
creating a GitHub Release, opening OR merging a PR, advancing the `typsphinx-doc-translations` pin
or tag, flipping REL-08's checkbox/Traceability row (`phase.complete` auto-flip hazard — verify it
did not fire at every plan close, revert if it did).
Permitted: editing tracked files, `git commit`, plain fast-forward `git push`, `gh workflow run
ci.yml --ref <branch>` (twice, D-12), `uv lock`/`uv sync`/`tox -e <env>`/`pytest`, hand-running
`scripts/extract_changelog_section.py` (no side effects).

### Discovery is run-time, not from written floors
**Source:** `57-CONTEXT.md` `<code_context>` → Established Patterns; D-10's repro grep; D-15's sweep.
**Apply to:** D-10's re-verification grep, D-15's invariant sweep, any "anywhere under X" claim.
Every "anywhere under X" criterion is checked by a repo-wide grep run live at execution time, never
by trusting a list (including this very PATTERNS.md's own file list, and CONTEXT.md's own
"measured this session" claims) as complete.

## No Analog Found

None — every file/artifact in this phase's scope has a strong, direct same-file-prior-release or
same-phase-prior-milestone analog.

## Metadata

**Analog search scope:** `CHANGELOG.md`, `docs/source/changelog.rst`,
`.planning/milestones/v0.8.0-phases/52-v0-8-0-release-prep-prep-only/`,
`.planning/milestones/v0.7.1-phases/46-v0-7-1-release-prep-prep-only/`, `pyproject.toml`,
`README.md`, `typsphinx/removed_config.py`, `tests/test_changelog_page_gate.py`,
`tests/test_two_key_selection_gate.py`, `docs/source/user_guide/configuration.rst`.
**Files scanned:** 13 target files/artifacts, 9 analog source files read.
**Pattern extraction date:** 2026-08-16.
</content>
