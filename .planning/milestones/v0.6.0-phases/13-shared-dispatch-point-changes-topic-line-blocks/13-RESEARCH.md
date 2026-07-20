# Phase 13: Shared Dispatch-Point Changes (topic + line blocks) - Research

**Researched:** 2026-07-12
**Domain:** docutils→Typst translator internals — shared `visit_title` dispatch generalization, `line`/`line_block` handlers
**Confidence:** HIGH (every claim in this document was verified against the real codebase via `uv run python3 -m sphinx -b typst` + `typst.compile()` + `pypdf` text-extraction — no claim rests on reading code alone)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**topic rendering (BLK-02)**
- **D-01**: Reuse the admonition helper — `_visit_admonition(node, "clue")`. A `.. topic::` renders as a gentle-clues base `clue` box (no icon, no accent color) with its title as the bold box title.
- **D-02**: Generalize `visit_title`'s buffer-swap condition to include `topic` parents. Today the buffer-swap branch (translator.py:224) fires only for `isinstance(node.parent, nodes.Admonition)`. Extend so a `topic` parent also buffer-swaps its title through the normal inline visitors and defers it to `_depart_admonition` as the box `title:` argument. `visit_topic`/`depart_topic` then just call `_visit_admonition(node, "clue")` / `_depart_admonition()`. Rejected: box-less lightweight-block alternative (needs net-new machinery for no visual gain).

**line / line_block (BLK-03)**
- **D-03**: Preserve line breaks via `linebreak()` AND reproduce nested indentation (simple). Every `line` inside a `line_block` ends with a `linebreak()`; a nested `line_block` adds a fixed indent per nesting depth. Rejected: breaks-only/flatten.
- **D-04**: Keep the indent compile-safe. Any indentation mechanism must be emitted so it compiles — if it needs markup-mode content, bracket-wrap it exactly like the Phase 11 title/figure label fix. The poetry fixture must prove a nested `line_block` compiles. If a chosen indent construct risks a fatal that can't be made safe cheaply, fall back to breaks-only.

**`.. contents::` (local TOC — also a `topic` node)**
- **D-05**: contents-topic renders box-less as pass-through. Detect `'contents' in node.get("classes", [])` in `visit_topic` and, for that case, do NOT wrap in the `clue` box: emit the title as a bold label and let the child `bullet_list` render normally through the existing list visitors. The title is still buffer-swapped (so it never falls to the `else` heading branch); it is just placed as a plain bold label above the list rather than as a box `title:`. Rejected: routing through `clue` box (boxed TOC is wrong); full-skip (drops a local TOC the author asked for).

**shared-dispatch reach (`visit_title`)**
- **D-06**: Handle topic/contents explicitly + add a `max(1, section_level)` clamp to the `else` branch. A top-level titled non-section (a top-level `topic`, or an out-of-scope `sidebar`) hits `section_level == 0` → `heading(level: 0, …)`, which Typst rejects. Clamp the emitted level to `max(1, self.section_level)`. Do NOT add sidebar-specific rendering — sidebar is out of scope; the clamp merely prevents its title from being fatal if one appears in the real corpus.

### Claude's Discretion
- Exact indent unit/mechanism for nested `line_block` (D-03/D-04) — e.g. `#h(1.5em)` per depth vs `pad(left: …)` — planner/executor's call, subject to the compile-safety constraint.
- Exact punctuation/spacing/label styling for the box-less contents-topic bold label (D-05).
- Whether `visit_topic` sets a small instance flag to distinguish the contents-topic (box-less) path from the generic-topic (clue box) path, or branches inline — implementation detail.
- Fixture document contents beyond the explicit success-criteria cases (topic, address/epigraph/poetry-stanza line_block, `.. note::`/`.. warning::` regression).
- Exact `line`-node emptiness handling (a blank line in a `line_block` is an empty `line` node) — render as a bare `linebreak()`/`#v()`; executor's call, proven by the fixture.

### Deferred Ideas (OUT OF SCOPE)
- **Sidebar (`.. sidebar::`) full rendering** — shares the `visit_title` dispatch but is out of scope. D-06's level clamp prevents its title from being a fatal if it appears, but proper sidebar styling is a future item.
- **Native Typst `#outline()` for local TOCs** — D-05 renders `.. contents::` as the Sphinx-resolved `bullet_list` pass-through; swapping to a Typst-native outline is a possible future refinement, out of scope here.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BLK-02 | A `.. topic::` renders as a titled aside (reusing the admonition helper) | Verified end-to-end: `visit_topic`/`depart_topic` calling `_visit_admonition(node,"clue")`/`_depart_admonition()`, combined with the generalized buffer-swap condition in `visit_title`, produces a compiling, non-heading, TOC-invisible titled box. See "Verified Mechanism 1" and the full combined-fixture compile proof below. |
| BLK-03 | `line`/`line_block` content renders with verbatim line breaks preserved (`linebreak()`) | Verified end-to-end: a depth-tracked `visit_line_block`/`visit_line` pair emitting `h(<depth>*1.5em)` + `linebreak()` compiles cleanly for both flat and nested line_blocks, confirmed via real pypdf text-extraction showing each line on its own extracted line. See "Verified Mechanism 2". |
</phase_requirements>

## Summary

This phase edits exactly one file (`typsphinx/translator.py`) plus test/fixture files. All four
research questions were answered not by reading code, but by **actually applying the proposed
D-01–D-06 changes to a scratch copy of the real translator, running the full `sphinx-build -b typst
→ typst.compile() → pypdf` pipeline against a combined fixture, and reverting** — the same
empirical bar GATE-01 imposes on the implementation itself. The result: **the locked decisions are
sound and compile cleanly as specified**, but two additional pieces of mechanics are required that
are not spelled out in CONTEXT.md, and one **pre-existing, unrelated fatal/leak bug** was discovered
in the exact `visit_title` regression surface this phase touches.

