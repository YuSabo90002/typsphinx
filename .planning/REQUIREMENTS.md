# Requirements: typsphinx — v0.6.2 rendering fidelity round 2

**Defined:** 2026-07-20
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable **and faithfully-rendered** output on the current ecosystem — output that matches the source rather than merely compiling fatal-free.

Source of record for every FID finding: `milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` (D-01a human-confirmed at the 17-03 gate, severity-final). Each requirement retains its catalogue **F-number** for traceability. Milestone invariant: zero new runtime deps, no `@preview` version bump, the 3-way version-sync surface stays untouched. Standing bar (GATE-01): every node-handler change ships or extends a real `typst.compile()` regression fixture.

## v1 Requirements

Requirements for the v0.6.2 milestone. Each maps to a roadmap phase.

### Block Separation (Cluster A — lost inter-block / inter-element separation)

- [x] **FID-02** (F1): Consecutive `paragraph`s inside a `list_item` render with visible separation instead of concatenating ("role.For example" → "role. For example"). Corpus-wide.
- [x] **FID-03** (F7): Multiple sibling `desc_signature`s (overloads / `alias` groups / multi-option directives) render on separate lines instead of running together on one line.
- [x] **FID-04** (F13): A `rubric` option-group heading (and a directive-option "Options" heading) renders separated from the first following `option`/`:field:` instead of merging onto it.
- [x] **FID-05** (F14): A `definition_list` `term` renders separated from its `definition` when the list is nested in a `list_item` or the definition body opens with a nested list.
- [x] **FID-06** (F15): Back-to-back body-less `confval` `desc` nodes render as distinct, separated entries instead of concatenating into one unbroken blob.

### Signature Spacing (Cluster B — lost intra-signature token spacing)

- [x] **FID-07** (F2): The `desc_annotation` "class "/"exception " keyword prefix keeps its trailing space ("classsphinx.builders…" → "class sphinx.builders…"). Every `py:class`/`py:exception`/`autoclass`.
- [x] **FID-08** (F3): C/C++ `desc_signature` and inline `c/cpp:expr` preserve all inter-token spaces (around `*`/`&`, type↔identifier, after keyword prefix): "Py_ssize_tnitems" → "Py_ssize_t nitems".
- [x] **FID-09** (F5): `field_list` `:type:`/`:default:` object-description fields render with colon-space and preserved field boundaries ("Type:int (a number)Default:42" → "Type: int (a number)  Default: 42").

### Margin Overflow (Cluster C — right-margin overflow / no wrapping; kin to the fixed F12)

- [x] **FID-10** (F6): A long run of inline `literal` roles wraps within the text margin instead of overflowing and clipping mid-token (clipping = content loss). `usage/domains/cpp` p.85.

### Paragraph Reflow (Cluster D)

- [x] **FID-11** (F9): reST semantic/soft line breaks inside a paragraph collapse to a single space instead of rendering as HARD line breaks (ragged short lines). Systemic, corpus-wide.

### Codly Config Leak (Cluster E)

- [x] **FID-12** (F11): A `literal_block` with BOTH a `:caption:` AND nested in a `list_item` does not leak its codly config wrapper as literal visible text (`{ codly(number-format: none)` … `}`); the `codly_prefix="#"` guard covers the combined caption+list-item case.

### Inline Styling (Cluster F — meaning-bearing inline styling, low severity)

- [x] **FID-13** (F8): External named `reference` hyperlinks render with distinguishing styling (link is meaning-bearing, D-06) and correct boundary spacing (no stray space where adjacent inline text exists). Corpus-wide.
- [x] **FID-14** (F10): `*` (PEP 3102 keyword-only) and `/` (PEP 570 positional-only) separators render without injecting their hover-title text inline ("* (Keyword-only parameters separator …)" → "*"). Every affected signature.

### PDF Naming (Issue #117)

