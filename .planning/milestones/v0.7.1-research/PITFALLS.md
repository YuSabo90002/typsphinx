# Pitfalls Research — v0.7.0 API Rendering Design Overhaul

**Domain:** Sphinx→Typst translator redesign (desc_*/field_list/admonition/rubric/topic
representation overhaul + new bundled Typst style module + greenfield citation support)
**Researched:** 2026-07-29
**Confidence:** HIGH — every pitfall below is either (a) a previously-shipped, artifact-cited defect
in *this* translator, or (b) derived directly from reading the current `translator.py`/`writer.py`/
`builder.py` implementation, not generic Typst/Sphinx advice.

## Critical Pitfalls

### Pitfall 1: Code-mode juxtaposition — the recurring "expected semicolon or line break" fatal

**What goes wrong:**
`translator.py` emits the entire document body inside one Typst code-mode block (`#{ ... }`,
`writer.py:138-141`). In code mode, two adjacent expressions with nothing between them
(`text("a")text("b")`, `strong({...})par({...})`) are a Typst parse error. A source `"\n"` or
`"\n\n"` between two code-mode statements is **cosmetic only** — it satisfies the parser (a real
line break IS a statement terminator) but produces **zero visual break** in the rendered PDF,
because the two resulting values still concatenate as adjacent inline content. Every new visitor
this milestone adds (signature wrapper, hanging-indent body, aligned field grid, citation list) sits
squarely in this hazard: it juxtaposes against whatever sibling came before/after it unless it
explicitly participates in the separator protocol.

**Why it happens:**
The translator has **three interacting separator protocols**, and a new handler that reuses only
one (by pattern-matching the nearest existing handler without reading `_emit_forced_break`'s and
`_add_paragraph_separator`'s docstrings) silently drops the others. This has happened repeatedly:

- **v0.6.0 GATE-02 fatals** (`.planning/PROJECT.md` Phase 11/14 entries): figure/image `:target:`
  buffer-swap and footnote-reference buffer-swap both discovered by the real-compile gate, not by
  code review — MILESTONES.md v0.6.0: *"a third, previously-hidden fatal Typst-compile bug (labels
  attached to code-mode statements are invalid Typst syntax)."*
- **v0.6.1 FID-01a** (wide-table margin clip) — a *layout* instance of the same class: `visit_literal`
  (`translator.py:1282-1360`) had to inject U+200B zero-width-space break opportunities because
  Typst's line-breaker (UAX14 rule LB13) refuses to break before a leading `:;,)]}!?` character even
  when preceded by real breakable `text(" ")` content.
- **v0.6.2 clusters A–F / FID-02..FID-14** (MILESTONES.md v0.6.2): adjacent-sibling concatenation —
  paragraphs-in-list-items, sibling `desc_signature`s, rubric/option headings, definition-list
  term↔definition, back-to-back body-less `confval`s — all fixed via `parbreak()`/`linebreak()`/
  `terms(separator:)`, i.e. the `_emit_forced_break` idiom.
- **v0.6.5 MATH-01** (`STATE.md`/PROJECT.md v0.6.5 entry): the most recent, most on-point instance.
  `visit_math` called `_add_paragraph_separator()` (protocol 1) but never checked
  `list_item_needs_separator` (protocol 3) or the code-mode concat helpers (protocol 2), so inline
  math after text inside a list item / field body / def-list term aborted the compile. **The premise
  going into that milestone was wrong** — it was scoped as "visit ordering," and the measured root
  cause was "scope gap: participates in only one of three separator protocols." The v0.7.0 redesign
  is exactly the kind of broad, many-new-handler change that reproduces this class at scale unless
  every new visitor is checked against all three protocols explicitly, not by analogy to one
  neighboring handler.

**How to avoid:**
See the dedicated **Separator Protocol Checklist** section below — treat it as a per-handler
pre-commit gate, not background knowledge. In short: every new `visit_*`/`depart_*` this milestone
adds must be checked against (1) the paragraph protocol, (2) the code-mode inline-concat protocol
(5 named contexts), and (3) the list-item protocol — independently, because a node can appear in any
combination of these three contexts and the existing code has no single dispatcher that does this
for you.

**Warning signs:**
- A new handler emits inline content via `self.add_text(...)`/`self.body.append(...)` without first
  calling `_add_paragraph_separator()` or checking `in_list_item`/`list_item_needs_separator`.
- A new BLOCK-level handler (signature wrapper, field grid, citation entry) never calls
  `_emit_forced_break()` and instead writes a literal `"\n"` or `"\n\n"` hoping it will visually
  separate from the next sibling.
- The GATE-01 fixture only exercises the node at the top level of a document, never inside a list
  item, field body, or definition-list term — this is precisely the blind spot that let MATH-01 ship
  in three separate v0.6.x releases before being caught.

**Phase to address:**
Every phase that adds or rewrites a `visit_*`/`depart_*` pair (desc_* redesign, field_list redesign,
admonition/rubric/topic redesign, citation implementation). This is not a one-time fix — it is a
per-handler discipline that must be re-applied in every phase of this milestone.

---

### Pitfall 2: Buffer-swap clobbers separator state, not just body content

**What goes wrong:**
Several existing handlers (`visit_title`/`depart_title` for admonition/topic/table-caption titles,
`visit_caption`/`depart_caption` for figure captions, `visit_footnote_reference`) temporarily
redirect `self.body` to an empty list, walk children through the normal visitor chain to capture
rendered output, then restore `self.body`. If only `self.body` is swapped and restored — not the
surrounding `in_paragraph`/`paragraph_has_content` (and, where applicable,
`in_list_item`/`list_item_needs_separator`) state — a nested `paragraph` child inside the swapped
region unconditionally resets those flags on its own `depart_paragraph`, silently clobbering the
**outer** paragraph's separator bookkeeping. The next sibling after the swap then loses its needed
separator and the compile aborts.

**Why it happens:**
`self.body` is one of many pieces of translator state that all move together conceptually (a
"rendering context"), but the buffer-swap idiom as first written only swapped the piece that was
visibly necessary (the output buffer) and missed the others. This is not hypothetical — it already
shipped and was caught only by the real-compile gate:

> MILESTONES.md v0.6.0, Phase 14: *"the real `typst.compile()` acceptance fixture ... caught and
> fixed a genuine paragraph-state-clobbering bug in `visit_footnote_reference`'s buffer-swap that
> would have made every realistic footnote citation a fatal compile abort."*

The current `visit_footnote_reference` implementation (`translator.py:2371-2393`) is the record of
the fix — it explicitly saves/restores `was_in_paragraph`/`was_paragraph_has_content` around the
nested `child.walkabout(self)` loop, with a comment naming this exact failure mode. `CONCERNS.md`
also names this as a standing fragile area: *"A forgotten `restore()` leaves downstream content in
the wrong buffer ... Separator state (`paragraph_has_content`, `list_item_has_content`) must be
saved/restored across swaps or subsequent elements lose their spacing."* Only ~5 of ~20 buffer-swap
sites in the codebase have real-compile regression coverage (CONCERNS.md, "Test Coverage Gaps").

