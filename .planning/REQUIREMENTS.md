# Requirements: typsphinx — milestone v0.7.1 (bug-fix round)

**Defined:** 2026-08-04
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered,
well-typeset output on the current ecosystem — and the documented configuration actually takes
effect, so a user who copies a documented `conf.py` example gets what the docs promise. The same
standard applies to the publishing surface: a URL the project publishes must actually resolve, and
the PDF a reader downloads must be the one typsphinx itself produced.

**Milestone framing.** This is a maintenance round, not a feature cycle. Every requirement below
closes something already known to be broken: the one requirement v0.7.0 could not close, the two
table defects Phase 42's own code review filed, a documentation page frozen two years back, the
first-run onboarding break recorded as SEED-001, and four small carried todos. Phase numbering
continues at **Phase 43**.

## v1 Requirements

### Tables

- [ ] **TBL-04**: A table nested inside a `list-table` cell renders both tables correctly — the
      enclosing table's accumulated cells, column count, column widths and caption all survive the
      inner table's visit and departure, so the outer table's body is its own rather than the inner
      table's. (Root cause: `translator.py`'s table state is a set of scalars — `in_table`,
      `table_cells`, `table_colcount`, `table_colwidths`, `table_caption`, and the lazily-created
      `table_cell_content` — with no notion of *which* table is being filled. `visit_table`
      unconditionally resets them on entry and `depart_table` unconditionally tears them down on
      exit. Pre-existing, verified byte-identical pre- and post-Phase-42.)
- [ ] **TBL-05**: A captioned table whose title renders to an empty or whitespace-only string still
      emits its id anchors, so a `:ref:`/`:numref:` to that table resolves instead of leaving a
      dangling label. (Root cause: `visit_table`'s captioned pre-check is structural —
      `bool(node.children) and isinstance(node.children[0], nodes.title)` — while `depart_table`'s is
      a value check, `if self.table_caption:`. When a title renders to `""` the two disagree and
      neither path anchors.)

### Configuration

- [ ] **CONF-08**: With `typst_documents` unset, `sphinx-build -b typstpdf` produces a PDF instead of
      exiting 0 with a warning and zero output — `typst_documents` resolves to a default derived from
      `root_doc`, `project` and `author`, with the target name in Sphinx's own LaTeX shape
      (`<project>.typ`, from `make_filename_from_project(project)`). An explicitly-set
      `typst_documents` always wins. **Known accepted cost, to be called out in the CHANGELOG:** for
      a user who has never set `typst_documents`, this **renames** the existing `-b typst` output
      (e.g. `index.typ` → `typsphinx.typ`), so it is a user-visible behavioural change inside a patch
      release. (Measured basis: Sphinx 9.1.0's LaTeX builder registers the callable default
      `default_latex_documents` and does *not* require `latex_documents`; probed live with an empty
      `conf.py`, it resolves to `[('index', 'probeproject.tex', 'Probe Project', 'Probe Author',
      'manual')]`.)

### Builder robustness

- [ ] **BLD-01**: A non-`str` docname reaching `TypstPDFBuilder.finish()` fails with an actionable
      typsphinx-level error rather than a raw `TypeError` out of `path.dirname()`. (Filed 2026-07-22
      from Phase 22.3 research, Pitfall 4. Same method CONF-08 touches.)

### Documentation

- [ ] **DOC-11**: The README Quick Start states what `typst_documents` does and when it must be set —
      including the CONF-08 default and the fact that an explicit setting overrides it — so a reader
      following the Quick Start exactly is not surprised by the output filename or by which documents
      become PDFs. (SEED-001.)
- [ ] **DOC-12**: The published documentation's changelog page carries every release through v0.7.1.
      (`docs/source/changelog.rst` is frozen at 0.4.0; 12 releases are missing.)

### Code quality and planning hygiene

- [ ] **QUA-01**: `_emit_id_anchors`'s docstring describes its actual callers — it currently calls
      `depart_figure` the sole user of `skip_ids`, which has been false since Phase 25 and became
      actively misleading when Phase 42 added `depart_table` as a second caller.
- [ ] **QUA-02**: `derive_typst_lang()`'s rejection-path warning is emitted from one place rather
      than duplicated verbatim across its two rejection branches, with no change to the warnings a
      build produces. (Phase 27.1 review IN-01.)
- [ ] **QUA-03**: `.planning/PROJECT.md` contains no unterminated HTML comment — both `<!--` openers
      in the archived-footer tail are closed, so no downstream reader silently swallows the rest of
      the file.

### Release

- [ ] **REL-04** *(carried from v0.7.0 — not met there)*: The GitHub Release body is the curated
      `## [X.Y.Z]` section of `CHANGELOG.md` rather than a `git log --pretty` commit dump, **proven
      by a real tag push whose `create-release` job runs to completion**. The extractor and the
      `release.yml` fix (the missing `astral-sh/setup-uv` / `Set up Python` steps) are already on
      `main`; what is owed is the end-to-end exercise. **This requirement's acceptance evidence is
      generated by the publish step itself and therefore cannot be discharged before
      `/gsd-complete-milestone`** — it must not be reported complete on the strength of the workflow
      file being correct, which is the precise error v0.7.0 made.
