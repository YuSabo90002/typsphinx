# Phase 25: Captioned Table Figure Wrap + Cross-References (reimplement PR#98) - Research

**Researched:** 2026-07-23
**Domain:** docutils→Typst translator node-handler reimplementation (single-file, `typsphinx/translator.py`)
**Confidence:** HIGH — every claim below was checked against the CURRENT repo code, a live `sphinx-build`/`typst.compile()` round-trip, or PR#98's actual diff (fetched via `gh pr diff 98`), not training-data recall.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Caption stays **below** the table — Typst's native default for
  `figure`. The translator emits position-agnostic output; `templates/base.typ`
  is **unchanged** (it currently has no figure/caption `#show` rule — verified,
  only `codly-init` and a `link` rule exist). This keeps the fix 100%
  translator-side and isolates the translator state-machine risk (phase intent).
- **D-02:** The translator MUST emit `kind: table` on every captioned-table
  figure. Beyond enabling native "Table N" numbering, `kind: table` is the
  selector hook that lets a user flip *only tables* to caption-above **without
  editing typsphinx code or `base.typ`** — by supplying their own `typst_template`
  (existing config) containing:
  `#show figure.where(kind: table): set figure.caption(position: top)`.
  Images/figures stay below. "Default below, customizable to above via a custom
  template" is thus a free consequence of D-01, not extra work.
- **D-03:** Defer reference rendering to **Typst-native** behavior. `:numref:` /
  `:ref:` convert to a Typst `@label` reference; `figure(kind: table)`'s
  supplement auto-renders "Table N". This satisfies SC#5 ("working Table N link")
  at minimum scope. Sphinx `numfig_format` / custom numref format strings
  (e.g. `` :numref:`Tbl. %s <t>` ``) are NOT honored — deferred (would require
  reading numfig config and expands beyond the PR#98 reimplement intent).
- **D-04:** The `:width:` `block(width: ...)` wraps the **entire figure**
  (caption included), mirroring the existing `depart_figure` idiom exactly:
  `block(width: 80%)[#figure(table(...), caption: {...}, kind: table) <label>]`.
  Reuse the established figure pattern so the `<label>` close lands inside the
  same markup bracket the `block(...)[...]` opens. Do NOT wrap only the inner
  `table()` (that would need a separately-built label-control path in
  `depart_table`).
- **D-05:** Cover all three caption-bearing directives — `.. table::`,
  `csv-table`, `list-table`. All converge on `nodes.table` with the caption as a
  `title` child, so a single wiring (`visit_title` buffers when `in_table`;
  `depart_table` consumes) covers all three automatically — same structural fact
  the `:width:` wiring already relies on.
- **D-06:** GATE-01 fixture (mandatory) MUST include, as real `typst.compile()`
  red→green cases: a **2+-table** document (stale-cell-buffer bug is invisible
  with one table), a **caption + `:width:`** composition case (verified
  *together*, not separately), and a **`:numref:`-resolves** case. Add one
  lighter caption-regression case each for `csv-table` and `list-table`.

### Claude's Discretion

- Exact id-selection for the `<label>` (which of a table's `ids` is primary vs.
  anchored as `metadata(none)`): mirror `depart_figure`'s established rule
  (`ids[0]` self-anchors in the `) <label>]` postfix; remaining ids anchored via
  `_emit_id_anchors(node, skip_ids={ids[0]})`). No collision with the table's
  existing `_emit_id_anchors` id anchors (SC#5).
- Buffer/save-restore mechanics for the `in_table` caption path — must not
  collide with the existing `visit_title` save/restore of `in_list_item` /
  `list_item_needs_separator`, the admonition/topic branch, or section-id anchors.

### Deferred Ideas (OUT OF SCOPE)

- **Config-injected preamble show rules** — a lightweight `typst_*` config to
  inject arbitrary preamble snippets (e.g. the table-caption-above show rule)
  without supplying a full custom template. Would make D-02's customization
  one-line instead of full-template. Its own future phase, not Phase 25.
- **Sphinx `numfig_format` / custom numref format-string fidelity** — honoring
  `` :numref:`Tbl. %s <t>` `` and localized supplements. Out of scope per D-03;
  candidate for a later cross-reference phase (cf. deferred XREF-02).
- `.planning/todos/pending/2026-07-22-citation-node-support-untracked.md`,
  dead-config/orphan-doc todos — reviewed, belong to other phases (26/27), not
  Phase 25.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| TBL-01 | `.. table:: Caption` (+ `csv-table`/`list-table`) renders as `figure(table(...), caption: {...}, kind: table)`, native "Table N" numbering, no stray heading; caption-less table stays plain `table()`; caption preserves inline markup; composes with `:width:`; correct on 2nd+ table (no stale-buffer loss) | See "Verified Mechanism 1" (stray-heading root cause), "Verified Mechanism 2" (stale-buffer live repro), Architecture Patterns, Code Examples |
| TBL-02 | `:numref:`/`:ref:` to a captioned table resolves to a working cross-reference — `figure(..., kind: table)` carries a Typst `<label>` derived from the table's docutils target id, no dangling/duplicate-label error, no collision with `_emit_id_anchors` | See "Verified Mechanism 3" (xref pipeline already generic — nothing to build), "Critical Pitfall 3" (`_emit_id_anchors` double-anchor collision — THE actual TBL-02 risk) |

</phase_requirements>

## Summary

This phase is a **narrow, well-bounded reimplementation** whose exact shape was
independently reverse-engineered three ways — reading the current
`typsphinx/translator.py`, running real `sphinx-build`/`typst.compile()`
round-trips against hand-written `.. table::` fixtures, and fetching PR#98's
actual diff via `gh pr diff 98` — and all three agree with CONTEXT.md's design
intent. Nothing here overturns a locked decision (D-01..D-06); this research
exists to de-risk the two Typst-behavior assumptions and precisely map the
current-code seams, which is what it does below, with three concrete,
**live-verified** findings that go beyond CONTEXT.md's abstract description:

1. **The stray-heading bug and the stale-buffer bug are BOTH reproduced live**
   in this repo, today, with the exact `.typ` output captured (see Verified
   Mechanisms 1 & 2). The stale-buffer bug is real and severe: a 2nd table's
   caption is not just malformed, it **disappears entirely** — confirmed by a
   real 2-table `sphinx-build -b typst` run whose output contains zero
   occurrences of the string `"Second Caption"`.
2. **PR#98's actual upstream fix (fetched via `gh pr diff 98`) reuses
   `self.table_cell_content` as the caption buffer** (not a `self.body` swap
   like `depart_figure`/`depart_caption` use) — this is not a stylistic choice,
   it is **required** by this codebase's `add_text()` dispatch rule (`in_table`
   AND `hasattr(table_cell_content)` → route to `table_cell_content`, not
   `self.body`). A naive port of the figure-caption buffer-swap idiom would
   silently misroute the caption's inline content into the cell buffer even
   with a correct-looking `self.body` swap, because `self.in_table` stays
   `True` throughout. See Critical Pitfall 2 — this is the single most
   important implementation detail this research surfaces.
3. **TBL-02 (cross-referencing) is *already functionally live* today** via the
   existing generic `visit_reference`/`depart_reference` `refid` branch and the
   existing unconditional `_emit_id_anchors(node)` call at the top of
   `visit_table` — verified by a real compile showing
   `link(<index:my-table>, text("Table 1"))` already resolving correctly for a
   captioned (but not-yet-figure-wrapped) table. The actual NEW risk TBL-01
   introduces for TBL-02 is a **double-anchor collision**: `visit_table`
   currently anchors `ids[0]` unconditionally BEFORE the title is even visited
   (so before we know the table is captioned); once `depart_table` also
   self-anchors `ids[0]` as the figure's own `<label>` (mirroring
   `depart_figure`), that id would be defined twice → Typst
   `label ... occurs multiple times` compile fatal. This is exactly what SC#5's
   "no collision with `_emit_id_anchors`" warns about, and the fix must move
   (not merely parameterize) the anchor call — see Critical Pitfall 3.

