# Phase 38: Structural Indentation + Info Fields - Research

**Researched:** 2026-08-01
**Domain:** Typst code-mode layout composition (`pad`/`block`) inside a docutils→Typst translator; docutils `field_list`/`docfields` structure
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

See `.planning/phases/38-structural-indentation-info-fields/38-CONTEXT.md` § Implementation
Decisions for the full text (D-01 through D-14, each with its own measured evidence table). Binding
summary, copied verbatim in substance:

- **D-01:** `desc_content` is wrapped in `pad(left: SHARED_INDENT_STEP, { … })`; nesting is left to
  compose structurally — there is no depth counter.
- **D-02:** `SHARED_INDENT_STEP` stays `"2.5em"`. Do not re-value it.
- **D-03:** the field list takes its own `pad` step, nested inside the body's — no separate constant.
- **D-04:** `visit_block_quote`/`depart_block_quote` are NOT touched — this is the binding reading of
  IND-04.
- **D-05:** FLD-03 uses the reference recipe — parameter name `strong(raw("…"))` bold monospace, type
  `emph(raw("…"))` italic monospace (owner choice, variant "A").
- **D-06:** FLD-03 is satisfied as written under D-05; do NOT amend REQUIREMENTS.md, and do not
  re-open this at verify time. The mechanical assertion must be written per sub-part (name vs type vs
  label), never as one blanket check over the field body.
- **D-07:** FLD-02's "inline prose" means the label and a single-value body share one line (owner
  choice). REQUIREMENTS.md's parenthetical about `_last_field_body_was_inline` is stale as a
  description of the docstring case — do not take it as evidence that nothing needs doing.
- **D-08:** the reason this matters is measured, not aesthetic — whole-document consequence on this
  project's own docs: 97 pages → 87 pages.
- **D-09:** `literal_strong`/`literal_emphasis` must stop delegating through the dummy-node trick,
  exactly as Phase 36's ADM-06 did for `desc_signature`/`rubric`. Whether the replacement is verbatim
  triplication or a shared helper is Claude's call (D-12), but the delegation itself is not a viable
  base to build D-05 on.
- **D-10:** Phase 38 voids the premise of Phase 37's SIG-08 fix, and must own the consequence — the
  planner must decide, with a fixture, whether the new emission is correct as-is or needs the
  bookkeeping reshaped, and must not simply assume Phase 37's mechanism still holds.
- **D-11:** the wrapper must not fight `block(sticky: true, …)` — a property to assert, not to assume.

### Claude's Discretion

- **D-12:** the indent primitive (`pad(...)` vs `block(inset:...)`) and the emission mechanics are
  Claude's to choose, decided by measurement. Binding constraints: compose on nesting without a
  counter; must not add vertical space reopening SIG-08's doubled-gap shape; must survive a page
  break with the indent intact; must route through `self.add_text(...)`, never
  `self.body.append(...)`. Same freedom covers the newline/`list_item_needs_separator` bookkeeping
  around the wrapper, and the mechanics of D-07's inline field.
- **D-13:** the stray `parbreak()` at the head of each bulleted field-list item is Claude's to fix or
  leave. Not raised with the owner. If touched, it needs its own assertion; if left, say so
  explicitly rather than silently.
- **D-14:** the exact-string migration strategy is Claude's to choose, under one non-negotiable
  constraint: ROADMAP SC#5 requires this phase's blast radius to be migrated inside the phase by
  hand-derived expected strings plus a recorded census (never regenerated from the new code's own
  output). Re-measure the census; do not inherit Phase 37's.

### Deferred Ideas (OUT OF SCOPE)

- Nothing new was deferred from this discussion. Scope stayed inside IND-01..05 and FLD-01..03 plus
  two folded todos (the stale `_desc_break_marker`/`self.body` reassignment hazard, and the
  pre-`37-09`-misnamed `EXPECTED_PAGE_COUNT_PRE_PHASE` constant) — both already live inside handlers
  this phase necessarily rewrites. Out of scope for this phase specifically: `desc_signature` and its
  inline children (Phase 37, complete); `rubric`/admonitions (Phase 39); citations (Phase 40); any
  user-overridable styling (Future STY-01/02/03).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| IND-01 | `desc_content` body indented one step relative to its own `desc_signature` | Architecture Pattern 1 (`pad()` composition, verified via compiled probe); Pattern 2 (measurement technique) |
| IND-02 | Indentation cumulative with nesting depth | Pattern 1 — verified on a 3-level compiled probe this session |
| IND-03 | A nested member's own signature aligns with its parent's body, no further step | Pattern 1 — verified: the nested signature is plain content inside the still-open outer `pad`, not re-wrapped |
| IND-04 | One shared indent constant drives desc nesting, field lists, and block quotes | `SHARED_INDENT_STEP` already exists (Phase 37 D-08); confirmed via grep this session that no second indent literal exists anywhere in `typsphinx/` (D-04) |
| IND-05 | Depth resets correctly across sibling `desc` nodes, no leak | Pattern 1 — verified: the probe's top-level sibling after a 3-level nest returns fully to the page margin |
| FLD-01 | Field list indented one step beyond the surrounding description body | Same `pad()` mechanism as IND-01, applied independently to `field_list` (D-03); Code Examples § |
| FLD-02 | Multi-value field body renders as bulleted list (non-regression); single-value stays inline prose | Pattern 3 — root cause traced to `docfields.py`, fix reuses the existing `_in_field_body` inline-concat context; Pitfall 4 flags an adjacent, separable cosmetic defect (D-13) not to conflate with this requirement |
| FLD-03 | Parameter name/type carry monospace treatment distinct from the plain-bold field label | Pattern 4 — verified leaf-emission shape (`strong(raw(...))`/`emph(raw(...))`), explicitly NOT reusing `_emit_signature_leaf_wrapper` (Pitfall avoided); Pitfall 2 covers the resolvable-cross-reference composition case |

</phase_requirements>

## Summary

Phase 38 has no new external dependency, no new package, and no new file format to learn — the
entire domain is (a) how Typst's stdlib `pad()` composes across nested code-mode calls, and (b) the
exact shape docutils' `docfields.py` hands the translator for `:param:`/`:type:`/`:returns:` field
lists. Both were verified **empirically this session** — not from training-data recall — by
compiling real Typst through `typst-py` 0.15.0 and by running a real `sphinx-build -b typst` against
hand-written fixtures, then reading the emitted `.typ` byte-for-byte.

