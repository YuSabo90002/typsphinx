# Architecture Research: v0.8.0 multi-master composition

**Domain:** Sphinx extension — Typst output builder, restructuring output composition in a mature
codebase (typsphinx)
**Researched:** 2026-08-11
**Confidence:** HIGH — every claim below is read from the current tree (`typsphinx/builder.py`,
`writer.py`, `template_engine.py`, `translator.py`) plus the installed Sphinx 9.1.0 source
(`sphinx/util/nodes.py:inline_all_toctrees`, `sphinx/environment/adapters/toctree.py`). No
external ecosystem research was needed — this is a design for code that already exists.

## Standard Architecture

### Current pipeline (as shipped)

```
Sphinx read phase
      │  env.toctree_includes populated (adapters/toctree.py:47)
      ▼
TypstBuilder.write()  (builder.py:384)
      │  ONE ledger for the WHOLE build:
      │  self._included_docnames = set()            (builder.py:99, 420)
      │  self.master_included_docnames = _compute…() (builder.py:116, 428)
      │
      ├─ for docname in sorted(docnames):             ← alphabetical, NOT DFS
      │     doctree = env.get_doctree(docname)
      │     write_doc(docname, doctree)   (builder.py:560 / :915 PDF override)
      │        │
      │        ├─ stem = _resolve_output_stem(docname)        (builder.py:156)
      │        ├─ path = _directory_preserving_relpath(...)   (builder.py:290)
      │        ├─ TypstWriter.translate()                     (writer.py:176)
      │        │     ├─ body = TypstTranslator(doctree).astext()
      │        │     │      visit_toctree emits include() INLINE,
      │        │     │      dedups against builder._included_docnames
      │        │     │      (translator.py:4722-4827, ledger at :4800)
      │        │     ├─ is_master = _is_master_document(docname) (writer.py:96)
      │        │     ├─ if master: TemplateEngine wraps body + toctree
      │        │     │   options extracted from THIS SAME doctree
      │        │     │   (template_engine.py:542, called at writer.py:331)
      │        │     └─ else: prepend 4 @preview imports only (writer.py:204-221)
      │        └─ write ONE file: stem+".typ" — contains EITHER a full
      │           templated document (master) OR bare content (included)
      ▼
TypstBuilder.finish() (builder.py:889) → copy_image_files / copy_template_assets
TypstPDFBuilder.finish() (builder.py:960) → for each typst_documents entry,
      re-resolve the SAME stem, compile that ONE file to PDF
```

**The three defects this redesign closes all trace to one structural cause**: composition
(who includes whom, at what heading depth) is decided *inside* a per-docname, alphabetically-ordered,
whole-build-shared write loop, using build-time booleans that don't know which *master* is asking.

### Proposed pipeline

```
Sphinx read phase  (unchanged: env.toctree_includes, env.found_docs)
      ▼
TypstBuilder.write()  (builder.py:384, kept as the seam)
      │
      ├─ for docname in sorted(docnames):
      │     doctree = env.get_doctree(docname)
      │     write_doc(docname, doctree)
      │        │  EVERY docname, master or not, writes ONLY a CONTENT file:
      │        │  destination = outdir/<docname>.typ   (no stem resolution)
      │        │  TypstWriter.translate() ALWAYS takes the "included" shape:
      │        │     4 @preview imports + body; visit_toctree emits NOTHING
      │        │     (pure SkipNode); no TemplateEngine call in this path at all
      │        └─ write CONTENT file
      │
      └─ AFTER the docname loop: _write_master_wrappers()   ← NEW
            for each typst_documents entry (master_docname, target, title, author, …):
               graph = compute_master_include_graph(env.toctree_includes, master_docname)
                        (NEW — per-master DFS, own `traversed` set, mirrors
                         sphinx.util.nodes.inline_all_toctrees's selection rule)
               toctree_opts = TemplateEngine.extract_toctree_options(
                                  env.get_doctree(master_docname))   (unchanged helper,
                                  new call site)
               stem = _resolve_output_stem(master_docname)      (builder.py:156, reused,
                                                                   now called once per ENTRY)
               path = _directory_preserving_relpath(master_docname, stem) (builder.py:290, reused)
               wrapper_body = render_include_graph(graph, current_docname=master_docname)
                        (NEW — replaces visit_toctree's old text; one
                         `context { set heading(offset: D) include("…".typ) }`
                         per graph entry, flattened, NOT nested)
               out = TemplateEngine(...).render(params, wrapper_body, template_file=...)
                        (moved from writer.py:223-363, unchanged internals)
               write ONE file: outdir/<path>.typ   ← THE WRAPPER
      ▼
TypstBuilder.finish()   (unchanged: copy_image_files / copy_template_assets)
TypstPDFBuilder.finish()  (unchanged: re-resolves the SAME stem, reads the
      WRAPPER back, compiles it — no code change needed here at all, because
      the wrapper is now written to exactly the path this method already expects)
```

