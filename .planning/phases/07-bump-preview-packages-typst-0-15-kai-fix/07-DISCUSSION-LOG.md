# Phase 7: Bump @preview Packages + typst 0.15 (kai fix) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-11
**Phase:** 7-bump-preview-packages-typst-0-15-kai-fix
**Areas discussed:** Visual regression tolerance

---

## Gray Area Selection

Four gray areas were surfaced. The user selected **one** to discuss; the other three were
routed to Claude's discretion (already locked by ROADMAP/REQUIREMENTS).

| Gray area | Description | Selected to discuss |
|-----------|-------------|---------------------|
| 検証ゲートの厳密さ (Verification gate rigor) | docs-pdf as-is vs. a pulled-forward all-4-package smoke fixture | |
| 見た目の回帰許容度 (Visual regression tolerance) | compile-only vs. also eyeball the rendered PDF | ✓ |
| バンプ戦略 (Bump strategy) | all-at-once then bisect-on-failure vs. incremental one-at-a-time | |
| codly 破損時の対応 (codly-break escalation) | how far to go if codly 1.3.0 breaks (patch/vendor/swap/pin) | |

---

## Visual Regression Tolerance

### Q1 — Gate level (how much visual verification in the "done" check)

| Option | Description | Selected |
|--------|-------------|----------|
| コンパイル + 目視確認 | Clean `kai`-free compile as hard gate + a human eyeball of the PDF's key elements | ✓ |
| コンパイルのみ | Error-free compile is the whole gate; accept whatever the new versions render | |
| 自動ビジュアル回帰 | Build golden-PDF / snapshot-diff infra to auto-detect visual drift | |

**User's choice:** コンパイル + 目視確認 (compile + human eyeball)
**Notes:** No golden-PDF baseline infra exists; this is a forward-port, not a redesign.

### Q2 — Handling when appearance actually changed

| Option | Description | Selected |
|--------|-------------|----------|
| 新見た目を受入 (壊れてなければ) | Accept the new rendering as the new baseline if nothing is broken | ✓ |
| 旧見た目を復元 | Restore the pre-bump look via config/override/show-rule | |
| ケースバイケース | Judge each change individually | |

**User's choice:** 新見た目を受入 (accept new look if not broken)
**Notes:** Keeps Phase 7 scope small and risk low; no restoration effort.

### Q3 — Comparison reference for the eyeball

| Option | Description | Selected |
|--------|-------------|----------|
| before/after 比較 | Compile a pre-bump "before" PDF (typst 0.14.9 + old pkgs) and diff against after | |
| after 単体の健全性確認 | Inspect only the post-bump PDF standalone for "not broken" | ✓ |

**User's choice:** after 単体の健全性確認 (standalone after-check)
**Notes:** Chose the lighter standalone check over a before/after diff.

### Q4 — Pass criterion for the standalone check

| Option | Description | Selected |
|--------|-------------|----------|
| 3要素チェックリスト | Fixed 3-point check: admonition icon+color / code highlighted / math typeset | |
| エラーグリフの有無のみ | Only check for broken/blank boxes, missing-glyph tofu (⬛), error glyphs | ✓ |
| 全ページ通読 | Human reads every page of the docs PDF | |

**User's choice:** エラーグリフの有無のみ (error-glyph presence only)
**Notes:** The empirical `kai`-free compile is the real gate; the visual glance is only a coarse
"nothing is visibly broken" backstop — no per-element visual audit.

---

## Claude's Discretion

Routed to the planner/researcher as already locked by ROADMAP/REQUIREMENTS (see CONTEXT.md
`<decisions>` → "Claude's Discretion" for the carried defaults):

- **Verification corpus/rigor** — use existing `tox -e docs-pdf` (confirmed to exercise all four
  packages); the dedicated smoke test stays Phase 9 (CI-02).
- **Bump strategy** — bump all four + typst together; bisect only if `kai` persists (ROADMAP contingency).
- **codly-break escalation** — patch/vendor → alternate highlighter → pin highest tolerant typst 0.15.x,
  only if the compile actually breaks on codly 1.3.0.

## Deferred Ideas

- Automated visual-regression / golden-PDF baseline — rejected as over-engineering for a maintenance cycle.
- Dedicated all-4-package `typst compile` smoke fixture — already scheduled as Phase 9 (CI-02).
- (v2, already tracked) CFG-01 user-configurable `@preview` versions; XOS-01 cross-OS docs-PDF CI.
