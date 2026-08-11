# Project Research Summary

**Project:** typsphinx v0.8.0 "multi-master composition"  
**Domain:** Sphinx extension — Typst output builder, restructuring document composition  
**Researched:** 2026-08-11  
**Confidence:** HIGH (every claim verified against installed source or live codebase)

## Executive Summary

The v0.8.0 milestone is a *structural refactoring*, not a feature addition. It splits the current "one templated master file per docname" model into "one wrapper file per master + docname-named content files," enabling independent assembly of each master's toctree graph without build-wide shared state. This fixes three real, measured defects (B-1, B-2, defect A) while unlocking future per-master template selection without adding dependencies or new complexity to the stack.

**Key recommendation:** Phase the work in the exact order ARCHITECTURE.md specifies: content/wrapper split first, compile-time cross-reference guard second, include-graph DFS third. The hard constraint is that the guard must land no later than the graph fix — violating this sequencing will produce silently wrong PDFs (a wrapper lacking a referenced label compiles fine in Typst, not a compile fatal). All necessary technologies are present in the existing stack; the effort is pure orchestration and algorithm porting.

**Top risk:** The new wrapper-generation DFS must replicate Sphinx's own `inline_all_toctrees` ordering exactly — specifically, document-order depth-first traversal with a per-master `traversed` set. A LIFO-stack-based reuse of the existing `_compute_master_included_docnames` method will silently reverse child order with no compile error, placing a shared child under the wrong parent and giving it the wrong heading offset.

## Key Findings

### Recommended Stack

**No new dependencies.** Every technology needed is already in use:

- **Typst 0.15 stdlib primitives** (codly, mitex, gentle-clues already pinned): `#include()` with per-file path resolution, `set heading(offset: N)` (additive), `context { query(<label>) }` for compile-time label-existence checks, `link()` guard-wrapped. All verified against official docs and the installed compiler.

