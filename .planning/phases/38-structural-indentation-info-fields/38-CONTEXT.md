# Phase 38: Structural Indentation + Info Fields - Context

**Gathered:** 2026-08-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Put a structural indent around a description body so the page shows containment: a `desc_content`
body sits one step inside its own `desc_signature`, indentation accumulates with nesting depth, a
nested member's own signature aligns with its parent's body rather than over-indenting, depth does
not leak across siblings, and the field-list block follows the same single constant instead of a
private magic number. Alongside it, the info-field block gets its real typography and its real
vertical rhythm.

**In scope** — the handlers that own the indent and the info-field bytes:
`visit/depart_desc_content` (both `pass` today, `typsphinx/translator.py:5102, 5108`),
`visit/depart_field_list` (5332, 5348), `visit/depart_field` (5361, 5367),
`visit/depart_field_name` (5392, 5408), `visit/depart_field_body` (5421, 5452),
`visit/depart_literal_strong` and `visit/depart_literal_emphasis` (5745–5767), and
`depart_desc`'s break bookkeeping (4798) to the extent Phase 38 voids its premise (D-10).

**Out of scope:**

- `desc_signature` and its inline children — Phase 37 owns them and is complete. The signature's
  wrapper, its hanging indent, its per-sub-part treatment and its `sticky: true` are all fixed
  points that Phase 38 must not re-shape. Phase 38 wraps *around* the body, never around the
  signature.
- `visit_block_quote` / `depart_block_quote` — locked out by D-04 below.
- `rubric` and admonitions — Phase 39 (ADM-01..05). Phase 39's SC#3 depends on this phase's indent
  existing, but the rubric handler itself is Phase 39's to change.
- Citations — Phase 40.
- `SHARED_INDENT_STEP`'s value — locked at `"2.5em"` by D-02; Phase 37's `golden.typ`, its gates and
  `37-EMISSION-CONTRACT.md` §3/§9/§10 are therefore untouched by any value change.
- Anything that makes the styling user-overridable — explicitly not a goal of v0.7.0.

</domain>

<decisions>
## Implementation Decisions

Every measurement cited below was taken **this session (2026-08-01)** by three means, all against
real tooling and none from recall:

1. a real `sphinx-build -b typst` of a hand-written `py:` domain sample (a `py:class::` containing a
   `py:method::` containing a `py:attribute::`, a field list with multi-value and single-value
   fields, a sibling top-level `py:function::`, and a block quote);
2. real `typst.compile()` / `typst.query()` probes through `typst-py` 0.15.0, reading left edges and
   baselines from `here().position()` and widths from `context measure(...)`;
3. **a working prototype**: a throwaway copy of `typsphinx/` under the session scratchpad, patched
   with the decisions below, driven over this project's own `docs/source` with a real
   `sphinx-build -b typst` and a real `typst.compile()` to a real 87-page PDF. **The repository was
   not modified.** Page images from that PDF are what the owner reviewed before deciding D-02.

### Indent mechanism — IND-01..IND-05

- **D-01: `desc_content` is wrapped in `pad(left: SHARED_INDENT_STEP, { … })`, and nesting is left to compose structurally — there is no depth counter.**
  Measured left edges from a compiled probe (11pt, page margin at 20.0pt):

  | Site | x |
  |---|---|
  | class `desc_signature` | 20.0pt (page margin) |
  | class `desc_content` body | 47.5pt (+27.5) |
  | nested method `desc_signature` | 47.5pt — equal to the class body |
  | nested method `desc_content` body | 75.0pt (+27.5) |
  | class body continuing after the nested member | 47.5pt |
  | sibling top-level `desc` after the nest | 20.0pt |

  That single table satisfies IND-01 (body > its own signature), IND-02 (cumulative with depth),
  IND-03 (the nested signature aligns with the parent body and gets **no** further step — it is
  inside the parent's `pad` and is not itself padded), and IND-05 (depth cannot leak, because the
  `pad` closes when `depart_desc_content` runs; there is no counter that could fail to reset).
  **IND-05 must therefore be asserted, not implemented** — REQUIREMENTS.md phrases it as "the
  nesting-depth counter resets correctly", but under D-01 no counter exists. Do not introduce one in
  order to make the requirement's wording literal.

