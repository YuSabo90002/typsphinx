# Requirements: typsphinx v0.9.0 — per-document templates

**Defined:** 2026-08-15
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered and
well-typeset output — and the documented configuration actually takes effect, so a user who copies a
documented `conf.py` example gets what the docs promise.

REQ-IDs continue from the highest number previously used in each category (BLD-04, CONF-13, DOC-14,
IMG-02, OUT-03, XREF-04). `TPL` is a new category introduced by this milestone.

## v1 Requirements

### Template registry

- [ ] **TPL-01**: User can define named template definitions in `typst_document_templates`, each
      carrying `template` **xor** `package`, plus an optional `template_function`
- [ ] **TPL-02**: User can select a named template per output document via element [4] of a
      `typst_documents` entry
- [ ] **TPL-03**: The built-in key `"typst"` resolves to the existing global configuration
      (`typst_template` / `typst_package` / `typst_template_function` / `typst_template_mapping`, or
      the bundled `base.typ` when none is set), so an existing `conf.py` produces the same PDF with
      no edit
- [ ] **TPL-04**: A four-element `typst_documents` tuple behaves identically to one whose fifth
      element is `"typst"`
- [ ] **TPL-05**: Several `typst_documents` entries can share one registry key

### Configuration validation

- [ ] **CONF-14**: An unregistered registry key stops the build, and the error names the registered
      keys
- [ ] **CONF-15**: A registry entry carrying both `template` and `package` stops the build
- [ ] **CONF-16**: Defining `"typst"` in the registry stops the build — it is a reserved key
- [ ] **CONF-17**: A `template` pointing at a file directly under `srcdir` stops the build — it has
      no bundle directory
- [ ] **CONF-18**: A registry key whose shape is unsafe as a single path segment stops the build:
      empty, `.`/`..`, containing `/` or `\`, a Windows reserved device name, a trailing dot or
      space, or differing from another key only by case
- [ ] **CONF-19**: A `conf.py` still setting a removed config value (`typst_template_assets`,
      `typst_authors`, or `typst_toctree_defaults`) gets a build warning naming its replacement

### Output layout

- [ ] **OUT-04**: Every used key's template bundle — the resolved template's parent directory — is
      copied wholesale to `<outdir>/_template/<key>/`, with `"typst"` handled by the same rule and
      not special-cased
- [ ] **OUT-05**: A template-relative asset reference such as `#image("logo.png")` resolves, because
      the template sits inside its own copied bundle
- [ ] **OUT-06**: A wrapper imports its own template by a path that does not depend on the wrapper's
      nesting depth
- [ ] **OUT-07**: `_template/` is reserved output space; a source tree that would write there stops
      the build

### Builder mechanics

- [ ] **BLD-05**: A non-`.typ` file belonging to the bundled `"typst"` template is present in the
      built wheel, not only in an editable install
- [ ] **BLD-06**: The bundle copy excludes VCS and OS metadata and does not follow a symlink out of
      the bundle

### v0.8.0-derived defects

- [ ] **XREF-05**: When two docnames sanitize to the same label string, a reference to the absent one
      degrades to plain text instead of linking to the other document
- [ ] **BLD-07**: A docname containing `#` or `>` cannot collide two include-edge keys
- [ ] **BLD-08**: An include chain deeper than Python's recursion limit fails with a named
      `ExtensionError` rather than a raw `RecursionError`
- [ ] **BLD-09**: A driveless-absolute Windows image URI reaches the rehome/relocate/warn branch on
      Python 3.13
- [ ] **IMG-03**: Two escaping absolute image URIs in different directories sharing a basename do not
      collide onto one relocation key

### Documentation

- [ ] **DOC-15**: `configuration.rst` describes element [4] as the registry key, retracting the
      "accepted and ignored" definition
- [ ] **DOC-16**: `templates.rst`'s asset example and `advanced.rst`'s `refs.bib` guidance describe
      what actually works under the bundle layout
- [ ] **DOC-17**: Migration guidance for the removed config values is published

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

Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TPL-01 | — | Pending |
| TPL-02 | — | Pending |
| TPL-03 | — | Pending |
| TPL-04 | — | Pending |
| TPL-05 | — | Pending |
| CONF-14 | — | Pending |
| CONF-15 | — | Pending |
| CONF-16 | — | Pending |
| CONF-17 | — | Pending |
| CONF-18 | — | Pending |
| CONF-19 | — | Pending |
| OUT-04 | — | Pending |
| OUT-05 | — | Pending |
| OUT-06 | — | Pending |
| OUT-07 | — | Pending |
| BLD-05 | — | Pending |
| BLD-06 | — | Pending |
| XREF-05 | — | Pending |
| BLD-07 | — | Pending |
| BLD-08 | — | Pending |
| BLD-09 | — | Pending |
| IMG-03 | — | Pending |
| DOC-15 | — | Pending |
| DOC-16 | — | Pending |
| DOC-17 | — | Pending |

**Coverage:**

- v1 requirements: 25 total
- Mapped to phases: 0
- Unmapped: 25 ⚠️

---
*Requirements defined: 2026-08-15*
