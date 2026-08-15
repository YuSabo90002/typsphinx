# typsphinx

## What This Is

typsphinx is a Sphinx extension that translates reStructuredText documentation into Typst markup (`.typ`) and compiles it to PDF, via the `sphinx-build -b typst` and `-b typstpdf` builders. It's a mature, PyPI-published Python package for teams who author docs in Sphinx but want Typst-quality typeset PDF output.

As of **v0.5.0 (shipped 2026-07-11)** the extension tracks the current ecosystem: **Sphinx 9.1, docutils 0.22, typst 0.15, Python 3.12–3.13**. v0.4.4 had pinned the dependency graph back to a known-good set (typst 0.14.9, `sphinx<9`, `docutils<0.22`) to escape multi-year rot; v0.5.0 moved forward — raising the pins, bumping the four bundled `@preview` packages in lockstep to versions that compile cleanly under typst 0.15 (closing the `unknown variable: kai` break), modernizing the soft-deprecated docutils/Sphinx API, and fixing a long-latent admonition render bug — so the extension is current again. Latest-only: older Sphinx/typst support is intentionally dropped; a compatibility range is out of scope.

**v0.6.0 (shipped 2026-07-13)** hardened the translator against real-world documentation: it now compiles Sphinx's own full `doc/` tree end-to-end through `typstpdf` with no fatal Typst errors (Issue #114 closed), fixing the fatal figure/image bugs and adding correct rendering for the highest-frequency previously-dropped nodes (version directives, `refid` cross-references, autodoc signature sub-parts, footnotes via a doctree pre-pass, transition/topic/line-block/glossary/abbreviation), plus a graceful-degrade net for out-of-scope graphical nodes — all behind a standing real-`typst.compile()` acceptance gate. Zero new runtime dependencies.

**v0.6.1 (shipped 2026-07-19)** moved output from "compiles fatal-free" to "renders faithfully": it implemented the last two silently-dropped nodes (`todo_node`, `manpage`), generalized the CSS-length converter into one shared helper (LEN-01), then ran a full 151/151-docname human-assisted visual audit of the compiled Sphinx `doc/` corpus PDF against its `-b html` baseline — cataloguing 15 systemic silent mis-render findings, fixing the sole high-severity one (wide-table glyph collision + right-margin clip) with a real-compile regression fixture, and closing on the full-corpus regression gate. Zero new runtime dependencies.

**v0.6.2 (2026-07-23)** and **v0.6.3 (2026-07-25)** closed the remaining silent mis-render findings and made the documented configuration actually take effect (`typst_elements` allowlist, captioned tables as numbered Typst figures, `lang` following Sphinx's `language`). **v0.6.4 (shipped 2026-07-28)** applied the same standard to the publishing surface: documentation hosting moved from GitHub Pages to **Read the Docs** — English (`/en/latest/`) and Japanese (`/ja/latest/`, built from the separate `typsphinx-doc-translations` repository as an RTD translation project) — with the downloadable PDF being the one `typstpdf` itself produced, every published URL verified resolving, and the hand-rolled multilang machinery deleted.

**v0.6.5 (shipped 2026-07-29)** was a one-defect hotfix: a document mixing prose and inline math no longer aborts the Typst compile. **v0.7.0 (shipped 2026-08-04)** turned the standard from "correct" to "well typeset": autodoc/API reference pages moved from a flat wall of proportional bold text to a real typographic design — monospace signatures with hanging-indent wrapping and no margin overflow, description bodies and field lists indenting by nesting depth off one shared constant, and admonitions re-bucketed onto a taxonomy the owner signed off against a desaturated render. The same milestone added full-round-trip docutils citation support (greenfield — a citation previously failed the compile outright), closed two remaining compile fatals, and made the GitHub Release body the curated `CHANGELOG` section instead of a commit dump.

**v0.7.1 (shipped 2026-08-11)** turned the standard inward, onto the gap between what the documentation promises and what a `conf.py` actually gets. `typst_documents` gained a LaTeX-shaped default derived from `root_doc`/`project`/`author`, so following the Quick Start produces a PDF instead of exiting 0 with a warning and zero output; an explicit entry's title and author reach the rendered document instead of being silently overridden by `project`/`author`; and the published custom-template parameter contract was rewritten onto the nine parameters typsphinx actually passes and locked with a RED-proved gate, with `typst_authors` removed outright. Structural rendering defects closed alongside: nested tables and figures stopped corrupting the enclosing structure (snapshot state stacks plus a new `legend` handler), an empty-titled caption still anchors its ids, and a toctree'd document's headings nest one level deeper instead of rendering flat. The milestone also received this project's first external contribution (Issue #130 / PR #131) and closed **REL-04**, unmet since v0.7.0, on evidence generated by a real tag push rather than on the workflow file being correct.

**v0.8.0 (shipped 2026-08-15)** made multi-master composition actually work. A `typst_documents` configuration declaring more than one master now produces a complete PDF for each of them: the unit of output split into a template-less docname-named **content** file per document plus a thin **wrapper** file per entry, and each wrapper computes its own include graph by document-order depth-first traversal and publishes it as Typst `state`, which content files read to emit **state-guarded** includes at their toctree's own position. A document reached from several masters therefore renders once in each master's PDF, at that master's own traversal position and heading level, instead of being dropped from all but one. Cross-reference existence moved to Typst's own compile-time decision, so a label absent from the compiling master degrades to plain text rather than aborting. This is a **breaking** minor release: one entry now writes two files, a target containing a path separator is honoured as a path (reversing v0.7.1 Phase 44), and any two logical files wanting one physical path abort loudly instead of silently overwriting.

## Core Value

The `typst`/`typstpdf` builders produce correct, compilable **and faithfully-rendered** output on the **current** ecosystem — Sphinx 9 and typst 0.15+ — with the runtime pins raised forward, the bundled `@preview` packages compiling cleanly (no `kai`-class breaks), and real-world documentation sets rendering to PDF that matches the source rather than merely compiling fatal-free. The same standard applies to the publishing surface: a URL the project publishes must actually resolve, and the PDF a reader downloads must be the one typsphinx itself produced. **From v0.7.0 the standard extends again: the output must be *well typeset*, not merely correct** — an API reference page has to read as a reference document, not as text that happens to compile.

## Current Milestone: v0.9.0 per-document templates

**Goal:** every `typst_documents` entry can use its own template, Typst Universe package, and
template-function arguments — instead of one globally-configured template being applied to every
master.

**Why now.** v0.8.0 made multi-master composition produce a complete PDF per master, but every one
of those PDFs is still typeset by the same template. Template resolution is read entirely from
global config: `writer.py:324-351` (per wrapper) and `builder.py:1124-1168` (once per build) both
read `typst_template` / `typst_package` / `typst_package_imports` / `typst_template_function` /
`typst_template_mapping` off `config` and never consult the entry. The v0.8.0 wrapper/content split
already threads the specific `typst_documents` entry into `TypstWriter.render_wrapper()`, so the
entry is in hand at the exact point the template is chosen — what is missing is a per-entry way to
name a template, and the ability to emit more than one template file.

**Target features:**

- **`typst_document_templates` registry (new config value)** — a dict of named template definitions.
  Each entry carries at most three keys: `template` (srcdir-relative local `.typ`) **xor** `package`
  (Typst Universe spec), plus `template_function` (`str` or `{"name", "params"}` dict). Two shapes
  fall out of the existing engine with no new predicate: declaring `"params"` selects the exclusive
  parameter set (`TemplateEngine.__init__`'s `params_specified`, D-D), omitting it selects the
  auto-derived set.
- **`typst_documents` element [4] becomes the registry key** — the slot exists and is already
  populated project-wide with the literal `"typst"`: `_default_typst_documents()` emits it
  (`builder.py:184`), `docs/source/conf.py` and both `examples/charged-ieee` configs set it, nine
  documentation examples show it, and `configuration.rst:80` defines it as *"Document class (usually
  "typst") — accepted and ignored"*. This milestone retires that definition and gives the slot
  meaning.
- **Built-in key `"typst"` defers to global config** — `typst_template` / `typst_package` /
  `typst_template_function` / `typst_template_mapping` if set, bundled `base.typ` otherwise. A
  four-element tuple behaves identically, per `configuration.rst:84`. This is what makes every
  existing `conf.py` keep working with zero edits.
- **One output rule, no exceptions: the resolved template's parent directory is copied wholesale to
  `<outdir>/_template/<key>/`.** `"typst"` is not special-cased — its bundle is
  `typsphinx/templates/` (one file, `base.typ`), or the global `typst_template`'s own directory, or
  the `<srcdir>/base.typ` shadow's directory. A package-only key has no bundle and copies nothing.
  Unifying the route is what makes the rest of this list collapse into deletions rather than
  additions.
- **Four mechanisms are deleted, not extended.** `_write_template_file()` disappears entirely —
  `resolve_template()` reads the file verbatim with no substitution, so the bundle copy already
  carries the template. `_copy_template_directory()`'s `.typ` exclusion disappears with it, since
  it existed only to avoid double-writing. `copy_template_assets()`'s three early returns
  disappear: the unset-global-`typst_template` guard because `"typst"` always resolves to
  something, and the `typst_package` guard because "has no bundle" becomes a per-key property. The
  collision detector's reserved `_template.typ` file claim (`builder.py:571`) becomes a single
  reserved `_template/` prefix.
- **Template-relative asset references start working** — the template now sits inside its own
  bundle, so `#image("logo.png")` resolves. This is the shape `templates.rst:106-113` already
  documents and which is currently wrong, and it retires `advanced.rst:129-138`'s instruction to
  write the outdir-root-relative `"_templates/refs.bib"` instead.
- **`typst_template_assets` is removed.** With every bundle copied wholesale there is nothing left
  for it to select, and this project does not leave inert config registered — v0.6.3's CONF-05
  deleted `typst_toctree_defaults` for exactly this reason. Its removal is the one user-visible
  breaking change in this milestone.
- **Fail-loud configuration errors** — an unregistered key, a registry entry carrying both
  `template` and `package`, a user-defined `"typst"` key (reserved), and a `template` pointing at a
  file directly under `srcdir` (it has no bundle directory; "copy the parent directory" would mean
  copying all of `srcdir`) each raise `ExtensionError`, following CONF-04's
  unknown-`typst_elements`-key and BLD-02/03/04's output-path-collision precedent. Registry keys
  become path segments, so they are charset-validated at config-read time.
- **Documentation** — `configuration.rst` (retract the element-[4] definition), `templates.rst`
  (the asset example becomes correct), `quickstart.rst`, `output_layout.rst`, `builders.rst`.
- **Clean up the five v0.8.0-derived defects** that shipped unfixed by decision D-01 or with only a
  test-side fix: the compile-time xref guard's label-collision false negative, the unescaped
  include-edge key separators, the unbounded recursion in `derive_master_edge_keys`, the escape
  branch's basename-only relocation key, and `_track_image`'s non-drive-aware `isabs` on Python
  3.13 Windows (product side still open — plan 52-09 fixed only the test).

**Decisions locked at scoping (2026-08-15), each measured rather than assumed:**

- **The registry is function-only — no `template_mapping` key.** `typst_template_mapping` overlaps
  `template_function` and is strictly weaker: it is a rename table whose source dict is the
  three-key `{project, author, release}` built at `writer.py:365`, so any other key it names can
  never fire; and `render()`'s D-B/D-D branch discards its entire output whenever `params` is
  declared, so the two can never both be in effect. The owner intends to remove the global value in
  a later milestone. Global `typst_template_mapping` is untouched here — it still works, with no
  deprecation notice and no warning.
- **P×A stays broken as-is.** A package with no declared `params` emits a Typst compile fatal for
  any master carrying a toctree, because two writes escape the D-05 package suppression:
  `map_parameters()` merges `typst_elements` unconditionally at its tail, and
  `render_wrapper()` calls `params.update(toctree_options)` *after* it (`writer.py:421-423`), so
  `toctree_maxdepth`/`toctree_numbered`/`toctree_caption` reach a third-party function that never
  declared them. This is why `examples/charged-ieee/approach1` uses the `params` route. Out of
  scope by owner decision.
- **`params` exclusivity is preserved**, so two entries sharing one registry key that declares
  `params` also share one literal title — the entry's own title/author elements are discarded. A
  custom template wanting non-default parameter names must use the `params` route and therefore
  gives up per-entry title/author. These two constraints cannot both be avoided; accepted.
- **`package_imports` and `elements` stay global** and apply to every document. No `assets` key is
  added to the registry — a bundle is always copied whole, which keeps the output rule to one
  sentence.
- **`"typst"` gets no exception in the output layout.** Moving it into `_template/typst/` was
  measured to break nothing here: all three real custom templates in this repository
  (`docs/source/_typst/custom_template.typ:91`, `examples/advanced/_templates/custom.typ:131`,
  `examples/charged-ieee/approach2/source/_templates/_template.typ`) reference fonts by *family
  name* only, with zero `#image()`/`#bibliography()`/`read()` path references, and no `.bib` file
  exists anywhere in the repository — `advanced.rst`'s `refs.bib` guidance describes a
  hypothetical. The exposure is limited to a wild template hardcoding an outdir-root-relative asset
  path, and the output directory is build-generated. One code path is worth more than the
  exception.

**Version rationale:** v0.9.0. The registry is additive and no existing `conf.py` needs editing to
keep working, but `typst_template_assets` is removed and the output layout of `_template.typ`
changes, so this is a breaking minor release — as v0.8.0 was.

<details>
<summary>v0.8.0 milestone brief (as scoped 2026-08-11) — retained for reference</summary>

### v0.8.0 multi-master composition

**Goal:** A `typst_documents` configuration declaring more than one master produces a complete PDF
for each of them — no silently dropped content, no compile failure. Re-shape the unit of composition
from "one `.typ` shared by every master" to "a per-master wrapper plus template-less content files",
cutting the single root the three known multi-master defects grow from.

**Target features:**

- **wrapper / content split** — every document is written as a docname-named content `.typ` carrying
  no template at all, and each `typst_documents` entry gains a new wrapper `.typ` holding the
  template application and the includes. The master/included binary in `writer.py:96`
  (`_is_master_document()`), which today selects the output shape, disappears. This closes **B-1**
  (the parent includes `guide/index.typ` from the docname while `_resolve_output_stem` names the file
  from the target, so Typst aborts with `file not found`) and **B-2** (an included master re-expands
  its template's title page and `#outline()` into the middle of the parent's body)
- **the wrapper publishes the per-master include edge set as Typst `state`; content files keep
  emitting their includes at the toctree's own position, guarded by that state** — the builder
  computes each master's include graph by mirroring `sphinx/util/nodes.py:485`
  `inline_all_toctrees` (document-order depth-first, first encounter wins, `traversed`
  re-initialised per master), then the wrapper emits
  `#state("inc", ()).update((<edge keys>))` before including the master's content. `visit_toctree`
  emits `context { set heading(offset: heading.offset + 1); if "<parent>><child>" in
  state("inc", ()).get() { include("<child>.typ") } }`, and the per-build ledger at
  `builder.py:99` becomes unnecessary. **The decision moves from write time to compile time**, which
  is what lets one shared content file behave correctly for every master. This closes **defect A**
  (a document toctree'd by two masters is included only into the one whose parent was written
  first, decided by docname sort order). Heading offsets stay relative — no DFS-depth arithmetic is
  needed in the wrapper
- **duplicate-target detection (CR-02)** — carry a registry of already-resolved targets so two
  entries naming the same target are caught, following CR-01's convention (fall back to the docname
  with a `WARNING`, never invent a filename the user did not write). Sphinx's own LaTeX builder has
  the identical bug (measured: exit 0, no collision warning, the first master's body gone), so this
  is a place typsphinx exceeds upstream rather than matches it
- **compile-time cross-reference degradation** — replace the build-time boolean at
  `translator.py:3073` with a `context` + `query` guard that decides at compile time whether the
  target label exists in this compilation unit. The dependency on `master_included_docnames` (a
  union across all masters) disappears, and `:orphan:` targets and per-master differences become
  correct through one mechanism. **Fixing defect A turns this configuration from a silent omission
  into a hard compile failure, so it must close in the same milestone**
- **the two PR #131 image defects** — `rehomed-converted-image-collides-with-srcdir-images-dir`
  (major: a converted image rehomed to `images/<basename>` collides with a real source image at
  `<srcdir>/images/<basename>`, so one is never copied and the other document renders the wrong
  picture with no warning — a regression in failure mode, since the same project used to abort
  loudly) and `track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` (minor). Both live in
  `TypstBuilder._track_image()`
- **v0.8.0 release prep** — version bump + curated CHANGELOG entry in the final phase (the standing
  v0.5.0 Phase 10 pattern); publish executes at `/gsd-complete-milestone`

**Key context:**

- **Every premise below was measured live on the current tree, 2026-08-11.** defect A: with two
  masters both toctree'ing `shared`, `index.pdf` reports `SHARED-CHAPTER-MARKER` **0** times while
  `bmaster.pdf` reports 1 — exit 0, no collision warning, and which master loses is decided by
  docname sort order. CR-02: two entries targeting `manual.typ` drop one master's body (already
  re-measured as still reachable in Phase 46). B-1/B-2 stand on the todos' 2026-08-05 measurements.
- **Masters are not concatenated — each produces its own independent PDF** (measured: `index.pdf`
  and `bmaster.pdf`). A shared chapter appearing in *both* PDFs is therefore the correct outcome,
  and the `label ... occurs multiple times` hazard holds only *within* a single PDF. This is what
  licenses a wrapper to expand the same content file into more than one master.
- **Sphinx's LaTeX builder composes at the doctree layer, so B-1/B-2/defect A cannot arise there**
  (measured: the shared chapter fully inlined into both `mastera.tex` and `masterb.tex`, with zero
  `\input`/`\include`). Adopting that model would delete the per-document `.typ` files, which the
  `-b typst` builder exists to produce — so the design decision for this milestone is to **stay at
  the file layer and reach the same result**.
- **The composition rule is `inline_all_toctrees`'s document-order depth-first traversal, first
  encounter wins — NOT "prefer the deeper path".** Each master seeds `traversed` with its own
  docname and recurses into each child immediately, so which position claims a multiply-reachable
  document depends purely on the order its parent lists its children. Measured both ways on the
  same structure: with `xmaster` listing `[zmid, shared]`, `shared` lands nested
  (`\chapter{Mid} / \section{Shared}`); with `[shared, zmid]` it lands at the direct position
  (`\chapter{Shared} / \chapter{Mid}`) and zmid's include of it is skipped. **A shared document's
  heading depth is therefore a property of the traversal order, not of the document.** Mirroring
  `inline_all_toctrees` gets this right by construction; a hand-rolled "prefer deeper" heuristic
  would silently diverge from Sphinx. **Sphinx's
  `document is referenced in multiple toctrees: [...], selecting: X <- Y` message governs none of
  this** — it comes from `_check_toc_parents` (`sphinx/environment/__init__.py:942-959`), which
  takes a plain lexicographic `max(parents)`, disagrees with the navigation-parent function
  `_get_toctree_ancestors` (`sphinx/environment/adapters/toctree.py:562-575`, last-read-order-wins),
  and is never consulted by `assemble_doctree`/`inline_all_toctrees`. **Do not port that tiebreak.**
  `env.toctree_includes` retains every edge (`xmaster -> ['zmid', 'shared']`), so typsphinx must
  perform the traversal itself — mirroring `inline_all_toctrees`, not the "selecting" message.
- **The `context` + `query` label-existence guard is measured working** (2026-08-11, typst-py
  0.15.0). The exact validated snippet, recorded here so planning does not have to re-derive it:

  ```typst
  #context {
    if query(<onlyx:onlyx-label>).len() > 0 { link(<onlyx:onlyx-label>, "Only In X") }
    else { text("Only In X") }
  }
  ```

  Compiled two ways against the same file: without the target document included, the compile
  **succeeds** and the PDF carries no link annotation (degraded to plain text); with it included,
  the compile succeeds and the PDF carries a real link annotation. The unguarded form fails the
  first case outright with `label <onlyx:onlyx-label> does not exist in the document`. Two further
  sites carry the same label-reference shape and must be enumerated during planning:
  `translator.py:3273/3281` (citation back-references) and `:4291`.
- **Two design routes were measured, rejected, and superseded — do not re-derive them.** (1) Keeping
  the write-time ledger and merely re-scoping it per master cannot serve the diamond
  `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]`: `q.typ` must omit the `q→c` include for `M`
  (which already reaches `c` via `p`) and emit it for `M'`, and one file written once cannot do
  both. (2) Having the wrapper carry the include graph *flattened* solves the diamond but **breaks
  document-order interleaving**: measured on the current tree, `visit_toctree` emits its
  `include()` at the toctree's own position, so a master with prose after its toctree — the shape
  of Sphinx's own default `index.rst`, which puts an "Indices and tables" section there — renders
  as prose → trailing section → chapters instead of prose → chapters → trailing section. The
  state-guarded form measured correct on both counts (diamond: `C-BODY` appears exactly once in
  each master's PDF from the same `q.typ`; interleaving: PROSE-BEFORE → CHAPTER-BODY → Indices →
  PROSE-AFTER), and additionally puts conditionally-included content into `#outline()` and keeps
  its labels `query`-able.
- **Known residual risk: the state-guarded include rests on Typst's `state`/`context` multi-pass
  layout convergence.** It is measured working on the diamond, interleaving, outline, and label
  cases, but not yet across the full Sphinx `doc/` corpus. **Make a GATE-02 full-corpus pass an
  explicit success criterion of the composition phase**, and treat a convergence failure as a
  design-level finding rather than a fixture bug. A related documented behaviour: a content `.typ`
  compiled standalone (outside any wrapper) sees an empty state and therefore includes no children
  — sane, but it must be documented, since `-b typst` users should compile the wrapper.
- **User-visible output-shape change.** With `typst_documents = [("index","manual.typ",…)]`,
  `manual.typ` stops being the whole document and becomes the wrapper, while the body moves to
  `index.typ`. Explain this together with v0.7.1's own rename (`index.typ` → `typsphinx.typ` under
  the default derivation) in the CHANGELOG.
- **Large test blast radius** — every assertion against a master `.typ`'s contents moves. v0.7.0's
  comparable change measured 10 test files / 61 render-gate classes.
- **Standing invariants carried forward:** zero new runtime dependencies; the `@preview` package
  count stays at **four** with no new version-lockstep site; every node-handler change ships a real
  `sphinx-build → typst.compile()` GATE-01 regression fixture recorded **red against the unfixed
  code** before being accepted as green. All three defects genuinely fail today, so the classic RED
  (a `TypstError`, or a measurably wrong emitted structure) is available.

**Carried-forward deferred items (still out of this milestone):** CFG-01, XOS-01, DEG-03, XREF-02,
CONF-06, RTD-05, RTD-06, LNK-01, CIT-07, STY-01/STY-02/STY-03, TOP-01, SEED-003 (the PEP 735
`[dependency-groups]` split), `ruff-generic-linux-elf-unrunnable-on-nixos`, and
`modernize-typing-imports-drop-up006-up035-ignore` (which `CLAUDE.md` independently forbids acting
on).

</details>

<details>
<summary>v0.7.1 close note — retained for reference</summary>

**v0.7.1 (bug-fix round) shipped 2026-08-11** with 19/19 v1 requirements complete and **zero known
gaps** — the first close in this project's recent history to owe nothing forward. REL-04, carried
unmet from v0.7.0, closed here on generated evidence. Phase numbering continues at **47**.

</details>

<details>
<summary>v0.7.1 milestone brief (as scoped 2026-08-04) — retained for reference</summary>

### v0.7.1 bug-fix round

**Goal:** Close, in one cycle, everything v0.7.0 left owed — its single unmet requirement, the known
defects its own reviews filed, and the first-run onboarding break — so the next release starts from a
clean ledger.

**Target features:**

- **REL-04 proven end to end** — `release.yml`'s `create-release` job runs to completion on a **real
  tag push**, producing a GitHub Release body that is the curated `## [X.Y.Z]` CHANGELOG section. The
  workflow fix (the missing `astral-sh/setup-uv` / `Set up Python` steps) is already on `main`; what
  is owed is the exercise, which only this release can provide. No rehearsal mechanism is built
  (owner decision 2026-08-04) — REL-04 closes at `/gsd-complete-milestone`, or carries again
- **Nested-table state corruption** — `translator.py`'s table state (`in_table`, `table_cells`,
  `table_colcount`, `table_colwidths`, `table_caption`, `table_cell_content`) is a set of **scalars**,
  so a table nested inside a `list-table` cell resets the enclosing table's accumulated cells on
  entry and tears its state down on exit — the outer table's body is silently replaced by the inner
  one's under the outer caption. Real, severe, and **pre-existing** (verified byte-identical pre- and
  post-Phase-42). STATE.md named it the strongest single candidate for this milestone
- **Whitespace-only table caption → dangling anchor** — `visit_table`'s structural pre-check
  (`isinstance(node.children[0], nodes.title)`) and `depart_table`'s value check
  (`if self.table_caption:`) disagree when a title renders to an empty string, so the table anchors
  its ids on neither path and a surviving reference is left dangling. Adjacent to Phase 42's TBL-03
  but outside its requirement
- **Stale docs changelog** — `docs/source/changelog.rst` is frozen at 0.4.0; 12 releases (0.4.4
  through 0.7.0) are missing from the published documentation
- **SEED-001 — `typst_documents` default derivation** — following the Quick Start exactly yields a
  `typstpdf` build that exits 0, emits one `WARNING`, and produces **zero PDFs**, because
  `typst_documents` defaults to `[]` and `TypstPDFBuilder.finish()` returns early on it. **Measured
  2026-08-04: Sphinx's own LaTeX builder does not require `latex_documents`** — it registers the
  callable default `default_latex_documents`, which resolves to
  `[(root_doc, make_filename_from_project(project) + '.tex', project, author, latex_theme)]` (probed
  live against Sphinx 9.1.0 with an empty `conf.py`). typsphinx follows that precedent: derive from
  `root_doc`/`project`/`author`, with the target name in LaTeX's own shape — `<project>.typ` — and
  document it in the README Quick Start as well
- **Four small carried todos** — the `_emit_id_anchors` docstring that still calls `depart_figure`
  the sole `skip_ids` user (false since Phase 25, actively misleading since Phase 42); non-`str`
  docname raising a raw `TypeError` out of `TypstPDFBuilder.finish()`; `derive_typst_lang()`'s
  verbatim-duplicated warning block across two rejection branches; and the two unterminated HTML
  comments in this file's archived-footer tail
- **v0.7.1 release prep** — version bump + curated CHANGELOG entry in the final phase (the standing
  v0.5.0 Phase 10 pattern); publish executes at `/gsd-complete-milestone`

**Key context:**

- **Version is v0.7.1 (patch) — owner decision 2026-08-04, taken with the cost stated.** Choosing
  LaTeX's `<project>.typ` target shape means a user who has never set `typst_documents` sees their
  existing `-b typst` output **renamed** (`index.typ` → `typsphinx.typ`), not merely joined by a new
  PDF. That is a user-visible behavioural change in a patch release. The owner was shown this
  explicitly, alongside the alternatives (bump to v0.8.0, or derive `<root_doc>.typ` and rename
  nothing) and chose to keep v0.7.1 and **call it out in the CHANGELOG**. The framing that justifies
  it: the renamed path is one that produced no PDF at all before, i.e. a broken path being repaired
  rather than a working one being changed
- **REL-04 cannot be proven before the close.** It is the only requirement in this milestone whose
  acceptance evidence is generated by the publish step itself. Every phase must treat it as
  prep-plus-handoff, exactly as v0.7.0's Phase 41 did — and the milestone must not report REL-04
  complete on the strength of the workflow file being correct, which is the precise error v0.7.0 made
- **v0.7.0's own closing lesson is unaddressed by scope and must be handled by process.** Both
  defects that surfaced at the v0.7.0 close — the `create-release` failure and the Windows cp1252
  test failure — share one cause: **the milestone branch was never pushed until the release PR**, so
  neither Windows CI nor a real tag push touched it during any of the eight phases. The owner
  declined a rehearsal mechanism as scope; pushing the milestone branch from the first phase costs
  nothing and would have caught the Windows failure eight phases sooner
- **Two of the four small todos are cheap because they sit next to bigger work.** The non-`str`
  docname hardening is in `TypstPDFBuilder.finish()` — the same method SEED-001's derivation touches.
  The `_emit_id_anchors` docstring is in `translator.py` next to both table requirements
- **`modernize-typing-imports-drop-up006-up035-ignore` is NOT in scope**, and must not be picked up
  opportunistically: `CLAUDE.md` independently instructs "don't modernize typing imports until that
  todo lands." Neither is `add-sphinx-linkcheck-ci-job` (Future requirement LNK-01)
- **Standing invariants carried forward:** zero new runtime dependencies; the `@preview` package
  count stays at **four** with no new version-lockstep site; every node-handler change ships a real
  `sphinx-build → typst.compile()` GATE-01 regression fixture recorded **red against the unfixed
  code** before being accepted as green. Both table defects are genuine failures today, so the
  classic RED (a `TypstError`, or a measurably wrong emitted structure) is available again — v0.7.0's
  structural-assertion amendment was specific to defects that compiled fine

**Carried-forward deferred items (still out of this milestone):** CFG-01 (user-configurable
`@preview` versions), XOS-01 (macOS/Windows `docs-pdf` CI), DEG-03 (real rendering for
`graphviz`/`inheritance_diagram`), XREF-02 (xrefs to external URLs), CONF-06 (`typst_elements`'s
remaining keys), RTD-05 (PR preview builds), RTD-06, LNK-01 (`sphinx linkcheck` CI job), CIT-07
(`sphinxcontrib-bibtex`), STY-01/STY-02/STY-03 (user-overridable per-directive styling, a bundled
Typst style module, and its Typst Universe publication), TOP-01 (boxing `.. contents::`), and the
`modernize-typing-imports-drop-up006-up035-ignore` todo.

</details>

<details>
<summary>v0.7.0 milestone brief (as scoped 2026-07-29) — retained for reference</summary>

### v0.7.0 API rendering design overhaul

**Goal:** Replace the provisionally-chosen Typst representations of the API-description and
admonition directive families with a real typographic design, so autodoc/API pages render as a
readable reference document — monospace signatures, hanging-indented bodies, and visually
distinguishable nesting — instead of the flat wall of proportional bold text they are today.
**typsphinx itself produces the good-looking output; making that styling user-overridable is
explicitly NOT a goal of this milestone** (owner decision 2026-07-29, after research measured that
Typst cannot deliver the shape that goal wanted — see Key context).

**Target features:**

- **`desc_*` + `field_list` redesign** — the four defects measured 2026-07-29 by building a
  `py:` domain sample through `-b typst` (the same doctree autodoc produces): (1) signatures emit
  `strong({text("class") text(" ") text("TemplateEngine") ...})` — proportional bold, never
  monospace; (2) `visit_desc_content`/`depart_desc_content` are **both `pass`**, so the description
  body is flush left with the signature and no hanging indent exists; (3) a nested
  `py:method::`/`py:attribute::` renders at the same left margin as a top-level `py:function::`, so
  class membership is visually unrecoverable; (4) `field_list` emits
  `strong(text("Parameters") + text(": "))` followed by a `list(...)`/`par(...)` — bold inline
  labels, no aligned two-column layout. Also visible in the same output: doubled `parbreak()`
  runs producing uneven inter-element spacing
- **admonition / rubric / topic redesign** — the same provisional-representation class.
  `visit_rubric` is `strong()` + an unconditional `linebreak()`; because rubric also carries
  autodoc's "Options" heading, this lands directly on API pages
- **citation support — full round trip** — greenfield: `translator.py` contains zero citation
  handlers (the only mention is a comment recording that `citation`/`citation_reference` were left
  untouched by D-07), so a document containing a citation emits adjacent expressions with no
  separator and **fails the Typst compile outright**. `visit_citation` / `visit_label` /
  `visit_citation_reference` render a labelled hanging-indent reference list plus a working
  `[Label]` → definition link and the docutils-supplied back-references, to the point where the
  citation syntax Phase 22.2 stripped out of `examples/charged-ieee/` can be restored.
  **Typst's own `bibliography()`/`cite()` machinery is deliberately not used** — measured
  2026-07-29: `cite()` alone fails with "the document does not contain a bibliography", and
  `bibliography()` consumes structured `.bib`/Hayagriva data in order to CSL-format and reorder it.
  docutils citations carry no structured fields (the body is already-written prose), and docutils
  has already resolved every reference (`citation_reference.refid` → `citation.ids[0]`, plus
  `backrefs`), so the work is pure typesetting with `link`/`label`/`grid`, verified to compile
- **`visit_math_block` redundant blank line** (v0.6.5 review WR-01, pending todo) — folded in
  because this milestone touches separator and spacing behaviour broadly; fixing it in isolation
  was deferred by v0.6.5 D-05 only because it would have forced re-deriving the GATE-01 fixture's
  expected strings immediately before a release
- **`release.yml` release-notes body from CHANGELOG** — the v0.6.4 GitHub Release body is 308
  lines, of which 296 are the workflow's own `git log --pretty` commit dump; `release.yml` never
  opens `CHANGELOG.md` at all today. Extract the `## [X.Y.Z]` section instead
- **v0.7.0 release prep** — version bump + curated CHANGELOG entry in the final phase (the standing
  v0.5.0 Phase 10 pattern); publish executes at `/gsd-complete-milestone`

**Key context:**

- **Sphinx's LaTeX-rendered PDF is a REFERENCE, not an authority** (owner decision 2026-07-29,
  revised from the initial "authority" framing): `https://app.readthedocs.org/projects/sphinx/downloads/pdf/master/`,
  measured live the same day — `200`, `application/pdf`, 3,227,122 bytes, **703 pages**,
  `/Producer: pdfTeX-1.40.22`, `/Creator: LaTeX with hyperref`, built 2026-07-22. It renders **the
  same Sphinx `doc/` corpus** that `tests/test_corpus_gate.py` already drives through `-b typstpdf`,
  and needs **no TeX toolchain** (none is installed: `pdflatex`/`latexmk`/`xelatex`/`lualatex`/`tex`
  all absent). Its measured values are the **starting point** — the recurring ≈22–25pt indent
  quantum, the per-node font roles (`desc_name` bold monospace, `desc_addname` regular monospace,
  `desc_parameter` italic proportional), the four admonition colour buckets — but the milestone
  deliberately diverges wherever Typst can do better. The goal is output that is good **as Typst**,
  not a LaTeX lookalike
- **Consequence for success criteria:** with the reference demoted, "matches the authority" is no
  longer the bar. Criteria split in two — **mechanically checkable structural properties** (the
  signature is emitted through `raw(...)` rather than `text(...)`; the description body carries a
  non-zero indent; a nested member's left edge is strictly greater than its parent's, measurable via
  `pypdf` bounding boxes) and **human visual UAT** for the aesthetic judgement. Requirements must
  draw that line explicitly per item rather than leaving it implicit
- **The reference's version skew is now harmless:** the RTD project exposes exactly one active
  version, `master` (RTD API v3, `count: 1`, measured 2026-07-29), while `test_corpus_gate.py`
  clones the tag matching the installed Sphinx (`v9.1.0`). This mattered only under page-by-page
  comparison, which the demotion removes
- **Precise parameter source:** the LaTeX sources ship inside the venv and can be read directly —
  `sphinx/texinputs/sphinxlatexobjects.sty` (386 lines — the `\pysigline` / `\py@sigparams` /
  `\sphinxbfcode` object typesetting), `sphinxlatexadmonitions.sty` (408), `sphinxpackageboxes.sty`
  (827)
- **No bundled Typst style module — the translator emits complete Typst directly** (owner decision
  2026-07-29). A module was researched and would have worked, but its main justification was letting
  users override the styling per directive, and that goal was dropped. Choosing direct emission keeps
  every generated `.typ` self-contained (portable and compilable on its own, with no sibling
  `_typsphinx.typ` dependency), needs no builder change, and removes a whole phase. The accepted
  costs: the emitted `.typ` is more verbose, and the shared indent constant lives only on the Python
  side
- **User-overridable per-directive styling is out of scope, and was measured to be unavailable in
  the shape originally wanted.** `show`/`set` selectors accept only genuine element functions — a
  bare `#let` function cannot be selected (`typst error: only element functions can be used as
  selectors`), and user-defined element types remain unimplemented upstream (`typst/typst#147`, open
  since 2023-03-22, no committed timeline). Label selectors (`show <label>: …`) were verified to
  deliver the equivalent capability if it is ever wanted again — recorded so the finding is not lost
- **Known cost, accepted:** the emitted `.typ` shape changes broadly, so existing exact-string test
  assertions are invalidated at scale (measured blast radius: 10 test files, 61 render-gate classes).
  GATE-01 fixtures need their expected strings re-derived and the GATE-02 full-corpus gate re-run
- **GATE-01 methodology change (this milestone only):** every prior fixture proved a compile fatal —
  RED was a `TypstError`, GREEN a valid `%PDF`. Every design defect in this milestone **compiles
  successfully today**, so "does not compile" is unavailable as the RED state. Each phase must define
  a structural / regex / `pypdf`-text RED assertion **before** any code is written, or the standing
  invariant degrades into regenerating expected strings from whatever the new code happens to emit.
  Citation is the one exception — it is a genuine compile fatal today and keeps the classic RED
- **Standing invariants carried forward:** zero new runtime dependencies; the `@preview` package
  count stays at **four** with no new version-lockstep site (research confirmed every required
  primitive — `raw`, `par(hanging-indent:)`, `block(inset:/stroke:/breakable:)`, `grid`, `terms`,
  `pad` — is Typst 0.15 standard library); every node-handler change ships a real `typst.compile()`
  GATE-01 regression fixture recorded **red against the unfixed code** before being accepted as green

**Carried-forward deferred items (still out of this milestone):** CFG-01 (user-configurable
`@preview` versions), XOS-01 (macOS/Windows `docs-pdf` CI), DEG-03 (real rendering for
`graphviz`/`inheritance_diagram`), XREF-02 (xrefs to external URLs), CONF-06 (`typst_elements`'s
remaining keys), RTD-05 (PR preview builds), LNK-01 (`sphinx linkcheck` CI job), plus the pending
todos not named above (non-`str` docname TypeError hardening, typing-import modernization,
`derive_typst_lang()` duplicated warning block, PROJECT.md unterminated HTML comments).

</details>

