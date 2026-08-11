# Phase 43: Table State Correctness — Nested Tables + Empty-Title Anchors - Research

**Researched:** 2026-08-04
**Domain:** Sphinx/docutils doctree → Typst markup translation (`typsphinx/translator.py` node-visitor
state management, node-handler completeness)
**Confidence:** HIGH — every claim below is either a direct `Read` of `typsphinx/translator.py` this
session (with line numbers and verbatim quotes), a command executed this session (`grep`,
`sphinx-build`, `typst.compile()`), or a citation of an existing in-repo artifact (`CONTEXT.md`, the
three source todos, `42-GATE-EVIDENCE-05.md`). No external library research was needed or performed:
this phase adds zero new dependencies and touches exactly one file.

## Summary

This phase closes two independent state-management defects and one node-handler gap, all living in
`typsphinx/translator.py`'s table/figure/anchor code, plus a stale docstring next to the same code.

**TBL-04 and FIG-01 are the same defect shape, twice.** `visit_table`/`depart_table` and
`visit_figure`/`depart_figure` each drive a handful of plain instance-attribute scalars
(`table_cells`, `table_colcount`, `table_colwidths`, `table_caption`, `table_cell_content`,
`in_thead`, `current_morecols`/`current_morerows` for tables; `figure_content`, `figure_caption`,
`_figure_block_width` for figures) that `visit_*` resets unconditionally on entry and `depart_*` tears
down unconditionally on exit. Nothing distinguishes "the container currently being filled" from "an
enclosing container that is still open," so when a table nests inside a table cell, or a figure nests
inside another figure's `legend`, the inner container's departure clobbers the outer's in-progress
state. **This research found the reachable scalar set is larger than the phase's own source todo
enumerated**: `self.in_thead` and `self.current_morecols`/`self.current_morerows` share the identical
clobber shape and are not on the todo's "measure these 5 things first" list — see Pitfall 1 below,
verified with a fresh probe this session.

**The two defects differ in one structural way that matters for the fix.** `depart_table` already
bypasses `add_text` and appends its rendered markup directly to `self.body` (a deliberate,
commented-on design choice — see Pitfall 2), so a nested table's fix must *also* solve "where does
the rendered markup go" (the outer cell's buffer, not `self.body`). `depart_figure`, by contrast,
already routes every emission through `self.add_text`, so nested-figure *content* already lands in
the right place once the state scalars are fixed — the only structural gap is that Typst's `figure()`
accepts exactly one positional body argument, and nothing today combines the image with any following
`legend` content into that one argument. **This session verified, with a real `typst.compile()` run,
that today's code produces a hard `TypstError` compile fatal for ANY multi-paragraph figure caption —
not merely a silently-dropped outer caption** (see Pitfall 4). A minimal fix (the existing
`{...}` code-block-join idiom this codebase already uses for headings and table cells) was verified to
compile correctly with both figures numbered and captioned.

TBL-05's fix is narrow and already fully decided by `CONTEXT.md` D-05/D-06/D-07: id anchoring in
`depart_table` must stop depending on the same truthiness check that gates figure-wrapping. QUA-01 is
a docstring-only rewrite naming both real callers — verified this session (`grep`) at 21 total
`_emit_id_anchors` call sites, 2 with `skip_ids` (line 2518, line 3370), matching the todo exactly.

**Primary recommendation:** implement TBL-04/FIG-01 as a **snapshot save/restore around nesting**
(push a full-state snapshot in `visit_table`/`visit_figure` only when already inside one, restore it
in `depart_table`/`depart_figure`) rather than converting every scalar to a `list[TableState]` stack
with per-consumer rewrites — it keeps the Phase 25 `table_cell_content` lifetime invariant and all ten
`self.in_table`/`self.in_figure` boolean-read consumers untouched, and it generalizes to N-deep
nesting by construction (push/pop once per level, no special-casing per depth). Build the snapshot
unit around the now-corrected, larger scalar set (see Discretion section below), not the original
5-item list.

## Architectural Responsibility Map

