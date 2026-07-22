# Codebase Concerns

**Analysis Date:** 2026-07-22

## Tech Debt

### Package-vs-Template Routing Logic (BUG-A through BUG-F)

**Issue:** Multiple subtle bugs in the routing between Typst Universe package imports and custom template handling were masked by weak tests that only asserted presence, not behavior.

**Files:** `typsphinx/template_engine.py` (BUG-A origin), `typsphinx/writer.py`, `typsphinx/builder.py`

**Impact:** 
- BUG-A: writer and builder disagreed about whether `_template.typ` exists, causing package-alone configurations to be unbuildable
- BUG-B: package-only masters had unrequested date parameters injected
- BUG-C: `typst_authors` rendered as quoted string instead of native array
- BUG-E: auto-derived defaults were not overridden by explicit configuration
- BUG-F: essential @preview imports were missing on package-only masters

**Fix approach:** Phase 22.2 centralized the routing decision into a single `resolve_package_for_engine()` function (`template_engine.py:15-39`) so writer/builder cannot re-diverge. Tests now count imports, not just assert presence. Regression fixtures confirm the fix works end-to-end via real `typst.compile()`.

---

## Known Bugs Fixed but With Caveats

### @preview Package Version Sync Hazard

**Issue:** The four Typst Universe `@preview` package versions (codly, codly-languages, mitex, gentle-clues) are declared in **three** places that must stay in lockstep.

**Files:** 
- `typsphinx/writer.py` (lines 143-146)
- `typsphinx/template_engine.py` (lines 374-377)
- `typsphinx/templates/base.typ`

**Mitigation:** `tests/test_preview_version_sync.py` asserts all three agree and fails CI loudly on desync. However:
- No automated enforcement during development (only at test-run time)
- A developer could bump one location and commit without running tests
- The mitigation is defensive, not preventive

**Fix approach:** Document in CLAUDE.md (done), enforce in CI (done), but a preventive hook (pre-commit) is not implemented.

---

### Nested Master Template Import Path (CR-01, Fixed in Phase 22.1)

**Issue:** Template import paths for nested masters used a sentinel-based approach that could collide with real directory names.

**Files:** `typsphinx/writer.py:_compute_template_import_path()`

**Impact:** A master whose directory is literally named `_template` would produce a malformed import path like `../.typ` instead of `../_template.typ`.

**Fix:** Phase 22.1-04 replaced the sentinel logic with a pure depth-based computation (`PurePosixPath(docname).parent.parts`), eliminating the collision risk. Pinned by a 7-case matrix and real-compile gate over `tests/fixtures/template_named_dir_master/`.

---

## Fragile Areas

### Buffer-Swap State Machine (Multiple Files)

**Issue:** The translator uses a buffer-swap idiom to capture nested content (figures, footnotes, list items) by temporarily redirecting `self.body` output and restoring it afterward. This is a powerful but brittle pattern.

**Files:** `typsphinx/translator.py` (state vars: `_saved_body_for_figure_caption`, `in_figure`, `in_caption`, `in_list_item`, `list_stack`, `in_table`, `in_thead`, `in_paragraph`, etc.)

**Fragility:** 
- A forgotten `restore()` leaves downstream content in the wrong buffer
- Nested buffer-swaps (figure inside list item inside table) compound complexity
- Separator state (`paragraph_has_content`, `list_item_has_content`) must be saved/restored across swaps or subsequent elements lose their spacing
- Line 1906-1913 (footnote buffer-swap) shows the actual failure pattern: the swap clobbered `in_paragraph`/`paragraph_has_content`, breaking any footnote followed by trailing text

**Coverage:** Phase 14 real-compile gate caught this bug; every buffer-swap site should have equivalent coverage.

**Safe modification:** When adding a new buffer-swap, save/restore ALL state vars that affect separator emission, not just the body. Test via real `typst.compile()` with content before/after.