- **D-02: `SHARED_INDENT_STEP` stays `"2.5em"`. Do not re-value it.**
  The owner compared three real compiled PDFs of this project's own `docs/source` — 2.5em / 2.0em /
  1.5em — rendered from the same anchored page (`TypstBuilder.write_doc` / `copy_image_files` /
  `copy_template_assets` / `finish`), against a fourth control page built from the unmodified
  translator, and chose 2.5em. Accumulated left edges at 2.5em: 27.5pt at the class body, 55.0pt at
  a method body, 82.5pt at a method's field list, against a measured text column of 453.54pt
  (`37-EMISSION-CONTRACT.md` §10). The rejected alternatives are recorded so nobody resurrects them
  as an "improvement": 2.0em (22.0pt/44.0/66.0, the low end of REQUIREMENTS.md's ≈22–25pt reference
  quantum) and 1.5em (16.5/33.0/49.5, where one step approaches Typst's own bullet-marker indent,
  measured at 9.36pt, and the hierarchy stops reading). Because the value does not move, Phase 37's
  `golden.typ`, its render gates and `37-EMISSION-CONTRACT.md` §3/§9/§10 need **no** re-derivation
  on account of the constant.

- **D-03: the field list takes its own `pad` step, nested inside the body's.**
  FLD-01 asks for one step beyond the surrounding description body; under D-01's composition that is
  simply a second `pad` inside the first, and it needs no separate constant. Measured in the
  prototype's real PDF: class body 27.5pt → method body 55.0pt → the method's `Parameters:` block
  82.5pt.

- **D-04: `visit_block_quote` / `depart_block_quote` are NOT touched. This is the binding reading of IND-04, recorded so verify-time does not re-open it.**
  Measured: `typsphinx/` contains **no** indent literal at any of the three sites IND-04 names — a
  repo-wide grep over `typsphinx/*.py` and `typsphinx/templates/*.typ` finds only `base.typ`'s title
  block (`2em`/`1em`/`1.2em`/`0.5em`) and the `inset: 8pt` in the `desc_signature` fallback box at
  `translator.py:4757`, none of which is a desc/field/quote indent. `block_quote` gets its indent
  from Typst's own `quote(block: true, …)` default, measured at **11.0pt** (1em at 11pt); the shared
  constant is 27.5pt. ROADMAP SC#4's checkable property — "a repo-wide grep over `typsphinx/` finds
  no second independent indent literal at those sites" — is therefore **already true and stays true**
  under D-01/D-03, since neither introduces a literal (both spell `SHARED_INDENT_STEP`). IND-04's
  purpose is to forbid per-node magic numbers, not to force every indent context onto one visual
  depth. The two rejected alternatives were compiled and shown to the owner:
  `pad(left: 2.5em, quote(block: true, …))` lands at 27.5 + 11.0 = **38.5pt**, so the constant's
  value would stop matching the depth it produces; dropping `quote()` for a bare `pad` reaches
  27.5pt but loses `quote()`'s own vertical spacing and destroys `visit_attribution`'s contract (the
  right-aligned "— Author", verified rendering today).

### Info fields — FLD-01..FLD-03

- **D-05: FLD-03 uses the reference recipe — parameter name `strong(raw("…"))` bold monospace, type `emph(raw("…"))` italic monospace (owner choice, variant "A").**
  Chosen from four real compiled renderings shown side by side, with Phase 38's indent already
  applied and the Phase 37 signature line above each for comparison. Measured starting state:
  `visit_literal_strong` and `visit_literal_emphasis` delegate to `visit_strong` / `visit_emphasis`
  via the dummy-node trick, so today the name emits `strong({text("name")})` (bold **proportional**)
  and the type `emph({text("str")})` (italic **proportional**) — neither is monospace, which is what
  FLD-03 exists to fix. The reference does the same thing this decision does:
  `sphinxlatexstyletext.sty:50` defines `\sphinxstyleliteralstrong#1{\sphinxbfcode{#1}}` and
  line 48 defines `\sphinxstyleliteralemphasis#1{\emph{\sphinxcode{#1}}}`. Rejected: variant B
  (type in regular monospace) and variant C (name in regular monospace).

