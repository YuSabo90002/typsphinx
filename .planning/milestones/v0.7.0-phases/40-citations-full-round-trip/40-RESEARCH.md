# Phase 40: Citations — Full Round Trip - Research

**Researched:** 2026-08-02
**Domain:** docutils `citation`/`label`/`citation_reference` handling in a Sphinx→Typst translator (single-pass, unified code-mode emission)
**Confidence:** HIGH — every claim below was either (a) copied verbatim from `40-CONTEXT.md`'s own same-day measurements, or (b) independently reproduced this session via a real `sphinx-build`, a real `typst.compile()`, or a repo-wide `grep`. No claim in this document is `[ASSUMED]`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Every value below was measured **this session (2026-08-02)** against Sphinx 9.1.0, typst-py 0.15.0
and pypdf. Full text lives in `40-CONTEXT.md`; the load-bearing lines are reproduced here so this
document is self-contained for the planner.

**The measured starting position:**
- `citation_reference` never reaches the translator under Sphinx — it is rewritten to a `pending_xref`
  and resolved to a plain `nodes.reference` (`refid=` same-doc, `refuri=` cross-doc) before the
  translator ever sees it. **The citing side already works** — `visit_reference` already emits
  `link(<index:krizhevsky2012>, text("[Krizhevsky2012]"))` for both cases via its existing refid/xref
  branches. CIT-03 is discharged as soon as the definition anchors the matching label.
