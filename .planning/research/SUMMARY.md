# Project Research Summary

**Project:** typsphinx
**Domain:** Typographic redesign of a Sphinx→Typst translator's API-description, admonition, and citation rendering
**Milestone:** v0.7.0 — API rendering design overhaul
**Synthesized from:** STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md
**Researched:** 2026-07-29
**Confidence:** HIGH overall (MEDIUM for the citation-design section only — the design authority contains no live citation example)

> **Provenance note (orchestrator, 2026-07-29):** the synthesizer agent hit the known issue-#222
> false refusal — it returned this document inline while fabricating a "system restrictions on
> report-file creation" write block. No such restriction exists. The orchestrator persisted the
> returned document here, unescaping HTML entities and correcting one gap item the agent re-raised
> after it had already been measured and closed (see "Gaps to Address Before Planning" #2).

## Executive Summary

The v0.7.0 redesign reshapes how typsphinx renders API documentation (signatures, field lists,
admonitions, citations) to match Sphinx's own LaTeX-rendered PDF, adopted as this milestone's design
authority. **No new Typst `@preview` packages are needed** — every required primitive exists in the
Typst 0.15 standard library, so the milestone's "the count stays at four" invariant holds with zero
tension. The critical path is to bundle one style module (`_typsphinx.typ`, typography-only,
~100–150 lines) inside the wheel and inject its import at two code-generation points
(`writer.py` for included documents, `template_engine.py` for master documents).

The **highest-risk seam** is not in the new code but in the old: `desc_signature` and `rubric` both
delegate to `visit_strong()`/`depart_strong()` through a dummy-node trick, so any change to
`strong()`'s shape silently affects two unrelated node families. That decoupling must land before
either family is restyled. The **most expensive single component** is `desc_content`'s cumulative
indent, which requires a nesting-depth counter and feeds six or more downstream features.
**Citations are greenfield but structurally cheap** — they need no document-order pre-pass, because
Typst's `link(<label>, ...)` resolves against the whole compiled document regardless of source
order, unlike `footnote()`'s call-site-body API that forced the existing footnote pre-pass.

The single most important finding is a **process change, not a technical one**. Every prior GATE-01
fixture in this project proved a compile fatal — RED was a `TypstError`, GREEN was a valid `%PDF`.
Every defect in *this* milestone compiles successfully today; the output is ugly, not broken. "Does
not compile" is therefore no longer available as the RED state, and each phase must define a
measurable structural / regex / pypdf-text assertion against the authority **before** any code is
written. Without that discipline, the standing invariant degrades into regenerating expected strings
from whatever the new (possibly wrong) code happens to emit.

## Key Findings

### From STACK.md

- Every typesetting primitive exists in stdlib: `raw()` for monospace, `par(hanging-indent:)` for
  wraps, `block(inset:)` for whole-block indent, `grid()`/`terms()` for two-column layout,
  `block(stroke: (left: ...))` for coloured rules, `block(breakable: false)` for page-break
  avoidance
- Bundle the new module as a `.typ` file under `typsphinx/templates/` — the existing
  `pyproject.toml` glob already covers it (zero config edits needed)
- Design the module API as **named functions only** (`#let api-signature(body, ...) = {...}`), not
  bare `#show`/`#set` rules — such rules do not propagate through an import. To apply styling
  automatically, expose a named wrapper (`with-api-styles(body)`) that each generated file applies
  explicitly via `#show:`
- **Module scoping is not automatic:** if the module calls `gentle-clues`/`codly`/`mitex`
  internally, it must import them itself — the outer file's imports are invisible inside imported
  modules (design decision: keep typography-only, or accept a new version-sync site)

### From FEATURES.md

- **Recurring indent quantum ≈22–25pt (≈2.2–2.5em @ 10pt)** — measured by `pdftotext -bbox` on the
  authority PDF, independently in `desc_content` and field-list contexts, agreeing within 3pt. One
  constant should drive all three consumers (desc nesting, field-list block + body, other
  block-indent contexts)
- Signature styling is font-specific, not uniform bold: `desc_name` → **bold monospace**,
  `desc_addname` → regular monospace, `desc_annotation` → **bold monospace**,
  `desc_parameter` → **italic proportional** (NOT monospace — a deliberate distinction from how the
  same parameter is styled inside a field body, where it is bold monospace name + italic monospace
  type)
- **No box or frame on signatures** (anti-feature guard) — resist the urge to "make it pop"
- The field list is a run-in description list, not a table: multi-value = bulleted list,
  single-value = inline. Field name = bold label
- **Admonition colour buckets (4 groups):** three concrete mismatches against the authority's
  taxonomy — `seealso` (currently info/blue → should be tip/green), `attention` (currently
  warning/orange → should be danger/red), generic `.. admonition::` (currently unstyled base `clue`
  → should be `info` with a dynamic title). All are one-line fixes
- `rubric` = no visual style beyond bold text at the context's indent level (no box, background, or
  resizing)
