# Phase 17 Audit Catalogue: Rendering-Fidelity Issues

**Requirement:** AUD-01 (17-CONTEXT.md D-01..D-11, 17-RESEARCH.md)
**Status:** Plan 17-04 COMPLETE — phase 17 (AUD-01) DONE. `FID-01a` (F12, the sole high-severity
root cause) appended to `.planning/REQUIREMENTS.md` §"Rendering Fidelity Audit"; the medium/low
pointer added under §"Future Requirements"; all five mechanical checks PASS (see "Validation
(Plan 17-04 mechanical checks)" below). Plan 17-03 COMPLETE — human confirmation gate PASSED
(D-01a). Plan 17-02 delivered all 151 of 151 docnames visually audited (Task 1) and the candidate
list classified, severity-finalized, and deterministically re-sorted (Task 2).
Findings F1–F15 recorded below (no new finding KINDS surfaced in this session's
changelog/examples pass; F8's occurrence list extended to `examples` pp.675,678). 15 candidate
rows were recorded. **Plan 17-03 human confirmation gate PASSED (2026-07-19, D-01a):** 14 rows
human-ACCEPTED (1 high [F12], 11 medium, 2 low [F8, F10]); 1 candidate REJECTED (F4 — see
"Rejected candidates" below); 0 excluded rows needed (out-of-scope sightings recorded inline
on tracker rows during Task 1). Clean-set spot-check: 6 pages / 4 clean docnames, 0 misses
(miss-rate 0%). Severities final; Phase 18 (FID-01) fixes the high-severity accepted rows (F12)
via `FID-01a`.

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

Populated as the multi-session visual pass proceeds (Plan 17-02, IN PROGRESS). Rows below use
the D-09 schema. Systemic (translator-level) findings are recorded once with a representative
docname/page set and an "Occurrence Count" noting the corpus-wide scope; Task 2 (out-of-scope
classification + severity finalization + deterministic re-sort) runs after every docname is
audited. Columns are the exact
D-09 required fields; every future row must have all 8 populated (SC#2 schema/completeness
check).

| # | Docname | Node Kind | Source-vs-Output Description | Severity | PDF Page | Occurrence Count | Minimal Repro (snippet or source-line pointer) | Disposition (D-01a) |
|---|---------|-----------|-------------------------------|----------|----------|-------------------|--------------------------------------------------|------------|
| 1 | `usage/referencing`, `usage/builders/index` (systemic — translator-level, corpus-wide) | `paragraph` (consecutive paragraphs inside a `list_item`) | Two or more blank-line-separated paragraphs within a single bullet/list item are concatenated with **no separator and no space**; HTML (D-04) renders each as its own `<p>` (vertical separation). The last word of paragraph 1 collides with the first word of paragraph 2, e.g. "…the role." + "For example…" → "role.**F**or example"; also "generated.This", "option.Custom", "files.Automatic". Paragraph structure inside the item is lost. Root cause confirmed in `typsphinx/translator.py`: `visit_paragraph`/`depart_paragraph` early-return when `self.in_list_item` is `True`, emitting neither a `par()` wrap nor any inter-paragraph separator (lines ~678–704). | medium | 50, 51, 54, 534 (first observed; systemic) | systemic — ≥5 observed pp.50–54; recurs at every multi-paragraph list item corpus-wide (also confirmed `changes/6.0` p.534, jQuery-removal changelog entry) | Bullet item with two paragraphs: `- keeps the visual output of the role.`⏎⏎`  For example, writing …` → renders "role.For example" | accepted |
| 2 | `usage/builders/index` (systemic — every Python-domain class/exception signature corpus-wide) | `desc_annotation` (Python-domain `class `/`exception ` keyword prefix) | The leading keyword annotation "class " / "exception " on a `py:class`/`py:exception`/`autoclass` signature loses its **trailing space**, merging with the qualified name: PDF shows "classsphinx.builders.html.StandaloneHTMLBuilder" vs. the authoritative "class sphinx.builders.html.StandaloneHTMLBuilder" (`-b text` baseline line 64). The "class"/"exception" keyword annotation is no longer a distinct token. | medium | 55–67 (first observed; systemic) | systemic — ~20 observed pp.55–67; recurs at every `py:class`/`py:exception`/`autoclass` signature corpus-wide | `.. py:class:: sphinx.builders.html.StandaloneHTMLBuilder` → renders "classsphinx.builders.html.StandaloneHTMLBuilder" | accepted |
| 5 | `usage/domains/standard` (systemic — object-description field lists) | `field_list` / `field` inside `desc_content` (confval `:type:`/`:default:`) | A confval's `:type:`/`:default:` fields render (text baseline) as a definition list ("Type:" then value indented; "Default:" then value). PDF renders them inline with no separation and no space after the colon: "the_answer Type:int (a number)Default:42" ("Type:int" no space; "number)Default:42" fields merged). Field-list structure lost + boundary merge. (Same class also seen in the `c:alias` `:options:` field "Options:maxdepth: int".) | medium | 70, 74 | systemic to object-description field lists | `.. confval:: the_answer`⏎`   :type: ``int`` (a *number*)`⏎`   :default: **42**` → "the_answer Type:int (a number)Default:42" | accepted |
| 3 | `usage/domains/c`, `usage/domains/cpp` (systemic — C and C++ domains) | `desc_signature` / inline `c:expr`/`cpp:expr` (C/C++ signatures & expressions) | Rendered C/C++ signatures and inline expressions lose **all inter-token spaces**: around the pointer `*`/`&`, between a type and its identifier, and after the keyword-annotation prefix. text baseline (authoritative): "PyObject *PyType_GenericAlloc(PyTypeObject *type, Py_ssize_t nitems)"; PDF: "PyObject*PyType_GenericAlloc(PyTypeObject*type, Py_ssize_tnitems)" — "Py_ssize_tnitems" merges type and parameter name. Also "structData", "inta", "doubleb", "intf(doublek)", "a*f(a)" (should be "a * f(a)"), "constData*", "classWrapper template<typenameTOuter>". | medium | 71–86 (first observed; systemic) | systemic — dozens across C/C++ domain signatures & inline expressions | `.. c:function:: PyObject *PyType_GenericAlloc(PyTypeObject *type, Py_ssize_t nitems)` → "PyObject*PyType_GenericAlloc(PyTypeObject*type, Py_ssize_tnitems)" | accepted |
| 7 | `usage/domains/python`, `usage/domains/cpp`, `usage/domains/c`, `usage/domains/restructuredtext`, `usage/restructuredtext/directives` (systemic) | `desc_signature` (multiple sibling signatures / overloads / options in one directive) | When one object directive declares multiple signatures (overloads, `c/cpp:alias` with several entries, `py:function` with several forms, or `rst:directive` with option children), HTML stacks them on separate lines. PDF concatenates them on one line with no break: "compile(source)compile(source, filename)compile(source, filename, symbol)"; "intavoidf(doubled)constvoidf(doubled)voidf(inti)voidf()"; "toctree:::caption: caption of ToC:glob:options:type: …". Signatures/options run together. Also confirmed for directive-alias groups (`.. version-added:: … .. versionadded:: …`, `.. code-block:: [language] .. sourcecode:: [language] .. code:: [language]`) and multi-field option lists (`:start-at: … :start-after: … :end-before: … :end-at: …`), `usage/restructuredtext/directives` pp.476,477,480,484. | medium | 74, 81, 86, 97, 102, 476, 477, 480, 484 | systemic — wherever a directive has multiple signature/option lines | `.. py:function:: compile(source)`⏎`                 compile(source, filename)` → "compile(source)compile(source, filename)" | accepted |
| 6 | `usage/domains/cpp` (watch other long inline-literal runs) | `literal` (long run of inline `:role:` literals on one line) | The C++ cross-reference role list ":cpp:any: :cpp:class: … :cpp:enum: :cpp:enumerator: …" is a long line of inline literals. HTML wraps it; PDF overflows the right text margin and is clipped mid-token ("…:cpp:enum: :cpp:er" then cut off), so trailing roles are not visible = content loss. | medium | 85 | ≥1; likely wherever long inline-literal runs occur | a paragraph of many space-separated inline literals longer than one line, e.g. `` :cpp:any: `` `` :cpp:class: `` … | accepted |
| 8 | `usage/theming`, `changes/1.6`, `examples` (systemic — corpus-wide) | `reference` (external / named hyperlink) | External named-reference hyperlinks ("Python 2 documentation", "Jinja documentation", "Haiku OS user guide", "sphinxdoc theme", "RTD", "create an issue or pull request on GitHub", "Read the Docs Sphinx Theme documentation") render as plain, visually-undistinguished text, sometimes leaving a stray space adjacent to the flattened link text: before the following period ("based on the Jinja documentation ." / "looks like the Python 2 documentation ." / "create an issue or pull request on GitHub ." `examples` p.675) OR before the following word ("RTD  PDF builds of Sphinx own docs are…", `changes/1.6` p.606, confirming the artifact is a general link-boundary space, not period-specific). When the flattened link is followed only by a paragraph/block boundary (no adjacent inline text), no stray-space artifact is visible — only the loss of link styling itself (`examples` p.678 "Read the Docs Sphinx Theme documentation", link immediately followed by a bullet list). HTML renders styled links with no stray space and clickable link styling throughout. (D-06: link flattened to plain text is meaning-bearing; the stray space is the concrete symptom where adjacent inline text exists.) | low | 109, 110, 606, 675, 678 | several pp.109-111; also confirmed `changes/1.6` p.606 and `examples` pp.675,678 (systemic — corpus-wide for external links) | a paragraph with an external named hyperlink immediately followed by a period, e.g. ``the `Jinja documentation <https://…>`_ .``; or followed by a word, e.g. ``` `RTD <https://readthedocs.org/>`_ PDF builds… ```; or as a standalone flattened link with no visible artifact, e.g. ``` `Read the Docs Sphinx Theme documentation <https://…>`_ ``` followed by a list | accepted |
| 9 | systemic — corpus-wide; first seen `development/tutorials/adding_domain` + `development/tutorials/autodoc_ext` | `Text` / `paragraph` (intra-paragraph soft/"semantic" line breaks) | A paragraph written with reStructuredText **semantic line breaks** (one clause per source line) renders with a HARD line break at *every* source-line boundary — ragged short lines with large right-margin gaps — instead of the reflowed, wrapped paragraph the HTML/text authority (D-04) produces. **Independent of content**: reproduced in plain-text, inline-literal-only, AND cross-reference paragraphs alike (initial custom-text-`:ref:` correlation was a red herring — the trigger is the soft newline itself). The artifact is only *visible* where source clauses are short; where the author's source lines run near the fill width the hard breaks coincide with natural wrap points and look normal (e.g. adding_domain "Moving on…", source lines 66–80 chars, renders flowing). Root cause (provisional): the translator preserves intra-paragraph source newlines as hard line breaks rather than collapsing them to a space (docutils/HTML/Typst-markup all collapse them). Text content + order preserved; paragraph reflow/justification lost. | medium | 142, 147, 151, 153, 154, 563 | systemic — corpus-wide; latent in every soft-wrapped paragraph; ≥8 visibly-broken paragraphs across the 2 tutorial docnames seen so far; also confirmed inside a changelog bullet list-item body (`changes/3.2` p.563), so not limited to top-level prose paragraphs | `There are several different documenter classes such as ``MethodDocumenter```⏎`or ``AttributeDocumenter`` available in the autodoc extension but`⏎… (autodoc_ext.rst L72-75, NO refs) → 4 forced short lines; contrast adding_domain.rst L158-161 (long source lines) renders flowing | accepted |
| 10 | `extdev/envapi`, `extdev/builderapi`, `extdev/domainapi` (systemic — every Python signature with a `*` keyword-only (PEP 3102) or `/` positional-only (PEP 570) separator; likely all `abbreviation`/`:abbr:` nodes) | `abbreviation` / `desc_sig_operator` (the `*` / `/` separator's `<abbr>` title) | A Python-domain signature's bare `*` (keyword-only) or `/` (positional-only) separator carries an `<abbr title="…parameters separator (PEP 3102/570)">` in HTML — the visible text is only `*` / `/`, the explanation is a hover tooltip; the `-b text` authority likewise shows only `*,` / `/,`. The PDF renders the abbr title INLINE — `* (Keyword-only parameters separator (PEP 3102))` and `/ (Positional-only parameter separator (PEP 570))` — injecting verbose internal API-doc metadata into the visible signature. More generally, `abbreviation`-node hover-title text is emitted as visible inline text. (For a genuine `:abbr:` role this inline expansion may be acceptable print behaviour since print has no hover; for the auto-generated `*`/`/` separators it clutters signatures — human-ACCEPTED at the 17-03 gate (low) as a real divergence: spurious internal metadata injected into every keyword-only/positional-only signature.) | low | 204, 206, 218 | systemic — every signature with a `*` (PEP 3102) or `/` (PEP 570) separator; recurs corpus-wide in API docs (esp. extdev/*) | authority `note_dependency(filename: str \| PathLike[str], *, docname: …)` → PDF `… * (Keyword-only parameters separator (PEP 3102)), …`; `ObjType(lname: str, /, *roles, **attrs)` → `… / (Positional-only parameter separator (PEP 570)), …` | accepted |
| 11 | `extdev/i18n` (systemic — every captioned code-block nested inside a list item / other markup context) | `literal_block` with `:caption:` (codly per-block config wrapper) | A code block that has BOTH a `:caption:` (→ Typst `figure(caption: […])[…]`) AND sits inside a list item (→ the translator's `{ … }` list-item wrapper, translator.py ~1495) leaks its codly config wrapper as **literal visible text**: `{ codly(number-format: none)` renders above the block and `}` below it (seen bracketing Listings 38/39/40). The translator explicitly knows this hazard (translator.py 1504-1520: "a bare `codly(...)` is typeset as LITERAL PROSE — leaking the config text"; the `codly_prefix = "#"` fix) but it fails for the combined list-item + caption case. HTML/text authority show only the captioned code, never the wrapper. Code content is preserved but spurious raw-markup garbage surrounds every such listing (and the codly config likely does not take effect). | medium | 232 | systemic — every captioned code-block inside a list item; recurs wherever numbered/bulleted steps embed captioned code (how-to/tutorial/config docs) | `.. code-block:: python`⏎`   :caption: src/init.py` inside a numbered-list step → renders `{ codly(number-format: none)` + code + `}` + "Listing N: src/init.py" | accepted |
| 12 | `extdev/deprecated` (systemic — any table too wide for the text block) | `table` / `tgroup` (multi-column table with long cell content) | A wide multi-column table whose cells hold long content overflows catastrophically: (a) long Target-column text spills past its column and **COLLIDES** with the Deprecated/Removed columns, interleaving glyphs into unreadable runs (`sphinx.environment.BuildEnvironment`**`anpp`**, `CheckExternalLinksBuilder.anchors 8.0 5.0 N/A`**`rs_ignore`**), and (b) the rightmost Alternatives column **overflows the right PAGE margin and is clipped** (`…format_exception_cut_f` cut off). The HTML authority (D-04) lays the table out with fitting/wrapping columns and loses nothing. Large portions of the table are rendered unreadable. Contrast: small narrow tables (transform-priority tables, appapi pp.186-188) render correctly — the failure is triggered by long cell content / total table width exceeding the text block. Related to F6 (right-margin clip) but table-specific and adds inter-column collision. | high | 239, 240, 241 | systemic — every table too wide for the text block (long dotted paths / many columns); recurs corpus-wide (e.g. `usage/configuration` tables) | the multi-page "deprecated APIs" grid table (`extdev/deprecated`, pp.239-249) → columns collide + right-edge clip; contrast the narrow appapi transform-priority tables which render fine | accepted |
| 13 | `man/sphinx-quickstart`, `usage/restructuredtext/directives` (systemic — any `.. rubric::`-style "Options" heading immediately followed by an option/field entry; man-page option groups AND directive-option field lists) | `rubric` + `desc`/`option` (option-group heading + following option) | A `.. rubric::` used as an option-group heading, immediately followed by an `.. option::` directive, renders with the rubric text CONCATENATED onto the first option with no separation: "Structure Options**--sep**", "Project Basic Options**-p PROJECT, --project=PROJECT**", "Extension Options**--ext-autodoc**", "Makefile and Batchfile Creation Options**--use-make-mode (-m)…**". The `-b text` authority renders the rubric on its own line (`-[ Structure Options ]-`) then the option separately; HTML likewise separates them. The option-group heading is no longer distinct from the option. Likely shares the F1 / block-separation root cause (consecutive block elements emitted with no inter-block break) but in a distinct node context (rubric→option). Also confirmed for Sphinx directive option-field lists: the "Options" sub-heading merges onto the first `:optionname:` field, e.g. "Options:class: class names (a list of class names…)", "Options:linenos: (no value)", "General options:class: …", "Options for formatting:dedent: …" — recurs pervasively (~10 occurrences) throughout `usage/restructuredtext/directives` pp.469,478,480,482,483,484,487,489,494. | medium | 300, 301, 469, 478, 480, 482, 483, 484, 487, 489, 494 | systemic — every rubric-headed option group AND every directive-option field-list heading; recurs across all man/* pages and any directive-reference docname | `.. rubric:: Structure Options`⏎`.. option:: --sep` → renders "Structure Options--sep" (authority: `-[ Structure Options ]-` then `--sep`) | accepted |
| 14 | `usage/configuration` (systemic — two related sub-patterns, both `definition_list` `term`+`definition`) | `definition_list` (`term` immediately followed by `definition`, or by a nested list's first `term`) | Two related divergences, both losing the line break between a bold definition-list **term** and whatever follows it, unlike the HTML/text authority which always places the term on its own line: **(a)** when an entire `definition_list` is nested inside a bullet `list_item`, EVERY term in that list merges onto the same line as the first line of its own definition — e.g. `'paragraphindent'` **Number of spaces to indent the first line of each paragraph,** (authority: term alone on one line, definition indented below); same for `'exampleindent'`, `'preamble'`, `'copying'` in the same nested list (texinfo_elements confval, "Keys that you may want to override include:" bullet). **(b)** when a `definition_list` term's own definition body begins with a NESTED list (another `definition_list` or a `field_list`), the OUTER term merges onto the same line as the nested list's FIRST term only (its own subsequent siblings separate correctly) — e.g. `Options for 'mecab':`**dic_enc:** (authority: `Options for 'mecab':` on its own line, then the nested field list's `dic_enc:` on the next). Contrast: definition lists NOT nested inside a bullet list_item, whose definition body is a plain paragraph (e.g. `'sphinx.search.ja.DefaultSplitter'`), render correctly with the term on its own line. Text content is preserved but the term/definition (and term/nested-term) boundary is visually lost. | medium | 343, 364, 365 | ≥2 confvals on this docname (`html_search_options`, `texinfo_elements`); likely recurs wherever a definition list is nested inside a bullet list_item, or a term's definition opens with a nested list, corpus-wide | `- Keys...:`⏎⏎ &nbsp;&nbsp;``'paragraphindent'``⏎&nbsp;&nbsp;&nbsp;&nbsp;Number of spaces to indent the first line... → renders "'paragraphindent'  Number of spaces to indent the first line..." on one line | accepted |
| 15 | `usage/extensions/coverage` (watch other confval-only pages) | `desc` (`confval` directive with NO body/description content) | When two or more `confval` directives with only `:type:`/`:default:` fields (no descriptive body paragraph) appear back-to-back, they concatenate into a single unbroken line with no visual separation at all between the confval names themselves: `coverage_c_path Type:Sequence[str]Default:()coverage_c_regexes Type:dict[str, str]Default:{}coverage_ignore_c_items Type:dict[str, Sequence[str]]Default:{}coverage_write_headline Type:bool Default:True` — four DISTINCT confvals merge into one blob. The HTML authority renders each as its own `<dl class="std confval">` block, visually separated even with an empty body. Related to F5 (Type/Default concat within one confval) and F7 (multi-name single confval) but distinct: here it's MULTIPLE SEPARATE desc/confval nodes with no body content losing their inter-block separation entirely. | medium | 408 | 1 confirmed occurrence (4 confvals merged); likely recurs wherever 2+ body-less confvals appear consecutively, corpus-wide | `.. confval:: coverage_c_path`⏎`   :type: ...`⏎`   :default: ...`⏎⏎`.. confval:: coverage_c_regexes`⏎... (coverage.rst L88-102, no body text on any of the 4) → all 4 headers run together on one line | accepted |

## Root-cause groups (D-10)

Plan 17-04 backlog-generation grouping, run against the human-confirmed, severity-final active
Issue Table above. Grouping key = (node kind, failure mode) — the same root cause recurring
across N docnames/occurrences is ONE group, never one group per occurrence (D-10; RESEARCH
Pitfall 6).

**High-severity groups (→ FID-01x, D-11):**

| Order | FID-01 ID | Finding | Root cause (node kind + failure mode) | Occurrences (docname, pp.) |
|---|---|---|---|---|
| 1 | FID-01a | F12 | `table`/`tgroup` — wide multi-column table whose cell content collides between columns AND whose rightmost column clips off the right page margin, when the table's total width exceeds the text block | `extdev/deprecated` pp.239,240,241 (systemic — recurs for any table too wide for the text block, corpus-wide) |

Severity tally confirmed from the active table above: **1 high (F12)**, 2 low (F8, F10), 11
medium (F1, F2, F3, F5, F6, F7, F9, F11, F13, F14, F15) = 14 accepted rows. Exactly one
high-severity root-cause group exists, so exactly one `FID-01x` is assigned: `FID-01a`.
Deterministic order (ordering edge, so re-runs/appends reproduce the same lettering): catalogue's
active Issue Table row order (ascending row #, itself docname/toctree-then-PDF-page ascending per
Plan 17-02 Task 2's deterministic re-sort) — F12 is the sole high row, so `FID-01a` is the only ID
this pass assigns; a future audit pass adding a second high root cause would append `FID-01b` next
in that same row-order sequence, never renumbering `FID-01a`.

**Root-cause kinship note (Phase 18 awareness, non-binding):** F6 (medium — a long run of inline
`literal` roles overflows and clips at the right text margin, `usage/domains/cpp` p.85) is a
RELATED overflow family — both F12 and F6 are right-edge/margin-overflow symptoms — but F6 is a
DIFFERENT node kind (`literal` inline run vs. `table`/`tgroup`) and stays medium per the D-08
rubric (content is clipped/unreadable in both, but F6's blast radius is one inline run, not a
whole multi-column data table). F6 therefore does NOT enter FID-01a or any FID-01x; it remains
recorded only via the medium/low pointer below. Flagging the kinship here purely so Phase 18's
planner can consider whether a shared "avoid right-margin overflow" primitive serves both F12's
fix and a later F6 fix, without conflating them into one requirement.

**Medium/low severity (13 rows: F1, F2, F3, F5, F6, F7, F8, F9, F10, F11, F13, F14, F15):** stay
fully recorded in this catalogue only, referenced by the single Future Requirements pointer added
to `REQUIREMENTS.md` (D-11) — never enumerated as individual `FID-01x` requirements.

## Validation (Plan 17-04 mechanical checks)

All five mechanical checks from RESEARCH's Validation Architecture (Phase Requirements →
Validation Map) were run against a **fresh** rebuild in this session (2026-07-19), not against
stale artifacts. Fresh build reused `tests/test_corpus_gate.py`'s unmodified helpers
(`get_or_clone_corpus` + `wire_typsphinx_into_corpus_conf` + `_run_corpus_sphinx_build("typstpdf",
...)`), same cached corpus tree (tag `v9.1.0`, SHA `cc7c6f435ad37bb12264f8118c8461b230e6830c`) as
the Provenance header above.

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | **SC#1 coverage** — progress tracker's docname set == corpus toctree closure (fresh recursive `#include()`/`include()` walk of a freshly-rebuilt `index.typ`, 151 docnames found, zero duplicates) | **PASS** | Fresh-walk docname set and the Per-Docname Progress Tracker's docname set are set-equal (151 == 151; symmetric difference is empty). Zero rows anywhere in the tracker carry the `🔲 NOT YET AUDITED` marker (the sole remaining match for that literal string in the whole file is the legend text defining the marker, not a live row). |
| 2 | **SC#2 schema** — every active Issue Table row (14 rows, F1–F3,F5–F15 minus F4-rejected) has all 8 D-09 columns + the `#` column non-empty (9 columns total) | **PASS** | Parsed all 14 active rows by cell-splitting on ` \| `; every row has exactly 9 non-empty cells. Zero blank-column rows. |
| 3 | **SC#3 classification** — no ACTIVE issue row (scoped to the Issue Table only, excluding "Excluded (out-of-scope)" and "Rejected candidates" subsections, per the plan's stated false-positive avoidance) matches `graphviz`/`inheritance_diagram`/`py:meth` | **PASS** | `grep -iE "graphviz\|inheritance.diagram\|py:meth"` over the 14 active-row lines only: zero matches. (An unscoped grep over the whole file DOES match — inside the "Excluded (out-of-scope)" and "Out-of-Scope Classification" sections, which is expected and correct; those sections exist specifically to document exclusions, so an unscoped grep is the known false-positive this check must avoid, per the plan's explicit note.) |
| 4 | **SC#4 backlog** — distinct `FID-01[a-z]` requirement entries in REQUIREMENTS.md == distinct high-severity root-cause group count | **PASS (1 == 1)** | `grep -oE '^\s*- \[.\] \*\*FID-01[a-z]+\*\*' .planning/REQUIREMENTS.md` → exactly one match, `FID-01a`. Root-cause groups table above lists exactly 1 high-severity group (F12). (A broader, unscoped `FID-01[a-z]+` regex over the whole REQUIREMENTS.md also matches the pre-existing narrative mentions "`FID-01a`, `FID-01b`, …" inside FID-01's own description and the Coverage/Phase-mapping notes — those are template prose, not appended requirement entries, and are excluded by scoping the check to actual `- [ ] **FID-01<letter>**` checkbox lines.) |
| 5 | **D-07 freshness** — re-run `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow` and confirm the reported PDF size / empty `unknown_visit` catalogue still match this catalogue's provenance header | **PASS (genuine, not environmentally-limited this session)** | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` → `1 passed in 13.67s`. A separate, identically-wired fresh build (same helpers, same corpus tree) was also produced to get a persistent `index.pdf`/`index.typ` for check #1's walk: `index.pdf` size = **15,153,646 bytes** (byte-for-byte match to the Provenance header above), `unknown_visit` catalogue = `{}` (empty, matches header). No sandbox ELF-exec limitation was hit this session (contrast the plan's documented contingency for that failure mode) — real `typst.compile()` ran end-to-end. |
| 6 (bonus, plan Task 2 item 6) | No `.png`/`.pdf`/scratch build artifact staged for commit | **PASS** | `git status --porcelain` at Plan 17-04 finalization shows only `.planning/REQUIREMENTS.md` and this catalogue file modified (plus a pre-existing unrelated `.planning/config.json` change from before this plan started, left untouched per the executor's scope). No image/PDF paths appear. All fresh-build scratch (PDF, `.typ`, page images) lives outside the repo under the session scratchpad, never `git add`ed. |

## Rejected candidates (Plan 17-03 human confirmation, D-01a)

The operator ruled accept/reject + final severity on every candidate at the 17-03 gate. One
candidate was **rejected** and removed from the active Issue Table; it is preserved here with the
rejection reason for auditability (not deleted):

| # | Docname | Node Kind | Provisional | Rejection reason (operator, D-01a) |
|---|---------|-----------|-------------|-------------------------------------|
| 4 | `usage/domains/c` | `desc` / `desc_content` field labels (`No-contents-entry:`/`No-index-entry:`) | medium | **Not a typsphinx bug.** Verified at the gate: the `-b html` authority (D-04) AND the `-b text` baseline BOTH render the `No-contents-entry:` / `No-index-entry:` labels — the corpus deliberately authors `:no-contents-entry:`/`:no-index-entry:` on this `c:function` to demonstrate the options (`doc/usage/domains/c.rst` §57–62), so the labels are builder-independent Sphinx behaviour (SC#3-style out-of-scope). The only genuine typsphinx divergence on that line — the labels/fields concatenated with no separation — is already captured by **F5** (field-list inline concat) and **F1** (block separation); F4 adds no independent fix scope. Page image reviewed by the operator (PDF p.72). |

## Excluded (out-of-scope)

**Task 2 sweep result:** zero active-table rows (F1–F15 above) matched an out-of-scope
signature — none reference `graphviz`, `inheritance_diagram`, a non-included-document
cross-reference, or a `py:meth`/autodoc-import warning. This is because the visual pass
(Task 1) never promoted an out-of-scope observation into the Issue Table in the first
place; instead, each out-of-scope sighting was recorded directly as an inline annotation
on the affected docname's progress-tracker row (SC#3 discipline applied at observation
time, not deferred to a later filtering pass). For auditability (so the exclusion is
visible, not silent — REQUIREMENTS.md "Out of Scope" / SC#3), the confirmed sightings are
listed here:

| Docname | PDF Page | Signature | Exclusion Reason |
|---------|----------|-----------|-------------------|
| `usage/extensions/graphviz` | 419-421 | `graphviz` directive | Every `.. graphviz::`/`.. graph::`/`.. digraph::` example on this docname is rendered as **literal rst syntax** (the page sets `.. highlight:: rst`), so no real graphviz directive is ever compiled/invoked here — nothing to exclude in practice, but the docname is the corpus's designated graphviz-extension reference page and is pre-classified out-of-scope per REQUIREMENTS.md regardless. |
| `usage/extensions/inheritance` | 423-425 | `inheritance_diagram` directive | Confirmed: the SC#3 "[inheritance diagram diagram omitted]" graceful-degrade placeholder appears at every `.. inheritance-diagram::` invocation on this docname, identically to the `-b html` baseline (DEG-01/DEG-02 working as designed) — intentional degrade, not a rendering-fidelity divergence. |
| `extdev/index` | 174 | `graphviz` placeholder | Out-of-scope graphviz degrade placeholder observed inline while auditing this docname for F9 (see progress tracker); not promoted to the Issue Table. |
| `extdev/event_callbacks` | 196 | `graphviz` placeholder | Out-of-scope graphviz degrade placeholder observed inline while auditing this docname for F7/F9; not promoted to the Issue Table. |
| `extdev/builderapi` | 205 | `graphviz` placeholder | Out-of-scope graphviz degrade placeholder observed inline while auditing this docname for F2/F3/F9/F10; not promoted to the Issue Table. |

No `py:meth`/autodoc-import-warning divergence was ever visually distinguishable as a
rendering-fidelity candidate during the pass (these are Sphinx build-log warnings, not
visible PDF/HTML page content), so none is enumerated above — consistent with
REQUIREMENTS.md's note that this category is "not enumerable in advance."

**Self-verification (Task 2 acceptance criteria):** grep of the active Issue Table for
`inheritance.diagram|graphviz|py:meth` returns zero matches (see automated verify below) —
confirming no excluded signature leaked into the active rows.

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


### Mapping note (observed during Plan 17-02 visual pass — infra, not an AUD-01 finding)

- **`development/html_themes/index` ↔ `development/html_themes/templating` boundary:** The Full Table
  above splits these as html_themes/index = `156-160; 169-172` and templating = `161-168`. The visual
  pass found the real split differs: html_themes/index's own content ends at its `42.4 Templating`
  heading on **p.161**, and the included `templating` doc (chapter 43, `43 Templating` … `43.5.9 Inject
  JavaScript…`) actually runs **161-172** (not 161-168). Pages 169-172 are templating `43.5.x` content,
  NOT an html_themes/index second fragment. The *outer* span 156-172 is correct and BOTH docnames were
  fully visually audited (every page 156-172 was read); only the internal per-docname attribution in the
  mapping table is inaccurate. Flagged as a possible 17-01 mapping-table fix (D-07 infra) — this is not a
  typsphinx rendering divergence, so it is intentionally NOT added to the Issue Table.

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

**Spot-check log (D-01a "clean set" miss-rate estimate):** populated at the Plan 17-03 human
confirmation gate (2026-07-19). The operator re-rendered a sample of docnames the tracker marks
`✅ AUDITED — no issues` and confirmed no missed in-scope divergence — every finding visible on
the sampled pages belonged either to an adjacent non-clean docname (already flagged) or to the
already-accepted systemic F9 (soft-wrap), never a false "clean" call:

| Sample size | Misses found | Miss rate | Confirmed by | Date |
|-------------|---------------|-----------|----------------|------|
| 6 pages / 4 clean docnames (`usage/quickstart` pp.22,24; `tutorial/describing-code` pp.36,38; `usage/domains/mathematics` p.89; `man/index` p.300) | 0 | 0% (0/6) | operator (17-03 gate) | 2026-07-19 |


| Docname | Status |
|---------|--------|
| `index` | ✅ AUDITED — no issues |
| `usage/installation` | ✅ AUDITED — no issues |
| `usage/quickstart` | ✅ AUDITED — no issues |
| `tutorial/index` | ✅ AUDITED — no issues |
| `tutorial/getting-started` | ✅ AUDITED — no issues |
| `tutorial/first-steps` | ✅ AUDITED — no issues |
| `tutorial/more-sphinx-customization` | ✅ AUDITED — no issues |
| `tutorial/narrative-documentation` | ✅ AUDITED — no issues |
| `tutorial/describing-code` | ✅ AUDITED — no issues |
| `tutorial/automatic-doc-generation` | ✅ AUDITED — no issues |
| `tutorial/deploying` | ✅ AUDITED — no issues |
| `tutorial/end` | ✅ AUDITED — no issues |
| `usage/index` | ✅ AUDITED — no issues |
| `usage/markdown` | ✅ AUDITED — no issues |
| `usage/referencing` | ⚠️ AUDITED — 1 issue(s) (F1) |
| `usage/builders/index` | ⚠️ AUDITED — 2 issue(s) (F1, F2) |
| `usage/domains/index` | ✅ AUDITED — no issues |
| `usage/domains/standard` | ⚠️ AUDITED — 1 issue(s) (F5) |
| `usage/domains/c` | ⚠️ AUDITED — 2 issue(s) (F3, F4) |
| `usage/domains/cpp` | ⚠️ AUDITED — 2 issue(s) (F3, F6) |
| `usage/domains/javascript` | ⚠️ AUDITED — 2 issue(s) (F2, F3) |
| `usage/domains/mathematics` | ✅ AUDITED — no issues |
| `usage/domains/python` | ⚠️ AUDITED — 3 issue(s) (F2, F3, F7) |
| `usage/domains/restructuredtext` | ⚠️ AUDITED — 2 issue(s) (F5, F7) |
| `usage/theming` | ⚠️ AUDITED — 2 issue(s) (F1, F8) |
| `usage/advanced/intl` | ⚠️ AUDITED — 1 issue(s) (F1) |
| `usage/advanced/websupport/index` | ✅ AUDITED — no issues |
| `usage/advanced/websupport/quickstart` | ✅ AUDITED — no issues |
| `usage/advanced/websupport/api` | ⚠️ AUDITED — 1 issue(s) (F2) |
| `usage/advanced/websupport/searchadapters` | ⚠️ AUDITED — 1 issue(s) (F2) |
| `usage/advanced/websupport/storagebackends` | ⚠️ AUDITED — 1 issue(s) (F2) |
| `development/index` | ✅ AUDITED — no issues |
| `development/tutorials/index` | ✅ AUDITED — no issues |
| `development/tutorials/extending_syntax` | ⚠️ AUDITED — 1 issue(s) (F8) |
| `development/tutorials/extending_build` | ⚠️ AUDITED — 1 issue(s) (F1) |
| `development/tutorials/adding_domain` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `development/tutorials/autodoc_ext` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `development/howtos/index` | ✅ AUDITED — no issues |
| `development/howtos/setup_extension` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `development/howtos/builders` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `development/html_themes/index` | ⚠️ AUDITED — 2 issue(s) (F9, F1) |
| `development/html_themes/templating` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `extdev/index` | ⚠️ AUDITED — 1 issue(s) (F9) [+ out-of-scope graphviz placeholder p.174, SC#3] |
| `extdev/appapi` | ⚠️ AUDITED — 4 issue(s) (F2, F3, F7, F9) |
| `extdev/event_callbacks` | ⚠️ AUDITED — 2 issue(s) (F7, F9) [+ out-of-scope graphviz placeholder p.196, SC#3] |
| `extdev/projectapi` | ⚠️ AUDITED — 3 issue(s) (F2, F3, F9) |
| `extdev/envapi` | ⚠️ AUDITED — 4 issue(s) (F2, F3, F9, F10) |
| `extdev/builderapi` | ⚠️ AUDITED — 4 issue(s) (F2, F3, F9, F10) [+ out-of-scope graphviz placeholder p.205, SC#3] |
| `extdev/eventapi` | ⚠️ AUDITED — 4 issue(s) (F2, F3, F7, F9) |
| `extdev/collectorapi` | ⚠️ AUDITED — 3 issue(s) (F2, F3, F9) |
| `extdev/markupapi` | ⚠️ AUDITED — 3 issue(s) (F2, F7, F9) |
| `extdev/domainapi` | ⚠️ AUDITED — 5 issue(s) (F2, F3, F7, F9, F10) |
| `extdev/parserapi` | ⚠️ AUDITED — 3 issue(s) (F2, F3, F9) |
| `extdev/nodes` | ⚠️ AUDITED — 3 issue(s) (F2, F3, F9) |
| `extdev/logging` | ⚠️ AUDITED — 3 issue(s) (F2, F7, F9) |
| `extdev/i18n` | ⚠️ AUDITED — 3 issue(s) (F3, F9, F11) |
| `extdev/utils` | ⚠️ AUDITED — 4 issue(s) (F2, F3, F9, F10) |
| `extdev/testing` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `extdev/deprecated` | ⚠️ AUDITED — 1 issue(s) (F12) [big multi-page deprecated-APIs table; F2/F3 also present in cell text] |
| `latex` | ⚠️ AUDITED — 2 issue(s) (F1, F9) [F1 pervasive via stacked versionadded/versionchanged notes; all narrow tables render fine] |
| `support` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `internals/index` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `internals/contributing` | ⚠️ AUDITED — 2 issue(s) (F1, F9) |
| `internals/release-process` | ⚠️ AUDITED — 1 issue(s) (F9) [small Date/Python table renders fine] |
| `internals/organization` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `internals/code-of-conduct` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `faq` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `authors` | ⚠️ AUDITED — 1 issue(s) (F9) [long bullet lists; Unicode names render fine] |
| `man/index` | ✅ AUDITED — no issues |
| `man/sphinx-quickstart` | ⚠️ AUDITED — 2 issue(s) (F13, F9) |
| `man/sphinx-build` | ⚠️ AUDITED — 1 issue(s) (F9) [options not rubric-grouped → no F13] |
| `man/sphinx-apidoc` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `man/sphinx-autogen` | ⚠️ AUDITED — 1 issue(s) (F9) |
| `usage/configuration` | ⚠️ AUDITED — 4 issue(s) (F5, F7, F9, F14) [F14 new — definition-list term/nested-term concatenation; no F12: all tables on this doc are narrow and render fine] |
| `usage/extensions/index` | ✅ AUDITED — no issues |
| `usage/extensions/apidoc` | ⚠️ AUDITED — 2 issue(s) (F5, F9) |
| `usage/extensions/autodoc` | ⚠️ AUDITED — 4 issue(s) (F1, F5, F9, F13) [F13 = "Options:no-index:" rubric+option concat, recurs many times] |
| `usage/extensions/autosectionlabel` | ✅ AUDITED — no issues |
| `usage/extensions/autosummary` | ⚠️ AUDITED — 2 issue(s) (F1, F9) [F1 = "templates.The" enumerated-list paragraph concat] |
| `usage/extensions/coverage` | ⚠️ AUDITED — 3 issue(s) (F5, F7, F15) [F15 new — todo_node "Todo" admonition confirmed rendering correctly on this page too] |
| `usage/extensions/doctest` | ⚠️ AUDITED — 3 issue(s) (F5, F7, F9) |
| `usage/extensions/duration` | ⚠️ AUDITED — 2 issue(s) (F5, F9) |
| `usage/extensions/extlinks` | ⚠️ AUDITED — 2 issue(s) (F5, F9) |
| `usage/extensions/githubpages` | ✅ AUDITED — no issues |
| `usage/extensions/graphviz` | ✅ AUDITED — no issues [note: every `.. graphviz::`/`.. graph::`/`.. digraph::` example on this page is shown as LITERAL rst syntax (`.. highlight:: rst` sets `::`-blocks to literal display), not an actual invocation — no real graphviz directive is ever compiled here, so the SC#3 `dot` degrade placeholder never appears on this docname; nothing out-of-scope to confirm] |
| `usage/extensions/ifconfig` | ✅ AUDITED — no issues |
| `usage/extensions/imgconverter` | ✅ AUDITED — no issues |
| `usage/extensions/inheritance` | ✅ AUDITED — no issues [SC#3 confirmed: "[inheritance diagram diagram omitted]" placeholder appears exactly as expected at every `.. inheritance-diagram::` invocation, pp.425+; out-of-scope, not an issue-table candidate] |
| `usage/extensions/intersphinx` | ⚠️ AUDITED — 2 issue(s) (F5, F7) |
| `usage/extensions/linkcode` | ⚠️ AUDITED — 1 issue(s) (F5) |
| `usage/extensions/math` | ⚠️ AUDITED — 1 issue(s) (F5) [admonitions (Tip/Info/Warning) render correctly] |
| `usage/extensions/napoleon` | ⚠️ AUDITED — 1 issue(s) (F5) [11pp; Google/NumPy code-block comparisons + admonitions all render correctly; no new findings] |
| `usage/extensions/todo` | ⚠️ AUDITED — 1 issue(s) (F5) |
| `usage/extensions/viewcode` | ⚠️ AUDITED — 1 issue(s) (F5) [Warning admonitions render correctly] |
| `usage/restructuredtext/index` | ✅ AUDITED — no issues [all examples shown as literal rst code-blocks, not real invocations] |
| `usage/restructuredtext/basics` | ✅ AUDITED — no issues [11pp, all examples literal rst; definition-list contrast case (not nested in list_item) renders term-on-own-line correctly, confirming F14 boundary] |
| `usage/restructuredtext/roles` | ✅ AUDITED — no issues [todo_node admonition regression-confirmed again p.465] |
| `usage/restructuredtext/directives` | ⚠️ AUDITED — 2 issue(s) (F13, F7) [29pp; F13 recurs heavily as "Options:optionname:" (rubric+field concat) — pp.469,478(x2),480(x2),482,483,484,487,489,494; F7 recurs as directive-alias-signature concat — pp.476,477,480(code-block/sourcecode/code)] |
| `usage/restructuredtext/field-lists` | ✅ AUDITED — no issues |
| `usage/restructuredtext/domains` | ✅ AUDITED — no issues [stub redirect page, minimal content] |
| `glossary` | ✅ AUDITED — no issues [definition list NOT nested in list_item — term-on-own-line contrast case confirmed correct] |
| `changes/index` | ✅ AUDITED — no issues [minimal stub page] |
| `changes/9.0` | ✅ AUDITED — no issues [dense changelog bullet lists; every bullet's "Patch by X" line renders as a correctly-separated continuation, no F1 concat] |
| `changes/8.2` | ✅ AUDITED — no issues |
| `changes/8.1` | ✅ AUDITED — no issues |
| `changes/8.0` | ✅ AUDITED — no issues [nested sub-bullets (`▸`) render correctly] |
| `changes/7.4` | ✅ AUDITED — no issues |
| `changes/7.3` | ✅ AUDITED — no issues |
| `changes/7.2` | ✅ AUDITED — no issues |
| `changes/7.1` | ✅ AUDITED — no issues |
| `changes/7.0` | ✅ AUDITED — no issues |
| `changes/6.2` | ✅ AUDITED — no issues [code-block example (HTML) renders fine] |
| `changes/6.1` | ✅ AUDITED — no issues [nested sub-bullets render correctly] |
| `changes/6.0` | ⚠️ AUDITED — 1 issue(s) (F1) [multi-paragraph bullet items concat — "frameworks.These", "below.The first option", "extension.The second option" — jQuery-removal changelog entry; code-block (Jinja/HTML) renders fine] |
| `changes/5.3` | ✅ AUDITED — no issues |
| `changes/5.2` | ✅ AUDITED — no issues |
| `changes/5.1` | ✅ AUDITED — no issues |
| `changes/5.0` | ⚠️ AUDITED — 1 issue(s) (F1) [same jQuery-removal multi-paragraph bullet item as changes/6.0, "below.To re-add jQuery" concat, p.539; rubric-style version labels ("5.0.0 b1"/"5.0.0 final") render on own line correctly] |
| `changes/4.5` | ✅ AUDITED — no issues |
| `changes/4.4` | ✅ AUDITED — no issues |
| `changes/4.3` | ✅ AUDITED — no issues |
| `changes/4.2` | ✅ AUDITED — no issues |
| `changes/4.1` | ✅ AUDITED — no issues [nested sub-sub-bullets render correctly] |
| `changes/4.0` | ✅ AUDITED — no issues [rubric-style version labels ("4.0.0b1"/"4.0.0b2") render on own line correctly] |
| `changes/3.5` | ✅ AUDITED — no issues [nested sub-bullets render correctly] |
| `changes/3.4` | ✅ AUDITED — no issues |
| `changes/3.3` | ✅ AUDITED — no issues |
| `changes/3.2` | ⚠️ AUDITED — 1 issue(s) (F9) [p.563 "C, add possibility of parsing..." bullet — 4 semantic-line-break sentences within ONE paragraph (no blank lines in source) render as 4 hard-broken lines, confirming F9 recurs in changelog bullet items too, not just prose paragraphs] |
| `changes/3.1` | ✅ AUDITED — no issues |
| `changes/3.0` | ✅ AUDITED — no issues [nested sub-bullets render correctly] |
| `changes/2.4` | ✅ AUDITED — no issues |
| `changes/2.3` | ✅ AUDITED — no issues [nested sub-bullets render correctly] |
| `changes/2.2` | ✅ AUDITED — no issues |
| `changes/2.1` | ✅ AUDITED — no issues [nested sub-bullets render correctly] |
| `changes/2.0` | ✅ AUDITED — no issues [nested sub-bullets render correctly] |
| `changes/1.8` | ✅ AUDITED — no issues [8pp; deprecation-list bullets (long dotted API-path names) render correctly, no wrapping/overflow issues] |
| `changes/1.7` | ✅ AUDITED — no issues [7pp; long dense bugfix/deprecation bullet lists, no F1/F9 recurrences] |
| `changes/1.6` | ✅ AUDITED — no issues [9pp; F8 recurs (external hyperlink flattened, extra-space artifact after link text "RTD  PDF builds…" p.606) — same pattern as F8's stray-space-before-period, here stray space after link before next word] |
| `changes/1.5` | ✅ AUDITED — no issues [8pp; dense bugfix/feature bullet lists, no F1/F9 recurrences] |
| `changes/1.4` | ✅ AUDITED — no issues [9pp; dense bugfix/feature bullet lists, no F1/F9 recurrences] |
| `changes/1.3` | ✅ AUDITED — no issues [11pp; dense bugfix/feature bullet lists incl. nested sub-bullets, no F1/F9 recurrences] |
| `changes/1.2` | ✅ AUDITED — no issues [9pp; dense bugfix/feature bullet lists incl. deeply nested sub-bullets, no F1/F9 recurrences] |
| `changes/1.1` | ✅ AUDITED — no issues [3pp; dense bugfix/feature bullet lists, no F1/F9 recurrences] |
| `changes/1.0` | ✅ AUDITED — no issues [6pp; dense bugfix/feature bullet lists, no F1/F9 recurrences] |
| `changes/0.6` | ✅ AUDITED — no issues [6pp; dense nested bullet lists incl. a code-block with codly caption badge, no F1/F9/F11 recurrences] |
| `changes/0.5` | ✅ AUDITED — no issues [4pp; dense nested bullet lists incl. a nested dash-sublist of translator credits, renders correctly] |
| `changes/0.4` | ✅ AUDITED — no issues [3pp; dense nested bullet lists, no F1/F9 recurrences] |
| `changes/0.3` | ✅ AUDITED — no issues [1pp; short bullet list] |
| `changes/0.2` | ✅ AUDITED — no issues [2pp; nested bullet lists incl. a multi-line code-block, renders correctly with codly caption badge] |
| `changes/0.1` | ✅ AUDITED — no issues [1pp; short bullet list, spans two "Sphinx 0.1" sub-releases] |
| `examples` | ✅ AUDITED — no issues [10pp; F8 recurs twice (p.675 "create an issue or pull request on GitHub ." stray space before period; p.678 "Read the Docs Sphinx Theme documentation" link flattened, no visible artifact since followed by list not text) — long flat bullet lists of project names render correctly throughout, including nested parenthetical annotations] |



## Next Steps (for Plan 17-02+)

1. Rasterize each docname's page range (`pdftoppm -png -r 150`, batched per docname per RESEARCH
   Pitfall 1 — never the whole 684-page PDF in one batch) into a session-scratch directory.
2. Optionally use the `-b text` baseline or `pypdf.extract_text()` per page range as a
   zero-new-tooling mechanical pre-filter to prioritize review order (never a substitute for the
   mandatory page-by-page visual look, RESEARCH Pitfall 3).
3. For each docname: open its rasterized pages, cross-check against its `-b html` baseline
   (D-04 authority), flag any in-scope divergence (D-06) as a candidate row in the Issue Table
   above (bias toward false positives — flag as a candidate per D-03 rather than silently passing),
   classify against the Out-of-Scope table before adding, then flip its progress-tracker row to
   `✅ AUDITED — no issues` or `⚠️ AUDITED — N issue(s)`.
4. Once every docname is audited, group "high"-severity rows by root cause (D-10) and append
   `FID-01a`, `FID-01b`, … to `.planning/REQUIREMENTS.md` (Plan 17-04); add a single
   medium/low pointer under Future Requirements (D-11).

## Post-Phase-17 Additions (surfaced during Phase 18 UAT — backlog, next milestone)

These findings were NOT part of the original F1–F15 audit set and do NOT alter the frozen
Phase-17 tally/ordering logic above. They are recorded here as the canonical F-series home for
backlog triage.

| Finding | Node kind + failure mode | Occurrences (docname, pp.) | Severity | Origin |
|---|---|---|---|---|
| F16 | `table`/`tgroup` **header row** — a header cell's plain-text label (no `.`/`_` break points, so ZWSP injection does not apply) overflows a narrow fr-sized column and collides with the adjacent header label. Introduced by Phase 18's `FID-01a` fr-column change (D-02): sizing columns to HTML `colwidth` % makes numeric/short-value columns narrow, and their wider header words (`Deprecated`, `Removed`) overflow. The prior equal-width `columns: {colcount}` sizing gave each header enough width, so this is a NEW regression the fr-column fix traded in for the body-cell fix. | `extdev/deprecated` pp.239, 242, 245 — header reads `DeprecatedRemoved` (systemic: recurs for any table whose header labels are wider than their content-proportioned fr column) | medium | Phase 18 UAT (2026-07-19), user-triaged to backlog |

**Fix direction (non-binding, for a future phase):** the fr-column primitive needs to protect a
column from clipping its own header — candidate approaches: a minimum column width floor, allowing
header text to wrap (word-break / soft-hyphen or ZWSP applied to header cells too, not only
`raw()` literal body content), or sizing fr weights from `max(header, body)` intrinsic width
rather than body `colwidth` alone. Kin to F12/F6's right-margin-overflow family.
