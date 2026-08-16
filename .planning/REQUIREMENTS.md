# Requirements: typsphinx v0.9.0 — per-document templates

**Defined:** 2026-08-15
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered and
well-typeset output — and the documented configuration actually takes effect, so a user who copies a
documented `conf.py` example gets what the docs promise.

REQ-IDs continue from the highest number previously used in each category (BLD-04, CONF-13, DOC-14,
IMG-02, OUT-03, XREF-04). `TPL` is a new category introduced by this milestone.

## v1 Requirements

### Template registry

- [x] **TPL-01**: User can define named template definitions in `typst_document_templates`, each
      carrying `template` **xor** `package`, plus an optional `template_function`

- [x] **TPL-02**: User can select a named template per output document via element [4] of a
      `typst_documents` entry

- [x] **TPL-03**: The built-in key `"typst"` resolves to the existing global configuration
      (`typst_template` / `typst_package` / `typst_template_function` / `typst_template_mapping`, or
      the bundled `base.typ` when none is set), so an existing `conf.py` produces the same PDF with
      no edit

- [x] **TPL-04**: A four-element `typst_documents` tuple behaves identically to one whose fifth
      element is `"typst"`

- [x] **TPL-05**: Several `typst_documents` entries can share one registry key

### Configuration validation

- [x] **CONF-14**: An unregistered registry key stops the build, and the error names the registered
      keys

- [x] **CONF-15**: A registry entry carrying both `template` and `package` stops the build
- [x] **CONF-16**: Defining `"typst"` in the registry stops the build — it is a reserved key
- [x] **CONF-17**: A `template` pointing at a file directly under `srcdir` stops the build — it has
      no bundle directory

- [x] **CONF-18**: A registry key whose shape is unsafe as a single path segment stops the build:
      empty, `.`/`..`, containing `/` or `\`, a Windows reserved device name, a trailing dot or
      space, or differing from another key only by case

- [x] **CONF-19**: A `conf.py` still setting a removed config value (`typst_template_assets`,
      `typst_authors`, or `typst_toctree_defaults`) gets a build warning naming its replacement

### Output layout

- [x] **OUT-04**: Every used key's template bundle — the resolved template's parent directory — is
      copied wholesale to `<outdir>/_template/<key>/`, with `"typst"` handled by the same rule and
      not special-cased

- [x] **OUT-05**: A template-relative asset reference such as `#image("logo.png")` resolves, because
      the template sits inside its own copied bundle

- [x] **OUT-06**: A wrapper imports its own template by a path that does not depend on the wrapper's
      nesting depth

- [x] **OUT-07**: `_template/` is reserved output space; a source tree that would write there stops
      the build

### Builder mechanics

- [x] **BLD-05**: A non-`.typ` file belonging to the bundled `"typst"` template is present in the
      built wheel, not only in an editable install

- [x] **BLD-06**: The bundle copy excludes VCS and OS metadata (the refusal clause for a linked file
      resolving outside the bundle was retracted by the owner at Phase 54 planning, D-03; the
      recorded behavior at a linked file is `os.walk(followlinks=False)` plus per-file
      `shutil.copy2`)

### v0.8.0-derived defects

- [x] **XREF-05**: When two docnames sanitize to the same label string, a reference to the absent one
      degrades to plain text instead of linking to the other document

- [x] **BLD-07**: A docname containing `#` or `>` cannot collide two include-edge keys
- [x] **BLD-08**: An include chain deeper than Python's recursion limit fails with a named
      `ExtensionError` rather than a raw `RecursionError`

- [x] **BLD-09**: A driveless-absolute Windows image URI reaches the rehome/relocate/warn branch on
      Python 3.13

- [x] **IMG-03**: Two escaping absolute image URIs in different directories sharing a basename do not
      collide onto one relocation key

### Phase 54 review findings