**Primary recommendation:** Port PR#98's `table_cell_content`-reuse buffer
idiom into current `visit_title`/`depart_title`/`depart_table` (not the
`self.body`-swap figure-caption idiom), add `del self.table_cell_content` at
the end of `depart_table` (root-cause fix for the stale-buffer bug, matching
PR#98's own fix), and move the table's id-anchoring so `ids[0]` is anchored
via `_emit_id_anchors(node, skip_ids={ids[0]})` in `depart_table` (post-caption,
mirroring `depart_figure` line-for-line) rather than unconditionally in
`visit_table`, for captioned tables only — non-captioned tables keep the
current unconditional `visit_table`-time anchor unchanged.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Caption capture (docutils `title` child → buffered string) | Translator (build-time, single-process Python) | — | `visit_title`/`depart_title` run inside the same in-process docutils tree walk; no other tier is involved |
| Figure-wrap + numbering emission (`figure(..., kind: table)`) | Translator (emits Typst source) | Typst compiler (executes the numbering) | Translator only emits the call; Typst's own `counter(figure.where(kind: table))` performs the actual "Table N" numbering at compile time |
| `:width:`/caption composition (`block(width:)[...]`) | Translator | — | Pure text-generation composition, no runtime tier |
| Label/anchor emission + collision avoidance | Translator | — | `_emit_id_anchors`/`_namespace_label` are pure translator-side label-string bookkeeping |
| `:numref:`/`:ref:` resolution to a label | Sphinx build (`doctree-resolved` phase, upstream of the writer) | Translator (`visit_reference`) + Typst compiler (`@label` lookup) | Sphinx's std domain resolves `pending_xref` → `reference(refid=...)` BEFORE the translator ever sees the node (already verified, no new code needed here); the translator only renders the resolved node; Typst performs the final same-document label lookup at compile time |
| "Table N" display text at read time | Typst compiler | — | Not Sphinx's numfig text — this is Typst's own supplement/counter machinery, independent of Sphinx's `numfig` setting (see Verified Mechanism 3 nuance) |

This phase is 100% single-tier (translator/build-time Python); there is no
browser, SSR, API, or CDN tier in this project. The map above exists mainly to
make explicit that "Table N" *rendering* is a Typst-compiler-owned capability,
not something the translator computes — this matters for D-03's scope
boundary (Sphinx's `numfig_format` is explicitly NOT plumbed through, and does
not need to be, because Typst owns the final number).

## Package Legitimacy Audit

**Not applicable — this phase introduces zero new dependencies.** `typst-py`
(pinned `>=0.15.0,<0.16`, verified installed version `0.15.0` in `uv.lock`) and
`pypdf` (installed, confirmed via `uv run python -c "import pypdf; print(pypdf.__version__)"` → `6.14.2`) are both **already** project dependencies used by the
existing GATE-01 render-gate test suite (`tests/test_pdf_render_gate.py`);
this phase reuses them, adding no new package. The milestone invariant ("zero
new runtime deps, no `@preview` version bump") is trivially satisfied — no
`@preview` package touches table/figure rendering.

## Verified Mechanisms (the two Typst-behavior assumptions + the xref pipeline)

### Verified Mechanism 1 — the stray-heading bug, live-reproduced

A real `sphinx-build -b typst` against a `.. table:: My Caption` fixture
(`numfig = True`, `:name: my-table`) emits, TODAY, on current `main`:

```typst
[#metadata(none) <index:my-table>]
heading(level: 1, {text("My Caption")})

table(
  columns: (3fr, 3fr),
  ...
)
```

Root cause, confirmed by reading `visit_title`/`depart_title`
(`typsphinx/translator.py:453-582`): the caption's `title` node's `.parent` is
the `nodes.table` (docutils stores a `.. table:: Caption` directive's caption
as a `title` *child* of `nodes.table` — confirmed via `publish_doctree`).
`visit_title` only special-cases `isinstance(node.parent, nodes.Admonition)`
or `nodes.topic`; a `nodes.table` parent matches neither, so it falls through
to the generic section-heading path, which checks
`isinstance(node.parent, nodes.section)` (False for a table parent) and emits
a bare `heading(level: N, {...})` — exactly the observed bug. `[VERIFIED:
live sphinx-build + translator.py read]`

### Verified Mechanism 2 — the stale-buffer bug, live-reproduced (2nd table swallows its caption ENTIRELY)

A real `sphinx-build -b typst` against a 2-table `.rst` fixture (both tables
captioned, both named) emits, TODAY:

```typst
[#metadata(none) <index:first-table>]
heading(level: 1, {text("First Caption")})

table( ... A/B/1/2 ... )


[#metadata(none) <index:second-table>]
table( ... C/D/3/4 ... )
```

**`"Second Caption"` does not appear anywhere in the output.** Root cause,
confirmed by reading `add_text()` (`translator.py:253-267`) and
`visit_entry`/`depart_entry` (`translator.py:2584-2631`): `add_text()` routes
to `self.table_cell_content` whenever `self.in_table and
hasattr(self, "table_cell_content")` — and `table_cell_content` is a plain
Python instance attribute that, once created by the FIRST table's
`visit_entry`, is reset to `[]` (not deleted) at the end of every
`depart_entry`, so it **persists as an existing (empty) attribute for the rest
of the translator's lifetime**. When the SECOND table's caption is visited
(before any of its own `visit_entry` calls), `self.in_table` is already `True`
(set at the top of `visit_table`) and `table_cell_content` already exists
(stale from table 1) — so any `add_text()` call made while processing that
caption is silently swallowed into the dead stale buffer, never read, never
appended to `self.body`. `[VERIFIED: live 2-table sphinx-build]`

**This is the exact defect PR#98 fixed upstream** (confirmed via
`gh pr diff 98 --repo YuSabo90002/typsphinx`, reproduced below in Code
Examples) — its root-cause fix is `del self.table_cell_content` at the end of
`depart_table`, not merely resetting to `[]`. The current codebase's
`depart_table` (`translator.py:2422-2485`) has NO such cleanup today (only
resets `table_cells`/`table_colcount`/`table_colwidths`) — this must be added.

### Verified Mechanism 3 — Typst's native `figure(kind: table)` numbering and `@label` resolution, plus the xref pipeline is ALREADY generic

Compiled directly with the repo's pinned `typst-py==0.15.0`:

```typst
#figure(table(columns: (1fr,1fr), [A],[B],[1],[2]),
  caption: [First table caption], kind: table) <tbl-first>
#figure(table(columns: (1fr,1fr), [C],[D],[3],[4]),
  caption: [Second table caption], kind: table) <tbl-second>
See @tbl-first and @tbl-second.
```

`typst.compile()` succeeds (11350-byte PDF, no error) — proving `kind: table`
and `@label` references to a `kind: table` figure are both accepted by
`typst-py 0.15.0` without any special preamble. Per Typst's official docs
(https://typst.app/docs/reference/model/figure/), setting `kind: table` (one
of the three kinds — `table`, `image`, `raw` — with automatic supplement
inference) makes the figure use the `"Table"` supplement and the
`counter(figure.where(kind: table))` counter automatically, with no
`base.typ`/preamble change needed — confirming D-01/D-02's "zero `base.typ`
change" claim structurally, not just by inspection. `[CITED:
typst.app/docs/reference/model/figure/]` The literal rendered "Table 1"/"Table
2" glyph text was NOT independently OCR-verified in this session (Typst
renders PDF/SVG text as vector glyph paths, not literal `<text>` elements or a
PDF text layer easily greppable without `pypdf`'s font-CMap-aware
`extract_text()` — this project's own GATE-01 render-gate suite already uses
exactly that pypdf-based extraction and should be reused, see Validation
Architecture) — this is standard, stable, extremely well-documented Typst
behavior (`[CITED]`, not first-hand OCR-verified pixel text in this session).

**Cross-reference pipeline — nothing new required.** A real
`sphinx-build -b typst` with `numfig = True` and
`` See :numref:`my-table` and :ref:`my-table`. `` against a captioned,
`:name:`-tagged table emits, TODAY (before any of this phase's changes):

```typst
par({text("See ")
link(<index:my-table>, 
text("Table 1"))
text(" and ")
link(<index:my-table>, 
text("My Caption"))
text(".")})
```

This is the EXISTING generic `visit_reference`/`depart_reference` same-document
`refid` branch (`translator.py:3543-3559`), driven purely by
`node.get("refid")` — it does not special-case `reftype == "numref"` at all.
It already resolves correctly today, for the current (heading-before-table,
un-figure-wrapped) output, because `_emit_id_anchors(node)` already runs
unconditionally at the top of `visit_table` (`translator.py:2348`) and anchors
every id the table carries. Sphinx's `:numref:` role pre-renders the LINK TEXT
itself (`text("Table 1")`, using Sphinx's OWN `numfig` counter, not Typst's) —
this pre-rendered text is orthogonal to whether the table is figure-wrapped;
D-03's "Typst-native" framing means "do not additionally try to make Typst
recompute or override this text," not "build a new resolution mechanism." No
new `visit_reference`/`pending_xref` code is needed for TBL-02 — **the only
real work item for TBL-02 is avoiding the anchor-collision described in
Critical Pitfall 3 below**, since the anchor mechanism itself already works.
`[VERIFIED: live sphinx-build with numfig=True]`

**Also confirmed via live doctree inspection:** Sphinx auto-assigns an id
(`ids="id1"`) to ANY captioned table — even with no explicit `:name:` — via
its own numfig/reference bookkeeping (identical to the well-known figure
auto-id behavior already documented in this file's `visit_figure` docstring).
This holds regardless of whether `numfig = True` is set. A caption-LESS table
gets NO auto-id. Practically: **every real-world captioned table Sphinx
produces WILL have `node.get("ids")` non-empty by the time `depart_table`
runs** — the "captioned but zero ids" case is reachable only via a hand-built
unit-test doctree (e.g. `nodes.table()` built directly, bypassing Sphinx's
id-assignment transform, exactly as PR#98's own `_build_table()` test helper
does) — not via a real `.rst` → Sphinx pipeline. `[VERIFIED: live doctree
dump via `app.env.get_doctree("index")` with and without `numfig`]`

## Architecture Patterns

### System Flow (doctree → figure-wrapped table)

```
docutils tree (already fully built before ANY visiting begins)
  nodes.table (ids=[] or ["id1"/"my-table"] -- auto/explicit)
    +-- nodes.title           <-- present ONLY if `.. table:: Caption`/csv/list caption given
    +-- nodes.tgroup
          +-- colspec...
          +-- thead (optional) -> row -> entry -> paragraph -> Text/inline
          +-- tbody -> row -> entry -> paragraph -> Text/inline

