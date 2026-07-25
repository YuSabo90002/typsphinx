# Phase 25: Captioned Table Figure Wrap + Cross-References (reimplement PR#98) - Context

**Gathered:** 2026-07-23
**Status:** Ready for planning

<domain>
## Phase Boundary

A captioned table (`.. table:: Caption`, and equally `csv-table` / `list-table`
with a caption) renders as a numbered `figure(table(...), caption: {...},
kind: table)` — native "Table N" numbering, no stray `heading()` above it,
inline markup preserved in the caption — that can be cross-referenced via
`:numref:` / `:ref:`. A caption-less table stays a plain `table()` and is never
speculatively figure-wrapped.

This is a faithful reimplementation of external PR#98 (AlCalzone) against current
`main`. PR#98 cannot be merged mechanically — its base is 2026-06-12 (`6d13667`)
and `translator.py` has since grown ~2700 → ~4900 lines, with `visit_title` /
`depart_title` / `depart_table` all replaced by different implementations
(`in_list_item` control, admonition/topic branching, section-id anchors, the
`:width:` → `block(width: ...)[#table(...)]` wrap, colwidth-based `columns`).
The phase reuses PR#98's design intent and tests, re-implemented on current code.

**Scope anchor:** clarify HOW to wrap/label captioned tables. New capabilities
(custom numref format strings, config-injected preamble show rules, csv/list-only
features) are out of scope — see Deferred Ideas.
</domain>

<decisions>
## Implementation Decisions

### Caption position (above vs. below)
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