<details>
<summary>v0.6.5 milestone brief (as scoped 2026-07-28) — retained for reference</summary>

### v0.6.5 inline-math separator hotfix

**Goal:** Fix backlog item 999.1 — inline math immediately following text emits no separator
before the `#mi(...)` call, so the generated Typst fails to compile — and release v0.6.5
promptly.

**Target features:**

- **999.1 fix** — when an inline math node follows text inside a paragraph, the emitted Typst
  has a valid separator between the preceding `text(...)` call and the `mi(...)` /
  `$...$` emission (suspected `translator.py` math/Text visit ordering — `visit_math` at
  `translator.py:3936` calls `_add_paragraph_separator()`, so the root cause needs measuring).
  Ships a real `typst.compile()` GATE-01 regression fixture proven fail-pre-fix
- **v0.6.5 release prep** — version bump + curated CHANGELOG entry in the final phase
  (the standing v0.5.0 Phase 10 pattern); publish executes at `/gsd-complete-milestone`

**Key context:** Minimal hotfix scope — none of the 5 pending todos or deferred requirements
(CFG-01, XOS-01, DEG-03, XREF-02, CONF-06, RTD-05, LNK-01) are pulled in. Standing milestone
invariants hold: zero new runtime dependencies, no `@preview` version bump, the 3-way
version-sync surface (4 package version strings) unchanged.

**Outcome:** both requirements delivered. The "suspected visit ordering" premise above was wrong —
the measured root cause was a *scope gap*: `visit_math` participated in only one of the translator's
three separator protocols. Scope held end to end; nothing outside the two requirements entered.

</details>

<details>
<summary>v0.6.4 milestone brief (as scoped 2026-07-25, amended 2026-07-26) — retained for reference</summary>

### v0.6.4 Read the Docs migration

**Goal:** Move documentation hosting from GitHub Pages to Read the Docs, so published URLs are
actually reachable and resolve correctly by version and by language.

**Target features:**

- **Establish the RTD build (en parent project)** — add `.readthedocs.yaml`. `docs/source/conf.py:51`'s
  `language` currently reads from the `SPHINX_LANGUAGE` environment variable, so make it also handle
  the `READTHEDOCS_LANGUAGE` RTD passes. Run `sphinx-build -b typstpdf` in `build.jobs` to output to
  `$READTHEDOCS_OUTPUT/pdf/`, so RTD's download menu serves typsphinx's own output (**whether the
  `typst-py` wheel runs in RTD's build environment is this milestone's sole technical unknown**)
- **Link ja as an RTD Translation project + retire the hand-rolled multilang setup** — RTD is one
  project = one language, and the translation model links a separate project to the parent under
  Translations (`/ja/latest/`). This means removing `docs/build_multilang.py` (180 lines), `tox.ini`'s
  `[testenv:docs-multilang]`, `docs/source/_templates/language-switcher.html`, and the
  `html_context`/`html_sidebars` language-switcher wiring at `conf.py:71-89`, replacing them with RTD's
  own native language flyout.
  **2026-07-26 revision (Phase 30 discussion, D-06) — this originally said "the 13 `.po` files under
  `docs/locale/ja/` carry over as-is," but that was reversed:** rather than importing the same
  repository twice, the project follows `sphinx-doc/sphinx-doc-translations`'s "dedicated translations
  repository + submodule" approach (measured via the RTD public API: all 15 of `sphinx`'s own
  translations are separate projects in separate repositories). The catalogs live on, but their address
  changes to `typsphinx-doc-translations`. `docs/Makefile`'s `gettext`/`locale-init`/`locale-update`
  targets move along with them (D-12)
- **Tear down GitHub Pages** — delete the `peaceiris/actions-gh-pages` deploy step at `docs.yml:57-63`
  and the PDF copy step at `:40-43`, and change `:34-35` from `docs-multilang` to `docs-html`.
  `tox -e docs-pdf` (the typstpdf regression gate) and the tag-time Release attachment at `:65-71`
  **survive**. Delete the `gh-pages` branch
- **URL cutover** — 10 sites in README (badge `:8`, header `:12`, `:267`, 7 deep links `:271-277`. The
  original "9 sites" figure was a tally error — the breakdown was already 10 items at the time),
  `pyproject.toml:56`'s `Documentation` (currently pointing at the GitHub README),
  `.planning/codebase/INTEGRATIONS.md`. `CHANGELOG.md:393` is left as-is because it's historical
  record (Phase 24 D-02 precedent)
- **Close #119 + set the repository About Website field** — #119 (external user put101's [BUG]
  website seems down, OPEN) has already received a reply promising "fix the Website link and the
  README deep links," which hasn't been carried out yet. Reply and close it after the migration
  completes. The About page's Website field is currently null
- **A repository-wide link-reachability CI job** (2026-07-25 revision — originally `sphinx-build -b
  linkcheck` was planned) — closes the process gap that let the 7 dead README deep links go unnoticed
  for months. Runs advisory (not a required check — the `drift.yml` precedent, D-07). **`sphinx
  linkcheck` is deliberately skipped this time**: research confirmed via grep that `github.io` appears
  zero times anywhere under `docs/source/`, and the 7 dead links exist only in `README.md` /
  `pyproject.toml` — structurally outside what `sphinx linkcheck` can ever see. A green linkcheck would
  only produce "false reassurance about exactly the bug class it was meant to prevent." The pending
  todo `add-sphinx-linkcheck-ci-job` stays open (moved to Future as requirement LNK-01)
- **Resolve the `docs/usage.rst` / `docs/installation.rst` orphan pair** — the same class of problem
  as `docs/configuration.rst`, which Phase 27 deleted. Measure toctree reachability to decide between
  deletion and relocation
- **v0.6.4 release** — version bump + CHANGELOG in the final phase; publish happens at
  `/gsd-complete-milestone`

**Key context:**

- **Requires manual user action (cannot be automated):** creating the 2 projects on RTD, linking them
  under Translations, setting the default version to `stable`, setting the repository About Website
  field
- **Version policy:** `latest` (follows main) + `stable` (latest semver tag), with `stable` as the
  default version. Since RTD started failing builds without a `.readthedocs.yaml` after 2023-09-25,
  documentation for existing tags v0.6.3 and earlier cannot be built retroactively — `stable` only
  becomes real starting from the v0.6.4 tag
- **Old URLs are not rescued:** per the owner's decision (2026-07-25) to delete gh-pages immediately,
  existing github.io links — including external references — become 404. No parallel redirect is kept
- **Four additional decisions confirmed after research (owner, 2026-07-25):**
  - **Fallback if `@preview` fetching doesn't work in RTD's sandbox** — give up on generating the PDF
    on RTD's side and link from the documentation to the PDF attached to the GitHub Release instead
    (the stable `releases/latest/download/` URL means no per-release edit is needed). This is the
    milestone's only genuine unknown, and it ranks above the wheel/font questions as a risk (the wheel
    was confirmed to have a `manylinux2014_x86_64` build in PyPI metadata, and the font question was
    confirmed via `typst-py`'s `embedded-fonts` feature in `Cargo.toml` — both are effectively settled)
  - **Loss of automatic browser-language redirection at the root** — accepted. RTD redirects to a
    version but does not auto-detect a visitor's language, so equivalent functionality is absent.
    Reimplementing it would mean reintroducing the custom template code this migration is trying to
    remove, so it will not be done
  - ~~**No Japanese PDF will be produced**~~ — **reversed on 2026-07-26 (Phase 30 discussion,
    D-01/D-04).** The original reasoning (`typst-py`'s embedded fonts have no CJK glyphs, requiring
    both a font install via `build.apt_packages` and a measured glyph gate) is still correct, but
    separating out the translations repository made it possible to write an independent
    `.readthedocs.yaml` for the ja side, turning "produce it or not" into an explicit choice, and the
    owner chose "produce it." **I18N-03 is promoted from Future to v1 and assigned to Phase 30.1.** The
    glyph gate is a content comparison against a local ja build (measured 94 pages / 1,811,337 bytes /
    1,997 CJK characters, 2026-07-26) plus visual inspection of the extracted text (D-03)
  - **Drop PR preview builds from v1** — a single checkbox on the owner's side with no repository-side
    work, and `docs.yml` already gates documentation builds on PRs. Can be enabled at any later time
    (RTD-05)
- **The timing of applying the default version sequences the "stable" decision rather than
  overturning it:** RTD's root redirect follows the Default Version setting even when the target
  version doesn't exist yet, so it stays at `latest` during the migration and switches to `stable`
  **after** the v0.6.4 tag builds green
- **There are two failure modes that present as a build success:** the Japanese project building
  green while rendering 100% English (I18N-01), and the PDF being produced with glyphs silently
  substituted (RTD-02 — Typst's font fallback emits neither a warning nor an error). Both require
  content-level verification
- **Invariant:** no `typsphinx/` runtime code changes, no `@preview` version bumps, the 3-way
  version-sync surface (the 4 package version strings) unchanged
- **Applying the v0.6.3 lesson:** verify "anywhere under X"-style success criteria with a
  repository-wide grep (v0.6.3 missed this twice)

**Carried-forward deferred items (still out of this milestone):** CFG-01 (making `@preview` versions
user-configurable), XOS-01 (macOS/Windows `docs-pdf` CI), DEG-03 (real rendering for
graphviz/inheritance_diagram), XREF-02 (xref links to external URLs), CONF-06 (`typst_elements`'s
remaining keys), unsupported `visit_citation`, TypeError hardening for non-`str` docnames, typing-import
modernization.

</details>

<details>
<summary>v0.6.3 milestone brief (as scoped 2026-07-23, amended 2026-07-25) — retained for reference</summary>

### v0.6.3 config & docs measured fidelity + captioned tables

**Goal:** Make the configuration written in the documentation actually take effect in the output, and
make the docs' description match the implementation — (1) dead-config cleanup round 2 (delete
`typst_toctree_defaults` / implement the pass-through for `typst_elements`'s non-mapped keys),
(2) reimplementing PR#98's captioned-table figure wrap against current `main`, (3) resolving the docs
claim-vs-measured-reality drift (deleting orphans, fixing phantom config names).

**Target features:**
- **Dead-config cleanup round 2** (the third and fourth instances of the same "registered but has no
  effect on output" config class as Phase 22.2's CONF-01..03):
  - **Delete (B)** `typst_toctree_defaults` from every surface (the `__init__.py` registration /
    `docs/configuration.rst` / `examples/advanced` / README:208) — writing `:maxdepth:` etc. directly
    on individual toctree directives is sufficient, so wiring this through has little value
  - **Implement (A)** the pass-through of `typst_elements`'s non-mapped keys (`papersize`/`fontsize`,
    etc.) to the template's `project()` — so the paper size and font size settings the PDF builder's
    users actually want take real effect. Fix the defect in `map_parameters` that discarded everything
    but `DEFAULT_PARAMETER_MAPPING`'s 3 keys (project/author/release)
  - Both must add a real config→output `typst.compile()` regression fixture (the same pattern as
    Phase 22.2 CONF-03's `test_package_only_config_gate.py` — so the defect doesn't get buried again
    as a fifth or sixth instance behind a registration-only test)
- **Reimplement PR#98 — captioned table figure wrap**: emit `.. table:: Caption` as
  `figure(table(...), caption: {...}, kind: table)` (numbered "Table N") instead of a redundant
  `heading()`. Account for the **composition** with the current `visit_title`/`depart_title`
  (`in_list_item` control / admonition-vs-topic branching / section-id anchors) and `depart_table`'s
  `:width:` → `block(width: ...)[#table(...)]` wrap (making caption and width coexist). Since external
  contributor AlCalzone's PR#98 is based on an old commit and can't merge (dirty), port its design
  intent and its 4 tests forward to the current cell format (`{par({text(...)})}`,
  `columns: (1fr, 1fr)`), and comment on PR#98
- **Docs measured fidelity**:
  - Delete the orphan `docs/configuration.rst` (526 lines, contains the wrong package name
    `sphinxcontrib.typst`, unreachable from any toctree)
  - Fix 5 nonexistent config names in `docs/source/user_guide/configuration.rst`:
    `typst_author`→`typst_authors`; `typst_papersize`/`typst_fontsize` become a working
    `typst_elements` example once (A) is implemented; the unregistered
    `typst_use_codly`/`typst_code_line_numbers` are deleted
  - **Typst's typesetting `lang` follows `language` (CONF-07 — added 2026-07-25, Phase 27.1)**:
    because `base.typ:61` hardcodes the typesetting language via
    `set text(size: fontsize, lang: "en")`, a project with `language = "ja"` gets its **body text
    translated** (Sphinx's own i18n transform already works — confirmed by measurement) while the
    labels Typst itself generates stay English. The captioned tables Phase 25 added come out as
    "Table 1" instead of 「表 1」, and figures as "Figure 1" instead of 「図 1」(Japanese for
    "Table 1" and "Figure 1", respectively). Add a `lang` parameter to `project()`, auto-derived from
    `config.language` on the default-template path only, with an explicit `typst_elements["lang"]`
    taking precedence on every path (the same pattern as Sphinx's own LaTeX builder
    `init_context()` precedence). **This amends the milestone invariant "`base.typ`
    byte-unchanged," but only for Phase 27.1** (the `@preview` version-string 3-way sync surface
    remains unchanged)

**Key context:** each item was root-caused into a pending todo with docname + node kind + file/line
(`dead-config-typst-elements-keys-and-toctree-defaults`, `reimplement-pr-98-captioned-table-figure-wrap`,
`delete-orphan-docs-configuration-rst`, `user-guide-configuration-phantom-config-names`). **Out of scope
this time:** the 404s on README's 7 github.io links (missing `/en/`) — left alone because the RTD
migration is expected to resolve them (and the RTD migration itself is also out of scope here).
Milestone invariant carried forward: zero new runtime deps, no `@preview` version bump, the 3-way
version-sync surface (the 4 package version strings) unchanged. **2026-07-25 revision:** "`base.typ`
byte-unchanged" is lifted, but only for Phase 27.1 (CONF-07) — the only change is adding a `lang`
parameter to `project()` and its `set text()` wiring. Every other phase stays byte-unchanged as before.
Standing GATE-01 bar: every node-handler change (PR#98) and config→output change ships/extends a real
`typst.compile()` regression fixture. Ship unit is the milestone (`branching_strategy: milestone`); a
final Release phase bumps version + CHANGELOG, publish executes at `/gsd-complete-milestone`.

**Carried-forward deferred items (still out of this milestone):**
- **CFG-01** (was FWD-03) — user-configurable `@preview` package versions (still v2)
- **XOS-01** — extend `docs-pdf` CI coverage to macOS and Windows

</details>

## Current State

**v0.8.0 SHIPPED 2026-08-15 — PyPI `typsphinx 0.8.0` live.** Six phases (47-52), 45 plans, 121
tasks, **24/24 v1 requirements complete, zero known gaps**. PR #133 merged to `main` with all 13
real CI checks green; tag `v0.8.0` on the merge commit `78e01e5`; release run `31861043480` ran
`validate` → `build` → `publish-pypi` → `create-release` all `success` after owner approval of the
`pypi` environment, and the GitHub Release body's first 70 lines are byte-identical to
`scripts/extract_changelog_section.py 0.8.0` with zero commit-dump-shaped lines. The standing
second tag was pushed on `typsphinx-doc-translations` by dispatching that repository's own
`update-pin.yml` (run `31861094950`, pin `a97fe73` → `78e01e5`, commit `588b96d`) rather than
advancing the pin by hand. Read the Docs `stable` measured live on both projects: `en` at
`78e01e53`, `ja` at `588b96da`, both reporting `0.8.0`, both serving `application/pdf` — the fifth
consecutive close needing no owner setting flip. **Four minor defects ship unfixed by decision
D-01**, all new failure classes created by features this milestone shipped, held to internal
disclosure only by D-03; the complete record is `milestones/v0.8.0-phases/52-*/52-HANDOFF.md` plus
`.planning/todos/pending/`.

<details>
<summary>v0.8.0 prep-phase state (Phase 52, pre-publish) — retained for reference</summary>

**v0.8.0 prep complete — Phase 52 complete 2026-08-15 (9 plans across 6 waves, 0/1 requirement IDs
closed by design, verification `passed` 9/9 must-haves, `52-REVIEW.md` 0 critical / 1 warning / 1
info).** The tree is bumped to `0.8.0` across `pyproject.toml`, `README.md` and `uv.lock` with the
editable install regenerated so `typsphinx.__version__` reports it live; the curated `## [0.8.0]`
CHANGELOG entry carries both breaking callouts (the output-shape change and the target-as-path
reversal) with `RELEASE_VERSIONS` extended to 14; and the milestone's central claim rests on a real
multi-master round trip — `TestThreeMasterGate` gained a page-level completeness proof over the
existing three-master fixture (every master's full include set present in its own PDF, nothing
outside it, no cross-master leakage), extending the class in place rather than forking a second
near-identical module over one fixture. `52-RELEASE-EVIDENCE.md` gives one verdict per SC#1–SC#5;
`52-HANDOFF.md` is the standalone publish checklist. Zero lines changed under `typsphinx/` across
the whole phase. **REL-07 remains open** — it closes at the publish, not here.

</details>

**Milestone invariant #5 paid for the second consecutive milestone, and paid four times over.**
Pushing the branch and dispatching CI mid-phase surfaced four real, pre-existing defects that local
execution structurally could not see, and the phase's CI history is three runs, not one: **RED (8
of 12 jobs) → 11/12 → GREEN 12/12**. Two of the four are worth carrying. First, **a test compared
against hardcoded Japanese Sphinx warning text** — the baselines in `49-SHAPES-RED-EVIDENCE.md` were
captured on a Japanese-locale machine, so every English-locale CI runner failed two parametrized
cases and took all six OS/Python lanes down with them; it reproduces locally in 4 seconds under
`LC_ALL=C`, which no one had ever run. The fix anchors on the two parts Sphinx never localizes (the
`file:line: WARNING:` prefix and the bracketed diagnostic tag) rather than swapping Japanese
literals for English ones, which would only have moved the dependency. Second, **`ruff` has been
unrunnable on this machine since Phase 45.2**, so an `I001` unsorted import block sat undetected in
`tests/test_builder.py` — exactly the gap D-08's "lint authority sits with CI" assignment exists to
cover. The remaining two were Windows-only: a `repr()`-escaping assertion, and CPython 3.13's change
to `ntpath.isabs()` (a driveless single-separator path is no longer absolute), which silently skipped
`_track_image()`'s entire rehome branch. **All four were fixed test-side**, in two plans added
mid-phase on owner authorization, so the prep-only fence survived to the release with `typsphinx/`
untouched — and the product-side inconsistency the fourth exposed (`builder.py:910` uses bare
`path.isabs()` while its sibling at ~112 deliberately uses `posixpath.isabs(...) or
_is_drive_qualified(...)`) was filed as a todo rather than erased by the test fix, because a green CI
with the finding lost would have been the worse outcome.

**The `phase.complete` auto-flip is now four-for-four on release-prep phases.** It flipped REL-07 to
`[x]`/`Complete` against the phase's own decision, the ROADMAP's own text and `52-HANDOFF.md`'s
closeout guard; diff-before-trusting caught it and the revert restored `REQUIREMENTS.md` to a
byte-identical checksum. Seven deferred items remain in `.planning/todos/pending/`, each named
individually in the handoff with its filename and the reason it ships unfixed. Next:
**`/gsd-complete-milestone`** (merge → tag `v0.8.0` → `release.yml` → PyPI + GitHub Release → the
second tag on `typsphinx-doc-translations` → the Read the Docs `stable` measurement on both).

**Phase 51 complete 2026-08-15 (6 plans across 3 waves, 1/1 requirement ID
DOC-14, verification `passed` 3/3 success criteria, `51-REVIEW.md` 1 critical / 1 warning).** The
two-layer output shape is now documented rather than left to be discovered: a new
`docs/source/user_guide/output_layout.rst` names the wrapper and content layers, says the wrapper is
the file to compile and that the builder's own log line lists the wrapper names, and states the
standalone-content behaviour (an empty `state`, therefore no children) as intended behaviour in
plain declarative prose rather than as a `note`/`warning` caveat (D-08). Target-as-path semantics
ship with built worked examples for the bare and explicit-path cases and all three refusal shapes
(`..`, absolute, drive-qualified), the Phase 47 collision abort, and the shared-child composition
consequence Phase 49 measured. `changelog.rst` gained a `Migrating from 0.7.x to 0.8.0` subsection
stating the change in old→new file names beside v0.7.1's own rename so the two are not confused.
`51-SWEEP-AUDIT.md` dispositions all 13 `51-RESEARCH.md` Part A rows. Zero lines changed under
`typsphinx/` across the whole phase.

**The phase's own defect class survived every plan and its own gate — and that is the finding worth
carrying.** Four published emitted-file claims omitted `_template.typ`, which `prepare_writing()`
writes at the outdir root and which every wrapper imports; deleting it makes the wrapper fail to
compile with `file not found`, so a reader following the published file set could not obey the
page's own instruction to compile the wrapper. The page contradicted **itself** (its file-count rule
counted `_template.typ`; its opening worked example did not) and contradicted **its own gate**
(`test_bare_target_emits_wrapper_and_content` asserts all three files exist), and both stayed green
because no test bound a *prose file-count* to a *measured file set*. It was caught by the post-phase
code review, not by execution. The companion finding is the same shape: `assert "ten" in text` was
vacuous — `"ten"` is a substring of `"written"` and `"content"`, both frequent on that page — so the
one numeric claim the gate nominally protected was never checked; the replacement was
**mutation-proved** (wrong number FAILS, sentence deleted FAILS, and the old assertion demonstrably
passes on that same deletion) rather than merely observed passing. Two further residuals in files no
plan had declared were surfaced by the audit's own independently-derived sweep — the audit was
instructed to derive its search set from the claim patterns rather than from the earlier plans' file
lists, precisely so it would not inherit their blind spot, and that is what found them. All were
fixed post-execution on owner instruction; one adjacent `conf.py`-drift finding was surfaced and
deliberately left. Next: **Phase 52 — v0.8.0 Release Prep (prep-only)**.

**Phase 50 complete 2026-08-14 (3 plans across 3 waves, 2/2 requirement IDs
IMG-01/IMG-02, verification `passed` with 1 owner override, `50-REVIEW.md` 1 critical / 1 warning /
1 info).** The two defects PR #131's own review filed against the code that PR introduced are closed
as one change to one method: `TypstBuilder._track_image()`'s absolute-URI branch now routes a
srcdir collision silently, and an outdir escape or a Windows cross-drive `relpath()` `ValueError`
with a warning, through one reserved `_typst_converted/` namespace. The collision decision is a
**filesystem probe, not a `self.images` membership test** — `write()` iterates `sorted(docnames)`,
so a dict check would have made the outcome depend on docname alphabetization, which is the
write-order dependence the phase set out to remove. Ordinary image handling is unchanged: the
D-12-pinned fixtures and gate are byte-unchanged across the whole phase, and the D-11 two-build
manifest diffs empty. Suite 1150 → 1156 passed, every increment accounted for.

**Three things are worth carrying forward.** First, **the RED held as an immovable target**: the
collision assertions were written and observed failing against the unfixed builder in wave 1, and
the entire diff wave 2 made to that gate module was the removal of two `xfail` decorator lines —
zero assertion text or expected value changed, verified by diff rather than asserted. Second,
**two planning documents were contradicted by measurement and neither was edited to match**:
RESEARCH.md cited `docs/source/examples/basic.rst:128` as a live `.. figure::` exercising the
ordinary-image path, but that line sits inside a `.. code-block:: rst` fence and `docs/source`
contains zero image assets at all, so SC#3's image claim is carried by the D-12-pinned render gates
and not by the two-build manifest it nominally rests on; and the manifest's own `find`-over-
everything recipe swept Sphinx's non-reproducible `.doctrees/` cache, proven by a third
identical-code build before the recipe was narrowed. Both were recorded as disclosed caveats
instead of being smoothed into a clean-looking result. Third, **the fix reintroduced its own
flagship failure shape one level deeper, and the two review lenses disagreed about how much that
matters**: the escape branch keys on `path.basename()` alone, so two escaping images sharing a
basename across different directories collide onto one key — rated Critical by code review and
`low / accept` by the phase's own T-50-03 threat model, which had pre-disclosed it with a hashed-key
remedy. Two items ship tracked rather than fixed by owner decision: that collision as a follow-up
todo (`resolves_phase: null`, carrying the hashed-key remedy and a RED-first instruction), and
IMG-02's missing written-first RED, closed by an **explicit, scoped override** recording that the
pre-fix observation does exist and pre-dates the fix by four days in the 2026-08-10 todo's direct
measurement — what was absent was its packaging as a pytest artifact, not the observation. The
override names its own residual: IMG-02's branches are GREEN-only inside this phase, so a future
rework there must record its own RED rather than inherit one. Next: **Phase 51 — Two-Layer Output
Documentation**.

**Phase 49 complete 2026-08-14 (6 plans, 8/8 requirement IDs COMP-05..12,
verification `passed` 5/5 success criteria).** The include decision now happens at **compile time**:
the builder computes a per-master include graph mirroring `inline_all_toctrees`, each wrapper
publishes its own edge set as Typst state under `typsphinx:include-edges`, and `visit_toctree` emits
a state-guarded include at its toctree's own position instead of an unconditional one. The
build-scoped `_included_docnames` ledger is deleted. **Defect A is closed on generated evidence** —
both masters' PDFs now carry the shared chapter's marker exactly once, read back through `pypdf` from
one byte-identical `shared.typ`, against the measured 2026-08-11 baseline of 0-and-1. The diamond,
three-master overlap, cycles, self-references, globs, orphans and a substring-collision shape all have
committed fixtures whose outcomes were **decided in wave 1 before any fixture or emitter existed**,
and GATE-02's unmodified 154-document corpus gate is green. Two limitations ride forward by decision
rather than by omission: the `:numref:` per-master divergence (owner-approved as documented, handed to
Phases 51/52) and two code-review warnings (edge-key separator collision, unbounded traversal
recursion), all three filed as tracked pending todos. Next: **Phase 50 — PR #131 Image Path Defects**.

**Phase 48 complete 2026-08-14 (7 plans, XREF-03/XREF-04, verification `passed` 19/19).** Whether a
reference's target label exists became a question Typst answers per compiled wrapper, through one
shared `_label_existence_guard()` helper; the build-time `master_included_docnames` union is gone.
This had to land before Phase 49, because fixing the include graph turns a silent omission into a hard
compile failure.

**Phase 47 complete 2026-08-12 (14 plans, 10/10 requirement IDs, verification
`passed` 12/12).** The two-layer output split has landed: content files are docname-named and
template-less, wrappers are per-`typst_documents`-entry and carry the template, and
`_is_master_document()` is gone. B-1 and B-2 are closed, target-as-path reverses v0.7.1's D-05/D-06/D-07
while keeping the escape guards, and all three collision classes (BLD-02/03/04) route through one
pre-write validator. Composition *semantics* are untouched by design — the wrapper reproduces today's
include behaviour through the new file shape, isolating "does the new file shape work" from "does the
new graph algorithm work" (Phase 49). The milestone branch `gsd/v0.8.0-multi-master-composition` is on
`origin` with a completed cross-OS CI run (invariant #5, discharged in-phase rather than at the release
PR). Next: **Phase 48 — Compile-Time Cross-Reference Guard**, which must land no later than Phase 49.

**v0.7.1 (bug-fix round) — SHIPPED 2026-08-11. 8 phases, 43 plans, 122 tasks, 19/19 v1 requirements
complete, zero known gaps.** PyPI `typsphinx 0.7.1` is live (wheel 135,318 B + sdist 580,288 B),
published by release run `31462027486` after owner approval of the `pypi` environment; the GitHub
Release carries both distributions plus the tag-time `typsphinx.pdf`. PR #132 merged to `main` with
all 15 CI checks green (merge commit `48bf135`), tagged `v0.7.1` there; `typsphinx-doc-translations`
took its standing second tag after `update-pin.yml` run `31462409929` advanced the submodule pin
`87f242a` → `48bf135`.

**REL-04 closed for the first time — and closed the way the requirement demanded.** v0.7.0 reported
its mechanism done on the strength of the workflow file being correct, and the release then failed at
`uv: command not found`. This close refused that shortcut: the acceptance evidence is release run
`31462027486`'s `Create GitHub Release` job completing **success** on a real tag push, and the
published body was then *measured* rather than assumed — its first 77 lines are byte-identical to
`scripts/extract_changelog_section.py 0.7.1`'s stdout, with zero `git log --pretty` commit-dump
lines. Phase 46 was scoped prep-only precisely so this could not be claimed early, and the fence
held: two independent `git tag` / `git ls-remote` probes 3m4s apart both came back empty at phase
close.

**Nine todos and two dormant seeds remain open, all by argued decision.** `46-HANDOFF.md`
§ "Deferred by decision, not oversight" enumerated every one before the close. The cluster worth
promoting first is the three `typst_documents`-modelling defects (duplicate targets silently dropping
a master — re-measured live in Phase 46 and still reachable after Phase 44's collision guard; a
master that is also a toctree child being unrepresentable; a shared document dropped from all but the
first master), followed by the two `_track_image` defects that ship in v0.7.1 unfixed by owner
decision D-27. The five Phase 45.1 "deferred items" were **re-measured at this close and found
already resolved** by Phase 45.2 (QUA-04) at their root cause, not carried.

<details>
<summary>Phase 46 execution detail (retained for context)</summary>

**Phase 46 complete 2026-08-11, 6/6 plans across 4 waves, verification `passed` 5/5 success
criteria, code review 0 critical / 3 warning / 2 info.**

