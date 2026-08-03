# Phase 37: Signature Typography — the `desc_*` Family - Research

**Researched:** 2026-08-01
**Domain:** Sphinx `desc_*` doctree → Typst signature typography (translator.py node handlers)
**Confidence:** HIGH — every load-bearing claim below was produced by running the real `sphinx-build`
against a live doctree, the real Sphinx v9.1.0 `doc/` corpus (already cached at
`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`), and the real `typst.compile()` (typst-py 0.15.0) this
session, not looked up. Where a finding rests on training knowledge only, it is explicitly tagged
`[ASSUMED]` and listed in the Assumptions Log.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: the signature is set entirely in monospace, with the parameter name the only italic (owner
  choice, "案B-1").** `desc_name`/`desc_annotation` → bold monospace (`strong(raw("…"))`);
  `desc_addname` → regular monospace (`raw("…")`); delimiters (`(` `)` `,` `=` `:`, `desc_optional`'s
  `[` `]`) → regular monospace; `desc_parameter`'s own parameter name → **italic** monospace
  (`emph(raw("…"))`); inline type annotation and default value inside `desc_parameter` → regular
  monospace (`raw("…")`). Measured font resolution: `strong(raw(…))` → `DejaVuSansMono-Bold`,
  `raw(…)` → `DejaVuSansMono`, `emph(raw(…))` → `DejaVuSansMono-Oblique` (real oblique face).
- **D-02: this deliberately diverges from the LaTeX reference (whole-parameter italic proportional),
  and that is allowed.** Both the reference recipe and an all-mono "whole parameter italic" variant
  were rendered and rejected by the owner.
- **D-03: SIG-04 is satisfied as written; do NOT amend REQUIREMENTS.md.** The mechanical assertion
  must be written **per sub-part** of `desc_parameter`, not as one blanket check.
- **D-04: `raw(...)` is the monospace primitive — not `text(font: …)`.** Proven: unaffected by the
  active `codly-init`/`#codly(...)` show rules; `visit_literal` already proves the primitive in the
  corpus; no new `@preview` package, no font configuration, no new version-lockstep site.
- **D-05: the parameter-name discriminator must be measured, not assumed.** Node type alone cannot
  separate a parameter's own name from its type annotation — both arrive as `desc_sig_name`. The
  discriminator must be derived from a dumped doctree covering positional, keyword-only, annotated,
  defaulted, and `**kwargs` parameters. *(See Architecture Patterns → D-05 below for the derived
  rule, re-measured and extended this session.)*
- **D-06: `par(hanging-indent: …)` plus U+200B injection into long dotted names. Nothing else.**
  `grid(columns: (auto, 1fr))` was measured and **rejected** (starves the parameter column for a long
  qualified name). `par(hanging-indent: 2.5em)` was **chosen**, measured on a hand-picked A4/2.5cm
  probe. Font shrinking is **not to be used**.
- **D-07: U+200B is required, and its scope is every long dotted name — `desc_addname` and dotted
  type annotations alike.** Measured at an artificial 9cm frame width, not yet re-measured against
  the real corpus at production page width. *(Re-measured this session — see below; the conclusion
  changes in an important way.)*
- **D-08: the hanging-indent step is introduced in Phase 37 as the shared indent constant Phase 38's
  IND-04 will reuse.** Exactly one Python-side constant; Phase 38 references it for `desc_content`,
  `field_list`, and `block_quote`.
- **D-09: Phase 37 does not touch `visit_desc_content`/`depart_desc_content`.** SIG-09 must be
  satisfied from the signature side alone. `block(sticky: true, …)` was confirmed to compile under
  typst 0.15 and is the obvious candidate. *(Confirmed and characterized in depth this session.)*
- **D-10: what replaces the `strong({...})` wrapper is Claude's discretion, decided by measurement.**
  Binding constraint: must not create a wrapper Phase 38's `desc_content` wrapper would nest inside
  redundantly, and must carry the SIG-07 hanging indent and SIG-09 keep-with-next without a second
  wrapper. *(Answered this session — see Architecture Patterns → D-10.)*
- **D-11: the dropped separator after a `desc_optional` group is fixed in Phase 37.** Root cause:
  `depart_desc_parameter` (`typsphinx/translator.py:4953-4962` in the pre-phase file) appends `", "`
  only when the *parameter* has a following sibling; the last parameter inside a `desc_optional` has
  none, so the group's own trailing separator is lost. No SIG requirement covers this; record as its
  own fixture.
- **D-12: SIG-08's "exactly one break" is Claude's to define.** Measured cause: a nested `py:method::`
  inside a `py:class::` produces `parbreak()\nparbreak()` because `depart_desc` emits an unconditional
  `parbreak()` for both the inner and outer `desc`. Sibling *signatures* inside one `desc` use a
  different mechanism (FID-03's leading `linebreak()`). If D-10 lands on `block(...)`, block spacing
  replaces some of this bookkeeping — say so explicitly in the plan.
- **D-13: the SIG-06 arrow glyph is Claude's to pick.** Current emission is `text(" -> ")`
  (`translator.py:4821`). Use U+2192 (`→`) unless measurement says otherwise, and assert no ASCII
  `->` remains anywhere in signature output. *(Corroborated this session.)*
- **D-14: the `golden.typ` migration strategy is Claude's to choose.** Either hand-derive only the
  changed signature lines and leave rubric/`**bold**`/list sections byte-identical, or freeze/narrow
  the Phase 36 gate and give Phase 37 its own fixture. **Binding, non-negotiable:** expected strings
  are hand-derived, never copied from the new code's own output. *(Recommendation made this session —
  see Common Pitfalls / Test Blast-Radius Census.)*

### Claude's Discretion

