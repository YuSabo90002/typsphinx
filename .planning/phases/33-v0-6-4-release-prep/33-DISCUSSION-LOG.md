# Phase 33: v0.6.4 Release Prep - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-28
**Phase:** 33-v0.6.4 Release Prep
**Areas discussed:** CHANGELOG 構成と BREAKING 判定, 公開前 planning ドキュメント英語化（ユーザー追加）

---

## 保留 todo の照合

| Option | Description | Selected |
|--------|-------------|----------|
| 折り込まない (Recommended) | Phase 28 と同じ裁定。解決済み 2 件の整理はマイルストーン close 側 | ✓ |
| 解決済み 2 件の整理のみ折り込む | github.io 404 / orphan クラスの todo ファイル移動を本フェーズに含める | |

**User's choice:** 折り込まない
**Notes:** 上位 2 件は Phase 31/30 で解決済み（ファイルが pending/ に残置）、残り 5 件はソース/CI 変更系で不変量 #3 の対象外。

---

## 討議領域の選択

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG 構成と BREAKING 判定 | コード変更ゼロの特殊なマイルストーンのエントリ構成 | ✓ |
| 不変量検証の証拠セット (SC#4) | 全差分 254 コミットへの断定に何を回すか | |
| ハンドオフチェックリストの範囲と置き場所 (SC#5) | 2 リポジトリタグ、flip 群、#119 等の集約 | |
| 30.1 レビュー警告 3 件の扱い | custom_template.typ の同期ガード外問題ほか | |

**User's choice:** CHANGELOG 構成と BREAKING 判定 のみ
**Notes:** 未選択 3 領域は Claude 裁量 + プラン時判断として CONTEXT に記録。

---

## CHANGELOG 構成と BREAKING 判定

### Q1: BREAKING ラベルの対象

| Option | Description | Selected |
|--------|-------------|----------|
| BREAKING なし (Recommended) | パッケージ無変更。404 はホスティング項目の本文但し書き | ✓ |
| 旧 URL 404 に BREAKING | 公開 URL の消滅を Phase 23 D-05 と同型の仕様破壊とみなす | |
| 404 + multilang 削除の両方に BREAKING | リポジトリ利用者も壊れる対象とみなす | |

**User's choice:** BREAKING なし → **D-01**

### Q2: ja サイト告知の翻訳カバレッジ表記

| Option | Description | Selected |
|--------|-------------|----------|
| 定性的な但し書き (Recommended) | 「部分的に翻訳済み。未翻訳箇所は英語」と数値なしで書く | |
| 24.3% を明記 | 実測値をリリース時点の事実として書く | |
| 但し書きなし | 「日本語サイトを公開」とだけ書く | ✓ |

**User's choice:** 但し書きなし（推奨案を採らずより簡潔を選択）→ **D-02**

### Q3: `### Verified` 節の構成

| Option | Description | Selected |
|--------|-------------|----------|
| 不変量のみ (Recommended) | git diff で証明可能な 3 点のみ。RTD 配信観測は時点依存で載せない | ✓ |
| 不変量 + RTD 配信観測 | Phase 32 ゲートの実 HTTP 観測もリリース時点の検証実績として載せる | |
| Verified 節を置かない | 不変量はリード段落の一行に畳む | |

**User's choice:** 不変量のみ → **D-03**

### Q4: セクション割り

| Option | Description | Selected |
|--------|-------------|----------|
| URL 修正を Fixed に (Recommended) | 死リンクはバグ → Fixed（Phase 23 D-03/D-04 踏襲）。5 節構成 | ✓ |
| URL 書き換えも Changed に統合 | 移行の一部として統合、Fixed 節を置かない | |
| 細部は Claude 裁量 | D-09 原則 + D-01〜03 だけ固定 | |

**User's choice:** URL 修正を Fixed に（プレビューの 5 節骨子ごと承認）→ **D-04**

---

## 公開前 planning ドキュメント英語化（ユーザー追加領域）

ユーザー発言: 「PROJECT.md が日本語混じりなのを公開前に英語に完全にしておく」。
実測: PROJECT.md 108 行 / ROADMAP.md 12 行 / MILESTONES.md 11 行 / STATE.md 1 行に日本語。

| Option | Description | Selected |
|--------|-------------|----------|
| PROJECT.md のみ | ユーザー指定ファイルだけ（108 行） | |
| トップレベル 4 ファイル (Recommended) | PROJECT + ROADMAP + MILESTONES + STATE。履歴アーカイブ対象外 | ✓ |

**User's choice:** トップレベル 4 ファイル → **D-05**

---

## Claude's Discretion

- SC#4 の証拠セットの範囲（フル pytest / docs ビルド / コーパスゲートの要否）
- SC#5 ハンドオフチェックリストの形式・置き場所（収載既知項目は CONTEXT `<specifics>`）
- CHANGELOG 各項目の文面、`uv.lock` 再生成手順、プラン分割
- D-05 英語化の訳文文体・用語統一

## Deferred Ideas

- 30.1 レビューの 3 Warnings（同期ガード第 4 サイトほか）— 討議未選択、planner 判断
- 解決済み todo 2 件の pending/ 整理 — マイルストーン close 側（ハンドオフ項目 8）