---

### Translator Size and Complexity

**Issue:** `typsphinx/translator.py` is ~4,973 lines with ~140 `visit_*`/`depart_*` methods, making it difficult to reason about state transitions.

**Files:** `typsphinx/translator.py`

**Fragility:**
- State machine spread across many methods with global state
- Buffer-swap nesting logic is easy to break
- Separator emission logic (inline vs. block) is complex and error-prone
- No structural abstraction; all state is file-level

**Scaling limit:** Adding support for new node types requires understanding the entire state machine. Past attempts to refactor were deferred due to risk.

**Safe modification:** Isolate new handler logic in its own methods, minimize state-machine coupling, add buffer-swap safety assertions, test via real-compile gates.

---

### CSS Length Converter Edge Cases

**Issue:** The `_convert_length_to_typst()` helper (Phase 16, LEN-01) converts CSS lengths to Typst units, but has unsupported unit fallback behavior.

**Files:** `typsphinx/translator.py:_convert_length_to_typst()`

**Edge cases:**
- Unsupported units (e.g., `ch`, `vw`, `vmin`) are silently dropped (return `None`)
- Callers must handle `None` gracefully; missing checks could silently lose width specifications
- Percentage units are passed through but may not work in all Typst contexts (e.g., `table(width: 50%)`is invalid)

**Fix approach:** Audit all call sites for `None` handling; add warnings for unsupported units. Test via real-compile gates on edge-case lengths.

---

### Image URI Glob Resolution

**Issue:** Sphinx's read-phase ImageCollector leaves `*`-glob URIs (e.g., `.. figure:: _static/foo.*`) unresolved. The builder's `post_process_images()` must glob-expand them to concrete candidates.

**Files:** `typsphinx/builder.py:post_process_images()` (lines 390-450)

**Fragility:**
- Glob expansion relies on file discovery at build time; missing files silently degrade to first-match
- Preference order is hardcoded (SVG > PNG > GIF > JPEG) with no user override
- A glob that matches zero files leaves the original `*` URI in the Typst source, causing a runtime compile error
- No degrade-to-plain-text path for truly missing images

**Fix approach:** Add logging for glob expansion results, consider adding a config option for preference order, add a degrade path for zero-match globs.

---

## Known Rendering Fidelity Gaps

### 13 Medium/Low Silent Mis-Render Findings (v0.6.1 Audit)

**Issue:** A human-assisted visual audit of Sphinx's 151-docname `doc/` tree PDF catalogued 15 systemic silent mis-render findings (1 high / 12 medium / 2 low).

**Files:** Findings are catalogued in `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`

**High-Severity (Fixed):**
- F12: Wide-table glyph collision + right-margin clip (Phase 18, fixed via fr-weighted `columns:` + U+200B injection)

**Medium/Low Severity (Deferred):**
- F1, F7, F13, F14, F15: Lost inter-block separation (adjacent paragraphs, `desc_signature`s, definitions)
- F2, F3, F5: Lost intra-signature token spacing (`desc_annotation` prefixes, C/C++ tokens, `:type:` colons)
- F6: Right-margin overflow / no wrapping (long inline-literal runs clipped mid-token)
- F9: Paragraph reflow lost (soft newlines render as hard breaks)
- F11: Codly config wrapper leak (literal_block with caption leaks wrapper as visible text)
- F8, F10: Meaning-bearing inline styling (external links flatten to plain text, PEP separators inject hover-title)
- F4 (rejected): Findings not accepted; out of scope

**Impact:** Silent mis-renders that compile clean but look wrong in the PDF. Users may not notice until careful visual inspection.

**Fix approach:** Each finding requires root-cause analysis + a translator handler fix + a real-compile regression fixture. Grouped by root cause into clusters A–F for Phase 21+ planning (already shipped). Non-blocking for v0.6.2 release.

---

## Code Review Findings (Recent Phases)

