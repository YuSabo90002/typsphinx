# Feature Research: v0.8.0 Multi-Master Composition

**Domain:** Sphinx extension multi-document/multi-master output (Sphinx → Typst)
**Researched:** 2026-08-11
**Confidence:** HIGH — every Sphinx-side claim below was read from the installed source
(`.venv/lib/python3.13/site-packages/sphinx` 9.1.0), not recalled; ecosystem claims about
other tools are WebSearch-sourced and marked accordingly with dates/URLs in Sources.

## Verified: Sphinx's LaTeX Builder (the direct precedent)

This is the closest upstream analog to `typst_documents`, and typsphinx's own milestone
plan explicitly patterns the wrapper's include graph on it
(`sphinx/util/nodes.py:485 inline_all_toctrees`). Read directly from
`sphinx/builders/latex/__init__.py` and `sphinx/util/nodes.py` (Sphinx 9.1.0).

### `latex_documents` entry anatomy

5 required positions + 1 optional (`sphinx/builders/latex/__init__.py:304-309`):
`(docname, targetname, title, author, theme, [toctree_only])`.

- **`theme`** (position 5, required) — a *named theme* (`'manual'`, `'howto'`, or a
  custom-registered one) resolved via `self.themes.get(themename)` and applied per entry
  (`update_doc_context`, line 361-367): it sets `docclass`, `papersize`, `pointsize`,
  `wrapperclass`, and (via `theming.py:32/66-68`) `toplevel_sectioning`
  (`'chapter'` vs `'section'`). **typsphinx has no positional equivalent**, but
  functionally overlaps with the *existing* `typst_template_mapping` /
  `typst_template_function` machinery — except those are currently **global**, applied
  identically to every master (verified: `typst_template_mapping` flows through
  `TemplateEngine.__init__(parameter_mapping=...)` in `template_engine.py:207-238`, with
  no per-docname branch anywhere in `builder.py`'s master-write path). A theme is a
  *choice of template*, and typsphinx already has templates — it just can't select a
  different one per master yet.
- **`toctree_only`** (position 6, optional bool, default `False`, line 307-309) — when
  `True`, `assemble_doctree` (line 379-388) discards the index doc's own body and
  synthesizes a bare document containing only its `toctree` nodes, so the PDF opens
  directly on the front matter/first chapter instead of the index page's own prose.
  **typsphinx has no equivalent** — every master's own content (whatever came before/after
  its `toctree::` directives) is always part of the wrapper's include graph.

### `assemble_doctree` / `inline_all_toctrees` — the three composition scenarios

All three were traced in `sphinx/builders/latex/__init__.py:369-415` and
`sphinx/util/nodes.py:485-534`.

1. **A document reachable from TWO masters** (confirmed, matches the milestone's own
   measurement). `write_documents` calls `self.assemble_doctree(docname, toctree_only,
   appendices=...)` once per `latex_documents` entry (line 318), and `assemble_doctree`
   seeds `inline_all_toctrees` with a **fresh** `traversed = [indexfile]` list *at that
   call site* (line 390: `inline_all_toctrees(self, self.docnames, indexfile, tree,
   darkgreen, [indexfile])`). Nothing carries state between entries. Each master therefore
   independently, fully inlines the shared doc — the exact behavior typsphinx's design
   note calls "not concatenated, each an independent PDF, a shared chapter in both is the
   correct outcome." **This is why LaTeX never needed a per-master ledger: `assemble_doctree`
   IS the fresh-traversed-list mechanism typsphinx's wrapper is being redesigned to mirror.**