D-10, D-12, D-13, D-08 (constant's home), and the `golden.typ` migration form (D-14) are Claude's
call, decided by measurement per the binding constraints above — not open for re-litigation with the
user. This research answers all of them from direct measurement.

### Deferred Ideas (OUT OF SCOPE)

Nothing new was deferred from the discuss-phase session. Out of this phase's scope, per the phase
boundary: `visit_desc_content`/`depart_desc_content` (Phase 38, IND-01), `field_list` (Phase 38,
FLD-01..03), `rubric`/admonitions (Phase 39, ADM-01..05), citations (Phase 40), and any
user-overridable per-directive styling (Future STY-01..03, explicitly out of v0.7.0).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SIG-01 | `desc_name` renders in bold monospace | D-01 table + Architecture Patterns → signature monospace propagation mechanism; Code Examples |
| SIG-02 | `desc_addname` renders in regular-weight monospace | Same mechanism; `desc_addname` gets `raw(...)` without the `strong()` wrap |
| SIG-03 | `desc_annotation` renders in the same bold monospace as `desc_name` | Same mechanism; `desc_annotation`'s keyword/space children route through the same `strong(raw(...))` path |
| SIG-04 | `desc_parameter` (incl. inline type annotation) renders distinctly from `desc_name` | D-05 discriminator (measured, extended below) + D-03's per-sub-part assertion framing |
| SIG-05 | Parameter-list delimiters render in monospace | Same monospace-propagation mechanism (blanket, not per-node-type) |
| SIG-06 | `desc_returns` renders a real arrow glyph, no ASCII `->` remains | D-13 corroborated: `raw("\u{2192}")` survives `pypdf` extraction as `→`, distinguishable from `->` |
| SIG-07 | A long fully-qualified signature does not overflow the right margin | Corpus-measured worst case (`Sphinx.add_object_type`, 311 chars / `sphinx.util.parsing.nested_parse_to_nodes`, 41-char qualname) does NOT overflow at production page width — see Pitfall 2 for the load-bearing correction to D-06/D-07's premise |
| SIG-08 | Sibling signatures/blocks separated by exactly one break | D-12 mechanism analysis + measured `block()` default-spacing hazard (Pitfall 1) |
| SIG-09 | Signature + first body line not split across a page break | `block(sticky: true, ...)` empirically proven this session with a real page-break fixture (Architecture Patterns → D-09/SIG-09) |

</phase_requirements>

## Summary

Every one of CONTEXT.md's four "must be measured, not guessed" items was measured this session
against real tooling, and three of them **change the plan's shape**, not just confirm it.

**D-05 (parameter-name discriminator):** re-measured across positional, keyword-only, defaulted,
`*args`/`**kwargs`, union-typed (`Foo | None`), generic (`list[int]`), and forward-ref-string
(`"Bar"`) parameters, plus `desc_optional`-bracket-syntax signatures. The rule holds cleanly: **the
first `desc_sig_name` that is a direct child of `desc_parameter` is always the parameter's own name,
and it is always a leaf** (no descendant elements); every subsequent `desc_sig_name` direct child is
part of the type annotation and may be a leaf (`int`) or a non-leaf wrapping a `reference`/punctuation
tree (`Foo | None`, where `Foo` resolves to a real xref). This resolved-reference case surfaces a
**genuinely new implementation requirement CONTEXT did not name**: `visit_Text` must gain a
monospace-mode flag (mirroring the existing `in_literal_block` gate) so that text nested inside a
resolved type reference — which must still route through `visit_reference`'s `link(...)` — emits
`raw(...)` instead of `text(...)`. `link(<label>, raw("Foo"))` is valid Typst; without this flag, a
resolved type annotation would either lose its monospace treatment or lose its clickability.

**D-06/D-07 (overflow strategy):** measured at the corpus's *real* page width (453.54pt available
column, A4/11pt/DejaVuSansMono, read from `base.typ` via Typst's own `layout()`/`measure()` — not
estimated), the worst signature in the entire Sphinx v9.1.0 `doc/` corpus
(`sphinx.application.Sphinx.add_object_type`, 311 characters total, addname 7 chars) and the worst
*qualified name* (`sphinx.util.parsing.nested_parse_to_nodes`, 41 chars) do **not** overflow — the
widest single unbroken monospace token found anywhere in 1,445 real signatures
(`Callable[[BuildEnvironment,`, 28 chars) measures 143pt, well under the 453.54pt column. CONTEXT's
own 9cm-frame probe and hand-picked `DefaultValueDocumenter` example (measured this session at
312.58pt) *also* fit at real page width. The `hanging-indent`/U+200B mechanism should still be
implemented (it is cheap, harmless, and correct engineering for a pathological future case — a
synthetic 98-char dotted identifier was measured to overflow by 65.6pt) but **the real corpus supplies
no naturally-occurring RED fixture for margin overflow**; GATE-01's RED state for SIG-07 must come
from a deliberately constructed synthetic signature, with the real corpus's worst case kept as a
non-regression control.

**SIG-09 (page-boundary):** `block(sticky: true, {...})` was compiled and proven with a real
page-break fixture this session — marking two consecutive blocks `sticky: true` correctly pulled both
of them *and* the first line of the following (non-sticky) body paragraph onto the next page as one
unit, versus the control (no `sticky`) where the signature stayed on the earlier page and the body
line alone was pushed to the next — exactly the SIG-09 defect. **A separate, load-bearing discovery
made in the course of proving this:** `block()`'s *default* spacing adds ~26.5pt of vertical gap at
each block boundary versus plain content flow (measured via `here().position()` before/after,
14.39pt baseline vs. 40.88pt with default block spacing). If D-10's `block(...)` wrapper is adopted
without explicitly zeroing `above`/`below`, every signature gains unwanted whitespace and stacks with
the existing `linebreak()`/`parbreak()` mechanisms to reproduce SIG-08's doubled-gap defect in a new
form. `block(above: 0pt, below: 0pt, sticky: true, {...})` measured back to the plain-flow baseline
(14.48pt) while `sticky: true` continued to work correctly.

**Test census:** the starting 13-file census in CONTEXT.md is short one file
(`tests/test_desc_bodyless_concat_render_gate.py`) and under-specifies which function in
`tests/test_pdf_render_gate.py` is at risk
(`test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline`, which asserts the literal
`"-> int"` string and will break under SIG-06). The full census, split into "will break" / "mentions
only, safe" / "conditionally at risk pending D-12", is in Common Pitfalls below. `golden.typ`'s exact
line-by-line content was read directly: rubric lines (`Options`, `A Rubric In A List Item`, `Trailing
Heading`) and the plain-`**bold text**` regression control are **not** touched by Phase 37 and should
stay byte-identical, while the `connect`/`compile`×3/`--sep` signature lines are the only ones that
change — this concretely supports D-14's option 1 (hand-derive only the changed lines).

**Primary recommendation:** implement a single new translator-state flag scoped to the whole
`desc_signature` subtree that makes `visit_Text` emit `raw(...)` instead of `text(...)` (D-05's
mechanism); wrap `desc_name`/`desc_annotation` content in `strong(raw(...))` and each parameter's own
name in `emph(raw(...))`; replace the current `strong({...})` open/close pair in
`visit_desc_signature`/`depart_desc_signature` with
`block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: <SIGNATURE_INDENT constant>, {...}))`
— one wrapper, satisfying D-09/SIG-09 and D-06/SIG-07 together, with no second wrapper for Phase 38 to
nest inside; keep the existing anchor emission (`[#metadata(none) <label>]`) and the FID-03 sibling
`linebreak()` mechanism as-is unless D-12's measurement (below) shows they must change to avoid
interacting badly with `block()`'s spacing.

## Architectural Responsibility Map

