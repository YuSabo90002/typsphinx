# Phase 43: Table State Correctness — Nested Tables + Empty-Title Anchors - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-04
**Phase:** 43-table-state-correctness-nested-tables-empty-title-anchors
**Areas offered:** Nested-table fix shape, Nesting scope, TBL-05 authoritative axis, Branch push + CI (SC#5)
**Areas selected by the owner:** Nesting scope, TBL-05 authoritative axis

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| 入れ子テーブルの修正形 | Full stack (`TableState`, all 10 `in_table` consumers rewritten) vs. snapshot save/restore keeping the scalar names | |
| 入れ子の対応範囲 | Which nesting shapes are fixed/fixtured; whether the nested-figure defect folds in | ✓ |
| TBL-05 のどちらの軸を採るか | Structural pre-check vs. caption truthiness | ✓ |
| ブランチ push と CI (SC#5) | When the milestone branch reaches origin; whether Windows-lane green gates Phase 44 | |

**Notes:** The two unselected areas are recorded in CONTEXT.md under "Claude's Discretion" rather
than dropped.

---

## Nesting scope

### Q1 — how far do the fixtures reach?

| Option | Description | Selected |
|--------|-------------|----------|
| 実測3形状＋3段重ね | The three measured-broken shapes plus one three-deep case, so depth generality is proven | ✓ |
| 実測3形状のみ | Narrowest fixture set; depth generality left unproven | |
| 到達可能な入れ子を全洗い出し | Enumerate every docutils path that can nest a table (figure, admonition, definition list, footnote…) | |

**User's choice:** 実測3形状＋3段重ね
**Notes:** The broader sweep the TBL-04 todo sketches was moved to Deferred Ideas.

### Q2 — how is the nested-figure breakage handled?

| Option | Description | Selected |
|--------|-------------|----------|
| todo に切り出す | File it with the measurement; different root cause (`legend` unsupported), outside the phase SCs | |
| 本フェーズで一緒に直す | Same class of change, same file — make it once | ✓ |
| in_figure のスカラー問題だけ確かめる | Measure only, fix nothing | |

**User's choice:** 本フェーズで一緒に直す

### Q3 — requirement granularity for the figure work

Asked twice. The first presentation offered 1 requirement / 2 requirements / 1-plus-conditional; the
owner replied **"latexがfigure入れ子になったらどうなるのか？"** — i.e. measure Sphinx's LaTeX builder
before choosing. Measurement was run and the question re-presented with it.

| Option | Description | Selected |
|--------|-------------|----------|
| 1 件（振る舞いで定義） | One behavioural requirement; the `legend` handler and `in_figure` nesting-safety are means | ✓ |
| 2 件（原因層ごと） | Split by cause; the second would close on an unproven symptom | |
| 1 件＋実測結果次第 | Add a second only if the `in_figure` clobber reproduces standalone | |

**User's choice:** 1 件（振る舞いで定義）
**Notes / measurement that decided it:** `-b latex` on the same nested-figure input emits no warning,
keeps `\caption{OUTERFIGCAP}\label{index:id1}`, and wraps the inner figure in `\begin{sphinxlegend}`.
LaTeX does not present the defect as two layers, so the requirement does not either.

### Q4 — byte-invariance corpus (SC#4)

| Option | Description | Selected |
|--------|-------------|----------|
| docs/source 全体＋tests/roots 全 root | Two-build method over both corpora; covers figure-bearing and table-bearing documents | ✓ |
| tests/roots 全 root のみ | Lighter; docs covered only by the compile-level full-corpus gate | |
| 代表 root を選抜 | Lightest; risks missing node-combination regressions | |

**User's choice:** docs/source 全体＋tests/roots 全 root

---

## TBL-05 authoritative axis

### Q1 — which check wins?

| Option | Description | Selected |
|--------|-------------|----------|
| アンカーだけ修復（描画は現状維持） | Carry the visit-side skip decision into depart; anchor on the else path; rendering unchanged | ✓ (final) |
| 構造判定を正にする | depart branches on the structural flag; empty caption becomes a numbered `figure(...)` | ✓ (initial, later reversed) |
| アンカー修復＋警告 | Anchor-only repair plus a new Sphinx warning | |

**User's choice:** first 構造判定を正にする, then — after asking for the LaTeX behaviour to be
measured — reversed to アンカーだけ修復.
**Notes:** The option "add `astext()` to the visit-side pre-check" was ruled out *before* the question
was asked, by measurement: the reproducing title's child is a `raw` node whose `astext()` is
`'<span></span>'` (non-empty) while its rendered output is empty.

### Q2 — warning on an empty-rendered caption?

The owner answered "Other": **"latex出力の挙動を確認する"**. Measurement was run on the identical
input and the question re-presented as a straight LaTeX-vs-structural choice.

| Option | Description | Selected |
|--------|-------------|----------|
| LaTeX に合わせる（アンカーだけ修復） | Rendering keeps the truthiness check (no caption, no number); labels emitted regardless; no warning | ✓ |
| 構造判定のまま進む | Keep the earlier answer; empty caption becomes a numbered figure, diverging from LaTeX | |

**User's choice:** LaTeX に合わせる（アンカーだけ修復）
**Notes / measurement:** `-b latex`, empty-rendered caption → no `\sphinxcaption`, no table number,
but `\phantomsection\label{index:id1}\label{index:tbl-target}` standalone, no warning. Normal caption
→ `\sphinxcaption{REALCAP}\label{index:id1}\label{index:tbl-target}`. Separately measured in Typst:
`caption: {}` and `caption: none` both render nothing yet still consume a figure number
(`Table 3: real` after two empty ones) — which is why "not figure-wrapped" matters.

---

## QUA-01 docstring scope

| Option | Description | Selected |
|--------|-------------|----------|
| skip_ids の記述だけ直す | Name the two real `skip_ids` callers; minimal edit | ✓ |
| 条件で書いて腐らない形に | Describe the *condition* under which a caller passes `skip_ids`, with current examples | |
| 全呼び出し元を列挙 | List all 21 call sites | |

**User's choice:** skip_ids の記述だけ直す
**Notes / measurement:** 21 call sites for `_emit_id_anchors`; only 2 pass `skip_ids`
(`depart_figure` L2518, `depart_table` L3370).

---

## Claude's Discretion

- The fix shape for nested container state (full stack vs. snapshot save/restore).
- Where the inner container's markup is routed so it lands inside the enclosing cell.
- RED gate test-file layout; whether table and figure gates share a file.
- SC#5 timing: when the milestone branch is pushed and whether a green Windows lane gates Phase 44.

## Deferred Ideas

- Other scalar-state containers beyond table/figure — file a todo with the emitted `.typ`, do not
  widen the phase again.
- The wider reachable-nesting sweep (table in admonition / definition list / footnote, …).
- `legend` support beyond what stops the outer caption vanishing.

## Roadmap / requirements amended during this discussion

- `REQUIREMENTS.md`: new **FIG-01** under a new "Figures" section; traceability row added; coverage
  11/11 → **12/12**; Phase 43 mapping note extended; the "no new node handlers" out-of-scope row now
  states FIG-01's exception explicitly.
- `ROADMAP.md`: Phase 43 requirements line, checklist line, **SC#2** amended (TBL-05 axis), **SC#4**
  amended (byte-invariance corpus), **SC#6** appended (FIG-01), and a dated amendment-log entry.
- `STATE.md`: current-focus and Active-Milestone coverage lines updated to 12/12; Phase 43 row.