- [x] **PDF-01** (Issue #117): `sphinx-build -b typstpdf` names the compiled PDF after the `typst_documents` target name (`manual.pdf`), not the source docname (`index.pdf`); `TypstPDFBuilder.finish()` derives the output name from the target tuple.

### PDF Compile Root (nested masters)

- [x] **PDF-02**: `sphinx-build -b typstpdf` resolves `#include()` and `image()` paths on the same basis the translator emits them (the master's own directory), so a master at a nested docname (`api/index`) compiles to PDF with its includes and images intact — matching what `-b typst` + a manual `typst compile` already produces. Output locations are unchanged.

### Dead Config Values (Phase 22.2, promoted from backlog 999.4/999.3 on 2026-07-22)

- [x] **CONF-01**: `typst_output_dir` is removed from every surface (registration, docs, the two registration-only tests, the `required_configs` list, the example projects, `CLAUDE.md`) with a `### Removed` CHANGELOG note. It is read nowhere and is structurally unimplementable as documented — `outdir` comes from the `sphinx-build` CLI argument. No deprecation period (owner decision 2026-07-21; Sphinx silently ignores unregistered `conf.py` variables, so removal is behaviorally invisible).
- [x] **CONF-02**: The `typst_package` (Typst Universe) path works end-to-end — a project configured with `typst_package` **alone** builds under `-b typstpdf` and compiles with zero Typst errors. Covers BUG-A (`_template.typ` imported but never written), BUG-B (unconditional `title`/`authors`/`date` injection), BUG-C (`typst_authors`/`typst_author_params` silently ignored — dead `_format_authors_with_details()`), and BUG-D (the wrong `docs/source/examples/advanced.rst` examples and important-note).
- [x] **CONF-03**: A config→output regression fixture asserts that setting a config value **changes the emitted output**, not merely that it is registered — covering both CONF-01 and CONF-02, with a real `typst.compile()` where the config affects compilable output (GATE-01). Registration-only assertions are insufficient going forward.

### Builder Warning Hardening (Phase 22.3, promoted from backlog 999.5 on 2026-07-22)

- [x] **WR-01**: `TypstPDFBuilder.finish()` no longer reports a successful build while silently emitting no PDF for a configured master. The missing-`.typ` branch (`builder.py:922-924` — the CONTEXT.md/earlier-REQUIREMENTS coordinate `895-897` was measured stale in Phase 22.3 research; a bare `logger.warning(...); continue` that never reached `failures`) is aligned with the compile-failure path, the adjacent malformed-`doc_tuple` skip is treated consistently (or its exemption is recorded), and the `finish()` docstring's D-04 "no silent success" claim matches implemented behavior. Resolved **behavioral** at `/gsd-discuss-phase 22.3` (D-01): both skip branches now append to `failures` and the build fails via the aggregate `ExtensionError`. Delivered in Phase 22.3.
- [x] **WR-02**: The nested-master render gate (`tests/test_nested_master_render_gate.py`, SC#2 / `G-22.1-2`) proves its property without asserting on `typst-py` error-message literals (`"escape"`, `"not found"`, `"usage.typ"`, `"_template.typ"`) — those are not a contracted upstream API, so a rewording upstream currently turns CI red with no typsphinx regression.

## v2 Requirements

Deferred to a future milestone. Tracked but not in this roadmap.

### Forward-ecosystem

- **CFG-01** (was FWD-03): User-configurable `@preview` package versions.

### Cross-OS verification

- **XOS-01**: Extend `docs-pdf` CI coverage to macOS and Windows.

## Out of Scope

Explicitly excluded from v0.6.2. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| F4 (audit finding) | REJECTED at the 17-03 gate — Sphinx-side, builder-independent; not a typsphinx bug |
| F12 (audit finding) | DONE in v0.6.1 (FID-01a, Phase 18) — wide-table collision/clip already fixed |
| DEG-03: real rendering for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline); v0.6.x renders a graceful-degrade placeholder |
| XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 |
| New reST constructs / new translation features | This is a fidelity/bug-fix cycle, not a feature cycle |
| `@preview` version bump or new runtime dependency | Milestone invariant — the 3-way version-sync surface stays untouched |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FID-02 | Phase 19 (Block Separation — Cluster A) | Complete |
| FID-03 | Phase 19 (Block Separation — Cluster A) | Complete |
| FID-04 | Phase 19 (Block Separation — Cluster A) | Complete |
| FID-05 | Phase 19 (Block Separation — Cluster A) | Complete |
| FID-06 | Phase 19 (Block Separation — Cluster A) | Complete |
| FID-07 | Phase 20 (Signature Token Spacing — Cluster B) | Complete |
| FID-08 | Phase 20 (Signature Token Spacing — Cluster B) | Complete |
| FID-09 | Phase 20 (Signature Token Spacing — Cluster B) | Complete |
| FID-10 | Phase 21 (Residual Fidelity — Cluster C) | Complete |
| FID-11 | Phase 21 (Residual Fidelity — Cluster D) | Complete |
| FID-12 | Phase 21 (Residual Fidelity — Cluster E) | Complete |
| FID-13 | Phase 21 (Residual Fidelity — Cluster F) | Complete |
| FID-14 | Phase 21 (Residual Fidelity — Cluster F) | Complete |
| PDF-01 | Phase 22 (typstpdf Target-Name PDF Fix) | Complete |
| PDF-02 | Phase 22.1 (typstpdf Compile-Root Alignment, INSERTED) | Complete |
| CONF-01 | Phase 22.2 (Dead Config-Value Sweep, INSERTED) | Not started |
| CONF-02 | Phase 22.2 (Dead Config-Value Sweep, INSERTED) | Not started |
| CONF-03 | Phase 22.2 (Dead Config-Value Sweep, INSERTED) | Not started |
| WR-01 | Phase 22.3 (typstpdf Builder Warning Hardening, INSERTED) | Not started |
| WR-02 | Phase 22.3 (typstpdf Builder Warning Hardening, INSERTED) | Not started |

**Coverage:**

- v1 requirements: 20 total
- Mapped to phases: 20 ✓
- Unmapped: 0 ✓

Phase 23 (v0.6.2 Release Prep + Regression-Gate Close) carries no FID/PDF requirement — it is the
prep-only release/close phase (version bump + CHANGELOG + closing full-corpus regression gate); all
20 v1 requirements are delivered by Phases 19–22.3.

---
*Requirements defined: 2026-07-20*
*Last updated: 2026-07-22 — WR-01/WR-02 added with the Phase 22.3 insertion (typstpdf builder warning hardening, promoted from backlog 999.5); 20/20 mapped to Phases 19–22.3; milestone v0.6.2*