typsphinx is a single-process build-time text transform (Sphinx doctree → Typst source → optional PDF
compile), not a multi-tier web application. The closest useful mapping is by pipeline stage:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Signature sub-part typography (bold/regular/italic monospace) | Translator (`TypstTranslator` node visitors) | — | All styling decisions are made at doctree-walk time; nothing is deferred to the template or the compile step |
| Return-arrow glyph substitution | Translator (`visit_desc_returns`) | — | Single call site, no template involvement |
| Long-signature overflow handling | Translator (emission shape: `par(hanging-indent:)`, U+200B injection) | Typst compiler (actual line-breaking) | The translator only emits the *hint*; Typst's own layout engine performs the actual wrap |
| Page-boundary keep-together | Translator (`block(sticky: true, ...)` emission) | Typst compiler (actual page-break decision) | Same split: translator emits the constraint, Typst enforces it during layout |
| Shared indent constant | Translator (module-level Python constant) | — | D-08: lives on the Python side per the "no bundled Typst style module" milestone invariant |
| Cross-reference resolution inside a type annotation | Translator (`visit_reference`, reused unmodified) | Sphinx core (doctree-resolved event, upstream of the translator) | The `reference`/plain-text split for resolved/unresolved xrefs happens in Sphinx's own `ReferencesResolver` post-transform, before the translator ever sees the doctree (confirmed via `Builder.write()` calling `env.get_and_resolve_doctree` before `write_doc`) |

## Standard Stack

No new package is introduced. D-04/D-06/D-09 use only Typst 0.15 standard-library primitives:
`raw()`, `strong()`, `emph()`, `par(hanging-indent:)`, `block(sticky:, above:, below:)`. This matches
milestone invariant #2 (the `@preview` package count stays at four) and REQUIREMENTS.md's Out-of-Scope
row confirming every required primitive is Typst 0.15 stdlib.

**Installation:** none required.

### Package Legitimacy Audit

**Not applicable.** This phase installs zero external packages (Python or Typst `@preview`). Milestone
invariant #1 (zero new runtime dependencies) and invariant #2 (four `@preview` packages, no new
lockstep site) are unaffected by design — confirmed by reading `typsphinx/templates/base.typ`
(no new import) and D-04's own reasoning (existing `visit_literal` already proves `raw(...)` compiles
under the active `codly-init`/`codly()` show rules).

## Architecture Patterns

### System Architecture Diagram

```
 doctree (desc_signature subtree, resolved xrefs already applied by Sphinx core)
   |
   v
 visit_desc_signature  ---- opens: block(above:0pt, below:0pt, sticky:true,
   |                                    par(hanging-indent: SIGNATURE_INDENT, {
   |                        sets: self.in_signature_text = True   <- NEW flag
   v
 [ desc_annotation ] -> strong(raw(...)) for "class"/"async" keyword + space
 [ desc_addname    ] -> raw(...) via visit_Text's monospace-mode branch
 [ desc_name       ] -> strong(raw(...))
 [ desc_parameterlist ]
     desc_parameter[0] -> emph(raw(...)) for first desc_sig_name child (the NAME)
                        -> raw(...) for every subsequent desc_sig_name/operator/
                           punctuation/space (the TYPE + DEFAULT), INCLUDING a
                           nested reference: link(<label>, raw("Foo")) when the
                           type resolves to a real xref (visit_reference unmodified,
                           visit_Text's flag makes its child text emit raw())
 [ desc_returns    ] -> raw(" ") + raw("\u{2192}") + raw(" ") + <return type, same
                          monospace-mode text>
   |
   v
 depart_desc_signature -- closes: }))) ; clears self.in_signature_text
                        -- emits [#metadata(none) <label>] anchor UNCHANGED
                        -- FID-03 sibling linebreak() / D-12 mechanism (see below)
```

### Recommended Project Structure

No new files or directories. All changes are inside `typsphinx/translator.py`'s existing
`desc_signature`/`desc_annotation`/`desc_addname`/`desc_name`/`desc_parameterlist`/`desc_parameter`/
`desc_optional`/`desc_returns`/`desc_sig_*` handlers (`typsphinx/translator.py:4640-5010` and
`5250-5310` in the pre-phase file), plus one new module-level constant (D-08, see below) and one new
instance-state flag read by `visit_Text` (`typsphinx/translator.py:1018-1091`).

### Pattern 1: the signature monospace-propagation flag (answers D-05's implementation gap)

**What:** a single boolean instance attribute (e.g. `self.in_signature_text`), set `True` in
`visit_desc_signature` and cleared in `depart_desc_signature`, checked by `visit_Text` exactly the way
`self.in_literal_block` is already checked there today.

**Why this is necessary, not optional:** measured this session — a resolved type annotation
(e.g. `timeout: Foo = None` where `Foo` is a real `py:class::`) arrives as
`desc_sig_name > reference > Text("Foo")`, i.e. the type's `reference` child must still be processed
by the existing, unmodified `visit_reference`/`depart_reference` (which emits
`link(<label>, ...)`) so the cross-reference keeps working — `visit_literal`'s "raise `SkipNode` and
process the whole string yourself" pattern is not usable here because it would skip the nested
`reference` entirely and silently drop the xref. The flag must therefore live at the `visit_Text`
level so it fires *underneath* `visit_reference` too, producing `link(<label>, raw("Foo"))` — verified
this session that `raw()` nested inside `link()`'s body argument is valid Typst (both `raw()` and
`link()`'s body parameter operate on `content`, not `str`).

**When to use:** for every text-bearing descendant of `desc_signature` — `desc_name`, `desc_addname`,
`desc_annotation`, `desc_sig_*`, the `inline.default_value` node, and (via `unknown_visit`'s
fall-through, since it does not raise `SkipNode`) `desc_sig_literal_string`/`desc_sig_literal_number`,
which have no dedicated handler today and were found by this session's measurement (a quoted forward
reference like `c: "Bar"` produces a `desc_sig_literal_string` node) — get monospace "for free" under
this scoped flag without needing new dedicated handlers.

**Example (illustrative, not literal diff):**
```python
# visit_Text (typsphinx/translator.py:1018), new branch alongside the
# existing in_literal_block early-return:
if self.in_signature_text:
    escaped = escape_typst_string(text_content)  # same helper visit_literal uses
    self.add_text(f'{prefix}raw("{escaped}")')
    # ... same _emit_inline_concat_separator / list_item_needs_separator
    # bookkeeping the existing text() branch already performs
    return
```

### Pattern 2: D-05's discriminator rule (measured across 8 parameter shapes)

**Rule:** within one `desc_parameter`, **the first `desc_sig_name` node that is a direct child is the
parameter's own name and is always a text-only leaf.** Wrap it in `emph(...)` in addition to the
blanket `raw(...)` from Pattern 1. Every other direct-child `desc_sig_name` (there is at most one more
in every measured case) is part of the type annotation; it gets `raw(...)` only, and if it is a
non-leaf (wraps a `reference`/punctuation tree for a union/generic/resolved type), its descendants are
processed normally under the same monospace flag.

**Evidence, per shape** (measured via `env.get_and_resolve_doctree`, this session):

