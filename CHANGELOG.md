# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for Future Releases
- BibTeX/bibliography support
- Glossary generation
- Index generation
- Pre-commit hooks
- Additional Typst Universe template integration

## [0.9.0] - 2026-08-17

This release lets every `typst_documents` entry choose its own template, Typst Universe package,
and template-function arguments through the validated `typst_document_templates` registry, instead
of one globally-configured template being applied to every master document. **This minor release
breaks two independent things** — read the `### Changed` and `### Removed` sections below, and see
the "Migrating from 0.8.x to 0.9.0" guide in the published documentation for the exact rewrite each
breaking change needs. What does **not** break: the registry itself is additive — a `conf.py` that
declares no `typst_document_templates` and no fifth `typst_documents` element keeps producing the
same PDF, because the built-in `"typst"` key resolves to exactly the same global configuration
(`typst_template` / `typst_package` / `typst_template_function` / `typst_template_mapping`) it
always did.

### Added

- **A `conf.py` can now declare per-document templates through the `typst_document_templates`
  registry (TPL-01, TPL-02, TPL-03, TPL-04, TPL-05, CONF-14, CONF-15, CONF-16, CONF-17,
  CONF-18).** Each entry carries `template` (a local `.typ` path) **xor** `package` (a Typst
  Universe spec), plus an optional `template_function`; a `typst_documents` entry's fifth element
  now names the registry key to use, several entries can share one key, and a four-element entry
  behaves identically to one whose fifth element is `"typst"`. The built-in `"typst"` key is
  resolved by the same rule as any declared key rather than being special-cased: it falls back to
  today's global `typst_template` / `typst_package` / `typst_template_function` /
  `typst_template_mapping` configuration, or the bundled default template when none of those is
  set — so a `conf.py` that declares no registry keeps working unchanged.

### Changed

- **Breaking: the `<srcdir>/base.typ` shadow-template route moved to
  `<srcdir>/_typst/base.typ` (OUT-04).** The reason, in one clause: the resolved template's
  parent directory is now copied wholesale to the output as that registry key's bundle, so it
  must be a real bundle directory and not the whole source tree. If your project still has a
  `<srcdir>/base.typ`, move it to `<srcdir>/_typst/base.typ`. If you do nothing, the build
  silently typesets with the bundled default template instead of your file — there is **no
  build-time warning** for this relocation, so this changelog entry is the only place it is
  announced.

- **Breaking: template layout is now validated before anything is written (WR-01, CR-01).** The
  reason, in one clause: the resolved template's parent directory is copied wholesale to the
  output as that registry key's bundle, so a template inside a directory Sphinx already treats
  as its own would republish that directory into public build output. Three configurations now
  stop the build: (a) a used registry key whose resolved template bundle directory is, contains,
  or is contained by any entry of Sphinx's `templates_path`; (b) a resolved template whose parent
  directory is the source directory itself or an ancestor of it — now caught before any file is
  written rather than at the end of the build; (c) a declared registry key differing from the
  built-in key only by case. Move the Typst template into a directory that is not on
  `templates_path` — this project uses `_typst/` — and update `typst_template` /
  `typst_document_templates` to match; Sphinx's own `templates_path` directory keeps its own
  meaning and can stay in place, which is what this repository's own documentation build does. If
  you do nothing, the build fails with a message naming the offending registry key, its resolved
  bundle directory, and the colliding entry — this is a hard failure by design: the rejected
  alternative, warning and skipping that key's bundle copy, leaves the wrapper importing a
  template file that was never written, so the emitted `.typ` tree cannot compile while the build
  reports success.

- **Breaking: every used template's bundle is now copied to its own directory under the output
  tree, and an explicit asset list no longer decides what reaches it (OUT-04, OUT-05, OUT-06,
  OUT-07, BLD-05, BLD-06).** v0.8.x wrote one shared template file, `_template.typ`, at the
  output root; v0.9.0 copies each used registry key's whole template bundle — the resolved
  template's parent directory — wholesale to `<outdir>/_template/<key>/<file>`, with the
  built-in `"typst"` key copied by the identical rule. If your template references an asset by a
  relative path (an `#image("logo.png")`, a partial `#import`), that asset must now live inside
  the template's own bundle directory — anywhere else, it will not reach the output.

### Fixed

- **A cross-reference to an absent target no longer links to a same-spelled decoy (XREF-05).**
  Two docnames that sanitized to the same Typst label used to let a reference whose real target
  document was absent from the compiling master resolve to the other, wrong document instead of
  degrading to plain text as an absent target always should. Note in passing: the fix makes label
  sanitization injective by re-escaping a literal occurrence of the sanitizer's own `_u<hex>_`
  escape token, so the emitted label name changes for an identifier that literally spells that
  token — the only such name in this repository is one test fixture's docname. PDF appearance is
  otherwise unchanged; only the label name in the emitted `.typ` output and the corresponding link
  destination name in the PDF move. Not a breaking change.

- **A document name containing `#` or `>` can no longer collide two include-edge keys (BLD-07).**
  Two structurally different include edges whose docnames contained one of those characters could
  previously derive the identical key, letting a state guard that should have stayed dark fire and
  duplicate or substitute a document's content in the compiled output. Document names without
  either character produce byte-identical keys, so nothing changes for an ordinary project.

- **An include chain deeper than this project's own bound now stops the build with a named error
  instead of a raw Python traceback (BLD-08).** An include chain deeper than the module's bound
  (500 — two orders of magnitude beyond any real documentation tree) now raises a
  `sphinx.errors.ExtensionError` naming the depth reached and the offending chain, instead of
  escaping as an uncaught interpreter `RecursionError`.

- **A driveless-absolute Windows image URI is classified like its sibling (BLD-09).** An absolute
  image URI written by a third-party extension in the driveless Windows shape (or the UNC shape)
  now reaches the relocate-and-warn path on Python 3.13, where it was previously left untouched —
  which mattered because an untouched rooted URI reached the image copy step, whose platform-native
  destination join discards the output directory for a rooted path.

- **Two escaping images sharing a basename no longer collapse onto one file (IMG-03).** Two
  absolute image URIs in different directories that share a filename and both fall outside the
  doctree directory used to collide onto one relocated file, so one image silently replaced the
  other. The user-visible consequence: the relocated file's emitted name now carries a short
  digest prefix ahead of the original filename, so the two images keep separate files.

### Removed

- **Breaking:** the `typst_template_assets` config value is removed (CONF-19) — every used
  template's bundle directory is now copied wholesale to the output, so an explicit asset list is
  no longer needed to select what reaches it; see the `### Changed` bundle-relocation entry above
  for what replaces it. Delete `typst_template_assets` from your `conf.py`; if you leave it set, a
  `config-inited` warning names the value and explains the wholesale copy, rather than the list
  being silently ignored — unlike v0.7.1's `typst_authors` removal, this one ships with a warning
  shim.

### Verified

- No new **runtime** dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.

## [0.8.0] - 2026-08-15

This release makes multi-master composition work: a `typst_documents` configuration declaring
more than one master now produces a complete PDF for each of them, with every document it reaches
rendering at that master's own traversal position and heading level instead of being silently
dropped from all but one. Achieving this required restructuring what typsphinx writes to disk, so
**this minor release can break a working configuration** — read the `### Changed` section below,
and see the "Migrating from 0.7.x to 0.8.0" guide in the published documentation for the exact
rewrite each of the three breaking changes needs.

### Added

- **Multi-master composition — every master now gets its own complete PDF (COMP-05, COMP-06,
  COMP-07, COMP-09, COMP-10, COMP-12)** — the builder computes each master's include graph by
  document-order depth-first traversal and publishes it as Typst `state`, so a document reached
  from more than one master renders once in each master's PDF, at that master's own traversal
  position, with its heading level varying independently per master; two masters requiring
  conflicting include sets from the same content file now resolve correctly instead of one
  silently winning.