- **D-06: FLD-03 is satisfied as written under D-05; do NOT amend REQUIREMENTS.md, and do not re-open this at verify time.**
  FLD-03's mechanical demand is that the name and type "carry monospace treatment **distinct from
  the plain-bold field label**" — the label stays `strong(text("Parameters") + text(": "))`,
  proportional, so both are distinct from it. FLD-03's accompanying prose ("the reference
  deliberately uses a *different* recipe here than in the signature, and collapsing the two would be
  wrong") is also honoured: the signature's recipe is *name italic-mono, type regular-mono*
  (Phase 37 D-01), the field body's is *name bold-mono, type italic-mono* — the two recipes are
  different, even though the field body's **type** and the signature's **name** happen to land on
  the same face. The owner saw exactly that overlap in the rendering and accepted it. The mechanical
  assertion must be written **per sub-part** (name vs type vs label), never as one blanket check
  over the field body.

- **D-07: FLD-02's "inline prose" means the label and a single-value body share one line (owner choice).**
  Measured pre-phase behaviour, from the real build: `:returns: Nothing at all.` emits
  `strong(text("Returns") + text(": "))` and then, on the next line, `par({text("Nothing at all.")})`
  — so the label and the value render on **separate** lines, in the compiled PDF's extracted text as
  well. The multi-value half already works: two `:param:` entries emit `list({…}, {…})` and one
  entry emits `par({…})`. So FLD-02's bulleted half is a **non-regression** obligation, and the
  inline half is real work. REQUIREMENTS.md's parenthetical ("the inline half already works via
  `_last_field_body_was_inline`") is **stale as a description of the docstring case**: that flag is
  only set when *every* child of `field_body` is inline, which happens for a docutils-collapsed body
  (a confval `:default:` written on the field's own line) but not for the ordinary
  `:param:`/`:returns:` docstring case, where docutils wraps the value in a `paragraph`. Do not take
  the parenthetical as evidence that nothing needs doing.

- **D-08: the reason this matters is measured, not aesthetic.**
  Vertical rhythm in the real pre-phase build, read from `here().position()` markers injected into
  the emitted `.typ`: `Parameters:` → its first bullet **14.245pt**; bullet → bullet **14.388pt**;
  two ordinary paragraphs **20.438pt**; and each single-value field — `Returns:` → `Return type:` →
  `Raises:` — **40.733pt**, because the bare label becomes one paragraph and the `par()` value
  becomes a second. Three different vertical intervals inside one field-list block. Under D-07 each
  single-value field costs one interval (20.438pt) instead of two, and the block reads as one
  rhythm. Whole-document consequence, measured on this project's own docs: **97 pages → 87 pages.**

### Interactions this phase must not walk into

- **D-09: `literal_strong` and `literal_emphasis` must stop delegating through the dummy-node trick, exactly as Phase 36's ADM-06 did for `desc_signature` and `rubric`.**
  They are the last two sites still constructing a throwaway `nodes.strong()` / `nodes.emphasis()`
  and calling the other handler's visitor (`translator.py:5745-5767`). D-05 makes their emission
  diverge from `strong` / `emph`, so the delegation has to go. Whether the replacement is a fourth
  and fifth verbatim copy (Phase 36 D-01 accepted triplication deliberately) or a shared helper is
  Claude's call — see D-12 — but the delegation itself is not a viable base to build D-05 on.
  Note also Phase 36 D-02: the shared `_strong_was_*` attribute names cause a `par()`-loss leak, and
  repairing that is **Phase 39's** deferred work, not this phase's. Do not fold it in; just do not
  make it worse.

- **D-10: Phase 38 voids the premise of Phase 37's SIG-08 fix, and must own the consequence.**
  `depart_desc` suppresses a duplicate `parbreak()` by testing `self._desc_break_marker ==
  len(self.body)` — i.e. "was anything emitted between the two departs"
  (`37-EMISSION-CONTRACT.md` §8). That test was designed while `depart_desc_content` was `pass`.
  Under D-01 it emits the `pad`'s closer, so `len(self.body)` **always** advances between an inner
  and an outer `depart_desc` and the suppression can never fire for a nested `desc` again.
  Reproduced on the prototype: the same sample emits 5 top-level `parbreak()` statements before the
  change and 6 after, with the breaks now landing at different `pad` depths rather than adjacent.
  The planner must decide, with a fixture, whether the new emission is correct as-is or needs the
  bookkeeping reshaped — **and must not simply assume Phase 37's mechanism still holds.**

- **D-11: the wrapper must not fight `block(sticky: true, …)`.**
  Measured on a deliberately short page: with `pad` around the body, a signature at a page boundary
  still keeps its body's first line on its own page, and a body that crosses a page break keeps its
  indent on the following page (left edge 47.5pt on both pages). So SIG-09 survives D-01 — but this
  is a property to assert, not to assume, because it is exactly what a wrapper change could break.

### Claude's Discretion

Recorded so planning does not re-open them with the owner.

- **D-12: the indent primitive and the emission mechanics are Claude's to choose, decided by measurement.**
  `pad(left: …, { … })` is what the prototype used and what every number above was measured
  through; `block(inset: (left: …), …)` is the obvious alternative and differs in its own
  above/below spacing. Binding constraints on whatever is chosen: it must compose on nesting without
  a counter (D-01), must not add vertical space that re-opens SIG-08's doubled-gap shape
  (`37-EMISSION-CONTRACT.md` §3's amendment), must survive a page break with the indent intact
  (D-11), and must route through `self.add_text(...)` rather than `self.body.append(...)` — the
  prototype proved the latter breaks inside a table, because `add_text` routes into
  `table_cell_content` and a direct `body.append` does not. The same freedom covers the newline and
  `list_item_needs_separator` bookkeeping around the wrapper, and the mechanics of D-07's inline
  field (the prototype achieved it by post-processing the emitted `.typ`, which is *not* an
  acceptable implementation — it was a rendering device for the owner's review only).

- **D-13: the stray `parbreak()` at the head of each bulleted field-list item is Claude's to fix or leave.**
  Measured: each `list({…})` item currently opens with a `parbreak()` and a blank line, which adds
  **7.15pt** before the first bullet (14.245pt with it, 7.15pt without) and nothing between items.
  Cosmetic, inside a handler this phase rewrites anyway. Not raised with the owner. If it is
  touched, it needs its own assertion; if it is left, say so explicitly rather than silently.

- **D-14: the exact-string migration strategy is Claude's to choose, under one non-negotiable constraint.**
  ROADMAP SC#5 requires this phase's blast radius to be migrated **inside the phase by hand-derived
  expected strings plus a recorded census**. Milestone invariant #4 forbids regenerating expected
  strings from the new code's output. Both hold regardless of which files the census turns out to
  contain. Starting points, all of which assert on bytes this phase changes:
  `tests/test_confval_field_spacing_render_gate.py`, `tests/test_confval_field_body_render_gate.py`,
  `tests/test_pdf_render_gate.py`, `tests/test_translator.py`. Re-measure the census; do not inherit
  Phase 37's.

### Folded Todos

Two of the three real matches are folded; the third is not (see Reviewed Todos). The owner delegated
the selection ("claude おすすめ") and these are the picks, with the reason each is structural rather
than opportunistic.

- **`.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md`** —
  `_desc_break_marker` compares `len(self.body)` across two `depart_desc` calls, but `self.body` is
  reassigned at five sites (`in_table` is guarded; `visit_term`/`visit_definition` via
  `_saved_body_stack`, the admonition title, and the figure caption are not), so the recorded
  integer can index a different list. Folded because **D-10 forces this phase into that exact state
  machine anyway** — Phase 38 invalidates the marker's premise, so the phase that re-derives the
  bookkeeping is the phase that should make it buffer-safe. The todo's own instruction is binding:
  build a `desc`-inside-a-glossary-definition fixture, record it RED against the current tree, and
  only then choose the fix (the todo suggests recording `(id(self.body), len(self.body))` rather
  than adding a sixth per-site guard).
- **`.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md`** —
  `EXPECTED_PAGE_COUNT_PRE_PHASE` in `tests/test_signature_page_boundary_render_gate.py` holds a
  post-`37-09` value. Folded because Phase 38 **measurably moves page counts** (97 → 87 on this
  project's own docs), so that constant must be re-measured inside this phase regardless; renaming
  it in the same commit costs nothing and stops the name from lying twice over.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and criteria

- `.planning/ROADMAP.md` § "Phase 38: Structural Indentation + Info Fields" — the goal and the five
  success criteria. SC#4 is the grep property D-04 reads narrowly; SC#5 is what binds D-14.
- `.planning/ROADMAP.md` § "🚧 v0.7.0 — API rendering design overhaul" — the binding constraints,
  especially #2 (the LaTeX reference is a starting point, not an authority — this is what licenses
  D-04's divergence) and #3/#4 (GATE-01's RED is structural for this milestone, because every defect
  here compiles fine today).
- `.planning/REQUIREMENTS.md` lines 64–101 — IND-01..IND-05 and FLD-01..FLD-03, with the ≈22–25pt
  reference quantum at lines 66–68 and the `[M]`/`[V]` legend at lines 8–21. Read D-01's note on
  IND-05's "counter" wording and D-07's note on FLD-02's stale parenthetical **before** treating
  either sentence as an implementation instruction.
- `.planning/REQUIREMENTS.md` lines 220–236 (Out of Scope) — in particular "Indenting a nested
  member's signature as far as its description" (covered positively by IND-03 / D-01), "Reusing the
  signature's italic-proportional parameter style for field-list parameter echoes", and "A literal
  grid/table layout for Parameters".
- `.planning/REQUIREMENTS.md` lines 237–256 — the six milestone invariants, notably #4 (RED is
  structural), #5 (test migration is owned per phase) and #6 ("anywhere under X" criteria are
  checked by repo-wide grep at discovery time).

### Prior phase context this one builds on

- `.planning/phases/37-signature-typography-the-desc-family/37-EMISSION-CONTRACT.md` — **the single
  most important upstream document.** §1 defines `SHARED_INDENT_STEP` and states in the source
  comment that Phase 38 reuses it; §3 (with its post-Wave-3 amendment) defines the signature wrapper
  `block(sticky: true, par(hanging-indent: 2.5em, {` and records the measured spacing regression
  that came from zeroing `above`/`below` — do not reintroduce that shape; §8 is the SIG-08 marker
  D-10 invalidates; §10 is the 453.54pt column measurement D-02 cites; §12 explicitly hands
  `visit_desc_content`/`depart_desc_content` to this phase.
- `.planning/phases/37-signature-typography-the-desc-family/37-CONTEXT.md` — D-01 (the per-sub-part
  signature recipe D-06 contrasts against), D-08 (the constant hand-off), D-09/D-10 (why Phase 37
  stayed out of `desc_content`, and the binding constraint that Phase 38's wrapper must not nest
  redundantly inside the signature's).
- `.planning/phases/36-shared-emission-seam-cleanup/36-CONTEXT.md` — D-01 (deliberate triplication
  of `visit_strong`'s body, the precedent D-09 follows) and D-02 (the shared `_strong_was_*`
  attributes and their `par()`-loss leak, which is **Phase 39's** to repair).
- `.planning/phases/37-signature-typography-the-desc-family/37-SPACING-FINDING.md` — the rasterised
  evidence that a wrapper's vertical spacing can silently overlap a signature with its own body's
  first line. The same failure mode is reachable from D-01's wrapper; this is the record of how it
  was caught.

### The reference (starting point, not authority)

- `.venv/lib/python3.13/site-packages/sphinx/texinputs/sphinxlatexstyletext.sty:48, 50` —
  `\sphinxstyleliteralemphasis#1{\emph{\sphinxcode{#1}}}` and
  `\sphinxstyleliteralstrong#1{\sphinxbfcode{#1}}`. This is D-05's evidence.
- `.venv/lib/python3.13/site-packages/sphinx/util/docfields.py:299, 315` — `TypedField.make_field`
  builds the parameter name as `addnodes.literal_strong` and the type as
  `addnodes.literal_emphasis`. This is why D-05's two handlers are the whole of FLD-03.

### Code under change

- `typsphinx/translator.py:23-29` — `SHARED_INDENT_STEP` and the comment that already names Phase 38
  as its second consumer.
- `typsphinx/translator.py:5102-5110` — `visit_desc_content` / `depart_desc_content`, both `pass`.
- `typsphinx/translator.py:5332-5359` — `visit_field_list` / `depart_field_list`, including the
  bug #4 list-item separator that D-12's bookkeeping has to preserve.
- `typsphinx/translator.py:5361-5390` — `visit_field` / `depart_field`, including FID-09's
  inter-field `"  "` separator and the CR-01 reasoning for why it only fires on collapsed-inline
  bodies. D-07 changes which bodies are inline, so this comment's premise must be re-read.
- `typsphinx/translator.py:5392-5419` — `visit_field_name` / `depart_field_name`, the
  `strong(` … `+ text(": "))\n` label emission whose trailing newline is what forces the value onto
  the next line.
- `typsphinx/translator.py:5421-5464` — `visit_field_body` / `depart_field_body` and the
  `_field_body_stack` / `_in_field_body` / `_last_field_body_was_inline` machinery.
- `typsphinx/translator.py:5745-5767` — `visit/depart_literal_strong` and
  `visit/depart_literal_emphasis`, the two remaining dummy-node delegations (D-09).
- `typsphinx/translator.py:4798-4855` — `depart_desc`; the marker test itself is at 4851-4854, and
  the ~50-line docstring above it states the premise D-10 invalidates ("if nothing has been appended
  to `self.body` since the immediately preceding desc's own `parbreak()` was recorded"). That
  docstring must be corrected, not just the code.
- `typsphinx/translator.py:2920-2985` — `visit_block_quote` / `depart_block_quote`, listed so the
  planner can confirm D-04's "no literal here" claim rather than take it on trust.

### Project standing rules

- `CLAUDE.md` § "Worktree-isolated execution" — worktree isolation is the standing execution mode;
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then `uv run …` is mandatory
  for every executor, not conditional.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — untouched by this phase (nothing here adds a
  package), but "no new lockstep site" is a milestone invariant.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured starting state (2026-08-01, real `sphinx-build -b typst`)

Source: a `py:class:: pkg.mod.Widget(name, size=10)` with a `:param:`/`:type:`/`:returns:`/`:rtype:`/
`:raises:` field list, containing a `py:method:: resize(width, height) -> None` with its own field
list, containing a `py:attribute:: inner`; then a sibling top-level `py:function:: toplevel(a)`.

Emitted `.typ` (abridged; Phase 37's signature shape is already in place):

```typst
block(sticky: true, par(hanging-indent: 2.5em, {raw("class")
…
strong(raw("Widget"))
raw("(") + emph(raw("name")) + … + raw(")")}))
[#metadata(none) <index:pkg.mod.Widget>]
par({text("A widget class body paragraph.")})     ← flush with the signature: IND-01's defect

strong(text("Parameters") + text(": "))            ← label, own paragraph
list({
parbreak()                                         ← D-13's stray break, +7.15pt
strong({text("name")})                             ← FLD-03's defect: bold PROPORTIONAL
text(" (")
emph({text("str")})                                ← FLD-03's defect: italic PROPORTIONAL
…
strong(text("Returns") + text(": "))
par({text("Nothing at all.")})                     ← D-07's defect: value on its own line
```

Compiled-PDF confirmation from the same run: `Parameters:` / `• name (str) – …` / `Returns:` /
`Nothing at all.` — the label/value split is visible in the output, not only in the source.

### Reusable assets

- **`quote(block: true, { … })` in `visit_block_quote` (`translator.py:2944-2958`)** — the existing,
  proven pattern for wrapping a run of code-mode body statements in a call that takes a content
  block. D-01's wrapper is the same shape; reuse its reasoning about why the body must be `{ … }`
  (code mode) and never `[ … ]` (markup mode), which is bug #15's fatal.
- **`self.add_text(...)`** — the buffer-aware writer. The prototype proved that
  `self.body.append(...)` produces broken output inside a table, because `add_text` routes into
  `table_cell_content` and a direct append does not (D-12).
- **`_add_paragraph_separator()` / `_emit_inline_concat_separator()` / `_mark_inline_concat_content()`** —
  the separator trio every inline emitter uses; `visit_literal` (`translator.py:1282-1360`) is the
  reference implementation and is also the existing proven `raw("…")` emission path D-05 needs,
  including its escaping.
- **`escape_typst_string(...)`** — the single source of truth for string-literal escaping. Note the
  load-bearing step order from `37-EMISSION-CONTRACT.md` §4: escape first, then inject `\u{200B}`,
  never the reverse.
- **`_emit_forced_break("parbreak()")` and `_desc_break_marker`** — the SIG-08 machinery D-10 puts
  back in play.

### Established patterns and constraints

- **The block-visitor separator pattern (bug #4)** — every block visitor emits a leading `"\n"` when
  `self.in_list_item and self.list_item_needs_separator`, and sets the flag on depart. Both
  `visit_field_list` and `visit_block_quote` already carry it. Any new wrapper must not break it:
  the failure mode is a Typst "expected semicolon or line break" fatal from a juxtaposed expression.
- **`in_table` routes emission elsewhere** — see `add_text` and the `not self.in_table` guard in
  `depart_desc`. A `desc` inside a table cell is reachable and must not be assumed away.
- **`self.body` is reassigned at five sites**, not one — `in_table` plus `visit_term`,
  `visit_definition`, the admonition title and the figure caption. This is the folded todo's subject
  and a hazard for any new position-based bookkeeping.

### Integration points

- `tests/test_corpus_gate.py` — the full-corpus `-b typstpdf` gate, `@pytest.mark.slow` and excluded
  from the default run by `-m "not slow"`; run it explicitly. A cached corpus already exists at
  `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/`.
- `tests/test_signature_page_boundary_render_gate.py` — page counts move under this phase; see the
  second folded todo.
- This project's own `docs/source` — a real autodoc corpus, and the one the owner's D-02 decision was
  made against. Building it outside `tox` needs `sphinx-autodoc-typehints` and `sphinx-intl` (the
  `docs` extra), which the default dev environment does not install.

</code_context>

<specifics>
## Specific Ideas

- **The owner decided against real compiled pages, not against descriptions** — the same standard
  Phase 37 set. D-05 was chosen from four side-by-side renderings with the Phase 37 signature line
  shown above each for comparison; D-02 from four real PDFs of this project's own documentation,
  including a control page built from the unmodified translator. Any later trade-off in this area
  should be resolved the same way: render it, then decide.
- **Two claims that were checked against reality this session and would have been wrong if assumed.**
  (1) REQUIREMENTS.md's "the inline half already works via `_last_field_body_was_inline`" does not
  hold for the ordinary docstring case (D-07). (2) Within the monospace family, `raw`, `emph(raw)`
  and `strong(raw)` have **identical** advance widths — measured 105.96pt for
  `Iterable[str] | None` in all three — so a variant choice among D-05's candidates changes no line
  widths; only proportional-vs-monospace does (`text(…)` measured 85.26pt for the same string).
  Measure before building on anything in the same family.
- **`SHARED_INDENT_STEP` at 2.5em sits just above REQUIREMENTS.md's ≈22–25pt reference quantum**
  (27.5pt at this project's 11pt body). The owner saw that stated, saw the 2.0em rendering that lands
  inside the band, and kept 2.5em. This is a deliberate divergence, not an oversight.

</specifics>

<deferred>
## Deferred Ideas

- **Nothing new was deferred from this discussion.** Scope stayed inside IND-01..05 and FLD-01..03
  plus the two folded todos, both of which live in handlers this phase necessarily rewrites.

### Reviewed Todos (not folded)

`todo.match-phase 38` returned eleven records. Eight are keyword false positives on the matcher's
0.4–0.6 band and are dismissed for the same reasons Phase 37 recorded:
`2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md` → **Phase 39**;
`2026-07-22-citation-node-support-untracked.md` → **Phase 40**;
`2026-07-29-release-notes-body-from-changelog-section.md` → **Phase 41**;
`2026-07-25-derive-typst-lang-duplicated-warning-block.md` (`template_engine.py`),
`2026-07-29-project-md-unterminated-html-comments.md` (planning docs),
`2026-07-22-add-sphinx-linkcheck-ci-job.md` (Future LNK-01),
`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`, and
`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` (`CLAUDE.md` forbids doing it
opportunistically) — all unrelated to this phase's handlers.

The one real match that is **reviewed but not folded**:

- `.planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md`
  — an unescaped `*` in `visit_desc_sig_name`'s docstring emits a docutils warning and renders a
  stray `problematic` node in this project's own API-reference PDF. It is in the `desc_*` family and
  is a one-character fix, but `visit_desc_sig_name` is **not** a handler Phase 38 changes, and the
  defect gates no IND or FLD requirement. Left pending so the phase's blast radius stays honest;
  Phase 39 also edits `translator.py` and is the natural next carrier.

</deferred>

---

*Phase: 38-Structural Indentation + Info Fields*
*Context gathered: 2026-08-01*