| Shape | Source | Structure at `desc_parameter` |
|---|---|---|
| Positional, untyped | `host` | `desc_sig_name["host"]` (single leaf — trivially "first") |
| Defaulted | `port: int = 8080` | `desc_sig_name["port"]`, `:`, space, `desc_sig_name["int"]` (leaf, unresolved builtin), space, `=`, space, `inline.default_value["8080"]` |
| Keyword-only separator | bare `*` | `desc_sig_operator[keyword-only-separator] > abbreviation["*"]` — **no `desc_sig_name` at all**; nothing to italicize |
| `*args` | `*args` | `desc_sig_operator["*"]`, `desc_sig_name["args"]` (first/only `desc_sig_name` — correct even though preceded by an operator) |
| `**kwargs: str` | typed py-domain form | `desc_sig_operator["**"]`, `desc_sig_name["kwargs"]`, `:`, space, `desc_sig_name["str"]` |
| Resolved type xref | `timeout: Foo = None` (`Foo` a real `py:class::`) | `desc_sig_name["timeout"]` (leaf), `:`, space, `desc_sig_name` **wrapping** `reference[refid=Foo] > "Foo"` (non-leaf!), space, `=`, space, `inline.default_value["None"]` |
| Union type | `a: Foo | None = None` | `desc_sig_name["a"]` (leaf), `:`, space, `desc_sig_name` wrapping `[reference("Foo"), space, desc_sig_punctuation("|"), space, Text("None")]` (non-leaf, mixed resolved+unresolved) |
| Generic/subscript | `b: list[int] = []` | `desc_sig_name["b"]` (leaf), `:`, space, `desc_sig_name` wrapping `["list", desc_sig_punctuation("["), "int", desc_sig_punctuation("]")]` |
| Quoted forward ref | `c: "Bar" = None` | `desc_sig_name["c"]` (leaf), `:`, space, `desc_sig_name` wrapping `desc_sig_literal_string["'Bar'"]` — **new node type, no dedicated handler today, falls through `unknown_visit` to plain text; needs no new handler under Pattern 1's blanket flag** |
| `desc_optional`-bracket-syntax signature | `.. py:function:: f(host, [timeout], **kwargs)` | **Coarser tokenizer**: no `desc_sig_space` nodes at all between tokens, and `**kwargs` arrives as ONE `desc_sig_name["**kwargs"]` (not split into operator + name) — but exactly one `desc_sig_name` per `desc_parameter`, so the "first" rule is trivially satisfied and there is never a type annotation to confuse it with (`[...]`-bracket-syntax signatures have no type-annotation support) |

