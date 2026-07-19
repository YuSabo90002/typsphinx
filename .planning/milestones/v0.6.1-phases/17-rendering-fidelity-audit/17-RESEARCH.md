# Phase 17: Rendering-Fidelity Audit - Research

**Researched:** 2026-07-19
**Domain:** PDF page-rasterization/inspection tooling, Sphinx multi-builder (`html`/`text`/`typstpdf`)
provenance, and the `#include()`-flattened Typst master's docname/page correlation. This is an
**audit-methodology** research phase, not a translator-code phase — no `typsphinx/` source is
touched.
**Confidence:** HIGH (every load-bearing claim below was verified by actually running the tooling
in this session against the real cached corpus, not just cited from docs)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Audit division of labor (human-assisted = Claude-first, human-confirmed)**
- **D-01: Claude does the first pass; the human confirms.** Claude renders the corpus PDF pages to
  images, reads them itself, cross-checks against the baseline, and builds a candidate-issue list.
  The human's role is confirming candidates and finalizing severity — not paging through hundreds
  of pages themself.
- **D-01a: The human confirms ALL candidates + spot-checks the "clean" set.** Every candidate is
  human-reviewed for accept/reject and severity. Additionally the human spot-checks a few pages
  Claude marked clean, to estimate the miss rate. This is the evidentiary bar for FID-01 (Phase 18
  work is scoped by these confirmations).
- **D-02: Progress is tracked per docname.** Audit progress ("audited / not yet") is recorded per
  document (.rst file), matching the catalogue's location key and giving clean session-resume
  boundaries. Expect the audit to span multiple sessions; the tracking artifact must survive
  interruption.
- **D-03: Uncertain cases go INTO the candidate list, flagged "uncertain."** When Claude cannot
  tell whether a divergence is an in-scope mis-render or an acceptable media difference, it
  includes the item as a flagged candidate for human judgment. Bias toward false positives, never
  silent false negatives.

**Comparison baseline**
- **D-04: The rendered HTML build is the authority; rST source is the tiebreaker.** "Faithful"
  means faithful to what Sphinx itself renders (post-toctree/xref-resolution, post-autodoc). Read
  the rST source only when intent needs confirming.
- **D-05: Build the HTML baseline locally from the SAME cached corpus.** `sphinx-build -b html`
  against `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc` (tag v9.1.0, SHA `cc7c6f4…`,
  the exact tree the PDF is built from — provenance per 15-CORPUS-REPORT.md). Never compare
  against www.sphinx-doc.org (version skew → false positives).
- **D-06: Divergence = content + structure + meaning-bearing style.** In scope: content
  loss/duplication/misordering; structural breakage (lists, tables, heading hierarchy); loss of
  meaning-bearing styling (literal/code text rendered as prose, lost emphasis, links flattened to
  plain text, table column misalignment). Out of scope: pure appearance differences (colors,
  fonts, margins, page breaks, theme chrome like sidebars/navigation) — these are expected
  PDF-vs-HTML media differences, not mis-renders.

**Catalogue format & severity rubric**
- **D-07: Catalogue = `17-AUDIT-CATALOGUE.md` in the phase directory** (the 15-CORPUS-REPORT.md
  precedent): a single committed Markdown with a provenance header (corpus tag/SHA, typst version,
  build command) + the issue records. Phase 18's planner reads it directly. No GitHub issues, no
  committed screenshots.
