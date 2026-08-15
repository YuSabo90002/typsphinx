# Stack Research

**Domain:** Sphinx→Typst output composition rework (v0.8.0 "multi-master composition" milestone)
**Researched:** 2026-08-11
**Confidence:** HIGH

## Headline Answer

**Nothing new needs to be installed.** No new PyPI runtime dependency, no new dev/test dependency,
no new `@preview` package, no new version-lockstep site. The milestone is a pure restructuring of
*how* the existing translator output is assembled into files, using Typst 0.15 standard-library
primitives (`include`, `set heading(offset:)`, `context`, `query`, `link`, `label`) that are already
in active use in `typsphinx/translator.py` and `typsphinx/writer.py` today, plus Python-side Sphinx
9.1 APIs (`env.toctree_includes`, `env.get_doctree`, `sphinx.util.nodes.inline_all_toctrees`) that
are stable, undeprecated, and already imported/vendored-as-reference by this codebase's own
docstrings (`builder.py`'s `_compute_master_included_docnames` already cites
`sphinx/util/nodes.py:485`). The prior stated in the question is correct; the effort below is spent
verifying it rather than manufacturing additions.

## Recommended Stack

### Core Technologies

No changes. The milestone ships entirely inside the existing stack:

| Technology | Version (pinned today) | Purpose | Why no change is needed |
|------------|------------------------|---------|--------------------------|
| `sphinx` | `>=9.1,<10` | Doctree read/build pipeline | `env.toctree_includes`, `env.get_doctree`, `Builder.write_doc`/`finish` — all present, undeprecated, unchanged in 9.1.0 (verified against installed package, see Sources) |
| `docutils` | `>=0.21,<0.23` | Node types (`toctree`, `section`, etc.) | Doctree shape the wrapper walks is unaffected by this milestone |
| `typst` (typst-py) | `>=0.15.0,<0.16` | `.typ` → PDF compilation | All four language primitives the wrapper design needs (`include`, `set heading(offset:)`, `context`+`query`, `link`) are stable Typst 0.15 stdlib features already exercised by the current translator/writer |

### Supporting Libraries

No additions. Existing bundled `@preview` packages are unaffected — see "@preview package impact" below.

### Development Tools

No additions. `pytest`, `pypdf`, `pillow`, `black`, `ruff`, `mypy`, `tox` all already cover what
this milestone's gates need (see "Test-side tooling" below).

## Installation

```bash
# No installation step. pyproject.toml's [project.dependencies] and
# [project.optional-dependencies].dev are unchanged by this milestone.
```

## Verification: Typst 0.15 language surface the wrapper design rests on

Typst's website docs (`typst.app/docs`) track the latest stable release; the currently installed
`typst-py` reports `0.15.0`, and the latest upstream Typst release is `0.15.1` (2026-07-17) — a
patch release (font/layout fixes only, no language changes). So the fetched docs below are
version-matched to the pin, not drifted ahead to an unreleased 0.16.

### 1. `include` path resolution — relative to the file it's written in, NOT the including file

**Read from documentation + confirmed by a Typst core maintainer (laurmaedje) on the official
forum**, not inferred:

> "When writing chapters of text, it is very natural to be able to use relative paths to include
> other chapters." … "Arguments retain their source location for error messages and the same
> source location mechanism is used to resolve relative paths."

This is **lexical, per-file resolution**: a relative path written inside `guide/index.typ` resolves
relative to `guide/index.typ`'s own location on disk, regardless of which wrapper (or how deeply
nested a wrapper) eventually `#include()`s it. Absolute paths (leading `/`) resolve against the
Typst project root instead.

