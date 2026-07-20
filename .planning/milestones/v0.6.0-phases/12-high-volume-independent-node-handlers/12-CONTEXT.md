# Phase 12: High-Volume Independent Node Handlers - Context

**Gathered:** 2026-07-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Add translator support for the highest-frequency previously-dropped docutils/Sphinx nodes,
entirely within `typsphinx/translator.py` (+ fixture dirs + the existing real-compile gate).
Each handler reuses an already-proven translator pattern, adds at most one new state variable,
and is independent of the others. Concretely:

- **VER-01** — `versionadded` / `versionchanged` / `deprecated` / `versionremoved`
  (`versionmodified` node, ×972 — the single most-frequent dropped node) render as an
  unboxed italic label + body, **not** a gentle-clues callout box.
- **XREF-01** — same-document internal cross-reference via `refid` (section anchors, `:term:`,
  `:ref:`) renders as a working PDF link instead of degrading to plain text; plain-text fallback
  fires **only** when both `refuri` and `refid` are absent; no path emits `link("", …)`.
- **DESC-01…04** — autodoc signature sub-parts: `desc_returns` (`-> int`), `desc_signature_line`
  (multi-line), `desc_optional` (`printf(fmt[, args])`, incl. nesting), `desc_inline` (`:cpp:expr:`,
  without the standalone-declaration `strong()` wrapper).
- **BLK-01 / BLK-04 / BLK-05 / BLK-06** — the trivial structural nodes: `transition` → horizontal
  rule; `.. glossary::` → its underlying definition list (pass-through); `tabular_col_spec`
  (`.. tabularcolumns::`) → skipped safely, no leak; `:abbr:` → inline `term (expansion)`.

This is the **second** phase of milestone v0.6.0, depending on Phase 11 (needs the Issue #114 fatal
fixes landed so fixtures compile, and reuses the GATE-01 real-compile acceptance pattern). Zero new
runtime dependencies; the 3-way `@preview` version-sync surface (writer.py / template_engine.py /
templates/base.typ) is untouched. Scope is HOW to implement this fixed node set — new node
*capabilities* beyond it belong to Phases 13–15. Empirical bar is a real `typst.compile()` outcome
per handler group, never string-agreement asserts alone.

</domain>

<decisions>
## Implementation Decisions

**Discussion mode:** user selected "全部おまかせ" — all gray areas resolved at Claude's
recommended default. Each decision below is the locked default; nothing is left open for re-asking.

### version directives (VER-01)
- **D-01: Label wording sourced from Sphinx, not hardcoded.** Derive the label text from Sphinx's
  own `versionlabels` map (the wording behind "Added in version 0.6:", "Changed in version 0.6:",
  "Deprecated since 0.6:", "Removed in version 0.6:") rather than hardcoding an English map in
  `translator.py`. This keeps wording in lockstep with the installed Sphinx and inherits its
  localization — and directly honors REQ VER-01's "matching Sphinx's own HTML/LaTeX wording **via
  the `versionlabels` map**". The researcher pins the exact import path (Sphinx keeps these in
  `sphinx.locale` / the changeset domain); if the symbol is not importable on the supported Sphinx
  floor, fall back to a small internal map that reproduces the same wording, documented as the
  fallback.
- **D-02: Sphinx-HTML-style inline layout.** Render as an emphasized inline label immediately
  followed by the body in the same block — e.g. `emph[Added in version 0.6:] body…` — matching
  Sphinx's HTML rendering, **not** a label on its own separate line. Unboxed (no gentle-clues
  callout, no border) per the requirement. `versionadded`/`versionremoved` carry only the label;
  `versionchanged`/`deprecated` carry label + explanatory body.

### internal cross-references (XREF-01)
- **D-03: Confirm-and-cover, not rebuild.** The `refuri`-empty + `refid`-present →
  `link(<refid>, …)` branch **already exists** from Phase 11 (translator.py:2119, FIG-02/D-03) and
  its condition is already general (any node, not just figure targets). Phase 12's XREF-01 work is
  therefore primarily: (a) verify that branch already resolves section anchors, `:term:`, and
  `:ref:` cross-references; (b) add the real-compile fixtures; (c) close any node-type-specific edge
  case found. Do not add parallel machinery.