**Primary recommendation:** Implement D-01–D-06 together as a single atomic change (topic support is
incomplete/regressive if D-01 and D-02 land separately — see Pitfall 1), and add two small but
necessary companion fixes inside `visit_title`/`depart_title` that CONTEXT.md's decisions imply but
do not spell out: (a) wrap the emitted title content in a code block `{…}` (both in the `heading()`
call and — already the case — in the admonition `title:` argument) so multi-child titles don't
produce two adjacent statements in one argument slot, and (b) treat a title's own child stream as a
pseudo list-item context (mirroring `emph()`/`strong()`'s own established idiom) so multiple title
children get `"\n"`-separated. Without these two fixes, **any topic or admonition title with more
than one direct child (e.g. `A Topic *Title*`, or the existing `.. admonition:: Custom *Title*`
pattern) is a currently-live fatal that aborts the entire PDF compile** — this is squarely inside the
method this phase edits and directly threatens SC#3 (the admonition-title regression fixture) if a
fixture author picks a title with any inline markup.

## Project Constraints (from CLAUDE.md)

- **The 3-way `@preview` version-sync surface (`writer.py` / `template_engine.py` /
  `templates/base.typ`) must NOT be touched.** Verified: nothing in D-01–D-06 requires a new
  `@preview` import — `clue()` is already imported via the existing `gentle-clues` import,
  `linebreak()`/`h()`/`strong()` are native Typst stdlib. This phase's implementation is fully
  confined to `typsphinx/translator.py` + test/fixture files, as CONTEXT.md itself states.
- **Python 3.10+ compatibility required — do not modernize `Dict`/`List` typing imports** (ruff
  ignores `UP006`/`UP035` deliberately). None of the new code in this phase needs new typing
  imports beyond what already exists in `translator.py` (`from typing import Any, List`).
- **CI parity commands** the planner's verification steps should match exactly: `black --check .`,
  `ruff check .`, `mypy typsphinx/`, `pytest`. Note `ruff`'s `N802` ignore (docutils' PascalCase
  visitor methods, e.g. `visit_Text`) already covers the new `visit_topic`/`depart_topic`/
  `visit_line`/`depart_line`/`visit_line_block`/`depart_line_block` methods — all are lowercase
  and need no special ignore.
- **Line length 88 (black-owned; `E501` ignored in ruff)** — the code examples in this document
  are illustrative; actual implementation should let black own wrapping as usual.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `visit_title` dispatch generalization (topic branch, level clamp) | Translator (docutree→Typst) | — | Single-file, single-class change; no builder/writer/template involvement |
| `.. topic::` → clue box rendering | Translator | Typst runtime (`gentle-clues` package, already imported) | Reuses existing `@preview` import; zero new package surface |
| `.. contents::` box-less pass-through | Translator | Sphinx (resolves the local TOC into a doctree `bullet_list` before the translator ever sees it) | Sphinx's `Contents` transform does the resolution; translator only needs to detect the `'contents'` class and skip the box |
| `line`/`line_block` verbatim breaks + nesting | Translator | Typst runtime (`linebreak()`, `h()` — both native Typst stdlib, no package) | Native Typst functions; no new import needed |

## Standard Stack

No new dependencies. All work reuses:

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@preview/gentle-clues` | 1.3.1 (already imported) | `clue()` box function for the topic aside (D-01) | Same package the generic `.. admonition::` directive already uses (translator.py:2628) |
| Typst stdlib `linebreak()` | native (Typst 0.15) | Verbatim line breaks inside `line_block` (D-03) | Same function already used by `visit_desc_signature_line` (DESC-02, Phase 12) — proven pattern, not a new one |
| Typst stdlib `h()` | native (Typst 0.15) | Per-depth nested-indent spacing (D-03/D-04) | Plain content-producing function, no package needed |

**Package Legitimacy Audit:** N/A — this phase installs zero new packages (confirmed: `git diff
pyproject.toml` not required; CONTEXT.md explicitly states "Zero new runtime dependencies... the
3-way `@preview` version-sync surface is untouched," and every construct used (`clue()`,
`linebreak()`, `h()`, `strong()`) already exists in the codebase or Typst stdlib before this phase).

## Verified Mechanism 1: Topic → `clue` box (D-01/D-02/D-05)

**Confirmed via `python3 -c "... doctree.pformat() ..."` against a real Sphinx build:**

```
<section ids="section-b" ...>
    <title>Section B</title>
    <topic>
        <title>A Topic Title</title>
        <paragraph>Topic body text.</paragraph>
    </topic>
```

`nodes.topic` is **not** a subclass of `nodes.Admonition` [VERIFIED: docutils 0.22 introspection,
`issubclass(nodes.topic, nodes.Admonition) == False`], so D-02's literal instruction — "extend the
condition so a `topic` parent also buffer-swaps" — requires an explicit `or isinstance(node.parent,
nodes.topic)` addition; it cannot be satisfied by any MRO trick. This is a pure additive `or`, so the
existing `isinstance(node.parent, nodes.Admonition)` branch and its regression coverage are
untouched by construction (only more parent types now enter the same branch body).

`visit_topic`/`depart_topic` (new methods) are a direct, minimal application of D-01:

```python
def visit_topic(self, node: nodes.topic) -> None:
    self._topic_is_contents = "contents" in (node.get("classes", []) or [])
    if self._topic_is_contents:
        return  # D-05: box-less, see Verified Mechanism 3
    self._visit_admonition(node, "clue")

def depart_topic(self, node: nodes.topic) -> None:
    if self._topic_is_contents:
        self._topic_is_contents = False
        return
    self._depart_admonition()