### Component responsibilities (old → new)

| Component | Today's responsibility | v0.8.0 responsibility |
|-----------|------------------------|------------------------|
| `TypstBuilder.write_doc()` | Resolve target-name stem, write EITHER a templated master OR bare content, for whichever docname the loop is on | Always write a docname-named CONTENT file. Stem resolution removed from this path entirely |
| `TypstWriter.translate()` | Branch master/included, apply template, extract toctree options | Always the "included" shape — imports + body. Loses ~190 lines (template application) |
| `TypstTranslator.visit_toctree` | Emit `include()` calls, dedup via build-wide ledger | No-op `SkipNode`. Composition is no longer a translator concern |
| `TypstTranslator._reference_anchor_decision` | Consult `builder.master_included_docnames` (build-time) to decide degrade-to-text | Pure function of node + doctree structure; no builder-state cross-reference decision at all |
| **NEW: wrapper generator** (proposed module, see below) | — | Own the per-master DFS, the flattened include/offset block, and the template-application call that `writer.py` used to make for masters |
| `TypstBuilder._resolve_output_stem` / `_directory_preserving_relpath` | Called once per docname in the write loop (mostly a no-op D-02 pass-through) | Called once per `typst_documents` ENTRY, exclusively for wrapper placement |
| `TypstPDFBuilder.finish()` | Re-resolve stem, compile that file | **Unchanged.** It already reads back "the file at the resolved stem path" — that file is now the wrapper instead of the old monolithic master, with zero code change required |

## Integration Points (file:line inventory)