### Phase 21 Advisory Warnings (Non-Blocking)

**WR-01 — FID-10 ZWSP Guard Breadth:** The U+200B zero-width-space break injection guard for wide inline-literals is broad; may over-apply to content that doesn't overflow.

**WR-02 — FID-14 astext Heuristic:** The `astext()` fallback for extracting PEP separator content is a heuristic; may misfire on complex nested structures.

**WR-03 — visit_Text Unit Coverage:** Unit tests for `visit_Text` do not cover all inline-context combinations.

**Status:** Accepted as release-polish candidates; no blocking blocker; tracked in `.planning/milestones/v0.6.1-phases/21-rendering-fidelity-fixes-stage-2/21-REVIEW.md`.

---

### Phase 22.2 Code Review Findings (Resolved)

**CR-01 — Double-Emission of @preview Imports (Fixed):** The D-02 essential-import hoist in `template_engine.py:render()` (lines 362-381) was never reached on the inline-default path, but the pre-existing test counted presence without checking for duplicates. Fixed to emit exactly once by guarding the hoist with `if not will_inline_default_template:`.

**WR-04 — Package-vs-Template Routing Re-Divergence (Fixed):** `resolve_package_for_engine()` is now the single source of the routing rule, preventing writer/builder from re-diverging into another BUG-A.

**Status:** All 6 findings resolved before phase close (`.planning/milestones/v0.6.2-phases/22.2-dead-config-value-sweep/22.2-REVIEW.md` §Resolution).

---

## Security Considerations

### No Critical Threats Outstanding

**Status:** Phase 22 security review closed 9/9 threats with `threats_open: 0` (`.planning/milestones/v0.6.2-phases/22-issue-117-pdf-naming-and-deprecation/22-SECURITY.md`).

**Key mitigations:**
- Path traversal guards in `_resolve_output_stem()` (D-06/D-07) prevent `typst_documents` target names from escaping the output directory
- Escape of Typst string literals via `escape_typst_string()` prevents inline-code-injection via docutils text nodes
- SkipNode gating on `config.todo_include_todos` prevents work-notes from leaking into public output

---

## Performance Bottlenecks

### Large Test Suite Runtime

**Issue:** Test suite is ~26,561 lines across 40+ test files; full run takes time.

**Files:** `tests/test_*.py`

**Characteristics:**
- ~20–30 tests marked as `slow` (e.g., `test_corpus_compiles_with_no_fatal_error`) invoke real `typst.compile()`
- Full suite ~560 tests; corpus gate alone requires a real ~14.4 MiB PDF compile
- Integration tests clone Sphinx's `doc/` tree (~400 files) and build through typsphinx

**Scaling limit:** Adding more corpus-level acceptance gates will slow CI further. Real-compile gates are necessary for correctness but expensive.

**Mitigation:** Tests can be run without slow tests via `pytest -m "not slow"`. CI runs full suite; local dev can skip slow tests during iteration.

---

### Sphinx Build Time on Large Doc Sets

**Issue:** Building Sphinx's own `doc/` tree through `typstpdf` takes ~10+ seconds per full build (docutils read phase + typsphinx write phase + typst compile).

**Impact:** Tight iteration loop on large docs is slow; minor changes require 10+ second rebuilds.

**Scaling limit:** A 500-docname tree would be significantly slower.

**Mitigation:** Sphinx's incremental build system helps; repeated builds of unchanged docs are faster. For development, test against smaller fixture sets.

---

## Environment-Specific Issues

### NixOS Sandbox Friction with uv Subprocess Tests

**Issue:** The NixOS dynamically-linked `uv` binary fails to launch in subprocess tests, producing ~45 environment-caused failures in each phase.

**Files:** Affects integration tests that spawn `sphinx-build` as a subprocess (e.g., `tests/test_integration_*.py`)