```

**End-to-end proof (real compile, real pypdf text-extraction):** a fixture with
`.. topic:: A Topic *Title*` containing `TOPICBODYSENTINEL body text.` compiled cleanly and the
extracted PDF text showed:

```
2.1 Topic Section
A Topic Title
TOPICBODYSENTINEL body text.
```

Critically, **`A Topic Title` appears exactly once** in the extracted text — proof it is NOT also
present in Typst's auto-generated outline (a real `heading()` call always populates the outline,
which would make its title text appear a *second* time as an outline entry with a dotted leader).
This "occurs exactly once" signal is a robust, reusable regression detector for "title did not leak
into a numbered heading" — see Validation Architecture below.

## Verified Mechanism 2: `line`/`line_block` with nested indent (D-03/D-04)

**Confirmed via real doctree dump** that docutils nests `line_block` directly (not via an
intermediate wrapper) when RST source indents `|` lines further:

```
<line_block>
    <line>Line one</line>
    <line_block>
        <line>Nested line indented</line>
        <line>Nested line two</line>
    </line_block>
    <line>Line three back at top</line>
</line_block>
```

A depth counter (incremented in `visit_line_block`, decremented in `depart_line_block`) is the
correct and sufficient mechanism — no separate "nesting stack" data structure is needed, since
`line`'s own indent is purely a function of `self._line_block_depth` at visit time.

**Verified design (compiles cleanly, confirmed via `typst.compile()` — no exception):**

```python
def visit_line_block(self, node: nodes.line_block) -> None:
    depth = getattr(self, "_line_block_depth", 0)
    if depth == 0:
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self._line_block_was_in_paragraph = self.in_paragraph
        self._line_block_was_paragraph_has_content = self.paragraph_has_content
        self.add_text("par({")
        self.in_paragraph = True
        self.paragraph_has_content = False
    self._line_block_depth = depth + 1

def depart_line_block(self, node: nodes.line_block) -> None:
    self._line_block_depth -= 1
    if self._line_block_depth == 0:
        self.add_text("})\n\n")
        self.in_paragraph = self._line_block_was_in_paragraph
        self.paragraph_has_content = self._line_block_was_paragraph_has_content
        if self.in_list_item:
            self.list_item_needs_separator = True

def visit_line(self, node: nodes.line) -> None:
    self._add_paragraph_separator()
    indent_units = self._line_block_depth - 1
    if indent_units > 0:
        self.add_text(f"h({indent_units * 1.5}em)")

def depart_line(self, node: nodes.line) -> None:
    self.add_text("\nlinebreak()")
