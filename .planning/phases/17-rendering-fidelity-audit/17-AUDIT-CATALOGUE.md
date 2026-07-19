# Phase 17 Audit Catalogue: Rendering-Fidelity Issues

**Requirement:** AUD-01 (17-CONTEXT.md D-01..D-11, 17-RESEARCH.md)
**Status:** Infrastructure ready (Plan 17-01 complete) — page-by-page visual pass NOT yet started (Plan 17-02+)

This is the D-07 deliverable: a single committed Markdown catalogue of every *silent*
rendering-fidelity issue found by visually diffing the compiled Sphinx-`doc/` corpus PDF
(`typstpdf` builder) against the same corpus's rendered HTML baseline (D-04/D-05 authority).
Phase 18's planner reads this file directly to build the FID-01a... fix backlog.

## Provenance

Measured **fresh, in this session** (2026-07-19) — NOT copied from
`.planning/phases/15-full-corpus-validation/15-CORPUS-REPORT.md` (RESEARCH Pitfall 7: that
report's PDF byte size, `15,124,122` bytes, predates Phase 16's `todo_node`/`manpage`
handlers and is now stale).

| Field | Value |
|-------|-------|
| Corpus source | `https://github.com/sphinx-doc/sphinx.git` |
| Resolved corpus tag | `v9.1.0` (matches installed `sphinx.__version__`) |
| Corpus clone commit SHA | `cc7c6f435ad37bb12264f8118c8461b230e6830c` |
| Corpus cache path | `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc` |
| Sphinx version | 9.1.0 |
| typst (typst-py) version | 0.15.0 |
| pypdf version | 6.14.2 (page-mapping/outline extraction) |
| typsphinx wiring | `tests/test_corpus_gate.py::wire_typsphinx_into_corpus_conf` (unmodified, reused) |
| PDF build command | `sys.executable -m sphinx -b typstpdf <corpus doc/> <scratch>/corpus_pdf_build` (via `tcg._run_corpus_sphinx_build`, unmodified) |
| HTML baseline build command | `sys.executable -m sphinx -b html <corpus doc/> <scratch>/corpus_html_build` (D-04/D-05 authority, same cached corpus) |
| Text pre-filter build command | `sys.executable -m sphinx -b text <corpus doc/> <scratch>/corpus_text_build` (optional triage aid, same cached corpus) |
| `index.pdf` byte size (THIS session) | **15,153,646 bytes** (~14.5 MiB) — differs from Phase 15's stale 15,124,122 bytes by +29,524 bytes, consistent with Phase 16's `todo_node`/`manpage` content now rendering instead of being silently dropped |
| `index.pdf` page count | **684 pages** |
| `typstpdf` build result | `build succeeded, 46 warnings` (0 errors) |
| `unknown_visit` catalogue (typstpdf build stderr) | **EMPTY** — `[]` — confirms Phase 16's TODO-01/MAN-01 handlers landed; `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` passed with the same empty-catalogue assertion this session |
| `-b html` baseline build result | `build succeeded, 24 warnings` (0 errors) |
| `-b text` pre-filter build result | `build succeeded, 24 warnings` (0 errors) |
| Environment smoke check | `nix-shell -p poppler-utils --run "pdftoppm -v"` → poppler-utils 26.06.0, exit 0 (in-sandbox network to cache.nixos.org available this session — no outside-sandbox fallback needed) |

All three builds (`typstpdf`, `html`, `text`) were run against the **SAME** cached corpus tree
in the **SAME** session, satisfying D-05. Build artifacts (PDF, per-docname `.typ`/`.html`/`.txt`
files, rasterized page PNGs) are **ephemeral scratch, never committed** — they lived in a
session-local scratch directory outside the repository and are not part of this commit.

## Severity Rubric (D-08, verbatim)

The axis is **"what does the reader lose."**