2. **A document reachable TWICE from ONE master** (a diamond entirely inside one master's
   toctree graph, e.g. `M → [p,q]`, `p → [c]`, `q → [c]`). Inside `inline_all_toctrees`
   (`sphinx/util/nodes.py:503-506`), the *same* `traversed` list is threaded through every
   recursive call for that one master's assembly. The check `if includefile not in
   traversed` means `c` is expanded fully at its **first-visited** site (document order,
   depth-first) and, at the second site, contributes **zero** `newnodes` — the toctree
   entry silently vanishes there, **with no warning emitted anywhere in this function**.
   One copy of `c` ends up in the master, at the position/depth of its first occurrence.
   This is almost certainly the *desired* LaTeX behavior (a chapter shouldn't typeset twice
   in one PDF) — but note it is achieved by **silent, unannounced pruning**, not a warning.
3. **A document listed in `latex_documents` (its own master) that is ALSO another master's
   toctree child — traced further, not previously measured.** There is **no cross-check
   at all** between `self.document_data` (the `latex_documents` list) and
   `env.toctree_includes` (the toctree graph) anywhere in `sphinx/builders/latex/__init__.py`
   — confirmed by an exhaustive grep of every `latex_documents` reference in the installed
   package (6 hits total, all in `init_document_data`/defaults, none touching
   toctree membership). Consequence: the shared doc is built **twice**, independently and
   with zero interaction: (a) once as its own standalone master via its own
   `document_data` loop iteration (full `\documentclass`, its own theme/title/author), and
   (b) once again, separately, inlined as a bare nested section inside whichever other
   master's `assemble_doctree` call reaches it via `toctree`. **No warning, no error, no
   flag connecting the two.** For typsphinx's wrapper/content-split design this is actually
   **already the structurally correct outcome and needs no special-casing**: the shared
   docname's content file carries no template-awareness, so it naturally (a) gets its own
   wrapper as a master (full template, its own PDF) and (b) gets `#include()`d bare into
   the other master's wrapper at whatever DFS depth, heading-offset-adjusted. Recommend a
   **regression fixture** proving this combination compiles correctly, not new production
   code — see Table Stakes below.

### The "selecting" message — verified to be a *different, narrower* mechanism than framed

Two **separate, non-communicating** functions resolve "which parent does this shared doc
belong to," and they can disagree:

- **`sphinx/environment/adapters/toctree.py:562-575 _get_toctree_ancestors`** — builds a
  `docname → parent` map via `parent |= dict.fromkeys(children, p)` while iterating
  `toctree_includes.items()`; because dict union overwrites on each later key, **the
  parent recorded for a doubly-referenced child is whichever `toctree_includes` entry was
  processed LAST in dict-insertion order** (i.e., document *read* order — unrelated to
  nesting depth). This function drives real behavior: it feeds `_resolve_toctree`'s pruning
  (`toctree.py:165`), i.e. the HTML sidebar / breadcrumb "ancestors" computation.
- **`sphinx/environment/__init__.py:942-959 _check_toc_parents`** — called exactly once,
  from `check_consistency()` (`environment/__init__.py:819`), purely to emit the
  **`logger.info`** (not even a warning — `type='toc', subtype='multiple_toc_parents'`)
  message `'document is referenced in multiple toctrees: %s, selecting: %s <- %s'`. Its
  "selecting" value is `max(parents)` — **plain Python string `max()`, i.e. lexicographic
  comparison of docnames. There is no depth computation anywhere in this function.**

**Correction to the milestone's own framing:** the "prefer the deeper path" description
(`zmid` over `xmaster`) is **not falsified** by the measured example — `'zmid' >
'xmaster'` lexicographically too, so the single measured case cannot distinguish "deeper
wins" from "alphabetically-last wins." Reading the source resolves the ambiguity: it is
**pure lexicographic string comparison**, coincidentally aligned with depth in that one
example. **What the "selecting" message actually governs: nothing that touches document
composition.** `assemble_doctree`/`inline_all_toctrees` (the code path that determines
what actually ends up IN a compiled master) never calls `_check_toc_parents` or consults
its result. The message is purely a diagnostic about HTML-style navigation
ancestry/breadcrumbs, and even *that* real mechanism (`_get_toctree_ancestors`) uses a
**different, non-lexicographic** tiebreak (last-read-order-wins) than the one the log
message reports. **Practical implication for typsphinx: there is no upstream "resolution
policy" worth mirroring here.** typsphinx's own multi-master model doesn't need a
single-winner tiebreak at all — the milestone's wrapper design sidesteps the whole
question by keeping every master's DFS independent (see Anti-Feature #4 below for why NOT
to add an analogous tiebreak).