| Site | Today | v0.8.0 | Action |
|------|-------|--------|--------|
| `builder.py:384` `TypstBuilder.write()` | Loops docnames, sets `_included_docnames`/`master_included_docnames` before the loop | Loop simplifies (drops both ledgers); **gains a call to the new wrapper-writing step after the loop** | **Modify** |
| `builder.py:99` `self._included_docnames` | Per-build include-dedup ledger, consulted by `visit_toctree` | No longer meaningful — `visit_toctree` never emits includes | **Delete** (attribute + its `init()`/`write()` reset at :99, :420) |
| `builder.py:101-117` `self.master_included_docnames` + docstring | Cross-doc degrade input | Superseded by the compile-time guard | **Delete** |
| `builder.py:118` `_compute_master_included_docnames()` | BFS over `env.toctree_includes` from every master, used only to feed the attribute above | Its ONLY consumer is deleted | **Delete** |
| `builder.py:156` `_resolve_output_stem()` | Called once per docname in `write_doc()`; D-02 branch (no entry) is the common case | Called once per `typst_documents` entry, inside the new wrapper step. D-02 branch becomes effectively unreachable from that call site (every docname passed in is, by construction, `entry[0]` for some entry) — keep the branch for defensive robustness, but note it as dead-in-practice | **Modify call site, keep body** |
| `builder.py:290` `_directory_preserving_relpath()` | Applied to every docname in `write_doc()` (usually a no-op passthrough) | Applied only to master docnames, for wrapper placement | **Modify call site, keep body** |
| `builder.py:560` `TypstBuilder.write_doc()` | Resolves stem via typst_documents, writes ONE file (master-shaped or included-shaped) | Drops stem resolution: `destination = path.join(outdir, docname + ".typ")` (docnames are already `/`-separated, nesting is automatic). Still sets `current_docname`, still calls `post_process_images`, still calls `writer.translate()` | **Modify — simplify** |
| `builder.py:605` `_write_template_file()` | Writes `_template.typ` once per build | **Unchanged.** Wrapper still imports it exactly as masters do today | No change |
| `builder.py:677` `copy_image_files()` | Copies every URI tracked in `self.images` | **Unchanged** — image tracking still happens per-docname in `post_process_images`/`write_doc`, for every content file including the former master's own | No change |
| `builder.py:889` `TypstBuilder.finish()` | Copies images/assets | **Unchanged** | No change |
| `builder.py:915` `TypstPDFBuilder.write_doc()` | Duplicates base `write_doc()` logic, hardcodes `.typ` suffix (needed because `self.out_suffix` is `.pdf` on this subclass) | Same simplification as the base method (docname-named content, no stem resolution). The `.typ`-hardcoding reason is unchanged, so the override still exists, just shrinks in lockstep with the base method. **Open simplification** (not required): since both methods converge to nearly-identical bodies differing only in that hardcoded suffix literal, a single shared `write_doc()` on the base class using a hardcoded `".typ"` literal (not `self.out_suffix`) would let `TypstPDFBuilder` inherit it unmodified — flag as a nice-to-have, not a requirement | **Modify** (or consolidate, Claude's discretion) |
| `builder.py:960` `TypstPDFBuilder.finish()` | Re-resolves stem, reads back `.typ`, compiles | **No code change.** It already reads "the file at the resolved-stem path" — make sure the new wrapper step runs and writes to that exact path *before* `finish()` executes | No change (ordering-dependent on the new step) |
| `writer.py:39-71` (`_resolve_entry_element`) | Resolves title/author for a master from its `typst_documents` entry | Still needed, but only by the wrapper generator now | **Move** to wrapper module |
| `writer.py:96` `TypstWriter._is_master_document()` | The master/included binary that selects output shape | No shape selection left to make — every docname is content | **Delete** |
| `writer.py:128-174` `_compute_template_import_path()` | Computes `_template.typ` import depth from a master's docname | Still needed, but only when building a wrapper. **The math is unchanged** (it was already keyed to the master's *docname* depth, not its target-renamed path — see placement discussion below) | **Move** to wrapper module, body unchanged |
| `writer.py:176` `TypstWriter.translate()` | Branches master/included; ~190 lines of template application for masters | Always takes today's "included" branch (writer.py:204-221) — this becomes the WHOLE method body | **Modify — drastic simplification** (drops writer.py:222-363 wholesale) |
| `template_engine.py:542` `extract_toctree_options()` | Called by `writer.translate()` on `self.document` (the doctree currently being visited, which IS the master when this runs) | Called by the wrapper generator on `env.get_doctree(master_docname)` — a fresh fetch, since wrapper generation runs after (and independent of) the per-docname write loop. Toctree `numbered`/`maxdepth`/`caption` are directive-option attributes set at parse time, unaffected by `apply_post_transforms`, so a second, non-post-transformed fetch is safe | **No change to the method; new call site** |
| `template_engine.py`'s `render()`/`map_parameters()`/`generate_package_import()` | Called from `writer.py:326-363` for masters | Called from the wrapper generator instead, with identical arguments in spirit (`params`, `body`, `template_file`) — `body` is now the flattened include-graph text instead of a translated doctree | **No change to `TemplateEngine` itself**; caller moves |
| `translator.py:4722-4827` `visit_toctree` / `depart_toctree` | Emits the include block, dedups via `builder._included_docnames` | Body reduces to `raise nodes.SkipNode` (no text emission at all) | **Modify — gut the body** |
| `translator.py:4305-4414` `_compute_relative_include_path()` | Used only by `visit_toctree` to compute include() relative paths | `visit_toctree` no longer calls it. The wrapper generator needs THE SAME algorithm (docname→docname relative path), so this becomes dead on `TypstTranslator` unless reused | **Delete from `TypstTranslator`; move (as a plain function or staticmethod) to the wrapper module** — do not fork a second copy |
| `translator.py:4416-…` `_compute_relative_image_path()` | Used by `visit_image` for every content file's images | **Unchanged** — content files stay docname-named, so this needs no change at all. This is worth stating explicitly: master-document images "just work" with zero special-casing now, where today they only work *because* `_directory_preserving_relpath` happens to keep the renamed master file in the same directory as its docname | No change (simplification side-effect) |
| `translator.py:3011-3103` `_reference_anchor_decision()` / `_ReferenceAnchorDecision` (defined :33-102) | Computes `degrade_xref_to_text` from `builder.master_included_docnames` (:3072-3076); folds it into `opens_wrapper` | Drops the `master_included_docnames` lookup and the `degrade_xref_to_text` field entirely. `opens_wrapper` simplifies to `bool(refuri or refid)`. Cross-document links are now ALWAYS attempted; the degrade decision moves into the Typst source itself (compile-time guard) | **Modify — remove a field and its derivation** |
| `translator.py:4985-5011` `visit_reference` cross-doc branch | `if degrade_xref_to_text: skip_link_wrapper` else emit `link(<label>, ` | Always emit the guarded form (see "Cross-reference guard" below) — the `if degrade_xref_to_text` branch and its warning disappear (or are repurposed as a compile-time-visible degrade, no build-time warning possible since the build no longer knows) | **Modify** |
| `translator.py:3272-3284` citation backrefs (`visit_citation`) | Unconditional `link(<label>, …)` | Same guarded form, enumerated explicitly by PROJECT.md as sharing "the same label-reference shape" | **Modify** |
| `translator.py:4287-4291` `visit_pending_xref` | Unconditional `link(<label>)[` — today's ONLY best-effort fallback with **zero** existence protection at all | Same guarded form | **Modify** |

