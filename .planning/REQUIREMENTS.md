# Requirements: typsphinx v0.6.0 — real-world robustness

**Defined:** 2026-07-11
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable output for large real-world documentation sets — Sphinx's own `doc/` tree compiles end-to-end through `typstpdf` with no fatal Typst errors, and the highest-frequency previously-dropped nodes render correctly.

**Driver:** Issue #114 — `.. figure::` with `:target:` (and `px` dimensions) generates invalid Typst, aborting the whole PDF. Widened per milestone scoping to "broad hardening": fix the two fatal figure/image bugs, then add support for the high-frequency dropped-node types that silently degrade Sphinx's own docs.

**Research:** `.planning/research/SUMMARY.md` (+ STACK/FEATURES/ARCHITECTURE/PITFALLS). Zero new runtime dependencies; all work is in `typsphinx/translator.py`. A single malformed node aborts the entire PDF compile — every node-handler group must ship a real-compile acceptance fixture.

## v1 Requirements

Requirements for the v0.6.0 release. Each maps to roadmap phases (see Traceability).

### Figure/Image — Issue #114 fatal bugs

- [x] **FIG-01**: A `.. figure::` / image whose `:width:`/`:height:` uses `px` or other CSS length units compiles to valid Typst — `px`→`pt` numeric conversion (1px = 0.75pt), `%`/`em`/`pt`/`cm`/`mm`/`in` pass through as valid Typst lengths, unrecognized units are warned-and-dropped rather than emitted verbatim
- [x] **FIG-02**: A `.. figure::` / standalone image with a `:target:` link (with or without a caption) emits valid Typst of the form `#figure(link("url")[#image(...)], caption: [...])` — the caption reaches the figure's `caption:` named argument via a buffer-swap and never leaks as a stray juxtaposed `text(...)` call

### Cross-references

- [x] **XREF-01**: A same-document internal cross-reference resolved via `refid` (section anchors, `:term:` links, etc.) renders as a working link instead of degrading to plain text; plain-text fallback fires only when both `refuri` and `refid` are absent

### Version directives

- [x] **VER-01**: `.. versionadded` / `versionchanged` / `deprecated` / `versionremoved` render as an unboxed italic label + body (matching Sphinx's own HTML/LaTeX wording via the `versionlabels` map), not as a gentle-clues callout box

### Autodoc signature nodes

- [x] **DESC-01**: A function/method return annotation (`desc_returns`, e.g. `-> int`) renders in the signature
- [x] **DESC-02**: A multi-line signature (`desc_signature_line`) renders with line breaks between lines
- [x] **DESC-03**: Optional trailing parameters (`desc_optional`, e.g. `printf(fmt[, args])`) render bracket-wrapped, including multi-level nesting
- [x] **DESC-04**: An inline signature fragment (`desc_inline`, e.g. `:cpp:expr:`) renders inline without the standalone-declaration `strong()` wrapper

### Footnotes

- [ ] **FN-01**: `footnote` / `footnote_reference` render via Typst-native `footnote[...]` — a doctree pre-pass indexes footnote bodies by id, the reference site emits the note inline, and a footnote cited more than once reuses the placed note by label rather than duplicating it

### Structural / block nodes

- [x] **BLK-01**: A `transition` (`----` scene break) renders as a horizontal rule (`line(length: 100%)`)
- [x] **BLK-02**: A `.. topic::` renders as a titled aside (reusing the admonition helper)
- [x] **BLK-03**: `line` / `line_block` content renders with verbatim line breaks preserved (`linebreak()`)
- [x] **BLK-04**: A `.. glossary::` renders as its underlying definition list (pass-through wrapper)
- [x] **BLK-05**: A `tabular_col_spec` (`.. tabularcolumns::`, LaTeX-only hint) is skipped safely without leaking content
- [x] **BLK-06**: An `:abbr:` abbreviation renders inline as "term (expansion)" (no PDF hover equivalent)

### Graceful degradation

- [x] **DEG-01**: A `graphviz` node renders a visible placeholder block + exactly one controlled warning, with no raw DOT source leaking into the PDF
- [x] **DEG-02**: An `inheritance_diagram` node renders the same graceful-degrade placeholder (shared helper with DEG-01)

### Validation gate

- [x] **GATE-01**: Each node-handler group ships a real-compile acceptance fixture (`sphinx-build → typst.compile() → pypdf` text extraction), not string-agreement unit tests alone (extends `tests/test_pdf_render_gate.py`)
- [ ] **GATE-02**: Sphinx's own `doc/` tree compiles end-to-end through `typstpdf` with no fatal `TypstCompilationError`; the remaining `unknown_visit` warnings are catalogued by frequency and the empty-URL warning-count reduction is measured before/after

## Future Requirements

Deferred to a later release. Tracked but not in the current roadmap.

### Styling refinements

- **TODO-01**: `todo_node` proper admonition styling — trigger: docs shipped with `todo_include_todos = True`
- **MAN-01**: `:manpage:` role styling (monospace/emphasis) — trigger: a systems-docs user reports it missing
- **LEN-01**: Generalize the CSS-length converter beyond `px` (unitless legacy HTML widths, additional units) — trigger: the next non-`px` length-unit fatal report

### Carried-forward (from v0.5.0)

- **CFG-01** (was FWD-03): user-configurable `@preview` package versions (`typst_package_imports` / dedicated config)
- **XOS-01**: extend `docs-pdf` CI coverage to macOS and Windows

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real `graphviz` / `inheritance_diagram` rendering | Requires shelling out to the `dot` CLI + image-format negotiation — a whole new subsystem, not a translator fix. Graceful-degrade placeholder only this milestone (DEG-01/02). |
| Eliminating all ~1979 dropped-node warnings | The gate is "no fatal errors," not "zero warnings." Long-tail rare nodes not in the named target set are deferred; re-measure and target the next-highest-frequency residual in a future milestone. |
| Literal 1:1 port of docutils footnote backref plumbing | Typst's `footnote[]` has its own numbering/placement/label-reuse; re-implementing HTML-style manual anchors fights the tool. FN-01 uses the native model instead. |
| New runtime dependency or `@preview` package bump | Research confirmed every target node maps to native Typst 0.15 or the already-bundled packages; the 3-way `@preview` version-sync surface stays untouched. |
| Sphinx-8/typst-0.14 ⇄ 9/0.15 compatibility range | typsphinx remains latest-only (established v0.5.0). |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FIG-01 | Phase 11 | Complete |
| FIG-02 | Phase 11 | Complete |
| XREF-01 | Phase 12 | Complete |
| VER-01 | Phase 12 | Complete |
| DESC-01 | Phase 12 | Complete |
| DESC-02 | Phase 12 | Complete |
| DESC-03 | Phase 12 | Complete |
| DESC-04 | Phase 12 | Complete |
| FN-01 | Phase 14 | Pending |
| BLK-01 | Phase 12 | Complete |
| BLK-02 | Phase 13 | Complete |
| BLK-03 | Phase 13 | Complete |
| BLK-04 | Phase 12 | Complete |
| BLK-05 | Phase 12 | Complete |
| BLK-06 | Phase 12 | Complete |
| DEG-01 | Phase 11 | Complete |
| DEG-02 | Phase 11 | Complete |
| GATE-01 | Phase 11 | Complete |
| GATE-02 | Phase 15 | Pending |

**GATE-01 note:** GATE-01 is a cross-cutting standing mandate. It is mapped to **Phase 11**, where
the real-compile acceptance-fixture pattern (`sphinx-build → typst.compile() → pypdf`, extending
`tests/test_pdf_render_gate.py`) is first established, and is echoed as a standing success criterion
in every subsequent node-handler phase (12, 13, 14). Each of those phases ships or extends its own
real-compile fixture rather than relying on string-agreement unit tests alone.

**Coverage:**

- v1 requirements: 19 total
- Mapped to phases: 19 ✓
- Unmapped: 0 ✓

Per-phase mapping: Phase 11 (FIG-01, FIG-02, DEG-01, DEG-02, GATE-01) · Phase 12 (XREF-01, VER-01, DESC-01, DESC-02, DESC-03, DESC-04, BLK-01, BLK-04, BLK-05, BLK-06) · Phase 13 (BLK-02, BLK-03) · Phase 14 (FN-01) · Phase 15 (GATE-02).

---
*Requirements defined: 2026-07-11*
*Last updated: 2026-07-11 after roadmap creation (Traceability populated, 19/19 mapped)*
