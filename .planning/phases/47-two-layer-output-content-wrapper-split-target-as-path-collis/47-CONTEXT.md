# Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection - Context

**Gathered:** 2026-08-11
**Status:** Ready for planning

<domain>
## Phase Boundary

The unit of output stops being "one `.typ` per docname whose shape depends on whether that docname
is a master". Every document is written as a docname-named **content** file carrying no template at
all, and every `typst_documents` entry gains a **wrapper** file carrying the template application
and the include of its master's content — so `writer.py:96`'s `_is_master_document()` binary
disappears. B-1 and B-2 close, a target becomes a path relative to the output directory (reversing
Phase 44's D-05/D-06/D-07 while keeping their security half), and any two logical files wanting one
physical path are reported instead of silently overwriting.

Composition semantics are deliberately **not** touched here — the wrapper reproduces today's include
behaviour through the new file shape, so "does the new file shape work at all" stays isolated from
"does the new graph algorithm work" (Phase 49).

</domain>

<decisions>
## Implementation Decisions

### Collision detection and reporting

- **D-01:** A wrapper target that resolves onto a content file's own path is a configuration error that fails the build with an `ExtensionError`, not a warning with a fallback — **Reversibility:** one-way — `docs/source/user_guide/configuration.rst:46-52` publishes the opposite contract (a colliding target warns and falls back), and `typsphinx/builder.py:275`'s `effective != docname` guard deliberately allows the self-collision case today. A configuration such as `[("index", "index.typ", ...)]` builds successfully in v0.7.x and will stop building. Undoing this after release means re-breaking users who already renamed their targets.

- **D-02:** Collisions are detected in one pass **before** the write phase, every offending entry is enumerated in a single error, and no output file is written when any collision is found — **Reversibility:** reversible — this mirrors `builder.py:1007`'s existing `failures`-list-then-one-`ExtensionError` shape from `TypstPDFBuilder.finish()`, so it is a relocation of an established pattern rather than a new one. One run of `sphinx-build` surfaces every target the user has to fix.

- **D-03:** All collision kinds route through **one** validator over a single logical-file-to-physical-path map — self-collision, a target landing on another document's content path, the reserved `_template.typ` infrastructure file, and two entries resolving to the same target (BLD-02) — and every one of them is an error with no fallback — **Reversibility:** one-way — this replaces `builder.py:264-283`'s CR-01 warning-and-fall-back-to-docname behaviour, which `tests/test_typst_documents_collision_gate.py` and `tests/test_builder_output_stem.py:334/352` currently assert. The old fallback is not merely being tightened, it is unusable after the split: falling back to the docname lands the wrapper exactly on that docname's content file, which is the self-collision D-01 refuses.

- **D-04:** Two entries naming the same docname with different targets are allowed — the validator asks only whether two logical files want one physical path, and a repeated docname does not — **Reversibility:** costly — once a documented-working configuration, removing it breaks user config files. It produces two wrappers over one content file, which is coherent given D-08 and becomes a first-class feature under CONF-13.

- **D-05:** Collision comparison is always `casefold()`-normalized on both sides, on every platform, so a target differing from another logical path only by case is an error on Linux as well — **Reversibility:** costly — the alternative (branching on the running filesystem's case sensitivity) is the exact "green on Linux, red on Windows" shape milestone invariant #5 exists to prevent, and unwinding a stricter rule after users have adapted their configs is a second breaking change. Unicode normalization (NFC/NFD) is **not** applied — only case folding — and the written filename keeps the user's exact bytes, preserving `builder.py:285-288`'s no-normalization rule on the write side.

### Output file shape

- **D-06:** Every content file carries the preamble `writer.py:208-218` prepends to included documents today — the four `@preview` imports plus `#show: codly-init.with()` and `#codly(languages: codly-languages)` — unchanged — **Reversibility:** reversible — for included documents this is exact status-quo preservation, and only master documents gain a preamble they did not have. Whether the resulting double `codly-init` application (wrapper and content both) is harmless must be settled by the GATE-01 fixture rather than assumed; the imports themselves cannot be dropped because `#include()` does not inherit imports from the parent file.

- **D-07:** The `-b typst` builder reports the wrapper files it wrote and names them as the files to compile — **Reversibility:** reversible — `-b typstpdf` already emits `Compiling N master document(s)` and `Generated PDF`, so this is the missing symmetric message on the markup-only builder. After the split the output directory holds roughly twice as many files and nothing in a filename distinguishes a wrapper from a content file.

### Forward compatibility

- **D-08:** A wrapper resolves its title and author from the entry it is being generated for, read positionally, not through `writer.py:24`'s `_resolve_entry_element()` docname first-match lookup — **Reversibility:** reversible — wrappers are per-entry objects after the split, so the docname search is both unnecessary and wrong for D-04's repeated-docname case, where it would give the second wrapper the first entry's title and author. Doing it now avoids rewriting this path when CONF-13 lands.

- **D-09:** The fifth tuple element stays accepted and ignored in this phase and must not be repurposed — **Reversibility:** reversible — REQUIREMENTS.md's rewritten CONF-13 reserves that position for the named template key, a decision closed on 2026-08-11 against the Sphinx 9.1.0 source. Any use of it here would have to be undone.

### Claude's Discretion

- Which files the `typstpdf` builder compiles to PDF. Wrappers only is the natural continuation of today's "only master documents are compiled" rule (`builder.py:967`); content files carry no template and compiling them would produce partial PDFs and double the build time.
- Where the unified validator lives, as long as D-02's before-write timing and D-03's single-code-path property hold, and as long as `TypstBuilder` owns it so `TypstPDFBuilder` inherits identical behaviour rather than re-implementing it.
- The exact wording of every new warning and error message.

### Folded Todos

- `.planning/todos/pending/2026-08-05-a-master-that-is-also-a-toctree-child-is-unrepresentable.md` (`resolves_phase: 47`) — "A master listed in typst_documents that is also another master's toctree child does not compile, and would re-expand its template mid-body if it did". This is B-1 plus B-2, covered by COMP-03 and COMP-04.
- `.planning/todos/pending/2026-08-04-duplicate-typst-documents-target-silently-drops-a-master.md` (`resolves_phase: 47`) — two entries with the same target silently drop one master's body. Covered by BLD-02, and by D-03 it now shares the unified validator with every other collision kind.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and constraints

- `.planning/ROADMAP.md` §"Phase 47" (lines 440-521) — the phase goal, the OUT-01 reversal note, the five success criteria, and the `**UI hint**: no` override
- `.planning/ROADMAP.md` §"Binding constraints" (lines 345-412) — constraint #2 (push the branch to `origin` in this phase), #4 (GATE-01 and its non-fatal amendment), #6 (no laundered gates — expected wrapper/content structure derived from first principles and written down before running the new emitter), #7 (no new `typst_*` config value, four `@preview` packages), #8, #9
- `.planning/REQUIREMENTS.md` — COMP-01..COMP-04, OUT-01..OUT-03, BLD-02..BLD-04 are this phase's ten requirements; CONF-13 (Future) reserves the fifth tuple element and records why v0.8.0 ships with one global template for every master
- `.planning/PROJECT.md` §"Current Milestone" (lines 23-157) — every premise measured live on 2026-08-11, in particular that masters are not concatenated (each produces its own independent PDF) and that two alternative designs were measured, rejected and superseded

### Published contracts this phase changes

- `docs/source/user_guide/configuration.rst:43-79` — the `typst_documents` tuple contract, element by element. Element 2's "A path component is not supported" is what OUT-01 reverses; element 5's "accepted and ignored" is what D-09 preserves
- `docs/source/user_guide/configuration.rst:211-272` — the `params` precedence rule and its `.. warning::`. Explains why a declared `params` discards each entry's own title and author, the limitation v0.8.0 ships with

### Code this phase rewrites

- `typsphinx/writer.py:96-126` — `_is_master_document()`, which must be gone (verified by repo-wide grep, per success criterion 1)
- `typsphinx/writer.py:204-221` — the included-document preamble D-06 generalizes to every content file
- `typsphinx/writer.py:24-73` — `_resolve_entry_element()`, whose docname first-match lookup D-08 bypasses for wrappers
- `typsphinx/builder.py:156-288` — `_resolve_output_stem()`, holding the D-06/D-07 path guard OUT-01 reverses, the OUT-02 security guard that stays, and the CR-01 collision block D-03 replaces
- `typsphinx/builder.py:290-323` — `_directory_preserving_relpath()`, implementing Phase 44's D-05 docname-directory forcing that OUT-01 removes
- `typsphinx/builder.py:28-47` — `_default_typst_documents()`, the derived five-element default entry
- `typsphinx/builder.py:960-1069` — `TypstPDFBuilder.finish()`, the existing aggregate-failures-then-one-`ExtensionError` pattern D-02 mirrors, and the read-back path that must follow the wrapper

### Tests whose expectations move

- `tests/test_typst_documents_collision_gate.py` — real `sphinx-build` subprocess gate for CR-01, currently asserting warn-and-fall-back
- `tests/test_builder_output_stem.py` — stem resolution including CR-01 cases at lines 334 and 352
- `tests/test_preview_version_sync.py` — pins the four `@preview` versions across `writer.py`, `template_engine.py` and `templates/base.typ`; the only place exact strings stay legitimate under binding constraint #6

### Project conventions

- `CLAUDE.md` — the `@preview` three-site version-sync hazard, the `tox-uv-bare` pin, the typing-import modernization ban, and the mandatory worktree-isolated execution protocol for every executor

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `TypstPDFBuilder.finish()`'s failures-list-then-single-`ExtensionError` pattern (`builder.py:1007-1069`) is the shape D-02 needs, one build stage earlier and on the base builder so both builders inherit it.
- `_compute_template_import_path()` (`writer.py:128-174`) already computes a depth-only relative path from a document to the outdir-root `_template.typ`, with no string equality against the reserved basename. Wrapper-to-content include paths need the same depth-based reasoning, and success criterion 2 requires those paths be computed from the wrapper's **resolved** output location rather than the master docname.
- `_default_typst_documents()` (`builder.py:28-47`) already emits a five-element entry, so any entry-shape handling must tolerate both four and five elements.

### Established Patterns

- Guard conventions are duplicated deliberately across `_is_master_document()`, `_compute_master_included_docnames()` and `_resolve_output_stem()`, each skipping a malformed entry rather than indexing it (`writer.py:114-121`). The unified validator must keep that tolerance — a malformed entry is `finish()`'s to report.
- `typst_template_function` accepting `str | dict` (`template_engine.py:251-264`) is this project's precedent for a type-dispatched config value, and the presence-of-key rather than truthiness predicate is an established habit worth preserving.
- No Unicode normalization, case folding or transliteration is applied to a written stem (`builder.py:285-288`). D-05 adds case folding to **comparison only**; the write side keeps this rule.

### Integration Points

- `get_target_uri()` (`builder.py:337-366`) is deliberately docname-based and must stay so — it is a round-trip identity for `_resolve_xref_docname`, and every emitted label is namespaced by source docname via `_namespace_label`. The wrapper rename must not leak into it.
- `builder.py:578` and `builder.py:929` both call `_resolve_output_stem`; both are write/read-back sites that must agree with the new wrapper placement.
- `master_included_docnames` and `_included_docnames` (`builder.py:99-116`) belong to Phases 48 and 49 respectively. This phase does not remove them.

</code_context>

<specifics>
## Specific Ideas

- The BLD-04 case fixture should use a target such as `Manual.typ` against a docname `manual`, per success criterion 4.
- The B-1 fixture must use a **nested** master whose target basename differs from its docname, so the wrapper's include paths are proven computed from the resolved output location rather than the raw docname — the exact way B-1 could be reintroduced one level up.
- Open question #3 (is B-2's mid-body template re-expansion a compile fatal or a compiles-fine-but-wrong-output defect) is owned by this phase but is closed by **measurement on the unfixed tree before any fix**, not by discussion. Its answer selects the GATE-01 RED shape for COMP-04.

</specifics>

<deferred>
## Deferred Ideas

- **Per-entry template configuration via a named template key in the fifth tuple element.** Raised during this discussion, designed, and recorded as the rewritten CONF-13 in `.planning/REQUIREMENTS.md` (commit `a54b794`). Deferred to its own milestone by owner decision on 2026-08-11 — v0.8.0 stays composition-only. D-09 keeps the slot free for it.
- **The global-`params` silent discard.** Because `typst_template_function`'s `params` is global and documented as the complete, exclusive parameter set, a multi-master build discards each entry's own title and author with no warning and renders every master with the same title page. Owner decision on 2026-08-11 was **no change in v0.8.0** — not even a warning. It ships as a limitation and is resolved by CONF-13.

### Reviewed Todos (not folded)

- `2026-08-05-shared-document-silently-dropped-from-all-but-first-master.md` — `resolves_phase: 49` (defect A, the include graph)
- `2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir.md` and `2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri.md` — `resolves_phase: 50` (IMG-01, IMG-02)
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — `resolves_phase: 46`, already closed
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — `resolves_phase: null`, Future requirement QUA-06

</deferred>

---

*Phase: 47-Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection*
*Context gathered: 2026-08-11*