## Where the wrapper generator belongs

**Proposal: a new module, `typsphinx/composition.py`**, owning everything that used to live in
`writer.py`'s master branch plus the new DFS. Rationale: `writer.py`/`TypstTranslator` are
per-docname, doctree-driven; the wrapper is per-*master*, graph-driven, and needs `env` (not a
single doctree) as its primary input. Bolting it onto `builder.py` would work mechanically but
mixes "drive the write loop" concerns with "know Sphinx's toctree graph and Typst's template
parameter shape" concerns that `template_engine.py`/`writer.py` already model cleanly. A new
module keeps `builder.py` a thin driver (as it is today) and gives the DFS + flattening logic, which
is genuinely new and needs its own tests, a home that isn't "yet another builder.py responsibility."

Proposed shape:

```python
# typsphinx/composition.py

def compute_master_include_graph(
    toctree_includes: dict[str, list[str]], master_docname: str,
) -> list[tuple[str, int]]:
    """Per-master DFS over env.toctree_includes, mirroring
    sphinx.util.nodes.inline_all_toctrees's selection rule: a SINGLE
    `traversed` set, scoped to THIS master only (never shared across
    masters — this is what fixes defect A and the diamond case), so
    the first-encountered (left-to-right, depth-first) path to any
    docname wins, exactly as Sphinx's own toctree resolution does.
    Returns [(docname, depth), ...] in DFS visit order, master itself
    first at depth 0.
    """

def render_include_graph(graph: list[tuple[str, int]], master_docname: str) -> str:
    """The wrapper's body: one flattened
    `context { set heading(offset: D) include("<relpath>.typ") }`
    per graph entry (D = the entry's DFS depth). Replaces the nested,
    runtime-relative `heading.offset + 1` scheme visit_toctree used —
    depth is now known statically per entry, so an ABSOLUTE offset per
    entry is equivalent and needs no runtime accumulation.
    """

def write_master_wrapper(builder, entry) -> None:
    """Orchestrates one typst_documents entry end-to-end: resolve
    stem/placement, fetch env.toctree_includes + one doctree (for
    toctree_* options only), build params via TemplateEngine (moved
    from writer.py), render, write.
    """
```

**What must be captured during the write loop vs. computed up front:**

- **Computed entirely up front, no write-loop dependency:** the include graph itself
  (`env.toctree_includes` is fully populated after Sphinx's read phase, exactly like
  `_compute_master_included_docnames()` already assumes at `builder.py:428` today).
- **Needs one extra doctree fetch per master, NOT captured from the loop:** toctree options
  (`numbered`/`maxdepth`/`caption`). Two designs were considered:
  - **(A, recommended) Re-fetch independently:** `env.get_doctree(master_docname)` again, after the
    per-docname loop, inside the wrapper step. Simple, decouples wrapper generation from write-loop
    ordering entirely (works even if a future incremental-build mode skips writing some content
    files), costs one extra pickle load per master (masters are typically few).
  - **(B) Thread state through the loop:** stash `extract_toctree_options(doctree)` into a
    `dict[str, dict]` keyed by master docname at the point in `write()`'s loop where
    `docname` happens to be a master's source, then hand that dict to the wrapper step. Avoids the
    re-fetch, but couples the wrapper step to loop-iteration side effects and needs a defensive
    fallback for the (currently theoretical, since `get_outdated_docs()` always yields every
    `found_docs`) case where a master docname is absent from that particular `docnames` set.

  **Recommendation: (A).** It is strictly simpler, and the milestone's own "no incremental build"
  status quo (`builder.py:325-335`, `get_outdated_docs()` always yields everything) means the cost
  difference is negligible today; (A) also doesn't foreclose adding real incrementality later.
- **Not needed by the wrapper at all:** per-content-file translator state (images, labels, body
  text) — the wrapper never touches a doctree's *content*, only its toctree-option attributes and
  `env.toctree_includes`' graph shape.

## Wrapper file placement and relative paths — an open choice

For a nested master, e.g. `typst_documents = [("api/index", "API.typ", …)]`, where should the
wrapper live?

### Option A — wrapper stays in the master docname's own directory (recommended)

