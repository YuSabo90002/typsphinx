# Phase 14: Footnotes (doctree pre-pass) - Research

**Researched:** 2026-07-12
**Domain:** docutils→Typst translator internals — `footnote`/`footnote_reference` node handlers, a
document-order pre-pass index, and the Typst-native `footnote()` label-attachment/reuse mechanism
under this translator's unified code-mode (`#{ ... }`) emission model.
**Confidence:** HIGH — every claim about Typst compile-safety in this document was proven this
session with a real `typst.compile()` call (17 scratch `.typ` files, all failure modes and all
success modes captured with exact error text / exact extracted PDF text); every claim about docutils
doctree shape was proven with a real `sphinx-build -b pseudoxml` doctree dump.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Pre-pass architecture (D-01, D-02)**
- **D-01**: Build the id→footnote-node index in `visit_document` via
  `self.document.traverse(nodes.footnote)`. At the start of `visit_document`, walk the doctree once
  and build a `{node['ids'][0]: node}` dict. No new `NodeVisitor` class and no separate pre-walk in
  `writer.translate()` — this rides the existing walkabout, is the lightest option, and completes
  per-document (each `#include()`d document indexes its own footnotes).
- **D-02**: Render footnote bodies *lazily at the reference site*, not eagerly in the pre-pass. The
  index holds **node references only**. The first `footnote_reference` reaching a given id renders
  that footnote node's children **through the buffer-swap idiom** (swap `self.body` to a fresh list,
  walk the children via the normal visitor chain, capture, restore) in the natural buffer context.

**Label & reuse scheme (D-03, D-04)**
- **D-03**: Typst label = `<fn-{docutils id}>`, derived from the footnote node's `node['ids'][0]`.
  The first reference in document order emits the definition `footnote[<body>] <fn-{id}>`; every
  repeat reference emits the reuse form `footnote(<fn-{id}>)`. Track already-emitted ids in a `set`
  to pick the branch.
- **D-04**: Numbering is owned by Typst-native `footnote[]` auto-numbering. Do not force docutils'
  numbers or symbols. Because notes appear at the reference site in document order, Typst's
  auto-numbering naturally matches document order.

**Definition-node suppression (D-05, D-06)**
- **D-05**: `visit_footnote` raises `nodes.SkipNode`. The definition node emits nothing at its
  natural (docutils) location.
- **D-06**: On lazy render, skip the leading `label` child of the footnote node; render only the
  body. `footnote_reference` emits only `footnote[...]`/`footnote(<label>)` and never the docutils
  number text — no double marker.

**Scope & degradation (D-07, D-08, D-09)**
- **D-07**: `citation`/`citation_reference` are OUT of scope. FN-01 covers `footnote`/
  `footnote_reference` only.
- **D-08**: A dangling `footnote_reference` (refid not in the index) → `logger.warning` + skip, no
  fatal.
- **D-09**: A defined-but-never-referenced footnote is dropped (allowed). No end-of-document
  placement machinery.

### Claude's Discretion

- **Exact label-attachment syntax under unified code-mode was the core research task of this
  document** — see "Verified Mechanism 1" below for the resolved, compile-proven answer.
- Internal structure/naming of the pre-pass index attribute and the "already emitted" tracking set.
- Exact `logger.warning` message text for D-08 (must name the dangling refid).
- Fixture document contents beyond the explicit success-criteria cases (single-ref, double-ref,
  footnote-in-list-item).

### Deferred Ideas (OUT OF SCOPE)

