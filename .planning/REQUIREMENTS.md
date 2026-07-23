# Requirements: typsphinx v0.6.3 — config & docs 実測整合 + captioned tables

**Defined:** 2026-07-23
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable **and faithfully-rendered** output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise.

## v1 Requirements

Requirements for this milestone. Each maps to a roadmap phase. Every config→output and node-handler change ships a fail-pre-fix real `typst.compile()` regression fixture (standing GATE-01 bar; template: `tests/test_package_only_config_gate.py`).

### Config (dead-config sweep round 2)

- [ ] **CONF-04**: User can set `papersize` and `fontsize` via `typst_elements` in `conf.py` (e.g. `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}`) and see them applied in the compiled `.typ`/PDF via the template's `project()` function — not silently dropped. Implemented as a **curated allowlist** (only keys `base.typ`'s `project()` declares; `base.typ` itself is unchanged), with `fontsize` emitted as a Typst **length** (not a quoted string) and `papersize` as a string; an unrecognized key fails loudly rather than silently, and baseline Sphinx metadata (`copyright`, etc.) is never leaked into `project()`.
- [ ] **CONF-05**: The registered-but-inert `typst_toctree_defaults` config value is removed from every surface (`__init__.py` registration, `docs/configuration.rst`, `examples/advanced`, README, and its registration-only test file) so it is no longer presented as a supported option. (Grep-confirmed zero consumers — pure removal.)

### Table rendering (PR#98 reimplementation)

- [ ] **TBL-01**: A `.. table:: Caption` directive renders as `figure(table(...), caption: {...}, kind: table)` with native "Table N" numbering (no stray `heading()` before the table); a table **without** a caption stays a plain `table()` (never speculatively figure-wrapped); the caption preserves inline markup; and caption composes correctly with the existing `:width:` block wrap (caption+width both present). Correct on the 2nd-and-later table in a single document (no caption lost to a stale cell buffer).
- [ ] **TBL-02**: A `:numref:` / `:ref:` reference to a captioned table resolves to a working cross-reference in the compiled PDF — the `figure(..., kind: table)` carries a Typst `<label>` derived from the table's docutils target id, and a reference to it renders as a resolvable link (e.g. "Table N"), without colliding with the table's existing `_emit_id_anchors` id anchors. Proven by a real `typst.compile()` fixture where a `:numref:` to a labeled table resolves (no dangling/duplicate-label error). Builds on TBL-01 (the figure must exist to be labeled).

### Docs fidelity

- [ ] **DOC-06**: The orphan `docs/configuration.rst` (526 lines, unreachable from any toctree, containing the wrong package name `sphinxcontrib.typst`) is deleted after confirming no unique useful content is lost and no live reference remains.
- [ ] **DOC-07**: The 5 phantom config names in `docs/source/user_guide/configuration.rst` are corrected or removed so every documented `typst_*` example matches a registered config: `typst_author` → `typst_authors`; `typst_use_codly` / `typst_code_line_numbers` deleted (no real equivalent); `typst_papersize` / `typst_fontsize` rewritten as working `typst_elements` examples **if CONF-04 has shipped**, otherwise delete-only.

## Future Requirements

Deferred to a future milestone. Tracked but not in this roadmap.

### Config

- **CONF-06**: Additional `typst_elements` keys beyond `papersize`/`fontsize` (e.g. `lang`, currently hardcoded in `base.typ`) — would require adding parameters to `base.typ`'s `project()`, out of this milestone's "base.typ unchanged" scope.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| github.io 404 doc links (README `/en/` prefix) + repo "Website" field | Owner decision 2026-07-23: folded into the RTD migration (~2026-07-30), not interim-fixed. Separate track from this milestone. |
| Read the Docs migration | Separate ~1-phase docs-hosting task, out of this code/docs-fidelity milestone. |
| Arbitrary `typst_elements` key pass-through | An undeclared kwarg to `project()` is a hard Typst compile fatal; curated allowlist only. Arbitrary pass-through already exists via `typst_template_function.params`. |
| New top-level `typst_papersize` / `typst_fontsize` config registrations | Would grow the config surface, against the dead-config-cleanup theme; `typst_elements` is the vehicle. |
| List-of-tables page generation | No Sphinx builder auto-generates one; out of scope. |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONF-04 | TBD | Pending |
| CONF-05 | TBD | Pending |
| TBL-01 | TBD | Pending |
| TBL-02 | TBD | Pending |
| DOC-06 | TBD | Pending |
| DOC-07 | TBD | Pending |

**Coverage:**
- v1 requirements: 6 total
- Mapped to phases: 0 (roadmap not yet created)
- Unmapped: 6 ⚠️

---
*Requirements defined: 2026-07-23*
*Last updated: 2026-07-23 after initial definition*