TypstTranslator.visit_table(node)
  |
  |-- [NEW] pre-check: node.children and isinstance(node.children[0], nodes.title)
  |          -> "is_captioned" flag (children already exist -- tree is complete)
  |-- [CHANGED] _emit_id_anchors(node) call:
  |          if NOT captioned: unchanged, anchor ALL ids now (current behavior)
  |          if captioned: SKIP here -- deferred to depart_table (avoids
  |            double-anchoring ids[0], which depart_table will self-anchor
  |            as the figure's own <label>)
  |-- self.in_table = True; table_cells=[]; table_colcount=0; table_colwidths=[]
  |-- [NEW] self.table_caption = None
  v
(docutils walks children)
  |
  v
TypstTranslator.visit_title(node)          [fires ONLY if captioned]
  |-- [NEW] branch: if self.in_table:
  |       -- buffer via self.table_cell_content = [] (add_text() ALREADY
  |          routes here while in_table=True -- reuse, do NOT self.body-swap)
  |       -- save/restore in_list_item + list_item_needs_separator
  |          (mirrors the admonition-title idiom at translator.py:477-480)
  |       -- return (no heading() emitted)
  v
(title's own inline children stream through normal visitors: visit_Text,
 visit_emphasis, etc. -- each add_text() call routes into table_cell_content,
 preserving inline markup, exactly like a normal table CELL's content does)
  v
TypstTranslator.depart_title(node)
  |-- [NEW] branch: if self._in_table_caption:
  |       -- self.table_caption = "".join(self.table_cell_content).strip()
  |       -- self.table_cell_content = []  (or del -- depart_table cleans up too)
  |       -- restore in_list_item / list_item_needs_separator
  |       -- return
  v
(tgroup/thead/tbody/row/entry visited exactly as today -- UNCHANGED)
  v
TypstTranslator.depart_table(node)
  |-- [UNCHANGED] build table_code via _build_columns_fr_arg()/_format_table_cell()
  |-- [UNCHANGED] :width: -> block(width:)[...] decision (converted_width)
  |-- [NEW] branch on self.table_caption:
  |       None      -> emit exactly as today: table(...) or block(width:)[#table(...)]
  |       not None  -> wrap in figure(table_code, caption: {table_caption}, kind: table)
  |                    -- composed WITH width per D-04:
  |                    block(width:)[#figure(...) <label>]  (block wraps the FIGURE)
  |                    -- bracket-wrap + <label> postfix ONLY if node.get("ids")
  |                       (mirrors depart_figure's ids-branch exactly, translator.py:2123-2132)
  |       [NEW] if captioned: self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
  |             -- anchors any OTHER (propagated-target) ids; self-anchors
  |                ids[0] via the figure's own <label> postfix, deferred from visit_table
  |-- [NEW] self.table_caption = None
  |-- [NEW] if hasattr(self, "table_cell_content"): del self.table_cell_content
  |         (root-cause fix for Verified Mechanism 2 -- PR#98's own fix)
  |-- self.in_table = False; table_cells=[]; table_colcount=0; table_colwidths=[]
  v
Typst compile: figure(kind: table) auto-numbers "Table N" via its own
  counter(figure.where(kind: table)); @label / link(<label>) resolve at the
  semantic pass (already proven generic -- Verified Mechanism 3)
```

### Pattern 1: Reuse `table_cell_content` as the caption buffer (NOT `self.body` swap)

**What:** Buffer the table caption's rendered inline content in
`self.table_cell_content`, exploiting `add_text()`'s EXISTING
`in_table`-gated routing, rather than swapping `self.body` the way
`depart_figure`/`depart_caption` do for figure captions.

**When to use:** Any time buffered content must be captured while
`self.in_table` remains `True` for the duration of the buffering (a table
caption is the only such case in this codebase).

**Why NOT the figure-caption `self.body`-swap idiom:** `depart_caption`'s
figure-caption buffer-swap (`translator.py:2171-2209`) works because figures
are NEVER inside `self.in_table`, so `add_text()` correctly falls through to
`self.body` (the swapped list) unconditionally. A table caption, by
definition, occurs WHILE `self.in_table is True` — so swapping `self.body`
alone does NOT change where `add_text()` routes; every inline visitor called
during caption processing (`visit_Text`, `visit_emphasis`, ...) would still
misroute into `table_cell_content` (stale or fresh), NOT into the swapped
`self.body`. This was confirmed by reading `add_text()`'s exact dispatch
condition and cross-checked against PR#98's actual fix, which deliberately
uses `table_cell_content`, not `self.body`, for exactly this reason.

```python
# Source: gh pr diff 98 --repo YuSabo90002/typsphinx (PR#98's actual fix,
# against the OLD ~2700-line base -- reproduce the INTENT against current code,
# not this literal diff, since current visit_table/depart_table/visit_title
# have all been substantially extended since)
if self.in_table:
    self._in_table_caption = True
    self.table_cell_content = []          # add_text() already routes here
    self._caption_saved_list_state = (
        self.in_list_item, self.list_item_needs_separator,
    )
    self.in_list_item = True              # caption content newline-separates
    self.list_item_needs_separator = False
    return
```

### Pattern 2: Defer id-anchoring for captioned tables to `depart_table` (mirror `depart_figure`)

**What:** For a captioned table, do NOT call `_emit_id_anchors(node)`
unconditionally in `visit_table` (current behavior for ALL tables); instead,
determine "is captioned" via a pre-check (`node.children` already fully built
at `visit_table` time — no need to wait for `visit_title` to fire), skip the
call there when captioned, and call
`self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` in
`depart_table` AFTER the figure's own `<label>` postfix has been emitted —
byte-for-byte the same rule `depart_figure` already uses
(`translator.py:2134-2139`).

**When to use:** Whenever a body element gains a NEW self-anchoring
`<label>`-postfix path that a pre-existing unconditional `_emit_id_anchors`
call would otherwise double-define.

```python
# Source: typsphinx/translator.py:2134-2139 (depart_figure, the established
# rule this pattern mirrors verbatim for depart_table)
self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
```

### Recommended file-level change map

```
typsphinx/translator.py
├── __init__               # add: self.table_caption=None, self._in_table_caption=False,
│                           #      self._saved_table_cell_content_for_caption (if needed)
├── visit_title / depart_title (453-582)  # add in_table branch (mirrors admonition-title idiom)
├── visit_table (2337-2371)               # guard/skip _emit_id_anchors when captioned
├── depart_table (2422-2485)              # figure-wrap branch + composed :width:,
│                                          #   deferred _emit_id_anchors, table_cell_content cleanup
tests/test_translator.py                  # port PR#98's 4 unit tests, adapted to current
│                                          #   cell form ({par({text("...")})}) and
│                                          #   columns: (1fr, 1fr); add a :width:+caption test
│                                          #   and a labeled-table test (ids[0] self-anchor)
tests/fixtures/captioned_table_render_gate/  # NEW GATE-01 fixture dir (conf.py + index.rst)
tests/test_pdf_render_gate.py             # NEW TestCaptionedTableRenderGate class (see
│                                          #   Validation Architecture -- this is the actual
│                                          #   template, not test_package_only_config_gate.py)
```

### Anti-Patterns to Avoid

- **Copying `depart_caption`'s `self.body`-swap idiom verbatim for the table
  caption.** As shown in Pattern 1, this silently misroutes content into a
  stale/fresh `table_cell_content` buffer regardless of the `self.body` swap,
  because `add_text()`'s routing condition checks `self.in_table`, not
  whether `self.body` was swapped.
- **Resetting `table_cell_content` to `[]` instead of `del`-ing it at the end
  of `depart_table`.** `hasattr(self, "table_cell_content")` stays `True`
  either way — only `del` makes the NEXT table's pre-entry `add_text()` calls
  (its own caption, or any anchor emitted before its first `visit_entry`)
  correctly fall through to `self.body`. This is PR#98's actual fix, not
  incidental cleanup.
- **Leaving `visit_table`'s `_emit_id_anchors(node)` call unconditional.**
  This double-anchors `ids[0]` for every captioned table once `depart_table`
  also self-anchors it as the figure's `<label>`, producing a Typst
  `label ... occurs multiple times` compile fatal that will NOT show up in
  translator-only unit tests (they don't compile) — only in the mandatory
  real-compile GATE-01 fixture. This is precisely why D-06 mandates a
  real-compile gate rather than trusting unit-test string assertions alone.
- **Emitting the bracket-wrap `[#figure(...) <label>]` unconditionally.**
  Mirror `depart_figure`'s `elif self._figure_block_width is not None` /
  `else` three-way branch exactly — a captioned table with NO ids (reachable
  only via a hand-built doctree, not real Sphinx output per Verified
  Mechanism 3) must fall to the bare `figure(...)` statement form, not a
  markup-mode bracket with no label to close.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "Table N" numbering | A custom Python counter incrementing per captioned table and interpolating "Table N" text | Typst's native `figure(kind: table)` supplement + `counter(figure.where(kind: table))` | Already proven to compile correctly with zero preamble change (Verified Mechanism 3); a hand-rolled Python counter would also have to track cross-document numbering across `#include()`s, duplicating logic Typst already owns |
| Cross-document/same-document label resolution | A custom link-text resolution or a `reftype=="numref"` special case in `visit_reference` | The existing generic `refid`/`_namespace_label`/`_emit_id_anchors` machinery | Already generic and already handles this exact shape (same-document refid → `link(<label>, ...)`) — verified live; no new code needed for the resolution mechanism itself |
| Inline-markup-preserving caption text | Deriving caption text via `node.astext()` | The buffer-swap idiom (Pattern 1), which routes caption children through the SAME inline visitors (`visit_Text`, `visit_emphasis`, ...) used everywhere else | `node.astext()` bypasses `escape_typst_string()` and inline-markup rendering entirely — this is explicitly called out as the root cause of a past "double-emission/juxtaposition fatal bug" in `depart_caption`'s own docstring (translator.py:2198-2201); a table caption must not repeat that mistake |

**Key insight:** Everything genuinely NEW in this phase is glue code inside
`translator.py` (about 40-60 lines across `visit_title`/`depart_title`/
`visit_table`/`depart_table`) — there is no hand-rollable "problem" to solve
here because Typst's `figure(kind: table)` and this codebase's own
`_emit_id_anchors`/`_namespace_label`/refid-resolution primitives already
solve the two hard sub-problems (numbering, resolution). The actual
engineering risk is entirely in **state-machine correctness** (buffer
routing, anchor timing) — confirmed by the fact that PR#98's upstream author
also hit and fixed exactly the stale-buffer bug, and this reimplementation
must additionally handle the NEW `_emit_id_anchors`-collision risk that
didn't exist on PR#98's much older base (that base predates the
`_emit_id_anchors`/labeled-figure feature entirely).

## Common Pitfalls

### Critical Pitfall 1: Stray `heading()` before the table (TBL-01 SC#1)

**What goes wrong:** Every captioned table renders with a spurious
section-level heading directly above it, and the caption is ALSO absent from
any figure/caption structure.
**Why it happens:** `visit_title`'s branch dispatch only recognizes
`nodes.Admonition`/`nodes.topic`/`nodes.section` parents (see Verified
Mechanism 1); `nodes.table` matches none, so it silently falls through to the
generic heading-emission path.
**How to avoid:** Add an explicit `self.in_table` (or
`isinstance(node.parent, nodes.table)`) branch in `visit_title`/`depart_title`,
checked BEFORE (or as a sibling to) the Admonition/topic check.
**Warning signs:** `"heading(" in output` for any table-caption unit test; a
compiled PDF showing an unwanted numbered section heading directly above a
table.

### Critical Pitfall 2: `add_text()` misroutes buffered caption content into a stale (or fresh-but-wrong) `table_cell_content`, even with a `self.body` swap

**What goes wrong:** A caption-buffering implementation that mimics
`depart_caption`'s figure-caption `self.body`-swap idiom appears correct in
isolation (single-table unit test may even pass, since `table_cell_content`
doesn't yet exist for the FIRST table) but silently breaks for any table
after the first, or for any caption containing inline markup whose visitor
calls `add_text()` more than once.
**Why it happens:** `add_text()`'s dispatch condition is
`self.in_table and hasattr(self, "table_cell_content")` — it does not consult
`self.body` at all. Swapping `self.body` has zero effect on this routing
decision. See Pattern 1 and Verified Mechanism 2 for the live-reproduced
proof.
**How to avoid:** Buffer via `self.table_cell_content` (which `add_text()`
already targets), per PR#98's actual fix — not via a `self.body` swap.
**Warning signs:** A 2-table fixture where the SECOND table's caption is
silently absent from output (not malformed — literally absent); this is
invisible in any single-table unit test, which is exactly why D-06 mandates
a 2+-table real-compile fixture.

### Critical Pitfall 3: `_emit_id_anchors` double-anchor collision for captioned tables (TBL-02 SC#5)

**What goes wrong:** `visit_table` (`translator.py:2348`) calls
`self._emit_id_anchors(node)` UNCONDITIONALLY, before the title/caption child
has even been visited (so before it's known whether the table will end up
figure-wrapped with its own `<label>`). If `depart_table` later ALSO
self-anchors `ids[0]` as the figure's `<label>` postfix (mirroring
`depart_figure`), that id is defined TWICE in the emitted Typst source, and
`typst.compile()` aborts at its semantic pass with
`label ... occurs multiple times` — a real, compile-fatal regression that
NO translator-only unit test (which never compiles) would catch.
**Why it happens:** `_emit_id_anchors`'s call site predates this phase's
figure-wrap work and was written when tables never self-anchored via a
markup-bracket `<label>` postfix at all — only via the generic
"anchor every id" path.
**How to avoid:** Pre-check whether the table is captioned in `visit_table`
(the tree is already fully built — `node.children and
isinstance(node.children[0], nodes.title)` is reliable and available
immediately, no need to wait for the title visitor to fire). If captioned,
skip the `visit_table`-time `_emit_id_anchors(node)` call entirely and defer
to `depart_table`'s `_emit_id_anchors(node, skip_ids=set(node.get("ids",
[])[:1]))` call (mirroring `depart_figure` verbatim), placed AFTER the
figure's own `<label>` close. Non-captioned tables keep the current
unconditional `visit_table`-time call, unchanged.
**Warning signs:** A real-compile GATE-01 fixture with a `:name:`-tagged
captioned table raises `TypstCompilationError` / "label ... occurs multiple
times"; this will NOT appear in `tests/test_translator.py` unit tests (they
never call `typst.compile()`), reinforcing why the mandatory GATE-01
real-compile fixture (D-06) is the correct verification bar, not a
substitute for it.

### Pitfall 4: `:numref:` display text is Sphinx's own numbering, not (necessarily) Typst's

**What goes wrong:** A GATE-01 fixture author might expect the compiled PDF's
`:numref:` link text to literally read whatever Typst's OWN
`counter(figure.where(kind: table))` would produce, and be confused when it
instead reads Sphinx's pre-rendered numfig text.
**Why it happens:** Sphinx's `:numref:` role is resolved (link text
pre-rendered) during the `doctree-resolved` phase, BEFORE the translator ever
sees the `reference` node — this is orthogonal to whatever Typst later
computes for the figure's own visible caption/supplement.
**How to avoid:** Per D-03, this is explicitly accepted/deferred scope — the
GATE-01 fixture's `:numref:`-resolves case should assert the LINK RESOLVES
(no dangling/duplicate-label compile error, `link(<label>` present, no
`link("",`) rather than asserting a SPECIFIC "Table N" string matches between
Sphinx's numfig text and Typst's own figure numbering.
**Warning signs:** A fixture conf.py without `numfig = True` — `:numref:`
still resolves the label (verified: label-anchoring is refid-driven, not
numfig-driven) but Sphinx emits a build WARNING and a different fallback text
shape; setting `numfig = True` in the GATE-01 fixture's `conf.py` produces the
cleanest, warning-free "Table 1"-style text and should be preferred.

## Code Examples

### Before (current bug, live-verified) — single captioned table

```typst
[#metadata(none) <index:my-table>]
heading(level: 1, {text("My Caption")})

table(
  columns: (3fr, 3fr),
  table.header({par({text("A")})}, {par({text("B")})}),
  {par({text("1")})}, {par({text("2")})},
)
```

### Before (current bug, live-verified) — SECOND table in one document, caption silently vanishes

```typst
[#metadata(none) <index:second-table>]
table(
  columns: (3fr, 3fr),
  table.header({par({text("C")})}, {par({text("D")})}),
  {par({text("3")})}, {par({text("4")})},
)
```
(no "Second Caption" text anywhere in the emitted source)

### After (target shape, D-04 composed with `:width:`)

```typst
block(width: 80%)[#figure(
table(
  columns: (3fr, 3fr),
  table.header({par({text("A")})}, {par({text("B")})}),
  {par({text("1")})}, {par({text("2")})},
),
  caption: {text("Width Caption")},
  kind: table
) <index:width-table>]
```

### After (target shape, no `:width:`, captioned, no other propagated ids)

```typst
[#figure(
table(
  columns: (3fr, 3fr),
  table.header({par({text("A")})}, {par({text("B")})}),
  {par({text("1")})}, {par({text("2")})},
),
  caption: {text("My Caption")},
  kind: table
) <index:my-table>]
```

### PR#98's actual upstream fix (fetched via `gh pr diff 98`), against its OLD ~2700-line base — the INTENT to port, not the literal diff

```python
# Source: gh pr diff 98 --repo YuSabo90002/typsphinx
# visit_title (new branch, added BEFORE the existing heading-emission code):
if self.in_table:
    self._in_table_caption = True
    self.table_cell_content = []
    self._caption_saved_list_state = (
        self.in_list_item, self.list_item_needs_separator,
    )
    self.in_list_item = True
    self.list_item_needs_separator = False
    return

# depart_title (new branch, added BEFORE the existing heading-close code):
if self._in_table_caption:
    self.table_caption = "".join(self.table_cell_content).strip()
    self.table_cell_content = []
    (self.in_list_item, self.list_item_needs_separator) = self._caption_saved_list_state
    self._in_table_caption = False
    return

# depart_table (root-cause stale-buffer fix, appended at the very end):
self.in_table = False
self.table_cells = []
self.table_colcount = 0
self.table_caption = None
if hasattr(self, "table_cell_content"):
    del self.table_cell_content
```

Current `depart_table` (`translator.py:2477-2485`) resets `table_cells`/
`table_colcount`/`table_colwidths` but has NO `table_cell_content` cleanup —
this `del` line must be added as part of this phase's fix, or the stale-buffer
bug (Verified Mechanism 2) persists even after the caption-buffering feature
is added (it would just also swallow the SECOND table's caption during
capture, same as today).

## State of the Art

| Old Approach (this repo, pre-phase) | Current/Target Approach | When Changed | Impact |
|--------------------------------------|--------------------------|---------------|--------|
| `.. table:: Caption` → stray `heading()` + plain `table()`, caption discarded/misrouted | `figure(table(...), caption: {...}, kind: table)`, native Typst numbering, `<label>` cross-ref | This phase | Captioned tables become numbered, cross-referenceable, and lose the spurious heading |
| Table id-anchoring: unconditional `_emit_id_anchors(node)` at `visit_table`-time for every table | Conditional: unconditional for non-captioned tables (unchanged); deferred to `depart_table` with `skip_ids={ids[0]}` for captioned tables | This phase | Avoids the double-anchor `label ... occurs multiple times` compile fatal introduced by the new figure `<label>` postfix |

**Deprecated/outdated:** None — this is a bug-fix/feature-completion
reimplementation of an external contributor's PR against a much-evolved
codebase, not a migration away from a previously-endorsed approach.

## Assumptions Log

> All claims below were either verified via a live `sphinx-build`/
> `typst.compile()` round-trip in this session, verified by reading the
> current `typsphinx/translator.py` source directly, or fetched from PR#98's
> actual diff/body via `gh pr diff`/`gh pr view`. The one exception:

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Typst's `figure(kind: table)` visibly renders "Table N" text in the compiled PDF glyph stream (not independently OCR/text-layer-verified this session — PDF/SVG text is vector glyph paths, not greppable without pypdf's CMap-aware extraction) | Verified Mechanism 3 | Extremely low — this is stable, official, widely-relied-upon Typst stdlib behavior (`[CITED: typst.app/docs/reference/model/figure/]`), and the phase's own GATE-01 fixture (using `pypdf.PdfReader(...).extract_text()`, an established pattern already in this repo) will independently prove it during implementation regardless |

**If this table is nearly empty:** correct — nearly every substantive claim in
this research was directly verified against live code/compile/PR evidence
this session, not training-data recall. The one residual assumption (A1) is
self-resolving at implementation time via the mandatory GATE-01 pypdf-based
fixture.

## Open Questions

1. **Should a caption's inline `literal` (inline code) content get the
   table-cell zero-width-space (ZWSP) wrap-hint treatment
   (`translator.py:1242-1254`)?**
   - What we know: that ZWSP hack is gated on `self.in_table` and exists to
     help Typst's line-breaker wrap long dotted/underscored identifiers
     *inside a narrow fr-column table cell*. If the caption-buffering
     implementation keeps `self.in_table = True` throughout (as Pattern 1
     recommends, reusing `table_cell_content`), a caption containing inline
     code (e.g. `` .. table:: See ``foo.bar_baz`` ``) would also receive this
     ZWSP treatment, even though a caption is not laid out in a narrow
     fr-column.
   - What's unclear: whether this is harmless (ZWSP is invisible either way)
     or cosmetically undesirable in a caption's wider layout context.
   - Recommendation: treat as harmless by default (zero-width space has no
     visible effect outside of enabling a break opportunity) and not worth a
     special-case; flag only if a GATE-01 fixture with an inline-code caption
     surfaces a visible artifact.
2. **Exact wording/shape of the `csv-table`/`list-table` "lighter caption-regression case"
   D-06 asks for** — CONTEXT.md says "one lighter caption-regression case
   each," without prescribing assertions. Recommendation: reuse the SAME
   sentinel-token + pypdf-`extract_text()`-count pattern established by
   `TestFigureCaptionRenderGate` (see Validation Architecture) — a single
   captioned `csv-table` and a single captioned `list-table`, each asserting
   the caption sentinel appears exactly once and no stray `heading(` leaks
   into the emitted `.typ` source.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | Real-compile GATE-01 fixture, `-b typstpdf` | Yes | 0.15.0 (pinned `>=0.15.0,<0.16` in `pyproject.toml`/`uv.lock`) | — |
| `pypdf` | PDF text-extraction assertions in the GATE-01 fixture (established pattern, `tests/test_pdf_render_gate.py`) | Yes | 6.14.2 | — |
| `sphinx` | `sys.executable -m sphinx` subprocess builds used by every fixture test | Yes (Sphinx v9.1.0 observed in this session) | — | — |

No missing dependencies; nothing blocks this phase.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (testpaths=`tests`, `error::DeprecationWarning` strict filter) |
| Quick run command | `pytest tests/test_translator.py -k table -x` |
| Full suite command | `pytest --cov=typsphinx --cov-report=term-missing` (or `tox -e cov`) |

### GATE-01 fixture — template correction from CONTEXT.md

CONTEXT.md cites `tests/test_package_only_config_gate.py` as the GATE-01
template. That file's pattern (class-scoped `build` fixture,
`TYPST_AVAILABLE` skip guard, real `-b typstpdf` compile, pre-fix-basis
failure-proof class) IS the right STRUCTURAL template and should be reused —
but its ASSERTION STYLE (matching strings in the emitted `.typ` SOURCE text)
is built for CONFIG→OUTPUT diffing, not for proving rendered CONTENT (a
caption's actual text, a cross-reference's actual resolved link) reached the
compiled PDF. This repo already has a MORE precisely-matching precedent for a
**node-handler** (not config) GATE-01 fixture:
`tests/test_pdf_render_gate.py`, specifically `TestFigureCaptionRenderGate`
(sentinel-token + `pypdf.PdfReader(...).extract_text()` + exact-count
assertion, guarding a figure-caption double-emission bug) and
`TestXrefRefidRenderGate` (asserting `link(<` presence, no `link("",`, and
that both the section-anchor's AND the referenced target's link text reached
the extracted PDF text). **Recommendation: model the new
`captioned_table_render_gate` fixture and its test class directly on these
two existing classes**, combining:
- `test_package_only_config_gate.py`'s class-scoped `build` fixture idiom
  (build once, assert many times) and `TYPST_AVAILABLE` skip-guard style, and
- `test_pdf_render_gate.py`'s `TYPST_AVAILABLE and PYPDF_AVAILABLE` combined
  skip guard, sentinel-token-per-caption convention, and
  `full_text.count(SENTINEL) == 1` exact-once assertion style, plus its
  existing `LEAK_SIGNATURES = ("par({", 'text("', 'raw("')` no-literal-leak
  check.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TBL-01 (SC#1: no stray heading, native numbering) | `.. table:: Caption` → `figure(..., kind: table)`, no `heading(` | unit + real-compile | `pytest tests/test_translator.py -k captioned_table -x` | ❌ Wave 0 (port PR#98's 4 tests, adapted) |
| TBL-01 (SC#2: caption-less stays plain) | No-caption table never figure-wrapped | unit (already exists as `test_table_conversion`, needs a negative assertion added) | `pytest tests/test_translator.py -k table_conversion -x` | Partial — extend existing test with `assert "figure(" not in output` |
| TBL-01 (SC#3: caption+width composed) | `block(width:)[#figure(...) <label>]` | real-compile (GATE-01 fixture) | new pytest class in `test_pdf_render_gate.py` | ❌ Wave 0 |
| TBL-01 (SC#4: 2nd+ table keeps its own caption) | 2-table doc, both captions present exactly once | unit (port PR#98's `test_table_caption_not_lost_after_previous_table`) + real-compile | `pytest tests/test_translator.py -k stale -x` | ❌ Wave 0 |
| TBL-02 (SC#5: `:numref:`/`:ref:` resolves) | `link(<label>` present, no dangling/duplicate label, real compile succeeds | real-compile (GATE-01 fixture) | new pytest class in `test_pdf_render_gate.py` | ❌ Wave 0 |
| D-05 (csv-table/list-table caption regression) | Lighter single-caption regression per directive type | real-compile (sentinel+count) | same GATE-01 fixture, additional `.rst` sections | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_translator.py -k table -x` (fast,
  no compile)
- **Per wave merge:** `pytest tests/test_pdf_render_gate.py -k captioned -x`
  (real compile, slower — marked `@pytest.mark.slow`) + full
  `pytest tests/test_translator.py`
- **Phase gate:** `pytest --cov=typsphinx --cov-report=term-missing` green
  before `/gsd-verify-work`, plus the mandatory GATE-01 fixture's red→green
  proof recorded in the plan's SUMMARY (per D-06/D-09 convention already
  established by this repo's other GATE-01 fixtures)

### Wave 0 Gaps

- [ ] `tests/fixtures/captioned_table_render_gate/conf.py` + `index.rst` —
      new GATE-01 fixture: 2+ captioned tables (distinct sentinel captions),
      one `:width:`+caption composition case, one `:numref:`/`:ref:` case
      (`numfig = True`), one lighter `csv-table` caption case, one lighter
      `list-table` caption case
- [ ] New test class in `tests/test_pdf_render_gate.py` (e.g.
      `TestCaptionedTableRenderGate`), modeled on `TestFigureCaptionRenderGate`
      + `TestXrefRefidRenderGate`
- [ ] Ported/adapted unit tests in `tests/test_translator.py`: PR#98's 4 tests
      (`test_captioned_table_renders_as_figure`,
      `test_table_caption_supports_inline_markup`,
      `test_table_caption_not_lost_after_previous_table`,
      `test_uncaptioned_table_not_wrapped_in_figure`) — assertions must be
      adapted from PR#98's old cell form (`text("Header 1")`, `columns: 2`) to
      current form (`{par({text("Header 1")})}`, `columns: (1fr, 1fr)`)
- [ ] A NEW unit test not present in PR#98 (since its base predates
      `_emit_id_anchors`): a captioned table WITH an explicit `:name:`/ids,
      asserting exactly one `<label>` definition for that id (guards Critical
      Pitfall 3's double-anchor regression at the unit-test layer, in
      addition to the real-compile gate)
- Framework install: none — pytest, typst-py, pypdf all already present

## Security Domain

`security_enforcement` is enabled (ASVS level 1) in `.planning/config.json`.
This phase's attack surface is unchanged from the existing figure/table
translation path — no new untrusted-input handling is introduced.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Build-time CLI tool, no auth surface |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Yes (reused, not new) | Caption text reaches Typst source exclusively through the EXISTING inline-visitor chain (`visit_Text` → `escape_typst_string()`), the same escaping every other body element already uses — no new raw-string interpolation path is introduced. `escape_typst_string()` (translator.py:24-55) remains the single source of truth. |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Typst source-injection via unescaped caption text (a caption containing `"`, `\`, or a literal `<label>`-like sequence breaking out of the `caption: {...}` code block) | Tampering | Route ALL caption text through the existing inline-visitor chain (never `node.astext()` — see Don't Hand-Roll table), which already applies `escape_typst_string()` at every `visit_Text` call; do not introduce a new, parallel raw-text path for the caption |
| Duplicate/dangling Typst label causing a full-document compile abort (a build-availability concern, not a confidentiality one, but worth naming since it's this phase's dominant verified risk) | Denial of Service (build-time) | Critical Pitfall 3's fix (deferred, `skip_ids`-guarded `_emit_id_anchors` call) — already the phase's primary implementation task |

## Sources

### Primary (HIGH confidence — verified this session)
- `typsphinx/translator.py` (current repo state) — `visit_title`/`depart_title`
  (453-582), `visit_table`/`_build_columns_fr_arg`/`_format_table_cell`/
  `depart_table` (2337-2485), `visit_figure`/`depart_figure` (2039-2151),
  `_emit_id_anchors` (311-382), `add_text` (253-267), `visit_entry`/
  `depart_entry` (2584-2631), `visit_reference`/`depart_reference`
  (3446-3623+), `_namespace_label` (3202-3238) — read directly, line numbers
  cross-checked against CONTEXT.md's citations (found accurate to within 0-1
  lines; no meaningful drift despite the file's growth to ~4900 lines)
- Live `sphinx-build -b typst` round-trips (this session) — single captioned
  table, 2-table stale-buffer repro, `:width:`+caption composition, `:numref:`/
  `:ref:` resolution, auto-id-assignment behavior with/without `numfig`
- `typst.compile()` (typst-py 0.15.0, pinned in this repo) — direct
  `figure(kind: table)` + `@label` compile-validity check
- `gh pr diff 98 --repo YuSabo90002/typsphinx` / `gh pr view 98` — PR#98's
  actual title, body, and full diff (the reimplementation's design source)
- `tests/test_pdf_render_gate.py` — `TestFigureCaptionRenderGate`,
  `TestXrefRefidRenderGate`, `LEAK_SIGNATURES`, `TYPST_AVAILABLE`/
  `PYPDF_AVAILABLE` skip-guard pattern
- `tests/test_package_only_config_gate.py` — class-scoped `build`-fixture
  structural pattern
- `pyproject.toml` / `uv.lock` — `typst-py` pin (`>=0.15.0,<0.16`, resolved
  `0.15.0`), pytest config

### Secondary (MEDIUM confidence)
- https://typst.app/docs/reference/model/figure/ — `kind`/`supplement`
  auto-inference for `table`/`image`/`raw` kinds (official Typst docs,
  fetched via WebSearch this session)

### Tertiary (LOW confidence)
- None — every substantive claim in this document traces to a Primary or
  Secondary source above.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies; both `typst-py` and `pypdf`
  already pinned/installed and already used by this exact test pattern
- Architecture: HIGH — the full doctree→translator→Typst flow was traced via
  live compiles at every step, not inferred from documentation alone
- Pitfalls: HIGH — all three Critical Pitfalls are backed by either a live
  reproduction (1, 2) or a direct code-path read plus the mechanics of
  `depart_figure`'s established precedent (3)

**Research date:** 2026-07-23
**Valid until:** 30 days (stable, single-repo, no external API/version churn
expected before this phase executes) — re-verify the `typst-py` pin and
Typst's `figure(kind:)` docs URL if this research is reused after a
`typst-py` version bump.