The headline finding: `desc_content`'s wrap-in-`pad(left: SHARED_INDENT_STEP, { … })` (D-01)
composes correctly with **zero extra bookkeeping** — nesting, non-leaking depth, and "nested
signature aligns with parent body" all fall out of `pad()`'s own block-nesting semantics, verified in
this session by compiling a synthetic 3-level fixture and reading `pypdf`'s **layout-mode** text
extraction (`extraction_mode="layout"`), which reconstructs left-edge indentation as leading
whitespace — the fallback this phase needs, since `pypdf`'s per-glyph `visitor_text` positions are
still unusable on Typst PDFs (`x=0, y=0`, the same limitation Phase 37 already documented). The
second finding is a genuine regression this session reproduced **on the current tree with a one-line
patch**: making `depart_desc_content` emit anything at all (as D-01 requires) breaks the SIG-08
duplicate-`parbreak()` suppression for the specific "nested `desc` with no trailing sibling content"
shape — proven against the project's own existing `tests/fixtures/signature_break_and_arrow_gate`
fixture, both broken (9 `parbreak()` instead of 8) and fixed (a one-line marker-propagation change
that restores 8) empirically in this session. The third finding is that D-07's "single-value field
body stays inline" defect has an exact, narrow root cause — a single-`nodes.paragraph` field body is
wrapped in Typst's own `par()`, which is unconditionally block-level and therefore starts a new
visual line regardless of any separator bookkeeping — and the fix composes with the field body's
*existing* inline-concat machinery (`_in_field_body`/`_field_body_has_content`), verified by tracing
`sphinx/util/docfields.py`'s `Field.make_field`/`GroupedField.make_field` to confirm every
single-value field body is *always* exactly one `paragraph` node, with no exceptions.

**Primary recommendation:** wrap `desc_content` and `field_list` each in their own
`pad(left: SHARED_INDENT_STEP, { … })`, routed through `self.add_text(...)` (never
`self.body.append(...)`, per the table-cell hazard already documented in CONTEXT.md D-12); fix
`depart_desc`'s SIG-08 marker by having `depart_desc_content` **propagate** the marker through its
own now-unavoidable closing bytes rather than treating them as "real" content (working patch
verified below); implement D-07's inline single-value field body by unwrapping the lone `paragraph`
child into the field body's existing `_in_field_body` concat context (mirroring the
already-working collapsed-inline case) instead of inventing a new mechanism; and give
`literal_strong`/`literal_emphasis` their own verbatim leaf-emission bodies (D-09) that reuse
`escape_typst_string` directly — **not** `_emit_signature_leaf_wrapper`, which unconditionally
injects the SIG-07 zero-width-space escape that no FLD decision asks for and that field-body
identifiers do not need.

## Architectural Responsibility Map

This project is a compiler pipeline (doctree → translator → template engine → `.typ` → PDF), not a
multi-tier web application, so the generic Browser/Server/API/CDN tiers do not apply. The table below
uses this project's own tiers (see `CLAUDE.md` § Architecture) as the closest faithful mapping.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `desc_content` structural indent (IND-01..05) | Translator (`visit/depart_desc_content`) | — | Pure node-to-Typst-call emission; no template or builder involvement |
| Field-list indent (FLD-01) | Translator (`visit/depart_field_list`) | — | Same pattern, reuses the same shared constant |
| Field-body list-vs-inline rendering (FLD-02) | Translator (`visit_field_body`, `visit_paragraph`) | — | Docutils already produces the right node shape (`bullet_list` vs. single `paragraph`); the translator only needs to route the single-paragraph case through the existing inline path |
| Field-body monospace typography (FLD-03) | Translator (`visit/depart_literal_strong`, `visit/depart_literal_emphasis`) | — | Leaf-emission, mirrors the Phase 37 `desc_sig_name` pattern but with a distinct (non-ZWSP) escape helper |
| Shared indent constant (IND-04) | Translator (module-level `SHARED_INDENT_STEP`) | — | Already exists (Phase 37, D-08); this phase is its second and third consumer, no new constant |
| `SIG-08` break-suppression interaction (D-10) | Translator (`depart_desc`, `depart_desc_content`) | — | A structural side effect of IND-01's wrapper; must be re-verified, not assumed to still hold |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Typst stdlib `pad()` | Typst 0.15 (pinned via `typst-py` 0.15.0, already a project dependency) | "Adds spacing around content" — the layout primitive this phase uses to indent `desc_content`/`field_list` | Official Typst stdlib function, `[CITED: https://typst.app/docs/reference/layout/pad]`. Zero new dependency: `typst-py` is already pinned and `pad` ships in it. Not used anywhere in `typsphinx/` yet — `grep -n '"pad('  typsphinx/translator.py typsphinx/templates/*.typ` returns nothing `[VERIFIED: grep, this session]` — so this is Phase 38's first use of the primitive, not a re-use of an existing pattern. |

No new package is installed or imported by this phase. Milestone invariant #1 (zero new runtime
dependencies) and #2 (`@preview` package count stays at four) are untouched — this phase adds no
`import` statement anywhere, only new Typst *stdlib* calls inside already-generated code-mode
strings.

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pypdf` | 6.14.2 (already pinned, per Phase 37) | Layout-mode text extraction for indent-position gates (SC#1/SC#2) | `page.extract_text(extraction_mode="layout")` — see Code Examples; per-glyph `visitor_text` positions remain unusable (`x=0, y=0`, re-confirmed this session) |
| `typst-py` | 0.15.0 (already pinned) | Compiling probes and fixtures for RED/GREEN gates | Same GATE-01 real-compile pattern as every prior phase |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pad(left: SHARED_INDENT_STEP, { … })` | `block(inset: (left: SHARED_INDENT_STEP), { … })` | `block()` carries its own `above`/`below` spacing defaults (the exact hazard Phase 37's SIG-08/wrapper amendment had to work around) and would need an explicit `spacing:`/`above:`/`below:` override to avoid re-opening that class of defect. `pad()` adds **zero** default vertical spacing of its own — `[VERIFIED, this session]` a `pad(left: 2.5em)[...]` compiled directly against an unwrapped baseline reported identical vertical extents in a `context measure(...)` probe. `pad` is the lower-risk choice and is what the owner's own prototype used (CONTEXT.md D-12). Left as Claude's discretion per D-12, but `pad` is the recommended default absent a reason to prefer `block`. |
| One `pad()` per desc/field-list level (composition, no counter) | A `self._desc_depth` integer multiplied into an inline `left: {depth}*SHARED_INDENT_STEP` | Explicitly **rejected by D-01**: a depth counter must be manually reset on every sibling boundary and is exactly the "leak across sibling desc nodes" failure mode IND-05 exists to prevent. Nesting `pad()` calls delegates depth-tracking to Typst's own layout engine, which cannot leak because each `pad()` closes with its own node's `depart_*`. |

**Installation:** none — no new packages.

**Version verification:** `typst-py` 0.15.0 and `pypdf` 6.14.2 are already pinned by Phase 37 and
present in this worktree's `.venv`; re-confirmed present and importable this session
(`uv run python -c "import typst, pypdf"` succeeds). Typst's `pad()` signature/behaviour was
verified directly against the compiler, not just the docs page, by compiling three probes this
session (see Code Examples).

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** Milestone invariant #2 (`@preview`
package count stays at four, no new lockstep site) is unaffected: `pad()` and `block()` are Typst
stdlib, requiring no `#import`. No `npm view`/`pip index versions`/`cargo search` verification is
needed because nothing is added to `pyproject.toml`, `uv.lock`, or any `#import "@preview/..."` line.