- `.. topic::` and `.. contents::` (local TOC) are boxed identically in the authority (same
  `sphinxShadowBox` family, plus a drop shadow neither gets elsewhere). Current typsphinx: topic
  boxed ✓, contents box-less ✗ per the deliberate D-05 choice — a genuine open design decision
- Citation bibliography: vanilla LaTeX `thebibliography` — plain `[Label]` entries, a
  dynamically-sized hanging indent derived from the widest label capped at 8 characters, document
  order never sorted, working cross-doc anchor/link

### From ARCHITECTURE.md

- **The style module must be written and importable unconditionally in every routing branch** —
  unlike `_template.typ` (deliberately never written on the `typst_package`-alone route), the new
  module must exist even there, because translator node handlers call its functions from
  `self.body`, which is generated identically in all routes. Implement a new
  `_write_style_module_file()` in `builder.py`, called unconditionally, separate from
  `_write_template_file()` and its conditional-skip pattern
- **Two separate import-injection sites:** (1) the included-doc preamble at `writer.py:149–166`,
  (2) the master-doc render in `template_engine.TemplateEngine.render()`. Both must emit the
  import-path line identically (reuse the existing per-depth relative-path helper; do not
  re-implement it). The master path's hoisted-imports gate
  (`template_engine.py:609–619`, `will_inline_default_template`) must **not** apply to the style
  module — unlike the four `@preview` imports, it is not duplicated inside `base.typ`
- The three in-repo custom templates are safe **by construction** — their content is loaded as
  opaque bytes and never parsed or rewritten — verified by tracing the load/render path and reading
  all three files in full
- **Highest-blast-radius seam:** `desc_signature` and `rubric` both delegate to
  `visit_strong()`/`depart_strong()` via a dummy node. **Decouple immediately** — give each its own
  open/close pair before changing either
- **Citations need no document-order pre-pass** — verified by executing docutils directly:
  `citation_reference.refid` resolves straight to `citation.ids[0]`, and Typst's `link(<label>, ...)`
  (already used for same-document xrefs) resolves whole-document regardless of source order
- **Five shared protocols demand explicit per-handler discipline:** paragraph separation, code-mode
  inline-concat (5 distinct contexts), list-item separation, buffer-swap state (save/restore beyond
  `self.body`), and forced sibling-boundary breaks. MATH-01 and the v0.6.x clusters were all
  single-protocol misses

### From PITFALLS.md

- **Separator protocol = the recurring fatal class:** code-mode juxtaposition (two expressions with
  nothing between them inside `#{...}`) is a parse error, and a source `"\n"` is parser-OK but
  produces zero visual separation. A 7-step checklist was derived line-by-line from the actual
  helpers (`_add_paragraph_separator`, `_emit_inline_concat_separator`,
  `_mark_inline_concat_content`, `_emit_forced_break`, `_emit_id_anchors`). Those helpers must be
  *called*, not pattern-matched from a neighbouring handler
- **Buffer-swap state clobbering breaks downstream silently:** swapping `self.body` alone is
  insufficient; `in_paragraph`/`paragraph_has_content` and, where applicable,
  `in_list_item`/`list_item_needs_separator` must be saved and restored, using a stack for nestable
  swaps. This shipped as a real bug in v0.6.0 Phase 14. Only about 5 of ~20 buffer-swap sites have
  real-compile coverage today
