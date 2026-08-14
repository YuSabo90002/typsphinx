# Requirements: typsphinx v0.8.0 — multi-master composition

**Defined:** 2026-08-11
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable and faithfully-rendered,
well-typeset output on the current ecosystem — and the documented configuration actually takes
effect, so a user who copies a documented `conf.py` example gets what the docs promise.

**Milestone goal:** A `typst_documents` configuration declaring more than one master produces a
complete PDF for each of them — no silently dropped content, no compile failure — by moving
composition from "one `.typ` shared by every master, with the include decision baked in at write
time" to "per-master wrapper files that publish their include edge set as Typst `state`, plus
template-less docname-named content files that emit state-guarded includes at the toctree's own
position".

## v1 Requirements

### Composition (COMP)

- [x] **COMP-01**: Every document is written as a docname-named content `.typ` with no template
      applied, so `writer.py`'s master/included binary no longer selects the output shape

- [x] **COMP-02**: Each `typst_documents` entry produces a wrapper `.typ` at its resolved target
      path, carrying the template application and the include of its master's content file

- [x] **COMP-03**: A document listed in `typst_documents` that is also another master's toctree
      child builds without Typst's `file not found` abort (B-1)

- [x] **COMP-04**: An included master no longer re-expands its template's title page and
      `#outline()` into the middle of the parent's body (B-2)

- [x] **COMP-05**: The builder computes each master's include graph by document-order depth-first
      traversal with first-encounter-wins, matching `sphinx.util.nodes.inline_all_toctrees`

- [x] **COMP-06**: The wrapper publishes its master's include edge set as Typst `state`, and content
      files emit state-guarded includes at their toctree's own position

- [x] **COMP-07**: A document toctree'd by two masters appears in both masters' PDFs (defect A)
- [x] **COMP-08**: Prose written before and after a `.. toctree::` keeps its position relative to the
      included content — the shape of Sphinx's own default `index.rst`

- [x] **COMP-09**: Two masters requiring conflicting include sets from the same content file (the
      diamond `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]`) both compile correctly, with the shared
      document appearing exactly once in each

- [x] **COMP-10**: Heading levels match Sphinx's own composition — relative offsets nest according to
      traversal order, so a multiply-reachable document's depth follows the order its parent lists
      its children

- [x] **COMP-11**: `visit_toctree` no longer emits an unconditional `include()`, and the build-scoped
      `_included_docnames` ledger is removed

- [x] **COMP-12**: The full Sphinx `doc/` corpus compiles fatal-free under the new composition,
      demonstrating that the `state`/`context` multi-pass layout convergence holds at real scale

### Output placement (OUT)

- [x] **OUT-01**: A `typst_documents` target is treated as a path relative to the output directory, so
      a bare name writes the wrapper at the output root and an explicit path writes it where the user
      asked — reversing v0.7.1 Phase 44's D-06/D-07 (a path in a target is rejected and truncated to
      its basename) and D-05 (a nested docname's output is forced into that docname's own directory)

- [x] **OUT-02**: A target that escapes the output directory — containing `..`, absolute, or
      drive-qualified — is still refused with a warning and a safe fallback

- [x] **OUT-03**: Content files keep their docname-derived names and locations regardless of where
      their master's wrapper is written

### Cross-references (XREF)

- [x] **XREF-03**: A cross-document reference whose target label is absent from the compiling master
      degrades to plain text at compile time instead of aborting the compile
      (`48-EVIDENCE.md` §"Guard contract, fixed by this measurement", §"SC#2 — site enumeration"
      row 1, §"D-11 compile-time cost")

- [x] **XREF-04**: Every label-reference emission site routes through one shared guard, and
      `master_included_docnames` is removed
      (`48-EVIDENCE.md` §"SC#2 — site enumeration" / §"SC#3 — the build-time mechanism is gone")

### Builder input hardening (BLD)

- [x] **BLD-02**: Two `typst_documents` entries resolving to the same target path are detected and
      reported instead of silently dropping one master's body

- [x] **BLD-03**: A wrapper target that collides with a content file's own path is detected
- [x] **BLD-04**: Collision detection behaves identically on case-insensitive filesystems

### Images (IMG)

- [ ] **IMG-01**: A converted image rehomed to `images/<basename>` no longer collides with a real
      source image at `<srcdir>/images/<basename>`

- [ ] **IMG-02**: An absolute image URI outside `doctreedir` no longer causes `copy_image_files()` to
      write outside the output directory

### Documentation (DOC)

- [ ] **DOC-14**: The published documentation describes the two-layer output — which file to compile,
      that a content file compiled standalone includes no children, the target-as-path semantics, and
      what changed from v0.7.x

### Release (REL)

- [ ] **REL-07**: v0.8.0 is released to PyPI with a curated CHANGELOG entry calling out the
      output-shape change and the target-as-path reversal

## Future Requirements