Reuse `_directory_preserving_relpath("api/index", "API")` unchanged → `outdir/api/API.typ`. This is
**exactly today's existing rule** for master file placement (D-05, `builder.py:290-323`) — no new
behavior, no new risk surface.

- **Consequence for `include()` paths:** the wrapper's effective directory equals
  `posixpath.dirname("api/index")` = `"api"`. Since content files are *always* docname-named and
  directory-preserved, computing each graph entry's relative include path is `_compute_relative_
  include_path(entry_docname, current_docname="api/index")` — i.e. **pass the master's own SOURCE
  docname**, not a synthetic wrapper name, and the existing (moved, unchanged) algorithm produces
  correct paths, including for the master's own depth-0 entry
  (`_compute_relative_include_path("api/index", "api/index")` → `"index"` →
  `include("index.typ")`, verified by tracing the function's same-directory branch).
- **Consequence for images inside content files:** none — see the integration-points table above.
  Image paths are computed per content file against ITS OWN docname, never against the wrapper's
  location, so this decision doesn't touch them at all.
- **Consequence for `_template.typ`'s import path:** none — `_compute_template_import_path()`
  already derives depth from the master's *docname* (`writer.py:173`,
  `len(PurePosixPath(docname).parent.parts)`), not from the target-renamed stem. Since Option A keeps
  the wrapper in that same directory, the existing, unmodified computation stays correct.

### Option B — wrapper always lands at the outdir root, verbatim target name

`("api/index", "API.typ", …)` → `outdir/API.typ`, ignoring the master docname's directory. Might
read as more "intuitive" for a bare (non-path) target name.

- **Consequence:** breaks the v0.6.2 Phase 22.1 alignment property this milestone's own B-1 defect
  exists to fix. Every relative-path helper (`_compute_relative_include_path`,
  `_compute_relative_image_path` — no, unaffected per above — and `_compute_template_import_path`)
  is calibrated to "the wrapper lives at the master docname's own directory depth." Moving the
  wrapper to the root while leaving content files where they are reintroduces exactly the
  basis-mismatch class B-1 is: the wrapper would need a SEPARATE relative-path basis
  (its true output location) from the one every reused helper assumes (docname-derived location),
  doubling the surface area those helpers need to support and risking a silent `file not found` at
  `typst.compile()` time for any project with a nested master.

**Recommendation: Option A.** It costs nothing (literal reuse of already-shipped, already-tested
logic), and Option B's only benefit (a "prettier" root-level path for a nested master with a bare
target name) is a cosmetic preference that direct-conflicts with the property this whole milestone
protects. If the owner wants Option B's file-location semantics later, it should be scoped as its
own follow-up that explicitly re-derives a wrapper-specific relative-path basis — not folded into
this milestone.

## Data flow changes

**What the translator no longer needs to know:**
- Which docnames belong to which master, or to any master at all (`master_included_docnames`
  disappears from its purview).
- Whether the CURRENT docname is a "master" (`_is_master_document` disappears; every docname is
  content).
- How to render a template, extract toctree options, or import a package (all of `writer.py`'s old
  master branch moves out of the translation path).

**What the builder now needs to compute that it didn't before:**
- The per-master DFS include graph (`compute_master_include_graph`), previously implicit in
  document-order `visit_toctree` calls scattered across the whole write loop.
- Per-master toctree options, via a SECOND doctree fetch (Option A above) that today's design gets
  "for free" because the master's own doctree happens to be in hand during `writer.translate()`.
- Wrapper placement + duplicate-target detection (CR-02) — a `set()` of already-resolved target
  paths threaded through the new wrapper-writing loop, populated as each `typst_documents` entry is
  processed. Because `_resolve_output_stem` now runs once per ENTRY (not once per docname), this
  registry is trivial to add locally — no new builder-instance state needed, unlike the deleted
  whole-build ledgers.

**Ordering constraints (Sphinx's read phase → `write()` → per-docname `write_doc()` → `finish()`):**
1. Sphinx's read phase must be complete before `env.toctree_includes` is trustworthy — already true
   today (`builder.py:422-428`'s existing comment states this explicitly; the same constraint now
   governs the NEW wrapper step, not just the deleted ledger).
2. Every content file `write_doc()` will `#include()` must exist on disk **before** `typst.compile()`
   runs (in `TypstPDFBuilder.finish()`), but does NOT need to exist before the wrapper `.typ` is
   *written* — Typst resolves `#include()` at compile time, not at wrapper-authoring time. This means
   the wrapper-writing step can run any time after `write()`'s docname loop finishes, and does not
   need to run interleaved with it. Recommended seam: **end of `TypstBuilder.write()`**, after the
   `for docname in sorted(docnames)` loop (`builder.py:432-444`), so both builders (`typst` and
   `typstpdf`, since `TypstPDFBuilder` does not override `write()`) get wrapper files from one shared
   code path, and `TypstPDFBuilder.finish()` needs no changes at all.
