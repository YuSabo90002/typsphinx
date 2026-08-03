# Phase 42: Captioned Table Drops Preceding Target Label - Context

**Gathered:** 2026-08-03
**Status:** Ready for planning

<domain>
## Phase Boundary

A captioned table immediately preceded by a standalone target emits Typst labels for **both**
ids — the one that becomes the figure's own `<label>` and the propagated target's — so the
surviving reference resolves instead of aborting the compile on a dangling label. Requirement
TBL-03, promoted from backlog item 999.2 on 2026-08-03.

In scope: the captioned-table emission path in `typsphinx/translator.py`, its RED/GREEN gate
fixtures, a permanent figure regression gate, a repo-wide sweep for the same misrouting class,
and the Phase 41 release-prep reconciliation carried by SC#6.

Out of scope: changing which id owns the figure label, fixing any non-image site the sweep turns
up, and the whitespace-only-title branch divergence. Those are recorded, not acted on.

</domain>

<decisions>
## Implementation Decisions

### Failing-shape scope

- **D-01: the RED gate fixture matrix covers all four measured-failing shapes.** They are: a
  target plus a `:name:`-carrying captioned table; a target plus a captioned table with no
  `:name:`; a captioned table inside a bullet-list item; and two consecutive standalone targets
  before one captioned table. All four were observed aborting a real compile during this
  discussion. The caption-less table case rides along as the byte-invariance control.

- **D-02: the id that owns the figure label does not change.** The first id stays the figure's
  own `<label>` and the remaining ids stay `metadata(none)` anchors, exactly as the code does
  today. Only the fact that the remaining ids never reach the body is fixed. Rationale — because
  typsphinx renders references as `link(<label>, …)`, the jump resolves against either anchor
  form, so promoting the human-authored id would change existing output for no functional gain.

- **D-03: the GREEN side asserts a successful compile plus the structure of the emitted output.**
  Both labels must be present and no label may be defined twice, so the fix cannot silently trade
  the dangling label for the duplicate-label fatal the in-code TBL-02 rationale warns about.

- **D-04: the caption-less path's byte invariance is proven by an empty two-build diff.** Two
  `sphinx-build -b typst` runs at a named pre-fix commit and a named post-fix
  commit, diff recorded in an evidence file. Same method as Phase 36's SC#2, not a golden file
  committed to the repo.

### Fix site

- **D-05: the fix is a call-ordering change inside the table departure handler only.** The
  `_emit_id_anchors` call moves after the point where the in-table flag is cleared. No new
  argument on the shared helper, no change to `add_text`, no other call site touched.