- **Compile-time cross-reference degradation (XREF-03, XREF-04)** — a reference whose target label
  is absent from the compiling master now degrades to plain text instead of aborting the compile;
  every label-reference emission site routes through one shared guard so demand and supply sides
  cannot diverge.
- **The published documentation now describes the two-layer output (DOC-14)** — which file to
  compile, what a standalone content-file compile does, and target-as-path semantics are all
  documented on the new output-layout page.

### Changed

- **Breaking:** the output shape — one `typst_documents` entry now writes TWO files instead of one
  (COMP-01, COMP-02, COMP-11, OUT-03). With
  `typst_documents = [("index", "manual.typ", "Title", "Author", "typst")]`, v0.7.x wrote
  `manual.typ` containing the whole document; v0.8.0 writes `manual.typ` as a thin wrapper
  (template application plus one include) and `index.typ` as the document body — every docname
  gets a content file, not only the ones named in `typst_documents`. This is a different change
  from v0.7.1's own `index.typ` → `<project>.typ` default-target rename: that changed what the
  target is *called*, this changes what the target file *contains*. A content file compiled
  standalone yields only its own body, with its state-guarded children absent and no error or
  warning.
- **Breaking:** the target-as-path reversal (OUT-01, OUT-02) — a target containing a path
  separator was rejected in v0.7.x and written under its basename; it is now honoured as-is
  relative to the output directory. This deliberately reverses v0.7.1 Phase 44's
  D-05/D-06/D-07; the security half is retained — a target escaping the output directory (`..`
  segments, absolute or drive-qualified paths) is still refused with a warning and a safe
  basename fallback.
- **Breaking:** the collision hard error (BLD-02, BLD-03, BLD-04) — a configuration whose wrapper
  target resolves onto a content file's own path now raises an `ExtensionError` before anything is
  written, instead of silently dropping that master's body. This stops a build that used to
  succeed, for the most common configuration shape (`("index", "index.typ", ...)`); collision
  detection behaves identically on case-insensitive filesystems.

### Fixed

- **A master that is also another master's toctree child now builds, and an included master no
  longer re-expands its template (COMP-03, COMP-04)** — a document listed in `typst_documents`
  that is also another master's toctree child previously failed or rendered incorrectly; an
  included master no longer re-expands its own template's title page and outline into the middle
  of the parent's body.
- **Prose around a toctree keeps its position (COMP-08)** — prose written before and after a
  `.. toctree::` now keeps its position relative to the included content instead of being
  reordered.
- **Two image-path defects fixed (IMG-01, IMG-02)** — a converted image rehomed to
  `images/<basename>` no longer collides with a real source image of the same basename; an
  absolute image URI outside the doctree directory no longer causes the copy step to write outside
  the output directory.

### Verified

- No new **runtime** dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.

## [0.7.1] - 2026-08-11

This release closes the gap between what typsphinx's documentation promises and what a `conf.py`
actually gets: `typst_documents` now resolves to a working default instead of silently producing
nothing, an explicit entry's title and author finally reach the rendered document, and the
published custom-template parameter contract matches what typsphinx actually passes. Several
rendering-structure defects in tables, figures, and toctree-driven heading nesting are also
repaired. Because several of these fixes tighten previously-loose configuration handling, **this
patch release can break a working configuration** — read the `### Changed` and `### Removed`
sections below, and see the "Migrating from 0.7.0 to 0.7.1" guide in the published documentation
for the exact rewrite each breaking change needs.

### Added

- **`typst_documents` now has a default, so following the Quick Start produces a PDF (CONF-08,
  DOC-11)** — with `typst_documents` unset, `sphinx-build -b typstpdf` previously exited 0 with a
  warning and produced zero output; it now resolves a default derived from `root_doc`, `project`,
  and `author`, in Sphinx's own LaTeX shape, and produces a real PDF. For a project that never set
  `typst_documents`, the emitted Typst filename changes from `index.typ` to a project-derived name
  (e.g. `quickstartdefaultgate.typ` for a project named "Quickstart Default Gate"), and the emitted
  body changes from an untemplated fragment of `@preview` imports to a fully templated document. If
  you `#include()` the old file from your own Typst source, update the include path.

### Changed

- **An explicit `typst_documents` entry's title and author now reach the rendered PDF (CONF-09)**
  — the `[2]` title and `[3]` author elements of an explicit `typst_documents` entry now override
  `config.project` / `config.author`, matching Sphinx's own LaTeX builder; previously they were
  silently ignored. A project whose entry's title/author differ from `project`/`author` will see
  its rendered title and author change.
- **Breaking:** a declared `typst_template_function` `params` dict is now the complete parameter
  set (CONF-11) — when `typst_template_function` is given in dict form with a `params` key, only
  those parameters are passed to the template function; the auto-derived `title`/`authors`/`date`,
  the `typst_elements` merge, and the `toctree_*` merge are all withheld. A project that declares a
  partial `params` dict today and relied on the auto-derived rest will now render with the
  template's own defaults (empty title, no author) instead of the previous merged result.
- **Breaking:** the auto-derived `lang` now reaches every non-package template route, and the
  published parameter contract matches what typsphinx actually passes (CONF-12, DOC-13) — an
  explicit `typst_template` or a `<srcdir>/base.typ` shadow template now receives the
  Sphinx-derived `lang` argument, same as the bundled default; a custom template that does not
  declare a `lang` parameter now fails the compile with `unexpected argument: lang`. The documented
  custom-template parameter contract was corrected to the nine parameters typsphinx actually
  passes.

### Fixed

- **Nested tables and figures no longer corrupt the enclosing structure, and an empty-titled
  caption still anchors its ids (TBL-04, TBL-05, FIG-01, TOC-01)** — a table nested inside a
  `list-table` cell no longer replaces the outer table's own cells, column count, or caption; a
  figure nested inside another figure no longer drops the outer figure's caption and instead
  renders correctly inside its legend; a captioned table whose title renders to an empty or
  whitespace-only string still emits its id anchors, so a `:ref:`/`:numref:` to it resolves instead
  of dangling; and a document reached through a `toctree` now renders its headings one level deeper
  than its parent, so the PDF outline nests instead of being flat, and nested toctrees compose.