3. `_write_template_file()` (`builder.py:605`, called once from `prepare_writing()`) must still run
   before any wrapper is written, exactly as it must today before any master is written — unaffected
   ordering, just re-stated for completeness.

## Cross-reference compile-time guard

The build-time judgment being replaced (`translator.py:3072-3076`) knows, at write time, which
docnames are reachable from *some* master. It cannot know which docnames are reachable from *the
specific master that will end up #including the current content file* — a content file is now
compiled zero, one, or many times, once per wrapper that includes it, and the SAME degrade decision
must come out differently in each compilation. That information genuinely does not exist until Typst
compiles a specific wrapper — hence "compile-time," not "build-time."

**Concept** (PROJECT.md records this as "measured working" against the current tree, but the exact
validated Typst source was not present in any file read for this research — re-derive/confirm the
precise syntax during planning, not at roadmap time):

```typst
context {
  let _body = { <the reference's rendered children go here> }
  if query(<the-target-label>).len() > 0 {
    link(<the-target-label>, _body)
  } else {
    _body
  }
}
```

The key STRUCTURAL implication for `translator.py`: today's streaming `visit_reference` /
`depart_reference` pair emits `link(<label>, ` immediately on visit and a bare `)` on depart — the
label is committed before any child content exists. A guard needs the label reference to appear
**twice** (once per branch) around content that is only fully known at depart time. The cleanest
fit, without introducing a buffering rewrite of `visit_reference`, is to open the `context { let
_body = {` scaffold on visit and close it with `}; if query(...).len() > 0 {…} else {…} }` on
depart — both ends only need the SAME label, which is already computed once (via
`_reference_anchor_decision`) and available at both call sites today. The three enumerated sites
(`translator.py:5007`, `:3273`/`:3281`, `:4291`) all currently do the "emit `link(<label>, `,
close later" shape and should route through one shared helper rather than three independent
implementations, mirroring how `_reference_anchor_decision` already unified the anchor-eligibility
judgment.

**Scope:** only sites where the label's presence in THIS compiled unit is not guaranteed by
construction. Same-document `#anchor` links (`translator.py:4980-4984`) do NOT need the guard — if
a content file is included at all, its own anchors are always present in that same `#include()`,
because content files are included wholesale, never partially.

**No new runtime dependency:** `context`/`query` are Typst standard-library builtins. The `@preview`
package count and its three-file version-lockstep (`writer.py`, `template_engine.py`,
`templates/base.typ`) are untouched by this change.

## Suggested build order

The dependency the milestone brief states explicitly must be respected: **fixing the include-graph
turns a currently-silent single-docname-alphabetical-order omission into a hard compile failure**
(a document shared by two masters, where a target label exists in one master's graph but not the
other's, currently just gets a `TypstError`-free but wrong PDF — after the fix, whichever master's
wrapper doesn't happen to include the target hits a dangling `label ... does not exist` fatal, since
the old build-time `master_included_docnames` degrade no longer runs). **Therefore the cross-reference
guard must land no later than the include-graph fix — ideally in the SAME phase, or immediately
before it, never after.**

Recommended phase order:

1. **Content/wrapper split, no include graph yet.** Every docname writes a template-less content
   file (`write_doc()` simplification); each `typst_documents` entry gets a wrapper that still emits
   includes the OLD way (single-toctree-node, no DFS) — i.e. reproduce today's behavior through the
   new file-shape, proving the split itself (closes B-1/B-2) without touching composition semantics
   yet. This isolates "does the new file shape work at all" from "does the new graph algorithm work."
2. **Compile-time cross-reference guard**, landed against the Phase-1 file shape. Must precede or
   accompany Phase 3 per the constraint above — this is the phase that makes the include-graph fix
   safe to ship.
3. **Per-master DFS include graph** (`compute_master_include_graph`, flattened offset rendering) —
   closes defect A and the diamond case. This is the phase where a shared document's cross-reference
   target being present in one master's graph and absent from another's stops being silently wrong
   and starts being a real compile question — which Phase 2's guard must already be answering
   correctly by the time this phase's GATE-01 fixtures run.
