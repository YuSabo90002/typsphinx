# Phase 3: Modernize Python Floor (3.10-3.13) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-04
**Phase:** 3-Modernize Python Floor (3.10-3.13)
**Areas discussed:** Single-version job pin, 3.13 wheel-gap / reformat contingency, Commit/batch granularity

---

## Area selection

Presented 4 candidate gray areas (multiSelect). User selected 3; deferred the 4th.

| Gray area | Selected |
|-----------|----------|
| 単一バージョンジョブのピン (single-version job pin) | ✓ |
| 3.13 wheel欠落・再フォーマットの逃げ道 (wheel-gap / reformat contingency) | ✓ |
| コミット/バッチ粒度 (commit/batch granularity) | ✓ |
| 検証の深さ (verification depth) | — (carried forward Phase 2 D-01: push→observe Actions = done) |

---

## Single-Version Job Python Pin

| Option | Description | Selected |
|--------|-------------|----------|
| フロア 3.10 に統一 | black/ruff target-version (py310) + mypy python_version (3.10) と interpreter が一致、floor が実際に行使される。PYVER-02 の "reconcile with floor" を素直に満たす | ✓ |
| 3.11 のまま (最小 diff) | 現状維持。3.11 は floor 以上なので技術的には reconcile 済みだが tool-config/interpreter がずれる | |
| 最新 3.13 に統一 | build/lint を最新で行使。ただし floor(3.10) 単体検証はマトリクス依存 | |

**User's choice:** フロア 3.10 に統一 (→ CONTEXT.md D-01)
**Notes:** All hardcoded `uv python install 3.11` (ci.yml ×5) + docs.yml setup-python + release.yml ×2 → 3.10.

---

## 3.13 Wheel-Gap Contingency

| Option | Description | Selected |
|--------|-------------|----------|
| 回避ピンで 3.13 を維持 | 該当依存を 3.13 対応版に小さく上げてマトリクスを 3.10-3.13 で完全に保つ | ✓ |
| 落とす前にブロッカー化して相談 | 回避困難なら 3.13 を除外せず blocker として表面化 | |
| Claude 判断 | 状況に応じて判断 | |

**User's choice:** 回避ピンで 3.13 を維持 (→ CONTEXT.md D-02)
**Notes:** Unlikely for 2026; a targeted dep bump *for 3.13 support* is allowed in-batch even though general tooling bumps are Phase 4.

---

## Reformatting from target-version Bump

| Option | Description | Selected |
|--------|-------------|----------|
| 同じバッチに含める | target-version 変更は Python 引き上げそのもの＝同一原因、1 アトミックバッチに含めるのが自然 | ✓ |
| 別コミットに分ける | Phase1 D-04 流儀で blame 分離。ただし 1 PR 内 | |
| 発生しなければ不要 | py39→py310 で black 出力はほぼ不変。差分が出た場合のみ適用 | |

**User's choice:** 同じバッチに含める (→ CONTEXT.md D-03)
**Notes:** Distinct from Phase 1, where the reformat was unrelated to the pin. Here it shares the root cause.

---

## Commit / Batch Granularity

| Option | Description | Selected |
|--------|-------------|----------|
| サーフェス別コミット × 1 PR | pyproject / tox / workflows を分割。blame・部分切り戻しを容易に。アトミック性は PR 単位の 1 グリーン CI で担保 | ✓ |
| 単一コミット | literally 1 コミットで最大限アトミック。切り戻しは全か無か | |
| Claude 判断 | プラン時に判断 | |

**User's choice:** サーフェス別コミット × 1 PR (→ CONTEXT.md D-04)
**Notes:** "One atomic batch" satisfied at PR level (single green CI run).

---

## Claude's Discretion

- Exact YAML shape of the ci.yml matrix `include:` mapping (add py313, drop py39).
- Ordering/number of per-surface commits within the single PR.
- `gh` invocations and PR-vs-push trigger tactic (must exercise docs.yml).

## Deferred Ideas

- Dev-tooling floor bumps + GitHub Actions version refreshes — Phase 4 (TOOL-01/02).
- Durability guardrails (`uv sync --locked`, weekly drift job, dependabot grouping, CI badge) — Phase 5.
