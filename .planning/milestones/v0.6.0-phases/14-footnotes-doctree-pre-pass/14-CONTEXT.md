# Phase 14: Footnotes (doctree pre-pass) - Context

**Gathered:** 2026-07-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Add `footnote` / `footnote_reference` node support to `typsphinx/translator.py` so that footnotes
render via **Typst-native `footnote[...]`** placed inline at the *reference* site (not at the
docutils definition location). This is the only architecturally-new item in the milestone: a
**document-order pre-pass** indexes footnote bodies by id so the reference site can emit the note,
and a footnote cited more than once **reuses its placed note by Typst label** rather than
duplicating the body. Requirement: **FN-01** only.

All work is confined to `translator.py` + fixture dirs + the existing real-compile gate
(`tests/test_pdf_render_gate.py`). Zero new runtime dependencies; the 3-way `@preview`
version-sync surface (writer.py / template_engine.py / templates/base.typ) is untouched. Scope is
HOW to implement this fixed node set — `citation` / `citation_reference` and other node
*capabilities* are out of scope. The empirical bar is a real `typst.compile()` outcome (GATE-01
standing pattern), never string-agreement asserts alone. Carried forward as locked project
patterns: the **buffer-swap idiom** (render inline children through the normal visitor chain,
**never `node.astext()`** — Phase 11/13) and **compile-safe emission under unified code-mode**
(`visit_document` opens `#{`; markup-mode constructs must be bracket-wrapped à la Phase 11).

</domain>

<decisions>
## Implementation Decisions

**Discussion mode:** interactive — user selected all four gray areas and accepted the recommended
default for each. Each decision below is locked.

### Pre-pass architecture (D-01, D-02)
- **D-01: Build the id→footnote-node index in `visit_document` via `self.document.traverse(nodes.footnote)`.**
  At the start of `visit_document`, walk the doctree once and build a `{node['ids'][0]: node}`
  dict. No new `NodeVisitor` class and no separate pre-walk in `writer.translate()` — this rides
  the existing walkabout, is the lightest option, and completes per-document (each `#include()`d
  document indexes its own footnotes). (Rejected: a dedicated pre-walk NodeVisitor — extra
  state-handoff plumbing for no gain; and leaning on docutils' `document.footnotes`/`autofootnotes`
  tables — pickup gaps and version-coupling risk.)
- **D-02: Render footnote bodies lazily at the reference site, not eagerly in the pre-pass.**
  The index holds **node references only**. The first `footnote_reference` reaching a given id
  renders that footnote node's children **through the buffer-swap idiom** (swap `self.body` to a
  fresh list, walk the children via the normal visitor chain, capture, restore) in the natural
  buffer context. This preserves inline markup/escaping and makes the "first-cite defines,
  repeat-cites reuse" split fall out naturally. (Rejected: eager pre-pass render into stored
  strings — the body would render outside/ahead of the main walkabout and could depend on
  mid-walk translator state.)

### Label & reuse scheme (D-03, D-04)
- **D-03: Typst label = `<fn-{docutils id}>`, derived from the footnote node's `node['ids'][0]`.**
  The docutils id is already `[a-z0-9-]` and document-unique, and the `footnote_reference`'s
  `refid` ties directly to it — collision-free with no side table. The **first reference in
  document order** emits the definition `footnote[<body>] <fn-{id}>`; every **repeat reference**
  emits the reuse form `footnote(<fn-{id}>)`. Track already-emitted ids in a `set` to pick the
  branch. (Rejected: a monotonic `fn-1, fn-2…` counter — needs a `refid`↔counter side table for
  no benefit over using the id directly.)
- **D-04: Numbering is owned by Typst-native `footnote[]` auto-numbering.** Do not force docutils'
  numbers or symbols. Because notes appear at the reference site in document order, Typst's
  auto-numbering naturally matches document order. `auto-symbol` footnotes (`[*]`) flow through the
  same `footnote[]` and take whatever mark Typst assigns — no strict symbol-glyph reproduction.
  (REQUIREMENTS already rejects a 1:1 port of docutils backref/number plumbing.)

### Definition-node suppression (D-05, D-06)
- **D-05: `visit_footnote` raises `nodes.SkipNode`.** The definition node emits **nothing** at its
  natural (docutils) location — satisfying SC#1 ("no floating body left at the docutils definition
  location"). The body is reached only via the D-01 index + D-02 lazy render, so skipping the
  definition node does not lose it.
- **D-06: On lazy render, skip the leading `label` child of the footnote node; render only the body.**
  A `footnote` node's first child is a `label` (docutils number + backref plumbing). The lazy
  render skips that `label` child and passes only the remaining paragraph body through the visitor
  chain (Typst supplies its own marker). Symmetrically, `footnote_reference` emits **only**
  `footnote[...]` / `footnote(<label>)` and never the docutils number text — no double marker.

### Scope & degradation (D-07, D-08, D-09)
- **D-07: `citation` / `citation_reference` are OUT of scope.** FN-01 covers `footnote` /
  `footnote_reference` only. Existing behavior for citation nodes is retained (degrade net handles
  them if unimplemented); captured as a deferred idea for the backlog.
