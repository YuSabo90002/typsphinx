# Phase 18: Fidelity Fixes + Regression-Gate Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-19
**Phase:** 18-fidelity-fixes-regression-gate-close
**Areas discussed:** Table fit strategy, Blast radius, Width-hint source

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| テーブルの収め方 (Table fit strategy) | How to render an over-wide table | ✓ |
| 影響範囲 (Blast radius) | All tables vs only-overflowing | ✓ |
| 幅ヒントの取得元 (Width-hint source) | colwidth only vs also tabularcolumns | ✓ |
| 回帰フィクスチャ (Regression fixture) | How a real-compile fixture fails without the fix | (not selected — left to Claude/research) |

**Notes:** GATE-03 excluded from discussion up front as mechanical (corpus re-compile + empty
`unknown_visit` assertion). Phase is discovery-sized with exactly one high-severity root cause (FID-01a / F12).

---

## Table fit strategy (収め方)

| Option | Description | Selected |
|--------|-------------|----------|
| colwidth比をfrで尊重 | `columns: (Nfr, Mfr, …)` from docutils `colspec['colwidth']`; most faithful to HTML colgroup widths | ✓ |
| 全列均等 (1fr) | Ignore colwidth, all `1fr`; simplest but distorts weighted tables | |
| 自動+上限ハイブリッド | Auto width, clamp to `fr` on overflow; ideal but Typst can't know width at translate time | |

**User's choice:** colwidth比をfrで尊重 (推奨)
**Notes:** Requires capturing `colwidth` in `visit_colspec` (currently `raise SkipNode` discards it).

---

## Blast radius (影響範囲)

| Option | Description | Selected |
|--------|-------------|----------|
| 全テーブル一律fr | Every table becomes colwidth-ratio `fr`; simple, deterministic, HTML-like; narrow tables stretch to full width (cosmetic) | ✓ |
| measureでコンパイル時判定 | Typst `context`+`measure` to only constrain on overflow; keeps narrow tables byte-identical but complex to emit + verify | |
| 列数・幅ヒントでヒューリスティック | Translate-time heuristic (col count / tabularcolumns) to switch fr/auto; fragile, no real width visibility | |

**User's choice:** 全テーブル一律fr (推奨)
**Notes:** Accepted cost — narrow tables that render at natural width today will fill the text block.
Content stays faithful; arguably closer to HTML container-filling behavior.

---

## Width-hint source (幅ヒントの取得元)

| Option | Description | Selected |
|--------|-------------|----------|
| colwidthのみ | Honor `colspec['colwidth']` only; `tabularcolumns` stays SkipNode | ✓ (final) |
| tabularcolumnsも拾う | Parse `.. tabularcolumns::` LaTeX column spec, override colwidth | (initially chosen, then reversed) |

**User's choice:** colwidth のみ (reversed from an initial "tabularcolumns も拾う")
**Notes:** User asked "how faithful is Sphinx's HTML to tabularcolumns?" — surfaced that
`.. tabularcolumns::` is a **LaTeX-only** directive that the HTML builder ignores entirely. Since
the Phase 17 D-04 fidelity authority is the HTML build, honoring tabularcolumns would *diverge* from
the baseline rather than converge on it. User reversed to colwidth-only (A) once the fact was clear.
This is the key correction of the session.

---

## Claude's Discretion

- **Regression-fixture proof design** (user deliberately did not select this area). The overflow is
  silent (no fatal, no warning), so the fixture must be constructed to genuinely regress on the unfixed
  translator; `.typ` string-agreement alone is disallowed by SC#1. Left to research/planning to resolve;
  candidate approaches noted in CONTEXT.md.
- Edge-case handling for the fr conversion (missing/zero colwidth → equal 1fr fallback; composition with
  the existing LEN-01 `block(width:)` wrapper).

## Deferred Ideas

- Honoring `.. tabularcolumns::` — rejected for v0.6.1 (HTML authority ignores it); revisit only under a
  future "match LaTeX PDF layout" goal.
- `measure`-at-compile-time conditional column sizing — deferred as over-engineering for a one-root-cause fix.
- F6 (medium, long inline `literal` right-margin overflow) — kin to F12 but different node kind + severity;
  next-milestone candidate, not FID-01a.
- The 13 medium/low audit findings (F1–F11, F13–F15) — recorded in the audit catalogue, next-milestone candidates.