## Architecture Patterns

### System Architecture Diagram

```
doctree (py:class > desc_signature, desc_content > [paragraph, field_list, py:method(nested desc)])
        │
        ▼
TypstTranslator.visit_desc_content ──emits──> "pad(left: 2.5em, {"
        │
        ├─ children stream normally (existing visitors, unmodified)
        │     │
        │     └─ nested desc (py:method) ──> block(sticky:true, par(hanging-indent:2.5em,{...}))
        │                                     [aligns with the OUTER pad's left edge — NOT re-indented,
        │                                      because it is plain content flowing inside the open pad]
        │                                     followed by ITS OWN visit_desc_content ──emits──>
        │                                     a SECOND, NESTED "pad(left: 2.5em, {" — this is where
        │                                      IND-02's cumulative +2.5em comes from
        │
        ├─ field_list ──emits──> "pad(left: 2.5em, {" (its own, independently nested step, FLD-01)
        │     │
        │     ├─ field_body with 2+ items ──> docutils already produced a bullet_list ──>
        │     │     existing visit_bullet_list ──> "list({...}, {...})" (FLD-02's bulleted half,
        │     │      ALREADY correct — no translator change needed here)
        │     │
        │     └─ field_body with exactly 1 paragraph child ──> UNWRAP the paragraph, route its
        │           children through the EXISTING _in_field_body inline-concat context (the same
        │           mechanism the all-inline collapsed case already uses) instead of "par({...})"
        │           ──> flows onto the SAME output line as the field_name's strong(...) (FLD-02's
        │            inline half, this phase's real work, D-07)
        │
        └─ depart_desc_content ──emits──> "})" (closes the pad) ──> THIS byte advancing
              self.body's length is what silently disarms depart_desc's SIG-08 marker (D-10) —
              depart_desc_content must PROPAGATE the marker through its own close (see Pitfall 1)
```

### Recommended Project Structure

No new files or directories — every change is inside the existing `typsphinx/translator.py` (the
handlers CONTEXT.md's `<domain>` section already enumerates). No new test *files* are strictly
required either, though a new render-gate fixture (mirroring
`tests/fixtures/signature_break_and_arrow_gate`'s pattern: one `.rst` exercising every SC in one
build) is the established project convention for Wave 0 (see `tests/fixtures/desc_rubric_decoupling_render_gate/`,
`tests/fixtures/signature_typography_gate/` for the precedent).

### Pattern 1: `pad()` composes correctly across nesting — no counter needed (D-01)

**What:** wrapping `desc_content` (and, separately, `field_list`) in
`pad(left: SHARED_INDENT_STEP, { <children> })` produces exactly the indent table CONTEXT.md's D-01
specifies, with **no depth-tracking state** — nesting is delegated entirely to Typst's own
containment/layout, and a nested member's *own signature* is genuinely not further indented because
it is plain content flowing inside the still-open outer `pad`, not a second `pad` around itself.

**When to use:** every site IND-04 names (`desc_content`, `field_list`) and nowhere else
(`block_quote` is explicitly out of scope, D-04).

**Verified this session** — compiled directly through `typst-py` 0.15.0, `extraction_mode="layout"`
text reconstruction shown as-is (each column of leading spaces below is one accumulated indent
step):

```python
# Source: this session's own probe, compiled via typst.compile()
src = '''
#set page(width: 300pt, height: 300pt, margin: 20pt)
#set text(size: 11pt)
#{
block(sticky: true, par(hanging-indent: 2.5em, {raw("class")
raw(" ") + strong(raw("Widget"))}))
pad(left: 2.5em, {
par({text("Class body paragraph.")})
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("resize"))}))
pad(left: 2.5em, {
par({text("Method body paragraph.")})
})
par({text("Class body continues.")})
})
par({text("Top level function body.")})
}
'''
```

Resulting layout-mode extraction:

```
class Widget
       Class body paragraph.

       resize
              Method body paragraph.
       Class body continues.
Top level function body.
```

This directly demonstrates, in one compiled artifact: IND-01 (`Class body paragraph.` is indented
past `class Widget`'s own left edge), IND-02 (`Method body paragraph.` is indented one further step
past `Class body paragraph.`), IND-03 (`resize`, the nested signature, aligns with `Class body
paragraph.` — it gets **no** extra step), and IND-05 (`Top level function body.` returns all the way
to the page margin — nothing leaks).

### Pattern 2: `pypdf` layout-mode extraction as the indent-measurement technique for SC#1/SC#2

**What:** `pypdf`'s per-glyph `visitor_text` callback still reports `x=0, y=0` on Typst-generated
PDFs in this sandbox `[VERIFIED, re-confirmed this session, matches Phase 37's prior finding]`.
`page.extract_text(extraction_mode="layout")`, however, reconstructs a monospace-like character grid
from the PDF's actual glyph positions and **does** preserve left-edge indentation as leading
whitespace — verified this session on a minimal two-line probe (flush text vs. `pad(left: 2.5em)`)
and on the full 3-level nesting probe above.

**When to use:** any SC#1/SC#2/SC#3-style "is X's left edge strictly greater than Y's" assertion.
The ROADMAP phrase "measured from `pypdf` bounding boxes" should be read as "measured via `pypdf`'s
layout-mode text-grid reconstruction, which is position-derived even though it is not a literal
per-glyph bounding-box API" — the literal per-glyph bbox API (`visitor_text`) does not work on this
project's PDFs, a limitation Phase 37 already hit and documented, and this session re-confirmed still
holds.

**Caveat:** layout-mode columns are **not** exact point measurements — they are a text-grid
approximation. For a *relative* assertion ("nested body's left edge > parent's left edge", "nested
signature's left edge == parent body's left edge") this is sufficient and was exactly how this
session's probes above were read. For an assertion that needs an exact point value (as Phase 37's
SIG-07 needed for column-width overflow), continue using Typst-side `context measure(...)`/
`context layout(...)` probes concatenated onto the emitted `.typ` before compiling — the pattern
`tests/test_signature_overflow_render_gate.py` and `tests/test_signature_page_boundary_render_gate.py`
already establish. Phase 38's SCs are relative ("strictly greater than"), so layout-mode text is
adequate on its own; do not over-engineer a `context measure()` probe where a leading-whitespace
comparison already proves the property.

```python
# Source: this session's own probe, using pypdf 6.14.2
import pypdf, io
reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
page = reader.pages[0]
layout_text = page.extract_text(extraction_mode="layout")
# Compare leading-whitespace run-length per line, or locate known marker
# substrings and compare their column offset within layout_text.
```

### Pattern 3: unwrap a single-`paragraph` field body into the existing inline-concat context (D-07)

**What:** tracing `sphinx/util/docfields.py` (both `Field.make_field`, used by `:returns:`/`:rtype:`,
and `GroupedField.make_field`'s `can_collapse` branch, used by a single `:param:`) shows the
single-value field body is **always** exactly one `nodes.paragraph` child — no other shape is
possible for this case `[VERIFIED: read sphinx/util/docfields.py:140-183,201-244 this session,
cross-checked by a real sphinx-build probe]`. The reason the label and value currently land on
separate lines is **not** a missing separator — it is that `visit_paragraph` unconditionally emits
`par({ ... })`, and Typst's `par()` is intrinsically block-level, so it starts its own visual
paragraph regardless of what cosmetic newline or lack thereof precedes it in the source `.typ`. The
already-working collapsed-inline case (a confval `:default:` written on one line) proves the
opposite path works: because its children are emitted as **bare, non-`par()`-wrapped** inline
content (`text(...)`, `strong({...})`, …) via the `_in_field_body`/`_field_body_has_content` concat
context, they flow onto the SAME implicit paragraph as the preceding `field_name`'s
`strong(...)` — no `+` join is even required between the label and the body; adjacent non-block
content in the same code-mode block simply flows together in Typst.

**When to use:** `visit_field_body`'s existing `all_inline` classification (line ~5443,
`all(isinstance(child, (nodes.Text, nodes.Inline)) for child in node.children)`) needs a **second**
case added — `len(node.children) == 1 and isinstance(node.children[0], nodes.paragraph)` — that
activates the *same* `_in_field_body = True` context, but additionally needs the lone paragraph's own
`visit_paragraph`/`depart_paragraph` to skip emitting the `par({`/`})` wrapper and instead behave like
the existing `self.in_list_item` fast-path (`visit_paragraph` already has this exact shape of
special-case branch for list items — see Code Examples). The paragraph's *children* then dispatch
completely unmodified, through the exact same `_emit_inline_concat_separator`/
`_mark_inline_concat_content`/`_enter_inline_concat_element` machinery the collapsed-inline case
already exercises for `Text`/`strong`/`emphasis`/`reference`/`literal_strong`/`literal_emphasis`
children — none of which needs new code of its own to support this.

**Downstream consequence to verify, not assume:** `depart_field`'s FID-09 inter-field `"  "`
separator is gated on `self._last_field_body_was_inline` (set from `self._in_field_body` at
`depart_field_body`). Once this pattern makes single-paragraph bodies also set
`_in_field_body = True`, `_last_field_body_was_inline` becomes `True` for `:returns:`/`:rtype:`/
`:raises:` fields too — which is *exactly* what D-08's vertical-rhythm goal wants (collapsing the
three-different-intervals problem down to one), but it is a real behavioural change to
`depart_field`'s firing pattern that needs its own fixture assertion, not an assumption that CR-01's
existing comment ("only correct for inline-collapsed bodies") still describes the full picture.