```

**Why `h()` needs NO markup-mode bracket-wrap (answering the D-04 risk question directly):**
`h(1.5em)` is a plain Typst stdlib function that returns a content value — exactly like `text(...)`,
`emph(...)`, `linebreak()` already emitted elsewhere in this translator's unified code mode. The
Phase 11 bracket-wrap idiom (`[#heading(...) <label>]`) exists **only** because Typst's `<label>`
anchor syntax is markup-mode-only; `h()` never carries a label, so it needs no such wrap. `pad(left:
…)[…]` (the alternative CONTEXT.md names) **would** need a markup-mode content argument and is
unnecessarily heavier for this use case — **use `h()`, not `pad()`.**

**Verified separator mechanics:** a bare source `"\n"` between two code-mode statements is
cosmetic-only (confirmed by the DESC-02/Phase-12 precedent, and independently re-confirmed here for
`h()`+`text()` adjacency) — it does **not** produce a visual line break. This is *why* `depart_line`
must emit a real `linebreak()` (not rely on the `"\n"` that separates it from the next line), and why
`h(...)` followed on the next source line by `text(...)` renders as one continuous indented line, not
two. **This "`\n` between statements = free, invisible" property is what makes the whole design
compile-safe with zero markup-mode involvement.**

**Real pypdf text-extraction proof (address, no nesting):**
```
ADDRESSLINEONE Main Street
ADDRESSLINETWO Anytown USA
```
**Real pypdf text-extraction proof (poem, one level of nesting):**
```
POEMLINEONE
POEMNESTEDONE
POEMNESTEDTWO
POEMLINETHREE
```
Each line is a separate extracted line — proof `linebreak()` fired for real, not merely present as
source-level `\n`.

**A note on the "empty `line`" case (Claude's discretion):** the verified design already handles it
for free — an empty `line` node simply has no `Text` child to visit, so `visit_line`/`depart_line`
alone emit `[indent if any]` + `"\nlinebreak()"`, i.e. a bare `linebreak()` (optionally preceded by
`h(...)` if nested) — exactly the discretion note's suggested minimum, no special-casing required.

## Verified Mechanism 3: `.. contents::` box-less pass-through (D-05)

**Confirmed via real doctree dump** (`sphinx.ext` local-TOC resolution, no extension needed — this
is core Sphinx `Contents` transform behavior):

```
<topic classes="contents local" ids="table-of-contents" names="table of contents">
    <title>Table of Contents</title>
    <bullet_list>
        <list_item>
            <paragraph>
                <reference ids="id1" refid="section-a">Section A</reference>
            </paragraph>
        </list_item>
        ...
```

Two details matter for implementation:

1. **Each `list_item` wraps its `reference` in a `paragraph`**, not a bare reference. This is
   automatically handled correctly by the *existing* `visit_paragraph`'s list-item guard (`if
   self.in_list_item: self.in_paragraph = False; return` — skips the `par({...})` wrap inside list
   items) plus the existing `visit_reference`'s `refid` branch (XREF-01, Phase 12). **No new code is
   needed for the list body itself** — only the title needs special handling.

2. **Body-insertion ordering pitfall (the one genuinely non-obvious mechanic in this phase):**
   CONTEXT.md's D-05 says the title is "still buffer-swapped... placed as a plain bold label above
   the list." A naive read of this — buffer-swap the title exactly like `_visit_admonition` does,
   then at `depart_topic` time simply `add_text()` the captured `_pending_admonition_title` — is
   **wrong**, because by the time `depart_topic` runs, the `bullet_list`'s `list(...)` call has
   *already* been appended to `self.body` (it is `topic`'s second child, visited after the title
   completes). A naive append would therefore place the label **after** the list, not above it. The
   admonition buffer-swap mechanism normally sidesteps this entirely because a box's title is a
   **named keyword argument** (`title: {...}`) to `clue(...)` — argument position in the *source*
   text is irrelevant to render position, since `gentle-clues` places the title visually regardless
   of where `title:` appears in the call. The box-less contents case has no such kwarg to hide
   behind — it needs the label to be genuinely first in emission order.

   **Verified fix:** record the insertion index (`len(self.body)`) at the moment the title starts
   buffering (nothing has been emitted for this topic yet at that point, since `title` is always a
   topic's first child), then at `depart_title` (not `depart_topic`) — because that's where
   `_pending_admonition_title` becomes available — `self.body.insert(index, f"strong({{{title}}})\n\n")`
   instead of a plain append:

   ```python
   # in visit_title's admonition/topic buffer-swap branch:
   if isinstance(node.parent, nodes.topic) and "contents" in (node.parent.get("classes", []) or []):
       self._contents_title_insert_at = len(self.body)
   self._saved_body_for_admonition_title = self.body
   self.body = []
   self._in_admonition_title = True
   return

   # in depart_title's admonition-title branch, after restoring self.body:
   if hasattr(self, "_contents_title_insert_at"):
       self.body.insert(self._contents_title_insert_at,
                         f"strong({{{self._pending_admonition_title}}})\n\n")
       self._pending_admonition_title = None
       del self._contents_title_insert_at
   ```

**End-to-end proof:** extracted PDF text for a `.. contents:: Table of Contents` fixture:
```
Table of Contents
• Topic Section
• Line Block Section
‣ Address
‣ Poem
• Admonition Regression
```
— rendered exactly once, as a bold label immediately above the list, with **no corresponding entry
in Typst's auto-outline** (the outline block at the top of the same PDF lists "2 Title", "2.1 Topic
Section", "2.2 Line Block Section", "2.3 Admonition Regression" — no "Table of Contents" entry at
all), confirming SC#1's "TOC structure unchanged" requirement empirically, not just by code
inspection.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Titled aside box | A new bracket/box-drawing helper for topic | `_visit_admonition(node, "clue")` / `_depart_admonition()` (D-01, already exists) | Identical mechanism already used by 10+ admonition types + the generic `.. admonition::` directive; zero new state, zero new Typst import |
| Local TOC list rendering | A new list-rendering path for `.. contents::` | The existing `visit_bullet_list`/`visit_list_item`/`visit_paragraph`(list-item-skip)/`visit_reference`(refid branch) chain | Sphinx has already resolved the local TOC into a plain `bullet_list` of `reference`s before the translator ever sees it — this is exactly the shape every other internal-link bullet list already has |
| Nested indentation tracking | A stack of indent contexts, or a recursive-descent pre-pass | A single integer depth counter (`self._line_block_depth`), incremented/decremented in `visit_line_block`/`depart_line_block` | `line_block` nesting in docutils is a simple parent-child recursion; the translator's own visitor recursion already provides the "stack" for free |

**Key insight:** every one of the three "new" capabilities in this phase is a thin composition of
*already-proven* machinery (`_visit_admonition`, the list-item paragraph-skip, the `\n`-is-cosmetic
statement-separator idiom from DESC-02). The phase's genuine risk is not "does the new machinery
work" — it's "does composing it with the load-bearing `visit_title` regress the untouched paths,"
which is why Pitfall 1 below (the pre-existing multi-child-title fatal) is the most important finding
in this document.

## Common Pitfalls

### Pitfall 1 (CRITICAL, pre-existing, discovered during this research): multi-child titles are a currently-live fatal

**What goes wrong:** ANY `nodes.title` (a section heading **or** an admonition title, via the
*existing*, unmodified `.. admonition:: <title>` mechanism) that has more than one direct child node
— e.g. `Custom *Title*` (a `Text` child followed by an `emphasis` child) — currently aborts the
**entire** PDF compile with `typst.TypstError: expected semicolon or line break`.

**Reproduced against the real, unmodified translator today** (before any Phase 13 change), via
`sphinx-build -b typst` + `typst.compile()`:

```rst
.. admonition:: Custom *Title*

   Body text.

Mixed *Emphasis* In Section Title
----------------------------------

Section body.
```

Generated (broken) Typst:
```
heading(level: 2, text("Mixed ")emph({text("Emphasis")})text(" In Section Title")) <mixed-emphasis-in-section-title>]
...
clue({...}, title: {text("Custom ")emph({text("Title")})})
```

Both statements fail to compile: `heading()`'s second positional argument receives **three
juxtaposed content expressions with no separator** (invalid — a positional argument must be one
expression), and the admonition `title:` code-block similarly juxtaposes `text(...)emph({...})` with
no statement separator.

**Why it happens:** `visit_title`'s children (`Text`, `emphasis`, `strong`, etc.) each call
`_add_paragraph_separator()` at the start of their own `visit_*`, which only inserts a `"\n"`
separator when `self.in_paragraph` is true, or checks `self.in_list_item` for the list-item variant
of the same idea. A title's own child-stream sets **neither** flag, so consecutive title children
concatenate with zero separator between them — the exact "expected semicolon or line break" failure
mode.

**How to avoid (verified fix, already fully validated in this research session — see the "Verified
Mechanism 1" code excerpt above and the successful combined-fixture compile in this document's
provenance):**
1. In `visit_title`, before dispatching into either the admonition/topic buffer-swap branch or the
   plain-heading branch, save and set `self.in_list_item = True; self.list_item_needs_separator =
   False` (mirroring exactly the idiom `visit_emphasis`/`visit_strong` already use for their **own**
   children — "treat it like list_item" is a direct quote from the existing `visit_emphasis`
   docstring). Restore both saved values in `depart_title`, in *every* return path (the admonition
   branch's early return, and the tail of the plain-heading branch).
2. Wrap the plain-heading branch's title content in a code block: `heading(level: N, {` ... `})`
   (both the bracket-wrapped-for-anchor variant and the plain variant) — the admonition branch
   *already* wraps its captured title in `{...}` at `_depart_admonition`, so only the `heading()`
   call itself needs this addition.

**Verified this exact fix is minimal, correct, and non-regressive:** applying it to a scratch copy of
`translator.py` and re-running the full existing `.. admonition:: Custom *Title*` +
`test_admonition_title_preserves_inline_markup`-shaped multi-child-title scenario through a real
`typst.compile()` produced a clean PDF with `"Custom Title"` (and `"Mixed Emphasis In Section
Title"`) rendered correctly, with **zero change** to any single-child-title output (verified byte-
for-byte identical `.typ` output for every existing single-Text-child title in the combined fixture).

