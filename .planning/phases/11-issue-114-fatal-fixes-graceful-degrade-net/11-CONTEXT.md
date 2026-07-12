# Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net - Context

**Gathered:** 2026-07-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix the two Issue #114 fatal Typst-compile bugs and add a graceful-degrade net for
graphical out-of-scope nodes, entirely within `typsphinx/translator.py`. Concretely:

- **FIG-01** — CSS/px length-unit conversion on `.. figure::`/image `:width:`/`:height:`.
- **FIG-02** — `:target:`-linked figure/image caption buffer-swap fix (no stray juxtaposed `text(...)`).
- **DEG-01 / DEG-02** — `graphviz` / `inheritance_diagram` degrade without aborting the compile.
- **GATE-01** — stand up the standing real-compile acceptance-gate pattern
  (`sphinx-build → typst.compile() → pypdf`) that every downstream node-handler phase extends.

This is the **first, blocking** phase of milestone v0.6.0: a single fatal node aborts the entire
PDF, so no later phase can be validated against a real compile until this lands. Zero new runtime
dependencies; the 3-way `@preview` version-sync surface (writer.py / template_engine.py /
templates/base.typ) is untouched. Scope is HOW to implement FIG/DEG/GATE — new node *capabilities*
beyond this set belong to Phases 12–15.

</domain>

<decisions>
## Implementation Decisions

### Graceful degradation (DEG-01 / DEG-02)
- **D-01:** `graphviz` and `inheritance_diagram` render a **visible placeholder block** in the PDF
  (a bordered/boxed block naming the node, e.g. `[graphviz diagram omitted]`) **plus exactly one**
  `logger.warning` naming the node type. This honors REQ DEG-01's literal "visible placeholder
  block" wording — the reader must be able to tell a diagram was there — and is stronger than the
  roadmap SC#3 "warning + no-leak" minimum. Do **not** reuse the gentle-clues warning box (avoids
  visual confusion with real admonitions), and do **not** silently skip. No raw DOT / diagram
  source may leak into the output. DEG-01 and DEG-02 share one helper.

### Length-unit conversion (FIG-01)
- **D-02:** Unit handling on image `:width:`/`:height:`:
  - `px` → `pt` via the CSS-canonical `1px = 0.75pt`.
  - **Bare unitless numbers are treated as `px`** (HTML/CSS convention) → `× 0.75pt`.
  - `%`, `em`, `pt`, `cm`, `mm`, `in` pass through as valid Typst lengths.
  - `pc` → convert to `pt`.
  - **Unknown / unconvertible units** (incl. `ex`) → emit **one** `logger.warning` and **drop the
    `width`/`height` dimension entirely** (image renders at natural size). Never emit a raw
    unsupported unit like `width: 200px` — that is the FIG-01 fatal case.
  - Centralize in a single `_convert_length_to_typst()` helper used by `visit_image`.

### `:target:` figure/image coverage (FIG-02)
- **D-03:** Support **both** external-URL targets (`link("url")[...]`) **and** internal
  reference / doc targets (`link(<label>)[...]`) in this phase — not just the external-URL Issue #114
  reproduction. Same buffer-swap code path handles both by branching on refuri vs refid; added cost
  is small and Sphinx's own `doc/` tree (the milestone corpus) uses internal `:target:` references
  heavily. Emit valid `#figure(link(...)[#image(...)], caption: [...])`; the caption reaches the
  `caption:` named argument via buffer-swap and never leaks as a stray juxtaposed `text(...)`.

### Acceptance gate (GATE-01)
- **D-04:** Extend the existing `tests/test_pdf_render_gate.py` (the v0.5.0 admonition D-04 gate:
  `sphinx-build → typst.compile() → pypdf` text-extraction with negative-control leak signatures).
  Keep the `slow` marker so local runs stay fast, but the gate **runs in CI's `cov` job where
  typst-py/pypdf are present** — i.e. it is **effectively required**: it must not `skip` in CI and
  fails loudly on any `TypstCompilationError`. This matches the milestone thesis that
  string-agreement unit tests alone are insufficient (pitfall #9). This gate is the standing bar
  every later node-handler phase (12–14) extends.

### Claude's Discretion
- Exact placeholder-block styling (border, padding, wording) — reader must recognize an omitted
  diagram; precise Typst styling is the planner/executor's call.
- Exact `logger.warning` message text (must name the node type).
- Internal structure of `_convert_length_to_typst()` and the DEG shared helper.
- Fixture document contents beyond the explicit success-criteria cases below.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` §"Figure/Image — Issue #114 fatal bugs", §"Graceful degradation",
  §"Validation gate" — FIG-01, FIG-02, DEG-01, DEG-02, GATE-01 definitions.
- `.planning/ROADMAP.md` §"Phase 11" — the four Success Criteria (px/units incl. `50%`/`3em`/
  unitless/`2in`; caption with `_ * `` ` `` [ ]`; graphviz + inheritance_diagram; the render gate).

