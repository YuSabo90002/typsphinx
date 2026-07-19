# Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor - Context

**Gathered:** 2026-07-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Render the last two node types the v0.6.0 warning audit confirmed are still silently
`unknown_visit`-dropped in the Sphinx corpus, and generalize v0.6.0's `visit_image`-local px→pt
length conversion into a single shared helper reused at every length-bearing site. All changes live
in `typsphinx/translator.py` (+ fixture dirs + the existing real-compile gate). Concretely:

- **TODO-01** — `.. todo::` (`todo_node`, ×10 in the corpus) renders its body as an admonition-style
  box instead of being silently dropped.
- **MAN-01** — `:manpage:` (`manpage` node, ×10) renders its literal page reference (e.g. `ls(1)`)
  instead of being silently dropped.
- **LEN-01** — the CSS-length → Typst-length conversion (`_convert_length_to_typst`, introduced in
  v0.6.0) is confirmed as the single shared helper and wired into **every** length-bearing site, not
  just `visit_image`.

First phase of milestone v0.6.1. All three items are independent, additive, low-risk translator
changes that do NOT depend on the later fidelity audit (Phase 17). Scope is HOW to implement this
fixed set — new node *capabilities* beyond it belong to Phases 17–18. Milestone invariants hold:
zero new runtime dependencies; the 3-way `@preview` version-sync surface (`writer.py` /
`template_engine.py` / `templates/base.typ`) stays untouched; every handler ships or extends a real
`typst.compile()` acceptance fixture (GATE-01 pattern) — string-agreement asserts alone never
suffice.

</domain>

<decisions>
## Implementation Decisions

### todo_node (TODO-01)
- **D-01: Box via the admonition helper as `task` + title "Todo".** Reuse the existing
  `_visit_admonition(node, "task", custom_title="Todo")` / `_depart_admonition()` pair
  (translator.py:3643). `task` is the closest semantic gentle-clues clue for a "to-be-done work
  item"; the title `"Todo"` matches Sphinx's own HTML admonition heading. The todo body (child
  paragraphs/lists) flows through the normal chain, exactly like `note`/`warning`.
- **D-01a: Fallback if `task` is absent.** gentle-clues 1.3.1 must actually expose a `task` clue
  function. The researcher MUST verify this against the bundled gentle-clues version; if `task` is
  not a valid clue, fall back to the base `clue` function with `custom_title="Todo"` (same treatment
  as generic `.. admonition::`, translator.py:3796). Do not invent a new package or bump the version.
- **D-01b: `todolist` is out of scope.** Only `todo_node` is in scope (the requirement and the
  corpus drop are `todo_node` ×10). The `todolist` aggregation node is NOT handled in this phase.