**Impact:** 
- Per-phase verification requires repeated environment-caused failure triage
- Real regressions are hard to distinguish from sandbox failures
- Each phase incurs a ~30-min analysis tax

**Status:** Documented in memory as `NixOS sandbox test env` but no reusable shim implemented.

**Fix approach:** A documented in-sandbox `uv` shim or wrapper that the test framework can use would save repeated per-phase investigation.

---

## Deferred Work (Next-Milestone Backlog)

### CFG-01 — User-Configurable @preview Package Versions

**Issue:** The four bundled `@preview` package versions are hardcoded and updated by hand.

**Files:** Versions in `writer.py`, `template_engine.py`, `templates/base.typ`

**Impact:** Users cannot experiment with newer `@preview` versions without forking the extension.

**Scope:** v2 / post-v0.6.2

**Fix approach:** Add `typst_preview_package_versions` config dict to allow per-package override; validate in CI that overrides compile cleanly.

---

### XOS-01 — Cross-OS `docs-pdf` CI Coverage

**Issue:** CI currently runs `docs-pdf` only on Linux.

**Files:** `.github/workflows/docs.yml`

**Impact:** macOS/Windows filesystem quirks (Unicode normalization, path handling) are untested.

**Deferred:** Phase 22 UAT accepted filesystem Unicode normalization (HFS+/APFS NFD vs. byte-preserving NFC) as documented out-of-scope OS behavior. Cross-OS CI coverage deferred to v2.

---

### Phase 22.3 — Builder Warning Hardening

**Issue:** The `finish()` method has multiple warning paths that need formalization.

**Files:** `typsphinx/builder.py:finish()` (lines 867-948)

**Current state:** Warning paths exist for missing `typst_documents`, malformed entries, missing `.typ` files, but the behavior is documented in the docstring (D-04 "no silent success") and needs verification that warnings align with the code.

**Status:** Pending Phase 22.3 implementation.

---

## Architectural Constraints

### Single-Threaded, Event-Loop-Free Architecture

**Issue:** The translator is not designed for concurrent use; all state is instance-level with no synchronization.

**Impact:** Sphinx's `allow_parallel = True` (builder.py line 37) enables parallel builds, but each process gets its own translator instance, so no actual sharing occurs. Safe but serialization is per-Sphinx-process, not per-translator.

**Scaling limit:** A 1000-docname tree building with 4 parallel Sphinx processes would be 4× as fast as single-threaded, but each process would still serialize its own docnames.

---

### Global State in Module Initialization

**Issue:** `typsphinx/__init__.py:setup()` registers config values and builders at import time.

**Impact:** A test that imports typsphinx twice (e.g., two independent Sphinx app instances) will register twice without de-duplication.

**Mitigation:** Tests use `temp_sphinx_app()` fixture which creates fresh Sphinx apps, avoiding re-registration collisions.

---

## Test Coverage Gaps

### Buffer-Swap Patterns Not Fully Covered

**Issue:** Buffer-swap idiom is used in ~20 places but only ~5 have real-compile regression fixtures.

**Files:** `typsphinx/translator.py` (state-swap sites), `tests/test_*_render_gate.py`

**Risk:** A new buffer-swap without proper coverage could introduce the footnote-separator-clobber bug again silently.

**Safe modification:** Every new buffer-swap MUST ship with a real-compile fixture that includes content both before and after the swapped block.

---

### Docutils Deprecation Warnings

**Issue:** `docutils 0.22` deprecated `.traverse()` in favor of `.findall()` (a non-deprecated alternative).

**Files:** `typsphinx/translator.py:visit_document()` uses `.findall()` (correct); other `.traverse()` calls may exist.

**Coverage:** Code already handles this; filterwarnings escalates `PendingDeprecationWarning` to error in pytest (pyproject.toml:88-89).

---

## Scaling Limits

### Translator Complexity at 4,973 Lines

**Concern:** Adding new node support requires understanding the entire state machine. Refactoring has been deferred due to risk.