4. **CR-02 duplicate-target detection** — cheap once Phase 1 moves `_resolve_output_stem` to a
   once-per-entry call site (a local `set()` in the new wrapper loop). Can ride with Phase 1 or land
   as its own small phase; has no ordering dependency on Phases 2/3.
5. **The two PR #131 image defects** (`TypstBuilder._track_image()` — rehomed-image collision with a
   real `srcdir/images/` file, and the absolute-URI-outside-doctreedir escape) — independent of the
   composition work; can run in parallel with any of the above, or last, since neither touches
   `write_doc()`'s composition shape.
6. **Release prep** (version bump, CHANGELOG) — last, per the standing v0.5.0 Phase 10 pattern.

**Explicit ordering constraint restated for the roadmapper:** Phase 3 (include-graph) must never ship
without Phase 2 (guard) already in place ahead of it. Do not schedule them as independently
parallelizable work.

## New vs. Modified inventory

| Item | New / Modified / Deleted | Notes |
|------|---------------------------|-------|
| `typsphinx/composition.py` (proposed name) | **New** | Houses `compute_master_include_graph`, the flattened offset/include renderer, `_resolve_entry_element` (moved from `writer.py:24-73`), `_compute_template_import_path` (moved from `writer.py:128-174`), and the moved relative-path helper from `translator.py:4305-4414` |
| `TypstBuilder._write_master_wrappers()` (or similar) | **New** | Orchestration entry point, called once from `write()` after the docname loop |
| `TypstBuilder.write_doc()` / `TypstPDFBuilder.write_doc()` | **Modified** | Drop stem resolution for content; both simplify |
| `TypstBuilder.write()` | **Modified** | Drops both ledgers; gains the wrapper-writing call |
| `TypstBuilder.init()` (`builder.py:76`) | **Modified** | Drop `_included_docnames`/`master_included_docnames` initialization |
| `TypstBuilder._compute_master_included_docnames()` | **Deleted** | Sole consumer removed |
| `TypstWriter._is_master_document()` | **Deleted** | No shape selection left |
| `TypstWriter.translate()` | **Modified — major simplification** | Loses ~190 lines |
| `TypstWriter._compute_template_import_path()` | **Moved** (not deleted) | Body unchanged |
| `TypstWriter._resolve_entry_element` (module-level fn) | **Moved** (not deleted) | Body unchanged |
| `TypstTranslator.visit_toctree` / `depart_toctree` | **Modified — gutted** | Body becomes `raise nodes.SkipNode` |
| `TypstTranslator._compute_relative_include_path` | **Deleted from translator, moved to `composition.py`** | Same algorithm, new owner |
| `TypstTranslator._compute_relative_image_path` | **Unchanged** | No code change |
| `TypstTranslator._reference_anchor_decision` / `_ReferenceAnchorDecision` | **Modified** | Drops `degrade_xref_to_text` field and its builder-state lookup |
| `TypstTranslator.visit_reference` / `depart_reference` | **Modified** | Guarded-link emission shape |
| `TypstTranslator.visit_citation` / `depart_citation` (backref sites, :3273/:3281) | **Modified** | Guarded-link emission shape |
| `TypstTranslator.visit_pending_xref` / `depart_pending_xref` | **Modified** | Guarded-link emission shape |
| Shared guarded-link helper on `TypstTranslator` | **New** | One place the three sites above call into |
| `_resolve_output_stem` / `_directory_preserving_relpath` (`builder.py:156`/`:290`) | **Modified call sites only** | Bodies unchanged; now called once per `typst_documents` entry |
| CR-02 duplicate-target registry | **New** | A local `set()` in the new wrapper-writing loop |
| `TemplateEngine` (`template_engine.py`, all of it) | **Unchanged** | Every method keeps its exact contract; only the caller moves |
| `TypstBuilder._track_image()` (PR #131 fixes) | **Modified** | Independent of composition work — two narrow bug fixes |
| `_write_template_file()`, `copy_image_files()`, `copy_template_assets()`, `post_process_images()`, `get_target_uri()`, `prepare_writing()` | **Unchanged** | No coupling to this redesign |
| `TypstPDFBuilder.finish()` | **Unchanged** | Reads back whatever the wrapper step wrote to the already-correct path |

## Risks and open questions

### Toctree-adjacent prose loses its in-document position

Today, if a master document's body contains a paragraph BEFORE its `.. toctree::` directive, then
the directive, then MORE prose AFTER it, the old `visit_toctree` splices includes exactly where the
directive sat, so "before" and "after" prose stay correctly interleaved with the included children.
In the flattened-DFS design, the master's own content file (with `visit_toctree` now a no-op) still
contains BOTH prose blocks — but with nothing between them where the toctree used to inject content
— and the wrapper appends children AFTER the master's own content file is included wholesale. Net
effect: any prose written AFTER a `.. toctree::` directive in a master document will now render
AFTER all of that toctree's children, not immediately after the toctree's position and before any
subsequent prose. Two (or more) separate `.. toctree::` directives in one document are similarly
flattened to one block at the end — `env.toctree_includes[docname]` already concatenates every
toctree directive's entries into one list in document order (verified:
`sphinx/environment/adapters/toctree.py:47`, `setdefault(docname, []).extend(...)`), so relative
ORDER between the two toctrees' children is preserved, but any prose that was written BETWEEN them
is not. This matches the overwhelmingly common Sphinx convention (a toctree at or near the end of an
index page, nothing meaningful after it) and is a direct, accepted consequence of "stay at the file
layer" rather than doctree-level splicing (the same design tradeoff PROJECT.md's Key Context section
already commits to). **Recommend:** name this explicitly as a documented limitation (CHANGELOG /
docs), and add one GATE-01 fixture asserting the accepted new ordering, so it is a decision on record
rather than an accidental regression discovered later.