*Raised as `WR-01`/`CR-01` in `phases/54-one-bundle-rule-template-key-per-document-selection-four-del/54-REVIEW.md`
and assigned to the inserted Phase 54.1. Both are defects in what Phase 54 shipped, on the same
`builder.py` bundle-copy surface. The same review's `WR-02` belongs to Phase 57's CHANGELOG
curation; `WR-03`, `WR-04` and `IN-01` are unassigned.*

- [x] **WR-01**: A used key's template bundle is never copied in a way that republishes the
      project's Sphinx `templates_path` directory into build output, and no published page under
      `docs/source/` recommends putting a Typst template in `_templates/` — the name
      `templates_path` defaults to. Phase 54 made the resolved template's parent directory the unit
      of copying, so the pre-existing documentation recommendation
      (`templates.rst`, `configuration.rst`: `typst_template = "_templates/custom.typ"`) now causes a
      user's Jinja override directory to be published. `typsphinx/` reads `templates_path` nowhere
      today — the collision is acknowledged only in the `template_engine.py:36` comment explaining
      why `_typst/` was chosen. Refusal-vs-warning is open going into `/gsd-discuss-phase 54.1`

- [x] **CR-01**: A CONF-17 violation on the built-in `"typst"` key, and a reserved-key case
      collision (a declared key differing from `"typst"` only by case, which CONF-18 does not catch
      because it compares declared keys only against each other), are both detected before any
      `.typ` file is written — not at `finish()`, which Sphinx runs only after `write()` has emitted
      every content and wrapper file. Today the A-01/CONF-17 guard lives in
      `_copy_used_template_bundles()`, so a global `typst_template` naming a bare filename at the
      source root writes a full, broken output tree and only then raises. This is the one path that
      breaks the invariant `_validate_output_path_collisions()` and
      `_validate_registry_key_references()` establish and
      `test_template_prefix_reservation_gate.py::test_no_typ_file_written_after_refusal` gates

### Documentation

- [x] **DOC-15**: `configuration.rst` describes element [4] as the registry key, retracting the
      "accepted and ignored" definition

- [ ] **DOC-16**: `templates.rst`'s asset example and `advanced.rst`'s `refs.bib` guidance describe
      what actually works under the bundle layout

- [ ] **DOC-17**: Migration guidance for the removed config values is published

### Release

- [ ] **REL-08**: v0.9.0 is published — PyPI wheel + sdist, GitHub Release carrying the curated
      `## [0.9.0]` CHANGELOG section, the second-repository tag on `typsphinx-doc-translations`, and
      Read the Docs `stable` serving 0.9.0 on both projects

      *Added at roadmap creation 2026-08-15, mirroring v0.8.0's REL-07. It is the requirement of the
      prep-only final phase (57), which takes zero irreversible action — REL-08 closes at
      `/gsd-complete-milestone`, on the publish, not on the prep. It stays `[ ]` through every plan
      of Phase 57; the `phase.complete` auto-flip has fired against this requirement shape at four
      consecutive release-prep closes and must be caught and reverted there.*

## Future Requirements

Acknowledged but out of this milestone.

### Configuration

- **CONF-06**: `typst_elements` keys beyond `papersize`/`fontsize`/`lang`
- **CFG-01**: user-configurable `@preview` package versions

### Template argument pipeline

- **TPL-06**: retire `typst_template_mapping` in favour of `template_function` — the two overlap and
  the mapping is strictly weaker (a rename table over the three-key `{project, author, release}`
  dict, discarded wholesale whenever `params` is declared). Owner intends removal in a later
  milestone; this one leaves it working, unwarned.

- **TPL-07**: replace implicit argument injection with an explicit `args` + `metadata` pair, which
  would dissolve `ELEMENTS_ALLOWLIST`, the `params` exclusivity branch, the `lang` auto-derivation
  guard, and the P×A failure below. Scoped and costed during v0.9.0 planning at 8+ phases /
  55–70 plans and a break of every existing `conf.py`; deferred as a v1.0 candidate.

### Cross-OS