- [ ] **REL-06**: v0.7.1 is released — `pyproject.toml` bumped as the sole version literal with
      `uv.lock` and `README.md` in lockstep, a curated `## [0.7.1]` CHANGELOG entry (explicitly
      calling out CONF-08's output-filename change), the post-bump tree proven green live, and the
      publish (merge → tag → `release.yml` → PyPI + GitHub Release, plus the standing second tag on
      `typsphinx-doc-translations`) executed at `/gsd-complete-milestone`.

## Future Requirements

Acknowledged, deliberately not in this milestone.

### Carried from earlier milestones

- **CFG-01**: user-configurable `@preview` package versions
- **XOS-01**: cross-OS `docs-pdf` CI on macOS and Windows
- **DEG-03**: real rendering (not a placeholder) for `graphviz` / `inheritance_diagram`
- **XREF-02**: link `manpage` / cross-references to external URLs via a configured base URL
- **CONF-06**: `typst_elements` keys beyond `papersize` / `fontsize` / `lang`
- **RTD-05**: Read the Docs pull-request preview builds
- **RTD-06**: documentation versions for tags before `v0.6.4`
- **LNK-01**: a `sphinx-build -b linkcheck` CI job
- **CIT-07**: `sphinxcontrib-bibtex` support (`:cite:` role, `.bib` files)
- **STY-01 / STY-02 / STY-03**: user-overridable per-directive styling, a bundled Typst style
  module, and its Typst Universe publication
- **TOP-01**: box `.. contents::` (local TOC) as Sphinx's LaTeX output does

### Open todos not scoped here

- **`modernize-typing-imports-drop-up006-up035-ignore`** — deferred *doubly deliberately*:
  `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands."

## Out of Scope

Explicitly excluded, with reasoning.

| Feature | Reason |
|---------|--------|
| A rehearsal mechanism for `create-release` (test tag / `workflow_dispatch` dry run) | Owner decision 2026-08-04. REL-04 closes on the real tag push at `/gsd-complete-milestone`; if it fails again it carries forward again. |
| Bumping to v0.8.0 to absorb CONF-08's output-filename rename | Owner decision 2026-08-04, taken after the rename was stated explicitly. The framing accepted: the renamed path produced no PDF at all before, so it is a broken path being repaired rather than a working one being changed. |
| Deriving `<root_doc>.typ` instead of `<project>.typ` (which would rename nothing) | Owner chose the LaTeX-consistent shape over the rename-free one. |
| New translation features, new reST constructs, new node handlers | This is a maintenance cycle, not a feature cycle. |
| Typing-import modernization | Forbidden by `CLAUDE.md` until its own todo lands — see Future Requirements. |

## Traceability

Filled during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TBL-04 | TBD | Pending |
| TBL-05 | TBD | Pending |
| CONF-08 | TBD | Pending |
| BLD-01 | TBD | Pending |
| DOC-11 | TBD | Pending |
| DOC-12 | TBD | Pending |
| QUA-01 | TBD | Pending |
| QUA-02 | TBD | Pending |
| QUA-03 | TBD | Pending |
| REL-04 | TBD | Pending |
| REL-06 | TBD | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 0
- Unmapped: 11 ⚠️ (filled by the roadmapper)

## Milestone Invariants

Standing bars this milestone inherits and must not relax:

1. **Zero new runtime dependencies.**
2. **The `@preview` package count stays at four**, with no new version-lockstep site. The existing
   sync surface is `writer.py` / `template_engine.py` / `templates/base.typ` plus `examples/**/*.typ`,
   guarded by `tests/test_preview_version_sync.py`.
3. **GATE-01 (since v0.6.0):** every node-handler change ships a real
   `sphinx-build → typst.compile()` regression fixture, recorded **red against the unfixed code**
   before it is accepted as green. Both table defects (TBL-04, TBL-05) fail observably today, so the
   classic RED is available again — v0.7.0's structural-assertion amendment applied only to defects
   that already compiled cleanly.
4. **"Anywhere under X" success criteria are checked by a repo-wide grep at discovery time**, never
   against the files a requirement happens to name.
5. **Push the milestone branch to `origin` from the first phase, not at the release PR.** Both
   defects that surfaced at the v0.7.0 close — REL-04's `create-release` failure and a Windows
   cp1252 test failure — share the single cause that the milestone branch was never pushed until the
   release PR, so neither Windows CI nor a real tag push ran against it during any of the eight
   phases.

---
*Requirements defined: 2026-08-04*
*Last updated: 2026-08-04 at milestone v0.7.1 scoping*