**Correction to CONTEXT.md's own claim:** D-05 stated the type annotation "wraps a `pending_xref`".
Measured this session: by the time the translator receives the doctree, `Builder.write()` has already
called `env.get_and_resolve_doctree()`, which runs Sphinx's `ReferencesResolver` post-transform — an
unresolved `pending_xref` is replaced by its own plain content (no wrapper node at all), and a
*resolved* one becomes a `reference` node, never a `pending_xref`. `pending_xref` nodes are only
visible in the **pre-resolution** doctree (e.g. via a raw pickle inspection), not in what
`write_doc`/the translator actually sees. This does not change the discriminator rule (still "first
`desc_sig_name` direct child"), but a discriminator implementation that checks
`isinstance(child, addnodes.pending_xref)` to detect "this is the type" would silently never fire —
check for `nodes.reference` instead, or better, don't check node type for the type-vs-name split at
all (the *position* rule above is sufficient and simpler).

### D-09 / SIG-09: page-boundary keep-together, empirically proven

**Measured, this session**, with a real `#set page(height: 120pt, margin: 10pt)` fixture and two
`block(sticky: true, [...])` calls followed by a plain paragraph:

- **Without `sticky`:** the two signature blocks stayed on the earlier page (fit in the remaining
  space); the following body paragraph alone was pushed to the next page — the exact SIG-09 defect.
- **With `sticky: true` on both blocks:** all three — both signature blocks *and* the following body
  paragraph — moved together onto the next page as one unit.

Sticky is **transitive**: a chain of consecutive `sticky: true` blocks all move together with the
first non-sticky content that follows. This means marking **every** `desc_signature`'s wrapper
`sticky: true` (uniformly, with no special-casing "last signature in a `desc`") is sufficient — the
chain automatically reaches forward past sibling overload signatures to whatever Phase 38 eventually
wraps `desc_content` in, with no desc-level bookkeeping needed in Phase 37.

**Load-bearing gotcha found in the same experiment:** Typst's `block()` has non-zero default
`above`/`below` spacing. Measured via `context { here().position() }` markers before/after a block
boundary at 11pt text:

| Configuration | Gap between two adjacent one-line blocks |
|---|---|
| Plain content flow, no `block()` (baseline) | 14.39pt |
| `block([...])`, `block([...])` (Typst defaults) | 40.88pt (+26.5pt vs. baseline) |
| `block(above: 0pt, below: 0pt, sticky: true, [...])` ×2 | 14.48pt (matches baseline) |

`sticky: true` continued to work correctly with `above`/`below` zeroed (re-verified with a second
page-break fixture). **Conclusion: the D-10 wrapper must explicitly set `above: 0pt, below: 0pt`**,
or every signature in the corpus gains ~26.5pt of unwanted whitespace and compounds with the existing
`linebreak()`/`parbreak()` mechanisms into a new doubled-gap defect — see Pitfall 1.

### D-10: recommended replacement for `strong({...})`

**Recommendation:** `block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent:
_SIGNATURE_INDENT, {...}))`, opened in `visit_desc_signature` and closed in `depart_desc_signature`,
replacing the current `{prefix}strong({{` / `}})` literal pair. This is **one wrapper composed of
exactly the two Typst primitives each binding constraint needs** (page-keeping via `block`,
hanging-indent via `par`) — not a second independent wrapper Phase 38 would have to reason about
nesting inside. `desc_name`/`desc_annotation` keep their own separate, INNER `strong(raw(...))` calls
around just their own content (per D-01's table — the signature as a whole is no longer uniformly
bold). The existing state-machine bookkeeping in the "verbatim copy of `visit_strong`'s body"
(paragraph separator, `_enter_inline_concat_element`, `in_list_item`/`list_item_needs_separator`
save-restore) is unaffected by this change — it manages how the signature integrates with *surrounding*
content (a def-list term, a list item, etc.), independent of which literal Typst call opens the
content block. Only the two literal strings change, and one additional closing `)` is needed for each
of `block(` and `par(`.

### D-12: sibling-signature / desc-level break convergence

**Measured root cause (confirmed, matches CONTEXT.md):** `depart_desc` emits an unconditional
`parbreak()` (`typsphinx/translator.py:4667`) for every `desc`, so a nested `py:method::` inside a
`py:class::` produces two consecutive `parbreak()` calls (inner desc's depart, then outer desc's
depart) with nothing between them. Sibling *signatures* inside the *same* `desc` (overloads) use the
independent FID-03 `_is_first_desc_signature` → leading `linebreak()` mechanism, which is unaffected
by the nested-desc doubling.

**Recommendation:** keep the two mechanisms distinct (they solve different problems — `linebreak()`
separates signature *lines* within one visual "signature block", `parbreak()` separates one `desc`
paragraph-block from the next) but fix `depart_desc`'s doubling directly: track whether this `desc`'s
`parbreak()` would be immediately followed by another `desc`'s `parbreak()` with nothing emitted in
between (the nested-desc case), and suppress the inner one — mirroring the existing
`_is_first_desc_signature`-style boolean-flag idiom already used at this exact call site's sibling
(FID-03), rather than introducing new state machinery. If D-10's `block()` wrapper is adopted, verify
in the GATE-01 fixture that `block()`'s own (zeroed) spacing does not silently absorb or duplicate
this fix — the two systems (Typst block layout spacing vs. explicit `parbreak()` tokens) are
orthogonal and must be tested together, not assumed compatible.

### Code Examples

Existing, proven `raw()` precedent (D-04's own citation, reused for escaping):
```python
# typsphinx/translator.py:1282 area, visit_literal (existing, unmodified)
escaped_code = escape_typst_string(code_content)
self.add_text(f'raw("{escaped_code}")')
```

D-05's discriminator, illustrative (per-`desc_parameter` bookkeeping, not literal diff):
```python
# in visit_desc_parameter (or a small helper called from it): reset a
# per-parameter "have we seen the name yet" flag, mirroring the existing
# _desc_parameter_has_content flag idiom already used for comma placement
self._param_name_seen = False

# in visit_desc_sig_name: if not self._param_name_seen and this node's
# parent is the current desc_parameter: wrap in emph(), set the flag True.
# Every subsequent desc_sig_name in the same desc_parameter is plain raw().
```

D-11's fix site (dropped `desc_optional` trailing separator):
```python
# depart_desc_optional (typsphinx/translator.py:4979 area) -- add the
# SAME "do I have a following sibling" check depart_desc_parameter already
# uses, but checked against the desc_optional node itself, and emit the
# comma INSIDE the closing bracket (mirroring Sphinx HTML's "[timeout, ]"):
def depart_desc_optional(self, node):
    if node.next_node(descend=False, siblings=True):
        self.add_text(' + raw(", ")')   # inside the bracket
    self.add_text(' + raw("]")')
    self._desc_parameter_has_content = True
```

D-13, corroborated arrow glyph (compiled and `pypdf`-extracted this session):
```typst
raw(" ") + raw("\u{2192}") + raw(" ") + raw("None")
// pypdf extract_text() on the compiled PDF: "connect() → None"
// '→' in text -> True ; '->' in text -> False
```

### Anti-Patterns to Avoid

- **Checking `isinstance(child, addnodes.pending_xref)` to find the type annotation.** Measured: the
  translator never sees an unresolved `pending_xref` — it is stripped to plain content or resolved to
  `nodes.reference` before `write_doc` runs. This check would silently never match.
- **Wrapping the whole `desc_parameter` in one `emph(raw(...))`.** Rejected by D-02/D-03 — the name is
  italic, the type/default are regular monospace. A blanket per-parameter wrap contradicts SIG-04's
  own reading (D-03).
- **Adopting `block()` for the signature wrapper without zeroing `above`/`below`.** Measured to add
  ~26.5pt of unwanted spacing per signature and compound with existing break mechanisms — see
  Pitfall 1.
- **Assuming the 9cm-frame / hand-picked-example overflow measurements transfer to production page
  width.** Measured this session: neither actually overflows at the real 453.54pt column. See
  Pitfall 2.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Monospace text | A custom `set text(font: "DejaVu Sans Mono")` scoped block | `raw(...)` (D-04) | Already proven in the corpus via `visit_literal`; no interaction with `codly`'s show rules; no new font-selection surface to keep in sync with the `ja` build's CJK fallback (a standing v0.7.0 risk noted in STATE.md) |
| Long-line wrapping | A custom width-measuring line-break algorithm in Python | `par(hanging-indent:)` + Typst's own line breaker | Typst already performs Knuth-Plass-style paragraph breaking on `raw()` string content at normal break points (spaces); the only gap is periods, closed by U+200B injection |
| Page-boundary keep-together | Manual page-height bookkeeping in the translator | `block(sticky: true, ...)` | Confirmed this session to compile and behave correctly under typst 0.15; the translator has no visibility into page geometry at doctree-walk time and should not try to replicate Typst's layout engine |

**Key insight:** every mechanism this phase needs (monospace primitive, paragraph wrapping, sticky
page-keeping) already exists in Typst 0.15's standard library and was proven to compose correctly
this session. The actual engineering risk is not "does Typst support X" but "does composing two of
these primitives together (e.g. `block()` + the pre-existing `linebreak()`/`parbreak()` mechanisms)
introduce a new spacing defect" — which is exactly what Pitfall 1 found.

## Common Pitfalls

### Pitfall 1: `block()`'s default spacing silently reintroduces a SIG-08-shaped defect

**What goes wrong:** if D-10's `block(sticky: true, ...)` wrapper is adopted without explicitly
setting `above: 0pt, below: 0pt`, every signature gains ~26.5pt of vertical whitespace at each block
boundary (measured, see D-09/SIG-09 above) — visually similar to, and additive with, the exact doubled
`parbreak()`/`linebreak()` defect SIG-08 is supposed to fix.
**Why it happens:** Typst's `block()` element has non-zero default `above`/`below` spacing
(intended for prose blocks like block quotes and figures); it was never designed to be a zero-cost
inline-content wrapper.
**How to avoid:** always pass `above: 0pt, below: 0pt` explicitly alongside `sticky: true`. Verified
this session that `sticky: true` continues to work correctly with these set to zero.
**Warning signs:** a GATE-01 fixture that renders visibly larger gaps around signatures than the
pre-phase translator, or a `pypdf` per-page line-count regression on the full-corpus gate.

### Pitfall 2: the real corpus does not exercise the overflow mechanism CONTEXT.md designed

**What goes wrong:** implementing SIG-07 against a corpus-derived RED fixture will fail to ever go
RED, because no real signature in Sphinx's `doc/` corpus is wide enough to overflow the production
page's 453.54pt text column even in monospace.
**Why it happens:** CONTEXT.md's `2.5em` hanging-indent and U+200B decisions were measured against an
artificially narrow 9cm (~255pt) frame, deliberately used to stress-test the wrapping technique — not
representative of the real ~453.54pt production column. Measured this session: the corpus's worst
signature (`Sphinx.add_object_type`, 311 chars total) and worst qualified name
(`sphinx.util.parsing.nested_parse_to_nodes`, 41 chars, 217.22pt wide) both fit comfortably; even
CONTEXT's own hand-picked `sphinx.ext.autodoc.preserve_defaults.DefaultValueDocumenter` example
measures 312.58pt — still under 453.54pt.
**How to avoid:** implement the hanging-indent + U+200B mechanism anyway (it is correct, cheap
defensive engineering, and it does not hurt the readability the owner approved), but construct the
GATE-01 RED fixture from a **deliberately synthetic** over-length dotted identifier (a ~90+ character
unbroken run was measured this session to overflow by 65.6pt at 453.54pt column width — e.g. extend
CONTEXT's own probe name with additional dotted segments), not from a corpus signature. Keep a
*separate*, real-corpus-derived assertion that proves the worst real signature stays within the margin
(a true non-regression check, expected to pass both before and after the fix, since it never actually
fails today either).
**Warning signs:** a "RED" fixture built from the real corpus that is GREEN even against the
unmodified pre-phase translator — that is not a fixture defect, it is telling you the corpus doesn't
reach the failure mode.

### Pitfall 3: `visit_literal`'s `SkipNode` pattern cannot be reused for `desc_sig_name`

**What goes wrong:** a naive implementation of D-05's monospace styling that copies `visit_literal`'s
"grab `node.astext()`, emit one `raw(...)`, raise `SkipNode`" pattern for a non-leaf `desc_sig_name`
(the type-annotation case) will silently produce plain string text for a resolved cross-reference
inside the type annotation, instead of a clickable `link(...)` — a rendering regression (a `Foo`
type annotation loses its hyperlink) that most likely will not be caught by any assertion that only
checks for the *substring* `"Foo"` in the emitted `.typ`.
**Why it happens:** `node.astext()` recursively concatenates ALL descendant text, silently discarding
structure — including a nested `reference` node's own semantics.
**How to avoid:** only leaf `desc_sig_name` nodes (the parameter's own name, and simple unresolved
builtin type names like `int`) may use the `astext()` + `raw()` + `SkipNode` shortcut. A non-leaf
`desc_sig_name` (detected by checking `len(node.children) > 1` or the presence of a non-`Text` child)
must be processed structurally — enter it, let its children (including any `reference`) dispatch
normally under the Pattern 1 monospace flag, then depart.
**Warning signs:** a GATE-01 fixture using a resolved type reference (like this session's `Foo | None`
probe) where the compiled PDF has no working hyperlink on the type name.

### Pitfall 4 (Test blast-radius census — verified and extended beyond CONTEXT.md's starting 13-file list)

CONTEXT.md's starting census (13 files + `golden.typ`) is missing one file and under-specifies one
function. Full census, verified this session by reading every file's actual assertions (not just
grepping for node names):

**Will break — hardcode the current `strong({text(...` wrapper or the ASCII arrow, must be migrated:**

| File / test | What breaks | Why |
|---|---|---|
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | `strong({text("connect")...`, three `strong({text("compile")...` blocks, `strong({text("--sep")})` | Full file read this session (below) — these are the ONLY lines that change; rubric lines and the plain-`**bold**` control do not |
| `tests/test_desc_rubric_decoupling_render_gate.py` | byte-identity assertion against `golden.typ` | Consumes the above fixture |
| `tests/test_desc_sig_space_render_gate.py` | asserts spacing "on the `strong({...})` run" (FID-08) | Directly tests `desc_sig_space` behavior inside the current wrapper |
| `tests/test_desc_signature_concat_render_gate.py` | `typ_text.index('strong({text("compile")')`, `'strong({text("solo")')` | Hardcodes the current `desc_name` wrapper exactly |
| `tests/test_rubric_option_concat_render_gate.py` | `typ_text.index('strong({text("--sep")})')` | This is an `.. option:: --sep` **desc_signature**, not the rubric it's compared against — confirmed by reading the file; the rubric half of the same test (`'strong({text("Structure Options")})'`) is unaffected (Phase 39 territory) |
| `tests/test_translator.py::test_desc_signature_rendering` | `"strong({" in output` | Loose substring check on the current wrapper shape |
| `tests/test_translator.py::test_desc_with_annotation_and_name` | `'strong({text("class")' in output` | Hardcodes current `desc_annotation` wrapper |
| `tests/test_translator.py::test_desc_parameterlist` | `'strong({text("function")' in output` | Hardcodes current `desc_name` wrapper |
| `tests/test_translator.py::test_full_api_description_structure` | `'strong({text("class")' in output` | Same |
| `tests/test_pdf_render_gate.py::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` | `assert "-> int" in full_text` | SIG-06 changes the arrow glyph; **not previously named at function granularity in CONTEXT.md's census** |

**Mentions `desc_*` names but asserts on something Phase 37 does not change — safe:**

| File | What it actually tests |
|---|---|
| `tests/test_confval_field_body_render_gate.py` | plain `**bold**` markup (`html_title`), routes through unmodified `visit_strong` |
| `tests/test_confval_field_spacing_render_gate.py` | `field_name`/`field` colon-spacing (Phase 38 FLD territory) |
| `tests/test_deflist_nested_definition_render_gate.py`, `tests/test_deflist_term_concat_render_gate.py` | no `desc_signature`-shaped assertions found on inspection |
| `tests/test_deflist_term_inline_children_gate.py` | plain `**bold**` inside definition-list terms, unmodified `visit_strong` |
| `tests/test_desc_container_propagated_target_render_gate.py`, `tests/test_desc_signature_anchor_render_gate.py` | the `[#metadata(none) <label>]` anchor and link resolution — D-10's recommendation explicitly preserves this emission unchanged |
| `tests/test_pdf_render_gate.py` (all other functions in the file) | unrelated node families (admonitions, figures, footnotes, etc.) |

**Conditionally at risk — depends on how D-12 is resolved, re-verify after implementation:**

| File / test | Depends on |
|---|---|
| `tests/test_desc_bodyless_concat_render_gate.py` (**new — not in CONTEXT.md's 13-file census**) | asserts `"parbreak()" in typ_text` between two body-less confval `desc` siblings; breaks only if D-12 changes `depart_desc`'s `parbreak()` mechanism itself |
| `tests/test_translator.py::test_desc_signature_line_multiline_emits_one_linebreak`, `..._single_line_emits_no_linebreak`, `..._resets_per_signature` | assert on `linebreak()` count/position via `output.count("linebreak()")`; the plain-text substrings they also check (`"template<typename T>"`, etc.) survive being re-wrapped in `raw(...)` since they check for the bare content substring, not the wrapper |

**D-14 recommendation:** adopt CONTEXT.md's option 1 (hand-derive only the changed signature lines in
`golden.typ`, leave rubric/`**bold**`/list sections byte-identical). Justification, from reading the
full 90-line fixture this session: only 7 of the file's ~35 content-bearing lines are
`desc_signature`-driven (`connect`'s signature, the three `compile` overload lines, `--sep`'s
signature — the `Options` rubric heading and body text/anchors are untouched). Re-deriving just those
lines makes the diff itself double as evidence that Phase 37 touched only what it claims to, at far
lower cost than standing up a parallel fixture (option 2).

## Runtime State Inventory

Not applicable — this is a rendering/typography phase (net-new node-handler behavior on
already-in-scope nodes), not a rename/refactor/migration phase. No stored data, live service config,
OS-registered state, secrets, or build artifacts reference the changed identifiers.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The corpus-derived worst-case figures (311-char signature, 41-char qualname, 143pt widest unbroken token) generalize to domains beyond `py:` (C/C++/JS) not present in the measured corpus pages | Summary, Pitfall 2 | A C++ template signature with heavier nesting could theoretically produce a wider unbroken token than anything measured; low risk since the corpus is large (1,445 real signatures measured) and C/C++ domains reuse the same `desc_sig_*` node family, so the monospace-propagation mechanism (Pattern 1) applies unchanged regardless of domain — only the *exact overflow threshold* is `py:`-corpus-specific |
| A2 | `block(above: 0pt, below: 0pt, sticky: true, ...)` does not introduce any other visible side effect (e.g. `inset:`, `radius:`, `fill:` defaults) beyond the measured spacing | D-09/SIG-09, D-10 | Low risk — `block()`'s other cosmetic defaults (`inset: 0pt`, no `fill`, no `stroke`) were not explicitly re-measured this session but match Typst 0.15's documented defaults from training knowledge; verify visually in the phase's own GATE-01 fixture |
| A3 | Typst's line-breaker treats `.` as a non-break-opportunity character uniformly across all font/script contexts relevant here (Latin identifiers) | Summary, D-06/D-07 | This matches the FID-01a precedent already proven in production (`visit_literal`'s existing in-table ZWSP injection) and this session's own measurement that an unbroken 90+ char dotted run does overflow without ZWSP; low risk |

**If this table is empty:** not applicable — see above.

## Open Questions

1. **Should the D-12 `depart_desc` doubled-`parbreak()` fix land in Phase 37 or be deferred?**
   - What we know: SIG-08 explicitly requires "exactly one break" and names the doubled `parbreak()`
     as the defect to remove; Phase 37's own requirements list includes SIG-08.
   - What's unclear: whether the fix should be a small, isolated boolean-flag change to `depart_desc`
     (recommended above) or should wait to see how D-10's `block()` wrapper's own spacing interacts
     with it first, since fixing `parbreak()` bookkeeping and changing the wrapper in the same phase
     creates two simultaneous variables in the same GATE-01 fixture.
   - Recommendation: implement both in Phase 37 (SIG-08 is explicitly in scope), but sequence the
     plan so the `depart_desc` flag fix and the `block()` wrapper change are proven with **separate**
     structural assertions before being combined in one full-signature fixture — mirroring Phase 36's
     own D-07 precedent of splitting a byte-identical change from a byte-changing one into separate
     plans/commits.

2. **Does the `desc_sig_literal_string`/`desc_sig_literal_number` `unknown_visit` warning matter for
   this phase?**
   - What we know: these node types have no dedicated handler and fall through to `unknown_visit`,
     which logs a warning but does not affect output (children still process normally). Under
     Pattern 1's blanket monospace flag, they get correct `raw(...)` styling for free.
   - What's unclear: whether silencing the warning (adding trivial `pass`-through `visit_desc_sig_*`
     entries for these two node types) is in scope for this phase or a separate cosmetic follow-up.
   - Recommendation: out of scope for Phase 37 (no SIG requirement names it, and REQUIREMENTS.md's
     `desc_sig_*` family list in the phase boundary does not include these two literal subtypes) —
     file a todo if the warning proves noisy in the full-corpus gate's log output.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst-py` | GATE-01 real-compile fixtures | ✓ | 0.15.0 (confirmed via `typst.compile()` this session) | — |