**How to avoid:**
Any new buffer-swap this milestone introduces (candidates: a signature's monospace-name segment
captured separately from its parameter list for column alignment; a field-list value captured for
grid-cell placement; a citation body captured for the bibliography list entry) MUST save/restore, at
minimum:
- `self.body` (the obvious one)
- `self.in_paragraph` / `self.paragraph_has_content`
- If the swap can occur inside a list item: `self.in_list_item` / `self.list_item_needs_separator`
  (mirror `visit_title`'s `_title_was_in_list_item`/`_title_was_list_item_needs_separator` pattern,
  `translator.py:531-534` and `618-619`)
- If nesting is possible (a swap triggered from inside another swap), use a stack, not a single
  scalar slot — `_saved_body_stack`/`_deflist_items_stack`/`_pending_term_stack`
  (`translator.py:227-229`) is the established idiom for exactly this; a single slot gets overwritten
  by the inner swap and silently drops the outer content (this was GATE-02 fatal #18, cited in the
  code comment at `translator.py:220-226`).

**Warning signs:**
- A buffer-swap is written that captures `self.body` but the diff shows no corresponding
  save/restore of `in_paragraph`/`paragraph_has_content` nearby.
- The new swap can be entered from inside another swap (e.g., a citation body containing emphasis
  which itself might contain a footnote reference) and only a bare scalar (not a stack) holds the
  saved state.
- The GATE-01 fixture for the new construct never places trailing content (a sentence, another list
  item) immediately after the swapped element — this is exactly the shape that exposed the
  footnote-reference bug and the shape a naive fixture omits.

