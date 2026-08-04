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

- [x] **TBL-04**: A table nested inside a `list-table` cell renders both tables correctly — the
      enclosing table's accumulated cells, column count, column widths and caption all survive the
      inner table's visit and departure, so the outer table's body is its own rather than the inner
      table's. (Root cause: `translator.py`'s table state is a set of scalars — `in_table`,
      `table_cells`, `table_colcount`, `table_colwidths`, `table_caption`, and the lazily-created
      `table_cell_content` — with no notion of *which* table is being filled. `visit_table`
      unconditionally resets them on entry and `depart_table` unconditionally tears them down on
      exit. Pre-existing, verified byte-identical pre- and post-Phase-42.)

- [x] **TBL-05**: A captioned table whose title renders to an empty or whitespace-only string still
      emits its id anchors, so a `:ref:`/`:numref:` to that table resolves instead of leaving a
      dangling label. (Root cause: `visit_table`'s captioned pre-check is structural —
      `bool(node.children) and isinstance(node.children[0], nodes.title)` — while `depart_table`'s is
      a value check, `if self.table_caption:`. When a title renders to `""` the two disagree and
      neither path anchors.)

### Figures

- [x] **FIG-01**: A figure nested inside another figure renders both figures correctly — the
      enclosing figure's caption, ids and state all survive the inner figure's visit and departure,
      and the inner figure renders inside the enclosing figure's legend rather than replacing or
      corrupting it. (Added 2026-08-04 during Phase 43 discussion, on the owner's decision to fold
      the figure path into the same fix. Measured that day: `.. figure::` nested in another
      `.. figure::`'s caption body puts the inner figure inside a docutils `legend` node; typsphinx
      has no `legend` handler, so `sphinx-build` emits `WARNING: unknown node type: <legend>`, the
      outer caption `OUTERFIGCAP` disappears entirely, and the inner `figure(...)` is injected as a
      content block straight after the outer `image("img.png")`. Sphinx's own LaTeX builder handles
      the same input without a warning — outer `\caption{OUTERFIGCAP}\label{index:id1}` survives and
      the inner figure is emitted inside a `sphinxlegend` environment. The second layer,
      `self.in_figure` / `self.figure_caption` being scalars with the same shape as the TBL-04
      clobber, is covered by this requirement as an implementation means, not as its own row.)

### Toctree and heading structure

- [x] **TOC-01**: A document reached through a `toctree` renders its headings one level deeper than
      its parent, so the PDF outline nests rather than being flat — and nested toctrees compose, a
      grandchild resolving one level deeper again. (Added 2026-08-04, after this milestone's roadmap
      was created, from the todo `toctree-heading-offset-ignored-because-visit-title-emits-abs`,
      severity major. Root cause: `visit_toctree` wraps its generated `include()` calls in a scope
      carrying `set heading(offset: 1)` (`translator.py:4761-4762`), but `visit_title` emits the
      heading with the **absolute** `level:` parameter (`translator.py:800-809`). In Typst `level:`
      is the final absolute level and overrides the ambient `heading(offset: …)`; only `depth:` is
      relative, resolving to `offset + depth` — so the offset is inert. Measured against the pinned
      `typst>=0.15.0,<0.16` (typst-py 0.15.0): under `set heading(offset: 2)`,
      `heading(level: 1, …)` resolves to level 1 while `heading(depth: 1, …)` resolves to level 3,
      `typst.query(…, 'heading', field='level')` → `[1, 3]`. The repair has **two** parts (D-07,
      2026-08-05): **(1)** `visit_title` emits `depth:` instead of `level:`; **(2)** `visit_toctree`
      emits a context-relative `set heading(offset: heading.offset + 1)` increment instead of an
      absolute assignment, so nested toctree scopes accumulate rather than replacing their parent's
      offset. Master documents render at `offset: 0`, where `depth == level`, so their **resolved
      heading level** is invariant — not their byte sequence: masters emit the same `heading()` call
      as included documents, so the keyword change lands in master output too. Proven by two stacked
      measurements, neither sufficient alone: resolved-level equality (`typst.query(…, 'heading',
      field='level')` identical before/after) plus normalised byte equality (the diff-derived
      emitted-form substitutions applied to the pre-fix `.typ` leave the post-fix files unchanged).
      Several existing tests assert the literal `heading(level: N` string and encode the buggy
      contract — they must be updated deliberately, with owner sign-off and a re-proof that the new
      assertions fail against the pre-fix commit.)

### Configuration

- [x] **CONF-08**: With `typst_documents` unset, `sphinx-build -b typstpdf` produces a PDF instead of
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