- **D-04: Safe-side against dangling labels.** `link(<label>)` to an anchor that was never emitted
  makes Typst abort — which violates the milestone's core "no fatal `TypstCompilationError`" bar.
  The contract: **never** emit `link("", …)`; the plain-text fallback fires only when both `refuri`
  and `refid` are absent (REQ XREF-01). Section anchors are already emitted (translator.py:272,
  :1061), and Sphinx resolves/warns unresolvable xrefs to plain text *before* the doctree reaches
  the translator, so a surviving `refid` normally resolves. The GATE fixture MUST exercise a
  section-anchor ref **and** a `:term:` ref that resolve to emitted anchors, proving working PDF
  links with no fatal. If a genuinely-dangling `refid` is ever observed against the real corpus
  (Phase 15), degrade it to plain text + one `logger.warning` rather than emit a label-abort — but
  do not add speculative degradation code now beyond what the fixtures prove necessary.

### autodoc signature sub-parts (DESC-01…04)
- **D-05: Faithful to the SC, minimal machinery.** Behaviour is fixed by ROADMAP SC#3 — render the
  return arrow (`-> int`), line breaks between `desc_signature_line`s, correctly nested
  `desc_optional` brackets (`printf(fmt[, args])`, multi-level). These reuse the existing `desc_*`
  visitor family (translator.py:2701+).
- **D-06: `desc_inline` strong()-suppression via context, not a global flag.** The standalone
  `strong()` wrapper that top-level declaration signatures get must be suppressed for inline
  fragments (`:cpp:expr:`). Gate the wrapper on "is this a standalone declaration" using the
  existing desc nesting / parent-node signal rather than introducing a broad new mode. Exact
  predicate is the planner/executor's call.

### trivial structural nodes (BLK-01 / BLK-04 / BLK-05 / BLK-06)
- **D-07:** Behaviour fully fixed by ROADMAP SC#4 / REQUIREMENTS — captured here so the planner does
  not re-derive:
  - `transition` → `line(length: 100%)` horizontal rule.
  - `.. glossary::` → pass through to its underlying `definition_list` (thin wrapper; the existing
    `visit_definition_list`, translator.py:1070, does the real work).
  - `tabular_col_spec` (`.. tabularcolumns::`) → `raise nodes.SkipNode`, no content leaked (it is a
    LaTeX-only layout hint with no Typst equivalent).
  - `:abbr:` → inline `term (expansion)`.
- **D-08: abbr expands on every occurrence.** Emit `term (expansion)` at each occurrence, stateless
  — a PDF has no `<abbr title>` hover equivalent, so the reader needs the expansion inline wherever
  it appears. No first-occurrence-only state variable.

### Claude's Discretion
- Exact `emph`/label punctuation and spacing for the version label (must reproduce Sphinx's wording
  and read as unboxed italic).
- The precise import path / fallback shape for the `versionlabels` wording (D-01).
- The exact predicate distinguishing a standalone declaration from an inline `desc_inline`
  fragment (D-06).
- Fixture document contents beyond the explicit success-criteria cases.
- Exact `logger.warning` wording for any dangling-refid degradation, should it prove necessary.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — VER-01, XREF-01, DESC-01…04, BLK-01/04/05/06 definitions
  (and the per-phase mapping line at the bottom).
- `.planning/ROADMAP.md` §"Phase 12" — the five Success Criteria (version label wording;
  refid link vs plain-text fallback + never `link("", …)`; signature return/multiline/optional/
  inline; transition/glossary/tabularcolumns/abbr; the GATE-01 standing bar).

### Prior-phase context (patterns to reuse — MUST read)
- `.planning/phases/11-issue-114-fatal-fixes-graceful-degrade-net/11-CONTEXT.md` — establishes the
  buffer-swap precedent, the `_link_has_content` juxtaposition guard, the `SkipNode` primitive, the
  refid link branch this phase generalizes, and the GATE-01 real-compile gate this phase extends.

### Research (implementation-grounding, from milestone v0.6.0)
- `.planning/research/SUMMARY.md` — zero-new-deps thesis; pitfall #9 (string-tests-prove-nothing)
  underpins the real-compile requirement; node-frequency ranking (versionmodified ×972,
  empty-URL/refid ×596) justifies this phase's ordering.
- `.planning/research/PITFALLS.md`, `.planning/research/ARCHITECTURE.md` — buffer-swap /
  `_has_content` flag / `SkipNode` patterns reused here.

### Code touchpoints (current state)
- `typsphinx/translator.py:2072`–`2198` `visit_reference` / `depart_reference` — the existing
  refid/refuri branch (XREF-01 core already present at :2119; empty-URL guard at :2138).
