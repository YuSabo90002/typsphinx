# Phase 12: High-Volume Independent Node Handlers - Research

**Researched:** 2026-07-12
**Domain:** docutils/Sphinx-node-to-Typst-markup translator handlers (single file: `typsphinx/translator.py`, 2999 lines post-Phase-11)
**Confidence:** HIGH — every node-shape claim below was verified in this session either by (a) direct `Read` of the current repository source (line numbers re-confirmed, not carried forward from CONTEXT.md), (b) a live `sphinx-build`/`env.get_doctree()` doctree dump against Sphinx 9.1.0 (the project's installed, pinned version) for every node type this phase touches, or (c) a real `typst.compile()` round-trip via `typst-py` proving specific candidate fixes both **fail** (documenting a real, previously-unknown bug) and **succeed** (proving the recommended fix). This is unusually deep verification for a research pass; treat findings marked `[VERIFIED: live doctree dump]` or `[VERIFIED: typst.compile()]` as ground truth, not inference.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Discussion mode:** user selected "全部おまかせ" — all gray areas resolved at Claude's
recommended default. Each decision below is the locked default; nothing is left open for re-asking.

#### version directives (VER-01)
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

#### internal cross-references (XREF-01)
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

#### autodoc signature sub-parts (DESC-01…04)
- **D-05: Faithful to the SC, minimal machinery.** Behaviour is fixed by ROADMAP SC#3 — render the
  return arrow (`-> int`), line breaks between `desc_signature_line`s, correctly nested
  `desc_optional` brackets (`printf(fmt[, args])`, multi-level). These reuse the existing `desc_*`
  visitor family (translator.py:2701+).
- **D-06: `desc_inline` strong()-suppression via context, not a global flag.** The standalone
  `strong()` wrapper that top-level declaration signatures get must be suppressed for inline
  fragments (`:cpp:expr:`). Gate the wrapper on "is this a standalone declaration" using the
  existing desc nesting / parent-node signal rather than introducing a broad new mode. Exact
  predicate is the planner/executor's call.

#### trivial structural nodes (BLK-01 / BLK-04 / BLK-05 / BLK-06)
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

### Deferred Ideas (OUT OF SCOPE)
- **BLK-02 / BLK-03** (topic titles, `line`/`line_block`) — Phase 13 (shared `visit_title`
  dispatch), not here.
- **FN-01** (footnotes, doctree pre-pass) — Phase 14, not here.
- **GATE-02** (full-corpus real `sphinx-build` of Sphinx's own `doc/` tree) — Phase 15; that is
  where a genuinely-dangling `refid`, if any, would surface and where the empty-URL reduction is
  measured.
- **Real graphviz / inheritance_diagram rendering** — out of scope for the whole milestone
  (placeholder-only, settled in Phase 11).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VER-01 | `versionadded`/`versionchanged`/`deprecated`/`versionremoved` render as unboxed italic label + body, matching Sphinx's `versionlabels` wording | Part 1 — **major finding: no import needed**; Sphinx already bakes the exact label text into the doctree as a classed `nodes.inline` at directive-parse time |
| XREF-01 | Same-document `refid` cross-reference (section anchor, `:term:`) renders as a working link; plain-text fallback only when both `refuri`/`refid` absent; never `link("", …)` | Part 2 — refid branch (translator.py:2119) confirmed working for `:ref:`/`:term:` via live compile, **but** a real, previously-undiscovered fatal bug found: glossary `:term:` targets have no anchor emitted, so any `:term:` xref currently aborts the whole compile |
| DESC-01 | `desc_returns` (`-> int`) renders in the signature | Part 3.1 — minimal literal-prefix fix, zero new state |
| DESC-02 | `desc_signature_line` renders with line breaks between lines | Part 3.2 — **major finding: source-level `\n` does NOT produce a visible break**; `linebreak()` (Typst stdlib, first use in this codebase) is required, confirmed via `typst.compile()` + `pypdf` extraction |
| DESC-03 | `desc_optional` (`printf(fmt[, args])`, incl. nesting) renders bracket-wrapped | Part 3.3 — confirmed via live doctree dump that nested optionals are literal sibling `desc_optional` nodes; recursive fix needs zero extra state |
| DESC-04 | `desc_inline` (`:cpp:expr:`) renders without the standalone `strong()` wrapper | Part 3.4 — **D-06 resolved**: the predicate is node-*type* dispatch, not parent inspection — `desc_signature` and `desc_inline` are distinct Sphinx node classes, so a plain pass-through `visit_desc_inline` is correct and sufficient |
| BLK-01 | `transition` renders as `line(length: 100%)` | Part 4.1 — genuine content gap (self-closing node, nothing renders today) |
| BLK-04 | `.. glossary::` renders its underlying definition list | Part 4.2 — content already flows through today; **but see XREF-01's term-anchor bug**, which BLK-04's fix must also close |
| BLK-05 | `tabular_col_spec` skipped safely, no leak | Part 4.3 — trivial `SkipNode`, already effectively a no-op today; explicit handler needed only to silence the warning |
| BLK-06 | `:abbr:` renders as `term (expansion)` | Part 4.4 — genuine content gap (`explanation` attribute is currently completely dropped); dummy-Text-node delegation reuses all existing escaping |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- All work is scoped to `typsphinx/translator.py` per CONTEXT.md and confirmed here — CLAUDE.md
  describes this file as "the file you will most often edit... ~140 `visit_*`/`depart_*` methods";
  this phase adds roughly a dozen more, consistent with the file's own convention.
- `ruff` ignores `N802` for docutils' PascalCase visitor method names — new handlers
  (`visit_versionmodified`, `visit_desc_returns`, `visit_transition`, etc.) need no additional
  suppression.
- Black line length 88; `E501` ignored (black owns wrapping).
- `mypy typsphinx/` runs in CI — every new method needs full type annotations
  (`def visit_transition(self, node: nodes.transition) -> None:`), matching the file's existing
  style throughout.
- `pyproject.toml` pins `requires-python = ">=3.12"` (the actual floor; CLAUDE.md's "py310–py313"
  text is stale, already flagged by 11-RESEARCH.md — no new action needed here, just don't
  reintroduce `Optional[]`/`Dict`/`List` typing-module imports for new code).
- No project skills directory (`.claude/skills/`, `.agents/skills/`) exists for this repo beyond the
  global GSD skill set.
- `tests/test_pdf_render_gate.py` is the standing GATE-01 acceptance harness (`sphinx-build -b typst
  → typst.compile() → pypdf`), with `LEAK_SIGNATURES = ("par({", 'text("', 'raw("')` as the
  negative-control tuple and `@pytest.mark.slow` + `@pytest.mark.skipif(not (TYPST_AVAILABLE and
  PYPDF_AVAILABLE))` as the class-level decorators for every fixture class added since Phase 11.
  New Phase 12 fixture classes should follow this exact shape (confirmed unchanged from
  11-RESEARCH.md's citation).

## Summary

Phase 12 is deceptively simple on paper ("reuse proven patterns, at most one new state variable
each") but this session's direct doctree dumps and `typst.compile()` experiments surfaced two
**genuine, previously-undocumented bugs** that change the phase's risk profile, plus one **major
simplification** of the locked D-01 decision:

1. **VER-01 needs no `versionlabels` import at all.** Sphinx's `VersionChange` directive
   (`sphinx/domains/changeset.py`, confirmed by reading the installed Sphinx 9.1.0 source) already
   computes the exact label wording via its own internal `versionlabels` dict **at parse time**,
   before the doctree ever reaches the translator, and bakes it in as a `nodes.inline(classes=
   ["versionmodified", "added"|"changed"|"deprecated"|"removed"])` prepended to the node's first
   child paragraph. A live doctree dump (`sphinx-build -b typst` on a `.. versionadded:: 0.6`
   fixture) confirms this exactly: `<inline classes="versionmodified added">Added in version 0.6:
   </inline>Some added text here.` The translator's job is not "reconstruct the label from
   `sphinx.locale`/`sphinx.domains.changeset.versionlabels`" — it is simply "detect the
   already-classed inline and render it in italic," which is a 6-line `visit_inline`/`depart_inline`
   extension delegating to the existing `visit_emphasis`/`depart_emphasis` dummy-node pattern. This
   is *more* robust than an import-based fix (no coupling to Sphinx internals, inherits
   localization automatically since Sphinx's own `_()` call already ran) and fully satisfies D-01's
   underlying intent ("sourced from Sphinx, not hardcoded").

2. **A real, currently-live fatal bug: `:term:` cross-references to glossary entries abort the
   whole PDF compile.** `visit_term`/`depart_term` (translator.py:1127–1162) buffers the term's
   rendered text but never emits a Typst label anchor for the term's docutils `ids` — so a `:term:`
   reference correctly resolves to `link(<term-Widget>, …)` (XREF-01's refid branch works exactly
   as D-03 predicted), but `<term-Widget>` is never defined anywhere. This was proven by extracting
   the actual `.typ` output from a live `sphinx-build` and feeding it directly to `typst.compile()`
   in this session: `TypstError: label <term-Widget> does not exist in the document`. This is not
   speculative — it is the **exact** `:term:` GATE fixture scenario CONTEXT.md's D-04 mandates
   ("The GATE fixture MUST exercise a section-anchor ref **and** a `:term:` ref that resolve to
   emitted anchors"). Without fixing `visit_term`/`depart_term` to bracket-wrap the buffered term
   content as `[#{...} <term-id>]` (the same markup-postfix label-attachment pattern Phase 11
   already established for `visit_title`/`visit_figure`), the phase's own required success
   criterion is unreachable. This is a **required code change**, not just "confirm-and-cover"
   verification — see Part 2.2.

3. **DESC-02 needs Typst's `linebreak()` function, not a source-level newline.** This session
   compiled a minimal `.typ` snippet with two `text(...)` statements joined only by a bare source
   `\n` and confirmed via `pypdf` extraction that they render on the **same visual line** with no
   space — source newlines between code-mode statements are purely cosmetic and produce zero visual
   effect. A second snippet using an explicit `linebreak()` statement between the two `text(...)`
   calls correctly produced two separate lines in the extracted PDF text. `linebreak()` is Typst
   stdlib (zero new dependency) but is a first-time use in this codebase.

4. **`:ref:` cross-references already work end-to-end**, confirmed via a live `sphinx-build` +
   inspection of the emitted `.typ` (`link(<section-b>, text("Section B"))`), validating D-03's
   confirm-and-cover thesis for the section-anchor half of XREF-01 without any code change.

5. **DESC-01/03/04 are all low-risk, minimal-diff fixes** confirmed against live doctree dumps
   (`desc_returns`, `desc_optional` incl. genuine multi-level nesting via `printf(fmt[, args[,
   more]])`, `desc_inline` via `:cpp:expr:`) — see Part 3.

**Primary recommendation:** Implement all ten node handlers as small, independent additions to
`typsphinx/translator.py`, but budget explicit attention (and its own real-compile fixture) for the
`visit_term` label-anchor fix — treat it as a required companion to XREF-01/BLK-04, not an optional
polish item, since without it the phase's mandated `:term:` GATE fixture cannot pass.

## Architectural Responsibility Map

Single-process CLI/library pipeline (Sphinx builder extension) — "tiers" are pipeline stages, not
client/server/DB layers, matching 11-RESEARCH.md's framing.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Version-label italicization (VER-01) | Translator (`visit_inline` classed-dispatch) | Sphinx `changeset` domain (upstream, already computed the wording) | The label *text* is Sphinx's responsibility (already resolved pre-translator); the translator only owns *styling* |
| `refid` link resolution (XREF-01) | Translator (`visit_reference`, already exists) | Docutils/Sphinx reference-resolution transforms (upstream) | Resolution happens before the translator sees the tree; translator only branches on the already-resolved attribute |
| Glossary-term anchor emission (XREF-01/BLK-04 companion fix) | Translator (`visit_term`/`depart_term`) | — | Purely a translator-owned gap — docutils assigns the id, but nothing in the translator ever turns it into a Typst label |
| Autodoc signature sub-parts (DESC-01…04) | Translator (`desc_*` visitor family, already exists) | Sphinx `py`/`cpp`/`c` domains (upstream, already produce the node shapes) | Node *shape* is domain-owned; the translator only owns the Typst-syntax mapping |
| Trivial structural nodes (BLK-01/04/05/06) | Translator | — | Pure syntax mapping, no cross-tier concerns |
| Real-compile acceptance gate | Test/CI harness (`tests/test_pdf_render_gate.py`) | CI `cov` job | Downstream verification tier, not part of the translator |

## Standard Stack

### Core

No new dependencies — every fix in this phase uses functions already imported/available or Typst
stdlib functions requiring zero new `import` statements in `.typ` output.

| Library | Version (pinned) | Purpose | Why Standard |
|---------|------|---------|--------------|
| `typst` (typst-py) | `>=0.15.0,<0.16` [VERIFIED: pyproject.toml] | Real PDF compile in the render gate; `linebreak()`, `emph()`, `line()`, `label()` are all Typst 0.15 stdlib — confirmed by direct `typst.compile()` execution in this session (not just docs lookup) | Already the project's compile engine |
| `sphinx` | `>=9.1,<10` [VERIFIED: pyproject.toml]; installed `.venv` has exactly `9.1.0` [VERIFIED: `python -c "import sphinx; print(sphinx.__version__)"` in this session] | Source of `versionmodified`/`desc_*`/`glossary`/`transition`/`tabular_col_spec`/`abbreviation` node shapes | Already the project's parser/domain layer |
| `docutils` | `>=0.21,<0.23` [VERIFIED: pyproject.toml] | `transition`, `abbreviation`, `definition_list`, `tabular_col_spec` are all core docutils node types | Already the project's parser |
| `pypdf` | `>=6.14,<7` [VERIFIED: pyproject.toml] | Text-extraction half of the render gate | Already used by GATE-01 |

### Supporting

None needed. `nodes.Text`, `nodes.emphasis`, `nodes.strong` (already imported via `docutils.nodes`)
are the only "new" constructor usages, and they are the exact same dummy-node-delegation idiom
already used at four other call sites in this file (`visit_title_reference`, `visit_literal_strong`,
`visit_literal_emphasis`, `visit_desc_signature`/`visit_rubric`).

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Detecting `"versionmodified" in node.get("classes", [])` inside `visit_inline` | Importing `sphinx.domains.changeset.versionlabels` and reconstructing the label text from `node["type"]`/`node["version"]` | **Rejected.** The import path exists (`sphinx.domains.changeset.versionlabels` — NOT `sphinx.locale.versionlabels`, which does not exist in Sphinx 9.1, confirmed by `ImportError` in this session) but reconstructing the text duplicates work Sphinx already did, risks drifting from Sphinx's exact wording/localization/`%` formatting, and requires the translator to depend on an internal domain module (`sphinx.domains.changeset` is not part of Sphinx's public extension API surface). The classed-inline approach needs zero coupling and is provably correct against the actual doctree shape. |
| Source-level `\n` between `desc_signature_line` siblings | `linebreak()` | **Rejected `\n`-only** — proven via direct `typst.compile()` + `pypdf` extraction in this session to produce zero visual line break. `linebreak()` is the only mechanism that visibly separates the lines. |
| `[#{...} <label>]` bracket-wrap for glossary term anchors | A code-mode-only `label("term-id")` statement appended via `+` to the term content | **Rejected the `+` form** — proven via direct `typst.compile()` in this session to raise `cannot add content and label` (a `label` value cannot be concatenated with `content` via `+` in Typst's type system). The bracket-wrap form (`[#{term_content} <term-id>]`), which is exactly the pattern Phase 11 already established for `visit_title`/`visit_figure`, was proven to compile correctly and to resolve the `:term:` link. |

**Installation:** None required — zero new packages.

**Version verification:** `sphinx` confirmed `9.1.0` installed [VERIFIED: `python -c
"import sphinx; print(sphinx.__version__)"` against `.venv`, this session]; `typst`/`pypdf` versions
confirmed unchanged from 11-RESEARCH.md's citation (`pyproject.toml`, this session, unchanged since
Phase 11).

## Package Legitimacy Audit

**Not applicable this phase.** Zero new external packages in any ecosystem — every fix uses either
already-imported `docutils.nodes` constructors or Typst stdlib functions (`emph`, `line`, `label`,
`linebreak`, `text`) that require no new `@preview` import. No legitimacy check is required.

**Packages removed due to [SLOP] verdict:** none (N/A — no packages proposed)
**Packages flagged as suspicious [SUS]:** none (N/A — no packages proposed)

## Architecture Patterns

### System Architecture Diagram

```
docutree (post-Sphinx-domain-processing, pre-translator)
        │
        ├─ versionmodified ──▶ paragraph ──▶ inline(classes=["versionmodified", <kind>]) + Text
        │        (label text ALREADY baked in by sphinx.domains.changeset.VersionChange.run(),
        │         confirmed via live doctree dump — translator only needs to detect + italicize)
        │
        ├─ reference(refuri="", refid="term-Widget") ──▶ Text("Widget")
        │        (pending_xref already resolved to `reference` by Sphinx's post-transform
        │         BEFORE the translator runs — visit_pending_xref is dead code for anything
        │         Sphinx itself resolves)
        │
        ├─ glossary ──▶ definition_list ──▶ definition_list_item ──▶ term(ids=["term-Widget"])
        │                                                          ──▶ definition ──▶ paragraph
        │        (definition_list ALREADY renders via existing visit_definition_list, but
        │         visit_term never emits a label anchor for its own ids -- FATAL GAP, see Part 2.2)
        │
        ├─ desc_signature ──▶ desc_name, desc_parameterlist(...desc_parameter, desc_optional...),
        │                     desc_returns
        │        (desc_signature already delegates to visit_strong; desc_returns/desc_optional
        │         need small additive handlers plugging into the SAME +-join / list-item-newline
        │         conventions already used by desc_parameter/desc_name)
        │
        ├─ desc_signature (is_multiline) ──▶ desc_signature_line × N
        │        (each line's content already renders via existing desc_sig_* handlers; the
        │         gap is purely the missing linebreak() between lines)
        │
        ├─ desc_inline (separate node CLASS from desc_signature -- Sphinx itself already
        │               distinguishes "standalone declaration" vs "inline fragment" at the
        │               node-type level; D-06's predicate is simply "which visit_* method fires")
        │
        ├─ transition (self-closing, no children -- currently renders NOTHING)
        ├─ tabular_col_spec (self-closing, no children -- currently renders nothing, just warns)
        └─ abbreviation(explanation="...") ──▶ Text("API")
                 (the Text child already renders; the explanation ATTRIBUTE is completely
                  dropped today -- genuine content gap)
        │
        ▼
┌───────────────────────────────────────────────────────────────────────┐
│ TypstTranslator (typsphinx/translator.py) -- ALL ten handlers land here │
│                                                                          │
│  visit_inline: classed-dispatch to visit_emphasis for versionmodified   │
│  visit_versionmodified/depart_versionmodified: transparent pass-through │
│  visit_term/depart_term: [FIX] bracket-wrap buffered content w/ <label> │
│  visit_desc_returns: literal " -> " prefix, reuses existing separators  │
│  visit_desc_signature_line: linebreak() before all-but-first line       │
│  visit_desc_optional/depart_desc_optional: literal "[" / "]" wrap,      │
│      recursive-safe (nested desc_optional just adds another pair)       │
│  visit_desc_inline/depart_desc_inline: transparent pass-through         │
│      (NOT delegated to visit_strong -- that's desc_signature's job)     │
│  visit_transition: emit line(length: 100%), SkipNode (no children)      │
│  visit_glossary/depart_glossary: transparent pass-through               │
│  visit_tabular_col_spec: SkipNode                                       │
│  visit_abbreviation/depart_abbreviation: pass-through term + dummy      │
│      Text(" (expansion)") delegation in depart (reuses visit_Text's     │
│      escaping regime automatically)                                     │
└───────────────────────────────────────────────────────────────────────┘
        │
        ▼
   body string ──▶ TemplateEngine ──▶ .typ file
        │
        ▼
┌───────────────────────────────────────────────────────────────────────┐
│ GATE-01 extension: tests/test_pdf_render_gate.py                        │
│   sphinx-build -b typst → typst.compile() → pypdf text-extraction       │
│   New fixture classes per handler group (mirrors Phase 11's 3-fixture   │
│   pattern), asserting: italic label present, term-ref link resolves     │
│   with no fatal, arrow/bracket/linebreak content present, no            │
│   LEAK_SIGNATURES, no raw DOT/tabularcolumns spec leaked                │
└───────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

No new directories or modules — additions land in existing locations, mirroring Phase 11's shape:

```
typsphinx/
└── translator.py            # + ~10 new visit_*/depart_* method pairs, +1 new state var
                              #   (_is_first_desc_signature_line), + fix to existing
                              #   visit_term/depart_term (label-anchor emission)
tests/
├── test_pdf_render_gate.py  # + new test classes (same file, same LEAK_SIGNATURES/skipif
                              #   convention as the 3 classes added in Phase 11)
└── fixtures/
    ├── version_modified_render_gate/     # new: versionadded/changed/deprecated/removed
    ├── xref_refid_render_gate/           # new: :ref: section anchor + :term: glossary ref
    ├── desc_signature_render_gate/       # new: desc_returns/desc_optional(nested)/
    │                                     #      desc_signature_line/desc_inline
    └── trivial_blocks_render_gate/       # new: transition/glossary/tabularcolumns/abbr
```

### Pattern 1: Classed-inline dispatch — VER-01's italic label (no admonition machinery)

**What:** `visit_inline` currently treats every `nodes.inline` as a transparent container
(`pass`/`pass`, translator.py:2621–2640) — used for xref-wrapper inlines, glossary index markers,
etc. `versionmodified`'s label is *also* a `nodes.inline`, distinguished only by its `classes`
attribute (`["versionmodified", "added"|"changed"|"deprecated"|"removed"]`, confirmed via live
doctree dump this session). Detect that specific class and delegate to the existing
`visit_emphasis`/`depart_emphasis` dummy-node pattern (translator.py:556–624) — the same idiom
already used four other places in this file (`visit_title_reference`, `visit_literal_emphasis`).

**When to use:** Any inline sub-content that needs styling based on its Sphinx-assigned CSS-style
class, without introducing a new node-specific visitor.

**Verified doctree shape** [VERIFIED: live `sphinx-build -b typst` dump, this session]:
```
<versionmodified type="versionadded" version="0.6">
  <paragraph translatable="0">
    <inline classes="versionmodified added">Added in version 0.6: </inline>
    Some added text here.
```

**Recommended implementation:**
```python
# visit_versionmodified/depart_versionmodified: transparent, mirrors visit_inline's own shape.
# Content (a single child paragraph, per changeset.py's VersionChange.run(), confirmed by
# reading sphinx/domains/changeset.py directly) already renders correctly through the existing
# visit_paragraph chain -- unknown_visit's default "warn, don't skip" behavior already lets it
# through today; these two methods exist purely to eliminate the warning (relevant to the
# future GATE-02 warning-count metric), not to fix a content bug.
def visit_versionmodified(self, node: addnodes.versionmodified) -> None:
    pass

def depart_versionmodified(self, node: addnodes.versionmodified) -> None:
    pass

# visit_inline/depart_inline: extend the existing transparent-container method with one
# classed-dispatch branch. D-02's "unboxed italic label" requirement is met by delegating to
# the file's own proven dummy-node-emphasis pattern -- zero new escaping/separator logic needed,
# it inherits visit_emphasis's paragraph/list-item state juggling for free.
def visit_inline(self, node: nodes.inline) -> None:
    if "versionmodified" in node.get("classes", []):
        dummy_emph = nodes.emphasis()
        self.visit_emphasis(dummy_emph)
        return
    pass

def depart_inline(self, node: nodes.inline) -> None:
    if "versionmodified" in node.get("classes", []):
        dummy_emph = nodes.emphasis()
        self.depart_emphasis(dummy_emph)
        return
    pass
```

**Why this needs no `versionlabels` import (supersedes D-01's speculated mechanism, honors its
intent):** `sphinx/domains/changeset.py`'s `VersionChange.run()` (read directly from the installed
`.venv/lib/python3.13/site-packages/sphinx/domains/changeset.py` in this session) computes
`text = versionlabels[name] % self.arguments[0]` and inserts `nodes.inline('', '%s: ' % text,
classes=classes)` (or `'%s.' % text` for content-less directives) as the first paragraph child —
**at directive-run time**, before the writer/translator ever sees the tree. `versionlabels` itself
(`{"versionadded": _("Added in version %s"), "versionchanged": _("Changed in version %s"),
"deprecated": _("Deprecated since version %s"), "versionremoved": _("Removed in version %s")}`)
lives at `sphinx.domains.changeset.versionlabels` — **not** `sphinx.locale.versionlabels`, which
does not exist (`ImportError: cannot import name 'versionlabels' from 'sphinx.locale'`, confirmed
this session against Sphinx 9.1.0). The `_()` call already applies whatever locale is active. The
translator detecting the resulting classed inline is strictly simpler, has zero import-path risk,
and automatically tracks Sphinx's exact wording/localization with no duplication.

**Bare-directive case (no body content) verified:** `.. versionadded:: 0.6` with no arguments/body
produces a single paragraph containing only the classed inline with the label text ending in `.`
(period, not colon) — confirmed by reading `changeset.py`'s `else:` branch (line ~109) — so
`versionadded`/`versionremoved` "carry only the label" (D-02) is automatically true with zero
translator-side branching on `node["type"]`.

### Pattern 2: `refid` link resolution — already works; one companion fix required

**What:** `visit_reference`'s `refid` branch (translator.py:2119, from Phase 11/FIG-02) already
handles the general case correctly. **Confirmed via live end-to-end `sphinx-build` + `typst.compile()`
in this session**, not just code inspection:

```typst
// Source: emitted by the CURRENT translator, unmodified, for `:ref:`section-b`` -- confirmed
// this compiles and the link resolves (section anchor already emitted by visit_title, :272)
link(<section-b>,
text("Section B"))
```

**The gap — glossary `:term:` anchors are never emitted (required companion fix):**
`visit_term`/`depart_term` (translator.py:1127–1162) buffer-swaps the term's rendered text but never
reads `node.get("ids")` — so `link(<term-Widget>, ...)` (correctly emitted by the SAME `refid`
branch for a `:term:` xref) points at a label that is never defined. **Proven fatal** by extracting
a real `sphinx-build` output and running it through `typst.compile()` directly in this session:

```
TypstError: label `<term-Widget>` does not exist in the document
```

**Recommended fix** — reuse Phase 11's own established "bracket-wrap for markup-mode label
attachment" pattern (the same fix `visit_title`/`visit_figure` already apply for section/figure
anchors, translator.py:238–279, :1253–1255), verified by direct `typst.compile()` in this session
(both single-statement and multi-statement buffered term content tested and confirmed to compile
and correctly attach the label to the *combined* content, not just the last statement):

```python
def depart_term(self, node: nodes.term) -> None:
    if isinstance(self.current_term_buffer, list):
        term_content = "".join(self.current_term_buffer).strip()
    else:
        term_content = ""

    if self.saved_body is not None:
        self.body = self.saved_body
    self.saved_body = None

    # Glossary terms are :term: cross-reference targets, resolved via the
    # existing refid link branch (visit_reference, XREF-01) -- but nothing
    # previously emitted a Typst anchor for the term's docutils-assigned
    # id, so a :term: reference compiled to a dangling label and aborted
    # the whole build (confirmed via direct typst.compile() in Phase 12
    # research). Bracket-wrap in markup content so the <label> postfix can
    # attach -- mirrors the visit_title/visit_figure label pattern from
    # Phase 11. Tested this session with typst.compile(): both a single
    # text() statement and a multi-statement buffer compile correctly and
    # the label attaches to the combined content.
    if node.get("ids"):
        label_id = node["ids"][0]
        term_content = f"[#{{{term_content}}} <{label_id}>]"

    self.current_term_buffer = term_content
```

**Failed alternative, do not use** (proven this session): appending a bare `label("term-id")` via
`+` to the term content (`text("Widget") + label("term-id")`) raises `TypstError: cannot add content
and label` — `+` cannot concatenate `content` and `label` value types in Typst's type system. The
bracket-wrap markup-postfix form is the only mechanism that works.

**`:ref:` vs `:term:` vs unresolvable — confirmed contract holds:** A live fixture with a properly
placed `.. _section-b:` label resolves `:ref:`section-b`` to `link(<section-b>, ...)` with no
warning. A deliberately mis-placed label (this session's first, buggy fixture attempt) produced
Sphinx's own `WARNING: Failed to create a cross reference. A title or caption not found` and the
xref degraded to **plain text** ("section-b" rendered as unlinked prose) — confirming D-04's claim
that Sphinx resolves/warns unresolvable xrefs to plain text *before* the doctree reaches the
translator; the translator never sees a genuinely-dangling `refid` from an unresolvable `:ref:`/
`:term:` in normal operation. The one dangling-anchor case that DOES reach the translator is the
`visit_term` gap above (Sphinx resolves the xref correctly; the translator just never emits the
target).

### Pattern 3: `desc_*` family extensions (DESC-01…04)

All four slot into the already-established `desc_*` visitor family (translator.py:2701–2999) using
its existing three sub-idioms (pure passthrough, literal-prefix injection, `+`-concatenation flag
pair) — confirmed against live doctree dumps for every case below.

#### 3.1 `desc_returns` (DESC-01) — literal arrow prefix

**Verified shape** [VERIFIED: live doctree dump, this session, both unresolved-type and
resolved-type-xref cases]:
```
<desc_returns xml:space="preserve">int</desc_returns>
<!-- or, if the return type resolves to a documented py:class -->
<desc_returns xml:space="preserve"><reference internal="1" refid="MyClass" ...>MyClass</reference></desc_returns>
```
**Confirmed via live build:** the second (resolved) case is emitted by the translator's *existing*,
unmodified `visit_reference` refid branch as `link(<MyClass>, text("MyClass"))` — the SAME XREF-01
machinery Pattern 2 covers, extending for free into signature return-type annotations with zero
extra code. `visit_pending_xref` (translator.py:1687) is confirmed dead code for this case — Sphinx
resolves `pending_xref` to a `reference` node before the translator ever runs (the raw,
pre-resolution `env.get_doctree()` dump shows `pending_xref`; the actual `sphinx-build` output shows
the resolved `reference` — confirmed by comparing both in this session).

**Fix** — content already streams through correctly via `unknown_visit`'s non-skipping fallback
(confirmed: `text(")")` followed by a newline-separated `text("int")` or `link(...)` already
compiles today); the only missing piece is the `" -> "` literal:
```python
def visit_desc_returns(self, node: addnodes.desc_returns) -> None:
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self.add_text('text(" -> ")')
    if self.in_list_item:
        self.list_item_needs_separator = True

def depart_desc_returns(self, node: addnodes.desc_returns) -> None:
    pass
```

#### 3.2 `desc_signature_line` (DESC-02) — `linebreak()`, not source `\n`

**Verified shape** [VERIFIED: live doctree dump, this session, via `.. cpp:function::`]: each
declaration's signature content (keyword, name, parameter list) is wrapped one level deeper than
`desc_signature` in a `desc_signature_line` child when the C++/C domain flags `is_multiline="1"` on
`desc_signature`. Content already renders correctly today (confirmed: `unknown_visit` doesn't skip,
so the existing `desc_sig_*`/`desc_name`/`desc_parameterlist` handlers already stream the line's
content through). **This session was unable to construct a live example with two genuine
`desc_signature_line` siblings under one `desc_signature`** (attempted `.. cpp:function::` back-to-
back and template-continuation syntax; both produced either two separate top-level `desc` blocks or
a Sphinx parse error) — flagged as an open item below; the single-line case is HIGH confidence, the
multi-line-separator mechanism is a direct, low-risk application of the file's own
`is_first_list_item` precedent (translator.py:63, :802, :898) regardless.

**Critical, empirically-proven correction:** a bare source-level `\n` placed between two `text(...)`
statements inside a code block does **not** produce a visible line break — confirmed by compiling
`{text("a")\ntext("b")}` and extracting PDF text, which reads `"ab"` on one line with no line break.
Only Typst's `linebreak()` (stdlib, first use in this codebase) produces a real break — confirmed by
compiling `{text("a")\nlinebreak()\ntext("b")}` and extracting two separate lines from `pypdf`.

**Recommended fix** (one new state variable — the phase's D-05-sanctioned allowance):
```python
# In __init__, alongside the other "is_first_*" state:
self._is_first_desc_signature_line: bool = True

def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
    dummy_strong = nodes.strong()
    self.visit_strong(dummy_strong)
    self._is_first_desc_signature_line = True  # reset per signature

def visit_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
    if not self._is_first_desc_signature_line:
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text("linebreak()")
        if self.in_list_item:
            self.list_item_needs_separator = True
    self._is_first_desc_signature_line = False

def depart_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
    pass
```
This is backward-compatible with the already-verified single-line case (the `if not
self._is_first_desc_signature_line` guard means the first line emits nothing extra).

#### 3.3 `desc_optional` (DESC-03) — literal bracket wrap, recursion-safe

**Verified nested shape** [VERIFIED: live doctree dump, this session, via `.. py:function::
printf(fmt[, args[, more]])`]:
```
<desc_optional>
  <desc_parameter><desc_sig_name>args</desc_sig_name></desc_parameter>
  <desc_optional>
    <desc_parameter><desc_sig_name>more</desc_sig_name></desc_parameter>
  </desc_optional>
</desc_optional>
```
The nested `desc_optional` is a **sibling** of the outer group's `desc_parameter`, not nested inside
it — matching the literal bracket structure of `fmt[, args[, more]]`.

**Recommended fix** — literal `[`/`]` wrap while remaining inside the parent's `in_desc_parameter`
`+`-join scope (do not toggle it off), reusing `_desc_parameter_has_content` (zero new state,
already exists at translator.py:85–87). The comma before the optional group is already correctly
emitted by the preceding sibling's `depart_desc_parameter` (`node.next_node(descend=False,
siblings=True)` already detects the following `desc_optional` as "a next sibling exists", confirmed
in this session's live output — `text(", ") + text("[") + ...`):
```python
def visit_desc_optional(self, node: addnodes.desc_optional) -> None:
    if self._desc_parameter_has_content:
        self.add_text(" + ")
    self.add_text('text("[")')
    self._desc_parameter_has_content = True

def depart_desc_optional(self, node: addnodes.desc_optional) -> None:
    self.add_text(' + text("]")')
    self._desc_parameter_has_content = True
```
**Recursion is automatic and needs no special-casing:** because `desc_optional`'s own visit/depart
logic is depth-agnostic (it only reads/writes the already-shared `_desc_parameter_has_content`
flag), a nested `desc_optional` fires the identical handler again, correctly producing
`text("[") + text("args") + text("[") + text("more") + text("]") + text("]")` for the multi-level
case above — confirmed by tracing the doctree structure against this handler shape (not yet run
through a modified translator, since that requires code changes out of this research agent's scope,
but the mechanism is identical to the already-proven single-level case and introduces no new
state-interaction risk).

#### 3.4 `desc_inline` (DESC-04) — pass-through resolves D-06 entirely

**Verified shape** [VERIFIED: live doctree dump, this session, via `:cpp:expr:`int``]:
```
<desc_inline classes="cpp-expr sig sig-inline cpp" domain="cpp">
  <desc_sig_keyword_type classes="kt">int</desc_sig_keyword_type>
</desc_inline>
```
**D-06's predicate, resolved:** Sphinx's own domain code already emits **distinct node classes** for
a standalone declaration (`desc_signature`, which the translator delegates to `visit_strong`) versus
an inline fragment (`desc_inline`, a structurally separate node type that never appears as a
`desc_signature`). No parent-node inspection or nesting-depth check is needed — the predicate is
simply "which `visit_*` method Sphinx's own node-type dispatch calls." Confirmed via live build:
without any explicit handler, `unknown_visit`'s default (warn, don't skip) already lets the child
`desc_sig_keyword_type` → Text stream through as plain `text("int")` with **no** `strong()`
wrapper — proving D-06's requirement is trivially satisfied by a transparent pass-through, the same
shape as `visit_inline`:
```python
def visit_desc_inline(self, node: addnodes.desc_inline) -> None:
    pass

def depart_desc_inline(self, node: addnodes.desc_inline) -> None:
    pass
```
This handler's only job is to silence the `unknown_visit` warning — zero content-behavior change
from what already renders correctly today.

### Pattern 4: Trivial structural nodes (BLK-01/04/05/06)

#### 4.1 `transition` (BLK-01) — genuine content gap

**Verified shape:** self-closing, no children (`<transition/>`). Confirmed via live build: today
this renders **nothing at all** (no horizontal rule appears anywhere in the emitted `.typ`) — this
is a true content gap, not just a warning-suppression task.
```python
def visit_transition(self, node: nodes.transition) -> None:
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self.add_text("line(length: 100%)\n\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
    raise nodes.SkipNode

def depart_transition(self, node: nodes.transition) -> None:
    pass  # unreached; kept for symmetry with visit_index/depart_index convention
```
`line(length: 100%)` confirmed to compile via direct `typst.compile()` in this session (used inline
inside the combined sanity-check snippet described in Pattern 1/2's verification work).

#### 4.2 `glossary` (BLK-04) — pass-through; anchor fix lives in `visit_term` (Pattern 2)

**Verified:** the `definition_list` child already renders correctly today via the existing
`visit_definition_list`/`visit_term`/`visit_definition` chain (confirmed: `unknown_visit` on
`glossary` doesn't skip, so it descends into the already-handled `definition_list` for free). The
fix needed for BLK-04 is *only* the transparent pass-through (to silence the warning); the *actual*
bug (dangling `:term:` anchor) is `visit_term`'s job, documented once in Pattern 2 above — do not
duplicate the anchor-emission fix here.
```python
def visit_glossary(self, node: addnodes.glossary) -> None:
    pass

def depart_glossary(self, node: addnodes.glossary) -> None:
    pass
```

#### 4.3 `tabular_col_spec` (BLK-05) — trivial `SkipNode`

**Verified shape:** self-closing (`<tabular_col_spec spec="|l|l|"/>`), no children — already
effectively a no-op today (nothing to leak since there's nothing to descend into), but D-07 mandates
an explicit `SkipNode` for defensive clarity and to silence the warning:
```python
def visit_tabular_col_spec(self, node: nodes.Node) -> None:
    raise nodes.SkipNode
```
No `depart_tabular_col_spec` needed (unreached).

#### 4.4 `abbreviation` (BLK-06) — dummy-Text-node delegation

**Verified shape:** `<abbreviation explanation="Application Programming Interface">API</abbreviation>`
— single `Text` child, `explanation` node attribute. Confirmed via live build: the `Text` child
("API") already renders correctly today (unknown_visit doesn't skip); the `explanation` attribute is
**completely dropped** — a genuine content gap.

**Recommended fix** — reuse the file's own dummy-node-delegation idiom (already used at
`visit_title_reference`, `visit_literal_strong`, `visit_literal_emphasis`) to route the appended
expansion text through `visit_Text`'s existing escaping regime and separator logic, satisfying D-08's
"stateless, expands every occurrence" requirement automatically (no state variable at all):
```python
def visit_abbreviation(self, node: nodes.abbreviation) -> None:
    pass  # let the term's own Text child render via the normal chain

def depart_abbreviation(self, node: nodes.abbreviation) -> None:
    explanation = node.get("explanation", "")
    if explanation:
        # Route through the existing visit_Text escaping/separator regime
        # (dummy-node delegation, same idiom as visit_title_reference /
        # visit_literal_strong) rather than a bespoke f-string interpolation
        # -- automatically inherits string-literal escaping for any
        # markup-special character in the explanation text.
        dummy_text = nodes.Text(f" ({explanation})")
        self.visit_Text(dummy_text)
```

### Anti-Patterns to Avoid

- **Importing `sphinx.domains.changeset.versionlabels` to reconstruct version-label text.**
  Unnecessary (Pattern 1) — the label is already baked into the doctree by Sphinx itself.
- **Using `node.astext()` for the `abbreviation`/`term` fixes.** Bypasses escaping (Pitfall 7,
  carried from 11-RESEARCH.md); the dummy-Text-node delegation pattern is the correct alternative.
- **Appending a bare `label(...)` via `+` to content.** Proven this session to raise a Typst type
  error (`cannot add content and label`) — always use the markup bracket-wrap form for label
  attachment on arbitrary content.
- **Assuming source-level `\n` between code-mode statements produces a visual line break.** Proven
  false this session — always use `linebreak()` for DESC-02.
- **Delegating `desc_inline` to `visit_strong` "for consistency with `desc_signature`."** This is
  exactly the D-06 violation the requirement forbids — `desc_inline` must remain a transparent
  pass-through.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Version-label wording/localization | A hardcoded English label map, or an import-based reconstruction of Sphinx's `versionlabels` dict | Detect the already-classed `nodes.inline` Sphinx itself emits | Sphinx already did this work at parse time; duplicating it only risks drift |
| Label attachment to arbitrary buffered content | A code-mode `label()` postfix hack | The markup bracket-wrap `[#{...} <label>]` pattern already proven in Phase 11 | The only form Typst's type system accepts for attaching a label to a content value built from multiple statements |
| Line breaks between signature lines | A source-formatting trick / relying on `\n` | Typst's native `linebreak()` | Source `\n` has zero effect on rendered output; proven via direct compile in this session |
| Optional-parameter bracket nesting | A depth-counter or a new state variable for nesting level | The recursive, depth-agnostic `desc_optional` handler (reuses `_desc_parameter_has_content`) | Sphinx already encodes nesting structurally as sibling `desc_optional` nodes; the handler doesn't need to know its own depth |
| Real-compile PDF validation | A bespoke Typst-syntax linter | The existing `tests/test_pdf_render_gate.py` pipeline | Already proven (Phase 8.1/11); string-level checking cannot detect any of the bugs this research found |

**Key insight:** Every fix in this phase is either (a) a pure pattern-reuse addition with zero new
machinery, or (b) a companion fix to an *already-proven* Phase 11 pattern (bracket-wrap label
attachment) applied to a location Phase 11 didn't touch (`visit_term`). Nothing in this phase
requires a genuinely new architectural idiom — confirmed by direct compile experimentation, not just
code-reading.

## Common Pitfalls

Carried forward from `.planning/research/PITFALLS.md` (milestone-level) where directly relevant,
plus two new pitfalls discovered in this session's live-compile experimentation.

### Pitfall 1 (carried forward): One bad node aborts the ENTIRE PDF
Still the standing bar — every fixture in this phase's extension to `test_pdf_render_gate.py` must
go through a real `typst.compile()`. This session's own discovery (the `:term:` dangling-label bug)
is a direct, concrete instance of this exact pitfall already live in the current codebase.

### Pitfall 2 (carried forward): Markup/code-mode mismatch
The `visit_term` label fix is a textbook instance: the buffered term content is code-mode
(`text(...)` calls); attaching a label requires briefly stepping into markup mode via `[#{...}
<label>]`, exactly mirroring the `visit_title`/`visit_figure` precedent.

### Pitfall 9 (carried forward): String-agreement testing alone proves nothing
Directly demonstrated again in this session: a purely code-reading pass over `visit_term` would
plausibly have concluded "the refid branch already handles `:term:`, nothing more to do" (matching
D-03's framing) — only a real `typst.compile()` round-trip surfaced the dangling-label fatal bug.

### New Pitfall 11: Source-level newlines between code-mode statements are cosmetic, not visual
**What goes wrong:** It is easy to assume — by analogy with the existing `_add_paragraph_separator`
convention (which inserts `\n` between sibling paragraph-content expressions purely to satisfy
Typst's "statements need a separator" grammar rule) — that inserting more `\n` characters
automatically means "these two things will render on separate lines." They do not. A source `\n`
between two code-mode statements is *only* a Typst-grammar-level statement separator; the rendered
output shows the two content values concatenated with **zero** visual space between them.
**Why it happens:** The existing codebase's separator convention (newline-joining sibling content
expressions inside a `{...}` block) coincidentally never needed an ACTUAL visible line break before
this phase — every prior newline-joined sequence (paragraph content, list items, admonition bodies)
was meant to render as continuous prose, so the distinction between "syntactic separator" and
"visual break" never mattered until DESC-02's explicit "line breaks between lines" requirement.
**How to avoid:** Use Typst's `linebreak()` (or `parbreak()` for paragraph-level breaks, not needed
in this phase) as an explicit, separate statement whenever a REQUIREMENT calls for a visible line
break — never assume a source `\n` alone satisfies it. Verify with a real `pypdf` text-extraction
assertion (e.g., asserting two known distinct signature-line substrings and confirming they are
NOT concatenated with no separator in the extracted text), not just a `.typ`-source substring check.
**Warning signs:** A `.typ`-source-only unit test asserting `"\n" in output` for a line-break
requirement — this passes trivially for the wrong reason (a syntactic separator that produces no
visible effect) and must be replaced with a real-compile extraction assertion.

### New Pitfall 12: `+` cannot concatenate `content` and `label` Typst values
**What goes wrong:** Attempting to attach a label to already-built content via `content_expr +
label("id")` raises `TypstError: cannot add content and label` at compile time — not a silent
failure, but still only discoverable via a real compile, not string inspection.
**Why it happens:** The file's established `+`-join convention (used pervasively for
`desc_parameter`/`link` content) makes `+` feel like the "default" way to combine any two emitted
pieces. Typst's type system treats `label` as a distinct value type from `content`, and `+` is only
defined between same/compatible types.
**How to avoid:** Any new anchor/label-emission site must use the markup bracket-wrap form (`[#{...}
<label>]`), matching the pattern already proven for `visit_title`/`visit_figure` in Phase 11 and
now `visit_term` in this phase — never attempt to `+`-join a `label(...)` call onto content.

## Code Examples

Verified patterns — all compiled directly via `typst.compile()` in this research session (not
merely read from documentation):

### 1. Italicized version label (Pattern 1), confirmed compiling
```typst
// Source: this session's direct typst.compile() verification
par({emph({text("Added in version 0.6: ")})
text("Some added text here.")})
```

### 2. Glossary term with a working `:term:` anchor (Pattern 2 fix), confirmed compiling
```typst
// Source: this session's direct typst.compile() verification (glossary_test3.typ)
par({text("See the term ")
link(<term-Widget>,
text("Widget"))
text(".")})

terms(terms.item([#{text("Widget")} <term-Widget>], par({text("A thing that does stuff.")})))
```

### 3. Multi-statement label attachment (proving the label attaches to combined content, not just
the last statement), confirmed compiling
```typst
// Source: this session's direct typst.compile() verification (glossary_test4.typ)
terms.item([#{text("Multi")
text(" Word")} <term-Multi>], par({text("Two words.")}))
```

### 4. `linebreak()` producing an actual visible break, confirmed via `pypdf` extraction
```typst
// Source: this session's direct typst.compile() + pypdf verification
strong({text("int")
text(" ")
text("overload_a")
text("(int x)")
linebreak()
text("int")
text(" ")
text("overload_b")
text("(int x, int y)")})
```
Extracted text: `'int overload_a(int x)\nint overload_b(int x, int y)'` — two genuinely separate
lines.

### 5. Signature with nested optional parameter and return arrow (Pattern 3.1/3.3 target shape,
manually assembled and confirmed compiling)
```typst
// Source: this session's direct typst.compile() verification (sanity.typ)
par({text("Prefix ")
text("(") + text("a") + text(", ") + text("[") + text("b") + text("]") + text(")")
text(" -> ")
text("int")})
```

### 6. Abbreviation expansion (Pattern 4.4 target shape, confirmed compiling)
```typst
// Source: this session's direct typst.compile() verification (sanity.typ)
par({text("API")
text(" (Application Programming Interface)")})
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `versionmodified` falls through `unknown_visit` (content renders, but plain, un-italicized, with a warning) | Explicit classed-inline dispatch renders the Sphinx-computed label in italic | This phase (VER-01) | Cosmetic-only fix for content that was already correct; eliminates ×972 warnings |
| `visit_term` never emits an anchor for its own `ids` | Bracket-wrapped `[#{...} <label>]` label attachment | This phase (XREF-01/BLK-04 companion fix) | **Fixes a genuine, currently-live fatal compile abort** for any document with a `:term:` cross-reference to a glossary entry |
| `desc_returns`/`desc_optional`/`desc_signature_line`/`desc_inline` fall through `unknown_visit` (content mostly already renders via child handlers, but incompletely/without correct punctuation/breaks) | Explicit handlers add the missing arrow, brackets, and line breaks | This phase (DESC-01…04) | Signature rendering becomes visually correct; `desc_inline` needed zero behavior change, only warning suppression |
| `transition`/`tabular_col_spec` render nothing (transition: true content gap; tabular_col_spec: correctly nothing, since it's a LaTeX-only hint) | Explicit `line(length: 100%)` for transition; explicit `SkipNode` for tabular_col_spec | This phase (BLK-01/05) | Transition gains real content; tabular_col_spec gains explicit intent (no behavior change) |
| `abbreviation`'s `explanation` attribute silently dropped | Dummy-Text-node delegation appends `" (expansion)"` | This phase (BLK-06) | Fixes a genuine content gap |

**Deprecated/outdated:** None.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A genuine multi-`desc_signature_line`-within-one-`desc_signature` doctree (not two separate `desc` blocks) was not constructed live in this session; the `linebreak()`-based fix design is based on the single-line case (verified) plus the `is_first_list_item` precedent (established pattern), not a directly observed multi-line dump | Pattern 3.2 | If the real multi-line shape differs from the assumed "N `desc_signature_line` siblings directly under one `desc_signature`" structure (e.g., if Sphinx wraps them differently for some domain/version combination), the `_is_first_desc_signature_line` reset point may need adjusting. **Mitigate:** the planner/executor should dump a real multi-line C/C++ or Python-overload doctree (e.g., a template declaration with `\` line continuation, or Sphinx's documented multi-signature `.. py:function::` continuation-line syntax) as a first implementation step, before finalizing the fixture. |
| A2 | The `desc_optional` recursive fix (Pattern 3.3) was verified against the doctree *structure* (confirmed via live dump) but not against an actual modified-translator compile, since modifying `translator.py` is out of this research agent's scope | Pattern 3.3 | Low risk — the mechanism is structurally identical to the already-proven single-level `desc_parameter`/`+`-join pattern; if nesting behaves unexpectedly, the GATE-01 fixture (which must include the `printf(fmt[, args[, more]])` case per the phase's own DESC-03 "incl. nesting" requirement) will catch it immediately via `typst.compile()` failure, not silently. |

## Open Questions

1. **Exact multi-line `desc_signature_line` construction syntax for the GATE fixture.**
   - What we know: `desc_signature_line` is real, confirmed via the C++ domain's `is_multiline="1"`
     `desc_signature` attribute; a single line's content renders correctly today via existing
     handlers.
   - What's unclear: this session could not find the exact reStructuredText syntax that produces
     TWO `desc_signature_line` siblings under ONE `desc_signature` (attempts produced either two
     separate `desc` blocks or a Sphinx parse error).
   - Recommendation: the planner/executor should consult Sphinx's own C/C++ domain test suite or
     documentation for the exact multi-declaration continuation syntax (likely a trailing `\` line
     continuation within a single `.. cpp:function::` block, per Sphinx's C++ domain docs on
     "declarations spanning multiple lines") as the first step of implementing/fixturing DESC-02,
     and dump the resulting doctree before finalizing the fixture content.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Sphinx | All node-shape verification, GATE fixtures | ✓ | 9.1.0 [VERIFIED this session] | — |
| typst-py | Real-compile verification (this research + GATE-01) | ✓ | matches `>=0.15.0,<0.16` pin [VERIFIED this session via successful `typst.compile()`] | — |
| pypdf | Text-extraction verification | ✓ | matches `>=6.14,<7` pin [VERIFIED this session via successful `PdfReader`] | — |

No missing dependencies. This phase's implementation environment is identical to Phase 11's
(already-proven working GATE-01 harness).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (via `tox -e cov`), config in `pyproject.toml` `[tool.pytest.ini_options]` |
| Config file | `pyproject.toml` (markers: `slow`; `addopts = "-v --strict-markers"`) |
| Quick run command | `pytest tests/test_pdf_render_gate.py -k <new_test_name> -v` |
| Full suite command | `pytest --cov=typsphinx --cov-report=term-missing` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VER-01 | All four version directives render italic label + correct body, compile cleanly | real-compile | `pytest tests/test_pdf_render_gate.py::TestVersionModifiedRenderGate -v` | ❌ Wave 0 — new fixture `tests/fixtures/version_modified_render_gate/` |
| XREF-01 | `:ref:` section anchor AND `:term:` glossary ref both resolve to working PDF links, no fatal | real-compile | `pytest tests/test_pdf_render_gate.py::TestXrefRefidRenderGate -v` | ❌ Wave 0 — new fixture `tests/fixtures/xref_refid_render_gate/`; **must include the `:term:` case, since this is the exact scenario proven fatal in this research** |
| DESC-01…04 | Return arrow, multi-line breaks, nested optional brackets, inline fragment (no `strong()`) all render correctly, compile cleanly | real-compile | `pytest tests/test_pdf_render_gate.py::TestDescSignatureRenderGate -v` | ❌ Wave 0 — new fixture `tests/fixtures/desc_signature_render_gate/` |
| BLK-01/04/05/06 | Transition rule, glossary definition list, tabularcolumns no-leak, abbr expansion all render/skip correctly, compile cleanly | real-compile | `pytest tests/test_pdf_render_gate.py::TestTrivialBlocksRenderGate -v` | ❌ Wave 0 — new fixture `tests/fixtures/trivial_blocks_render_gate/` |

### Sampling Rate
- **Per task commit:** the specific new test class for that handler group (`pytest
  tests/test_pdf_render_gate.py -k <ClassName>`)
- **Per wave merge:** `pytest tests/test_pdf_render_gate.py -v` (all render-gate classes,
  Phase 11 + Phase 12)
- **Phase gate:** Full suite green (`pytest --cov=typsphinx`) before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/fixtures/version_modified_render_gate/` — covers VER-01 (all four directive kinds,
      including a content-less `.. versionadded::` to exercise the period-vs-colon wording branch)
- [ ] `tests/fixtures/xref_refid_render_gate/` — covers XREF-01, **must include a `:term:` case**
      (this research proved it is currently fatal without the `visit_term` companion fix)
- [ ] `tests/fixtures/desc_signature_render_gate/` — covers DESC-01…04; **the DESC-02 sub-case
      needs the multi-line `desc_signature_line` construction syntax resolved first (Open
      Question 1)** before the fixture can exercise the genuine multi-line case; the single-line
      + arrow + nested-optional + inline-fragment sub-cases have no such blocker
- [ ] `tests/fixtures/trivial_blocks_render_gate/` — covers BLK-01/04/05/06
- [ ] New test classes in `tests/test_pdf_render_gate.py` (4 classes, mirroring the exact
      `@pytest.mark.slow` + `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE))`
      shape of the three classes Phase 11 added)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Not applicable — this is a docs-build-time translator, no auth surface |
| V3 Session Management | no | Not applicable |
| V4 Access Control | no | Not applicable |
| V5 Input Validation | yes | Reuse the existing `visit_Text` string-literal escaping regime (backslash → quote → `\n`/`\r`/`\t`, in that order) for every new interpolation site this phase introduces (`abbreviation.explanation`, the term-content bracket-wrap). Never introduce a new ad-hoc f-string interpolation of raw docutils attribute/`astext()` content — always route through `visit_Text` (directly or via dummy-node delegation) or an existing proven helper. |
| V6 Cryptography | no | Not applicable |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unescaped `abbreviation.explanation` (author-controlled RST attribute text) interpolated directly into generated Typst source | Tampering (malformed/malicious markup-special characters in doc source corrupting or crashing the Typst compile) | Route through `visit_Text` via dummy-node delegation (Pattern 4.4) — inherits the existing string-literal escaping automatically; never build a raw f-string from `node.get("explanation")` |
| A dangling/incorrectly-constructed label reference (this phase's own `visit_term` discovery) | Denial of Service (build-time) — a single malformed anchor aborts the ENTIRE document compile, not just the affected page (Pitfall 1, carried forward) | Every new label-emission site must be proven via a real `typst.compile()` fixture, not code inspection alone — exactly the gap that let the `:term:` bug ship in Phase 11 undetected |

## Sources

### Primary (HIGH confidence)
- `typsphinx/translator.py` (own repo, direct `Read` this session, current post-Phase-11 state,
  2999 lines) — all cited line numbers re-confirmed in this session, not carried forward from
  CONTEXT.md
- `.venv/lib/python3.13/site-packages/sphinx/domains/changeset.py` (installed Sphinx 9.1.0 source,
  direct `Read` this session) — `VersionChange.run()`, `versionlabels`, `versionlabel_classes`
- Live `sphinx-build -b typst` + `env.get_doctree()` doctree dumps (this session, against a series
  of purpose-built fixtures covering `versionmodified`, `:ref:`/`:term:`, `glossary`, `transition`,
  `tabular_col_spec`, `abbreviation`, `desc_returns`, `desc_optional` incl. nesting,
  `desc_signature_line`, `desc_inline`)
- Direct `typst.compile()` executions via the project's own pinned `typst-py` (this session) —
  proved both failing cases (dangling `:term:` label, `content + label` type error, `\n`-only
  line-break attempt) and succeeding fixes (bracket-wrap label attachment, `linebreak()`,
  arrow/bracket text construction)
- `tests/test_pdf_render_gate.py` (own repo, direct `Read` this session) — GATE-01 harness shape,
  `LEAK_SIGNATURES`, `@pytest.mark.slow`/`@pytest.mark.skipif` convention
- `.planning/phases/11-issue-114-fatal-fixes-graceful-degrade-net/11-RESEARCH.md`,
  `.planning/research/{SUMMARY,PITFALLS,ARCHITECTURE}.md` — milestone-level precedent, Pitfalls
  1–10, established state patterns (buffer-swap, dummy-node delegation, `+`-concatenation,
  list-item-style `{}` blocks)
- `pyproject.toml`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`,
  `CLAUDE.md` — project constraints, requirement/success-criteria wording, dependency pins

### Secondary (MEDIUM confidence)
- None this session — every claim that would normally be MEDIUM (node shapes, Sphinx internals) was
  upgraded to HIGH via direct live verification rather than left as documentation-sourced inference.

### Tertiary (LOW confidence)
- The exact reStructuredText syntax producing a genuine multi-`desc_signature_line` doctree (Open
  Question 1, Assumption A1) — flagged explicitly, not asserted as fact.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, all functions confirmed via direct `typst.compile()`
  execution in this session, not just documentation lookup
- Architecture: HIGH — every node shape confirmed via live doctree dumps against the project's
  actual installed Sphinx 9.1.0, not inferred from generic docutils/Sphinx documentation
- Pitfalls: HIGH — two of the pitfalls in this document (source-`\n` vs `linebreak()`, `content +
  label` type error) were discovered by deliberately compiling the WRONG approach first and
  observing the actual `TypstError`, not reasoned from first principles
- DESC-02 multi-line construction: MEDIUM — single-line case HIGH confidence, genuine multi-line
  doctree shape not directly observed this session (see Open Question 1)

**Research date:** 2026-07-12
**Valid until:** 30 days (stable, single-file, no fast-moving external dependency; re-verify sooner
only if the Sphinx floor version changes, since Pattern 1's finding is specifically tied to Sphinx
9.1.0's `sphinx/domains/changeset.py` implementation)