| `pypdf` | PDF-text/bounding-box assertions | ✓ | 6.14.2 | — |
| Sphinx `doc/` corpus (cached) | SIG-07 real-corpus measurement | ✓ | v9.1.0, cached at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0` | — |
| `pdftotext` (poppler) | Reference-font-role cross-check named in REQUIREMENTS.md's SIG section preamble | ✗ | — | `pypdf` + Typst's own `measure()`/`layout()` context functions, used throughout this research, are a fully adequate substitute — demonstrated this session to give reliable pt-precision measurements without needing a compiled binary |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** `pdftotext` — not installed in this sandbox; `pypdf` combined
with Typst's own `context { measure(...) }` / `context layout(size => ...)` functions (used
extensively in this research) fully substitutes for geometric measurement needs. `pypdf`'s
`extract_text(visitor_text=...)` was found unreliable for *per-glyph x/y positions* on Typst-generated
PDFs in this sandbox (repeatedly reported `x=0, y=0`) — plain `extract_text()` (no visitor) and
Typst's own `measure()`/`layout()` were the reliable methods used for every geometric claim in this
document. **Recommend the plan use the same approach** (Typst-side `context measure(...)` probes
compiled via `typst.compile()`, cross-checked with `pypdf`'s plain-text extraction for content/order
assertions) rather than relying on `pypdf` bounding-box extraction for exact glyph positions.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), plus the project's own GATE-01 real-`typst.compile()` render-gate pattern |
| Config file | `pyproject.toml` (pytest); no separate framework config for the render-gate pattern — it's plain pytest fixtures + subprocess/`typst.compile()` calls, e.g. `tests/test_pdf_render_gate.py`'s `_run_sphinx_build_typst` helper |
| Quick run command | `uv run pytest tests/test_translator.py -k desc -x` (unit-level, no compile) |
| Full suite command | `uv run pytest -m "not slow"` (excludes the `@pytest.mark.slow` full-corpus gate) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SIG-01 | `desc_name` emits `strong(raw(...))`, structural, RED-before-fix | unit (translator) + render-gate | `uv run pytest tests/test_translator.py::test_desc_with_annotation_and_name -x` (rewritten) | ✅ exists, needs rewrite |
| SIG-02 | `desc_addname` emits `raw(...)` without `strong()` | unit + render-gate | new test in `tests/test_translator.py` | ❌ Wave 0 |
| SIG-03 | `desc_annotation` emits the SAME `strong(raw(...))` as `desc_name` | unit + render-gate | rewritten `test_desc_with_annotation_and_name` | ✅ exists, needs rewrite |
| SIG-04 | Per-sub-part distinct treatment inside `desc_parameter` (D-03: per-sub-part, not blanket) | unit — one assertion per sub-part (name `emph`, type/default `raw` only) | new parametrized test | ❌ Wave 0 |
| SIG-05 | Delimiters (`(` `)` `,` `=` `desc_optional` brackets) emit `raw(...)` | unit + render-gate | rewritten `test_desc_parameterlist`, new `desc_optional` case | ✅/❌ partial |
| SIG-06 | `desc_returns` emits `raw("\u{2192}")`; no `->` anywhere in signature output | render-gate, compiled-PDF `pypdf` text (`'→' in text and '->' not in text`) | rewrite `tests/test_pdf_render_gate.py::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` | ✅ exists, needs rewrite |
| SIG-07 | Synthetic long-dotted-name fixture stays within `pypdf`/Typst-`measure()`-verified column width; real-corpus worst case is a non-regression control | new render-gate, Typst `context measure(...)` + `pypdf` text | new `tests/test_signature_overflow_render_gate.py` | ❌ Wave 0 |
| SIG-08 | Exactly one break between sibling signatures / desc blocks (nested-desc doubling gone) | render-gate, structural `.typ` assertion (`output.count("parbreak()")`) | new/rewritten fixture covering nested `py:class`+`py:method` | ❌ Wave 0 (extends existing `test_desc_bodyless_concat_render_gate.py` pattern) |
| SIG-09 | Signature + first body line share a page under a forced page-break fixture | render-gate, `pypdf` per-page text containment | new `tests/test_signature_page_boundary_render_gate.py`, following this session's proven `#set page(height:, margin:)` + `block(sticky:)` pattern | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_translator.py -k "desc or signature" -x` (fast,
  no `typst.compile()`)
