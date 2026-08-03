# Phase 38 — Emission Contract

**Authored:** 2026-08-01 (plan-phase)
**Status:** normative for every Phase 38 plan
**Purpose:** the single, hand-derivable specification of exactly what byte sequence each handler this
phase touches emits after Phase 38. Every expected string in this phase — the new gates, the migrated
pre-existing assertions, and `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` — is
derived **from this document**, never from running the new code (ROADMAP SC#5, milestone
invariant #4).

Provenance of every figure below: measured **2026-08-01** by the discussion session
(`38-CONTEXT.md`, real `sphinx-build -b typst` + `typst.compile()` + a full working prototype over
this project's own `docs/source`) and independently re-verified the same day by the research session
(`38-RESEARCH.md`, three `typst.compile()` probes plus a patch-and-rebuild of the project's own
`tests/fixtures/signature_break_and_arrow_gate`). Nothing here rests on recall. Where a byte is
**specified rather than measured**, it is labelled `[specified]` and the reason is given.

---

## 0. Why this document exists

ROADMAP SC#5 and milestone invariant #4 forbid regenerating expected strings from the new code's own
output. That is only enforceable if a specification exists that is precise enough for a human — or an
executor with no access to the new code — to write the expected bytes down first. This document is
that specification. If an assertion and this document disagree, **re-derive the assertion from this
document**; never paste what the translator printed. If the *translator* and this document disagree
and the translator is right, **amend this document with the measured reason** (the Phase 37 §3
amendment is the precedent) — do not silently update the assertion.

---

## 1. No new constant (IND-04, D-02)

`SHARED_INDENT_STEP = "2.5em"` already exists at `typsphinx/translator.py:29`, introduced by Phase 37
(D-08) with a source comment that already names Phase 38 as its second consumer. **Phase 38 defines no
new indent constant and changes no existing value.** D-02 locks `"2.5em"`; the rejected 2.0em and
1.5em renderings are recorded in `38-CONTEXT.md` D-02 so nobody resurrects them as an "improvement".

Because the value does not move, Phase 37's `golden.typ` signature lines, its render gates, and
`37-EMISSION-CONTRACT.md` §3/§9/§10 need **no** re-derivation on account of the constant. They need
re-derivation only because of §2 below (a new wrapper is inserted *around the body*, never around the
signature).

### 1.1 SC#4's grep property, measured at discovery time

Milestone invariant #6 requires "anywhere under X" criteria to be checked by a repo-wide grep at
discovery time. Run 2026-08-01 during planning, over the whole of `typsphinx/`:

| Match | File:line | Is it a desc / field-list / block-quote indent? |
|---|---|---|
| `2em`, `1em`, `1.2em`, `0.5em` | `typsphinx/templates/base.typ:69-72` | No — the title block's font size and vertical spacing |
| `inset: 8pt`, `stroke: 0.5pt`, `radius: 2pt` | `typsphinx/translator.py:4757` | No — the `desc_signature` fallback box |
| `h(0.6em)` | `typsphinx/translator.py:2021` | No — an **indented comment** describing Typst's own `terms()` default separator; nothing is emitted |
| `0pt` / `13.2pt` | `typsphinx/translator.py:4887-4893, 4959` | No — **docstring** prose recording Phase 37's §3 amendment measurements |
| `SHARED_INDENT_STEP` | `typsphinx/translator.py:29, 4964` | Yes — the one definition and its one existing consumer |

`grep -rn 'pad(' typsphinx/` returns **nothing**: Phase 38 is the first use of the primitive in this
codebase. So SC#4's checkable property — "a repo-wide grep over `typsphinx/` finds no second
independent indent literal at those sites" — **is already true pre-phase and must stay true**, since
§2 and §3 below both spell `SHARED_INDENT_STEP` and neither introduces a literal.

**The mechanical form of the SC#4 assertion** (a `== 0` gate on an unfiltered file would count this
document's own prose and every docstring, so it is forbidden): over
`typsphinx/translator.py` with full-line **and** indented comments filtered out
(`grep -vE '^[[:space:]]*#'`), a search for a numeric `em`-suffixed literal returns **exactly one**
line — the `SHARED_INDENT_STEP` assignment at line 29. Record the verbatim command and its output.

### 1.2 `block_quote` is deliberately NOT converted (D-04, binding)

`visit_block_quote` / `depart_block_quote` (`typsphinx/translator.py:2920-2982`) are **not touched by
this phase.** `block_quote` takes its indent from Typst's own `quote(block: true, …)` default,
measured at **11.0pt** (1em at 11pt) against the shared constant's 27.5pt. Both alternatives were
compiled and shown to the owner and both were rejected: wrapping the quote in a `pad` lands at
27.5 + 11.0 = 38.5pt (the constant would stop matching the depth it produces), and dropping `quote()`
for a bare `pad` reaches 27.5pt but loses `quote()`'s own vertical spacing and destroys
`visit_attribution`'s right-aligned attribution contract. IND-04's purpose is to forbid per-node magic
numbers, not to force every indent context onto one visual depth. **Do not re-open this at verify
time.**

---

## 2. `desc_content` — the body wrapper (IND-01/02/03/05, D-01, D-12)

**Open** — `visit_desc_content`, replacing the current `pass`:

    pad(left: 2.5em, {

built as `f"pad(left: {SHARED_INDENT_STEP}, {{"`, routed through `self.add_text(...)`.

**Close** — `depart_desc_content`, replacing the current `pass`:

    })\n

routed through `self.add_text("})\n")`.

### 2.1 `self.add_text`, never `self.body.append` (D-12, binding)

The prototype proved a direct `self.body.append(...)` produces broken output inside a table cell,
because `add_text` routes into `table_cell_content` and a bare append does not. Every byte this phase
emits goes through `add_text`. This also applies to the two **pre-existing** `self.body.append`
calls this phase's own touch surfaces — see §3.1.

### 2.2 The trailing newline on the close is load-bearing `[specified]`

`38-RESEARCH.md`'s Code Examples show `self.add_text("})")` with no trailing newline. This contract
**specifies `"})\n"` instead**, for one reason: `depart_desc` immediately follows with
`_emit_forced_break("parbreak()")`, which prepends no newline of its own outside a list item. A bare
`"})"` would therefore juxtapose the `pad(...)` expression against `parbreak()` on one physical source
line, which is the Typst "expected semicolon or line break" fatal class this codebase has already hit
four separate times (bug #4 / GATE-02 fatals #8, #12, #18). `depart_block_quote` — the direct analog,
the only other handler that wraps a run of code-mode body statements in a call taking a content block —
already emits `"})\n\n"` for exactly this reason. The extra newline is cosmetic in Typst and cannot
change rendering; its absence can abort the build. The safe form is specified.

If a real build shows the bare form is also valid, that is a contract amendment (§0), not a licence to
change assertions.

### 2.3 Composition — no depth counter (D-01, binding)

Nesting is left to compose structurally. **There is no depth counter and none may be introduced**,
including to make IND-05's "the nesting-depth counter resets correctly" wording literal. Under D-01 no
counter exists; **IND-05 is asserted, not implemented.** A counter must be manually reset at every
sibling boundary and is precisely the leak failure mode IND-05 exists to prevent.

Measured left edges from the compiled probe (11pt body, page margin 20.0pt):

| Site | x | Requirement it satisfies |
|---|---|---|
| class `desc_signature` | 20.0pt (page margin) | — |
| class `desc_content` body | 47.5pt (+27.5) | IND-01 |
| nested method `desc_signature` | 47.5pt — **equal** to the class body | IND-03 |
| nested method `desc_content` body | 75.0pt (+27.5) | IND-02 |
| class body continuing after the nested member | 47.5pt | IND-02 |
| sibling top-level `desc` after the nest | 20.0pt | IND-05 |

The nested signature receives no further step because it is plain content flowing inside the
still-open outer `pad`, not itself wrapped. IND-05 cannot leak because the `pad` closes when
`depart_desc_content` runs.

### 2.4 The empty-body case

Sphinx creates a `desc_content` node even when the directive has no body (a body-less `confval`, a
bare `py:function::`). The wrapper pair is therefore emitted around an empty content block. This must
compile, and `tests/test_desc_bodyless_concat_render_gate.py` — the FID-06 sibling body-less control —
must stay green.

### 2.5 `block(sticky: true, …)` must survive (D-11)

Measured on a deliberately short page with the wrapper in place: a signature at a page boundary still
keeps its body's first line on its own page, and a body crossing a page break keeps its indent on the
following page (left edge 47.5pt on both pages). SIG-09 survives D-01 — **assert it, do not assume
it**, because a wrapper change is exactly what could break it.

### 2.6 Separator bookkeeping around the wrapper (D-12, Claude's discretion)

Whether `visit_desc_content` needs `visit_block_quote`'s bug #4 leading-newline guard
(`if self.in_list_item and self.list_item_needs_separator: self.add_text("\n")`) and whether
`depart_desc_content` should set `list_item_needs_separator = True` is the executor's call under D-12,
**decided by the fixture**: a `desc` inside a list item and a `desc` inside a table cell are both in
scope, and `tests/test_field_list_in_list_item_render_gate.py` plus
`tests/test_desc_bodyless_concat_render_gate.py` are the controls that settle it. Whatever is chosen
must not break the block-visitor separator pattern; the failure mode is a Typst "expected semicolon or
line break" fatal from a juxtaposed expression.

---

## 3. `field_list` — the second, independently nested step (FLD-01, D-03)

**Open** — `visit_field_list`, after the existing bug #4 separator guard, which is unchanged:

    pad(left: 2.5em, {

built as `f"pad(left: {SHARED_INDENT_STEP}, {{"` via `self.add_text(...)`.

**Close** — `depart_field_list`, replacing the current bare `self.body.append("\n")`:

    })\n

via `self.add_text("})\n")`. The existing
`if self.in_list_item: self.list_item_needs_separator = True` is unchanged.

FLD-01 asks for one step beyond the surrounding description body; under §2's composition that is
simply a second `pad` inside the first, and it needs **no separate constant**. Measured in the
prototype's real PDF: class body 27.5pt → method body 55.0pt → the method's `Parameters:` block
82.5pt, against a measured text column of 453.54pt (`37-EMISSION-CONTRACT.md` §10).

### 3.1 A latent pre-existing bug this phase's own touch surfaces (D-12)

`depart_field_list`'s pre-phase `self.body.append("\n")` bypasses `add_text` entirely, so a
`field_list` inside a table cell misroutes **today**. The line must change to `self.add_text(...)`
regardless of the wrapper. The same is true of `depart_field`'s `self.body.append('\ntext("  ")\n')`
(line 5390), `visit_field_name`'s `self.body.append("strong(")` (5403), `depart_field_name`'s
`self.body.append(' + text(": "))\n')` (5414) and `depart_field_body`'s `self.body.append("\n")`
(5464). Converting these five sites to `add_text` is **byte-identical outside a table** and is the
correct scope for this phase; it is not a licence to change what they emit.

---

## 4. Field bodies — inline single value, bulleted multi value (FLD-02, D-07, D-08)

### 4.1 Measured starting state

Pre-phase, from the real build:

- `:returns: Nothing at all.` emits `strong(text("Returns") + text(": "))` and then, on the **next
  line**, `par({text("Nothing at all.")})`. The label and value render on separate lines in the
  compiled PDF's extracted text as well as in the source.
- Two `:param:` entries emit `list({…}, {…})`; one entry emits `par({…})`.

So FLD-02's bulleted half is a **non-regression obligation** and the inline half is the real work.
REQUIREMENTS.md's parenthetical ("the inline half already works via `_last_field_body_was_inline`") is
**stale as a description of the docstring case**: that flag is set only when *every* child of
`field_body` is inline, which happens for a docutils-collapsed body (a `confval` `:default:` written
on the field's own line) but not for the ordinary `:param:`/`:returns:` docstring case, where docutils
wraps the value in a `paragraph`.

### 4.2 Root cause and the shape of the fix

A single-value field body is **always exactly one `nodes.paragraph`** — verified by reading
`sphinx/util/docfields.py:140-183,201-244` (`Field.make_field` and `GroupedField.make_field`'s
`can_collapse` branch). The defect is that `visit_paragraph` unconditionally wraps it in Typst's
`par(...)`, which is intrinsically block-level and therefore starts a new visual paragraph regardless
of any separator bookkeeping.

The fix classifies that shape in `visit_field_body`
(`len(node.children) == 1 and isinstance(node.children[0], nodes.paragraph)`), activates the
**existing** `_in_field_body` / `_field_body_has_content` inline-concat context, and adds a branch to
`visit_paragraph`/`depart_paragraph` that skips the `par({` / `})` wrapper — mirroring the
`self.in_list_item` fast-path that already exists in both. The paragraph's children then dispatch
completely unmodified through the same `_emit_inline_concat_separator` / `_mark_inline_concat_content`
machinery the collapsed-inline case already exercises. **Do not invent a second concat mechanism.**

### 4.3 The observable contract (this is what the gates assert)

Mechanics are the executor's under D-12. These three properties are not:

1. **Inline join.** A single-value field's label and value are adjacent on ONE line of the compiled
   PDF's extracted text. Pinned string for the gate fixture, hand-derived here:
   `Returns: Nothing at all.` — one space after the colon, no line break.
2. **Fields stay separate paragraphs.** Two consecutive single-value fields must **not** run together
   on one line. `Returns:`, `Return type:` and `Raises:` each occupy their own paragraph. This is
   D-08's whole point, and it is a trap: `depart_field`'s FID-09 inter-field `"  "` separator is
   gated on `_last_field_body_was_inline`, so naively letting the new classification set that flag
   joins all three onto one line and produces a *zero* interval where D-08 measured 20.438pt.
   The FID-09 separator must therefore stay scoped to the **docutils-collapsed** case only. If that
   requires a state distinction between "collapsed-inline" and "single-paragraph-unwrapped", make it —
   the RESEARCH anti-pattern forbids a second *concat* mechanism, not a separator discriminator.
3. **The collapsed-inline case is byte-identical.** `tests/test_confval_field_spacing_render_gate.py`'s
   `PINNED_SC3_STRING = "Type: int (a number)  Default: 42"` and
   `tests/test_confval_field_body_render_gate.py`'s
   `'text("The value of ") + strong({text("html_title")})'` must both stay green **unchanged**. Those
   two fields legitimately DO share one line via FID-09.

### 4.4 Measured vertical rhythm this changes (D-08)

Read from `here().position()` markers injected into the emitted `.typ` of the real pre-phase build:
`Parameters:` → its first bullet **14.245pt**; bullet → bullet **14.388pt**; two ordinary paragraphs
**20.438pt**; and each single-value field — `Returns:` → `Return type:` → `Raises:` — **40.733pt**,
because the bare label is one paragraph and the `par()` value is a second. Three different vertical
intervals inside one field-list block. Under the fix each single-value field costs one interval
(20.438pt) instead of two. Whole-document consequence, measured on this project's own docs:
**97 pages → 87 pages.**

### 4.5 D-13 — the stray `parbreak()` at the head of each bulleted item: **LEFT IN PLACE**

D-13 is Claude's discretion and requires an explicit statement either way. **Decision, taken at plan
time: leave it untouched.**

Evidence, from the grep `38-RESEARCH.md` Open Question 2 asked for, run 2026-08-01 during planning:
`tests/test_inline_math_after_text_render_gate.py:291` pins the exact shape
`"list({\nparbreak()\n\nmi(`a+b`)"`. The break is emitted by `visit_paragraph`'s **`self.in_list_item`
fast-path**, which fires for *every* list item in the document — not only field-list bullets — so
removing it changes bullet, enumerated and definition lists repo-wide. That is a cosmetic ~7.15pt
change (14.245pt with it, 7.15pt without, nothing between items) with a repo-wide blast radius and an
already-pinned falsifier, sitting outside FLD-02's actual requirement. Lower-risk default: leave it,
and record it here rather than silently.

This decision must be restated in `38-TEST-CENSUS.md` and in the phase closeout, not left in planning.

---

## 5. `literal_strong` / `literal_emphasis` (FLD-03, D-05, D-06, D-09)

### 5.1 Measured starting state and the delegation to remove

Both handlers currently construct a throwaway `nodes.strong()` / `nodes.emphasis()` and call the other
handler's visitor (`typsphinx/translator.py:5745-5767`) — the last two dummy-node delegation sites in
the translator, the same trick Phase 36's ADM-06 removed for `desc_signature` and `rubric`. Today the
parameter name emits `strong({text("name")})` (bold **proportional**) and the type
`emph({text("str")})` (italic **proportional**); neither is monospace, which is what FLD-03 exists to
fix. D-05 makes their emission diverge from `strong` / `emph`, so the delegation cannot remain.

### 5.2 Target shapes (D-05, owner choice, variant "A")

| Node | Post-phase emission | Reference |
|---|---|---|
| `literal_strong` (parameter name) | `strong(raw("<escaped>"))` — bold monospace | `sphinxlatexstyletext.sty:50`, `\sphinxstyleliteralstrong#1{\sphinxbfcode{#1}}` |
| `literal_emphasis` (parameter type) | `emph(raw("<escaped>"))` — italic monospace | `sphinxlatexstyletext.sty:48`, `\sphinxstyleliteralemphasis#1{\emph{\sphinxcode{#1}}}` |
| `field_name` (the label) | `strong(text("Parameters") + text(": "))` — **unchanged**, proportional bold | — |

`<escaped>` is `escape_typst_string(node.astext())` — the shared helper `visit_literal`'s leaf branch
already uses. Emission is the `visit_literal` leaf idiom: `_add_paragraph_separator()`, the
`_emit_inline_concat_separator()` fallback, the `f'{prefix}…'` emission with
`prefix = "#" if self._in_markup_mode else ""`, the `_mark_inline_concat_content()` fallback, then
`raise nodes.SkipNode`. The two `depart_*` methods become unreachable (as `depart_literal` already is)
and stay as stubs for docutils' dispatcher contract.

Whether the two bodies are verbatim copies (Phase 36 D-01's deliberate triplication, which D-09 cites
as the precedent) or share a small private helper is the executor's call under D-12. What is **not**
optional: the delegation goes, and the escaping helper is `escape_typst_string`.

### 5.3 The trap: `_emit_signature_leaf_wrapper` must not be reused

Phase 37's `_emit_signature_leaf_wrapper` already produces `wrapper(raw("…"))` and is therefore the
tempting shortcut. It calls `_escape_signature_text`, which unconditionally injects the SIG-07
zero-width-space break opportunity after every `.`. **No FLD requirement or CONTEXT decision authorizes
that injection in a field body.** Field bodies are not measured to overflow the way dotted signature
qualnames are, and adding it here would smuggle new, unauthorized, unmeasured behaviour in under an
unrelated refactor.

**The mechanical form of this assertion is an OUTPUT assertion, not a source grep:** no zero-width
space — neither the literal U+200B byte nor its 8-character Typst escape — appears anywhere inside a
field body's emitted bytes. That proves the wrong helper was not used without grepping the source for a
helper name.

### 5.4 Cross-reference composition (Pitfall 2)

A `:type:` whose value resolves as a cross-reference produces `literal_emphasis` **nested inside** a
`reference` node, which the translator renders as `link(<label>, …)`. Measured pre-phase shape:
`link(<index:Widget>,` newline `emph({text("Widget")}))`. Post-phase this becomes
`link(<index:Widget>, emph(raw("Widget")))`. **Do not special-case it**: the generic leaf-emission body
composes correctly because `link()`'s second argument is just a content value, exactly as
`visit_desc_sig_name` rule 3 already lets a resolved xref's `raw(...)` compose inside `link()` in the
signature family (`37-EMISSION-CONTRACT.md` §5.2). A test suite with only unresolved types (`int`,
`str`) would pass even if this were broken — the fixture must contain a resolvable `:type:`.

### 5.5 D-06 — FLD-03 is satisfied as written; assert per sub-part

FLD-03's mechanical demand is that the name and type carry monospace treatment **distinct from the
plain-bold field label**. The label stays proportional, so both are distinct from it. FLD-03's prose
("the reference deliberately uses a different recipe here than in the signature") is also honoured:
the signature's recipe is *name italic-mono, type regular-mono* (Phase 37 D-01), the field body's is
*name bold-mono, type italic-mono*. The two recipes differ, even though the field body's **type** and
the signature's **name** land on the same face; the owner saw exactly that overlap in the rendering and
accepted it. **Do NOT amend REQUIREMENTS.md and do not re-open this at verify time.**

The assertion must be written **per sub-part** — name vs type vs label, three separate checks — never
as one blanket check over the field body.

### 5.6 Within-family width note

Measured: `raw`, `emph(raw)` and `strong(raw)` have **identical** advance widths (105.96pt for
`Iterable[str] | None` in all three), while the proportional `text(...)` form measures 85.26pt for the
same string. A variant choice inside the monospace family changes no line widths; proportional →
monospace does. Field-list lines therefore get *wider* under this phase, which is one input to the
page-count re-measure in §7.

---

## 6. `depart_desc`'s SIG-08 marker (D-10) and the folded buffer-swap todo

### 6.1 The premise Phase 38 voids

`depart_desc` suppresses a duplicate `parbreak()` by testing `self._desc_break_marker == len(self.body)`
— "was anything emitted between the two departures" (`37-EMISSION-CONTRACT.md` §8). That test was
designed while `depart_desc_content` was `pass`. Under §2 it emits the `pad`'s closer, so
`len(self.body)` **always** advances between an inner and an outer `depart_desc` and the suppression
can never fire again for a nested `desc`.

**Reproduced empirically** by the research session, on the project's own existing
`tests/fixtures/signature_break_and_arrow_gate` fixture (`SigBreakOuterClassOne` is exactly the
"nested `desc` with no trailing sibling content" shape): patching `depart_desc_content` to emit any
byte takes the fixture from **8** total `parbreak()` to **9**, with two adjacent breaks reappearing at
the nested member's boundary.

### 6.2 The fix — marker propagation through `depart_desc_content`

`depart_desc_content` records whether the marker still equals `len(self.body)` **before** emitting its
close, emits the close, and if it did, advances the marker past its own bytes. The outer
`depart_desc` then still sees "nothing happened" and correctly suppresses its own duplicate.
`depart_desc` itself needs **no code change** under this fix.

Verified by the research session to restore the count from 9 to **8**, matching the pre-phase baseline
exactly including which boundary gets which count. `SigBreakOuterClassTwo` (the "content follows the
nested member" control) is unaffected in all three variants compiled — pre-phase, broken, and fixed.

D-10 requires the planner to decide **with a fixture** rather than assume Phase 37's mechanism still
holds. The decision recorded here: adopt marker propagation, and prove it with an assertion that is
RED pre-phase. The count assertion alone cannot be RED pre-phase (it is already 8 and correct today),
so the RED must be a **conjunction**: the emitted `.typ` contains the body wrapper's opening and
closing tokens **and** the total `parbreak()` count is exactly 8. Pre-phase that fails on the wrapper's
absence; post-§2 without propagation it fails on the count; only the specified implementation satisfies
both.

### 6.3 `depart_desc`'s docstring premise must be corrected, not just the code

The ~50-line docstring at `typsphinx/translator.py:4816-4849` states the premise D-10 invalidates
("if nothing has been appended to `self.body` since the immediately preceding desc's own `parbreak()`
was recorded"). The sentence is still literally true, but the *reason* nothing is appended past a
suppressed nested `desc`'s break must now account for the pad closer being a "counts as nothing" byte
rather than "no bytes at all". **Correct the docstring in the same edit.**

### 6.4 The folded buffer-swap todo

`.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md` is folded into
this phase because D-10 forces it into the same state machine. `len(self.body)` indexes whichever list
`self.body` currently points at, and `self.body` is reassigned at **five** sites — `in_table` (guarded)
plus `visit_term` / `visit_definition` (via `_saved_body_stack`), the admonition title, and the figure
caption (all unguarded). A recorded integer can therefore index a different list, spuriously matching
(suppressing a needed break) or spuriously failing to match (emitting the doubled break SIG-08 removes).

The todo's own instruction is binding: **build the fixture first** (a `desc` inside a glossary
definition, plus a nested `desc` inside that), record the measured behaviour against the current tree,
and only then choose the fix. The suggested shape is to make the marker identify the *buffer* as well
as the position — recording `(id(self.body), len(self.body))` — rather than adding a sixth per-site
guard, since the existing `in_table` guard already demonstrates that per-site guards do not generalise.

**Honest handling if the fixture is GREEN pre-phase:** record the verbatim measurement, keep the
fixture as a non-regression control, and re-run it after §2 lands — the pad closer changes what the
marker sees, so the hazard's reachability changes with it. Do not retro-fit the fixture into a RED it
did not produce.

---

## 7. Pre-existing exact-string blast radius (SC#5 census input)

`38-TEST-CENSUS.md` (plan 38-04) is the authority; this is its **starting** input, to be re-measured by
reading assertions rather than grepping node names. D-14 forbids inheriting Phase 37's census.

**Expected to break** — hand-migrate from this document:

| File | Why | Contract § | Predicted owning plan |
|---|---|---|---|
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | byte-identity gate; every `desc_content` gains the wrapper pair | §2 | 38-05 |
| `tests/test_confval_field_spacing_render_gate.py` | `field_list` gains a wrapper; `PINNED_SC3_STRING` itself must stay green | §3, §4.3 | 38-06 |
| `tests/test_confval_field_body_render_gate.py` | same wrapper; the collapsed-inline assertion must stay green | §3, §4.3 | 38-06 |
| `tests/test_field_list_in_list_item_render_gate.py` | `field_list` inside a list item — the §2.6 / §3 separator interaction | §3 | 38-06 |
| `tests/test_pdf_render_gate.py` | PDF text/layout assertions over API pages | §2, §4, §5 | 38-05 / 38-07 |
| `tests/test_translator.py` | the `desc` and field-list structural assertions | §2, §3, §4, §5 | 38-05 / 38-06 / 38-07 |
| `tests/test_signature_page_boundary_render_gate.py` | page counts move; `EXPECTED_PAGE_COUNT_PRE_PHASE` is also the second folded todo's rename subject | §2, §4.4, §5.6 | 38-08 |
| `tests/test_signature_typography_multi_signature_page_count_gate.py` | `EXPECTED_PAGE_COUNT = 4` on a multi-signature page | §2, §4.4 | 38-08 |

**Expected to stay green, and serving as controls:**
`tests/test_desc_bodyless_concat_render_gate.py` (§2.4), `tests/test_signature_break_and_arrow_gate.py`
(§6.2 — its count must remain 8), `tests/test_inline_math_after_text_render_gate.py` (§4.5 — its pinned
`parbreak()` shape is why D-13 is left alone), `tests/test_signature_typography_gate.py`,
`tests/test_desc_signature_concat_render_gate.py`, `tests/test_rubric_option_concat_render_gate.py`
(rubric halves are Phase 39 territory and must not be edited).

**Page counts are a measurement, not an expected string.** Re-measuring a page count against the
post-phase build is legitimate and required (D-08 measures 97 → 87 on this project's own docs); pasting
an emitted `.typ` fragment into a golden is not. Keep the distinction explicit in every commit that
moves one.

---

## 8. Out of scope for Phase 38 (do not fold in)

- `desc_signature` and its inline children — Phase 37, complete. Its wrapper, hanging indent,
  per-sub-part treatment and `sticky: true` are fixed points. Phase 38 wraps *around the body*, never
  around the signature.
- `visit_block_quote` / `depart_block_quote` — D-04, §1.2.
- `rubric` and admonitions — Phase 39 (ADM-01..05). Phase 39's SC#3 depends on this phase's indent
  existing, but the rubric handler is Phase 39's to change.
- Citations — Phase 40.
- Renaming the shared `_strong_was_*` attributes and repairing their `par()`-loss leak — Phase 36 D-02,
  deferred to Phase 39. Do not fold it in; just do not make it worse.
- `visit_desc_sig_name`'s unescaped-asterisk docstring warning
  (`.planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md`) —
  reviewed and deliberately **not** folded; that handler is not one Phase 38 changes.
- Any new `@preview` package, any new runtime dependency, any new version-lockstep site.
- Anything that makes the styling user-overridable — Future STY-01/02/03.

---

*Phase: 38 — Structural Indentation + Info Fields*
*Emission contract authored: 2026-08-01 at plan time, from the measurements recorded in
38-CONTEXT.md, 38-RESEARCH.md and 38-PATTERNS.md*
