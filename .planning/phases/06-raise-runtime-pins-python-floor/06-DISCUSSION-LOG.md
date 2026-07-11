# Phase 6: Raise Runtime Pins + Python Floor - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-09
**Phase:** 6-raise-runtime-pins-python-floor
**Areas discussed:** main Red-Window / Branch Strategy

---

## Gray-Area Selection (multiSelect)

| Area | Description | Selected |
|------|-------------|----------|
| main 赤ウィンドウ戦略 (branch strategy) | How to keep `main` healthy while Phase 6–8 leave PDF/docs-pdf lanes intentionally red | ✓ |
| lockfile 再生成の方法 | targeted upgrade vs full re-resolve | (deferred to planner) |
| Phase 6 の完了検証ゲート | what proves the atomic raise landed before Phase 8's full suite | (deferred to planner) |
| 非 matrix ジョブの Python 版 | 3.12 floor vs 3.13 latest for single-runner jobs | (deferred to planner) |

**User's choice:** Only "main 赤ウィンドウ戦略".

---

## main Red-Window / Branch Strategy

### Q1 — Overall integration strategy

| Option | Description | Selected |
|--------|-------------|----------|
| v0.5.0 統合ブランチ | `release/v0.5.0` branch holds Phase 6–9; main stays green; merge at milestone end | ✓ |
| フェーズ毎に main へ | merge each phase to main as it lands (main goes red Phase 6–7) | |
| main で直接作業 | no branch, work on main directly | |

**User's choice:** v0.5.0 統合ブランチ.

### Q2 — Merge-to-main timing

| Option | Description | Selected |
|--------|-------------|----------|
| 全 CI 緑後に一括 | merge locally once Phase 9 all-green | |
| Phase ごとに段階マージ | staged per-phase merges | |

**User's choice (free text):** 「そもそもマイルストーンコンプリートで PR を発行して github 側でマージ」 — merge only at milestone completion, via a **GitHub Pull Request merged on the GitHub side** (not a local merge). Refines the "全 CI 緑後に一括" option into an explicit PR-based flow.

### Q3 — Handling the intentionally-red PDF/docs-pdf lanes on the branch

| Option | Description | Selected |
|--------|-------------|----------|
| 赤のまま受容 | integration branch isn't main, so accept red; no CI config changes; returns green at Phase 7 | ✓ |
| 一時的に allow-failure/skip | temporarily continue-on-error / skip docs-pdf until Phase 7, then restore | |

**User's choice:** 赤のまま受容.
**Notes:** Explicitly no temporary CI config edits — avoids a "restore the skip" follow-up; the `kai` fix in Phase 7 restores green naturally.

---

## Claude's Discretion

Deferred to the planner (with defaults recorded in CONTEXT.md `<decisions>`):
- lockfile regeneration method → default: targeted `uv lock --upgrade-package` (minimal diff).
- Phase-6 done-ness verification gate → default: `sphinx-build` builder-registration smoke + clean import (full suite is Phase 8).
- non-matrix job Python version → default: move single-runner jobs `3.10 → 3.12` (new floor).

## Deferred Ideas

- typst 0.15 raise + `@preview` bumps + `kai` fix → Phase 7 (roadmapped).
- `traverse()`→`findall()` + full API/test compatibility → Phase 8 (roadmapped).
- No new out-of-phase capabilities were raised.