### manpage (MAN-01)
- **D-02: Render as `emph` (italic), Sphinx-HTML-faithful.** Emit `#emph[` on visit, let the
  node's own `Text` child render `ls(1)` through the normal chain, emit `]` on depart. This matches
  Sphinx's HTML `<em class="manpage">` and LaTeX `\sphinxstyleliteralemphasis` (both italic).
  Chosen over the no-op passthrough (which loses the manpage distinction) and over `raw()`
  monospace (which diverges from Sphinx's italic rendering).
- **D-02a: No linkification.** `manpages_url`-based linking is a separate Sphinx feature and is out
  of scope — render the literal page-reference text only, per the requirement.

### CSS-length converter (LEN-01)
- **D-03: Proactive — audit and wire every length-bearing site (not image-only).** SC#3 explicitly
  requires the conversion "reused at every length-bearing site." The researcher audits every node
  that can carry a CSS-length attribute (`:width:`/`:height:` on image — already wired; `:figwidth:`
  on figure; `:width:` on `.. table::` / `.. csv-table::` / `.. list-table::`; any other
  length-normalized attribute docutils produces) and routes each through `_convert_length_to_typst`.
- **D-03a: Boundary between "fix" and "enable" — both are in scope, neither is scope creep.** For
  each audited site classify it:
  - *Currently emits a length to Typst but un-/mis-converted* → route through the shared helper (this
    is the original px→pt bug class the helper was created to prevent).
  - *Currently ignores the length entirely* (e.g. figure `:figwidth:`, table `:width:` are not
    presently passed to Typst at all) → wire it in through the shared helper. Because SC#3 mandates
    "every length-bearing site," this wiring IS the LEN-01 requirement, not a new capability —
    document it as such so the scope guard is not tripped during review.
- **D-03b: Single source of truth, no duplicated conversion.** After the refactor there must be
  exactly one conversion implementation (`_convert_length_to_typst`); no site may contain its own
  px→pt / pc→pt arithmetic. The unsupported-unit → drop-with-one-warning contract (D-02 from Phase
  11) is preserved at every wired site.

### Claude's Discretion
- Exact `emph`/wrapper punctuation and whitespace for `manpage`.
- The precise predicate/order for auditing length-bearing sites and the exact per-site wiring shape
  (planner/executor call), provided D-03b's single-source invariant holds.
- Fixture document contents beyond the explicit success-criteria cases (each of the three changes
  needs at least one real-compile fixture per SC#4).
- Exact `logger.warning` wording for any unsupported-unit drop at newly-wired sites.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — TODO-01, MAN-01, LEN-01 definitions and the per-phase mapping line.
- `.planning/ROADMAP.md` §"Phase 16" — the four Success Criteria (todo_node admonition-style;
  manpage literal text; single shared length helper at every site; real-compile fixture per change)
  and the milestone standing bar / invariants.

### Prior-phase decisions this phase reuses
- `.planning/phases/12-high-volume-independent-node-handlers/12-CONTEXT.md` — admonition-helper
  conventions (`_visit_admonition` reuse, gentle-clues clue mapping, `abbr` no-op-visit +
  depart-append pattern) that TODO-01/MAN-01 follow.
- `.planning/phases/11-issue-114-fatal-fixes-graceful-degrade-net/11-CONTEXT.md` — the D-02 length
  decision behind `_convert_length_to_typst` (px = 0.75pt, pc = 12pt, %/em/pt/cm/mm/in passthrough,
  unknown unit → drop + one warning) that LEN-01 generalizes.

### Code touch-points (all in `typsphinx/translator.py`)
- `_convert_length_to_typst` (line ~3009) — the shared helper LEN-01 generalizes.
- `visit_image` / width+height wiring (lines ~2472, ~2510) — current sole caller; the reference
  wiring pattern for other sites.
- `_visit_admonition` / `_depart_admonition` (lines ~3643, ~3808) — TODO-01 reuses these.
- `visit_abbreviation` / `depart_abbreviation` (lines ~4047) — the inline-node visit/depart shape
  MAN-01's `emph` handler mirrors.
- `visit_figure` / `depart_figure` (lines ~1868, ~1899) — a candidate length-bearing site for the
  LEN-01 audit (figure `:figwidth:`).

### Test gate
- `tests/test_pdf_render_gate.py` / `tests/test_corpus_gate.py` — the GATE-01 real-`typst.compile()`
  acceptance pattern every change in this phase must ship or extend (SC#4).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_visit_admonition(node, clue_type, custom_title=...)` + `_depart_admonition()`: box-rendering
  machinery for TODO-01; title flows through the admonition-aware `visit_title`/`depart_title`
  buffer-swap automatically.
- `_convert_length_to_typst(value)`: already a method (not inline), already implements the full
  px/pc/passthrough/unknown-drop logic — LEN-01 is largely audit + wire-in, not a rewrite.
- `visit_abbreviation`/`depart_abbreviation`: the template for a lightweight inline node whose Text
  child carries the visible content (MAN-01's `emph` wrapper is the same shape with `#emph[`…`]`).

### Established Patterns
- Inline nodes wrap in `#func[` on visit and `]` on depart, letting the Text child render normally
  through `visit_Text` (inherits the string-escaping regime) — MAN-01 follows this.
- Length attributes are converted at emit time via the shared helper and dropped (attribute omitted)
  when the unit is unsupported, rather than emitted verbatim (which was the FIG-01 fatal case).
- Every node-handler phase ships/extends a real `typst.compile()` fixture; local env can run real
  compiles (typst 0.15.0 present; corpus cached at `~/.cache/typsphinx-corpus-gate`).

### Integration Points
- New `visit_todo_node`/`depart_todo_node` and `visit_manpage`/`depart_manpage` methods register via
  docutils' visitor dispatch (PascalCase not required for these snake_case node names).
- LEN-01 wiring connects the audited length-bearing visitors to the existing `_convert_length_to_typst`.

</code_context>

<specifics>
## Specific Ideas

- `manpage` example content to render: `ls(1)` (from ROADMAP SC#2) — italic per D-02.
- todo box heading text: literally `"Todo"` (matches Sphinx HTML).

</specifics>

<deferred>
## Deferred Ideas

- `todolist` node handling (the `.. todolist::` aggregation directive) — out of scope for Phase 16;
  candidate for a future fidelity phase if the corpus needs it.
- `manpages_url`-based linkification of `:manpage:` references — separate Sphinx feature, out of
  scope.

None of the above are blockers; captured so they are not lost.

</deferred>

---

*Phase: 16-silent-drop-node-handlers-length-converter-refactor*
*Context gathered: 2026-07-13*
