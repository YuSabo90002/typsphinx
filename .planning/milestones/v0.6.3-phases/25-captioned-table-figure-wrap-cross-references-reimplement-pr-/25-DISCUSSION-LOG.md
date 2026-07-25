# Phase 25: Captioned Table Figure Wrap + Cross-References - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-23
**Phase:** 25-captioned-table-figure-wrap-cross-references-reimplement-pr-98
**Areas discussed:** Caption position, Cross-reference fidelity, caption+width composition, Directive/test coverage

---

## Caption position (above vs. below)

| Option | Description | Selected |
|--------|-------------|----------|
| Typst default (below) | Caption below the table; translator-only; `base.typ` unchanged; fidelity to PR#98; keeps translator state-machine risk isolated | ✓ |
| Force tables above | Add `#show figure.where(kind: table): set figure.caption(position: top)` to `base.typ` — template change + separate base.typ risk | |

**User's choice:** Typst default (below).
**Notes:** User asked whether the design could be structured so a *custom template*
can later flip captions to above **without editing `base.typ`**. Confirmed yes:
caption position is a template-layer show-rule concern, the translator emits
position-agnostic output, and — because every captioned table carries
`kind: table` — a user's own `typst_template` can add one show rule
(`#show figure.where(kind: table): set figure.caption(position: top)`) to move
*only tables* above, images untouched. Verified `base.typ` currently has no
figure/caption show rule. This customizability is a free consequence of choosing
"below" and always emitting `kind: table`. The heavier "inject preamble snippet
via config" idea was noted as a deferred future phase.

---

## Cross-reference text fidelity (`:numref:` / `:ref:`)

| Option | Description | Selected |
|--------|-------------|----------|
| Defer to Typst-native | `@label` ref; `figure(kind: table)` supplement auto-renders "Table N"; minimum scope; satisfies SC#5 | ✓ |
| Honor Sphinx numfig format | Reproduce `numfig_format` / custom `:numref:` format strings; needs numfig config read; large scope expansion beyond the PR#98 reimplement intent | |

**User's choice:** Defer to Typst-native.
**Notes:** —

---

## caption + `:width:` composition (nesting order)

| Option | Description | Selected |
|--------|-------------|----------|
| block wraps whole figure | `block(width:)[#figure(table(...), caption:, kind: table) <label>]` — mirrors existing `depart_figure`; `<label>` close inside the same bracket | ✓ |
| block wraps inner table only | `figure(block(width:)[#table(...)], caption:, kind: table)` — width constrains table only; needs a separate label-control path in `depart_table` | |

**User's choice:** block wraps whole figure (existing figure idiom).
**Notes:** Selected preview locked the output shape:
`block(width: 80%)[#figure(table(columns: (1fr, 1fr), ...), caption: {[My caption]}, kind: table) <tbl-label>]`.

---

## Directive / test coverage

| Option | Description | Selected |
|--------|-------------|----------|
| All three | `.. table::` + `csv-table` + `list-table`; single `visit_title`/`depart_table` wiring covers all (all converge on `nodes.table`, caption as `title` child); GATE-01 core on `.. table::` + light csv/list caption regressions | ✓ |
| `.. table::` only | Minimum scope; csv/list captions stay plain table, expand later if needed | |

**User's choice:** All three.
**Notes:** Cost is low — the same structural fact the `:width:` wiring already
relies on means one wiring covers all three directive types.

---

## Claude's Discretion

- `<label>` primary-id selection: mirror `depart_figure` (`ids[0]` self-anchors;
  remaining ids via `_emit_id_anchors(node, skip_ids={ids[0]})`), no collision
  with existing `_emit_id_anchors` anchors (SC#5).
- Buffer save/restore mechanics for the `in_table` caption path — must coexist
  with the existing `visit_title` `in_list_item` / `list_item_needs_separator`
  save/restore, admonition/topic branch, and section-id anchors.

## Deferred Ideas

- Config-injected preamble show rules (lightweight alternative to a full custom
  template for the table-caption-above show rule) — future phase.
- Sphinx `numfig_format` / custom numref format-string fidelity — future
  cross-reference phase.