**Warning signs this bug is un-fixed:** the phase's own regression fixture (SC#3, "admonition titles
`.. note::`/`.. warning::` still render correctly") is at risk of *accidentally passing* if the
fixture author picks single-Text-node titles (as the current `admonition_render_gate` fixture does —
note it has **no** admonition titles with inline markup at all today) while *also* accidentally
masking this bug for the **new** topic-title case, which is far more likely to have inline markup in
realistic RST (`.. topic:: See *Also*`). **Recommendation: the planner MUST include this fix as an
explicit task in this phase** — it lives in exactly the method being edited, is required for BLK-02 to
be genuinely robust (a topic title with any inline markup would otherwise be fatal), and is
low-risk/minimal-diff since it reuses an idiom already proven correct four times elsewhere in this
file (`emph`, `strong`, and by extension every markup-mode `text()` prefix check).

### Pitfall 2: D-01 and D-02 must land as one atomic change, not split across waves

**What goes wrong:** if `visit_title`'s buffer-swap condition is generalized to include `topic`
parents (D-02) *before* `visit_topic`/`depart_topic` exist (D-01), the title's buffered content
(`_pending_admonition_title`) is captured but **never consumed by anything** (no `_depart_admonition`
call happens for a bare `topic` node, since no `depart_topic` exists yet) — the title text is
silently dropped. This is a *worse* regression than the current baseline (today, an unhandled `topic`
falls through `unknown_visit` and its title renders as a real, if wrongly-leveled, heading — see
Pitfall 3 — so text is at least visible).