**Implication for the wrapper design:** content files stay resolvable exactly as they are today
even after every wrapper moves to `set` its own template and its includes are driven from a
different file. An `#image("../foo.png")` or a nested `#include("other.typ")` written inside a
content file keeps working unmodified when that content file is pulled into a wrapper at any
directory depth, because Typst never re-resolves it relative to the wrapper. This directly
retires **B-1** (today's "parent includes from the docname, output stem from the target" mismatch)
as a *class* of bug, not just today's specific instance.

### 2. `#include()` DOES inherit the enclosing `show`/`set` style chain

**Read from an official Typst GitHub discussion, maintainer laurmaedje replying directly**, not
inferred:

> "If you `#set math.equation(numbering: "(1)")` in main.typ all included files (after the set
> rule) will also be affected."

Style rules (`set`/`show`) are not lexically confined to the file they're written in — they apply
to the document flow from the point they're established onward, and `#include()` splices the
included file's returned content into that same flow at the call site. This is the exact mechanism
the multi-file-book pattern (`main.typ` sets, then `#include`s chapter files) documented across the
Typst community relies on.

**Implication for the wrapper design:** a wrapper can `set heading(offset: N)` immediately before
each `#include(<docname>.typ)` and have that offset apply to every heading inside that included
content file — including headings inside files that content file itself further `#include()`s,
*unless* a deeper file re-`set`s `heading(offset:)` itself (nested `set` rules override for their
own remaining scope, standard Typst scoping). Since content files carry no template and (per the
milestone's own scope) no `set heading(offset:)` of their own, this composes cleanly: the wrapper's
per-include `offset` derived from DFS depth is the *only* place that rule is set, so there's no
override collision to design around.

### 3. `context { }` + `query(<label>)` for compile-time label-existence — array-based, not
error-based

**Read from official docs (Query, Context, Label reference pages) plus corroborating community
usage (GitHub issues/discussions on the `.len()`-check idiom)**:

- `query()` must run inside a `context` block (it is a *contextual* function).
- `query(<label>)` returns an **array** of matching elements. When no element carries that label,
  the array is empty (`.len() == 0`) — **querying a nonexistent label is not an error**, it is the
  standard, documented way to test existence.
- The conventional idiom (used throughout the Typst ecosystem, and already the shape typsphinx uses
  per PROJECT.md's own live measurement) is: `#context { if query(<label>).len() > 0 { link(...) }
  else { plain-text } }`.
- No documentation-stated restriction on using a `query()` result inside a conditional to decide
  whether to `link()` — this is the documented, common pattern, not a workaround.

**Implication:** this is not new territory for typsphinx — PROJECT.md already records this exact
guard as "measured working" against the live tree. The stack-research contribution here is the
external confirmation that this is *documented, supported* behavior (not an implementation detail
that could silently regress), plus the fact that two more call sites (`translator.py:3273/3281`
citation back-references, and `:4291`) share the same shape and should follow the same guard.

### 4. `set heading(offset: N)` — additive, not absolute

**Read directly from the official Heading reference page**:

> "The starting offset of each heading's `level`, used to turn its relative `depth` into its
> absolute `level`."

Formula, stated in the docs: **`level = offset + depth`**. It is **additive/relative**, not an
absolute reassignment — a heading written with `=` (syntactic depth 1) under `offset: 2` becomes
`level` 3, not `level` 2. This matches the milestone's own design ("`set heading(offset: N)` per
include derived from DFS depth" — i.e., the wrapper computes an additive shift per include, not a
literal target level).

Composition across nested scopes is not spelled out verbatim in the reference page (confirmed by
direct fetch — the docs state the formula but not nested-`set` interaction explicitly); the nested
behavior above (innermost `set` wins for its remaining scope) is standard Typst `set`-rule scoping,
not `heading`-specific, and is consistent with community usage of this exact "one offset per
include depth" pattern for book-style multi-chapter documents.

### 5. Version-sensitivity risk toward Typst 0.16

No announced breaking change to `include`, `heading(offset:)`, `context`, or `query` was found in
the changelog index or the two most recent release notes (0.15.0, 0.15.1). These are long-standing,
widely-relied-upon stdlib primitives (the multi-chapter `include` + `set heading(offset:)` pattern
and the `context`+`query` existence-check idiom both predate 0.15 in community usage), so the risk
of a silent 0.16 behavior change is assessed **LOW**. The project's existing `typst>=0.15.0,<0.16`
pin plus the weekly `drift.yml` re-resolution job (per CLAUDE.md) is the correct, already-existing
mitigation — no new safeguard is needed for this milestone specifically.

## Verification: Sphinx 9.1 Python API surface

All read directly from the **installed** `sphinx==9.1.0` package
(`.venv/lib/python3.13/site-packages/sphinx/`), not recalled — HIGH confidence, primary source.

| API | File:line | Status in 9.1.0 | Notes |
|---|---|---|---|
| `env.toctree_includes` | `environment/__init__.py:188` | Plain `dict[str, list[str]]` attribute, no deprecation | Actively used by Sphinx's own `Builder.write()` (sorted for determinism at line 739) — this is core infrastructure, not a legacy escape hatch |
| `env.get_doctree(docname)` | `environment/__init__.py:650` | Plain method, no deprecation | Used by both the LaTeX builder's `assemble_doctree` and typsphinx's own existing `write()` override |
| `sphinx.util.nodes.inline_all_toctrees` | `util/nodes.py:485` | **Not** deprecated | A *different*, unrelated function in the same module (`nested_parse_with_titles`, line 393-407) carries a "will be deprecated in Sphinx 8" docstring note — do not confuse the two. `inline_all_toctrees` itself has no such marker and is the live reference algorithm the LaTeX and Texinfo builders both still call |
| `Builder.write_doc()` | `builders/__init__.py:828` | Abstract extension point (`raise NotImplementedError`), no deprecation | Correct, intended override point — typsphinx already uses it |
| `Builder.prepare_writing()` | `builders/__init__.py:820` | No-op extension point, no deprecation | Available if the wrapper generator needs a pre-write hook distinct from `write_doc`/`finish` |
| `Builder.finish()` | `builders/__init__.py:846` | No-op extension point, no deprecation | typsphinx already uses this for PDF compilation in `TypstPDFBuilder` |
| `Builder.write()` | `builders/__init__.py:704` | **Decorated `@final`** | See note below — pre-existing, not new to this milestone |
| `LaTeXBuilder.assemble_doctree` | `builders/latex/__init__.py:369` | Live, calls `inline_all_toctrees` at line 389 | Confirms `inline_all_toctrees(builder, docnameset, docname, tree, colorfunc, traversed)` is the still-current call shape to mirror, matching PROJECT.md's stated reference point |

**`@final` note (pre-existing, not a new risk introduced by this milestone):** `Builder.write()`
carries `typing.final` in Sphinx 9.1. typsphinx's `TypstBuilder` already overrides it today
(`builder.py:384`, to preserve raw `toctree` nodes instead of Sphinx's default
`get_and_resolve_doctree()`-expanded ones) — a pattern that predates this milestone. `@final` is a
static-analysis-only marker; nothing breaks at runtime. `pyproject.toml`'s `[tool.mypy.overrides]`
already disables the `override` and `misc` error codes for `typsphinx.*` (`pyproject.toml:145`),
which is what keeps this override green under `mypy typsphinx/`. Whatever this milestone's wrapper
generator does (continuing to override `write()`, or moving the toctree-graph-walk logic into
`write_doc`/`finish` using `env.toctree_includes` directly instead) works within this same,
already-accepted pattern — no new mypy exemption is required.

**No PendingDeprecationWarning/DeprecationWarning exposure found** in any of the above call paths
under Sphinx 9.1.0 — relevant because `pyproject.toml`'s `filterwarnings` already escalates both to
hard errors (`pyproject.toml:85-97`). The only `RemovedInSphinx11Warning` (a `PendingDeprecationWarning`
subclass) sites in the installed package are unrelated `builder.app`/`env.app`/`events.app` accessors
(`deprecation.py:13`, `builders/__init__.py:142`) — typsphinx's translator/writer/builder code does
not touch those attributes, and this milestone's design doesn't introduce a new touch point either.

## Test-side tooling: no gap

`pypdf>=6.14,<7` and `pillow>=12.3,<13` (already dev dependencies, `pyproject.toml:46-47`) are
sufficient for the milestone's stated assertions — multiple PDFs from one build, per-master content
presence/absence, heading-level checks — because each is just "open PDF N, extract text/structure,
assert." Nothing about asserting on N independent PDF outputs instead of 1 requires new tooling;
it's the same `pypdf.PdfReader` call made once per master's output path.

**One already-available, zero-new-dependency option worth naming for the roadmap (not a
requirement):** the installed `typst` Python package (`typst-py`, already pinned) exposes a
`typst.query(input, selector, field=None, one=False, ...)` function at the Python binding level —
distinct from the in-language `context`+`query()` used inside `.typ` files. This lets a test compile
a `.typ` wrapper and then query it by selector/label directly (e.g., heading `level` fields, or
label presence) without going through PDF text extraction at all. It ships with the dependency
that's already pinned, so reaching for it costs nothing new — but `pypdf`/`pillow` already fully
cover the milestone's stated needs, so this is a "could simplify some assertions later," not a gap
to fill now.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| Stay at the file-composition layer (per-master wrapper `#include()`s content files) | Compose at the doctree layer like Sphinx's `LaTeXBuilder` (inline everything into one doctree before translation, emit one `.typ` per master with no `#include()`s at all) | Only if the `-b typst` builder's per-document `.typ` output were dropped as a goal — PROJECT.md already rules this out explicitly: doctree-layer composition would delete the per-document `.typ` files that builder exists to produce |
| `context`+`query(<label>)` compile-time existence guard | A build-time Python-computed boolean (today's `master_included_docnames` approach) | Never, for this milestone — the build-time approach is exactly what's being retired; it can't express "does this label exist in *this specific compiled unit*" once one content file can be `#include()`d into more than one wrapper |
| `env.toctree_includes` walked directly (mirroring `inline_all_toctrees`'s DFS) | Re-fetching each doctree via `env.get_doctree()` and walking live `toctree` nodes (today's `TypstBuilder.write()` override approach) | `env.toctree_includes` is cheaper (no doctree deserialization) and is what the milestone's own stated design ("mirror `sphinx/util/nodes.py:485`... at the file-composition layer") calls for; doctree-node walking remains relevant only if the translator itself still needs raw `toctree` nodes for something other than composition (a `write_doc`-time question, not a stack question) |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| A 5th `@preview` Typst Universe package (e.g. a "book"/"chapterize" template package) to drive the wrapper's include graph or heading offsets | Breaks the standing zero-new-dependency / four-package invariant for no capability gain — `include`, `set heading(offset:)`, `context`+`query` are already stdlib and already used in this codebase | Hand-written wrapper generation using the four primitives above, exactly as scoped in PROJECT.md |
| A Python templating engine addition (Jinja2, Mako, etc.) for wrapper generation | `template_engine.py` already has a working, dependency-free template-rendering approach for the *existing* master template step; the wrapper is a structurally similar (arguably simpler — no user-facing customization surface stated for it) generation task | Extend `TemplateEngine`/existing string-building patterns in `writer.py`/`template_engine.py` |
| `sphinx.util.nodes.inline_all_toctrees` called directly at the Python/doctree layer to *produce* the wrapper's Typst output | It builds a merged **doctree** (docutils nodes) for a single-file translation pass — exactly the doctree-layer composition PROJECT.md explicitly rejects for this milestone (would delete the per-document `.typ` files) | Use it only as the *algorithmic reference* for DFS order/`traversed`-list semantics, reimplemented over `env.toctree_includes` at the file-composition layer, as the milestone's own key-context notes already state |
| A new Python PDF-diffing or PDF-assertion library for the multi-master test gates | `pypdf`/`pillow` already installed and already used by GATE-01/GATE-02-style gates; "several PDFs from one build" is not a different *kind* of assertion, just more of the same kind | Reuse `pypdf.PdfReader` per output path, as existing tests already do |

## Stack Patterns by Variant

**If the wrapper generator needs a pre-`write_doc` hook to build the per-master include graph
before any content file is written:**
- Use `Builder.prepare_writing(docnames)` (an existing, undeprecated, no-op-by-default extension
  point at `builders/__init__.py:820`)
- Because it runs once per `write()` invocation before any `write_doc` call, and is the same
  extension point Sphinx's own builders use for this kind of pre-computation

**If the wrapper generator instead needs the fully-resolved `env.toctree_includes` graph (built
during the read phase, before any write-phase hook runs):**
- Read `self.env.toctree_includes` directly inside whichever hook is chosen — it's populated by the
  time `write()` starts (Sphinx's own `Builder.write()` sorts it at line 739, confirming it's fully
  populated pre-write)
- Because this avoids re-walking doctrees via `env.get_doctree()` for graph-shape information that
  `env.toctree_includes` already has in the cheaper `dict[str, list[str]]` form

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| `typst-py 0.15.0` (installed) | Typst language docs at `typst.app/docs` (tracks 0.15.1, latest stable) | 0.15.1 is a patch release (font/layout fixes only per its release notes) — no language-surface drift between the installed compiler and the fetched docs |
| `sphinx 9.1.0` (installed) | This milestone's Python API surface | Verified directly against the installed package tree; no deprecation warnings on any API this milestone newly depends on |
| Four `@preview` packages (codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7, gentle-clues 1.3.1) | Wrapper/content split | Unaffected — both wrapper and content files continue to need their own `@preview` imports exactly as master/included files do today (Typst's `#include()` still does not inherit *import* statements, only style rules — an orthogonal fact already documented in `writer.py:206`), so the version-lockstep site count does not grow |

## Sources

- `https://typst.app/docs/reference/scripting/` — `include` syntax reference (confirms syntax; does
  not itself state path-resolution rule, which was confirmed via the forum thread below)
- `https://forum.typst.app/t/why-are-paths-always-relative-to-the-current-file/306` — Typst core
  maintainer (laurmaedje) confirming per-file lexical path resolution — HIGH confidence (primary
  maintainer statement)
- `https://github.com/typst/typst/discussions/2201` — official Typst GitHub discussion, maintainer
  laurmaedje confirming `set`/`show` rule inheritance across `#include()` — HIGH confidence
- `https://typst.app/docs/reference/model/heading/` — official Heading reference page, `offset`
  parameter exact wording and `level = offset + depth` formula — HIGH confidence (primary docs)
- `https://typst.app/docs/reference/introspection/query/` — official Query reference page — HIGH
  confidence (primary docs)
- `https://typst.app/docs/reference/context/` — official Context reference page — HIGH confidence
  (primary docs)
- `https://typst.app/docs/changelog/`, `https://github.com/typst/typst/releases/tag/v0.15.0`,
  `https://github.com/typst/typst/releases/tag/v0.15.1` — version-currency check (0.15.1 is a patch
  release, no language-surface changes) — HIGH confidence
- Installed `sphinx==9.1.0` package source, read directly:
  `environment/__init__.py`, `util/nodes.py`, `builders/__init__.py`, `builders/latex/__init__.py`,
  `deprecation.py` — HIGH confidence (primary source, matches this project's exact pinned version)
- `/home/yuta/Documents/typsphinx/pyproject.toml` — current dependency/tooling declarations
- `/home/yuta/Documents/typsphinx/typsphinx/builder.py`, `typsphinx/writer.py` — existing
  implementation this milestone extends (confirms `@final`-override pattern predates this milestone,
  confirms current dedup/degradation mechanisms being replaced)
- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` §"Current Milestone: v0.8.0" — milestone
  scope and live-measured defect evidence (2026-08-11)
- Installed `typst-py 0.15.0` Python binding, introspected directly (`typst.query` signature) — HIGH
  confidence (primary source)

---
*Stack research for: v0.8.0 multi-master composition (typsphinx)*
*Researched: 2026-08-11*
</content>