- **high** (locked by SC#4): content lost, unreadable, or grossly mis-structured.
- **medium**: content readable but meaning or distinction lost (code-literal rendered as prose,
  lost emphasis, link flattened to plain text, table column shift, …).
- **low**: meaning intact but finish is sloppy (stray whitespace, indentation wobble, …).

**Comparison baseline (D-04):** the rendered HTML build (`-b html` above) is the authority;
rST source is read only when intent needs confirming. **Divergence scope (D-06):** content
loss/duplication/misordering, structural breakage (lists, tables, heading hierarchy), and loss
of meaning-bearing styling are IN scope. Pure appearance differences (colors, fonts, margins,
page breaks, theme chrome like sidebars/navigation) are expected PDF-vs-HTML media differences,
NOT findings — never catalogue them.

## Out-of-Scope Classification (SC#3)

Per `.planning/REQUIREMENTS.md`'s Out of Scope table, the following are pre-classified as
out-of-scope and must **never** enter the issue table below, regardless of how they look on
either side of the comparison (RESEARCH Pitfall 4):

| Signature | Reason | Known docnames in this corpus |
|-----------|--------|--------------------------------|
| `graphviz` / `inheritance_diagram` directive nodes | Intentional graceful-degrade placeholder (DEG-01/DEG-02) — full graphical rendering is DEG-03 (deferred). Both `-b html` and `-b typstpdf` independently show the same non-fatal `dot` 実行不可 degrade placeholder; this is working as designed, not a divergence. | `usage/extensions/graphviz`, `usage/extensions/inheritance` |
| Non-included-document cross-references | `typstpdf` compiles a single master document; a target outside the `#include()` tree cannot be linked, so plain-text degradation is spec-appropriate. | (identified during the visual pass, not enumerable in advance) |
| Sphinx-side autodoc import failures / `py:meth` unresolved-reference warnings | Emitted during Sphinx's read/resolve phase, builder-independent (occur under `-b html` too); caused by the corpus's own missing optional deps, not by typsphinx rendering. | (identified during the visual pass, not enumerable in advance) |

## Issue Table (D-09 schema)

Empty — the page-by-page visual pass (Plan 17-02+) has not started yet. Columns are the exact
D-09 required fields; every future row must have all 8 populated (SC#2 schema/completeness
check).

| # | Docname | Node Kind | Source-vs-Output Description | Severity | PDF Page | Occurrence Count | Minimal Repro (snippet or source-line pointer) | Uncertain? |
|---|---------|-----------|-------------------------------|----------|----------|-------------------|--------------------------------------------------|------------|
| _(none yet)_ | | | | | | | | |

## Docname → Page-Range Mapping

Derived mechanically (RESEARCH Pattern 2, corrected v2 — see "Mapping Methodology" below) by
combining `pypdf`'s PDF outline/bookmark API (`PdfReader(...).outline` +
`get_destination_page_number()`, structural PDF metadata — never the in-body `#outline()`
rendered page, RESEARCH anti-pattern) with a **position-ordered** recursive walk of the master
`index.typ`'s `#include("...")` calls interleaved with its own `heading(level: ...)` calls, in
the exact textual order they appear in each `.typ` file (== Typst's sequential rendering order).

**151 distinct docnames**, covering pages 16–684 (front-matter pages 1–15 — cover page + the
Typst-generated in-body `#outline()` table of contents — belong to no docname and are excluded
from the per-docname audit unit; D-02 tracks docname progress, not front-matter pages).

Pages marked "(shared)" mean the docname's own content ends on the SAME page the next docname's
content begins (no page break between them) — both docnames still get a `#heading()` on that
page and are independently locatable via the PDF viewer's bookmark panel or a `Ctrl+F` for the
listed "First Heading" text.

### Mapping Methodology (deviation from a literal "one contiguous range" reading of the plan)

RESEARCH Pattern 2's "first heading = start page, next start − 1 = end page" recipe assumes a
docname's own headings are all textually contiguous before its first `#include()` call. The
mandated boundary spot-check (RESEARCH Pitfall 2) caught a real violation of that assumption
during this session: a naive "count headings then take a contiguous slice of the flat outline"
partition misattributed page 48's `13.1 User guide` heading (a level-2 heading that is
literally part of the master `index` docname's own content — Sphinx's `doc/index.rst` has FOUR
h2 sections — "Get started" / "User guide" / "Community guide" / "Reference guide" — each
immediately followed by its own `toctree`, so `index`'s own headings are genuinely interleaved
between four separate groups of child pages) to `usage/index` instead of `index`.

**Fix applied:** walk each `.typ` file's own text **position-ordered** (both `heading(` calls
and `include(` calls sorted by their character offset in the source, not grouped by type),
recursing into an included child file at the exact point its `include()` call appears. This
produces one (docname, title, page) tag per heading in TRUE rendering order, verified by
re-running all 4 mandated spot-checks (corpus-start `index` p.16, mid-corpus
`usage/configuration` p.313, corpus-end `examples` p.675, and the exact `index`/`usage/index`/
`usage/markdown`/`usage/referencing` 4-way page-49 adjacency edge case) against the actual
rasterized PDF pages — all 4 confirmed correct after the fix (see `17-01-SUMMARY.md`
"Deviations" for the full before/after evidence).

**Consequence for the table below:** 5 docnames have **non-contiguous own content** (their
headings are split across more than one page range because they are multi-toctree-group landing
pages) — flagged with multiple page ranges in the Pages column: `index`, `usage/domains/index`,
`development/html_themes/index`, `man/index`, `usage/extensions/index`. Every OTHER docname
(146 of 151) has a single clean contiguous range. This is a more accurate representation of the
real document structure than forcing one artificial contiguous range per docname would be, and
still satisfies D-02's actual need: "for any docname, look up where its content is."


### Full Table (151 docnames, page 1-indexed)