- The defect is entirely on the definition side: `text("Krizhevsky2012")par({text("Krizhevsky, A.
  …")})`, which fails `typst.compile()` with verbatim `TypstError: expected semicolon or line break`
  (SC#1's classic RED).
- `citation` carries a Sphinx-added `docname` attribute; a duplicate key defined in two documents
  keeps **both** definitions (Sphinx warns, doesn't drop), each with its own document's `ids`.
- `backrefs` are same-document only (docutils itself never populates cross-document backrefs).
- Sphinx's HTML and LaTeX builders disagree on back-references (HTML renders them, LaTeX does not) —
  D-01 rules for HTML.

**D-01:** typsphinx follows Sphinx's HTML convention — back-references ARE rendered. `link()` +
`<label>` is sufficient; `bibliography()` is not involved.
**D-02:** the back-reference marker sits immediately after the label, in the same left column, in
HTML's order.
**D-03:** an entry with exactly one citing site emits no `(1)` — the label text itself becomes the
back-link. Two-or-more emits a plain (non-linked) label plus `(1,2)` (bare comma, no space).
**D-04:** the grid (D-05) governs the layout the marker lives in.
**D-05:** a run of consecutive `citation` siblings is emitted as ONE `grid(columns: (auto, 1fr))`,
not one grid per entry.
**D-06:** a non-citation node between two citations breaks the run; the next run realigns
independently.
**D-07:** an uncited citation definition still renders, with a plain (non-linked) label. **This is
the opposite of the footnote precedent** (Phase 14 D-09 silently drops unreferenced footnotes).
**D-08:** the back-reference guarantee is same-document only (matches docutils' own `backrefs` and
Sphinx HTML).
**D-09:** ROADMAP SC#3's "every citing location" wording is corrected to same-document scope, per
D-08 (see Roadmap Evolution handling below).
**D-10:** the 2+ document fixture stays, purpose changed: proves (a) a cross-document citing site's
forward link resolves, (b) a key defined in two documents separates into `index:same2020` /
`second:same2020` without a duplicate-label fatal.
**D-11:** `examples/charged-ieee/` is restored **verbatim**, not expanded — one entry, one citing
site; `(1,2)` and D-05's widest-label alignment are NOT visible there and must be proven by the
phase's own fixtures.
**D-12:** the two samples go back to being byte-identical (they differ today only in a top-of-file
RST comment).
**D-13:** every label this phase emits goes through `_namespace_label`/`_sanitize_label`
(`typsphinx/translator.py:3576, 3519`), namespaced by the **citation's own** `docname` — never
`_current_docname()`.
**D-14:** adding an anchor at the citing site must not change the emitted bytes of any reference that
is not a citation target — the planner must **prove** non-regression (full-corpus gate), not assume
it from the `ids` heuristic alone.

### Claude's Discretion
- The grid's `column-gutter`/`row-gutter` values and any extra inter-entry vertical separation.
- Run-detection implementation shape for D-05 (sibling look-ahead in `visit_citation` vs. a doctree
  pre-pass index like the footnote one) — provided the grid opens once per run, closes once.
- The mechanism for the D-14 citing-site anchor (bracket-wrap in `visit_reference` vs. a
  backrefs-driven index consulted there), subject to D-14's non-regression constraint.
- Whether `visit_label` is a real handler or the `label` child is skipped positionally (like
  `visit_footnote_reference` skips `footnote_node.children[1:]`).
- Which document/exact `pypdf` extraction the SC#4 document-order assertion is taken from.

### Deferred Ideas (OUT OF SCOPE)
- Cross-document back-references (rejected as D-08 — would require a typsphinx-owned env-wide
  pre-pass neither Sphinx builder provides).
- Expanding `examples/charged-ieee/` into a multi-entry reference list (rejected as D-11 — the
  restore must read as "restore what was broken", not a new demo).
- CIT-07 (`sphinxcontrib-bibtex`, `.bib` files, Typst's native `bibliography()`/`cite()`) — a
  different node family entirely, future requirement.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CIT-01 | A document containing a citation **compiles** (classic `TypstError` RED, the milestone's sole exception) | §"GATE-01 RED capture" below; independently reproduced this session (verbatim exception text quoted) |
| CIT-02 | A citation definition renders as `[Label]` + hanging-indent body, continuation aligned past the label | §"Emission shapes" D-05/D-02/D-03/D-07 probes, real `typst.compile()` + `pypdf` `extraction_mode="layout"` readback |
| CIT-03 | An in-text `[Label]` reference **links to its definition** | Already discharged by the existing `visit_reference` (verified via real build); D-14's own-`ids` anchor is the only new work on this side |
| CIT-04 | A definition carries back-references to every (same-document) citing location | §"Emission shapes" D-01/D-02/D-03 grid+link probe, `/Annots` + `visitor_text` `cm[4]`/`cm[5]` readback |
| CIT-05 | `examples/charged-ieee/` citation syntax restored, both approaches build clean | §"Sample restoration" — exact restoration diffs pulled from commits `8bed1a3`/`c014a0b` |
| CIT-06 | Citation entries render in document order, unsorted | §"Run detection" — the grid is filled row-by-row in doctree traversal order; no sort step anywhere in the design |
</phase_requirements>

## Summary

The phase is smaller than it looks: **the citing side (CIT-03) is already correct and needs no new
code** — Sphinx's citation domain rewrites every `[Label]_` into a resolved `nodes.reference` before
the translator ever sees a `citation_reference`, and `visit_reference`'s existing refid/xref branches
already emit the right `link(...)` call for both same-document and cross-document citing sites. The
entire defect and the entire new-code surface live on the **definition side**: two new handlers
(`visit_citation`/`depart_citation`, and either a real `visit_label` or a positional skip) that must
(a) group a run of sibling `citation` nodes into one `grid(columns: (auto, 1fr))` per D-05, (b) emit
each row's left-column label in one of two shapes depending on `len(node["backrefs"])` (D-03), (c)
attach the row's own definition anchor and, for the 1-backref case, make the label itself the
back-link, and (d) leave an uncited entry's label as plain, unlinked text (D-07 — the deliberate
inverse of the footnote precedent). A third, much smaller change touches `visit_reference`
(`typsphinx/translator.py:3820`): guard-add a bracket-wrapped `<label>` attachment when the reference's
own `ids` is non-empty, so the back-reference side of the round trip has a target — verified this
session, on the real corpus, that ordinary (non-citation) references carry `ids=[]` while every
citation-derived reference carries a populated `ids` list.

Every emission shape below was verified this session with an actual `.typ` probe compiled through
`typst.compile()` and read back through `pypdf` — the grid, the two label shapes, the uncited entry,
and the six resulting `/Link` annotations all behave exactly as `40-CONTEXT.md` describes. The correct
structural precedent for the new block-level handler pair is **`_visit_admonition`/`_depart_admonition`**
(`typsphinx/translator.py:4343, 4394`), not the footnote handlers — footnotes never emit their
definition in place (SkipNode fires immediately, the body renders lazily at the first reference),
whereas a citation definition renders in its own natural doctree position, exactly like an admonition
does. This document also independently reproduces the classic `TypstError` (verbatim, via a fresh
two-document Sphinx probe) and identifies one previously unmeasured wrinkle: nesting a citation inside
a **list item** fails today with a *different* error (`label ... does not exist in the document`, a
semantic-pass fatal) rather than the classic syntax fatal — the planner should treat "citation at top
level" and "citation inside a list item" as two independently-verified fixtures, not one.

**Primary recommendation:** Model `visit_citation`/`depart_citation` on `_visit_admonition`/
`_depart_admonition`'s open/close shape (propagated-target anchor first, then the list-item leading
separator, then the block-opening call; on depart, close the call and set
`list_item_needs_separator`), but replace the single-node open/close with a **run-scoped** open/close
(open the `grid(...)` on the first citation of a run, emit one row per citation, close on the last
citation of the run) using a sibling-lookahead check for "is my next sibling also a `citation`" — no
new pre-pass index is required, unlike D-05's rejected-as-unnecessary footnote-index analogy, because
citation definitions are read in natural document order and never need the footnote-style
"referenced-before-defined" pre-pass docutils' own doctree ordering already handles the CIT-06
in-order requirement for free.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Citation definition rendering (grid, labels, hanging indent) | Translator (`typsphinx/translator.py`, new `visit_citation`/`depart_citation`/`visit_label`) | Typst output (`grid()`/`link()`/`<label>`) | All layout logic is emitted Typst source; no template/config surface is touched (locked out of `bibliography()`) |
| Citing-site anchoring (D-14) | Translator (`visit_reference`, existing) | — | `visit_reference` is the sole emission site for every reference/link in the corpus; the anchor guard is a small addition there, not a new node handler |
| Cross-document label namespacing (D-13) | Translator (`_namespace_label`/`_sanitize_label`, existing, reused unchanged) | — | Already the single derivation point for every anchor/link in the codebase; no new helper needed |
| Sample restoration (CIT-05) | Sphinx source (`examples/charged-ieee/*/source/index.rst`) | Test suite (`tests/test_examples_charged_ieee_gate.py`, existing, unchanged) | Pure content restoration; the existing end-to-end gate already builds these samples and asserts zero warnings, which doubles as the regression check once citations return |
| GATE-01 RED evidence | Test suite (new fixture + evidence file) | — | Standing project convention (Phase 36-39 pattern), the milestone's sole classic-`TypstError` exception |

## Standard Stack

No new library is introduced. This phase's entire "stack" is the two already-installed pieces this
project always uses for its render gates:

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `typst-py` | 0.15.0 (already pinned, `pyproject.toml`) | Real-compile GATE-01 verification (`typst.compile()`) | Same tool every other GATE-01 fixture in this repo uses; verified importable this session (`/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/typst/__init__.py`) |
| `pypdf` | already a dev dependency | Compiled-PDF structural assertions (hanging indent via `extraction_mode="layout"`, link geometry via `/Annots` and `visitor_text`'s `cm[4]`/`cm[5]`) | Same tool every `*_render_gate.py` in this repo uses |

**Installation:** none — both dependencies are already present; `uv sync --extra dev` (already run this
session) resolves them.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `grid(columns: (auto, 1fr))` per-run (D-05) | Typst `par(hanging-indent: ...)` with a fixed length | Rejected in CONTEXT.md D-05: measured that `2.5em`/`4em` both fail to clear the widest real label (`[Krizhevsky2012]` measures 84pt) |
| Emitted `link()`+`<label>` round trip (D-01) | Typst's native `bibliography()`/`cite()` | Locked out at v0.7.0 scoping — incompatible with CIT-06's "document order, unsorted" and there is no structured `.bib`/Hayagriva data to feed it (a docutils citation is already-written prose) |

## Package Legitimacy Audit

**Not applicable.** This phase adds no new runtime or dev dependency — `typst-py` and `pypdf` are
already pinned and in use by every other render-gate test in this repository. No `pip`/`npm` install
step exists in this phase's plan.

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (citation domain already ran)
        |
        v
Sphinx citation-domain resolver
  citation_reference -> pending_xref -> nodes.reference (refid= same-doc | refuri= cross-doc)
        |                                          |
        v                                          v
  (never reaches translator)          visit_reference (typsphinx/translator.py:3820)
                                        - EXISTING: emits link(<docname:label>, text("[Label]"))
                                        - NEW (D-14): if node["ids"] non-empty, bracket-wrap the
                                          whole link(...) call and attach <docname:idN> so the
                                          definition's back-reference has a target
        |
        v (doctree also contains, elsewhere, in natural document order)
  nodes.citation (Body element, NOT Inline)
        |
        v
  visit_citation (NEW)                     depart_citation (NEW)
   - is this the FIRST citation of a run?    - is this the LAST citation of a run?
     (previous sibling is not a citation)      (next sibling is not a citation)
   - if yes: emit grid(columns:(auto,1fr){    - if yes: close grid(...)\n\n
       ...else: just continue the open grid  - else: just continue (next row follows)
   - emit this row's two cells:
       [label-cell],  [body-cell],
        |                    |
        v                    v
  label shape (D-03/D-07)   citation's paragraph child(ren)
   - len(backrefs)==0: plain label, no link      renders via the NORMAL visitor chain
   - len(backrefs)==1: label text itself IS      (visit_paragraph etc.), buffer-swapped
     the back-link to the sole citing <idN>       the same way _visit_admonition's body
   - len(backrefs)>=2: plain label + "(1,2)"      does -- NOT node.astext()
     where each number links to its own <idN>
   - every label/anchor routed through
     _namespace_label(node["docname"], ...)
```

### Recommended Project Structure

No new files/modules. Everything lands in the existing single translator:

```
typsphinx/
├── translator.py     # + visit_citation, depart_citation, (+ visit_label OR positional skip)
│                      # + guarded addition inside visit_reference/depart_reference (D-14)
tests/
├── fixtures/
│   └── citation_render_gate/           # NEW fixture (2-doc, forward ref, repeated cite, uncited)
├── test_citation_render_gate.py        # NEW (name suggested) -- GATE-01 RED->GREEN, layout, backrefs, order
examples/charged-ieee/
├── approach1/source/index.rst          # restored (D-11/D-12)
└── approach2/source/index.rst          # restored (D-11/D-12)
```

### Pattern 1: Block-level open/close mirroring `_visit_admonition`/`_depart_admonition`

**What:** The correct structural precedent for `visit_citation`/`depart_citation` is the admonition
helper pair, not the footnote handlers.
**When to use:** Any Body-level (non-Inline) node that must render in place, in document order,
inside whatever container it is found in (top-level body, list item, block quote, ...).
**Example (verified precedent, unmodified — read, not to be copied verbatim, since citation needs a
RUN-scoped variant):**
```python
# Source: typsphinx/translator.py:4343-4426 (existing, verified this session)
def _visit_admonition(self, node, clue_type, custom_title=None):
    self._emit_id_anchors(node)                                    # propagated-target anchor first
    if self.in_list_item and self.list_item_needs_separator:        # list-item leading separator
        self.add_text("\n")
    ...
    self.add_text(f"{clue_type}({{")                                # open the code-mode call

def _depart_admonition(self):
    self.add_text("}")
    ...
    self.add_text(")\n\n")
    if self.in_list_item:
        self.list_item_needs_separator = True                      # trailing separator bookkeeping
```
The citation variant differs only in being **run-scoped**: `visit_citation` must check whether the
previous sibling is also a `citation` (if so, do NOT re-open the grid — just start emitting this
row), and `depart_citation` must check whether the next sibling is also a `citation` (if so, do NOT
close the grid yet).

### Pattern 2: The `[#expr <label>]` bracket-wrap for `<label>` attachment in code mode

**What:** Typst's `<label>` postfix is markup-mode syntax; inside this translator's unified `#{ ... }`
code-mode wrapper it is a parse error as a bare statement. The established fix
(14-RESEARCH.md Verified Mechanism 1, reused at `visit_footnote_reference`/`depart_term`) is to wrap
the whole expression in `[...]` and attach the label to the bracket.
**When to use:** Every DEFINITION site this phase creates (the grid row's own anchor; the D-14 citing
reference's own anchor).
**Example (verified this session, real `typst.compile()`, produces a working `/Link` annotation):**
```typst
// Verified 2026-08-02 via a real typst.compile() probe (see Code Examples below)
[#link(<id1>, [Krizhevsky2012]) <krizhevsky2012>]
```
A `<label>` used as a plain call ARGUMENT (`link(<krizhevsky2012>, ...)`) needs no bracket-wrap — only
the ATTACHMENT postfix does.

### Anti-Patterns to Avoid
- **Treating the footnote handlers as a template for policy (not just mechanism).** `visit_footnote`
  raises `SkipNode` unconditionally — a footnote's definition NEVER renders at its natural position;
  it renders lazily, once, at the first `visit_footnote_reference`. A citation definition renders
  IN PLACE, every time, at its own doctree position (D-01/D-05 assume this). Reusing the footnote
  handlers' `SkipNode`-at-definition shape would silently drop every citation body from the document.
- **Assuming an uncited citation should be dropped (Phase 14 D-09's footnote policy).** D-07 is the
  explicit, deliberate REVERSAL of that footnote precedent for citations.
- **Assuming "code-mode concat" protocol participation is needed for the citation DEFINITION.**
  Verified this session (`docutils.nodes.citation.__mro__` includes `Body`, NOT `Inline`) — a
  citation cannot structurally nest inside any of this translator's `_CONCAT_CONTEXTS`
  (`in_desc_parameter`, `_in_link`, `_in_term`, `_in_field_body`, `_in_attribution` —
  `typsphinx/translator.py:1053-1059`), all of which hold Inline content only. `field_body`'s own
  multi-child branch (`typsphinx/translator.py:5750-5752`) confirms this: a `field_body` whose
  children are NOT all-inline and NOT a single paragraph falls through to the plain block path
  (`_in_field_body = False`), so a citation nested there would render via the ordinary block
  protocol, never the concat one. The "code-mode concat" protocol IS relevant to this phase, but only
  on the CITING side — `visit_reference` (which already interacts with all three protocols) is where
  D-14's new guard must be proven non-regressive.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Label uniqueness across documents | A new per-citation namespacing scheme | `_namespace_label(node["docname"], raw_id)` / `_sanitize_label` (`typsphinx/translator.py:3576, 3519`, unchanged) | D-13 requires it explicitly; it is already the single derivation point every anchor/link in the codebase shares — inventing a second one would break the "definition and reference compute the identical token independently" invariant |
| Detecting whether a reference is a "toctree ref" vs. a "citation-derived ref" | A new node-type check or a citation-specific attribute lookup | `node.get("ids")` — verified this session (real doctree dump) that only citation-derived references carry a non-empty `ids`; toctree/`:ref:` references carry `ids=[]` | Cheapest possible discriminator, already present on the node, no new bookkeeping |
| Document-order preservation (CIT-06) | A sort key or an explicit ordering pass | Nothing — docutils' own doctree traversal order (which the translator already visits depth-first, left-to-right) is document order by construction | Any sort step would be ADDED complexity fighting the grain of the existing single-pass visitor; the requirement is satisfied by doing nothing |

**Key insight:** every piece of "infrastructure" this phase might be tempted to build (a citation
index, a new namespacing scheme, a sort/ordering pass) already exists in the codebase or is
free from the existing traversal order. The actual new work is narrowly two node handlers plus one
small guarded addition to an existing one.

## Runtime State Inventory

Not applicable — this is a greenfield node-handler phase (zero existing handlers for `citation`/
`label`), not a rename/refactor/migration. No stored data, live service config, OS-registered state,
secrets, or build artifacts reference these node types today (`grep -rn "visit_citation\|visit_label"
typsphinx/` returns nothing pre-phase).

## Common Pitfalls

### Pitfall 1: Reasoning about the "three separator protocols" as if the citation DEFINITION must
participate in all three the way `visit_footnote_reference` (an INLINE node) does

**What goes wrong:** SC#5 explicitly instructs the new handlers be "checked explicitly against all
three separator protocols ... rather than by analogy to the footnote handlers." A naive reading might
try to make `visit_citation` interact with `_inline_concat_context()`/`_enter_inline_concat_element()`
the way `visit_footnote_reference` does.
**Why it happens:** `visit_footnote_reference` is the nearest, most recently-touched precedent in the
file, and it DOES interact with all three protocols — but it is an Inline node cited from within a
paragraph, a fundamentally different position in the tree than a Body-level `citation`.
**How to avoid:** Verified this session — `nodes.citation` is `Body`, not `Inline` (`docutils.nodes`
MRO check). It can appear at top level or inside a `list_item`/`block_quote` (both hold Body
children), but NOT inside any of the five code-mode concat contexts (all Inline-only). The
DEFINITION-side handler only needs the **paragraph-context leading/trailing hygiene** (mirrored from
`_visit_admonition`) and the **list-item protocol** (`in_list_item`/`list_item_needs_separator`). The
**code-mode concat protocol only matters on the CITING side**, which is already handled by the
existing, unmodified `visit_reference`.
**Warning signs:** A `visit_citation` implementation that checks `self._in_link`/`self._in_term`/etc.
is over-engineered — it can never fire (citation cannot be a child there), but is harmless if present;
flag it in review as dead code rather than a real defect.

### Pitfall 2: Assuming a citation's failure mode is identical wherever it is nested

**What goes wrong:** Assuming the "does not compile" GATE-01 RED (SC#1's classic `TypstError: expected
semicolon or line break`) is the ONLY failure shape a pre-phase citation can produce, and building
only one fixture for it.
**Why it happens:** The top-level (section-body) case IS a pure syntax fatal — verified this session,
reproduced with a real 2-document Sphinx probe (see GATE-01 RED capture below).
**How to avoid:** Verified this session that nesting a citation inside a `list_item` produces a
**different**, semantic-pass fatal instead: `label \`<index:nested2021>\` does not exist in the
document` (a real `typst.compile()` run against the pre-phase translator's own list-item output). This
happens because the label's bare `Text` child renders through `visit_Text` with no separator logic of
its own, and only "accidentally" avoids the syntax fatal because the PRECEDING sibling paragraph left
`list_item_needs_separator=True` dangling — the citation's own definition anchor is never emitted
(no handler exists), so the citing reference's `link(<...>)` call resolves to nothing. The planner
should build (or at minimum reason about) the list-item-nested case as its own, separately-verified
scenario, not assume the top-level RED fixture also covers it.
**Warning signs:** A fixture or GATE-01 evidence file that only ever exercises "citation immediately
under a section" — this misses SC#5's own three-separator-protocol testing mandate for the reference
side and under-covers the list-item nesting case for the definition side.

### Pitfall 3: Duplicate-key resolution does not always keep a same-document citing reference pointed
at the same-document definition

**What goes wrong:** Assuming (per D-10's "index:same2020 / second:same2020" framing) that a citing
reference INSIDE `index.rst` to a duplicate-defined `Same2020` will always resolve to `index.rst`'s
own definition.
**Why it happens:** Sphinx's citation domain registers citations by KEY across the whole build; on a
duplicate key, the LATER registration (in doctree-traversal/build order, not necessarily the same
document as any given reference) wins as the domain's authoritative target for ALL references to that
key, regardless of which document made the reference.
**How to avoid:** Verified this session with a real 2-document probe: a `[Same2020]_` reference
physically located in `index.rst`, with `Same2020` ALSO (re-)defined later in `second.rst`, resolved
to `link(<second:same2020>, ...)` — a CROSS-document link — not `<index:same2020>`. This is not a bug;
`visit_reference`'s existing xref-resolution machinery already handles it correctly, because Sphinx's
resolver (not the translator) decides the target BEFORE the translator runs. The planner's D-10
fixture should not assert "same-document reference always produces a same-document link" — it should
assert whatever Sphinx's resolver actually decided, and should keep the DEFINITION-side namespacing
(`index:same2020` / `second:same2020`, both correctly non-colliding) as the property under test, not
the reference-resolution direction.
**Warning signs:** A fixture assertion hard-coding "the index.rst citing site links to
`<index:same2020>`" — this will fail not because of a translator defect, but because it encodes an
incorrect assumption about Sphinx's own duplicate-key resolution order.

## Code Examples

### D-05/D-02/D-03/D-07: the grid, both label shapes, and the uncited entry — verified via a real
`typst.compile()` + `pypdf` readback this session

```typst
// Source: hand-written probe, compiled successfully this session
// (typst-py 0.15.0, /home/yuta/Documents/typsphinx/.venv)
#{
  [Text before citing site #link(<krizhevsky2012>, [Krizhevsky2012])<id1> continues here.]
  parbreak()
  [Second citing site (Multi2020) #link(<multi2020>, [Multi2020])<id3> and again #link(<multi2020>, [Multi2020])<id4> in the same paragraph.]
  parbreak()
  grid(
    columns: (auto, 1fr),
    column-gutter: 0.5em,
    row-gutter: 0.8em,
    // D-03, exactly-one-backref shape: the label text ITSELF is the back-link.
    [#link(<id1>, [Krizhevsky2012]) <krizhevsky2012>], [Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). ImageNet classification with deep convolutional neural networks. Advances in neural information processing systems, 25.],
    // D-03, 2+-backrefs shape: plain (non-linked) label + "(1,2)" marker, bare comma.
    [[Multi2020] (#link(<id3>, [1]),#link(<id4>, [2])) <multi2020>], [Body of multi-backref entry, with a continuation line that is long enough to wrap onto a second visual line so hanging-indent alignment can be checked precisely across more than one line of body text here.],
    // D-07: uncited entry -- plain, non-linked label, still renders.
    [Never1999], [Uncited entry body text goes here, no back-reference exists for this one.],
  )
}
```

Compiled clean (`typst.compile()` exit with no exception). `pypdf` readback confirmed:

- `extraction_mode="layout"` reconstructs the hanging indent exactly as HTML/D-05 describe — every
  row's body starts at the SAME column, past the widest label:
  ```
  Krizhevsky2012        Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). ImageNet classification with
                        deep convolutional neural networks. Advances in neural information processing
                        systems, 25.
  [Multi2020] (1,2)     Body of multi-backref entry, with a continuation line that is long enough to wrap
                        onto a second visual line so hanging-indent alignment can be checked precisely
                        across more than one line of body text here.
  Never1999             Uncited entry body text goes here, no back-reference exists for this one.
  ```
- `page.get('/Annots')` produced **exactly 6** `/Link` annotations (2 forward citing-site links for
  the single-backref row + 1 forward citing-site link... — precisely matching CONTEXT.md's own
  4-annotation smaller probe scaled up by the extra Multi2020 citing site): every forward link (citing
  site -> definition) and every backward link (definition's own back-reference marker -> citing site)
  resolved to a real `/Rect` bounding box, e.g. `[171.04314, 760.21063, 242.05914, 774.59863]` for the
  first citing site.
- `visitor_text`'s `cm[4]`/`cm[5]` (NOT `tm[4]`/`tm[5]`, which reported `0.0` on every glyph in this
  probe) gave real, usable per-glyph x/y positions matching the `/Annots` rectangles almost exactly
  (e.g. `cm4=171.04314` for the "Krizhevsky2012" glyph run at the first citing site). This CONFIRMS
  `40-CONTEXT.md`'s own "`cm[4]+tm[4]`" measurement technique is correct for THIS construct — it does
  not contradict `38-RESEARCH.md` Pattern 2's finding that `visitor_text` is unusable for
  `desc_content`/`field_list` left-edge measurement; that finding was specifically about `tm[4]`/`tm[5]`
  (both `0.0` there too), not about `cm[4]`/`cm[5]` being universally broken.

### Independently reproduced GATE-01 classic RED (verbatim, this session)

```
$ sphinx-build -b typstpdf <src-with-citations> <build>
...
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: expected semicolon or line break
    Location: <build>/index.typ
    Details: expected semicolon or line break
```
(Reproduced against a fresh 2-document probe with a forward reference, a repeated citation, and a
cross-document duplicate key — same message `40-CONTEXT.md` recorded, confirmed independently.)

### Real doctree evidence for D-14 (this session, `env.get_and_resolve_doctree`)

```
reference ids= []      refid= sec2            refuri= None                text= Section Two          # :ref: to a section
reference ids= ['id1']  refid= krizhevsky2012  refuri= None                text= [Krizhevsky2012]     # same-doc citing site
reference ids= ['id2']  refid= krizhevsky2012  refuri= None                text= [Krizhevsky2012]     # same-doc citing site (repeat)
reference ids= ['id3']  refid= None            refuri= second.typ#same2020 text= [Same2020]           # cross-doc citing site
reference ids= []      refid= None            refuri= second.typ          text= Second Document       # toctree-generated ref
```
Every citation-derived reference in this probe carries a populated `ids`; every other reference
(a `:ref:` and the auto-generated toctree entry link) carries `ids=[]`. This directly corroborates
D-14's premise on a fresh, independently-built probe.

### Current pre-phase failure inside a list item (previously unmeasured — see Pitfall 2)

```
$ sphinx-build -b typst <src-with-list-item-citation> <build>   # exit 0 (translate only)
$ typst.compile('<build>/index.typ')
typst.TypstError: label `<index:nested2021>` does not exist in the document
```
Raw emitted fragment (`<build>/index.typ`), showing the accidental (not designed) newline that
prevents the SYNTAX fatal here, unlike the top-level case:
```typst
list({
parbreak()
text("Item one, a plain paragraph.")
}, {
parbreak()
text("Item two contains a citation list:")
text("Nested2021")
parbreak()
text("A citation nested inside a list item's body.")
parbreak()
text("Referenced here ")
link(<index:nested2021>, text("[Nested2021]"))
text(" within the same item.")
})
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No citation handler at all (`unknown_visit`/`unknown_departure` fallback) | Real `visit_citation`/`depart_citation`/`visit_label` handlers | This phase (v0.7.0 Phase 40) | `-b typstpdf` stops aborting; `-b typst` stops silently writing invalid `.typ` |
| `examples/charged-ieee/` with citation syntax stripped (Phase 22.2, commits `8bed1a3`/`c014a0b`) | Citation syntax restored verbatim (D-11/D-12) | This phase | Both samples exercise a real reference list again |

**Deprecated/outdated:** none — this is greenfield handler addition, not a replacement of an existing
mechanism.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | (none) | — | Every claim in this document was either copied verbatim from `40-CONTEXT.md`'s own same-day measurements or independently reproduced this session via a real command (quoted above). No new `[ASSUMED]` claim is introduced. |

**This table is empty** — no user confirmation is needed beyond what `40-CONTEXT.md` already settled.

## Open Questions

1. **Exactly which sibling-adjacency check should `visit_citation`/`depart_citation` use for D-05's
   run detection — `node.parent.index(node)` +/- 1, or a cached "next citation" pointer?**
   - What we know: `visit_reference`'s existing `next_is_target` check (`typsphinx/translator.py:3892-3898`)
     is the established idiom in this file for "is my sibling also an X" — `node.parent.index(node)`
     then bounds-check `+1`/`-1` into `node.parent.children`.
   - What's unclear: whether a `citation` can ever have a non-`citation`, non-whitespace sibling
     INSERTED transparently by a Sphinx transform between two source-adjacent citations (would break
     the "one grid per run" assumption in a way invisible at the RST source level).
   - Recommendation: mirror the `next_is_target` idiom exactly (cheap, already proven, no new state);
     verify with a fixture containing an explicit non-citation node between two `.. [X]` blocks (D-06
     already calls this out as the expected/correct behavior, not a bug).

2. **Should `depart_citation` re-derive "is this the last citation of the run" from
   `node.parent.index(node)+1`, or should `visit_citation` push a flag consumed by `depart_citation`?**
   - What we know: both are equally cheap; the codebase has precedent for both styles
     (`_field_body_stack`-style push/pop vs. `node.parent.next_node(...)`-style re-derivation at
     `depart_field_body`, `typsphinx/translator.py:5799-5801`).
   - What's unclear: which reads more clearly given the grid must also track "is this the FIRST row of
     an already-open grid" to decide whether to emit a leading `,` between rows.
   - Recommendation: left to Claude's Discretion per `40-CONTEXT.md`; either is structurally sound.

## Environment Availability

Skipped — this phase has no external tool/service dependency beyond `typst-py`/`pypdf`, both already
verified present and importable (`Standard Stack` above).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ (project pin, `pyproject.toml` `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`, markers `slow`/`integration`, `filterwarnings = ["error::DeprecationWarning", "error::PendingDeprecationWarning"]`) |
| Quick run command | `uv run pytest tests/test_citation_render_gate.py -x` (new module, suggested name; no `slow` marker needed for the translate+compile-only assertions) |
| Full suite command | `uv run pytest -m "not slow"` (fast tier); `uv run pytest tests/test_corpus_gate.py -m slow` (the milestone's SC#5 full-corpus gate, network-dependent, skips gracefully offline) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CIT-01 | Real `-b typstpdf` compile succeeds (classic RED->GREEN) | real-compile gate | `uv run pytest tests/test_citation_render_gate.py -k compile -x` | ❌ Wave 0 — new fixture + new module, GATE-EVIDENCE file recording the verbatim pre-fix `TypstError` |
| CIT-02 | Hanging indent, label-then-body, continuation aligned past label | compiled-PDF `pypdf` structural (`extraction_mode="layout"`) | `uv run pytest tests/test_citation_render_gate.py -k layout -x` | ❌ Wave 0 — same fixture, new assertions |
| CIT-03 | In-text `[Label]` resolves to definition | compiled-PDF `/Annots` + `.typ`-string assert | `uv run pytest tests/test_citation_render_gate.py -k link -x` | Partial — `visit_reference`'s existing behavior is unit-tested elsewhere (`test_cross_doc_label_namespace_render_gate.py`); the NEW D-14 anchor half needs a new assertion |
| CIT-04 | Back-references to every same-document citing location | compiled-PDF `/Annots` + `visitor_text` `cm[4]`/`cm[5]` | `uv run pytest tests/test_citation_render_gate.py -k backref -x` | ❌ Wave 0 — new fixture must include 2+ citations of the same key |
| CIT-05 | `examples/charged-ieee/` restored, builds clean | existing end-to-end example gate | `uv run pytest tests/test_examples_charged_ieee_gate.py -x` | ✅ exists — re-run after restoring the `.rst` files; its own `_assert_no_warnings` doubles as the regression check |
| CIT-06 | Document order, unsorted | compiled-PDF extracted-text order assert | `uv run pytest tests/test_citation_render_gate.py -k order -x` | ❌ Wave 0 — same fixture, new assertion comparing extracted-text index of each label |
| D-14 (folded, non-regression) | Adding the citing-site anchor changes no other reference's bytes | full-corpus regression | `uv run pytest tests/test_corpus_gate.py -m slow` | ✅ exists — re-run as the phase's final gate |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_citation_render_gate.py -x` (fast tier target; keep
  no `slow` marker on the translate+single-doc-compile assertions so this stays sub-5s)
- **Per wave merge:** `uv run pytest -m "not slow"` plus `uv run pytest tests/test_examples_charged_ieee_gate.py -x`
- **Phase gate:** full suite green (`uv run pytest`) before `/gsd-verify-work`; the full-corpus
  `-b typstpdf` gate (`tests/test_corpus_gate.py -m slow`) re-run green per D-14's non-regression
  requirement, network permitting (a skip is NOT the gate passing — it must actually run at least
  once before phase close, per the milestone's own standing convention)

### Wave 0 Gaps
- [ ] New fixture directory `tests/fixtures/citation_render_gate/` (or similar): 2 documents, a
      forward reference (definition after first use), 2+ citations of the same key (for the
      multi-backref D-03 shape and CIT-04's proof), a cross-document citation, a duplicate key across
      both documents (D-10), and an uncited definition (D-07)
- [ ] New test module (suggested `tests/test_citation_render_gate.py`) covering CIT-01..CIT-04, CIT-06
      per the table above
- [ ] GATE-EVIDENCE file recording the verbatim pre-fix `TypstError: expected semicolon or line break`
      (mirroring the `39-GATE-EVIDENCE-0N.md` convention) — see Common Pitfalls / GATE-01 section below
      for what to capture
- [ ] `examples/charged-ieee/{approach1,approach2}/source/index.rst` restoration (exact diffs
      identified below, from commits `8bed1a3`/`c014a0b`)
- [ ] Re-run (not edit) `tests/test_examples_charged_ieee_gate.py` after the restoration — no code
      change needed in this file itself; `_assert_no_warnings` will fail pre-fix (unknown-node
      warnings) and pass post-fix, doubling as SC#5's separator-protocol proof on real shipped content
- [ ] A new assertion (not a new fixture) on `visit_reference`'s existing test coverage
      (`tests/test_cross_doc_label_namespace_render_gate.py` is the closest existing precedent for a
      2-document namespacing proof) OR a dedicated small module for D-14's own-`ids` anchor guard

## GATE-01 RED capture (research focus item 6)

**What to record, and how, so it survives the fix landing:**

1. **The GATE-EVIDENCE file** (new, e.g. `40-GATE-EVIDENCE-01.md`, mirroring the Phase 39 convention
   at `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-0{1..5}.md`) should
   record, verbatim, against the plan-start commit:
   - The fixture `.rst` source (a document with at least one `.. [Label]` definition and one
     `[Label]_` reference).
   - The exact pre-fix emitted `.typ` fragment for the citation
     (`text("Krizhevsky2012")par({text("Krizhevsky, A. …")})` shape — confirmed byte-identical this
     session on an independent fresh probe).
   - The exact exception, reproduced this session:
     ```
     sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation
     failed: TypstError: expected semicolon or line break
         Location: <build>/index.typ
         Details: expected semicolon or line break
     ```
   - The commit hash the RED was captured against (per the repo's durable-gate convention).

2. **The actual pytest module must be a genuine RED->GREEN flip, not the "durable mechanical
   reconstruction" pattern** used by `tests/test_typst_elements_pass_through_gate.py`'s
   `TestPreFixBasisFailureProof` (which only proves `pytest.raises(Exception)` against a
   hand-spliced-from-post-fix-output basis, and is written to survive AFTER the original buggy code
   path no longer exists in any form). CIT-01 is different: the actual pre-fix code path (the
   `unknown_visit` fallback for `citation`/`label`) is what is currently broken, and the SAME test,
   run against the SAME fixture, must fail today and pass after `visit_citation`/`depart_citation`/
   `visit_label` land — mirroring `tests/test_confval_field_body_render_gate.py`'s shape exactly:
   ```python
   # Pattern to follow (verified existing precedent, tests/test_confval_field_body_render_gate.py:111-192)
   def test_citation_gate_compiles_via_real_typst_compile(self, citation_render_gate_dir, temp_build_dir):
       result = _run_sphinx_build_typstpdf(citation_render_gate_dir, temp_build_dir)
       assert result.returncode == 0, (
           f"sphinx-build -b typstpdf failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
       )
       assert "expected semicolon or line break" not in result.stderr
       pdf_output = temp_build_dir / "index.pdf"
       assert pdf_output.exists() and pdf_output.stat().st_size > 0
   ```
   Pre-fix, `result.returncode` is non-zero and `result.stderr` contains the exact fatal quoted above
   (`TypstPDFBuilder.finish()` logs it as an ERROR via `ExtensionError`, matching this repo's existing
   convention for compile fatals surfaced through the `typstpdf` builder). Post-fix, the SAME
   assertions pass. This is the "survives the fix landing" property SC#1 asks for: the test is never
   deleted or rewritten, it just flips.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|-------------------|
| V2 Authentication | no | N/A — build-time Sphinx extension, no runtime auth surface |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes | `escape_typst_string` (used centrally inside `visit_Text`, `typsphinx/translator.py:1212+`) — every citation label and body Text node routes through the SAME, already-existing escaping path via the normal visitor chain (buffer-swap, never `node.astext()`); this phase introduces NO new text-emission primitive and must not add a second escaping routine |
| V6 Cryptography | no | N/A — no cryptographic operation anywhere in this pipeline |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Typst label-syntax injection via an unsanitized citation key (e.g. a key containing `@`, `/`, or other Typst-label-invalid characters) | Tampering | Route every new label through the existing `_namespace_label`/`_sanitize_label` (D-13, unchanged) — already handles the documented `@`->`_u40_`-style encoding; no new sanitizer needed |
| A structurally-required separator (grid-open/grid-close, list-item leading newline) silently miscounted, merging or over-separating adjacent citation runs | Denial of service (rendering-correctness class, mirrors prior phases' equivalent findings) | The GATE-01 fixture (above) plus the D-06 "non-citation node breaks the run" fixture assert the EXACT expected byte/row shape, not just "compiles" |
| A dangling citing reference (a `[Label]_` whose definition was removed/renamed) emitting a `link(<missing-label>)` call | Denial of service (fatal compile abort) | Mirror the existing dangling-target guard pattern (`visit_footnote_reference`'s `logger.warning` + `raise nodes.SkipNode`, `typsphinx/translator.py:2549-2555`) if a same-document citing reference's `refid` cannot be resolved — though note this is already Sphinx's own responsibility pre-translator in the common case (Sphinx itself warns `citation not found` and leaves the reference unresolved before the translator runs) |

## Sources

### Primary (HIGH confidence — real command output, this session)
- `sphinx-build -b typst`/`-b typstpdf` on a hand-written 2-document probe (this session) — verbatim
  `unknown node type: <citation ...>` warnings, verbatim `.typ` defect shape, verbatim `TypstError`.
- `env.get_and_resolve_doctree` dump of `nodes.reference` (`ids`/`refid`/`refuri`) on the same probe
  (this session) — the D-14 discriminator evidence.
- `typst.compile()` + `pypdf` readback (`extract_text(extraction_mode="layout")`, `page.get('/Annots')`,
  `extract_text(visitor_text=...)`'s `cm[4]`/`cm[5]`) on a hand-written grid+link probe (this session).
- `docutils.nodes.citation.__mro__` / `docutils.nodes.label.__mro__` (this session) — confirms `Body`,
  not `Inline`.
- `git show 8bed1a3` / `git show c014a0b` (this session) — the exact restoration diffs for CIT-05.
- `typsphinx/translator.py` read directly, this session: `visit_footnote`/`visit_footnote_reference`
  (2510-2633), `_namespace_label`/`_sanitize_label` (3576/3519/3567), `visit_reference`/
  `depart_reference` (3820-4031), `_visit_admonition`/`_depart_admonition` (4343-4426),
  `_CONCAT_CONTEXTS`/`_inline_concat_context`/`_enter_inline_concat_element`/
  `_exit_inline_concat_element` (1053-1141), `visit_paragraph`/`depart_paragraph` (832-947),
  `visit_document` (473-506, the footnote pre-pass precedent), `_emit_id_anchors` (400-471),
  `visit_field_body`/`depart_field_body` (5692-5807).
- `tests/test_corpus_gate.py:210-241, 490-503` read directly — confirms both `citation` mentions are
  synthetic unit-test strings for the warning-parser, not live-build assertions; no change required
  there.
- `tests/test_desc_break_marker_buffer_swap_gate.py:239-246` read directly — confirms the "Phase 40's
  citation work is the sole exception" comment and its context.
- `tests/test_examples_charged_ieee_gate.py` read in full — confirms `_assert_no_warnings` will
  naturally re-exercise the CIT-05 restoration as a regression gate with zero code changes needed.

### Secondary (MEDIUM confidence)
- `40-CONTEXT.md` — the phase's own same-day (2026-08-02) measurement record; treated as authoritative
  per the task's instruction not to re-litigate it, and independently corroborated wherever this
  document re-derived the same facts.
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-RESEARCH.md`'s Validation Architecture /
  Security Domain sections — the template this document's equivalent sections follow.

### Tertiary (LOW confidence)
- None — every claim in this document traces to a primary or secondary source above.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependency; both tools already verified importable this session.
- Architecture: HIGH — every emission shape independently compiled and read back this session.
- Pitfalls: HIGH — the list-item nesting failure mode and the duplicate-key resolution direction were
  both independently reproduced this session (not carried over from `40-CONTEXT.md`, which did not
  measure these two specific scenarios).

**Research date:** 2026-08-02
**Valid until:** 2026-09-01 (30 days — stable domain, no external API/version drift risk; re-verify if
`typst-py` or `docutils` are bumped before this phase lands)