### `latex_appendices`, `latex_toplevel_sectioning`, and the rest of the multi-doc surface

- **`latex_appendices`** (global `list[str]` of docnames) — appended, verbatim, to the
  END of **every** non-`'howto'`-themed master's assembled doctree
  (`assemble_doctree(docname, toctree_only, appendices=self.config.latex_appendices if
  theme.name != 'howto' else [])`, line 318-324). One global list, unconditionally shared
  by all masters that don't opt out via theme. **No typst equivalent.** Given typsphinx's
  per-master wrapper design, a user can already get the identical effect by adding the
  appendix docname to every master's own `toctree::` — this config value mainly saves
  *editing N toctrees* for N masters that share the same appendix set. Real but modest
  value; not required for correctness.
- **`latex_toplevel_sectioning`** (global, `None`/`'part'`/`'section'`, read in
  `sphinx/writers/latex.py:375-388`) — controls whether a master's top-level doc maps to
  `\part`, `\chapter`, or `\section` in the emitted LaTeX. **typsphinx already has a
  structural equivalent, in scope this milestone:** the wrapper's `set heading(offset: N)`
  derived from each doc's DFS depth in the per-master include graph achieves the same
  effect (how "high" a doc's headings render) without any new config surface — this LaTeX
  feature exists because LaTeX's sectioning commands are fixed-name (`\chapter` vs
  `\section`), a constraint Typst's numeric heading levels don't share. **No new work
  needed; note it in the wrapper's design doc as "structurally already covered."**
- **Texinfo and man-page builders corroborate the same 3-part pattern** (read directly):
  `sphinx/builders/texinfo.py:69-131` uses the identical
  `N-tuple config → per-entry assemble_doctree → inline_all_toctrees` shape as LaTeX (own
  copy of the algorithm, same "fresh traversed list per entry" property).
  `sphinx/builders/manpage.py:55-98` skips `assemble_doctree` entirely but still calls
  `inline_all_toctrees(self, docnames, docname, tree, darkgreen, [docname])` per
  `man_pages` entry with a fresh `traversed` list each time (line 90-92) — same
  independence guarantee, simpler because man pages have no theme/appendix concept. This
  corroborates that "N independent config entries, each producing one complete, freshly-
  assembled output via its own DFS traversal" is Sphinx's own established, three-times-
  repeated pattern for multi-document output — not a one-off LaTeX quirk. typsphinx's
  wrapper design (this milestone) brings the `-b typst`/`-b typstpdf` builders into line
  with that same, well-worn shape.
- **`singlehtml` and `epub3` are useful *negative* precedents** (`sphinx/builders/
  singlehtml.py`, `sphinx/builders/epub3.py`) — both always resolve to `root_doc` only;
  neither builder has any N-entries-in/N-outputs-out concept at all. This confirms the
  "one tree → several independent deliverables" feature is **not universal** across Sphinx
  builders — it is specifically the province of the "document assembly" builders
  (LaTeX/Texinfo/man), which is exactly the family `typst_documents` already models itself
  on.

## Other Builders and Extensions Surveyed