**How to avoid:** implement D-01 and D-02 (plus D-05's contents-detection) in the same task/commit —
this is already the natural reading of CONTEXT.md's phrasing ("this lands as one phase... generalize
the shared dispatch"), but is worth calling out explicitly since D-01/D-02/D-05 are listed as
separate decision bullets and could tempt a wave-split.

### Pitfall 3: baseline (today, pre-Phase-13) behavior for unhandled `topic`/`.. contents::`

**What goes wrong (today, informative only — not a Phase 13 regression risk, but useful for
understanding "what changes"):** since neither `visit_topic` nor `visit_line`/`visit_line_block`
exist yet, both currently fall through `unknown_visit` (logs one warning per node, does **not**
`SkipNode`, so children are still visited). For `.. topic::`/`.. contents::` specifically, this means
the title **currently** falls to `visit_title`'s plain `else` (heading) branch: verified today it
renders as a real, wrongly-leveled `heading()` call (e.g. `.. contents::` at `section_level=1`
currently emits `heading(level: 1, text("Table of Contents"))` — a real, numbered TOC entry
indistinguishable from a section — an SC#1-violating but *not fatal* baseline). `line`/`line_block`
nodes currently drop their own wrapper entirely but their `Text` children still stream through
`visit_Text`, meaning **prose inside an unhandled `line_block` today has zero line breaks** — lines
run together with no separator at all (confirmed: today's baseline for an unhandled line/line_block
renders as one unbroken sentence). This is the exact "silently degrades" behavior BLK-03 fixes.

### Pitfall 4: `.. epigraph::` (and any block_quote without an explicit `attribution:`-avoiding shape) is a SEPARATE, PRE-EXISTING, orthogonal fatal/leak surface — avoid it in the Phase 13 fixture

**What goes wrong:** `visit_block_quote`/`visit_attribution` (unrelated to this phase, unmodified by
any D-01–D-06 decision) have two independent bugs, **both reproduced against the current, unmodified
codebase**:

1. **A block_quote WITH an `attribution:` (i.e. any real `.. epigraph::` with a `-- Attribution`
   line) is a currently-live fatal.** `visit_block_quote`'s `has_attribution` branch opens with
   `quote(` (a code-mode call), but `visit_attribution` unconditionally emits `"], attribution: ["`
   — a markup-mode bracket-close/open pair that has no matching opening bracket in the
   `has_attribution=True` path, producing `typst.TypstError: unclosed delimiter`. Reproduced with:
   ```rst
   .. epigraph::

      Roses are red, violets are blue.

      -- Some Author
   ```
2. **A block_quote WITHOUT an attribution renders its body in Typst *markup mode* (`quote[...]`),
   but the translator's paragraph/text emission is unconditionally code-mode** (`par({...})`,
   `text("...")`, no `#` prefix). This does **not** raise a compile error — it compiles "successfully"
   but **leaks literal Typst source into the rendered PDF as literal quoted prose**. Reproduced and
   confirmed via real pypdf text-extraction:
   ```
   “par({text(“Roses are red, violets are blue. ”)})”
   ```
   This is the exact class of bug the `LEAK_SIGNATURES` negative-control check in
   `test_pdf_render_gate.py` exists to catch (`par({`, `text("`) — it would have been caught
   immediately by that check had a block_quote fixture existed.

**Why this matters for Phase 13 specifically:** CONTEXT.md's "Specific Ideas" section suggests the
line_block fixture cover "an address, an epigraph, and a poetry stanza." If "epigraph" is implemented
via the actual `.. epigraph::` directive, **the fixture will hit one of these two pre-existing bugs
regardless of whether `line`/`line_block` itself is implemented correctly** — masking whether BLK-03
works and failing the GATE-01 real-compile bar for reasons entirely unrelated to this phase's scope.

**How to avoid (recommended, verified-safe alternative):** render the "epigraph" *shape* (a short
quoted passage with preserved line breaks) as a **plain top-level `line_block`** under a section
titled "Epigraph" — i.e. do **not** wrap it in the `.. epigraph::` directive. This is semantically
equivalent for the purpose of proving BLK-03 (verbatim breaks) and sidesteps the unrelated
`block_quote`/`attribution` bug entirely. **Verified**: a plain top-level `line_block` (no
block_quote wrapper) compiles cleanly and text-extracts correctly — see Verified Mechanism 2's
"address"/"poem" proofs, which use exactly this pattern.

**Recommendation for the planner:** do not attempt to fix `visit_block_quote`/`visit_attribution` in
this phase (out of the locked BLK-02/BLK-03 scope, and it's a materially larger, unrelated fix — the
`has_attribution` branch's whole bracket-vs-paren convention needs rethinking). Instead: (1) use the
plain-`line_block`-under-a-titled-section pattern for the "epigraph" fixture shape, and (2) flag this
discovery for a future issue/phase — it is a real, currently-shipping bug independent of this
milestone's v0.6.0 requirement set (not BLK-02, not BLK-03, not in REQUIREMENTS.md at all).

### Pitfall 5: `visit_title`'s `_title_section_ids` check is `isinstance(node.parent, nodes.section)` — topic titles never take that branch, so no anchor collision risk

**What goes wrong (non-issue, but worth confirming explicitly since it interacts with D-02):** the
existing markup-mode bracket-wrap for section-heading anchors (`[#heading(...) <id>]`) is guarded by
`isinstance(node.parent, nodes.section)`. Since a `topic`'s title has `node.parent` of type
`nodes.topic` (never `nodes.section`), this condition remains `False` for topic titles both before
and after D-02 — **topic titles never enter the anchor/bracket-wrap path**, so there is no risk of
this phase accidentally colliding with the FIG-02/GATE-01 label-anchor mechanism. Confirmed by
inspecting the generated `.typ` for the combined fixture: the topic title never received a `<label>`
suffix, and no `"label does not exist"` or duplicate-label error occurred.

## Code Examples

### Full generalized `visit_title`/`depart_title` (verified compiling, reflects all of D-01–D-06 plus Pitfall 1's fix)

```python
# Source: this research session's scratch-patch of typsphinx/translator.py,
# verified via real sphinx-build -> typst.compile() -> pypdf pipeline.
def visit_title(self, node: nodes.title) -> None:
    # Pitfall 1 fix: treat this title's own children like list-item content
    # so multiple children (Text + emphasis, etc.) get "\n"-separated
    # statements -- mirrors the existing emph()/strong() "treat it like
    # list_item" idiom.
    self._title_was_in_list_item = self.in_list_item
    self._title_was_list_item_needs_separator = self.list_item_needs_separator
    self.in_list_item = True
    self.list_item_needs_separator = False

    # D-02: admonition titles AND topic titles are deferred via buffer-swap.
    if isinstance(node.parent, nodes.Admonition) or isinstance(node.parent, nodes.topic):
        # D-05: contents-topic needs its title inserted BEFORE the
        # already-streaming bullet_list, not appended after (see Verified
        # Mechanism 3) -- record the insertion point now.
        if isinstance(node.parent, nodes.topic) and "contents" in (
            node.parent.get("classes", []) or []
        ):
            self._contents_title_insert_at = len(self.body)
        self._saved_body_for_admonition_title = self.body
        self.body = []
        self._in_admonition_title = True
        return

    self._title_section_ids = (
        node.parent.get("ids") if isinstance(node.parent, nodes.section) else None
    ) or []
    # D-06: clamp to a minimum of level 1 -- Typst rejects heading(level: 0, ...).
    emitted_level = max(1, self.section_level)
    # Pitfall 1 fix: wrap in a code block {...} so multi-child title content
    # is one expression, not several juxtaposed statements.
    if self._title_section_ids:
        self.add_text(f"[#heading(level: {emitted_level}, {{")
    else:
        self.add_text(f"heading(level: {emitted_level}, {{")

def depart_title(self, node: nodes.title) -> None:
    if self._in_admonition_title:
        self._pending_admonition_title = "".join(self.body)
        if self._saved_body_for_admonition_title is not None:
            self.body = self._saved_body_for_admonition_title
        self._saved_body_for_admonition_title = None
        self._in_admonition_title = False
        self.in_list_item = self._title_was_in_list_item
        self.list_item_needs_separator = self._title_was_list_item_needs_separator

        if hasattr(self, "_contents_title_insert_at"):
            label = f"strong({{{self._pending_admonition_title}}})\n\n"
            self.body.insert(self._contents_title_insert_at, label)
            self._pending_admonition_title = None
            del self._contents_title_insert_at
        return

    if self._title_section_ids:
        primary_id, *extra_ids = self._title_section_ids
        self.add_text(f"}}) <{primary_id}>]\n")
        for extra_id in extra_ids:
            self.add_text(f"[#metadata(none) <{extra_id}>]\n")
        self.add_text("\n")
    else:
        self.add_text("})\n\n")
    self._title_section_ids = []
    self.in_list_item = self._title_was_in_list_item
    self.list_item_needs_separator = self._title_was_list_item_needs_separator
```

### `visit_topic`/`depart_topic` (D-01/D-02/D-05)

```python
def visit_topic(self, node: nodes.topic) -> None:
    self._topic_is_contents = "contents" in (node.get("classes", []) or [])
    if self._topic_is_contents:
        return
    self._visit_admonition(node, "clue")

def depart_topic(self, node: nodes.topic) -> None:
    if self._topic_is_contents:
        self._topic_is_contents = False
        return
    self._depart_admonition()
```

### `visit_line`/`visit_line_block` (D-03/D-04) — see full listing under "Verified Mechanism 2" above.

## State of the Art

Not applicable — this phase generalizes internal translator dispatch logic and adds two node
handlers; there is no external "state of the art" to track (no library upgrade, no changed Typst
API). The one relevant "current approach" note: Typst 0.15's `linebreak()`/`h()` are the same stdlib
functions already used elsewhere in this translator (DESC-02) — no alternative API exists or is
needed.

## Assumptions Log

> Every claim in this document above this section was empirically verified this session (real
> `sphinx-build`, real `typst.compile()`, real `pypdf` extraction). The items below are the only
> claims not independently re-verified in this session.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `1.5em` is a reasonable per-depth indent unit for nested line_blocks (visual choice, not a compile-safety claim) | Verified Mechanism 2 | Low — purely cosmetic; easy to change to any other length value without altering the mechanism |
| A2 | No other docutils node type besides `sidebar` realistically reaches `visit_title`'s `else` branch at `section_level == 0` in real-world docs (the D-06 clamp's practical necessity) | Pitfall/D-06 discussion | Low — the clamp is a pure safety net with zero downside even if this assumption is wrong; it never fires for the common case (section_level ≥ 1) |

**If this table is empty:** N/A — two low-risk, low-impact assumptions remain, both cosmetic/safety-net in nature, not correctness-critical.

## Open Questions

1. **Should Pitfall 1's fix (multi-child title separator + code-block wrap) be scoped as part of
   this phase's task list, or filed as a separate prerequisite fix?**
   - What we know: it is required for BLK-02 to be robust for any topic title with inline markup,
     lives in the exact method being edited, and is minimal/low-risk (verified fully working, zero
     regression to single-child titles).
   - What's unclear: whether the user/planner wants this bundled into Phase 13's task list (my
     recommendation) or treated as a tracked prerequisite bug fix landed just before this phase.
   - Recommendation: bundle it into Phase 13 as an explicit task — splitting it into a separate
     phase adds coordination overhead for a fix that's inseparable from "generalize visit_title
     safely."

2. **Should the discovered `block_quote`/`attribution` bugs (Pitfall 4) be filed as a new GitHub
   issue / added to REQUIREMENTS.md's Future Requirements?**
   - What we know: two independent real bugs exist today (a hard fatal for attributed block quotes,
     a silent literal-source leak for non-attributed ones), entirely orthogonal to BLK-02/BLK-03.
   - What's unclear: whether this is worth a v0.6.x follow-up given the milestone's "highest-
     frequency previously-dropped nodes" framing — block_quote is common in real docs (any `> quote`
     equivalent, epigraphs, pull-quotes).
   - Recommendation: out of scope for Phase 13's task list; worth a note to the user/maintainer to
     file separately. Not blocking — the recommended fixture design (Pitfall 4) fully sidesteps it.