- **Per wave merge:** `uv run pytest -m "not slow"` (includes all GATE-01 real-compile render gates,
  excludes the full-corpus `@pytest.mark.slow` gate)
- **Phase gate:** `uv run pytest -m "not slow"` plus an explicit `uv run pytest tests/test_corpus_gate.py -m slow` full-corpus run before `/gsd-verify-work`, per this milestone's standing practice

### Wave 0 Gaps

- [ ] `tests/test_signature_overflow_render_gate.py` — covers SIG-07 (synthetic overflow RED fixture
      + real-corpus non-regression control, per Pitfall 2)
- [ ] `tests/test_signature_page_boundary_render_gate.py` — covers SIG-09 (forced page-break fixture,
      per the proven `#set page(height:, margin:)` + `block(sticky:)` pattern from this research)
- [ ] A parametrized `desc_parameter` sub-part unit test covering all 8 shapes measured in D-05's
      table above (SIG-04) — no existing test covers the union-type/resolved-xref/quoted-forward-ref
      cases
- [ ] Extension of `test_desc_bodyless_concat_render_gate.py`-style nested-`desc` fixture to prove
      SIG-08's "exactly one break" for the `py:class::`/`py:method::` nesting case specifically (the
      existing fixture covers body-less *sibling* desc, not nested desc)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Build-time, local, single-user CLI tool; no auth surface |