**Phase to address:**
Any phase introducing a new buffer-swap (most likely: the signature-wrapper phase, if column
alignment requires capturing rendered name/param sub-segments; the citation phase, since the
citation body must route through the normal visitor chain per the project's own stated non-negotiable
— "never `node.astext()`", see `visit_caption`'s docstring, `translator.py:2232-2236`).

---

### Pitfall 3: Label attachment rules — code-mode vs. markup-mode, and duplicate labels across the corpus

**What goes wrong:**
Typst's `<label>` postfix syntax is **markup-mode only**. Attaching it directly after a bare
code-mode statement (`block(...) <label>`, `grid(...) <label>`) inside this translator's unified
`#{ ... }` document wrapper is a parse error that aborts the *entire* compile, not just the one
element. Separately, Typst refuses to compile a document with two definitions of the same label name
("label ... occurs multiple times") — a **hard failure**, not a warning.

**Why it happens (and why it's already solved, if you follow the existing pattern):**
This was discovered as a real fatal during v0.6.0's Phase 11 GATE-01 development (MILESTONES.md:
*"discovering a third, previously-hidden fatal Typst-compile bug (labels attached to code-mode
statements are invalid Typst syntax)"*), and the fix that shipped is the pattern every current label
site uses: **never attach `<label>` as a postfix on a code-mode call**. Instead, either (a)
bracket-wrap the whole call in markup content (`[#figure(...) <label>]`, used by `visit_figure`,
`translator.py:2161-2165` / `2189-2191`; `visit_footnote_reference`'s definition branch,
`translator.py:2394`), or (b) emit a **separate, self-contained, zero-content markup statement**
`[#metadata(none) <label>]` immediately after the code-mode call closes
(`_emit_id_anchors`, `translator.py:331-402`; `depart_desc_signature`, `translator.py:4713-4722`;
`visit_rubric`'s `_emit_id_anchors(node)` call). Form (b) is what `desc_signature` currently uses —
the label is **not** literally attached to the `strong({...})` call; it is its own following
statement. This means **wrapping `desc_signature`'s content in `block(...)` or `grid(...)` does not
by itself break label attachment**, as long as the redesign keeps using form (b) rather than trying
to attach `<label>` directly onto the new wrapper call.

Every DEFINITION and REFERENCE site must also route the raw docutils id through both
`_namespace_label()` (`translator.py:3344-...`) and `_sanitize_label()`
(`translator.py:3287-3333`) — never write a raw id into a Typst label token by hand. Two reasons this
matters for the redesign specifically:
1. **Duplicate labels are real and already fatal in this corpus**: the whole multi-document tree
   flattens into one Typst master via `#include()`, but docutils ids are only unique *within* a
   document — `_namespace_label` exists specifically because two documents can carry the same
   section slug (`translator.py:3347-3353`). A citation implementation that mints label names from
   citation *keys* (e.g. `[Smith2020]`) without namespacing by docname will collide the instant two
   documents cite different works whose docutils-generated ids happen to match, or whose *bibliography
   keys* legitimately repeat across chapters.
2. **Invalid label characters abort the whole compile**: `_sanitize_label` exists because Sphinx ids
   can contain `@`, whitespace, and other characters Typst's `<...>` syntax rejects outright
   (`translator.py:3299-3304`, citing the real C-domain `@data`/`@alias` corpus fatal). A citation key
   containing punctuation (common in BibTeX-style keys, e.g. `Author:2020vw`) must go through this
   same helper, not be embedded raw.

**What breaks specifically if a signature is wrapped in `block(...)`/`grid(...)`:**
- **Safe, if the existing form-(b) anchor pattern is preserved**: emit `block(...)`/`grid(...)` as
  its own code-mode statement, then emit `\n[#metadata(none) <label>]\n` as a following, separate
  statement — exactly what `depart_desc_signature` already does after its `strong({...})` call.
- **Unsafe**: attempting `[#block(...) <label>]` where the wrapped content is a **grid cell**, not
  the top-level call — Typst attaches a label to the single value immediately preceding it, so a
  label meant for the whole signature accidentally binds to only the last grid cell's content if the
  postfix form is used carelessly inside a multi-cell `grid(...)` call. Form (b) — a wholly separate
  trailing statement — sidesteps this ambiguity entirely and should be preferred over any postfix
  form for wrapped signatures.
- **Unsafe**: if the redesign moves the id-anchor emission to happen *inside* a `grid()`/`block()`
  argument list (e.g., trying to anchor a specific cell), the anchor becomes just another
  comma-separated argument value rather than a markup postfix — `_emit_id_anchors`'s existing
  bracket-wrap technique does not compose with being nested inside another call's argument list
  without the same "separate trailing statement" treatment.

**Warning signs:**
- A diff introduces `<label>` directly following a `block(`/`grid(`/other new wrapper call with no
  intervening bracket-close.
- A new label-minting site (citation keys, signature aliases) builds the label string by
  f-string-concatenating the raw docutils id/citation key without a `_namespace_label`/
  `_sanitize_label` call.
- The GATE-01 fixture for the redesigned signature or citation only tests ONE signature/citation per
  document — duplicate-label collisions only surface with 2+ same-named or same-keyed entries, or
  2+ documents in a multi-doc corpus (mirror the existing
  `test_cross_doc_label_namespace_render_gate.py` and `test_duplicate_include_label_render_gate.py`
  patterns).

**Phase to address:**
The desc_* signature redesign phase (must preserve the existing anchor form when introducing the new
wrapper) and the citation phase (greenfield label-minting must reuse `_namespace_label`/
`_sanitize_label` from day one, not invent a parallel scheme).

---

### Pitfall 4: Layout traps specific to a real typographic design (page-breaking, indentation, overflow, color, CJK)

**What goes wrong (five related failure modes):**

1. **Page-breaking inside a signature or between signature and body.** Nothing in the current
   codebase sets Typst's `block(breakable: false)` anywhere — every existing `block()` call
   (`visit_figure`'s LEN-01 width wrapper, `translator.py:2160`) accepts Typst's *default*
   `breakable: true`. A monospace signature block is exactly the kind of content that looks broken
   if split mid-line across a page boundary (e.g. the parameter list wraps to the next page while the
   function name stays on the previous one). This is a genuinely new risk this milestone introduces
   — no prior phase had a multi-line, visually-cohesive block that mattered this much.
2. **Nested indentation accumulating unboundedly.** The one existing per-depth indent mechanism —
   `_line_block_depth` (`translator.py:254-262`, `4346-4390`) — is a single integer counter reset to
   0 only at depth-0 departure (`translator.py:4370-4371`), with an explicit code comment recording
   *why* a scalar (not a stack) suffices: docutils' own recursion provides the stack. A `desc`
   nesting counter for class→method→nested-function API pages needs the **same discipline**: reset
   at the outermost `desc`, incremented per nested `desc`, and — critically — **must not leak across
   sibling top-level `desc` nodes** (a module-level function following a deeply nested class must not
   inherit the class's leftover indent). `desc` nodes can also nest through non-`desc` intermediaries
   (a `desc_content` containing a `field_list` containing further prose before a nested `desc`) — the
   depth counter must be driven by `desc`/`desc_content` visit/depart specifically, not by generic
   block nesting, or indentation will accumulate on wrong siblings.
3. **Long monospace signatures overflowing the right margin.** The project already hit and fixed the
   width-analog of this problem once: v0.6.1 FID-01a (wide-table glyph collision) fixed via two
   independent techniques — `depart_table` emitting `fr`-weighted `columns: (Nfr, ...)` from docutils
   colwidth (`translator.py` `depart_table`), and `visit_literal` injecting U+200B after `.`/`_` in
   in-table `raw()` content (`translator.py:1308-1320`) because Typst's UAX14 line-breaker (rule
   LB13) refuses a break before a leading `:;,)]}!?` character even after real breakable space
   (`translator.py:1321-1341`, FID-10). **This generalizes but does not transfer automatically**: the
   U+200B injection is currently gated on `self.in_table` (width-constrained cell) OR a specific
   leading-punctuation heuristic — a monospace signature is a *different* width-constrained context
   (the page's text width, not a table cell) with different overflow characters (long
   dotted-namespace Python signatures like `typsphinx.template_engine.TemplateEngine.__init__`, or
   C++ template signatures with many `<`/`,`/`::` tokens). The fix must be re-derived for this new
   context, not assumed to already apply — `_convert_length_to_typst`'s CSS-length helper
   (CONCERNS.md) also silently drops unsupported units, which is a separate overflow-adjacent trap if
   the redesign tries to size the signature block from any docutils-supplied width hint.
4. **Colour choices failing in greyscale.** The bundled `gentle-clues` admonitions (`info`/`warning`/
   `tip`/`error`/`danger`/`task`) already carry colour-coded boxes, and the codebase's own
   external-link styling (`custom_template.typ:56-62`, `#show link: it => underline(text(fill: blue,
   it.body))`) is colour-only with no non-colour cue (no icon, no distinct border weight). If the
   redesign adds new colour-differentiated visual cues for signature nesting depth or field-type
   grouping, a purely-colour-coded distinction is invisible in the PDF a user prints greyscale or
   views with a colour-vision deficiency, and there is currently **no established non-colour fallback
   convention anywhere in this codebase** to copy — this is genuinely new ground, not a
   pattern-reuse risk.
5. **CJK interaction.** The project ships a Japanese docs build (`docs/source/_typst/custom_template.typ`)
   with an explicit `font: ("Libertinus Serif", "Noto Serif CJK JP")` fallback, added because Typst's
   *automatic* fallback search silently failed to select a glyph for three specific CJK Unified
   Ideographs even though a covering font was fontconfig-visible in the same build container
   (`custom_template.typ:14-25`, "this round's own root-cause finding states plainly that automatic
   fallback already tried (and failed with) a covering font"). If the redesign's new style module
   introduces its own `set text(font: ...)` or per-element font overrides (e.g. a monospace font for
   signatures distinct from the body serif), that override risks **shadowing** the custom template's
   CJK fallback list for exactly the elements it touches (API signatures, field labels) — a
   regression that would only surface in the `ja` RTD build, not the `en` one, and Typst's font
   fallback failure mode is **silent** (no warning, no error — glyphs simply substitute or drop,
   per STATE.md's carried v0.6.4 lesson "RTD-02 — Typst's font fallback emits neither a warning nor
   an error").

**How to avoid:**
- Explicitly decide and test `block(breakable: false)` (or an equivalent single-signature
  cohesion strategy) for the signature wrapper; verify behavior at a real page boundary (a fixture
  with enough preceding content to push a signature near a page break) rather than assuming default
  `breakable: true` is fine.
- Model nesting depth as a `desc`-specific counter reset at the outermost `desc`/`desc_content`
  boundary, following the `_line_block_depth` idiom (comment-documented reset rule, not a new
  invention) — and add a GATE-01 fixture with 3+ levels of nesting (module → class → nested class →
  method) plus a SIBLING top-level `desc` immediately after, to catch depth leakage.
- Re-derive (don't assume) an overflow strategy for monospace signatures against realistic long
  fully-qualified Python/C++ names pulled from the real corpus (Sphinx's own `doc/` tree, already the
  project's standing GATE-02 fixture source) — measure actual overflow before choosing ZWSP
  injection vs. a different technique (e.g. `hyphenate: false` + explicit break points, or reducing
  font size for long signatures).
- Choose non-colour-redundant cues (icon + colour, or border style + colour, not colour alone) for
  any new visual differentiation, and verify with a greyscale render of the compiled PDF.
- Any new font declaration in the style module must be additive to (not replacing) the existing
  `Noto Serif CJK JP` fallback chain, and a `ja` RTD-equivalent local build must be re-measured for
  glyph presence after the change (the project's own D-03 four-check bar from Phase 30.1 is the
  reusable template: page count, byte-identical non-CJK text, CJK font present, visual confirmation).

**Warning signs:**
- No fixture exercises a signature near a real page boundary.
- The nesting-depth counter is a plain instance variable incremented in `visit_desc` with no matching
  reset check against a sibling `desc` at the same original depth.
- The GATE-01 fixture for the new signature style only uses short example signatures
  (`def foo(x)`), never a realistic fully-qualified long one drawn from the actual corpus.
- Any new `set text(...)`/`show raw: ...`/font declaration in the style module is written and tested
  only against the `en` build.

**Phase to address:**
The desc_*/field_list redesign phase (breakability, indentation, overflow) and the styling-module
phase (colour/CJK) — but the CJK regression check specifically must be re-run at the release-prep
phase against the `ja` build, since it is the kind of defect (STATE.md: "two failure modes that
present as a build success") that a green English-only CI run cannot detect.

---

### Pitfall 5: Test-suite blast radius — GATE-01 discipline under a redesign, not a bugfix

**What goes wrong:**
The exact-string test-suite pattern this project uses throughout (`assert 'strong({text("class")
text(" ") ...' in output`, and the dozens of similar assertions across the ~10 files touching
`desc_signature`/`desc_content`/`field_list`/`field_name` and the 61 `TestX RenderGate` classes in
`tests/test_*_render_gate.py`) is built on the assumption that a fix changes the emitted `.typ`
shape in one narrow, intentional way. A redesign inverts that assumption: **every** exact-string
assertion touching `desc_*`/`field_list`/admonition/rubric emission is expected to change, on
purpose, in this milestone. The trap is treating "the test suite is red" as equivalent to "something
is broken" and mass-regenerating expected strings to match whatever the new code happens to emit —
which silently launders an actual regression (a genuinely wrong new shape) into a passing test,
because the assertion was rewritten from the new (possibly buggy) output rather than derived
independently from the design authority.

**Why it happens:**
`CONCERNS.md` already names the general anti-pattern this project has caught before ("Tests That
Assert Presence Without Counting" — CR-01, Phase 22.2, where a duplicate-import bug shipped because
tests asserted presence, not exact count) — the redesign-scale version of the same failure is "tests
that assert against the code's own output" rather than against an independently-derived expected
shape. The project's own standing invariant exists precisely to prevent this:

> STATE.md / PROJECT.md Accumulated Context: *"Standing GATE-01 bar (since v0.6.0): every
> node-handler change ships a real `sphinx-build → typst.compile()` regression fixture, recorded
> **red against the unfixed code** before it is accepted as green."*

The trap this milestone specifically introduces: **"the old behaviour was not a crash, just ugly."**
Every prior GATE-01 fixture in this project's history proved a fatal compile abort transitioning
RED→GREEN (a `typst.TypstError` becoming a successful `%PDF` compile) — an unambiguous, mechanical
signal. This milestone's target defects (proportional bold instead of monospace, flush-left body
instead of hanging indent, no visual nesting) **all compile successfully today** — the "RED" state
for this milestone's fixtures cannot be "does not compile," it must be "compiles, but the rendered
output does not match the design authority" (Sphinx's own LaTeX PDF, per PROJECT.md's stated
authority). That is a fundamentally different, harder-to-mechanize RED state than every prior
GATE-01 fixture in this project's history, and the discuss/plan phase for each sub-redesign must
decide up front what the measurable RED assertion is (a structural/regex check on the `.typ` output,
a pypdf-extracted-text layout check, a rendered-page visual diff against the authority) before
writing the fixture — not default to "no fixture, because nothing crashes."

**How to avoid:**
- Sequence the redesign so exact-string assertions are updated **per sub-area** (desc_signature,
  then field_list, then admonition/rubric) in the same phase/plan that changes that area's emission
  — never as a blanket "fix all broken tests" pass at the end that regenerates expected strings from
  observed output.
- For each redesigned area, derive the new expected `.typ` shape from the design authority
  (Sphinx's own LaTeX `.sty` sources, per PROJECT.md's Secondary Reference:
  `sphinxlatexobjects.sty`, `sphinxlatexadmonitions.sty`) or from a hand-reasoned Typst equivalent —
  **before** running the new code — so the assertion is not just an echo of whatever the
  implementation produced.
- For each redesigned area, define the GATE-01 RED state explicitly at plan time: since "does not
  compile" is not available as the differentiator here (old output compiles fine), use one of:
  structural regex assertions on the `.typ` source (e.g. "signature body uses `raw(...)`/monospace
  font, not `text(...)`" ), pypdf-extracted-text ordering/whitespace checks, or a documented manual
  visual comparison against the LaTeX PDF authority recorded as evidence (the project's established
  "human confirmation gate" pattern from the v0.6.1 audit, `17-03`).
- Keep a running census of exact-string assertions expected to break, sub-area by sub-area (the 10
  files + 61 render-gate classes found in this research are a starting inventory), so "did I touch
  every site that needs updating" is checked by grep, not by trusting `pytest` to surface every
  stale assertion (a test that was checking for the OLD wrong shape and now silently passes because
  it happens to also match the NEW wrong shape would not be caught by running the suite alone).

**Warning signs:**
- A plan's task list says "update failing tests to match new output" without naming which assertions
  were independently re-derived vs. copy-pasted from a test run.
- A phase closes with the observation "nothing crashed, so it must be fine" for a construct whose
  entire purpose this milestone is to make **look** different, not just compile.
- The full suite goes from green to red to green again within one phase with no intermediate
  artifact recording what the RED state's failure message actually said (mirrors the project's own
  established practice of capturing the verbatim `TypstError` text at RED, as v0.6.5's fixture did).

**Phase to address:**
Every redesign phase must own its own test-migration scope; a dedicated closing phase should NOT be
the first place exact-string assertions are touched — that reintroduces exactly the "regenerate from
observed output" trap this pitfall describes. The full-corpus GATE-02 gate should be re-run at the
end of each major sub-area (desc_*, then admonition, then citation), not deferred to one release-prep
run at the very end.

---

### Pitfall 6: The `@preview` lockstep hazard grows a fifth (unguarded) surface

**What goes wrong:**
Four `@preview` package version strings currently live in exactly **three** guarded surfaces —
`writer.py:155-158`, `template_engine.py:612-615`, `templates/base.typ` — enforced by
`tests/test_preview_version_sync.py`. That test also globs `examples/**/*.typ` as a fourth,
lighter-weight surface (drift-detection only, not full lockstep identity). There is a known,
currently **unguarded** fifth site: `docs/source/_typst/custom_template.typ`
(`custom_template.typ:39-44`) — a full hand-copy of `base.typ`'s imports, carried as an open Warning
from Phase 30.1's review (STATE.md: *"`custom_template.typ` is an unguarded FOURTH `@preview`
version-lockstep site (the sync test watches 3 surfaces + `examples/`)"*). Introducing a new bundled
Typst style module (this milestone's explicit deliverable) is a **new class** of shared-asset
sync risk, layered on top of the pre-existing unguarded one, unless its integration points are
deliberately kept out of that lockstep shape.

**Why it happens:**
The milestone brief is explicit that the new module must be importable from *every* generated `.typ`
file — master, included, and (implicitly) any custom-template-driven output — because "Typst's
`#include()` does not inherit imports from the parent file, so each file must re-declare" (PROJECT.md
Target Features). That is structurally identical to the existing `@preview` import problem: the same
import lines currently live in `writer.py`'s included-doc branch (`writer.py:153-163`) AND
`template_engine.py`'s master-doc render path (`template_engine.py:609-618`). Adding the new
module's import line to both of those sites reproduces the two-site lockstep shape
`test_preview_version_sync.py` was written to guard — except this time there is no "version number"
to desync (the module is bundled, not fetched, per the milestone's stated invariant: *"this milestone
creates no fifth version-lockstep site — the new module is bundled, not fetched"*), so the risk is
not a *version* mismatch but an **import-statement drift** mismatch: `writer.py`'s included-doc path
emitting a different import path/name than `template_engine.py`'s master-doc path, or the builder
failing to copy the module file to every location the two import paths expect it (mirroring the
exact CR-01/nested-master pattern already fixed once — `_compute_template_import_path`'s per-depth
relativization, `writer.py:118-119`, was rewritten specifically because a sentinel-based path scheme
collided with real directory names).

There is also a distinct, already-shipped structural trap directly relevant to *copying* the new
module: `builder.py`'s `_write_template_file()` **skips writing `_template.typ` entirely** when a
Typst Universe package is configured alone with no custom template
(`builder.py:565-566`, `if typst_package and not raw_template_path: return`) — this is intentional
for `_template.typ` (a package-alone master genuinely needs no separate template file), but if the
new style module's on-disk copy step is bolted onto this same conditional (rather than given its own
unconditional copy path), a package-alone build would silently never receive the style module file
on disk while the translator still emits `#import "..."` referencing it — a guaranteed build-time
"file not found" for exactly the routing configuration that already caused BUG-A
(`CONCERNS.md`: *"writer and builder disagreed about whether `_template.typ` exists, causing
package-alone configurations to be unbuildable"*).

**How to avoid:**
- Extend `test_preview_version_sync.py` (or add a sibling test) to also assert the new module's
  import line/path is identical across `writer.py`'s included-doc branch and
  `template_engine.py`'s master-doc branch — treat it as a lockstep pair from day one, not an
  afterthought caught by a later audit.
- Give the module's on-disk copy step its **own** unconditional code path in `builder.py`, separate
  from `_write_template_file()`'s package-alone early return — verify with a real
  `sphinx-build -b typstpdf` using `typst_package` alone (no custom template) as a dedicated GATE-01
  fixture, mirroring the BUG-A regression test the routing-centralization fix (`resolve_package_for_
  engine()`, `template_engine.py:15-39`) already established.
- Close the pre-existing `custom_template.typ` gap in the same milestone if the new module touches
  that file at all (e.g. if `docs/source/_typst/custom_template.typ` needs updating to import the
  new module too) — do not let a second unguarded surface accumulate on top of the first one that is
  already on record as a carried Warning.
- Verify the nested-master import-path computation (`_compute_template_import_path`,
  `writer.py:71-119`) is reused for the new module's relative path, not re-implemented — a second,
  independent relativization scheme is exactly how CR-01 (the `_template` sentinel collision) was
  introduced the first time.

**Warning signs:**
- A diff adds the new module's `#import` line to only one of `writer.py`/`template_engine.py`.
- `builder.py`'s copy step for the new module is textually inside (or copy-pasted from)
  `_write_template_file()`'s body, inheriting its `typst_package`-alone early return.
- No GATE-01 fixture exercises the `typst_package`-alone configuration with the new module present.
- `test_preview_version_sync.py` is left unmodified even though a new shared-import surface was
  added.

**Phase to address:**
The styling-module-scaffolding phase (should be early, since desc_*/admonition redesign phases
depend on the module existing and being importable everywhere) — with its own dedicated
package-alone-routing GATE-01 fixture as an explicit success criterion, not folded silently into a
later phase's acceptance bar.

---

### Pitfall 7: Citation nodes are greenfield — and the "no separator" failure is already reproduced in this repo

**What goes wrong:**
`translator.py` currently has **zero** handlers for `citation`, `citation_reference`, or `label`
(the docutils node docutils uses for a citation's own visible `[Key]` marker — distinct from the
`nodes.label`-as-in-"a title/caption" usage elsewhere in this codebase). Because there is no
registered `visit_citation`/`visit_citation_reference`, docutils falls through to
`unknown_visit` (`translator.py:3800-3811`), which only logs a warning and does **not** raise
`SkipNode` — so the citation's children are still visited by the default machinery, emitting bare
`text(...)` calls with none of the separator-protocol bookkeeping any real handler would apply. This
exact failure is already recorded, first-hand, in this repository:

> `examples/charged-ieee/approach1/source/index.rst:1-4` (removed at Phase 22.2, commits `8bed1a3`/
> `c014a0b`): *"typsphinx's translator has no handler for reStructuredText citation nodes, so a
> citation directive and its reference emit adjacent expressions with no separator inside a Typst
> code block, which is a hard Typst syntax error."*

This means the greenfield implementation is not free of the separator-protocol hazard just because
it has no legacy shape to preserve — it must apply the FULL checklist (Pitfall 1) from its very
first line of code, with no existing handler to imitate for this specific node family.

**Docutils node-structure specifics that are easy to get wrong (no prior code in this repo to check
against):**
- **`citation` vs. `citation_reference` vs. `label`**: a `nodes.citation` is a *definition* (like
  `nodes.footnote`) — it has a `nodes.label` as its FIRST child (the visible `[Key]` marker text,
  e.g. `Smith2020`) followed by body content (typically a paragraph). A `nodes.citation_reference`
  is the *inline* citing site (`[Smith2020]_` in source) and carries a `refname`/`refid` pointing at
  the citation's docutils id, analogous to `footnote_reference`'s `refid`. The existing
  `visit_footnote`/`visit_footnote_reference` pair (`translator.py:2278-2401`) is the closest
  structural analog in this codebase and should be the primary pattern to adapt — including its
  document-order pre-pass index (`visit_document`'s `self._footnote_index`, built via
  `self.document.findall(nodes.footnote)` *before* any body content is visited, specifically because
  footnote/citation *definitions* are frequently positioned after their first citing reference in
  source order) — but citations differ from footnotes in ways that break a naive copy-paste:
  - Footnotes render **inline** at first citation (auto-numbered, no persistent visible label reused
    elsewhere); citations render as a **stable, reusable key** (`[Smith2020]`) that must look
    identical at every citing site, not just the first — so the "definition on first use, bare reuse
    after" split `visit_footnote_reference` performs (`translator.py:2359-2394`) does not directly
    apply; every citation reference should probably emit the same `[Key]`-styled link form regardless
    of citation order.
  - A `citation`'s `label` child is NOT skipped by position the same way `visit_footnote`'s
    `footnote_node.children[1:]` slice skips docutils' auto-generated numeral label
    (`translator.py:2388`) — for a citation, the `label` child IS the meaningful, user-visible
    bibliography key and must be rendered, not discarded.
- **Forward references / citations defined after use**: mirror the footnote pre-pass's stated reason
  for existing (`translator.py:410-420`, "footnote definitions are frequently positioned AFTER their
  citing footnote_references in source order") — citations have the identical ordering hazard (a
  `.. [Smith2020]` definition commonly appears in a trailing "References" section, well after every
  `[Smith2020]_` reference in the body). A document-order pre-pass index, built in `visit_document`
  exactly like `self._footnote_index`, is very likely required for citations too — attempting to
  render a citation reference by walking forward through the doctree at citing time (rather than via
  a pre-built index) will dangle on the (common) case of citations gathered in a bibliography section
  at the end.
- **Duplicate labels**: `_namespace_label`/`_sanitize_label` (Pitfall 3) apply here with an
  extra wrinkle specific to citations: citation keys are **author-chosen strings**, not
  docutils-generated ids, so they are far more likely to collide across documents than
  auto-slugged section ids (e.g. two chapters both citing a paper and each defining their own local
  `.. [GoF95]` in a per-chapter bibliography) — the corpus-wide flattening via `#include()`
  (Pitfall 3) makes this a near-certainty for any multi-document bibliography scheme, not an edge
  case. Decide the citation-key namespacing rule (per-document, like the existing default, vs. a
  single project-wide namespace merging duplicate keys) as an explicit design decision, not an
  emergent accident of reusing `_namespace_label`'s current per-docname default unmodified.
- **`:cite:` from sphinxcontrib-bibtex is a different extension and different node types — do not
  conflate.** docutils' native `citation`/`citation_reference` (`.. [Key]` / `` [Key]_ ``) are what
  this milestone scopes (PROJECT.md: *"`visit_citation` / `visit_label` / `visit_citation_reference`
  render a `thebibliography`-equivalent labelled list"*). `sphinxcontrib-bibtex`'s `:cite:` role is a
  **separate third-party Sphinx extension**, not a dependency of this project (not present in
  `pyproject.toml`), and it constructs its own custom docutils nodes at parse time distinct from
  bare `citation`/`citation_reference` — a `sphinx-build` using that extension would present entirely
  different node classes to this translator, which `visit_citation`/`visit_citation_reference` would
  never see. Do not scope-creep into handling `sphinxcontrib-bibtex`'s node types under the belief
  that "citations" is one problem — verify (via a real doctree dump, the way `charged-ieee`'s
  removed example presumably needs to be restored) which node classes the actual `examples/
  charged-ieee` restoration target produces before assuming native docutils citation syntax is
  sufficient for it.

**How to avoid:**
- Build the citation implementation directly off `visit_footnote`/`visit_footnote_reference` as a
  structural template, but explicitly diverge on: (a) the label child is rendered, not skipped; (b)
  every reference (not just the first) renders the same visible-key form; (c) namespacing strategy
  for citation keys is an explicit, documented decision, not `_namespace_label`'s default reused
  blindly.
- Apply the full Pitfall 1 separator-protocol checklist to `visit_citation`/`visit_citation_reference`
  from the first draft — there is no existing correct implementation to copy verbatim, only the
  footnote analog (which differs, per above) and the general protocol rules.
- Restore `examples/charged-ieee`'s stripped citation syntax as the acceptance fixture (PROJECT.md
  names this explicitly: *"to the point where the citation syntax Phase 22.2 stripped out of
  `examples/charged-ieee/` can be restored"*) — this gives a real, already-known-desired doctree
  shape to test against, and the removal commits (`8bed1a3`, `c014a0b`) are the exact source text to
  reintroduce.
- Confirm with a real doctree inspection (not assumption) whether `charged-ieee`'s citation needs are
  satisfied by bare docutils `citation`/`citation_reference`, or whether the sample was actually
  relying on `sphinxcontrib-bibtex` syntax before removal — this determines whether the milestone's
  stated scope is sufficient or whether a dependency decision needs to be surfaced to the owner.

**Warning signs:**
- A citation reference's rendering logic branches on "first use vs. reuse" copy-pasted from
  `visit_footnote_reference` without re-deriving whether that branch even makes sense for a
  reusable, stable citation key.
- No document-order pre-pass index exists for citation definitions, and a fixture with a trailing
  "References" section (definitions after all uses) is never tested.
- `_namespace_label` is called with the raw citation key and no discussion of whether that produces
  the intended cross-chapter behavior.
- A GATE-01 fixture never includes 2+ citations, 2+ documents, or a citation defined after its first
  use.

**Phase to address:**
The dedicated citation phase (explicitly scoped last/greenfield per the milestone brief) — should
start from a real doctree dump of the restored `charged-ieee` sample, not from a hypothetical.

---

## Separator Protocol Checklist

Derived directly from `translator.py`'s implementation (not paraphrased) — apply this to **every**
new or rewritten `visit_*`/`depart_*` pair this milestone touches.

**Step 1 — Classify the node.**
- Can it appear as **inline content inside a paragraph** (or paragraph-like context)? → Protocol A.
- Can it appear inside a **list item's `{ }` content block** (`in_list_item`)? → Protocol B.
- Can it appear inside one of the **five code-mode concat contexts**
  (`in_desc_parameter`, `_in_link`, `_in_term`, `_in_field_body`, `_in_attribution` —
  `translator.py:929-935`)? → Protocol C.
- Is it a **block-level construct with siblings** (another instance of itself, or a differently-typed
  sibling immediately before/after) that must visually separate even though nothing wraps it in a
  paragraph/list/concat context? → Protocol D.
- Does it carry `ids` that a same-/cross-document reference might resolve to? → Anchor rule.

A single node can require more than one protocol simultaneously (e.g. `visit_math` needed A + B + C
all at once — this is exactly what MATH-01 got wrong the first time).

**Step 2 — Protocol A (paragraph).**
At the very start of `visit_*`, call `self._add_paragraph_separator()`
(`translator.py:319-329`) before emitting anything. It is a no-op unless `in_paragraph` is currently
True, so it is safe to call unconditionally.

**Step 3 — Protocol B (list-item, INLINE nodes).**
Immediately after Step 2, for an inline/leaf node:
```python
if not self._emit_inline_concat_separator():
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
```
(mirrors `visit_literal`, `translator.py:1301-1303`, and `visit_math`, `translator.py:3967-3969`).
At the END of the visitor, after emitting content:
```python
if not self._mark_inline_concat_content():
    if self.in_list_item:
        self.list_item_needs_separator = True
```
Never write the list-item leading/trailing bookkeeping without routing it through
`_emit_inline_concat_separator()`/`_mark_inline_concat_content()` first — those two helpers are the
single source of truth for which of the five concat contexts (Step 4) takes precedence, and hand-rolled
duplicate logic will desync from it.

**Step 3b — Protocol B (list-item, BLOCK-level nodes: figures, tables, admonitions, field lists,
citations-as-block, signature wrapper).**
At the LEADING edge of `visit_*`:
```python
if self.in_list_item and self.list_item_needs_separator:
    self.add_text("\n")
    self.list_item_needs_separator = False
```
(mirrors `visit_figure`, `translator.py:2140-2142`, and `visit_field_list`, `translator.py:4912-4914`).
At the TRAILING edge of `depart_*`:
```python
if self.in_list_item:
    self.list_item_needs_separator = True
```
(mirrors `depart_figure`, `translator.py:2216-2217`, and `depart_field_list`, `translator.py:4926-4927`).

**Step 4 — Protocol C (code-mode concat contexts).**
If the new node can be a sibling inside a def-list term, a link body, a desc parameter list, a
collapsed inline field body, or a block-quote attribution, do NOT hand-write a `+`-join — call
`_emit_inline_concat_separator()`/`_mark_inline_concat_content()` (Step 3 already routes through
these for inline nodes). If the new node OPENS its own such context (the way `visit_field_body`
activates `_in_field_body` only for an all-inline body, `translator.py:5008-5017`), push/pop the
prior state via the established stack idiom (`_field_body_stack`, `_inline_concat_stack`) — never a
bare scalar, or a nested instance of the same context will clobber the outer one.

**Step 5 — Protocol D (forced sibling-boundary breaks).**
For a construct that must visually separate from an adjacent sibling of the same or a different
type, but is NOT wrapped in a paragraph/list-item/concat context that already handles it (e.g. two
consecutive signature blocks, a rubric followed by its content, a `desc` followed by another `desc`):
use `self._emit_forced_break("parbreak()")` or `self._emit_forced_break("linebreak()")`
(`translator.py:289-317`) — **never** a bare `self.add_text("\n")` or `self.add_text("\n\n")`
expecting it to produce a visual gap; it will not (this is the single most-repeated root cause in
this project's history — see Pitfall 1).

**Step 6 — Anchor rule.**
If the node carries `ids`, call `self._emit_id_anchors(node)` (`translator.py:331-402`) — do not
hand-roll a `<label>` postfix. It already: (a) drives the same list-item separator bookkeeping as
Step 3b, (b) routes every id through `_namespace_label`/`_sanitize_label`, (c) dedupes, and (d)
emits the anchor as a self-contained markup-mode statement (never a code-mode postfix — Pitfall 3).
If the node self-anchors one id through its own bracket-wrap (like `depart_figure`'s `ids[0]`), pass
`skip_ids={...}` to avoid a double-definition abort.

**Step 7 — Fixture requirement (non-negotiable, per the standing GATE-01 bar).**
Every new/changed handler ships a real `sphinx-build → typst.compile()` fixture, recorded **RED**
against the pre-fix/pre-change code (capture the verbatim `TypstError` text, per v0.6.5's practice),
covering at minimum:
- The node at the top level of a document.
- The node as the FIRST and as a LATER child inside a list item.
- The node inside a field body / definition-list term, if the node can plausibly appear there.
- Two or more instances of the node as SIBLINGS (catches missing Protocol D breaks).
- If block-level: the node followed by trailing content in the same list item (catches missing
  trailing `list_item_needs_separator = True`).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Hand-rolling list-item separator bookkeeping instead of calling `_emit_inline_concat_separator`/`_mark_inline_concat_content` | Feels simpler for a "just this one node" case | Desyncs from the single source of truth the moment a second concat context becomes relevant; reproduces MATH-01's exact defect class | Never |
| Deriving new GATE-01 fixtures' expected strings from a fresh `pytest` run's actual output rather than an independently-reasoned expected shape | Fast, "green" quickly | Silently accepts a wrong redesign shape as correct (Pitfall 5) | Never for the redesigned constructs; acceptable only for genuinely unrelated pre-existing assertions incidentally touched by an unrelated whitespace change |
| Copying `_write_template_file`'s package-alone early-return pattern for the new module's copy step | Reuses existing code path, less new code | Silently drops the module file for `typst_package`-alone builds (reproduces BUG-A's class) | Never — give the module copy its own unconditional path |
| Using a bare scalar (not a stack) for a new buffer-swap's saved state | Less code for the simple case | Breaks the instant the swap can nest (reproduces GATE-02 fatal #18's class) | Only if the new construct is provably non-nestable — document the proof in the code comment, mirroring `_line_block_depth`'s documented reasoning |
| Attaching `<label>` directly as a postfix on a new `block()`/`grid()` wrapper call | Looks simpler than the existing "separate trailing statement" form | Fatal parse error in code mode, or ambiguous binding to only the last grid cell | Never — always use the `_emit_id_anchors`/form-(b) pattern |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| Bundled style module ↔ `writer.py` included-doc path | Adding the module's import only to `template_engine.py`'s master-doc render, forgetting `writer.py`'s separate included-doc import block (`writer.py:153-163`) | Add to both sites in the same commit; extend `test_preview_version_sync.py` (or a sibling test) to assert they match |
| Bundled style module ↔ package-alone routing | Piggybacking the module's on-disk copy on `_write_template_file()`'s `typst_package`-alone early return | Give the copy step its own unconditional path; add a package-alone GATE-01 fixture |
| Bundled style module ↔ nested masters | Re-implementing relative-path computation instead of reusing `_compute_template_import_path` | Reuse the existing per-depth helper (`writer.py:118-119`) verbatim |
| Bundled style module ↔ the three in-repo custom templates | Assuming a custom template needs to import the new module itself | Per the milestone's own design, the translator-emitted body already carries its own import lines (mirroring the `@preview` imports) — custom templates receive pre-imported body content and should need zero changes; verify this holds for all three (`examples/advanced/_templates/custom.typ`, `docs/source/_typst/custom_template.typ`, `examples/charged-ieee/approach2/source/_templates/_template.typ`) |
| Bundled style module ↔ `docs/source/_typst/custom_template.typ`'s CJK font fallback | New per-element font overrides (e.g. monospace for signatures) silently shadow the existing `Noto Serif CJK JP` fallback for exactly the elements they touch | Any new font declaration must extend, not replace, the existing fallback chain; re-run the D-03 four-check bar against a local `ja` build |
| Citation implementation ↔ `sphinxcontrib-bibtex` | Assuming `:cite:` role support is in scope because "citations" sounds like one feature | `sphinxcontrib-bibtex` is a separate, not-installed extension producing different node classes; verify via a real doctree dump which nodes `examples/charged-ieee`'s restoration actually needs before assuming bare docutils citation syntax suffices |

## Layout / Rendering Traps

| Trap | Symptoms | Prevention | Threshold |
|------|----------|------------|-----------|
| Signature block splits across a page boundary | A function's name on one page, its parameter list starting on the next | Explicit `block(breakable: false)` (or equivalent) decision, tested with a fixture placing the signature near a page break | Any signature near the current page's remaining vertical space |
| Nesting-depth counter leaks across sibling `desc` nodes | A module-level function inherits indentation from a preceding deeply-nested class | Depth counter driven specifically by `desc`/`desc_content` visit/depart, reset at the outermost boundary, following the `_line_block_depth` idiom | 2+ levels of nesting followed by a sibling at depth 0 |
| Long fully-qualified signature overflows the right margin | Text clipped or running off the page edge in the rendered PDF | Re-derive an overflow strategy (ZWSP injection at natural break points, or an alternative) against real long signatures pulled from the corpus, not short examples | Any signature longer than the current page's text width — measure against the actual Sphinx `doc/` corpus |
| Colour-only visual differentiation | Nesting depth or field grouping invisible in greyscale print | Pair colour with a non-colour cue (icon/border/weight); verify with a greyscale render | Any new colour-coded distinction |
| New font declarations shadow the CJK fallback | Silent glyph substitution/drop in the `ja` build only, no warning or error (per STATE.md's carried RTD-02 lesson) | Extend, don't replace, the existing font list; re-measure the `ja` build's glyph presence after any font change | Any `set text(font:...)`/`show raw:...` touching signature or field styling |

## "Looks Done But Isn't" Checklist

- [ ] **New `desc_*`/`field_list`/admonition/rubric handler compiles cleanly:** verify it also
      compiles when nested inside a list item, a definition-list term, and a field body — not just
      at the top level of a document (Pitfall 1).
- [ ] **New buffer-swap restores state:** grep the diff for every `self.body = [...]` assignment and
      confirm a matching `in_paragraph`/`paragraph_has_content` (and, if applicable,
      `in_list_item`/`list_item_needs_separator`) save/restore pair exists nearby (Pitfall 2).
- [ ] **New label-emitting site is namespaced and sanitized:** grep for any f-string that builds a
      `<...>` label token without a `_namespace_label`/`_sanitize_label` call (Pitfall 3).
- [ ] **New wrapper (`block()`/`grid()`) never attaches `<label>` as a direct postfix:** confirm the
      anchor is a separate trailing markup statement, matching `_emit_id_anchors`'s form (Pitfall 3).
- [ ] **New GATE-01 fixture defines a measurable RED state that is not "does not compile":** for a
      cosmetic/layout redesign, the RED assertion must be a structural/regex/pypdf-text check against
      the design authority, recorded before the fix (Pitfall 5).
- [ ] **New bundled module is importable from a `typst_package`-alone build:** a dedicated fixture
      exercises this configuration, not just the default-template path (Pitfall 6).
- [ ] **Citation fixture includes a citation defined AFTER its first reference, and 2+ documents:**
      catches both the forward-reference ordering hazard and cross-document label collisions
      (Pitfall 7).
- [ ] **Any new font/colour choice is verified against the `ja` build and a greyscale render**, not
      just the default English/colour PDF (Pitfall 4).

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|---------------|
| 1. Code-mode juxtaposition / cosmetic-only `\n` | Every phase adding/rewriting a handler (desc_*, field_list, admonition/rubric/topic, citation) | GATE-01 fixture per Step 7 of the Separator Protocol Checklist, covering top-level + list-item + field-body/term contexts |
| 2. Buffer-swap state clobber | Any phase introducing a new buffer-swap (likely signature-wrapper and citation phases) | GATE-01 fixture with trailing content immediately after the swapped element |
| 3. Label attachment / duplicate labels | Signature-wrapper phase; citation phase | GATE-01 fixture with 2+ signatures/citations and, for citations, 2+ documents |
| 4. Layout traps (page-break, indentation, overflow, colour, CJK) | desc_*/field_list redesign phase (breakability/indent/overflow); styling-module phase (colour/CJK) | Page-boundary fixture; 3+-level nesting + sibling fixture; long-signature-from-corpus fixture; greyscale render check; re-run `ja` build's D-03 four-check bar |
| 5. Test-suite blast radius / GATE-01 discipline under "not a crash, just ugly" | Every redesign phase individually, not a single closing phase | Per-sub-area RED state defined and recorded before the fix; running census of touched exact-string assertions |
| 6. `@preview`/bundled-module lockstep hazard (5th surface) | Styling-module-scaffolding phase (early) | Extended `test_preview_version_sync.py`-style check; package-alone GATE-01 fixture |
| 7. Citation node structure specifics | Citation phase (greenfield, scoped last) | GATE-01 fixture: forward reference, 2+ citations, 2+ documents; doctree dump confirming `sphinxcontrib-bibtex` is out of scope |

## Sources

- `.planning/PROJECT.md` — Current Milestone (v0.7.0) scope and design authority; Key Decisions;
  full v0.6.0–v0.6.5 Validated requirement entries (cited by phase/requirement ID throughout)
- `.planning/MILESTONES.md` — v0.6.0 through v0.6.5 shipped-milestone summaries (GATE-01/GATE-02
  fatals, FID-01a, clusters A–F, MATH-01)
- `.planning/codebase/CONCERNS.md` — Buffer-Swap State Machine fragility, Translator Size/Complexity,
  Test Coverage Gaps, Anti-Patterns Observed
- `.planning/STATE.md` — Accumulated Context (standing GATE-01 bar, carried Phase 30.1 Warnings
  including the unguarded `custom_template.typ` lockstep site, RTD-02 silent-font-fallback lesson)
- `typsphinx/translator.py` — direct code reading: `_emit_forced_break` (289-317),
  `_add_paragraph_separator` (319-329), `_emit_id_anchors` (331-402), the code-mode concat context
  table (929-935), `visit_title`/`depart_title` (473-650), `visit_figure`/`depart_figure`/
  `visit_caption`/`depart_caption` (2105-2276), `visit_footnote_reference` (2295-2401), `_visit_
  admonition`/`_depart_admonition` (4106-4168), `visit_desc*`/`depart_desc*`/`visit_field*`/
  `visit_rubric` family (4619-5132), `visit_math`/`visit_math_block` (3936-4065), `_sanitize_label`/
  `_namespace_label` (3287-...), `unknown_visit` (3800-3811)
- `typsphinx/writer.py` — `_compute_template_import_path` (71-119), `translate()`'s master/included
  routing and included-doc import block (121-166)
- `typsphinx/builder.py` — `_write_template_file`'s package-alone early return (521-592)
- `docs/source/_typst/custom_template.typ` — CJK font-fallback rationale and the unguarded
  `@preview` import block (1-125)
- `tests/test_preview_version_sync.py` — the three-surface lockstep test and its `examples/**`
  fourth-surface glob (1-134)
- `examples/charged-ieee/approach1/source/index.rst:1-4`,
  `examples/charged-ieee/approach2/source/index.rst:1-4` — the recorded, first-hand citation
  no-separator syntax-error description, and commits `8bed1a3`/`c014a0b` that removed the citation
  content

---
*Pitfalls research for: typsphinx v0.7.0 API rendering design overhaul*
*Researched: 2026-07-29*
