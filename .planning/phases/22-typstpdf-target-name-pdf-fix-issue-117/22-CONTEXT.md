# Phase 22: typstpdf Target-Name PDF Fix (Issue #117) - Context

**Gathered:** 2026-07-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `typst_documents`' **target name** (tuple element `[1]`) actually govern the emitted output
filenames — for **both** the `.typ` and the `.pdf`. Independent of the Phases 19–21 translator
series; the change lives in `typsphinx/builder.py` only.

**Verified root cause (measured during discussion, 2026-07-21):** `doc_tuple[1]` is **never read
anywhere in the codebase**. `grep -rn "\[1\]" typsphinx/{builder,writer,template_engine}.py`
returns nothing; `writer.py:53-56` reads only `doc_tuple[0]` (master-vs-included test).
Both write sites derive the filename from the **docname**:

- `TypstBuilder.write_doc()` — `builder.py:329`: `path.join(self.outdir, docname + self.out_suffix)`
- `TypstPDFBuilder.write_doc()` — `builder.py:646`: `path.join(self.outdir, docname + ".typ")`
- `TypstPDFBuilder.finish()` — `builder.py:706` (read) / `builder.py:721` (write):
  `docname + ".typ"` / `docname + ".pdf"`

**ROADMAP SC#2 carries a factual error — planner MUST NOT trust it.** SC#2 says the fix should be
"consistent with the already-correct `.typ` filename mapping". There is no correct `.typ` mapping:
the `.typ` is named `index.typ`, not `manual.typ`. `docs/configuration.rst:43` documents the target
name as "Output .typ filename", so the `.typ` side violates the published contract too. The phase
scope is therefore **both** filenames (D-01), not the PDF alone. ROADMAP SC#2's wording should be
corrected as part of this phase's work.

**Measured blast radius (all 62 `typst_documents` entries under `tests/` + `docs/` enumerated):**
only **2** entries have `target != docname` and therefore change behavior:

| Location | Entry | Output before → after |
|---|---|---|
| `tests/roots/test-basic/conf.py:12-14` | `("index", "output.typ", …)` | `index.typ` → `output.typ` / `output.pdf` |
| `docs/source/conf.py` | `("index", "typsphinx", …)` | `index.typ` → `typsphinx.typ` / `typsphinx.pdf` |

The other 60 entries are `("index", "index", …)` (target == docname, extension-less) and are
byte-identical before and after. The raw "238 `index.typ` references in `tests/`" count is
misleading — nearly all belong to fixtures whose output name does not move.

**Out of scope:** the Phase 19–21 translator fixes (done); the Phase 23 release prep (version bump
+ CHANGELOG + closing corpus gate); backlog 999.3 (`typst_package` path broken end-to-end); any
`pdf.py` change (`compile_typst_to_pdf` is name-agnostic — it takes content + `root_dir`, so no
edit is expected there despite the roadmap naming `pdf.py`). Milestone invariant carried forward:
**zero new runtime dependencies, no `@preview` version bump, the 3-way version-sync surface
(`writer.py` / `template_engine.py` / `templates/base.typ`) untouched.**

</domain>

<decisions>
## Implementation Decisions

### Scope of the rename
- **D-01: Fix BOTH the `.typ` and the `.pdf` filename** — not the PDF alone. Rationale: the `.typ` side is equally broken and `docs/configuration.rst:43` already documents the target name as the output `.typ` filename, so a PDF-only fix would leave `index.typ` + `manual.pdf` — an incoherent pair that still contradicts the docs. Rejected: PDF-only (smaller diff, but preserves the documented-contract violation and creates a mismatched pair).
- **D-02: The fix targets the master-document write path only.** Documents NOT listed in `typst_documents` (toctree-included children) have no target name and keep being written as `docname + ".typ"` — unchanged. Only entries present in `typst_documents` get the target-name treatment.

### Target-name normalization
- **D-03: Strip only a literal trailing `.typ`, then append the builder's suffix.** `'output.typ'` → stem `output` → `output.typ` / `output.pdf`; `'typsphinx'` (extension-less) → stem `typsphinx` → `typsphinx.typ` / `typsphinx.pdf`. Both forms occur in the real corpus and both MUST work.
- **D-04: Do NOT use `os.path.splitext`.** It would mangle a period-bearing stem (`'v1.2-manual'` → `'v1'`). Rejected explicitly for that reason. Extension-less target names are **valid input**, never a warning or an error — `docs/source/conf.py` itself uses one.