| V3 Session Management | No | No sessions |
| V4 Access Control | No | No access-control surface |
| V5 Input Validation | Partial, already covered | The only "untrusted input" this phase touches is docstring/signature text originating from a project's own Python source (via autodoc) or hand-authored `.rst` — already routed through the existing `escape_typst_string` helper (reused unmodified by every new `raw(...)` call site this phase adds, per Pattern 1/D-04) before being embedded in a Typst string literal. No new injection surface is introduced; no new escaping logic is written |
| V6 Cryptography | No | No cryptographic operations |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Typst string-literal injection via unescaped signature text (e.g. a parameter default value containing a literal `"` or `\`) | Tampering | Already mitigated project-wide by `escape_typst_string`, reused unmodified for every new `raw(...)` emission site this phase adds — no new escaping code is written, closing off a class of "forgot to escape the new code path" regressions by construction |

No new threat surface is introduced by this phase: it adds styling to already-parsed, already-escaped
signature content: no new external input, no new network/file/subprocess calls, no new dependency.

## Sources

### Primary (HIGH confidence — direct execution this session)

- Real `sphinx-build`/`env.get_and_resolve_doctree()` doctree dumps against 8 constructed parameter
  shapes (positional, keyword-only, defaulted, `*args`, `**kwargs`, union type, generic/subscript
  type, quoted forward reference) and against `desc_optional`-bracket-syntax signatures — D-05's
  discriminator rule and its correction to CONTEXT.md's "pending_xref" claim.
- Real `sphinx-build -b typst` full-corpus run (Sphinx v9.1.0 `doc/`, cached at
  `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`, 1,445 real `desc_signature` nodes measured) — SIG-07
  worst-case figures.
- Real `typst.compile()` (typst-py 0.15.0) probes using the project's own `_template.typ` — `measure()`
  and `layout()` context-function readings for available column width (453.54pt) and token widths;
  `block(sticky:)` page-boundary A/B tests; `block()` default-vs-zeroed spacing measurement via
  `here().position()`.
- `pypdf` 6.14.2 `extract_text()` on compiled PDFs — arrow-glyph survival (D-13), page-content
  containment for the sticky tests, corpus-page text.
- Direct reading of `typsphinx/translator.py` (relevant ranges: 1018-1091 `visit_Text`, 1093-1170
  `visit_emphasis`, 1203-1360 `visit_strong`/`visit_literal`, 3588-3800 `visit_reference`,
  4640-5010 the full `desc_*` family, 5250-5310 `desc_sig_*`), `tests/*.py` (all 14 files in the
  blast-radius census), and `tests/fixtures/desc_rubric_decoupling_render_gate/{index.rst,golden.typ}`
  in full.

### Secondary (MEDIUM confidence)

- `.planning/phases/37-signature-typography-the-desc-family/37-CONTEXT.md` — the owner's locked
  decisions D-01..D-14, cross-checked against this session's own measurements where CONTEXT flagged
  "must be measured."
- `.planning/phases/36-shared-emission-seam-cleanup/36-CONTEXT.md` and its `36-*.md` artifacts — the
  seam this phase builds on (verbatim-copy triplication, shared `_strong_was_*` state, the `par()`-loss
  bug deferred to Phase 39).

### Tertiary (LOW confidence)

- None. Every claim in this document is either directly measured this session (Primary) or copied
  verbatim from CONTEXT.md's own already-locked, owner-approved decisions (Secondary). No claim rests
  on unverified training knowledge alone except the three items in the Assumptions Log, which are
  explicitly flagged.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; every primitive (`raw`, `strong`, `emph`, `par`, `block`)
  confirmed to compile under the real project template this session.
- Architecture (D-05 discriminator, D-09/D-10 wrapper, D-12 break convergence): HIGH — each answered
  by direct execution against real doctrees/real compiles, not inferred.
- Pitfalls (block spacing, corpus overflow non-manifestation, `SkipNode` hazard, test census): HIGH —
  each is a specific, reproduced, numerically-measured finding, not a generic warning.

**Research date:** 2026-08-01
**Valid until:** 30 days (stable — no external ecosystem dependency; the only decay vector is a
future Typst/typst-py or Sphinx version bump, neither of which is scheduled within this milestone)