### The diamond-graph invariant is a first-class success criterion, not a side effect

PROJECT.md names this explicitly: `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]` must resolve
correctly. Because `compute_master_include_graph`'s `traversed` set is re-initialized PER MASTER
(never shared across `typst_documents` entries, and never shared with any other master's DFS), `c`
is correctly included exactly once in `M`'s wrapper (deduplicated within `M`'s own DFS, first-visit
wins per Sphinx's own "prefer the deeper path" rule) and independently exactly once in `M'`'s
wrapper. Any implementation that reuses a SINGLE `traversed`/ledger across multiple wrapper builds
(the same design mistake `builder.py:99`'s deleted whole-build ledger made) silently reintroduces
defect A. Make this the explicit unit-test shape for the DFS function, not just an integration gate.

### `_resolve_output_stem`'s D-02 branch becomes dead-in-practice

Once its only caller is the once-per-`typst_documents`-entry wrapper loop, the "no matching entry"
branch (`builder.py:199-203`) can never actually fire (every docname passed in IS `entry[0]` for the
entry being processed). This is not a bug — the branch stays correct and harmless — but it is worth
noting for the executor so nobody spends time trying to construct a test that exercises it through
the new call site; its existing unit-test coverage (if any, calling the method directly) remains
valid.

### Import duplication does not change in kind, only in count

Because the former master's own docname now ALSO becomes an ordinary `#include()`d content file with
its own 4-package import block (previously it had exactly one import block, from the inlined/
imported template), every wrapper now imports `codly`/`codly-languages`/`mitex`/`gentle-clues` one
MORE time than before (once for the wrapper itself via `TemplateEngine.render()`, once for what used
to be inlined master content, plus once per child as today). This is linear in document count either
way and Typst already tolerates repeated `#import` of the same package across sibling `#include()`s
(that's exactly what today's multi-child masters already do) — flagged for completeness, not as a
risk.

## Sources

- `typsphinx/builder.py` (full file, this session) — `TypstBuilder`/`TypstPDFBuilder`, lines cited
  throughout
- `typsphinx/writer.py` (full file, this session) — `TypstWriter`, lines cited throughout
- `typsphinx/template_engine.py` (full file, this session) — `TemplateEngine`, unaffected by this
  redesign except for caller relocation
- `typsphinx/translator.py` — `visit_toctree`/`depart_toctree` (:4722-4837), `_reference_anchor_
  decision`/`_ReferenceAnchorDecision` (:33-102, :3011-3103), `visit_reference` (:4839-5024),
  `visit_citation` backrefs (:3230-3329), `visit_pending_xref` (:4262-4304),
  `_compute_relative_include_path`/`_compute_relative_image_path` (:4305-…), `_resolve_xref_docname`
  (:4617-…), `visit_document`/`depart_document` (:630-…)
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/util/nodes.py:485`
  (`inline_all_toctrees`) — the upstream selection-rule this milestone's DFS mirrors at the
  file-composition layer
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/environment/adapters/
  toctree.py:47` — confirms `env.toctree_includes[docname]` concatenates every toctree directive's
  entries in document order
- `.planning/PROJECT.md` — "Current Milestone: v0.8.0 multi-master composition" section (measured
  defect evidence, scope, carried-forward deferrals)

---
*Architecture research for: typsphinx v0.8.0 multi-master composition*
*Researched: 2026-08-11*