- **D-06: a repo-wide sweep runs for the same misrouting class.** Findings outside the image
  path are filed as todos and not fixed here; a finding in the image path **is** fixed inside
  this phase (owner's condition, stated verbatim during discussion). The sweep's result is
  recorded as evidence either way, including a null result.

- **D-07: the image-path measurement is re-taken formally inside the sweep.** The measurement
  made during this discussion is reference material only and is not admissible as phase evidence.

- **D-08: the whitespace-only-title branch divergence is filed as a todo.** The visit-side and
  depart-side captioned checks use different axes, so a table whose title renders to an empty
  string may emit no anchor on either path. Whether rST can even reach that state is unverified.
  Nothing in this phase is changed for it.

### Figure handling

- **D-09: a permanent figure regression gate is added.** Phase 25 modelled the table path on the
  figure path, so a durable gate stops a future table-side change from being copied back into a
  broken figure path. This also discharges SC#2.

- **D-10: the figure gate covers the three measured shapes.** A `:name:`-carrying figure with a
  preceding target, a figure with no `:name:` and a preceding target, and a figure inside a
  bullet-list item. The two-consecutive-targets shape is not measured for figures and is not
  required.

### Claude's Discretion

- **SC#6 reconciliation mechanics.** The owner accepted the proposed handling without further
  discussion: add the TBL-03 line directly to the CHANGELOG's unreleased `## [0.7.0]` section;
  re-measure Phase 41's SC#4 invariant sweep over a SHA range that includes Phase 42 and write
  the result as a **new** evidence file under this phase's directory rather than editing any
  `41-*` artifact; and if `phase.complete` flips the REL-04 / REL-05 checkboxes or traceability
  rows, revert that before committing (Phase 41 hit this exact behaviour on 2026-08-03).
- Fixture file layout, test module naming, plan and commit granularity, and whether the new
  shapes extend the existing captioned-table fixture or get their own.

### Folded Todos

- `.planning/todos/pending/2026-08-03-captioned-table-drops-preceding-target-label.md` — the
  phase's own detail record, promoted from `SEED-002`. Its Acceptance list is a subset of this
  phase's success criteria; it stays pending until the phase executes. Six other todos scored as
  keyword-only matches and were not presented.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### This phase's scope and history
- `.planning/ROADMAP.md` § Phase 42 — goal, six success criteria, the two open questions, and the
  amended execution-order note that puts Phase 42 after the release-prep phase.
- `.planning/REQUIREMENTS.md` § TBL-03 — the requirement text, and milestone invariant #4 which
  names TBL-03 as an exception that keeps the classic compile-failure RED.
- `.planning/todos/pending/2026-08-03-captioned-table-drops-preceding-target-label.md` — the
  owner's verbatim report, the breadcrumb list, and the acceptance checklist.
- `.planning/milestones/v0.6.3-phases/25-captioned-table-figure-wrap-cross-references-reimplement-pr-/25-CONTEXT.md`
  and `…/25-RESEARCH.md` — Phase 25's D-04 (the table path was modelled on the figure path) and
  Critical Pitfall 3 (the duplicate-label fatal), which the fix must not violate.

### Release reconciliation (SC#6)
- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-HANDOFF.md` — the 7-item publish
  checklist that runs only after this phase verifies; item 6 documents the REL-04 / REL-05
  checkbox-flip hazard.
- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-CONTEXT.md` § D-11 — the scope
  definition of the SC#4 invariant sweep this phase must re-measure.
- `CHANGELOG.md` § `## [0.7.0]` — unreleased; gains the TBL-03 line.

### Code
- `typsphinx/translator.py` — the table departure handler (captioned versus caption-less
  branch), its self-anchoring of the first id, its `_emit_id_anchors` call with the skip set, the
  table visit handler's captioned pre-check, and the helper's own docstring which states the
  in-table routing rule the defect violates.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured during this discussion (scratchpad only — NOT phase evidence)

These measurements answer the ROADMAP's two open questions ahead of time. They were taken in a
throwaway Sphinx project and **were not recorded as artifacts**, so SC#1 and SC#2 still require
their own recorded reproductions. Treat the following as a strong starting hypothesis, not as
settled evidence.

- The failure reproduces. A standalone target immediately before a captioned table produces
  `typst.compile()` failing with `label <index:tbl-target> does not exist in the document`.
- The target's id **does** reach the table departure handler. Observed ids were
  `['tbl-name', 'tbl-target']` with matching names — so the breadcrumb hypothesis that the id
  never arrives is wrong.
- Likely mechanism: the departure handler calls `_emit_id_anchors` while the in-table flag is
  still set, and `add_text` routes into the per-cell buffer while that flag is set, so the anchor
  is appended to a dead buffer and never reaches the body. The table's own emission deliberately
  uses direct body appends to avoid this same hazard, and the table visit handler's comment
  states the rule explicitly.
- The defect is wider than reported. Without `:name:`, docutils' auto-generated id becomes the
  figure's label and the human-authored target id is the one dropped — so a table with no
  `:name:` fails too.
- A table inside a bullet-list item fails. Two consecutive targets before one captioned table
  drop **both** propagated ids.
- Captioned figures are unaffected — with `:name:`, without `:name:`, and inside a list item, both
  the figure label and the propagated anchor are emitted and the document compiles.
- Bare images are unaffected — both the named anchor and the propagated target anchor are emitted.
- A target placed **inside** a table cell routes correctly into the cell content and compiles.
  This is why an unconditional body-direct change to the shared helper would be a regression, and
  it is the measured basis for D-05.

### Reusable assets
- `tests/fixtures/captioned_table_render_gate/` — an existing GATE-01 fixture for TBL-01 / TBL-02
  with a `:numref:` and `:ref:` case already in it, compiled by `tests/test_pdf_render_gate.py`.
- `tests/fixtures/figure_target_caption_render_gate/` — the figure-side analogue, with an image
  asset already committed.
- `tests/fixtures/table_in_list_item_render_gate/` — the list-item table shape already exists as a
  fixture, including a top-level control table for byte-invariance.

### Established patterns
- GATE-01 fixtures live under `tests/fixtures/<name>/` with a `conf.py` plus `index.rst` carrying
  sentinel strings, and are driven from a render-gate test module.
- The RED-before-fix convention: the assertion is recorded failing against the unfixed code in its
  own commit before the fix lands.

### Integration points
- The fix is one call-site move inside the table departure handler; everything else in this phase
  is fixtures, evidence, a sweep, and the Phase 41 reconciliation.

</code_context>

<specifics>
## Specific Ideas

- The owner's condition on the sweep was explicit and narrow: sweep everywhere, but only an
  **image**-path finding gets fixed inside this phase; everything else becomes a todo.
- The owner declined to widen the fix into the shared emission helper, keeping this phase away
  from the shared-seam class of change that Phase 36 had to isolate.

</specifics>

<deferred>
## Deferred Ideas

- The whitespace-only-title branch divergence between the table visit and departure handlers —
  todo to be filed by this phase, not fixed here (D-08).
- Any non-image misrouting the repo-wide sweep discovers — todo only (D-06).
- Promoting the human-authored id to the figure label instead of the first id — rejected for this
  phase (D-02); revisit only if a `:numref:` requirement ever needs it.

</deferred>

---

*Phase: 42-captioned-table-drops-preceding-target-label*
*Context gathered: 2026-08-03*