**Example — mirrors the existing list-item fast-path already in `visit_paragraph`:**

```python
# Source: typsphinx/translator.py:800-837 (existing code, shown as the PATTERN to extend)
def visit_paragraph(self, node: nodes.paragraph) -> None:
    self._emit_id_anchors(node)
    if self.in_list_item:
        self._emit_forced_break("parbreak()")
        self.in_paragraph = False
        return
    # NEW: an analogous fast-path keyed on the field-body single-paragraph
    # classification set in visit_field_body would go here, BEFORE the
    # par({ wrap below -- skip the wrapper, let children dispatch inline.
    self.in_paragraph = True
    self.paragraph_has_content = False
    self.add_text("par({")
```

### Pattern 4: `literal_strong`/`literal_emphasis` get their own leaf-emission bodies, NOT `_emit_signature_leaf_wrapper` (D-09, D-05)

**What:** `visit_literal_strong`/`visit_literal_emphasis` currently delegate through a dummy-node
trick to `visit_strong`/`visit_emphasis`, producing the content-block shape `strong({text("width")})`
`[VERIFIED: real sphinx-build probe this session]`. D-05's target shape is `strong(raw("width"))` —
the code-mode-call shape, matching Phase 37's `desc_name`/`desc_sig_name` precedent, not the
content-block shape. The tempting shortcut — reuse `_emit_signature_leaf_wrapper` (Phase 37's
helper, which already produces exactly `wrapper(raw("..."))`) — is a **trap**:
`_emit_signature_leaf_wrapper` calls `self._escape_signature_text`, which unconditionally injects the
`\u{200B}` zero-width-space break opportunity after every `.` (the SIG-07 mechanism). No FLD
requirement or CONTEXT.md decision asks for ZWSP injection in field-body parameter echoes, field
bodies are not measured to overflow the way dotted signature qualnames are, and introducing it here
would be new, unauthorized, unmeasured behaviour smuggled in under an unrelated refactor.

**When to use:** write two small, independent leaf-emission bodies (mirroring Phase 36 D-01's
"deliberate triplication" precedent, which D-09 explicitly cites as the pattern to follow) that reuse
`escape_typst_string` directly — the same helper `visit_literal`'s leaf branch already uses with no
ZWSP — not `_escape_signature_text`.

```python
# Source: this session, modelled on typsphinx/translator.py:1427-1505 (visit_literal's
# leaf-emission shape) -- escape_typst_string only, no ZWSP injection.
def visit_literal_strong(self, node: nodes.inline) -> None:
    self._add_paragraph_separator()
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
    escaped = escape_typst_string(node.astext())
    prefix = "#" if self._in_markup_mode else ""
    self.add_text(f'{prefix}strong(raw("{escaped}"))')
    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True
    raise nodes.SkipNode
# visit_literal_emphasis: identical shape, wrapper name "emph" instead of "strong".
```

**Verified this session that `literal_emphasis` is not always the outermost node:** a `:type:` field
whose value resolves as a cross-reference (e.g. `:type width: Widget` where `Widget` is a `py:class::`
defined in the same doc) produces `literal_emphasis` **nested inside** a `reference` node, which the
translator already renders as `link(<label>, ...)`. A real probe this session compiled to:

```
link(<index:Widget>, 
emph({text("Widget")}))
```