- **D-08: A dangling `footnote_reference` (refid not in the index) → `logger.warning` + skip, no fatal.**
  Emitting a bodyless `footnote()` reference in Typst can error, so on a missing refid we
  log a warning and emit nothing — consistent with the milestone's no-fatal / graceful-degrade net.
- **D-09: A defined-but-never-referenced footnote is dropped (allowed).** By design bodies appear
  only at reference sites, so an unreferenced footnote's body simply never emits. docutils itself
  warns on unreferenced footnotes; this case is outside the success criteria. Optionally add a
  warning, but do not build end-of-document placement machinery.

### Claude's Discretion / research flags
- **Exact label-attachment syntax under unified code-mode is the core research task.**
  `visit_document` opens `#{` (unified code mode), where the markup `[content] <label>` /
  `footnote(<label>)` forms may not attach directly. Research (RESEARCH.md in plan-phase) + the
  GATE-01 render gate must confirm a **compile-safe** emission — likely the Phase 11 bracket-wrap
  idiom around the `footnote[…] <label>` construct. The SC#2 "no duplicated body" bar *requires* a
  working reuse mechanism; if the `<label>` + `footnote(<label>)` pairing cannot be made
  compile-safe as written, research must find the working Typst reference form before locking the
  emission — this is the primary thing to prove with a real `typst.compile()`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirement & phase spec
- `.planning/REQUIREMENTS.md` — **FN-01** (line 36): the single requirement this phase delivers;
  also the "Rejected" table (Typst-native footnote model vs docutils backref port).
- `.planning/ROADMAP.md` §"Phase 14: Footnotes (doctree pre-pass)" — Goal + the 4 Success Criteria
  (single-ref, double-ref-no-dup, inline-markup body, GATE-01 fixture with footnote-in-list-item).

### Code to read / mirror
- `typsphinx/translator.py:175` — `visit_document` (index-build site; note it opens `#{` unified
  code mode → compile-safe emission constraint).
- `typsphinx/translator.py:1358-1385` — figure-caption **buffer-swap idiom** (`visit_caption` /
  `depart_caption`); the exact pattern to mirror for lazy footnote-body render.
- `typsphinx/translator.py:2700` — `visit_topic` and the shared `visit_title` buffer-swap
  (Phase 13) — reference for the buffer-swap-never-astext convention.
- `typsphinx/writer.py:60` — `TypstWriter.translate()` / `document.walkabout(self.visitor)`
  (where the single walkabout runs; confirms no separate pre-walk is needed for D-01).
- `tests/test_pdf_render_gate.py` — GATE-01 standing bar; existing render-gate classes
  (`TestFigureCaptionRenderGate`, `TestVersionModifiedRenderGate`) are the template for a new
  `TestFootnoteRenderGate` (real `typst.compile()`, sentinel-once + no-source-leak asserts).

### Prior-phase decisions carried forward
- `.planning/phases/11-issue-114-fatal-fixes-graceful-degrade-net/11-CONTEXT.md` — buffer-swap
  (D-03/D-04), bracket-wrap for markup-mode content, GATE-01 render-gate origin.
- `.planning/phases/13-shared-dispatch-point-changes-topic-line-blocks/13-CONTEXT.md` —
  `visit_title` generalization + buffer-swap-title precedent.

*No dedicated ADR exists for footnotes; RESEARCH.md is to be produced in `/gsd-plan-phase`.*

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Buffer-swap idiom** (`depart_caption` at `translator.py:1380`; `visit_title` /
  `_depart_admonition`): save `self.body`, swap to a fresh list, walk children through the normal
  visitor chain, join, restore. Directly reused for D-02 lazy footnote-body render.
- **GATE-01 render-gate class pattern** (`tests/test_pdf_render_gate.py`): copy a
  `Test*RenderGate` class → `TestFootnoteRenderGate` exercising single-ref, double-ref, and
  footnote-inside-a-list-item (SC#4), asserting body text present exactly once + no source leak.

### Established Patterns / Constraints
- **Unified code-mode:** `visit_document` emits `#{` — all output is code-mode. Any markup-mode
  construct (label attachment, `footnote[...]`) must be emitted compile-safe, per the Phase 11
  bracket-wrap precedent. This is the main implementation hazard (see research flag above).
- **Graceful-degrade net:** prefer `logger.warning` + skip over a fatal (D-08).

### Integration Points
- **Greenfield:** no `visit_footnote` / `visit_footnote_reference` handlers exist today — this
  phase adds them plus the `visit_document` index step. No existing handler is modified except the
  index-build insertion at the top of `visit_document`.

</code_context>

<specifics>
## Specific Ideas

- Notes render **inline at the reference site**, never at the docutils definition location.
- A footnote cited twice: marker at both sites, body emitted once via `<fn-{id}>` label; the second
  citation is `footnote(<fn-{id}>)`.
- Body sourced via buffer-swap (inline `emph`/`literal` + markup-special chars must survive) —
  never `astext()`.
- GATE-01 fixture must cover: single-reference, double-reference, and footnote-inside-a-list-item.

</specifics>

<deferred>
## Deferred Ideas

- **`citation` / `citation_reference` node support** — same footnote-family plumbing but a distinct
  requirement; out of FN-01 scope. Note for a future phase / backlog.

</deferred>

---

*Phase: 14-footnotes-doctree-pre-pass*
*Context gathered: 2026-07-12*