- `typsphinx/translator.py:2701`–`2975` the `desc_*` visitor family — DESC-01…04 extend this
  (no `desc_returns` / `desc_optional` / `desc_signature_line` / `desc_inline` handlers exist yet).
- `typsphinx/translator.py:1070` `visit_definition_list` / `:1127` `visit_term` — glossary
  pass-through target (BLK-04).
- `typsphinx/translator.py:2200` `unknown_visit` / `:2213` `unknown_departure` — where
  `versionmodified`, `transition`, `tabular_col_spec`, `abbreviation` currently fall through and get
  dropped; new explicit `visit_*` overrides needed.
- `tests/test_pdf_render_gate.py` — the standing real-compile gate (GATE-01) to extend with
  per-handler-group fixtures.
- Sphinx `versionlabels` map (D-01) — researcher to pin the exact import location on the supported
  Sphinx floor.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase-11 refid link branch** (`visit_reference`, translator.py:2119) — already emits
  `link(<refid>, …)` for empty-refuri + refid; condition is general. XREF-01 mostly verifies +
  fixtures this rather than adding code.
- **`_link_has_content` juxtaposition guard** (translator.py:88, :527, :542) — the established
  pattern preventing bare adjacent code-mode expressions; relevant if version label + body or
  abbr term + expansion ever need concatenation discipline.
- **`desc_*` visitor family** (translator.py:2701+) — DESC-01…04 plug into the existing signature
  rendering rather than building a parallel path.
- **`visit_definition_list` / `visit_term`** (translator.py:1070, :1127) — glossary (BLK-04) is a
  thin wrapper delegating to these.
- **`raise nodes.SkipNode`** — the clean primitive for `tabular_col_spec` (BLK-05); used throughout
  for comment/raw/target.
- **`tests/test_pdf_render_gate.py`** — GATE-01 real-compile scaffold (typst-py + pypdf,
  `slow`-marked, negative-control leak tokens); extend, don't reinvent.

### Established Patterns
- **Code-mode emission** — the translator emits Typst function calls without `#` prefix; adjacent
  expressions must be `+`/newline separated or wrapped in a named arg. Version label + body and
  abbr term + expansion must respect this juxtaposition rule.
- **Section-anchor emission** — `<label>` anchors are already emitted for sections/targets
  (translator.py:272, :1061, :1647), which is what makes XREF-01's `link(<refid>)` resolve.
- **`unknown_visit` = silent drop** — nodes without an explicit handler are currently dropped; the
  ×972 versionmodified loss is exactly this. Adding a handler is the fix.

### Integration Points
- All production changes land in `typsphinx/translator.py`, plus new fixture project dirs and
  `tests/test_pdf_render_gate.py`. No edits to `writer.py`, `builder.py`, `template_engine.py`,
  `templates/base.typ`, or the `@preview` version-sync surface.

</code_context>

<specifics>
## Specific Ideas

- Version label must reproduce Sphinx's exact wording (e.g. "Added in version 0.6:") sourced from
  the `versionlabels` map, rendered unboxed and italic, inline before the body — never a
  gentle-clues box.
- XREF-01 fixture must include a resolving section-anchor ref **and** a `:term:` ref, and assert the
  compiled PDF has a working link with no fatal and no `link("", …)` leak.
- DESC fixture must cover: a `-> int` return, a multi-line signature, `printf(fmt[, args])` nested
  optionals, and an inline `:cpp:expr:` fragment (no standalone `strong()`).
- Trivial-node fixture must cover: a `----` transition, a `.. glossary::`, a `.. tabularcolumns::`
  (assert no leaked content), and an `:abbr:` (assert `term (expansion)`).

</specifics>

<deferred>
## Deferred Ideas

- **BLK-02 / BLK-03** (topic titles, `line`/`line_block`) — Phase 13 (shared `visit_title`
  dispatch), not here.
- **FN-01** (footnotes, doctree pre-pass) — Phase 14, not here.
- **GATE-02** (full-corpus real `sphinx-build` of Sphinx's own `doc/` tree) — Phase 15; that is
  where a genuinely-dangling `refid`, if any, would surface and where the empty-URL reduction is
  measured.
- **Real graphviz / inheritance_diagram rendering** — out of scope for the whole milestone
  (placeholder-only, settled in Phase 11).

None raised outside phase scope during discussion.

</deferred>

---

*Phase: 12-High-Volume Independent Node Handlers*
*Context gathered: 2026-07-12*