### Cross-reference text fidelity (`:numref:` / `:ref:`)
- **D-03:** Defer reference rendering to **Typst-native** behavior. `:numref:` /
  `:ref:` convert to a Typst `@label` reference; `figure(kind: table)`'s
  supplement auto-renders "Table N". This satisfies SC#5 ("working Table N link")
  at minimum scope. Sphinx `numfig_format` / custom numref format strings
  (e.g. `` :numref:`Tbl. %s <t>` ``) are NOT honored — deferred (would require
  reading numfig config and expands beyond the PR#98 reimplement intent).

### caption + `:width:` composition
- **D-04:** The `:width:` `block(width: ...)` wraps the **entire figure**
  (caption included), mirroring the existing `depart_figure` idiom exactly:
  `block(width: 80%)[#figure(table(...), caption: {...}, kind: table) <label>]`.
  Reuse the established figure pattern so the `<label>` close lands inside the
  same markup bracket the `block(...)[...]` opens. Do NOT wrap only the inner
  `table()` (that would need a separately-built label-control path in
  `depart_table`).

### Directive / test coverage
- **D-05:** Cover all three caption-bearing directives — `.. table::`,
  `csv-table`, `list-table`. All converge on `nodes.table` with the caption as a
  `title` child, so a single wiring (`visit_title` buffers when `in_table`;
  `depart_table` consumes) covers all three automatically — same structural fact
  the `:width:` wiring already relies on.
- **D-06:** GATE-01 fixture (mandatory, template `tests/test_package_only_config_gate.py`)
  MUST include, as real `typst.compile()` red→green cases: a **2+-table** document
  (stale-cell-buffer bug is invisible with one table), a **caption + `:width:`**
  composition case (verified *together*, not separately), and a **`:numref:`-resolves**
  case. Add one lighter caption-regression case each for `csv-table` and
  `list-table`.

### Claude's Discretion
- Exact id-selection for the `<label>` (which of a table's `ids` is primary vs.
  anchored as `metadata(none)`): mirror `depart_figure`'s established rule
  (`ids[0]` self-anchors in the `) <label>]` postfix; remaining ids anchored via
  `_emit_id_anchors(node, skip_ids={ids[0]})`). No collision with the table's
  existing `_emit_id_anchors` id anchors (SC#5).
- Buffer/save-restore mechanics for the `in_table` caption path — must not
  collide with the existing `visit_title` save/restore of `in_list_item` /
  `list_item_needs_separator`, the admonition/topic branch, or section-id anchors.

### Folded Todos
- **`.planning/todos/pending/2026-07-23-reimplement-pr-98-captioned-table-figure-wrap.md`**
  (`resolves_phase: 25`). Problem: `.. table:: Caption` stores its caption as a
  `title` child; the generic `visit_title` emits a stray `heading()` before the
  table, and a stale `table_cell_content` buffer from a prior table can swallow
  the caption. Solution: buffer the caption when `in_table`, consume it in
  `depart_table` as a `figure(..., caption:, kind: table)` wrap; compose with the
  existing `:width:` wrap; port AlCalzone's 4 tests, adapting assertions to
  current cell form (`{par({text("...")})}`) and `columns: (1fr, 1fr)`. This todo
  *is* the phase — fully folded into scope. (Reminder from the todo: comment on
  PR#98 to inform AlCalzone that current-code follow-up is needed and that we are
  taking over the reimplementation.)
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & phase scope
- `.planning/REQUIREMENTS.md` — TBL-01 (captioned-table figure wrap; no stray
  heading; caption-less stays plain; inline markup; caption+width; 2nd-table
  stale-buffer), TBL-02 (`:numref:`/`:ref:` → working `<label>` cross-ref, no
  collision with `_emit_id_anchors`).
- `.planning/ROADMAP.md` — Phase 25 section: Goal, 5 Success Criteria, and the
  **GATE-01 standing bar** (mandatory fail-pre-fix real `typst.compile()`
  regression fixture; 2+-table + caption+width + `:numref:`-resolves).
- `.planning/todos/pending/2026-07-23-reimplement-pr-98-captioned-table-figure-wrap.md`
  — the reimplementation spec (folded above); links PR#98
  (https://github.com/YuSabo90002/typsphinx/pull/98).

### Reusable code patterns (the reimplementation's templates)
- `typsphinx/translator.py:2040-2152` (`visit_figure` / `depart_figure`) — the
  captioned-figure idiom to mirror: `[#figure(...) caption: {...} <label>]`
  bracket-wrap, `block(width: ...)[#figure(...)]` composition, and
  `_emit_id_anchors(node, skip_ids={ids[0]})` for propagated targets.
- `typsphinx/translator.py:453-582` (`visit_title` / `depart_title`) — the
  buffer-swap idiom for admonition/topic titles + the `in_list_item` /
  `list_item_needs_separator` save/restore the new `in_table` caption path must
  coexist with.
- `typsphinx/translator.py:2337-2476` (`visit_table` / `depart_table`,
  `_build_columns_fr_arg`, `_format_table_cell`) — current table emission, the
  `:width:` → `block(width: ...)[#table(...)]` wrap, and the documented stale
  `table_cell_content` misrouting hazard (use `self.body.append`, never
  `self.add_text`, at the `table(` / close sites).
- `typsphinx/translator.py:311` (`_emit_id_anchors`) and `_namespace_label` —
  the label/anchor primitives; SC#5 forbids collision with these.
- `typsphinx/templates/base.typ` — verified to have NO figure/caption `#show`
  rule; MUST remain unchanged (D-01).

### Test gate template
- `tests/test_package_only_config_gate.py` — GATE-01 fixture pattern to follow.
- `tests/test_translator.py` — where the ported PR#98 unit tests land.

### Codebase maps (optional background)
- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONVENTIONS.md`,
  `.planning/codebase/TESTING.md`.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`visit_figure`/`depart_figure` captioned-wrap idiom** — near-exact template
  for the table wrap: bracket-wrap `[#figure(...) <label>]` for labeled output,
  `caption: {{...}}` code-block wrap of buffered inline content, and
  `block(width:)[...]` composition. D-04 deliberately keeps the table path
  structurally identical.
- **admonition/topic title buffer-swap** in `visit_title`/`depart_title` — the
  proven save/`self.body = []`/restore pattern to reuse for buffering the table
  caption while preserving inline markup.
- **`_emit_id_anchors` / `_namespace_label`** — reuse for the `<label>`; the
  `skip_ids` argument already exists for the "self-anchor ids[0], anchor the
  rest" split (figure uses it).
- **`_build_columns_fr_arg` / `_format_table_cell`** — unchanged; the figure wrap
  goes around the existing `table()` emission, not through it.

### Established Patterns
- **Unified code-mode document + markup-bracket `<label>` postfix** — Typst
  `<label>` is only valid as a markup-mode postfix, so labeled emission must
  bracket-wrap (`[#... <label>]`). Same fatal-parse-error class Issue #114 found.
- **stale `table_cell_content` buffer hazard** — at `depart_table`'s emission
  sites use `self.body.append`, never `self.add_text`, or output misroutes into a
  prior table's cell buffer (this is exactly the bug SC#4 guards).
- **block-visitor list-item separator** (`list_item_needs_separator`) — the table
  figure wrap must keep honoring it (visit_table already does).

### Integration Points
- Caption ingress: docutils stores `.. table::` (and csv/list) captions as a
  `title` child of `nodes.table`; `visit_title` fires while `self.in_table` is
  True → branch there to buffer instead of emitting a heading.
- Caption egress + label: `depart_table` consumes the buffered caption and wraps
  the (already width-composed) `table()` into `figure(..., caption:, kind: table)`
  with the `<label>` postfix.
</code_context>

<specifics>
## Specific Ideas

- User explicitly wants the "default below, later-switchable to above" property to
  be **structural**: achievable purely via a custom `typst_template` show rule,
  with no `base.typ` edit. Captured as D-01/D-02.
- Output shape locked by D-04 (block wraps the whole figure):
  `block(width: 80%)[#figure(table(columns: (1fr, 1fr), ...), caption: {...}, kind: table) <tbl-label>]`.
</specifics>

<deferred>
## Deferred Ideas

- **Config-injected preamble show rules** — a lightweight `typst_*` config to
  inject arbitrary preamble snippets (e.g. the table-caption-above show rule)
  without supplying a full custom template. Would make D-02's customization
  one-line instead of full-template. Its own future phase, not Phase 25.
- **Sphinx `numfig_format` / custom numref format-string fidelity** — honoring
  `` :numref:`Tbl. %s <t>` `` and localized supplements. Out of scope per D-03;
  candidate for a later cross-reference phase (cf. deferred XREF-02).

### Reviewed Todos (not folded)
- `2026-07-22-citation-node-support-untracked.md` — keyword-matched but belongs to
  the deferred citation-node backlog, not table figures.
- `2026-07-22-dead-config-typst-elements-keys-and-toctree-defaults.md`,
  `2026-07-22-delete-orphan-docs-configuration-rst.md`,
  `2026-07-22-user-guide-configuration-phantom-config-names.md` — these are
  Phase 26 (CONF-04) / Phase 27 (DOC-06/DOC-07) work, not Phase 25.
</deferred>

---

*Phase: 25-captioned-table-figure-wrap-cross-references-reimplement-pr-98*
*Context gathered: 2026-07-23*