**Examples:**
- Adding a new admonition type requires understanding the `_visit_admonition()` / `_depart_admonition()` state machine
- Adding a new list type requires understanding list nesting, item separators, and buffer swaps
- Adding a new table feature requires understanding column-width logic, thead, tbody, tfoot state

**Scaling limit:** Beyond ~150 visit/depart methods, the risk of state-machine bugs grows exponentially.

**Mitigation:** Existing patterns are well-tested; new handlers should follow established patterns closely and add real-compile fixtures.

---

## Missing Critical Features

### No Graceful Degrade for Unsupported Graphical Nodes

**Issue:** graphviz and inheritance_diagram nodes explicitly skip via `raise nodes.SkipNode`, leaving a blank in the output.

**Files:** `typsphinx/translator.py:visit_graphviz()`, `visit_inheritance_diagram()`

**Impact:** A sphinx project using graphviz will have missing diagrams in the PDF (transparent to the user unless they check carefully).

**Scope:** Graceful degrade (placeholder + warning) is out of scope; these nodes are considered unsupported by Typst.

**Fix approach:** Add a placeholder-image generator or link-out to external SVG, but that's a v2+ feature.

---

## Dependencies at Risk

### typst-py Pinned to <0.16

**Issue:** `typst>=0.15.0,<0.16` is pinned strictly to avoid surprises from major releases.

**Files:** `pyproject.toml:30`

**Risk:** When typst 0.16 is released, a user who bumps it may hit unknown compat issues.

**Mitigation:** The weekly `drift.yml` workflow (DUR-02) would catch the issue and file an alert.

**Fix approach:** When typst 0.16 is released, test against it in a feature branch before bumping the pin in main.

---

### Sphinx 9.1 < 10 Tight Bound

**Issue:** `sphinx>=9.1,<10` is bounded to avoid Sphinx 10.0 compat unknowns.

**Risk:** Same as typst-py; Sphinx 10.0 may have API changes that require work.

**Mitigation:** Weekly drift.yml would alert; test in feature branch before bump.

---

## Anti-Patterns Observed

### Test That Assert Presence Without Counting

**Pattern:** Tests like `assert "@preview/codly:1.3.0" in output` pass even if the import is duplicated 3 times.

**Example:** CR-01 in Phase 22.2 — the `render()` essential-import hoist was double-emitting @preview imports, but tests never failed because they only checked presence.

**Fix:** Use `output.count("@preview/codly:1.3.0") == 1` for exact-count assertions on critical imports.

**Status:** Fixed in Phase 22.2; new tests should avoid this pattern.

---

### Silent Fallback Without Warning

**Pattern:** When an optional feature (e.g., custom template path) is not found, the code silently falls back without warning the user.

**Example:** `template_engine.py:158-161` logs a warning for missing custom templates, but doesn't warn when a @preview package fails to compile.

**Fix approach:** Every fallback should log at least a warning; consider raising an exception for critical paths.

---

## Summary

The codebase is in a **stable, production-ready state** (v0.6.2 shipped). The identified concerns are:
- **Fixed but noted:** Package-routing bugs (BUG-A–F), nested-master template import collision (CR-01)
- **Known and mitigated:** @preview version-sync (test guard), buffer-swap brittleness (real-compile gates), translator complexity (test coverage)
- **Deferred:** 13 rendering-fidelity polish items (audit findings), user-configurable @preview versions (CFG-01), cross-OS CI (XOS-01)
- **Architectural:** Single-threaded design is correct for Sphinx; large test suite is necessary for fidelity
- **Testing gaps:** Buffer-swap patterns could use more comprehensive coverage; some fallback paths are silent

**For future maintainers:** Pay close attention to state-machine correctness in translator.py, always add real-compile fixtures for new node handlers, and keep the @preview version-sync test passing.

---

*Concerns audit: 2026-07-22*