- **Absolute image URIs from Sphinx's image converter or downloader no longer abort the Typst
  compile (Issue #130, PR #131, @christianwehe)** — building with an image-conversion extension
  (`sphinxcontrib.rsvgconverter`, `sphinxcontrib.inkscapeconverter`, `sphinx.ext.imgconverter`) or
  a downloaded remote image previously copied no image at all and made the Typst compile abort
  with "file not found"; both cases now copy and resolve correctly.
- **A malformed docname fails with an actionable typsphinx error, and the published changelog page
  is current (BLD-01, DOC-12)** — a non-`str` docname reaching `TypstPDFBuilder.finish()` now
  raises an actionable typsphinx-level error instead of a raw `TypeError` from deep inside the
  builder; and the published documentation's changelog page, frozen at 0.4.0 for two years, now
  carries every release through this one.

### Removed

- **Breaking:** the `typst_authors` config value is removed (CONF-10) — 0.7.0's documentation
  announced its removal in a future major release; this patch release removes it now.
  `typst_authors` is an unregistered `conf.py` variable that Sphinx ignores without any warning, so
  a project that still sets it loses its author information silently. See the migration guide for
  the `typst_template_function` `params["authors"]` rewrite; there is no deprecation shim.

### Verified

- No new **runtime** dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.

## [0.7.0] - 2026-08-04

API reference pages become readable in this release: autodoc/API output moves from a flat wall of
proportional bold text to something that reads as a typeset reference document — monospace
signatures, a hanging indent on description bodies, and visually distinguishable nesting between a
class and its members. The appearance of every emitted `.typ` file and its compiled PDF changes for
anyone building API documentation. Citations gain full round-trip support alongside this: a
document containing a citation no longer fails the Typst compile outright.

### Added

- **Citations — full round trip (CIT-01, CIT-02, CIT-03, CIT-04, CIT-05, CIT-06)** — `.. [Label]`
  definitions render as labelled hanging-indent entries in document order, `[Label]_` in-text
  references link to their definition, and each definition carries back-references to every citing
  location. Previously a document containing a citation failed the Typst compile outright — zero
  citation handlers existed. The citation syntax removed from `examples/charged-ieee/` in Phase 22.2
  is restored.

### Changed

- **Signatures render as real typography (SIG-01, SIG-02, SIG-03, SIG-04, SIG-05, SIG-06, SIG-07,
  SIG-08, SIG-09)** — object names, module/class qualifiers, keywords, parameters, and delimiters
  now render in bold and regular-weight monospace with italic proportional parameters and a real
  arrow glyph for return annotations, replacing the flat proportional-bold text emitted before. Long
  signatures wrap without overflowing the page margin, sibling signatures are separated by exactly
  one break, and a signature never splits from the first line of its body across a page break.
- **Description bodies and field lists indent by nesting depth (IND-01, IND-02, IND-03, IND-04,
  IND-05, FLD-01, FLD-02, FLD-03)** — a description body now indents relative to its own signature,
  cumulatively with nesting depth, off one shared indent constant, so a nested class member's body
  is visibly deeper than its parent's while the nested member's own signature aligns with its
  parent's body margin. Field lists (Parameters / Returns / Return type / Raises / Variables) indent
  one step beyond the surrounding body, and a field body's parameter names and types carry monospace
  treatment distinct from the plain-bold field label.
- **Admonition taxonomy re-bucketed and rubric now indents with its body (ADM-01, ADM-02, ADM-03,
  ADM-04, ADM-05, ADM-06)** — `seealso` joins the green `hint`/`tip` bucket and `attention` joins the
  red family instead of the orange warning bucket it used before, a generic `.. admonition::` renders
  as a styled box carrying its own title, and a `rubric` nested inside a description body (including
  autodoc's "Options" heading) indents with that body instead of sitting flush against the page
  margin.

### Fixed

- **Block math inside a list item no longer emits a redundant blank line (MATH-02)** — the extra
  blank line between the math expression and the following paragraph break, carried over from the
  v0.6.5 Phase 34 review, is gone.
- **A captioned table immediately preceded by a standalone target no longer drops the target's
  label (TBL-03)** — both the table's own name-derived label and the propagated target's label
  are now emitted, so a reference to either resolves instead of aborting the compile on a
  dangling label.

### Verified

- Zero new runtime dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.

## [0.6.5] - 2026-07-29

Fixes a compile-blocking defect where a document mixing prose and math could abort the Typst
compile: inline and display math no longer emit without a valid separator from surrounding text.
The runtime change is confined to the math handlers in `typsphinx/translator.py` — both the inline
and the display-math visitor gained separator participation — with no other file under `typsphinx/`
touched. Zero new runtime dependencies; the bundled `@preview` version-sync surface is untouched.

### Fixed

- **Inline math immediately after text no longer aborts the `typstpdf` compile (MATH-01)** — in
  bullet-list items, definition-list terms, and the like (including display math inside a list
  item, which is the same user-visible change), a missing separator between the preceding text
  emission and the `mi(...)` / `$...$` call previously produced Typst that failed to compile. Fixed
  on both emission paths — the mitex default and the native path.

### Verified

- Zero new runtime dependencies across the full milestone diff.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The full-corpus (Sphinx v9.1.0 `doc/`) `-b typstpdf` re-run remains fatal-free.

## [0.6.4] - 2026-07-28

Moves documentation hosting from GitHub Pages to Read the Docs: every published URL now resolves
against a Read the Docs project, a Japanese documentation site is live for the first time, and the
PDF a reader downloads from either site is the one typsphinx's own `typstpdf` builder produced — not
a LaTeX pipeline this project doesn't dogfood. The hand-rolled multi-language publishing machinery
this migration made obsolete is gone from the repository. Zero new runtime dependencies; the bundled
`@preview` version-sync surface (now covering four declaration sites) is untouched, and no line under
`typsphinx/` changed in this milestone.

### Added

- **Japanese documentation site at `/ja/latest/` (I18N-01, I18N-03)** — built from a separate
  `typsphinx-doc-translations` repository (a git submodule of this repository plus the relocated
  `ja` gettext catalogs) with its own Read the Docs project, linked under the English parent's
  Translations settings. The Japanese site is also downloadable as a PDF with its CJK glyphs
  correctly rendered.
- **Repository-wide link-check CI (CI-05)** — an advisory `links.yml` workflow now checks every
  published link across the whole repository (not just `docs/source/`, which is where Sphinx's own
  `linkcheck` cannot see the README/`pyproject.toml` links that motivated this).

### Changed

- **Documentation hosting moved from GitHub Pages to Read the Docs (RTD-01..RTD-04)** — built from a
  `.readthedocs.yaml` in the repository, with typsphinx itself installed from the in-repo commit
  (never a stale PyPI wheel). The downloadable PDF is produced by this project's own `typstpdf`
  builder via `build.jobs.build.pdf`, not Read the Docs' LaTeX pipeline.

### Removed

- **Hand-rolled multi-language publishing machinery and orphan documentation (I18N-02, DOC-08)** —
  `docs/build_multilang.py`, the custom language-switcher template, the `docs-multilang` tox
  environment, and the unreachable `docs/usage.rst`/`docs/installation.rst` orphan pair are gone.
  Language switching now works through Read the Docs' own flyout.
- **GitHub Pages hosting and the `gh-pages` branch (CI-04)** — the `peaceiris/actions-gh-pages` deploy
  step is removed from CI; the tag-time PDF Release attachment is unaffected. **Old
  `github.io` URLs now return 404 with no redirect** — an accepted cost of the immediate cutover.
  Automatic browser-language redirection at the documentation root is also gone: Read the Docs
  redirects to a *version*, never to a visitor's detected *language*; restoring that behavior would
  mean re-adding the custom template code this migration removes.

### Fixed

- **Seven dead documentation links in README/PyPI metadata resolved (DOC-09, DOC-10, Issue #119)** —
  every published documentation URL (README badges, deep links, `pyproject.toml`'s `Documentation`
  metadata) now points at `https://typsphinx.readthedocs.io/` and was confirmed live over real HTTP.

### Verified

- Milestone invariant held: zero new runtime dependencies, no `@preview` package version bump, the
  four-surface version-sync guard (`writer.py` / `template_engine.py` / `templates/base.typ` /
  `examples/**/*.typ`) untouched, and zero changes under `typsphinx/` across the full milestone diff.

## [0.6.3] - 2026-07-25

Closes out the config & docs fidelity milestone: configuration values documented in `typst_elements`
now reliably reach the compiled Typst output (an unrecognized key now fails the build loudly instead
of being silently dropped, and a second long-dead config value is removed), captioned tables render
as native Typst figures with "Table N" numbering and resolvable cross-references, and the Typst
typesetting language of every auto-generated label now follows Sphinx's own `language` setting
instead of being hardcoded to English. The user-facing configuration docs were also corrected to
match the registered config surface. Zero new runtime dependencies; the bundled `@preview`
version-sync surface is untouched.

### Added

- **Captioned tables render as numbered, cross-referenceable figures (TBL-01, TBL-02)** — a
  `.. table:: Caption` (or a captioned `csv-table`/`list-table`) now emits
  `figure(table(...), caption: {...}, kind: table)` with Typst's native "Table N" numbering, instead
  of a bare `table()` with no numbering and a stray preceding heading. A `:numref:`/`:ref:` to a
  captioned table now resolves to a working cross-reference in the compiled PDF. A table without a
  caption still renders as a plain `table()` (never speculatively figure-wrapped).

### Changed

- **BREAKING: An unrecognized `typst_elements` key now fails the build (CONF-04)** — previously, any
  `typst_elements` key outside `papersize`/`fontsize`/`lang` was silently dropped with no effect on
  the build; it now aborts with `ExtensionError: typst_elements: unknown key ...`. If your `conf.py`
  sets a key outside this allowlist, remove it; to keep passing a custom value through to a custom
  template, use `typst_template_function.params` instead. `papersize` and `fontsize` set via
  `typst_elements` now also reach the compiled `.typ`/PDF (previously silently dropped regardless of
  the allowlist).

### Removed

- **BREAKING: `typst_toctree_defaults` config value removed (CONF-05)** — it was registered but never
  consumed by any code path. A `conf.py` still setting it is silently ignored by Sphinx (unregistered
  config values produce no warning), and removal changes no build's output since the value never
  affected one. No deprecation period.

### Fixed

- **Typst's typesetting language now follows Sphinx's `language` config (CONF-07)** —
  `templates/base.typ` previously hardcoded `lang: "en"`, so a `language = "ja"` project's body text
  was already translated (Sphinx's own i18n transform) but Typst-generated labels stayed English —
  e.g. a captioned table showed "Table 1" instead of "表 1". The default template now derives `lang`
  from `config.language`; an explicit `typst_elements = {"lang": ...}` still overrides it on every
  path. Applies to the default-template path only — a custom template, `typst_package`, or a
  source-directory `base.typ` shadow is unaffected and must still declare its own `lang`.
- **The bundled `examples/advanced` sample builds again** — it was unbuildable on two independent
  axes: its `typst_elements` carried five keys outside the CONF-04 allowlist (now rejected loudly by
  this release), and its `_templates/custom.typ` had drifted three milestones behind on its
  `@preview` pins, aborting the compile with `unknown variable: kai`. The template now declares
  `papersize`/`fontsize`/`lang` in its `project()` — so the example demonstrates the allowlist rather
  than decorating around it — and `test_preview_version_sync.py` gained a check over
  `examples/**/*.typ` so a bundled sample can no longer drift out of lockstep unnoticed.
- **User-facing configuration docs corrected to match the registered config surface (DOC-07)** —
  `docs/source/user_guide/configuration.rst`'s `typst_author` renamed to the real `typst_authors`, the
  non-existent `typst_use_codly`/`typst_code_line_numbers` removed, and `typst_papersize`/
  `typst_fontsize` rewritten as working `typst_elements` examples; `docs/source/api/index.rst`'s
  redundant, drifted "Available Configuration Values" table removed in favor of a single canonical
  `:doc:` pointer.

### Verified

- Closing full-corpus regression gate: the Sphinx `doc/` v9.1.0 corpus, re-run through `-b typstpdf`,
  remains fatal-free, produces a valid `%PDF`-magic-byte output, and the `unknown_visit` catalogue
  remains empty.
- Milestone invariant held (as amended 2026-07-25): zero new runtime dependencies, no `@preview`
  package version bump, the 3-way version-sync surface (`writer.py` / `template_engine.py` /
  `templates/base.typ`) untouched by version string; `templates/base.typ`'s only diff from `main` is
  the 2-line `lang` parameter added in Phase 27.1.

## [0.6.2] - 2026-07-23

Rendering-fidelity round 2: closes out the remaining 13 medium/low findings from the v0.6.1 audit
across six root-cause clusters, fixes the typstpdf output-filename bug (Issue #117) and a
nested-master compile-root defect, repairs the Typst Universe (`typst_package`) template path
end-to-end, hardens the builder against silent partial-success, removes two long-dead config
values, and corrects several stale README/CLAUDE.md claims. Zero new runtime dependencies; the
bundled `@preview` version-sync surface is untouched.

### Removed

- **BREAKING: `typst_output_dir` and `typst_author_params` config values removed (CONF-01)** —
  both were registered but never read: `outdir` is controlled by the `sphinx-build` CLI argument,
  not a config value, and `typst_author_params` was silently ignored by the author-formatting code
  path. Neither ever affected compiled output, so removal changes no build's result; a `conf.py`
  still setting either is silently ignored by Sphinx (unregistered config values produce no
  warning), not an error. No deprecation period.

### Fixed

- **Lost block separation across five constructs (FID-02–FID-06)** — paragraphs inside list items,
  sibling signatures, rubric/option headings, definition-list terms, and back-to-back body-less
  confvals all rendered run-together with no visible break; each now renders with its own separation.
- **Lost intra-signature token spacing (FID-07–FID-09)** — the `class `/`exception ` keyword prefix,
  C/C++ signature/expression tokens (around `*`/`&`, type↔identifier), and object-description
  `:type:`/`:default:` fields all lost their spaces or boundaries; all now render correctly spaced.
- **Long inline-literal runs no longer clip at the right margin (FID-10)** — a long run of inline
  `:role:` literals now wraps within the text block instead of overflowing and clipping mid-token.
- **Soft/semantic paragraph line breaks now reflow (FID-11)** — a paragraph written with one clause
  per source line previously forced a hard break at every line; it now reflows into a justified
  paragraph like every other builder produces.
- **Codly config wrapper no longer leaks as visible text (FID-12)** — a captioned code block nested in
  a list item no longer prints its internal `{ codly(...) }` config wrapper as literal prose.
- **Meaning-bearing inline styling restored (FID-13–FID-14)** — external hyperlinks render with
  distinguishing link styling again, and Python `*`/`/` (PEP 3102/570) signature separators no longer
  inject their internal hover-title text inline.
- **`sphinx-build -b typstpdf` names the output PDF after your configured target, not the source
  docname (PDF-01, Issue #117)** — e.g. with `typst_documents = [("index", "mydoc", "My Manual",
  "Author")]`, the compiled PDF is now `mydoc.pdf` (previously `index.pdf`). If your CI or release
  pipeline references the old docname-based filename, update it.
- **Nested master documents compile with their includes and images intact (PDF-02)** — a master at a
  nested docname (e.g. `api/index`) now resolves `#include()`/`image()` paths on the same basis the
  translator emits them, matching what `-b typst` plus a manual `typst compile` already produced.
- **`typst_package` (Typst Universe template) configured alone now builds and compiles with zero
  Typst errors (CONF-02, CONF-03)** — fixes a missing `_template.typ` write, unconditional
  `title`/`authors`/`date` injection into templates that don't accept them, and
  `typst_authors`/`typst_author_params` being silently ignored. A new config→output regression
  fixture now asserts that a config value actually changes the compiled output, not merely that
  it's registered.
- **`sphinx-build -b typstpdf` no longer reports success while silently skipping a configured
  master (WR-01, WR-02)** — a missing `.typ` file or an unknown docname now fails the build with an
  aggregated error listing every failed master, instead of a bare warning and a `build succeeded`
  exit. (The nested-master render-gate test was also decoupled from `typst-py`'s internal
  error-message wording, so an unrelated upstream wording change can no longer turn CI red.)
- **README.md and CLAUDE.md corrected to match measured behavior (DOC-01–DOC-05)** — removed
  unverifiable test-count and coverage numbers with no enforced gate, reworded "Configuration
  Options" as an explicitly partial list linking to the real built documentation, dropped a false
  citation-support claim (added Citations to Known Limitations instead), removed a stale Glossary
  limitation, and corrected CLAUDE.md's Python-version floor (3.10+ → 3.12+) throughout.

### Verified

- Closing full-corpus regression gate: the Sphinx `doc/` v9.1.0 corpus, re-run through
  `-b typstpdf`, remains fatal-free, produces a valid `%PDF`-magic-byte output, and the
  `unknown_visit` catalogue remains empty.
- Milestone invariant held: zero new runtime dependencies, no `@preview` package version bump, the
  3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) untouched.

## [0.6.1] - 2026-07-20

Rendering fidelity: move `typstpdf` output from "compiles fatal-free" (achieved
in v0.6.0) to "renders faithfully to the source". Implements the last two
silently-dropped nodes, unifies length conversion across all figure/table
sites, and — driven by a full human-assisted visual audit of the Sphinx `doc/`
corpus — fixes the sole high-severity mis-render. Zero new runtime dependencies;
the bundled `@preview` version-sync surface is untouched.

### Added

- `todo_node` now renders as a gentle-clues `task()` box, gated on Sphinx's
  `todo_include_todos` config so draft work-notes never leak into published PDFs
  (TODO-01)
- `manpage` roles now render as italic literal page text via delegation to the
  emphasis handler (MAN-01)

### Changed

- Generalized v0.6.0's `visit_image`-local px→pt conversion into one shared
  `_convert_length_to_typst` helper, reused at every length-bearing figure and
  table site (LEN-01)

### Fixed

- **Wide-table glyph collision + right-margin clip (FID-01a)** — multi-column
  tables whose cell content exceeded the text block previously collided glyphs
  between columns and clipped the rightmost column off the page margin. Fixed by
  emitting fr-weighted `columns: (Nfr, …)` derived from docutils colwidth in
  `depart_table` and injecting U+200B break points after `.`/`_` in in-table
  content, proven by a real-compile `wide_table_render_gate` regression fixture

### Verified

- Full 151/151-docname human-assisted rendering-fidelity audit of the Sphinx
  v9.1.0 `doc/` corpus PDF against its `-b html` baseline (AUD-01); 15 systemic
  findings catalogued and human-confirmed. The 13 medium/low findings are
  tracked as backlog for a future milestone
- Closing corpus regression gate (GATE-03): the full ~684-page corpus re-run
  through `-b typstpdf` remains fatal-free with the `unknown_visit` catalogue
  empty of `todo_node`/`manpage`

## [0.6.0] - 2026-07-13

Real-world robustness: compile a large real-world documentation set (Sphinx's
own `doc/` tree) through the `typstpdf` builder with no fatal Typst errors, and
render the most-frequent previously-dropped docutils/Sphinx nodes correctly.
Driven by Issue #114. Zero new runtime dependencies — all work is in
`typsphinx/translator.py`; the bundled `@preview` version-sync surface is
untouched.

### Fixed

- **Issue #114 — fatal figure/image bugs**
  - `.. figure::`/image `:width:`/`:height:` in `px` (or other CSS length units)
    now converts to valid Typst — `px`→`pt` numeric conversion (1px = 0.75pt),
    `%`/`em`/`pt`/`cm`/`mm`/`in` pass through, unrecognized units are
    warned-and-dropped instead of emitted verbatim (FIG-01)
  - `.. figure::`/standalone image with a `:target:` link now emits valid
    `#figure(link(...)[#image(...)], caption: [...])` — the caption reaches the
    `caption:` argument via a buffer-swap and no longer leaks as a stray
    juxtaposed `text(...)` call (FIG-02)
  - Fixed additional latent fatals surfaced by the real-compile gate: labels
    attached to code-mode statements, a dangling `:term:` glossary anchor, and a
    footnote-buffer-swap paragraph-state clobber

### Added

- **High-frequency previously-dropped node handlers** (all with real-compile
  acceptance fixtures)
  - `refid` same-document cross-references (`:ref:` section anchors, `:term:`
    glossary links) render as working links instead of degrading to plain text
    (XREF-01)
  - `versionadded`/`versionchanged`/`deprecated`/`versionremoved` render as an
    unboxed italic Sphinx-worded label, not a callout box (VER-01)
  - Autodoc signature sub-parts: `desc_returns`, `desc_signature_line`,
    `desc_optional`, `desc_inline` (DESC-01…04)
  - `footnote`/`footnote_reference` via Typst-native `footnote[...]` using a
    document-order doctree pre-pass — first cite defines, repeat cites reuse by
    label (FN-01)
  - `transition` → horizontal rule, `.. topic::` → titled aside, `line`/
    `line_block` → verbatim `linebreak()`, `.. glossary::` → definition list,
    `.. tabularcolumns::` safely skipped, `:abbr:` → "term (expansion)"
    (BLK-01…06)
- **Graceful degradation** — `graphviz` and `inheritance_diagram` render a
  visible placeholder block + exactly one warning, with no raw source leaking
  (DEG-01/DEG-02)
- **Validation gates**
  - Standing real-compile acceptance-fixture pattern
    (`sphinx-build → typst.compile() → pypdf`) extended by every node-handler
    group (GATE-01)
  - Full-corpus gate: Sphinx's own `doc/` tree compiles end-to-end through
    `-b typstpdf` with no fatal `TypstCompilationError` (~14.4 MiB PDF,
    0 errors); residual `unknown_visit` warnings catalogued and the empty-URL
    reduction measured before/after (GATE-02)

## [0.5.0] - 2026-07-11

### Changed

- **Forward-Ecosystem Port**
  - Sphinx re-pinned to the `>=9.1,<10` line, `docutils` to `>=0.21,<0.23`, and `typst` to
    the `>=0.15.0,<0.16` line
  - Python floor raised to 3.12-3.13 (3.10 and 3.11 dropped from the support matrix)
  - Bundled `@preview` packages bumped in lockstep: `mitex` (`0.2.4`→`0.2.7`, the fix for
    `unknown variable: kai` under typst 0.15), `gentle-clues` (`1.2.0`→`1.3.1`), and
    `codly-languages` (`0.1.1`→`0.1.10`); `codly` confirmed to already compile cleanly at `1.3.0`

### Fixed

- **Admonition Rendering** (Phase 8.1)
  - Fixed a translator markup/code-mode mismatch that caused `.. note::`-style admonitions
    to render literal, unevaluated Typst source instead of typeset prose
  - Added coverage for previously-missing admonition types (`hint`, `error`, `danger`,
    `attention`, generic `.. admonition::`)

### Added

- **CI Durability Guardrails**
  - Added a `typst compile` smoke test that exercises all bundled `@preview` packages via
    real function calls, catching `kai`-class breaks before release
  - Updated `drift.yml` and the Dependabot dependency group to the new major-version ceilings

## [0.4.4] - 2026-07-05

### Changed

- **CI/Release Durability**
  - Python support floor raised to 3.10-3.13, with the CI and tox test matrices reconciled to match
  - `softprops/action-gh-release` bumped from `v2` to `v3` in the release workflow
  - `--locked` appended to every `uv sync` call site across the CI, docs, and release workflows
  - GitHub Actions artifact actions (`upload-artifact`/`download-artifact`) bumped to their Node 24 majors

### Added

- **Dependency and Release Guardrails**
  - Added a weekly dependency drift-detection workflow
  - Added a `sphinx-typst-stack` Dependabot group and a CI status badge to the README
  - Added Sphinx i18n infrastructure with Japanese translations and multi-language GitHub Pages support

### Fixed

- Fixed the release workflow's version-verify step to fall back from `tomllib` to `tomli` on Python versions where `tomllib` is unavailable

## [0.4.3] - 2025-11-01

### Changed

- **Project Status & Authorship**
  - Updated development status to "Production/Stable" in PyPI classifiers
  - Updated author information across all project files
  - Removed "Beta Release" designation from PyPI installation instructions

### Added

- **Template Asset Support** ([#75](https://github.com/YuSabo90002/typsphinx/issues/75))
  - Automatic copying of template assets (fonts, images, logos) to output directory
  - Three operation modes:
    - Default: Automatically copy entire template directory
    - Explicit: Specify assets with `typst_template_assets` list (supports glob patterns)
    - Disabled: Empty list `[]` prevents automatic copying
  - New configuration value: `typst_template_assets`
  - Only applies to local templates (`typst_template`), not Typst Universe packages
  - Added 8 comprehensive test cases for all scenarios
  - Updated documentation with usage examples

### Fixed

- **Empty URL Link Handling for Typst 0.14.1+ Compatibility** ([#77](https://github.com/YuSabo90002/typsphinx/issues/77))
  - Fixed empty URL references causing Typst 0.14.1 compilation errors
  - References with empty `refuri` attributes now rendered as plain text instead of invalid `link("", ...)`
  - Added warning messages for broken references to aid debugging
  - Updated Typst dependency to `>=0.14.1` for stricter URL validation support
  - Added comprehensive test coverage for empty URL handling scenarios
  - Prevents "URL must not be empty" errors in CI/CD pipelines

## [0.4.2] - 2025-10-29

### Fixed

- **Empty Table Cells Rendering** ([#68](https://github.com/YuSabo90002/typsphinx/issues/68), [#70](https://github.com/YuSabo90002/typsphinx/pull/70))
  - Fixed empty table cells causing Typst compilation errors
  - All table cells (normal and spanning) now wrapped in content blocks `{}`
  - Empty cells output as `{}` instead of bare commas
  - Prevents "unexpected comma" syntax errors in Typst
  - Added 5 comprehensive test cases for empty cell scenarios

- **Image Relative Paths in Nested Documents** ([#69](https://github.com/YuSabo90002/typsphinx/issues/69), [#72](https://github.com/YuSabo90002/typsphinx/pull/72))
  - Fixed image paths in nested documents failing to resolve during Typst compilation
  - Implemented `_compute_relative_image_path()` method (mirrors Issue #5 toctree fix)
  - Image URIs now adjusted based on output file location
  - Supports all path patterns: root, nested, deep nested, same directory, subdirectory, cross-directory
  - Added 6 comprehensive test cases for image path adjustment
  - Backward compatible: root document images unchanged

## [0.4.1] - 2025-10-26

### Fixed

- **Table Cell Unified Code Mode Compliance** ([#65](https://github.com/YuSabo90002/typsphinx/pull/65))
  - Fixed `table.cell()` argument order to match Typst signature (content as first positional argument)
  - Removed unnecessary markup mode `[...]` wrapping from table cells
  - Table cells now pass content type directly: `table.cell(content, colspan: 2)`
  - Improved consistency with Unified Code Mode guideline across all table elements

## [0.4.0] - 2025-10-26

### Fixed

- **Document Wrapper Preservation** ([#61](https://github.com/YuSabo90002/typsphinx/issues/61))
  - Fixed `#{...}` wrapper being lost in nested toctree structures
  - Implemented stream-based rendering to replace body swapping anti-pattern
  - Document wrapper now preserved throughout nested structures

- **Nested Lists Syntax** ([#62](https://github.com/YuSabo90002/typsphinx/issues/62))
  - Fixed nested lists generating invalid Typst syntax (`strong(...)list(...)`)
  - List items now use content blocks with newline separators
  - Proper separation between elements in list items

### Changed

- **Stream-Based Rendering Architecture**
  - Replaced body swapping with direct appending to `self.body`
  - State management using flags instead of buffer manipulation
  - Improved maintainability and predictability

- **Content Block Architecture**
  - Changed `strong()` and `emph()` to use content blocks: `strong({...})`, `emph({...})`
  - List items wrapped in `{...}` blocks with newline separators
  - Enables proper nesting: `strong({text("bold")})\nlist({...})`

- **Unified Code Mode Compliance**
  - Updated `link()` format from `link(url)[content]` to `link(url, content)`
  - Removed `#` prefixes from functions in code mode (table, admonitions)
  - Added `#` prefixes inside markup mode blocks `[...]` for label attachment
  - API signatures properly formatted: `text("(") + text("param") + text(")")`

### Changed (from v0.3.0)

- **BREAKING: Unified Code Mode Architecture** ([#4](https://github.com/YuSabo90002/typsphinx/issues/4))
  - Entire document now wrapped in `#{...}` code block for consistent function syntax
  - All Typst elements use bare function names without `#` prefix inside code block
  - All text wrapped in `text()` function with proper string escaping
  - All paragraphs wrapped in `par()` function to mark boundaries
  - Lists use function calls: `list(...)`, `enum(...)`, `terms(...)`
  - Inline code uses `raw()` with string escaping for `+` operator compatibility
  - Math functions use backtick raw strings: `mi(\`...\`)`, `mitex(\`...\`)`
  - Toctree uses `{...}` scope block for `set` rule isolation
  - Fixes underscores in text being interpreted as subscript markup
  - Fixes special characters requiring escaping in content mode
  - Generated `.typ` files compile cleanly without syntax errors
  - PDF output remains identical to previous versions
  - **Migration**: Existing projects will need to regenerate `.typ` files

- **Migrate CI to Tox**
  - GitHub Actions workflows now use tox commands for consistency
  - Added `docs-html`, `docs-pdf`, and `docs` tox environments
  - Simplified CI configuration with single source of truth in `tox.ini`
  - Improved local/CI consistency - same commands work in both environments
  - Updated test, lint, type-check, and coverage jobs to use tox
  - Documentation builds now reproducible locally with `tox -e docs-html` or `tox -e docs-pdf`
  - Fixed paths in existing tox environments (sphinxcontrib/ → typsphinx/)

### Added

- **Documentation Site with GitHub Pages** ([#36](https://github.com/YuSabo90002/typsphinx/issues/36))
  - Comprehensive documentation site hosted on GitHub Pages at https://yusabo90002.github.io/typsphinx/
  - Complete user guide covering installation, quickstart, configuration, builders, and templates
  - Extensive examples section with basic and advanced use cases
  - API reference with autodoc integration
  - Contributing guide with development workflow
  - Automated documentation deployment via GitHub Actions
  - HTML documentation built with Sphinx and Furo theme
  - PDF documentation generated using typsphinx itself (dogfooding)
  - PDF artifacts uploaded to GitHub Releases for tagged versions
  - Documentation badge added to README
  - 13 comprehensive documentation pages created

- **Typst Universe Template Support** ([#13](https://github.com/YuSabo90002/typsphinx/issues/13))
  - Full support for Typst Universe templates (charged-ieee, modern-cv, etc.)
  - `typst_template_function` now accepts dictionary format: `{"name": "ieee", "params": {...}}`
  - New `typst_authors` configuration for detailed author information (department, organization, email)
  - Template-specific parameters can be configured directly in `conf.py`
  - Python variable references work naturally in configuration (no special syntax needed)
  - Backward compatibility maintained for all existing configurations
  - Added comprehensive charged-ieee examples demonstrating two approaches:
    - Approach 1: Configuration-based (recommended, simple)
    - Approach 2: Custom template with Typst code (flexible)
  - Added 8 new test cases (4 for dict format, 4 for author details)
  - All 365 tests passing with full backward compatibility

- **Image File Copying Support** ([#38](https://github.com/YuSabo90002/typsphinx/issues/38))
  - Image files referenced in documents are now automatically copied to the output directory
  - Preserves directory structure when copying images
  - Enables successful PDF builds for documents containing images
  - Implemented `post_process_images()` and `copy_image_files()` methods in TypstBuilder
  - Images are copied before PDF compilation in TypstPDFBuilder
  - Added 9 comprehensive test cases covering various scenarios
  - No configuration required - images are copied automatically

- **Table Header Wrapping Support** ([#40](https://github.com/YuSabo90002/typsphinx/issues/40))
  - Table headers now wrapped in `table.header()` for proper Typst rendering
  - Enables automatic header repetition on multi-page tables
  - Provides accessibility metadata for screen readers and assistive technologies
  - Supports multi-row headers (`:header-rows: N` with N > 1)
  - Maintains backward compatibility for tables without headers
  - Added `in_thead` state flag to track header section in translator
  - Modified cell storage to include `is_header` flag
  - Updated `depart_table()` to generate `table.header()` wrapper for header cells
  - Complies with Typst documentation recommendations for table accessibility
  - Added 4 comprehensive test cases covering various header scenarios

- **Table Cell Spanning Support** ([#39](https://github.com/YuSabo90002/typsphinx/issues/39))
  - Added support for horizontal cell spanning (colspan) via `morecols` attribute
  - Added support for vertical cell spanning (rowspan) via `morerows` attribute
  - Cells with spanning now generate `table.cell(colspan: N, rowspan: M)` syntax
  - Supports combined horizontal and vertical spanning in same cell
  - Works correctly with header cells inside `table.header()`
  - Maintains backward compatibility for tables without cell spanning
  - Created `_format_table_cell()` helper method for consistent cell formatting
  - Reads `morecols`/`morerows` attributes in `visit_entry()`
  - Extended cell storage to include `colspan` and `rowspan` fields
  - Added 5 comprehensive test cases covering various spanning scenarios

## [0.3.0] - 2025-10-23

### Changed (Breaking)
- **Package Rename**: `sphinxcontrib-typst` → `typsphinx`
  - Changed to a simpler and more unique name
  - Reflects the nature of this package as a builder
  - PyPI package name: `typsphinx`
  - Python import: `import typsphinx`
  - Sphinx extension name: `extensions = ['typsphinx']`
  - Package structure: `sphinxcontrib/typst/` → `typsphinx/`
  - **Migration steps**:
    1. `pip uninstall sphinxcontrib-typst`
    2. `pip install typsphinx`
    3. Update `conf.py`: `extensions = ['sphinxcontrib.typst']` → `extensions = ['typsphinx']`

### Rationale
- `sphinxcontrib-*` namespace is traditionally for extensions that add directives or roles
- This package is primarily a builder (Sphinx→Typst conversion) and needs a more appropriate name
- Current low user base makes this the optimal timing for the change
- Unique and memorable name that represents the integration of Typst and Sphinx

## [0.2.2] - 2025-10-23

### Added
- **Additional Code Block Options Support** ([#31](https://github.com/YuSabo90002/typsphinx/issues/31))
  - Added support for `:lineno-start:` option to specify starting line number for code blocks
  - Added support for `:dedent:` option (handled automatically by Sphinx during parsing)
  - `:lineno-start:` works with codly's `start` parameter to display custom line numbers
  - Both options work correctly in combination with existing options (`:linenos:`, `:emphasize-lines:`, etc.)
  - Sphinx now supports 6 out of 8 standard code-block directive options (75%)
  - Added 7 comprehensive test cases covering various scenarios

- **Raw Directive Support** ([#25](https://github.com/YuSabo90002/typsphinx/issues/25))
  - Added support for docutils `raw` directive (`.. raw:: typst`)
  - Typst-specific content (`format='typst'`) is passed through to output
  - Other formats (html, latex, etc.) are skipped and logged
  - Format name matching is case-insensitive
  - Implemented `visit_raw()` and `depart_raw()` methods in TypstTranslator
  - Added 6 comprehensive test cases covering various scenarios

### Fixed
- **Code Block Directive Options Support** ([#20](https://github.com/YuSabo90002/typsphinx/issues/20))
  - Fixed `:linenos:` option being ignored - now properly controls line number display in code blocks
  - Fixed `:caption:` and `:name:` options causing "unknown node type: container" warnings
  - Code blocks with `:caption:` now wrapped in `#figure()` with proper caption
  - Code blocks with `:name:` now generate Typst labels for cross-referencing
  - Added `visit_container()` and `depart_container()` methods to handle Sphinx literal-block-wrapper containers
  - Extended `visit_literal_block()` and `depart_literal_block()` to support caption and label generation
  - Modified `visit_caption()` to skip caption text output for captioned code blocks (prevents duplication)
  - Line numbers now disabled by default when `:linenos:` is not specified (via `#codly(number-format: none)`)
  - All four options (`:linenos:`, `:caption:`, `:name:`, `:emphasize-lines:`) now work correctly together
  - Added comprehensive test coverage for all code block option combinations

- **PDF Builder codly Import Missing** ([#28](https://github.com/YuSabo90002/typsphinx/issues/28))
  - Fixed `typstpdf` builder failing with "unknown variable: codly" error
  - Added codly package imports to document-level essential imports in `template_engine.py`
  - Document files now include `#import "@preview/codly:1.3.0": *` and `#import "@preview/codly-languages:0.1.1": *`
  - Enables PDF generation for documents with code blocks (prerequisite for Issue #20)
  - No breaking changes - only adds imports alongside existing mitex/gentle-clues imports

### Documentation
- **README Math Example Fix** ([#33](https://github.com/YuSabo90002/typsphinx/pull/33))
  - Fixed incorrect double-escaped backslashes in math directive example
  - Changed `\\int` to `\int` for correct reStructuredText syntax
  - Helps users write proper reStructuredText files

## [0.2.1] - 2025-10-18

### Fixed
- **Table Content Duplication** ([#19](https://github.com/YuSabo90002/typsphinx/issues/19))
  - Fixed duplicate table content in Typst output where cell content appeared both as plain text and inside `#table()` structure
  - Affects all reStructuredText table formats: list-table, grid table, simple table, csv-table
  - Modified `add_text()` method to route text to `table_cell_content` when inside table cells
  - Modified `depart_table()` to use `self.body.append()` directly for table structure output
  - Added comprehensive test coverage for all table formats

- **RST Comments Rendered as Plain Text** ([#21](https://github.com/YuSabo90002/typsphinx/issues/21))
  - Fixed reStructuredText comments appearing as plain text in Typst output
  - Comments (lines starting with `..`) are now properly skipped during conversion
  - Resolved "unknown node type: comment" warning messages
  - Added `visit_comment()` and `depart_comment()` methods to TypstTranslator
  - Comments are completely omitted from output as intended for source-level documentation

## [0.1.0b1] - 2025-10-13

### Added

#### Core Features
- **Sphinx Builder Integration** (Requirement 1)
  - TypstBuilder registered as standard Sphinx builder
  - Entry point automatic discovery: `sphinx.builders` → `typst = "sphinxcontrib.typst"`
  - Command: `sphinx-build -b typst` and `sphinx-build -b typstpdf`

- **Doctree to Typst Conversion** (Requirement 2)
  - TypstWriter and TypstTranslator for node conversion
  - Support for 70+ standard docutils nodes + 14+ Sphinx addnodes
  - Document structure: sections, paragraphs, lists, tables
  - Inline elements: emphasis, strong, literal, subscript, superscript
  - Admonitions via gentle-clues (`@preview/gentle-clues:1.2.0`):
    - `note` → `#info[]`
    - `warning`/`caution` → `#warning[]`
    - `tip` → `#tip[]`
    - `important` → `#warning(title: "Important")[]`
    - `seealso` → `#info(title: "See Also")[]`

- **Cross-References and Links** (Requirement 3)
  - `nodes.reference` → `#link(url)[text]`
  - `nodes.target` → `<label>`
  - `addnodes.pending_xref` → `#link(<label>)[text]` or `#ref(<label>)`
  - Document and figure cross-references with `numref`
  - Inline references (`nodes.inline` with `xref` class)

- **Mathematical Expressions** (Requirements 4 & 5)
  - **LaTeX math via mitex** (`@preview/mitex:0.2.4`):
    - Block math: `#mitex(\`...\`)`
    - Inline math: `#mi(\`...\`)`
    - Supports LaTeX commands, environments, user-defined macros
  - **Native Typst math**:
    - Block: `$ ... $` with labeled equations
    - Inline: `$...$`
    - Typst-specific functions: `cal()`, `bb()`, `subset.eq`, etc.
  - **Fallback mode**: Basic LaTeX→Typst conversion when `typst_use_mitex = False`

- **Images and Figures** (Requirement 6)
  - `nodes.image` → `#image("path")`
  - `nodes.figure` → `#figure()` with captions
  - `nodes.table` → `#table()` with headers and rows
  - Figure/table labels and cross-references

- **Code Highlighting** (Requirement 7)
  - **Codly integration** (`@preview/codly:1.3.0` + `@preview/codly-languages:0.1.1`):
    - Automatic line numbering for all code blocks
    - Syntax highlighting for 50+ languages
    - Highlight specific lines via `#codly-range(highlight: (...))`
    - Language-specific icons and colors

- **Template System** (Requirement 8)
  - TemplateEngine for Typst template management
  - Default template with project metadata integration
  - Custom template support via `typst_template` config
  - Template parameter mapping: `typst_template_mapping`
  - Sphinx metadata → template parameters (title, authors, date, etc.)
  - Support for Typst Universe packages

- **Self-Contained PDF Generation** (Requirement 9)
  - TypstPDFBuilder using typst-py (PyPI: `typst>=0.11.1`)
  - No external Typst CLI required
  - Command: `sphinx-build -b typstpdf`
  - Automatic .typ → .pdf conversion
  - Platform support: Linux, macOS, Windows

- **Error Handling and Logging** (Requirement 10)
  - Sphinx logger integration with warning/error levels
  - Unknown node fallback with warnings
  - Template/resource error handling
  - PDF compilation error reporting (`TypstCompilationError`)

- **Multi-Document Integration** (Requirement 13)
  - Each .rst → independent .typ file
  - `toctree` → `#include()` directives
  - Heading level adjustment: `#set heading(offset: 1)`
  - `#outline()` managed in templates (not in document body)
  - Toctree options → template parameters:
    - `:maxdepth:` → `toctree_maxdepth`
    - `:numbered:` → `toctree_numbered`
    - `:caption:` → `toctree_caption`

#### Configuration Options
- `typst_use_mitex`: Enable/disable mitex for LaTeX math (default: `True`)
- `typst_template`: Custom template path
- `typst_elements`: Template parameters (paper size, fonts, etc.)
- `typst_template_mapping`: Sphinx metadata to template parameter mapping
- `typst_toctree_defaults`: Default toctree options
- `typst_package`: External Typst Universe package
- `typst_package_imports`: Package imports
- `typst_template_function`: Template function name
- `typst_output_dir`: Output directory structure
- `typst_debug`: Debug mode

#### Documentation and Examples
- Installation guide: `docs/installation.rst`
- Usage guide: `docs/usage.rst` (600+ lines)
- Configuration reference: `docs/configuration.rst` (400+ lines, 11 config values)
- Basic example: `examples/basic/`
- Advanced example: `examples/advanced/` (toctree, LaTeX math, code, tables)

#### Testing and Quality Assurance
- **286 tests** with **93% code coverage**:
  - Unit tests: builder, translator, template engine, PDF generation
  - Integration tests: basic, multi-document, advanced features
  - Documentation tests: installation, configuration, usage
  - Example tests: basic and advanced examples
- **Multi-version testing** via tox:
  - Python 3.9, 3.10, 3.11, 3.12
  - tox environments: py39, py310, py311, py312, lint, type, cov
- **CI/CD pipeline** (GitHub Actions):
  - Test matrix: 3 OSes × 4 Python versions
  - Lint (black, ruff), type check (mypy)
  - Code coverage reporting (Codecov)
  - Package build validation (twine check)
- **Code quality tools**:
  - black (code formatting)
  - ruff (linting)
  - mypy (type checking)

### Known Limitations

- **Requirement 11** (Extensibility and Plugin Support): Custom node handler registry not yet implemented
  - Planned for v0.2.0
  - Workaround: Extend TypstTranslator directly
- **Bibliography**: BibTeX integration not yet supported
- **Glossary**: Glossary generation not yet supported
- **Index**: Index generation not yet supported

### Technical Details

#### Requirements Fulfilled
- Requirement 1: Sphinx Builder Integration (100%)
- Requirement 2: Doctree to Typst Conversion (100%)
- Requirement 3: Cross-References and Links (100%)
- Requirement 4: Math Support (mitex) (100%)
- Requirement 5: Typst Native Math (100%)
- Requirement 6: Figures and Tables (100%)
- Requirement 7: Code Highlighting (100%)
- Requirement 8: Templates and Customization (100%)
- Requirement 9: Self-Contained PDF Generation (100%)
- Requirement 10: Error Handling and Logging (100%)
- ⏳ Requirement 11: Extensibility (Planned for v0.2.0)
- Requirement 12: Testing and Documentation (100%)
- Requirement 13: Multi-Document Integration (100%)

**Total: 12 out of 13 requirements fully implemented**

#### Dependencies
- Python: ≥3.9
- Sphinx: ≥5.0
- docutils: ≥0.18
- typst (typst-py): ≥0.11.1

#### Typst Packages Used
- `@preview/mitex:0.2.4`: LaTeX math rendering
- `@preview/codly:1.3.0`: Code syntax highlighting
- `@preview/codly-languages:0.1.1`: Language definitions
- `@preview/gentle-clues:1.2.0`: Admonition styling

### Development Tools
- **uv**: Fast package management and dependency resolution
- **pytest**: Testing framework (286 tests)
- **tox**: Multi-version testing automation
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking
- **sphinx-testing**: Sphinx extension testing helpers

---

## [0.2.0] - 2025-10-16

### Fixed

- **Issue #5**: Fixed nested toctree relative path issues in `#include()` directives (PR #14)
  - Corrected relative path calculation for nested toctree structures
  - Added comprehensive debug logging for path resolution
  - Added E2E Typst compilation tests and integration tests
  - Improved code coverage to 94%

- **Issue #10**: Fixed typstpdf builder auto-discovery (PR #12)
  - Registered `typstpdf` builder in `entry_points` for automatic Sphinx discovery
  - Updated documentation to reflect optional extension registration
  - Added test coverage for typstpdf entry point

### Improved

- **Issue #7**: Simplified toctree output format (PR #15)
  - Changed from multiple `#block(breakable: true)[]` to single content block
  - Improved readability and maintainability of generated Typst code
  - Resolved lint and format errors in test files

### Documentation

- **Issue #6**: Documented custom node support using Sphinx standard API (PR #16)
  - Added "Working with Third-Party Extensions" section to README.md
  - Documented usage of Sphinx's standard `app.add_node()` API
  - Provided practical example with sphinxcontrib-mermaid integration
  - Clarified that NodeHandlerRegistry is unnecessary - Sphinx already provides this functionality
  - **Requirement 11 is now complete**: Custom node support via Sphinx's standard extension mechanism

- **Issue #8**: Added acknowledgment for AI-assisted development (PR #9)
  - Added Claude Code and Kiro-style Spec-Driven Development to acknowledgments

- **PR #11**: Improved CLAUDE.md with repository information and guidelines
  - Added repository owner and URL information
  - Added language guidelines for GitHub interactions
  - Added issue template references

### Dependencies

- **Dependabot updates**:
  - Bump astral-sh/setup-uv from 4 to 7 (PR #1)
  - Bump actions/checkout from 4 to 5 (PR #2)
  - Bump codecov/codecov-action from 4 to 5 (PR #3)

### Requirements Status

**All 13 requirements now fully implemented**:
- Requirement 1: Sphinx Builder Integration (100%)
- Requirement 2: Doctree to Typst Conversion (100%)
- Requirement 3: Cross-References and Links (100%)
- Requirement 4: Math Support (mitex) (100%)
- Requirement 5: Typst Native Math (100%)
- Requirement 6: Figures and Tables (100%)
- Requirement 7: Code Highlighting (100%)
- Requirement 8: Templates and Customization (100%)
- Requirement 9: Self-Contained PDF Generation (100%)
- Requirement 10: Error Handling and Logging (100%)
- Requirement 11: Extensibility and Plugin Support (100%) - **Now complete**
- Requirement 12: Testing and Documentation (100%)
- Requirement 13: Multi-Document Integration (100%)

### Testing

- **317 tests** with **94% code coverage**
- All tests passing across Python 3.9, 3.10, 3.11, 3.12
- CI/CD pipeline validated on Linux, macOS, Windows

---

[0.9.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.0
[0.8.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.8.0
[0.7.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.1
[0.7.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.7.0
[0.6.5]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.5
[0.6.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.4
[0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3
[0.6.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.2
[0.6.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.1
[0.6.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.0
[0.5.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.5.0
[0.4.4]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.4
[0.4.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.3
[0.4.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.2
[0.4.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.1
[0.4.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.4.0
[0.3.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.3.0
[0.2.2]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.2
[0.2.1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.1
[0.2.0]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.2.0
[0.1.0b1]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.1.0b1
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD
