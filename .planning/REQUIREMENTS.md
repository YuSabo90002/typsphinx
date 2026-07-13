# Requirements: typsphinx — v0.6.1 rendering fidelity

**Defined:** 2026-07-13
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable output for large real-world documentation sets — and now, output that *renders faithfully* to the source, not merely compiles fatal-free.

## v1 Requirements (v0.6.1)

Requirements for this milestone. Each maps to a roadmap phase.

### Node Rendering

Nodes the v0.6.0 warning audit confirmed are still silently `unknown_visit`-dropped in the Sphinx corpus.

- [ ] **TODO-01**: A `.. todo::` directive (`todo_node`) renders its body content in the PDF (as an admonition-style block) instead of being silently dropped — the `unknown node type: <todo_node>` warning is eliminated (×10 in the corpus).
- [ ] **MAN-01**: The `:manpage:` role (`manpage` node) renders as its literal page reference text (e.g. `ls(1)`) instead of being silently dropped — the `unknown node type: <manpage>` warning is eliminated (×10 in the corpus).

### Length Handling

- [ ] **LEN-01**: The CSS-length → Typst-length conversion (introduced in v0.6.0 as a `visit_image`-local px→pt fix) is generalized into a single shared helper and reused at every length-bearing site, so any node carrying a CSS length attribute converts consistently (no duplicated/divergent conversion logic).

### Rendering Fidelity Audit

The discovery core of this milestone: warnings only surface *dropped* content; *silent* mis-renders (output that compiles cleanly and emits no warning, yet diverges from the source) require a visual audit.

- [ ] **AUD-01**: The compiled Sphinx-`doc/` corpus PDF is visually audited against the rendered HTML / rST source, and every silent mis-render issue found is catalogued with location (docname + node kind), a source-vs-output description, and a severity rating.
- [ ] **FID-01**: Every AUD-01 issue at severity "high" (content lost, unreadable, or grossly mis-structured) is fixed, each fix proven by a real `typst.compile()` regression fixture (GATE-01 pattern). The concrete per-issue list is enumerated by AUD-01 and appended here as `FID-01a`, `FID-01b`, … once the audit completes.

### Regression Gate

- [ ] **GATE-03**: After all v0.6.1 changes, the full Sphinx-`doc/` corpus still compiles fatal-free through `typstpdf` (GATE-02 non-regression), and the `unknown_visit` catalogue no longer contains `todo_node` or `manpage`.

## Future Requirements

Acknowledged but deferred beyond v0.6.1.

### Graceful-degrade upgrades

- **DEG-03**: Real rendering (not a placeholder) for `graphviz` / `inheritance_diagram` — requires an image-generation pipeline; large scope.
- **XREF-02**: Link `manpage` / cross-references to external URLs where a base URL is configured (e.g. a manpage URL template).

### Configuration

- **CFG-01** (from v0.5.0 backlog): user-configurable `@preview` package versions.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fixing Sphinx-side warnings (autodoc import failures ×22, `py:meth 参照先が見つかりません` ×13) | Emitted during Sphinx's read/resolve phase, builder-independent (occur under the HTML builder too); caused by the corpus's own missing optional deps, not by typsphinx rendering. |
| Full graphical rendering of `graphviz` / `inheritance_diagram` | Intentional graceful-degrade placeholder is working as designed (DEG-01/DEG-02); real rendering is DEG-03 (future). |
| Making non-included-document cross-references into live links | typstpdf compiles a single master document; a target not in the `#include()` tree cannot be linked, so plain-text degradation is spec-appropriate. |
| Cross-OS docs-PDF CI (macOS/Windows) — XOS-01 | Carried from v0.5.0 backlog; orthogonal to rendering fidelity. |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUD-01 | Phase [N] | Pending |
| TODO-01 | Phase [N] | Pending |
| MAN-01 | Phase [N] | Pending |
| LEN-01 | Phase [N] | Pending |
| FID-01 | Phase [N] | Pending |
| GATE-03 | Phase [N] | Pending |

**Coverage:**
- v1 requirements: 6 named (FID-01 expands after AUD-01)
- Mapped to phases: 0 (roadmap pending)
- Unmapped: 6 ⚠️

---
*Requirements defined: 2026-07-13*
*Last updated: 2026-07-13 after initial v0.6.1 definition*
