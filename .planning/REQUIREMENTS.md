# Requirements: typsphinx v0.7.0 — API rendering design overhaul

**Defined:** 2026-07-29
**Core Value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered
output on the current ecosystem — and, from this milestone, output that is *well typeset*, not
merely correct.

## Verification legend

The design authority was demoted to a **reference** during scoping (owner decision 2026-07-29), so
"matches Sphinx's LaTeX PDF" is no longer the bar. Every requirement below is therefore tagged with
how it is judged:

- **[M] Mechanical** — checkable by an automated assertion over the emitted `.typ`, the compiled
  PDF's extracted text, or `pypdf` bounding boxes. These carry the GATE-01 fixtures.

- **[V] Visual UAT** — an aesthetic judgement the owner makes by looking at the rendered PDF. No
  automated gate can settle it; the phase records the evidence and the owner signs off.

Most requirements are **[M]** for their structural property and **[V]** for their final look; the
tag names whichever is *load-bearing* for accepting the requirement.

## v1 Requirements

### Signatures — the `desc_*` family (SIG)

Measured 2026-07-29 by building a `py:` domain sample through `-b typst` (the same doctree autodoc
produces). Reference font roles from `sphinxlatexobjects.sty` + `pdftotext -bbox` on the reference
PDF.

- [x] **SIG-01** [M]: A `desc_name` (the object's own name) renders in **bold monospace**. Today it
      renders through `strong({...})` — proportional bold — because `visit_desc_signature` delegates
      wholesale to `visit_strong` via a dummy node.

- [x] **SIG-02** [M]: A `desc_addname` (the module/class qualifier prefix, e.g. `sphinx.builders.`)
      renders in **regular-weight monospace**, visually subordinate to the name. Today it carries no
      styling at all.

- [x] **SIG-03** [M]: A `desc_annotation` (the leading `class ` / `exception ` keyword) renders in
      the **same bold monospace as `desc_name`** — the reference gives it no separate treatment.

- [x] **SIG-04** [M]: Signature parameters (`desc_parameter`, including any inline type annotation)
      render **distinctly from `desc_name`** — the reference uses italic proportional. Today they
      emit plain `text()` with no distinguishing style.

- [x] **SIG-05** [M]: The parameter-list delimiters (`(`, `)`, `,`, `=`, and `desc_optional`'s
      brackets) render in monospace, consistent with the name.

- [x] **SIG-06** [M]: `desc_returns` renders a real arrow glyph (e.g. `→`) rather than the ASCII
      `->` it emits today.

- [x] **SIG-07** [M]: A long fully-qualified signature **does not overflow the right page margin**.
      The strategy must be derived by measuring real long signatures from the Sphinx `doc/` corpus —
      the v0.6.1 FID-01a fix (U+200B injection + fr-weighted columns) was for wide *tables* and must
      not be assumed to transfer to full-width signatures.

- [x] **SIG-08** [M]: Sibling signatures (overloads, alias groups, multi-option directives) and
      their surrounding blocks are separated by exactly one break — the doubled `parbreak()` runs
      visible in the measured output are gone.

- [x] **SIG-09** [M]: A signature and the first line of its description body are **not split across
      a page break**.

### Indentation and nesting (IND)

The reference's recurring indent quantum is **≈22–25pt (≈2.2–2.5em at 10pt)**, measured
independently at three sites (a class's `desc_content`, a nested member's body, a field-list
wrapper) and agreeing within 3pt.

- [x] **IND-01** [M]: A `desc_content` body is indented one step relative to its own
      `desc_signature`. Today `visit_desc_content` and `depart_desc_content` are **both `pass`**, so
      the body sits flush with the signature and no hanging indent exists at all.

- [x] **IND-02** [M]: Indentation is **cumulative with nesting depth** — a `py:method::` inside a
      `py:class::` has its description one step deeper than the class's own body. Today a nested
      member renders at the same left margin as a top-level `py:function::`, so class membership is
      visually unrecoverable. Verified by asserting a nested member's body x-position is strictly
      greater than its parent's.

- [x] **IND-03** [M]: A nested member's **own signature** aligns with its parent's body margin — it
      does **not** receive a further indent step. (Stated as a requirement because the naive
      implementation over-indents; the reference never does this.)

- [x] **IND-04** [M]: One shared indent constant drives the desc/field indent contexts — desc
      nesting and field lists — rather than independent magic numbers per node type. (Block quotes
      are an intentional non-consumer: they use Typst's own `quote(block: true, …)` default spacing.
      Scoped by 38-CONTEXT.md D-04, which measured the alternatives; the requirement forbids
      per-node magic numbers, it does not force one visual depth on every indent context.)

- [x] **IND-05** [M]: The nesting-depth counter **resets correctly across sibling `desc` nodes**, so
      depth cannot leak and accumulate unboundedly across a document.

### Info fields — `field_list` (FLD)

- [x] **FLD-01** [M]: A field list (Parameters / Returns / Return type / Raises / Variables) is
      indented one step beyond the surrounding description body. Today it is not indented at all.

- [x] **FLD-02** [M]: A field body with multiple values renders as a **bulleted list**; a
      single-value body stays inline prose. (The inline half already works via
      `_last_field_body_was_inline`; the bulleted half must be verified to survive the redesign.)

- [x] **FLD-03** [M]: Inside a field body, a parameter's **name and type carry monospace treatment
      distinct from the plain-bold field label** — the reference deliberately uses a *different*
      recipe here than in the signature, and collapsing the two would be wrong.

### Admonitions, rubric, and topic (ADM)

Bucket taxonomy from `sphinx.sty` — four colour groups, not ten independent styles.

- [x] **ADM-01** [M]: `seealso` renders in the same bucket as `hint`/`tip` (green "success"), not
      the blue "note" bucket it uses today.

- [x] **ADM-02** [M]: `attention` renders in the same bucket as `danger`/`error` (red), not the
      orange "warning" bucket it uses today.

- [x] **ADM-03** [M]: A generic `.. admonition::` renders as a **styled box carrying its own custom
      title**, not the unstyled base `clue` it produces today. The dynamic-title plumbing already
      exists via `_pending_admonition_title`.

- [x] **ADM-04** [V]: Admonition types stay distinguishable **in greyscale**. The four title-band
      tints are all mid-high-luminance pastels and desaturate to similar greys, so the distinction
      must be carried by icon and border, not hue alone. **Met on icon-shape grounds** — the owner's
      recorded sign-off (`39-ADM04-SIGNOFF.md`) confirms the four kinds are distinguishable via icon
      shape in the greyscale render; the title-band luminance itself is uniform and carries no
      distinguishing signal, recorded as an explicit caveat, not a defect, since the requirement
      only needs *some* non-hue channel to carry the distinction and icon shape does.

- [x] **ADM-05** [M]: A `rubric` nested inside a description body **indents with that body** rather
      than sitting flush to the page margin — it follows structural nesting and gets no indent rule
      of its own. (`rubric` also carries autodoc's "Options" heading, so this lands on API pages.)

- [x] **ADM-06** [M]: `rubric` no longer routes through the shared `visit_strong` dummy-node
      delegation, so it and `desc_signature` can be styled independently.

### Citations (CIT)

Greenfield — `translator.py` has zero citation handlers today. Scope is bare docutils citations
(`.. [Label]` definition + `[Label]_` reference), confirmed by `git show 8bed1a3`;
`sphinxcontrib-bibtex` is not involved. Typst's own `bibliography()`/`cite()` machinery is
deliberately unused — it consumes structured `.bib`/Hayagriva data in order to CSL-format and
reorder, while docutils citations are already-written prose with references already resolved.

- [ ] **CIT-01** [M]: A document containing a citation **compiles**. Today the unhandled
      `citation`/`label` nodes emit adjacent expressions with no separator, so `-b typstpdf` fails
      outright and `-b typst` silently writes an invalid `.typ`. *(This is the one requirement in
      the milestone that keeps the classic GATE-01 RED — a real `TypstError` before the fix.)*

- [ ] **CIT-02** [M]: A citation definition renders as a **labelled entry with a hanging indent** —
      `[Label]` followed by the entry body, with continuation lines aligned past the label.

- [ ] **CIT-03** [M]: An in-text `[Label]` reference **links to its definition**, resolved from
      docutils' own `refid`. No document-order pre-pass is required (verified by executing docutils:
      `citation_reference.refid` resolves directly to `citation.ids[0]`, and Typst's `link(<label>)`
      resolves whole-document regardless of source order).

- [ ] **CIT-04** [M]: A definition carries **back-references to every citing location**, from
      docutils' `backrefs` — the same navigation Sphinx's HTML renders as `(1,2)`.

- [ ] **CIT-05** [M]: The citation syntax Phase 22.2 stripped out of `examples/charged-ieee/`
      (both approaches) is **restored**, and both samples build clean. An IEEE paper template
      shipping without a references section is the concrete defect this closes.

- [ ] **CIT-06** [M]: Citation entries render in **document order, unsorted**, matching docutils'
      own semantics.

### Spacing regression (MATH)

- [x] **MATH-02** [M]: Block math inside a list item emits **no redundant blank line**. Carried from
      the v0.6.5 Phase 34 review (WR-01) — `visit_math_block`'s unconditional `"\n\n"` stacks with
      the `list_item_needs_separator` flag Phase 34 added. Deferred then only because it would have
      forced re-deriving the GATE-01 fixture's expected strings immediately before a release; this
      milestone re-derives them anyway.

### Release and CI (REL)

- [ ] **REL-04** [M]: The GitHub Release body is the **curated `## [X.Y.Z]` CHANGELOG section**, not
      the `git log --pretty` commit dump `release.yml` generates today (the v0.6.4 body was 308
      lines, of which 296 were that dump). `release.yml` does not read `CHANGELOG.md` at all today.

- [ ] **REL-05** [M]: v0.7.0 is released — version bumped as the sole literal in `pyproject.toml`
      with `uv.lock` and `README.md` in lockstep, a curated CHANGELOG entry written, and the
      publish executed at `/gsd-complete-milestone` (tag → `release.yml` → PyPI + GitHub Release,
      plus the standing second tag on `typsphinx-doc-translations`).

## Future Requirements

Acknowledged, not in this roadmap.

### User-configurable styling

- **STY-01**: Let a user restyle each directive kind from their own template. **Measured available**
  via label selectors (`show <typsphinx-signature>: it => …`) — verified to fire on every
  occurrence, cross `#include()` boundaries, and leave defaults intact when the template does
  nothing. Dropped from v0.7.0 when the goal narrowed to "typsphinx itself produces good output."
  Note the shape originally wanted (`show api-signature: …` on a plain function) is **impossible** —
  `show`/`set` selectors accept only element functions, and user-defined element types are
  unimplemented upstream (`typst/typst#147`, open since 2023-03-22, no committed timeline).

- **STY-02**: Bundle the styling primitives as an importable Typst module shipped inside typsphinx.
  Researched and viable (unconditional write path, two import-injection sites, import-path sync);
  dropped because its main justification was STY-01.

- **STY-03**: Publish that module to Typst Universe. Moot while STY-02 is deferred.

### Other deferred items

- **TOP-01**: Box `.. contents::` (local TOC) the way the reference does — see Out of Scope for why
  this milestone keeps the existing behaviour.

- **CIT-07**: `sphinxcontrib-bibtex` support (`:cite:` role, `.bib` files). A different node family
  entirely, and the natural implementation would use Typst's native `bibliography()`/`cite()` — the
  machinery this milestone deliberately avoids for docutils citations. Verified feasible:
  `bibliography(bytes(...))` compiles without a file on disk.

- **CFG-01** — user-configurable `@preview` package versions (deferred since v0.5.0)
- **XOS-01** — macOS/Windows `docs-pdf` CI (deferred since v0.5.0)
- **DEG-03** — real rendering for `graphviz` / `inheritance_diagram` (deferred since v0.6.1)
- **XREF-02** — xrefs to external URLs via a configured base URL (deferred since v0.6.1)
- **CONF-06** — `typst_elements` keys beyond papersize/fontsize/lang (deferred since v0.6.3)
- **RTD-05** — pull-request preview builds (one owner-side checkbox)
- **LNK-01** — a `sphinx-build -b linkcheck` CI job

## Out of Scope

Explicitly excluded, with reasoning, to prevent scope creep and re-litigation.

| Item | Reason |
|---|---|
| A box, frame, or background tint on signatures | The reference deliberately does not do this. The temptation is to add a `codly`-style code background to "make signatures pop"; that would be a deviation dressed as an improvement |
| Per-token syntax highlighting inside signatures (colouring `desc_sig_operator`/`desc_sig_keyword` separately) | Sphinx's LaTeX writer has **zero** visitor overrides for the `desc_sig_*` family — every fragment inside a parameter inherits one style. Token colouring risks looking gaudy and fails greyscale |
| Reusing the signature's italic-proportional parameter style for field-list parameter echoes | The reference deliberately uses two different recipes for the same semantic content in the two contexts. Collapsing them is unfaithful, not simpler |
| A literal grid/table layout for Parameters | It is a description list, not a table. A grid also breaks awkwardly across pages |
| Indenting a nested member's signature as far as its description | Over-indents; matches no measured case. Covered positively by IND-03 |
| A drop shadow on admonition boxes | Only `topic`/`contents`/`sidebar` boxes carry one in the reference. Adding it to note/warning blurs the grammar separating "aside" from "structural" boxes |
| Rounded corners on admonitions | The apparent rounded example in the reference PDF is a *user-customized* demonstration chapter, not the default. The default is sharp-cornered |
| Boxing `.. contents::` (local TOC) | The reference boxes it identically to `topic`, but typsphinx's box-less rendering is a deliberate prior decision (D-05), and with the reference demoted from authority it no longer compels the change. Filed as Future TOP-01 |
| User-overridable per-directive styling | Goal narrowed by the owner. Filed as Future STY-01 with the measured mechanism recorded so nothing is lost |
| A bundled Typst style module | Its main justification was the above. Direct emission keeps each `.typ` self-contained and removes a phase. Filed as Future STY-02 |
| Typst Universe publication | Moot without the module |
| A new `@preview` package | Research confirmed every required primitive (`raw`, `par(hanging-indent:)`, `block(inset:/stroke:/breakable:)`, `grid`, `terms`, `pad`) is Typst 0.15 standard library. The count stays at four with no new version-lockstep site |
| Typst's `bibliography()`/`cite()` for docutils citations | Consumes structured `.bib`/Hayagriva data in order to CSL-format and reorder. docutils citations carry no structured fields and must not be reordered |
| Page-by-page comparison against the reference PDF | The reference was demoted to a starting point, not an authority. Its `master`-vs-`v9.1.0` version skew mattered only under this comparison and is now moot |

## Milestone invariants

Standing constraints this milestone must not violate. Verified mechanically at release prep.

1. **Zero new runtime dependencies.**
2. **The `@preview` package count stays at four**, with no new version-lockstep site.
3. **Every node-handler change ships a real `typst.compile()` GATE-01 regression fixture**, recorded
   **red against the unfixed code** before being accepted as green.

4. **GATE-01 RED is redefined for this milestone.** Every prior fixture proved a compile fatal; every
   design defect here compiles successfully today, so RED must be a structural / regex /
   `pypdf`-text assertion defined **before** any code is written. Regenerating expected strings from
   the new code's own output is a violation of this invariant, not a shortcut. CIT-01 is the sole
   exception and keeps the classic `TypstError` RED.

5. **Test migration is owned per phase**, never deferred to a single blanket closing pass. Measured
   blast radius: 10 test files, 61 render-gate classes.

6. **"Anywhere under X" success criteria are checked by a repo-wide grep at discovery time**, never
   against the files a requirement happens to name (standing since v0.6.4).

## Traceability

Populated during roadmap creation (2026-07-29). Every v1 requirement maps to exactly one phase.
Phase numbering continues from v0.6.5's last phase (35).

| Requirement | Phase | Status |
|-------------|-------|--------|
| SIG-01 | Phase 37 | Complete |
| SIG-02 | Phase 37 | Complete |
| SIG-03 | Phase 37 | Complete |
| SIG-04 | Phase 37 | Complete |
| SIG-05 | Phase 37 | Complete |
| SIG-06 | Phase 37 | Complete |
| SIG-07 | Phase 37 | Complete |
| SIG-08 | Phase 37 | Complete |
| SIG-09 | Phase 37 | Complete |
| IND-01 | Phase 38 | Complete |
| IND-02 | Phase 38 | Complete |
| IND-03 | Phase 38 | Complete |
| IND-04 | Phase 38 | Complete |
| IND-05 | Phase 38 | Complete |
| FLD-01 | Phase 38 | Complete |
| FLD-02 | Phase 38 | Complete |
| FLD-03 | Phase 38 | Complete |
| ADM-01 | Phase 39 | Complete |
| ADM-02 | Phase 39 | Complete |
| ADM-03 | Phase 39 | Complete |
| ADM-04 | Phase 39 | Complete |
| ADM-05 | Phase 39 | Complete |
| ADM-06 | Phase 36 | Complete |
| CIT-01 | Phase 40 | Pending |
| CIT-02 | Phase 40 | Pending |
| CIT-03 | Phase 40 | Pending |
| CIT-04 | Phase 40 | Pending |
| CIT-05 | Phase 40 | Pending |
| CIT-06 | Phase 40 | Pending |
| MATH-02 | Phase 36 | Complete |
| REL-04 | Phase 41 | Pending |
| REL-05 | Phase 41 | Pending |

**Per-phase totals:**

| Phase | Name | Requirements | Count |
|-------|------|--------------|-------|
| 36 | Shared-Emission Seam Cleanup | ADM-06, MATH-02 | 2 |
| 37 | Signature Typography — the `desc_*` Family | SIG-01..SIG-09 | 9 |
| 38 | Structural Indentation + Info Fields | IND-01..IND-05, FLD-01..FLD-03 | 8 |
| 39 | Admonition Taxonomy + Rubric Nesting | ADM-01..ADM-05 | 5 |
| 40 | Citations — Full Round Trip | CIT-01..CIT-06 | 6 |
| 41 | v0.7.0 Release Automation + Release Prep | REL-04, REL-05 | 2 |

**Coverage:**

- v1 requirements: **32** total (9 SIG + 5 IND + 3 FLD + 6 ADM + 6 CIT + 1 MATH + 2 REL). *Corrected
  2026-07-29 during roadmap creation — this line previously read "29 total", which was a tally
  error; no requirement was added, removed, or reworded.*

- Mapped to phases: 32
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-29*
*Last updated: 2026-07-29 — traceability populated at roadmap creation (Phases 36–41)*