- **D-08: Severity rubric — the axis is "what does the reader lose":**
  - **high** (locked by SC#4): content lost, unreadable, or grossly mis-structured.
  - **medium**: content readable but meaning or distinction lost (code-literal rendered as prose,
    lost emphasis, link flattened to plain text, table column shift, …).
  - **low**: meaning intact but finish is sloppy (stray whitespace, indentation wobble, …).
- **D-09: Per-issue record = SC#2's required 3 fields + reproduction info.** Each issue records:
  docname + node kind; source-vs-output description; severity; PDF page number; occurrence count
  (same root cause); and a minimal reproducing rST snippet (or a pointer to the corpus source
  line). Phase 18 fix-plans and their regression fixtures start directly from the catalogue.

**FID-01 backlog granularity**
- **D-10: One FID-01x per ROOT CAUSE, not per occurrence.** The same translator defect appearing
  in N places is ONE requirement, with occurrence locations listed inside it. This matches Phase
  18's unit of work (handler-level fixes) and maps 1:1 to fix plans.
- **D-11: Only "high" issues become FID-01a…; medium/low go to Future Requirements.** The
  REQUIREMENTS.md append registers exactly the high-severity root causes as FID-01a, FID-01b, …
  (SC#4 as written). Medium/low stay fully recorded in the catalogue, referenced from
  REQUIREMENTS.md "Future Requirements" as a single pointer entry (next-milestone candidates) —
  v0.6.1 scope does not grow.

### Claude's Discretion
- PDF page-image extraction tooling and resolution (e.g. pdftoppm/mutool), and how pages are
  batched per session.
- Exact tabular schema/column layout of `17-AUDIT-CATALOGUE.md` and of the per-docname progress
  tracker (a checklist inside the catalogue or a sibling file — planner's choice, as long as it is
  committed and resumable, per D-02).
- How the HTML baseline build handles the corpus conf's doc-build-only extensions (same
  install-vs-degrade judgment Phase 15 already made for `typstpdf`; reuse its wiring approach).
- Any low-cost mechanical pre-filters (e.g. text-extraction diff) Claude uses internally to
  prioritize its own first pass — provided every page still gets a visual look (SC#1's
  page-by-page bar) and the D-01a confirmation flow is unchanged.

### Deferred Ideas (OUT OF SCOPE)
- **Medium/low fidelity fixes** — recorded in the catalogue and pointed to from Future
  Requirements (D-11), but NOT part of v0.6.1's Phase 18 obligation (high only, per SC#4).
- **Committed screenshot evidence per issue** — considered for the catalogue (D-07/D-09); rejected
  to keep the repo lean. Page numbers + repro snippets are the durable evidence; images stay
  session-local.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUD-01 | The compiled Sphinx-`doc/` corpus PDF is visually audited against the rendered HTML / rST source, and every silent mis-render issue found is catalogued with location (docname + node kind), a source-vs-output description, and a severity rating. | This document's PDF↔docname mapping (verified via `pypdf` outline + `#include()`-order walk), the verified `pdftoppm`/`mutool` rasterization path, the verified `-b html`/`-b text` baseline builds, and the Validation Architecture section (coverage/consistency checks the catalogue must satisfy before it is considered complete). |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **No new runtime or dev dependency is needed for this phase.** `pypdf>=6.14,<7` is already a dev
  dependency (`pyproject.toml` `[project.optional-dependencies].dev`) and is sufficient for both the
  docname/page mapping and the text-extraction pre-filter (verified below). Page **rasterization**
  (turning PDF pages into PNG images Claude can actually look at) has no pure-Python
  already-installed option — it requires an external CLI (`pdftoppm` or `mutool`), invoked ad hoc via
  `nix-shell -p poppler-utils` / `nix-shell -p mupdf` (verified working in this session), never added
  to `pyproject.toml`.
- **`typsphinx/` is not touched.** This phase's only artifacts are `17-AUDIT-CATALOGUE.md` and a
  `.planning/REQUIREMENTS.md` append. Any helper script written to execute the audit (mapping,
  pre-filter diff) is ephemeral/scratch tooling, not shipped package code, and is exempt from the
  `black`/`ruff`/`mypy` gates that apply to `typsphinx/*.py` — but if the planner chooses to commit
  such a script (e.g. under a new `scripts/` or `tests/`-adjacent location) it MUST follow the
  project's Python 3.10+ / `black`/`ruff`/`mypy` conventions like everything else in the repo.
- **The `@preview` version-sync hazard is inert for this phase** — no `writer.py` /
  `template_engine.py` / `templates/base.typ` changes occur, so `tests/test_preview_version_sync.py`
  is unaffected.
- **Reuse `tests/test_corpus_gate.py`'s helpers, don't reinvent them** (per CONTEXT.md canonical
  refs): `get_or_clone_corpus`, `wire_typsphinx_into_corpus_conf`, `_run_corpus_sphinx_build`
  (parameterized by builder name — `"typstpdf"`, `"html"`, and `"text"` all verified to work through
  it unmodified) are the correct integration points, not new subprocess plumbing.

## Summary

The three genuinely-open technical questions this phase depends on — page-image extraction
tooling, the HTML baseline build, and PDF↔docname mapping — were all resolved **empirically** in
this research session, against the real cached corpus, not assumed. `pdftoppm` (poppler-utils) and
`mutool` (mupdf-tools) are not on the sandbox `PATH` by default but both install and run cleanly via
`nix-shell -p poppler-utils` / `nix-shell -p mupdf` (network access to the NixOS binary cache is
available in this session). `pdftoppm -png -r 150` produces legible, right-sized (~180–250 KB/page)
PNG output — confirmed by actually reading a rendered page back through the `Read` tool. The `-b
html` baseline build was run end-to-end against the SAME cached corpus tree reusing
`test_corpus_gate.py`'s helpers unmodified (parameterizing the existing `builder` argument), and it
independently reproduced the exact same doc-build-only-extension degradations (missing `dot`,
missing `sphinxcontrib.websupport`) that REQUIREMENTS.md's Out-of-Scope table already excludes —
confirming Phase 15's install-vs-degrade judgment transfers to `-b html` without new work. The
PDF↔docname/page mapping does not need OCR or fuzzy text matching: Typst headings are
bookmarked-in-the-PDF-outline by default, and the compiled master `.typ`'s `#include()` call order
IS the toctree DFS order IS the PDF's page order — combining a recursive `include()` walk with
`pypdf`'s outline API gives an exact, mechanical page-range per docname. A pure-`pypdf`
(`page.extract_text()`, already a dev dependency) or Sphinx's built-in `-b text` builder (one `.txt`
per docname, zero mapping work needed) both work as fast, zero-new-tooling mechanical pre-filters to
prioritize the mandatory page-by-page visual pass — neither replaces it, per CONTEXT.md's
discretion note.

**Primary recommendation:** Build the PDF via the reused `typstpdf` corpus-gate helpers, build the
HTML (authority, D-04/D-05) and `-b text` (pre-filter source) baselines from the SAME cached corpus
tree via the same helpers, derive an exact docname→page-range table from `pypdf`'s outline API
combined with a recursive walk of the master `.typ`'s `#include()` order, use `pypdf.extract_text()`
per page range as a zero-new-tooling mechanical pre-filter to prioritize the visual pass, then
rasterize each docname's page range with `nix-shell -p poppler-utils -- pdftoppm -png -r 150` into a
session-scratch directory (never committed) and read the pages via the `Read` tool docname-by-docname,
checking off progress as you go (D-02) — before writing/updating `17-AUDIT-CATALOGUE.md`.

## Architectural Responsibility Map

