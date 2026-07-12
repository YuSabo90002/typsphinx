# Phase 13: Shared Dispatch-Point Changes (topic + line blocks) - Context

**Gathered:** 2026-07-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Generalize the load-bearing `visit_title` dispatch in `typsphinx/translator.py` so that a
`.. topic::` title renders as a titled inline aside (not a numbered section heading), and add
`line` / `line_block` handlers that preserve verbatim line breaks. Because `visit_title` is a
shared, regression-heavy method that every admonition and section heading already depends on,
this lands as one phase that also ships regression fixtures for the existing admonition titles
(the Phase 8.1 behavior). Requirements: **BLK-02** (topic aside) and **BLK-03** (line/line_block
breaks) only.

All work is confined to `translator.py` + fixture dirs + the existing real-compile gate
(`tests/test_pdf_render_gate.py`). Zero new runtime dependencies; the 3-way `@preview`
version-sync surface (writer.py / template_engine.py / templates/base.typ) is untouched. Scope is
HOW to implement this fixed node set — new node *capabilities* beyond topic/line_block belong to
Phases 14–15. The empirical bar is a real `typst.compile()` outcome (GATE-01 standing pattern),
never string-agreement asserts alone.

</domain>

<decisions>
## Implementation Decisions

**Discussion mode:** interactive — user selected all four gray areas and accepted the recommended
default for each. Each decision below is locked.

### topic rendering (BLK-02)
- **D-01: Reuse the admonition helper — `_visit_admonition(node, "clue")`.** A `.. topic::`
  renders as a gentle-clues base `clue` box (no icon, no accent color) with its title as the bold
  box title. This is the literal reading of REQ BLK-02 ("reusing the admonition helper") and also
  satisfies ROADMAP SC#1 ("titled aside … bold inline label … not a numbered heading … TOC
  structure unchanged"): the `clue` box is unboxed-of-semantics/neutral, its title is bold, and
  because it never calls `heading()` the document's heading/TOC structure is unaffected.
- **D-02: Generalize `visit_title`'s buffer-swap condition to include `topic` parents.** Today the
  title buffer-swap branch (translator.py:224) fires only for `isinstance(node.parent,
  nodes.Admonition)`. Extend the condition so a `topic` parent also buffer-swaps its title through
  the normal inline visitors and defers it to `_depart_admonition` as the box `title:` argument.
  `visit_topic`/`depart_topic` then just call `_visit_admonition(node, "clue")` /
  `_depart_admonition()`. This is the core "shared dispatch-point generalization" of the phase.
  (Rejected the box-less lightweight-block alternative — it requires net-new machinery for no
  visual gain over the neutral `clue` box.)

### line / line_block (BLK-03)
- **D-03: Preserve line breaks via `linebreak()` AND reproduce nested indentation (simple).**
  Every `line` inside a `line_block` ends with a `linebreak()`; a nested `line_block` (poetry
  stanza / multi-level address) adds a fixed indent per nesting depth so the structural
  indentation survives — not just the breaks. SC#2 only mandates breaks, so the indentation is the
  chosen default beyond the minimum, because an address/stanza without indentation loses its
  meaning. (Rejected breaks-only/flatten — cheaper but drops the structure line_block exists to
  carry.)
- **D-04: Keep the indent compile-safe.** Any indentation mechanism (e.g. `pad`/`h`) must be
  emitted so it compiles — if it needs markup-mode content, bracket-wrap it exactly like the
  Phase 11 title/figure label fix rather than emitting a code-mode construct that aborts. The
  poetry fixture must prove a nested `line_block` compiles. If a chosen indent construct ever risks
  a fatal that can't be made safe cheaply, fall back to breaks-only (D-03's floor) rather than ship
  a fatal.