Deferred to a later release. Tracked but not in this roadmap.

### Configuration

- **CONF-13**: Per-master templates via a **named template key in the 5th tuple element**. The
  shape question this entry used to carry ("a 5th positional tuple element mirroring
  `latex_documents`' `theme`, versus a dict-shaped config") was **closed by measurement on
  2026-08-11**, during the v0.8.0 Phase 47 discussion. Deferred to a milestone of its own —
  v0.8.0 stays composition-only and does **not** touch the 5th element, which this requirement
  reserves.

  **The precedent is exact, and was read on the installed Sphinx 9.1.0**
  (`sphinx/builders/latex/__init__.py`): `docname, targetname, title, author, themename =
  entry[:5]` followed by `theme = self.themes.get(themename)`. LaTeX's 5th element is a **name
  looked up in a theme registry**, not an inline value — so the same position in
  `typst_documents` should be a key into a registry of named template definitions.

  **The design.** A template definition unifies what is scattered across four global config
  values today — where the template comes from (`typst_template` file *or* `typst_package` +
  `typst_package_imports`) and how it is called (`typst_template_function`'s name + `params`) —
  into one object:

  ```python
  typst_templates = {
      "ieee":   {"package": "@preview/charged-ieee:0.1.4",
                 "function": {"name": "ieee", "params": {...}}},
      "manual": {"template": "_templates/manual.typ",
                 "function": {"name": "project"}},
  }
  typst_documents = [
      ("index",   "manual.typ",   "User Manual", "Alice", "manual"),
      ("bmaster", "handbook.typ", "Field Guide", "Bob",   "ieee"),
  ]
  ```

  **Backward compatibility is by meaning, not by tolerance.** `docs/source/user_guide/
  configuration.rst:73-79` documents the 5th element as "Document class (usually `"typst"`) --
  accepted and ignored", and three real five-element tuples already exist in this repository
  (`docs/source/conf.py:73`, `examples/charged-ieee/approach1/conf.py:17`,
  `examples/charged-ieee/approach2/conf.py:16`), all passing the literal `"typst"`. Making
  `"typst"` the **name of the built-in default definition** — whose contents are the existing
  global `typst_template` / `typst_package` / `typst_package_imports` /
  `typst_template_function` values — leaves all three working unchanged and producing identical
  output, while the two `charged-ieee` examples become the showcase for the new form once
  rewritten to `"ieee"`.

  **Why it is worth a milestone.** It is the only route that closes the defect this design was
  found through: `typst_template_function`'s `params` is global *and* documented as the
  "complete, exclusive" parameter set (`docs/source/user_guide/configuration.rst:215-223`), so
  under a multi-master configuration every `typst_documents` entry's own title (element `[2]`)
  and author (element `[3]`) are **discarded with no warning** and every master renders the same
  title page. v0.8.0 ships with that as a documented limitation (owner decision, 2026-08-11).
  This is the same failure family as QUA-05.

  **Still open at this level:** whether `typst_elements`, `typst_template_mapping`, and
  `typst_template_assets` belong inside a template definition (assets and mapping look like they
  do; `typst_elements`' papersize/fontsize/lang may be a property of the document rather than of
  the template); and whether the net config surface is framed as adding one value or as the
  consolidation it actually is — four values folding into one, with the old four retained as the
  implicit `"typst"` definition and deprecable later. Note this would **reverse v0.8.0's binding
  constraint #7** ("no new `typst_*` config value"), which is scoped to that milestone's wrapper
  placement and is revisitable here.

- **CONF-06**: `typst_elements` keys beyond papersize / fontsize / lang
- **CFG-01**: User-configurable `@preview` package versions

### Quality / tooling

- **QUA-05**: `typst_authors`' missing fail-loud shim — the value was removed in v0.7.1 and Sphinx
  ignores unregistered `conf.py` variables silently, so author information vanishes without a trace

- **QUA-06**: `ruff` cannot run on the maintainer's NixOS machine (generic-linux ELF; a `flake.nix`
  repair in the same family as QUA-04)

- **QUA-07**: SEED-003 — split the `dev` extra into PEP 735 `[dependency-groups]`
- **LNK-01**: `sphinx-build -b linkcheck` CI job
- **XOS-01**: cross-OS docs-PDF CI on macOS and Windows

### Rendering

- **DEG-03**: real rendering for `graphviz` / `inheritance_diagram`
- **XREF-02**: link `manpage` / xrefs to external URLs via a configured base URL
- **CIT-07**: `sphinxcontrib-bibtex` support
- **STY-01 / STY-02 / STY-03**: user-overridable per-directive styling, a bundled Typst style module,
  and its Typst Universe publication

- **TOP-01**: box `.. contents::` as the LaTeX reference does

### Hosting

- **RTD-05**: pull-request preview builds
- **RTD-06**: documentation versions for tags before `v0.6.4`

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Doctree-layer composition (Sphinx's LaTeX `assemble_doctree` model) | Would delete the per-document `.typ` files the `-b typst` builder exists to produce. Measured as immune to B-1/B-2/defect A, and deliberately not adopted for that reason |
| Porting Sphinx's `selecting: X <- Y` toctree-parent tiebreak | `_check_toc_parents` uses a lexicographic `max(parents)`, disagrees with `_get_toctree_ancestors`, and is never consulted by `assemble_doctree`/`inline_all_toctrees`. It governs nothing about composition |
| Cross-master include deduplication | Each master is an independent PDF; a shared chapter appearing in both is correct, not duplication |
| Forcing a single root document | Multi-master is the feature, not a degenerate case |
| New runtime dependencies | Standing invariant since v0.6.0. Research confirmed every primitive needed (`include`, `set heading(offset:)`, `context`, `query`, `state`) is Typst 0.15 standard library |
| A fifth `@preview` package or a new version-lockstep site | Standing invariant; the count stays at four |
| A new `typst_*` config value for wrapper placement | Target-as-path (OUT-01) expresses both placements with no new config surface. This project has removed config values in four consecutive milestones rather than adding them |
| `modernize-typing-imports-drop-up006-up035-ignore` | `CLAUDE.md` independently instructs not to act on this until the todo lands |

## Open Questions for Planning

Not requirements — decisions each owning phase must close with measurement.

1. **`translator.py:4291`** — is this a fourth independent degradation site, or does it already route
   through `_reference_anchor_decision`? Unread during research; XREF-04 depends on the answer.

2. **`:numref:` divergence** — Sphinx bakes `:numref:` text from the project-wide `env.toc_fignumbers`
   at build time, while Typst's figure/table counters are per-compiled-wrapper. These can diverge once
   masters carry different subsets, **with no compile error to catch it**. Needs a live two-master
   fixture before being treated as settled or dismissed.

3. **B-2's RED state** — is the mid-body template re-expansion a compile fatal or a
   compiles-fine-but-wrong-output defect? Determines whether COMP-04's GATE-01 fixture uses the
   classic `TypstError` RED or a structural assertion.

4. **CR-01 self-collision policy** — now that every docname unconditionally gets a content file, a
   target resolving onto its own master's docname is a real wrapper-vs-content collision. Allow, or
   refuse? BLD-03 needs the policy fixed.

5. **Case-normalization scope** — normalize collision comparisons, or refuse case-differing targets
   outright? BLD-04 needs the policy fixed.

## Traceability

Filled at roadmap creation, 2026-08-11 (Phases 47-52).

| Requirement | Phase | Status |
|-------------|-------|--------|
| COMP-01 | Phase 47 | Complete |
| COMP-02 | Phase 47 | Complete |
| COMP-03 | Phase 47 | Complete |
| COMP-04 | Phase 47 | Complete |
| COMP-05 | Phase 49 | Complete |
| COMP-06 | Phase 49 | Complete |
| COMP-07 | Phase 49 | Complete |
| COMP-08 | Phase 49 | Complete |
| COMP-09 | Phase 49 | Complete |
| COMP-10 | Phase 49 | Complete |
| COMP-11 | Phase 49 | Complete |
| COMP-12 | Phase 49 | Complete |
| OUT-01 | Phase 47 | Complete |
| OUT-02 | Phase 47 | Complete |
| OUT-03 | Phase 47 | Complete |
| XREF-03 | Phase 48 | Complete |
| XREF-04 | Phase 48 | Complete |
| BLD-02 | Phase 47 | Complete |
| BLD-03 | Phase 47 | Complete |
| BLD-04 | Phase 47 | Complete |
| IMG-01 | Phase 50 | Pending |
| IMG-02 | Phase 50 | Pending |
| DOC-14 | Phase 51 | Pending |
| REL-07 | Phase 52 | Pending |

**Coverage:**

- v1 requirements: 24 total
- Mapped to phases: 24 ✓
- Unmapped: 0

Every v1 requirement maps to exactly one phase; no requirement appears in two phases. Phase
distribution: Phase 47 — 10 (COMP-01..04, OUT-01..03, BLD-02..04); Phase 48 — 2 (XREF-03, XREF-04);
Phase 49 — 8 (COMP-05..12); Phase 50 — 2 (IMG-01, IMG-02); Phase 51 — 1 (DOC-14); Phase 52 — 1
(REL-07).

The five "Open Questions for Planning" above are **not** requirements, carry no REQ-IDs, and are not
counted here. Each is assigned to the phase that must close it by measurement: #3 (B-2's RED state),
#4 (CR-01 self-collision policy) and #5 (case-normalization scope) → Phase 47; #1
(`translator.py:4291`'s nature) → Phase 48; #2 (`:numref:` divergence) → Phase 49.

---
*Requirements defined: 2026-08-11*
*Last updated: 2026-08-11 - traceability filled at roadmap creation (Phases 47-52)*
