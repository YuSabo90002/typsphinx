---
created: 2026-08-03T21:24:40+09:00
title: A captioned table emits only its `:name:`-derived Typst label and drops the id of an immediately preceding standalone target, leaving a dangling label that fails the compile
area: translator
resolves_phase: 42
roadmap_entry: "Phase 42 / TBL-03 (promoted 2026-08-03 from backlog 999.2)"
source: .planning/seeds/SEED-002-captioned-table-drops-preceding-target-label.md (promoted 2026-08-03)
files:
  - typsphinx/translator.py (`depart_table` at line 3249 — the captioned vs. caption-less branch)
  - typsphinx/translator.py (line 3318-3328 — the captioned path self-anchors `node["ids"][0]` as the figure's `<label>`)
  - typsphinx/translator.py (line 3341 — `_emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))`)
  - typsphinx/translator.py (`visit_target` at line 3689 / `depart_target` at line 3763)
---

## Problem

Reported by the project owner on 2026-08-03, verbatim:

> キャプション付き表で typsphinx は Typst ラベルを `:name:` 由来の 1 個しか出さず、直前の独立ターゲットの id を捨てる。リンクだけ残り dangling label で失敗。キャプションなしの表は正常。

In English: for a **captioned** table, typsphinx emits only one Typst label — the one derived from
`:name:` — and drops the id contributed by a standalone target (`.. _label:`) placed immediately
before the table. The reference to the dropped label still survives in the output, so the Typst
compile fails on a dangling label. A **caption-less** table is reported to behave correctly.

This is a hard compile failure, not a cosmetic degradation: the document does not build. It is also
squarely in the project's stated core value — a reference the project emits must actually resolve —
applied to intra-document cross-references.

**Reproduction status: NOT yet reproduced in-repo.** The statement above is the owner's report. No
minimal `.rst` case, no captured Typst error text, and no observed `node["ids"]` contents have been
recorded yet. Establish those first (see Acceptance below) — do not start from the hypothesis in the
next section.

## Status

Filed 2026-08-03 as **backlog Phase 999.2** in `.planning/ROADMAP.md` (§ Backlog), at the owner's
direction, and **promoted the same day into v0.7.0 as Phase 42 / requirement TBL-03** at
`/gsd-review-backlog`. The todo stays **pending** until the phase executes — the ROADMAP Phase 42
entry is the sequencing record, this file stays the detail record. Next action:
`/gsd-discuss-phase 42`.

Not a v0.7.0 regression: the captioned-table `figure()` wrap it lives in is TBL-01/TBL-02 from
Phase 25 (v0.6.3, shipped 2026-07-25), so this has shipped in every release since.
**Superseded at promotion:** this record originally said the defect does not block the pending
v0.7.0 publish. The owner decided on 2026-08-03 that it does — `/gsd-complete-milestone` now runs
after Phase 42 verifies. Phase 42's SC#6 additionally owns reconciling Phase 41's CHANGELOG entry
and invariant sweep with this fix's diff.

## Solution

TBD — investigate before choosing an approach.

Breadcrumbs collected 2026-08-03 at the Phase 41 tree. **These are places to start looking, not a
diagnosis:**

- `typsphinx/translator.py:3249` — `depart_table`. The captioned path (`if self.table_caption:`) and
  the caption-less path (`else:`) diverge here, matching the reported "caption-less is fine"
  asymmetry.
- `typsphinx/translator.py:3318-3328` — the captioned path self-anchors **`node["ids"][0]` only** as
  the figure's own `<label>`.
- `typsphinx/translator.py:3341` — `self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))`.
  Note for whoever picks this up: this line *does* appear to emit the remainder ids (`ids[1:]`), and
  carries an in-code rationale (TBL-02 / Critical Pitfall 3) that re-anchoring `ids[0]` here would be
  a Typst "label ... occurs multiple times" fatal. So the drop may originate **upstream** — the
  standalone target's id may never reach `node["ids"]` at all, or may land at an index this logic
  skips. Confirm which before assuming the fix belongs at this line; a naive change here risks
  trading a dangling label for a duplicate-label fatal.
- `typsphinx/translator.py:3689` / `:3763` — `visit_target` / `depart_target`, which handle the
  standalone `.. _label:` preceding the table.
- `typsphinx/translator.py:517` — an existing note that a captioned **figure** likewise self-anchors
  `ids[0]`. The table path was modelled on `depart_figure` (Phase 25, D-04), so the same class of
  bug may apply to captioned figures. Untested — check it as part of the same investigation.

Related history: the captioned-table `figure()` wrap is TBL-01/TBL-02 from Phase 25.

## Acceptance

- [x] A minimal `.rst` snippet reproduces the failure, with the Typst error text captured verbatim
- [x] The actual `node["ids"]` / `node["names"]` contents in the failing case are recorded, settling
      whether the target's id reaches `depart_table` at all
- [x] Whether captioned **figures** exhibit the same drop is answered either way
- [x] A GATE-01-style fixture is recorded RED before the fix lands (project convention)
- [x] The fix does not regress the caption-less path (byte-for-byte unchanged, Phase 25 SC#2) and does
      not introduce a duplicate-label fatal

## Resolution

Closed by **Phase 42 (Captioned Table Drops Preceding Target Label)**, completed 2026-08-04 —
6/6 plans, verification `passed` 6/6 SC, requirement TBL-03 validated.

The root cause was not a misplaced anchor but a **discarded** one. `depart_table`'s trailing
`_emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))` fired while `self.in_table` was
still `True`, so `add_text()` diverted the propagated-target anchor into `self.table_cell_content`
— a buffer `del`eted a few statements later and never read again. The whole production fix is that
one call moved past `self.in_table = False`, gated on a `was_captioned` boolean captured before
`self.table_caption` is reset (`e5575f3`, the only commit in the phase touching `typsphinx/`).

Answers to the questions this todo left open:

- **The target's id does reach `depart_table`** — `node["ids"] == ['tbl-name', 'tbl-target']`,
  recorded in `42-GATE-EVIDENCE-01.md` along with the verbatim
  `TypstError: label \`<index:tbl-target>\` does not exist in the document`.
- **Captioned figures do NOT share the drop** — measured, not inferred; `add_text` never consults
  `self.in_figure`. `42-GATE-EVIDENCE-02.md`. A permanent figure-side regression gate
  (`tests/test_figure_propagated_target_render_gate.py`) now guards that path.
- **No duplicate-label fatal was introduced** — `skip_ids` was carried across byte-for-byte, and the
  emitted `.typ` for all four failing shapes was checked for duplicate labels
  (`42-GATE-EVIDENCE-04.md`).
- **The caption-less path is byte-for-byte unchanged** — proven by an empty two-build diff carrying
  a positive control (two distinct resolved `typsphinx.__file__` paths plus a deliberately non-empty
  diff for the captioned shapes), `42-GATE-EVIDENCE-05.md`.

RED-before-GREEN held structurally: `git merge-base --is-ancestor d28f2c8 e5575f3` returns true, and
wave 1 left `typsphinx/` byte-unchanged, so the real `TypstError` RED was recorded against unfixed
production code. Suite 7 failed / 814 passed → **821 passed / 1 skipped / 0 failed**.

Two related defects were split out rather than absorbed:
`2026-08-03-table-whitespace-only-title-anchor-divergence.md` (D-08, the visit/depart captioned-check
disagreement) and `2026-08-04-nested-table-clobbers-outer-table-state.md` (review IN-02, pre-existing
nested-table state clobber).
