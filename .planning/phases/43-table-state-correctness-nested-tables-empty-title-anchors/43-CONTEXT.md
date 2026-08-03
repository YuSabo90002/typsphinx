# Phase 43: Table State Correctness — Nested Tables + Empty-Title Anchors - Context

**Gathered:** 2026-08-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `translator.py`'s **container state** survive nesting, and make a table's **id anchoring**
independent of whether its caption happens to render to anything.

Concretely, four requirements:

- **TBL-04** — a table nested inside another table's cell no longer clobbers the enclosing table's
  accumulated cells, column count, column widths and caption.
- **TBL-05** — a captioned table whose title renders to an empty string still anchors its ids, so a
  `:ref:` to it resolves instead of aborting the whole Typst compile.
- **FIG-01** *(added 2026-08-04 during this discussion, owner decision — see ROADMAP amendment log)*
  — a figure nested inside another figure keeps the outer figure's caption, ids and state, and the
  inner figure renders inside the outer figure's legend.
- **QUA-01** — `_emit_id_anchors`'s docstring stops calling `depart_figure` the sole `skip_ids` user.

Plus the milestone-invariant obligation the roadmap put on this phase: the milestone branch reaches
`origin` and CI runs against it **during this phase** (SC#5), not at the release PR.

Not in this phase: any other nesting-shaped defect that measurement turns up in a *different*
container (see Deferred Ideas), and any change to how non-nested, non-empty-caption documents render.
</domain>

<decisions>
## Implementation Decisions

### Nesting scope and fixtures

- **D-01:** The GATE-01 RED fixtures cover the **three measured-broken table shapes plus one
  three-deep case**: `list-table` in `list-table`, grid `table` in `list-table`, `list-table` in grid
  `table`, and a three-level nest. The three-deep case is included specifically so the fix is shown to
  generalize over depth rather than over the one shape that was measured first — if a chosen fix
  passes the three two-level shapes but fails three-deep, that is a signal the fix shape is wrong.
  — **Reversibility:** reversible — fixtures are additive.

- **D-02:** **Nested figures are fixed in this phase**, not filed as a todo. Measured 2026-08-04: a
  `.. figure::` inside another figure's caption body lands in a docutils `legend` node; typsphinx has
  no `legend` handler, `sphinx-build` emits `WARNING: unknown node type: <legend>`, the outer caption
  is dropped entirely, and the inner `figure(...)` is injected as a content block straight after the
  outer `image(...)`. The owner's reason for folding it in: it is the same class of change in the same
  file, and making it twice is worse than making it once.
  — **Reversibility:** costly — it widens what SC#4's byte-invariance evidence must cover; backing it
  out after the evidence is recorded would invalidate that recording (the Phase 42 lesson).

- **D-03:** The figure work is tracked as **one new requirement, FIG-01, defined by behaviour**
  ("a nested figure keeps the outer figure's caption, ids and state; the inner figure renders inside
  the legend"), **not** as two requirements split by cause. The `legend` handler and the
  `in_figure`/`figure_caption` nesting-safety are *implementation means* under it. Rationale, measured:
  Sphinx's LaTeX builder does not present these as two layers either — it just nests correctly, with
  the inner figure inside a `sphinxlegend` environment and the outer `\caption{...}\label{...}` intact.
  `REQUIREMENTS.md` and `ROADMAP.md` were amended during this discussion (12/12 mapped; Phase 43 gains
  SC#6, appended not inserted, so SC#1-5 keep their cited numbers).
  — **Reversibility:** costly — undoing means editing REQUIREMENTS.md, the traceability table, the
  coverage counts, the ROADMAP amendment log and STATE.md back out again.

- **D-04:** SC#4's byte-invariance evidence uses the **`42-GATE-EVIDENCE-05.md` two-build method**
  (old tree exported with `git archive` to a separate directory, `typsphinx.__file__` asserted to
  resolve INTO that tree, plus a positive control proving the two builds really ran different code)
  over **all of `docs/source` AND every root under `tests/roots`**. The figure path is in scope now,
  so figure-bearing existing documents must be in the compared corpus, not just table-bearing ones.
  An empty diff means nothing without the positive control.
  — **Reversibility:** reversible.

### TBL-05 — which axis is authoritative

- **D-05:** **Match Sphinx's LaTeX builder: make id anchoring independent of the captioned decision.**
  Rendering keeps `depart_table`'s truthiness check — a table whose title renders empty stays a bare
  `table(...)`, is **not** figure-wrapped, and consumes **no** table number — while its ids get
  anchored on that path too. This reverses an earlier in-discussion answer ("structural check wins")
  after the owner asked for the LaTeX behaviour to be measured; the measurement decided it.

  Measured 2026-08-04, Sphinx 9.1.0, identical `index.rst`:
  - empty-rendered caption, `-b latex` → **no `\sphinxcaption` at all** (so no table number), but
    `\phantomsection\label{\detokenize{index:id1}}\label{\detokenize{index:tbl-target}}` is emitted
    standalone and `\hyperref[tbl-target]` resolves. **No warning.**
  - normal caption, `-b latex` → `\sphinxcaption{REALCAP}\label{index:id1}\label{index:tbl-target}`.

  This is the same "follow the builder Sphinx already ships" reasoning CONF-08 used in Phase 44.
  — **Reversibility:** reversible — it is a branch condition in `depart_table`, local.

- **D-06:** **No new warning** for a caption that renders empty. LaTeX emits none for the identical
  input, and the existing build's warning output stays unchanged.
  — **Reversibility:** reversible.

- **D-07:** The visit-side pre-check **cannot** be made value-aware, and no plan should try. Measured:
  in the reproducing construct the title's child is a `raw` node — `title.astext()` is
  `'<span></span>'` (**non-empty**) while `visit_raw` raises `SkipNode` for `format != typst` so the
  **rendered** result is empty. Any `astext()`-based pre-check therefore misses this exact case. The
  rendered value is only knowable after the title has been visited, i.e. at depart time.

### QUA-01 — docstring scope

- **D-08:** Fix **only** the `skip_ids` "sole user" sentence, naming the actual two callers
  (`depart_figure` at L2518 and `depart_table` at L3370, added in Phase 42). Do not enumerate all
  callers in the docstring. Measured: `_emit_id_anchors` has **21** call sites and only **2** pass
  `skip_ids`; an exhaustive list is exactly the thing that rotted into QUA-01 in the first place.
  Note for the executor: this phase may add or move callers, so make this edit **after** the
  nesting work lands, and re-grep before writing the sentence rather than trusting this count.
  — **Reversibility:** reversible.

### Claude's Discretion

The following were deliberately left to research/planning — the owner did not select them for
discussion, so no decision is locked and the planner should choose on measured grounds:

- **The fix shape for the nested-container state.** Full stack (`list[TableState]` with every
  consumer asking "the innermost frame") versus a snapshot save/restore in `visit_table`/`depart_table`
  that keeps the existing scalar attribute names and leaves all 10 `self.in_table` consumers
  untouched. Constraint that must survive either way: the Phase 25 `table_cell_content` lifetime
  invariant (created by the first `visit_entry`, reset to `[]` not deleted, `del`eted only in
  `depart_table` so `hasattr` goes False for the next table) — see the comment at L3376-3386 and
  todo item 1.
- **Where the inner container's emitted markup is routed** so it lands inside the enclosing cell
  rather than in `self.body` (today `depart_table` appends to `self.body` directly).
- **Test file layout** for the RED gates, and whether the table and figure gates share a file.
- **When in the phase the milestone branch is pushed** (SC#5) and whether a green Windows lane gates
  the handoff to Phase 44.

### Folded Todos

All three of this phase's pre-mapped todos are folded — they are the requirements themselves:

- `.planning/todos/pending/2026-08-04-nested-table-clobbers-outer-table-state.md` → TBL-04. Carries
  the reproducing rST, the byte-identical pre/post-Phase-42 proof that it is pre-existing, and a
  5-item "measure these first" list that is load-bearing for the fix shape.
- `.planning/todos/pending/2026-08-03-table-whitespace-only-title-anchor-divergence.md` → TBL-05.
  Note: its "reachability unknown" status is now **resolved — reachable** (see Specific Ideas), and
  its instruction not to re-run the trailing-whitespace `.. table:: ` probe still stands.
- `.planning/todos/pending/2026-08-04-emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user.md`
  → QUA-01.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap (amended during this discussion)
- `.planning/REQUIREMENTS.md` — TBL-04, TBL-05, **FIG-01 (new)**, QUA-01; traceability now 12/12;
  the "no new node handlers" out-of-scope row now carries FIG-01's stated exception.
- `.planning/ROADMAP.md` §"Phase 43" — SC#1-#6. SC#2 and SC#4 were amended in place; SC#6 is new and
  was **appended** so SC#1-#5 keep the numbers other artifacts already cite (notably SC#5 = the
  milestone-branch push, milestone invariant #5).

### The three source todos
- `.planning/todos/pending/2026-08-04-nested-table-clobbers-outer-table-state.md` — reproducing rST,
  the "measure these 5 things first" list, and the gate requirement (structural RED, since the broken
  output compiles cleanly).
- `.planning/todos/pending/2026-08-03-table-whitespace-only-title-anchor-divergence.md` — the two
  disagreeing checks with line numbers, and the already-run negative probe not to repeat.
- `.planning/todos/pending/2026-08-04-emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user.md`

### Method precedents from Phase 42 (archived under `.planning/milestones/v0.7.0-phases/`)
- `.planning/milestones/v0.7.0-phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-05.md`
  — **the** byte-invariance two-build method D-04 mandates, including the positive control without
  which an empty diff proves nothing.
- `.planning/milestones/v0.7.0-phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-03.md`
  §1.5 — the `depart_table` MISROUTED analysis that produced TBL-03's fix and named this phase's
  TBL-05 divergence.
- `.planning/milestones/v0.7.0-phases/42-captioned-table-drops-preceding-target-label/42-REVIEW.md`
  — IN-02, where the nested-table clobber was first surfaced.

### Code under change
- `typsphinx/translator.py` — `__init__` L161-182 (the scalar state, incl. `in_figure`),
  `add_text` L423-437, `visit_title` L613/L663-672, `depart_title` L735/L753-760,
  `_emit_id_anchors` L481 (docstring L516 area), `visit_table` L3149 (`is_captioned` L3173,
  skip L3174-3175), `depart_table` L3249 (caption truthiness L3304, `was_captioned` L3353,
  `in_table` clear L3355, anchor call L3370, teardown L3372-3388),
  `visit_figure`/`depart_figure` L2439/L2518/L2522, other `in_table` consumers at L1621-1651,
  L5545-5562, L5891-5905.

### Project conventions
- `CLAUDE.md` — worktree-isolated execution is the standing mode: `env -u VIRTUAL_ENV -u
  UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then run everything via `uv run`. Also: do not
  modernize typing imports (`UP006`/`UP035`) in this phase.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`tests/test_*_render_gate.py`** — an established GATE-01 fixture family (`test_wide_table_render_gate.py`,
  `test_citation_render_gate.py`, `test_substitution_definition_render_gate.py`, …) that already does
  `sphinx-build → typst.compile() → pypdf` text extraction. `pypdf>=6.14,<7` is a declared dev
  dependency, so PDF-level assertions need no new dependency (milestone invariant #1 holds).
- **`_emit_id_anchors(node, skip_ids=...)`** — the anchoring primitive TBL-05 needs; no new mechanism
  required, only a call on the path that currently has none.
- **`_build_columns_fr_arg()` / `_format_table_cell()`** — table rendering is already factored out of
  `depart_table`'s branches, so a state change does not force a rendering rewrite.

### Established Patterns
- **Scalar container state.** `in_table` + `table_cells` + `table_colcount` + `table_colwidths` +
  `table_caption` + lazily-created `table_cell_content`, mirrored by `in_figure` + `figure_caption`.
  Both are reset on visit and torn down on depart, which is exactly the defect. `add_text` diverts
  every append on the single `self.in_table` boolean.
- **`table_cell_content`'s deliberate lifetime** (Phase 25 root-cause fix, comment at L3376-3386):
  reset to `[]` at `depart_entry`, `del`eted only at `depart_table`, because `add_text`'s
  `hasattr(self, "table_cell_content")` conjunct depends on it. Any rewrite must preserve or
  consciously supersede this — not accidentally revert it.
- **Anchor placement differs by path.** Non-captioned tables anchor in `visit_table` (before the
  table); captioned tables anchor in `depart_table` **after** `self.in_table` is cleared (Phase 42's
  TBL-03 fix — anchoring before the clear routes the anchor into the doomed cell buffer).

### Integration Points
- `visit_table` / `depart_table` / `visit_entry` / `depart_entry` / `visit_row` / `visit_colspec`.
- `visit_title` / `depart_title` (they borrow `table_cell_content` for the caption, gated on
  `self.in_table` — todo item 2: they need the same frame-awareness or the caption attaches to the
  wrong table).
- `visit_figure` / `depart_figure`, plus a **new** `visit_legend` / `depart_legend`.
- `add_text` — the diversion predicate is the single point every nesting decision flows through.

</code_context>

<specifics>
## Specific Ideas

Everything below was measured in this session, on the main tree, with the repo venv. It is evidence
the researcher should build on, not re-derive.

**1. TBL-05 is reachable, and it is fatal.** Reproducing document:

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

- Doctree: `table ids: ['id1', 'tbl-target']`, first child is a `title` whose only child is a `raw`
  node; `title.astext()` == `'<span></span>'`.
- `-b typst` emits `link(<index:tbl-target>, …)` with **no matching anchor anywhere**.
- `-b typstpdf` → `TypstError: label <index:tbl-target> does not exist in the document`, whole
  document aborted, **zero PDFs**.
- Fixture note: the `:ref:` **must** carry explicit link text. With a bare `` :ref:`tbl-target` ``
  Sphinx itself refuses first — `WARNING: Failed to create a cross reference. A title or caption not
  found` — and degrades to plain text, so the Typst-level failure never happens and the RED does not
  reproduce.

**2. Three table nesting shapes lose the outer table entirely** (all exit 0, no warning, and the
broken output **compiles fine** — so the RED must be structural, not a `TypstError`):

- `list-table` in `list-table` — already recorded in the TBL-04 todo.
- grid `table` in `list-table` — emitted `.typ` is `figure(table(<inner cells>), caption:
  {text("OUTERCAP")}, kind: table)`; `OUTERHEADA` / `OUTERHEADB` / `OUTERPLAIN` are all absent.
- `list-table` in grid `table` — same shape, **plus** the outer table's other cell (`OUTERD`) leaks
  out as a bare `par({text("OUTERD")})` after the figure.

**3. Nested figures fail differently** — via the missing `legend` handler, not (provably) via the
`in_figure` scalar. `WARNING: unknown node type: <legend>`, outer caption `OUTERFIGCAP` gone, and the
inner figure injected as a content block right after the outer `image("img.png")`.

**4. Sphinx's LaTeX builder is the reference behaviour for all three** (no warnings in any case):

- nested figure → outer `\caption{OUTERFIGCAP}\label{index:id1}`, then `\begin{sphinxlegend}` wrapping
  the inner `\begin{figure}…\caption{INNERFIGCAP}\label{index:id2}\end{figure}`.
- grid table in list-table → outer `\sphinxcaption{OUTERCAP}\label{index:id1}` with `OUTERHEADA`,
  `OUTERHEADB`, `OUTERPLAIN` all present and the inner table nested inside the outer cell.
- empty-rendered caption → no `\sphinxcaption`, standalone `\phantomsection\label{…}`.

**5. Typst numbering, measured directly via `typst.compile()` + pypdf.** `caption: {}` and
`caption: none` both render **no visible caption line**, but both still **consume a figure number** —
two empty-caption `kind: table` figures followed by a real one produced `Table 3: real`. This is why
D-05's "not figure-wrapped, consumes no number" matters: figure-wrapping an empty caption would shift
every later table's number by one.

</specifics>

<deferred>
## Deferred Ideas

- **Other scalar-state containers.** The nesting fix should be *designed* against the reachable set,
  but only tables and figures are in this phase. If measurement turns up the same clobber shape in a
  third container, file a todo with the emitted `.typ` — do not widen the phase again.
- **The wider "reachable nesting set" sweep** the TBL-04 todo's acceptance list sketches (table in
  admonition, in definition list, in footnote, …). D-01 deliberately scoped fixtures to the three
  measured shapes plus three-deep instead. Anything found later belongs in its own todo.
- **`docutils` `legend` beyond nested figures.** The `legend` handler FIG-01 adds exists to stop the
  outer caption vanishing. Broader legend styling/typesetting is not in scope.

### Reviewed Todos (not folded)

- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — matched on keywords only.
  Explicitly forbidden here by `CLAUDE.md` and by REQUIREMENTS.md's "Open todos not scoped here".
- `2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md` — `resolves_phase: 44` (BLD-01).
- `2026-08-04-docs-changelog-page-stale-at-0-4-0.md`, `2026-07-25-derive-typst-lang-duplicated-warning-block.md`,
  `2026-07-29-project-md-unterminated-html-comments.md` — `resolves_phase: 45`.
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — `resolves_phase: 46`.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — LNK-01, future requirement, not in v0.7.1.

</deferred>

---

*Phase: 43-Table State Correctness — Nested Tables + Empty-Title Anchors*
*Context gathered: 2026-08-04*