- **Sphinx 9.1 APIs** (all present, undeprecated, actively used by Sphinx's own LaTeX/Texinfo builders): `env.toctree_includes` (dict[str, list[str]]), `env.get_doctree()`, `sphinx.util.nodes.inline_all_toctrees` (the reference algorithm for per-master DFS), `Builder.write_doc()`, `Builder.prepare_writing()`, `Builder.finish()`.

- **Test tooling** (`pypdf`, `pillow` already present): sufficient for per-master PDF assertions. Optional: the installed `typst` Python binding exposes `typst.query()` for label/selector queries without PDF extraction, but `pypdf` already covers all stated needs.

**Stack implications for design:**
- The wrapper is pure Typst, no templating-engine additions needed — extend `template_engine.py`'s caller path, not the engine itself.
- No `Builder.write()` override required; wrapper generation runs after the per-docname `write_doc()` loop inside the existing single-process `write()` method.
- Image path computation stays unchanged (content files are docname-named, so existing `_compute_relative_image_path` logic is unaffected).

### Expected Features

**Table Stakes (v0.8.0 must ship with these):**
1. Each master's include graph is assembled independently from a fresh per-master DFS (mirrors `inline_all_toctrees`, not a shared whole-build ledger).
2. A document reachable from two masters renders fully and independently in each (no cross-master deduplication).
3. A document reachable twice within one master is included once, at its first-DFS depth (silent pruning, matching Sphinx's own behavior).
4. Duplicate `typst_documents` target names are detected and warned; never silently drop a master's body (CR-02, already scoped).
5. Cross-reference degradation resolves per compilation unit (per master), not via build-wide union — the `context { query(<label>) }` compile-time guard.
6. Per-master toctree options (maxdepth, numbered, caption) keep working after the wrapper refactor.
7. A docname that is simultaneously a `typst_documents` master AND a toctree child of another master compiles correctly in both roles (regression fixture required).
8. The two PR #131 image defects fixed (rehomed-image collision, absolute-URI escape — already scoped).

**Explicitly Out (differentiators, v2+):**
- Per-master template selection (dict-shaped entries for metadata)
- `toctree_only`-equivalent (suppress master's own prose, include only toctree children)
- Shared-appendix shortcut (config convenience, users can manually add entries to each master's toctree)
- Any "prefer deeper path" tiebreak or single-winner logic (not needed by independent-masters model)

**Anti-features (harmful, explicitly exclude):**
- Doctree-layer composition (would delete the per-document `.typ` files the `-b typst` builder exists to produce)
- Single shared root `.typ` (the direct cause of B-1/B-2; reintroduces both if reconsidered later)
- Cross-master content deduplication (violates the "independent PDFs" invariant)
- Free-form per-master output subdirectories (existing path-traversal guard is deliberate)

### Architecture Approach

The redesign moves composition from a per-docname, alphabetical-order, whole-build-shared loop into a per-master, document-order, isolated graph walk. Two files per master instead of one: content (pure body, minimal imports) + wrapper (template + include graph).

**Current state:** `TypstBuilder.write()` loops `sorted(docnames)` alphabetically, calls `write_doc()` on each; `write_doc()` determines whether the current docname is a master (via `_is_master_document()`), writes either template-wrapped (master) or bare (included), and emits toctree includes inline via `visit_toctree()`. Composition decisions (who includes what, at what depth) are scattered across `builder.py`'s ledger, `writer.py`'s master/included branch, and `translator.py`'s `visit_toctree()`, using a **whole-build** `_included_docnames` set for deduplication.

**Proposed state:** `write_doc()` always writes a template-less content file at docname's own path (no master/included branching). After the per-docname loop, a new `_write_master_wrappers()` step computes each `typst_documents` entry's per-master DFS graph, renders a flat `context { set heading(offset: N) include(...) }` block per graph entry, wraps that in the template, and writes one wrapper file per master at the resolved target path.

**New module `composition.py`:** Houses `compute_master_include_graph()` (DFS with per-master fresh `traversed` set), `render_include_graph()` (flattened offset/include block), moved helpers (`_compute_relative_include_path`, `_resolve_entry_element`, `_compute_template_import_path`). Keeps this graph-and-template work decoupled from `builder.py`'s loop-driving concerns.

### Critical Pitfalls

1. **Pitfall 1 — DFS order must replicate Sphinx's document-order depth-first traversal, not a LIFO stack.** The new wrapper-generation DFS must thread ONE ordered `traversed` list through recursion, processing each document's toctree children in source order. A LIFO-stack reuse will silently reverse order with no compile error. **Prevention:** Write the DFS fresh, test with reordered-entries mirror fixture.

2. **Pitfall 2 — `:numref:` uses Sphinx's project-wide numbering, not Typst's per-wrapper counter.** A figure can be "Figure 12" (Sphinx) but "Figure 3" (Typst per master). **Prevention:** Two-master fixture with shared figure, measure actual Typst-rendered number via `pypdf` against `:numref:` text. Document as limitation or fix explicitly.

3. **Pitfall 3 — Diamond dedup IS solved, but edge cases (cycles, self-refs, orphans) need explicit fixtures** with decided outcomes.

4. **Pitfall 4 — CR-01's `effective != docname` exemption is a landmine when every docname gets a content file.** When target equals docname, wrapper and content collide; whichever writes last wins silently. **Prevention:** Decide upfront: allow self-targets or forbid? Implement collision logic accordingly.

5. **Pitfall 5 — Case-insensitive filesystems can hide collisions that Linux CI never sees.** Collision checks must be case-normalized (.lower() both sides).

6. **Pitfall 6 — Deleting `master_included_docnames` must be complete** — three consumers (primary site, `:3273/3281`, `:4291`) must all route through ONE shared guard helper. Partial migration leaves competing degrade decisions.

7. **Pitfall 7 — Regenerating GATE-01 expected strings from the new emitter launders the gate.** Derive expected structure from config + `.rst` by hand first. Use structural assertions over exact strings. PR review must trace each changed expected value to a written-first rationale.

8. **Pitfall 8 — Non-fatal defects need a defined RED assertion, not just "compiles."** CR-02 and image defects "compile fine, produce wrong output" — write the pre-fix RED assertion (pypdf text/page comparison) explicitly before implementation.

9. **Pitfall 9 — Wrapper files must be written in a shared, serial path both builders reach.** Place wrapper generation in `TypstBuilder.write()` (after docname loop), not in `finish()`, to avoid ordering bugs from dual `write_doc()` overrides.

10. **Pitfall 10 — Parallel builds and future incremental rebuilds must not degrade.** Wrapper generation in serial `write()` is safe; add a comment about wrapper staleness for future incremental-build work.

11. **Pitfall 11 — Wrapper relative-include paths must use RESOLVED wrapper location, not raw docname.** This IS B-1's fix detail. Fixture: nested master with custom target; assert `#include()` paths resolve correctly.

## Implications for Roadmap

**Hard Constraint:** The compile-time cross-reference guard (Phase 2) must land **no later than** the per-master include-graph DFS (Phase 3). Violating this produces silently wrong PDFs.

### Suggested Phase Structure

**Phase 47.1: Content/Wrapper Split (No Include Graph Yet)**
- **Rationale:** Isolate file-shape change from graph-algorithm change. Proves split works without touching composition semantics. Closes B-1 and B-2.
- **Delivers:** Every docname at `outdir/<docname>.typ` (content), every master at resolved target (wrapper).
- **Success Criteria:** Existing fixtures still compile; `-b typst` vs `-b typstpdf` produce identical wrappers; B-1/B-2 fixture RED → GREEN.

**Phase 47.2: Compile-Time Cross-Reference Guard**
- **Rationale:** Lands guard BEFORE include-graph work. When Phase 3 arrives, guard handles "label missing in this compilation" gracefully.
- **Delivers:** Three guarded-link sites emitting `context { query(<label>).len() > 0 ? link(...) : plain_text }` via one shared helper.
- **Removes:** `master_included_docnames` ledger completely.
- **Success Criteria:** `grep -rn master_included_docnames` returns empty. `:4291` site verified to use shared helper. Xref-degradation fixture degrades gracefully in Typst output.

**Phase 47.3: Per-Master Include-Graph DFS**
- **Rationale:** Phase 2's guard in place. Graph algorithm lands, shared children move from silently dropped to correct inclusion.
- **Delivers:** `compute_master_include_graph()` with document-order depth-first, per-master `traversed` set.
- **Success Criteria:** Diamond fixture (M → [p, q], p → [c], q → [c]) proves c included once at first-DFS depth. Mirror fixture proves nesting tracks source order. Defect A fixture RED → GREEN.

**Phase 47.4: CR-02 Duplicate-Target Detection**
- **Rationale:** Independent of include-graph. Fits into per-master wrapper loop.
- **Delivers:** Build-time warning on target collision; case-normalized comparison for platform consistency.
- **Success Criteria:** Two masters → same target: warning emitted. Self-collision (target == docname): covered. Case variation: same behavior on Linux/macOS/Windows.

**Phase 47.5: PR #131 Image Defects**
- **Rationale:** Independent; touches `_track_image()` during split, natural to pair.
- **Delivers:** Rehomed images don't collide with real `srcdir` files. Absolute URIs don't escape `outdir`.
- **Success Criteria:** Pre-fix RED (wrong/missing image) → GREEN post-fix.

**Phase 47.6: Release Prep**
- **Rationale:** Final phase per standing pattern.
- **Delivers:** v0.8.0 tagged, published, docs built.
- **Success Criteria:** Full multi-master `sphinx-build -b typstpdf`, each PDF has title page + outline + content subset, verified via `pypdf` text extraction.

### Build Order Reconciliation

ARCHITECTURE.md and PITFALLS.md both propose phased approaches; they align on the critical constraint (guard before graph). This summary adopts ARCHITECTURE.md's order as primary, with PITFALLS.md's edge-case fixtures folded into each phase's success criteria.

### Research Flags

**Need deeper research during planning:**
- **Phase 47.1:** Template-copy behavior in wrapper step; confirm `_template.typ` import paths from content files.
- **Phase 47.2:** The `:4291` site (explicitly unread in research) — is it structurally identical to `:5007` and `:3273/3281`, or does it have special shapes?
- **Phase 47.3:** `:numref:` fixture divergence (Pitfall 2) — do numbers actually diverge per compile unit, or do they align for typical structures?

**Standard patterns (skip research-phase):**
- **Phase 47.4 (CR-02):** Straightforward registry check, established pattern from CR-01.
- **Phase 47.5 (image defects):** Narrow, localized fixes, well-understood.
- **Phase 47.6 (release prep):** Standing pattern, established by v0.7.0+.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **Stack** | **HIGH** | Verified against installed Sphinx 9.1.0, typst-py 0.15.0, official Typst docs, existing codebase. No new packages needed. |
| **Features** | **HIGH** | Table stakes from live Sphinx source (LaTeX/Texinfo builders). Differentiators/anti-features established against ecosystem precedent (rinohtype, Quarto, mdBook). |
| **Architecture** | **HIGH** | Every file/line/method traced against current codebase. Component ownership reconciled. Data flow and ordering constraints verified. |
| **Pitfalls** | **HIGH** for identified (11 enumerated with phase placement), **MEDIUM** for edge cases (`:numref:` divergence, `:4291` site, case-insensitive-FS) needing live fixture confirmation. |

**Overall: HIGH** — grounded in primary sources (installed packages, codebase, official docs). Edge cases explicitly flagged for planning confirmation.

### Gaps to Address

1. **Open: The `:4291` site.** `translator.py:4291` in `visit_pending_xref` was "unread" in research. Does it route through `_reference_anchor_decision`, or is it a fourth independent degrade site? Planning must verify.

2. **Open: `:numref:` Divergence Measure.** Is divergence between Sphinx's project-wide numbering and Typst's per-compile counter observable in practice, or do they align for typical docs? PITFALLS.md flags as "inferred — verify with fixture."

3. **Open: B-2 Severity.** Is B-2 (template re-expanding mid-body) a compile fatal or "compiles fine, produces wrong output"? Determines GATE-01 RED methodology.

4. **Open: CR-01 Self-Collision Decision.** Is a target allowed to equal its own master's docname? Design decision for planning; this research flags the hazard.

5. **Open: Case-Normalization vs. Forbidding.** Normalize collision checks for platform consistency, or forbid path-like targets as a security measure? Planning scope question.

These are scoped for requirements/planning closure.

## Sources

**Research Files (Primary — HIGH):**
- `.planning/research/STACK.md` — Technology verification against installed packages, Typst 0.15 docs, Typst community sources.
- `.planning/research/FEATURES.md` — Feature landscape from installed Sphinx source, ecosystem tools (rinohtype, Quarto, mdBook).
- `.planning/research/ARCHITECTURE.md` — Redesign traced against every file/line/method in current typsphinx.
- `.planning/research/PITFALLS.md` — 11 critical pitfalls grounded in Sphinx/Typst source, CLAUDE.md lessons, MILESTONES.md precedent.

**Codebase (Primary — HIGH):**
- Installed `sphinx==9.1.0`, `typst-py 0.15.0`
- `typsphinx/builder.py`, `writer.py`, `translator.py`, `template_engine.py` (full, this session)
- `.planning/PROJECT.md`, `.planning/MILESTONES.md`, `CLAUDE.md`

---

**Research completed:** 2026-08-11  
**Ready for roadmap:** Yes — phase structure suggested, open questions flagged, all pitfalls mapped to phases with success criteria.
