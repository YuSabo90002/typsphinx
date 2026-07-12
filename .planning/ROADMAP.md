# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- 🚧 **v0.6.0 — real-world robustness** — Phases 11–15 (in progress)

## Phases

**Phase Numbering:**

- Integer phases (11, 12, 13): Planned milestone work
- Decimal phases (11.1, 11.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>✅ v0.4.4 — CI-repair + modernize (Phases 1–5) — SHIPPED 2026-07-05</summary>

Restored a fully green CI pipeline on `main` by pinning the runtime dependency graph back to a
known-good, reproducible combination, then modernized the Python floor (3.10–3.13) and dev tooling
and installed durability guardrails so the drift cannot silently recur. Full phase detail, success
criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.4.4-ROADMAP.md`](milestones/v0.4.4-ROADMAP.md).

- [x] Phase 1: Pin Runtime Dependencies to Known-Good (2/2 plans) — completed 2026-07-04
- [x] Phase 2: Verify the Green Baseline (3/3 plans) — completed 2026-07-04
- [x] Phase 3: Modernize Python Floor (3.10–3.13) (2/2 plans) — completed 2026-07-04
- [x] Phase 4: Refresh Dev Tooling (4/4 plans) — completed 2026-07-04
- [x] Phase 5: Durability Guardrails (4/4 plans) — completed 2026-07-05

</details>

<details>
<summary>✅ v0.5.0 — forward-ecosystem (Phases 6–10 + 8.1) — SHIPPED 2026-07-11</summary>

Ported typsphinx forward from the v0.4.4 known-good pins to the current ecosystem — Sphinx 9.1,
docutils 0.22, typst 0.15, Python 3.12–3.13 — bumping the four bundled `@preview` packages in
lockstep to compile cleanly (empirically closing the `unknown variable: kai` break), modernizing the
soft-deprecated docutils/Sphinx API, fixing a long-latent admonition markup/code-mode render bug,
adding a `typst compile` smoke gate, keeping the full 3-OS × Python 3.12–3.13 CI matrix green, and
releasing v0.5.0 to PyPI. Latest-only, no compatibility range. Full phase detail, success criteria,
decisions, and tech-debt notes are preserved in
[`milestones/v0.5.0-ROADMAP.md`](milestones/v0.5.0-ROADMAP.md).

- [x] Phase 6: Raise Runtime Pins + Python Floor (1/1 plan) — completed 2026-07-09
- [x] Phase 7: Bump @preview Packages + typst 0.15 (kai fix) (1/1 plan) — completed 2026-07-11
- [x] Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22) (3/3 plans) — completed 2026-07-11
- [x] Phase 8.1: Admonition Rendering Fix (INSERTED) (4/4 plans) — completed 2026-07-11
- [x] Phase 9: Green CI Matrix + Smoke Test + Guardrails (2/2 plans) — completed 2026-07-11
- [x] Phase 10: Version-String Fix + v0.5.0 Release (2/2 plans) — completed 2026-07-11

</details>

### 🚧 v0.6.0 — real-world robustness (In Progress)

**Milestone Goal:** Compile a large real-world documentation set (Sphinx's own `doc/` tree) through
the `typstpdf` builder with no fatal Typst errors, and render the most-frequent previously-dropped
docutils/Sphinx nodes correctly. Driven by Issue #114: fix the two fatal figure/image bugs first
(a single fatal node aborts the whole PDF, so nothing downstream can be validated against a real
compile until this lands), then add high-frequency dropped-node support. Zero new runtime
dependencies — all work is in `typsphinx/translator.py`. The standing empirical bar is real
`typst.compile()` outcomes, not string assertions: every node-handler phase ships a real-compile
acceptance fixture (`sphinx-build → typst.compile() → pypdf`).

- [x] **Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net** - px→pt length helper + figure caption/`:target:` buffer-swap fix + graphviz/inheritance_diagram skip overrides; stands up the per-phase real-compile gate (blocking prerequisite for the whole milestone) (completed 2026-07-12)
- [ ] **Phase 12: High-Volume Independent Node Handlers** - versionmodified (×972), empty-URL/`refid` cross-refs (×596), autodoc `desc_*` sub-parts, and the trivial transition/glossary/tabular_col_spec/abbr nodes — all pattern-reuse, one new state var at most
- [ ] **Phase 13: Shared Dispatch-Point Changes (topic + line blocks)** - generalize the load-bearing `visit_title` for topic + render `line`/`line_block` with verbatim breaks, landed with admonition-title regression fixtures
- [ ] **Phase 14: Footnotes (doctree pre-pass)** - `footnote`/`footnote_reference` via Typst-native `footnote[...]` — the only architecturally-new item (document-order pre-pass), sequenced late to build confidence
- [ ] **Phase 15: Full-Corpus Validation** - real `sphinx-build -b typstpdf` of Sphinx's own `doc/` tree with no fatal error; catalogue residual warnings + measure empty-URL reduction

## Phase Details

### Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net

**Goal**: The two Issue #114 fatal bugs are fixed and the graphical out-of-scope nodes degrade
gracefully, so a real `typst.compile()` of a figure/image + graphviz fixture produces a PDF with no
`TypstError`. This unblocks real-compile validation of every downstream node handler (a single fatal
node aborts the entire PDF, so no later phase can be validated against a real compile until this
lands) and establishes the per-phase real-compile acceptance-gate pattern the rest of the milestone
extends.
**Depends on**: Nothing (first phase of milestone; builds on the v0.5.0 green baseline)
**Requirements**: FIG-01, FIG-02, DEG-01, DEG-02, GATE-01
**Success Criteria** (what must be TRUE):

  1. A `.. figure::`/image with `:width: 200px` — plus fixtures covering `50%`, `3em`, a bare unitless number, and `2in` — compiles to a PDF via real `typst.compile()` with no "unknown unit"/`TypstError`; `px`→`pt` converts numerically (1px = 0.75pt), valid units pass through, and unrecognized units are warned-and-dropped rather than emitted verbatim.
  2. A `.. figure::`/standalone image with a `:target:` link and a caption (including a caption containing `_`, `*`, `` ` ``, `[`, `]`) compiles to a PDF whose caption text is present exactly once, reaches the figure's `caption:` named argument via a buffer-swap, and never leaks as a stray juxtaposed `text(...)` call.
  3. A document containing a `.. graphviz::` and an `inheritance_diagram` node compiles to a PDF without aborting; each emits exactly one controlled `logger.warning` naming the node, and no raw DOT/diagram source leaks into the output.
  4. A `tests/test_pdf_render_gate.py`-style acceptance fixture (`sphinx-build → typst.compile() → pypdf` text-extraction with negative-control leak signatures) exercises the above and fails loudly on any `TypstCompilationError` — establishing the standing real-compile gate (GATE-01) that every later node-handler phase extends.