| Tool | Multi-document affordance | Table stakes vs. differentiator (for typsphinx) |
|------|---------------------------|---------------------------------------------------|
| **rinohtype** (`rinoh` Sphinx builder, PDF-from-doctree — the closest non-LaTeX analog to typsphinx) | `rinoh_documents` is a **list of dicts**, not tuples (`doc`/`target` required; `template`, `title`, `logo`, `stamp`, arbitrary extra keys accepted as free-form per-document metadata usable in a custom template) — confirmed via rinohtype's own Sphinx-builder docs. Crucially: **`template` is a per-document key**, i.e. rinohtype already supports what typsphinx currently cannot (a different template per master). | Differentiator (future milestone) — dict-shaped config + per-master template selection. Not required for v0.8.0 correctness. |
| **sphinx-multiversion** | Builds N *whole builds* (one per git tag/branch) into N output directories, by checking out each ref into a temp dir and re-running Sphinx per ref — not a "several masters in one build" mechanism at all; orthogonal axis (version) rather than typsphinx's axis (multiple simultaneous manuals from one checkout). | Not applicable — different problem (versioning, not multi-master). Confirms multi-master and multi-version are separate concerns typsphinx should not conflate. |
| **EPUB3 / singlehtml** | Always exactly one output from `root_doc`; no multi-entry config at all (verified above). | N/A — these builders simply don't have this feature; not a source of precedent either way. |

## Typst-Native and Other Markup-First Toolchains