(the pre-phase shape). Under the fix this becomes `link(<index:Widget>, emph(raw("Widget")))` — the
new leaf body must compose correctly as a `link()` argument exactly the way `visit_desc_sig_name`
rule 3 already lets a resolved cross-reference's `raw(...)` compose inside `link()` in the signature
family (Phase 37 contract §5.2). Do not special-case this: the generic leaf-emission shape (not a
`raise nodes.SkipNode`-avoiding early return, and no `isinstance` check on the parent) composes
correctly here for the same reason it already does in the signature family — `link()`'s second
argument is just a content value, and `emph(raw(...))`/`strong(raw(...))` are both content values
regardless of what wraps them.

### Anti-Patterns to Avoid

- **A `self._desc_depth` counter for indentation.** Explicitly rejected by D-01/IND-05 — a counter
  must be manually zeroed at every sibling boundary and is precisely the "leak" failure mode this
  phase must prove does *not* happen. `pad()` nesting needs no counter at all (Pattern 1).
- **Reusing `_emit_signature_leaf_wrapper` for `literal_strong`/`literal_emphasis`.** Injects an
  unauthorized ZWSP escape into field-body text (Pattern 4).
- **Treating `depart_desc_content`'s new closing bytes as a normal `add_text` call with no marker
  awareness.** Silently reopens the SIG-08 double-`parbreak()` defect for nested-`desc`-with-no-
  trailing-content (Pitfall 1, verified below with a working one-line fix).
- **Inventing a new state flag for D-07's single-value inline join.** The existing
  `_in_field_body`/`_field_body_has_content` concat context already does everything needed; a
  second mechanism would duplicate logic that must then be kept in sync by hand (Pattern 3).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Nested indentation that doesn't leak across siblings | A depth counter with manual reset logic | `pad(left: SHARED_INDENT_STEP, { … })`, one call per nesting site, no shared state | Typst's own block-containment model already provides correct nesting/reset semantics; verified this session across a 3-level fixture with zero extra Python state |
| "Is A's left edge greater than B's" PDF assertion | A custom PDF content-stream parser to recover glyph coordinates | `pypdf.PdfReader(...).pages[i].extract_text(extraction_mode="layout")`, compare leading-whitespace / column offsets | `pypdf`'s own layout-mode reconstruction already does the glyph-position-to-text-grid work; per-glyph `visitor_text` is proven unusable on this project's PDFs (both this session and Phase 37) |
| Detecting whether a field body is "multi-value" | A heuristic scan of field-body text for delimiters | `isinstance` check on the field body's existing docutils shape (`bullet_list` present → multi-value; else check paragraph count) | docutils' own `docfields.py` (`GroupedField`/`TypedField`) already decides multi-vs-single and encodes it structurally — the *shape* of the doctree is the ground truth, not a text heuristic |

**Key insight:** every "hand-roll" temptation in this phase (indent depth tracking, PDF geometry
parsing, field-body shape detection) already has a structural, verified-this-session substitute one
layer below the translator — Typst's own layout engine, `pypdf`'s layout-mode extraction, and
docutils' own field-body node shape, respectively. The translator's job stays "map node shape to
Typst call", never "recompute a layout property Typst or docutils has already computed".

## Common Pitfalls

### Pitfall 1: `depart_desc_content`'s new emission silently disarms the SIG-08 marker