- **XOS-01**: cross-OS docs-PDF CI (macOS/Windows)
- **QUA-06**: `ruff` unrunnable on NixOS (a `flake.nix`-side repair)
- **QUA-07**: split the `dev` extra into PEP 735 `[dependency-groups]` (SEED-003)
- **LNK-01**: `sphinx-build -b linkcheck` CI job

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fixing the P×A cell (a `package` with no declared `params` emits a Typst compile fatal for any master with a toctree) | Owner decision. Two writes escape the D-05 package suppression — `map_parameters()` merges `typst_elements` unconditionally at its tail, and `render_wrapper()` calls `params.update(toctree_options)` after it. This is why `examples/charged-ieee/approach1` uses the `params` route. Belongs with TPL-07's explicit-argument redesign, not here |
| Relaxing `params` exclusivity so a shared registry key can carry per-entry titles | Preserving the D-B/D-D exclusivity keeps one rule; two entries sharing a key that declares `params` share its literal title, which is accepted |
| `template_mapping` / `package_imports` / `elements` / `assets` keys in the registry | `template_mapping` duplicates `template_function`; the other three stay global and apply to every document. Adding an `assets` key would break the one-sentence bundle rule |
| Deprecating `typst_template_mapping` in this milestone | Removal is intended later (TPL-06); warning about it now would change behaviour for a value this milestone does not touch |
| `numref` number divergence across masters | Excluded from every published surface by owner override D-07 at the v0.8.0 close; classified as a bug for a later milestone |
| Modernizing typing imports | `CLAUDE.md` independently forbids it until its todo lands |

## Traceability

Populated at roadmap creation, 2026-08-15. Every v1 requirement maps to exactly one phase; no
requirement appears twice and none is unmapped. Phase numbering continues from v0.8.0's last phase
(52), so this milestone runs **Phases 53–57**.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TPL-01 | Phase 53 | Complete |
| TPL-02 | Phase 54 | Complete |
| TPL-03 | Phase 53 | Complete |
| TPL-04 | Phase 53 | Complete |
| TPL-05 | Phase 53 | Complete |
| CONF-14 | Phase 53 | Complete |
| CONF-15 | Phase 53 | Complete |
| CONF-16 | Phase 53 | Complete |
| CONF-17 | Phase 53 | Complete |
| CONF-18 | Phase 53 | Complete |
| CONF-19 | Phase 54 | Complete |
| OUT-04 | Phase 54 | Complete |
| OUT-05 | Phase 54 | Complete |
| OUT-06 | Phase 54 | Complete |
| OUT-07 | Phase 54 | Complete |
| BLD-05 | Phase 54 | Complete |
| BLD-06 | Phase 54 | Complete |
| WR-01 | Phase 54.1 (Bundle Directory Safety, INSERTED) | Complete |
| CR-01 | Phase 54.1 (Bundle Directory Safety, INSERTED) | Complete |
| XREF-05 | Phase 55 | Complete |
| BLD-07 | Phase 55 | Complete |
| BLD-08 | Phase 55 | Complete |
| BLD-09 | Phase 55 | Complete |
| IMG-03 | Phase 55 | Complete |
| DOC-15 | Phase 56 | Complete |
| DOC-16 | Phase 56 | Pending |
| DOC-17 | Phase 56 | Pending |
| REL-08 | Phase 57 | Pending |

**Per-phase totals:** Phase 53 → 9 · Phase 54 → 8 · Phase 55 → 5 · Phase 56 → 3 · Phase 57 → 1.

**Coverage:**

- v1 requirements: 26 total (25 defined 2026-08-15 + REL-08 added at roadmap creation)
- Mapped to phases: 26
- Unmapped: 0 ✓
- Duplicated across phases: 0 ✓

Requirements listed under **Future Requirements** and **Out of Scope** are deliberately unmapped and
are not counted in this tally.

---
*Requirements defined: 2026-08-15 · Traceability populated at roadmap creation 2026-08-15 (Phases 53–57)*