**Plans**: 3/3 plans complete
**Wave 1**

- [x] 11-01-PLAN.md — FIG-01 px→pt length converter + DEG-01/02 graphviz/inheritance_diagram graceful-degrade placeholder (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 11-02-PLAN.md — FIG-02 figure caption buffer-swap + internal `:target:` refid branch (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 11-03-PLAN.md — GATE-01 real-compile render gate: 3 fixtures + 3 test classes (wave 3)

### Phase 12: High-Volume Independent Node Handlers

**Goal**: The highest-frequency previously-dropped nodes — version directives, same-document
cross-references, autodoc signature sub-parts, and the trivial structural nodes — render correctly.
All reuse already-proven translator patterns with at most one new state variable each and are
independent of one another, so they group into one phase; each ships a real-compile fixture.
**Depends on**: Phase 11 (needs the Issue #114 fatal fixes landed so fixtures actually compile, and reuses the real-compile gate pattern it established)
**Requirements**: VER-01, XREF-01, DESC-01, DESC-02, DESC-03, DESC-04, BLK-01, BLK-04, BLK-05, BLK-06
**Success Criteria** (what must be TRUE):

  1. `.. versionadded`/`versionchanged`/`deprecated`/`versionremoved` render as an unboxed italic label + body matching Sphinx's own `versionlabels` wording (e.g. "Added in version 0.6:"), not as a gentle-clues callout box, and the containing document compiles to a PDF.
  2. A same-document internal cross-reference resolved via `refid` (a section anchor or `:term:` link) renders as a working PDF link instead of degrading to plain text; the plain-text fallback fires only when both `refuri` and `refid` are absent, and no path ever emits `link("", …)`.
  3. A typed signature with a return annotation (`-> int`), a multi-line signature, nested optional trailing parameters (`printf(fmt[, args])`), and an inline `:cpp:expr:` fragment all render correctly in a compiled PDF — return arrow present, line breaks between lines, brackets correctly nested, and the inline fragment without the standalone-declaration `strong()` wrapper.
  4. A `----` transition renders as a horizontal rule, a `.. glossary::` renders its underlying definition list, a `.. tabularcolumns::` hint is silently skipped with no leaked content, and an `:abbr:` renders inline as "term (expansion)" — all proven in fixtures that compile cleanly.
  5. Each handler group ships or extends a real-compile acceptance fixture (GATE-01 standing bar), never string-agreement asserts alone.

**Plans**: TBD

### Phase 13: Shared Dispatch-Point Changes (topic + line blocks)

**Goal**: `visit_title`'s dispatch — a load-bearing method every admonition and section heading
already depends on — is generalized so a `topic` title renders inline (not as a numbered heading),
and `line`/`line_block` content renders with verbatim line breaks. Because this edits a shared,
regression-heavy method rather than adding isolated handlers, it lands as one phase that also ships
regression fixtures for the existing admonition titles.
**Depends on**: Phase 11 (needs the real-compile gate); sequenced after Phase 12 so the `visit_title` generalization lands with several simpler wins behind it
**Requirements**: BLK-02, BLK-03
**Success Criteria** (what must be TRUE):

  1. A `.. topic:: Title` renders as a titled aside with its title as a bold inline label — not a numbered section heading — so the document's heading/TOC structure is unchanged, with its body typeset below; the document compiles to a PDF.
  2. `line`/`line_block` content (an address, epigraph, or poetry stanza) renders with every line break preserved via `linebreak()`, compiling to a PDF.
  3. Existing admonition titles (`.. note::`, `.. warning::` — the Phase 8.1 behavior) still render correctly after the `visit_title` generalization, proven by a regression fixture inside the same real-compile gate.
  4. A real-compile acceptance fixture (GATE-01 standing bar) covers topic + line_block together with the admonition-title regression.

**Plans**: TBD

### Phase 14: Footnotes (doctree pre-pass)

**Goal**: `footnote`/`footnote_reference` render via Typst-native `footnote[...]` using a new
document-order pre-pass that indexes footnote bodies by id — the only architecturally-new item in the
milestone. Notes appear inline at the reference site (not at the docutils definition location), and a
footnote cited more than once reuses its placed note by label rather than duplicating it. Sequenced
late so the new pattern is applied with the confidence of the earlier phases behind it; independent
of Phases 12–13.
**Depends on**: Phase 11 (needs the real-compile gate); no dependency on Phases 12–13
**Requirements**: FN-01
**Success Criteria** (what must be TRUE):

  1. A document with a footnote referenced once renders a single Typst-native `footnote[...]` at the reference site (marker + body) and compiles to a PDF whose body text is present exactly once — with no floating body left at the docutils definition location.
  2. A footnote referenced from two places renders a marker at both sites without duplicating the note body — the second citation reuses the placed note by label.
  3. A footnote body containing inline markup (`emph`/`literal`) and markup-special characters renders correctly (sourced via buffer-swap through the normal visitor chain, never `astext()`), compiling cleanly.
  4. A real-compile acceptance fixture (GATE-01 standing bar) exercises the single-reference, double-reference, and footnote-inside-a-list-item cases.

**Plans**: TBD

### Phase 15: Full-Corpus Validation

**Goal**: Sphinx's own `doc/` tree compiles end-to-end through the `typstpdf` builder with no fatal
`TypstCompilationError` — the milestone's stated acceptance bar. The residual `unknown_visit`
warnings are catalogued by frequency (the next milestone's backlog input) and the empty-URL
warning-count reduction from the XREF-01 fix is measured before/after against the real corpus.
**Depends on**: Phases 11–14 (all node handlers must be in place)
**Requirements**: GATE-02
**Success Criteria** (what must be TRUE):

  1. A real `sphinx-build -b typstpdf` of Sphinx's own `doc/` tree completes with no fatal `TypstCompilationError` — the empirical milestone gate.
  2. The remaining `unknown_visit` warnings from that build are catalogued by frequency and recorded as the next milestone's backlog input (the gate is "no fatal errors," not "zero warnings").
  3. The empty-URL cross-reference warning count is measured before and after the XREF-01 fix against the same corpus, quantifying the reduction rather than assuming it.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 11 → 12 → 13 → 14 → 15

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Pin Runtime Dependencies to Known-Good | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 2. Verify the Green Baseline | v0.4.4 | 3/3 | Complete | 2026-07-04 |
| 3. Modernize Python Floor (3.10–3.13) | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 4. Refresh Dev Tooling | v0.4.4 | 4/4 | Complete | 2026-07-04 |
| 5. Durability Guardrails | v0.4.4 | 4/4 | Complete | 2026-07-05 |
| 6. Raise Runtime Pins + Python Floor | v0.5.0 | 1/1 | Complete | 2026-07-09 |
| 7. Bump @preview Packages + typst 0.15 (kai fix) | v0.5.0 | 1/1 | Complete | 2026-07-11 |
| 8. API & Test Compatibility (Sphinx 9 / docutils 0.22) | v0.5.0 | 3/3 | Complete | 2026-07-11 |
| 8.1 Admonition Rendering Fix (INSERTED) | v0.5.0 | 4/4 | Complete | 2026-07-11 |
| 9. Green CI Matrix + Smoke Test + Guardrails | v0.5.0 | 2/2 | Complete | 2026-07-11 |
| 10. Version-String Fix + v0.5.0 Release | v0.5.0 | 2/2 | Complete | 2026-07-11 |
| 11. Issue #114 Fatal Fixes + Graceful-Degrade Net | v0.6.0 | 3/3 | Complete   | 2026-07-12 |
| 12. High-Volume Independent Node Handlers | v0.6.0 | 0/TBD | Not started | - |
| 13. Shared Dispatch-Point Changes (topic + line blocks) | v0.6.0 | 0/TBD | Not started | - |
| 14. Footnotes (doctree pre-pass) | v0.6.0 | 0/TBD | Not started | - |
| 15. Full-Corpus Validation | v0.6.0 | 0/TBD | Not started | - |

---
*Roadmap created: 2026-07-04 · Reorganized: 2026-07-05 at v0.4.4 milestone close · v0.5.0 phases (6–10) added: 2026-07-09 · Reorganized: 2026-07-11 at v0.5.0 milestone close · v0.6.0 phases (11–15) added: 2026-07-11*
