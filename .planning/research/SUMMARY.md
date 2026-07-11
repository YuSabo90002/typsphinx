# Project Research Summary: typsphinx v0.6.0 "Real-World Robustness"

**Project:** typsphinx v0.6.0 (Issue #114 fix + high-frequency dropped-node support)  
**Domain:** Sphinx→Typst translator robustness (docutils node handler development)  
**Researched:** 2026-07-11  
**Confidence:** HIGH (grounded in direct codebase read + official Typst/docutils/Sphinx specs)

## Executive Summary

typsphinx v0.6.0 is a narrow, single-file maintenance milestone focused on two fatal compile-blocking bugs (Issue #114: px-unit and caption-juxtaposition) and twelve high-frequency dropped-node types that silently degrade real-world Sphinx documentation. The recommended approach is **zero new runtime dependencies** — every target node type maps either to native Typst 0.15 stdlib (footnote(), line(), block()) or the already-bundled gentle-clues package, with all work concentrated in `typsphinx/translator.py` (new `visit_*`/`depart_*` methods and one small length-conversion helper). The core risk is that a single malformed node deep in a 900-page corpus (Sphinx's own docs, the acceptance target) aborts the entire PDF build — mitigation requires standing up real-compile acceptance fixtures alongside each node-handler phase, not relying on string-level unit tests that miss syntax errors.

The milestone's gate is empirical: Sphinx's own `doc/` tree must compile cleanly end-to-end through `typstpdf` with no fatal TypstCompilationErrors. This is achievable with high confidence given the stack verification (zero blocked dependencies) and architectural analysis (five established state patterns, one new pre-pass pattern for footnotes), but requires disciplined per-phase validation since one oversight (a missed edge case in a length-conversion, an unescaped caption character, an orphaned parenthesis) will surface only at compile time on the real corpus, not in small fixture tests.

## Key Findings

### Recommended Stack

**No new dependencies, no version bumps needed.** Every target node type is achievable within Typst 0.15 and the already-bundled four `@preview` packages (gentle-clues 1.3.1, codly 1.3.0, codly-languages 0.1.10, mitex 0.2.7). The three-way `@preview` version-sync surface (writer.py / template_engine.py / templates/base.typ) is untouched.

**Core technologies (unchanged from v0.5.0):**
- **Typst 0.15.x** — all target node types map to: (a) native length units (pt, mm, cm, in, em, %), (b) native function calls (footnote(), line(), link(), figure()), or (c) already-supported gentle-clues clue functions (tip, info, warning, danger, error).
- **Docutils 0.22.4 + Sphinx 9.1** — all target node types already exist in the doctree; no version bump needed.
- **Python 3.12–3.13** + **typst-py 0.15.x** — unchanged runtime.

**No new PyPI package, no new @preview package required.** Gentle-clues is reused for versionmodified (added/changed/deprecated/removed) via the existing `_visit_admonition` helper, but rendered as an unboxed italic label (different from the admonition-box convention).

### Expected Features

**Must have (fatal bugs blocking the entire milestone gate):**
- **px/CSS length-unit conversion** (Issue #114 bug 1) — convert `px`/`%`/`em`/bare-unitless docutils image `:width:`/`:height:` values to Typst-valid units before emission (1px = 0.75pt by CSS convention). Non-compliance = hard Typst compile error, aborting the whole document.
- **`:target:`-linked figure invalid juxtaposition fix** (Issue #114 bug 2) — fix buffer-swap in `visit_caption`/`depart_caption` so caption text does not leak as a stray `text(...)` call juxtaposed directly after the image with no separator. Non-compliance = Typst parse error at compile time.

**High-frequency table stakes:**
- **versionmodified** (×972) — render as unboxed italic label + body
- **Empty-URL / refid cross-reference fix** (×596) — extend `visit_reference` to check `refid` for same-document anchors
- **desc_returns, desc_signature_line, desc_optional, desc_inline** (×187 + ×59 + ×6 + ×13) — extend existing `desc_*` family
- **footnote / footnote_reference** — needs doctree pre-pass to index footnote bodies, then emit inline at reference site
- **transition, topic, glossary, line_block, line** — reuse established patterns (line(), `{}` wrapper, no-op pass-through)
- **graphviz / inheritance_diagram graceful-degrade** — explicit `visit_*` + `SkipNode` + logging

### Architecture Approach

**Single-file implementation:** `typsphinx/translator.py` only. Five established state patterns are reused (buffer-swap, dummy-node delegation, `+`-concatenation flags, `{}` list-item block, graceful degrade); one new pattern (document-order pre-pass for footnotes). No changes to writer.py, builder.py, template_engine.py, or templates/base.typ.

**Critical state patterns to maintain:**
1. Buffer-swap (defer content) — used for figure caption fix and footnote pre-pass
2. Dummy-node delegation — used for topic title
3. Code-mode `+`-concatenation flags — used for desc_optional and desc_signature_line
4. List-item-style `{}` blocks — used for topic body, line_block, line
5. Graceful degrade — explicit log + skip for graphviz/inheritance_diagram

### Critical Pitfalls

1. **One bad node aborts entire PDF** — a single malformed width or unescaped caption deep in the corpus is fatal to the whole build, not just one page. Mitigation: real `typst.compile()` fixtures per phase, not string-only tests.

2. **Markup-mode vs. code-mode mismatch** — emitting literal Typst source as inert text (the v0.5.0 admonition precedent) is invisible in string assertions but obvious in PDF. Always decide explicitly and use buffer-swap to render through the normal visitor chain.

3. **Figure-caption double-emission leak (NEW)** — `depart_caption` extracts caption via `node.astext()` but never suppresses normal traversal, so text appears twice: once as stray `text(...)` juxtaposed after `image(...)` (syntax error without separator), once correctly as `caption: [...]`. Fix: buffer-swap in `visit_caption`/`depart_caption` like admonition titles.

4. **Function-call juxtaposition** — Typst code-mode requires `+`, `;`, or newline between expressions; `image(...)text(...)` is a parse error. Any new handler emitting siblings must use `_has_content` flag pattern or wrap content in named parameter.

5. **px→pt is not 1:1** — Typst has no `px` unit. Current code passes `node["width"]` verbatim, emitting `width: 200px` which is a hard compile error. Conversion: `1px = 0.75pt` (CSS canonical). Also handle `%`, `em`, `in`, `cm`, `mm`, `pt` (pass through), `pc` (convert), `ex` (approximate or drop).

6. **Footnote modeling mismatch** — docutils splits footnote into reference (inline) + definition (sibling block), but Typst's `footnote[body]` is a single inline call. Naive port produces doubled or misplaced notes. Fix: pre-pass to index bodies by id, emit `footnote[...]` at reference site, `SkipNode` at definition.

7. **Escaping regimes** — three distinct regimes exist (string-literal escaping, markup-mode escaping, label constraints). Using `node.astext()` bypasses all escaping, causing `"Config_file [v2]"` to corrupt. Never use `astext()`; buffer-swap through normal visitors instead.

8. **Empty-URL `link("", ...)` trap** — Typst rejects empty URLs. Current `visit_reference` has the guard, but any new reference-emitting code path must independently check. Centralize via a shared `_emit_link()` helper.

9. **String-agreement testing alone proves nothing** — substring assertions like `"info[" in output` passed for months while the PDF showed literal `par({text(...)})`. Every new node handler must ship a real-compile fixture (`sphinx-build → typst.compile() → pypdf`), not just unit tests.

10. **Graceful degradation done wrong** — silent swallowing (no warning) or a fallback that itself emits invalid Typst. Always pair with `logger.warning()` naming the node type. Use `raise nodes.SkipNode` cleanly before any output is touched.

## Implications for Roadmap

### Phase 1: Issue #114 Fatal Bug Fixes (Unblocks Everything)

**Rationale:** The two fatal bugs are blocking — nothing else can be tested against Sphinx's real `doc/` tree until this compiles clean. Both hit the same code paths (figure caption, image width).

**Delivers:**
- `_convert_length_to_typst()` helper (px→pt, unitless, pc, ex, pass-throughs)
- Buffer-swap fix in `visit_caption`/`depart_caption`/`depart_figure`
- `visit_graphviz`/`visit_inheritance_diagram` explicit skip overrides

**Addresses:** Issue #114 fatal compile errors (image width + figure caption); graceful degradation net for graphical nodes

**Avoids:** Pitfalls 1, 3, 4, 5, 9 (standing bar: real `typst.compile()` fixtures per phase)

### Phase 2: High-Volume, Low-Complexity, Independent Handlers

**Rationale:** All reuse existing proven patterns with zero or one new state variable each; independent of each other. High user value (×596 empty-URL, ×972 versionmodified, ×187+ autodoc descs). Safe to parallelize.

**Delivers:**
- `visit_versionmodified`/`depart_versionmodified` (direct `_visit_admonition` reuse)
- Empty-URL `refid` fallback in `visit_reference`
- `visit_desc_returns`, `visit_desc_inline`, `visit_desc_optional`
- `visit_transition`, `visit_glossary`

**Addresses:** versionmodified rendering, empty-URL false positives, autodoc signature parts, transition, glossary

**Avoids:** Pitfalls 2, 7, 8, 9 (each ships real-compile fixture; docstring states mode assumption; no `astext()`)

### Phase 3: Shared Dispatch-Point Changes (Single PR, Regression-Heavy)

**Rationale:** `visit_title` is load-bearing; editing it requires regression tests. Must ship together with dependent node types.

**Delivers:**
- Generalize `visit_title` to three-way branch (admonition→kwarg, topic→inline-strong, default→heading)
- `visit_topic`/`depart_topic` with `{...}` wrapper + `in_list_item`-borrowing
- `visit_line_block`/`visit_line` with `linebreak()` insertion and `_is_first_line` flag

**Addresses:** topic rendering, line-block with preserved breaks

**Avoids:** Pitfalls 1, 2, 9 (regression fixtures for admonition titles + new topic titles; real-compile gate)

### Phase 4: Footnote / Footnote_Reference (Highest Complexity, Own Phase)

**Rationale:** Only new architectural pattern (document-order pre-pass + id-keyed lookup) in the milestone; sequenced last to build confidence from earlier phases. No dependency on phases 1–3.

**Delivers:**
- Pre-pass in `visit_document` to index footnote bodies by id
- `visit_footnote` delegates to pre-pass, raises `SkipNode`
- `visit_footnote_reference` emits `footnote[<looked-up-body>]` at reference site

**Addresses:** footnote/footnote_reference rendering for prose-heavy docs

**Avoids:** Pitfalls 6, 7, 9 (pre-pass design review; real-compile fixture with multiple references)

### Phase 5: Full-Corpus Validation (Depends on All)

**Rationale:** Once all node handlers are in place, compile Sphinx's own `doc/` tree end-to-end through `typstpdf`.

**Delivers:**
- Real Sphinx `doc/` build validation (no fatal TypstCompilationErrors)
- Remaining `unknown_visit` warnings catalogued by frequency (next milestone's input)
- Empirical measurement of "empty-URL reduction post-fix"

**Addresses:** Acceptance gate; next milestone's roadmap

### Ordering Rationale

- Phase 1 must go first (fatal bugs block everything)
- Phases 2–3 can overlap (2→3 sequential safer for shared `visit_title` regression testing)
- Phase 4 sequenced last intentionally (highest complexity, new pattern, builds confidence)
- Phase 5 last by definition (validation gate)

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **Stack** | **HIGH** | Zero-dependency claim verified via Typst 0.15 reference docs + official typst-py source. Three-way @preview sync verified via direct repo read. No version bump needed confirmed by tracing every node to native/bundled equivalent. |
| **Features** | **HIGH** | High-frequency counts (×972, ×596, etc.) from PROJECT.md; node shapes confirmed via Sphinx source + docutils API conventions. Empty-URL refid hypothesis is code-grounded but post-fix empirical measurement flagged as necessary. |
| **Architecture** | **HIGH** | Every existing state pattern traced line-by-line against translator.py. New pre-pass pattern is standard technique. Two MEDIUM-confidence items flagged: versionmodified child shape and footnote attributes (not verified against live doctree dump; flagged for verification before implementation). |
| **Pitfalls** | **HIGH** | All 10 pitfalls grounded in direct codebase read + official Typst docs + project history (v0.5.0 admonition bug = primary precedent). No inference. |
| **Overall** | **HIGH** | Stack, features, pitfalls are HIGH. Architecture is HIGH except two MEDIUM-confidence verify-before-implementation items. Phase structure is HIGH confidence (derived from dependency analysis). |

### Gaps to Address

1. **Exact node shapes (MEDIUM confidence):**
   - Does `versionmodified` have inline children directly, or nested in a paragraph?
   - What attribute name links `footnote_reference` to its target `footnote`? (Assumed `refid`.)
   - **Handling:** Build throwaway doctree dump as first step of Phase 4 planning.

2. **Post-Phase-2 empirical validation:**
   - The ×596 empty-URL figure is a strong signal for refid hypothesis, but actual post-fix reduction should be measured.
   - **Handling:** Phase 2 plan should include "measure before/after warning count" acceptance criterion.

3. **Footnote re-citation syntax confirmation:**
   - Exact Typst `footnote(<label>)` re-citation call shape needs real `typst compile` spot-check.
   - **Handling:** Phase 4 design review should include small test file compiled live.

4. **Versionmodified rendering convention:**
   - FEATURES.md recommends "unboxed italic label," but gentle-clues reuse renders as callout box (different visually).
   - **Handling:** Phase 2 plan should explicitly call out the visual trade-off and confirm stakeholder acceptance.

## Sources

### Primary (HIGH confidence)
- `/home/yuta/Documents/typsphinx/typsphinx/translator.py` (direct read, ~2794 lines)
- `.planning/research/STACK.md` (2026-07-11)
- `.planning/research/FEATURES.md` (2026-07-11)
- `.planning/research/ARCHITECTURE.md` (2026-07-11)
- `.planning/research/PITFALLS.md` (2026-07-11)
- [Typst Official Docs](https://typst.app/docs/reference/) — fetched live 2026-07-11
- `typsphinx/writer.py` + `template_engine.py` + `templates/base.typ` (direct read)
- `.planning/PROJECT.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`
- `tests/test_pdf_render_gate.py` (Phase 8.1 real-compile precedent)

### Secondary (MEDIUM confidence)
- [Sphinx extdev/nodes documentation](https://www.sphinx-doc.org/en/master/extdev/nodes.html)
- [Docutils Node Reference](https://docutils.sourceforge.io/docs/ref/doctree/)

### Tertiary (verify before implementation)
- Exact versionmodified child structure in real Sphinx doctree (inferred, not dumped)
- Exact footnote_reference→footnote cross-linking attribute (assumed `refid`)
- Exact Typst `footnote(<label>)` re-citation syntax (flagged for real-compile spot-check)

---

**Research completed:** 2026-07-11  
**Ready for requirements definition:** YES — phase structure is clear, dependencies are mapped, critical pitfalls are identified with per-phase prevention strategies.