### Output location for nested docnames
- **D-05: Rename the basename in place — the output file stays in the docname's own directory.** `('sub/index', 'manual.typ', …)` → `outdir/sub/manual.typ` and `outdir/sub/manual.pdf`, NOT `outdir/manual.typ`. Rationale: the translator emits child includes and image URIs relative to the master's **docname** location (`_compute_relative_include_path`, `translator.py:2928`, emitted at `:3428` as `include("<rel>.typ")`; `_compute_relative_image_path`, `:3043`). Moving the master's output elsewhere without rebasing those paths would invalidate them for `-b typst`. **Known limitation, deliberately accepted:** this keeps multi-master deliverables scattered across the output tree, and it does NOT fix the pre-existing `-b typstpdf` root mismatch (see `<deferred>`) — Phase 22 fixes the filename bug only and leaves the layout/rebasing question to a separate item. Owner-confirmed 2026-07-21. Rejected: collecting masters at the outdir root (correct end state, but requires rebasing relative-path computation in `translator.py` — a different bug from Issue #117).
- **D-06: A path-bearing target name is an explicitly GUARDED case — warn, then fall back to its basename.** `'sub/manual.typ'` → `logger.warning` ("a path is not supported in a `typst_documents` target name; emitting `manual.typ` next to the source document instead") → `manual` placed next to the docname. Rationale: honoring a user-supplied directory would re-introduce exactly the relative-path breakage D-05 avoids, but silently discarding the path leaves the user with output somewhere they did not ask for and no signal — the mismatch must be surfaced. A warning (not an error) keeps builds that currently "work" (the path is being ignored today anyway) from breaking, and users running `sphinx-build -W` still get a hard failure. Rejected: raising `ExtensionError` (breaks previously-building configs), and interpreting the target as an outdir-relative path (flexible, but pushes the relative-path recomputation problem into this phase, far beyond its scope).
- **D-07: The guard detects separators portably, and covers traversal and absolute forms.** Trigger on `/` **and** `os.sep`/`os.altsep` (so a Windows `sub\manual.typ` is caught on every platform), and treat `..` segments and absolute/drive-qualified targets as the same guarded case. `os.path.basename` alone is not a sufficient detector — detect first, warn, then reduce.

### Backward compatibility
- **D-08: Clean break — no compatibility shim.** `index.typ` / `index.pdf` simply stop being emitted when a target name differs. No duplicate file, no copy, no symlink. Rationale: this is a bug fix restoring documented behavior; emitting both would leave permanent garbage with no defined removal point. Rejected: dual output (breaks nobody but never ends) and a deprecation-warning period (over-engineered for a documented-contract restoration).
- **D-09: The behavior change MUST be carried into the Phase 23 CHANGELOG `[0.6.2]` entry** as a user-visible output-filename change, not buried as an internal fix — users with CI referencing `build/pdf/index.pdf` need to see it. This is a hand-off obligation to Phase 23, not extra work here.

### Verification (GATE-01)
- **D-10: The gate is a real-compile test driven by `tests/roots/test-basic`,** which already declares `("index", "output.typ", …)`. Run `-b typstpdf` against it and assert `output.typ` and `output.pdf` exist with valid `%PDF` magic — and, to make the assert genuinely fail pre-fix, additionally assert `index.typ` / `index.pdf` are **absent**. Pre-fix the builder emits `index.*` and no `output.*`, so both halves fail. Rejected: a brand-new dedicated `tests/fixtures/` render-gate project (duplicates a root that already exercises the exact condition).
- **D-11: Existing tests that assert `index.typ` against `test-basic` must be updated to `output.typ`, not worked around.** They encode the buggy behavior; updating them is part of the fix. The planner must enumerate them (they are the `tests/roots/test-basic`-consuming subset, NOT all 238 `index.typ` occurrences) and confirm the 60 target==docname fixtures stay untouched.
- **D-12: `docs/source/conf.py` output moves to `typsphinx.typ` / `typsphinx.pdf`** — verify `tox -e docs-pdf` and the full-corpus gate (`tests/test_corpus_gate.py`) still pass, updating any hardcoded `index.typ` / `index.pdf` path in the docs-build or corpus-gate machinery. This is a required part of the phase, not a follow-up.

