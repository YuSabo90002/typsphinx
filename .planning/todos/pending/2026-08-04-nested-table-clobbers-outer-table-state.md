---
created: 2026-08-04T00:52:00+09:00
title: A table nested inside a list-table cell clobbers the outer table's in-progress state, silently emitting the inner table's body under the outer table's caption
area: translator
resolves_phase: null
roadmap_entry: null
source: "Phase 42 / 42-REVIEW.md IN-02 (2026-08-03) -- captioned-table-drops-preceding-target-label; independently reproduced by the orchestrator 2026-08-04"
files:
  - typsphinx/translator.py (`__init__` at lines 161-179 -- every table state attribute is a SCALAR: `self.in_table`, `self.table_cells`, `self.table_colcount`, `self.table_colwidths`, `self.table_caption`, plus `self.table_cell_content` created lazily by the first `visit_entry`)
  - typsphinx/translator.py (`add_text` at lines 423-437 -- diverts EVERY append into `self.table_cell_content` on the single boolean `self.in_table`, with no notion of which table is being filled)
  - typsphinx/translator.py (`visit_table` at line 3149 -- sets `self.in_table = True` and resets `table_cells`/`table_colcount`/`table_colwidths` at lines 3194-3197, unconditionally discarding any enclosing table's accumulated cells)
  - typsphinx/translator.py (`depart_table` at line 3249 -- unconditionally sets `self.in_table = False` and resets `table_cells`/`table_colcount`/`table_colwidths`/`table_caption` at lines 3371-3375, so the INNER table's departure tears down the OUTER table's state)
---

## Problem

The translator's entire table state is a set of **scalar** attributes, not a stack. Nothing in
`visit_table` / `depart_table` / `add_text` distinguishes "the table currently being filled" from
"some enclosing table that is still open". docutils permits a `table` node inside a `list-table`
cell, so the nesting is reachable from ordinary rST.

When it nests, the inner table's `depart_table` runs first and unconditionally executes
`self.in_table = False` plus the `table_cells` / `table_colcount` / `table_colwidths` /
`table_caption` resets. That is the OUTER table's in-progress state. The outer `depart_table` then
runs against an already-torn-down state and emits whatever is left.

**The failure mode is not "the outer table disappears" — it is worse than that.** The emitted
document is structurally well-formed and plausible-looking, but it states something false: the
INNER table's body is emitted **underneath the OUTER table's caption**, and every outer cell —
including the header row — is gone. A reader has no signal that anything was dropped.

### Measured 2026-08-04 (orchestrator, main tree, not transcribed from the review)

Probe input (`.. list-table:: Outer table caption` with `:header-rows: 1`, one plain outer cell,
and a nested `.. list-table::` in the other cell):

```rst
.. list-table:: Outer table caption
   :header-rows: 1

   * - OUTERHEADERONE
     - OUTERHEADERTWO
   * - OUTERCELLPLAIN
     - .. list-table::

          * - INNERCELLA
            - INNERCELLB
```

Emitted `index.typ`, verbatim and complete for the table:

```typst
figure(
table(
  columns: (50fr, 50fr),
  {par({text("INNERCELLA")})},
  {par({text("INNERCELLB")})},
),
  caption: {text("Outer table caption")},
  kind: table
)
```

- `OUTERHEADERONE`, `OUTERHEADERTWO`, `OUTERCELLPLAIN` — **all absent from the output entirely.**
- The surviving `table(...)` is the INNER table's body, wearing the OUTER table's
  `caption:` and `kind: table`. The two halves of the figure describe different tables.
- `sphinx-build -b typst` exited 0 with **no warning and no error**.
- `typst.compile()` on the result **succeeds** (17802-byte PDF). There is no downstream error
  surface either — unlike TBL-03, which at least failed loudly at the label-resolution pass.

### Confirmed pre-existing — Phase 42 neither introduced nor worsened it

The identical probe was built against the pre-fix tree at `19a6378` (exported with `git archive`
into a scratch directory; the build's resolved `typsphinx.__file__` was asserted to point INTO that
scratch tree, so the two builds genuinely ran different `depart_table` code) and against the
post-fix main tree. **The two `index.typ` outputs are byte-identical.** Phase 42's change moved one
call site and did not touch nesting state, exactly as its scope fence (D-05) required.

## Status

Filed by the Phase 42 orchestrator at the owner's request after code review surfaced it as IN-02
(classified Info there only because it is out of that diff's blast radius, not because the impact is
minor — silent structural data loss is a direct hit on the project's core value that emitted output
must be faithful).

Deliberately not fixed inside Phase 42: converting scalar state to a stack is a semantics change to
table handling generally, far outside D-05's "move one call past the `in_table` reset" fence, and
it would land after `42-GATE-EVIDENCE-05.md` (SC#4 byte-invariance) and `42-SC4-INVARIANTS.md`
(SC#6 milestone-invariant sweep) had already been recorded over a SHA range ending at the fix
commit — invalidating the range those artifacts measured.

## Solution

Direction, not a prescription. The shape is clear but the blast radius is not yet measured.

**The likely fix** is to replace the scalar attributes with a stack — e.g. a `self._table_stack:
list[TableState]` where `TableState` holds `cells`, `colcount`, `colwidths`, `caption`,
`cell_content` — so `visit_table` pushes and `depart_table` pops-and-restores rather than resets.
`add_text`'s diversion predicate becomes "is the stack non-empty" and appends to the TOP frame.

**Before writing that, measure these, because each one is load-bearing and none is currently known:**

1. **`table_cell_content`'s lifetime is deliberately weird and must not be broken.** The comment at
   `depart_table` (lines 3376-3380) records a Phase 25 root-cause fix: the buffer is created by the
   first `visit_entry` and reset to `[]` rather than deleted, precisely so it persists as an
   existing attribute — `add_text`'s `hasattr(self, "table_cell_content")` conjunct depends on that.
   A stack rewrite must preserve or consciously supersede that invariant, not accidentally revert it.
2. **`visit_title` / `depart_title` reach into the same buffer.** Lines 663-672 and 754-755 borrow
   `self.table_cell_content` to collect a table caption, gated on `self.in_table`. Those two sites
   need the same stack-awareness or the caption will attach to the wrong frame.
3. **Other `self.in_table` consumers exist beyond the table handlers** — at minimum lines 1621-1651
   (a documented independent branch) and the TBL-03 site at 3344-3370. Enumerate all of them
   (`grep -n 'self\.in_table' typsphinx/translator.py`) and decide per-site whether "any table open"
   or "the innermost table" is the right question.
4. **`self.in_figure` (lines 161, 2439, 2522) is the same scalar pattern** and may have the same
   nesting defect on the figure path. Phase 42 measured that `add_text` never consults `in_figure`,
   so figures do not share TBL-03 — but that is a different question from whether nested figures
   clobber each other. Worth a probe in the same investigation.
5. **How far does nesting reach?** This todo measured `list-table` inside `list-table`. Also probe
   `.. table::` (grid table) as the inner and/or outer, a table nested inside a figure, and a
   table nested inside a table nested inside a table, so the fix is designed against the real
   reachable set rather than the one shape that was measured first.

**Gate requirement:** this is a node-handler change, so milestone invariant #4 applies — it needs a
recorded-RED GATE-01 fixture. Unlike TBL-03 the defect does NOT fail the Typst compile (measured
above: it compiles fine), so the RED must be a **structural** assertion over the emitted `.typ`, not
a `TypstError`. The probe in this file is directly usable as that fixture's input; assert that the
outer header text and the outer plain cell are present in the output, and that the caption belongs
to the same table whose cells are emitted.

## Acceptance

- [ ] Enumerate the reachable nesting set (at least: `list-table` in `list-table`, grid `table` in
      `list-table`, `list-table` in grid `table`, table in figure, three-deep) and record which
      shapes lose data, with the emitted `.typ` for each
- [ ] Determine whether `self.in_figure` has the same nesting defect (item 4 above), and either fold
      it into this fix or file it separately with its own measurement
- [ ] Land a recorded-RED GATE-01 fixture asserting the OUTER table's cells and header survive and
      that the caption matches the table it wraps — structural assertions, since the broken output
      compiles cleanly
- [ ] Convert the scalar table state to a stack (or an equivalent that fixes the clobber), keeping
      the Phase 25 `table_cell_content` lifetime invariant intact (item 1 above)
- [ ] Prove the single-table path is byte-for-byte unchanged, by the two-build diff method with a
      positive control (see `42-GATE-EVIDENCE-05.md` for the method — an empty diff means nothing
      unless the two builds are shown to have run different code)