| # | Docname | Pages (1-indexed) | First Heading | Notes |
|---|---------|--------------------|-----|-------|
| 1 | `index` | 16-17; 48-48; 282(shared); 300(shared) (non-contiguous — landing page interleaves own headings between toctree groups) | 2 Sphinx |  |
| 2 | `usage/installation` | 18-20 | 3 Installing Sphinx |  |
| 3 | `usage/quickstart` | 21-26 | 4 Getting started |  |
| 4 | `tutorial/index` | 27-27 | 5 Build your first project |  |
| 5 | `tutorial/getting-started` | 28-29 | 6 Getting started |  |
| 6 | `tutorial/first-steps` | 30-31 | 7 First steps to document your project using Sphinx |  |
| 7 | `tutorial/more-sphinx-customization` | 32-32 | 8 More Sphinx customization |  |
| 8 | `tutorial/narrative-documentation` | 33-34 | 9 Narrative documentation in Sphinx |  |
| 9 | `tutorial/describing-code` | 35-39 | 10 Describing code in Sphinx |  |
| 10 | `tutorial/automatic-doc-generation` | 40-42 | 11 Automatic documentation generation from code |  |
| 11 | `tutorial/deploying` | 43-47 | 12 Appendix: Deploying a Sphinx project online |  |
| 12 | `tutorial/end` | 48 (shared with adjacent doc, no dedicated full page) | 13 Where to go from here |  |
| 13 | `usage/index` | 49 (shared with adjacent doc, no dedicated full page) | 14 Using Sphinx |  |
| 14 | `usage/markdown` | 49 (shared with adjacent doc, no dedicated full page) | 15 Markdown |  |
| 15 | `usage/referencing` | 49-53 | 16 Cross-references |  |
| 16 | `usage/builders/index` | 54-67 | 17 Builders |  |
| 17 | `usage/domains/index` | 68-68; 103-105 (non-contiguous — landing page interleaves own headings between toctree groups) | 18 Domains |  |
| 18 | `usage/domains/standard` | 69-70 | 19 The Standard Domain |  |
| 19 | `usage/domains/c` | 71-75 | 20 The C Domain |  |
| 20 | `usage/domains/cpp` | 76-86 | 21 The C++ Domain |  |
| 21 | `usage/domains/javascript` | 87-88 | 22 The JavaScript Domain |  |
| 22 | `usage/domains/mathematics` | 89 (shared with adjacent doc, no dedicated full page) | 23 The Mathematics Domain |  |
| 23 | `usage/domains/python` | 89-101 | 24 The Python Domain |  |
| 24 | `usage/domains/restructuredtext` | 102-102 | 25 The reStructuredText Domain |  |
| 25 | `usage/theming` | 106-111 | 26 HTML theming |  |
| 26 | `usage/advanced/intl` | 112-117 | 27 Internationalization |  |
| 27 | `usage/advanced/websupport/index` | 118 (shared with adjacent doc, no dedicated full page) | 28 Sphinx Web Support |  |
| 28 | `usage/advanced/websupport/quickstart` | 118-122 | 29 Web Support Quick Start |  |
| 29 | `usage/advanced/websupport/api` | 123-123 | 30 The WebSupport class |  |
| 30 | `usage/advanced/websupport/searchadapters` | 124-124 | 31 Search adapters |  |
| 31 | `usage/advanced/websupport/storagebackends` | 125 (shared with adjacent doc, no dedicated full page) | 32 Storage backends |  |
| 32 | `development/index` | 125 (shared with adjacent doc, no dedicated full page) | 33 Extending Sphinx |  |
| 33 | `development/tutorials/index` | 125 (shared with adjacent doc, no dedicated full page) | 34 Tutorials |  |
| 34 | `development/tutorials/extending_syntax` | 125-129 | 35 Extending syntax with roles and directives |  |
| 35 | `development/tutorials/extending_build` | 130-140 | 36 Extending the build process |  |
| 36 | `development/tutorials/adding_domain` | 141-151 | 37 Adding a reference domain |  |
| 37 | `development/tutorials/autodoc_ext` | 152-154 | 38 Developing autodoc extensions |  |
| 38 | `development/howtos/index` | 155 (shared with adjacent doc, no dedicated full page) | 39 How-tos |  |
| 39 | `development/howtos/setup_extension` | 155-155 | 40 Depend on another extension |  |
| 40 | `development/howtos/builders` | 156 (shared with adjacent doc, no dedicated full page) | 41 Configuring builders |  |
| 41 | `development/html_themes/index` | 156-160; 169-172 (non-contiguous — landing page interleaves own headings between toctree groups) | 42 HTML theme development |  |
| 42 | `development/html_themes/templating` | 161-168 | 43 Templating |  |
| 43 | `extdev/index` | 173-176 | 44 Sphinx API |  |
| 44 | `extdev/appapi` | 177-194 | 45 Application API |  |
| 45 | `extdev/event_callbacks` | 195-201 | 46 Event callbacks API |  |
| 46 | `extdev/projectapi` | 202-202 | 47 Project API |  |
| 47 | `extdev/envapi` | 203-204 | 48 Build environment API |  |
| 48 | `extdev/builderapi` | 205-207 | 49 Builder API |  |
| 49 | `extdev/eventapi` | 208-209 | 50 Event Manager API |  |
| 50 | `extdev/collectorapi` | 210-210 | 51 Environment Collector API |  |
| 51 | `extdev/markupapi` | 211-214 | 52 Docutils markup API |  |
| 52 | `extdev/domainapi` | 215-221 | 53 Domain API |  |
| 53 | `extdev/parserapi` | 222-222 | 54 Parser API |  |
| 54 | `extdev/nodes` | 223-228 | 55 Doctree node classes added by Sphinx |  |
| 55 | `extdev/logging` | 229-229 | 56 Logging API |  |
| 56 | `extdev/i18n` | 230-232 | 57 i18n API |  |
| 57 | `extdev/utils` | 233-237 | 58 Utilities |  |
| 58 | `extdev/testing` | 238-238 | 59 Testing API |  |
| 59 | `extdev/deprecated` | 239-249 | 60 Deprecated APIs |  |
| 60 | `latex` | 250-281 | 62 LaTeX customization |  |
| 61 | `support` | 282 (shared with adjacent doc, no dedicated full page) | 63 Get support |  |
| 62 | `internals/index` | 282 (shared with adjacent doc, no dedicated full page) | 64 Contribute to Sphinx |  |
| 63 | `internals/contributing` | 282-287 | 65 Contributing to Sphinx |  |
| 64 | `internals/release-process` | 288-288 | 66 Sphinx's release process |  |
| 65 | `internals/organization` | 289-289 | 67 Organization of the Sphinx project |  |
| 66 | `internals/code-of-conduct` | 290-290 | 68 Sphinx Code of Conduct |  |
| 67 | `faq` | 291-296 | 69 Sphinx FAQ |  |
| 68 | `authors` | 297-299 | 70 Sphinx authors |  |
| 69 | `man/index` | 300(shared); 308(shared) (non-contiguous — landing page interleaves own headings between toctree groups) | 71 Command-line tools |  |
| 70 | `man/sphinx-quickstart` | 300-301 | 72 sphinx-quickstart |  |
| 71 | `man/sphinx-build` | 302-307 | 73 sphinx-build |  |
| 72 | `man/sphinx-apidoc` | 308-310 | 74 sphinx-apidoc |  |
| 73 | `man/sphinx-autogen` | 311-312 | 75 sphinx-autogen |  |
| 74 | `usage/configuration` | 313-374 | 76 Configuration |  |
| 75 | `usage/extensions/index` | 375(shared); 450-450 (non-contiguous — landing page interleaves own headings between toctree groups) | 77 Extensions |  |
| 76 | `usage/extensions/apidoc` | 375-376 | 78 sphinx.ext.apidoc – Generate API documentation from Python packages |  |
| 77 | `usage/extensions/autodoc` | 377-399 | 79 sphinx.ext.autodoc – Include documentation from docstrings |  |
| 78 | `usage/extensions/autosectionlabel` | 400 (shared with adjacent doc, no dedicated full page) | 80 sphinx.ext.autosectionlabel – Allow referencing sections by their title |  |
| 79 | `usage/extensions/autosummary` | 400-406 | 81 sphinx.ext.autosummary – Generate autodoc summaries |  |
| 80 | `usage/extensions/coverage` | 407-408 | 82 sphinx.ext.coverage – Collect doc coverage stats |  |
| 81 | `usage/extensions/doctest` | 409-415 | 83 sphinx.ext.doctest – Test snippets in the documentation |  |
| 82 | `usage/extensions/duration` | 416-416 | 84 sphinx.ext.duration – Measure durations of Sphinx processing |  |
| 83 | `usage/extensions/extlinks` | 417-417 | 85 sphinx.ext.extlinks – Markup to shorten external links |  |
| 84 | `usage/extensions/githubpages` | 418-418 | 86 sphinx.ext.githubpages – Publish HTML docs in GitHub Pages |  |
| 85 | `usage/extensions/graphviz` | 419-421 | 87 sphinx.ext.graphviz – Add Graphviz graphs | OUT OF SCOPE (SC#3 — graphviz/inheritance_diagram graceful-degrade placeholder, DEG-01/02) |
| 86 | `usage/extensions/ifconfig` | 422-422 | 88 sphinx.ext.ifconfig – Include content based on configuration |  |
| 87 | `usage/extensions/imgconverter` | 423 (shared with adjacent doc, no dedicated full page) | 89 sphinx.ext.imgconverter – A reference image converter using Imagemagick |  |
| 88 | `usage/extensions/inheritance` | 423-425 | 90 sphinx.ext.inheritance_diagram – Include inheritance diagrams | OUT OF SCOPE (SC#3 — graphviz/inheritance_diagram graceful-degrade placeholder, DEG-01/02) |
| 89 | `usage/extensions/intersphinx` | 426-430 | 91 sphinx.ext.intersphinx – Link to other projects' documentation |  |
| 90 | `usage/extensions/linkcode` | 431-431 | 92 sphinx.ext.linkcode – Add external links to source code |  |
| 91 | `usage/extensions/math` | 432-436 | 93 Math support for HTML outputs in Sphinx |  |
| 92 | `usage/extensions/napoleon` | 437-447 | 94 sphinx.ext.napoleon – Support for NumPy and Google style docstrings |  |
| 93 | `usage/extensions/todo` | 448 (shared with adjacent doc, no dedicated full page) | 95 sphinx.ext.todo – Support for todo items |  |
| 94 | `usage/extensions/viewcode` | 448-449 | 96 sphinx.ext.viewcode – Add links to highlighted source code |  |
| 95 | `usage/restructuredtext/index` | 451 (shared with adjacent doc, no dedicated full page) | 97 reStructuredText |  |
| 96 | `usage/restructuredtext/basics` | 451-461 | 98 reStructuredText Primer |  |
| 97 | `usage/restructuredtext/roles` | 462-466 | 99 Roles |  |
| 98 | `usage/restructuredtext/directives` | 467-495 | 100 Directives |  |
| 99 | `usage/restructuredtext/field-lists` | 496-496 | 101 Field Lists |  |
| 100 | `usage/restructuredtext/domains` | 497-497 | 102 MOVED: Domains |  |
| 101 | `glossary` | 498-498 | 103 Glossary |  |
| 102 | `changes/index` | 499-499 | 104 Changelog |  |
| 103 | `changes/9.0` | 500-504 | 105 Sphinx 9.0 |  |
| 104 | `changes/8.2` | 505-508 | 106 Sphinx 8.2 |  |
| 105 | `changes/8.1` | 509-511 | 107 Sphinx 8.1 |  |
| 106 | `changes/8.0` | 512-513 | 108 Sphinx 8.0 |  |
| 107 | `changes/7.4` | 514-518 | 109 Sphinx 7.4 |  |
| 108 | `changes/7.3` | 519-523 | 110 Sphinx 7.3 |  |
| 109 | `changes/7.2` | 524-526 | 111 Sphinx 7.2 |  |
| 110 | `changes/7.1` | 527-528 | 112 Sphinx 7.1 |  |
| 111 | `changes/7.0` | 529-529 | 113 Sphinx 7.0 |  |
| 112 | `changes/6.2` | 530-531 | 114 Sphinx 6.2 |  |
| 113 | `changes/6.1` | 532-532 | 115 Sphinx 6.1 |  |
| 114 | `changes/6.0` | 533-534 | 116 Sphinx 6.0 |  |
| 115 | `changes/5.3` | 535 (shared with adjacent doc, no dedicated full page) | 117 Sphinx 5.3 |  |
| 116 | `changes/5.2` | 535-535 | 118 Sphinx 5.2 |  |
| 117 | `changes/5.1` | 536-537 | 119 Sphinx 5.1 |  |
| 118 | `changes/5.0` | 538-540 | 120 Sphinx 5.0 |  |
| 119 | `changes/4.5` | 541-541 | 121 Sphinx 4.5 |  |
| 120 | `changes/4.4` | 542-542 | 122 Sphinx 4.4 |  |
| 121 | `changes/4.3` | 543-545 | 123 Sphinx 4.3 |  |
| 122 | `changes/4.2` | 546-546 | 124 Sphinx 4.2 |  |
| 123 | `changes/4.1` | 547-548 | 125 Sphinx 4.1 |  |
| 124 | `changes/4.0` | 549-552 | 126 Sphinx 4.0 |  |
| 125 | `changes/3.5` | 553-556 | 127 Sphinx 3.5 |  |
| 126 | `changes/3.4` | 557-559 | 128 Sphinx 3.4 |  |
| 127 | `changes/3.3` | 560-561 | 129 Sphinx 3.3 |  |
| 128 | `changes/3.2` | 562-563 | 130 Sphinx 3.2 |  |
| 129 | `changes/3.1` | 564-567 | 131 Sphinx 3.1 |  |
| 130 | `changes/3.0` | 568-572 | 132 Sphinx 3.0 |  |
| 131 | `changes/2.4` | 573-574 | 133 Sphinx 2.4 |  |
| 132 | `changes/2.3` | 575-576 | 134 Sphinx 2.3 |  |
| 133 | `changes/2.2` | 577-578 | 135 Sphinx 2.2 |  |
| 134 | `changes/2.1` | 579-581 | 136 Sphinx 2.1 |  |
| 135 | `changes/2.0` | 582-587 | 137 Sphinx 2.0 |  |
| 136 | `changes/1.8` | 588-595 | 138 Sphinx 1.8 |  |
| 137 | `changes/1.7` | 596-602 | 139 Sphinx 1.7 |  |
| 138 | `changes/1.6` | 603-611 | 140 Sphinx 1.6 |  |
| 139 | `changes/1.5` | 612-619 | 141 Sphinx 1.5 |  |
| 140 | `changes/1.4` | 620-628 | 142 Sphinx 1.4 |  |
| 141 | `changes/1.3` | 629-639 | 143 Sphinx 1.3 |  |
| 142 | `changes/1.2` | 640-648 | 144 Sphinx 1.2 |  |
| 143 | `changes/1.1` | 649-651 | 145 Sphinx 1.1 |  |
| 144 | `changes/1.0` | 652-657 | 146 Sphinx 1.0 |  |
| 145 | `changes/0.6` | 658-663 | 147 Sphinx 0.6 |  |
| 146 | `changes/0.5` | 664-667 | 148 Sphinx 0.5 |  |
| 147 | `changes/0.4` | 668-670 | 149 Sphinx 0.4 |  |
| 148 | `changes/0.3` | 671-671 | 150 Sphinx 0.3 |  |
| 149 | `changes/0.2` | 672-673 | 151 Sphinx 0.2 |  |
| 150 | `changes/0.1` | 674-674 | 152 Sphinx 0.1 |  |
| 151 | `examples` | 675-684 | 153 Projects using Sphinx |  |


## Per-Docname Progress Tracker (D-02)

Tracks audit progress per docname (.rst source file), giving clean session-resume boundaries
across the multi-session visual pass (D-02). Every docname below is initialized to
**"🔲 NOT YET AUDITED"** — textually distinct from the two tokens the visual pass (Plan 17-02+)
will use on completion:

- `✅ AUDITED — no issues` (docname reviewed, no divergence found)
- `⚠️ AUDITED — N issue(s)` (docname reviewed, N candidate issues added to the Issue Table above)

This distinction is deliberate (empty-input edge, D-02): a docname that has genuinely been
reviewed and found clean must NEVER be confusable with a docname that has not been looked at
yet. `usage/extensions/graphviz` and `usage/extensions/inheritance` are still tracked here (they
still need a pass to confirm ONLY the known out-of-scope degradation is present, per SC#3) —
they are not exempted from progress tracking, only from becoming issue-table candidates.

**Spot-check log (D-01a "clean set" miss-rate estimate):** not yet populated — this is completed
by the human confirmer once the visual pass (Plan 17-02+) has produced a meaningful "clean" set
to sample from. Recorded here as a placeholder so the schema is visible before that pass starts:

| Sample size | Misses found | Miss rate | Confirmed by | Date |
|-------------|---------------|-----------|----------------|------|
| _(not yet run)_ | | | | |


| Docname | Status |
|---------|--------|
| `index` | 🔲 NOT YET AUDITED |
| `usage/installation` | 🔲 NOT YET AUDITED |
| `usage/quickstart` | 🔲 NOT YET AUDITED |
| `tutorial/index` | 🔲 NOT YET AUDITED |
| `tutorial/getting-started` | 🔲 NOT YET AUDITED |
| `tutorial/first-steps` | 🔲 NOT YET AUDITED |
| `tutorial/more-sphinx-customization` | 🔲 NOT YET AUDITED |
| `tutorial/narrative-documentation` | 🔲 NOT YET AUDITED |
| `tutorial/describing-code` | 🔲 NOT YET AUDITED |
| `tutorial/automatic-doc-generation` | 🔲 NOT YET AUDITED |
| `tutorial/deploying` | 🔲 NOT YET AUDITED |
| `tutorial/end` | 🔲 NOT YET AUDITED |
| `usage/index` | 🔲 NOT YET AUDITED |
| `usage/markdown` | 🔲 NOT YET AUDITED |
| `usage/referencing` | 🔲 NOT YET AUDITED |
| `usage/builders/index` | 🔲 NOT YET AUDITED |
| `usage/domains/index` | 🔲 NOT YET AUDITED |
| `usage/domains/standard` | 🔲 NOT YET AUDITED |
| `usage/domains/c` | 🔲 NOT YET AUDITED |
| `usage/domains/cpp` | 🔲 NOT YET AUDITED |
| `usage/domains/javascript` | 🔲 NOT YET AUDITED |
| `usage/domains/mathematics` | 🔲 NOT YET AUDITED |
| `usage/domains/python` | 🔲 NOT YET AUDITED |
| `usage/domains/restructuredtext` | 🔲 NOT YET AUDITED |
| `usage/theming` | 🔲 NOT YET AUDITED |
| `usage/advanced/intl` | 🔲 NOT YET AUDITED |
| `usage/advanced/websupport/index` | 🔲 NOT YET AUDITED |
| `usage/advanced/websupport/quickstart` | 🔲 NOT YET AUDITED |
| `usage/advanced/websupport/api` | 🔲 NOT YET AUDITED |
| `usage/advanced/websupport/searchadapters` | 🔲 NOT YET AUDITED |
| `usage/advanced/websupport/storagebackends` | 🔲 NOT YET AUDITED |
| `development/index` | 🔲 NOT YET AUDITED |
| `development/tutorials/index` | 🔲 NOT YET AUDITED |
| `development/tutorials/extending_syntax` | 🔲 NOT YET AUDITED |
| `development/tutorials/extending_build` | 🔲 NOT YET AUDITED |
| `development/tutorials/adding_domain` | 🔲 NOT YET AUDITED |
| `development/tutorials/autodoc_ext` | 🔲 NOT YET AUDITED |
| `development/howtos/index` | 🔲 NOT YET AUDITED |
| `development/howtos/setup_extension` | 🔲 NOT YET AUDITED |
| `development/howtos/builders` | 🔲 NOT YET AUDITED |
| `development/html_themes/index` | 🔲 NOT YET AUDITED |
| `development/html_themes/templating` | 🔲 NOT YET AUDITED |
| `extdev/index` | 🔲 NOT YET AUDITED |
| `extdev/appapi` | 🔲 NOT YET AUDITED |
| `extdev/event_callbacks` | 🔲 NOT YET AUDITED |
| `extdev/projectapi` | 🔲 NOT YET AUDITED |
| `extdev/envapi` | 🔲 NOT YET AUDITED |
| `extdev/builderapi` | 🔲 NOT YET AUDITED |
| `extdev/eventapi` | 🔲 NOT YET AUDITED |
| `extdev/collectorapi` | 🔲 NOT YET AUDITED |
| `extdev/markupapi` | 🔲 NOT YET AUDITED |
| `extdev/domainapi` | 🔲 NOT YET AUDITED |
| `extdev/parserapi` | 🔲 NOT YET AUDITED |
| `extdev/nodes` | 🔲 NOT YET AUDITED |
| `extdev/logging` | 🔲 NOT YET AUDITED |
| `extdev/i18n` | 🔲 NOT YET AUDITED |
| `extdev/utils` | 🔲 NOT YET AUDITED |
| `extdev/testing` | 🔲 NOT YET AUDITED |
| `extdev/deprecated` | 🔲 NOT YET AUDITED |
| `latex` | 🔲 NOT YET AUDITED |
| `support` | 🔲 NOT YET AUDITED |
| `internals/index` | 🔲 NOT YET AUDITED |
| `internals/contributing` | 🔲 NOT YET AUDITED |
| `internals/release-process` | 🔲 NOT YET AUDITED |
| `internals/organization` | 🔲 NOT YET AUDITED |
| `internals/code-of-conduct` | 🔲 NOT YET AUDITED |
| `faq` | 🔲 NOT YET AUDITED |
| `authors` | 🔲 NOT YET AUDITED |
| `man/index` | 🔲 NOT YET AUDITED |
| `man/sphinx-quickstart` | 🔲 NOT YET AUDITED |
| `man/sphinx-build` | 🔲 NOT YET AUDITED |
| `man/sphinx-apidoc` | 🔲 NOT YET AUDITED |
| `man/sphinx-autogen` | 🔲 NOT YET AUDITED |
| `usage/configuration` | 🔲 NOT YET AUDITED |
| `usage/extensions/index` | 🔲 NOT YET AUDITED |
| `usage/extensions/apidoc` | 🔲 NOT YET AUDITED |
| `usage/extensions/autodoc` | 🔲 NOT YET AUDITED |
| `usage/extensions/autosectionlabel` | 🔲 NOT YET AUDITED |
| `usage/extensions/autosummary` | 🔲 NOT YET AUDITED |
| `usage/extensions/coverage` | 🔲 NOT YET AUDITED |
| `usage/extensions/doctest` | 🔲 NOT YET AUDITED |
| `usage/extensions/duration` | 🔲 NOT YET AUDITED |
| `usage/extensions/extlinks` | 🔲 NOT YET AUDITED |
| `usage/extensions/githubpages` | 🔲 NOT YET AUDITED |
| `usage/extensions/graphviz` | 🔲 NOT YET AUDITED |
| `usage/extensions/ifconfig` | 🔲 NOT YET AUDITED |
| `usage/extensions/imgconverter` | 🔲 NOT YET AUDITED |
| `usage/extensions/inheritance` | 🔲 NOT YET AUDITED |
| `usage/extensions/intersphinx` | 🔲 NOT YET AUDITED |
| `usage/extensions/linkcode` | 🔲 NOT YET AUDITED |
| `usage/extensions/math` | 🔲 NOT YET AUDITED |
| `usage/extensions/napoleon` | 🔲 NOT YET AUDITED |
| `usage/extensions/todo` | 🔲 NOT YET AUDITED |
| `usage/extensions/viewcode` | 🔲 NOT YET AUDITED |
| `usage/restructuredtext/index` | 🔲 NOT YET AUDITED |
| `usage/restructuredtext/basics` | 🔲 NOT YET AUDITED |
| `usage/restructuredtext/roles` | 🔲 NOT YET AUDITED |
| `usage/restructuredtext/directives` | 🔲 NOT YET AUDITED |
| `usage/restructuredtext/field-lists` | 🔲 NOT YET AUDITED |
| `usage/restructuredtext/domains` | 🔲 NOT YET AUDITED |
| `glossary` | 🔲 NOT YET AUDITED |
| `changes/index` | 🔲 NOT YET AUDITED |
| `changes/9.0` | 🔲 NOT YET AUDITED |
| `changes/8.2` | 🔲 NOT YET AUDITED |
| `changes/8.1` | 🔲 NOT YET AUDITED |
| `changes/8.0` | 🔲 NOT YET AUDITED |
| `changes/7.4` | 🔲 NOT YET AUDITED |
| `changes/7.3` | 🔲 NOT YET AUDITED |
| `changes/7.2` | 🔲 NOT YET AUDITED |
| `changes/7.1` | 🔲 NOT YET AUDITED |
| `changes/7.0` | 🔲 NOT YET AUDITED |
| `changes/6.2` | 🔲 NOT YET AUDITED |
| `changes/6.1` | 🔲 NOT YET AUDITED |
| `changes/6.0` | 🔲 NOT YET AUDITED |
| `changes/5.3` | 🔲 NOT YET AUDITED |
| `changes/5.2` | 🔲 NOT YET AUDITED |
| `changes/5.1` | 🔲 NOT YET AUDITED |
| `changes/5.0` | 🔲 NOT YET AUDITED |
| `changes/4.5` | 🔲 NOT YET AUDITED |
| `changes/4.4` | 🔲 NOT YET AUDITED |
| `changes/4.3` | 🔲 NOT YET AUDITED |
| `changes/4.2` | 🔲 NOT YET AUDITED |
| `changes/4.1` | 🔲 NOT YET AUDITED |
| `changes/4.0` | 🔲 NOT YET AUDITED |
| `changes/3.5` | 🔲 NOT YET AUDITED |
| `changes/3.4` | 🔲 NOT YET AUDITED |
| `changes/3.3` | 🔲 NOT YET AUDITED |
| `changes/3.2` | 🔲 NOT YET AUDITED |
| `changes/3.1` | 🔲 NOT YET AUDITED |
| `changes/3.0` | 🔲 NOT YET AUDITED |
| `changes/2.4` | 🔲 NOT YET AUDITED |
| `changes/2.3` | 🔲 NOT YET AUDITED |
| `changes/2.2` | 🔲 NOT YET AUDITED |
| `changes/2.1` | 🔲 NOT YET AUDITED |
| `changes/2.0` | 🔲 NOT YET AUDITED |
| `changes/1.8` | 🔲 NOT YET AUDITED |
| `changes/1.7` | 🔲 NOT YET AUDITED |
| `changes/1.6` | 🔲 NOT YET AUDITED |
| `changes/1.5` | 🔲 NOT YET AUDITED |
| `changes/1.4` | 🔲 NOT YET AUDITED |
| `changes/1.3` | 🔲 NOT YET AUDITED |
| `changes/1.2` | 🔲 NOT YET AUDITED |
| `changes/1.1` | 🔲 NOT YET AUDITED |
| `changes/1.0` | 🔲 NOT YET AUDITED |
| `changes/0.6` | 🔲 NOT YET AUDITED |
| `changes/0.5` | 🔲 NOT YET AUDITED |
| `changes/0.4` | 🔲 NOT YET AUDITED |
| `changes/0.3` | 🔲 NOT YET AUDITED |
| `changes/0.2` | 🔲 NOT YET AUDITED |
| `changes/0.1` | 🔲 NOT YET AUDITED |
| `examples` | 🔲 NOT YET AUDITED |



## Next Steps (for Plan 17-02+)

1. Rasterize each docname's page range (`pdftoppm -png -r 150`, batched per docname per RESEARCH
   Pitfall 1 — never the whole 684-page PDF in one batch) into a session-scratch directory.
2. Optionally use the `-b text` baseline or `pypdf.extract_text()` per page range as a
   zero-new-tooling mechanical pre-filter to prioritize review order (never a substitute for the
   mandatory page-by-page visual look, RESEARCH Pitfall 3).
3. For each docname: open its rasterized pages, cross-check against its `-b html` baseline
   (D-04 authority), flag any in-scope divergence (D-06) as a candidate row in the Issue Table
   above (bias toward false positives — flag "uncertain" per D-03 rather than silently passing),
   classify against the Out-of-Scope table before adding, then flip its progress-tracker row to
   `✅ AUDITED — no issues` or `⚠️ AUDITED — N issue(s)`.
4. Once every docname is audited, group "high"-severity rows by root cause (D-10) and append
   `FID-01a`, `FID-01b`, … to `.planning/REQUIREMENTS.md` (Plan 17-04); add a single
   medium/low pointer under Future Requirements (D-11).