### Claude's Discretion
- **Where the name-derivation lives** — a small shared helper on `TypstBuilder` (e.g. resolving docname → output stem via a `typst_documents` lookup) reused by `TypstBuilder.write_doc`, `TypstPDFBuilder.write_doc`, and `TypstPDFBuilder.finish` is the obvious shape, but the planner settles the exact factoring. The invariant is that all three sites agree, so `finish()` can never look for a `.typ` the write path did not produce.
- **Unit tests for the normalization rule** — the compile gate (D-10) is the required floor; adding table-driven unit tests for the D-03/D-04/D-06 stem cases (extension present/absent, period-bearing stem, path separator) is allowed and encouraged, but not mandated.
- **Duplicate / colliding target names** (two entries resolving to the same output file, or a target colliding with an included child's `docname.typ`) — not raised in discussion and not present in the corpus. Planner may add a defensive warning if it costs nothing; do not build validation machinery for it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Issue + requirement source of record
- `.planning/ROADMAP.md` §"999.2 — Issue #117: typstpdf PDF uses source name instead of target name" (~line 362) — the original issue text: reported against v0.6.0 / Sphinx 9.1 / Python 3.14. Note its claim "The `.typ` filename mapping appears honored" is **disproven** by this phase's measurement (see `<domain>`).
- `.planning/ROADMAP.md` §"Phase 22" (lines 230-249) — goal + 4 success criteria. **SC#2's "already-correct `.typ` filename mapping" premise is factually wrong** (see `<domain>`); the phase corrects it rather than inheriting it.
- `.planning/REQUIREMENTS.md:45` — **PDF-01** requirement text. Written PDF-first; D-01 widens delivery to the `.typ` as well, which strictly supersets PDF-01.
- [Issue #117](https://github.com/YuSabo90002/typsphinx/issues/117) — upstream bug report (`bug`, OPEN).

### Published contract this fix restores
- `docs/configuration.rst:38-60` — the `typst_documents` reference. **Line 43** defines element 2 as "**Target name** (str): Output .typ filename (e.g., `'output.typ'`)" — the contract the `.typ` side currently violates. Line 52 is the exact `('index', 'manual.typ', …)` example from the issue.

### Code — the sites to change
- `typsphinx/builder.py:329` — `TypstBuilder.write_doc()` `.typ` destination (`docname + self.out_suffix`).
- `typsphinx/builder.py:646` — `TypstPDFBuilder.write_doc()` `.typ` destination (`docname + ".typ"`).
- `typsphinx/builder.py:703-725` — `TypstPDFBuilder.finish()`: reads `doc_tuple[0]` only (line 705), reads `docname + ".typ"` (line 706), writes `docname + ".pdf"` (line 721). All three must move to the resolved target stem in lockstep.
- `typsphinx/builder.py:142-153` — `get_target_uri()` (`docname + self.out_suffix`). Check whether cross-document link resolution depends on it; if it does, decide deliberately whether it follows the rename (a link to a renamed master) or stays docname-based.

### Code — must NOT break
- `typsphinx/translator.py:2932` `_compute_relative_path()` and `:3418-3428` — child `include("<rel>.typ")` emission, computed relative to the master's own location. This is why D-05 keeps the master in its docname directory.
- `typsphinx/writer.py:49-58` — `_is_master_document()` matches on `doc_tuple[0]`; master-vs-included branching is keyed to the **source** name and must stay that way (D-02).
- `typsphinx/pdf.py` — `compile_typst_to_pdf(content, root_dir=…)` is filename-agnostic. No change expected despite the roadmap naming `pdf.py`.

### Tests + fixtures
- `tests/roots/test-basic/conf.py:12-14` — the only test root with `target != docname` (`"output.typ"`); the D-10 gate driver.
- `docs/source/conf.py` — target `"typsphinx"` (extension-less); the D-12 verification surface. Exercised by `tox -e docs-pdf`.
- `tests/test_builder.py`, `tests/test_builder_requirement13.py`, `tests/test_integration_nested_toctree.py`, `tests/test_config_template_mapping.py`, `tests/test_config_toctree_defaults.py` — the `index.typ`-asserting modules; the planner must determine which actually consume `test-basic` (those need the D-11 update) versus their own `target == docname` fixtures (untouched).
- `tests/test_corpus_gate.py` — the standing full-corpus regression gate; must stay green through the `docs/source` rename (D-12).
- `tests/test_preview_version_sync.py` — the 3-way `@preview` version-sync gate; untouched by this phase, must stay green (milestone invariant).
- `tests/test_desc_signature_concat_render_gate.py` — the canonical GATE-01 fixture shape (real `-b typstpdf` compile + `%PDF` magic, invoked via `sys.executable -m sphinx`, **never** `uv run`, per the NixOS-sandbox PATH hazard). Follow this invocation convention.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`tests/roots/test-basic`** — already declares `("index", "output.typ", …)`, i.e. the exact
  `target != docname` condition Issue #117 describes. No new fixture project is needed (D-10).
- **`compile_typst_to_pdf(content, root_dir)`** (`pdf.py`) — content-in / bytes-out, filename-agnostic.
  The fix is purely about where `finish()` writes the returned bytes.
- **GATE-01 render-gate shape** (`tests/test_desc_signature_concat_render_gate.py`) — the established
  "build via `sys.executable -m sphinx` → assert emitted artifact → assert `%PDF` magic" pattern;
  reused verbatim, only the assertion subject changes (filename instead of content).

### Established Patterns
- **`typst_documents` tuple = `(sourcename, targetname, title, author)`** — documented at
  `writer.py:53` and `builder.py:704`, both of which then use element `[0]` only. Element `[1]` is
  dead across the whole package; this phase gives it its first consumer.
- **Master-vs-included branching keys on the SOURCE name** (`writer.py:55`) — the target name must
  not leak into that predicate (D-02).
- **Relative-path flattening for toctree children** (`translator.py:2932`/`:3428`) — the master's
  physical location is load-bearing, which is what pins D-05.

### Integration Points
- All edits land in `typsphinx/builder.py`. No `translator.py`, no `writer.py`, no
  `template_engine.py`, no `templates/base.typ` change — the `@preview` version-sync surface is
  untouched by construction.
- Two consumer-side updates ride along: the `test-basic`-consuming test assertions (D-11) and the
  `docs/source` build path (D-12).

</code_context>

<specifics>
## Specific Ideas

- Both filename halves move together: `('index', 'manual.typ', …)` → `manual.typ` **and**
  `manual.pdf`. `index.*` is no longer emitted for that entry.
- Normalization: strip a literal trailing `.typ` only; extension-less target names are valid;
  `os.path.splitext` is explicitly forbidden (would eat `v1.2-manual`).
- Nested docname: rename the basename in place (`sub/index` + `manual.typ` → `outdir/sub/manual.typ`).
- A path inside the target name is a **guarded** case, not a silent reduction: detect it (`/`,
  `os.sep`/`os.altsep`, `..` segments, absolute/drive-qualified forms), emit a `logger.warning`
  naming the file that will actually be written, then fall back to the basename. Never raise.
  `sphinx-build -W` users get a hard failure from the warning for free.
- The gate asserts both directions: `output.typ` / `output.pdf` **present** AND `index.typ` /
  `index.pdf` **absent** — so it fails against the pre-fix builder on both counts.
- Phase 23 hand-off: the CHANGELOG `[0.6.2]` entry must call out the output-filename change as
  user-visible.

</specifics>

<deferred>
## Deferred Ideas

- **`get_target_uri()` semantics for renamed masters** — if cross-document link resolution turns out
  not to depend on it, leave it docname-based and note the reasoning; a deliberate redesign of
  Typst-side cross-document URIs is out of scope here.
- **Duplicate / colliding target-name validation** — no corpus case exists; a defensive warning is
  optional, validation machinery is deferred.
- **Interpreting the target name as an outdir-relative path** (`'sub/manual.typ'` placing the file
  under `outdir/sub/`) — rejected (D-06). Revisit only alongside a real solution to relative
  include/image path recomputation.
- **Master-output layout + the `-b typst` / `-b typstpdf` root mismatch + dead `typst_output_dir`** —
  captured in full at `.planning/todos/pending/2026-07-21-master-output-layout-and-dead-typst-output-dir.md`.
  Three findings surfaced while deciding D-05, all outside this phase:
  (a) `compile_typst_to_pdf()` writes the master to a temp file at **outdir root** (`pdf.py:140-149`)
  and compiles it there, so `-b typstpdf` resolves `include()`/`image()` from the root, while the
  translator emits them relative to the **docname directory** (`translator.py:2928`/`:3043`) — a
  master with a nested docname is therefore **already broken today** under `-b typstpdf`, and only
  root-level masters happen to work. (b) Because the output tree mirrors the source tree, declaring
  multiple masters scatters the deliverables across directories (`_build/pdf/manual.pdf` +
  `_build/pdf/api/api-reference.pdf`) with master and `#include()`-part `.typ` files intermixed.
  (c) `typst_output_dir` is registered (`__init__.py:60`) and documented
  (`docs/configuration.rst:255-267`) but read nowhere — the natural fix for (b) is a dead config.
  **Owner's call (2026-07-21): not in Phase 22.** Collecting the deliverables requires rebasing the
  relative-path computation onto the output location, which is a translator change and a different
  bug from Issue #117. D-05 stands.
- **Backlog 999.3 (`typst_package` path broken end-to-end)** — separate backlog item, separate
  surface (`writer.py`/`template_engine.py`), not this phase. Note (c) above is the same species:
  a documented config that never runs, escaping because no fixture covers it.
- **Read the Docs hosting migration** — unrelated docs-infrastructure todo.

### Reviewed Todos (not folded)
- `todos/pending/2026-07-21-verify-template-function-names-in-package-examples.md` — "typst_package
  (Typst Universe) path is broken end-to-end" (matcher score 0.6, keyword-only match on
  "typst"/"builder"). **Not folded** — already tracked as backlog item 999.3; different root cause
  and different files (`writer.py:151-153`, `template_engine.py:186-191`), no overlap with the
  target-name derivation.
- `todos/pending/2026-07-21-move-documentation-hosting-to-read-the-docs.md` — RTD hosting migration
  (score 0.2, keyword match on "build"). **Not folded** — docs infrastructure, unrelated to PDF-01.

</deferred>

---

*Phase: 22-typstpdf Target-Name PDF Fix (Issue #117)*
*Context gathered: 2026-07-21*