- [ ] **CONF-09**: An explicit `typst_documents` entry's `[2]` title and `[3]` author take effect in
      the rendered document, overriding `config.project` / `config.author` as they do in Sphinx's
      LaTeX builder, with a defined and tested precedence against `typst_authors` and a defined
      fallback when the element is absent or empty. No element of the published five-element
      contract is left silently inert. (Measured 2026-08-04: the complete set of indexed accesses is
      `writer.py:68`, `builder.py:141`, `builder.py:194-195`, `builder.py:986` — `[2]`, `[3]` and
      `[4]` are read by nothing, while `configuration.rst` and `templates.rst:189` both tell readers
      they are. Blast radius: 5 of 104 in-repo entries have `entry[2] != project`.) **This
      requirement reverses Phase 44's D-02**, which deferred the consumption out of v0.7.1 — owner
      decision 2026-08-04. **Second accepted CHANGELOG callout alongside CONF-08's rename:** for a
      user whose entry title/author differ from `project`/`author`, the rendered title and author
      change inside a patch release.

### Builder robustness

- [x] **BLD-01**: A non-`str` docname reaching `TypstPDFBuilder.finish()` fails with an actionable
      typsphinx-level error rather than a raw `TypeError` out of `path.dirname()`. (Filed 2026-07-22
      from Phase 22.3 research, Pitfall 4. Same method CONF-08 touches.)

### Documentation

- [ ] **DOC-11**: The README Quick Start states what `typst_documents` does and when it must be set —
      including the CONF-08 default and the fact that an explicit setting overrides it — so a reader
      following the Quick Start exactly is not surprised by the output filename or by which documents
      become PDFs. (SEED-001.)

- [ ] **DOC-12**: The published documentation's changelog page carries every release through v0.7.1.
      (`docs/source/changelog.rst` is frozen at 0.4.0; 12 releases are missing.)

- [ ] **DOC-13**: A custom template that declares exactly the parameters the published documentation
      lists compiles — the published contract and the parameters typsphinx actually passes agree in
      both directions, and the standing consequence (adding a template parameter breaks a
      correctly-written custom template) is recorded where the contract is documented.
      (`templates.rst:186-192` lists four parameters; `writer.py:259-261` also passes three
      `toctree_*` parameters unconditionally, and the CONF-04 merge adds any configured
      `typst_elements` key. Reproduced 2026-08-04: `TypstError: unexpected argument:
      toctree_maxdepth` on the documented example. Filed from Phase 44.1's `<deferred>` block.)

### Code quality and planning hygiene

- [x] **QUA-01**: `_emit_id_anchors`'s docstring describes its actual callers — it currently calls
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
      calling out **both** user-visible changes — CONF-08's output-filename rename and CONF-09's
      rendered title/author change), the post-bump tree proven green live, and the
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

### Filed during this milestone

- **CONF-10**: remove the `typst_authors` config value. `typst_authors` is pure sugar over
  `typst_template_function["params"]["authors"]` — rendering the same author dictionary through
  both routes was measured (Phase 44.2 D-06) to produce a **byte-identical** `authors:` value, the
  only difference being the order of named arguments in the emitted call, which is semantically
  irrelevant in Typst. Not done in Phase 44.2 because it is a breaking change and v0.7.1 is a patch
  release already carrying two user-visible changes (CONF-08's output-filename rename and CONF-09's
  title/author change), both of which REL-06 requires the CHANGELOG to call out — a third would
  contradict that boundary. Phase 44.2 already narrowed the setting's own scope: after its D-05
  reorder, `typst_authors` remains authoritative only on a package-alone build (`typst_package` set,
  no `typst_template`) whose active `parameter_mapping` does not map `"author"` — measured in
  `44.2-01-SUMMARY.md` for the fixture that deliberately sets a custom mapping omitting `"author"`,
  and independently confirmed in `44.2-GATE-EVIDENCE-03.md` § 4-5 for a real in-repo file
  (`examples/charged-ieee/approach1/conf.py`) that hits the same narrowing for a different reason —
  `typst_package` set with `typst_template_mapping` left completely unset, which
  `TemplateEngine.__init__` resolves to an *empty* mapping rather than the default one, so
  `"author"` is never an active key there either. The removal must touch: the config registration in
  `typsphinx/__init__.py`, the override block in `typsphinx/template_engine.py`, both
  `typst_authors` sections in `docs/source/user_guide/configuration.rst`, the `typst_authors`
  mention in `docs/source/examples/advanced.rst`, and the `typst_authors` tests in
  `tests/test_template_engine.py` and `tests/test_package_only_config_gate.py`. It owes one
  migration: `examples/charged-ieee/approach1/conf.py`'s `typst_authors` block moves into that
  file's already-present `typst_template_function` dict. A deferred defect travels with it:
  `typst_authors` combined with the bundled default template produces no PDF at all (the template's
  document-author assignment receives an array of dictionaries where a string is expected) — Phase
  44.2's D-05 incidentally unbreaks the case where an entry also supplies an author, but a project
  setting only `typst_authors` stays broken until this removal lands.

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
| New translation features, new reST constructs, new node handlers | This is a maintenance cycle, not a feature cycle. **One exception, taken by owner decision 2026-08-04:** FIG-01 adds a `legend` node handler. It is admitted because it is not new capability for its own sake — it is the repair path for a measured silent-data-loss defect (the outer figure's caption disappears today), which is the same class of defect the rest of this milestone closes. |
| Typing-import modernization | Forbidden by `CLAUDE.md` until its own todo lands — see Future Requirements. |

## Traceability

Filled during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TBL-04 | Phase 43 | Complete |
| TBL-05 | Phase 43 | Complete |
| FIG-01 | Phase 43 | Complete |
| QUA-01 | Phase 43 | Complete |
| CONF-08 | Phase 44 | Complete |
| BLD-01 | Phase 44 | Complete |
| TOC-01 | Phase 44.1 | Complete |
| CONF-09 | Phase 44.2 | Pending |
| DOC-11 | Phase 45 | Pending |
| DOC-12 | Phase 45 | Pending |
| QUA-02 | Phase 45 | Pending |
| QUA-03 | Phase 45 | Pending |
| DOC-13 | Phase 45.1 | Pending |
| REL-06 | Phase 46 | Pending |
| REL-04 | Phase 46 | Pending (closes at `/gsd-complete-milestone`) |

**Coverage:**

- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

**Phase mapping notes:**

- **Phase 43** groups both table defects with QUA-01 because all three live in `translator.py`'s
  table/anchor code; the docstring QUA-01 corrects describes a helper Phase 43 calls. **FIG-01 was
  added to Phase 43 on 2026-08-04 during phase discussion** (owner decision), because the nested-
  figure defect shares the scalar-state shape TBL-04 fixes and lives in the same file — making the
  same class of change once rather than twice.

- **Phase 44** groups CONF-08 and BLD-01 because both change `TypstPDFBuilder.finish()` — the
  derivation and the input hardening are made once, in one place.

- **Phase 44.1** was **inserted 2026-08-04**, after the roadmap was created, to carry TOC-01 alone.
  It is not folded into Phase 44 (which owns `TypstPDFBuilder.finish()`) or Phase 45 (documentation
  and hygiene) because it changes `visit_title`'s emitted heading form — a translator change under
  GATE-01 with its own deliberate test-churn cost. It runs **after** Phase 44 rather than before:
  both change what the Quick Start path emits, and Phase 44's SC#4 hands Phase 46 a measured
  before/after filename pair that must not be taken across a concurrent heading-shape change.

- **Phase 44.2** was **inserted 2026-08-04**, after the roadmap was created, to carry CONF-09 alone —
  **reversing Phase 44's D-02**, which had deferred this consumption out of the milestone. It is not
  folded back into Phase 44 (complete and shipped) and runs after Phase 44.1 because
  `tests/roots/test-basic/conf.py` is one of the five affected entries and sits inside 44.1's SC#3
  byte-invariance corpus. It runs before Phases 45 and 45.1 for the same reason Phase 45 follows
  Phase 44: those phases document behaviour, which must land first — `templates.rst:189`'s claim
  that `title` comes from `typst_documents` is exactly the claim CONF-09 makes true and DOC-13 must
  then verify rather than rewrite.

- **Phase 45** follows Phase 44 because DOC-11 must document the behaviour CONF-08 actually shipped,
  including the measured output filename. QUA-02 (`template_engine.py`) and QUA-03 (`.planning/`
  docs hygiene) ride along as small independent items rather than each becoming a phase.

- **Phase 45.1** was **inserted 2026-08-04**, after the roadmap was created, to carry DOC-13 alone.
  It is not folded into Phase 45 (documentation currency) because the repair may land in
  `writer.py`'s parameter merge or in `templates/base.typ` rather than in documentation alone — the
  route is deliberately unchosen at insertion, and Phase 45's criteria are all documentation-side.
  It runs **after** Phase 45 on sequencing rather than dependency: the two touch disjoint files, but
  both edit published documentation and each phase's build evidence should be attributable to it.

- **Phase 46** is prep-only and takes **zero irreversible action**. REL-04's row stays open through
  the phase by design: its acceptance evidence is a real tag push whose `create-release` job runs to
  completion, which only `/gsd-complete-milestone` can generate. The phase discharges the
  verification-and-handoff share only; do not flip this row on the strength of the workflow file
  being correct.

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
*Last updated: 2026-08-04 at Phase 43 discussion (FIG-01 added by owner decision; Phases 43-46, 12/12 mapped)*