### `.. contents::` (local TOC — also a `topic` node)
- **D-05: contents-topic renders box-less as pass-through.** `.. contents::` parses to a `topic`
  node carrying the `'contents'` class and a child `bullet_list` of internal links (Sphinx has
  already resolved the local TOC). Detect `'contents' in node.get("classes", [])` in `visit_topic`
  and, for that case, do NOT wrap in the `clue` box: emit the title as a bold label and let the
  child `bullet_list` render normally through the existing list visitors. This avoids a boxed table
  of contents and avoids the level-0 heading fatal. The title is still buffer-swapped (so it never
  falls to the `else` heading branch); it is just placed as a plain bold label above the list
  rather than as a box `title:`. (Rejected: routing contents through the same `clue` box — a boxed
  TOC is wrong; and full-skip — dropping a local TOC the author asked for.)

### shared-dispatch reach (`visit_title`)
- **D-06: Handle topic/contents explicitly + add a `max(1, section_level)` clamp to the `else`
  branch.** The `else` branch of `visit_title` currently emits `heading(level: self.section_level,
  …)`; a top-level titled non-section (a top-level `topic`, or an out-of-scope `sidebar`) hits
  `section_level == 0` → `heading(level: 0, …)`, which Typst rejects (levels are ≥ 1) — a latent
  fatal at the load-bearing method. Clamp the emitted level to `max(1, self.section_level)` so no
  title can ever emit a level-0 heading, regardless of node type. This is a pure safety net that
  directly serves the milestone's no-fatal bar. Do NOT add sidebar-specific rendering — sidebar is
  out of scope (not in BLK-02/03); the clamp merely prevents its title from being fatal if one
  appears in the real corpus. (Rejected strict-scope-only — it leaves a known level-0 fatal class
  live at the exact method this phase is already editing.)

### Claude's Discretion
- Exact indent unit/mechanism for nested `line_block` (D-03/D-04) — e.g. `#h(1.5em)` per depth vs
  `pad(left: …)` — planner/executor's call, subject to the compile-safety constraint.
- Exact punctuation/spacing/label styling for the box-less contents-topic bold label (D-05).
- Whether `visit_topic` sets a small instance flag to distinguish the contents-topic (box-less)
  path from the generic-topic (clue box) path, or branches inline — implementation detail.
- Fixture document contents beyond the explicit success-criteria cases (topic, address/epigraph/
  poetry-stanza line_block, `.. note::`/`.. warning::` regression).
- Exact `line`-node emptiness handling (a blank line in a `line_block` is an empty `line` node) —
  render as a bare `linebreak()`/`#v()`; executor's call, proven by the fixture.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — BLK-02 (`.. topic::` → titled aside reusing the admonition helper)
  and BLK-03 (`line`/`line_block` → verbatim line breaks via `linebreak()`); per-phase mapping line
  at the bottom (Phase 13 = BLK-02, BLK-03).
- `.planning/ROADMAP.md` §"Phase 13: Shared Dispatch-Point Changes (topic + line blocks)" — the
  four Success Criteria (topic titled-aside not-heading + unchanged TOC; line_block breaks
  preserved; admonition-title regression still passes; real-compile fixture covering all three).

### Prior-phase context that constrains this phase
- `.planning/phases/12-high-volume-independent-node-handlers/12-CONTEXT.md` — the immediately-prior
  decisions (VER-01 classed-inline dispatch, XREF-01 refid link contract, trivial-node idioms) and
  the "minimal machinery / reuse proven patterns" ethos this phase continues.
- `.planning/STATE.md` §"Accumulated Context" — the standing GATE-01 bar and the "one bad node
  aborts the ENTIRE PDF" blocker that makes the D-06 level clamp and D-04 compile-safety mandatory.

### Code anchors (load-bearing — read before editing)
- `typsphinx/translator.py:206` `visit_title` / `:248` `depart_title` — the shared dispatch to
  generalize (admonition buffer-swap branch :224; section-anchor branch :239–:283; the `else`
  heading branch to clamp).