This project has no browser/API/DB tiers; the relevant "tiers" are the three stages of the actual
data-flow pipeline (`CLAUDE.md` Architecture section, verified this session against the file
structure):

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Nested-container state tracking (TBL-04, FIG-01's state half) | Translator (`translator.py` visitor state) | — | Purely an in-process Python object's instance-attribute lifecycle; no other tier participates |
| Routing rendered markup to the correct buffer (cell vs. document body) | Translator (`add_text` dispatch + `depart_table`/`depart_figure`) | — | `add_text` is the single dispatch point every nesting decision flows through (per `CONTEXT.md` Integration Points) |
| `legend` node markup composition (FIG-01's routing half) | Translator (new `visit_legend`/`depart_legend`) | Typst compiler (accepts/rejects the composed expression) | The translator decides what Typst syntax to emit; the Typst compiler is the semantic backstop that turns a wrong composition into a real, catchable `TypstError` |
| Id anchor emission independent of caption truthiness (TBL-05) | Translator (`depart_table`) | Typst compiler (label-resolution pass aborts on a missing label) | Same split as above — the fatal this phase closes is a real Typst compile-time label-resolution error, not a translator-only concern |
| Docstring accuracy (QUA-01) | Translator (comment/docstring only) | — | Zero runtime effect; pure maintainer-facing documentation |
| GATE-01 regression proof | Test suite (`tests/test_*_render_gate.py`) driving `sphinx-build` → `typst.compile()` → `pypdf` | Builder (`TypstPDFBuilder.finish()`, unmodified this phase) | The gate exercises the full pipeline but this phase changes only the Translator tier |

No capability in this phase belongs in the Builder (`builder.py`) or `TemplateEngine`
(`template_engine.py`) tiers — confirmed by `CONTEXT.md`'s "Code under change" list, which cites only
`typsphinx/translator.py` line ranges.

## Standard Stack

### Core

No new dependency is introduced by this phase. The existing pinned stack (verified this session,
`Read pyproject.toml` lines 26-47) is:

| Library | Version (pinned range) | Purpose | Why Standard |
|---------|-------------------------|---------|--------------|
| `sphinx` | `>=9.1,<10` | Doctree construction, builder framework, `SphinxTranslator` base class | Already the project's core dependency; `TypstTranslator` subclasses `sphinx.util.docutils.SphinxTranslator` (`translator.py:15,139`, verified) |
| `docutils` | `>=0.21,<0.23` | The doctree node types this phase adds/fixes handlers for (`nodes.table`, `nodes.figure`, `nodes.legend`) | Sphinx's own doctree representation; `nodes.legend` confirmed present in the installed 0.21.x tree this session (`docutils.nodes.legend.__mro__` → `(legend, Part, Element, Node, object)`) |
| `typst` (typst-py) | `>=0.15.0,<0.16` | Compiles emitted `.typ` to PDF; the GATE-01 acceptance surface for both TBL-04/TBL-05/FIG-01 | Already in use throughout the render-gate test family; version confirmed installed this session: `typst-py 0.15.0` |

### Supporting (dev/test only, already declared)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | `>=8.4,<10` | Test runner for the new GATE-01 fixtures | Every `test_*_render_gate.py` |
| `pypdf` | `>=6.14,<7` | PDF text extraction for structural assertions (both tables/figures appear, in the right place, with the right numbering) | Already the established idiom (`test_wide_table_render_gate.py`); confirmed installed this session: `pypdf 6.14.2` |

### Alternatives Considered

Not applicable — this phase is a bug fix inside an existing, single-file translator; no library
substitution question arises. `Milestone Invariant #1` ("zero new runtime dependencies") is trivially
held.

**Installation:** none required — no `pyproject.toml` change.

## Package Legitimacy Audit

**Not applicable.** This phase installs no new packages of any kind (`npm`/`pip`/`cargo` — the project
is Python-only). All libraries touched (`sphinx`, `docutils`, `typst`, `pytest`, `pypdf`) are already
declared dependencies, verified present in `pyproject.toml` and importable in the project's own `uv`
venv this session. The Package Legitimacy Gate protocol is skipped per its own precondition ("every
phase that installs external packages").

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (already fully built before any visiting begins)
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│ TypstTranslator (typsphinx/translator.py) — one visit_X/depart_X   │
│ pair per docutils node type, called by docutils' walkabout()       │
│                                                                     │
│   visit_table ──┐                     ┌── visit_figure             │
│   (push state    │                     │   (push state             │
│    if nested)    │                     │    if nested)             │
│        │          ▼                     ▼        │                 │
│        │   [emits via self.body   [emits via   │                 │
│        │    .append(...) directly  self.add_text │                 │
│        │    -- bypasses add_text   -- ALREADY   │                 │
│        │    on purpose, see        routes         │                 │
│        │    Pitfall 2]             correctly]      │                 │
│        │                                          │                 │
│   depart_table ──── restore outer state    depart_figure ──── restore│
│   (route markup      if nested            (state-only fix;   outer  │
│    to enclosing                            markup already     state │
│    cell buffer if                          streams correctly  if    │
│    nested, else                            via add_text)      nested│
│    self.body)                                                       │
│                                                                     │
│   [NEW] visit_legend/depart_legend — combine image + legend        │
│   content into figure()'s single body argument via {...} join      │
│                                                                     │
│   depart_table (TBL-05) ── _emit_id_anchors fires regardless of    │
│   whether the rendered caption is figure-wrapped                   │
└───────────────────────────────────────────────────────────────────┘
        │
        ▼
   self.body → "".join() → .typ markup string
        │
        ▼
   TypstWriter / TemplateEngine (unmodified this phase) wraps in template
        │
        ▼
   typst.compile() (typst-py) ── Typst's own parser/label-resolution pass
   is the semantic backstop: a wrong composition here is what turns into
   the real, catchable TypstError this phase's GATE-01 fixtures assert on
        │
        ▼
   PDF (asserted via pypdf text extraction in the new GATE-01 fixtures)
```

A reader can trace both this phase's use cases end to end: a nested `list-table`/`table` enters
`visit_table` twice (push, push), and the inner `depart_table` must route its rendered `table(...)`/
`figure(...)` string into the *restored* enclosing cell's buffer, not `self.body`, before the outer
`depart_table` ever runs. A nested `figure` enters `visit_figure` twice; because `depart_figure`
already streams through `add_text`, the fix there is state-restore only, plus the new `legend` handler
composing the outer figure's single body argument.

### Recommended Project Structure

No new files under `typsphinx/` — this phase's entire production diff is inside
`typsphinx/translator.py`. New test files, following the established one-file-per-defect convention
(verified this session, `ls tests/*.py`: `test_wide_table_render_gate.py`,
`test_captioned_table_propagated_target_render_gate.py`,
`test_figure_propagated_target_render_gate.py`, etc.):

```
tests/
├── fixtures/
│   ├── nested_table_render_gate/          # TBL-04: one index.rst with 4 sections
│   │   ├── conf.py                        #   (list-in-list, grid-in-list, list-in-grid,
│   │   └── index.rst                      #    3-deep) — mirrors the existing convention of
│   │                                       #    combining shape + control in one fixture
│   │                                       #    (see table_in_list_item_render_gate/index.rst)
│   ├── table_empty_caption_anchor_render_gate/   # TBL-05
│   │   ├── conf.py
│   │   └── index.rst                      # the exact reproducing rST from CONTEXT.md <specifics> §1
│   └── nested_figure_render_gate/         # FIG-01
│       ├── conf.py
│       ├── img.png
│       └── index.rst
├── test_nested_table_render_gate.py
├── test_table_empty_caption_anchor_render_gate.py
└── test_nested_figure_render_gate.py
```

QUA-01 needs no fixture or test file — it is a comment-only diff (per the todo's own acceptance
list: "no GATE-01 fixture required, suite still green").

### Pattern 1: Snapshot Save/Restore Around Container Nesting (recommended fix shape for TBL-04/FIG-01)

**What:** In `visit_table`/`visit_figure`, if the corresponding boolean (`self.in_table`/
`self.in_figure`) is already `True` when the visitor fires, push a snapshot of the CURRENT scalar
values onto a small private stack before resetting them for the new (inner) container. In
`depart_table`/`depart_figure`, decide the rendered-markup destination based on whether the stack is
non-empty, then pop and restore the outer values.

**When to use:** Exactly this phase's two defects — any docutils container whose translator state is
scalar-shaped and whose node type is reachable inside its own descendant tree.

**Verified precedent for the `{...}` code-block-join half (used by the `legend` handler below), from
this codebase's own established idiom** — `visit_title`'s docstring, read this session
(`translator.py:725-728`):

```python
# Pitfall-1 fix: wrap the title content in a code block {...} so
# multi-child title content is one expression, not several
# juxtaposed statements (mirrors _depart_admonition's existing
# {...} wrap of the buffered admonition title).
```

and `_format_table_cell` (`translator.py:3236-3237`, verified):
```python
if colspan == 1 and rowspan == 1:
    return f"{indent}{{{content}}},\n"
```

Both already rely on Typst code blocks (`{ ... }`) sequentially joining multiple already-rendered
expressions into ONE content value — the exact mechanism a `legend` handler needs (Pattern 2 below).

### Pattern 2: `{...}` Code-Block Join for Multi-Piece Figure Body (FIG-01's routing half)

**What:** Typst's `figure(body, caption: ..., kind: ...)` accepts exactly one positional `body`
argument. Today, `visit_figure` emits a bare `image(...)` call as that argument (correct when the
image is the figure's only content). When a `legend` follows the caption, its content must be
combined with the image into ONE content value, or Typst raises a parse error at the argument
boundary.

**Verified this session** — a direct, hand-built `typst.compile()` experiment (no translator code
touched), confirming the composition works and numbers/captions both figures correctly:

Input (`/tmp/.../typstexp/test.typ`):
```typst
#{
[#figure(
  {
  image("img.png")
  figure(
  image("img.png"),
  caption: [INNERFIGCAP]
  )
  },
  caption: [OUTERFIGCAP]
) <id1>]
}
```

`typst.compile()` exit: **success**. `pypdf`-extracted text: `"Figure 2: INNERFIGCAP\nFigure 1:
OUTERFIGCAP"` — both figures present, correctly numbered (the outer is numbered 1 because Typst's
figure counter increments in the order the `figure()` calls are evaluated, not in final-layout
position), and the outer's own caption preserved.

**When to use:** Only when the figure node actually has a `legend` child — an unconditional `{...}`
wrap would change the emitted bytes for every existing image-only figure (see Pitfall 5, SC#4
byte-invariance). Gate the wrap on `bool([c for c in node.children if isinstance(c, nodes.legend)])`
(or equivalent), checked once in `visit_figure` (the doctree is already fully built at that point, per
the same "checked reliably before visiting begins" idiom `visit_table`'s own docstring already
documents at line 3167).

### Pattern 3: Two Distinct RED-Gate Shapes (GATE-01 mechanics for this phase)

This phase's three fixed defects fall into TWO different RED shapes established by prior phases
(`STATE.md` "GATE-01 (since v0.6.0)" + v0.7.0's amendment):

| Defect | RED shape | Verified evidence |
|--------|-----------|---------------------|
| TBL-04 (nested tables) | **Structural** — the broken output compiles cleanly (todo: "17802-byte PDF... There is no downstream error surface either") | Already measured in the source todo; not re-derived here per the research-priorities instruction |
| TBL-05 (empty-caption anchors) | **Classic `TypstError`** — `typst.compile()` aborts at the label-resolution pass | Already measured in the source todo (`"label <index:tbl-target> does not exist"`) |
| FIG-01 (nested figures) | **Classic `TypstError`** — **this session's own measurement corrects the phase description's framing.** `CONTEXT.md`/`REQUIREMENTS.md` describe FIG-01 as "the outer caption disappears entirely," which is true but understates the defect: **today's translator produces a Typst syntax error that aborts the ENTIRE compile**, not a silently-degraded-but-valid document. | See Pitfall 4 below for the exact reproduction and error text |

**Recommendation:** write FIG-01's GATE-01 fixture as a classic-`TypstError` RED (assert
`result.returncode != 0` / the specific error substring pre-fix, then assert a real PDF with both
figures' captions post-fix, via `pypdf` text extraction) — simpler and stronger than a structural-only
assertion, and it matches what CIT-01/TBL-03 already established as precedent for defects that abort
the compile.

### Anti-Patterns to Avoid

- **Unconditionally wrapping figure body in `{...}`:** breaks SC#4's byte-invariance requirement for
  every existing image-only figure in `docs/source` and `tests/roots/test-basic`. Gate on legend
  presence (Pattern 2).
- **Bypassing `add_text` for the nested-table markup emission without restoring state first:**
  `depart_table`'s existing `self.body.append(...)` calls happen BEFORE `self.in_table = False` is
  set (verified: lines 3269-3342 precede line 3355) specifically to dodge a stale-buffer hazard
  (Pitfall 2). Any rewrite must preserve — or consciously and explicitly supersede — this ordering,
  not accidentally invert it.
- **Treating `self.in_table`/`self.in_figure` as the complete state set:** as this session's Pitfall
  1 shows, `self.in_thead` and `self.current_morecols`/`self.current_morerows` share the exact same
  clobber shape and are easy to miss (the phase's own source todo missed them).
- **Re-deriving the TBL-04/TBL-05 reachability evidence:** `CONTEXT.md`'s `<specifics>` section is
  measured, dated 2026-08-04, and explicitly marked "build on it, do not re-derive." This research
  only re-derives FIG-01's mechanics, per the research-priorities instruction, because CONTEXT's own
  description of FIG-01 needed correcting (Pitfall 4) and the `legend`/`{...}` composition question
  was explicitly left open for research.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Id anchoring for a node with propagated target ids | A new anchor/label mechanism | `self._emit_id_anchors(node, skip_ids=...)` (`translator.py:481-552`, already exists) | It already handles dedup, list-item separator bookkeeping, and the `skip_ids` double-definition hazard; TBL-05 only needs a new *call site*, not new machinery |
| PDF-content assertions for the new GATE-01 fixtures | A hand-rolled PDF text scraper | `pypdf.PdfReader(...).pages[i].extract_text()` | Already the established idiom (`test_wide_table_render_gate.py:162-163`), and `pypdf>=6.14,<7` is already a declared dev dependency — no new install |
| Byte-invariance proof for SC#4 | A committed golden `.typ` file | The two-build `git worktree` + `typsphinx.__file__` isolation-proof method (`42-GATE-EVIDENCE-05.md`) | The owner explicitly chose this method over a golden file at Phase 42 (D-04 note: "the owner chose the two-build diff method over a committed golden, and over doing both") — re-litigating that choice here would contradict a standing project decision |
| Multi-piece Typst content composition | A custom string-concatenation join with manual separator logic | The `{...}` code-block-join idiom already used by `visit_title` and `_format_table_cell` | Verified this session to compile correctly for the figure-body case too (Pattern 2); reusing an already-proven idiom is lower-risk than inventing a new composition rule |

**Key insight:** every mechanism this phase needs (anchoring, PDF assertion, byte-invariance proof,
multi-piece content join) already exists somewhere in this codebase or its immediate history. The
work is applying each to a new nesting case, not designing anything new from scratch — consistent with
this being a maintenance-round phase.

## Common Pitfalls

### Pitfall 1: The reachable scalar set is larger than the phase's own source todo lists

**What goes wrong:** A fix that only handles `table_cells`/`table_colcount`/`table_colwidths`/
`table_caption`/`table_cell_content` (the todo's own "measure these 5 things first" list) will still
be broken for a table nested inside a **header** cell, or one where the outer cell carries
`colspan`/`rowspan`.

**Why it happens — verified this session, not in the source todo:**

`visit_thead`/`depart_thead` (`translator.py:3435-3453`, read this session):
```python
def visit_thead(self, node: nodes.thead) -> None:
    # Mark that we're in the header section
    self.in_thead = True

def depart_thead(self, node: nodes.thead) -> None:
    # Mark that we're no longer in the header section
    self.in_thead = False
```

consumed by `depart_entry` (`translator.py:3530-3538`, read this session):
```python
self.table_cells.append(
    {
        "content": cell_text,
        "is_header": self.in_thead,
        ...
    }
)
```

`self.in_thead` is a bare boolean with exactly the same unconditional-reset shape as
`table_colcount`/`table_caption` — if a table nested inside an outer *header* cell has its own
`thead`, the inner table's `depart_thead` leaves `self.in_thead = False` when it returns control to the
outer table's remaining header-row entries, silently misclassifying them as body cells.

**Reproduced this session** (`sphinx-build -b typst` against a fresh fixture: outer `list-table`
`:header-rows: 1` whose first header cell contains a nested `list-table` with its own header row):
the outer table collapses entirely (same clobber symptom already documented for TBL-04), which
prevents isolating `in_thead`'s own contribution in this particular probe — but the underlying hazard
is structurally verified (same unconditional-write, unconditional-read shape) and must be included in
whatever fix TBL-04 lands, or a fix that only restores the 5 originally-named scalars will leave this
sub-case silently broken.

Also verified, narrower blast radius (only matters when the outer cell ALSO uses `colspan`/`rowspan`
AND contains a nested table): `current_morecols`/`current_morerows`
(`translator.py:3505-3506` set in `visit_entry`, `translator.py:3527-3528` consumed in `depart_entry`)
share the same "set once, read once, but a nested table's own entries overwrite it in between" shape.

**How to avoid:** build the TBL-04/FIG-01 snapshot/frame around the FULL scalar set — `table_cells`,
`table_colcount`, `table_colwidths`, `table_caption`, `table_cell_content` (existence + value),
`in_thead`, `current_morecols`, `current_morerows` — not just the 5 the source todo names.

**Warning signs:** a GATE-01 fixture with a nested table inside a **header** cell (not just a plain
body cell) that asserts the outer header cell's text renders inside `table.header(...)`, not as a
plain body cell.

### Pitfall 2: `depart_table` deliberately bypasses `add_text` — any rewrite must preserve or consciously replace the reason why

**What goes wrong:** Naively routing the nested table's rendered markup through `self.add_text(...)`
instead of a direct buffer append can silently discard the OUTER table's own rendering for the
TOP-LEVEL (non-nested) case.

**Why it happens** — verified this session, `translator.py:3277-3279` (comment, read verbatim):
```python
# Use self.body.append directly (NEVER self.add_text) at this
# site -- see the comment below about the stale
# table_cell_content buffer misrouting hazard.
```

At the point `depart_table` emits `table_code`/`figure_code`, `self.in_table` is STILL `True`
(it is only set `False` at line 3355, AFTER the emission block). If a NON-nested table's own LAST
entry left `table_cell_content` reset-but-not-deleted (the Phase 25 invariant, Pitfall 3), calling
`add_text` here would misroute the table's own render into that orphaned buffer instead of
`self.body` — a silent, total loss of the table's output.

**How to avoid:** the routing decision for a nested table's rendered markup must be an EXPLICIT
branch (stack non-empty → append into the restored enclosing frame's cell buffer; stack empty →
append to `self.body`, exactly as today), not a blanket switch to `add_text`. Do the restore/pop
BEFORE deciding the destination, so the "stack empty" case is byte-identical to current behavior.

### Pitfall 3: The Phase 25 `table_cell_content` lifetime invariant is easy to break by a well-intentioned rewrite

**What goes wrong:** `table_cell_content` is deliberately created by the FIRST `visit_entry`, reset to
`[]` (not deleted) at every `depart_entry`, and `del`eted ONLY in `depart_table`
(`translator.py:3376-3388`, comment read verbatim this session):
```python
# Stale-buffer root-cause fix (25-RESEARCH.md Verified Mechanism 2):
# table_cell_content is created by the FIRST table's visit_entry and
# reset to [] (not deleted) at every depart_entry, so it persists as an
# EXISTING attribute for the rest of the translator's lifetime.
```
A stack/frame rewrite that makes `table_cell_content` a per-frame dataclass field but forgets to
replicate the "only delete when the OUTERMOST table closes" rule reintroduces the Phase 25 bug this
comment fixes: the next table's caption title would silently misroute into a leftover buffer.

**How to avoid:** whichever fix shape is chosen, the `del`/hasattr-goes-False semantics must fire
ONLY when the stack becomes empty (the closing table was the outermost), never on an inner table's
own close.

### Pitfall 4: FIG-01's real defect is a hard compile fatal, not merely a dropped caption — verified this session

**What goes wrong:** Trusting `CONTEXT.md`'s description ("the outer caption disappears entirely")
without re-measuring leads to writing FIG-01's GATE-01 RED as a structural-only assertion, when it
should be a much stronger classic-`TypstError` assertion.

**Verified this session** — a real `sphinx-build -b typstpdf` run against a figure nested inside
another figure's second paragraph (docutils' `legend`):

```
WARNING: unknown node type: <legend><figure ids="id2">...
```
Emitted `index.typ` (verbatim, relevant excerpt):
```typst
[#figure(
  image("img.png")[#figure(
  image("img.png"),
  caption: {text("INNERFIGCAP")}
) <index:id2>]
) <index:id1>]
```
`sphinx-build -b typstpdf` result:
```
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index:
Typst compilation failed: TypstError: unexpected argument
```

**Even a PLAIN-TEXT legend with no nested figure at all is already broken today** (verified this
session, a second, simpler probe):
```typst
[#figure(
  image("img.png")par({text("A plain legend paragraph, no nested figure.")})
,
  caption: {text("OUTERFIGCAP")}
) <index:id1>]
```
```
TypstError: expected comma
```

**Why it happens:** `image(...)` followed directly by a bracket `[...]` (or any other expression) is
parsed by Typst as `image(...)` receiving an unwanted second argument/trailing content block — a
genuine syntax error, not a semantic loss. `visit_legend`/`depart_legend` do not exist
(`grep -n 'def visit_legend\|def depart_legend' typsphinx/translator.py` → no matches, confirmed this
session), so docutils' `unknown_visit` fires (a warning-only override, `translator.py:4590-4601`,
confirmed to just log and continue — it does NOT raise `SkipNode`/`SkipChildren`), and the legend's
children stream straight into whatever the current `add_text` destination is with no wrapping at all.

**How to avoid:** write FIG-01's GATE-01 RED as a classic-`TypstError` assertion (assert the specific
error substring pre-fix; assert a real compiled PDF with both captions post-fix via `pypdf`), matching
Pattern 3 above. Note also that fixing this correctly (Pattern 2's `{...}` join) will likely ALSO fix
the plain-legend-with-no-nested-figure case as a side effect — this is fine and expected (the root
cause is identical), even though FIG-01's stated scope is specifically the nested-figure shape; do not
narrow the fix to special-case "only when the legend contains a figure."

### Pitfall 5: `visit_table`'s structural captioned pre-check cannot be made value-aware (TBL-05, D-07 — already decided, restated for planning)

**What goes wrong:** An instinct to fix TBL-05 by making `visit_table`'s `is_captioned` check
"smarter" (e.g., checking `title.astext()`) will not work.

**Why it happens** — already measured and recorded in `CONTEXT.md` D-07 and the source todo: the
reproducing construct's title child is a `raw` node; `title.astext()` returns `'<span></span>'`
(non-empty), while `visit_raw` raises `SkipNode` for `format != typst`, so the RENDERED result is
empty. The rendered value is only knowable after the title has actually been visited — i.e., at
`depart_table` time, not `visit_table` time.

**How to avoid:** per D-05, keep `visit_table`'s structural pre-check exactly as-is (it correctly
decides whether to skip the unconditional visit-side anchor call, to avoid a duplicate-label fatal),
and make `depart_table`'s id-anchor emission independent of `if self.table_caption:` — call
`_emit_id_anchors` unconditionally whenever `is_captioned` was true, regardless of whether the
rendered caption ended up empty. Keep the SEPARATE `if self.table_caption:` check that gates
figure-wrapping (rendering) exactly as it is today — the two checks are allowed to keep disagreeing
about "captioned" (D-05's explicit framing), matching Sphinx's own LaTeX builder behavior (measured by
the owner 2026-08-04: no `\sphinxcaption`/no table number, but `\phantomsection\label{...}` still
emitted, no warning).

## Code Examples

### The exact TBL-05 reproducing construct (from `CONTEXT.md`, verbatim — not re-derived)

```rst
.. role:: raw-html(raw)
   :format: html

.. _tbl-target:

.. table:: :raw-html:`<span></span>`

   +---+---+
   | a | b |
   +---+---+

See :ref:`the table <tbl-target>`.
```

Note: the `:ref:` must carry explicit link text (`the table <tbl-target>`) — a bare
`` :ref:`tbl-target` `` makes Sphinx itself refuse first with its own warning and degrade to plain
text, masking the Typst-level failure. Do not simplify this fixture by removing the explicit link
text.

### `depart_table`'s current unconditional emission (the code the fix must touch), verbatim (`translator.py:3304-3342`)

```python
if self.table_caption:
    # TBL-01/D-02: figure-wrap with native "Table N" numbering.
    figure_code = (
        f"figure(\n{table_code},\n"
        f"  caption: {{{self.table_caption}}},\n"
        f"  kind: table\n)"
    )
    if node.get("ids"):
        label = self._namespace_label(
            self._current_docname(), node["ids"][0]
        )
        if converted_width is not None:
            self.body.append(
                f"block(width: {converted_width})[#{figure_code} "
                f"<{label}>]\n\n"
            )
        else:
            self.body.append(f"[#{figure_code} <{label}>]\n\n")
    elif converted_width is not None:
        self.body.append(
            f"block(width: {converted_width})[#{figure_code}]\n\n"
        )
    else:
        self.body.append(f"{figure_code}\n\n")
else:
    # Caption-less path: byte-for-byte unchanged (SC#2).
    ...
```

### TBL-03's ordering constraint the TBL-05/TBL-04 fixes must respect (`translator.py:3355-3370`, verbatim)

```python
self.in_table = False

# TBL-02/Critical Pitfall 3: ids[0] is already self-anchored above
# as the figure's own <label> -- anchoring it again here would
# define it TWICE (Typst "label ... occurs multiple times" compile
# fatal). Anchor only a PROPAGATED remainder id (ids[1:]); no-op
# when there is none.
#
# TBL-03 (Phase 42): this call must run AFTER self.in_table is
# cleared above. add_text() (see that method) diverts every append
# into self.table_cell_content while self.in_table is set, and that
# buffer is `del`eted a few statements below -- so an anchor emitted
# from the old pre-reset call site never reached self.body at all;
# it was silently discarded along with the buffer.
if was_captioned:
    self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
```

For TBL-05, `was_captioned` (`translator.py:3353`, `self.table_colcount > 0 and bool(self.table_caption)`)
must NOT be the gate for the anchor call — it must instead use the STRUCTURAL `is_captioned` decided
at `visit_table` time (stashed onto an instance attribute, since `depart_table` cannot re-derive it
from the doctree at this point without re-checking `node.children[0]`, which is cheap and available:
`node.children` is unchanged between visit and depart).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Table/figure translator state as unconditionally-reset scalars | Snapshot save/restore around nesting (this phase) | Phase 43 (proposed) | Nested tables/figures render correctly instead of silently clobbering the enclosing container |
| `depart_table`'s caption-truthiness gates BOTH rendering and id-anchoring | Caption-truthiness gates rendering only; a separate structural check gates anchoring (TBL-05, D-05) | Phase 43 (proposed) | Matches Sphinx's own LaTeX builder behavior (measured 2026-08-04): an empty-rendered caption keeps its label, even with no visible caption or table number |
| No `legend` node handler (unknown node type warning, hard compile fatal for ANY multi-paragraph figure) | `visit_legend`/`depart_legend` compose the legend into the figure's single body argument via `{...}` | Phase 43 (proposed) | Closes a pre-existing hard fatal, not just a data-loss defect — verified this session to be broader than the FIG-01 requirement's stated nested-figure scope |

**Deprecated/outdated:** none — this is new-territory bug-fixing, not a library migration.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `{...}` code-block-join composition (Pattern 2) is the RIGHT fix shape for `legend`, as opposed to some other Typst construct (e.g., `stack()`, `block()`) | Architecture Patterns / Pattern 2 | Low — verified this session via a real `typst.compile()` run to produce correct numbering and both captions; an alternative construct might also work, but this one is proven and reuses an existing codebase idiom |
| A2 | The reproduction of the `in_thead` hazard (Pitfall 1) generalizes beyond the one probe run this session (its own effect could not be cleanly isolated because the general TBL-04 clobber already collapses the whole outer table in that probe) | Common Pitfalls / Pitfall 1 | Medium — if wrong, `in_thead` might turn out to be self-correcting once the general TBL-04 fix lands (e.g., if it happens to be restored as a side effect of some frame designs); the planner should re-verify this specific sub-case (nested table inside a HEADER cell) once a fix shape is chosen, with a dedicated fixture, rather than assume this research's structural argument alone suffices |
| A3 | `docutils`'s "second and later figure paragraph becomes a `legend` node" behavior is stable across the pinned `docutils>=0.21,<0.23` range, not just the installed 0.21.x version this session measured against | Common Pitfalls / Pitfall 4 | Low — this is long-standing, version-independent docutils behavior (the figure directive's caption/legend split predates 0.21), but was only directly measured against the one installed version |

**If this table is empty:** N/A — see rows above. All three are LOW-to-MEDIUM risk refinements, not
load-bearing unknowns; none blocks planning.

## Open Questions

1. **Exact snapshot/frame data structure (dataclass vs. tuple vs. small named-stack-of-dicts)**
   - What we know: the snapshot must cover `table_cells`, `table_colcount`, `table_colwidths`,
     `table_caption`, `table_cell_content` (value + existence), `in_thead`, `current_morecols`,
     `current_morerows` for tables; `figure_content`, `figure_caption`, `_figure_block_width` for
     figures — see Discretion section below for the fuller comparison.
   - What's unclear: whether the planner should also fold `_saved_body_for_figure_caption` and
     `_caption_saved_list_state`-style save/restore idioms already used elsewhere in this file into
     the SAME snapshot object, or keep them as separate, already-working machinery untouched.
   - Recommendation: keep them separate — they are unrelated buffer-swap idioms for a DIFFERENT
     purpose (deferred rendering of an admonition/figure caption's own inline content) that already
     work correctly today and are not implicated in the nesting clobber (they save/restore around a
     SINGLE node's visit, not around an arbitrary-depth nesting boundary).

2. **Whether the `legend` handler needs any visual styling at all, or purely structural pass-through**
   - What we know: Sphinx's own LaTeX writer's `visit_legend`/`depart_legend` are trivial
     (`self.body.append(CR + r'\begin{sphinxlegend}')` / the matching close) — no font/size change,
     just a semantic wrapper.
   - What's unclear: whether Typst readers expect ANY visual distinction for legend text (smaller/
     italic, matching many HTML themes' `.legend` CSS class) — out of this phase's scope per
     `CONTEXT.md`'s Deferred Ideas ("Broader legend styling/typesetting is not in scope").
   - Recommendation: no styling — a bare `{...}`-join structural fix, matching the phase's explicit
     scope fence.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| `typst` (typst-py) | GATE-01 fixtures' `typst.compile()` calls | ✓ | 0.15.0 | — |
| `pypdf` | GATE-01 fixtures' PDF text-extraction assertions | ✓ | 6.14.2 | — |
| `uv` | Per-worktree provisioning (`CLAUDE.md` "Worktree-isolated execution") | ✓ | 0.11.25 | — |
| Python | Runtime | ✓ | 3.13.13 | — |
| `origin` git remote reachability | SC#5 (push milestone branch to `origin` during this phase) | ✓ (remote reachable; `git ls-remote --heads origin` succeeded this session) | — | — |

**Missing dependencies with no fallback:** none.

**Milestone branch push status (SC#5), verified this session:** `git rev-parse --abbrev-ref HEAD` →
`gsd/v0.7.1-bug-fix-round`; `git ls-remote --heads origin` does **not** list this branch yet (only
`main`, two `dependabot/*` branches, the prior `gsd/v0.7.0-*` branch, and two `worktree-agent-*`
branches). **SC#5 is not yet satisfied** — the plan must push this branch to `origin` during this
phase, per milestone invariant #5.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest `>=8.4,<10` (verified, `pyproject.toml:37`), config in `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `python_files = ["test_*.py"]`) |
| Config file | `pyproject.toml` (no separate `pytest.ini`) |
| Quick run command | `uv run python -m pytest tests/test_nested_table_render_gate.py tests/test_table_empty_caption_anchor_render_gate.py tests/test_nested_figure_render_gate.py -x` |
| Full suite command | `uv run python -m pytest` (matches CI; per `CLAUDE.md` worktree section, run every command via `uv run` inside a worktree) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| TBL-04 | Nested table (4 shapes: list-in-list, grid-in-list, list-in-grid, 3-deep) preserves outer cells/caption/colcount | integration (structural RED, per Pattern 3 — the broken output compiles cleanly) | `uv run python -m pytest tests/test_nested_table_render_gate.py -x` | ❌ Wave 0 |
| TBL-05 | Empty-rendered-caption table still anchors ids | integration (classic-`TypstError` RED — aborts at label resolution) | `uv run python -m pytest tests/test_table_empty_caption_anchor_render_gate.py -x` | ❌ Wave 0 |
| FIG-01 | Nested figure preserves outer caption/ids/state; inner renders inside legend; no `unknown node type` warning | integration (classic-`TypstError` RED, per Pitfall 4 — corrects the phase description's framing) | `uv run python -m pytest tests/test_nested_figure_render_gate.py -x` | ❌ Wave 0 |
| QUA-01 | `_emit_id_anchors`'s docstring names both real `skip_ids` callers | manual/documentation verification only — comment-only diff, no runtime behavior change | `grep -n 'skip_ids' typsphinx/translator.py` (re-grep at fix time, per the todo's own instruction not to trust its recorded count) | N/A — no test required |

### Sampling Rate

- **Per task commit:** the quick-run command above.
- **Per wave merge:** `uv run python -m pytest` (full suite) plus `black --check .`, `ruff check .`,
  `mypy typsphinx/` (matching CI exactly, per `CLAUDE.md` Commands section).
- **Phase gate:** full suite green, plus the D-04 two-build byte-invariance sweep over
  `docs/source/**` and `tests/roots/test-basic` (see Package/Standard-Stack sections — no new
  artifact needed; reuse `42-GATE-EVIDENCE-05.md`'s method verbatim, widened per D-04) before
  `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] `tests/fixtures/nested_table_render_gate/{conf.py,index.rst}` — covers TBL-04 (4 shapes: list-
  in-list per the existing todo reproduction, grid-in-list, list-in-grid, and a 3-deep nest, per D-01)
- [ ] `tests/test_nested_table_render_gate.py` — structural assertions per Pattern 3
- [ ] `tests/fixtures/table_empty_caption_anchor_render_gate/{conf.py,index.rst}` — covers TBL-05,
  using the exact reproducing rST quoted in Code Examples above (do not simplify away the explicit
  `:ref:` link text)
- [ ] `tests/test_table_empty_caption_anchor_render_gate.py` — classic-`TypstError`-then-fixed
  assertions per Pattern 3
- [ ] `tests/fixtures/nested_figure_render_gate/{conf.py,img.png,index.rst}` — covers FIG-01
- [ ] `tests/test_nested_figure_render_gate.py` — classic-`TypstError`-then-fixed assertions, per
  Pitfall 4's corrected framing (assert the pre-fix `TypstError: unexpected argument` substring, not
  merely a missing-caption structural check)
- [ ] No new pytest fixture/conftest infrastructure needed — the established
  `_run_sphinx_build_typstpdf` subprocess helper pattern (seen in
  `tests/test_table_in_list_item_render_gate.py` and `tests/test_wide_table_render_gate.py`) can be
  copy-adapted per new test file, matching existing convention (no shared conftest helper exists for
  this across render-gate files today, verified: each file defines its own).

## Security Domain

`security_enforcement` is enabled (`config.json` `workflow.security_enforcement: true`,
`security_asvs_level: 1`).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|---------------------|
| V2 Authentication | No | This phase touches a build-time document translator with no runtime auth surface |
| V3 Session Management | No | No session concept in this codebase |
| V4 Access Control | No | No access-control surface |
| V5 Input Validation | Partial | The translator already handles malformed/edge-case doctree shapes defensively (e.g., `_build_columns_fr_arg`'s fallback for missing/invalid colwidth data, `translator.py:3213-3218`); this phase's fix must not introduce a new unhandled edge case (e.g., a stack-underflow if `depart_table`/`depart_figure` somehow fires without a matching prior `visit_*` — defensive `if self._table_state_stack:` guards, not bare `.pop()`) |
| V6 Cryptography | No | No cryptographic operations in this phase |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Malformed/adversarial rST input causing a translator crash (DoS against a CI build) | Denial of Service | Defensive `hasattr`/length checks already used throughout `translator.py` (e.g., `_build_columns_fr_arg`'s fallback path); this phase's stack/snapshot mechanism should use `if stack:` guards before `pop()`/`[-1]` indexing rather than assuming balanced push/pop, even though docutils' own tree-walking guarantees balanced visit/depart calls in practice |

No other ASVS category is meaningfully applicable — this is a document-transform library with no
network-facing runtime component; the "attacker" model here is at most "a malformed or adversarially
crafted rST source file breaking a CI build," which V5's defensive-coding control already covers.

## Sources

### Primary (HIGH confidence — direct `Read`/command execution this session)

- `typsphinx/translator.py` — full read of: `__init__` state (lines 140-197), `add_text` (423-437),
  `_emit_id_anchors` (481-552), `visit_title`/`depart_title` (623-800), `visit_figure`/`depart_figure`
  (2418-2530), `visit_caption`/`depart_caption` (2532-2589), `visit_table`/`depart_table` (3149-3394),
  `visit_tgroup`/`visit_colspec`/`visit_thead`/`depart_thead`/`visit_row`/`visit_entry`/`depart_entry`
  (3395-3539), `visit_image`/`depart_image` (3648-3708), the three other `in_table` consumers
  (1600-1663, 5520-5568, 5860-5913), `unknown_visit`/`unknown_departure` (4590-4611)
- `grep -n '_emit_id_anchors('` — 21 total call sites, 2 with `skip_ids` (lines 2518, 3370) — matches
  QUA-01's todo exactly
- `grep -n 'self\.in_table\|self\.in_figure'` — full consumer enumeration, cross-checked against
  `CONTEXT.md`'s cited line numbers
- Direct `sphinx-build -b typst`/`-b typstpdf` runs against three fresh probe fixtures this session:
  nested-figure-in-legend (Pitfall 4), plain-text legend with no nested figure (Pitfall 4), nested
  table inside a header cell (Pitfall 1)
- Direct `typst.compile()` experiment (Pattern 2) proving the `{...}` code-block-join composition for
  a figure body containing both an image and a nested figure
- `pyproject.toml` — dependency versions (lines 26-47), pytest config (74-83)
- `.planning/milestones/v0.7.0-phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-05.md` — full read, the two-build byte-invariance method D-04 mandates
- `git ls-remote --heads origin`, `git rev-parse --abbrev-ref HEAD` — SC#5's current unmet status
- `uv run python -c "import typst/pypdf"` — installed version confirmation

### Secondary (MEDIUM confidence — in-repo artifacts, not independently re-measured beyond what's cited above)

- `.planning/phases/43-table-state-correctness-nested-tables-empty-title-anchors/43-CONTEXT.md` — all
  decisions D-01 through D-08, the Discretion section, the three folded todos
- `.planning/todos/pending/2026-08-04-nested-table-clobbers-outer-table-state.md`
- `.planning/todos/pending/2026-08-03-table-whitespace-only-title-anchor-divergence.md`
- `.planning/todos/pending/2026-08-04-emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user.md`
- `docutils.nodes.legend.__mro__` (installed 0.21.x) and `sphinx.writers.latex`'s `visit_legend`/
  `depart_legend` source, both introspected via `uv run python -c "..."` this session

### Tertiary (LOW confidence)

- None — this phase required no external web research (zero new dependencies, entirely in-repo code
  archaeology plus direct local experimentation).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; all versions read directly from `pyproject.toml` and
  cross-checked against the installed `uv` venv this session.
- Architecture (fix-shape comparison): HIGH — every consumer site cited is quoted verbatim from a
  `Read` this session, including the two NEWLY discovered consumers (`in_thead`, `current_morecols`/
  `current_morerows`) not present in the phase's own source todo.
- Pitfalls: HIGH for Pitfalls 1-3 and 5 (direct code reads with line numbers and quotes); HIGH for
  Pitfall 4 (a real, reproduced `TypstError` this session, correcting the phase description's own
  framing).
- FIG-01 fix-shape recommendation (Pattern 2): MEDIUM-HIGH — the composition was verified to compile
  correctly in isolation (hand-built `.typ`, not yet wired through `translator.py`); the exact
  detection logic for "does this figure have a legend child" and its precise wiring into
  `visit_figure`/`depart_figure` remains an implementation decision for planning/execution.

**Research date:** 2026-08-04
**Valid until:** No external dependency drift risk (zero new packages); the in-repo line-number
citations are valid until the next commit touches `typsphinx/translator.py` — re-grep before trusting
any specific line number if this phase's plan is executed more than a few commits after this research
(mirrors QUA-01's own "re-derive the list at fix time" instruction).