**What goes wrong:** the SIG-08 fix (`depart_desc`, Phase 37 D-12/contract §8) suppresses a duplicate
`parbreak()` by testing `self._desc_break_marker == len(self.body)` — "was anything appended since
the immediately preceding desc's own break". Once `depart_desc_content` emits its `pad()` closer
(D-01's requirement), `len(self.body)` **always** advances between an inner `desc`'s break and an
outer `desc`'s break, so the suppression can never fire again for a nested `desc` with no trailing
sibling content — reintroducing exactly the doubled-`parbreak()` defect SIG-08 fixed.

**Why it happens:** the marker's "was anything appended" heuristic cannot distinguish "a
zero-height wrapper-closing token" from "real content" — both advance `len(self.body)` identically.

**Reproduced empirically this session**, on the project's own existing
`tests/fixtures/signature_break_and_arrow_gate` fixture (which already contains the exact
"class with a one-line body containing a nested method with its own one-line body" SIG-08 shape,
`SigBreakOuterClassOne`), by patching `depart_desc_content` to emit a single marker token and
rebuilding with `sphinx-build -b typst`:

```
# BEFORE (current translator): 8 total parbreak() in the fixture's .typ, exactly ONE
# between SigBreakOuterClassOne's nested method and the next heading.
#
# AFTER (depart_desc_content emits ANY byte): 9 total parbreak() -- TWO adjacent
# parbreak() reappear at exactly that boundary:
#   ...PADCLOSEparbreak()
#   PADCLOSEparbreak()
```

**How to avoid — verified working fix (one-line change to `depart_desc_content`), reproduced this
session restoring the count to 8:**

```python
# Source: this session's own patch, verified via a real sphinx-build -b typst rebuild
# of tests/fixtures/signature_break_and_arrow_gate (parbreak() count: 9 -> 8, matching
# the pre-phase baseline exactly, including which boundary gets which count).
def visit_desc_content(self, node: addnodes.desc_content) -> None:
    self.add_text(f"pad(left: {SHARED_INDENT_STEP}, {{")

def depart_desc_content(self, node: addnodes.desc_content) -> None:
    # Propagate the SIG-08 marker THROUGH this close: if nothing "real" was
    # emitted since the marker was last set, closing the pad doesn't count
    # as real content either -- advance the marker past our own bytes too,
    # so the OUTER desc's depart_desc still sees "nothing happened" and
    # correctly suppresses its own duplicate break.
    propagate = self._desc_break_marker == len(self.body)
    self.add_text("})")
    if propagate:
        self._desc_break_marker = len(self.body)
```

Re-verified the "content follows the nested member" control case
(`SigBreakOuterClassTwo`, which has a trailing paragraph after its nested method) is **unaffected**
by either the regression or the fix — it correctly keeps exactly one break both before and after,
in all three variants compiled this session (pre-phase / broken / fixed).

**Warning signs:** any GATE-01 fixture built from `tests/fixtures/signature_break_and_arrow_gate`'s
pattern showing a `parbreak()` count off by exactly +1 per nested-`desc`-with-no-trailing-content
occurrence; a rasterised page showing visibly doubled vertical gap between a nested member's body and
the next heading/section.

### Pitfall 2: field-body cross-references can wrap `literal_emphasis`/`literal_strong` — don't assume they're always the outermost node

**What goes wrong:** a naive `visit_literal_emphasis` that assumes it is always called directly under
`field_body`/`paragraph` (never inside a `reference`) would still work for the *common* case (an
unresolved type name), but the assumption is false and untested for the *resolvable* case.

**Why it happens:** `sphinx/util/docfields.py`'s `Field.make_xref` wraps `literal_emphasis` inside a
`pending_xref` when the type role resolves — Sphinx's own `Builder.write()` resolves this to a
`reference` node before the translator ever sees the doctree (same mechanism Phase 37's contract §5.2
already documents for signature parameters).

**How to avoid:** verified this session — a plain, generic leaf-emission body (no `isinstance` check
on `node.parent`) composes correctly as a `link()` argument with zero special-casing, because
`link()`'s body argument is just a content value. Write the fix the way Pattern 4 above does, and
add a fixture exercising a resolvable `:type:` (a `:type foo: SomeLocalClass` where `SomeLocalClass`
is a `py:class::` in the same doc) so this composition is asserted, not merely assumed.

**Warning signs:** a test suite with only unresolved-type fixtures (`int`, `str`) would pass even if
this composition were broken — the resolvable-type case is the one that would catch it.

### Pitfall 3: `pypdf`'s per-glyph position API remains unusable — don't reach for it

**What goes wrong:** `pypdf.PageObject.extract_text(visitor_text=...)` reports `x=0, y=0` for every
glyph on Typst-generated PDFs in this sandbox.

**Why it happens:** unresolved upstream/environment interaction between Typst's PDF generation and
`pypdf`'s text-matrix parsing — Phase 37 documented this and this session's own re-probe reproduced
the identical `x=0.0, y=0.0` result on a fresh two-line test PDF.

**How to avoid:** use `extraction_mode="layout"` (Pattern 2) for relative left-edge comparisons, or a
Typst-side `context measure(...)`/`context layout(...)` probe concatenated onto the `.typ` before
compiling (the established Phase 37 pattern) when an exact point value is required.

**Warning signs:** any new test that calls `extract_text(visitor_text=...)` and asserts on the
reported `x`/`y` values directly — this will silently pass or fail on `0.0` regardless of the actual
rendered position, producing a test that cannot detect the defect it claims to guard.

### Pitfall 4: the "stray `parbreak()` at the head of every list item" is a pre-existing, unrelated behaviour (D-13)

**What goes wrong:** `visit_paragraph`'s `if self.in_list_item:` fast-path calls
`self._emit_forced_break("parbreak()")` **unconditionally** — including for the very FIRST paragraph
in a list item, not just the second-and-later ones the FID-02 docstring describes. This adds a
`parbreak()` immediately after every `list_item`'s opening `{`, even when there is nothing to
separate from.

**Why it happens:** `visit_list_item` resets `list_item_needs_separator = False` on entry, but
`_emit_forced_break`'s own logic still unconditionally emits the break token regardless of that flag
— the flag only gates the *leading newline*, not the break itself.

**How to avoid / whether to avoid:** this is D-13, explicitly **Claude's discretion** — it is
cosmetic (measured ~7.15pt of extra space before a bulleted field's first item, per CONTEXT.md), it
predates this phase, and it sits inside a handler this phase's field-body work touches anyway
(`visit_field_body`'s multi-value path routes through the general `visit_bullet_list`/
`visit_list_item`/`visit_paragraph` machinery). If left untouched, say so explicitly in the phase's
own record rather than silently; if fixed, it needs its own fixture assertion (do not fold it
silently into a FLD-02 assertion, since it is not what FLD-02 requires).

**Warning signs:** a "before/after" spacing comparison on the bulleted-Parameters case showing an
unexplained ~7pt gap above the first bullet that neither FLD-01 nor FLD-02 predicts.

## Code Examples

Verified patterns from this session's own direct compilation/build (no external doc citations needed
beyond `pad`'s official reference page, already cited above):

### Indenting `desc_content` and `field_list` (Pattern 1 combined with FLD-01)

```python
# Source: this session's verified probe (compiles clean under typst-py 0.15.0)
def visit_desc_content(self, node: addnodes.desc_content) -> None:
    self.add_text(f"pad(left: {SHARED_INDENT_STEP}, {{")

def depart_desc_content(self, node: addnodes.desc_content) -> None:
    propagate = self._desc_break_marker == len(self.body)
    self.add_text("})")
    if propagate:
        self._desc_break_marker = len(self.body)

def visit_field_list(self, node: nodes.field_list) -> None:
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
        self.list_item_needs_separator = False
    self.add_text(f"pad(left: {SHARED_INDENT_STEP}, {{")   # NEW

def depart_field_list(self, node: nodes.field_list) -> None:
    self.add_text("})\n")                                   # was: self.body.append("\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
```

`field_list`'s pre-phase `depart_field_list` uses `self.body.append("\n")` directly (bypassing
`add_text`) — D-12's `add_text`-not-`body.append` constraint means this line must change to
`self.add_text(...)` regardless of the pad wrapper, since a `field_list` inside a table cell would
otherwise misroute today. Worth flagging as a latent, unrelated-but-adjacent bug this phase's own
touch of the function surfaces.

### Measuring relative indentation from a compiled PDF (Pattern 2)

```python
# Source: this session's own probe against typst-py 0.15.0 + pypdf 6.14.2
import typst, pypdf, io

pdf_bytes = typst.compile(emitted_typ_source.encode())
reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
layout_text = reader.pages[0].extract_text(extraction_mode="layout")
# Find each marker line and compare len(line) - len(line.lstrip(" ")):
# a strictly greater leading-space count is the SC#1/SC#2 assertion.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `desc_content` flush with its own signature (no indent at all) | `desc_content` wrapped in `pad(left: 2.5em, {...})` | This phase | Page now visually shows containment; SIG-08's marker logic needs the propagation fix above |
| Field-list parameter name/type in proportional bold/italic (`strong({text(...)})`/`emph({text(...)})`) | Monospace bold/italic (`strong(raw(...))`/`emph(raw(...))`) | This phase (FLD-03) | Matches the reference's `docfields.py` recipe (bold-mono name / italic-mono type), distinct from the signature's own (italic-mono name / regular-mono type) recipe — D-06 explicitly accepts this partial overlap |
| Single-value field body on its own line (`par({...})` after the label) | Single-value field body inline with its label | This phase (FLD-02/D-07) | Measured whole-document consequence on this project's own docs: 97 pages → 87 pages (CONTEXT.md D-08) |

**Deprecated/outdated:** none — this phase introduces `pad()` as a first-time-used stdlib primitive;
nothing existing is being replaced by a newer library version.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ROADMAP SC#1/SC#2's "measured from `pypdf` bounding boxes" is satisfiable via `extraction_mode="layout"` text-grid reconstruction rather than a literal per-glyph bounding-box API, because the literal API is proven unusable on this project's PDFs | Pattern 2, Pitfall 3 | Low — verified empirically this session on both a minimal probe and the full 3-level nesting probe; the same substitution Phase 37 already made and had accepted at verification |
| A2 | `pad()` (vs. `block(inset:)`) is the correct default primitive absent an owner objection | Standard Stack § Alternatives Considered | Low — CONTEXT.md D-12 explicitly leaves this as Claude's discretion; `pad` is what the owner's own real-compiled prototype used, and is measured to add zero default vertical spacing, avoiding a repeat of Phase 37's `block()` spacing hazard |
| A3 | The SIG-08 marker-propagation fix sketched in Pitfall 1 is A viable fix, not THE mandated fix | Pitfall 1 | Low — D-10 explicitly leaves the *fix* undetermined ("must decide, with a fixture") while requiring the regression be found and addressed; this session's patch is offered as a verified-working candidate, not a locked decision |

**All three assumptions above carry LOW risk** because each was independently verified against real
tooling this session (a real `typst.compile()`, a real `sphinx-build`, and a real patch-and-rebuild
of the project's own existing fixture) rather than being carried over from training-data recall.

## Open Questions

1. **Does the D-07 single-paragraph-unwrap mechanism need to also handle a field body whose one
   paragraph itself contains a nested block element (e.g. a paragraph that somehow wraps a literal
   block)?**
   - What we know: `docfields.py`'s `Field.make_field`/`GroupedField.make_field` (the autodoc path)
     always produces a genuinely flat `paragraph` containing only inline children for the single-value
     case — verified by reading the source. A user-authored plain rST field list (not autodoc-driven)
     could theoretically contain other node shapes.
   - What's unclear: whether any real-world field list (inside the project's own docs, or the Sphinx
     `doc/` corpus the slow gate drives) ever produces a single-paragraph field body containing
     something other than pure inline content.
   - Recommendation: the `isinstance` check in Pattern 3 (`len(children) == 1 and isinstance(children[0], nodes.paragraph)`)
     is safe regardless — if the one paragraph child itself contains block content, `visit_paragraph`'s
     children still dispatch normally; the risk is only aesthetic (an inline join that reads oddly),
     not a compile failure. No corpus fixture is known to exercise this edge; flag as a residual, low-
     priority item for the corpus gate to catch if it exists.

2. **Should the D-13 stray `parbreak()` (Pitfall 4) be fixed in this phase or explicitly left?**
   - What we know: it is cosmetic, pre-existing, inside a handler this phase's own field-body work
     necessarily touches (`visit_field_body`'s multi-value path), and CONTEXT.md D-13 marks it as
     Claude's discretion.
   - What's unclear: whether fixing it changes any currently-pinned exact-string test (a repo-wide
     grep for `parbreak()` near `list(` call sites in existing golden files would answer this before
     deciding).
   - Recommendation: decide during planning, not research — grep existing goldens for the exact
     `list({\nparbreak()` shape first; if any existing pinned test relies on it being present, leaving
     it is the lower-risk default.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst-py` | Compiling every GATE-01 fixture in this phase | ✓ | 0.15.0 | — |
| `pypdf` | Layout-mode text extraction for SC#1/SC#2 gates | ✓ | 6.14.2 | — |
| `sphinx` | Building fixtures via `-b typst`/`-b typstpdf` | ✓ | 9.1.0 | — |
| `pdftotext` (poppler) | Cross-checking font roles against the reference — not needed this phase (no new font role introduced) | ✗ | — | Not required; `pypdf` + Typst's own `measure()`/`layout()` already fully substitute, per Phase 37's own finding, re-confirmed unnecessary here since Phase 38 introduces no new font/weight combination beyond what Phase 37 already verified |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** `pdftotext` — not installed in this sandbox; not needed for
this phase's own scope (no new SIG-family font-role work).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), plus the project's own GATE-01 real-`typst.compile()` render-gate pattern |
| Config file | `pyproject.toml`; no separate render-gate config, plain pytest fixtures calling `sys.executable -m sphinx` + `typst.compile()`/`pypdf` |
| Quick run command | `uv run pytest tests/test_translator.py -k "desc or field" -x` |
| Full suite command | `uv run pytest -m "not slow"` |
| Estimated runtime | quick ~5s · full suite ~45s (measured at Phase 37 close: 43.24s) · `-m slow` full-corpus gate several minutes |

**Environment constraint (unchanged from Phase 37, still binding):** new fixtures MUST use the
`sys.executable -m sphinx` subprocess pattern, never `subprocess.run(["uv", "run", "sphinx-build", ...])`.
Executors in isolated worktrees must provision with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` before any test run (per
`CLAUDE.md` § Worktree-isolated execution, the standing execution mode for this project).

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| IND-01 | `desc_content` body left edge > its own `desc_signature`'s | render-gate (compiled PDF, `pypdf` layout-mode) | new fixture + `tests/test_desc_content_indent_render_gate.py` (name TBD by planner) | ❌ Wave 0 |
| IND-02 | Nested member's body indented one further step than parent's body | render-gate, same fixture | same file | ❌ Wave 0 |
| IND-03 | Nested member's own signature aligns with parent body, no extra step | render-gate, same fixture | same file | ❌ Wave 0 |
| IND-04 | One shared constant drives desc/field-list indent | structural (grep) | `grep -rn "em\b" typsphinx/translator.py` filtered to indent-context sites, or a `.typ`-output substring check that both sites emit `SHARED_INDENT_STEP`'s literal value | ❌ Wave 0 |
| IND-05 | Depth resets across sibling `desc` (no leak) | render-gate, same 3-level fixture plus a top-level sibling after the nest | same file | ❌ Wave 0 |
| FLD-01 | `field_list` indented one step beyond surrounding body | render-gate | same fixture family | ❌ Wave 0 |
| FLD-02 | Multi-value → bulleted list (non-regression); single-value → inline | unit (`.typ` structural) + render-gate (PDF text adjacency, mirroring `test_confval_field_spacing_render_gate.py`'s `PINNED_SC3_STRING` pattern) | extends/new file | ⚠️ partial — multi-value already covered indirectly, single-value needs Wave 0 |
| FLD-03 | Param name bold-mono, type italic-mono, distinct from proportional-bold label — asserted **per sub-part** (D-06) | unit (`.typ` structural, parametrized) | new parametrized test mirroring `tests/test_signature_typography_gate.py`'s `test_sig04_*` family shape | ❌ Wave 0 |
| D-10 (no FLD/IND id) | SIG-08 marker propagation survives IND-01's wrapper | unit (`.typ` `parbreak()` count) | extends `tests/test_signature_break_and_arrow_gate.py` (already has the exact fixture shape needed — `SigBreakOuterClassOne`/`Two`) | ✅ fixture exists, new assertion needed |

**GATE-01 RED requirement (milestone invariant #4):** every assertion above must be recorded RED
against the pre-phase translator. Because `visit_desc_content`/`depart_desc_content` are currently
`pass` and the field-body defects currently compile fine, RED must come from a structural assertion
(indent presence / monospace primitive / inline-adjacency), never a compile failure — same
methodology as Phase 37.

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_translator.py -k "desc or field" -x`
- **Per wave merge:** `uv run pytest -m "not slow"`
- **Phase gate:** `uv run pytest -m "not slow"` green, plus an explicit
  `uv run pytest tests/test_corpus_gate.py -m slow` full-corpus run before `/gsd-verify-work`
  (milestone standing practice, unchanged from Phase 37)

### Wave 0 Gaps

- [ ] A new render-gate fixture exercising the full IND-01..05 nesting shape in one build (class →
      nested method → nested method's own field list → sibling top-level function) — the single most
      valuable new fixture this phase needs; mirrors `tests/fixtures/signature_break_and_arrow_gate`'s
      "one fixture, many `class Test*RenderGate` cases" convention
- [ ] A parametrized FLD-03 unit test asserting bold-mono name / italic-mono type / plain-bold label
      **per sub-part**, per D-06's binding instruction (never one blanket check over the field body)
- [ ] An assertion extending `tests/test_signature_break_and_arrow_gate.py`'s existing
      `SigBreakOuterClassOne`/`Two` cases to cover the post-IND-01 `parbreak()` count (Pitfall 1) —
      no new fixture file needed, the fixture already exists and already contains both the defect
      shape and its non-regression control
- [ ] A resolvable-`:type:`-cross-reference fixture (Pitfall 2) — not present in any existing fixture
      this session found; needed to prove `literal_emphasis` composes correctly inside `link()`

*Framework install: not required — pytest, `typst-py` 0.15.0 and `pypdf` 6.14.2 are all present.*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — build-time tool, no runtime auth surface |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes | `escape_typst_string` (`typsphinx/translator.py:32`) — the sole escaping helper. This phase's two new leaf-emission sites (`literal_strong`, `literal_emphasis`) MUST route through it directly, exactly like `visit_literal`'s existing leaf branch, and must NOT introduce a second escaping helper or reuse `_escape_signature_text` (which layers an unrelated ZWSP injection on top, per Pitfall 4 above) |
| V6 Cryptography | no | N/A — no cryptographic operation anywhere in this pipeline |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Typst string-literal injection via unescaped field-body text (parameter names/types echoed from docstrings, which are author-controlled but still pass through the same escaping boundary as every other text node) | Tampering | Route every new user-text emission site through `escape_typst_string` (never a second helper); mirrors Phase 37's T-37-01, closed the same way |
| A structurally-required break silently suppressed, merging two `desc` blocks (or a field-list block and its following content) into one visually-unseparated run | Denial of service (rendering-correctness class, mirrors Phase 37's T-37-05) | The `depart_desc_content` marker-propagation fix in Pitfall 1, verified this session; must ship with the two named fixture cases (`SigBreakOuterClassOne`/`Two`) both asserted green |
| A new runtime dependency or `@preview` package slipping in via this phase's own work | Tampering (supply chain) | Not applicable — no import statement is added anywhere by this phase (Package Legitimacy Audit § above); verify at phase close with the same `git diff -- pyproject.toml` / `find typsphinx -name "*.typ"` check Phase 37's T-37-10 used |

## Sources

### Primary (HIGH confidence)

- This session's own `typst.compile()` probes (3 independent compiles: two-line indent probe,
  3-level nesting probe, SIG-08 marker-propagation before/after/fixed probes on
  `tests/fixtures/signature_break_and_arrow_gate`) — every code example and every "verified this
  session" claim above traces to one of these.
- This session's own `sphinx-build -b typst` runs against hand-written fixtures (a `py:class`/
  `py:method`/`py:attribute`/field-list probe, and a resolvable `:type:` cross-reference probe) —
  independently reproduces every byte-level claim CONTEXT.md's D-01/D-02/D-05/D-07/D-08 make, with no
  disagreement found.
- `typsphinx/translator.py` (read directly, current tree: lines 1-45, 200-600, 800-1237, 1238-1600,
  4740-4880, 5080-5480, 5700-5768, 2900-2985) — every existing pattern cited above (`add_text`,
  `_emit_forced_break`, `_add_paragraph_separator`, the concat-context machinery, `visit_literal`,
  `visit_paragraph`'s list-item fast-path, `visit_block_quote`) is quoted from direct reads, not
  recall.
- `sphinx/util/docfields.py` (`.venv/lib/python3.13/site-packages/sphinx/util/docfields.py`, read
  directly, lines 78-260) — the exact `Field.make_field`/`GroupedField.make_field`/`make_xref` logic
  that determines field-body node shape.

### Secondary (MEDIUM confidence)

- [https://typst.app/docs/reference/layout/pad](https://typst.app/docs/reference/layout/pad) —
  official Typst `pad()` reference ("Adds spacing around content"), cross-checked against this
  session's own compiled probes (not taken on faith alone).
- `.planning/phases/37-signature-typography-the-desc-family/37-EMISSION-CONTRACT.md`,
  `37-TEST-CENSUS.md`, `37-VALIDATION.md`, `37-SECURITY.md` — the immediate-prior phase's own
  measured artifacts, treated as MEDIUM (project-internal, owner-approved, but not independently
  re-verified byte-for-byte in this session except where explicitly noted "re-confirmed").

### Tertiary (LOW confidence)

- None — every claim in this document traces to either a direct source read this session or a real
  compile/build this session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new package; `pad()`'s behaviour independently verified against the real
  compiler three separate times this session.
- Architecture: HIGH — every composition claim (nesting, marker propagation, single-paragraph
  unwrap) was verified with a working, compiled/built artifact this session, not inferred from
  reading code alone.
- Pitfalls: HIGH — Pitfall 1 (SIG-08 marker) was reproduced as an actual regression AND fixed with a
  verified working patch on the project's own real fixture; Pitfall 2 (cross-reference nesting) was
  reproduced with a real resolvable-type build; Pitfall 3 (pypdf position API) re-confirms Phase 37's
  finding; Pitfall 4 (D-13) is a direct code read, cross-checked against CONTEXT.md's own measurement.

**Research date:** 2026-08-01
**Valid until:** 30 days (stable domain — Typst stdlib and docutils' `docfields.py` are not
fast-moving; the pinned `typst-py`/`pypdf`/`sphinx` versions are the same ones Phase 37 already
locked in)
