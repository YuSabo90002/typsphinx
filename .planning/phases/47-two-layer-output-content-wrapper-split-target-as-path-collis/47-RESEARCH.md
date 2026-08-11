# Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection - Research

**Researched:** 2026-08-11
**Domain:** Sphinx builder/writer internals; Typst `#include()` path resolution; real-compile
regression-fixture technique for non-fatal defects
**Confidence:** HIGH — every empirical claim below was measured this session against the unfixed
tree, with captured command/compile output. No claim in the "measured" sections is inferred.

## Summary

This phase replaces one file-shape decision (`_is_master_document()`'s master/included binary) with
two independently-resolved paths per `typst_documents` entry: a docname-derived **content** path
(no template, always written) and a target-derived **wrapper** path (template + include, written
once per entry). Both open questions this phase owns were closed **this session by direct
measurement on the unfixed tree**, not by inference:

- **Open question #3 (B-2's RED shape): CLOSED. B-2 is a compiles-fine-but-wrong-output defect, not
  a compile fatal.** A minimal fixture — an outer master whose toctree includes a nested master's
  content file, with that content file's template application present (today's shape once B-1 is
  worked around) — compiled successfully through `typst.compile()` and produced a 6-page PDF
  containing a **second title page** and a **second `#outline()`/"Contents" table** sandwiched
  between the outer document's own prose and the nested document's own body. COMP-04's GATE-01 RED
  must therefore be a structural `pypdf`-text assertion (per binding constraint #4), not a
  `TypstError`.
- **B-1 (already known to be a compile fatal) was independently reconfirmed**: `TypstError('file not
  found (searched at .../guide/index.typ)')`, because the parent's `#include()` is derived from the
  raw docname while the target file is written under a target-derived name. COMP-03's GATE-01 RED
  keeps the classic `TypstError` form.
- **Typst's `#include()` path is resolved relative to the *including file's own directory*, not the
  compile root.** Confirmed with four independent compiles (downward-only, upward-only, and both
  failing/succeeding forms). `..` segments are legal. This means wrapper→content include paths need
  a full two-path relative computation (`posixpath.relpath`-equivalent, computed from the wrapper's
  **resolved** output directory to the content file's docname-derived directory), not
  `_compute_template_import_path()`'s existing depth-only `"../"` counter, which assumes the
  importing file's own directory equals the importer's docname directory and the imported file is
  always at the outdir root — neither assumption holds for a general wrapper→content pair once
  OUT-01 lets a wrapper land anywhere.
- **BLD-02 (duplicate target silently drops a master) and the self-collision case (D-01's premise)
  were independently reproduced this session**, matching the pending todo's own re-measurement and
  CONTEXT.md's stated premises exactly.
- **The RED-evidence technique for the three non-fatal collision defects already exists in this
  repo**: `pypdf` is a pinned dev dependency (`pyproject.toml:46`, `pypdf>=6.14,<7`) and
  `tests/test_pdf_render_gate.py` is the established class-scoped
  `sphinx-build → typst.compile() → pypdf.extract_text()` pattern; `tests/test_typst_documents_collision_gate.py`
  is the established real-subprocess pattern for asserting collision-warning text plus per-file
  content-marker survival.

**Primary recommendation:** Do not delete `_resolve_output_stem()`'s guard logic wholesale — its
`is_guarded` boolean (`builder.py:222-227`) currently OR-combines the separator-based rule OUT-01
reverses with the three escape rules OUT-02 keeps; the reversal is disentangling one term from that
boolean, not deleting the function. Content-file placement needs no `_resolve_output_stem` call at
all (it is always `outdir/<docname>.typ`); only wrapper placement calls the (rewritten) resolver.
Factor the near-duplicate `TypstBuilder.write_doc()` / `TypstPDFBuilder.write_doc()` bodies into one
shared write path so "byte-identical across builders" becomes structural rather than a maintained
coincidence — this generalizes the same "`TypstBuilder` owns it, `TypstPDFBuilder` inherits it"
principle CONTEXT.md's Claude's-Discretion note already applies to the collision validator.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Content-file emission (docname → `.typ`, no template) | Backend / Builder (`TypstBuilder.write_doc`) | Writer (`TypstWriter.translate`) | The builder decides *where* a file is written; the writer decides *what* is emitted into it. Both must agree the content path is always docname-derived. |
| Wrapper-file emission (target → `.typ`, template + include) | Backend / Builder (`TypstBuilder.write_doc`, new wrapper-write path) | Writer / TemplateEngine | Wrapper placement is a builder-side path decision (OUT-01/OUT-02); wrapper *contents* (template application, include statement) are writer/TemplateEngine concerns. |
| Collision detection across the logical-file-to-physical-path map | Backend / Builder (new unified validator, pre-write per D-02) | — | Must run before any file is written and see every entry at once — a per-document write-time decision (today's `_resolve_output_stem`) cannot detect a two-entry collision by construction. |
| `#include()` path computation (wrapper → content) | Writer (`TypstWriter`, generalizing `_compute_template_import_path`) | Builder (must supply the wrapper's *resolved* output location) | The writer emits the Typst source; it needs the builder-computed resolved wrapper path as an input, since Typst path resolution is relative to the including file's own directory (measured this session), not the docname. |
| Security guard on escaping targets (OUT-02) | Backend / Builder (`_resolve_output_stem`, the surviving guard terms) | — | Pure path-string validation before any filesystem write; no writer/template involvement. |

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** A wrapper target that resolves onto a content file's own path is a configuration error
  that fails the build with an `ExtensionError`, not a warning with a fallback.
- **D-02:** Collisions are detected in one pass **before** the write phase, every offending entry is
  enumerated in a single error, and no output file is written when any collision is found.
- **D-03:** All collision kinds route through **one** validator over a single logical-file-to-
  physical-path map — self-collision, a target landing on another document's content path, the
  reserved `_template.typ` infrastructure file, and two entries resolving to the same target
  (BLD-02) — and every one of them is an error with no fallback.
- **D-04:** Two entries naming the same docname with different targets are allowed.
- **D-05:** Collision comparison is always `casefold()`-normalized on both sides, on every platform.
  Unicode normalization (NFC/NFD) is **not** applied — only case folding — and the written filename
  keeps the user's exact bytes.
- **D-06:** Every content file carries the preamble `writer.py:208-218` prepends to included
  documents today — the four `@preview` imports plus `#show: codly-init.with()` and
  `#codly(languages: codly-languages)` — unchanged.
- **D-07:** The `-b typst` builder reports the wrapper files it wrote and names them as the files to
  compile.
- **D-08:** A wrapper resolves its title and author from the entry it is being generated for, read
  positionally, not through `writer.py:24`'s `_resolve_entry_element()` docname first-match lookup.
- **D-09:** The fifth tuple element stays accepted and ignored in this phase and must not be
  repurposed.

### Claude's Discretion

- Which files the `typstpdf` builder compiles to PDF (wrappers only).
- Where the unified validator lives, as long as D-02's before-write timing and D-03's single-code-path
  property hold, and as long as `TypstBuilder` owns it so `TypstPDFBuilder` inherits identical
  behaviour rather than re-implementing it.
- The exact wording of every new warning and error message.

### Deferred Ideas (OUT OF SCOPE)

- Per-entry template configuration via a named template key in the fifth tuple element (CONF-13,
  deferred to its own milestone).
- The global-`params` silent discard (no change in v0.8.0; ships as a documented limitation, resolved
  by CONF-13).

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COMP-01 | Every document written as a docname-named content `.typ`, no template | Confirmed content-file path needs no `_resolve_output_stem` call — it is always `outdir/<docname>.typ`; `_directory_preserving_relpath`'s directory-preservation half survives here unconditionally |
| COMP-02 | Each `typst_documents` entry produces a wrapper `.typ` at its resolved target path | `_resolve_output_stem`'s surviving terms (post OUT-01/OUT-02 split) become the wrapper-path resolver; D-03's unified validator gates it |
| COMP-03 | B-1 closes: nested master-as-toctree-child builds without `file not found` | B-1 reconfirmed this session (`TypstError('file not found ...')`); root cause is `#include()` computed from raw docname while the target file is written under a target-derived name — fixed by computing include paths from the wrapper's **resolved** location (measured `#include()` semantics below) |
| COMP-04 | B-2 closes: included master no longer re-expands template mid-body | Open question #3 closed this session: compiles-fine-but-wrong-output, not fatal — GATE-01 RED must be structural/`pypdf`, see Validation Architecture |
| OUT-01 | Target treated as output-dir-relative path (reversing D-05/D-06/D-07 of Phase 44) | `_resolve_output_stem`'s `is_guarded` boolean (`builder.py:222-227`) must be disentangled — the separator-membership term is removed, the three escape terms stay |
| OUT-02 | Escaping targets (`..`, absolute, drive-qualified) still refused with warning + fallback | The three surviving `is_guarded` terms (`".." in segments`, `path.isabs(stem)`, `is_drive_qualified`) plus their existing fallback-to-basename logic (`builder.py:228-249`) are reused verbatim |
| OUT-03 | Content files stay docname-derived regardless of wrapper placement | Structural consequence of COMP-01's content-path rule being independent of `_resolve_output_stem` entirely |
| BLD-02 | Two entries resolving to same target detected, not silently dropped | Reproduced this session: exit 0, no warning, first master's body absent from the shared `manual.typ` (`grep -c` evidence below) |
| BLD-03 | Wrapper target colliding with a content file's own path detected | Self-collision case reproduced this session: `("index","index.typ",...)` builds successfully today via the `effective != docname` escape at `builder.py:275` — becomes a real physical collision once content files unconditionally exist |
| BLD-04 | Collision detection behaves identically on case-insensitive filesystems | Reproduced this session on Linux (case-sensitive): `Manual.typ` (target) vs `manual` (docname) do NOT collide today, confirming the gap is real and invisible on Linux CI |

## Standard Stack

No new runtime or dev dependency is required by this phase (binding constraint #7). The one library
this phase's testing strategy leans on — `pypdf` — is **already** a pinned dev dependency.

### Core (existing, reused)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pypdf` | `>=6.14,<7` [VERIFIED: /home/yuta/Documents/typsphinx/pyproject.toml:46 — `"pypdf>=6.14,<7",`] | Text-extraction from compiled PDFs for structural RED/GREEN assertions | Already the project's own standing pattern (`tests/test_pdf_render_gate.py`, `tests/test_admonition_pdf_render_gate` classes) since v0.6.0 |
| `typst-py` (`typst`) | pinned elsewhere in `pyproject.toml` (unchanged this phase) | Real `typst.compile()` acceptance gate (GATE-01/GATE-02 standing invariant) | Standing project invariant since v0.6.0 |

### Alternatives Considered

None — this phase adds no new packages. Package Legitimacy Audit is not applicable (see below).

**Installation:** N/A — no `pip install` / `uv add` needed. `pypdf` is already present in the `dev`
extra and importable in the current checkout's `.venv` (confirmed this session: `import pypdf` used
directly for the B-2 measurement below).

## Package Legitimacy Audit

**Not applicable.** This phase installs zero new external packages (binding constraint #7: "no new
`typst_*` config value... zero new runtime dependencies" — this phase's own scope never proposes a
new package either). `pypdf` is pre-existing, pinned, and already imported in test code; it requires
no fresh legitimacy check.

## Architecture Patterns

### System Architecture Diagram

```
                     typst_documents = [(docname, target, title, author, tmpl), ...]
                                          |
                                          v
                    +--------------------------------------------+
                    |  TypstBuilder.write()  (builder.py:384)     |
                    |  - unified pre-write collision validator     |  <-- NEW (D-02/D-03)
                    |    over {content path} u {wrapper paths}     |
                    |    u {"_template"} -- one pass, all entries  |
                    +--------------------+------------------------+
                                          | (fails loud -> ExtensionError,
                                          |  no file written, if any collision)
                                          v
              +---------------------------+----------------------------+
              |                                                        |
              v                                                        v
  +---------------------------+                        +----------------------------------+
  |  content-file write path  |                        |  wrapper-file write path (per     |
  |  (EVERY docname, always)  |                        |  typst_documents entry, once)     |
  |  path = outdir/<docname>  |                        |  path = resolved target under     |
  |    .typ  (COMP-01/OUT-03) |                        |    outdir, OUT-01 path-as-path,   |
  |  TypstWriter: NO template,|                        |  OUT-02 escape guard survives      |
  |  D-06 preamble (4 imports |                        |  TypstWriter: FULL template        |
  |  + codly-init) always     |                        |  (D-08 positional title/author),   |
  +-------------+-------------+                        |  #include() of THIS entry's        |
                |                                       |  master content, path computed     |
                |                                       |  from wrapper's RESOLVED location  |
                |                                       |  to content's docname-derived path |
                |                                       |  (posixpath.relpath-equivalent --  |
                |                                       |  NOT the depth-only counter)       |
                |                                       +-------------------+----------------+
                |                                                           |
                +-----------------------------+  content .typ  <-----------+
                                               |  is #include()d by
                                               |  its entry's wrapper
                                               v
                                     [Typst #include() resolves
                                      relative to the WRAPPER's own
                                      directory -- measured this
                                      session, see Common Pitfalls]
                                               |
                                               v
                          TypstPDFBuilder.finish(): compiles WRAPPER
                          files only (Claude's Discretion), reads back
                          via the SAME resolved wrapper path used at
                          write time (builder.py:1036's call site)
```

### Recommended Project Structure

No new files/modules are implied structurally — this is a builder/writer-internal rewrite. The
existing three-file split (`writer.py`, `builder.py`, `template_engine.py`) stays; the new unified
collision validator is a new method on `TypstBuilder` (Claude's Discretion on exact placement, D-02
timing and D-03 single-path-ness are the only hard constraints).

### Pattern 1: Content path is unconditional — no resolver call

**What:** Every content file's output path is `path.join(self.outdir, docname + ".typ")`
(docname already carries its own `/`-separated directory, e.g. `"guide/index"` → `outdir/guide/index.typ`).
**When to use:** Always, for every docname in `env.found_docs`, regardless of whether that docname
also has a `typst_documents` entry.
**Why this matters:** `_resolve_output_stem()` and `_directory_preserving_relpath()` exist today to
answer "where does THIS docname's MASTER output go" — a question that conflated two different
concerns (is this a master? what does its target resolve to?). Once every docname unconditionally
gets a content file, that file's path is never a function of `typst_documents` at all — it is a pure
function of the docname. Only the WRAPPER'S path is target-derived.

### Pattern 2: `#include()` path must be computed from resolved locations, not docnames

**What:** A general "compute the Typst-syntax include-path string from file A (the wrapper, at its
OUT-01-resolved location) to file B (the content file, at its docname-derived location)" function.
**When to use:** Every wrapper's include of its own entry's content file.
**Example (measured this session, not from docs):**
```python
# Source: this session's own posixpath.relpath cross-check against real
# typst.compile() results (see Common Pitfalls below for the raw evidence)
import posixpath

def compute_include_path(wrapper_resolved_dir: str, content_path: str) -> str:
    """wrapper_resolved_dir: dirname of the wrapper's own OUTPUT path
    (relative to outdir root, '' for outdir root itself).
    content_path: the content file's OWN path (relative to outdir root),
    e.g. 'guide/index.typ'.
    Typst #include() resolves relative to the INCLUDING file's own
    directory -- confirmed empirically, see Common Pitfalls -- so this is
    a genuine two-path relpath, not a depth-only "../" counter.
    """
    start = wrapper_resolved_dir or "."
    return posixpath.relpath(content_path, start=start)
```
**Why `_compute_template_import_path()` (writer.py:128-174) does NOT generalize as-is:** that
function computes `depth = len(docname.parent.parts)` and returns `"../" * depth + "_template.typ"`
— it silently assumes (a) the importing file's own resolved directory equals its docname's
directory, and (b) the imported file is always at the outdir root (so only upward `"../"` segments
are ever needed, never a downward path component). Both assumptions are false for a wrapper once
OUT-01 lets a wrapper's target be an arbitrary path unrelated to its docname's directory, and false
in general for content files that can sit deeper than their wrapper. The general two-path relpath
above is required; `_compute_template_import_path()`'s form only remains valid for its own original
job (locating the outdir-root `_template.typ`, which genuinely is always at the root).

### Anti-Patterns to Avoid

- **Reusing `_directory_preserving_relpath()` for wrapper placement:** that function's entire purpose
  is D-05's docname-directory forcing, which OUT-01 explicitly reverses. Any code path that still
  calls it for a wrapper's path is a latent D-05 regression.
- **Computing the wrapper→content include path from the raw docname** (as today's
  `visit_toctree`/translator does): this is the literal root cause of B-1 — measured this session,
  see Common Pitfalls.
- **Deleting `_resolve_output_stem()`'s `is_guarded` boolean wholesale:** it currently combines the
  OUT-01-reversed term with the OUT-02-kept terms in one OR-expression (`builder.py:222-227`);
  wholesale deletion silently drops the security half too.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wrapper→content relative path computation | A new bespoke depth-counting scheme (copy-pasting `_compute_template_import_path`'s shape) | `posixpath.relpath(content_path, start=wrapper_dir)` (or equivalent manual walk) | Measured this session: Typst's `#include()` resolution is a genuine two-endpoint relative path, confirmed to accept both upward-only, downward-only, and mixed forms — `posixpath.relpath` is the standard-library primitive for exactly this, and using anything narrower (depth-only) silently breaks the downward-segment case |
| PDF content assertions for non-fatal defects | Regex-scraping `.typ` source text alone | `pypdf.PdfReader(...).pages[i].extract_text()` (already a pinned dependency, already an established project pattern) | `.typ` source structure does not prove what the COMPILED document actually contains (e.g. a second title page is only visible in the rendered PDF's page/text structure, not obviously in the `.typ` source, which just looks like an ordinary nested `#show: project.with(...)` call) |
| Collision detection at write time, per-document | A per-`_resolve_output_stem`-call scan of `found_docs` (today's shape) | A single pre-write pass building one map from every logical file (content paths ∪ wrapper paths ∪ `"_template"`) to its physical path, checking for duplicates — the `TypstPDFBuilder.finish()` failures-list-then-one-`ExtensionError` shape (`builder.py:1007-1074`), relocated one build stage earlier | Per-document resolution structurally cannot see a SECOND entry's target — this is exactly why BLD-02 exists today; D-02/D-03 require a build-wide view before any write happens |

**Key insight:** every collision-adjacent defect in this phase (BLD-02, BLD-03, BLD-04, and the D-01
self-collision case) shares one root cause: `_resolve_output_stem()` answers "what is THIS entry's
own name" with no visibility into any OTHER entry or into the now-unconditional content-file
existence. The unified validator is not an incremental patch to that function — it is a different
question asked at a different time (before any write, over the whole `typst_documents` list plus the
full `found_docs` set), and no amount of hardening the per-entry resolver closes it.

## Common Pitfalls

### Pitfall 1: B-1 — include path derived from docname, file written under a target-derived name

**What goes wrong:** `TypstError('file not found (searched at .../guide/index.typ)')`.
**Why it happens:** The parent's `visit_toctree` emits `include("guide/index.typ")` — computed from
the child's raw docname — while `_resolve_output_stem` names that child's OWN output file from its
`typst_documents` target entry (today, truncated to a basename and forced into the docname's own
directory by D-05/D-06/D-07), so the file physically written is `guide/guide.typ`, never
`guide/index.typ`.
**Measured evidence (this session, unfixed tree):**
```
$ .venv/bin/python -m sphinx -b typst <fixture: index master toctree-including
  "guide/index", ALSO itself a typst_documents entry targeting "manuals/guide.typ"> ...
WARNING: a path is not supported in a typst_documents target name:
  'manuals/guide.typ' -- using 'guide' instead
build succeeded, 1 warning.
$ find out_typ -type f
  out_typ/guide/guide.typ     <- actually written (D-05/D-06/D-07 shape)
  out_typ/outer.typ           <- includes "guide/index.typ" (docname-derived)
$ python -c "typst.compile('outer.typ', root='out_typ')"
TypstError('file not found (searched at .../out_typ/guide/index.typ)')
```
**How to avoid:** Compute the wrapper's `#include()` target from the same resolved content-file
location the content-file writer uses (`outdir/<docname>.typ`, unconditionally under COMP-01) — never
from the wrapper's own target-derived name.
**Warning signs:** Any code path that derives an include string from `typst_documents[i][1]` (the
target) rather than `typst_documents[i][0]` (the docname).

### Pitfall 2: B-2 — an included master's template re-expands mid-body (compiles fine, wrong output)

**What goes wrong:** The compile SUCCEEDS but the PDF contains a second title page and a second
`#outline()` in the middle of the parent's body.
**Why it happens:** `_is_master_document()` is a build-wide binary — a docname that is BOTH a
`typst_documents` entry AND another master's toctree child gets the FULL template applied to its own
`.typ` file (title page, `#outline()`, `#show: project.with(...)`), and when that file is
`#include()`d by its parent, Typst inlines all of that content exactly where the `#include()` sits.
**Measured evidence (this session, B-1 worked around by copying the file to the path the parent
expects, isolating B-2's own effect):**
```
$ python -c "typst.compile('outer.typ', root='out_typ')"
COMPILE SUCCEEDED
$ python -c "import pypdf; ...extract_text() per page..."
page 0: "Outer Master / Probe Author / 1"                    <- outer's own title page
page 1: "Contents ... 2 Outer Master ... 2.2 Nested Master"  <- outer's own outline
page 2: "2 Outer Master / OUTER-PROSE-MARKER / 3"             <- outer's own prose
page 3: "Nested Master / Probe Author / 4"                    <- SECOND title page, mid-body
page 4: "2.1 Contents / Contents ... / 5"                      <- SECOND outline, mid-body
page 5: "2.2 Nested Master / GUIDE-BODY-MARKER / 6"           <- nested master's own body
```
Six pages total; pages 3-4 (a full second title page + a full second table of contents) sit between
the outer document's own prose (page 2) and the nested document's own content (page 5) — exactly the
"mid-body re-expansion" defect description.
**Closes open question #3:** the compile does NOT fail. COMP-04's GATE-01 RED must be a structural
`pypdf`-text assertion (e.g. "the compiled outer PDF's text contains the string `'Nested Master'`
followed later by a second `'Contents'` occurrence before `GUIDE-BODY-MARKER'`, or: page count > the
expected page count for a template-less inclusion") — NOT a `TypstError` assertion, since none
occurs.
**How to avoid:** Once every docname's content file (COMP-01) carries no template unconditionally,
this defect cannot recur by construction — there is no longer a `.typ` file that is "sometimes a
master, sometimes a fragment" depending on inclusion context.

### Pitfall 3: `#include()` resolves relative to the including file's own directory — NOT the compile root

**What goes wrong:** Assuming Typst's `#include("...")` path is resolved against the `root:` passed
to `typst.compile()` (the outdir) leads to wrong paths for any wrapper not located at the outdir
root.
**Measured evidence (this session, four independent micro-fixtures, isolated from Sphinx entirely):**
```
# root/manuals/wrapper_rootrel.typ:  #include("guide/index.typ")   [no ../]
typst.compile(..., root=root) -> FAILS:
  file not found (searched at root/manuals/guide/index.typ)

# root/manuals/wrapper_relfile.typ:  #include("../guide/index.typ")
typst.compile(..., root=root) -> SUCCEEDS
  (pypdf: page text includes "Content Body" / "CONTENT-MARKER")

# root/shallow_wrapper.typ (at outdir root):  #include("very/deep/nested/docname.typ")
typst.compile(..., root=root) -> SUCCEEDS   [downward-only, no ../, confirms
                                              a wrapper at the outdir root needs
                                              NO relative prefix for deeper content]

# root/manuals/sub/guide.typ (2 levels deep):  #include("../../root_content.typ")
typst.compile(..., root=root) -> SUCCEEDS   [upward-only, confirms a deeply
                                              nested wrapper needs a full climb
                                              back to a root-level content file]
```
**How to avoid:** Compute the include path as a genuine relative path between the wrapper's own
resolved output directory and the content file's docname-derived directory (see Pattern 2 above),
never as a function of the docname alone and never assuming either endpoint is at the outdir root.
`..` segments in an include path are legal — confirmed by the third and fourth fixtures above.

### Pitfall 4: `is_guarded`'s four conditions are one OR-expression — OUT-01 cannot delete the whole thing

**What goes wrong:** A naive "delete the D-06/D-07 path guard" reading of OUT-01 risks deleting
OUT-02's security half too, since both live inside the same boolean at `builder.py:222-227`:
```python
is_guarded = (
    any(sep in stem for sep in separators)   # <- OUT-01 REVERSES this term only
    or ".." in segments                       # <- OUT-02 KEEPS this term
    or path.isabs(stem)                       # <- OUT-02 KEEPS this term
    or is_drive_qualified                     # <- OUT-02 KEEPS this term
)
```
**Why it happens:** All four conditions were written as one guard in Phase 44 because, at the time,
"any path component at all" was uniformly rejected — there was no reason to distinguish "a path that
merely goes somewhere else under outdir" (OUT-01's now-legal case) from "a path that escapes outdir
entirely" (OUT-02's still-illegal case).
**How to avoid:** Split the boolean: compute a new `escapes_outdir` condition (the three OUT-02 terms
only) that still triggers the existing fallback-to-basename-with-warning path (`builder.py:228-249`);
a bare separator-bearing-but-non-escaping stem is no longer guarded at all and instead becomes the
literal relative wrapper path, joined under `outdir`.
**Warning signs:** A test asserting "any `/` in a target name warns and truncates" (see Tests Whose
Expectations Move below) still passing after the change — that is a sign OUT-01 was not actually
applied.

### Pitfall 5: Case-insensitive collision hazard is invisible on Linux CI

**What goes wrong:** A target differing from a docname (or another target) only by case is treated as
a DIFFERENT path on Linux (the CI runner's default local dev filesystem) but the SAME path on
Windows and macOS's default filesystem — so a fixture proving this defect closed must run on all
three, and a Linux-only local run cannot detect its absence.
**Measured evidence (this session):**
```python
# conf.py
typst_documents = [
    ("index", "index.typ", "Index Master", "Probe"),
    ("manual", "Manual.typ", "Manual Master", "Probe"),   # note the capital M
]
```
```
$ .venv/bin/python -m sphinx -b typst ...
build succeeded.   (no warning at all)
$ find out -maxdepth 1 -name '*.typ'
  out/Manual.typ
  out/index.typ
```
Two DIFFERENT files on this (Linux, case-sensitive) filesystem — no collision detected, none exists
here. On a case-insensitive filesystem (Windows, default macOS APFS) these would be the SAME path,
and (once content files exist unconditionally under COMP-01) the docname `manual`'s own content file
and the wrapper for entry `("manual", "Manual.typ", ...)` would silently overwrite whichever writes
last.
**How to avoid:** D-05 (locked) mandates `casefold()`-normalized comparison on **every** platform, not
a runtime `sys.platform` branch — this is exactly what prevents "green on Linux, red on Windows".
**Warning signs:** Any collision-detection code that compares raw strings (`==`) rather than
`.casefold()`-normalized strings.

## Code Examples

### Content-file path (unconditional, COMP-01/OUT-03)
```python
# Derived this session from reading builder.py's write_doc() bodies
# (builder.py:560-603, :915-958) -- both currently compute a stem via
# _resolve_output_stem() even for non-master docnames, where that call is a
# no-op (entry_found stays False, docname returned unchanged, D-02). Once
# every docname unconditionally gets a content file, that no-op path IS the
# entire rule -- no resolver call is needed for the content path at all:
content_path = path.normpath(path.join(self.outdir, docname + ".typ"))
```

### Wrapper's #include() of its own content file
```python
# Source: this session's own measured Typst #include() semantics (Pitfall 3)
import posixpath

def content_include_path(wrapper_relative_dir: str, content_relative_path: str) -> str:
    start = wrapper_relative_dir or "."
    return posixpath.relpath(content_relative_path, start=start)

# e.g. wrapper resolved to "manuals/guide.typ" (dir "manuals"),
# content at "guide/index.typ" ->
#   posixpath.relpath("guide/index.typ", start="manuals") == "../guide/index.typ"
```

### D-06's preamble (verbatim, unchanged, generalizes to every content file)
```python
# Source: typsphinx/writer.py:208-218 (verbatim, read this session)
imports = []
imports.append("// Essential imports for included document")
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.10": *')
imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.3.1": *')
imports.append("")
imports.append("// Initialize codly")
imports.append("#show: codly-init.with()")
imports.append("#codly(languages: codly-languages)")
imports.append("")
```
[VERIFIED: /home/yuta/Documents/typsphinx/typsphinx/writer.py:208-218 — code block quoted verbatim
above matches the file exactly at these line numbers.]

## State of the Art

| Old Approach | Current Approach (this phase) | When Changed | Impact |
|--------------|-------------------------------|---------------|--------|
| One `.typ` per docname; shape (templated vs. fragment) selected by `_is_master_document()` at write time | Two `.typ`s per master entry: an always-templateless content file (every docname) + a templated wrapper file (per `typst_documents` entry) | This phase | `_is_master_document()` is deleted entirely (verified by repo-wide grep per SC#1); B-1/B-2 close by construction |
| A `typst_documents` target with a path component is rejected and truncated to its basename, forced into the docname's own directory (Phase 44 D-05/D-06/D-07) | A target is a path relative to the output directory; a bare name writes at the output root, an explicit path writes where written | This phase (OUT-01, a deliberate reversal) | The common `[("index", "index.typ", ...)]` config now collides with the content file it sits beside — this is exactly why the collision work rides with this phase rather than following it |
| Collision detection (CR-01) compares only against `env.found_docs ∪ {"_template"}`, one entry at a time, warn-and-fallback | One pre-write validator over the full logical-to-physical map, error-and-abort (D-01/D-02/D-03) | This phase | `tests/test_typst_documents_collision_gate.py` and two `test_builder_output_stem.py` cases move from asserting exit-0-with-warning to asserting a non-zero exit with `ExtensionError` |

**Deprecated/outdated:**
- `_directory_preserving_relpath()` (`builder.py:290-323`): its entire purpose (D-05's directory
  forcing) is reversed by OUT-01 for wrapper placement. It is not necessarily deleted outright — its
  directory-preservation SHAPE may still be needed for content-file placement (a docname's directory
  IS unconditionally where its content file goes) — but its target-forcing role for wrappers is gone.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `posixpath.relpath`'s output form is accepted verbatim by Typst's `#include()` in every case, not just the four shapes measured this session (downward-only, upward-only, same-directory implicit via `_compute_template_import_path`'s existing precedent, and the mixed `../guide/index.typ` case) | Architecture Patterns / Pattern 2, Code Examples | A content file at the same resolved directory as its wrapper would need `posixpath.relpath` to return a bare filename with no `./` prefix — untested this session; low risk since Typst's docs (not fetched this session, see below) describe `#include()` paths as ordinary filesystem-relative strings, consistent with everything measured |
| A2 | Typst's `#include()` path semantics documented above (relative to the including file, `..` legal) hold identically across the pinned `typst-py` version range this project uses, not just the specific installed version this session measured against | Common Pitfalls / Pitfall 3 | If a `typst-py` bump changed this semantic it would be a breaking, easily-caught regression (every `#include()` in the corpus would fail) — not a silent risk, but the claim itself was not cross-checked against Typst's own official documentation this session (no `mcp__context7__*` / web fetch was available/used; the finding is empirical-only, from direct `typst.compile()` runs against the version already pinned and installed in this checkout) |
| A3 | The exact `is_guarded` boolean shown in Pitfall 4 is the complete and only place OUT-01/OUT-02's split needs to happen — no other code path independently re-implements a similar path-rejection rule | Common Pitfalls / Pitfall 4 | A repo-wide grep for `os.sep`, `os.altsep`, `isabs`, or similar path-guard vocabulary was not exhaustively run this session beyond reading `builder.py` and `writer.py` in full; a missed second site would let an escaping target slip through OUT-02 undetected until a fixture catches it |

**Note on provenance:** every row in this table is tagged `[ASSUMED]`-equivalent because it extends a
directly-measured empirical finding to a case not itself measured, or leans on the absence of a
counter-example rather than an authoritative source. Everything ELSE in this document that is stated
as fact (B-1's exact error text, B-2's page-by-page PDF structure, `#include()`'s directional
resolution, BLD-02's silent-drop reproduction, the self-collision reproduction, the case-collision
reproduction, and every quoted line range from `writer.py`/`builder.py`) was captured directly this
session via `Read` and real `sphinx-build`/`typst.compile()`/`pypdf` runs, and is marked `[VERIFIED:
<this session's command output>]` in context above.

## Open Questions

All five "Open Questions for Planning" assigned to Phase 47 by `REQUIREMENTS.md`/`ROADMAP.md` are
addressed:

1. **B-2's RED state (open question #3): CLOSED this session** — compiles-fine-but-wrong-output. See
   Summary and Pitfall 2.
2. **CR-01 self-collision policy (open question #4): CLOSED by CONTEXT.md D-01** (locked, not
   reopened here) — refuse with `ExtensionError`. This research independently reconfirmed the OLD
   (pre-fix) behavior for the planner's before/after framing: `[("index", "index.typ", ...)]` builds
   successfully today with no warning (measured this session).
3. **Case-normalization scope (open question #5): CLOSED by CONTEXT.md D-05** (locked, not reopened
   here) — `casefold()` on both sides, every platform, no Unicode normalization. This research
   independently reconfirmed the gap is real and invisible on Linux (measured this session, Pitfall
   5).

No further open questions from this research beyond the three Assumptions-Log items above, which are
low-risk and self-detecting (a wrong assumption fails loudly at either `typst.compile()` or an
existing test).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst-py` (import name `typst`) | GATE-01/GATE-02 real-compile fixtures (COMP-03, COMP-04, BLD-02..04, OUT-02) | ✓ (confirmed this session — used directly for all measurements above) | pinned in `pyproject.toml` (unchanged this phase) | — |
| `pypdf` | RED/GREEN structural PDF-text assertions (COMP-04, BLD-02..04) | ✓ (confirmed this session — used directly for the B-2 page-text measurement) | `>=6.14,<7` [VERIFIED: pyproject.toml:46] | — |
| `uv` / `.venv` (main checkout) | Running `sphinx-build` as `sys.executable -m sphinx` per the project's own established subprocess-test convention | ✓ (main-tree `.venv/bin/python` resolves `typsphinx` to the editable checkout, confirmed this session) | — | — |
| Windows / macOS CI lanes | SC#5's evidence requirement (milestone invariant #5, binding constraint #2) | ✓ — `.github/workflows/ci.yml` already runs `matrix.os: [ubuntu-latest, windows-latest, macos-latest]` [VERIFIED: .github/workflows/ci.yml:17, read this session] | — | — |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`; existing suite already contains real-subprocess `sphinx-build` gates) |
| Config file | `pyproject.toml` (no new config needed) |
| Quick run command | `pytest tests/test_builder_output_stem.py tests/test_typst_documents_collision_gate.py -x` (fast subset covering the resolver/collision surface this phase rewrites) |
| Full suite command | `pytest` (or `tox -e py313`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Pre-fix RED required (binding constraint #4)? | File Exists? |
|--------|----------|-----------|-------------------|------------------------------------------------|-------------|
| COMP-01 | Every docname gets a template-less content `.typ` | integration (real `sphinx-build` subprocess) | `pytest tests/test_two_layer_output_gate.py -x` | Structural: assert content file has NO `#show: project.with(` and NO template import | ❌ new, Wave 0 |
| COMP-02 | Each entry gets a wrapper at its resolved target path | integration | same module, path-assertion tests | Structural: assert wrapper file EXISTS at the target-derived path and content does NOT (pre-fix: today's single-file shape) | ❌ new, Wave 0 |
| COMP-03 | B-1 closes (nested master-as-child compiles) | integration + real `typst.compile()` | `pytest tests/test_two_layer_output_gate.py::test_b1... -x` | **Classic `TypstError` RED** — reproduced this session (`file not found (searched at .../guide/index.typ)`); record this exact string as the pre-fix fixture assertion | ❌ new, Wave 0 |
| COMP-04 | B-2 closes (no mid-body template re-expansion) | integration + real `typst.compile()` + `pypdf` text extraction | `pytest tests/test_two_layer_output_gate.py::test_b2... -x` | **Structural `pypdf` RED** (binding constraint #4) — pre-fix assertion: the parent's compiled PDF page-text sequence contains a SECOND occurrence of a title-page-shaped block (author line + isolated page number) and a SECOND `"Contents"` heading before the nested content's own body marker; post-fix: neither appears | ❌ new, Wave 0 |
| OUT-01 | Target-as-path (bare → root, path → where written) | unit + integration (real `sphinx-build`) | `pytest tests/test_builder_output_stem.py -x` (existing module, expectations MOVE — see below) | Not applicable (this is a behavior CHANGE with tests that move, not a non-fatal defect) | ✅ existing, expectations change |
| OUT-02 | Escaping targets (`..`, absolute, drive-qualified) still refused | unit + integration | `pytest tests/test_builder_output_stem.py -x` (the three surviving guard-term cases) | Not applicable — this is a preserved behavior; a REGRESSION test (not a RED-then-GREEN fixture) proves it survives the OUT-01 rewrite | ✅ existing, subset kept |
| OUT-03 | Content files stay docname-derived regardless of wrapper placement | integration | `pytest tests/test_two_layer_output_gate.py -x` | Not applicable — structural invariant, assert directly post-fix | ❌ new, Wave 0 |
| BLD-02 | Duplicate targets detected, not silently dropped | integration (real `sphinx-build` subprocess) | `pytest tests/test_collision_validator_gate.py::test_bld02... -x` | **Structural RED** — reproduced this session: exit 0, `manual.typ` contains `OTHER-MASTER-MARKER-BBB` (count 1) but NOT `INDEX-MASTER-MARKER-AAA` (count 0), no collision warning in combined stdout/stderr; post-fix: non-zero exit, `ExtensionError` naming both entries | ❌ new, Wave 0 |
| BLD-03 | Wrapper-vs-content self-collision detected | integration | `pytest tests/test_collision_validator_gate.py::test_bld03... -x` | **Structural RED** — reproduced this session: `[("index","index.typ",...)]` exits 0 with no warning today; post-fix: `ExtensionError` per D-01 | ❌ new, Wave 0 |
| BLD-04 | Case-insensitive-filesystem parity | integration, MUST run on Windows/macOS CI lanes (already present) | `pytest tests/test_collision_validator_gate.py::test_bld04... -x` (assert on the `casefold()`-normalized comparison directly at the unit level, since the physical-collision consequence is only observable on a real case-insensitive filesystem) | **Structural RED at the unit level** (the comparison function does not `casefold()`) — reproduced the *consequence* this session on Linux (no warning for `Manual.typ` vs `manual`), but the fixture proving BLD-04's fix must assert the comparison ITSELF folds case, since Linux CI cannot observe the physical collision | ❌ new, Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_builder_output_stem.py tests/test_two_layer_output_gate.py tests/test_collision_validator_gate.py -x`
- **Per wave merge:** full `pytest` run + `black --check .` / `ruff check .` / `mypy typsphinx/`
- **Phase gate:** full suite green, plus a real `-b typst` and `-b typstpdf` build of the B-1/B-2
  fixture and the collision fixtures, before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_two_layer_output_gate.py` — new module, covers COMP-01/02/03/04, OUT-03 (content/
  wrapper path placement, B-1's `TypstError`, B-2's structural `pypdf` assertion)
- [ ] `tests/test_collision_validator_gate.py` — new module, covers BLD-02/03/04 (each its own
  pre-fix RED per binding constraint #4)
- [ ] `tests/test_builder_output_stem.py` — existing module, EXPECTATIONS MOVE for OUT-01 (path
  targets no longer truncated) while the three OUT-02 escape cases are kept as regression tests, and
  lines 334/352 (the CR-01 fallback assertions) move to expect `ExtensionError` instead of a
  fallback, per D-03 replacing CR-01 [VERIFIED: /home/yuta/Documents/typsphinx/tests/test_builder_output_stem.py:334-352 — read this session, both are `test_resolve_output_stem_falls_back_on_*_collision` functions asserting `builder._resolve_output_stem("index") == "index"`]
- [ ] `tests/test_typst_documents_collision_gate.py` — existing module, EVERY test in it currently
  asserts `result.returncode == 0` and a warning substring for what D-01/D-03 now make an
  `ExtensionError` (non-zero exit) — this whole module's assertions invert
- [ ] `tests/test_preview_version_sync.py` — NOT expected to change (the four `@preview` versions are
  unaffected by this phase), but must be re-run once content files carry the D-06 preamble
  unconditionally, to confirm the sync check still covers every emitted `.typ` shape

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | N/A — build-time file-generation tool, no auth surface |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | **Yes** | `typst_documents` target strings are user-supplied `conf.py` input; OUT-02's escape guard (`..`, absolute, drive-qualified rejection) IS the input-validation control — reuse the existing, already-measured-working three-term guard rather than writing a new one |
| V6 Cryptography | No | N/A |
| V12 File and Resources | **Yes** | The core hazard this phase's security half defends against is path traversal: a `typst_documents` target that resolves OUTSIDE `outdir` via `..`/absolute/drive-qualified segments. `path.isabs()` + explicit `".." in segments` + drive-letter detection is the correct, minimal control for this — no path-sanitization library is needed or justified (a hand-written check against a small, closed set of escape shapes is standard practice for this narrow a validation, and rewriting it with a third-party library would be net-negative complexity for no security gain) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Path traversal via a `conf.py`-supplied target string escaping `outdir` (writing outside the intended output tree) | Tampering / Elevation of Privilege (writes outside the sandboxed output directory) | OUT-02's surviving guard terms (`".." in segments`, `path.isabs(stem)`, drive-qualification check) — already implemented and measured working pre-phase; this phase's job is to PRESERVE these three terms while removing only the fourth (separator-membership) term, per Pitfall 4 |
| Silent data loss via unintended file-path collision (a wrapper physically overwriting a content file, or one master overwriting another's) | Tampering (unintended overwrite) / Denial of Service (silent loss of a document's compiled output) | D-01/D-02/D-03's unified pre-write validator — this phase's own core deliverable |
| Case-insensitive-filesystem collision invisible in CI | Tampering (same overwrite hazard, but undetected until deployed on Windows/macOS) | D-05's `casefold()`-normalized comparison on every platform (not runtime-conditional), plus SC#5's requirement that CI actually exercise Windows/macOS lanes |

`conf.py` is themselves already a trusted-input surface (it is arbitrary Python executed by the
project owner running `sphinx-build`) — the threat model here is "a well-meaning but mistaken
`conf.py`", not an adversarial one; this matches the existing project convention (`_resolve_output_stem`'s
docstring and D-01..D-09's own framing treat `typst_documents` misconfiguration as a build-quality
concern, not an attacker-controlled surface).

## Sources

### Primary (HIGH confidence — measured this session)

- `/home/yuta/Documents/typsphinx/typsphinx/writer.py` (full file read this session) — `_resolve_entry_element` (24-73), `_is_master_document` (96-126), `_compute_template_import_path` (128-174), `translate()` including the D-06 preamble (176-363, preamble at 204-221)
- `/home/yuta/Documents/typsphinx/typsphinx/builder.py` (full file read this session) — `_default_typst_documents` (28-47), `_compute_master_included_docnames` (118-154), `_resolve_output_stem` (156-288, `is_guarded` at 217-227, CR-01 collision block at 264-283), `_directory_preserving_relpath` (290-323), `get_target_uri` (337-366), `write()` (384-444), `TypstBuilder.write_doc` (560-603, stem resolution at 578), `_write_template_file` (605-675), `TypstPDFBuilder.write_doc` (915-958, stem resolution at 929), `TypstPDFBuilder.finish` (960-1074, third `_resolve_output_stem` call at 1036, failures-list pattern at 1007-1074)
- Direct `sphinx-build`/`typst.compile()`/`pypdf` measurements this session (all commands and output
  captured above): B-1 reconfirmation, B-2 isolation, `#include()` path-resolution semantics (4
  fixtures), BLD-02 reconfirmation, self-collision (D-01 premise) reconfirmation, case-collision
  (BLD-04 premise) reconfirmation
- `.planning/todos/pending/2026-08-05-a-master-that-is-also-a-toctree-child-is-unrepresentable.md` and
  `.planning/todos/pending/2026-08-04-duplicate-typst-documents-target-silently-drops-a-master.md`
  (both read this session) — prior measurements this session's own reproductions independently
  confirm
- `/home/yuta/Documents/typsphinx/tests/test_pdf_render_gate.py` (read this session) — established
  `sphinx-build → typst.compile() → pypdf` pattern
- `/home/yuta/Documents/typsphinx/tests/test_typst_documents_collision_gate.py` (read this session) —
  established real-subprocess collision-warning-plus-content-survival pattern
- `/home/yuta/Documents/typsphinx/tests/test_builder_output_stem.py` (partial read, lines 300-400,
  this session) — the two CR-01 fallback tests whose expectations D-03 inverts
- `/home/yuta/Documents/typsphinx/.github/workflows/ci.yml` (grepped this session) — confirms
  windows-latest/macos-latest CI lanes already exist
- `/home/yuta/Documents/typsphinx/pyproject.toml` (grepped this session) — `pypdf>=6.14,<7` pinned dev
  dependency
- `.planning/phases/47-.../47-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`,
  `.planning/ROADMAP.md` (§Phase 47, §Binding constraints), `.planning/PROJECT.md` (§Current
  Milestone) — all read in full this session

### Secondary (MEDIUM confidence)

- None consulted this session (no web search or Context7 lookup was performed — Typst's own
  `#include()` semantics were established empirically rather than from official documentation; see
  Assumptions Log A1/A2).

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies, `pypdf` pin verified directly from `pyproject.toml`
- Architecture (content/wrapper split, `#include()` semantics): HIGH — every claim measured this
  session against the unfixed tree with captured command output
- Pitfalls: HIGH — all five pitfalls are directly reproduced defects with captured evidence, not
  inferred from the todo records alone (though those records independently corroborate)
- Open question #3 (B-2's RED shape): HIGH — definitively closed by direct measurement this session

**Research date:** 2026-08-11
**Valid until:** No external time-decay risk (no library-version research); valid until the unfixed
tree's `writer.py`/`builder.py` are themselves modified by this phase's own implementation, at which
point the "unfixed tree" measurements in this document become historical (pre-fix) evidence rather
than current-state fact — exactly their intended role as GATE-01 pre-fix RED baselines.

## Working-Tree Cleanliness

All measurement fixtures were built under the scratchpad directory
(`/tmp/claude-1000/-home-yuta-Documents-typsphinx/9c81fbcb-349f-44ed-8d49-a734e70d64ed/scratchpad/`),
never inside the repository tree. `git status --porcelain` was run twice this session (before writing
this file and immediately before this final check) and returned empty both times — the working tree
is clean.
