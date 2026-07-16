# Phase 17: Rendering-Fidelity Audit - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-16
**Phase:** 17-rendering-fidelity-audit
**Areas discussed:** 監査の分業方式, 比較ベースライン, カタログ形式と重大度基準, FID-01 バックログの粒度

---

## 監査の分業方式

### Q1: 一次パスは誰がやるか

| Option | Description | Selected |
|--------|-------------|----------|
| Claude 一次抽出→人間確認 (Recommended) | Claude が PDF ページを画像化して読み、候補リスト化。人間は確認と重大度判定に専念 | ✓ |
| 人間主導 + Claude 記録係 | 人間がページをめくり口頭報告、Claude が記録 | |
| 両者並行(ダブルチェック) | 両者が独立に全ページを見て突き合わせ | |

### Q2: 人間の確認範囲

| Option | Description | Selected |
|--------|-------------|----------|
| 候補全件確認 + 抜き取り (Recommended) | 候補は全件人間が採否・重大度確定。クリーン判定ページも抜き取り確認 | ✓ |
| high 候補のみ確認 | high 候補だけ確認、medium/low は Claude 判定を採用 | |
| 最後にドラフト一括レビュー | カタログ完成稿を文書レビューのみ | |

### Q3: 進捗の区切り/チェックポイント単位

| Option | Description | Selected |
|--------|-------------|----------|
| docname 単位 (Recommended) | .rst ファイルごとに監査済み/未を記録 | ✓ |
| PDF ページ番号単位 | ページ番号で区切る(再コンパイルでずれるリスク) | |
| 章(トップレベル toctree)単位 | 大きなまとまりで区切る(中断耐性低) | |

### Q4: 不確実ケースの扱い

| Option | Description | Selected |
|--------|-------------|----------|
| 候補に含めて人間判定 (Recommended) | 迷ったら「不確実」フラグ付きで候補入れ。偽陽性に寄せる | ✓ |
| 別バケツで後回し | uncertain リストに分離し監査完了後に仕分け | |
| Claude が自己判定 | 除外定義と HTML 見た目を基準に Claude が決め切る | |

**User's choice:** 全問とも Recommended を選択

---

## 比較ベースライン

### Q1: 「忠実なレンダリング」の基準(正)

| Option | Description | Selected |
|--------|-------------|----------|
| HTML ビルドを正とし rST で補強 (Recommended) | 同コーパスの HTML ビルドを主対象、意味確認時のみ rST 参照 | ✓ |
| rST ソースを正とする | ソース直読み(autodoc 等では非現実的) | |
| 常に両方突き合わせ | 全箇所で HTML + rST 両参照(コスト約2倍) | |

### Q2: HTML ベースラインの調達方法

| Option | Description | Selected |
|--------|-------------|----------|
| キャッシュ済みコーパスからローカルビルド (Recommended) | v9.1.0 コーパス(SHA cc7c6f4)から sphinx-build -b html。同一ソース・同一バージョン | ✓ |
| 公開ドキュメント(www.sphinx-doc.org)を参照 | ビルド不要だがバージョン不一致の偽陽性リスク | |

### Q3: 「逸脱」としてカタログに載せる境界

| Option | Description | Selected |
|--------|-------------|----------|
| 内容+構造+意味的スタイル (Recommended) | 内容/構造 + 意味を担うスタイル喪失まで対象。純粋な見た目は対象外 | ✓ |
| 内容+構造のみ | スタイル逸脱は一切カタログしない | |
| 見た目の差分を全部 | 媒体差を除くあらゆる見た目差を網羅 | |

**User's choice:** 全問とも Recommended を選択

---

## カタログ形式と重大度基準

### Q1: カタログの置き場所と形式

| Option | Description | Selected |
|--------|-------------|----------|
| 17-AUDIT-CATALOGUE.md (Recommended) | フェーズディレクトリの単一 Markdown。provenance ヘッダ + issue 表 | ✓ |
| GitHub Issues に起票 | issue ごとに GitHub Issue(二重管理になる) | |
| md + スクリーンショット同梱 | 証拠画像もコミット(リポジトリ肥大化) | |

### Q2: medium / low の境界定義

| Option | Description | Selected |
|--------|-------------|----------|
| 意味損失=medium、外観のみ=low (Recommended) | 判定軸は「読者が何を失うか」。high は SC#4 定義のまま | ✓ |
| 頻度を加味した二軸判定 | 影響の深さ × 発生頻度(SC#4 と基準が二重化) | |
| 事前定義せず事例ベース | 事例ごとに相対判断(セッション間でブレるリスク) | |

### Q3: 1 issue あたりの記録項目

| Option | Description | Selected |
|--------|-------------|----------|
| 必須 3 点 + 再現情報 (Recommended) | SC#2 の 3 点 + PDF ページ番号・発生件数・最小再現 rST 断片 | ✓ |
| SC#2 の必須 3 点のみ | 最小限(Phase 18 で探し直しの二度手間) | |
| フルスキーマ(証拠画像参照含む) | ページ画像パスまで毎件記録 | |

**User's choice:** 全問とも Recommended を選択

---

## FID-01 バックログの粒度

### Q1: FID-01a… の 1 件の単位

| Option | Description | Selected |
|--------|-------------|----------|
| 根本原因単位 (Recommended) | 同一不具合は 1 要件に集約、発生箇所は要件内列挙。Phase 18 の修正単位と一致 | ✓ |
| 発生箇所単位 | 箇所ごとに 1 要件(重複要件が並ぶ) | |
| ノード種別単位 | node kind ごとに 1 要件(完了判定が曖昧化) | |

### Q2: REQUIREMENTS.md への追記範囲

| Option | Description | Selected |
|--------|-------------|----------|
| high のみ FID-01x、他は Future 行き (Recommended) | FID-01a… は high のみ(SC#4 の文面通り)。medium/low は Future Requirements にポインタ | ✓ |
| high + medium を登録 | medium も FID-01x 化(スコープ肥大リスク) | |
| 全重大度を登録 | low まで全登録(要件表がノイズ化) | |

**User's choice:** 全問とも Recommended を選択

---

## Claude's Discretion

- PDF ページ画像化のツールと解像度、セッションごとのページバッチ方法
- 17-AUDIT-CATALOGUE.md の表スキーマ詳細と docname 進捗トラッカーの置き方(カタログ内チェックリスト or 別ファイル)
- HTML ベースラインビルドでのコーパス conf の doc-build-only 拡張の扱い(Phase 15 の判断を踏襲)
- 一次パスの優先順位付けに使う機械的プレフィルタ(テキスト抽出 diff 等)— 全ページ視覚確認の SC#1 バーと D-01a 確認フローを崩さない範囲で

## Deferred Ideas

- medium/low の修正 — カタログ + Future Requirements ポインタに記録、v0.6.1 Phase 18 の義務外
- issue ごとの証拠スクリーンショットのコミット — リポジトリ肥大化を避けて不採用(ページ番号 + 再現断片が恒久証拠)