- `typsphinx/translator.py:2470` `_visit_admonition` / `:2501` `_depart_admonition` — the helper
  BLK-02 reuses; note the code-mode `{...}` title-wrap contract and `title:` argument mechanism.
- `typsphinx/translator.py:2216` `unknown_visit` — where `line`/`line_block` are currently dropped
  (no handlers today).
- `tests/test_pdf_render_gate.py` — the GATE-01 real-compile acceptance harness (`sphinx-build →
  typst.compile() → pypdf` with negative-control leak signatures) that the Phase 13 fixture
  extends.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_visit_admonition(node, clue_type, custom_title=None)` / `_depart_admonition()`
  (translator.py:2470/2501): the exact helper BLK-02 reuses for the topic box (`clue_type="clue"`).
  Already handles the code-mode content-block open/close and the buffered-title `title:` argument.
- The admonition-title buffer-swap in `visit_title`/`depart_title` (`_saved_body_for_admonition_title`,
  `_pending_admonition_title`, `_in_admonition_title`, lines 224–228 / 260–266): the mechanism to
  extend to `topic` parents (D-02) rather than reinvent.
- The Phase 11 markup bracket-wrap idiom for anything that must carry a `<label>` or compile in
  markup mode (title anchors at :243/:276, figure captions): the template for D-04 compile-safe
  indentation.
- Existing list visitors (`visit_bullet_list`/`visit_definition_list`, e.g. :1070): render the
  contents-topic child `bullet_list` as-is (D-05 pass-through).

### Established Patterns
- **Classed dispatch by parent/class** — Phase 12's `visit_inline` keys behavior off
  `node.get("classes", [])` (versionmodified). D-05 reuses the same idiom to detect the
  `'contents'` topic.
- **Emit in code mode; bracket-wrap only when markup is required** — the translator runs in a
  unified code mode; every new emission (`linebreak()`, indent, box) must respect that, and
  anything needing markup (labels, some layout) is bracket-wrapped (Phase 11 lesson).
- **Real-compile gate over string asserts** — GATE-01: every handler group ships or extends a
  `typst.compile()` fixture; string agreement alone never suffices.

### Integration Points
- `visit_title` is the single shared dispatch point touched by D-02 (topic branch) and D-06 (level
  clamp); admonition + section-heading behavior MUST remain byte-identical for the regression
  fixture to pass.
- New `visit_topic`/`depart_topic`, `visit_line`/`depart_line`, `visit_line_block`/
  `depart_line_block` methods slot into the translator's existing visitor family.
- The Phase 13 fixture extends `tests/test_pdf_render_gate.py` (new fixture doc + test class)
  covering topic + line_block + the admonition-title regression together.

</code_context>

<specifics>
## Specific Ideas

- topic box = gentle-clues base `clue` (neutral, no icon/accent) — the same function the generic
  `.. admonition::` directive already uses (translator.py:2628), keeping topic visually consistent
  with the admonition family.
- line_block fixture should cover all three SC#2 shapes explicitly: an address, an epigraph, and a
  poetry stanza (the poetry stanza being the nested-indentation case that exercises D-03/D-04).
- Regression fixture must include at least `.. note::` and `.. warning::` titles (the Phase 8.1
  behavior) to prove the `visit_title` generalization did not disturb admonition titles.

</specifics>

<deferred>
## Deferred Ideas

- **Sidebar (`.. sidebar::`) full rendering** — shares the `visit_title` dispatch but is out of
  scope (not in BLK-02/03). D-06's level clamp prevents its title from being a fatal if it appears,
  but proper sidebar styling is a future item, not this phase.
- **Native Typst `#outline()` for local TOCs** — D-05 renders `.. contents::` as the Sphinx-resolved
  `bullet_list` pass-through; swapping to a Typst-native outline is a possible future refinement,
  out of scope here.

</deferred>

---

*Phase: 13-Shared Dispatch-Point Changes (topic + line blocks)*
*Context gathered: 2026-07-12*