This project has no browser/API/CDN tiers (it is a Sphinx builder extension); the map below uses
the project's actual pipeline stages instead.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PDF compilation (source of truth for what to audit) | `typsphinx` translator/writer + `typst-py` (`typsphinx/pdf.py`) | — | Already built by Phase 11–16; this phase only *consumes* the compiled artifact, never modifies the compile path. |
| HTML baseline (D-04 authority) | Sphinx core `-b html` builder | — | Runs against the exact same cached corpus/conf; typsphinx's `extensions.append('typsphinx')` wiring is inert for this builder. |
| Text pre-filter source | Sphinx core `-b text` builder / `pypdf.extract_text()` | — | Neither is authoritative (D-04 fixes HTML as authority) — both are internal, disposable triage aids only. |
| Page rasterization (PDF → viewable images) | External CLI (`pdftoppm`/`mutool`, via `nix-shell`) | — | No pure-Python rasterizer is already a project dependency; this is audit-only tooling, never a shipped/runtime dependency. |
| Docname↔page mapping | `pypdf` (PDF outline API) + master `.typ` `#include()`-order walk | — | Mechanical, exact — no OCR/heuristic needed for the mapping itself. |
| Visual comparison judgment (SC#1/SC#2) | Claude (first pass, D-01) → Human (confirmation, D-01a) | — | Locked by CONTEXT.md; not automatable — this is the phase's actual "work." |
| Catalogue + FID-01x backlog authorship | Phase-directory Markdown artifact (`17-AUDIT-CATALOGUE.md`) + `.planning/REQUIREMENTS.md` append | — | No code; the phase's entire output surface (D-07). |

## Standard Stack

### Core

| Tool | Version (verified this session) | Purpose | Why Standard |
|------|-----------------------------------|---------|---------------|
| `pypdf` | 6.14.2 `[VERIFIED: already in pyproject.toml dev extra, imported successfully]` | Read compiled PDF's page count, outline/bookmarks (docname→page mapping), and per-page text (pre-filter) | Already a project dev dependency (`tests/test_pdf_render_gate.py` lineage); zero new install. |
| `sphinx-build -b html` | Sphinx 9.1.0 (installed) `[VERIFIED: ran successfully this session, returncode 0, "build succeeded, 36 warnings"]` | D-05's HTML baseline (comparison authority) | Built-in Sphinx builder; reuses the exact corpus/conf `test_corpus_gate.py` already wires. |
| `sphinx-build -b text` | Sphinx 9.1.0 (installed) `[VERIFIED: ran successfully this session, returncode 0, "build succeeded, 35 warnings", one .txt per docname]` | Optional pre-filter source (plain reading-order text, pre-split by docname — no page-mapping step needed) | Built-in Sphinx builder; not the authority (D-04 fixes HTML as authority) — internal triage aid only. |
| `pdftoppm` (poppler-utils) | 26.06.0 `[VERIFIED: nix-shell -p poppler-utils -- pdftoppm -v, this session]` | Rasterize PDF page ranges to PNG for Claude's visual pass | Matches Adobe/most PDF viewers' rendering (Poppler is the reference renderer most desktop tools embed); cleanest/fastest CLI of the two candidates. |
| `mutool draw` (mupdf-tools) | 1.27.2 `[VERIFIED: nix-shell -p mupdf -- mutool -v, this session]` | Fallback rasterizer if `pdftoppm`/poppler-utils is unavailable in a given session | Same job, different renderer; default DPI is lower (72 vs pdftoppm's 150) so `-r 150` (or equivalent) must be passed explicitly if used. |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `nix-shell -p poppler-utils` / `nix-shell -p mupdf` | n/a (Nix ad hoc shell) | Obtain `pdftoppm`/`pdftotext` or `mutool` without a permanent system/project install | Every session, since neither is pre-installed on `PATH` in this sandbox — verified this session; `nix-shell -p poppler_utils` (underscore) is a **stale/wrong attribute name** (`error: 'poppler_utils' has been renamed to/replaced by 'poppler-utils'`) — use the hyphenated form. |
| `git worktree` | n/a | NOT needed for this phase (no translator revert like Phase 15's XREF-01 before/after) | N/A — listed only to note it is out of scope here, unlike Phase 15. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pdftoppm` (poppler) | `mutool draw` (mupdf) | Both verified working; `mutool`'s default DPI (72) is much lower than `pdftoppm`'s (150), so an explicit `-r`/resolution flag is mandatory with `mutool` where it's optional (already-sane default) with `pdftoppm`. Prefer `pdftoppm` unless it's unavailable in a given execution session. |
| `pdftoppm`/`mutool` (external CLI, needs `nix-shell`) | Python `pdf2image` / `PyMuPDF` (`fitz`) | Both `[ASSUMED — not verified this session]` `pdf2image`/`PyMuPDF` are NOT installed (`ImportError` confirmed for both, plus `PIL`) and would require adding a new dev dependency — rejected: the milestone invariant favors zero new deps, and the ad hoc `nix-shell -p poppler-utils` path already works with no `pyproject.toml` change. |
| Manual/eyeballed docname→page mapping | `pypdf` outline API + `#include()`-order walk | Manual guessing under D-02's per-docname resumability requirement would be slow and error-prone across a 684-page, 154-docname corpus; the mechanical mapping is exact and nearly free (already-installed `pypdf`). |
| `pdftotext`-based pre-filter | `pypdf.extract_text()` or Sphinx `-b text` | `pdftotext -layout` (verified, clean output) needs `nix-shell`; both alternatives need zero extra tooling (`pypdf` already installed, `-b text` is Sphinx built-in) — prefer one of those two unless `pypdf`'s text extraction proves unreliable on a specific page's layout (e.g. dense tables), in which case fall back to `pdftotext -layout` for that page only. |

**Installation:** None required — no `pyproject.toml` change. Ad hoc tool acquisition per session:
```bash
nix-shell -p poppler-utils --run "pdftoppm -png -r 150 -f <start> -l <end> index.pdf out/page"
# or, if poppler-utils is unavailable in a given session:
nix-shell -p mupdf --run "mutool draw -o out/page-%d.png -r 150 index.pdf <start>-<end>"
```

**Version verification:** All versions above were verified directly in this research session
(`pdftoppm -v`, `pdftotext -v`, `mutool -v`, `python -c "import pypdf; print(pypdf.__version__)"`,
`python -c "import importlib.metadata as m; print(m.version('typst'))"` → `0.15.0`) — not looked up
from training data or a registry search.

## Package Legitimacy Audit

**Not applicable.** This phase adds zero packages to `pyproject.toml` (no `npm`/`pip install`
anywhere in scope). The only "new" tools used (`pdftoppm`/`pdftotext` from `poppler-utils`, `mutool`
from `mupdf`) are system/Nix packages fetched ad hoc via `nix-shell -p <name>` for the duration of a
single audit command — never installed into the Python project's dependency tree, never a runtime or
dev dependency of the shipped `typsphinx` package. The Package Legitimacy Gate (npm/PyPI/crates
registry-slopsquat checking) does not apply to Nix system packages and is skipped.

**Packages removed due to [SLOP] verdict:** none (N/A — no packages evaluated).
**Packages flagged as suspicious [SUS]:** none (N/A).

## Architecture Patterns

### System Architecture Diagram

```
Sphinx doc/ corpus (cached, pinned v9.1.0, SHA cc7c6f4...)
        |
        |-- sphinx-build -b typstpdf --> .typ files + index.pdf (already-shipped pipeline;
        |                                 this phase only CONSUMES this output)
        |
        |-- sphinx-build -b html     --> per-docname .html files   (D-04/D-05 AUTHORITY baseline)
        |
        `-- sphinx-build -b text     --> per-docname .txt files    (optional pre-filter source,
                                          NOT the authority)

index.pdf
        |-- pypdf: PdfReader(...).pages           --> page count (684, verified)
        |-- pypdf: PdfReader(...).outline         --> nested bookmarks, resolvable to page numbers
        |                                              via get_destination_page_number()
        |-- (recursive #include() walk of index.typ) --> linear docname sequence (toctree DFS order)
        |
        `-- COMBINE outline + include()-order  --> exact docname -> [start_page, end_page] table
                    |
                    |-- pypdf.extract_text() per page range   --\
                    |                                            >-- mechanical PRE-FILTER (triage
                    `-- vs. per-docname -b text .txt content  --/    only, never skips a page)
                    |
                    `-- pdftoppm -r 150 (per docname page range) --> session-scratch PNG images
                                |
                                `-- Claude reads PNGs (Read tool) page-by-page (SC#1)
                                        |
                                        `-- cross-check against docname's .html (D-04 authority),
                                            fall back to .rst source only to confirm intent (D-04)
                                                |
                                                |-- clean --> mark docname audited (D-02 progress)
                                                `-- divergence found --> candidate issue
                                                        (bias false-positive, flag "uncertain" per D-03)
                                                                |
                                                                `-- classify against REQUIREMENTS.md
                                                                    Out-of-Scope table (SC#3)
                                                                            |
                                        candidates ---------------> human confirms + sets severity (D-01a)
                                                                            |
                                        17-AUDIT-CATALOGUE.md <-------------+
                                                |
                                                `-- "high" root causes --> REQUIREMENTS.md append
                                                    (FID-01a, FID-01b, ... one per ROOT CAUSE, D-10)
                                                    "medium"/"low" --> Future Requirements pointer (D-11)
```

### Recommended Project Structure

No `typsphinx/` source changes. Phase-directory artifacts only:

```
.planning/phases/17-rendering-fidelity-audit/
├── 17-CONTEXT.md              # already exists (input to this research)
├── 17-RESEARCH.md             # this file
├── 17-AUDIT-CATALOGUE.md      # THE deliverable (D-07): provenance header + issue records
│                                 + an embedded per-docname progress checklist section (D-02) --
│                                 recommended as ONE file, not a sibling, to keep D-07's "single
│                                 committed Markdown" framing literal; a sibling
│                                 17-AUDIT-PROGRESS.md is equally valid per CONTEXT.md discretion
│                                 if the planner prefers to keep the catalogue itself lean.
└── 17-01-PLAN.md / 17-01-SUMMARY.md  # standard GSD plan/summary artifacts
```

Ephemeral, NEVER committed (per the "no committed screenshots" deferred decision):
```
<scratch-dir>/17-audit/
├── corpus_pdf_build/     # sphinx-build -b typstpdf output (index.pdf + per-docname .typ)
├── corpus_html_build/    # sphinx-build -b html output (D-04 authority)
├── corpus_text_build/    # sphinx-build -b text output (optional pre-filter source)
└── page_images/          # pdftoppm/mutool PNG output, batched per docname, deleted after review
```

### Pattern 1: Reuse `_run_corpus_sphinx_build`'s builder parameter, don't reinvent it

**What:** `tests/test_corpus_gate.py::_run_corpus_sphinx_build(builder, source_dir, build_dir, env=None)`
already accepts an arbitrary `builder` string and drives `sys.executable -m sphinx -b <builder> ...`
as a subprocess (sidestepping the documented `uv run <compiled-binary>` NixOS PATH hazard).
**When to use:** For all three builds this phase needs (`typstpdf`, `html`, `text`) — verified this
session that `"html"` and `"text"` both work through this exact function, unmodified, with no new
plumbing.
**Example (verified this session):**
```python
# Source: tests/test_corpus_gate.py (reused, not modified)
import sys
sys.path.insert(0, "tests")
import test_corpus_gate as tcg
from pathlib import Path

cache_root = Path.home() / ".cache" / "typsphinx-corpus-gate"
doc_dir = tcg.get_or_clone_corpus(cache_root)          # cached, no re-clone
tcg.wire_typsphinx_into_corpus_conf(doc_dir)             # idempotent

pdf_out  = tcg._run_corpus_sphinx_build("typstpdf", doc_dir, Path("<scratch>/corpus_pdf_build"))
html_out = tcg._run_corpus_sphinx_build("html",     doc_dir, Path("<scratch>/corpus_html_build"))
text_out = tcg._run_corpus_sphinx_build("text",     doc_dir, Path("<scratch>/corpus_text_build"))
# All three verified returncode == 0 this session.
```

### Pattern 2: Docname→page-range mapping via PDF outline + `#include()`-order walk

**What:** Typst headings default to `outlined: true` (and therefore `bookmarked: auto` → bookmarked)
unless a call site explicitly overrides it. Grepping `typsphinx/templates/base.typ` and
`typsphinx/translator.py` confirms only the toctree-caption heading uses `outlined: false`; every
content heading (`visit_title`'s `heading(level:, ...)` call) uses the (bookmarked) default. This
means every section heading in the compiled PDF has a resolvable page number via `pypdf`'s outline
API — verified this session: 276 nested bookmark entries were extracted from the 684-page corpus PDF,
each resolving to an exact page via `reader.get_destination_page_number(item)`.

Separately, the compiled master `.typ` (e.g. `index.typ` for this corpus, `typst_documents`'s source
docname) contains `include("relative/path.typ")` lines in exactly Sphinx's toctree DFS order —
verified this session (`grep -n "#include(" index.typ` → ordered list matching the corpus's toctree
structure). Nested toctrees mean a doc's own `.typ` file (e.g. `usage/index.typ`) contains further
`include(...)` calls for ITS children — a full recursive walk from the master reconstructs the
complete linear docname sequence, which is exactly the linear order Typst lays content out in the
PDF.

**When to use:** Before starting the visual pass, to convert D-02's "per docname" progress tracking
into concrete PDF page ranges.
**Example:**
```python
# Source: verified this session against ~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0
import pypdf

reader = pypdf.PdfReader("index.pdf")
print(len(reader.pages))       # 684 (verified this session)

outline = reader.outline        # nested list of pypdf.generic.Destination + sub-lists
def walk(items):
    for item in items:
        if isinstance(item, list):
            yield from walk(item)
        else:
            yield item.title, reader.get_destination_page_number(item)

for title, page in list(walk(outline))[:5]:
    print(title, "-> page", page)
# '2 Sphinx' -> page 15
# '2.1 Get started' -> page 17
# '3 Installing Sphinx' -> page 17
# ...
```
The `include("...")` order (from the master `.typ`, recursively) supplies the docname for each
heading-encounter-order slot; the first heading encountered for a given docname is its start page,
the next docname's start page (minus 1) is its end page.

### Pattern 3: Zero-new-tooling text pre-filter (Claude's Discretion)

**What:** Both `pypdf.extract_text()` (per page, already installed) and Sphinx's built-in `-b text`
builder (one clean `.txt` per docname, no page-mapping step needed at all) produce legible,
reading-order plain text with no new tooling. Verified this session on a real corpus page:
```
Tip
When using docker images, please use docker run command to invoke sphinx
commands.  For example, you can use following command to create a Sphinx
project:
$ docker run -it --rm -v /path/to/document:/docs sphinxdoc/sphinx
sphinx-quickstart console
...
```
**When to use:** As an internal triage aid ONLY — diff a docname's `-b text` output (or its PDF page
range's `pypdf.extract_text()`) against a normalized-whitespace version of the same docname's HTML
baseline text (D-04 stays the authority; text-diffing is never itself the judgment). Large diffs get
priority in the visual pass; near-zero diffs still get the mandatory SC#1 visual look, just possibly
a faster skim — this must never substitute for looking at the actual page image.

### Anti-Patterns to Avoid

- **Guessing docname→page boundaries by eyeballing the PDF's table of contents (`#outline()`
  in-body page) instead of `pypdf`'s programmatic outline API.** The in-body outline page is
  rendered *content* (page numbers as text, subject to the same layout/wrapping the audit is
  checking) — the PDF **viewer bookmark** structure (`reader.outline`) is structural PDF metadata,
  exact and unambiguous.
- **Committing rasterized page images or a rebuilt PDF to git.** Explicitly rejected in CONTEXT.md's
  Deferred Ideas — keep all image/PDF-build artifacts in a scratch directory outside the repo.
- **Treating the text pre-filter's silence as "audited."** A docname with a near-zero text diff still
  needs its pages opened and read (SC#1's literal wording is page-by-page, not "diff-guided
  sampling") — the pre-filter changes review ORDER/SPEED, not review COVERAGE.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF page rasterization | A custom PDF-parsing/rendering routine | `pdftoppm` (poppler) or `mutool draw` (mupdf), both verified installable via `nix-shell` | PDF rendering (fonts, embedded images, layout) is a solved, hard problem; poppler/mupdf are the reference implementations most tools embed. |
| PDF outline/bookmark extraction | Manual regex over raw PDF bytes | `pypdf.PdfReader(...).outline` + `get_destination_page_number()` | Already-installed, well-tested library; the PDF outline/destinations object model has real structural nuance (nested lists, named vs. explicit destinations) not worth reimplementing. |
| HTML/text corpus baseline | Re-parsing the corpus's `.rst` source by hand | `sphinx-build -b html` / `-b text` (the same Sphinx already installed) | Sphinx's own builders already resolve toctrees, autodoc, cross-references, intersphinx — exactly the "post-resolution" state D-04 requires as the authority; hand-parsing rST would silently diverge from what Sphinx itself renders. |

**Key insight:** Every tool this phase needs (`pypdf`, `sphinx-build -b html/text`, `pdftoppm`/
`mutool` via `nix-shell`) already exists, is already verified working against the real corpus, and
requires zero new project dependencies — the temptation to hand-roll would only be to avoid the
`nix-shell` step, which is a false economy (an ad hoc shell invocation vs. reimplementing a PDF
rasterizer).

## Common Pitfalls

### Pitfall 1: Blowing the session/context budget with one giant 684-page dump

**What goes wrong:** Rasterizing and reading all 684 pages in one batch produces ~150 MB of PNGs
(verified: ~180–250 KB/page at 150 DPI × 684 pages) and floods a single session's context.
**Why it happens:** The corpus is large (154 docnames, 684 pages) and D-01 assigns Claude the full
first pass.
**How to avoid:** Batch strictly per docname (or small docname groups within one toctree subtree),
matching D-02's per-docname progress unit exactly — rasterize only the page range for the docname(s)
being reviewed in this session slice, review, mark progress, delete that batch's images, move on.
**Warning signs:** A single `pdftoppm` invocation covering more than ~20–30 pages at once, or image
files accumulating in the scratch directory across multiple docnames without cleanup.

### Pitfall 2: Assuming heading-encounter order in the outline always exactly matches
`#include()` order without cross-checking

**What goes wrong:** A docname with unusual structure (e.g. content before its first heading, or a
heading with `outlined: false` somewhere unexpected) could shift the naive "Nth heading = Nth
docname" alignment by one, silently misattributing a page range to the wrong docname.
**Why it happens:** The mapping in Pattern 2 assumes a 1:1 correspondence between "first heading
encountered" and "docname boundary," which holds for the vast majority of docs (title heading is
always first) but should be spot-checked, not blindly trusted for all 154 docnames.
**How to avoid:** After building the mapping table, spot-check a handful of entries (start of corpus,
middle, end, and any doc with a caption-only toctree page) by opening that exact page and confirming
the visible content matches the expected docname's title/opening content.
**Warning signs:** A docname's mapped page range that looks implausibly short/long relative to its
`.rst` file's line count, or a docname whose mapped start page shows a DIFFERENT doc's title text.

### Pitfall 3: Re-litigating D-05/D-06 by comparing against an internet-hosted Sphinx
version or flagging pure-appearance differences

**What goes wrong:** Comparing against `www.sphinx-doc.org` (a different, possibly newer Sphinx
version's rendering) or flagging PDF-vs-HTML page-break/font/color/sidebar differences as "issues"
produces false positives that both waste human confirmation time (D-01a) and pollute the FID-01
backlog with non-bugs.
**Why it happens:** These are the two most tempting shortcuts (internet lookup is faster than a
local build; visual differences ARE visually obvious even when explicitly out of scope).
**How to avoid:** D-05/D-06 already lock the answer — always diff against the SAME cached corpus's
local `-b html` build, and mentally filter page-break/font/color/theme-chrome differences before
even considering them "candidates."
**Warning signs:** Any catalogue entry whose "source-vs-output description" is purely about color,
font, margin, or page-break placement with no content/structure/meaning-bearing-style component.

### Pitfall 4: Misinterpreting the graphviz/`dot`-missing placeholder as a finding

**What goes wrong:** Verified this session: `dot` is not installed, so BOTH the `-b html` and `-b
typstpdf` builds independently degrade graphviz/inheritance-diagram nodes to the same graceful-degrade
placeholder (a `WARNING: dot コマンド 'dot' は実行できません` build warning, non-fatal). Because both
builds show "the same placeholder," it might look like a matched/clean comparison worth confirming —
but any graphviz/inheritance-diagram-related divergence at all is REQUIREMENTS.md Out-of-Scope
("intentional graceful-degrade placeholder is working as designed (DEG-01/DEG-02); real rendering is
DEG-03 (future)") and should not even enter the candidate list, regardless of what it looks like on
either side.
**Why it happens:** `dot` is absent from this environment, so the audit will encounter this pattern
repeatedly across the corpus's several graphviz-using docs.
**How to avoid:** Pre-classify graphviz/inheritance_diagram nodes as out-of-scope BEFORE the visual
pass (they're identifiable by docname/node-kind from the corpus's known extension list), not during
it.
**Warning signs:** A candidate issue whose docname touches `usage/extensions/graphviz.rst` or any
`.. graphviz::`/`.. inheritance-diagram::` directive.

### Pitfall 5: Confusing Sphinx's locale-dependent CLI/log output for document content

**What goes wrong:** Verified this session: with the current locale, `sphinx-build`'s own progress
messages print in Japanese ("モジュールコードをハイライトしています…", "画像をコピー中…") — this is
Sphinx's own UI/log text, not corpus document content, and has zero bearing on the audit.
**Why it happens:** Locale-driven Sphinx UI strings are unrelated to (and easily confused with) the
actual corpus content being audited, especially when skimming build logs for warnings.
**How to avoid:** Only parse `WARNING:`/`ERROR:`-prefixed lines (matching the existing
`UNKNOWN_NODE_RE`/`EMPTY_URL_SIGNATURE` patterns in `test_corpus_gate.py`) for build-diagnostic
purposes; ignore all other stdout/stderr as locale-dependent build-progress noise.
**Warning signs:** None expected to affect the catalogue directly — noted here purely so a future
executor doesn't waste time investigating Japanese text in a build log as if it were a rendering bug.

### Pitfall 6: One FID-01x per occurrence instead of per root cause (violates D-10)

**What goes wrong:** If the same translator defect (e.g. a specific node-kind mishandling) surfaces
in 8 different docnames, writing 8 separate `FID-01a`...`FID-01h` entries balloons Phase 18's scope
and breaks the 1:1 mapping to "handler-level fixes" D-10 requires.
**Why it happens:** The catalogue naturally accumulates one row per PAGE where an issue is spotted;
without deliberate grouping, that maps to "one row = one requirement" by default.
**How to avoid:** Before appending to REQUIREMENTS.md, group catalogue rows by root cause (same node
kind + same failure mode), emit exactly one `FID-01x` per group, and list every occurrence's
docname/page inside that single entry (per D-09's "occurrence count" field).
**Warning signs:** More `FID-01x` entries than distinct node kinds/failure modes observed in the
"high" severity rows.

### Pitfall 7: Recording stale provenance numbers from Phase 15's report instead of this
phase's own fresh build

**What goes wrong:** Verified this session: rebuilding the corpus PDF today (with Phase 16's
`todo_node`/`manpage` handlers landed) produces `15,153,646` bytes, NOT Phase 15's `15,124,122` bytes
(a `+29,524` byte delta — consistent with content that now renders instead of being silently
dropped). Copying Phase 15's byte count into the D-07 provenance header would be factually wrong for
THIS phase's actual audited artifact.
**Why it happens:** 15-CORPUS-REPORT.md is the nearest precedent and its numbers are easy to
copy-paste without re-measuring.
**How to avoid:** Record the CURRENT session's own build's PDF size/page-count/warning-count in
`17-AUDIT-CATALOGUE.md`'s provenance header — reuse the corpus tag/SHA (those genuinely ARE
unchanged, verified: still `v9.1.0` / `cc7c6f435ad37bb12264f8118c8461b230e6830c`) but re-measure the
PDF's own byte size and the `unknown_visit` catalogue (should be EMPTY now, confirming Phase 16
landed — also re-verified this session: the corpus PDF gate test passed with the empty-catalogue
assertion).

## Code Examples

### Reuse the corpus-gate clone/wiring helpers (verified this session)
```python
# Source: tests/test_corpus_gate.py (import and reuse, do not duplicate)
import sys
sys.path.insert(0, "tests")
import test_corpus_gate as tcg
from pathlib import Path

cache_root = Path.home() / ".cache" / "typsphinx-corpus-gate"
doc_dir = tcg.get_or_clone_corpus(cache_root)   # returns cached path, no re-clone
tcg.wire_typsphinx_into_corpus_conf(doc_dir)    # idempotent conf.py append
tag = tcg.resolve_corpus_tag()                  # "v9.1.0"
```

### Rasterize a docname's page range (verified this session, poppler-utils 26.06.0)
```bash
nix-shell -p poppler-utils --run \
  "pdftoppm -png -r 150 -f 20 -l 22 index.pdf page_images/page"
# produced page-020.png (181472 bytes), page-021.png (244666 bytes), page-022.png (251296 bytes)
```

### Extract a docname's page range as plain text with pypdf (verified this session)
```python
# Source: pypdf 6.14.2, already installed, no new dependency
import pypdf
reader = pypdf.PdfReader("index.pdf")
text = reader.pages[20].extract_text()
# Clean, reading-order text: "Tip\nWhen using docker images, please use docker run..."
```

## State of the Art

| Old Approach (Phase 15's warning-based discovery) | Current Approach (Phase 17) | When Changed | Impact |
|-----------------------------------------------------|------------------------------|---------------|--------|
| Catalogue `unknown_visit` WARNING-level drops (nodes with no handler at all) | Visually audit the compiled PDF for SILENT divergence (nodes that DO have a handler but render wrong/incompletely, emitting no warning) | This phase (v0.6.1's stated milestone shift) | Warnings can no longer be the discovery signal — the audit is the only remaining discovery mechanism for this class of bug. |

**Deprecated/outdated:** None — this is the first phase of its kind in the project; there is no
prior "rendering fidelity audit" methodology in this repo to supersede.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pdf2image`/`PyMuPDF` (`fitz`) are viable alternative rasterizers if `nix-shell`/poppler/mupdf become unavailable in a future execution session | Standard Stack, Alternatives Considered | LOW — confirmed NOT currently installed (`ImportError` verified); if `nix-shell` access is lost in a future session, the planner would need to either add one of these as a genuinely new dev dependency (against the milestone's zero-new-deps spirit for a one-off audit tool) or find another rasterization path. Flag for human confirmation only if `nix-shell -p poppler-utils`/`nix-shell -p mupdf` fail in the actual execution session. |
| A2 | Nix binary-cache network access (verified working in THIS research session) will also be available in the phase's actual execution session | Standard Stack, Environment Availability | MEDIUM — if the execution session has no network access to `cache.nixos.org`, `nix-shell -p poppler-utils`/`-p mupdf` will hang or fail; the executor should verify this at the start of Phase 17's actual work (a fast `nix-shell -p poppler-utils --run "pdftoppm -v"` smoke check) before committing to the rasterization plan, and fall back to running that step outside the sandbox if it fails. |

## Open Questions

1. **Exact catalogue/progress-tracker file split (embedded section vs. sibling file).**
   - What we know: CONTEXT.md leaves this fully to the planner's discretion; D-07 literally says "a
     single committed Markdown," which slightly favors embedding the progress tracker as a section
     inside `17-AUDIT-CATALOGUE.md` rather than a sibling `17-AUDIT-PROGRESS.md`.
   - What's unclear: Whether a 154-docname progress checklist embedded in the same file as the issue
     records will make the catalogue unwieldy to edit incrementally across many sessions (D-02 implies
     multi-session editing).
   - Recommendation: Default to ONE file (matches D-07's literal wording); if the planner's execution
     experience shows the combined file becoming unwieldy mid-audit, splitting to a sibling file is an
     explicitly sanctioned discretion-level change, not a scope violation.

2. **Whether the mechanical text pre-filter is worth the implementation cost given the corpus is
   "only" 684 pages / 154 docnames.**
   - What we know: The mandatory visual pass (SC#1) already requires opening every page regardless of
     what the pre-filter says — the pre-filter only affects REVIEW ORDER/SPEED, never coverage.
   - What's unclear: Whether writing and running a text-diff pre-filter script actually saves net time
     versus just working through docnames in toctree order without it, for a corpus this size (as
     opposed to a much larger one where triage would matter more).
   - Recommendation: Treat the pre-filter as fully optional (already Claude's Discretion per
     CONTEXT.md) — the planner may choose to skip it entirely and go straight to ordered page-by-page
     review without materially violating any locked decision.

## Environment Availability

| Dependency | Required By | Available (this session) | Version | Fallback |
|------------|--------------|----------------------------|---------|----------|
| Cached Sphinx `doc/` corpus (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`) | The entire audit (source of the PDF/HTML/text builds) | ✓ (verified: tag `v9.1.0`, SHA `cc7c6f435ad37bb12264f8118c8461b230e6830c`, unchanged from Phase 15) | v9.1.0 | Re-clone via `tcg.get_or_clone_corpus` (needs network to `github.com/sphinx-doc/sphinx`) if the cache is ever cleared. |
| `typst-py` (real `typst.compile()`) | Building `index.pdf` via `-b typstpdf` | ✓ (verified: `import typst` succeeds, `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` PASSED in 13.63s, fresh `index.pdf` = 15,153,646 bytes / 684 pages, `unknown_visit` catalogue is EMPTY confirming Phase 16 landed) | 0.15.0 | None needed — working in this session. If a future session's sandbox is in the ELF-exec-broken state (see project memory `nixos-sandbox-test-env.md`), run the build outside the sandbox instead. |
| `sphinx-build -b html` | D-05 baseline | ✓ (verified: returncode 0, "build succeeded, 36 warnings") | Sphinx 9.1.0 | None needed. |
| `sphinx-build -b text` | Optional pre-filter source | ✓ (verified: returncode 0, "build succeeded, 35 warnings", one `.txt` per docname) | Sphinx 9.1.0 | None needed; or skip the pre-filter entirely (fully optional per CONTEXT.md discretion). |
| `pypdf` | Page count, outline/bookmark mapping, `extract_text()` pre-filter | ✓ (verified: 6.14.2, already a dev dependency) | 6.14.2 | None needed. |
| `pdftoppm`/`pdftotext` (poppler-utils) | Page rasterization (primary), text pre-filter (alternative) | ✓ via `nix-shell -p poppler-utils` (verified: 26.06.0; NOT on default `PATH`) | 26.06.0 | `mutool draw` (mupdf-tools), also verified available this session. |
| `mutool` (mupdf-tools) | Page rasterization (fallback rasterizer) | ✓ via `nix-shell -p mupdf` (verified: 1.27.2; NOT on default `PATH`) | 1.27.2 | `pdftoppm` (primary; prefer it — sane default DPI). |
| `dot` (graphviz) | NOT required by this phase | ✗ (confirmed absent — `which dot` empty) | — | None needed — graphviz/inheritance-diagram nodes are entirely REQUIREMENTS.md Out-of-Scope (DEG-01/DEG-02/DEG-03); their placeholder rendering is not something this audit should even attempt to evaluate. |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:**
- `pdftoppm`/`pdftotext`/`mutool` are not pre-installed on `PATH` — both install via `nix-shell -p
  <name> --run "<command>"` ad hoc (verified working this session, network access to
  `cache.nixos.org` confirmed present). If a future execution session lacks that network access,
  page rasterization must move outside the sandbox (matching the same "full local env" fallback the
  phase description already anticipates for the corpus builds themselves) — but note this research
  session found the corpus BUILDS (`typstpdf`/`html`/`text`) and the rasterization tooling BOTH
  working in-sandbox, which is a materially different (better) starting position than the phase
  description's stated assumption. Re-verify sandbox state with a quick smoke check
  (`nix-shell -p poppler-utils --run "pdftoppm -v"` + the corpus PDF gate test) at the start of Phase
  17's actual execution session, since the project's own memory notes the sandbox's ELF-exec
  restriction is a togglable, session-dependent state, not a fixed property of this repo.

## Validation Architecture

This phase produces a Markdown artifact via human-assisted visual review, not code exercised by
`pytest` — there is no traditional unit-test framework applicable to "is this catalogue correct."
Validation instead means a small set of **mechanically checkable consistency/coverage properties**
the finished `17-AUDIT-CATALOGUE.md` (and its REQUIREMENTS.md append) must satisfy, plus the
CONTEXT.md-mandated human spot-check. These are lightweight enough to run as ad hoc shell/Python
checks (or a short throwaway script), not a pytest suite — no new test framework is needed or
recommended.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None (artifact-based phase — see rationale above) |
| Config file | n/a |
| Quick run command | Ad hoc consistency checks (see table below), each independently runnable |
| Full suite command | Re-run all consistency checks below + the existing `tests/test_corpus_gate.py::TestCorpusRenderGate` (confirms the audited PDF is still the current, fatal-free, empty-`unknown_visit`-catalogue build before finalizing the catalogue's provenance header) |

### Phase Requirements → Validation Map
| Req/SC | Behavior | Check Type | Mechanical Check | Automatable? |
|--------|----------|------------|-------------------|---------------|
| SC#1 | Every page of the compiled PDF was visually compared | Coverage check | Per-docname progress tracker (D-02) shows every docname from the corpus's actual toctree closure as "audited," none left "not yet" | Yes — compare the tracker's docname list against `builder.master_included_docnames` (or a fresh recursive `#include()` walk) for set equality. |
| SC#2 | Every catalogued issue has docname + node kind, source-vs-output description, and severity | Schema/completeness check | Every row in `17-AUDIT-CATALOGUE.md`'s issue table has all D-09 required fields non-empty | Yes — a short script/grep asserting no table row has a blank required column. |
| SC#3 | Out-of-scope degradations are excluded from the catalogue | Classification check | No catalogue row's docname/node-kind matches a known Out-of-Scope signature (graphviz/inheritance_diagram nodes, non-included-doc xref targets, `py:meth`/autodoc-import warning text) | Yes — grep the catalogue for the known out-of-scope node kinds/warning substrings; any match is a scope violation needing removal. |
| SC#4 | Every "high" issue is enumerated as FID-01a…, one per ROOT CAUSE (D-10) | Backlog-generation check | Count of distinct `FID-01x` entries appended to REQUIREMENTS.md equals the count of distinct root-cause GROUPS among "high" severity catalogue rows (not the raw row/occurrence count) | Yes — count `FID-01[a-z]+` matches in REQUIREMENTS.md vs. count of distinct (node-kind, failure-mode) groups among high-severity catalogue rows. |
| D-01a | Human confirmed every candidate + spot-checked the clean set | Human sign-off + miss-rate estimate | Catalogue records the spot-check sample size and any misses found (miss-rate = misses / sample size) | No — inherently human; the catalogue should just RECORD the outcome so it's auditable later. |
| D-07 | Provenance header matches THIS session's actual build, not stale Phase 15 numbers | Freshness check | Catalogue's provenance header's PDF byte size / page count / corpus SHA match a fresh `test_corpus_gate.py`-driven rebuild done at catalogue-finalization time | Yes — re-run the corpus PDF gate test and diff its reported size against the header (see Pitfall 7). |

### Sampling Rate
- **Per docname reviewed:** Update the progress tracker (D-02) immediately; no batch-deferred updates
  (multi-session resumability depends on this being current at all times, not just at phase end).
- **Per session:** Re-verify the environment smoke check (corpus build + rasterization tooling both
  still working) before resuming — the sandbox's real-compile capability is session-state-dependent
  (see Environment Availability).
- **Phase gate (before `/gsd-verify-work`):** Run all five mechanical checks in the map above; resolve
  any failure before considering the catalogue final.

### Wave 0 Gaps
- [ ] No pre-existing coverage/classification-check script exists — the planner should decide whether
  to write one short ad hoc script (not committed, or committed under a location outside `typsphinx/`
  if reproducibility across sessions is valued) or run the checks manually via grep/count at
  catalogue-finalization time. Either is acceptable; nothing blocks starting the audit itself.
- [ ] `tests/test_corpus_gate.py::TestCorpusRenderGate` already exists and was reconfirmed passing
  this session — no gap there, just note it should be re-run once more at catalogue-finalization time
  per D-07's freshness check (Pitfall 7), not only at the start of the audit.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|--------------------|
| V2 Authentication | No | Phase touches no auth surface — local file/subprocess work only. |
| V3 Session Management | No | N/A. |
| V4 Access Control | No | N/A. |
| V5 Input Validation | Marginal | The corpus is a pinned, already-vetted (Phase 15) `git clone` of `github.com/sphinx-doc/sphinx` at a fixed tag/SHA — not untrusted input this phase introduces. Any ad hoc helper script parsing the master `.typ`'s `include(...)` lines (Pattern 2) should still avoid `eval`/`exec`-style parsing of that content — plain string/regex extraction (as `test_corpus_gate.py`'s own `UNKNOWN_NODE_RE` already does) is sufficient and matches existing project convention. |
| V6 Cryptography | No | N/A. |
| V12 Files and Resources | Yes | All external process invocations must follow the existing project pattern: `subprocess.run([...], capture_output=True, text=True)` with an explicit argument list (never `shell=True`, never string-interpolated commands) — exactly how `_run_corpus_sphinx_build` and `get_or_clone_corpus` already invoke `sphinx`/`git`. Any new `pdftoppm`/`mutool`/`nix-shell` invocation this phase adds should follow the identical pattern (explicit arg list, no shell interpolation of docnames/paths). |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Path/argument injection via a docname or page-range value flowing into a shelled-out `pdftoppm`/`mutool`/`nix-shell` command | Tampering | Explicit `subprocess.run([list, of, args], shell=False)` (never string-formatted into a shell command), matching the existing `_run_corpus_sphinx_build`/`get_or_clone_corpus` pattern in `tests/test_corpus_gate.py`. Docnames in this corpus are attacker-uncontrolled (fixed, pinned upstream tree) but the pattern should hold regardless. |
| Accidentally committing rasterized page images (which could embed corpus content verbatim, though the corpus itself is public/MIT-licensed Sphinx docs, so this is a hygiene concern, not a confidentiality one) | Information Disclosure (low severity here) | Keep all rasterized images in a scratch/temp directory outside the repo, never `git add`ed — already locked in by CONTEXT.md's Deferred Ideas ("committed screenshot evidence... rejected to keep the repo lean"). |

## Sources

### Primary (HIGH confidence — verified by direct execution in this session)
- `nix-shell -p poppler-utils --run "pdftoppm -v; pdftotext -v"` → poppler-utils 26.06.0
- `nix-shell -p mupdf --run "mutool -v"` → mupdf 1.27.2
- `uv run --extra dev python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` →
  1 passed in 13.63s (real `typst.compile()` succeeded in this sandbox session)
- Manual re-run of the corpus `-b typstpdf` / `-b html` / `-b text` builds via
  `tests/test_corpus_gate.py`'s `_run_corpus_sphinx_build` helper (all three returncode 0)
- `pypdf.PdfReader(...).outline` / `.pages` / `.get_destination_page_number()` against the freshly
  built `index.pdf` (684 pages, 276 outline entries)
- `pdftoppm -png -r 150` output read back via the `Read` tool (visual legibility confirmed on a real
  corpus page)
- `git -C ~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0 rev-parse HEAD` →
  `cc7c6f435ad37bb12264f8118c8461b230e6830c` (matches 15-CORPUS-REPORT.md exactly)

### Secondary (MEDIUM confidence — WebSearch, cross-checked against official docs)
- [Heading – Typst Documentation](https://typst.app/docs/reference/model/heading/) — confirmed
  `outlined`/`bookmarked` default behavior (headings bookmark-by-default when outlined).
- [pdftoppm(1) — poppler-utils manpage](https://manpages.debian.org/testing/poppler-utils/pdftoppm.1.en.html) —
  default DPI (150) and general usage.
- [mutool draw – MuPDF docs](https://mupdf.readthedocs.io/en/latest/tools/mutool-draw.html) — default
  DPI (72), confirming the explicit-resolution requirement noted in Alternatives Considered.

### Tertiary (LOW confidence)
- None — every claim in this document was either directly verified this session or cited from an
  official-docs source above; nothing rests on unverified training-data recall alone.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every tool/version was actually run in this session, not looked up.
- Architecture (docname↔page mapping): HIGH — the mapping mechanism was proven end-to-end against
  the real 684-page corpus PDF this session (outline extraction + `include()`-order both confirmed).
- Pitfalls: HIGH — five of seven pitfalls were directly observed as real behavior in this session
  (graphviz degrade, locale noise, byte-count drift, empty-catalogue confirmation); the remaining two
  (batching/mapping-alignment) are reasoned from the verified corpus scale (154 docnames/684 pages).

**Research date:** 2026-07-19
**Valid until:** Should be re-verified if the corpus cache is ever cleared/re-cloned (a new Sphinx
release would shift the tag/SHA/page count), or if this repo's sandbox network/ELF-exec state changes
between sessions — otherwise stable for the remaining life of the v0.6.1 milestone (~7–14 days is a
reasonable revalidation window given the milestone's short horizon).