- **Label attachment rules are strict:** Typst's `<label>` postfix is markup-mode only —
  `block(...) <label>` inside `#{...}` is a parse fatal (the v0.6.0 "labels attached to code-mode
  statements" class). The existing `_emit_id_anchors()` pattern — a separate, self-contained markup
  statement `[#metadata(none) <label>]` on a following line — is safe to reuse even when signatures
  are wrapped in `block()`/`grid()`. Every label routes through
  `_namespace_label()`/`_sanitize_label()`
- **Layout traps that are genuinely new ground:** page-break mid-signature (`block(breakable:)` is
  unused anywhere in the codebase today), nesting-depth leaking across siblings (reset at the
  outermost `desc`, following the documented `_line_block_depth` idiom), long fully-qualified
  signatures overflowing the margin (re-derive the strategy — do not assume the FID-01a ZWSP
  approach transfers from tables to full-width signatures), colour-only cues failing in greyscale,
  CJK font-fallback shadowing (a new `set text(font: ...)` must extend the existing Noto Serif CJK JP
  fallback, not replace it)
- **GATE-01 methodology change (CRITICAL)** — see the dedicated section below
- **Test-suite blast radius measured:** 10 files, 61 render-gate classes
- **Module import-path lockstep:** the new module's import-path line (not a version — it is bundled)
  must stay in sync between `writer.py` and `template_engine.py`, reproducing the two-site shape the
  `@preview` imports already have. `builder.py`'s `_write_template_file()` early return for
  `typst_package`-alone builds (BUG-A's class) must not be inherited by the new copy step
- **Citation greenfield risks:** the docutils citation node structure (definition + reference +
  label child) differs from footnotes in ways that break a naive copy. The exact failure mode is
  already recorded first-hand in `examples/charged-ieee/`'s removal-commit message

## Critical Decisions for Requirements Definition

These were each flagged by one or more research agents specifically so they would be decided
explicitly rather than fall out of implementation by default.

1. **Style-module internal `@preview` dependencies** — typography-only, or wrap
   `gentle-clues`/`codly`/`mitex` internally (which creates a new version-lockstep site, in tension
   with the milestone invariant)? **Recommendation:** typography-only; keep the admonition
   gentle-clues calls in `translator.py:_visit_admonition`

2. **Field-list two-column layout** — `grid(columns: (auto, 1fr))` for fine control, or `terms()`
   as the semantically native element? **Recommendation:** `grid` for column-width control — decide
   consciously, not by default

3. **`.. contents::` (local TOC): boxed or box-less?** The deliberate D-05 box-less choice versus
   authority evidence to box it identically to `topic`. **No recommendation** — a design choice with
   UX implications; decide at requirements

4. **Citation-label namespacing** — per-document (allowing a duplicate `[GoF95]` across chapters) or
   merged project-wide? **Recommendation:** per-document (mirrors the existing `_namespace_label`
   default); document the choice explicitly

5. **Signature hanging-continuation indent accuracy** — a fixed approximation, or computed alignment
   to the first parameter? Typst has no direct `\parbox`-at-computed-width primitive.
   **Recommendation:** a fixed approximation validated against the corpus's longest realistic
   signatures. **Complexity:** medium-high if exactness is required; low if approximate is acceptable

6. **Citation bibliography pre-pass?** Architecture finds none needed (use `link()` whole-document
   resolution, as `:ref:` already does). **Recommendation:** no pre-pass; let dangling references
   surface as Typst compile fatals

7. **Style-module filename and structure** — one file or several, and what output filename?
   **Recommendation:** one file (keeps the two-site import-sync pitfall simple). If it exceeds
   ~200 lines, refactor then

## Single Shared Indent Constant

**One constant must drive all indent consumers:** ≈22–25pt (≈2.2–2.5em @ 10pt), measured
independently in `desc_content` and field-list contexts and agreeing within 3pt.

| Consumer | Current | Target |
|----------|---------|--------|
| `desc_content` indent | `pass` (zero — the defect) | +2.2–2.5em |
| `field_list` block indent | `pass` (zero — the defect) | +2.2–2.5em |
| Field-body indent | Likely correct | Verify it uses the same constant |
| Nested `py:method::` under `py:class::` | `pass` (cumulative; needs a depth counter) | +2.2–2.5em per level |

Define **one named constant in the style module** (e.g. `#let indent-unit = 2.4em`) and use it for
all consumers. Document which consumer drives each use.

## GATE-01 Methodology Change — Process, Not Tool

**Standing invariant since v0.6.0:** "every node-handler change ships a real
`sphinx-build → typst.compile()` fixture, recorded **red** against the unfixed code."

**This milestone inverts the assumption.** Every prior fixture proved a compile fatal (RED =
`TypstError`, GREEN = `%PDF`). This milestone's defects — proportional instead of monospace, missing
indent, invisible nesting — **all compile successfully today**. RED cannot be "does not compile."

**Each phase must define a measurable RED assertion *before* coding:**

- Structural/regex — e.g. "the signature uses `raw(...)`, not a bare `text(...)`"
- pypdf-text — extract bounding boxes, assert indent/alignment against the authority, run red
  against the unfixed code
- Manual visual — side-by-side authority PDF vs typsphinx output with recorded evidence

**Consequence for test maintenance:** exact-string assertions *will* break — expected and
intentional. Do **not** mass-regenerate them from a fresh pytest run. Derive the new expected `.typ`
shape from the authority (or a hand-reasoned equivalent) *before* running the new code. Update per
sub-area within the owning phase, never as a single blanket closing phase.

## Highest-Blast-Radius Seam

`desc_signature` and `rubric` both delegate to `visit_strong()`/`depart_strong()` via a dummy-node
trick. Any change to `strong()`'s open/close shape silently affects both unrelated families.
**Decouple first** — give each its own pair before changing either.

## Reconciled Build Order

All three of ARCHITECTURE, PITFALLS, and FEATURES proposed a sequence independently. They agree on:
module scaffolding first; `desc_*`/`field_list` as the broad-blast-radius centre; citations as
independently landable; math/release housekeeping as unrelated. They differ on where the
`visit_strong` decoupling sits (ARCHITECTURE folds it into the desc phase; PITFALLS wants it
isolated) and on whether admonitions precede or parallel the desc work. The reconciliation isolates
the decoupling as its own gate, because it is the one change whose correctness criterion is
"rendering is byte-identical before and after."

| Phase | Deliverable | Rationale | Deps |
|-------|-------------|-----------|------|
| **1** | Style-module scaffolding (`_typsphinx.typ`, `_write_style_module_file()`, import injection at both sites) | Additive, low blast radius. Everything later depends on it. Fixture: the module appears in `outdir` and imports cleanly from all routes, **including `typst_package`-alone** | None |
| **2a** | Decouple `desc_signature`/`rubric` from the shared `visit_strong` | Prerequisite for independent restyling. Gate: rendering identical pre/post | 1 |
| **2b** | Redesign `desc_*` and `field_list` (fonts, indent, nesting) | Broad blast, high complexity. Sequence: indent → nesting depth → signature wrapping → field-list layout. GATE-01 per sub-area with structural RED assertions | 1, 2a |
| **3** | Admonition / rubric / topic redesign, incl. the three colour-bucket fixes | Additive-shaped, moderate blast. Can run parallel to 2b once 1 + 2a land | 1, 2a |
| **4** | Citation support (greenfield handlers) | Structurally independent. Apply the full separator-protocol checklist from day one. Fixture: forward reference, 2+ citations, 2+ documents | 1 |
| **5** | `visit_math_block` blank-line fix + `release.yml` CHANGELOG extraction | Self-contained, unrelated to the design work | None |
| **6** | Release prep (version bump, CHANGELOG) | Standard final phase | 1–5 |

## Confidence Assessment

| Area | Confidence | Basis | Gaps |
|------|-----------|-------|------|
| **Stack** | **HIGH** | Live Typst 0.15 docs fetched directly; `typst/typst#595` cross-check on include/import scoping; every typsphinx claim cited `file:line` | None |
| **Features** | **HIGH** (design), **MEDIUM** (citations) | `pdftotext -bbox` measurement of the authority PDF + line citations into Sphinx's own installed sources (the LaTeX writer module and the `.sty` files, both read from the venv — external references, not repository files); citations have no live example in the authority corpus (verified by exhaustive grep) | Citation polish unverified; `grid` vs `terms` open; `.. contents::` deferred to requirements |
| **Architecture** | **HIGH** | Full-file reads of `builder.py`/`writer.py`/`template_engine.py`; all three custom templates read; docutils executed directly to verify citation node structure | Module `@preview` deps is a design choice, not a finding; the fourth-site risk reasoned from documented scoping, not a live `typst compile` |
| **Pitfalls** | **HIGH** | Every pitfall is either a previously-shipped artifact-cited defect or derived from a direct read of the translator | Overflow strategy must be re-derived against real corpus signatures; breakability and colour are new ground for this codebase |
| **Overall** | **HIGH** | Three angles converge on the same build order; decisions named rather than defaulted; seams identified; the process change is explicit | Requirements must decide the seven questions above |

## Gaps to Address Before Planning

1. **Signature overflow (medium).** U+200B injection was the FID-01a fix for wide *tables*;
   signatures occupy full page width — a different context. Measure realistic long signatures from
   the Sphinx corpus, then decide between ZWSP injection, explicit wrap points, or a font-size
   reduction. Do not assume the existing approach transfers.

2. **Citation flavour — CLOSED, not a gap.** *(Orchestrator correction, 2026-07-29: the synthesizer
   re-raised this after it had been measured and closed.)* The syntax stripped from
   `examples/charged-ieee/` was **bare docutils citations** — a `.. [Krizhevsky2012] …` definition
   plus a `[Krizhevsky2012]_` inline reference — verified via `git show 8bed1a3`. Zero `.bib` files
   exist anywhere under `examples/`, and no `conf.py` declares a bibtex extension.
   `sphinxcontrib-bibtex` and its `:cite:` role are **not** involved and are out of scope. No
   doctree dump is required before the citation phase.

3. **CJK font-fallback baseline (low-medium).** New font declarations risk shadowing the existing
   Noto Serif CJK JP fallback in the `ja` RTD build. Confirm the existing fallback chain and
   establish a re-run protocol for the D-03 four-check bar (page count, byte-identical text, glyph
   present, visual) as part of release prep.

## Implications for Roadmap

**Six sequenced phases** (table above) with explicit dependencies. **Blast-radius call-outs:**
Phase 1 is additive and prerequisite; Phase 2a exists solely to eliminate the highest seam before
any reshape; Phases 2b–3 carry broad impact and concentrate the GATE-01 fixture invalidation.
**Research flags:** Phases 2b, 3, and 4 likely warrant phase-level research during planning
(specific RED assertions, overflow strategy, citation node structure). **Standard patterns:**
Phase 1 scaffolding and Phase 5 math/release follow proven patterns and can skip research; Phase 6
uses the existing release-prep flow.

**Ready for Requirements Definition.**

## Sources

- `.planning/research/STACK.md` — Typst module/import mechanics, verified stdlib primitive
  signatures, the no-new-package verdict, Typst Universe packaging notes, and the Python-packaging
  change needed to ship a second bundled `.typ`
- `.planning/research/FEATURES.md` — per-area table-stakes / differentiator / anti-feature tables
  for signatures, description bodies, info fields, admonitions, rubric/topic, and citations, with
  `pdftotext -bbox` measurements and LaTeX-source line citations
- `.planning/research/ARCHITECTURE.md` — integration points with `file:line` citations, the
  new-vs-modified component split, the custom-template non-breakage trace, and the citation
  doctree-structure verification
- `.planning/research/PITFALLS.md` — the separator-protocol checklist, buffer-swap rules,
  label-attachment rules, layout traps, test-suite blast radius, module-lockstep hazard, and the
  GATE-01 methodology change
- Design authority: `https://app.readthedocs.org/projects/sphinx/downloads/pdf/master/`
  (703 pages, pdfTeX-1.40.22, built 2026-07-22)
- Sphinx LaTeX style sources in the local venv: `sphinxlatexobjects.sty` (386 lines),
  `sphinxlatexadmonitions.sty` (408), `sphinxpackageboxes.sty` (827),
  `sphinxlatexindbibtoc.sty` (69)