The v0.7.1 tree is ready to publish and proven green, with zero irreversible action taken. This is
the standing prep-only Release phase: bump, curate, prove, hand off. `pyproject.toml` is the sole
`0.7.1` literal with `uv.lock` and `README.md` in lockstep and the editable metadata regenerated so
`typsphinx.__version__` actually reports `0.7.1`; `CHANGELOG.md` carries a curated `## [0.7.1]` entry
that calls out both user-visible behavioural changes inside a patch release (CONF-08's output-filename
rename, CONF-09's rendered title/author change) three ways at once, because D-01 held the version at
`0.7.1` and so the version number itself carries no warning.

**SC#3's authority is a live CI run, not a local one, and the phase was built around that.** Local
never sees Windows or macOS, and on this machine `tox -e lint` cannot run at all. So D-23 split the
proof into two dispatched runs: run 1 (`31456868265`) confirmed the Windows path-separator repair
that *cannot* be verified locally, deliberately placed at the head of the phase so a missed repair
could not land its retry commits after the version bump; run 2 (`31458368833`, on pushed SHA
`26b2e6c`) carries the bump and the `## [0.7.1]` entry and **is** SC#3's authority — 12/12 jobs green.
The verifier re-fetched that run rather than trusting the transcript. The local half — both docs
builds, the full-corpus `-b typstpdf` gate, and a single `ja` build — is recorded as what CI
structurally does not produce.

**Two requirements deliberately did not close, and that is the phase's point.** REL-04's acceptance
evidence is a real tag push whose `create-release` job runs to completion, which only the publish can
generate; v0.7.0 reported this requirement's mechanism as done on the strength of the workflow file
and the release then failed, and this phase was scoped so it could not repeat that. REL-06's own text
ends "*and the publish … executed at `/gsd-complete-milestone`*". Both rows stayed `[ ]` through every
plan — and **the recorded `phase.complete` auto-flip hazard did recur**: at close-out it flipped REL-06
to `[x]`, and `close_phase_todos` moved the REL-04 todo to `completed/` on the strength of a
`resolves_phase: 46` line written on 2026-08-04, before the phase was scoped prep-only. Both were
caught by the diff-before-trusting guard `46-HANDOFF.md` item 6 carries forward from `41-HANDOFF.md`,
and both were reverted. The hazard is now three-for-three on release-prep phases specifically.

**A plan-verification defect was found twice, independently, and corrected rather than scored as a
gap.** Plans 46-01 and 46-05 each hit the acceptance command `git diff origin/main..HEAD --
typsphinx/` (expected empty), which is unsatisfiable by construction under `branching_strategy:
milestone` — `origin/main`'s merge-base with this branch predates Phase 43, so five phases of
legitimate un-mirrored work diverge. The corrected anchor `c72be91..HEAD` (the tip immediately after
this phase's own merge) *is* empty and proves the prep-only fence directly. Both the literal and the
corrected command are recorded verbatim in the evidence, rather than the literal one being quietly
swapped out.

Code review found 0 critical. Two of its three warnings are against `typsphinx/builder.py`'s
`_track_image`, which entered this diff via the PR #131 merge this phase performed, not via the
phase's own edits: an un-guarded namespace collision where a rehomed converted image's
`doctreedir`-relative path can silently shadow a user image at the same source-relative path, and a
missing containment check on `path.relpath(resolved_uri, self.doctreedir)`. Both are filed, not fixed
— the prep-only fence forbids `typsphinx/` edits here.

</details>

<!-- Prior: v0.7.1 — Phase 45.2 complete 2026-08-11, 5/5 plans across 4 waves, verification
`passed` 7/7 success criteria, code review 0 critical / 1 warning / 2 info. QUA-04 validated. -->

**Phase 45.2 detail (superseded as "current" by Phase 46, retained for context):**

**v0.7.1 (bug-fix round) — Phase 45.2 complete 2026-08-11, 5/5 plans across 4 waves, verification
`passed` 7/7 success criteria, code review 0 critical / 1 warning / 2 info. QUA-04 validated.**

The task runner this project documents as its own now actually runs on the maintainer's machine.
The repair was one dependency name: `pyproject.toml`'s `dev` extra moved from `tox-uv` (a meta
package bundling a PyPI `uv` wheel) to `tox-uv-bare` (the same upstream author's split without it),
which removes the generic-linux ELF at `.venv/bin/uv` that NixOS has no loader for. Measured
before/after on the main tree under the outer `uv run pytest` that `CLAUDE.md` mandates for every
worktree executor: **45 failed / 939 passed → 984 passed / 0 failed**, byte-identical to the
`.venv/bin/python -m pytest` control, with the sorted node-id delta confirming every pre-fix failure
converted and nothing regressed.

A second defect was found in the same file and fixed with it. Every `tox.ini` environment sets
`runner = uv-venv-lock-runner`, which provisions from `uv.lock` via `uv sync` and therefore installs
only what `pyproject.toml` declares — so the `deps =` lists on `[testenv]`, `lint`, `type` and `cov`
had never installed anything, and those environments have never contained `black`, `ruff`, `mypy` or
`pytest`. They now declare `extras = dev`, the shape `docs-html`/`docs-pdf`/`docs` already used.
**This is what closed the CI false-green:** CI invokes `uv run tox`, which prepends `.venv/bin` to
`PATH`, so `black --check .` and `ruff check .` were passing out of the outer venv while
`lint: freeze>` showed neither tool inside the tox environment — CI's green had never validated
`tox.ini`. It does now.

Three things are worth carrying forward. **The project's own recorded diagnosis was wrong and was
corrected rather than worked around**: `uv` was framed as "not on PATH" when it was on PATH and
simply the wrong build, and the 45 failures were carried for several milestones as unfixable NixOS
environmental false positives — a framing that forced PR #131's review to compare against a `main`
baseline instead of reading absolute counts. **The correction was scoped, not swept**: a mechanical
repo-wide grep for `exit 127` / `command not found` would have deleted six records describing
REL-04's genuinely different `create-release` failure, which are the recorded justification for an
open requirement; those six were named in advance and left byte-unchanged, and the eight test
docstrings had their *tense* corrected without their (factually correct) diagnosis being rewritten.
**Making tox real surfaced a defect it had been hiding**: with the tools finally running inside the
tox environments, CI exposed `[testenv]`'s `package = wheel` — present since the repo's first commit
— silently dropping `typsphinx/templates/base.typ` from non-editable installs, failing 23 tests
across every OS. Fixed in-phase (`package = editable`, the lock runner's own default).

Two defects were deliberately routed out rather than fixed, both filed as todos: `.venv/bin/ruff` is
the same class of generic-linux ELF and cannot execute here (every available repair is NixOS-local,
the category this milestone declined), so `tox -e lint` reaches and passes `black --check .` and
then stops — named, not reframed as an environmental false positive; and `tox -e py312` cannot run
locally because no Python 3.12 exists in the devShell. CI remains red on exactly two
`windows-latest` jobs from a path-separator bug in a guard Phase 45.1 added the day before, isolated
and filed. Known follow-up, not a gap: `CLAUDE.md:11` and `CLAUDE.md:77` still name the removed
`tox-uv` package, left unfixed because SC#7 fences this phase to the `dev` extra, `tox.ini` and
`uv.lock` — a fence Phase 46's SC#3 depends on (code review WR-01).

<!-- Prior: v0.7.1 — Phase 45.1 complete 2026-08-10, 7/7 plans across 6 waves (6 planned +
1 gap-closure round), verification `passed` 10/10 must-haves, code review 0 critical / 2 warning /
1 info. DOC-13, CONF-10, CONF-11 and CONF-12 validated. -->

**Phase 45.1 detail (superseded as "current" by Phase 45.2, retained for context):**

A reader who writes a custom template from the published documentation now gets a build that works.
The contract is exclusivity, not merge: a declared `typst_template_function["params"]` is the
**complete** parameter set, so the auto-derived `title`/`authors`/`date`, the `typst_elements`
allowlist merge and the `toctree_*` merge are all withheld — the predicate is the *presence* of the
key, so `params: {}` passes nothing (CONF-11, D-B). The auto-derived Typst `lang` was widened the
other way: it now reaches **every** non-package route — the bundled default, an explicit
`typst_template`, and a `<srcdir>/base.typ` shadow alike — and is withheld only under
`typst_package`, because typsphinx never introspects a third-party Universe function's signature
(CONF-12, D-I). `typst_authors` was removed outright (CONF-10, D-F); rich author structure is
expressed through `typst_template_function`'s `params` route instead.

The phase's own closure round is the part worth remembering. Plan 06 proved the published contract
and the shipped behaviour agreed in both directions — but its enumeration read `templates.rst` and
nothing else, so a stale pre-CONF-12 claim survived on `configuration.rst`, the very page
`templates.rst` cross-references. Plan 07 corrected that prose and replaced the one-shot manual
sweep with a permanent guard (`tests/test_docs_contract_claims_gate.py`) that derives route truth by
*calling* `TemplateEngine.uses_bundled_default_template()` over four route configurations, compares
it to the docs' published claim set by **set equality in both directions** (no containment), closes
its claim-page list by assertion in both directions so neither a new claim page nor a rotted
exclusion can pass, and is proved fail-first against the verbatim pre-fix sentence. D-J's declined
parameter-name lockstep test stays declined: the guard is on the claim-correctness axis and does not
read `docs/source/_typst/custom_template.typ` at all.

Known follow-up, not a gap: `examples/charged-ieee/approach1` (the README's "Recommended" sample)
and `templates.rst`'s introductory sample declare `params` without a `title` key on the
`typst_package` route, so under D-B exclusivity the example's compiled PDF never receives a title —
a pre-existing example-quality defect the verifier confirmed predates this phase and which no
DOC-13-scoped page claims otherwise (code review WR-01).

<!-- Prior: v0.7.1 — Phase 45 complete 2026-08-10, 4/4 plans across 3 waves, verification
`passed` 5/5 success criteria, code review 0 critical / 3 warning / 0 info. DOC-11, DOC-12,
QUA-02 and QUA-03 validated. -->

**Phase 45 detail (superseded as "current" by Phase 45.1, retained for context):**

Documentation currency closed the two drift channels the milestone carried. `docs/source/changelog.rst`
now delegates to repo-root `CHANGELOG.md` through `myst-parser` (`docs` extra only), so the page that
sat 12 releases stale carries every release from 0.4.1 through 0.7.0 and a future release costs one
`CHANGELOG.md` entry rather than a re-derivation. README / `quickstart.rst` /
`user_guide/configuration.rst` now describe what Phase 44 actually shipped: `typst_documents` is
optional, an unset value derives one master entry from `make_filename_from_project(project)`, and an
explicit setting always wins. Both claims are bound to real `sphinx-build` runs by new gates
(`tests/test_changelog_page_gate.py`, `tests/test_quickstart_docs_gate.py`) rather than to requirement
prose. The two carried hygiene todos closed with a single production change:
`derive_typst_lang()`'s rejection warning now has exactly one call site, and the whole phase's
`typsphinx/` diff is that one hunk in `typsphinx/template_engine.py`.

Known follow-up, not a gap: delegating the changelog made a pre-existing contradiction visible
side-by-side on the live page — `changelog.rst`'s "0.2.x → 0.3.x: no breaking changes" against
`CHANGELOG.md`'s 0.3.0 breaking package rename (code review WR-01). It was out of scope for
Phase 45's plans.

<!-- Prior: v0.7.1 — Phase 44.2 complete 2026-08-07, 7/7 plans across 7 waves (3 planned +
4 gap-closure rounds), verification `passed` 6/6 must-haves, code review 0 critical / 1 warning /
1 info. CONF-09 validated. -->

**Phase 44.2 detail (superseded as "current" by Phase 45, retained for context):**

An explicit `typst_documents` entry's `[2]` title and `[3]` author now reach the compiled document,
as they do in Sphinx's LaTeX builder, instead of being silently ignored while `config.project` /
`config.author` win. The published five-element contract in
`docs/source/user_guide/configuration.rst` is no longer partly inert. The production change is
small and confined to `typsphinx/writer.py` and `typsphinx/template_engine.py`.

**The notable part is what it took to get the DOCUMENTATION right, not the code.** The runtime fix
landed in wave 1 and never changed again — every one of the four subsequent verification rounds
failed on the same defect class in prose: a published sentence making an unscoped universal or
negative-existential claim about when `params["authors"]` is written, which is false because
`authors` is written at **more than one pipeline stage**. Round 2 keyed the rule on the mapping
*source* key instead of the assignment *target*. Round 3 corrected that and introduced
`configuration.rst:194`'s "and nothing else in typsphinx replaces it" — false, because
`typst_template_function`'s dict-form `params["authors"]` is applied later, in `render()`.

**Root cause of the recurrence, measured rather than guessed: the enumeration inherited the
author's frame.** Round 3 built a per-sentence enumeration specifically to break the cycle and it
failed the same way — its site set was derived from the passages its own plan had edited (only 3 of
9 graded sites were even in `configuration.rst`), and its row space was scoped to
`map_parameters()`'s writers, so `render()`'s `all_params.update(self.typst_template_params)` — a
fourth writer of the same key, at a later stage — had no axis in it at all. The false clause sat
*inside* a graded site's own cited line range while the row quoted the following sentence.

Round 4 inverted the derivation and split it across two waves so the grader was not the author:
wave 6 enumerated the **writers first, from the AST, across the whole pipeline**, then derived the
prose that must be true and published it as an ordered **two-stage rule**; wave 7 ran in a separate
worktree and session with no memory of what wave 6 intended, re-derived the stage set from the code
itself, and graded every claim-bearing sentence against per-stage falsification rows with a runnable
no-silent-drop equality assertion. That independent grading found and fixed a genuine residual
(two bullets still using unscoped "is then passed" language) — the mechanism worked. The
falsifying three-knob configuration is now a passing gate at two levels: a real `sphinx-build -b
typst` with a control, and an API-level cell spanning `map_parameters()` and `render()` in one body
(`tests/test_authors_pipeline_stage_gate.py`).

**v0.7.1 (bug-fix round) — Phase 44.1 complete 2026-08-05, 4/4 plans across 3 waves, verification
`passed` 8/8 SC, code review `clean`. TOC-01 validated.**

A document reached through a `toctree` now renders its headings one level deeper than its parent, so
the PDF outline nests instead of being flat — and nested toctrees compose. The repair has **two**
parts, and the second was only found by measuring: `visit_title` now emits Typst's *relative*
`heading(depth: N)` instead of the absolute `heading(level: N)` (in Typst, `level:` overrides the
ambient `heading(offset: …)`; only `depth:` resolves to `offset + depth`), and `visit_toctree`'s
scope opener now emits `context { set heading(offset: heading.offset + 1) }` instead of the absolute
`set heading(offset: 1)`. Part 2 exists because `set heading(offset: N)` is an **absolute assignment**
on Typst's style chain, so a nested scope *replaces* its parent's offset rather than adding to it —
three nesting levels queried as `[1, 2, 2]` with part 1 alone, and `[1, 2, 3]` with both. The whole
production change is confined to `typsphinx/translator.py`; `typsphinx/templates/base.typ` is
byte-unchanged.

**The phase's method is the notable part, not its size.** Every claim is anchored to a resolved
level from `typst.query(…, 'heading', field='level')` against a *compiled* document, never to a grep
of the `.typ` source — the defect being fixed was precisely one where the source looked right and the
resolved output was wrong. Master-document invariance (SC#3) is proved two ways over the full
`docs/source` corpus plus every root under `tests/roots`, because either half alone is insufficient:
resolved-level equality would miss a non-heading diff, and byte equality after mechanical
substitution would not show the substituted text still resolves to the same level. One recorded
exception survives that proof (`docs/source/api/index.typ`), traced word-for-word to Sphinx autodoc
rendering the phase's own rewritten `visit_toctree` docstring — an artifact of documenting the change,
not a leak of it.

**The assertion migration surfaced a failure mode worth remembering: tests that go SILENT rather than
RED.** Four of the seven `tests/test_topics.py` sites were *negative* assertions — "no heading was
emitted here". Once the emitted literal changed, the string they searched for could no longer be
produced by any code path, so all four kept passing while detecting nothing. A mechanical
find-and-replace over positive assertions would have missed every one. Each was re-proved against the
pre-fix commit with a per-guard positive control, and the site census was re-derived by repo-wide
grep rather than transcribed — which found sites the planning document's own addendum had undercounted.

**v0.7.1 (bug-fix round) — Phase 44 complete 2026-08-04, 5/5 plans across 4 waves (4 planned + 1
gap closure), verification `passed` 6/6 must-haves. CONF-08 and BLD-01 both validated.**

`typst_documents` no longer defaults to `[]`. It resolves to a Sphinx-native derived default —
registered as a callable default exactly the way Sphinx's own LaTeX builder registers
`latex_documents` — deriving from `root_doc`/`project`/`author` with the target name in LaTeX's own
shape, `make_filename_from_project(project)` → `<project>.typ`. Following the Quick Start with no
`typst_documents` line now produces a real PDF instead of exiting 0 with one warning and zero output.
An explicitly-set `typst_documents` always wins; an explicit empty list stays a deliberate opt-out.
BLD-01 rode along in the same method: a non-`str` docname reaching `TypstPDFBuilder.finish()` now
fails with an actionable typsphinx-level error instead of a raw `TypeError` out of `path.dirname()`.
**The accepted, owner-stated cost is a user-visible rename** of the existing `-b typst` output for
anyone who never set `typst_documents`; the before/after pair was measured on real builds
(44-GATE-EVIDENCE-03.md) and is the source text Phase 46 owes the CHANGELOG.

**The phase's own code review again found a BLOCKER in the surface the phase had just widened** —
the same shape as Phase 43, and worth remembering as a pattern rather than a coincidence. Making the
default derived meant a pre-existing collision mechanism became reachable with ZERO configuration:
an ordinary project named after its first chapter (`project = "Chapter 1"` alongside a
toctree-included `chapter1.rst`) had the derived master silently destroy that chapter's rendered
output on `-b typst` (exit 0, no warning) and hard-fail `-b typstpdf` with `TypstError: cyclic
import`; a project slugifying to `_template` clobbered the shared template file every master
imports. Gap-closure plan 44-05 closed it at the single normalization site both the write path and
the PDF read-back path already flow through (`_resolve_output_stem`), comparing the
directory-qualified effective path — not the bare stem — against `env.found_docs` and the reserved
`_template`, then warning and falling back to the docname. Four real `sphinx-build` subprocess
scenarios cover (docname collision × `_template` clobber) × (derived path × explicit path).

**One defect of the same class remains open and is deliberately NOT closed here (CR-02).** Two
explicit `typst_documents` entries naming the same target as *each other* still silently drop one
master's output at exit 0 with no warning — neither target is itself a docname, so the new
`found_docs` membership test cannot fire. It is not a regression of this phase (it predates the
derived default and needs a deliberately duplicated explicit config, unreachable from the Quick
Start), 44-05 recorded it as an out-of-scope observation before executing, and 44-VERIFICATION.md
independently judged it outside all five SCs. Filed as
`.planning/todos/pending/2026-08-04-duplicate-typst-documents-target-silently-drops-a-master.md`.

**v0.7.1 (bug-fix round) — Phase 43 complete 2026-08-04, 6/5 plans across 4 waves (5 planned + 1
gap closure), verification `passed` 6/6 SC. TBL-04, TBL-05, FIG-01 and QUA-01 all validated.**

Three container-state defects in `TypstTranslator` shared one root cause: scalar state that a nested
container of the same kind silently clobbered. The phase replaced each with a guarded stack —
`_push_table_state`/`_pop_table_state` (TBL-04), `_push_figure_state`/`_pop_figure_state` plus a new
`visit_legend`/`depart_legend` handler (FIG-01), and a `_table_is_captioned` snapshot splitting a
table's RENDERING decision from its ANCHORING decision (TBL-05). The whole production change is
confined to `typsphinx/translator.py` (+518/−53); no other module, no dependency change.

**The phase's own code review then found a BLOCKER in code the phase had just introduced** —
`visit_legend` saved separator state in flat scalars, so a legend inside a legend leaked
`in_list_item=True` into the rest of the document, emitting silently wrong Typst with exit 0 and no
warning. It was reproduced independently before any fix, closed by gap-closure plan 43-06 with a real
stack and a regression gate, and plan 43-05's SC#4/SC#5 evidence was regenerated against the fixed
tip. Worth remembering: the original FIG-01 work looked complete and passed its own gates — the
defect class the phase existed to fix survived one level up in the very handler that fixed it.

**Two milestone-process facts established here.** (1) `.github/workflows/ci.yml`'s `push:` trigger is
scoped to `branches: [main, develop]`, so pushing a milestone branch registers **no** `ci.yml` run —
CI on a milestone branch must be started via the pre-existing `workflow_dispatch` trigger
(`gh workflow run ci.yml --ref <branch>`). This is a second, independent reason the v0.7.0 Windows
lanes never ran, beyond "the branch was never pushed". (2) Milestone invariant #5 was discharged
inside the first phase of the milestone rather than at the release PR: `gsd/v0.7.1-bug-fix-round` is
on `origin`, and CI run `30870536482` against the phase's final tip completed `success` across all 12
lanes including both Windows lanes.

**v0.7.0 — API rendering design overhaul: 8 of 8 phases complete (36, 37, 38, 39, 40, 40.1, 41, 42),
57/57 plans. Prepped and fully verified but NOT published — the remaining work is the publish itself.
Next action: `/gsd-complete-milestone`.**

**Amended 2026-08-03 (`/gsd-review-backlog`, owner decision):** backlog item 999.2 was promoted into
this milestone as **Phase 42 — Captioned Table Drops Preceding Target Label**, adding requirement
**TBL-03** (v1 total 32 → 33) *after* Phase 41 had already completed. The owner decided the v0.7.0
publish blocks on it. The paragraphs below describing Phase 41 as the milestone's last phase are
accurate as of Phase 41's close but no longer describe the milestone's end state — Phase 42 is that
end state, and it closed on 2026-08-04.

Phase 42 (Captioned Table Drops Preceding Target Label) completed 2026-08-04, 6/6 plans across 3
waves, verification `passed` 6/6 SC, TBL-03 validated. The defect was not a misplaced anchor but a
**discarded** one: `depart_table`'s trailing
`_emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` fired while `self.in_table` was still
True, so `add_text()` diverted the propagated-target anchor into `self.table_cell_content` — a buffer
`del`eted a few statements later and never read. The entire production fix is that one call moved
past `self.in_table = False`, gated on a `was_captioned` boolean captured before `self.table_caption`
is reset; `typsphinx/translator.py` is the only source file the phase touched, in a single commit.

The phase is a *classic* GATE-01 case under milestone invariant #4 (alongside CIT-01): the defect
fails the Typst compile rather than compiling wrong, so the fixture was recorded RED as a real
`TypstError` (`label \`<index:tbl-target>\` does not exist in the document`) against unfixed
production code — `git merge-base --is-ancestor` confirms the RED commit is a strict ancestor of the
fix commit, and wave 1 left `typsphinx/` byte-unchanged. Suite went 7 failed / 814 passed (all 7 in
the new gate module) → **821 passed / 1 skipped / 0 failed**. SC#2 was answered by measurement rather
than inference: captioned figures do **not** share the drop, and a permanent figure-side regression
gate now stops a future change from copying the table path's defect back into the image path. A
repo-wide sweep of all 21 `_emit_id_anchors` call sites found `depart_table` to be the sole misrouted
one, with the image path a recorded null result. SC#4's caption-less byte-invariance was proven by
an empty two-build diff carrying a positive control (a non-empty diff for the captioned shapes and
two distinct resolved `typsphinx.__file__` paths), so the empty result is meaningful rather than the
false-empty an unprovisioned worktree would produce.

Two items are deliberately left open rather than closed here. Code review finding **WR-01** — the
`_emit_id_anchors` docstring still claims `depart_figure` is the "sole user" of `skip_ids`, false
since Phase 25 — was not fixed, because touching `translator.py` after the SC#4 byte-invariance
proof and the SC#6 invariant sweep were recorded would put the change outside the SHA range those
artifacts measured. Finding **IN-02** is a real, severe, *pre-existing* bug (verified byte-identical
pre- and post-fix): a table nested inside a `list-table` cell silently drops the outer table
structure, because `in_table`/`table_cell_content` are scalars rather than a stack. Neither blocks
v0.7.0.

Phase 41 (v0.7.0 Release Automation + Release Prep) completed 2026-08-03, 7/7 plans across 3 waves,
verification `passed` 5/5 SC. `release.yml` now builds the GitHub Release body from `CHANGELOG.md`'s
curated `## [X.Y.Z]` section via a committed, pytest-covered extractor, with the `git log --pretty`
commit dump removed rather than fenced, and a CHANGELOG-existence check added to the `validate` job
strictly upstream of `build` / `publish-pypi` / `create-release` — so a missing section now fails
before PyPI is published to, instead of after. The tree is bumped to 0.7.0 across its three lockstep
sites with a curated `## [0.7.0]` entry and its link-block rollover.

The phase's evidence is deliberately measurement-first: the post-bump tree was proven green live
(805 passed / 1 skipped, lint/type trio clean, the full-corpus Sphinx `doc/` `-b typstpdf` gate
**executed** rather than skipped, both docs dogfooding builds exit 0); the milestone invariants were
re-derived over the SHA-anchored full diff rather than transcribed from prior records (zero new
runtime dependencies, `@preview` still four packages with no new lockstep site, 51 changed node
handlers each mapped to a recorded-RED GATE-01 fixture); and the `ja` glyph bar's fourth check is the
owner's own visual sign-off, since Typst's font fallback is silent and this milestone added 24
`raw(` call sites that resolve to a monospace family with no CJK coverage.

**Two things are worth carrying forward.** First, the phase's `execute:post` code review found a
shell-injection defect in `release.yml` (`${{ }}` interpolated inside `run:` blocks, exploitable via
a tag name); it was fixed inside the phase, and the fix covered *every* shell-context interpolation
in the file, not just the one this phase added — the anti-pattern pre-dated Phase 41 at two other
sites, including the actual untrusted entry point. Second, `phase.complete` auto-flipped REL-04's and
REL-05's checkboxes against the phase's own decision that the flip is close-side work; the flip was
caught by diffing against a pre-run copy and reverted. Both are recorded in
`41-REL04-EVIDENCE.md`, `41-REVIEW.md`, and `41-HANDOFF.md`.

Phase 40.1 (Citation Degradation Hardening, INSERTED) completed 2026-08-02, 4/4 plans, verification
`passed` 5/5 SC. It closed the three graceful-degradation gaps `40-REVIEW.md` recorded, under
milestone invariant #4's RED-before-fix discipline: `visit_citation`'s backref loop is fail-closed
when the citing `nodes.reference` cannot be located (WR-01, a whole-document Typst compile fatal
reachable from an ordinary `.. only::`-pruned citing site); `_citation_run_neighbour` treats an
ids-less `nodes.target` as inert so one reference list stops silently splitting into two grids
(WR-02); and the D-14 anchor judgement — previously written in two places held together by nothing —
is now one shared `_reference_anchor_decision` predicate returning the anchor label alongside the
boolean, with `_citing_reference_has_own_anchor` deleted rather than kept as a delegator (WR-03).
Because that last one rewrites `visit_reference`, a hot path handling every link in the codebase,
Phase 40's D-14 non-regression obligation was re-incurred and discharged: byte-identical `.typ`
emission for the frozen control fixture (sha256 matched a baseline captured before any translator
byte changed), the full-corpus `-b typstpdf` gate **observed** green rather than skipped, and 799
passed / 1 skipped across the full suite. `40.1-NONREGRESSION.md` §4 leaves Phase 41's SC#4 sweep a
change-site → RED manifest to read rather than a pile to reconstruct.

Phase 40 (Citations — Full Round Trip) completed 2026-08-02, 5/5 plans, verification `passed` 5/5 SC
+ 6/6 requirements. A document containing docutils citations no longer aborts the Typst compile; it
renders a real reference list — one hanging-indent grid per run of consecutive definitions, bodies
aligned past the widest label in that run, `[Label]` links resolving in both directions, docutils'
own same-document back-references, and document order preserved. `examples/charged-ieee`'s citation
syntax is restored in both approaches, byte-identical to each other again.

**The phase's own gate needed repairing before it could grade the work — and that is the part worth
remembering.** Four of nine selectors stayed RED after the handlers landed, and all four traced to
defects in the Wave-0 test module rather than the translator: a sentinel-column helper that measured
the line's leading whitespace instead of the marker's column (so it could never pass in either
direction, making it incapable of validating CIT-02 at all), two helpers tripping an escalated Sphinx
deprecation before reaching any citation assertion, and a concat check demanding a shape that D-14 —
decided by this same phase — had deliberately changed. Repairing a gate module that two other plans
had explicitly forbidden touching is indistinguishable from laundering a green, so the correction was
made a separate plan (40-05) under two prohibitions — no observed value transcribed into the module,
no assertion weakened — and closed with a re-proof rather than an assurance: restored over the
pre-fix translator the corrected module goes 9/9 RED, checked independently three times. The six
amendments are recorded in Section 8 of `40-GATE-EVIDENCE-01.md` with the original RED left
byte-unchanged, the same amended-against-measurement treatment SC#3 received earlier in the phase.

**Three latent edge cases are recorded and open** (`40-REVIEW.md`, adjudicated non-blocking in
verification): WR-01, where a `None` from `_find_citing_reference` falls through as *eligible*
instead of being skipped like the adjacent no-anchor case, which would emit a `link()` to a label
nothing attaches — the compile-fatal class this phase exists to remove, reachable only via the stale
id-registry shape `_find_citing_reference`'s own docstring documents; WR-02, an ids-less
`nodes.target` not treated as an emits-nothing sibling by the run scan, which could split one
reference list into two grids; and WR-03, D-14 eligibility logic duplicated across two call sites
with no enforced invariant keeping them in sync. None is exercised by the phase's eleven-scenario
fixture.

Prior phase (39) detail follows. Admonitions now carry the meaning their type implies: `seealso`
moved to the hint bucket (`tip`), a generic `.. admonition::` renders as a styled `notify` box
carrying its own custom title, `topic` routes to `abstract`, and static titles come from
`sphinx.locale.admonitionlabels` through the shared `escape_typst_string` boundary rather than from
hand-written literals. The two folded rubric defects Phase 36 deferred here are closed:
`visit_rubric`/`depart_rubric` own their save slots (ending the document-wide `par()`-wrapper loss
a nested inline-markup rubric used to cause), and the double-counted id-anchor separator is gone.

**The red family is three functions, not one — a recorded design reversal, not a defect repair.**
The phase originally shipped with locked decision D-03 folding `attention`, `danger` and `error`
onto a single `error()` call. Conversational UAT after verification surfaced gap `G-39-1`: shown a
live A/B/C render comparison, the owner reversed D-03. Plans 39-09..39-13 closed it additively —
`danger` → gentle-clues `danger()`, `attention` → `memo()`, `error` unchanged, so `"error"` is now
passed by exactly one call site where three passed it before. D-03's original text, ADM-02's
original wording and ROADMAP SC#1's original clause all survive verbatim under dated superseded
markers beside their replacements (`D-03-R`), so a later reader can see both decisions and why the
second followed the first. ADM-02's surviving intent is that `attention` leaves the orange warning
group for the red family — never that it be byte-identical to `danger`/`error`.

ADM-04 — the milestone's only `[V]` requirement — was closed by **owner sign-off against a real
greyscale render**, and then **re-taken** under the new taxonomy: the original artifact had been
rendered from code that folded the three red types into one, so it could not evidence a taxonomy in
which they are three. The re-render was produced from post-reversal code with the routing gates
verified green first, and the owner approved it against a checkpoint that named the
`attention`/`error` adjacency explicitly. Both verdicts are on file; the amendment states which is
operative. Suite 774 passed / 1 skipped / 0 failed; the full-corpus `-b typstpdf` gate re-run for
real (not skipped) against Sphinx `v9.1.0`. Remaining: Phase 40 (Citations — Full Round Trip,
structurally independent and the milestone's one classic `TypstError`-RED exception) and Phase 41
(release automation + prep).

**Phase 37 (Signature Typography — the `desc_*` Family) complete 2026-08-01, 9/9 plans,
verification `passed` 9/9.** An API signature now
reads as a signature: `desc_name`/`desc_annotation` in bold monospace, `desc_addname` in
regular-weight monospace, every parameter-list delimiter through the same monospace primitive, each
parameter's own name in italic, a real `→` glyph reaching the reader's PDF (SIG-06), a
hanging-indent + U+200B overflow mechanism (SIG-07), page keep-together (SIG-09), and exactly one
break between blocks (SIG-08). The folded D-11 defect is fixed too — the optional-group comma now
lands *inside* the bracket, matching Sphinx's own HTML writer. All nine SIG requirements are
Complete; `typsphinx/` delta is still `translator.py` only. Suite 686 passed / 1 skipped / 0 failed
(up 33 from Phase 36's 653), and the slow full-corpus `-b typstpdf` gate passes against 1,445 real
Sphinx v9.1.0 `doc/` signatures.

The phase's method is worth recording, because it is what made the result checkable. Wave 1 wrote
every assertion RED against the untouched translator *before* any code edit — 33 node ids, matched
exactly with zero unexpected failures — and each later wave was verified by node-id **set
difference**, never by count (flipping 2 / 20 / 11 / 1 with zero regressions at every boundary).
Expected strings were hand-derived from `37-EMISSION-CONTRACT.md` throughout; `golden.typ` turned
green in Wave 4 with **zero reconciliation**, independently confirming Wave 1's derivation.

The one genuine mid-flight failure is the most useful thing the phase produced. The post-merge gate
after Wave 3 caught a Phase 34 invariance golden going red, and the render showed **every** signature
overlapping the first line of its own description body. The cause was the emission contract itself:
its `above: 0pt, below: 0pt` mandate came from a probe that did not carry surrounding paragraph flow,
and compensated for a doubled-gap defect that Wave 2 had already removed at source. Plan 37-09
(authored mid-execution on the owner's decision) amended the contract with the corrected measurement
*and the reason the original probe missed*, so Phase 38 does not re-derive the same mistake when it
wraps `desc_content`.

Phases 40–41 (citations, release prep) are unstarted. The `par()`-loss leak deferred out of Phase 36
by decision (D-02) is **closed** — Phase 39 owned `rubric` and fixed it. Still open from Phase 37's
code review and filed as todos: `_desc_break_marker` goes stale across `self.body` buffer swaps
outside the guarded `in_table` path (warning-level, needs a GATE-01 fixture first), an unbalanced `*`
in a docstring, and `EXPECTED_PAGE_COUNT_PRE_PHASE` now holding a post-phase value. New from Phase
39's code review (WR-01, not yet filed): six admonition unit tests in `tests/test_admonitions.py`
were not updated to assert the `, title: "…"` argument the handlers now emit, and some of their
docstrings are factually stale as a result — a coverage gap only, since the render-gate module
covers the actual emitted output.

**Shipped: v0.6.5 — inline-math separator hotfix (2026-07-29).** Both phases (34, 35) complete,
2/2 requirements. MATH-01 is closed: a paragraph mixing prose and inline math — including with no
intervening whitespace, and inside list items, field bodies, and definition-list terms — now builds
through `sphinx-build -b typstpdf` on both the mitex and native emission paths instead of aborting
the Typst compile. The fix is three lines of protocol participation in `visit_math` plus the
list-item half in `visit_math_block`, matching `visit_literal`'s existing pattern. Suite is
649 passed / 1 skipped (up 2 from v0.6.4's 647 — the two new GATE-01 tests); the `typsphinx/` delta
this milestone is confined to those two visitors (+45 lines, `translator.py` only).

Phase 35 completed the prep half: `pyproject.toml` / `README.md` / `uv.lock` all name `0.6.5`
(`typsphinx.__version__` reports it), a curated `## [0.6.5]` CHANGELOG entry is in place with the
tail link block rolled over, and Phase 34's three test-side review Warnings (WR-02/03/04) are closed
by a Construct G fixture addition plus four exact-string assertions across both emission paths —
zero `typsphinx/` change. Milestone invariants were asserted mechanically over the full
`eb696bb`-anchored diff: no new runtime dependency (the `uv.lock` delta is the 1-line self-pin), no
`@preview` bump, all four version-sync surfaces untouched. 5/5 must-haves verified
(`35-VERIFICATION.md`), code review clean. The publish half — merge to `main`, tag `v0.6.5` →
`release.yml` → PyPI + GitHub Release, plus the standing second tag on `typsphinx-doc-translations`
— executed at the milestone close per `35-HANDOFF.md`. Closeout `override_closeout`: no milestone
audit was run (owner decision — a 2-phase hotfix whose release-evidence document already covered the
audit's ground). Deferred by decision and filed as todos: WR-01 (`visit_math_block`'s redundant
blank line in list items — needs a translator change, D-05) and the `release.yml`
release-notes-body rework (D-11).

**Shipped: v0.6.4 — Read the Docs migration (2026-07-28).** All 6 phases (29, 30, 30.1, 31, 32, 33) /
33 plans complete; milestone audit `passed` (13/13 requirements, integration checker all-wired);
closeout `verified_closeout`. Documentation now lives at `https://typsphinx.readthedocs.io/` —
English and Japanese behind RTD's own flyout, PDFs produced by `typstpdf` itself via the
`build.jobs.build.pdf` override (Branch A: `@preview` egress from RTD's sandbox works). GitHub Pages
is gone: no deploy step, no `gh-pages` branch, github.io 404 confirmed live. Published `typsphinx
0.6.4` to PyPI via `release.yml` on the `v0.6.4` tag at milestone close; every release now tags two
repositories (parent + `typsphinx-doc-translations`).

**Codebase:** ~7.4k LOC Python under `typsphinx/`; v0.6.5's code delta is 8 files, +560/−4, of which
the runtime half is +45 lines in `translator.py`. Full suite 649 passed / 1 skipped. Standing guards:
4-surface `@preview` version-sync test (+ `examples/**`), advisory lychee link check (`links.yml`),
stale-URL regression tests, docs-pdf CI gate, and the GATE-01 real-`typst.compile()` fixture suite.

**Carried forward (non-blocking):** 8 pending todos (STATE.md Deferred Items — 5 carried, 3 filed
during v0.6.5) + 3 quality warnings from 30.1's review (contributing.rst toolchain step;
`custom_template.typ` as an unguarded fourth `@preview` lockstep site; no structural tests over the
live translations-repo manifests). Accepted losses: no browser-language auto-redirect; old
github.io URLs 404 with no stubs. Known cosmetic gap: the GitHub Release body is still a ~296-line
commit dump rather than the curated CHANGELOG section (todo filed, D-11).

## Milestone History / Next

> **Note (2026-07-25):** this section is a frozen v0.6.0-era snapshot retained for reference. Its
> "Next milestone" line refers to v0.6.1, which shipped 2026-07-19. The authoritative records are
> `MILESTONES.md` (shipped history) and the **Current Milestone** section at the top of this file
> (v0.6.4, active).

**v0.6.0 real-world robustness — SHIPPED 2026-07-13.** Goal achieved: Sphinx's own `doc/` tree compiles through `typstpdf` with no fatal Typst errors (Issue #114 closed) and the most-frequent previously-unsupported nodes render correctly. Details below retained for reference.

**Next milestone: v0.6.1 rendering fidelity — SCOPING (started 2026-07-13).** See the Current Milestone section at the top. Known items: TODO-01 (`todo_node`), MAN-01 (`:manpage:`), LEN-01 (CSS-length converter); plus a visual fidelity audit of the corpus PDF to discover-and-fix silent mis-render issues. The "13 post-GATE-02 debug sessions" once cited here were already-fixed *fatal* corpus bugs (see the Current State correction), not open polish work.

**Original v0.6.0 goal (for reference):** Compile a large real-world documentation set (Sphinx's own `doc/` tree) through the `typstpdf` builder with no fatal Typst errors, and render the most-frequent previously-unsupported docutils/Sphinx nodes correctly — driven by Issue #114.

**Target features:**
- **figure/image fatal-bug fix (Issue #114 core):** convert `px`/CSS length units to Typst-valid `pt` (or drop), and fix `:target:`-linked figures — emit `#figure(link(...)[#image(...)], caption: [...])` instead of the invalid `link(url, image(...))text(caption)` juxtaposition
- **`versionmodified` support** (×972 in Sphinx docs): `.. versionadded` / `versionchanged` / `deprecated`
- **empty-URL cross-reference handling** (×596): reduce silent plain-text degradation; resolve links where possible
- **autodoc signature nodes:** `desc_returns`, `desc_signature_line`, `desc_inline`, `desc_optional` (complementing the existing `desc_signature` / `desc_content` support)
- **other high-frequency nodes:** `footnote` / `footnote_reference`, `transition`, `topic`, `line` / `line_block`
- **graceful degradation** for graphical/out-of-scope nodes (`graphviz`, `inheritance_diagram`): warn without aborting the compile — full support out of scope

**Carried-forward deferred items (still v2, not in this milestone):**

- **CFG-01** (was FWD-03): user-configurable `@preview` package versions
- **XOS-01**: extend `docs-pdf` CI coverage to macOS and Windows

## Requirements

### Validated

<!-- Existing capabilities inferred from the mapped codebase. -->

- ✓ `sphinx-build -b typst` builder: reST → Typst markup (`.typ`) — existing
- ✓ `sphinx-build -b typstpdf` builder: Typst → PDF via typst-py — existing
- ✓ Visitor-pattern translator covering headings, paragraphs, inline markup, code blocks, tables, figures, lists, references, admonitions, math (mitex) — existing
- ✓ Template engine: default template, custom templates, Typst Universe (`@preview/*`) package support — existing
- ✓ Master vs. included document handling (`#include()`), image/asset copying, nested directory preservation — existing
- ✓ i18n scaffolding (sphinx-intl), full pytest suite (~400 tests), tox-based lint/typecheck/coverage, GitHub Actions CI + docs + release workflows — existing
- ✓ Runtime dependencies pinned to a reproducible known-good set (typst 0.14.9, `sphinx<9`, `docutils<0.22`); `uv.lock` regenerated and committed; tree lint-clean (`black`/`ruff`) — Validated in Phase 1
- ✓ Every CI job green across the full 3-OS × Python matrix (12 test lanes + lint/type-check/coverage/build/integration) and `docs.yml` end-to-end incl. the multi-language PDF-copy step, confirmed by an observed Actions run — Validated in Phase 2 (CI run 28702240846)
- ✓ The 3-way `@preview` version sync (`writer.py`, `template_engine.py`, `templates/base.typ`) guarded by an automated test that fails CI loudly on desync — Validated in Phase 2
- ✓ Supported Python range modernized to 3.10–3.13: `requires-python>=3.10`, 3.9 dropped / 3.13 added across pyproject classifiers, tox `env_list`, and the CI matrix; black/ruff/mypy target-versions aligned to the 3.10 floor; `uv.lock` regenerated minimal-diff — Validated in Phase 3 (green ci.yml run 28709253590 + docs.yml run 28709253571 on PR #104; all four 3.13 lanes + lint green)
- ✓ Dev tooling floors modernized with guard ceilings (`pytest>=8.4,<10`, `mypy>=1.13,<3.0`, `black>=26,<27`, `ruff>=0.15,<0.16`, `tox>=4.56,<5`, `tox-uv>=1.35,<2`) across pyproject.toml + tox.ini; artifact actions bumped to node24 (upload-artifact@v7 / download-artifact@v8); stale `Test Python 3.9` required-check removed from main protection — Validated in Phase 4 (green ci.yml/docs.yml on PR #105)
- ✓ Durability guardrails installed: `uv sync --locked` at all 9 sites (DUR-01 lockfile-currency gate), standalone weekly+dispatch `drift.yml` forward-drift detector with deduplicated issue reporting + least-privilege perms (DUR-02), `sphinx-typst-stack` Dependabot group scoped to the runtime trio (DUR-03), README CI status badge (DUR-04); `softprops/action-gh-release` @v2→@v3 node24 bump — Validated in Phase 5 (merged PR #106 green: ci.yml run 28730645396 + docs.yml run 28730645381; drift.yml validated post-merge via workflow_dispatch run 28730876125; drift-check confirmed absent from main's required checks)
- ✓ Runtime pins raised forward to the v0.5.0 target ecosystem: `sphinx>=9.1,<10` (FWD-01), `docutils>=0.21,<0.23` (PIN-01, resolves 0.22.4), Python floor raised to 3.12–3.13 across all 21 declaration sites — pyproject `requires-python`/classifiers, tox `env_list`, the ci/docs/release/drift workflows, and black/ruff/mypy target-versions (PIN-02); `uv.lock` regenerated + `uv sync --locked` green (PIN-03). The extension imports and registers both builders under Sphinx 9.1 and `sphinx-build -b typst` builds green; `typst` intentionally left `>=0.14.1,<0.15` (Phase 7). All work on `release/v0.5.0`, `main` untouched — Validated in Phase 6 (7/7 must-haves; 06-VERIFICATION.md)
- ✓ typst raised to `>=0.15.0,<0.16` (FWD-02) and the four bundled `@preview` packages bumped in lockstep across the 3 sync sites — mitex 0.2.4→0.2.7 (the actual `kai` fix, mitex CHANGELOG PR #201), gentle-clues 1.2.0→1.3.1, codly-languages 0.1.1→0.1.10, codly 1.3.0 unchanged (registry ceiling, empirically confirmed to compile) (PKG-01/PKG-02/PKG-03); `uv.lock` regenerated (typst 0.14.9→0.15.0), `test_preview_version_sync.py` + full 402-test suite green, `black`/`ruff` clean. **The empirical `kai` gate is closed**: `tox -e docs-pdf` compiles to a 101-page PDF with zero `TypstError`/`unknown variable: kai` (verified by two independent real compiles) — Validated in Phase 7 (4/4 must-haves; 07-VERIFICATION.md)
- ✓ Green CI matrix observed + `kai`-class smoke guard + guardrails confirmed for v0.5.0: an all-green Actions run across the full 3-OS × Python 3.12–3.13 matrix (lint, type-check, coverage, build, integration ×2) plus `docs.yml` build-docs — 13/13 jobs green, observed on PR #112 (`release/v0.5.0 → main`, left **unmerged** per D-03 for Phase 10) (CI-01); a `typst compile` smoke test (`tests/test_preview_smoke_gate.py` + `tests/fixtures/preview_smoke/`) that exercises all four bundled `@preview` packages via real function calls — incl. a `.. math::` block routing through mitex, the exact path the historical `kai` break lived in and the one the admonition-only gate never invoked — and fails loudly on any `TypstError`, with a documented negative-control proving it catches the `unknown variable: kai` regression (CI-02); durability guardrails (`pyproject` ceilings `sphinx<10`/`typst<0.16`/`docutils<0.23`, `drift.yml`, `sphinx-typst-stack` Dependabot group) confirmed already correct — a verified no-op per D-06 (CI-03); stale `main` branch-protection `required_status_checks` reconciled (removed the non-existent `Test Python 3.10/3.11 on ubuntu-latest` contexts, kept core gates + ubuntu 3.12/3.13, other protection settings preserved). All on `release/v0.5.0`, `main` untouched — Validated in Phase 9 (8/8 must-haves; 09-VERIFICATION.md)
- ✓ v0.5.0 release *prepared* on `release/v0.5.0` (REL-01, version-fix half): `typsphinx/__init__.py` `__version__` is now single-sourced via `importlib.metadata.version("typsphinx")` (with a `PackageNotFoundError`→`"unknown"` fallback, retiring the stale `0.4.3`), `pyproject.toml` bumped `0.4.4`→`0.5.0` as the **sole** version literal, `uv.lock` regenerated in lockstep (`uv sync --extra dev --locked` green), a new independent `tomllib` drift-guard test added (`test_version_matches_pyproject_toml`, keeping the existing `test_setup_version_matches`), and a curated `CHANGELOG.md` `## [0.5.0]` entry added under the top `## [Unreleased]` (the single source for the eventual Release body). **Phase 10 was RE-SCOPED to prep-only (D-01/D-02):** no tag, no publish, no merge — the publish half (merge PR #112 → tag `v0.5.0` → `release.yml` → PyPI wheel+sdist + GitHub Release) is **DEFERRED to `/gsd-complete-milestone`**, mirroring the v0.4.4 precedent — Validated in Phase 10 (6/6 must-haves; 10-VERIFICATION.md; 413/413 tests green, black/ruff/mypy clean; `main` untouched, PR #112 left OPEN)
- ✓ The ten highest-frequency previously-dropped Sphinx nodes render as correct, compilable Typst (v0.6.0 Phase 12): `versionmodified` version directives as unboxed italic Sphinx-worded labels via a `visit_inline` classed-dispatch to the existing emphasis idiom (VER-01, ×972 in Sphinx docs, no `versionlabels` import); same-document `refid` cross-references — `:ref:` section anchors + `:term:` glossary refs (XREF-01, ×596) including a fatal `:term:` fix (bracket-wrap `<label>` anchor in `depart_term`); the autodoc `desc_*` signature sub-parts `desc_returns`/`desc_signature_line`/`desc_optional`/`desc_inline` (DESC-01..04); and the trivial structural nodes `transition`/`glossary`/`tabular_col_spec`/`abbreviation` (BLK-01/04/05/06) — all via pattern-reuse in `translator.py` with exactly one new state var (`_is_first_desc_signature_line`) and zero new `@preview`/runtime dependencies. Each of the four handler groups ships a real `typst.compile()` GATE-01 acceptance fixture (render-gate suite now 8 classes — 4 Phase-11 + 4 Phase-12 — all green; 375-test fast suite green; mypy/ruff/black clean) — Validated in Phase 12 (10/10 must-haves; 12-VERIFICATION.md)
- ✓ The load-bearing `visit_title`/`depart_title` dispatch generalized so `.. topic::` renders as a titled `clue` aside (D-01/D-02) and `.. contents::` renders box-less as a bold label above its Sphinx-resolved bullet list (D-05), with two currently-live `visit_title` fatals closed — the level-0 heading class (`max(1, section_level)` clamp, D-06) and the multi-child-title concatenation fatal (list-item separator idiom + `{...}` heading wrap, Pitfall-1); and `line`/`line_block` now render each line via a real `linebreak()` with a per-depth `h()` indent for nested blocks (D-03/D-04, BLK-03), fixing the prior "lines run together" baseline. Zero new `@preview`/runtime deps; the 3-way version-sync surface untouched. Proven by a combined GATE-01 real-`typst.compile()` acceptance fixture (`topic_line_block_render_gate`) covering topic + contents + address + poem + admonition-title regression in one PDF — the topic and contents titles each appear exactly once (count==1, no auto-outline leak), address/poem sentinels extract as separate lines, and `.. admonition:: Custom *Title*` renders correctly. Render-gate suite now 9 classes; full non-integration suite 393 green; ruff/black/mypy clean — Validated in Phase 13 (9/9 must-haves; 13-VERIFICATION.md; BLK-02/BLK-03)
- ✓ Footnotes render via Typst-native `footnote[...]` using a document-order doctree pre-pass (FN-01 — the one architecturally-new item of v0.6.0): `visit_document` builds an id→footnote-node index via `self.document.findall(nodes.footnote)` before body content is visited (`.traverse()` replaced with the non-deprecated `.findall()`, a Rule-1 fix under the repo's strict `DeprecationWarning` filter); `visit_footnote` raises `SkipNode` so no floating body is left at the docutils definition site; `visit_footnote_reference` emits the bracket-wrapped definition form `[#footnote({body}) <fn-id>]` on first citation (body rendered via the buffer-swap idiom, never `astext()`, skipping the leading `label` child) and the bare reuse form `footnote(<fn-id>)` on repeat citation, with a dangling-refid `logger.warning`+skip guard (a bodyless reuse is a real Typst fatal). Numbering owned by Typst-native auto-numbering (document order). The real-compile GATE-01 caught and closed a genuine fatal — the buffer-swap clobbered the outer paragraph's `in_paragraph`/`paragraph_has_content` separator state, aborting any footnote followed by trailing text — fixed with the file's own save/restore convention. Proven by the `footnote_render_gate` fixture + `TestFootnoteRenderGate` (SC#1–4: single-ref body-once, double-ref reuse-no-dup, inline-markup/special-char body, footnote-in-list-item) all green via one real `typst.compile()` per class; render-gate suite now 10 classes; full non-integration suite 402 green; ruff/black/mypy clean; the 3-way `@preview` version-sync surface untouched — Validated in Phase 14 (10/10 must-haves; 14-VERIFICATION.md; FN-01)

- ✓ Issue #114 figure/image fatal bugs fixed + graceful-degrade net + the standing real-compile gate (v0.6.0 Phase 11): `_convert_length_to_typst()` px→pt / CSS-length conversion wired into `visit_image` (FIG-01); figure caption buffer-swap + `:target:` `refid` branch so captioned/linked figures emit valid `#figure(link(...)[#image(...)], caption: [...])` (FIG-02); `graphviz`/`inheritance_diagram` render a bordered placeholder + one warning + `SkipNode` (DEG-01/02); and `tests/test_pdf_render_gate.py` established the `sphinx-build → typst.compile() → pypdf` acceptance-fixture pattern, discovering a third latent label-in-code-mode fatal in the process (GATE-01) — Validated in Phase 11 (11-VERIFICATION.md)
- ✓ Full-corpus validation — the milestone gate (v0.6.0 Phase 15): a real `sphinx-build -b typstpdf` of Sphinx's own full `doc/` tree compiles with no fatal `TypstCompilationError` (~14.4 MiB PDF, `build succeeded, 66 warnings, 0 errors`); residual `unknown_visit` warnings catalogued (`todo_node` ×10, `manpage` ×10) as next-milestone backlog; empty-URL warning count measured before/after the XREF-01 fix (delta 0 on this corpus, with an honest definition-side-vs-reference-side methodology note) via git-worktree isolation (GATE-02) — Validated in Phase 15 (15-VERIFICATION.md; 15-CORPUS-REPORT.md)
- ✓ The last two silently-dropped nodes render + the length converter generalized (v0.6.1 Phase 16): `.. todo::` renders as a gentle-clues `task()` box gated on `config.todo_include_todos` via `raise nodes.SkipNode` — mirroring every official Sphinx builder, so internal work-notes never leak into published output (TODO-01); the `:manpage:` role renders its literal page text italic via 100% delegation to `visit_emphasis`/`depart_emphasis` — no bespoke state machine, no linkification (MAN-01); and `_convert_length_to_typst` is wired into `visit_figure`/`depart_figure` (`:figwidth:`) and `depart_table` (`:width:` across `table`/`csv-table`/`list-table`) using the `block(width: ...)[...]` wrapper — the only Typst-valid way to apply a computed width to `figure()`/`table()` (LEN-01). Each ships a real-`typst.compile()` GATE-01 fixture (todo enabled/disabled, manpage ×3 contexts, figwidth px/%/unsupported-unit, table width); zero new dependencies; security threat register closed (7/7, 16-SECURITY.md) — Validated in Phase 16 (16-VERIFICATION.md; UAT 1/1 passed)
- ✓ The compiled Sphinx `doc/` corpus PDF visually audited against source, every silent mis-render catalogued (v0.6.1 Phase 17 — AUD-01): all 151 docnames of the Sphinx v9.1.0 corpus were rendered and cross-checked page-by-page against the `-b html` authority baseline, yielding a severity-rated catalogue of 15 systemic findings (1 high / 12 medium / 2 low), each with location (docname + node kind), a source-vs-output description, and out-of-scope degradations (graphviz/inheritance placeholders, non-included-doc xrefs) explicitly separated so the fix backlog targets only fidelity bugs typsphinx owns. Human-confirmed at the central 17-03 gate (D-01a: 14 accepted / 1 rejected, final severities signed off); the sole high-severity finding grouped by root cause into `FID-01a` and appended to REQUIREMENTS.md, with a medium/low Future-Requirements pointer. Five mechanical consistency checks PASS (`17-VALIDATION.md`) — verified via the human confirmation gate + downstream Phase 18 real-compile proof in lieu of a machine `VERIFICATION.md` (audit/docs phase)
- ✓ The audit's sole high-severity finding fixed + the closing regression gate (v0.6.1 Phase 18 — FID-01a/GATE-03): the wide-table glyph-collision + right-margin-clip bug (F12) fixed by emitting fr-weighted `columns: (Nfr, …)` from docutils colwidth in `depart_table` and injecting U+200B after `.`/`_` in in-table `raw()` content via `visit_literal` — proven by a new `wide_table_render_gate` collision-absence real-compile fixture that would fail without the fix (FID-01); then the full ~684-page Sphinx `doc/` corpus re-run through `-b typstpdf` fatal-free (689-page `index.pdf`, valid `%PDF` magic), the `unknown_visit` catalogue confirmed empty of `todo_node`/`manpage`, and the SC#4 invariant (zero new runtime deps, no `@preview` version bump, 3-way sync surface untouched) held (GATE-03) — Validated in Phase 18 (18-VERIFICATION.md)

- ✓ The 13 medium/low silent mis-render findings from the v0.6.1 audit fixed as one coherent `translator.py` series grouped by root cause — v0.6.2 (FID-02..FID-06 block separation Phase 19; FID-07..FID-09 signature token spacing Phase 20; FID-10..FID-14 inline-literal overflow / paragraph reflow / codly-wrapper leak / external-link styling / PEP-separator hover-title Phase 21), each pinned by a fail-pre-fix real-`typst.compile()` GATE-01 fixture
- ✓ `sphinx-build -b typstpdf` names the compiled PDF after the `typst_documents` target, not the source docname — v0.6.2 Phase 22 (PDF-01, Issue #117): one guarded `TypstBuilder._resolve_output_stem()` governs all three `.typ`/`.pdf` output-path sites; and a nested master (`api/index`) compiles with its `#include()`s and images intact because `finish()` compiles each master's own on-disk `.typ` at its real location — v0.6.2 Phase 22.1 (PDF-02)
- ✓ Dead/registered-but-inert config values eliminated and the broken Typst-Universe path repaired — v0.6.2 Phase 22.2 (CONF-01..CONF-03): `typst_output_dir` + `typst_author_params` deleted from every surface, the `typst_package`-alone path now compiles end-to-end (BUG-A..BUG-D fixed), locked by a standing config→output regression gate
- ✓ The `typstpdf` builder fails loudly instead of a silent successful build for a missing/malformed master, and the render gate no longer asserts on `typst-py`'s uncontracted error wording — v0.6.2 Phase 22.3 (WR-01/WR-02, resolved behavioral at discuss)
- ✓ README/CLAUDE.md/pyproject comments re-derived from measured behavior — v0.6.2 Phase 22.4 (DOC-01..DOC-05): unverifiable numeric claims removed rather than re-measured, configuration list marked explicitly partial and pointed at the real docs page, Status/methodology/capability claims corrected, Python-floor claims aligned to `>=3.12`; a `README`↔`pyproject` version-sync ratchet test added in Phase 23

- ✓ The registered-but-inert `typst_toctree_defaults` config value deleted from every user-facing + code surface (registration in `__init__.py`, README, `examples/advanced/`, a surgical excise from the orphan `docs/configuration.rst` — file kept for Phase 27) and its registration-only test file removed — v0.6.3 Phase 24 (CONF-05, dead-config sweep round 2 part B): pure grep-proven-inert removal (zero consumers in `translator.py`/`writer.py`/`builder.py`/`template_engine.py`), honest bar = grep-zero on the enumerated surfaces + green suite (519 passed / 0 failed) + extension imports & both builders register; `CHANGELOG.md:553` historical listing left intact (D-02); GATE-01 N/A (no config→output change) — Validated in Phase 24 (24-VERIFICATION.md, 5/5 must-haves)
- ✓ PR#98 (AlCalzone) captioned-table figure-wrap reimplemented against current `translator.py` — v0.6.3 Phase 25 (TBL-01/TBL-02): a captioned `.. table::` / `csv-table` / `list-table` emits `figure(table(...), caption: {...}, kind: table)` with native "Table N" numbering and no stray `heading()`, composed with the existing `:width:` `block(width:)[...]` wrap (D-04); the stale-`table_cell_content`-buffer caption-loss bug fixed at root (`del`, not a reset) so the 2nd-and-later table keeps its caption; and a single Typst `<label>` from `ids[0]` via deferred `_emit_id_anchors(skip_ids={ids[0]})` so `:numref:`/`:ref:` resolve with no double-anchor compile-fatal. Caption-less tables stay plain `table()`; `templates/base.typ` byte-unchanged and no `@preview` bump (D-01 / milestone invariant). Proven by 8 translator unit tests + a real-`typst.compile()` GATE-01 fixture (`TestCaptionedTableRenderGate`: 2+-table, caption+width, numref/ref-resolves, csv/list-table) and a durable fail-pre-fix proof (`TestCaptionedTablePreFixBasisFailureProof`); unit suite 116/116, fast suite 567 green — Validated in Phase 25 (25-VERIFICATION.md, 7/7 must-haves)
- ✓ `typst_elements` `papersize`/`fontsize` reach the template's `project()` (dead-config sweep round 2 part A) — v0.6.3 Phase 26 (CONF-04): a 100% Python-side fix — `writer.py` stops laundering `typst_elements` through the `sphinx_metadata` dict (and drops the now-dead `copyright` key), passing it as a separate `map_parameters(sphinx_metadata, typst_elements=...)` argument; `template_engine.py` gains a curated module-level `ELEMENTS_ALLOWLIST` (`papersize`→string, `fontsize`→raw) merged additively after the existing back-fill/`typst_authors` logic without disturbing the `if not self.typst_package` guard, a `RawTypst` frozen-dataclass marker emitted verbatim by a new `_format_typst_value` isinstance branch (checked before the `str` branch — avoids the double-formatting trap) so `fontsize` emits as an unquoted Typst length while `papersize` stays a quoted string, and a fail-loud `sphinx.errors.ExtensionError` on any unknown key naming it + listing supported keys. Copyright non-leak is structural (only `parameter_mapping` ∪ allowlist keys ever reach `project()`). `templates/base.typ` byte-unchanged (sha256 `1d27336…`, milestone invariant), zero new deps, no `@preview` bump. Proven by 10 new unit tests + four real-`typst.compile()` GATE-01 fixtures (positive papersize, positive fontsize SEPARATELY, unknown-key-aborts, copyright-non-leak) and a durable `TestPreFixBasisFailureProof` (undeclared-kwarg + leaked-copyright reconstructions), with a recorded manual red→green (3/10 RED without the fix); full suite 615 passed / 1 skipped / 0 failed — Validated in Phase 26 (26-VERIFICATION.md, 5/5 must-haves)
- ✓ Docs measured fidelity — every documented `typst_*` name matches a registered config value, the orphan config doc is gone, and config lives in ONE canonical place — v0.6.3 Phase 27 (DOC-06/DOC-07): the unreachable orphan `docs/configuration.rst` (489 lines, wrong package name `sphinxcontrib.typst`, in the dead root `docs/` tree with no `conf.py`) deleted together with its collateral test `tests/test_documentation_configuration.py` (11 functions that hard-asserted the orphan's existence — a research-caught trap the plan/discuss/scout missed; deleting the orphan alone would redden the suite); the 5 phantom names purged from `docs/source/user_guide/configuration.rst` (`typst_use_codly`/`typst_code_line_numbers` removed, the type-invalid `typst_author = (tuple)` "Simple Format" subsection deleted in favor of the dict "Detailed Format", `typst_papersize`/`typst_fontsize` rewritten as the working `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` leveraging Phase 26's CONF-04 allowlist — the only two legal element keys); the redundant "Available Configuration Values" `list-table` deleted from `docs/source/api/index.rst` (kept the `See :doc:` pointer so config is documented in ONE place), with `docs/locale/ja/LC_MESSAGES/api/index.po` + `user_guide/configuration.po` regenerated via the SCOPED two-file `sphinx-build -b gettext` (removed msgids left as inert `#~` obsolete, not hand-stripped). **SC#4's "anywhere under `docs/source/`" clause exposed a scoping gap the discuss/research/plan chain missed** — the same phantom codly names also lived in `docs/source/examples/advanced.rst` + `examples/basic.rst` conf.py snippets; removed there too (post-verify gap-closure `59bf66d`), so the registered-set cross-check is now clean across ALL of `docs/source/`. Docs-only → GATE-01 N/A; `base.typ` byte-unchanged, zero new deps, no `@preview` bump, 3-way version-sync surface untouched; the deletion-bearing branch was manually fast-forward-merged past the `worktree.cleanup-wave` deletion guard (D-13) after confirming the 2-file scope. Proven by grep-zero phantom + registered-set cross-check + green `docs-multilang`/`docs-pdf` (only the 1 pre-existing `translator.py` warning) + green suite (deleted test not collected, siblings green) — Validated in Phase 27 (27-VERIFICATION.md, 6/6 must-haves)
- ✓ Typst's typesetting language (`set text(lang:)`) follows Sphinx's `language` conf — v0.6.3 Phase 27.1 (CONF-07): added a `lang: "en"` parameter to `project()` in `templates/base.typ` and wired it to `set text(size: fontsize, lang: lang)` (the change is strictly 2 lines — within the scope of the 2026-07-25 invariant amendment; the 4 `@preview` packages' version strings, i.e. the 3-way sync surface, are unchanged); added `derive_typst_lang()` to `template_engine.py` (takes everything before the first `_`/`-`/`@` and lowercases it, accepting only via the ASCII-restricted `re.fullmatch(r"[a-z]{2,3}", head)` — because Python's `str.isalpha()` is Unicode-aware and returns `True` for CJK, so a `language` value written as a Japanese-language string (e.g. `language = "日本語"`, i.e. "Japanese" written in Japanese) would trigger a Typst hard fatal), `ELEMENTS_ALLOWLIST["lang"]`, and `TemplateResolution`/`resolve_template()`/`uses_bundled_default_template()`, which record the resolution source as a byproduct of the priority walk `load_template()` already performs (D-06 explicitly rejects a second, duplicate implementation of the priority logic); `writer.py` only auto-derives on the default-template path, pre-merging it **under** the user's `typst_elements` via a right-side-wins `effective_elements` union, so the explicit setting's priority is structural, not incidental (D-05). None of the 3 other paths — custom template / `typst_package` / `<srcdir>/base.typ` shadowing — receive any injection at all, so an existing user who has merely set `language` doesn't break with `unexpected argument: lang` (D-06). An unconvertible value warns and omits the parameter rather than aborting the build (D-03). SC#1 is proved as a split per D-07 — `ja` via a real compile plus the generated `.typ`'s `lang: "ja"` (font-independent), and the supplement's language-following behavior via `de` plus an NBSP-tolerant regex over pypdf-extracted text proving the presence of "Tabelle 1"/"Abbildung 1" and the absence of their English forms (bundling a CJK font binary was explicitly rejected, since CI's ubuntu runner's CJK font availability is unconfirmed). **The orchestrator found and fixed 3 defects after merge**: I001/N811 that slipped through because the executor couldn't run ruff inside its worktree (broke CI); code-review finding CR-01 (`typst_elements = None` aborted the build with a `dict | None` TypeError — a regression from before this phase, when `map_parameters()`'s `or {}` handled it; reproduced via a real `sphinx-build` and pinned with a `null_elements` fixture); and 5 docs-build-warning lines added by Plan 01's docstring (invisible to the executor from inside its own worktree — Plan 01's code wasn't present yet when Plan 02 took its baseline measurement). Real `typst.compile()` GATE-01: 21 module tests / 8 fixtures, with a durable pre-fix-basis proof; full suite 656 passed / 1 skipped / 0 failed, black/ruff/mypy clean, docs build back to the pre-phase baseline of 4 lines — Validated in Phase 27.1 (27.1-VERIFICATION.md, 12/12 must-haves, 5/5 SC)
- ✓ v0.6.3 released — v0.6.3 Phase 28 (prep, no requirement IDs) + the `/gsd-complete-milestone` publish: `pyproject.toml` bumped to 0.6.3 as the sole version literal with `uv.lock` in lockstep and `README.md:315` updated, a curated `## [0.6.3]` CHANGELOG entry (6 of 7 ledger IDs in 5 user-visible bullets; DOC-06 omitted per D-10; exactly 2 BREAKING labels), and the closing full-corpus regression gate run live on the post-bump tree (`1 passed in 12.87s`, valid `%PDF`, `unknown_visit` catalogue empty). SC#4 held as amended (zero new runtime deps, no `@preview` bump, `base.typ` diff confined to Phase 27.1's 2-line `lang` parameter); SC#5 scope fence held through prep, with the irreversible publish executed at milestone close
- ✓ Japanese documentation published on Read the Docs as a translation project of the English parent, serving actual Japanese prose behind RTD's own flyout (both directions owner-observed), from a separate `typsphinx-doc-translations` repository (13 relocated `.po` catalogs + submodule pin auto-advanced by an observed scheduled workflow), with the Japanese PDF proven glyph-correct against D-03's four-check bar including owner visual confirmation of the corrected artifact — v0.6.4 Phase 30.1 (I18N-01/I18N-03; 30.1-VERIFICATION.md `passed`, UAT 1/1, 26/26 threats closed)
- ✓ Every published documentation URL points at Read the Docs and resolves over real HTTP, with a standing advisory repo-wide link guard — v0.6.4 Phase 31 (DOC-09/DOC-10/CI-05): `.github/workflows/links.yml` (lychee; https/http only; `.planning/`, `CHANGELOG.md`, `tests/fixtures/` deliberately excluded; advisory — confirmed absent from required status checks) installed FIRST and proven by a recorded red negative-control run (run 30205112477: all 7 old-host README deep links flagged, `pyproject.toml` proven in-scan via a `--dump-inputs` diagnostic) before any rewrite per D-09 ordering; then `README.md` (incl. RTD's own build-status badge + the ja documentation link), `pyproject.toml` `[project.urls] Documentation`, and `.planning/codebase/INTEGRATIONS.md` (full Hosting/CI/Env refresh) repointed at `typsphinx.readthedocs.io`, every URL fetched live (200), guarded by `tests/test_no_stale_github_io_links.py` (4 tests; the retired host survives only in `CHANGELOG.md` by design); repo About → Website set to the RTD root (302→200 observed). Issue #119: close-reply drafted (`31-ISSUE-119-REPLY-DRAFT.md`), the close itself an owner-decided post-merge handoff to `/gsd-complete-milestone` (D-15 — not a gap). The one `verification: backstop` truth (a cancelled/superseded Link Check run leaves zero repository state) proven live in UAT: run 30267597698 cancelled 4 s after queue, full `git ls-remote` diff vs. pre-push baseline clean — Validated in Phase 31 (31-VERIFICATION.md `passed`, UAT 1/1)
- ✓ The bundled `examples/advanced` sample builds again, and bundled samples are now watched for `@preview` drift — closed at the v0.6.3 milestone close (not a phase): its `typst_elements` carried 5 keys outside the CONF-04 allowlist and its `_templates/custom.typ` sat three milestones behind on its `@preview` pins (`unknown variable: kai`); measurement showed `project()` declared neither `papersize` nor `fontsize`, so the template now declares `papersize`/`fontsize`/`lang` and drives its `set page`/`set text` from them. `tests/test_preview_version_sync.py` gained a check over `examples/**/*.typ` (red against the pre-fix file, green after). Verified by a real `sphinx-build -b typstpdf` producing a 248 KB PDF; full suite 657 passed / 1 skipped; black/ruff/mypy clean
- ✓ The hand-rolled multi-language publishing machinery is gone and the orphan doc pair is resolved — v0.6.4 Phase 30 (I18N-02/DOC-08): one deletion round removed `docs/build_multilang.py`, the language-switcher (`docs/source/_templates/page.html` + `custom.css` wiring), the six i18n/multilang `docs/Makefile` targets (D-12/D-13 — `docs/Makefile` back to the stock two-target skeleton), the `docs-multilang` tox testenv, `docs/locale/ja/` (13 `.po` + 13 `.mo`; the sole live copy now lives in `typsphinx-doc-translations`, existence-gated pre-deletion per PD-01), and the unreachable `docs/usage.rst`/`docs/installation.rst` orphan pair with their collateral tests; `docs.yml` repointed to single-language `tox -e docs-html` with `publish_dir` → `./docs/_build/html` (D-14 — the `peaceiris` deploy step itself survives for Phase 32's gated teardown); `docs/source/conf.py` cross-repo regions SHA-pinned unchanged so the ja RTD build is untouched. Deletion-guard manual merge landed as predicted. Proven by 30-EVIDENCE.md gates + UAT 3/3: docs.yml run 30269906943 green on milestone PR #124 (documentation-html artifact from `docs/_build/html`), live `/en/latest/` shows zero switcher/`custom.css` markup (RTD build 33763874), and neither Furo READTHEDOCS-gated sidebar slot renders on the hosted site (open question resolved: no ad placement) — Validated in Phase 30 (30-VERIFICATION.md `passed`, UAT 3/3, 17/17 threats closed)
- ✓ v0.6.4 release prep complete, publish handed off — v0.6.4 Phase 33 (REL-02 prep half; prep-only, no irreversible action): `pyproject.toml` bumped to 0.6.4 as the sole version literal with `uv.lock` self-pin in lockstep (1 insertion / 1 deletion, zero transitive drift) and `README.md` Status → `Stable (v0.6.4)` in the same commit; a curated `## [0.6.4] - 2026-07-28` CHANGELOG entry with zero BREAKING labels (D-01 — no packaged behavior changed; the github.io-404-no-redirect and browser-language-redirect losses disclosed in the Removed body) and a `### Verified` section held to three `git diff`-mechanically-provable invariants (D-03), plus the tail link-block rollover; the four top-level `.planning/` documents (PROJECT/ROADMAP/MILESTONES/STATE) translated JA→EN meaning-preserving (D-05 — byte-identical requirement-ID census, heading/table-row counts unchanged; human UAT meaning-preservation spot-check passed); `33-RELEASE-EVIDENCE.md` re-verified the RTD `Documentation` URL live (302→200, timestamped 2026-07-27T21:15:32Z) and re-asserted the three milestone invariants over the full re-measured 279-commit `main..HEAD` diff with a non-empty positive control beside the empty `typsphinx/` diff; `33-HANDOFF.md` enumerates the 8 publish/owner-manual items with owner and ordering and proves via empty `git tag -l v0.6.4` / `git ls-remote --tags origin v0.6.4` that no tag or publish occurred — REL-02's publish half (PyPI + `/en/stable/`+`/ja/stable/` serving the release) structurally requires the tag and executes at `/gsd-complete-milestone` — Validated in Phase 33 (33-VERIFICATION.md `passed`, UAT 1/1, 14/14 threats closed)

- ✓ English documentation live on Read the Docs from `.readthedocs.yaml`, with the RTD-served PDF proven to be `typstpdf`'s own artifact — v0.6.4 Phase 29 (RTD-01/RTD-02/RTD-03/RTD-04): raw build log proves in-repo install; `@preview` egress resolved to Branch A; D-12 content comparison (93==93 pages, byte-identical text, CJK font present); root URL owned at Default Version `latest` (29-VERIFICATION.md `passed`)
- ✓ GitHub Pages torn down irreversibly behind a freshly re-taken RTD-is-serving gate — v0.6.4 Phase 32 (CI-04): deploy step + permissions removed with the tag-time Release step byte-unchanged, `origin/gh-pages` deleted with `ls-remote` proof, github.io 404 observed live, two guard tests with a recorded red negative control (32-VERIFICATION.md `passed` 12/12)
- ✓ v0.6.4 published at milestone close: PR #124 merged, `v0.6.4` tagged, `release.yml` → PyPI + GitHub Release; Issue #119 closed with the owner-approved reply; milestone audit `passed` 13/13 — v0.6.4 close (2026-07-28)

- ✓ Inline math immediately following text compiles on both emission paths — v0.6.5 Phase 34 (MATH-01, backlog 999.1): root-caused by measurement as a **scope gap, not a visit-ordering bug** — `visit_math` called only `_add_paragraph_separator()`, which is deliberately a no-op inside a list item (`visit_paragraph` never sets `in_paragraph` there) and inside the five code-mode concat contexts, so math emitted after a sibling juxtaposed with zero separator characters and `typst.compile()` rejected the document. Fixed by applying the existing, already-tested `visit_literal` pattern to the one visitor pair never retrofitted: `visit_math` now participates in all three separator protocols (paragraph / code-mode concat / list-item) and `visit_math_block` in the list-item half only (D-01 — a block node is never a concat-context sibling, so emitting a `+` operator around it would be wrong). Zero new helpers; the mitex/native branch, `_convert_latex_to_typst` call, and label-anchor emission are byte-unchanged. Pinned by a real `typst.compile()` GATE-01 fixture (`tests/fixtures/inline_math_after_text_render_gate/` + `tests/test_inline_math_after_text_render_gate.py`) covering list item / field body / def-list term / list-item block math / top-level control on both the mitex default and `-D typst_use_mitex=0` native paths, **recorded RED against the unfixed translator** with the verbatim `TypstError: expected semicolon or line break` captured, then GREEN — and independently re-reproduced at verification time by restoring the pre-fix translator and re-observing the identical RED. Non-regression proven by set-comparison against the pre-fix baseline (NEW-failures empty, FIXED = the two gate tests, CARRIED empty; 649 passed / 1 skipped), the full-corpus `-b typstpdf` gate fatal-free, a 93-page docs dogfooding PDF, and direct visual inspection of the rendered pages. Zero new runtime dependencies; the four-surface `@preview` version-sync surface untouched — Validated in Phase 34 (34-VERIFICATION.md `passed` 5/5; 34-GATE-EVIDENCE.md)

- ✓ v0.6.5 released — v0.6.5 Phase 35 (REL-03 prep half; prep-only, no irreversible action) + the `/gsd-complete-milestone` publish: `pyproject.toml` bumped to 0.6.5 as the sole version literal with `uv.lock` in lockstep (a 1-line self-pin, zero transitive drift) and `README.md` Status updated; a curated `## [0.6.5] - 2026-07-29` CHANGELOG entry (lead paragraph + one `### Fixed` bullet + three `### Verified` bullets, no BREAKING — no packaged API changed) with the tail link block rolled over; Phase 34's three test-side review Warnings closed by a Construct G fixture addition plus four exact-string assertions across both emission paths, each proven able to fail by a one-character perturbation, with zero `typsphinx/` change; and `35-RELEASE-EVIDENCE.md` proving the post-bump tree green across seven live runs (full pytest 649/1, black/ruff/mypy, the full-corpus `-b typstpdf` gate, and both `tox -e docs-html` / `docs-pdf` dogfooding builds per D-12), the three milestone invariants mechanically over the `eb696bb`-anchored full diff with a positive control proving the pathspec works, and the scope fence held (empty `git tag -l v0.6.5` and `git ls-remote --tags origin v0.6.5`, re-observed independently at two moments). The publish half — merge to `main`, tag `v0.6.5` → `release.yml` → PyPI + GitHub Release, plus the standing second tag on `typsphinx-doc-translations` — executed at the milestone close per `35-HANDOFF.md`'s six-item checklist — Validated in Phase 35 (35-VERIFICATION.md `passed` 5/5) + v0.6.5 close (2026-07-29)

- ✓ The shared-emission seam is cleaned up so later v0.7.0 restyling phases have independent handlers, and block math stops stacking a redundant break — v0.7.0 Phase 36 (ADM-06, MATH-02): `visit_desc_signature`/`depart_desc_signature` and `visit_rubric`/`depart_rubric` no longer borrow `visit_strong`/`depart_strong`'s body via a dummy `nodes.strong()` node; each now inlines that body verbatim, so Phase 37 (signature typography) and Phase 39 (rubric nesting) can restyle independently. The triplication is the recorded decision (D-01), not an accident — no shared helper, and branches unreachable from `desc_signature`/`rubric` were kept rather than pruned (D-03), because the binding constraint was a zero byte-delta. The decoupling's acceptance was **byte-identity, not judgement**: a combined-construct fixture's emitted `.typ` is byte-identical across the decoupling commit alone, proven by a diff of two real `sphinx-build -b typst` runs at named commits, with the golden captured **before** any decoupling edit existed (`git log --follow` shows exactly one commit on that path, predating the change — so the proof is not circular). The SC#1 delegation census dropped 6 → 2 sites, the two survivors being `visit_literal_strong`/`depart_literal_strong` (out of scope, Phase 38). MATH-02 closed by one statement in `visit_math_block` (`list_item_needs_separator` `True` → `False`, D-06): that handler already emits its own unconditional `"\n\n"`, so arming the shared flag stacked a second separator; clearing rather than merely not setting is what makes the `:label:` path correct, since `_emit_id_anchors` arms the flag before the math is emitted. Recorded RED structurally on both the mitex and native paths and both the plain and `:label:` forms, with the GREEN strings derived **by hand** from the recorded RED strings (never regenerated from the fixed code), plus a PDF-text invariance guard comparing extracted text per emission path against its own committed baseline — never PDF bytes, which are unsatisfiable because Typst embeds `CreationDate`/`ModDate`. Full suite 653 passed / 1 skipped / 0 failed with the post-change failing-node-ID set empty and equal to the recorded pre-change set; `pyproject.toml`/`uv.lock` and all `@preview` version-sync surfaces unchanged — Validated in Phase 36 (36-VERIFICATION.md `passed` 4/4; 36-GATE-EVIDENCE.md; code review 0 critical)

- ✓ An API signature reads as a signature — v0.7.0 Phase 37 (SIG-01..SIG-09): bold monospace `desc_name` and `desc_annotation`, regular-weight monospace `desc_addname`, italic-proportional parameters distinct from the name, monospace delimiters, a real `→` glyph for `desc_returns`, no right-margin overflow, exactly one break between sibling signatures, and no page break between a signature and its body's first line. Notable measurement that inverted the phase's own premise: the corpus (1,445 real `desc_signature` nodes) has a 311-char worst-case signature and a 143pt widest unbreakable token against a **453.54pt** production column read from Typst's own `layout()`/`measure()` — nothing in the real corpus overflows, so SIG-07's RED fixture had to be a synthetic ~90-char dotted identifier and the corpus worst case became a non-regression control instead. Validated in Phase 37 (37-VERIFICATION.md `passed` 9/9, `behavior_unverified: 0`)

- ✓ The page shows structure: description bodies indent inside their own signature, nesting accumulates so class membership is visually recoverable, and field lists follow the same single constant — v0.7.0 Phase 38 (IND-01..IND-05, FLD-01..FLD-03): one named `SHARED_INDENT_STEP = "2.5em"` (`typsphinx/translator.py:29`) drives `desc_content` (via `par(hanging-indent:)` plus a `pad(left:)` wrapper) and `field_list`, with no second independent indent literal anywhere in `typsphinx/`; a nested member's own signature aligns with its parent's body rather than taking a further step, and the depth counter resets across sibling `desc` nodes so depth cannot leak. Field bodies gained the reference's own recipe: a multi-value body renders as a bulleted list while a single-value body stays inline prose, and a parameter's name/type carry monospace treatment (`strong(raw(…))` / `emph(raw(…))`) distinct from the plain-bold proportional field label — reached only through Typst's `raw(...)` primitive, never by naming a font family, which would silently shadow the `ja` build's CJK fallback. **IND-04's scope is narrower than the roadmap's original prose and that was ruled deliberate, not a miss:** `block_quote` is an intentional non-consumer keeping Typst's own `quote(block: true, …)` default spacing (11.0pt vs. the constant's 27.5pt; wrapping it would land at 38.5pt and destroy `visit_attribution`'s right-aligned attribution), so at UAT the owner corrected the ROADMAP/REQUIREMENTS wording rather than the code (D-04, 38-UAT.md test 1). One gap-closure round was needed: FLD-02's inline single-value body held at top level but regressed inside a bullet/enumerated list item because `visit_paragraph` tested `in_list_item` before `_field_body_unwrapped_paragraph` — found independently by both the code review and the verification pass, closed by plan 38-09. Validated in Phase 38 (38-VERIFICATION.md `passed` 8/8 after re-verification, 0 gaps remaining; 38-SECURITY.md 20/20 threats closed; full suite 706 passed / 0 failed)

- ✓ Admonitions, the generic `.. admonition::` directive, `topic`, and `rubric` are redesigned to the same standard — v0.7.0 Phase 39 (ADM-01..ADM-05): the ten admonition types now land in the reference's four colour buckets rather than an ad-hoc spread — `note→info`, `warning`/`caution`/`important`→`warning`, `tip`/`hint`/`seealso`→`tip`, `error`/`danger`/`attention`→`error` — with `seealso` and `attention` the two types that moved (ADM-01, ADM-02), a generic `.. admonition::` rendering as a styled `notify` box carrying its own custom title (ADM-03), and `topic` routed to `abstract` on its non-`contents` branch. Static titles are sourced once from `sphinx.locale.admonitionlabels` instead of hand-written literals and pass through the shared `escape_typst_string` boundary, so a translated locale string cannot break the emitted Typst. **ADM-04 is the milestone's only `[V]` requirement and was closed by owner sign-off, not by a grep** (`39-ADM04-SIGNOFF.md`): against a real desaturated render of a six-box probe compiled from post-fix code, the owner judged the kinds distinguishable **by icon shape** — exactly the channel ADM-04 names — and recorded, as an accepted caveat rather than a defect, that **title-band luminance is uniform and carries no distinguishing signal** (D-06's measured 5.4-point band spread is too narrow to serve alone). No styling change was made, neither fallback lever (per-bucket border thickness, per-bucket header-band colour) was chosen, and no todo was filed — the caveat is a recorded property of the design, not latent work. Two folded rubric defects were closed in the same phase: `visit_rubric`/`depart_rubric` gained their own `_rubric_was_*` save slots, ending the document-wide `par()`-wrapper loss that a nested inline-markup rubric caused by clobbering `visit_strong`'s shared slots (the D-02 leak Phase 36 deferred here), and the double-counted id-anchor separator was removed. Full suite 763 passed / 1 skipped / 0 failed; the full-corpus `-b typstpdf` gate was **re-run for real** (tag `v9.1.0`, PASSED — not a skip); milestone invariants held (no new runtime dependency, `@preview` count stays 4, gentle-clues pin unchanged at `1.3.1`) — Validated in Phase 39 (39-VERIFICATION.md `passed` 5/5; 39-GATE-EVIDENCE-01..04.md; 39-TEST-CENSUS.md re-measured, matching both the discussion-time and planning-time censuses exactly; code review 0 critical / 1 warning / 2 info)

- ✓ `citation` / `label` / `citation_reference` render as a labelled reference list with working `[Label]` → definition links and back-references, and `examples/charged-ieee`'s citation syntax is restored — v0.7.0 Phase 40 (CIT-01..CIT-06): a document containing a citation used to abort the Typst compile outright, because `citation` and `label` had no handler and the emitted `.typ` juxtaposed two code-mode expressions. The definition side is now `visit_citation`/`depart_citation`/`visit_label`, rendering a run of consecutive definitions as ONE `grid(columns: (auto, 1fr))` so every entry body starts past the widest label in that run; a paragraph between two definitions breaks the run into two independently-aligned grids while a sibling that emits nothing (an RST comment, a system message) does not. Back-reference markers follow docutils' own `backrefs` order and its own same-document scope, with `len(backrefs) == 1` putting the back-link on the bracketed label itself and `>= 2` appending a comma-separated marker list; an uncited definition still renders, with a plain non-linked label — the deliberate inverse of Phase 14's footnote policy, which drops an unreferenced footnote. Every label routes through the existing `_namespace_label`/`_sanitize_label` pair, namespaced by the citation node's OWN `docname` rather than `_current_docname()`, which is what makes a key defined in two documents produce two non-colliding anchors instead of a duplicate-label compile fatal; no second escaping routine was introduced. **SC#3 was amended mid-phase against measurement, not waived** (D-08/D-09, plan 40-02): docutils populates `backrefs` with same-document citing sites only — Sphinx's own HTML builder has the same limitation and its LaTeX builder renders no back-references at all — so the roadmap's original "back-references to every citing location" was narrowed to that scope with a dated Roadmap Evolution bullet, and a cross-document citing site gets a working forward link and no back-reference. **The phase's durable lesson is about the gate, not the handlers.** CIT-01 was the milestone's sole requirement where "does not compile" was available as the RED state, and that RED was captured verbatim against a named commit before any handler existed (`40-GATE-EVIDENCE-01.md`), together with a second, independently-isolated pre-fix failure shape: a citation nested in a list item aborts at Typst's *semantic* pass with a missing-label error, not at the syntax fatal. After the handlers landed, four of nine gate selectors stayed RED — and all four turned out to be defects in the gate module itself, not in the translator. A separate gap-closure plan (40-05) repaired six such assertions: two helpers calling `env.get_and_resolve_doctree` without `tags=` (raising `RemovedInSphinx11Warning`, which this project's own `filterwarnings` escalates to an error before any citation assertion runs); a sentinel-column measurement copied from `test_rubric_indent_invariance.py` that returns the *line's* leading whitespace rather than the *marker's* column, which in a citation grid reads the label's column and could therefore never pass in either direction; a concat sub-check demanding a bare `link(` that contradicts D-14's own bracket-wrap; an attached-anchor helper recognising only the `<label>` shorthand and not the `#label("…")` function form the code actually emits; and a `\(\d+\)` single-backref guard that false-positived on body prose while never matching the real marker shape. **Because "edit the test until it passes" is indistinguishable from laundering a gate, the corrected module was re-proved able to fail**: restored over the pre-fix translator it goes 9/9 RED, verified independently three times (by 40-05, by the orchestrator, and by the verifier), and no observed measurement or label token was transcribed into the test file — the amendments live in Section 8 of `40-GATE-EVIDENCE-01.md`, with Sections 1–7 byte-unchanged. CIT-05 got its own RED-to-GREEN gate on real shipped content at zero test cost: both samples were restored to git blob `82831eb0` (byte-identical to each other again, so template wiring is once more their only intended difference) and `tests/test_examples_charged_ieee_gate.py` was re-run, never edited, across the whole phase — Validated in Phase 40 (40-VERIFICATION.md `passed` 5/5 SC + 6/6 requirements; full suite 783 passed / 1 skipped / 0 failed; full-corpus `-b typstpdf` gate re-run for real and PASSED, not skipped; zero new runtime dependencies, `@preview` count still 4; code review 0 critical / 3 warning / 1 info)

- ✓ Citation degradation paths fail closed instead of emitting a dangling `link()` — v0.7.0 Phase 40.1 (INSERTED; no new REQ-IDs — hardens code delivered under CIT-01/CIT-03/CIT-04 and closes `40-REVIEW.md`'s three warnings): a backref whose citing `nodes.reference` cannot be found in the resolved doctree (an `.. only::`-pruned citing site) is skipped rather than emitting a label target nothing defines, which previously aborted the whole-document compile; `_citation_run_neighbour`'s inert-sibling skip list widened to treat an ids-less `nodes.target` as inert, closing a silent structural regression that split one intended run of definitions into two independently-aligned grids; and the duplicated anchor-eligibility judgement collapsed into one shared silent predicate (`_ReferenceAnchorDecision` / `_reference_anchor_decision`) consulted by both `visit_reference` and the backref loop, returning the anchor label itself so link target and attached anchor come from one expression. Each RED's provenance is recorded per warning rather than assumed — WR-01 against a real `sphinx-build`, WR-02/WR-03 against directly-assembled doctrees with the exhausted real-build attempt lists and the reason each shape is unconstructible — and `40.1-NONREGRESSION.md` §4 is the change-site → RED manifest Phase 41's SC#4 sweep reads as a cross-phase contract — Validated in Phase 40.1 (40.1-VERIFICATION.md `passed` 5/5)

- ✓ **REL-04 — validated at the v0.7.1 close (2026-08-11), after carrying unmet through v0.7.0.** The real `v0.7.1` tag push on merge commit `48bf135` fired `release.yml` run `31462027486`, whose `create-release` job completed **success** — the first end-to-end exercise of this workflow file since the missing `astral-sh/setup-uv` / `Set up Python` steps were added to `main`. The published body was measured, not assumed: lines 1–77 are byte-identical to `scripts/extract_changelog_section.py 0.7.1`'s stdout (`diff` clean), followed by an Installation block and GitHub's auto-generated PR list; a `git log --pretty` commit-dump shape matches **0** lines. The v0.7.0-era history that made this requirement carry is retained below. — Validated at the v0.7.1 milestone close

- ⚠ *(v0.7.0-era record, superseded by the line above — retained for the history of why REL-04 carried.)* The GitHub Release body sourced from the curated `## [X.Y.Z]` CHANGELOG section — v0.7.0 Phase 41 built it, the v0.7.0 close proved it does not yet work end to end. Phase 41 (plan 41-01) delivered a stdlib-only, positional `## [X.Y.Z]` extractor (`scripts/extract_changelog_section.py`), pytest-covered, wired into both `release.yml` jobs, with the ~296-line `git log --pretty` dump **removed rather than fenced**; extraction is positional (first `^## [<version>]` line, terminated by the next `^## [` or EOF) so the two identically-named `## [Unreleased]` headings cannot make a numeric version order-dependent, and a missing or empty section exits non-zero rather than shipping an empty body. The same phase converted every shell-context `${{ }}` interpolation in `release.yml` to `env:` passing (code review CR-01). **What the first real tag push exposed:** the `create-release` job calls `uv run …` but has no `astral-sh/setup-uv` step — `validate` and `build` both do, `create-release` never needed uv until REL-04 wired the extractor into it. Release run `30848860064` went `validate` ✓ → `build` ✓ → `publish-pypi` ✓ → `create-release` ✗ (`uv: command not found`, exit 127), leaving the empty-bodied PDF-only release `docs.yml` creates. The v0.7.0 body and its missing wheel/sdist assets were repaired by hand at the close, so the published artifact matches the requirement — the automation has still never produced it. `release.yml` gained the missing steps on `main` after the release; REL-04 closes when a real tag push exercises it end to end.

- ✓ A captioned table immediately preceded by a standalone target no longer drops the target's label — v0.7.0 Phase 42 (TBL-03, promoted out of backlog 999.2 on 2026-08-03 *after* Phase 41 had already closed — the first requirement this project has added to an already-complete milestone): `depart_table`'s trailing `_emit_id_anchors` call ran *after* `self.in_table = False` had already been reset, so a captioned table's propagated-target anchor was written into a buffer that then got discarded — the surviving reference to that id had nothing to resolve against and the compile aborted on a dangling label. Fixed by moving the call past the reset, gated on a `was_captioned` boolean captured pre-reset. The defect is **table-only**: a dedicated figure-side fixture plus a 7-method regression gate proved the figure path was already correct and stays green with zero production changes, and a full static sweep of all 21 `_emit_id_anchors` call sites in `translator.py` found exactly one misrouted site (this one). Keeps the classic `TypstError` RED — the milestone invariant #4's second exception alongside CIT-01 — Validated in Phase 42 (42-VERIFICATION.md `passed` 6/6; 42-GATE-EVIDENCE-01..05.md)

- ✓ v0.7.0 released — v0.7.0 Phase 41 (REL-05 prep half; prep-only, no irreversible action) + the `/gsd-complete-milestone` publish: `pyproject.toml` bumped to 0.7.0 as the sole version literal with `uv.lock` and `README.md` in lockstep and `typsphinx.__version__` reporting it; a curated `## [0.7.0]` CHANGELOG entry (lead paragraph + Added/Changed/Fixed/Verified) with the tail link block rolled over; the post-bump tree proven green live (805 pytest passed / 1 skipped, black/ruff/mypy clean, the full-corpus `-b typstpdf` gate genuinely executed and PASSED, both docs dogfooding builds green including the `ja` build's four-check glyph bar signed off verbatim by the owner); and all three milestone invariants proven mechanically over the SHA-anchored full milestone diff. The scope fence was proven held by two independent empty-tag probes 2m44s apart, and the seven-item `41-HANDOFF.md` checklist recorded exactly what the close would execute. The publish half — merge to `main`, tag `v0.7.0` → `release.yml` → PyPI + GitHub Release, plus the standing second tag on `typsphinx-doc-translations` — executed at the milestone close — Validated in Phase 41 (41-VERIFICATION.md `passed` 5/5) + v0.7.0 close (2026-08-04)

- ✓ Nested tables and figures survive nesting, and an empty-titled caption still anchors — v0.7.1 Phases 43 + 44.1 (TBL-04, TBL-05, FIG-01, TOC-01): `translator.py`'s table state moved from a set of scalars to a snapshot save/restore stack (`_push_table_state`/`_pop_table_state`), so a table nested in a `list-table` cell no longer replaces the outer table's cells, column count, or caption — closed across all seven measured shapes with a recorded RED baseline and a two-build byte-invariance proof. A `visit_legend`/`depart_legend` pair plus `_push_figure_state`/`_pop_figure_state` closed the figure-in-figure case (previously a hard `TypstError` that also dropped the outer caption), and the phase's own code review caught a legend-in-legend state leak that a real `List[Tuple[bool, bool]]` stack fixed. `depart_table`'s single "is this captioned?" check split into independently-gated RENDERING and ANCHORING decisions, so a title rendering to the empty string still emits its ids. Separately, `visit_title` emits relative rather than absolute depth, so a toctree'd document's headings nest one level deeper and the PDF outline stops being flat — Validated in Phases 43 and 44.1

- ✓ The documented configuration actually takes effect — v0.7.1 Phases 44, 44.2, 45.1 (CONF-08, CONF-09, CONF-10, CONF-11, CONF-12, DOC-13, BLD-01): `typst_documents` unset now derives a default from `root_doc`/`project`/`author` mirroring `sphinx.builders.latex.default_latex_documents`, so the Quick Start produces a real PDF instead of exiting 0 with a warning and zero output (measured on before/after builds from throwaway worktrees at named commits), with a target-name collision falling back to the docname with a WARNING rather than silently destroying content. An explicit entry's `[2]` title and `[3]` author now reach the compiled PDF's metadata (proven through `pypdf`), backed by a 27-test precedence matrix. The published custom-template parameter contract was rewritten onto the nine parameters typsphinx actually passes and locked with a RED-proved gate; a declared `typst_template_function` `params` dict became the complete parameter set; the auto-derived `lang` reaches every non-package template route; `typst_authors` was removed outright with no deprecation shim; and a non-`str` docname fails through the aggregate `failures` list instead of a raw `TypeError` — Validated in Phases 44, 44.2, 45.1

- ✓ The published changelog page stopped being two years stale, and the local toolchain works — v0.7.1 Phases 45 + 45.2 (DOC-11, DOC-12, QUA-01, QUA-02, QUA-03, QUA-04): `docs/source/changelog.rst` now renders live from repo-root `CHANGELOG.md` via myst-parser's `include::` `:parser:` mechanism, closing the drift channel at its source rather than backfilling it once; `CHANGELOG.md` gained the missing v0.4.4 release and was deduplicated to one `[Unreleased]` heading, with a real-build gate proving all 12 previously-missing releases render clean on both `-b html` and `-b typstpdf`. Renaming `tox-uv` to `tox-uv-bare` dropped the bundled generic-linux `uv` wheel whose ELF NixOS cannot exec: all four tox environments now provision with no `TOX_UV_PATH` override, and the full pytest suite under an outer `uv run pytest` went from 45 failures to zero — Validated in Phases 45 and 45.2

- ✓ Absolute image URIs from Sphinx's image converter or downloader no longer abort the compile — v0.7.1, Issue #130 / PR #131 by @christianwehe, this project's first external contribution. Building with `sphinxcontrib.rsvgconverter`, `sphinxcontrib.inkscapeconverter`, `sphinx.ext.imgconverter`, or a downloaded remote image previously copied no image at all and made the Typst compile abort with "file not found" — Validated via the merge into the v0.7.1 milestone branch in Phase 46

- ✓ v0.7.1 released — v0.7.1 Phase 46 (REL-06 prep half; prep-only, zero irreversible action) + the `/gsd-complete-milestone` publish (REL-06 publish half + REL-04): the tree bumped, the `## [0.7.1]` CHANGELOG entry curated with all four breaking changes called out, the post-bump tree proven green on a live CI run rather than a local one (12/12 jobs, run `31458368833`), and a seven-item handoff checklist written. The publish then executed: PR #132 merged with 15/15 checks green, tag `v0.7.1` on `48bf135`, release run `31462027486` completing `validate` → `build` → `publish-pypi` → `create-release` all success, PyPI `typsphinx 0.7.1` live, and the standing second tag pushed on `typsphinx-doc-translations` — Validated in Phase 46 (46-VERIFICATION.md `passed` 5/5) + v0.7.1 close (2026-08-11)

- ✓ The unit of output became two layers, and every "two logical files want one physical path" case became loud — v0.8.0 Phase 47 (COMP-01..04, OUT-01..03, BLD-02..04): every document is now written as a docname-named **content** `.typ` carrying no template, and every `typst_documents` entry gains a **wrapper** `.typ` carrying the template application and the include of its master's content, so `writer.py`'s `_is_master_document()` output-shape binary is gone (repo-wide grep, not a file read). This closed **B-1** (the parent included `guide/index.typ` from the docname while the resolver named the file from the target, so Typst aborted `file not found`) and **B-2** (an included master re-expanded its template's title page and `#outline()` into the middle of the parent's body). OUT-01 is a deliberate, stated **reversal** of v0.7.1 Phase 44's D-05/D-06/D-07 — a target is now a path relative to the output directory, so a bare name writes at the output root and an explicit path writes where the user asked — while OUT-02 keeps the security half: `..`, absolute and drive-qualified targets stay refused with a warning and a safe fallback. The collision work rode with the split because the split *creates* the hazard: duplicate targets (BLD-02), wrapper-vs-content self-collision (BLD-03) and case-insensitive-filesystem collisions (BLD-04) are all detected by ONE pre-write validator over a single `_is_usable_typst_documents_entry()` predicate now consulted at all five sites that need the entry-usability answer — including the include-set computation that decides whether a cross-reference emits a real `link(<label>)` or degrades to plain text. Composition *semantics* were deliberately left untouched for Phase 49. Two of the three `typst_documents`-modelling todos carried since the v0.7.1 close are resolved here — Validated in Phase 47 (47-VERIFICATION.md `passed`, 12/12 truths, 10/10 requirement IDs)

- ✓ Whether a cross-reference's target exists became a question **Typst answers per compiled wrapper**, not one the builder answers once for all masters — v0.8.0 Phase 48 (XREF-03, XREF-04): every label-reference emission site now routes through ONE shared helper, `_label_existence_guard()`, which wraps the reference in `context { if query(<label>).len() > 0 { link(<label>, …) } else { … } }`. The build-time union over `master_included_docnames` is gone outright (repo-wide grep returns zero matches, per milestone invariant #4), which is what makes Phase 49's include-graph fix safe to ship: after the graph lands, a shared document referencing a target present in one master but not another would otherwise be a hard `label ... does not exist in the document` abort rather than today's silent omission. The helper is the single derivation point by construction — it never derives a label itself, taking only `_namespace_label()`'s output so demand and supply sides cannot spell a label differently — and its four call sites cover the `visit_reference` cross-document branch, `visit_citation`'s back-reference loop, and `visit_pending_xref`; ordinary same-document anchors stay deliberately unguarded, pinned by negative tests. Measured cost: **-2.37%** on a full-corpus compile, against tiers fixed before the measurement. **UAT surfaced a pre-existing defect the phase then closed** (G-48-4): a whole-document `:doc:` reference — a refuri with no `#anchor` — had been emitted since Phase 15 as `link("<docname>.pdf", …)`, a URI action PDF viewers resolve as a nonexistent local file, so the published documentation's own "What's Next?" links were dead. Three gap-closure plans introduced a per-document self-anchor (`<docname:__tsx-doc__>`, a token no docutils `make_id` output can spell) and routed the whole-document case through the same guard: in the project's own PDF, internal destinations went 37 → 72 and broken `.pdf`-suffixed URI actions 40 → 5, the remaining five being the Sphinx-generated `genindex`/`py-modindex`/`search` virtual pages that have no PDF counterpart and stay dead by explicit owner choice. Two limits are accepted and filed rather than hidden: a coincidental docname/label-namespace collision can still link to the wrong document, and an `:orphan:` target now degrades with no diagnostic at any layer — Validated in Phase 48 (48-VERIFICATION.md `passed`, 19/19 must-haves, 48-UAT.md 16/16, 48-SECURITY.md `threats_open: 0`)

- ✓ The include decision moved from **write time to compile time**, so one shared content file behaves correctly for every master that includes it — v0.8.0 Phase 49 (COMP-05..COMP-12): the builder computes each master's include graph by document-order depth-first traversal with first-encounter-wins, mirroring `sphinx.util.nodes.inline_all_toctrees` with `traversed` re-initialised per master (`TypstBuilder._build_include_edge_map()`, `derive_master_edge_keys()`); each wrapper publishes its own edge set as Typst state under `typsphinx:include-edges`; and `visit_toctree` emits, at its toctree's own position, `if "<parent>#<occurrence>><child>" in state(...).get() { include(...) }` instead of an unconditional `include()`. The build-scoped `_included_docnames` ledger is **deleted** (COMP-11), and both the graph side and the emission side iterate `includefiles` rather than `entries`, so `self` and external-URL toctree entries produce no guard at all — which dissolved the live `file not found ... self.typ` abort as a structural consequence rather than a separate fix. **Defect A is closed on generated evidence, not on the code looking correct**: against the measured 2026-08-11 baseline where a two-master project's `index.pdf` reported `SHARED-CHAPTER-MARKER` 0 times and `bmaster.pdf` 1, both PDFs now report it exactly once, read back through `pypdf` from one byte-identical `shared.typ` (SHA-256 compared, not two reads of two files). The diamond `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]` compiles correctly from one shared file, three masters sharing two overlapping children each render each child exactly once, and resolved heading levels are asserted through `typst.query(..., 'heading', field='level')` on the compiled document rather than by grepping `.typ`. **The phase's discipline was that every expected value was written down before anything could produce it**: wave 1 fixed the emission contract against nine real `typst.compile()` probes (closing D-09 — a one-element array literal missing its trailing comma is not a syntax error, it silently degrades `in` from array membership to substring containment) and authored the fixture specification, the degenerate-shape outcome table and a repo-wide assertion census across 19 test modules, all before any fixture or emitter existed; waves 2-3 then transcribed rather than derived. The 16 post-fix assertions were committed as `xfail(strict=True)` naming their own fix plan and flipped to real passes when it landed. GATE-02's full 154-document Sphinx `doc/` corpus gate ran **unmodified** and green, and a pre/post silent-omission control (added at verification, not planned) measured the corpus PDF at 15,422,134 → 15,412,931 bytes with `.typ` count unchanged at 156 — the speed-up is not content loss. Two limitations are **tracked rather than hidden**: `:numref:` numbers diverge per master and vanish entirely for a figure reachable only from a non-root master (owner-approved as a documented limitation handed to Phases 51/52 — and the measurement corrected D-01's own "zero warning" hypothesis, since Sphinx 9.1.0 does warn at the reference site), and two code-review warnings (edge-key separator collision, unbounded traversal recursion) were filed as pending todos by owner decision. — Validated in Phase 49 (6/6 plans; 49-VERIFICATION.md `passed` 5/5 success criteria; 49-UAT.md 2/2 dispositioned; 49-REVIEW.md 0 blockers)

- ✓ The two `TypstBuilder._track_image()` defects PR #131's own review filed against the code that PR introduced are closed as one change to one method — v0.8.0 Phase 50 (IMG-01/IMG-02): the absolute-URI branch now relocates a rehome target that collides with a real source image at `<srcdir>/images/<basename>` (silently) and one that escapes `doctreedir`, including the Windows cross-drive `relpath()` `ValueError` (with a warning), both under one reserved `_typst_converted/` top-level namespace so `copy_image_files()` still copies the file and every destination it computes stays under `outdir`. The collision decision is a filesystem probe rather than a `self.images` membership check, so it does not depend on `sorted(docnames)` order. IMG-01's pre-fix RED was recorded first against the unfixed builder and read out of the compiled PDF via `pypdf`; the fix was proven by removing exactly two `xfail` decorator lines with zero assertion edits. Ships with two tracked items: IMG-02 had no pytest-recorded written-first RED (closed by a scoped owner override citing the 2026-08-10 manual measurement that pre-dates the fix by four days), and a second-order basename collision inside the reserved namespace filed as a minor follow-up todo.

- ✓ v0.8.0 released — v0.8.0 Phase 52 (REL-07 prep half; prep-only, zero irreversible action, zero lines under `typsphinx/`) + the `/gsd-complete-milestone` publish (REL-07 publish half): the tree bumped to `0.8.0` across `pyproject.toml`/`README.md`/`uv.lock` with the editable install regenerated so `typsphinx.__version__` reports it live, the `## [0.8.0]` CHANGELOG entry curated with both breaking callouts marked `**Breaking:**`, and the post-bump tree proven green on a live CI run rather than a local one — honestly, on the **third** dispatch (RED 8/12 → 11/12 → GREEN 12/12, run `31858016832`), the three-run history recorded append-only rather than collapsed. The publish then executed: PR #133 merged with all 13 real checks green, tag `v0.8.0` on `78e01e5`, release run `31861043480` completing `validate` → `build` → `publish-pypi` → `create-release` all success, PyPI `typsphinx 0.8.0` live, the GitHub Release body measured byte-identical to the extractor's output over its first 70 lines, and the standing second tag pushed on `typsphinx-doc-translations` via its own dispatched `update-pin.yml` — Validated in Phase 52 (52-VERIFICATION.md `passed` 9/9 must-haves) + v0.8.0 close (2026-08-15)

- ✓ The output-shape change stopped being something a user discovers and became something the documentation states — v0.8.0 Phase 51 (DOC-14): a new `docs/source/user_guide/output_layout.rst` names the **wrapper** and **content** layers, says the wrapper at the entry's target is the file to compile (and that `-b typst` prints the wrapper names itself), and states standalone-content compilation — empty `state`, therefore no children — as intended, well-defined behaviour in plain prose rather than as a caveat (D-08). Target-as-path ships with built worked examples for the bare and explicit-path cases, all three refusal shapes with their verbatim warning text and safe fallbacks, the Phase 47 collision abort with its exact `ExtensionError`, and Phase 49's shared-child consequence in the user's language; `changelog.rst` states the v0.7.x change in old→new file names beside v0.7.1's own `index.typ` → `<project>.typ` rename so the two are not confused. The claim-to-build binding is a permanent 13-test gate over five fixtures that never skips and needs no `typst-py`. `:numref:` divergence is **excluded by owner decision** (D-06/D-07) and stays a pending todo. Zero lines under `typsphinx/`. **The carrying lesson is a negative one:** the phase's own defect class — a false emitted-file claim — survived all six plans *and* the gate, because the page contradicted both itself and its own passing test while no test bound published prose to a measured file set; the post-phase code review found it, and the gate's one numeric assertion (`"ten" in text`) was independently vacuous, `"ten"` being a substring of `"written"` and `"content"`. Both fixed post-execution, the assertion replacement mutation-proved rather than observed passing; two further residuals in files no plan had declared were found only because the completeness audit was required to derive its search set from the claim patterns instead of from the earlier plans' file lists — Validated in Phase 51 (51-VERIFICATION.md `passed`, 3/3 success criteria, no gaps, no human verification required)

### Active

<!-- Scoped 2026-08-11 for v0.8.0, all six items closed at the 2026-08-15 close. `.planning/REQUIREMENTS.md`
     is the authoritative, REQ-ID'd list; this section only ever carries the active milestone's headline
     commitments, and is re-scoped by `/gsd-new-milestone`. -->

**v0.9.0 per-document templates (scoped 2026-08-15)** — every `typst_documents` entry can use its
own template, package, and template-function arguments:

- [ ] A new `typst_document_templates` registry names template definitions (`template` xor
      `package`, plus `template_function`), and `typst_documents` element [4] selects one — the slot
      `configuration.rst:80` currently defines as "accepted and ignored"
- [ ] The built-in key `"typst"`, and a four-element tuple, defer to global config, so every
      existing `conf.py` keeps working unchanged
- [ ] Every key's template bundle — `"typst"` included, with no exception — is copied wholesale to
      `<outdir>/_template/<key>/`, so template-relative asset references resolve
- [ ] `_write_template_file()`, `_copy_template_directory()`'s `.typ` exclusion,
      `copy_template_assets()`'s three early returns, and the reserved `_template.typ` file claim
      are deleted rather than extended; `typst_template_assets` is removed as inert config
- [ ] Misconfiguration fails loudly: unregistered key, `template` + `package` in one entry, a
      user-defined `"typst"` key, and a `template` directly under `srcdir`
- [ ] The five v0.8.0-derived defects that shipped unfixed by decision D-01, or with only a
      test-side fix, are closed

<details>
<summary>v0.8.0's Active list (complete, shipped 2026-08-15) — retained for reference</summary>

**v0.8.0 multi-master composition (SHIPPED 2026-08-15)** — a `typst_documents` configuration with
more than one master produces a complete PDF for each:

- [x] Every document is written as a docname-named content `.typ` with no template applied, and each
      `typst_documents` entry gains a wrapper `.typ` carrying the template — closing the include-path
      vs. output-filename mismatch (`file not found`) and the mid-body template re-expansion
      — **Phase 47**
- [x] The wrapper publishes its master's include edge set as Typst `state` and content files emit
      state-guarded includes at their toctree's own position (graph computed document-order
      depth-first, mirroring `sphinx/util/nodes.py` `inline_all_toctrees`), so a document toctree'd
      by two masters reaches both instead of only the first-written one, prose around a toctree keeps
      its position, and the same content file serves masters with conflicting include sets
      — **Phase 49** (checkbox corrected at the Phase 50 close-out; the phase itself completed
      2026-08-14 with 8/8 requirement IDs COMP-05..12)
- [x] Two `typst_documents` entries naming the same target are detected rather than silently dropping
      one master's body, following CR-01's fall-back-to-docname-with-a-`WARNING` convention
      — **Phase 47** (extended in-phase to wrapper-vs-content self-collision and case-insensitive
      filesystems, under one pre-write validator)
- [x] A cross-document reference degrades at compile time via a `context` + `query` label-existence
      guard, so a shared document referencing a target absent from this master no longer aborts the
      compile once the include graph is fixed — **Phase 48**
- [x] A converted image rehomed to `images/<basename>` no longer collides with a real source image at
      `<srcdir>/images/<basename>`, and an absolute URI outside `doctreedir` no longer escapes `outdir`
      — **Phase 50** (both relocated under one reserved `_typst_converted/` namespace: the collision
      silently, the escape and the Windows cross-drive `ValueError` with a warning)
- [x] v0.8.0 released to PyPI with a curated CHANGELOG entry calling out the output-shape change
      and the target-as-path reversal — **Phase 52 prep half + the `/gsd-complete-milestone` publish**

**Not scoped into v0.8.0**, carried as candidates:

- **`typst_authors`'s missing fail-loud shim** (D-03, declined for v0.7.1 on prep-only-fence
  consistency grounds). The config value is gone as of v0.7.1, but a `conf.py` still setting it gets
  no error — Sphinx ignores unregistered variables silently — so the author information vanishes
  without a trace.
- **`ruff` cannot run locally on NixOS** — the same generic-linux-ELF family as QUA-04, but on the
  `flake.nix` side. CI holds lint authority so nothing is blocked, but the maintainer's own machine
  cannot run one of the three gates CI enforces.
- **SEED-003** — split the `dev` extra into PEP 735 `[dependency-groups]` so each tox environment
  installs only what it needs.

</details>

### Out of Scope

- Configurable `@preview` package versions (FWD-03, tech-debt item) — deferred; v0.5.0 bumps the bundled versions in-place rather than making them user-configurable
- A Sphinx 8/typst 0.14 ⇄ Sphinx 9/typst 0.15+ compatibility range — v0.5.0 is latest-only; supporting both old and new majors simultaneously is out of scope
- Incremental-build rebuild tracking, translator state-management refactor — orthogonal tech debt, not part of a CI-repair milestone
- New translation features / new reST constructs — this is a maintenance cycle, not a feature cycle

## Context

- **Failure evidence (CI run, 2026-07-04):** loose pins resolved `sphinx==9.0.4`, `docutils==0.22.4`, `typst==0.15.0`, Python 3.11. Three buckets: (1) `black --check` reformats 3 files (`docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`); (2) 7 PDF-integration tests + all 12 matrix jobs + docs PDF build fail on `typst.TypstError: unknown variable: kai` — a pinned `@preview` package incompatible with the typst 0.15 compiler; (3) matrix jobs exit 254/1 cascading from the same compile error. Type Check and Build Package jobs currently pass.
- **`kai` origin:** the symbol appears nowhere in typsphinx source — it comes from inside a pinned Typst Universe package (likely `gentle-clues:1.2.0` or `codly`) when compiled by typst 0.15. Pinning typst back to the 0.14.x line where those packages compile is the fix.
- **Codebase map:** `.planning/codebase/` (ARCHITECTURE, STACK, CONCERNS, CONVENTIONS, INTEGRATIONS, STRUCTURE, TESTING) refreshed 2026-07-04.
- **Tech-debt note (from CONCERNS.md):** hardcoded `@preview` versions live in two places (`typsphinx/writer.py`, `typsphinx/template_engine.py`) plus `typsphinx/templates/base.typ` — keep these three in sync when pinning.
- **`kai` root cause resolved (Phase 7):** the `unknown variable: kai` break came specifically from **mitex** (fixed in mitex 0.2.6, PR #201), not gentle-clues/codly as originally speculated in the failure evidence above. Bumping mitex 0.2.4→0.2.7 cleared it; codly 1.3.0 compiles clean under typst 0.15.
- **Known follow-up bug — RESOLVED in Phase 8.1 (2026-07-11):** `.. note::` / admonitions rendered literal Typst source (`par({text(...)})`) instead of typeset prose — a markup-vs-code-mode mismatch in `typsphinx/translator.py::_visit_admonition` (discovered Phase 7, pre-existing since 2025-10-13; orthogonal to `@preview` versions, invisible until `docs-pdf` first compiled post-`kai`-fix). **Fix:** `_visit_admonition`/`_depart_admonition` now emit the code-mode content-block form `clue_type({...})` (was markup `clue_type[`), and titles route through a `visit_title`/`depart_title` buffer-swap that preserves inline markup (D-02) and fixed a latent title double-emission bug. Scope also widened per discussion: 5 previously-missing admonition types added (`hint`→tip, `error`→error, `danger`→danger, `attention`→warning, generic `.. admonition::`→base `clue()`; D-06), unit asserts strengthened to structural checks (D-03), nested-content coverage (D-05), and a real D-04 acceptance gate (`tests/test_pdf_render_gate.py` + `tox -e docs-pdf`: compile → `pypdf` text-extraction → no-leak assertion) that proves the fix in a real render. Full suite 411/411 green; gentle-clues 1.3.1 / `@preview` versions unchanged.

- **Shipped state (2026-08-15, v0.8.0):** PyPI `typsphinx 0.8.0` — Sphinx 9.1 / docutils 0.22 / typst 0.15, Python 3.12–3.13. Four bundled `@preview` packages, unchanged through this milestone and guarded across four sync surfaces; **zero runtime dependencies added since v0.6.0**, and no new `typst_*` config value — all three asserted mechanically over the SHA-anchored milestone diff with each detector fire-tested against a real violation. Documentation on Read the Docs in English and Japanese, the latter built from `typsphinx-doc-translations`, which carries its own matching `v0.8.0` tag on pin `78e01e5`. **The output shape changed in a user-visible, breaking way** — one `typst_documents` entry now writes a wrapper plus a content file per docname, and a target containing a path separator is honoured as a path.
- **Shipped state (2026-08-11, v0.7.1):** PyPI `typsphinx 0.7.1` — Sphinx 9.1 / docutils 0.22 / typst 0.15, Python 3.12–3.13. Four bundled `@preview` packages (codly, codly-languages, mitex, gentle-clues), unchanged through this milestone and guarded across four sync surfaces. Zero runtime dependencies added since v0.6.0. Documentation on Read the Docs in English and Japanese, the latter built from the separate `typsphinx-doc-translations` repository, which carries its own matching `v0.7.1` tag.
- **Local toolchain (fixed 2026-08-11, QUA-04):** `tox` works on the maintainer's NixOS machine for the first time. The `dev` extra depends on **`tox-uv-bare`**, not `tox-uv` — the plain meta package bundles a PyPI `uv` wheel whose generic-linux ELF cannot exec on NixOS, and `uv.find_uv_bin()` searches `.venv/bin` first and reads no environment variable. `CLAUDE.md` records this so it is not "simplified" back. `ruff` remains unrunnable locally for the same ELF reason (its own todo); CI holds lint authority.
- **Open defects the project knows about and chose to ship (as of the v0.8.0 close, 2026-08-15):** four minor defects, all NEW failure classes created by v0.8.0's own features, deferred by decision D-01 and held to internal disclosure only by D-03 — a label-collision false negative in the compile-time xref guard (`a/b` vs `a_u2f_b`), unescaped `#`/`>` separators in `make_include_edge_key`, unbounded recursion in `_derive_master_edge_keys` (raw `RecursionError`, not a named `ExtensionError`), and the basename-keyed image escape branch colliding with the rel-URI-keyed collision branch. Plus one carried outside that set: `_track_image()` gates on OS-native `path.isabs()`, so a driveless-absolute image URI is not rehomed under Python 3.13 on Windows (`typsphinx/builder.py:910`) — surfaced by Phase 52's own CI chase, fixed test-side only, filed rather than erased. The `:numref:` per-master divergence stays excluded from every published surface by D-07 and remains a pending todo. *(Superseded: three `typst_documents`-modelling defects, enumerated in `46-HANDOFF.md` § "Deferred by decision, not oversight" and carried into this file's Active candidates, were all closed by v0.8.0 Phases 47 and 49.)* *(The two `TypstBuilder._track_image()` defects that stood here — IMG-01, the silent-wrong-picture failure-mode regression, and IMG-02, the outdir escape — were closed by v0.8.0 Phase 50 on 2026-08-14 and are no longer open. One second-order residual of that fix ships tracked: two escaping absolute URIs sharing a basename still collide inside the reserved namespace — `2026-08-14-escape-branch-relocation-key-uses-basename-only-two-escaping-images-can-collide.md`, severity minor, unreachable through stock Sphinx.)*

## Constraints

- **Tech stack**: Python package; Sphinx builder API; Typst via typst-py — pinning must keep the extension importable and the builders registered
- **Compatibility**: `@preview` package versions and the typst compiler version must be mutually compatible — this is the crux of the fix
- **Reproducibility**: `uv.lock` must be regenerated to match the new pins; tox/uv drives all CI checks
- **Platforms**: CI runs ubuntu/macos/windows — pins must produce green on all three
- **Release process (from v0.6.2 onward — decided 2026-07-20):** the ship unit is the **milestone**, not the phase (`branching_strategy: milestone`). Every PyPI-published milestone MUST include an explicit **final Release phase** that bumps `pyproject.toml` version + adds the `CHANGELOG.md` `[X.Y.Z]` entry (the v0.5.0 Phase 10 pattern); the milestone's phases execute on a `gsd/vX.Y-*` branch and `gsd-ship vX.Y` opens one observation/release PR (CI observed green before merge). The irreversible publish — tag `vX.Y` → `release.yml` → PyPI — is executed at `/gsd-complete-milestone` (audit-then-publish) on the confirmed-green merge commit. **Push `main` to `origin` at every milestone close** to prevent the recurring branch/main drift (retrospective lesson #7). *(v0.6.1 was retroactively released on 2026-07-20 via this process: release PR #118 (CI matrix green) → merge to `main` (pushed to `origin`) → pyproject/uv.lock/CHANGELOG bumped to 0.6.1 → tag `v0.6.1` on the merge commit → `release.yml` published `typsphinx==0.6.1` to PyPI + GitHub Release. The `pypi` deployment environment gates publish behind a manual approval + 15-min wait_timer.)*

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Land the compile-time cross-reference guard (Phase 48) BEFORE the include graph (Phase 49), though no requirement forced the order (roadmap binding constraint #1, 2026-08-11) | The graph turns a silently-omitted document into a reachable-and-absent label, so shipping it first would ship a fatal `label ... does not exist` abort in between | ✓ Good — held through execution; Phase 48 also closed a pre-existing whole-document `:doc:` dead-link defect (40 broken URI actions → 5) that UAT surfaced only because the guard work looked there |
| Ship four minor defects unfixed and hold them to internal disclosure only — no `### Known Limitations` CHANGELOG section, no GitHub issue, no ROADMAP backlog item (D-01/D-03, owner decision 2026-08-14) | All four need unusual input shapes; the v0.7.1 D-27 precedent applies, with one distinction on the table: unlike D-27's pre-existing pair, all four here are NEW failure classes created by features this milestone shipped | — Pending: `52-HANDOFF.md` plus `.planning/todos/pending/` are the complete record, deliberately the only surface. Revisit if any becomes reachable through stock Sphinx |
| Fix all four CI-surfaced defects test-side rather than product-side, to preserve Phase 52's zero-`typsphinx/`-lines prep-only fence (owner decision, 2026-08-15) | A prep-only release phase that edits the product stops being prep-only; the alternative was reopening an already-verified phase at the release | ✓ Good, with one condition attached: the product-side inconsistency the fourth defect exposed (`builder.py:910`) was filed as a todo rather than erased by the test fix — a green CI with that knowledge lost would have been worse than a red one |
| Close v0.8.0 as `override_closeout` without a `MILESTONE-AUDIT.md` (owner decision, 2026-08-15) | `init.manager` reported all 6 phases `phase_complete=true` / `verification_status=passed`, and every v1 requirement except the publish-gated REL-07 was already Complete before the close began | — Pending (fifth consecutive milestone closed this way; the pattern is now the norm rather than the exception, and worth a deliberate decision rather than a repeated default) |
| Advance the `typsphinx-doc-translations` pin by dispatching that repository's own `update-pin.yml` rather than by a hand-made clone-edit-commit (2026-08-15) | The workflow already exists, is scheduled daily, and encodes the submodule-ref and POT-Creation-Date-churn handling correctly; a hand-made commit would be a second, undogfooded path | ✓ Good — one dispatch produced the pin advance and the ja catalog resync, including `output_layout.po`, which independently confirmed Phase 51's new page reached the translation source |
| Pin runtime deps to known-good rather than upgrade forward | Fastest, lowest-risk path to green CI; avoids a large sphinx-9/typst-0.15 porting effort in a maintenance cycle | Confirmed: full 3-OS × Python matrix green in Phase 2 (CI run 28702240846) |
| Pin `typst` to 0.14.x compatible with bundled `@preview` packages | The `kai` break is a typst 0.15 ⇄ package incompatibility; reverting the compiler restores compilation | Confirmed: `typst==0.14.9` (resolved in `uv.lock`); `docs-pdf` builds `index.pdf` locally with no `kai` error (typst 0.15.0 reproduces it) |
| Modernize Python floor to 3.10–3.13 (drop EOL 3.9, add 3.13) | 3.9 reached EOL Oct 2025; "green + modernize" scope | Confirmed in Phase 3: full 3.10–3.13 matrix + `docs.yml` green on PR #104 (no 3.13 wheel gap; D-03 ruff pyupgrade reformat fired and was fixed in-batch; `conf.py` `tomllib`→`tomli` backport for the 3.10 docs floor) |
| Defer supporting sphinx 9 / typst 0.15 to a future milestone | Explicitly chosen to pin, not port; keeps scope bounded | — Pending |
| `sphinx<9`/`docutils<0.22` ceilings are precautionary, not load-bearing for the `kai` break (D-03) | The `kai` break is purely the typst 0.15 compiler; per RESEARCH's Linux reproduction, `docs-pdf` builds with `typst` pinned even with sphinx/docutils unbounded. Ceilings still applied per D-03 as guardrails against unrelated sphinx-9 / docutils-0.22 drift | Precautionary (not load-bearing) confirmed on Linux; `docs-pdf` builds green with typst 0.14.9, sphinx 7.4.7/8.1.3, docutils 0.21.2. Full 3-OS × Python-version matrix confirmation is Phase 2's gate |
| Accept already-green pytest 9.1.1 / mypy 2.1.0 with next-major ceilings, not a rollback to literal `pytest~=8.4`/`mypy<2.0` (D-01, Phase 4) | Phase 3's green CI already resolved pytest 9.1.1 + mypy 2.1.0; rolling back would shrink the confirmed known-good set. Honor TOOL-01's spirit ("no risky major flips") via guard ceilings instead — a deliberate, user-owned deviation from TOOL-01's literal wording | Applied: `pytest>=8.4,<10`, `mypy>=1.13,<3.0` in pyproject.toml + tox.ini; Phase 4 CI green on PR #105 |
| All refreshed dev tools get `floor+<next-major` guard ceilings, incl. tox-uv (D-02/D-07, Phase 4) | Matches Phase 1's defensive runtime pinning + the anti-drift milestone theme; no bare `>=` floor leaving an unbounded re-resolution path | Applied lockstep across pyproject.toml `[dev]` + tox.ini (4 mirror points incl. `[tox] requires` for tox-uv): black `>=26,<27`, ruff `>=0.15,<0.16`, tox `>=4.56,<5`, tox-uv `>=1.35,<2` |
| Bump artifact actions to node24: upload-artifact@v5→v7, download-artifact@v6→v8 (D-03 AMENDED 2026-07-05, Phase 4) | Post-research: v5/v6 still declare node20, which GitHub removes from hosted runners 2026-09-16; the original "already at latest majors" premise was wrong | Applied across ci.yml/docs.yml/release.yml (7 + 3 occurrences), runtime-verified node24; Phase 4 CI green |
| Remove stale `Test Python 3.9 on ubuntu-latest` required status check from `main` branch protection, add 3.13 (Phase 4) | Phase-3 leftover: 3.9 was dropped from the CI matrix but the required-check list wasn't updated, leaving a permanent "Expected — waiting for status" pending that blocked PR #105 despite all 18 jobs green | Applied via `gh api PATCH`; PR #105 became MERGEABLE/CLEAN. Required set now ubuntu 3.10–3.13 + Lint/Type/Coverage/Build |
| `softprops/action-gh-release@v2` node20 straggler tracked, not force-bumped in Phase 4 | Outside 04-02's authorized edit scope (artifact-actions only) and needs its own verification; `@v3` exists and is node24 | Deferred to Phase 5 (durability-guardrails) as a tracked item, not silently closed |
| Close the milestone with durability guardrails: `--locked` lockfile-currency gate + standalone weekly `drift.yml` + `sphinx-typst-stack` Dependabot group + README CI badge; softprops@v3 (Phase 5, D-01..D-11) | Install anti-drift controls so the silent multi-year rot this milestone fixed cannot recur unnoticed; keep the drift job advisory (never a required check, D-07) so it reports without blocking merges | Confirmed in Phase 5: PR #106 merged green (ci.yml 28730645396 / docs.yml 28730645381); drift.yml validated via post-merge `workflow_dispatch` (run 28730876125 success, no drift issue = no forward drift); D-11 softprops@v3 runtime confirmation RESOLVED at the v0.4.4 release: `Create GitHub Release` ran green (release run 28731646924, tag `v0.4.4`) |
| Fix `release.yml` version-verify step: `import tomllib` → `tomllib`/`tomli` fallback (v0.4.4 release, PR #110) | PYVER-02's 3.10 floor reconciliation left the tag-only Validate step importing stdlib-only `tomllib` on 3.10; it crashed on the first `v0.4.4` tag push (a release-only regression not exercised by any PR CI) | Fixed on `main` (merge dae500a); re-pushed `v0.4.4` tag; release run 28731646924 green end-to-end → PyPI `typsphinx==0.4.4` (wheel+sdist) + GitHub Release published |
| v0.5.0 latest-only forward port; Python floor → ≥3.12 (drop 3.10/3.11) | Sphinx 9.1's own `requires-python` forces ≥3.12; a Sphinx-8/typst-0.14 ⇄ 9/0.15 compatibility range is out of scope for a maintenance cycle | ✓ Good: full 3-OS × Python 3.12–3.13 matrix green (PR #112, 13/13) |
| Group FWD-02 (typst re-pin + no-`kai` compile) with the `@preview` bump in Phase 7, not the pin-raise | Raising typst without the package bump leaves CI red on `kai`; both must land atomically | ✓ Good: `kai` closed on first real `docs-pdf` compile, no bisect needed — root cause was mitex 0.2.6+, not gentle-clues/codly as originally speculated |
| Escalate both `DeprecationWarning` and `PendingDeprecationWarning` in the permanent pytest `filterwarnings` guard (Phase 8, deviation from CONTEXT's DeprecationWarning-only text) | Sphinx's `RemovedInSphinxNNWarning` family subclasses `PendingDeprecationWarning`; guarding only `DeprecationWarning` would miss forward-deprecation signals | ✓ Good: suite green under the stricter guard |
| Insert Phase 8.1 to fix the admonition markup/code-mode render bug mid-milestone | The bug (literal `par({text(...)})` leak) pre-dated the milestone but only became visible once `docs-pdf` first compiled post-`kai`-fix; orthogonal to `@preview` versions | ✓ Good: real `sphinx-build → typst.compile → pypdf` acceptance gate proves the fix; 5 missing admonition types added as scope-widen |
| Single-source `__version__` via `importlib.metadata`; `pyproject.toml` sole literal (Phase 10) | Root-cause fix for the stale hardcoded `0.4.3` string — version drift becomes structurally impossible; an independent `tomllib` re-parse test guards against the tautology | ✓ Good: importing typsphinx reports `0.5.0`; drift-guard test green |
| Re-scope Phase 10 to prep-only; defer the publish half (merge PR #112 → tag → PyPI) to `/gsd-complete-milestone` | Mirrors the v0.4.4 precedent — keep the release-execution gate at milestone close so CI-green is confirmed on the exact merge commit before publishing | ✓ Good: executed at v0.5.0 close |
| v0.6.0: fix Issue #114 fatal figure/image bugs FIRST (Phase 11) as a blocking prerequisite, with a standing real-`typst.compile()` acceptance gate (GATE-01) as the empirical bar for every node-handler phase | A single fatal node aborts the whole PDF, so no downstream handler can be validated against a real compile until #114 lands; string-agreement asserts don't catch compile fatals | ✓ Good: GATE-01 caught 3 additional latent fatals (label-in-code-mode, dangling `:term:` anchor, footnote separator-state clobber); GATE-02 full-corpus compile green |
| v0.6.0 milestone audit run before close (as with v0.5.0); acknowledge the 13 post-GATE-02 rendering-polish debug sessions as deferred backlog rather than blocking the close | The 13 debug sessions are non-fatal render-quality bugs discovered *after* GATE-02 went green — outside v0.6.0's definition of done (fatal-free compile + the 19 named requirements, all met); blocking on them would conflate a shipped milestone with its follow-on polish | ✓ Good: audit passed 19/19 requirements, 16/16 integration seams; 13 items recorded in STATE.md Deferred Items |
| Deliver v0.6.0 via a release PR (`release/v0.6.0 → main`) whose body closes Issue #114, then tag the merge commit → PyPI — not a direct-to-main tag push | Matches the v0.5.0 PR #112 "observation PR" precedent: the full 3-OS × Python CI matrix runs on the PR and is observed green before publishing, and merging auto-closes the driving issue | Pending — executed at v0.6.0 close |
| Gate `visit_todo_node` on `config.todo_include_todos` via `raise nodes.SkipNode` (Phase 16) | Mirrors every official Sphinx builder (html/latex/text/man/texinfo); prevents draft work-notes leaking into published PDFs (T-16-01) | ✓ Good: enabled/disabled both pinned by real-compile fixture tests |
| `visit_manpage`/`depart_manpage` delegate 100% to `visit_emphasis`/`depart_emphasis`; no linkification (Phase 16, D-02/D-02a) | Duck-typed delegation reuses the separator/list-item/inline-concat/markup-mode state machine for free — no bespoke handler to drift; `manpages_url` unset means a reference child can't occur | ✓ Good: fixture asserts `link(` absent; italic renders in paragraph/list/caption contexts |
| Wrap the whole `figure()`/`table()` call in `block(width: ...)[...]` rather than passing `width:` as a kwarg; convert length once at visit, consume at depart (Phase 16) | Typst's `figure()`/`table()` both reject a direct `width:` kwarg (real-compile-verified); converting twice would double-fire the unsupported-unit warning | ✓ Good: both render-gate tests compile fatal-free; a kwarg regression aborts the compile loudly |
| Discover silent mis-renders via a human-assisted page-by-page visual audit of the corpus PDF vs. the `-b html` baseline, not warnings (Phase 17) | Warnings only surface *dropped* content; output that compiles fatal-free AND emits no warning yet diverges from source is invisible to any automated gate — only visual inspection finds it | ✓ Good: 15 systemic findings surfaced across 151 docnames, human-confirmed at the 17-03 gate (14 accepted / 1 rejected) |
| Append only the high-severity audit finding to REQUIREMENTS.md as `FID-01a`; record the 13 medium/low findings as a single Future-Requirements pointer, not as enumerated requirements (Phase 17) | Keeps the milestone's definition-of-done bounded to what materially breaks fidelity (content lost/unreadable/grossly mis-structured); enumerating low-severity polish as requirements would balloon scope | ✓ Good: FID-01a was the sole high finding; medium/low backlog preserved in `17-AUDIT-CATALOGUE.md` without blocking close |
| Fix wide-table overflow with fr-weighted `columns:` from docutils colwidth AND in-table U+200B break injection — both halves, not fr alone (Phase 18) | fr-weighted columns fix the proportional layout but long unbroken dotted API paths (`sphinx.environment.BuildEnvironment`) still overflow their cell; the ZWSP after `.`/`_` gives Typst legal break points | ✓ Good: `wide_table_render_gate` collision-absence fixture passes; the fix would fail without either half |
| Route every output-path derivation through one `TypstBuilder._resolve_output_stem`, and strip only a literal trailing `.typ` instead of using `os.path.splitext` (Phase 22, D-04) | The rule was re-derived at three write/read-back sites and drifted, which is what produced Issue #117; `splitext` would truncate a legitimate `v1.2-manual` target to `v1` | ✓ Good: `os.path.splitext` absent from `builder.py`; 24 locked cases in `test_builder_output_stem.py`; the five identity-mapping regression modules passed unmodified |
| Guard path-bearing / absolute / drive-qualified / `..` targets by warning and reducing to `path.basename` rather than raising (Phase 22, D-06/D-07) | `conf.py` is arbitrary Python Sphinx already executes, so this is defense against accidental escape and a UX signal — not containment of a hostile author; raising would break builds over a typo | ✓ Good: T-22-01/02 closed at `threats_open: 0`; degenerate targets fall back to the docname instead of opening an empty or bare-dotfile basename |
| Accept macOS/Linux filesystem Unicode normalization (HFS+/APFS NFD vs. byte-preserving NFC) as an out-of-scope OS behavior (Phase 22 UAT, option b, 2026-07-21) | The half typsphinx controls — verbatim pass-through of a non-ASCII target with no normalization, case folding, or transliteration — is proven by `test_resolve_output_stem_preserves_non_ascii_target`; the OS half needs a macOS runner the project does not have, and matches the `verification: backstop` prose already in `22-01-PLAN.md` | ✓ Accepted: recorded as a documented limitation; adjacent to the standing XOS-01 v2 item (cross-OS `docs-pdf` CI) |
| Close v0.6.1 as `override_closeout` — accept Phase 17's human confirmation gate + `17-VALIDATION.md` + Phase 18's downstream real-compile proof in lieu of a machine `VERIFICATION.md` | Phase 17 is a pure audit/documentation phase producing a catalogue, not code; `init.manager` can't certify a docs phase, but its output was human-confirmed and proven downstream by the FID-01a fixture + corpus gate | ✓ Good: operator accepted the verification override at close; no real coverage gap |
| Make `typst_elements` a curated, hand-maintained allowlist that fails loud on an unknown key, rather than passing keys through (Phase 26, CONF-04, D-03/D-06) | A `.typ` `project()` signature can't be reliably introspected from Python, and an undeclared kwarg is a hard Typst compile fatal — so pass-through would trade a silent drop for a cryptic compile abort. Arbitrary pass-through already exists via `typst_template_function.params` | ⚠️ Revisit: correct, but it broke the bundled `examples/advanced` at the same stroke and that went unnoticed until the milestone close. The fail-loud message is good; the gap was that nothing built the shipped samples |
| Gate `lang` auto-derivation to the bundled-default-template path only, and pre-merge it *under* the user's `typst_elements` (Phase 27.1, CONF-07, D-05/D-06) | Injecting into a custom-template or `typst_package` build would hand those users an undeclared kwarg for merely setting `language` — a hard fatal. Pre-merging under the user dict makes explicit-wins structural rather than incidental, mirroring Sphinx's own LaTeX `init_context()` precedence | ✓ Good: three non-regression fixtures prove no non-default path receives an injected argument |
| Extend the `@preview` version-sync guard over `examples/**/*.typ` (v0.6.3 close) | The guard watched only the three extension-internal surfaces, so a bundled sample sat three milestones behind on its pins — and a stale pin there is not cosmetic, it makes the shipped sample fail to compile outright. Scoped to packages the project itself pins, so an example on a different toolkit (charged-ieee) is unaffected | ✓ Good: verified red against the pre-fix file, green after; drift channel closed |
| Close v0.6.3 as `override_closeout` without a `MILESTONE-AUDIT.md` (owner decision, 2026-07-25) | All 6 phases were `phase_complete` + `verification_status: passed` with 7/7 requirements checked off, and Phase 28 had already re-run the full-corpus gate, the full pytest suite, and both docs-build environments live on the post-bump tree — covering the audit's requirement-coverage and integration ground | — Pending: no gap surfaced at close, but the one real defect found (unbuildable `examples/advanced`) was found by asking about open todos, not by any gate. A cheap "do the shipped examples build?" check would have caught it earlier |
| Separate `typsphinx-doc-translations` repository with the parent pinned as a submodule tracking `gsd/v0.6.4-read-the-docs-migration`, not `main` (Phase 30.1, PD-02) | Measured: `origin/main` has no `.readthedocs.yaml` and no `_resolve_language()`, so a `main`-tracking submodule pins a tree RTD refuses to build; the sphinx-doc-translations precedent (RTD API: all 15 sphinx translations are separate repos) fixed the repo model | ✓ Good: ja site builds green from the pin and the scheduled auto-advance works — at the cost of a third owed post-merge flip (`.gitmodules` `branch` → `main`), recorded alongside the two RTD Default-branch flips |
| Fix the ja-PDF glyph defect via option-b — a docs-side custom `typst_template` + explicit `derive_typst_lang()` re-derivation — accepted as a deliberate reach into Phase 29's verified English artifact (Phase 30.1, owner decision at Plan 10) | Option-a (ja manifest only) could not fix it, option-c (accept + todo) abandons I18N-03's bar, option-d (`typsphinx/` change) is barred by milestone invariant #3; option-b was taken with the English PDF re-measured before/after to prove non-regression | ✓ Good: corrected artifact (SHA `23885dcd…`) passes all four D-03 checks incl. owner visual confirmation; English PDF unregressed; leaves `custom_template.typ` as a fourth unguarded `@preview` lockstep site (carried Warning) |
| Install the link guard BEFORE the URL rewrite and record a red negative-control run (Phase 31, D-09) | A guard never seen red proves nothing — the pre-rewrite failing run demonstrates the job detects exactly the bug class (dead published links) it exists to catch, before the links it must catch are gone | ✓ Good: negative control run 30205112477 red (all 7 old-host README deep links flagged); post-rewrite tree green; job confirmed advisory (absent from required status checks) |
| Split Issue #119's close out of Phase 31 to the post-merge `/gsd-complete-milestone` (Phase 31, D-15) | The rewritten URLs live on the milestone branch; closing the issue while `main` still serves dead links would promise a fix the default branch does not yet have | ✓ Good: owner approved the draft at close (2026-07-28); posted and closed after PR #124 merged, with the fix live on `main` |
| v0.6.4 CHANGELOG carries zero BREAKING labels; the migration's user-visible losses are disclosed in the Removed body instead (Phase 33, D-01/D-04) | No packaged (pip-installed) behavior changed — the losses are hosting-side (github.io 404s with no redirect, browser-language auto-redirect gone). A BREAKING label on a docs-hosting change would train readers to ignore the label where it matters | ✓ Good: disclosure asserted by Task acceptance criteria; T-33-04 closed |
| CHANGELOG `### Verified` restricted to invariants `git diff` can mechanically prove; the live-RTD observation stays out of the CHANGELOG (Phase 33, D-03) | A published claim without a standing re-verification mechanism rots silently — the RTD 302→200 observation is a point-in-time fact recorded with a timestamp in `33-RELEASE-EVIDENCE.md` instead | ✓ Good: three invariants backed by recorded live diff output over the re-measured 279-commit range, with a non-empty positive control beside the empty `typsphinx/` diff |
| Translate the four top-level `.planning/` docs JA→EN before the milestone merge, meaning-preserving with structural invariants (Phase 33, D-05) | Merging makes them publicly readable; translation makes the decision record legible without corrupting it — wrong claims stay equally wrong, narrow scopes stay equally narrow | ✓ Good: requirement-ID census byte-identical, heading/table-row counts unchanged; human meaning-preservation spot-check passed (UAT 1/1) |
| Run `/gsd-audit-milestone` before the v0.6.4 close instead of repeating v0.6.3's audit-less override (owner choice, 2026-07-28) | v0.6.3's close-time lesson: its one real defect was found by a side question, not a gate; a cheap audit (3-source requirements cross-reference + integration checker) closes that class | ✓ Good: audit `passed` 13/13 with zero gaps — the first verified_closeout since v0.4.4 |
| Curate the auto-generated MILESTONES.md entry down from 24 raw plan one-liners to 6 accomplishments in house style (v0.6.4 close) | The CLI dump includes truncated/broken lines and per-plan noise; the entry is the durable shipped-history record and must stay readable | ✓ Good |
| Reproduce and measure 999.1 before fixing it, treating the backlog note's "math/Text visit ordering" as a hypothesis rather than a finding (Phase 34) | The note's own premise was checkable and false — `visit_math` already called `_add_paragraph_separator()`. Fixing the named suspect would have changed nothing | ✓ Good: the real cause (a *scope gap* — participation in one of three separator protocols, so the fatal only surfaced in list items / field bodies / def-list terms) is not reachable from the guess. Measuring first also produced the fixture's exact RED evidence |
| Apply the existing `visit_literal` separator-protocol pattern rather than write a new helper (Phase 34) | `visit_math` was the one visitor pair never retrofitted; reusing the already-tested pattern keeps the mitex/native branch and label emission byte-unchanged | ✓ Good: +45 lines total, zero new helpers, no regression against the pre-fix baseline (NEW-failures empty) |
| `visit_math_block` participates in the list-item protocol only, not the code-mode concat protocol (Phase 34, D-01) | A block node is never a concat-context sibling — emitting a `+` operator around it would be wrong | ✓ Good |
| Defer WR-01 (`visit_math_block`'s redundant blank line) to a todo rather than fix it in the release phase (Phase 35, D-05) | Cosmetic; fixing it would force re-deriving the GATE-01 fixture's expected strings and re-running the full-corpus gate immediately before a release | ✓ Good: kept the hotfix release fast, and the deferral is a filed record rather than a lost one |
| Keep REL-03 at `[ ]` through the release-prep phase; flip it only at close (Phase 35, D-10) | Prep completion is not a publish. The v0.6.4 REL-02 precedent | ✓ Good: the scope fence was provable — empty `git tag -l` / `git ls-remote --tags` at phase end meant nothing needed unwinding. Note `phase.complete` tries to auto-flip this; the flip was reverted and re-applied here at close |
| Close v0.6.5 as `override_closeout` without a `MILESTONE-AUDIT.md` (owner decision, 2026-07-29) | A 2-phase / 2-requirement hotfix where `init.manager` reported both phases verified and `35-RELEASE-EVIDENCE.md` had already re-run the full suite, the lint/type trio, the full-corpus gate, and both docs dogfooding builds live on the post-bump tree | — Pending: v0.6.3's audit-less close taught that gates miss what only a question surfaces; the cheap check here was Phase 35's live docs-build pair, which v0.6.3 lacked |
| Sphinx's LaTeX-rendered PDF is a **reference, not an authority** (v0.7.0 scoping, 2026-07-29) | No success criterion is "matches the reference page-by-page"; its measured values (indent quantum, font roles, colour buckets) are design inputs, and each criterion is either mechanically checkable or an explicit visual sign-off | ✓ Good: the reference's `master`-vs-`v9.1.0` version skew became moot the moment it was demoted, and the one `[V]` requirement (ADM-04) closed on an owner sign-off against a real desaturated render rather than on a comparison |
| Redefine GATE-01's RED state for the milestone: structural / regex / `pypdf`-text assertions written **before** any code (milestone invariant #4) | Every prior fixture in this project proved a compile fatal, but every v0.7.0 design defect *compiles successfully today* — regenerating expected strings from the new code's own output would launder the gate | ✓ Good, and it held under pressure: in Phase 40 four of nine gate selectors stayed RED after the handlers landed and all four were defects in the gate module itself; the corrected module was re-proved 9/9 RED against the pre-fix translator three independent times rather than accepted because it now passed |
| Ship the good-looking output typsphinx itself produces; **do not** make the styling user-overridable (owner decision, 2026-07-29) | Research measured that the shape the goal wanted is impossible — Typst's `show`/`set` selectors accept only element functions, and user-defined element types are unimplemented upstream (`typst/typst#147`, open since 2023-03-22, no committed timeline) | ✓ Good: STY-01/STY-02 filed as Future with the measured label-selector mechanism recorded, so nothing was lost; a bundled style module was dropped with them and every emitted `.typ` stays self-contained |
| Reverse locked decision D-03 mid-phase and split the red admonition bucket into three distinct clue functions (owner, 2026-08-02, D-03-R) | Shown a live A/B/C render at UAT, the owner judged the collapsed red bucket wrong. Phase 39 was re-opened *after* it had closed 5/5 rather than filing the difference as debt | ✓ Good: plans 39-09..39-13 closed it with a fresh RED, ADM-04 re-signed-off against a post-reversal render, and the corpus gate re-run green — the closed-phase gate was overridden deliberately, on evidence |
| Block the v0.7.0 publish on Phase 42 rather than shipping first and fixing after (owner, 2026-08-03) | Backlog item 999.2 was a compile fatal, and the milestone's own standard is that output compiles. Promoting it took v0.7.0 from 7/7 to 7/8 and `REQUIREMENTS.md` from 32 to 33 v1 requirements | ✓ Good: Phase 42's SC#6 carried the reconciliation Phase 41 would otherwise have owned (its CHANGELOG entry and invariant sweep were both measured against a tree predating Phase 42), so the release notes shipped complete |
| Keep REL-04/REL-05 at `[ ]` through the release-prep phase; flip only at close (Phase 41, repeating the Phase 35 D-10 precedent) | Prep completion is not a publish, and REL-04's body swap is first *exercised* by the same tag push REL-05 describes | ✓ **Vindicated harder than intended.** The reasoning was exactly right: the tag push *was* the first exercise, and it failed. Flipping REL-04 at prep time would have shipped a false Complete. As it went, both were flipped at the close before the publish, and REL-04 had to be flipped back when the run failed — so the lesson tightens to: at a close that performs a publish, flip a publish-gated requirement **after** the run is green, not before it starts. The auto-flip hazard was separately made falsifiable by `42-CLOSEOUT-GUARD.md` and did not recur |
| Close v0.7.0 as `override_closeout` without a `MILESTONE-AUDIT.md` (owner decision, 2026-08-04) | `init.manager` reported all 8 phases `phase_complete=true` / `verification_status=passed`, and every v1 requirement except the two publish-gated REL rows was already Complete before the close began | — Pending (second consecutive milestone closed this way; if a gap surfaces post-release, revisit whether the audit should be mandatory for multi-phase milestones) |
| Repair the v0.7.0 GitHub Release by hand and revert REL-04 to Pending, rather than moving the published tag to re-run the workflow (owner decision, 2026-08-04) | Moving a tag that PyPI has already published against risks a duplicate-upload failure and rewrites published history; repairing the artifact makes the release correct for users today, while leaving REL-04 open keeps the record honest about what the automation has actually done | — Pending: closes when the next real tag push runs `create-release` to completion |
| Never push the milestone branch until the release PR (v0.7.0, emergent — not a deliberate decision) | — | ⚠️ **Revisit — done, and it worked.** Both defects found at the v0.7.0 close were invisible until the branch was pushed: the Windows cp1252 test failure and REL-04's `uv: command not found`. v0.7.1 turned this into milestone invariant #5 (push from Phase 43, not at the release PR) and the invariant paid: a Windows-only path-separator defect in the contract-claims gate surfaced on a dispatched CI run during Phase 46 rather than at the release PR |
| Make "push the milestone branch to `origin` from the FIRST phase" milestone invariant #5 (v0.7.1, 2026-08-04) | Both v0.7.0 close defects shared one cause — the branch was never pushed until the release PR, so neither Windows CI nor a real tag push ran against it during eight phases | ✓ Good: Phase 43 carried it as SC#5 and pushed in wave 1 (dispatching `ci.yml` by hand, since the push trigger does not fire for this branch name). Phase 46's Windows-only defect was caught by a dispatched run and fixed before the release PR existed |
| Keep Phase 46 prep-only with an absolute scope fence, and hold REL-04/REL-06 at `[ ]` until the publish actually succeeds (v0.7.1, D-03 + roadmap constraints #2/#3) | v0.7.0 reported REL-04's mechanism done on the strength of the workflow file being correct, and the release then failed. The only evidence that closes REL-04 is generated by the publish | ✓ **Good — and the hazard it guarded against recurred.** `phase.complete` auto-flipped REL-06 to `[x]` and `close_phase_todos` moved the REL-04 todo to `completed/` at Phase 46 close-out; both were caught by the diff-before-trusting guard carried from `41-HANDOFF.md` and reverted (commit `73d6a86`). That makes the auto-flip hazard three-for-three on release-prep phases. The rows were flipped only after run `31462027486`'s `create-release` reported success |
| Decline a fail-loud shim for the removed `typst_authors` (owner, D-03) | Adding a `typsphinx/` shim in Phase 46 is exactly the class of code change the prep-only fence excludes; the alternative was resequencing a closed phase | ⚠️ **Revisit in the next milestone.** The silent-loss failure mode is real and measured — a `conf.py` still setting `typst_authors` gets no error and loses its author information — and a removal is precisely the change that most needs a shim. v0.7.1 shipped without one |
| Ship the two `_track_image()` defects unfixed, with no `### Known Limitations` CHANGELOG section and no GitHub issue (owner, D-27) | Argued in full against the counter-case (regression in failure mode, non-exotic reachability, silent wrong output being the failure class this project's core value names directly, the `CHANGELOG.md:817` precedent, an otherwise-empty public issue tracker) and declined; fixing them in Phase 46 would contradict D-03's own reasoning | ⚠️ **Revisit.** Both records stay in `todos/pending/` and are named in this file's Active candidates. The major one is a regression in failure mode — the same project used to abort loudly and now renders the wrong picture silently |
| Rename `tox-uv` to `tox-uv-bare` rather than set `TOX_UV_PATH` in `flake.nix` (v0.7.1, QUA-04) | The rejected alternative was measured working and declined: it repairs `tox` only, leaves the pytest failures untouched, and is a NixOS-local workaround rather than a fix | ✓ Good: one dependency name fixed both symptoms at the root. All four tox environments provision with no override, and the full suite under an outer `uv run pytest` went 45 failures → 0 — which also retired the five Phase 45.1 deferred items rather than carrying them |
| Close v0.7.1 as `override_closeout` without a `MILESTONE-AUDIT.md` (owner decision, 2026-08-11) | Third consecutive close taken this way. `init.manager` reported all 8 phases `phase_complete=true` / `verification_status=passed`, 17/19 requirements were already Complete, and the 2 remaining were the publish-gated REL rows the close itself discharges | — Pending. The v0.7.0 entry above said "if a gap surfaces post-release, revisit whether the audit should be mandatory" — none surfaced from the v0.7.0 close, and v0.7.1 shipped with zero known gaps |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-15 at the **v0.8.0 milestone close** (`/gsd-complete-milestone`) — full evolution review complete. **v0.8.0 multi-master composition SHIPPED**: 6 phases (47-52), 45 plans, 121 tasks, 24/24 v1 requirements complete, zero known gaps. PyPI `typsphinx 0.8.0` published by release run `31861043480` (all five jobs `success`, `create-release` included — the job that failed at the v0.7.0 close, observed directly rather than assumed); GitHub Release body byte-identical to the CHANGELOG extractor over its first 70 lines; `typsphinx-doc-translations` pin advanced to `78e01e5` and tagged `v0.8.0` via its own dispatched `update-pin.yml`; Read the Docs `stable` measured live on both projects at `0.8.0` with both PDFs served. Roadmap and requirements archived to `milestones/v0.8.0-*`; phase directories to `milestones/v0.8.0-phases/`; `REQUIREMENTS.md` removed via `git rm` for the next milestone. Requirements Active carries v0.8.0's completed list until `/gsd-new-milestone` re-scopes it; next-milestone candidates tracked there and in the ROADMAP Backlog. **The close's own carrying lesson:** REL-07 was flipped only after the publish actually succeeded, and the `REQUIREMENTS.md` checksum recorded in `52-HANDOFF.md`'s closeout guard (`566859ea…`) still matched immediately before the flip — the prep phase's fence held end to end. Phase numbering continues at **53**. Prior footer retained below.*

<!-- Prior: *Last updated: 2026-08-15 — **Phase 52 complete** (v0.8.0 Release Prep, prep-only; 9 plans across 6 waves — 7 authored plus 52-08 and 52-09 added mid-phase on owner authorization — `52-VERIFICATION.md` `passed` 9/9 must-haves with no gaps and no human verification required, `52-REVIEW.md` 0 critical / 1 warning / 1 info). The tree is bumped to `0.8.0` across all three release surfaces with the editable install regenerated, the curated `## [0.8.0]` entry carries both breaking callouts with `RELEASE_VERSIONS` at 14, and the milestone's central claim rests on a real multi-master round trip rather than unit-level fixture passes — `TestThreeMasterGate` gained a page-level completeness proof (every master's full include set in its own PDF, nothing outside it, no cross-master leakage), extending the existing class in place after the researcher measured that `52-CONTEXT.md`'s D-10 had named the wrong module. Zero lines under `typsphinx/`. **REL-07 remains open** — it closes at the publish. **Four things are worth carrying forward.** First, **milestone invariant #5 paid four times over**: the dispatched CI run came back RED on 8 of 12 jobs from four real pre-existing defects local execution structurally could not see, and the phase's honest CI history is three runs — RED → 11/12 → GREEN 12/12 — recorded as append-only sections rather than collapsed into a clean final run. Second, **a test had been comparing against hardcoded Japanese Sphinx warning text** since Phase 49; every English-locale runner failed it, and it reproduces locally in 4 seconds under `LC_ALL=C` — a command no one had run, on a branch whose CI only fires via `workflow_dispatch`. The fix anchors on the parts Sphinx never localizes (the `file:line: WARNING:` prefix and the bracketed tag) rather than swapping Japanese literals for English, which would only have relocated the dependency. Third, **`ruff` has been unrunnable on this machine since Phase 45.2**, so an `I001` violation sat undetected in `tests/test_builder.py` — the precise gap D-08's "lint authority sits with CI" assignment exists to cover. Fourth, **the test fix was not allowed to erase the finding**: CPython 3.13's `ntpath.isabs()` change (driveless paths no longer absolute) exposed that `builder.py:910` uses bare `path.isabs()` while its sibling at ~112 deliberately uses `posixpath.isabs(...) or _is_drive_qualified(...)`; the owner chose the test-side route to preserve the prep-only fence, so the product inconsistency was filed as a todo — a green CI with that knowledge lost would have been worse than a red one. The `phase.complete` auto-flip is now **four-for-four on release-prep phases**: it flipped REL-07 against the phase's own decision, the ROADMAP's own text and `52-HANDOFF.md`'s closeout guard, and diff-before-trusting caught it — `REQUIREMENTS.md` restored to a byte-identical checksum. Seven deferred todos stay open, each named individually in the handoff. Milestone v0.8.0 is ready for `/gsd-complete-milestone`. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-08-15 — **Phase 51 complete** (Two-Layer Output Documentation; 6 plans across 3 waves, 1/1 requirement ID DOC-14, `51-VERIFICATION.md` `passed` 3/3 success criteria with no gaps and no human verification required, `51-REVIEW.md` 1 critical / 1 warning). The two-layer output shape is documented rather than discovered: `docs/source/user_guide/output_layout.rst` names the wrapper and content layers, says the wrapper is the file to compile, and states standalone-content compilation as intended behaviour in plain prose (D-08); target-as-path ships with built worked examples for the bare and explicit-path cases and all three refusal shapes, plus the Phase 47 collision abort and Phase 49's shared-child consequence; `changelog.rst` states the v0.7.x change in old→new file names beside v0.7.1's own rename. A permanent 13-test gate over five fixtures binds the prose to real `-b typst` builds, never skips, and needs no `typst-py`. Suite 1156 → 1173 passed. Zero lines under `typsphinx/`. **Four things are worth carrying forward.** First, and most important: **the phase's own defect class survived all six plans and its own gate.** Four published file-set claims omitted `_template.typ` — which every wrapper `#import`s, so removing it makes the wrapper fail to compile — and the contract page therefore contradicted *itself* (its file-count rule counted the file; its opening worked example did not) *and* its own passing test, because no test bound a prose file-count to a measured file set. The post-phase code review caught it; execution did not. Second, **a gate assertion was independently vacuous**: `assert "ten" in text` is satisfied by `"written"` and `"content"`, so the one numeric claim it nominally protected was never checked — the replacement was **mutation-proved** (wrong number FAILS, sentence deleted FAILS, old assertion demonstrably passes on that same deletion) rather than merely observed passing, since re-observing a green test cannot distinguish a fixed assertion from a differently-vacuous one. Third, **the completeness audit was required to derive its search set from the claim patterns rather than from the earlier plans' file lists**, and that instruction is what surfaced two residuals in files no plan had declared — deriving the search set from the text being corrected would have inherited the same blind spot one level deeper. Fourth, **the parallel wave's real collision was not in `files_modified`**: the four Wave-2 plans had provably disjoint file scopes and still broke the build at merge, because one plan changed `README.md` while a test file it did not own asserted a pinned link inventory over that same file — post-merge testing, not scope analysis, is what catches this. The `phase.complete` auto-flip was diffed before trusting for the sixth consecutive close-out; this time it touched `REQUIREMENTS.md` not at all (DOC-14 was already closed by 51-06). One adjacent `conf.py`-drift finding in `examples/advanced/README.md` was surfaced and deliberately left by owner decision. Prior footer retained below.* -->

---
*Prior: 2026-08-14 — **Phase 50 complete** (PR #131 Image Path Defects; 3 plans across 3 waves, 2/2 requirement IDs IMG-01/IMG-02, `50-VERIFICATION.md` `passed` with `overrides_applied: 1`, `50-REVIEW.md` 1 critical / 1 warning / 1 info). Both defects PR #131's review filed against its own code are closed as one change to `TypstBuilder._track_image()`'s absolute-URI branch, relocating a srcdir collision silently and an outdir escape or cross-drive `ValueError` with a warning, all through one reserved `_typst_converted/` namespace; the collision test is a filesystem probe rather than a `self.images` membership check, so the outcome does not depend on `sorted(docnames)` order. Suite 1150 → 1156 passed with every increment accounted for; D-12 fixed points byte-unchanged; D-11 two-build manifest diffs empty. **Three things are worth carrying forward.** First, the RED held as an immovable target: wave 2's entire diff to the gate module was removing two `xfail` decorator lines, with zero assertion text or expected value changed — verified by diff, not asserted, and the same check confirmed wave 3's four unit tests never reference `RESERVED_IMAGE_NAMESPACE` and so are not tautological. Second, **two planning documents were contradicted by measurement and neither was edited to match**: RESEARCH.md cited a live `.. figure::` at `docs/source/examples/basic.rst:128` that is actually inside a `.. code-block:: rst` fence — `docs/source` holds zero image assets at all, so SC#3's image claim rests on the D-12-pinned render gates and not on the two-build manifest it nominally cites — and the manifest recipe swept Sphinx's non-reproducible `.doctrees/` cache, proven by a third identical-code build before being narrowed; both were recorded as disclosed caveats rather than smoothed away. Third, **the fix reintroduced its own flagship failure shape one level deeper and the review lenses split on severity**: the escape branch keys on `path.basename()` alone, so two escaping images sharing a basename across directories collide onto one key — Critical to code review, `low / accept` to the phase's own T-50-03 threat model, which had pre-disclosed it with a hashed-key remedy. Two items ship tracked by owner decision: that collision as a follow-up todo (`resolves_phase: null`, carrying the remedy and a RED-first instruction), and IMG-02's missing written-first RED, closed by an explicit scoped override recording that the pre-fix observation exists and pre-dates the fix by four days in the 2026-08-10 todo's direct measurement — what was missing was its packaging as a pytest artifact, not the observation — with the residual named: IMG-02's branches are GREEN-only here, so a future rework must record its own RED. The `phase.complete` auto-flip was diffed before trusting for the fifth consecutive close-out; this time it was correct (IMG-01/IMG-02 genuinely closed, no unrelated deferred ID touched). Prior footer retained below.*

<!-- Prior: *Last updated: 2026-08-14 — **Phase 49 complete** (Per-Master Include Graph with State-Guarded Includes; 6 plans across 5 waves, 8/8 requirement IDs COMP-05..12, `49-VERIFICATION.md` `passed` 5/5 success criteria, `49-UAT.md` 2/2 dispositioned, `49-REVIEW.md` 0 blockers / 2 warnings). The include decision moved from write time to compile time; the `_included_docnames` ledger is deleted; defect A and the diamond are closed on `pypdf`-read PDF evidence rather than on inspection. **Three things are worth carrying forward.** First, the phase spent its entire first wave writing down what everything should be — the emission contract measured against nine real `typst.compile()` probes, the fixture specification, the degenerate-shape outcome table, and a repo-wide assertion census over 19 modules — so waves 2-3 transcribed expected values instead of deriving them, and the 16 post-fix assertions sat as `xfail(strict=True)` naming their own fix plan until it landed. Second, **two measurements contradicted the phase's own planning documents and neither was edited to match**: `:numref:` case (b) does emit a Sphinx warning where D-01 and the expected-structure document both asserted "zero warning" (traced to `_resolve_numref_xref`'s `except ValueError` branch in the installed Sphinx 9.1.0), and the corpus gate ran ~50% faster than Phase 48's baseline — which was checked for the silent-omission failure mode this phase forbids by building the corpus pre- and post-phase with one identical probe (15,422,134 → 15,412,931 bytes, `.typ` count 156 → 156; not content loss). Third, **an executor flipped three requirement IDs to Complete while every corresponding assertion was still a strict xfail**; the orchestrator caught it by diffing the merged tracking files and reverted, which is the same diff-before-trusting guard that has now paid off on four separate close-outs. Three findings ship tracked rather than fixed by owner decision: the `:numref:` divergence (`resolves_phase: 52`, naming both the Phase 51 docs and Phase 52 CHANGELOG obligations so neither goes dark), the edge-key separator collision, and the unbounded traversal recursion. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-08-14 — **Phase 48 complete** (Compile-Time Cross-Reference Guard; 7 plans, 2/2 requirement IDs, `48-VERIFICATION.md` `passed` 19/19, `48-UAT.md` 16/16, `48-SECURITY.md` `threats_open: 0`). Label existence is now decided by Typst per compiled wrapper through one shared `_label_existence_guard()` helper; the build-time `master_included_docnames` union is gone. UAT caught a pre-existing whole-document `:doc:` dead-link defect (G-48-4, live since Phase 15) which three gap-closure plans closed with a per-document self-anchor — the project's own PDF went from 40 broken file-URI links to 5, the remainder being Sphinx's virtual pages, left dead by owner decision.* -->

<!-- Prior: Last updated: 2026-08-11 at the **start of milestone v0.8.0** (`/gsd-new-milestone`) — **v0.8.0 multi-master composition** scoped. A `typst_documents` configuration declaring more than one master is broken in three ways, all growing from one root: a single `.typ` per docname shared by every master. The milestone re-shapes composition into per-master wrapper files carrying the template and the toctree include graph, plus template-less docname-named content files — closing the include-path/filename mismatch (`file not found`), the mid-body template re-expansion, and the silent loss of a document toctree'd by two masters. Duplicate-target detection, a `context` + `query` compile-time cross-reference guard (needed because fixing the include graph turns a silent omission into a hard compile failure), and the two `TypstBuilder._track_image()` defects shipped unfixed in v0.7.1 by decision D-27 ride along. **Every premise was measured live on the current tree during scoping** rather than taken from the todo records — including the reproduction of all three defects, the confirmation that masters compile to independent PDFs (which is what licenses expanding one content file into several wrappers), and a comparison against Sphinx's own LaTeX builder, which composes at the doctree layer and is therefore immune to two of the three but carries the duplicate-target bug identically. The LaTeX model was considered and **rejected**: adopting it would delete the per-document `.typ` files the `-b typst` builder exists to produce, so this milestone stays at the file layer and reaches the same result. Version is **v0.8.0, not a patch** — `manual.typ` stops being the whole document and becomes a wrapper, a user-visible output-shape change. Phase numbering starts at **47**. Prior footer retained below. -->

---

*Last updated: 2026-08-15 — started milestone **v0.9.0 per-document templates** via `/gsd-new-milestone`. Scoped over an extended measured discussion in which four of my own framings were corrected against the source rather than accepted. **The 5th `typst_documents` element is not a hypothetical slot**: `_default_typst_documents()` emits `"typst"` into it (`builder.py:184`), `docs/source/conf.py` and both `examples/charged-ieee` configs set it, and `configuration.rst:80` defines it as "accepted and ignored" — so making it the registry key is a promotion of an existing populated placeholder, not a tuple extension, and `"typst"` deferring to global config is what keeps every existing `conf.py` working untouched. **`typst_template_mapping` genuinely duplicates `template_function`** and is strictly weaker (a rename table over the three-key dict built at `writer.py:365`, discarded wholesale by `render()`'s D-B/D-D branch whenever `params` is declared), so the registry is function-only and the global value will be removed in a later milestone — untouched here. **The template-asset spec was already per-template**: `_copy_template_directory()` copies the *directory* containing the template and mirrors srcdir structure, so no new config is needed — only the enumeration source changes, and `copy_template_assets()`'s early return on an unset global `typst_template` would otherwise make a registry-only project silently copy nothing. **Root placement was not forced**: writing each registry template into its own source directory's mirror puts it beside its assets, making `#image("logo.png")` work and `templates.rst:106-113`'s currently-wrong example correct, while `"typst"` keeps the root `_template.typ` so `docs/source` and `approach2` are unaffected. Deliberately NOT fixed: the P×A cell (a package with no declared `params` emits a compile fatal for any master with a toctree, because `typst_elements` and `params.update(toctree_options)` both escape the D-05 suppression) — owner decision, and the reason `approach1` uses the `params` route. Five v0.8.0-derived defects ride along. Next: define REQUIREMENTS.md, then the roadmap. Prior footer retained below.*

---

<!-- Prior: *Last updated: 2026-08-11 at the **v0.7.1 milestone close** (`/gsd-complete-milestone`) — full evolution review complete. **v0.7.1 (bug-fix round) shipped: 8 phases (43–46, incl. inserted 44.1, 44.2, 45.1, 45.2) / 43 plans / 122 tasks, 19/19 v1 requirements validated, zero known gaps, `override_closeout`.** PyPI `typsphinx 0.7.1` is live (wheel 135,318 B + sdist 580,288 B) via release run `31462027486`; PR #132 merged with 15/15 CI checks green (`48bf135`), tagged `v0.7.1`, and `typsphinx-doc-translations` took its standing second tag after `update-pin.yml` run `31462409929` advanced the pin `87f242a` → `48bf135`. **This milestone closed the gap between what the documentation promises and what a `conf.py` gets**: `typst_documents` gained a LaTeX-shaped default so the Quick Start produces a PDF, an explicit entry's title and author reach the rendered document, the custom-template parameter contract was rewritten onto the nine parameters actually passed and locked with a RED-proved gate, `typst_authors` was removed, nested tables and figures stopped corrupting the enclosing structure, and the published changelog page stopped being two years stale by rendering live from `CHANGELOG.md`. Four things are worth carrying forward. **REL-04 finally closed, and closed correctly**: carried unmet from v0.7.0 where it was reported done on the strength of the workflow file, it was here proved by a real tag push whose `create-release` completed success, with the published body then *measured* byte-identical to the extractor's output rather than assumed. **Milestone invariant #5 paid immediately**: pushing the branch from Phase 43 surfaced a Windows-only defect on a dispatched CI run in Phase 46, not at the release PR — the exact failure mode that cost v0.7.0 two defects. **The `phase.complete` auto-flip hazard is now three-for-three on release-prep phases**: it flipped REL-06 and auto-closed the REL-04 todo at Phase 46 close-out, and the diff-before-trusting guard caught both again (`73d6a86`). **A root-cause fix retired five deferred items**: renaming `tox-uv` to `tox-uv-bare` (QUA-04) took the full suite from 45 failures to 0 and made `tox` work locally for the first time, dissolving the Phase 45.1 deferrals rather than carrying them. Archived to `milestones/v0.7.1-ROADMAP.md` + `v0.7.1-REQUIREMENTS.md` with phase artifacts under `milestones/v0.7.1-phases/`; `REQUIREMENTS.md` removed for the next milestone. **Nine todos and two dormant seeds stay open, every one argued in `46-HANDOFF.md` before the close** — the `typst_documents`-modelling cluster of three, the two `_track_image` defects shipped unfixed by decision D-27, and the declined `typst_authors` fail-loud shim are this file's named Active candidates. Next milestone starts at **Phase 47**. Prior footer retained below.* -->

---
*Prior: 2026-08-11 — Phase 46 (v0.7.1 Release Prep, prep-only) complete, 6/6 plans across 4 waves, verification `passed` 5/5 success criteria, code review 0 critical / 3 warning / 2 info. **Every v0.7.1 phase is done — the milestone is prepped, proven green, and awaits `/gsd-complete-milestone`.** The tree is publish-ready with zero irreversible action taken: `git tag -l v0.7.1` and `git ls-remote --tags origin v0.7.1` are both empty, verified twice by the phase 3m4s apart and a third time by the verifier independently. `pyproject.toml` is the sole `0.7.1` literal with `uv.lock`/`README.md` in lockstep and `typsphinx.__version__` regenerated to match; the curated `## [0.7.1]` CHANGELOG entry marks both user-visible patch-release behaviour changes (CONF-08's filename rename, CONF-09's title/author change) three ways, since D-01 held the version at `0.7.1` and the number itself warns no one. **SC#3's proof is a live CI run because it has to be** — local sees neither Windows nor macOS and `tox -e lint` cannot execute on this machine at all — so D-23 dispatched two: run `31456868265` first, to confirm a Windows-only path-separator repair that is unverifiable locally, placed at the head of the phase so a missed repair could not land retry commits after the bump; then run `31458368833` on pushed SHA `26b2e6c`, carrying the bump and the changelog entry, 12/12 green, re-fetched by the verifier rather than read from the transcript. **Two requirements deliberately did not close and that is the design.** REL-04's acceptance evidence is a real tag push whose `create-release` job completes — v0.7.0 called this mechanism done on the strength of the workflow file and the release then failed, and this phase was fenced so it could not repeat that; REL-06's own text ends "*and the publish … executed at `/gsd-complete-milestone`*". **The recorded `phase.complete` auto-flip hazard recurred and was caught again**: close-out flipped REL-06 to `[x]` and auto-closed the REL-04 todo on a `resolves_phase: 46` line predating the prep-only scoping; both were reverted via the diff-before-trusting guard `46-HANDOFF.md` item 6 carries from `41-HANDOFF.md`, making the hazard three-for-three on release-prep phases specifically. **A plan-verification defect was found twice independently and corrected rather than scored as a gap:** `git diff origin/main..HEAD -- typsphinx/` is unsatisfiable under `branching_strategy: milestone` (the merge-base predates Phase 43), and the corrected anchor `c72be91..HEAD` is genuinely empty; both forms are recorded verbatim rather than the literal being quietly swapped. Code review: 0 critical, and two of three warnings belong to PR #131's `_track_image` — which this phase merged but, under the prep-only fence, could not fix — both filed as todos. `46-HANDOFF.md` carries the seven-item publish checklist. Prior footer retained below.*

---
<!-- Prior: *Last updated: 2026-08-04 at the **start of milestone v0.7.1** (`/gsd-new-milestone`) — a bug-fix round scoped by the owner from the carried ledger, starting at **Phase 43**. Nine items in scope: REL-04 (the sole unmet v0.7.0 requirement, closable only by a real tag push at `/gsd-complete-milestone` — no rehearsal mechanism, owner decision); the two table defects Phase 42's review filed (`nested-table-clobbers-outer-table-state`, a real and severe **pre-existing** bug where scalar table state lets an inner `list-table` table tear down the outer one, and the whitespace-only-caption anchor divergence); the docs changelog page frozen at 0.4.0 with 12 releases missing; SEED-001's first-run onboarding break; and four small carried todos (the `_emit_id_anchors` docstring, non-`str` docname `TypeError` hardening, `derive_typst_lang()`'s duplicated warning block, and this file's two unterminated HTML comments). **SEED-001's direction was decided by measurement, not preference:** the owner's stated rule was "check whether Sphinx's LaTeX builder requires `latex_documents`," and a live probe against Sphinx 9.1.0 with an empty `conf.py` resolved `latex_documents` to `[('index', 'probeproject.tex', 'Probe Project', 'Probe Author', 'manual')]` — LaTeX registers the callable default `default_latex_documents` and does **not** require the setting. typsphinx follows suit, with LaTeX's own target shape `<project>.typ`. **The accepted cost was stated before the choice and taken anyway:** that shape **renames** existing `-b typst` output for users who never set `typst_documents` (`index.typ` → `typsphinx.typ`), which is a user-visible behavioural change inside a patch version. The owner was shown the alternatives (bump to v0.8.0, or derive `<root_doc>.typ` and rename nothing) and chose v0.7.1 with a CHANGELOG call-out, on the framing that the renamed path produced no PDF at all before. Explicitly NOT in scope, and not to be picked up opportunistically: `modernize-typing-imports-drop-up006-up035-ignore` (`CLAUDE.md` independently forbids it) and LNK-01. Prior footer retained below.* -->

---
*Last updated: 2026-08-04 at the **v0.7.0 milestone close** (`/gsd-complete-milestone`) — full evolution review complete. **v0.7.0 (API rendering design overhaul) shipped: 8 phases (36–42, incl. inserted 40.1) / 57 plans / 158 tasks, 32/33 v1 requirements validated (REL-04 carried to v0.7.1), `override_closeout`.** API reference pages became readable: monospace signatures with hanging-indent wrapping and no margin overflow, description bodies and field lists indenting by nesting depth off one shared `SHARED_INDENT_STEP` constant, admonitions re-bucketed onto a taxonomy the owner signed off against a desaturated render, greenfield full-round-trip docutils citations (a citation previously aborted the compile outright), and two remaining compile fatals closed (MATH-02, TBL-03). Zero new runtime dependencies; the `@preview` package count stayed at four with no new version-lockstep site; every node-handler change carries its own recorded-RED GATE-01 fixture. Three things are worth carrying forward. **The gate held under pressure rather than being laundered**: in Phase 40 four of nine selectors stayed RED after the handlers landed, all four were defects in the gate module itself, and the corrected module was re-proved 9/9 RED against the pre-fix translator three independent times before being trusted. **A locked decision was reversed on evidence**: shown a live render at UAT the owner overturned D-03 and re-opened an already-closed Phase 39 rather than filing the difference as debt. **A recurring tooling hazard was made falsifiable**: `phase.complete` auto-flipping REL-04/REL-05 was caught and reverted in Phase 41, then pre-empted in Phase 42 by `42-CLOSEOUT-GUARD.md` recording the four at-risk lines verbatim with a checksum — and it did not recur. Archived to `milestones/v0.7.0-ROADMAP.md` + `v0.7.0-REQUIREMENTS.md` with phase artifacts under `milestones/v0.7.0-phases/`; `REQUIREMENTS.md` removed for the next milestone. **One requirement did not close: REL-04.** Its extractor is correct and hand-verified, but the first real tag push failed because the `create-release` job calls `uv run` without an `astral-sh/setup-uv` step (run `30848860064`, exit 127) — PyPI published, the GitHub Release did not. The v0.7.0 release body and assets were repaired by hand and `release.yml` fixed on `main`; REL-04 closes when a real tag push exercises it end to end, so it is the sole item in Requirements Active. Carried candidate scope (5 deferred todos, SEED-001, Future STY-01/STY-02/TOP-01) is listed under Current Milestone. **Both defects this close surfaced — REL-04's and the Windows cp1252 test failure — share one cause: the milestone branch was never pushed until the release PR, so neither Windows CI nor a real tag push ran against it during any of the eight phases.** Next milestone starts at **Phase 43**. Prior footer retained below.*

<!-- Prior: *Last updated: 2026-08-04 — Phase 42 (Captioned Table Drops Preceding Target Label) complete, 6/6 plans across 3 waves, verification `passed` 6/6 success criteria, TBL-03 validated. **All eight v0.7.0 phases are done (36, 37, 38, 39, 40, 40.1, 41, 42), 57/57 plans — the milestone is prepped, reconciled and awaits `/gsd-complete-milestone`.** The defect was not a misplaced anchor but a **discarded** one, and naming that correctly is what made the fix one call site instead of a rewrite: `depart_table`'s trailing `_emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` fired while `self.in_table` was still True, so `add_text()` diverted the propagated-target anchor into `self.table_cell_content` — a buffer `del`eted a few statements later and never read again. Moving that one call past `self.in_table = False`, gated on a `was_captioned` boolean captured before `self.table_caption` is reset, is the entire production change; `typsphinx/translator.py` is the only source file the phase touched, in a single commit. **The phase's discipline was ordering, and it is falsifiable rather than asserted.** TBL-03 is milestone invariant #4's second classic-RED exception (alongside CIT-01) because it fails the Typst compile rather than compiling wrong, so the RED had to be a real `TypstError` recorded against unfixed code: `git merge-base --is-ancestor` confirms the RED commit is a strict ancestor of the fix commit, and wave 1 left `typsphinx/` byte-unchanged, so the RED genuinely predates the fix. Suite went 7 failed / 814 passed (all 7 inside the new gate module, 0 elsewhere) → 821 passed / 1 skipped / 0 failed. **Two open questions were closed by measurement instead of inference.** Captioned figures do *not* share the drop (SC#2) — answered with a real build, and a permanent figure-side gate now stops a future change from copying the table path's defect back into the image path. A sweep of all 21 `_emit_id_anchors` call sites found `depart_table` the sole misrouted one, with the image path a recorded null result rather than an unexamined assumption. **SC#4's proof carries its own positive control**, which is the part worth carrying forward: an empty caption-less diff proves nothing if both builds imported the same `typsphinx`, so the evidence records two distinct resolved `typsphinx.__file__` paths *and* a deliberately non-empty diff for the captioned shapes before presenting the empty one. **The REL-04/REL-05 auto-flip hazard did not recur this time.** Phase 41 was hit by it and reverted; Phase 42 armed `42-CLOSEOUT-GUARD.md` with the four at-risk lines recorded verbatim plus a checksum, and the post-`phase.complete` diff came back containing exactly the two legitimate TBL-03 lines with REL-04/REL-05 byte-identical — so the hazard looks specific to release-prep phases rather than universal, and the guard is now a concrete baseline to diff against instead of a remembered warning. **Two findings are deliberately left open.** Code review WR-01 (the `_emit_id_anchors` docstring still calling `depart_figure` the "sole user" of `skip_ids`, false since Phase 25) was not fixed here because touching `translator.py` after the SC#4 and SC#6 artifacts were recorded would move the change outside the SHA range they measured. IN-02 is a real, severe, pre-existing bug verified byte-identical pre- and post-fix: a table nested inside a `list-table` cell silently drops the outer table structure, because `in_table`/`table_cell_content` are scalars rather than a stack. Neither blocks v0.7.0.* -->

<!-- Prior: *Last updated: 2026-08-03 — Phase 41 (v0.7.0 Release Automation + Release Prep) complete, 7/7 plans across 3 waves, verification `passed` 5/5 success criteria. **All seven v0.7.0 phases are done (36, 37, 38, 39, 40, 40.1, 41), 51/51 plans — the milestone is prepped and awaits `/gsd-complete-milestone`.** REL-04 landed end to end: `release.yml` now sources the GitHub Release body from `CHANGELOG.md`'s curated `## [X.Y.Z]` section through a committed, pytest-covered extractor, the `git log --pretty` commit dump is removed rather than fenced behind a fallback, and a CHANGELOG-existence check sits in the `validate` job strictly upstream of `build` / `publish-pypi` / `create-release` — so a missing section fails *before* PyPI is published to, which is the whole point of the change. REL-05's prep half landed too (0.7.0 as the sole literal in `pyproject.toml`, `uv.lock` + `README.md` in lockstep, curated `## [0.7.0]` entry with its link-block rollover), but **REL-04 and REL-05 are deliberately still `[ ]` / Pending** — their text requires the publish, which is close-side. `phase.complete` auto-flipped all four lines against that decision and the flip was caught by diffing against a pre-run copy and reverted; `41-HANDOFF.md` item 6 had predicted exactly this and told the next run to check. **What is worth carrying is that the phase measured rather than transcribed.** SC#4's invariants were re-derived over the SHA-anchored full milestone diff (394 commits recounted on the spot, not copied from CONTEXT/RESEARCH), and the census honestly surfaced the one thing a softer reading would have buried — `pillow` was added to the `dev` extra in Phase 39 — rather than letting "zero new runtime dependencies" absorb it. SC#3's corpus gate was recorded as **executed**, not skipped. SC#5 proves an *absence* (no tag exists), which no test can assert, so it is two independent observations transcribed verbatim. And the `ja` glyph bar's fourth check is the owner's own eyes: Typst's font fallback is silent — no warning, no error, correct text extraction — and this milestone added 24 `raw(` call sites that resolve to a monospace family with no CJK coverage, so the mechanical checks (94/94 pages, CJK +34, `NotoSerifCJKjp-ExtraLight` present on both sides) were explicitly held to be insufficient on their own. **One defect was found after the plans closed and fixed inside the phase:** the code review caught `${{ }}` expressions interpolated into `run:` blocks in `release.yml` — a tag name containing `$(...)` would execute as code in a job holding `contents: write`. The fix converted *every* shell-context interpolation in that file, not just the one this phase added, because measuring the base commit showed the anti-pattern pre-dated Phase 41 at two further sites including the actual untrusted entry point; repairing only the new line would have been cosmetic.* -->

<!-- Prior: *Last updated: 2026-08-02 — Phase 40.1 (Citation Degradation Hardening, INSERTED) complete, 4/4 plans, verification `passed` 5/5 success criteria. No new requirements — this phase hardens code already delivered under CIT-01/CIT-03/CIT-04 and closes the three warnings `40-REVIEW.md` carried forward (WR-01/WR-02/WR-03), which the footer below explicitly deferred "by decision, not fixed silently." **Six of seven v0.7.0 phases are done — only Phase 41 (Release Automation + Release Prep) remains.** The fixes are small; the discipline around them is the point. **WR-01**: `visit_citation`'s backref loop short-circuited `ref_node is not None and not …` to `False` when `_find_citing_reference` returned `None`, falling through as *eligible* and emitting `link(<docname:refid>, …)` at a label nothing attaches — a whole-document compile fatal, and reachable from an entirely ordinary `.. only:: <undefined-tag>` around a citing `[Label]_`, so its RED landed on a real `sphinx-build` on the first attempt. **WR-02**: `_citation_run_neighbour` exists precisely to keep emit-nothing siblings from breaking a run, but named only `comment`/`system_message`; an ids-less `nodes.target` also emits nothing yet split one reference list into two independently-aligned grids with no error anywhere. **WR-03**: the D-14 anchor judgement was written in two places held together by nothing — `visit_reference` deciding from three conditions, `_citing_reference_has_own_anchor` re-deriving from one and assuming the other two — so it is now one `_reference_anchor_decision` predicate that derives its own inputs (D-06) and returns the anchor *label* alongside the boolean (D-07), with the old helper deleted rather than kept as a delegator (D-05). **What is worth carrying is how the REDs were established when the topology could not be built.** Per D-01 the phase refused "not reproducible" as an answer: WR-02's evidence file enumerates all five plausible RST shapes and the docutils-0.22.4 target-chaining fact that makes the minimal single-blocker topology unconstructible; WR-03's records both D-08 routes and why each is unreachable (Route A a control-flow fact about `_find_citing_reference`'s matching, Route B because a node reachable through it never carries a `refuri`). Only then do the REDs fall back to assembled doctrees — and WR-02's is *structural* (`count("grid(") == 2 → 1`) because that warning compiles cleanly by construction and has no fatal to catch. The RED-before-fix claim was verified mechanically rather than accepted: `git diff --stat` of `typsphinx/translator.py` at each of the three RED-recording commits (`0ebe8c3`, `7aa1fe3`, `ae9a0fe`) against its pre-fix baseline is **empty**. Because WR-03 rewrites `visit_reference` — every link in the codebase, toctree entries included — D-06 re-incurred Phase 40's D-14 non-regression obligation, and the baseline sha256 for that proof was captured in plan 01 Task 1 *before any translator byte changed*, precisely so the later comparison could not be circular; both `index.typ`/`second.typ` came back byte-identical, re-derived independently three times (plan 03, plan 04, verifier). Full suite **799 passed / 1 skipped / 0 failed**; the full-corpus `-b typstpdf` gate **observed green** (4 passed in 14.10s against a cache-hit corpus — the single SKIP is the separate `TYPSPHINX_CORPUS_REPORT=1` diagnostic, and a skipped gate would not have satisfied SC#5); `black`/`ruff`/`mypy` clean. `40.1-NONREGRESSION.md` §4 is a change-site → RED manifest — evidence file, RED form, provenance, pytest selector, and recording commit per row — written for Phase 41's SC#4 sweep to read rather than reconstruct. Code review 0 critical / 1 warning / 1 info, both non-blocking and both adjudicated in verification: **WR-01 is a test-integrity gap, not a behavioural defect** — `_reference_anchor_decision` (and so `_resolve_xref_docname`) runs **twice** per citing reference that has both a `refuri` and a paired citation `backrefs` entry, once from `visit_reference` and once from `visit_citation`'s backref loop, which is currently harmless because the predicate is pure and both calls agree; the problem is that `test_wr03_xref_resolution_happens_once_per_reference` builds no paired citation, so its fixture structurally cannot reach the second call site and would stay green if someone later moved the degrade warning into the shared predicate. Independently instrumented and confirmed: WR-03's own topology → call_count 2, the test's fixture → 1. The logic was unified as D-05 required; the call site was not. IN-01 (out of scope): citations inside a bare `list_item` do not compile at all today, with or without the WR-02 change, so that fix's docstring caveat about weakened list-item inertness currently has zero practical exposure. Next: Phase 41 (v0.7.0 Release Automation + Release Prep) — the milestone's last phase. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-08-02 — Phase 40 (Citations — Full Round Trip) complete, 5/5 plans, verification `passed` 5/5 success criteria + 6/6 requirements. One Active bullet moved to Validated (the citation bullet); CIT-01..CIT-06 all complete. **Five of six v0.7.0 phases are done — only Phase 41 (Release Automation + Release Prep) remains.** The handlers themselves were the small part: `visit_citation`/`depart_citation`/`visit_label` plus a guarded own-`ids` bracket-wrap in `visit_reference` (D-14), +348 lines in `translator.py` and nothing else under `typsphinx/`. **What this phase is actually a lesson about is what happens when the gate itself is wrong.** CIT-01 was the milestone's sole requirement where "does not compile" was available as the RED state (ROADMAP binding constraint #3), and that RED was captured verbatim against a named commit before any handler existed, together with a second independently-isolated pre-fix failure shape — a citation nested in a list item aborts at Typst's *semantic* pass with a missing-label error, not at the syntax fatal. After the handlers landed, four of nine selectors stayed RED, and the executor's claim that all four were test defects rather than translator defects was the most self-serving conclusion available — so it was re-measured rather than accepted. It held: `_leading_columns`, copied verbatim from `test_rubric_indent_invariance.py` where the marker IS the first glyph on its line, returns the LINE's leading whitespace, which in a citation grid is the label's column, so `test_layout_...` compared a label column against a body indent and could never pass in EITHER direction — it was incapable of validating CIT-02 or D-05 at all. A direct `pypdf` layout extraction showed the rendering was already correct: all five entry bodies and every wrapped continuation line at column 28, the widest label occupying 0..27. **Repairing a gate module that two other plans explicitly forbade touching is indistinguishable from laundering a green, so it was made the owner's call, not the orchestrator's**, and executed as a separate gap-closure plan (40-05) under two prohibitions: no observed value transcribed into the module (the number 28 appears in the evidence file and nowhere in the test), and no assertion weakened, skipped, xfailed or narrowed. The plan closed with a re-proof rather than an assurance — restored over the pre-fix translator (`8b22bf6`) the corrected module goes **9/9 RED**, verified three times independently (40-05, orchestrator, verifier). Two further defects surfaced during that work and are the reason the count is six, not four: `_attached_anchor_tokens` recognised only the `<label>` shorthand and not the `#label("…")` form `depart_reference` actually emits, and a `\(\d+\)` single-backref guard both false-positived on body prose ("Hinton, G. E. (2012)") and could never match the real marker shape, since ordinals are emitted inside `[1]`/`[2]` content blocks passed to `link()`. All six are recorded as amendments-against-measurement in Section 8 of `40-GATE-EVIDENCE-01.md` with Sections 1–7 byte-unchanged — the same treatment SC#3 received earlier in the phase when D-08/D-09 narrowed its back-reference claim to docutils' own same-document `backrefs` scope (matching Sphinx's own HTML builder; its LaTeX builder renders no back-references at all). CIT-05 got a RED-to-GREEN gate on real shipped content at zero test cost: both `examples/charged-ieee` samples restored to git blob `82831eb0` — byte-identical to each other again, so template wiring is once more their only intended difference — with `tests/test_examples_charged_ieee_gate.py` re-run and provably never edited across the whole phase. Full suite **783 passed / 1 skipped / 0 failed**; full-corpus `-b typstpdf` gate **re-run for real and PASSED** (the one SKIP in that output is the separate `TYPSPHINX_CORPUS_REPORT=1` diagnostic, not the gate); `black`/`ruff`/`mypy` clean; milestone invariants held — zero new runtime dependencies, `@preview` count still 4. Code review 0 critical / 3 warning / 1 info, all adjudicated real but non-blocking and all outside the eleven-scenario fixture: **WR-01 is the one worth carrying** — a `None` from `_find_citing_reference` falls through as *eligible* instead of being skipped like the adjacent no-anchor case, so it would emit a `link()` to a label nothing attaches, the exact compile-fatal class this phase removed; its reachability is the stale id-registry shape that function's own docstring documents. WR-02: an ids-less `nodes.target` is not treated as an emits-nothing sibling by the run scan and could split one reference list into two grids. WR-03: D-14 eligibility duplicated across two call sites with no enforced invariant. Deferred by decision, not fixed silently. Environment note that recurred again: the `.venv/bin/uv` shim can fail to apply because `command -v uv` resolves to the venv's own stale copy once it is on PATH — symptom is ~45 unrelated integration tests failing under the NixOS stub loader; verify the symlink points into `/nix/store`, not back into `.venv`. Next: Phase 41 (v0.7.0 Release Automation + Release Prep) — the milestone's last phase. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-08-02 — Phase 39 (Admonition Taxonomy + Rubric Nesting) **re-closed after gap-closure round G-39-1**, 13/13 plans, verification `passed` 5/5. The phase had already closed at 8/8 (footer retained below) when conversational UAT surfaced `G-39-1`: shown a live A/B/C render comparison, the owner **reversed locked decision D-03**, splitting the collapsed red admonition bucket into three distinct gentle-clues functions (`danger()` / `memo()` / `error()`). The closed-phase gate (#3569) was explicitly overridden by the owner to plan the closure. **The durable lesson is how the reversal was recorded rather than applied silently:** plan 39-10 touched no code at all — its whole job was to mark D-03 superseded in place, add a dated `D-03-R` beside it, restate ADM-02 around its *intent* (`attention` leaves the orange warning group for the red family) rather than around function identity, and amend ROADMAP SC#1 — every original wording preserved verbatim, zero deletions, so a reader six months out sees both decisions and why the second followed the first. Only then did 39-11 change two call sites. A second-order consequence was recorded rather than quietly fixed: `39-05-SUMMARY.md`'s grep guard "the `danger` id is passed by zero call sites" is now **exactly one** — recorded as an inversion caused by a design reversal, not as a correction of an error, with `39-05-SUMMARY.md` itself left unedited. **ADM-04 was re-taken, not inherited:** the artifact on record had been rendered from code that folded the three red types into one, so it could not evidence a taxonomy in which they are three; 39-12 re-rendered from post-reversal code (routing gates verified green in the same worktree *first*), extended the probe so `error`/`danger`/`attention` sit contiguous, and put a blocking checkpoint to the owner that named the `attention`/`error` adjacency explicitly — with a deliberate prohibition on presenting the expected improvement, since predicting the answer would anchor the judgement it was meant to inform. The owner's verbatim response was one word, `approved`, and it is recorded as exactly that alongside the question text it answered, with an explicit note that no per-pair prose was volunteered — no owner commentary was fabricated to match the earlier sign-off's style. Both verdicts survive in `39-ADM04-SIGNOFF.md`; the amendment states which is operative. `39-VERIFICATION.md`'s Truth #1 amendment was **mirrored into `39-GAP-G39-1-CLOSEOUT.md`** because `{phase}-VERIFICATION.md` is a verify-reserved filename a later run regenerates wholesale — and that mirroring, not the backup, is what actually preserved it. Full suite **774 passed / 1 skipped / 0 failed**; full-corpus `-b typstpdf` gate **re-run for real** (tag `v9.1.0`, clone SHA `cc7c6f43`, PASSED — the one SKIP in that output remains the separate `TYPSPHINX_CORPUS_REPORT=1` diagnostic, not the gate); `black`/`ruff`/`mypy` clean; milestone invariants re-checked including a fourth lockstep surface the sync test does not guard (`docs/source/_typst/custom_template.typ`) — gentle-clues `1.3.1` everywhere, `@preview` count 4, zero new runtime dependency. Code review 0 critical / 1 warning / 2 info; both advisory items adjudicated in verification as real but non-blocking: **WR-01** the two renamed admonition tests still do not assert the `, title: "…"` argument (proven end-to-end in the render-gate modules instead), and **IN-01** `test_red_family_types_route_to_distinct_clue_functions`'s docstring claims three adjacent red-family boxes where the fixture has only `attention`/`error` adjacent and `danger` five sections away — a genuine documentation-accuracy defect by this phase's own standard, though the underlying safety property does not depend on adjacency (the recognized clue-function token set is complete, so the backward-scan false-green cannot occur at any distance). **Correction to the footer below: `39-SECURITY.md` now exists** (`status: verified`, `threats_open: 0`) — it was produced after that footer was written, so its "no SECURITY.md was produced" note is stale. Next: Phase 40 (Citations — Full Round Trip), no longer deferred. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-08-02 — Phase 39 (Admonition Taxonomy + Rubric Nesting) complete, 8/8 plans, verification `passed` 5/5, no gap-closure round needed. One Active bullet moved to Validated (the admonition / rubric / topic bullet); ADM-01..ADM-05 all complete. **The phase's one genuinely human decision was ADM-04**, the milestone's only `[V]` requirement, and it is worth recording how it actually resolved because the first relay of the verdict was wrong. The owner's opening reaction to the greyscale render was that the boxes looked the same and that the requirement might have been infeasible from the outset; on that reading the orchestrator relayed "cannot distinguish, accepted, no lever, no todo" to the executor. The owner then clarified: the *icons* differ and therefore the kinds ARE distinguishable — the "all the same" observation was about **luminance**, not about distinguishability overall. The corrected verdict is the operative one and reached `39-ADM04-SIGNOFF.md` before any Task 3 commit, so no commit carries the superseded framing; the SIGNOFF preserves both parts explicitly and marks which is the verdict. Net: **ADM-04 MET on icon-shape grounds — exactly the channel ADM-04 itself names — with uniform title-band luminance recorded as an accepted caveat, not a defect.** No styling change, neither fallback lever chosen (per-bucket border thickness / header-band colour; a dashed border was verified not to exist as an option — gentle-clues 1.3.1's `clue()` left edge takes only thickness, paint, and cap), no todo filed. The other durable result is that the RED-first discipline held across waves: plans 39-01/39-02 recorded six bucket assertions and four rubric assertions RED against the untouched translator, and the post-merge gate after Wave 2 correctly showed exactly those four still failing — they were plan 39-06's owned RED (D-13/D-11), not a regression, verified against `39-GATE-EVIDENCE-02.md` node-id-by-node-id before advancing. The literal GSD rule would have skipped the tracking update on a non-zero suite; doing so would have deadlocked the phase against its own recorded RED, so tracking advanced with the deviation stated. Full-corpus `-b typstpdf` gate **re-run for real** (tag `v9.1.0`, PASSED — a skip would not have satisfied SC#5, and the one SKIP in that output is a separate `TYPSPHINX_CORPUS_REPORT=1`-gated diagnostic, not the gate). Full suite 763 passed / 1 skipped / 0 failed; census re-measured (not recalled) and matching both the discussion-time and planning-time counts exactly; milestone invariants held (no new runtime dependency, `@preview` count 4, gentle-clues pin `1.3.1`); docs dogfood build 91 pages (+1 explained). Code review 0 critical / 1 warning / 2 info — WR-01: six admonition unit tests do not assert the new `, title: "…"` argument and some docstrings are now factually stale (coverage gap; the render-gate module covers real output). **No `39-SECURITY.md` was produced** even though `workflow.security_enforcement` is active — run `/gsd-secure-phase 39` before the milestone close if that gate is to be honoured. Environment finding worth carrying: on this NixOS host the known `ruff` shim is **not sufficient** for worktree executors — a fresh worktree's `uv sync`-installed `.venv/bin/uv` is also a generic-linux ELF that fails under the stub loader and shadows the Nix-store `uv` for `subprocess.run(["uv","run","sphinx-build",…])` children (45 failures at exit 127 before the second shim, all passing after). Next: Phase 40 (Citations — Full Round Trip), structurally independent of 39 and the milestone's one classic `TypstError`-RED exception (CIT-01). Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-08-02 — Phase 38 (Structural Indentation + Info Fields) complete, 9/9 plans, verification `passed` 8/8 after one gap-closure round. Two Active bullets moved to Validated (the `desc_*` bullet, delivered across Phases 37–38; and the `field_list` bullet) — note Phase 37's own Validated entry was backfilled here, having been missed at its transition. IND-01..IND-05 + FLD-01..FLD-03 all complete. The phase's one genuinely contested point was scope, not code: ROADMAP SC#4 and REQUIREMENTS IND-04 both read "one indent constant drives desc nesting, field lists, **and block quotes**", but the shipped code deliberately excludes `block_quote` per the locked D-04 decision — measured, not assumed: Typst's `quote()` default indent is 11.0pt against the constant's 27.5pt, `pad(left: 2.5em, quote(block: true, …))` lands at 38.5pt so the constant would stop matching the depth it produces, and dropping `quote()` for a bare `pad` reaches 27.5pt but loses `quote()`'s vertical spacing and destroys `visit_attribution`'s right-aligned "— Author". At UAT the owner ruled the **prose stale, not the implementation**, so both documents were narrowed to the desc/field contexts with the non-consumer recorded — mirroring the FLD-02 parenthetical corrected earlier in the same phase — and `test_ind04_d04_block_quote_not_converted` stands as the standing guard that the exclusion is not silently reverted. Gap-closure round: FLD-02's single-value inline body regressed inside bullet/enumerated list items (`visit_paragraph` tested `in_list_item` before `_field_body_unwrapped_paragraph`, so D-13's forced `parbreak()` re-split the label from its value), found independently by the code review and the verification pass and closed by plan 38-09. The two new emission sites this phase adds route through the shared `escape_typst_string` boundary (`translator.py:6090`) and reach monospace only through Typst's `raw(...)` primitive — never a font family, which emits neither warning nor error while shadowing the `ja` build's CJK fallback. Full suite 706 passed / 0 failed on the closing run; 38-SECURITY.md 20/20 threats closed at ASVS L1 (no dependency change, `@preview` lockstep intact at 4/4/4, full-corpus gate green). Next: Phase 39 (Admonition Taxonomy + Rubric Nesting) — its SC#3 consumes this phase's indent constant, and ADM-04 (greyscale distinguishability) is the milestone's only `[V]` requirement. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-08-01 — Phase 36 (Shared-Emission Seam Cleanup) complete, 4/4 plans, verification `passed` 4/4. MATH-02 moved Active -> Validated; ADM-06 closed as the precondition Phases 37/39 depend on. The phase's entire claim was "nothing changed except one blank line", and every leg of that claim was made falsifiable rather than asserted: SC#2's golden `.typ` was captured against the untouched translator BEFORE any decoupling edit existed (D-07) and never regenerated -- `git log --follow` shows exactly one commit on that path, predating the change -- so the byte-identity test is a real regression guard, not a tautology; SC#3's GREEN strings were derived by hand from the recorded RED strings by removing exactly one newline, with the derivation written down before the fix landed, per milestone invariant #4; and SC#4's acceptance was set-equality against the Plan 01 pre-change failing-node-ID set rather than "zero failures", because an absolute-zero criterion in this sandbox either strands the phase or invites quietly deleting tests until the number looks right. Both sets came out empty. Decoupling is verbatim triplication of `visit_strong`'s body across three handler pairs (D-01) with unreachable branches kept rather than pruned (D-03) -- the duplication is the decision, since Phase 37 restyles signatures and Phase 39 restyles rubrics and neither can move while the bodies are shared. MATH-02 is one statement (`list_item_needs_separator` `True` -> `False`, D-06); clearing rather than merely not setting is what makes the `:label:` path correct, because `_emit_id_anchors` arms the flag before the math is emitted. Full suite 653 passed / 1 skipped / 0 failed; black/ruff/mypy clean; full-corpus `-b typstpdf` gate green; `pyproject.toml`/`uv.lock` and all four `@preview` sync surfaces byte-unchanged across the phase. Code review 0 critical / 1 warning / 1 info (advisory: the two PDF-text baselines are byte-identical to each other without that being asserted or documented; the `dummy_strong_count == 2` check is a whole-file substring count rather than AST-scoped). Deferred by decision and filed: the `par()`-loss leak from the shared `_strong_was_*` slot names (D-02), routed to Phase 39. Next: Phase 37 (Signature Typography -- the `desc_*` Family). Prior footer retained below.* -->


<!-- Prior: *Last updated: 2026-07-29 after starting milestone **v0.7.0 API rendering design overhaul** (`/gsd-new-milestone`) — phase numbering continues at **Phase 36**. Scope confirmed with the owner over four decisions: (1) the design authority is **Sphinx's own LaTeX-rendered PDF** at `app.readthedocs.org/projects/sphinx/downloads/pdf/master/` — measured live this day as 200 / `application/pdf` / 3,227,122 B / 703 pages / pdfTeX-1.40.22, and it is the LaTeX rendering of the very corpus `test_corpus_gate.py` already drives through `-b typstpdf`, so PDF-to-PDF comparison needs no TeX install (none exists on this machine); the RTD project exposes only `master` as active while the gate pins `v9.1.0`, a skew recorded for planning to settle. (2) The styling primitives are consolidated into **one importable Typst module bundled inside typsphinx**, copied beside `_template.typ` and imported per generated file — chosen over emitting inline or adding `#let`s to `base.typ` precisely because it leaves the three in-repo custom templates working unmodified; **Typst Universe publication is explicitly deferred**, only the API boundary is drawn for it. (3) Scope covers `desc_*` + `field_list` **and** admonition / rubric / topic. (4) Version is **v0.7.0**, a minor bump, because the rendered output changes on every page. `citation` support is full round-trip (definition + reference + backlink) and is greenfield — `translator.py` has zero citation handlers today. Also folded in: the v0.6.5 WR-01 `visit_math_block` blank-line todo (this milestone touches separator behaviour broadly, which was the sole reason D-05 deferred it) and the `release.yml` release-notes-body rework (the v0.6.4 Release body is 308 lines of which 296 are a commit dump; the workflow never reads `CHANGELOG.md`). The four provisional-representation defects were measured, not assumed, by building a `py:` domain sample through `-b typst`: proportional-bold signatures, `visit_desc_content`/`depart_desc_content` both `pass` (no hanging indent), nested members at the top-level margin, and `field_list` as bold inline labels. Accepted cost: the emitted `.typ` shape changes broadly, invalidating exact-string assertions at scale. Standing invariants unchanged — zero new runtime dependencies, the `@preview` count stays at four, GATE-01 fail-pre-fix fixtures per node-handler change. Next: define REQUIREMENTS.md, then the roadmap. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-29 after the v0.6.5 milestone close (`/gsd-complete-milestone`) — full evolution review complete. **v0.6.5 (inline-math separator hotfix) shipped: 2 phases / 8 plans / 27 tasks, 2/2 v1 requirements validated.** A document mixing prose and math no longer aborts the Typst compile. The defect was root-caused **by measurement** rather than from the backlog note's guess — the note blamed "math/Text visit ordering," but `visit_math` already called `_add_paragraph_separator()`; the real cause was a scope gap (participation in one of the translator's three separator protocols), so the fatal surfaced in list items, definition-list terms, and collapsed confval field bodies rather than in plain paragraphs. Fixed on both the mitex and native emission paths by applying the existing `visit_literal` pattern (+45 lines, `translator.py` only, zero new helpers), pinned by a GATE-01 real-`typst.compile()` fixture recorded RED pre-fix and independently re-reproduced RED at verification. Milestone code delta 8 files / +560 / −4; zero new runtime dependencies; all four `@preview` version-sync surfaces byte-unchanged. Closeout `override_closeout`: no `v0.6.5-MILESTONE-AUDIT.md` (owner decision at close — for a 2-phase hotfix, `35-RELEASE-EVIDENCE.md`'s seven live runs already covered the audit's requirement-coverage and integration ground), 8 pending todos acknowledged as deferred. Requirements Active cleared; archived to `milestones/v0.6.5-ROADMAP.md` + `v0.6.5-REQUIREMENTS.md` with phase artifacts under `milestones/v0.6.5-phases/`; `.planning/REQUIREMENTS.md` removed (fresh one comes from `/gsd-new-milestone`); ROADMAP.md collapsed to a one-line milestone entry. Next: `/gsd-new-milestone` (numbering continues at Phase 36). Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-29 — Phase 35 (v0.6.5 Release Prep) complete, 5/5 plans, verification `passed` 5/5. **All v0.6.5 phases (34, 35) are complete — the milestone is ready for `/gsd-complete-milestone`.** Prep half delivered and independently re-measured at verification: `pyproject.toml` sole literal / `README.md` Status / `uv.lock` all at `0.6.5` with `typsphinx.__version__` reporting it and both version-sync guard tests green (SC#1); curated `## [0.6.5]` CHANGELOG entry matching D-01–D-04 (1 Fixed bullet, 3 Verified bullets, no BREAKING) with the tail link block rolled over — 25 insertions / exactly 1 deletion, no historical entry disturbed (SC#2); the post-bump tree green on a live run across pytest (649 passed / 1 skipped), black / ruff / mypy, the corpus gate, and both `tox -e docs-html` / `docs-pdf` dogfooding builds per D-12 (SC#3); milestone invariants asserted mechanically over the `eb696bb`-anchored full diff with a positive control proving the pathspec works — `uv.lock` delta is the 1-line self-pin (zero new runtime deps), all four `@preview` sync surfaces byte-empty, `typsphinx/` name-only diff exactly `translator.py` from Phase 34 (SC#4); scope fence held — `git tag -l v0.6.5` and `git ls-remote --tags origin v0.6.5` both empty, re-confirmed independently by the verifier (SC#5). Phase 34's three test-side review Warnings closed: Construct G (labeled `.. math::` inside a list item) added to the GATE-01 fixture plus four exact-string assertions across both emission paths, each proven able to fail by a one-character RED/GREEN perturbation — zero `typsphinx/` change. Notable measurement: RESEARCH.md's caution that WR-04's candidate string needed a spacing fix was itself wrong — `visit_math_block`'s native branch intentionally emits `$ E = m c^2 $` with interior spaces, a different code path from inline math's space-free form. Code review `clean` (0/0/0, 5 files). Deferred by decision and filed as todos: WR-01 (`visit_math_block` redundant blank line — needs a translator change, D-05/D-10) and the `release.yml` release-notes-body rework (D-11). REL-03 deliberately left `[ ]` per D-10 — prep completion is not a publish; the flip, the tag, `release.yml` → PyPI + GitHub Release, and the standing second tag on `typsphinx-doc-translations` all execute at close per `35-HANDOFF.md`'s six-item checklist. Next: `/gsd-complete-milestone`. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-28 — Phase 34 (Inline Math After Text — Separator Fix) complete, 3/3 plans, verification `passed` 5/5. MATH-01 moved Active → Validated. Root cause measured, not guessed: a scope gap in `visit_math`, which called only `_add_paragraph_separator()` — a deliberate no-op inside list items and the five code-mode concat contexts — so math after a sibling juxtaposed with zero separator and the Typst compile aborted. Fixed by applying the existing `visit_literal` separator-protocol pattern to `visit_math` (all three protocols) and `visit_math_block` (list-item half only, D-01); zero new helpers, mitex/native branch and label emission byte-unchanged. Pinned by a GATE-01 real-`typst.compile()` fixture recorded RED pre-fix and independently re-reproduced RED at verification time. Non-regression by set-comparison against the pre-fix baseline (649 passed / 1 skipped, NEW-failures empty), full-corpus `-b typstpdf` fatal-free, 93-page docs dogfooding PDF, visual page inspection. Code review 0 critical / 4 warnings (advisory: WR-01 cosmetic double blank line in `visit_math_block`; WR-02/03/04 uncovered constructs — labeled-equation-in-list-item, Construct F, native-path block math). Milestone invariants held: zero new runtime deps, no `@preview` bump. Next: Phase 35 (v0.6.5 release prep). Prior footer retained below.* -->

<!-- Prior: 2026-07-28 — started milestone v0.6.5 (inline-math separator hotfix) via `/gsd-new-milestone`. Scoped from the owner's direction (「999.1を修正してすみやかにverUpしたい」, i.e. "fix 999.1 and version-up promptly"): minimal two-item scope — the backlog 999.1 inline-math-after-text missing-separator Typst compile error, fixed with a GATE-01 real-`typst.compile()` fail-pre-fix regression fixture, plus a prep-only release phase (version bump + CHANGELOG; publish at `/gsd-complete-milestone`). No pending todos or deferred requirements pulled in. Standing invariants: zero new runtime deps, no `@preview` bump, 3-way version-sync surface unchanged. Requirements → REQUIREMENTS.md; phases → ROADMAP.md. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-28 after v0.6.4 milestone close — Read the Docs migration shipped (6 phases / 33 plans, audit `passed` 13/13, verified_closeout): PR #124 merged, `v0.6.4` tagged, `release.yml` → PyPI + GitHub Release; Issue #119 closed; archives at `milestones/v0.6.4-*`. Owner-manual steps owed post-close: two RTD Default-branch flips → `main`, `.gitmodules` `branch` → `main` (translations repo), Default Version `latest` → `stable` after the tag builds green. Next: `/gsd-new-milestone`. Prior footer retained below.* -->


<!-- Prior: *Last updated: 2026-07-28 after Phase 33 (v0.6.4 Release Prep) complete — the milestone's final phase, prep-only with the scope fence proven held (empty `git tag -l v0.6.4` + `git ls-remote --tags origin v0.6.4` recorded in `33-HANDOFF.md`): version bumped to 0.6.4 (`pyproject.toml` sole literal, `uv.lock` self-pin 1-in/1-out, README Status same-commit), curated `## [0.6.4]` CHANGELOG entry (zero BREAKING per D-01, losses disclosed in Removed; `### Verified` held to three diff-provable invariants per D-03; tail link block rolled), the four top-level `.planning/` docs translated JA→EN meaning-preserving (D-05; human UAT spot-check passed 1/1), `33-RELEASE-EVIDENCE.md` re-verifying the RTD Documentation URL live (302→200) and the three milestone invariants over the re-measured 279-commit diff. Verification `passed`; 14/14 threats closed (33-SECURITY.md). **All 6 v0.6.4 phases complete — milestone ready for `/gsd-complete-milestone`** (merge PR #124 → tag `v0.6.4` → PyPI + GitHub Release), which also owes: Issue #119 close (D-15 draft), the two RTD Default-branch reverts + `.gitmodules` `branch` → `main`, Default Version `latest` → `stable` after the tag builds green, and the dependabot PR #123 revival-hazard check. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-28 after Phase 32 (GitHub Pages Teardown, IRREVERSIBLE) complete — CI-04 delivered behind a same-day GREEN evidence gate (fresh RTD en/ja HTML + both PDFs + root resolution, 2026-07-27): `docs.yml` Pages deploy step + `pages: write`/`id-token: write` removed with `contents: write` and the tag-time Release step retained byte-identical to merge-base `771ec56f` (D-06 guard tests + recorded red negative control); post-teardown tree observed green on draft PR #124 (run 30275369792, docs-pdf step-level success); `origin/gh-pages` deleted with live `ls-remote` proof (SHA matched baseline `f97862d`); github.io 404 CONFIRMED live, no redirect, no stub. Revival hazard (main's stale docs.yml, dependabot PR #123) handed to `/gsd-complete-milestone` in 32-EVIDENCE.md `## Handoffs`. Verification passed 12/12 live-rechecked; suite 647 passed / 1 skipped; code review 0 critical / 1 warning (raw-text vs YAML-parse guard style — the plan's deliberate idiom choice) / 1 info. Hosting-migration todo (2026-07-21) auto-closed. Next: Phase 33 v0.6.4 release prep. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-27 after Phase 30 (Hand-Rolled Multi-Language Machinery & Orphan Removal) complete — I18N-02 + DOC-08 delivered: the multilang machinery (`build_multilang.py`, language switcher, `docs/Makefile` i18n targets, `docs-multilang` testenv, `docs/locale/ja/`) and the `docs/usage.rst`/`installation.rst` orphan pair are gone on a green tree; `docs.yml` repointed single-language (deploy step preserved for Phase 32 per D-14). UAT completed 3/3 once milestone PR #124 opened: docs.yml run 30269906943 green (build-docs 37s, `documentation-html` artifact from `docs/_build/html`), live `/en/latest/` switcher/`custom.css` markup = 0, Furo READTHEDOCS-gated sidebar slots = 0 on RTD build 33763874 (no ad placement — open question resolved). 17/17 threats closed (30-SECURITY.md). Phases 29/30/30.1/31 complete — next: Phase 32 GitHub Pages Teardown (IRREVERSIBLE), behind its freshly re-taken RTD-is-serving gate. Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-27 after Phase 31 (Published-URL Cutover + Repo-Wide Link Guard) complete — DOC-09 + DOC-10 (split per D-15) + CI-05 delivered: every published documentation URL (README incl. RTD badge + ja link, `pyproject.toml` `[project.urls]`, INTEGRATIONS.md full refresh) repointed at `typsphinx.readthedocs.io` and fetched live over HTTP; the advisory repo-wide lychee guard `links.yml` installed guard-first with a recorded red negative-control run (30205112477) per D-09; `tests/test_no_stale_github_io_links.py` locks the rewrite; About → Website set to the RTD root. Issue #119's close is a drafted post-merge handoff (`/gsd-complete-milestone`, D-15). UAT 1/1: the backstop truth (cancelled Link Check run leaves zero repo state) proven by live cancellation (run 30267597698) + full `ls-remote` baseline diff. api-coverage verify-gate false-positived again on INTEGRATIONS.md prose (override recorded in 31-VERIFICATION.md). Next: Phase 30's outstanding UAT (partial — resume before the irreversible Phase 32). Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-26 after Phase 30.1 (Translations Repository + Japanese RTD Site, INSERTED) complete — I18N-01 + I18N-03 delivered: `/ja/latest/` serves real Japanese prose behind RTD's own flyout from the new `typsphinx-doc-translations` repository (submodule pin on `gsd/v0.6.4-read-the-docs-migration` per PD-02, auto-advanced by an observed scheduled workflow after Plan 08's branch-fetch fix), and the Japanese PDF is glyph-correct (option-b fix: docs-side custom `typst_template` + `derive_typst_lang()` re-derivation; corrected artifact SHA `23885dcd…` passed D-03's four checks incl. owner visual confirmation, UAT 1/1). Verification `passed` after a gap-closure round (plans 07–11); 26/26 threats closed. Three post-merge flips owed (parent/ja RTD Default branch + `.gitmodules` `branch` → `main`); `docs/locale/ja/` deletion deferred to Phase 30 (PD-01). Next: Phase 30 (multilang machinery removal + orphan pair — expect the deletion guard). Prior footer retained below.* -->

<!-- Prior: *Last updated: 2026-07-25 — started milestone v0.6.4 (Read the Docs migration) via `/gsd-new-milestone`.
Scoped from the owner's direction (「RTD に移行するぜ」, i.e. "let's move to RTD") against the pending-todo
backlog, with four scoping decisions taken at questioning: **multilingual** → RTD's translation-project
model (en parent + ja child, retiring the hand-rolled `build_multilang.py` and the language-switcher);
**PDF** → produce the typstpdf-built PDF via `build.jobs` to `$READTHEDOCS_OUTPUT/pdf/` and serve it from
RTD too (the CI `docs-pdf` regression gate and the Release attachment both survive); **the old Pages
site** → cut over immediately with no parallel redirect (accepting that existing github.io links become
404); **what's bundled** → closing #119 + setting the About Website field, an advisory `sphinx-linkcheck`
CI job, and resolving the `docs/usage.rst`/`installation.rst` orphan pair. **Version policy** is `latest`
+ `stable`, defaulting to `stable` (since RTD started failing builds without a `.readthedocs.yaml` after
2023-09-25, existing tags can't be built retroactively — `stable` only becomes real starting from the
v0.6.4 tag). **Cut a tag** (publish v0.6.4 to PyPI). Milestone invariant: no `typsphinx/` runtime code
changes, no `@preview` version bump, the 3-way version-sync surface unchanged. Requirements →
REQUIREMENTS.md; phases → ROADMAP.md. Prior footer retained below.* -->

<!-- (continued prior footers below) -->


<!-- Prior: *Last updated: 2026-07-25 after the v0.6.3 milestone close.* Milestone v0.6.3 (config & docs measured fidelity + captioned tables) shipped: 6 phases / 12 plans / 28 tasks, 7/7 v1 requirements validated, archived to `milestones/v0.6.3-ROADMAP.md` + `v0.6.3-REQUIREMENTS.md` with phase artifacts under `milestones/v0.6.3-phases/`, tagged `v0.6.3` and published via `release.yml` (PyPI + GitHub Release). Closeout was `override_closeout`: no `MILESTONE-AUDIT.md` (owner accepted — Phase 28's live gate re-run stood in) and 9 pending todos acknowledged as deferred. One defect was found and fixed at the close itself, before the tag: the bundled `examples/advanced` sample was unbuildable on two independent axes (5 `typst_elements` keys outside the CONF-04 allowlist Phase 26 had just made fail-loud, and `custom.typ` three milestones behind on its `@preview` pins — `unknown variable: kai`), repaired by having the template declare `papersize`/`fontsize`/`lang` and by extending `test_preview_version_sync.py` over `examples/**/*.typ`. `.planning/REQUIREMENTS.md` removed (fresh one comes from `/gsd-new-milestone`); ROADMAP.md collapsed to a one-line milestone entry. Prior footer retained below.* -->


<!-- Prior: *Last updated: 2026-07-25 — Phase 28 complete (v0.6.3 release prep + regression-gate close, prep-only / no requirement IDs): `pyproject.toml` bumped 0.6.2→0.6.3 as the **sole** version literal with `uv.lock` regenerated in lockstep (self-entry 1 line, zero dependency/transitive drift; `uv sync --locked` green) and `README.md:315` → `Stable (v0.6.3)`; a curated `## [0.6.3]` CHANGELOG entry covering 6 of the 7 v1 ledger IDs bundled into 5 user-visible-change bullets (DOC-06 deliberately omitted — D-10, unreachable-orphan cleanup, never user-visible; the ROADMAP SC#2 "all 7" wording was amended to 6 by owner decision) with exactly 2 BREAKING labels (CONF-04 Changed / CONF-05 Removed, Fixed clean per the D-01/D-03 asymmetry), `### Verified` held to the same 4 facts as the v0.6.2 precedent under D-11 (no number without a verification mechanism), plus the `[0.6.3]:` tag link and the `[Unreleased]:` compare advanced to `v0.6.3...HEAD`; and the closing regression gate run live on the post-bump tree — corpus gate genuinely PASSED not skipped (`1 passed in 12.87s`, `Unknown Visit Catalogue: []`, zero SKIPPED lines), full suite 656 passed / 1 skipped / 0 failed, `docs-pdf` 2 / `docs-multilang` 4 warning lines (both the pre-existing `visit_toctree` docstring defect, out of scope per D-06) — all recorded verbatim in `28-VERIFICATION.md` with a duplicate copy of the gate log in `28-02-SUMMARY.md` as the non-clobberable record. SC#4 invariant held **as amended**: zero new runtime deps, `@preview` grep across all 3 declaration sites returns zero, `base.typ` diff exactly `2\t1` (the Phase 27.1 `lang` parameter, nothing else). SC#5 scope fence held: no tag, no publish, no merge; `typsphinx/`/`tests/`/`docs/`/`examples/`/`.github/` all porcelain-clean; zero new test code (D-05–D-08 rule test-infrastructure expansion out of scope for a prep phase). 5/5 SC and 17/17 observable truths verified with independent re-runs on the main checkout (28-VERIFICATION.md); code review 0 critical / 1 warning / 1 info, both non-defects outside the fence (a pre-existing second `## [Unreleased]` heading at CHANGELOG.md:771; the `[0.6.3]:` link 404ing until the tag is cut — which is SC#5 being satisfied). **A long-standing execution hazard was root-caused and fixed this session:** the "45 integration tests fail only inside executor worktrees" problem recurring since Phase 22.1 is not the NixOS sandbox and not the editable install — `uv sync` installs a `uv` wheel into `.venv/bin/`, `uv run` puts that dir first on PATH, and the tests' `subprocess.run(["uv","run","sphinx-build",...])` therefore resolves a generic-linux ELF `uv` NixOS cannot exec (exit 127); the main checkout's copy merely happens to be patchelf'd. `ln -sf "$(command -v uv)" .venv/bin/uv` after `uv sync` closes it (probe: `11 failed, 1 passed` → `12 passed`), which is why this phase's worktree executors could run the unfiltered full suite for the first time. All 5/5 v0.6.3 phases done; 7/7 v1 requirements delivered — milestone ready for `/gsd-complete-milestone` (merge → tag `v0.6.3` → `release.yml` → PyPI + GitHub Release). Prior footer retained below.* -->
<!-- Prior: Last updated: 2026-07-24 — Phase 27 complete (DOC-06/DOC-07: docs measured fidelity — orphan `docs/configuration.rst` + its collateral test `tests/test_documentation_configuration.py` deleted; 5 phantom config names purged from `user_guide/configuration.rst` (codly knobs + tuple `typst_author` gone; papersize/fontsize → working `typst_elements`); api/index.rst config `list-table` deleted → single `See :doc:` pointer; scoped ja `.po` regen with inert `#~` obsoletes; SC#4 "anywhere" clause caught a scoping gap — phantom codly names in `examples/advanced.rst`/`basic.rst` removed too (gap-closure `59bf66d`); docs-only GATE-01 N/A, base.typ byte-unchanged, no `@preview` bump; deletion branch manually merged past the `worktree.cleanup-wave` guard (D-13) after 2-file scope confirm; grep-zero + registered-set cross-check + green docs build + green suite; 6/6 must-haves in 27-VERIFICATION.md; 4/5 v0.6.3 phases done — next Phase 28 v0.6.3 release prep). Phase 26 complete (CONF-04: `typst_elements` `papersize`/`fontsize` now reach `project()` — 100% Python-side: `writer.py` stops laundering via `sphinx_metadata` + drops dead `copyright`; `template_engine.py` gains a curated `ELEMENTS_ALLOWLIST` merged additively, a `RawTypst` marker emitting `fontsize` as an unquoted length before the `str` branch while `papersize` stays quoted, and fail-loud `ExtensionError` on unknown keys; copyright non-leak is structural; `base.typ` byte-unchanged, zero new deps, no `@preview` bump; 10 unit tests + 4 real-`typst.compile()` GATE-01 fixtures + durable pre-fix proof + recorded manual red→green; 615 passed / 1 skipped / 0 failed; 5/5 must-haves in 26-VERIFICATION.md; 3/5 v0.6.3 phases done — next Phase 27 docs measured fidelity). Phase 25 complete (TBL-01/TBL-02: PR#98 captioned-table figure-wrap reimplemented against current `translator.py` — `figure(..., caption:, kind: table)` "Table N", `:width:`-composed, stale-buffer root-fix via `del`, single `<label>` via deferred `_emit_id_anchors(skip_ids)`; caption-less stays plain; base.typ byte-unchanged, no `@preview` bump; 8 unit tests + real-`typst.compile()` GATE-01 fixture + fail-pre-fix proof; 116/116 unit, 567 fast-suite green; 7/7 must-haves in 25-VERIFICATION.md; 2/5 v0.6.3 phases done). Phase 24 complete (CONF-05: `typst_toctree_defaults` deleted from all enumerated surfaces, grep-zero + 519 tests green, GATE-01 N/A). Milestone v0.6.3 (config & docs measured fidelity + captioned tables) started via `/gsd-new-milestone`. Scoped from the owner's direction (dead-config cleanup + PR#98 + making the build match the documentation) against the pending-todo backlog. Decisions: `typst_toctree_defaults` → delete (B, low wiring value); `typst_elements`'s non-mapped keys → implement (A, papersize/fontsize are in high demand for the PDF); reimplement PR#98 against current `main`; delete docs orphans + fix phantom names; the github.io 404 links are out of scope this time (resolved by the RTD migration).Milestone invariant carried: zero new runtime deps, no `@preview` bump, 3-way version-sync surface untouched; GATE-01 real-`typst.compile()` bar on every node-handler + config→output change. Requirements → REQUIREMENTS.md; phases → ROADMAP.md. Prior footer retained below.* -->

<!-- Prior: 2026-07-23 at v0.6.2 milestone close (`/gsd-complete-milestone`) — full evolution review complete. v0.6.2 (rendering fidelity round 2) shipped: the 13 medium/low v0.6.1 audit findings resolved as one coherent `translator.py` series (clusters A–F, FID-02..FID-14), plus Issue #117 target-name PDF (PDF-01), nested-master compile-root alignment (PDF-02), the dead-config sweep + `typst_package` repair (CONF-01..CONF-03), builder-warning hardening (WR-01/WR-02), and the README/CLAUDE.md accuracy pass (DOC-01..DOC-05) — 25/25 v1 requirements delivered across 9 phases / 30 plans. Closeout `override_closeout` (Phase 22.3's single `pytest-xdist` backstop truth abstained to human per the honest-verifier rule; all 22.3 ROADMAP SCs independently verified with direct evidence; operator acknowledged that item + 9 pending-todo backlog entries as deferred — STATE.md Deferred Items). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched. Requirements Active cleared; milestone archived to `milestones/v0.6.2-ROADMAP.md` / `v0.6.2-REQUIREMENTS.md`; tagged `v0.6.2` (publish via `release.yml` → PyPI + GitHub Release). Next milestone scoped via `/gsd-new-milestone`. Prior footer retained below.* -->

<!-- Prior: 2026-07-21 — Phase 22 complete (Issue #117 / PDF-01: `_resolve_output_stem` single-sources the `typst_documents` target-name rule across all three write/read-back sites; GATE-01 real-compile + 24 normalization cases; security `threats_open: 0`; UAT closed 1/1 with the non-ASCII filesystem-normalization backstop accepted as out-of-scope OS behavior). Phase 22.1 (PDF-02, typstpdf compile-root alignment for nested masters) was inserted and is next; then Phase 23 (release prep). Prior footer retained below.* -->

<!-- Prior: 2026-07-20 — Phase 21 complete (Clusters C/D/E/F: FID-10..14); the v0.6.2 translator-fix series (Phases 19–21) is done and verified, remaining: Phase 22 (#117) + Release. Earlier 2026-07-20: started milestone v0.6.2 (rendering fidelity round 2) via `/gsd-new-milestone`. Scoped from §999.1 (the 13 medium/low v0.6.1 audit findings, grouped by root cause into clusters A–F) + §999.2 (Issue #117 typstpdf target-name PDF bug). Milestone invariant carried forward: zero new runtime deps, no `@preview` bump, 3-way version-sync surface untouched; standing GATE-01 real-`typst.compile()` bar applies to every node-handler change. Requirements → REQUIREMENTS.md; phases → ROADMAP.md. Prior footer retained below.* -->

<!-- Prior: 2026-07-19 at v0.6.1 milestone close (`/gsd-complete-milestone`) — full evolution review complete. v0.6.1 (rendering fidelity) shipped: `typstpdf` output now renders faithfully, not merely compiles fatal-free. All 6 v1 requirements validated (TODO-01/MAN-01/LEN-01 Phase 16; AUD-01 Phase 17 — full 151-docname human-assisted visual audit → 15-finding catalogue; FID-01a/GATE-03 Phase 18 — wide-table fix + full-corpus regression gate). Closeout `override_closeout` (Phase 17 audit-phase verification via human gate + validation + downstream real-compile proof, operator-accepted). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched. Requirements Active cleared; the 13 medium/low audit findings + CFG-01/XOS-01 tracked as next-milestone backlog. Next milestone scoped via `/gsd-new-milestone`. Prior footer retained below. -->


<!-- Prior: 2026-07-13 — started milestone v0.6.1 (rendering fidelity): reconciled stale debug-session metadata (13 files → `resolved`), corrected the v0.6.0 backlog framing, re-confirmed GATE-02 green via a real corpus rebuild + a full warning audit (66 warnings, only `todo_node`/`manpage` are typsphinx content-drops), and scoped v0.6.1 = TODO-01/MAN-01/LEN-01 + a visual fidelity audit. Prior: 2026-07-13 at v0.6.0 milestone close (`/gsd-complete-milestone`) — full evolution review complete. v0.6.0 (real-world robustness) shipped: Sphinx's own `doc/` tree compiles end-to-end through `typstpdf` with no fatal Typst errors (Issue #114 closed), all 19 v1 requirements validated, milestone audit passed (19/19 requirements, 16/16 integration seams wired, 5/5 E2E flows), zero new runtime dependencies. Requirements Active cleared; 13 post-GATE-02 rendering-polish debug sessions + SC#2 `todo_node`/`manpage` handlers acknowledged as next-milestone backlog. Delivered via a release PR (`release/v0.6.0 → main`, closes #114) → tag `v0.6.0` → PyPI. Prior footer retained below for history.* -->

<!-- Prior: 2026-07-11 at v0.5.0 milestone close (`/gsd-complete-milestone`) — full evolution review complete. v0.5.0 shipped: Sphinx 9.1 / docutils 0.22 / typst 0.15 / Python 3.12–3.13, all 14 v1 requirements validated, milestone audit passed, released to PyPI + GitHub Release. Requirements Active cleared; next-milestone candidates (CFG-01, XOS-01) tracked. -->


<!-- Prior: 2026-07-11 after Phase 10 (Version-String Fix + v0.5.0 Release) complete — the FINAL phase of the v0.5.0 milestone. Phase 10 was re-scoped to release *preparation only* (D-01/D-02): `typsphinx.__version__` is now single-sourced from `importlib.metadata` (reporting `0.5.0`, stale `0.4.3` gone) with a `PackageNotFoundError` fallback; `pyproject.toml` is the sole version literal (`0.5.0`); `uv.lock` regenerated; a genuine `tomllib` drift-guard test added; and a curated `CHANGELOG.md` `[0.5.0]` entry prepared as the single source for the Release body. 6/6 must-haves verified (10-VERIFICATION.md); 413/413 tests green, black/ruff/mypy clean on `release/v0.5.0`. Scope fence held: no tag, no PyPI publish, no GitHub Release, `main` untouched, PR #112 left OPEN. **All v0.5.0 phases (6–10 + 8.1) are complete — the milestone is ready for `/gsd-complete-milestone`, which executes the deferred REL-01 publish half (merge PR #112 → tag `v0.5.0` → `release.yml` → PyPI + GitHub Release), mirroring the v0.4.4 precedent.* -->

<!-- Prior: 2026-07-11 after Phase 9 (Green CI Matrix + Smoke Test + Guardrails) complete — the v0.5.0 stack (Sphinx 9.1 / docutils 0.22 / typst 0.15) is now observed all-green in real CI for the first time: PR #112 (`release/v0.5.0 → main`) shows 13/13 jobs green across the full 3-OS × Python 3.12–3.13 matrix + `docs.yml` build-docs, left **unmerged** for Phase 10 (CI-01). A `typst compile` smoke test (`tests/test_preview_smoke_gate.py` + `tests/fixtures/preview_smoke/`) now guards all four bundled `@preview` packages via real function calls incl. a `.. math::` block through mitex — closing the `kai`-class coverage gap the admonition-only gate missed, proven by a documented negative-control (CI-02). Durability guardrails confirmed already correct (verified no-op, D-06) and the stale `main` branch-protection required-checks reconciled (CI-03 + access-control durability). 8/8 must-haves; 09-VERIFICATION.md; 412/412 tests green; black/ruff/mypy clean on `release/v0.5.0`; `@preview` versions unchanged. Next: Phase 10 (v0.5.0 PyPI release) — add the `__version__` 0.4.3→0.5.0 fix to PR #112, merge, tag, publish.* -->