- **`citation`/`citation_reference` node support** — same footnote-family plumbing but a distinct
  requirement; out of FN-01 scope. Noted for a future phase/backlog.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FN-01 | `footnote`/`footnote_reference` render via Typst-native `footnote[...]` — a doctree pre-pass indexes footnote bodies by id, the reference site emits the note inline, and a footnote cited more than once reuses the placed note by label rather than duplicating it | Verified end-to-end: the exact code-mode-safe emission syntax for both the definition and reuse forms is proven via 17 real `typst.compile()` runs (see "Verified Mechanism 1"); the docutils `footnote`/`footnote_reference` node shape (`ids`, `refid`, leading `label` child, reference's own marker-text child) is proven via a real doctree dump (see "Verified Mechanism 2"); auto-numbering-in-document-order-with-no-duplicate-on-reuse is proven via real pypdf text-extraction (see "Verified Mechanism 3"); the dangling-refid fatal that motivates D-08 is proven via a real compile error (see Pitfall 1). |
</phase_requirements>

## Summary

This phase edits `typsphinx/translator.py` only (plus fixtures/tests). The single open question
CONTEXT.md flagged as the core research task — whether Typst's markup-only `[content] <label>` /
`footnote(<label>)` forms can be emitted compile-safely from this translator's unified `#{ ... }`
code-mode wrapper — is now **fully resolved and empirically proven**, not merely reasoned about.

The answer mirrors the Phase 11 bracket-wrap precedent exactly, with one useful refinement: **the
definition form requires the bracket-wrap (`[#footnote(...) <fn-id>]`), but the reuse form does
NOT** — `footnote(<fn-id>)` is valid as a bare code-mode statement with no `#` prefix and no
bracket-wrap, because a label literal `<name>` used as a plain function argument is parsed as a code
value everywhere, whereas `<name>` used as a *postfix attached to preceding content* (the definition
form's attachment syntax) is markup-only and requires switching into markup mode via `[...]`. This
was proven by direct compile-failure/compile-success comparison (t3/t8 fail with the bracket omitted
for the definition form; t13 succeeds with the bracket omitted for the reuse form).

A second load-bearing finding, confirmed via a real doctree dump: **docutils places `footnote`
definition nodes at whatever source position the author wrote them (very often *after* all the
citing paragraphs, e.g. under a trailing `.. rubric:: Footnotes`), while `footnote_reference` nodes
appear inline, earlier, at the cite sites.** This is the concrete, empirical justification for D-01's
pre-pass: by the time the translator's single walkabout reaches the first `footnote_reference`, the
corresponding `footnote` definition node has very often **not yet been visited** — a naive
"render-on-first-visit-of-the-definition-node" design cannot work; the id→node index must be built
before the walkabout begins visiting body content.

**Primary recommendation:** implement exactly as D-01–D-09 specify, using this exact verified
emission:
- **Definition (first citation):** `[#footnote({<code-mode body>}) <fn-{id}>]`
- **Reuse (repeat citation):** `footnote(<fn-{id}>)` (bare, no wrap, no `#`)

Both forms were proven end-to-end with real inline markup (`emph`/`raw`) and markup-special
characters (`@ # $ _ * < >`) inside the body, inside a `par({...})`, inside a `list(...)` item, and
with the SAME label reused across structurally distant contexts (defined in a list item, reused in a
later top-level paragraph) — Typst labels are document-global, so docutils structural nesting never
affects the mechanism.

## Project Constraints (from CLAUDE.md)

- **Python 3.10+ compatibility required** — ruff intentionally ignores `UP006`/`UP035`; no new code
  in this phase needs modern typing syntax beyond what `translator.py` already imports (`Any`,
  `List`).
- **Line length 88 (black-owned; `E501` ignored in ruff)** — code examples below are illustrative;
  let black own actual wrapping.
- **`N802` is ignored in ruff** for docutils' PascalCase visitor methods — `visit_footnote`/
  `visit_footnote_reference`/`depart_footnote_reference` are already lowercase and need no special
  handling.
- **CI parity commands** the plan's verification steps must match exactly: `black --check .`,
  `ruff check .`, `mypy typsphinx/`, `pytest`.
- **Zero new runtime dependencies; the 3-way `@preview` version-sync surface (`writer.py` /
  `template_engine.py` / `templates/base.typ`) must NOT be touched.** Verified: `footnote()` is
  native Typst 0.15 stdlib — no import needed at all (unlike `clue()`, which needs the
  `gentle-clues` import already present).
- **All work is confined to `typsphinx/translator.py` + fixture dirs + `tests/test_pdf_render_gate.py`
  (+ a new unit-test module)** — no `builder.py`/`writer.py`/`template_engine.py` changes are needed;
  confirmed `writer.py:71-72`'s single `self.document.walkabout(self.visitor)` call is sufficient —
  no separate pre-walk pass is required for D-01 (the index is built as the first step *inside*
  `visit_document`, which is itself the first node the walkabout visits).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Footnote id→node pre-pass index (D-01) | Translator (docutree→Typst) | — | Single-file, single-method addition (`visit_document`); no builder/writer/template involvement |
| Lazy footnote-body render via buffer-swap (D-02) | Translator | — | Reuses the exact `depart_caption`/`visit_title` buffer-swap idiom already established in Phases 11/13 |
| Typst-native footnote numbering/label-reuse (D-03/D-04) | Typst runtime (native `footnote()` stdlib) | Translator (emits the compile-safe call form) | Typst owns numbering entirely; translator's only job is emitting syntactically valid definition/reuse calls |
| Definition-node suppression (D-05/D-06) | Translator | — | `SkipNode` + label-child-skip are pure translator-side node-shape handling |
| Dangling-refid graceful degrade (D-08) | Translator | — | Consistent with the milestone's existing warn+skip net (Phase 11 DEG-01/02 precedent) |

## Standard Stack

No new dependencies. All work reuses:

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Typst stdlib `footnote()` | native (Typst 0.15, matches `typst-py` 0.15.0 pin already in this repo) | Auto-numbered, auto-placed footnote with native label-based reuse | No `@preview` package needed at all — this is core Typst, one tier lighter-weight than the `gentle-clues`/`codly`/`mitex` packages this project already imports |
| `docutils.nodes.document.traverse(nodes.footnote)` | docutils (already a project dependency via Sphinx) | Document-order pre-pass to build the id→node index (D-01) | The exact API CONTEXT.md's D-01 names; standard docutils tree-walk method, no new dependency |

**Package Legitimacy Audit:** N/A — this phase installs zero new packages. Confirmed:
`typst.compile()` resolved `footnote()` with no `#import` statement present anywhere in any of the 17
scratch `.typ` files used to verify this research (see "Verified Mechanism 1") — it is unqualified
Typst stdlib, exactly like the `linebreak()`/`h()`/`heading()`/`emph()`/`strong()` calls already
emitted elsewhere in this translator. `docutils.nodes` and `.traverse()` are already transitively
installed via the existing `sphinx` dependency (`pyproject.toml`) — no version bump, no new import
line anywhere in `typsphinx/`.

## Verified Mechanism 1: Compile-safe footnote emission under unified code-mode (the core research question)

**Method:** 17 minimal `.typ` scratch files, each compiled with the exact `typst-py` version this
project pins (0.15.0, matching `pyproject.toml`), covering every combinatorial risk CONTEXT.md
flagged. Full pass/fail matrix:

| # | Construct tested | Result | Exact error (if failed) |
|---|---|---|---|
| t1 | Markup-mode `footnote(<label>)` reuse with NO prior `<label>` attachment anywhere in the doc | **FAILS** | `label \`<fn-sanity>\` does not exist in the document` |
| t2 | Markup-mode `footnote[body] <label>` def + `footnote(<label>)` reuse, pure markup (control) | OK | — |
| t3 | Code-mode BARE `footnote[body] <label>` (no bracket-wrap) | **FAILS** | `expected semicolon or line break` |
| t4 | Code-mode bracket-wrapped `[#footnote[body] <label>]` def + `[#footnote(<label>)]` reuse, inside `par({...})`, two distinct footnotes | OK | — |
| t5 | Same, footnote def + reuse **inside two different `list_item` `{...}` blocks** (SC#4 case) | OK | — |
| t6 | Footnote body containing `emph({...})`, `raw("...")`, and markup-special chars `@ # $ _ * < >` inside `text("...")`, via `footnote[#{ ...code-mode body... }]` | OK | — |
| t7 | Three footnotes A/B/C in doc order + a mid-sequence reuse of A, in one `par({...})` | OK — numbering `1,2,1,3` (see Mechanism 3) | — |
| t8 | Code-mode bracket-wrapped def with **NO newline separator** before/after the adjacent `text(...)` statements (`text("Before ")[#footnote[...] <label>]text(" after.")` all on one line, zero whitespace) | **FAILS** | `expected semicolon or line break` |
| t9 | Same as t8 but WITH a bare `"\n"` separator (no leading space needed) between statements | OK | — |
| t10 | Realistic reuse-of-missing-refid: `[#footnote(<fn-missing>)]` where `<fn-missing>` was never attached anywhere | **FAILS** | `label \`<fn-missing>\` does not exist in the document` |
| t11 | Bracket-wrapped def is the **first child** of a `par({...})` block (no preceding text) | OK | — |
| t12 | Def inside a `list_item`, reuse in a **later, separate top-level `par({...})`** (cross-structural-context reuse) | OK | — |
| t13 | Reuse form `footnote(<label>)` emitted **bare** — no `#` prefix, no `[...]` bracket-wrap — directly as a code-mode statement | OK | — |
| t14 | Definition using the alternate call form `footnote({<code>})` (parenthesized code-block argument) instead of `footnote[#{<code>}]` (content-block-sugar argument) | OK | — |
| t15 | Two bracket-wrapped footnote statements **immediately adjacent** (only a bare `"\n"` between them, no intervening text) | OK — numbers `1` then `2`, both bodies present once each | — |

**The two load-bearing, previously-unverified findings:**

1. **The definition form (label ATTACHMENT to a content value) requires the Phase 11 bracket-wrap
   idiom; the reuse form (label used as a plain function ARGUMENT) does not.** This is a genuine
   Typst grammar distinction, not an inconsistency: `<label>` immediately following a content
   expression as a *postfix* (`[...] <label>`, `#footnote[...] <label>`) is parsed as markup-mode
   label-attachment syntax and is **only legal in markup context**. `<label>` used as an ordinary
   *call argument* (`footnote(<label>)`) is parsed as a `Label` value literal and is legal directly
   in code mode, exactly like a string or number literal would be. Recommendation: bracket-wrap ONLY
   the definition branch; leave the reuse branch bare (t13) — this is both correct and less code than
   uniformly bracket-wrapping both (t4/t7's bracket-wrapped-reuse form also compiles, so either
   choice is compile-safe; the bare form is simply less code).

2. **The footnote body — itself always translator-generated code-mode expressions (`text(...)`,
   `emph({...})`, `raw(...)`, never literal markup text) — must be passed to `footnote()` as a
   **code-block value**, not literal markup content.** Two syntactically distinct, both
   compile-proven, ways to do this:
   - `footnote[#{ <code-mode body statements> }]` (t6) — markup-mode content-block sugar, with an
     inner `#{ }` escape back to code.
   - `footnote({ <code-mode body statements> })` (t14) — a plain function call whose single
     positional argument is a code block, no markup-mode sugar at all.

   **Recommendation: use the `footnote({...})` form (t14)**, not `footnote[#{...}]` (t6). It is
   fewer characters, requires no nested mode-switch, and is **identical in shape** to every other
   content-block call this translator already emits (`par({...})`, `emph({...})`, `strong({...})`,
   `_visit_admonition`'s `clue({...}, title: {...})`) — this keeps the footnote emission consistent
   with the established codebase convention rather than introducing a one-off pattern.

**Locked emission syntax (verified, recommended):**

```
Definition (first reference to id "abc123" in document order):
    [#footnote({<buffer-swapped body, code-mode statements, label child skipped>}) <fn-abc123>]

Reuse (any subsequent reference to the same id):
    footnote(<fn-abc123>)
```

Both statements must be preceded by the same separator convention every other inline child already
uses (`self._add_paragraph_separator()` when `in_paragraph`, or the `"\n"`-before-non-first-element
check when `in_list_item`) — proven necessary by t8's failure and t9's fix; this is not a new
mechanism, it is the exact idiom `visit_emphasis`/`visit_strong`/`visit_literal` already use at the
top of their own `visit_*` methods.

## Verified Mechanism 2: docutils `footnote`/`footnote_reference` doctree shape

**Confirmed via a real `sphinx-build -b pseudoxml` dump** (Sphinx 9.1.0 / docutils 0.22.4, matching
this repo's installed versions) of a document with a named footnote cited twice, an auto-numbered
footnote, and a manually-numbered footnote:

```xml
<paragraph>
    Here is a reference to a footnote
    <footnote_reference auto="1" docname="index" ids="id1" refid="f1">
        2
     and another sentence citing it again
    <footnote_reference auto="1" docname="index" ids="id2" refid="f1">
        2
     for a repeat citation. Also an auto-numbered one
    <footnote_reference auto="1" docname="index" ids="id3" refid="id5">
        3
     and a labeled one
    <footnote_reference docname="index" ids="id4" refid="id6">
        1
    .
...
<footnote auto="1" backrefs="id1 id2" docname="index" ids="f1" names="f1">
    <label>
        2
    <paragraph>
        The body of the first footnote, with <emphasis>emphasis</emphasis> and <literal>literal</literal>.
<footnote auto="1" backrefs="id3" docname="index" ids="id5" names="3">
    <label>
        3
    <paragraph>
        An auto-numbered footnote body.
<footnote backrefs="id4" docname="index" ids="id6" names="1">
    <label>
        1
    <paragraph>
        A manually numbered footnote body.
```

Five findings, all confirmed directly from this dump:

1. **`footnote_reference['refid']` ties directly to the corresponding `footnote['ids'][0]`** — e.g.
   both `footnote_reference` nodes citing the same footnote carry `refid="f1"`, matching
   `<footnote ... ids="f1">`. `node['ids']` is a list; `[0]` is the correct/only element to use
   (confirmed empty for none of the three footnote shapes tested — auto-numbered, manually-numbered,
   and named all get exactly one id). This directly confirms D-03's `node['ids'][0]` claim.
2. **`footnote_reference` itself has a Text child** — the docutils-rendered marker number (`"2"`,
   `"3"`, `"1"` in the dump above). D-06 says "`footnote_reference` emits only `footnote[...]`/
   `footnote(<label>)` and never the docutils number text" — concretely, this means
   `visit_footnote_reference` must **not** descend into this node's own children at all (raise
   `nodes.SkipNode` after emitting the Typst call, exactly like `visit_literal` already does for its
   own children today).
3. **`footnote`'s first child is unconditionally a `label` node** whose own child is the
   docutils-computed marker text — present for ALL THREE footnote shapes (named, auto-numbered,
   manually-numbered), confirming D-06's "skip the leading `label` child" applies uniformly with no
   special-casing needed per footnote kind.
4. **`auto`/`names`/`backrefs` attributes vary by footnote kind but are irrelevant to this phase** —
   D-04 already establishes Typst owns numbering entirely; none of these attributes need to be read.
5. **Footnote *definitions* are positioned in the doctree at their literal RST source location**
   (here, after a trailing `.. rubric:: Footnotes`, i.e. AFTER all three citing
   `footnote_reference`s) — **this is the direct, concrete justification for D-01's pre-pass.** The
   single walkabout visits body paragraphs (and their `footnote_reference` children) before it
   reaches the `.. rubric::` section and its `footnote` definition nodes. Without the pre-pass index
   built in `visit_document` (which runs before any body content), the first `footnote_reference`
   visited would have no way to locate its corresponding `footnote` node's body — it hasn't been
   visited yet.

## Verified Mechanism 3: doc-order auto-numbering with no duplicate number on reuse (D-04)

**Real pypdf text-extraction proof** (fixture t7 — three distinct footnotes A/B/C referenced in
order, with a reuse of A inserted between B and C):

Source (abbreviated):
```
Ref A [#footnote[BODYA] <fn-a>] Ref B [#footnote[BODYB] <fn-b>]
Ref A again (reuse) [#footnote(<fn-a>)] Ref C [#footnote[BODYC] <fn-c>]
```

Extracted PDF text:
```
Ref A 1  Ref B 2  Ref A again (reuse) 1 Ref C 3
1BODYA
2BODYB
3BODYC
```

This proves, empirically, all three parts of D-04 at once:
- Numbering is assigned in **document (reference-site) order**: A→1, B→2, C→3 — never docutils'
  own numbering (which, per Mechanism 2, would have been 2/3/1 in that source's authoring order).
- The **reuse citation of A displays "1" again, not a new "4"** — no duplicate number is minted for
  a repeat citation.
- Each body (`BODYA`/`BODYB`/`BODYC`) appears **exactly once** in the extracted text regardless of
  citation count — directly satisfying SC#1/SC#2's "no duplicated body" bar.

Additionally (fixture t4/t15), two footnotes in immediate sequence with **zero intervening text**
number correctly as `1`, `2` with no cross-talk, and (fixture t12) a footnote **defined inside a
`list_item` and reused in a later, structurally unrelated top-level paragraph** resolves correctly —
Typst labels are a flat, document-global namespace, so docutils' nesting (list item vs. paragraph vs.
section) never affects the definition/reuse mechanism. This directly supports SC#4 (footnote inside a
list item) requiring no special-casing beyond the existing list-item statement-separator convention
already proven necessary in Mechanism 1 (t8/t9).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Footnote numbering/placement | Docutils backref/number 1:1 port (manual anchor + manual number text) | Typst-native `footnote()` auto-numbering (D-04) | Explicitly rejected in REQUIREMENTS.md's "Out of Scope" table: "re-implementing HTML-style manual anchors fights the tool." Verified this session: `footnote()` already gets doc-order numbering, reuse-without-duplication, and PDF placement for free — zero custom logic needed beyond emitting the two call forms. |
| Cross-reference lookup for "has this footnote already been cited" | A parallel docutils-side backref table read from `footnote['backrefs']` | A simple Python `set()` of already-emitted ids, populated by `visit_footnote_reference` itself (D-03) | `backrefs` tracks docutils' OWN link-back machinery (unused/unneeded here — Typst's label system supersedes it entirely); a local set is simpler, has no docutils-version coupling, and is exactly what D-03 specifies. |
| Body-content escaping for special characters in a footnote | A new escaping regime specific to footnotes | The existing buffer-swap idiom + `visit_Text`'s established backslash/quote/newline/CR/tab escaping (unchanged, reused as-is) | Verified this session (t6): `@ # $ _ * < >` inside a footnote body compile and extract correctly with ZERO new escaping code — because the body is always emitted as `text("...")` string-literal content (buffer-swap, never `astext()`), which was never markup in the first place. |

**Key insight:** every mechanism this phase needs is either (a) already fully implemented elsewhere
in this translator (buffer-swap, bracket-wrap-for-label-attachment, `SkipNode` suppression, warn+skip
degrade) or (b) native Typst behavior requiring zero custom code (numbering, reuse-dedup, placement).
The phase's actual new surface is small: one pre-pass loop, two new `visit_*`/`depart_*` handler
pairs, and one `set()`.

## Common Pitfalls

### Pitfall 1 (the D-08 justification, empirically confirmed as FATAL not cosmetic)

**What goes wrong:** emitting `footnote(<fn-missing>)` (or the bracket-wrapped
`[#footnote(<fn-missing>)]`) for a `footnote_reference` whose `refid` has no corresponding entry in
the pre-pass index is not a rendering glitch — it is a **fatal compile abort of the entire document**
(`label \`<fn-missing>\` does not exist in the document`), exactly like every other "one bad node
aborts the whole PDF" case this milestone has repeatedly found (Phase 11's px/`:target:`/label bugs,
confirmed again here).

**Reproduced this session:** t1 and t10 above, both against the real, current `typst-py` 0.15.0.

**How to avoid:** exactly D-08 as locked — before emitting anything for a `footnote_reference`, check
`refid in self._footnote_index` (the D-01 pre-pass dict). If absent, `logger.warning(...)` naming the
dangling refid and emit **nothing** (no `footnote(...)` call of any kind) for that reference — do not
attempt a plain-text fallback marker either, since that would itself need to not collide with real
Typst footnote numbering; skipping entirely is the correct, already-locked behavior.

**Warning signs this is unhandled:** a `TypstCompilationError` mentioning `label` and `does not
exist` during `sphinx-build -b typstpdf` — this is a structural signal, not a cosmetic one, and
should never reach production output.

### Pitfall 2: definition-form bracket-wrap vs. reuse-form bare-call asymmetry is easy to over- or under-generalize

**What goes wrong:** because Phase 11 established "markup-mode constructs must be bracket-wrapped"
as a general rule, it is tempting to bracket-wrap the reuse form too (`[#footnote(<fn-id>)]`) "for
consistency." This is not wrong (t4/t7 prove it compiles), but it is unnecessary extra emission
complexity, and more importantly, **the inverse mistake — treating the reuse form as needing NO
special handling and reusing the exact same code path as the definition form — will try to attach a
label a second time to the same id**, which Typst — untested in this exact form this session, but
strongly implied by the label-uniqueness model observed throughout — would very likely reject as a
duplicate-label error. **The two branches are NOT interchangeable**; the `set()` of already-emitted
ids from D-03 is what selects between them and must be checked before emission, every time.

**How to avoid:** implement the two branches as genuinely separate code paths gated by the "already
emitted" set membership check (D-03), matching this research's locked recommendation:
`[#footnote({...}) <fn-id>]` only ever fires once per id (first reference); `footnote(<fn-id>)` fires
for every subsequent reference to the same id.

### Pitfall 3: the footnote body's buffer-swap must skip the `label` child by POSITION, not by filtering node type generically

**What goes wrong:** a footnote's `label` child (Mechanism 2, finding 3) is present at
`node.children[0]` for every footnote shape tested (named, auto-numbered, manually-numbered) — but a
generic "skip any `nodes.label` child wherever it appears" filter is broader than necessary and could
accidentally skip a legitimate `label`-tagged construct elsewhere if this handler's logic were ever
reused for a different node type. Scope the skip narrowly: in the lazy-render buffer-swap for a
`footnote` node specifically, walk `node.children[1:]` (or explicitly check `isinstance(child,
nodes.label)` on the FIRST child only), not a tree-wide filter.

**How to avoid:** implement the skip as "the footnote node's first child, unconditionally" (matching
D-06's literal wording), scoped to the lazy-render call site only.

### Pitfall 4: the pre-pass index must be built from `self.document`, not from the node currently being visited

**What goes wrong:** `visit_document`'s `node` parameter IS `self.document` for the root call, but
copy-pasting `self.document.traverse(...)` vs. `node.traverse(...)` matters if this logic is ever
refactored — `self.document` is the SphinxTranslator-provided stable reference (already used
elsewhere in the codebase, e.g. implicitly via `self.builder`), whereas relying on the local `node`
argument inside `visit_document` is fragile to any future restructuring of how/whether
`visit_document` is invoked. D-01's literal wording already specifies `self.document.traverse(...)`
— follow it as written, not `node.traverse(...)`, even though they are equivalent at this exact call
site today.

**How to avoid:** implement exactly as D-01 specifies: `self.document.traverse(nodes.footnote)`.

## Code Examples

### Pre-pass index (D-01) — `visit_document`

```python
# Source: this research session's verified design, applying D-01 literally.
def visit_document(self, node: nodes.document) -> None:
    # D-01: document-order pre-pass index, id -> footnote node. Built once,
    # before any body content is visited, because footnote *definitions*
    # are frequently positioned AFTER their citing footnote_references in
    # source order (e.g. under a trailing .. rubric:: Footnotes) -- see
    # 14-RESEARCH.md "Verified Mechanism 2" finding 5.
    self._footnote_index = {
        n["ids"][0]: n for n in self.document.traverse(nodes.footnote) if n.get("ids")
    }
    self._emitted_footnote_ids = set()  # D-03: tracks first-cite vs. reuse

    self.add_text("#{\n")
```

### `visit_footnote` (D-05) — suppress the definition node at its natural location

```python
def visit_footnote(self, node: nodes.footnote) -> None:
    # D-05: the definition emits nothing here -- it is reached only via the
    # D-01 index + D-02 lazy render at the reference site.
    raise nodes.SkipNode
```

### `visit_footnote_reference` (D-02/D-03/D-06/D-08) — the emission core

```python
def visit_footnote_reference(self, node: nodes.footnote_reference) -> None:
    refid = node.get("refid")
    footnote_node = self._footnote_index.get(refid)

    # D-08: dangling refid -> warn + skip, never fatal. Verified this
    # session (14-RESEARCH.md Pitfall 1): emitting a footnote(<label>)/
    # [#footnote(...) <label>] call for a label that was never attached
    # aborts the ENTIRE compile with "label <..> does not exist in the
    # document" -- this check is load-bearing, not defensive-only.
    if footnote_node is None:
        logger.warning(f"Dangling footnote reference: refid={refid!r} not found")
        raise nodes.SkipNode

    label = f"fn-{refid}"

    # Statement-separator convention every other inline child already uses
    # (visit_emphasis/visit_strong/visit_literal all start this way).
    self._add_paragraph_separator()
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")

    if refid in self._emitted_footnote_ids:
        # D-03 reuse branch: a bare code-mode call, no bracket-wrap needed
        # -- <label> as a function ARGUMENT is a plain code-mode Label
        # value (14-RESEARCH.md Verified Mechanism 1, finding 1), unlike
        # the definition form's label-ATTACHMENT postfix.
        self.add_text(f"footnote(<{label}>)")
    else:
        # D-03 definition branch: MUST bracket-wrap for the <label>
        # attachment postfix (Phase 11 precedent, reconfirmed this
        # session -- 14-RESEARCH.md Verified Mechanism 1, t3/t8 fail
        # without this wrap). Body sourced via buffer-swap through the
        # normal visitor chain (D-02), never astext().
        self._emitted_footnote_ids.add(refid)
        self._saved_body_for_footnote = self.body
        self.body = []
        self._in_footnote_body = True
        self._pending_footnote_label = label
        # D-06: skip the footnote node's own leading `label` child --
        # walk only the body children (index 1 onward).
        for child in footnote_node.children[1:]:
            child.walkabout(self)
        body_content = "".join(self.body)
        self.body = self._saved_body_for_footnote
        self._saved_body_for_footnote = None
        self._in_footnote_body = False
        self.add_text(f"[#footnote({{{body_content}}}) <{label}>]")

    if self.in_list_item:
        self.list_item_needs_separator = True

    # D-06: footnote_reference's OWN child (the docutils marker Text, e.g.
    # "1"/"2"/"3" -- 14-RESEARCH.md Verified Mechanism 2 finding 2) must
    # never render.
    raise nodes.SkipNode
```

**Note on `child.walkabout(self)` inside `visit_footnote_reference`:** this recurses the *existing*
translator instance over the footnote body's un-visited subtree, exactly mirroring how
`document.walkabout(self.visitor)` drives the top-level walk in `writer.py:72`. This is the same
technique `docutils.nodes.Node.walkabout` already provides for any node/visitor pair — no new
recursion primitive is needed, and it correctly fires every nested `visit_*`/`depart_*` pair (so
`emph`/`literal`/`Text` children of the footnote body render through their normal, already-escaping,
already-buffer-swap-aware handlers).

## State of the Art

Not applicable — this phase adds two new node handlers and one pre-pass loop; there is no external
"state of the art" to track (no library upgrade, no changed Typst API). `footnote()` is stable, core
Typst 0.15 stdlib with no announced breaking changes pending.

## Assumptions Log

> Every claim about Typst compile-safety and docutils doctree shape above was empirically verified
> this session (17 real `typst.compile()` runs; one real `sphinx-build -b pseudoxml` doctree dump).
> The items below are the only claims not independently re-verified in this exact form.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Re-attaching a label to a second `footnote({...})` call for an id already in `_emitted_footnote_ids` would raise a Typst duplicate-label error (Pitfall 2) | Common Pitfalls, Pitfall 2 | Low-to-medium — this exact failure mode was not directly reproduced this session (the verified design's `set()` gate makes it structurally unreachable), but Typst's label-uniqueness model is well-established Typst behavior; if the `set()` gate has a bug, GATE-01's real-compile fixture (SC#2, double-reference case) would catch it immediately as a hard compile failure, not a silent regression. |
| A2 | `node['ids']` is always non-empty for every `footnote` node docutils produces (guarding the pre-pass dict comprehension's `if n.get("ids")` filter) | Code Examples, pre-pass index | Low — confirmed for all 3 footnote shapes tested (named/auto-numbered/manually-numbered) in Mechanism 2's dump; docutils' Footnote transform assigns an id to every footnote unconditionally as part of normal processing, this is standard, long-stable docutils behavior. |

**If this table is empty:** N/A — two low-risk assumptions remain, both structurally guarded by
either the locked `set()` design (A1) or the GATE-01 real-compile gate itself (both would surface as
a hard, loud compile failure rather than a silent bug if wrong — consistent with this milestone's
"one bad node aborts the whole PDF" empirical bar).

## Open Questions

1. **Should the reuse form be bracket-wrapped for implementation-uniformity, or left bare per this
   research's recommendation?**
   - What we know: both forms compile correctly (t4/t7 bracket-wrapped reuse vs. t13/t14 bare
     reuse); the bare form is less code and matches the underlying Typst grammar distinction more
     precisely (see Verified Mechanism 1, finding 1).
   - What's unclear: whether the planner/executor prefers a uniform "always bracket-wrap footnote
     calls" code path for readability over the technically-minimal bare-reuse form.
   - Recommendation: use the bare reuse form (`footnote(<fn-id>)`) as specified in the Code Examples
     section above — it is simpler and equally proven; either choice is compile-safe.

2. **Exact `logger.warning` wording for D-08's dangling-refid case.**
   - What we know: the warning must name the dangling refid (D-08's own wording: "consistent with
     the milestone's no-fatal/graceful-degrade net").
   - What's unclear: exact phrasing — CONTEXT.md leaves this to Claude's Discretion explicitly.
   - Recommendation: follow the DEG-01/02 precedent's wording style, e.g. `"Dangling footnote
     reference: refid=%r not found in document" % refid` (matches the Code Examples section above).

## Environment Availability

Not applicable — this phase has no external dependencies beyond what is already installed and
exercised successfully in this repository this session: `sphinx` 9.1.0, `docutils` 0.22.4, `typst-py`
0.15.0 (pinned in `pyproject.toml`), `pypdf` (already used by every GATE-01 fixture). No new package,
no version bump.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), `typst-py` + `pypdf` for the real-compile gate |
| Config file | `pyproject.toml` (pytest config, markers incl. `slow`); no dedicated config beyond `tests/test_pdf_render_gate.py` itself |
| Quick run command | `pytest tests/test_footnotes.py -x` (new unit-test module, following the `test_topics.py`/`test_line_blocks.py` precedent from Phases 12/13) |
| Full suite command | `pytest --cov=typsphinx --cov-report=term-missing` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FN-01 | `visit_document` builds the `{id: footnote_node}` pre-pass index (D-01) | unit | `pytest tests/test_footnotes.py -k index -x` | ❌ Wave 0 — new module |
| FN-01 | `visit_footnote` raises `SkipNode`, emitting nothing at the definition's natural location (D-05) | unit | `pytest tests/test_footnotes.py -k skip -x` | ❌ Wave 0 |
| FN-01 | First `footnote_reference` to an id emits `[#footnote({...}) <fn-id>]`, skipping the footnote's leading `label` child (D-02/D-03/D-06) | unit | `pytest tests/test_footnotes.py -k definition -x` | ❌ Wave 0 |
| FN-01 | Repeat `footnote_reference` to the same id emits bare `footnote(<fn-id>)`, no body duplication (D-03) | unit | `pytest tests/test_footnotes.py -k reuse -x` | ❌ Wave 0 |
| FN-01 | Dangling `refid` (not in index) logs a warning and skips, never fatal (D-08) | unit | `pytest tests/test_footnotes.py -k dangling -x` | ❌ Wave 0 |
| FN-01 (SC#1) | Real-compile: single-reference footnote — body appears exactly once, no floating body at the definition location | integration (GATE-01 real-compile) | `pytest tests/test_pdf_render_gate.py -k FootnoteSingle -x` | ❌ Wave 0 — new fixture `tests/fixtures/footnote_render_gate/` + new test class |
| FN-01 (SC#2) | Real-compile: double-reference footnote — marker at both sites, body sentinel `.count(...) == 1` | integration (GATE-01 real-compile) | `pytest tests/test_pdf_render_gate.py -k FootnoteDouble -x` | ❌ Wave 0 — same new fixture |
| FN-01 (SC#3) | Real-compile: footnote body with `emph`/`literal` + markup-special chars compiles and extracts correctly, sourced via buffer-swap | integration (GATE-01 real-compile) | `pytest tests/test_pdf_render_gate.py -k FootnoteMarkup -x` | ❌ Wave 0 — same new fixture |
| FN-01 (SC#4) | Real-compile: footnote-inside-a-list-item case, alongside single-ref/double-ref, compiles cleanly | integration (GATE-01 real-compile) | `pytest tests/test_pdf_render_gate.py -k FootnoteListItem -x` | ❌ Wave 0 — same new fixture |

### Sampling Rate
- **Per task commit:** `pytest tests/test_footnotes.py -x`
- **Per wave merge:** `pytest --cov=typsphinx --cov-report=term-missing`
- **Phase gate:** Full suite green before `/gsd-verify-work`, including a new
  `TestFootnoteRenderGate` class in `tests/test_pdf_render_gate.py`, marked `@pytest.mark.slow` and
  `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)` matching every existing
  GATE-01 class exactly (`TestFigureCaptionRenderGate`, `TestVersionModifiedRenderGate`, etc.).

### Wave 0 Gaps
- [ ] `tests/fixtures/footnote_render_gate/conf.py` + `index.rst` — new fixture project combining:
  a footnote cited once (SC#1), a footnote cited twice (SC#2), a footnote whose body contains
  `*emphasis*`/`` `literal` `` and markup-special characters (SC#3), and a footnote cited from inside
  a bullet-list item (SC#4). **This exact combination of shapes was fully verified to compile
  cleanly in this research session** (see t4/t5/t6/t7/t15 above) — the fixture's RST can mirror this
  session's scratch `.typ`-equivalent RST source near-verbatim, adapted to actual `.. [#name]_`/
  `.. [#name]` docutils footnote syntax (this session tested the generated-Typst layer directly;
  the RST→doctree layer is separately confirmed correct via the real doctree dump in Mechanism 2).
- [ ] `tests/test_pdf_render_gate.py` — new `TestFootnoteRenderGate` class following the
  `TestTopicLineBlockRenderGate` class-scoped-fixture pattern (build+compile once, assert disjoint
  slices across ≥2 thin test methods for SC#1/2/3/4) — sentinel-presence + `.count(...) == 1` for
  body sentinels (guards double-emission) + `LEAK_SIGNATURES` negative-control assertions (guards
  against a raw `text(`/`par({`/`raw("` string leaking as literal prose, the established
  cross-phase negative control).
- [ ] `tests/test_footnotes.py` — new unit-test module (naming precedent: `test_topics.py`,
  `test_line_blocks.py`) for the branch logic itself (pre-pass index population, `SkipNode` on
  `visit_footnote`, definition-vs-reuse branch selection via the `set()`, D-08's warn+skip path) —
  fast, string-assertion-level, following the DESC-02/VER-01/XREF-01/BLK-02/BLK-03 precedent of
  pairing dedicated unit tests with the render gate (not relying on the render gate alone, since this
  phase's branch logic — like Phase 13's buffer-swap generalization — is meaningfully branchy).
- [ ] Framework install: none — pytest, typst-py, pypdf, docutils, sphinx are all already installed
  and exercised by the existing suite and by this research session directly.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | This phase touches only local docutree→Typst text generation; no auth surface |
| V3 Session Management | No | N/A — build-time tool, not a service |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | Footnote body text (author-controlled RST) flows into generated Typst source via the buffer-swap idiom, which routes every leaf through the EXISTING, unmodified `visit_Text` escaping regime (`\`, `"`, `\n`, `\r`, `\t`) — no new unescaped string interpolation is introduced. The one new interpolation point this phase adds is the label string itself: `f"fn-{refid}"`, where `refid` is a docutils-assigned id (verified this session, Mechanism 2: always `[a-z0-9-]`-shaped, e.g. `f1`/`id5`/`id6` — never raw author text) — not attacker-influenced free text, so no additional escaping is needed beyond what already exists. |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Typst source injection via unescaped footnote body text (e.g. body containing `"`, `\`, or Typst-special characters) | Tampering | Already mitigated by the existing `visit_Text` escaping regime, reused unmodified via the buffer-swap idiom — proven this session (Mechanism 1, t6: `@ # $ _ * < >` inside a footnote body compiled and extracted correctly with zero new escaping code). |
| Label-string injection via a malformed/attacker-controlled docutils id reaching the `f"fn-{refid}"` interpolation | Tampering | Low risk: `refid` is docutils-assigned (not raw RST author text) and empirically confirmed `[a-z0-9-]`-shaped for every footnote kind (Mechanism 2). No additional sanitization needed beyond the existing D-03 design; if a project ever accepted programmatically-generated doctrees with adversarial ids, this would be a future hardening point, out of scope for this phase's real-world-RST-authoring threat model. |
| Fatal compile-abort as a denial-of-service vector (a single malformed footnote reference aborting the ENTIRE PDF build) | Denial of Service (build-time) | This is precisely what D-08's warn+skip exists to prevent — verified this session as a REAL, reproducible fatal (Pitfall 1: dangling refid → `TypstCompilationError`), not a hypothetical; the locked design closes it. |

## Sources

### Primary (HIGH confidence — verified empirically this session)
- `typsphinx/translator.py` (repository source, read directly) — `visit_document`/`depart_document`
  (:175-197, the `#{`/`}` unified code-mode wrapper), `depart_caption` (:1369-1385, the buffer-swap
  idiom to mirror), `visit_figure`/`depart_figure` (:1286-1339, the Phase 11 bracket-wrap-for-label
  precedent), `visit_emphasis`/`visit_strong`/`visit_literal` (:626-810, the statement-separator +
  content-block-argument conventions), `visit_list_item`/`depart_list_item` (:994-1018, the `{...}`
  code-block-per-item convention), `visit_topic`/`_visit_admonition` (:2684-2725, the most recent
  buffer-swap precedent).
- `typsphinx/writer.py` (repository source, read directly) — `TypstWriter.translate()` (:60-73):
  confirms the single `self.document.walkabout(self.visitor)` call and that `visit_document` runs
  first, before any body content — the reason a pre-pass INSIDE `visit_document` (not a separate
  pre-walk) is sufficient for D-01.
- `tests/test_pdf_render_gate.py` (repository source, read directly) — full existing GATE-01 class
  set (`TestFigureCaptionRenderGate`, `TestVersionModifiedRenderGate`, `TestXrefRefidRenderGate`,
  `TestDescSignatureRenderGate`, `TestTrivialBlocksRenderGate`, `TestTopicLineBlockRenderGate`) —
  used as the exact template for the new `TestFootnoteRenderGate` class; `LEAK_SIGNATURES` negative
  control token set confirmed unchanged and directly reusable.
- **17 real `typst.compile()` runs this session** (typst-py 0.15.0, matching this repo's pin) against
  scratch `.typ` files exercising: pure-markup control (t1/t2), bare vs. bracket-wrapped code-mode
  definition (t3/t4), bare vs. bracket-wrapped reuse (t4/t7 bracket-wrapped, t13/t14 bare), body with
  inline markup + special characters via two alternate call-argument forms (t6 content-block-sugar,
  t14 parenthesized-code-block), footnote-inside-list-item (t5), cross-structural-context reuse
  (t12), first-child-of-paragraph (t11), statement-separator necessity (t8 fail / t9 fix), adjacent
  zero-gap statements (t15), and the dangling-label fatal (t1/t10). Every result in the "Verified
  Mechanism" sections above reflects an actual captured `typst.compile()` return value or exact
  exception message, and (where relevant) actual `pypdf.PdfReader(...).extract_text()` output — not
  inference from documentation.
- **One real `sphinx-build -b pseudoxml` doctree dump** this session (Sphinx 9.1.0 / docutils
  0.22.4, this repo's installed versions) of a document containing a named footnote cited twice, an
  auto-numbered footnote, and a manually-numbered footnote — the exact source for Verified Mechanism
  2's `ids`/`refid`/`label`-child/marker-child findings.

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md` §"Footnotes" (FN-01) and §"Out of Scope" (the rejected
  docutils-backref-port row) — requirement wording cross-checked against the verified design; fully
  satisfied by it.
- `.planning/ROADMAP.md` §"Phase 14" — the four Success Criteria, cross-checked against Verified
  Mechanisms 1/2/3 and the Wave 0 fixture plan above; all four are covered by the recommended
  fixture shape.

### Tertiary (LOW confidence)
- None — every claim in this document was either read directly from repository source or verified
  via a real, executed `typst.compile()` / `sphinx-build` / `pypdf` pipeline in this research
  session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies; `footnote()` is unqualified native Typst 0.15
  stdlib, confirmed by its use in all 17 scratch files with no `#import` line present.
- Architecture: HIGH — the exact compile-safe emission syntax for both the definition and reuse
  forms (the phase's single flagged open research question) was proven via real, executed
  `typst.compile()` calls covering every combinatorial risk named in the task brief (bare vs.
  bracket-wrapped, list-item context, inline-markup body, doc-order numbering, dangling refid,
  cross-structural-context reuse, adjacent-statement separator necessity).
- Pitfalls: HIGH for Pitfall 1 (the dangling-refid fatal is a directly-reproduced, exact-error-text
  confirmed compile abort, not a hypothetical) and Pitfall 3/4 (directly derived from the real
  doctree dump). MEDIUM for Pitfall 2's duplicate-label-on-re-attachment claim (A1 in the Assumptions
  Log) — logically sound and structurally unreachable given the locked `set()`-gated design, but not
  independently reproduced as a standalone failing compile this session.

**Research date:** 2026-07-12
**Valid until:** No expiry driver identified (no external API/library version dependency beyond
`typst-py`, already pinned in `pyproject.toml`); revalidate if `typst-py`'s pinned version changes,
or if `translator.py`'s buffer-swap/bracket-wrap conventions are restructured by an intervening
phase.