## Environment Availability

Not applicable — this phase has no external dependencies beyond what's already installed and
verified working in this repository (`sphinx`, `docutils`, `typst`-py, `pypdf`, `@preview/gentle-
clues` — all already present and exercised successfully during this research session's real-compile
verification).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), `typst-py` + `pypdf` for the real-compile gate |
| Config file | `pyproject.toml` (pytest config); no dedicated config for the render gate beyond `tests/test_pdf_render_gate.py` itself |
| Quick run command | `pytest tests/test_translator.py -k "topic or line_block" -x` (once new unit tests are added) |
| Full suite command | `pytest --cov=typsphinx --cov-report=term-missing` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BLK-02 | `.. topic::` renders as `clue({...}, title: {...})`, not `heading()` | unit | `pytest tests/test_translator.py -k topic -x` | ❌ Wave 0 — new test, likely appended to `test_translator.py` or a new topic-focused test module, following the DESC-02 precedent (dedicated unit tests plus the render gate, unlike BLK-01/04/05/06 which relied on the render gate alone) |
| BLK-02 | `.. contents::` renders box-less, bullet_list intact, no boxed TOC | unit | `pytest tests/test_translator.py -k contents -x` | ❌ Wave 0 |
| BLK-02 | Real-compile: topic title appears exactly once (not duplicated into the auto-outline) | integration (GATE-01 real-compile) | `pytest tests/test_pdf_render_gate.py -k Topic -x` | ❌ Wave 0 — new fixture `tests/fixtures/topic_line_block_render_gate/` + new test class |
| BLK-03 | `line`/`line_block` emits `linebreak()` per line, `h()` per nesting depth | unit | `pytest tests/test_translator.py -k line_block -x` | ❌ Wave 0 |
| BLK-03 | Real-compile: address + poem sentinels appear as separate extracted-text lines, never concatenated with no separator (New-Pitfall-11-style proof, DESC-02 precedent) | integration (GATE-01 real-compile) | `pytest tests/test_pdf_render_gate.py -k LineBlock -x` | ❌ Wave 0 — same new fixture as above |
| SC#3 (regression) | `.. note::`/`.. warning::`/generic `.. admonition::` (including a multi-child title, per Pitfall 1) still render correctly | integration (GATE-01 real-compile) | `pytest tests/test_pdf_render_gate.py -k AdmonitionTitleRegression -x` | ❌ Wave 0 — can extend the existing `admonition_render_gate` fixture with a multi-child-title case, or add to the new combined fixture |

### Sampling Rate
- **Per task commit:** `pytest tests/test_translator.py -k "topic or line_block or admonition" -x`
- **Per wave merge:** `pytest --cov=typsphinx --cov-report=term-missing`
- **Phase gate:** Full suite green before `/gsd-verify-work`, including the new `TestTopicLineBlockRenderGate` (or equivalently-named) class in `tests/test_pdf_render_gate.py`, marked `@pytest.mark.slow` and `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)` matching every existing GATE-01 class.