### Research (implementation-grounding)
- `.planning/research/SUMMARY.md` — zero-new-deps thesis; Phase-1 delivers section; the 10 pitfalls
  (esp. #1 one-bad-node-aborts, #3 caption double-emission, #4 juxtaposition, #5 px≠1:1,
  #9 string-tests-prove-nothing, #10 graceful-degrade-done-wrong).
- `.planning/research/PITFALLS.md`, `.planning/research/ARCHITECTURE.md` — buffer-swap /
  `_has_content` flag / `SkipNode` patterns to reuse.

### Code touchpoints (current, buggy state)
- `typsphinx/translator.py:1201` `visit_caption` / `:1217` `depart_caption` — currently uses
  `node.astext()`; must become buffer-swap (source of the FIG-02 double-emission).
- `typsphinx/translator.py:1163` `visit_figure` / `:1179` `depart_figure` — figure assembly + caption.
- `typsphinx/translator.py:1501` `visit_image` (`:1527`–`:1533` emit `width`/`height` verbatim — the
  FIG-01 fatal path).
- `typsphinx/translator.py:1548` `visit_target` / reference handling — for FIG-02 `:target:` link
  wrapping (external `refuri` vs internal `refid`).
- `graphviz` / `inheritance_diagram` — **no handlers exist today**; they fall through to
  `unknown_visit`. New explicit `visit_*` overrides needed.
- `tests/test_pdf_render_gate.py` — the gate to extend (GATE-01).
- `.github/workflows/docs.yml` (runs `tox -e docs-pdf`) and `tox.ini` `[testenv:docs-pdf]` /
  `[testenv:cov]` — CI surfaces where the real compile already runs.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Admonition title buffer-swap** (v0.5.0 Phase 8.1, `visit_title`/`_visit_admonition`) — the exact
  buffer-swap precedent for the FIG-02 caption fix (render caption through the normal visitor chain
  into a deferred buffer, never `astext()`).
- **`_link_has_content` / `_desc_parameter_has_content` flags** (translator.py ~`:80`, `:499`) — the
  established juxtaposition-guard pattern; reuse the idea so `image(...)` + caption never sit as bare
  adjacent expressions.
- **`tests/test_pdf_render_gate.py`** — real-compile gate scaffold (typst-py + pypdf, `slow`-marked,
  negative-control leak tokens) — extend rather than reinvent for GATE-01.
- **`raise nodes.SkipNode`** — used throughout (comment/raw/target); the clean primitive for
  DEG-01/02 after emitting the placeholder + single warning.

### Established Patterns
- **Code-mode emission** — translator emits Typst function calls without `#` prefix; expressions must
  be separated by `+`/`;`/newline or wrapped in a named arg (`caption:`) — the juxtaposition rule
  that FIG-02 must respect.
- **`self.in_figure` / `self.figure_caption` state** already threads figure assembly; the caption
  buffer-swap plugs into this existing state rather than adding parallel machinery.

### Integration Points
- All changes land in `typsphinx/translator.py` (+ a fixture dir + `tests/test_pdf_render_gate.py`).
  No edits to `writer.py`, `builder.py`, `template_engine.py`, `templates/base.typ`, or the
  `@preview` version-sync surface.

</code_context>

<specifics>
## Specific Ideas

- Placeholder wording in the spirit of `[graphviz diagram omitted]` — reader-legible, node-named.
- Caption stress fixture must include markup-special chars `_ * ` `` ` `` ` [ ]` and assert the
  caption text appears **exactly once** (pypdf extraction), guarding against the double-emission leak.
- Length fixtures must cover: `200px`, `50%`, `3em`, a bare unitless number, `2in`, and at least one
  unknown/unconvertible unit that must warn-and-drop.

</specifics>

<deferred>
## Deferred Ideas

- **Real `graphviz` / `inheritance_diagram` rendering** (shell out to `dot`, image negotiation) —
  explicitly Out of Scope this milestone; placeholder-only here.
- **LEN-01** — generalizing the length converter beyond the named units (legacy unitless HTML widths
  beyond the px assumption, additional exotic units) — Future Requirement, trigger = next non-`px`
  length-unit fatal report.
- Node handlers VER-01 / XREF-01 / DESC-* / BLK-* / FN-01 — Phases 12–14, not here.

None raised outside phase scope during discussion.

</deferred>

---

*Phase: 11-Issue #114 Fatal Fixes + Graceful-Degrade Net*
*Context gathered: 2026-07-11*
