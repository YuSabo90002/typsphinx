# Phase 32: GitHub Pages Teardown (IRREVERSIBLE) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-27
**Phase:** 32-github-pages-teardown-irreversible
**Areas discussed:** 撤去前ゲートの証拠深度, docs.yml の削減深度, SC#3 観測CI実行の手段

**Area selection:** 4 領域を提示(上記 3 + gh-pages 復活ハザード)。オーナーは 3 領域を選択し、
復活ハザードは議論スキップ → CONTEXT にハザード明記・対処は planner/オーナー判断として記録。

---

## 撤去前ゲートの証拠深度

### Q1: ja HTML の検証深度

| Option | Description | Selected |
|--------|-------------|----------|
| 内容照合まで踏む (推奨) | `/ja/latest/user_guide/builders.html`(65/65 全訳)を curl し既知の翻訳済み文字列を grep。「全英語でも緑」を確実に排除 | ✓ |
| HTTP 200 + 言語マーカー | `lang="ja"` 等の構造マーカーまで。軽いが全英語配信を見逃す | |

### Q2: PDF 側のゲート証拠

| Option | Description | Selected |
|--------|-------------|----------|
| en+ja 両方を配信確認 (推奨) | 両 PDF URL を curl、HTTP 200 + マジックバイト + 常識的サイズ/ページ数。忠実性の再検証はしない | ✓ |
| en のみ配信確認 | SC#1 の単数「the PDF」を RTD-03 系譜(en)と読む | |
| 内容比較まで再実施 | ローカルベースラインとのページ数/テキスト比較を繰り返す(最重、基準コミット不一致で偽赤の恐れ) | |

### Q3: ゲートと撤去のプラン構造

| Option | Description | Selected |
|--------|-------------|----------|
| 別プランで分離 (推奨) | Plan 1 = ゲート(記録のみ)、Plan 2 = 撤去(Plan 1 依存)。赤なら構造的に撤去に入らない | ✓ |
| 同一プランの先頭タスク | 軽いが順序保証がプラン内規律任せ | |
| 任せる | planner 裁量 | |

### Q4: 「freshly re-taken」の鮮度定義

| Option | Description | Selected |
|--------|-------------|----------|
| 撤去と同日 + 直前再確認 (推奨) | 完全証拠は同日有効 + 撤去プラン先頭で 4 URL のステータス再確認。日またぎは完全版再実行 | ✓ |
| ゲート緑のまま有効 | 経過時間の上限なし | |

---

## docs.yml の削減深度

### Q1: 削減範囲

| Option | Description | Selected |
|--------|-------------|----------|
| ステップ+不要権限も削除 (推奨) | peaceiris ステップ + 未使用の `pages: write` / `id-token: write` を削除。`contents: write` は Release 添付に必要で残置 | ✓ |
| デプロイステップのみ削除 | ROADMAP の文面どおり最小 diff | |

### Q2: 再発防止ガードテスト

| Option | Description | Selected |
|--------|-------------|----------|
| 追加する (推奨) | gh-pages デプロイ不在 + Release ステップ存在を断定する小テスト(既存の docs.yml 形状断定パターン踏襲) | ✓ |
| 追加しない | 一回限りの撤去とみなし diff 最小 | |

**Notes:** HTML/PDF アーティファクト upload 残置と INTEGRATIONS.md 差分更新(31 D-18)は
既決事項として確認のみ。

---

## SC#3 観測CI実行の手段

### Q1: 実現手段

| Option | Description | Selected |
|--------|-------------|----------|
| マイルストーン draft PR (推奨) | pull_request トリガーで docs.yml 発火。Phase 30 UAT test 1 の blocked も同時解除。リポジトリ変更ゼロ | ✓ |
| workflow_dispatch 追加 | 恒久改善だが非既定ブランチへの dispatch 可否が未実測。Phase 30 は解消しない | |
| backstop 記録で繰り延べ | Phase 30 前例はあるが 2 フェーズが UAT 未完のまま終盤まで残る | |

### Q2: draft PR を開くタイミング

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 32 の前に開く (推奨) | 先に draft PR → `/gsd-verify-work 30` で Phase 30 完結 → Phase 32 計画/実行。順序の循環を解消 | ✓ |
| Phase 32 実行中に開く | Phase 30 完了ゲートの読み替えが必要になり順序保証が弱まる | |

---

## Claude's Discretion

- ゲートで grep する翻訳済み文字列の選定、PDF サイズ/ページ数しきい値
- ガードテストの関数名・断定の厳密さ
- draft PR のタイトル・本文(英語・簡潔)
- 404 確認のリトライ姿勢(CDN キャッシュ猶予)
- INTEGRATIONS.md 差分更新の記述粒度

## Deferred Ideas

- gh-pages 復活ハザードの恒久対処(議論スキップ — CONTEXT にハザード明記、対処は
  planner 提案 + オーナー判断。最低限 `/gsd-complete-milestone` での ls-remote 再確認を推奨)