| Tool | "One tree → several deliverables" convention | Shared-chapter handling |
|------|-----------------------------------------------|--------------------------|
| **Typst itself** | No first-party multi-document/book system. `#include()` is the only primitive; community convention (Typst's own examples-book, GitHub Discussion #2201) is a flat `chapters/*.typ` + one `main.typ` that includes them all. Typst has **no cross-file label resolution and no global imports by design** (`typst/typst` issues were closed "not planned" as against Typst's core design) — every included file must re-declare its own imports, which is exactly the constraint CLAUDE.md already documents and typsphinx already works around (`writer.py`'s minimal-import-prepend for included docs). | No convention exists for "one chapter, two books" — confirms typsphinx is filling a **genuine gap in the Typst ecosystem itself**, not just re-solving a problem other tools already handle well. |
| **Asciidoctor** | `include::chapter.adoc[leveloffset=+1]` — a **per-inclusion-site relative heading offset**, explicitly designed so the same chapter file can be (a) published standalone with its own document title and (b) included into a parent book at a shifted heading level, all from one file. | This is the closest cross-ecosystem precedent for the milestone's own planned mechanism (`set heading(offset: N)` derived from DFS depth at each include site). **Validates the design**: "offset computed per include-site, not stored on the shared file" is an established, working pattern elsewhere, not a novel invention. |
| **mdBook** | `SUMMARY.md` defines exactly one book; no native mechanism found (searched official docs/GitHub) for referencing the same source file from two `SUMMARY.md` trees — community workarounds are OS-level symlinks or external preprocessors. | mdBook has **no answer** to "a chapter that belongs to more than one book." Typsphinx's wrapper design, once complete, will do something a fairly popular contemporary tool doesn't support natively at all. |
| **Quarto (book projects)** | Multiple books from one source tree = multiple **Project Profile** YAML files (`_quarto-basic.yml`, `_quarto-advanced.yml`), each declaring its own chapter list — the same "N independent config entries, each with its own include list" shape as `latex_documents`/`typst_documents`. Quarto explicitly has **no "render all profiles" command** — building N books requires N separate `quarto render --profile X` invocations. | typsphinx already does better here (existing feature, not part of this milestone): `TypstPDFBuilder.finish()` iterates every `typst_documents` entry and compiles all masters in **one** `sphinx-build` invocation — worth explicitly protecting as an invariant while doing the wrapper rework, since it's a real, already-earned advantage over a widely-used contemporary tool. |

## Feature Landscape

### Table Stakes (a correct v0.8.0 implementation must have these)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Each master's include graph assembled independently, from a fresh per-master traversal state | Established 3-times-over in Sphinx itself (LaTeX/Texinfo/man-page all seed a fresh `traversed` list per entry) — this is the industry-standard shape, not a typsphinx invention | MEDIUM (already scoped: wrapper/content split + per-master include graph) | Directly closes defect A; mirrors `inline_all_toctrees`'s per-call `traversed` list |
| A doc reachable from two masters renders fully, independently, in each | Confirmed via `assemble_doctree`'s fresh-`traversed`-per-call behavior; matches typsphinx's own already-stated invariant "masters are not concatenated" | Included in the wrapper work above | No dedup across masters — see Anti-Feature #3 |
| A doc reachable twice within ONE master is included once, at its first-DFS-encountered depth, without breaking the compile | Matches LaTeX's own (silent, unwarned) `inline_all_toctrees` behavior — this is expected/correct, not a defect, in the one-master case | Included in the wrapper work above | Already measured per milestone context; no warning needed to match upstream, though typsphinx may choose to log more helpfully than upstream does (optional, non-blocking) |
| Duplicate `typst_documents` target names across entries are detected and warned, never silently drop a master's body | Sphinx's own LaTeX builder has the **identical bug and zero detection** for this exact case (verified: no cross-check anywhere in `latex_documents` handling) — so typsphinx doing better here is itself table-stakes-level correctness, this is not optional polish | LOW–MEDIUM (already scoped as CR-02) | Simultaneously the milestone's clearest point of *exceeding* upstream — see differentiator framing below |
| Cross-reference degradation is resolved per compilation unit (per master), not via a single build-wide union set | Direct consequence of masters being independently assembled — a union-based `master_included_docnames` becomes wrong the moment two masters have different include sets | MEDIUM–HIGH (already scoped: `context`+`query` compile-time guard) | Two more label-reference sites share the shape and must be covered: `translator.py:3273/3281` (citation back-refs), `:4291` |
| Per-master `toctree` option resolution (`maxdepth`→`#outline(depth:)`, `numbered`, `caption`) keeps working after the wrapper refactor | **Already built and already correct** — `TemplateEngine.extract_toctree_options` (`template_engine.py:542-586`) reads the maxdepth/numbered/caption off *that master's own* first toctree node, exactly mirroring LaTeX's own `tocdepth` handling (`latex/__init__.py:312-316`, also TOC-listing-depth only, not content pruning) | LOW (regression risk only — verify the wrapper-generation code path still calls this per master) | Not new work; a "don't regress" item as the master/included branch in `writer.py` is torn out |
| A docname that is simultaneously its own `typst_documents` master AND a toctree child of another master compiles correctly in both roles | Verified Sphinx allows this silently and with no cross-check at all (LaTeX builder) — and typsphinx's wrapper design produces the structurally correct result for free (own wrapper as master; bare `#include` at whatever depth in the other master) | LOW (needs a regression fixture, not new logic — confirmed no special-casing required by the design) | Add a GATE-01 fixture: one docname is both a `typst_documents` entry and toctree'd elsewhere; assert both PDFs compile and both contain its content |
| The two PR #131 image defects (rehomed-image collision with a real `srcdir` image; rehome path escaping `outdir` for non-`doctreedir` absolute URIs) | Both are already real, measured regressions in `TypstBuilder._track_image()` unrelated to the master/included split but living in the same builder file being reworked | LOW–MEDIUM each (already scoped) | Independent of the composition model — worth fixing in the same milestone mainly because the file is already open, not because multi-master *causes* them |

### Differentiators (competitive value, explicitly OUT of this milestone)

| Feature | Value Proposition | Complexity | Notes |
|---------|--------------------|------------|-------|
| Per-master template selection (rinohtype's `template=` key precedent) | Different manuals (e.g. an internal "howto" vs. a formal "manual") often want different cover pages / layouts; today every `typst_documents` entry shares one global template | MEDIUM | **Enabled by, not included in,** this milestone — once every master has its own wrapper `.typ`, that wrapper is exactly the natural place to `#import` a per-master-chosen template. Needs its own config-shape decision; don't fold into v0.8.0's already-large blast radius |
| Richer/dict-shaped `typst_documents` entries with arbitrary metadata (rinohtype precedent) | Lets a custom template read master-specific values (subtitle, stamp, logo) without inventing new positional tuple slots forever | MEDIUM–HIGH | Config-compatibility question of its own; explicitly defer — this milestone's own risk log already flags "large test blast radius" from the wrapper/content split alone |
| Shared-appendix shortcut (`latex_appendices` equivalent) — a config list of docnames auto-appended to every master | Saves editing N toctrees by hand when N masters share a common "glossary"/"license" chapter set | LOW–MEDIUM | Users can already get the identical effect today by adding the docname to each master's own toctree; this is a convenience wrapper around already-correct behavior, not new capability |
| `toctree_only`-equivalent — suppress a master's own index-page prose, emit only its toctree structure | Lets an `index.rst` written for HTML (with a "Welcome to..." landing paragraph) drive a PDF that opens straight on front matter/chapter 1 | LOW | Straightforward once the wrapper exists (skip the root content file, include only its resolved children); genuinely useful for projects whose `root_doc` is HTML-navigational, not book front matter |
| More informative "docname serves double duty" note (master + included child) | Sphinx gives zero signal for this combination (verified); a one-line `logger.info` is cheap and prevents user confusion the day they add a manual's own docname to a sibling manual's toctree by accident | LOW | Genuinely optional polish riding on the table-stakes fixture above — do not let it grow scope |

### Anti-Features (attractive-looking, explicitly exclude)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|----------------|-------------------|-------------|
| Abandon per-document `.typ` output and assemble each master purely at the in-memory doctree layer (LaTeX's own model, exactly) | "Sphinx's own reference builder does it this way and it structurally cannot have B-1/B-2/defect A at all" — verified true (LaTeX's `assemble_doctree` produces zero `\input`/`\include`) | Deletes the very artifact the `-b typst` builder exists to produce: inspectable, individually-compilable per-document `.typ` files. The milestone's own PROJECT.md already reaches this conclusion and rejects it explicitly | Stay at the file layer, mirror `inline_all_toctrees`'s *algorithm* (fresh traversal state per master) without adopting its *output shape* (one flattened in-memory tree) |
| A single, shared root `.typ` file applied uniformly across every master (the exact shape this milestone is dismantling) | Looks like it reduces duplication / write work versus one wrapper per master | This is the direct cause of B-1 and B-2 (a shared template file re-expanding its title page/outline mid-body when re-included); reintroducing it — even as a later "optimization" — reopens both defects | One wrapper `.typ` per `typst_documents` entry, each applying the template independently; content files stay template-free |
| Cross-master content deduplication (detect that two masters render the same chapter and cross-link instead of duplicating the typeset text) | Smaller total output size, faster incremental builds, "DRY" appeal | Breaks the explicit design invariant that masters produce independent, standalone PDFs (a reader of `bmaster.pdf` should never need `index.pdf` open to read a chapter); reintroduces exactly the "which master does this belong to" ambiguity the wrapper design exists to eliminate structurally | Accept duplication across independently-produced PDF artifacts as correct and cheap — Typst compiles fast, disk is cheap, and each PDF stays genuinely self-contained |
| A "prefer the deeper/more-specific parent" (or any single-winner) tiebreak for a doc claimed by multiple masters or multiple toctree parents | Sphinx appears to do this (`'selecting: zmid <- shared'`) | Verified the actual mechanism is `max(parents)` — **plain lexicographic string comparison with no depth concept at all** — and that it doesn't even agree with the *other* internal Sphinx function (`_get_toctree_ancestors`, last-read-order-wins) that governs real behavior (breadcrumb ancestry). There is no coherent "resolution policy" here worth porting, and copying an incidental artifact of Sphinx's HTML-navigation code as if it were a deliberate design choice would import a bug, not a feature | typsphinx's own model needs no single-winner tiebreak at all: masters are independent, so "which master does this belong to" is never a question that needs answering for composition (only CR-02's *target-name* collisions need a winner, and that already has its own warn-and-fallback convention) |
| Per-master conditional content inside a shared content file (e.g. a directive letting one `.typ` render differently depending on which master included it) | "One chapter, two slightly different versions for two audiences" seems efficient | Directly violates the milestone's own foundational property that content files carry **no** master-awareness ("the unanswerable question... removed from the shared content files") — reintroducing conditional-per-master logic into a content file recreates exactly what B-1/B-2/defect A came from | If a chapter must genuinely differ per audience, make it two distinct docnames (Sphinx's own `only::`/tag mechanism already resolves audience-conditional content at the doctree-read layer, upstream of typsphinx entirely) |
| Free-form per-master output subdirectories / structured naming (`manuals/foo.pdf`) | Looks like natural organization for a project with many manuals | typsphinx's existing target-name guard (`builder.py` D-06/D-07) **deliberately forbids path separators** in a `typst_documents` target specifically to prevent path-traversal and cross-master collisions; Sphinx's own LaTeX builder doesn't support subdirectories either (flat `outdir`) | Not ruled out forever, but requires its own deliberate collision-safety redesign — do not lift the existing guard as a side effect of this milestone's other work |

## Feature Dependencies

```
wrapper/content split (this milestone)
    └──requires──> master/included binary at writer.py:96 removed
                       └──enables──> per-master include graph in the wrapper (this milestone)
                                          └──enables──> compile-time xref degradation via context+query (this milestone)
                                          └──enables (future)──> per-master template selection (differentiator, deferred)
                                          └──enables (future)──> toctree_only-equivalent (differentiator, deferred)

duplicate-target detection (CR-02, this milestone)
    └──independent of──> per-master include graph (separate registry, same "warn + docname fallback" convention as CR-01)

"docname is both a master and a toctree child" regression fixture
    └──depends on──> wrapper/content split landing first (the property being verified doesn't exist as a clean guarantee before it)

per-master toctree option resolution (maxdepth/numbered/caption)
    └──already built──> must be re-verified, not re-implemented, once writer.py's master branch is torn out

shared-appendix shortcut / dict-shaped typst_documents / per-master templates (differentiators)
    └──all depend on──> wrapper/content split shipping first (the wrapper file is the natural anchor point for every one of them)
```

### Dependency Notes

- **Per-master include graph requires the master/included binary's removal first**: the
  graph has to live somewhere that is unambiguously "per master," and today's
  `_is_master_document()` split means there is no such place — every included document's
  `.typ` is currently written once, shared by whichever masters reach it. The wrapper is
  what creates the per-master anchor point.
- **CR-02 (duplicate-target detection) is independent of the include-graph work** — it
  operates purely on the `typst_documents` config list itself (comparing target names
  across entries), not on the toctree graph, so it can be built and tested without waiting
  on the wrapper split, though shipping them in the same milestone is reasonable since both
  touch `builder.py`.
- **All differentiators here share one dependency**: none of them are worth attempting
  before the wrapper exists, because the wrapper is precisely the file each one would need
  to extend (a per-master template import, a per-master metadata dict, a per-master
  toctree-only truncation). Sequencing them into a later milestone, after the wrapper has
  shipped and stabilized, is lower-risk than trying to design the wrapper's shape and its
  extension points simultaneously.

## Explicitly Out of This Milestone

Per the downstream requirements author's already-decided scope (wrapper/content split,
per-master include graph, duplicate-target detection, compile-time xref degradation, two
image defects, release prep), the following researched items are differentiators or
anti-features that should **not** be pulled into v0.8.0 requirements, even though they
surfaced directly from studying the same code paths this milestone touches:

- Per-master template selection (differentiator — needs its own config-shape milestone)
- Dict-shaped / arbitrary-metadata `typst_documents` entries (differentiator — config
  compatibility risk on top of an already-large blast radius)
- Shared-appendix shortcut, `toctree_only`-equivalent (differentiators — real but modest
  value, cleanly deferrable; users have a manual workaround for the first today)
- Any single-winner tiebreak for doc-claimed-by-multiple-parents (anti-feature — not
  needed by typsphinx's independent-masters model at all, and the closest upstream
  precedent is not something worth mirroring — see Anti-Features table)
- Cross-master content deduplication (anti-feature — violates the "independent PDFs"
  invariant)
- Free-form per-master output subdirectories (anti-feature-adjacent — the existing
  target-name path guard is deliberate; don't lift it here)

## Sources

- `sphinx/builders/latex/__init__.py` (Sphinx 9.1.0, installed at
  `.venv/lib/python3.13/site-packages/sphinx/builders/latex/__init__.py`) — `latex_documents`
  anatomy, `init_document_data`, `write_documents`, `assemble_doctree`, `latex_appendices`,
  theme/`toctree_only` handling — read directly, function/line references above
- `sphinx/util/nodes.py:485-534` (Sphinx 9.1.0) — `inline_all_toctrees`
- `sphinx/environment/__init__.py:797-823, 914-960` (Sphinx 9.1.0) — `check_consistency`,
  `_traverse_toctree`, `_check_toc_parents` (the `max(parents)` "selecting" message)
- `sphinx/environment/adapters/toctree.py:32-47, 119-200, 560-576` (Sphinx 9.1.0) —
  `note_toctree`, `_resolve_toctree`, `_get_toctree_ancestors`
- `sphinx/writers/latex.py:375-388` (Sphinx 9.1.0) — `latex_toplevel_sectioning` consumption
- `sphinx/builders/texinfo.py:69-131`, `sphinx/builders/manpage.py:55-98` (Sphinx 9.1.0) —
  corroborating N-tuple-config + fresh-`inline_all_toctrees`-per-entry pattern
- `sphinx/builders/singlehtml.py`, `sphinx/builders/epub3.py` (Sphinx 9.1.0) — negative
  precedent (no multi-entry config)
- `/home/yuta/Documents/typsphinx/typsphinx/builder.py` (project source) — existing
  `_resolve_output_stem`, `_included_docnames`/`master_included_docnames` ledger,
  D-06/D-07 path guard
- `/home/yuta/Documents/typsphinx/typsphinx/template_engine.py:542-586` (project source) —
  `extract_toctree_options`, confirming per-master maxdepth/numbered/caption already works
- `/home/yuta/Documents/typsphinx/typsphinx/templates/base.typ:43,79-86` (project source) —
  `toctree_maxdepth` feeds `#outline(depth:)` only (TOC-listing depth, not content pruning)
- rinohtype Sphinx builder docs — `rinoh_documents` dict shape, per-document `template` key
  ([mos6581.org/rinohtype/master/sphinx.html](https://www.mos6581.org/rinohtype/master/sphinx.html),
  WebSearch, 2026-08-11)
- Typst multi-file project conventions — GitHub Discussion
  [typst/typst#2201](https://github.com/typst/typst/discussions/2201), Typst Examples Book
  ([sitandr.github.io](https://sitandr.github.io/typst-examples-book/book/basics/must_know/project_struct.html)),
  bibliography-across-files issue
  [typst/typst#424](https://github.com/typst/typst/issues/424) (WebSearch, 2026-08-11)
- Asciidoctor `leveloffset` on `include::` — official docs
  ([docs.asciidoctor.org/asciidoc/latest/directives/include-with-leveloffset](https://docs.asciidoctor.org/asciidoc/latest/directives/include-with-leveloffset/))
  (WebSearch, 2026-08-11)
- mdBook `SUMMARY.md` — official docs
  ([rust-lang.github.io/mdBook/format/summary.html](https://rust-lang.github.io/mdBook/format/summary.html));
  no native cross-book chapter-sharing mechanism found (WebSearch, 2026-08-11)
- Quarto book Project Profiles — official docs
  ([quarto.org/docs/projects/quarto-projects.html](https://quarto.org/docs/projects/quarto-projects.html))
  and community discussion
  [quarto-dev/discussions#9152](https://github.com/orgs/quarto-dev/discussions/9152)
  (WebSearch, 2026-08-11)
- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` — v0.8.0 milestone brief (goal,
  target features, key context, carried-forward deferred items) and `CLAUDE.md` —
  architecture overview

---
*Feature research for: typsphinx v0.8.0 multi-master composition*
*Researched: 2026-08-11*