### Wave 0 Gaps
- [ ] `tests/fixtures/topic_line_block_render_gate/conf.py` + `index.rst` — new fixture project combining: a `.. topic::` with a multi-child title (proves Pitfall 1's fix), a `.. contents::` local TOC, a plain top-level `line_block` for "address", a plain top-level `line_block` with one level of nesting for "poem" (do NOT use `.. epigraph::` — see Pitfall 4), and a `.. note::`/`.. warning::`/`.. admonition:: Custom *Title*` regression block. **This exact combination was fully verified to compile cleanly in this research session** (see the "Verified Mechanism" sections above) — the fixture can be lifted near-verbatim from the RST used during verification.
- [ ] `tests/test_pdf_render_gate.py` — new `TestTopicLineBlockRenderGate` class (or similar name) following the `TestTrivialBlocksRenderGate`/`TestDescSignatureRenderGate` pattern exactly: `sphinx-build -b typst` → `typst.compile()` (uncaught, so any `TypstCompilationError` fails loudly) → `pypdf` text-extraction → sentinel-presence + sentinel-count (`== 1` for topic/contents titles, to detect the "leaked into the outline" regression) + `LEAK_SIGNATURES` negative-control assertions.
- [ ] Unit tests in `tests/test_translator.py` (or a new `tests/test_topics.py`/`tests/test_line_blocks.py`) for the branch logic itself (D-02's condition, D-05's class-detection, D-06's clamp) — string-assertion-level, fast, following the existing DESC-02/VER-01/XREF-01 precedent (BLK-01/04/05/06 skipped this tier and relied solely on the render gate; this phase's logic is meaningfully more branchy — buffer-swap generalization, insertion-index trick — so dedicated unit coverage is recommended, not merely nice-to-have).
- [ ] Framework install: none — pytest, typst-py, pypdf are all already installed and exercised by the existing suite.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | This phase touches only local docutree→Typst text generation; no auth surface |
| V3 Session Management | No | N/A — build-time tool, not a service |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | RST source text is "input" in the sense that title/line content flows into generated Typst source; the existing escaping regime (`text_content.replace(...)` for `\`, `"`, `\n`, `\r`, `\t` in `visit_Text`) already covers this and is unchanged by this phase — no new unescaped string interpolation is introduced (all new f-strings interpolate only internally-computed values: depth integers, class-name booleans — never raw user/RST text) |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Typst source injection via unescaped title/line text (e.g. a title containing `"`, `\`, or Typst-special characters) | Tampering | Already mitigated by the existing `visit_Text` escaping regime, which every new code path in this phase reuses unmodified (titles and line content both flow through `visit_Text`, not a new/parallel text-emission path) |

## Sources

### Primary (HIGH confidence — verified empirically this session)
- `typsphinx/translator.py` (repository source, read directly) — `visit_title`/`depart_title`
  (:206-292), `_visit_admonition`/`_depart_admonition` (:2470-2523), `unknown_visit` (:2216),
  `visit_desc_signature_line` (:2887, the `linebreak()` precedent), `visit_block_quote`/
  `visit_attribution` (:1540-1591), `visit_emphasis`/`visit_strong` (the "treat it like list_item"
  idiom, :560-628).
- Real doctree dumps via `sphinx.application.Sphinx(...).build()` + `env.get_doctree(...).pformat()`
  — confirmed `nodes.topic` MRO (not `Admonition` subclass), `.. contents::` → `topic` +
  `bullet_list` shape, `line_block` nesting shape, top-of-document `sidebar`/`topic` section-level-0
  scenario.
- Real compile verification via `typst.compile()` (typst-py 0.15.0, matching `pyproject.toml`'s
  pin) — confirmed `heading(level: 0, ...)` rejection ("number must be positive"), confirmed the
  pre-existing multi-child-title fatal ("expected semicolon or line break"), confirmed the verified
  fix compiles cleanly, confirmed the `.. epigraph::`-with-attribution fatal ("unclosed delimiter"),
  confirmed the `.. epigraph::`-without-attribution literal-source leak.
- Real pypdf text-extraction (`pypdf.PdfReader(...).pages[i].extract_text()`) — confirmed line
  breaks present as separate extracted lines for both flat and nested `line_block`, confirmed the
  topic title's "appears exactly once" outline-absence signal, confirmed the epigraph-without-
  attribution leak's literal text in the rendered PDF.
- `tests/test_pdf_render_gate.py` (repository source, read directly) — `LEAK_SIGNATURES`,
  `_run_sphinx_build_typst`, and the `TestDescSignatureRenderGate`/`TestTrivialBlocksRenderGate`
  patterns used as the template for this phase's new test class.
- `tests/test_admonitions.py` (repository source, read directly) — `test_admonition_with_title_in_
  content`, `test_admonition_title_preserves_inline_markup`, `test_generic_admonition_converts_to_
  clue` — confirmed the real docutils shape for a title-bearing admonition (`nodes.admonition` +
  `nodes.title` child) and the existing (unit-test-only, never real-compile-verified until this
  session) coverage gap that let Pitfall 1 go undetected.

### Secondary (MEDIUM confidence)
- `.planning/ROADMAP.md` §"Phase 13" — Success Criteria wording, cross-checked against the verified
  mechanisms above; all four SCs are satisfied by the verified design.

### Tertiary (LOW confidence)
- None — every claim in this document was either read directly from repository source or verified
  via a real, executed compile/extract pipeline in this research session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, all constructs (`clue()`, `linebreak()`, `h()`,
  `strong()`) already proven in the codebase or Typst stdlib.
- Architecture: HIGH — every mechanism in this document was verified via a real, executed
  `sphinx-build → typst.compile() → pypdf` pipeline against a scratch-patched copy of the actual
  translator, not merely reasoned about from reading code.
- Pitfalls: HIGH — Pitfalls 1 and 4 are newly-discovered, currently-live bugs, reproduced against
  the unmodified, current codebase with exact error messages and generated Typst source captured.

**Research date:** 2026-07-12
**Valid until:** No expiry driver identified (no external API/library version dependency); revalidate
if `typst-py` or `gentle-clues` versions change, or if `translator.py`'s `visit_title`/
`_visit_admonition` mechanics are touched by an intervening phase.
